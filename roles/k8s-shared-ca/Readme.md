# k8s-shared-ca ロール

このロールは Cilium Cluster Mesh などで共有する Kubernetes 共通認証局(Certificate Authority)証明書 (CA)（以下、共通CA）を `ansible-playbook` コマンド実行ノード(以下, `制御ノード`と記載)上で準備し, コントロールプレーン各ホストへ 所有者`root:root`, アクセス権`600` で展開します。

共通CAの主な用途は以下の通りです。

- `k8s_shared_ca_replace_kube_ca: true` を指定した場合の kube-apiserver / controller-manager / scheduler 等コアコンポーネント証明書の再発行時に使用
- `roles/k8s-ctrlplane/tasks/config-cluster-mesh-tools.yml` が, クラスタ証明書を埋め込んだ`kubeconfig`を生成する処理(`create-embedded-kubeconfig.py --shared-ca`) 内で, `kubeconfig`に埋め込むクラスタ証明書として使用
- Cilium Cluster Mesh 用 `cilium-ca` Kubernetes 上で機密情報を保持するリソース(`Secret`) を発行する `cilium-shared-ca` ロールが共通CAとして参照 (`cilium_shared_ca_enabled: true` かつ `cilium_shared_ca_reuse_k8s_ca: true` を指定した場合に, この共通CAで `cilium-ca` Kubernetes 上で機密情報を保持するリソース(`Secret`) を生成し, Cluster Mesh で相互接続する複数 Kubernetes クラスタ間の mTLS を同一発行元で統一する目的で使用されます)

`enable_create_k8s_ca` と `k8s_common_ca` の組み合わせで以下のように動作します。

| enable_create_k8s_ca | k8s_common_ca | ロールの挙動 |
| -------------------- | ------------- | ------------ |
| false                | 必須          | 指定ディレクトリ内の `cluster-mesh-ca.crt` と `cluster-mesh-ca.key` を利用します。これらのファイルが読めない場合は, 即エラーで`playbook`の動作を終了します。 |
| true                 | 有効          | 指定ディレクトリ内の共通CAを最優先で再利用します。 |
| true                 | 読めない      | 指定ディレクトリにアクセスできない場合は警告を出したうえでロール内に含まれる共通CAまたは新規生成にフォールバックします。 |
| true                 | 未指定        | `roles/k8s-shared-ca/files/shared-ca/` に既存のCAがあれば再利用します。無ければ OpenSSL で新規生成し, `files/shared-ca/` に保存して次回以降も利用します。 |

このロールは再実行可能な設計になっており, 既存ファイルがある場合は作成済みの証明書, 鍵ファイルを再利用します。

生成した共通CAはセキュリティ要件に応じて, 適切に運用, 管理してください。

## 変数一覧

共通CAとして参照される基準の証明書と秘密鍵の組は, このロールでは `k8s_shared_ca_*` で指示されたファイルを意味する。

1. `vars/all-config.yml` 等で `enable_create_k8s_ca` / `k8s_common_ca` を設定します。
2. 共通CAを再生成する場合は, `k8s_common_ca` を空にし, `roles/k8s-shared-ca/files/shared-ca/` を空にしてからプレイブックを実行します。
3. `ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml --tags k8s-shared-ca` で単体実行し, CAが生成, 配布されることを確認します。
4. 正常実行後, 各コントロールプレーンノード上で `/etc/kubernetes/pki/shared-ca/` 配下に `600` 権限の CA鍵/証明書が作成されていることを確認します。
5. `k8s_shared_ca_replace_kube_ca` を `true` にした場合は, `sudo openssl x509 -noout -issuer -in /etc/kubernetes/pki/apiserver.crt` などで API サーバ証明書の発行者が共通CA (`cluster-mesh-ca`) へ切り替わっていることを確認します。併せてワーカーノードの再 join を行い, 新しいルートCAを信頼させます。
6. `roles/k8s-ctrlplane/tasks/config-cluster-mesh-tools.yml` が呼び出す `create-embedded-kubeconfig.py` は `--shared-ca` オプションでこの証明書を埋め込むため, `cilium clustermesh status` 等で TLS エラーが解消されることを確認してください。

## 保管ポリシー

- 生成された CA 秘密鍵 (`cluster-mesh-ca.key`) は **必ず** 所有者:`root:root`, アクセス権`600`で保持します。

セキュリティ要件に応じて, 制御ノード上では `ansible-vault encrypt roles/k8s-shared-ca/files/shared-ca/cluster-mesh-ca.key` などを用いて暗号化保管することを推奨します。Vault パスワードは別媒体で管理してください。セキュリティ要件に応じて別途対策を検討, 実施してください。

また, 耐災害性を確保する必要がある用途では, オフラインバックアップとして, 暗号化されたメディア ( ハードウェアトークンやフルディスク暗号化済みUSBストレージ等 )に CA 鍵と証明書, Vault パスワード情報を保管するなどの対策を別途実施してください。

## ローテーション手順の指針

1. 新しい CA を生成する場合は, 既存クラスタの再構築前に `roles/k8s-shared-ca/files/shared-ca/` をバックアップし, 必要なら Vault へも保存します。
2. `enable_create_k8s_ca: true` のまま `roles/k8s-shared-ca/files/shared-ca/` を空にしてプレイブックを再実行すると, 新しい共通CAが生成されます。
3. 既存クラスタへの段階的移行が必要な場合は, サービス停止計画を立てた上で以下を順に実行します。
   - 新CA配布 (`k8s-shared-ca` ロール再実行)
   - Cilium Cluster Mesh 証明書の再発行
   - `cilium clustermesh status` による疎通確認
4. ローテーション後は旧CAを失効または安全に廃棄し, Vaultおよびオフラインバックアップを更新します。

## 検証ポイント

- 制御ノードの `roles/k8s-shared-ca/files/shared-ca/` に期待した CA ファイルが存在する。
- コントロールプレーン各ノードに `k8s_shared_ca_output_dir` が `0700`, CAファイルが `0600` で配置されている。
- `k8s_shared_ca_replace_kube_ca: true` の場合, `/etc/kubernetes/pki/ca.crt` / `ca.key` が共通CAへ置き換わり, `apiserver.crt` 等の証明書発行者が `cluster-mesh-ca` となっている。
- `create-embedded-kubeconfig.py --shared-ca` で生成した kubeconfig の `certificate-authority-data` が共通CAに差し変わっている ( スクリプトの INFO ログで確認可能 )。
- Cluster Mesh 接続後に `cilium clustermesh status` で TLS エラーが発生しない。
