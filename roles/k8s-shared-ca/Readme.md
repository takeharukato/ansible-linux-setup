# k8s-shared-ca ロール

このロールは Cilium Cluster Mesh などで共有する Kubernetes 共通認証局(Certificate Authority)証明書 (CA) ( 以下, 共通CA )を `ansible-playbook` コマンド実行ノード(以下, `制御ノード`と記載)上で準備し, 各コントロールプレーンノードへ 所有者`root:root`, アクセス権`600` で展開します。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Application Programming Interface | API | アプリケーション同士がやり取りする方法を定めた仕様。 |
| Custom Resource Definition | CRD | Kubernetes APIを拡張してユーザ独自のリソース種別を定義する仕組み。 |
| Role-Based Access Control | RBAC | ユーザやサービスアカウントが実行可能な操作を役割(Role)で制限する仕組み。 |
| Service Account | - | Kubernetes内部でPodが他のリソースにアクセスする際に用いる仮想的なアカウント。 |
| ClusterRole | - | Kubernetesクラスタ全体に適用される権限の集合。 |
| ClusterRoleBinding | - | ClusterRoleをユーザやサービスアカウントに紐付ける仕組み。 |
| Role | - | 特定の名前空間内で有効な権限の集合。 |
| RoleBinding | - | Roleをユーザやサービスアカウントに紐付ける仕組み。 |
| Namespace | - | Kubernetes内部でリソースを論理的に分離する単位。 |
| ポッド ( Pod ) | - | Kubernetes上で動作するコンテナの最小単位。 |
| デーモンセット ( DaemonSet ) | - | Kubernetesクラスタ内の全ノード(または指定した一部のノード)で必ずPodを1つずつ起動させるリソース。 |
| デプロイメント ( Deployment ) | - | 指定した数のPodを維持し, ローリングアップデート等を管理するリソース。 |
| StatefulSet | - | 状態を持つアプリケーションのPodを順序付けて管理するリソース。 |
| サービス ( Service ) | - | Podへのアクセスを抽象化し, 負荷分散やサービスディスカバリを提供するリソース。 |
| Ingress | - | Kubernetesクラスタ外部からHTTP/HTTPS通信を受け付け, 内部のServiceへルーティングする仕組み。 |
| コンフィグマップ ( ConfigMap ) | - | 設定情報を保持し, Podへ環境変数やファイルとして注入するリソース。 |
| シークレット ( Secret ) | - | 機密情報を保持し, Podへ安全に注入するリソース。 |
| PersistentVolume | PV | Kubernetesクラスタ内で利用可能なストレージリソースを表すオブジェクト。 |
| PersistentVolumeClaim | PVC | ユーザがPVを要求する際に利用するリソース。 |
| StorageClass | - | 動的にPVをプロビジョニングする際のストレージ種別を定義するリソース。 |
| Kubernetes ノード ( Kubernetes Node ) | - | Kubernetesクラスタを構成する物理マシンまたは仮想マシン。 |
| コントロールプレーンノード ( Control Plane Node ) | - | Kubernetesクラスタ全体を管理, 制御する中枢ノード群。kube-apiserver, kube-controller-manager, kube-schedulerなどが動作する。 |
| ワーカノード ( Worker Node ) | - | 実際にアプリケーションのPodを実行するノード。 |
| kube-apiserver | - | KubernetesのAPIリクエストを受け付け, etcdへの読み書きを仲介するコンポーネント。 |
| kube-controller-manager | - | Deployment, ReplicaSetなど各種コントローラを実行し, Kubernetesクラスタの状態を監視, 調整するコンポーネント。 |
| kube-scheduler | - | 新規作成されたPodを適切なNodeへ配置するコンポーネント。 |
| kubelet | - | 各Node上で動作し, Podの起動, 停止, 監視を行うエージェント。 |
| kube-proxy | - | 各Node上でServiceのネットワークルールを管理するコンポーネント。 |
| etcd | - | KubernetesのKubernetesクラスタ状態を保存する分散Key-Valueストア。 |
| Container Network Interface | CNI | コンテナ間のネットワーク接続を標準化するプラグイン仕様。 |
| Cilium | - | eBPFを活用した高性能なCNIプラグイン。ネットワークポリシーやサービスメッシュ機能を提供する。 |
| Multus | - | 複数のCNIプラグインを同時に使用できるようにするメタCNIプラグイン。 |
| Container Runtime Interface | CRI | Kubernetesがコンテナランタイムと通信するための標準インターフェース。 |
| containerd | - | Dockerから分離された軽量なコンテナランタイム。 |
| kubeadm | - | Kubernetesクラスタの初期構築と管理を支援する公式ツール。 |
| kubectl | - | Kubernetesクラスタを操作するためのコマンドラインツール。 |
| Helm | - | Kubernetesアプリケーションのパッケージ管理ツール。Chart形式でアプリケーションを配布, インストールする。 |
| Chart | - | Helmで管理されるアプリケーションパッケージの単位。Kubernetes Manifestのテンプレート集。 |
| Operator | - | アプリケーション固有の運用知識をコードで自動化するKubernetesの拡張パターン。 |
| Custom Resource | CR | CRDで定義されたユーザ独自のリソースの実体。 |
| Admission Controller | - | APIリクエストがetcdに保存される前に検証, 変更を行うプラグイン。 |
| Network Policy | - | Pod間の通信を制御するファイアウォールルールを定義するリソース。 |
| Label | - | リソースに付与するKey-Value形式のメタデータ。リソースの分類, 検索に利用される。 |
| Selector | - | Labelを利用してリソースを選択する条件式。 |
| Annotation | - | リソースに付与するKey-Value形式の補足情報。ツールやコントローラが参照するメタデータ。 |
| Taint | - | Kubernetes ノードに設定する特殊なマークで, 特定の条件を満たさないPodの配置を拒否する。 |
| Toleration | - | PodがTaintを持つNodeへ配置されることを許可する設定。 |

共通CAの主な用途は以下の通りです。

- `k8s_shared_ca_replace_kube_ca: true` を指定した場合の kube-apiserver / controller-manager / scheduler 等コアコンポーネント証明書の再発行時に使用
- `roles/k8s-ctrlplane/tasks/config-cluster-mesh-tools.yml` が, クラスタ証明書を埋め込んだ`kubeconfig`を生成する処理(`create-embedded-kubeconfig.py --shared-ca`) 内で, `kubeconfig`に埋め込むクラスタ証明書として使用
- Cilium Cluster Mesh 用 `cilium-ca` Kubernetes 上で機密情報を保持するリソース(`Secret`) を発行する `k8s-cilium-shared-ca` ロールが共通CAとして参照 (`k8s_cilium_shared_ca_enabled: true` かつ `k8s_cilium_shared_ca_reuse_k8s_ca: true` を指定した場合に, この共通CAで `cilium-ca` Kubernetes 上で機密情報を保持するリソース(`Secret`) を生成し, Cluster Mesh で相互接続する複数 Kubernetes クラスタ間の mTLS を同一発行元で統一する目的で使用されます)

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

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `enable_create_k8s_ca` | `false` | 共通CAをロール内で新規生成するか、既存ファイルを必須とするかを切り替えます。|
| `k8s_common_ca` | `""` | 既存の共通CAが格納されたディレクトリパス。未指定時はロール同梱資材または新規生成にフォールバックします。|
| `k8s_shared_ca_output_dir` | `/etc/kubernetes/pki/shared-ca` | コントロールプレーンノードに配布する共通を一式の配置先ディレクトリ。|
| `k8s_shared_ca_cert_filename` | `cluster-mesh-ca.crt` | 共通CA証明書ファイル名。|
| `k8s_shared_ca_key_filename` | `cluster-mesh-ca.key` | 共通CA秘密鍵ファイル名。|
| `k8s_shared_ca_subject` | `/CN=cilium-cluster-mesh-ca` | 新規生成時に指定する証明書サブジェクト。|
| `k8s_shared_ca_valid_days` | `3650` | 新規生成する共通CAの有効日数。|
| `k8s_shared_ca_key_size` | `4096` | 新規生成時に使用するRSA鍵長。|
| `k8s_shared_ca_digest` | `sha256` | 証明書署名に利用するダイジェストアルゴリズム。|
| `k8s_shared_ca_replace_kube_ca` | `false` | Kubernetes既定のルートCAを共通CAへ置き換えるかを制御します。|

## ロール内の動作

共通CAとして参照される基準の証明書と秘密鍵の組は, このロールでは `k8s_shared_ca_*` で指示されたファイルを意味する。

1. `vars/all-config.yml` 等で `enable_create_k8s_ca` / `k8s_common_ca` を設定します。
2. 共通CAを再生成する場合は, `k8s_common_ca` を空にし, `roles/k8s-shared-ca/files/shared-ca/` を空にしてからプレイブックを実行します。
3. `ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml --tags k8s-shared-ca` で単体実行し, CAが生成, 配布されることを確認します。
4. 正常実行後, 各コントロールプレーンノード上で `/etc/kubernetes/pki/shared-ca/` 配下に `600` 権限の CA鍵/証明書が作成されていることを確認します。
5. `k8s_shared_ca_replace_kube_ca` を `true` にした場合は, `sudo openssl x509 -noout -issuer -in /etc/kubernetes/pki/apiserver.crt` などで kube-apiserver証明書の発行者が共通CA (`cluster-mesh-ca`) へ切り替わっていることを確認します。併せてワーカーノードの再 join を行い, 新しいルートCAを信頼させます。
6. `roles/k8s-ctrlplane/tasks/config-cluster-mesh-tools.yml` が呼び出す `create-embedded-kubeconfig.py` は `--shared-ca` オプションでこの証明書を埋め込むため, `cilium clustermesh status` 等で TLS エラーが解消されることを確認してください。

## 保管ポリシー

- 生成された CA 秘密鍵 (`cluster-mesh-ca.key`) は **必ず** 所有者:`root:root`, アクセス権`600`で保持します。

セキュリティ要件に応じて, 制御ノード上では `ansible-vault encrypt roles/k8s-shared-ca/files/shared-ca/cluster-mesh-ca.key` などを用いて暗号化保管することを推奨します。Vault パスワードは別媒体で管理してください。セキュリティ要件に応じて別途対策を検討, 実施してください。

また, 耐災害性を確保する必要がある用途では, オフラインバックアップとして, 暗号化されたメディア ( ハードウェアトークンやフルディスク暗号化済みUSBストレージ等 )に CA 鍵と証明書, Vault パスワード情報を保管するなどの対策を別途実施してください。

## ローテーション手順の指針

1. 新しい CA を生成する場合は, 既存Kubernetesクラスタの再構築前に `roles/k8s-shared-ca/files/shared-ca/` をバックアップし, 必要なら Vault へも保存します。
2. `enable_create_k8s_ca: true` のまま `roles/k8s-shared-ca/files/shared-ca/` を空にしてプレイブックを再実行すると, 新しい共通CAが生成されます。
3. 既存Kubernetesクラスタへの段階的移行が必要な場合は, サービス停止計画を立てた上で以下を順に実行します。
   - 新CA配布 (`k8s-shared-ca` ロール再実行)
   - Cilium Cluster Mesh 証明書の再発行
   - `cilium clustermesh status` による疎通確認
4. ローテーション後は旧CAを失効または安全に廃棄し, Vaultおよびオフラインバックアップを更新します。

## 検証ポイント

- 制御ノードの `roles/k8s-shared-ca/files/shared-ca/` に期待した CA ファイルが存在する。
- 各コントロールプレーンノードに `k8s_shared_ca_output_dir` が `0700`, CAファイルが `0600` で配置されている。
- `k8s_shared_ca_replace_kube_ca: true` の場合, `/etc/kubernetes/pki/ca.crt` / `ca.key` が共通CAへ置き換わり, `apiserver.crt` 等の証明書発行者が `cluster-mesh-ca` となっている。
- `create-embedded-kubeconfig.py --shared-ca` で生成した kubeconfig の `certificate-authority-data` が共通CAに差し変わっている ( スクリプトの INFO ログで確認可能 )。
- Cluster Mesh 接続後に `cilium clustermesh status` で TLS エラーが発生しない。
