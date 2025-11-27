# cilium-shared-ca ロール

Cilium Cluster Mesh で利用する `cilium-ca` は Kubernetes 上で機密情報を保持するリソース(`Secret`)です。このロールは共通CAから `cilium-ca` を生成して適用し, Cluster Mesh 間で共通CAを統一することで TLS ハンドシェイクの失敗や 機密情報保持リソース(`Secret`) の不一致を防ぎます。

## 実行フロー

1. `load-params.yml` で変数を読み込みます。
2. `cilium-ca.yml` が共通CAの証明書と鍵を取得し, `kubectl apply` で `kube-system/cilium-ca` 機密情報保持リソース(`Secret`) を更新します。
3. 既存の `package.yml` など残りのタスクを従来通り実行します。

機密情報保持リソース(`Secret`)の適用は `run_once` で一度だけ実行し, Manifest はテンポラリファイルに書き出した後に削除します。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `cilium_shared_ca_enabled` | `false` | このロールによる 機密情報保持リソース(`Secret`)作成を有効化します。|
| `cilium_shared_ca_reuse_k8s_ca` | `false` | `k8s-shared-ca` が配布した共通CAを再利用します。|
| `cilium_shared_ca_output_dir` | `/etc/kubernetes/pki/cilium-shared-ca` | 証明書と鍵を自動生成する際の出力ディレクトリを指定します。|
| `cilium_shared_ca_cert_filename` | `cilium-ca.crt` | 自動生成する証明書のファイル名を指定します。|
| `cilium_shared_ca_key_filename` | `cilium-ca.key` | 自動生成する秘密鍵のファイル名を指定します。|
| `cilium_shared_ca_cert_path` | `""` | 既存の証明書ファイルをフルパスで指定する場合に設定します。|
| `cilium_shared_ca_key_path` | `""` | 既存の秘密鍵ファイルをフルパスで指定する場合に設定します。|
| `cilium_shared_ca_kubeconfig` | `/etc/kubernetes/admin.conf` | 機密情報保持リソース(`Secret`) 適用時に利用する kubeconfig を指定します。|
| `cilium_shared_ca_secret_name` | `cilium-ca` | 生成する 機密情報保持リソース(`Secret`) の名前を指定します。|
| `cilium_shared_ca_secret_namespace` | `kube-system` | 機密情報保持リソース(`Secret`) を配置する Namespace を指定します。|
| `cilium_shared_ca_secret_type` | `Opaque` | 作成する 機密情報保持リソース(`Secret`) の `type` を指定します。|
| `cilium_shared_ca_secret_cert_key` | `ca.crt` | 機密情報保持リソース(`Secret`) に格納する証明書データのキー名を指定します。|
| `cilium_shared_ca_secret_key_key` | `ca.key` | 機密情報保持リソース(`Secret`) に格納する秘密鍵データのキー名を指定します。|
| `cilium_shared_ca_secret_labels` | `{ "app.kubernetes.io/managed-by": "Helm" }` | 機密情報保持リソース(`Secret`) に対して Helm 管理ラベルを明示的に指定する変数です。未指定でも Helm が `app.kubernetes.io/managed-by: Helm` を自動付与します。|
| `cilium_shared_ca_secret_annotations` | `{ "meta.helm.sh/release-name": "cilium", "meta.helm.sh/release-namespace": "kube-system" }` | 機密情報保持リソース(`Secret`) に対して Helm 管理アノテーションを明示的に指定する変数です。未指定でも Helm が `meta.helm.sh/*` を自動付与します。|
| `cilium_shared_ca_auto_create` | `true` | 共通CAファイルが存在しない場合に自動生成するかどうかを指定します。|
| `cilium_shared_ca_key_size` | `4096` | 自動生成する秘密鍵のビット長を指定します。|
| `cilium_shared_ca_valid_days` | `3650` | 自動生成する証明書の有効日数を指定します。|
| `cilium_shared_ca_digest` | `sha256` | 証明書生成時に使用するダイジェストアルゴリズムを指定します。|
| `cilium_shared_ca_subject` | `/CN=Cilium Cluster Mesh CA` | 自動生成する証明書のサブジェクトを指定します。|

## 共通CAを流用する場合

`cilium_shared_ca_reuse_k8s_ca` を `true` に設定すると, 同一ホストで事前に実行した `k8s-shared-ca` ロールが展開した共通CA (`k8s_shared_ca_cert_path` / `k8s_shared_ca_key_path`) を利用します。これらの設定値が存在しない場合はタスクが失敗するため, `cilium_shared_ca_reuse_k8s_ca` を有効にする際は必ず `k8s-shared-ca` ロールを先に適用してください。

## Cilium Cluster Mesh 用の共通CAを自動生成する場合

`cilium_shared_ca_auto_create` を `true` に設定すると, Cilium Cluster Mesh 用の共通CAを自動生成します。

`cilium_shared_ca_output_dir` と `cilium_shared_ca_cert_filename` / `cilium_shared_ca_key_filename` で指定したファイルが存在しない場合のみ `openssl` を用いて証明書と鍵を生成します。指定したファイルが既に存在する場合は上書きせず, そのまま利用します。

`cilium_shared_ca_auto_create` を `false` に設定すると, ロールは `*_filename` で指定したファイルに対して書き込みを行わず, 既存ファイルが存在する前提で動作します。

`cilium_shared_ca_cert_path` / `cilium_shared_ca_key_path` を指定した場合は, `cilium_shared_ca_auto_create` の値に関わらずこれらのファイルを使用します。`*_filename` に指定したファイルが存在しない状態で `cilium_shared_ca_auto_create: false` として実行すると, プレイブックはエラーで終了します。

## CA を明示的に指定する場合

独自に作成した CA を使用したい場合は, 証明書と鍵をあらかじめ `cilium_shared_ca_output_dir` に配置するか, `cilium_shared_ca_cert_path` / `cilium_shared_ca_key_path` にフルパスを設定してください。必要に応じて `cilium_shared_ca_auto_create` を `false` に切り替えます。

## 機密情報保持リソース(`Secret`) 適用時の注意

- `cilium_shared_ca_enabled` が `false` の場合, このロールは 機密情報保持リソース(`Secret`) を変更しません。
- Manifest は `/tmp` に一時的に生成し, `kubectl apply` 実行後に削除します。
- `kubectl` コマンドは `become: true` で実行するため, 対象ホストで sudo 実行が可能である必要があります。
- 既定では `cilium_shared_ca_kubeconfig: /etc/kubernetes/admin.conf` を参照し, コントロールプレーン上の管理者権限 kubeconfig を利用します。機密情報保持リソース(`Secret`) は etcd に保存され, すべてのコントロールプレーンへ同期されます。
- タスク全体に `run_once: true` を指定しているため, 実際に `kubectl apply` を実行するのは 1 ノードのみです。実行ノードを明示したい場合は `delegate_to: "{{ groups['k8s_ctrl_plane'][0] }}"` などを追加してください。
- 別の kubeconfig を利用したい場合は, `cilium_shared_ca_kubeconfig` を目的のパスに上書きしてください。
- `cilium_shared_ca_output_dir` と `cilium_shared_ca_cert_filename` / `cilium_shared_ca_key_filename` は自動生成時の保存先を指定する変数です。`*_path` を空文字にしている場合は, これらの組み合わせを自動で利用します。
- `cilium_shared_ca_cert_path` / `cilium_shared_ca_key_path` は既存ディレクトリや任意ファイル名をそのまま利用したい場合に設定します。これらを指定した場合, `output_dir` と `*_filename` の組み合わせより優先されます。
- `cilium_shared_ca_reuse_k8s_ca: false` かつ `cilium_shared_ca_auto_create: true` の場合, `openssl` で証明書と鍵を自動生成します。生成先は `cilium_shared_ca_output_dir` で, 既存ファイルがあれば上書きせずに利用します。自動生成を無効化したい場合は `cilium_shared_ca_auto_create: false` を指定してください。
- 先に `k8s-shared-ca` ロールを適用しておくと, 同じ証明書と鍵のパスがそのまま引き継がれるため, 追加設定なしで共通CAを再利用できます。

## トラブルシューティング (CA 不一致時)

1. 両クラスタで `cilium-ca` 機密情報保持リソース(`Secret`) が存在するかを確認します。

    ```bash
    kubectl --context <context> -n kube-system get secret cilium-ca
    ```

    機密情報保持リソース(`Secret`) が片側で欠落している場合は, 該当コントロールプレーンに対して `k8s-ctrl-plane` プレイブックを再実行し, `k8s-shared-ca` => `cilium-shared-ca` の順にロールを適用してください。

2. 機密情報保持リソース(`Secret`) が存在していても内容が一致しない場合は, `ca.crt` のハッシュを比較します。

    ```bash
    kubectl --context <context> -n kube-system get secret cilium-ca -o jsonpath='{.data.ca\.crt}' | base64 -d | sha256sum
    ```

    ハッシュが揃わない場合は, 一致していないクラスタ側で `kubectl delete secret cilium-ca` を実行した後に, `ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml --limit <hostname> -t k8s-shared-ca,cilium-shared-ca` を実行して 機密情報保持リソース(`Secret`) を再生成してください。

3. 機密情報保持リソース(`Secret`) を更新した後は, 両クラスタで Cilium DaemonSet を再起動し, 新しい CA を読み込ませます。

    ```bash
    kubectl --context <context> -n kube-system rollout restart ds cilium
    ```

4. `cilium clustermesh status` でクラスタ間接続を確認し, 全ノードが接続済みであれば復旧完了です。NodePort に関する警告が気になる場合は ServiceType を LoadBalancer などへ変更することも検討してください。

## 設定例

`vars/all-config.yml` で以下のように設定します。

```yaml
cilium_shared_ca_enabled: true
cilium_shared_ca_reuse_k8s_ca: true
```
