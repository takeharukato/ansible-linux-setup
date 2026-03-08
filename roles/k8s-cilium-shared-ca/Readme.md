# k8s-cilium-shared-ca ロール

Cilium Cluster Mesh で利用する `cilium-ca` は Kubernetes 上で機密情報を保持するリソース(`Secret`)です。このロールは共通認証局 (Certificate Authority) 証明書 (`CA`) ( 以下, 共通CA )を基に `cilium-ca` を生成して適用し, Cluster Mesh 間で共通CAを統一することで Transport Layer Security (`TLS`) ハンドシェイクの失敗や 機密情報保持リソース(`Secret`) の不一致を防ぎます。

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
| 名前空間 ( name space)  | - | Kubernetes内部でリソースを論理的に分離する単位。 |
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
| Serviceエンドポイント ( Service Endpoint ) | - | Serviceのバックエンドとして通信を受けるPod, または, 当該の通信を受けるPodに加え, 当該の通信を受けるPodへ通信を届けるためのネットワーク上の転送先情報全体を指す。 |
| Serviceエンドポイント情報 ( Service Endpoint Information ) | - | Serviceエンドポイントを特定して転送先を決めるための情報。主にバックエンドPodのIPアドレス, ポート番号, プロトコル, 所属クラスタ名(またはクラスタ識別子)で構成される。 |
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

## 前提条件

- Kubernetesクラスタが構築済みであること
  - kubeadm で初期化されたコントロールプレーンノードが存在する
  - `/etc/kubernetes/admin.conf` が配置され, kubectl で管理可能な状態
- kubectl コマンドが利用可能であること
  - コントロールプレーンノード上で `kubectl version --client` が成功する
- kubeconfigファイルへのアクセス権限があること
  - 既定では `/etc/kubernetes/admin.conf` を使用
  - cluster-admin 相当の権限が必要 (Secret の作成, 更新権限)
- 証明書生成に必要な openssl コマンドがインストール済みであること
  - CA自動生成機能 (`k8s_cilium_shared_ca_auto_create: true`) を利用する場合に必須
- sudo 権限が利用可能であること
  - Secret 適用時に `become: true` で実行するため
- Cilium が Kubernetes クラスタにインストール済み, またはインストール予定であること
  - 本ロールは Cilium が参照する Secret を準備するが, Cilium 本体のインストールは別途必要
- **k8s-shared-ca ロールとの依存関係**
  - `k8s_cilium_shared_ca_reuse_k8s_ca: true` を設定する場合, 事前に `k8s-shared-ca` ロールを適用する必要がある
  - k8s-shared-ca ロールが生成した共通CA (`k8s_shared_ca_cert_path`, `k8s_shared_ca_key_path`) を参照するため
  - k8s-shared-ca ロールを適用していない状態で `reuse_k8s_ca: true` にするとタスクが失敗する
  - 同一の共通CAを複数のKubernetesクラスタで共有する場合, 全クラスタで k8s-shared-ca ロールを先に適用してから本ロールを実行すること

## 実行方法

### Makefile を使用

```bash
make run_k8s_ctrl_plane
```

コントロールプレーンノード向けプレイブックを実行すると, 本ロールも含まれます。

### Ansible コマンド直接実行

```bash
# 全対象ホストに適用
ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml --tags k8s-cilium-shared-ca

# 特定ホストのみ適用
ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml --tags k8s-cilium-shared-ca --limit <hostname>
```

本ロールは通常, k8s-ctrl-plane プレイブックに含まれます。タグで絞り込み実行することで, 本ロール単独での適用も可能です。

## 実行フロー

本ロールは以下の順序で処理を実行します:

1. **パラメータ読み込み** (`load-params.yml`): OS 別パッケージ定義 (`vars/packages-ubuntu.yml`, `vars/packages-rhel.yml`) とクラスタ共通変数 (`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込みます。
2. **CA 証明書パス決定** (`config-cilium-ca.yml`): `k8s_cilium_shared_ca_reuse_k8s_ca` が `true` の場合は k8s-shared-ca ロールの共通CAパス (`k8s_shared_ca_cert_path`, `k8s_shared_ca_key_path`) を利用します。`false` の場合は `k8s_cilium_shared_ca_output_dir` と `*_filename` からパスを組み立てます。`k8s_cilium_shared_ca_auto_create: true` かつ CA ファイルが存在しない場合は, openssl で共通CAと秘密鍵を自動生成します。
3. **cilium-ca Secret 生成・適用** (`config-cilium-ca.yml`): 共通CAと秘密鍵をbase64エンコードし, `templates/cilium-ca-secret.yaml.j2` を使用して Secret Manifest を `/tmp` に一時生成します。`kubectl apply` で `kube-system/cilium-ca` Secret を作成, 更新します。Manifest ファイルは適用後に削除されます。
4. **Cluster Mesh TLS 証明書生成** (`clustermesh-ca.yml`): `k8s_cilium_clustermesh_secret_enabled: true` の場合のみ実行されます。`templates/cilium-clustermesh-openssl.cnf.j2` で OpenSSL 設定ファイルを生成し, `k8s_cilium_clustermesh_tls_san_dns` に指定された DNS 名を Subject Alternative Name (SAN) に埋め込みます。openssl を使用して共通CAで署名された TLS サーバ証明書と秘密鍵を生成します。
5. **cilium-clustermesh Secret 生成・適用** (`clustermesh-ca.yml`): 共通CA, TLS 証明書, TLS 秘密鍵をbase64エンコードし, `templates/cilium-clustermesh-secret.yaml.j2` を使用して Secret Manifest を `/tmp` に一時生成します。`kubectl apply` で `kube-system/cilium-clustermesh` Secret (`type: kubernetes.io/tls`) を作成, 更新します。Manifest ファイルは適用後に削除されます。
6. **パッケージインストール** (`package.yml`): 必要なパッケージをインストールします (該当する場合)。
7. **ディレクトリ作成** (`directory.yml`): 必要なディレクトリを作成します。
8. **サービス設定** (`service.yml`, `config.yml`): サービス関連の設定を行います (該当する場合)。

## 主要変数

### ロール制御変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_cilium_shared_ca_enabled` | `false` | このロールによる Secret作成を有効化します。|
| `k8s_cilium_shared_ca_reuse_k8s_ca` | `false` | `k8s-shared-ca` が配布した共通CAを再利用します。|
| `k8s_cilium_clustermesh_secret_enabled` | `true` | Cluster Mesh 用 Secret を生成するかどうかを制御します。|

### CA管理変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_cilium_shared_ca_output_dir` | `/etc/kubernetes/pki/cilium-shared-ca` | 証明書と鍵を自動生成する際の出力ディレクトリを指定します。|
| `k8s_cilium_shared_ca_cert_filename` | `cilium-ca.crt` | 自動生成する証明書のファイル名を指定します。|
| `k8s_cilium_shared_ca_key_filename` | `cilium-ca.key` | 自動生成する秘密鍵のファイル名を指定します。|
| `k8s_cilium_shared_ca_cert_path` | `""` | 既存の証明書ファイルをフルパスで指定する場合に設定します。|
| `k8s_cilium_shared_ca_key_path` | `""` | 既存の秘密鍵ファイルをフルパスで指定する場合に設定します。|
| `k8s_cilium_shared_ca_auto_create` | `true` | 共通CAファイルが存在しない場合に自動生成するかどうかを指定します。|
| `k8s_cilium_shared_ca_key_size` | `4096` | 自動生成する秘密鍵のビット長を指定します。|
| `k8s_cilium_shared_ca_valid_days` | `3650` | 自動生成する証明書の有効日数を指定します。|
| `k8s_cilium_shared_ca_digest` | `sha256` | 証明書生成時に使用するダイジェストアルゴリズムを指定します。|
| `k8s_cilium_shared_ca_subject` | `/CN=Cilium Cluster Mesh CA` | 自動生成する証明書のサブジェクトを指定します。|
| `cilium_shared_ca_kubeconfig` | `/etc/kubernetes/admin.conf` | Secret 適用時に利用する kubeconfig を指定します。|

### cilium-ca Secret設定変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_cilium_shared_ca_secret_name` | `cilium-ca` | 生成する Secret の名前を指定します。|
| `k8s_cilium_shared_ca_secret_namespace` | `kube-system` | Secret を配置する 名前空間 を指定します。|
| `k8s_cilium_shared_ca_secret_type` | `Opaque` | 作成する Secret の `type` を指定します。|
| `k8s_cilium_shared_ca_secret_cert_key` | `ca.crt` | Secret に格納する証明書データのキー名を指定します。|
| `k8s_cilium_shared_ca_secret_key_key` | `ca.key` | Secret に格納する秘密鍵データのキー名を指定します。|
| `k8s_cilium_shared_ca_secret_labels` | `{ "app.kubernetes.io/managed-by": "Helm" }` | Secret に対して Helm 管理ラベルを明示的に指定する変数です。|
| `k8s_cilium_shared_ca_secret_annotations` | `{ "meta.helm.sh/release-name": "cilium", "meta.helm.sh/release-namespace": "kube-system" }` | Secret に対して Helm 管理アノテーションを明示的に指定する変数です。|

### Cluster Mesh TLS設定変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_cilium_clustermesh_tls_cert_filename` | `cilium-clustermesh.crt` | 生成する Cluster Mesh TLS 証明書のファイル名を指定します。|
| `k8s_cilium_clustermesh_tls_key_filename` | `cilium-clustermesh.key` | 生成する Cluster Mesh TLS 秘密鍵のファイル名を指定します。|
| `k8s_cilium_clustermesh_tls_subject` | `/CN=clustermesh-apiserver` | Cluster Mesh 用 TLS 証明書のサブジェクトを指定します。|
| `k8s_cilium_clustermesh_tls_san_dns` | `["clustermesh-apiserver.kube-system.svc.cluster.local", "clustermesh-apiserver.kube-system.svc"]` | Subject Alternative Name (SAN) に追加する DNS 名リストを指定します。|
| `k8s_cilium_clustermesh_tls_valid_days` | `3650` | Cluster Mesh 用 TLS 証明書の有効日数を指定します。|
| `k8s_cilium_clustermesh_tls_key_size` | `4096` | Cluster Mesh TLS 秘密鍵のビット長を指定します。|

### cilium-clustermesh Secret設定変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_cilium_clustermesh_secret_name` | `cilium-clustermesh` | Cluster Mesh 用に生成する Secret の名前を指定します。|
| `k8s_cilium_clustermesh_secret_namespace` | `kube-system` | Cluster Mesh 用 Secret を配置する 名前空間 を指定します。|
| `k8s_cilium_clustermesh_secret_cert_key` | `ca.crt` | Cluster Mesh 用 Secret に格納する共通CAデータのキー名を指定します。|
| `k8s_cilium_clustermesh_secret_tls_cert_key` | `tls.crt` | Cluster Mesh 用 TLS サーバ証明書を格納するキー名を指定します。|
| `k8s_cilium_clustermesh_secret_tls_key_key` | `tls.key` | Cluster Mesh 用 TLS サーバ秘密鍵を格納するキー名を指定します。|
| `k8s_cilium_clustermesh_secret_labels` | `{ "app.kubernetes.io/managed-by": "Helm" }` | Cluster Mesh 用 Secret に付与する追加ラベルを指定します。|
| `k8s_cilium_clustermesh_secret_annotations` | `{ "meta.helm.sh/release-name": "cilium", "meta.helm.sh/release-namespace": "kube-system" }` | Cluster Mesh 用 Secret に付与する追加アノテーションを指定します。|

Cluster Mesh 用の Secret 生成は `k8s_cilium_clustermesh_secret_enabled` が有効な場合にのみ動作します。TLS サーバ証明書と秘密鍵は共通CAで署名され, Subject Alternative Name (SAN) へ `k8s_cilium_clustermesh_tls_san_dns` で指定した Service 名が埋め込まれます。Kubernetesクラスタ固有の Service 名を利用する場合は, このリストを変数で上書きしてください。

## デフォルト動作

| 条件 | 結果 |
| --- | --- |
| `cilium_shared_ca_kubeconfig` が空文字列または未定義 | CA証明書パス決定 (`config-cilium-ca.yml`) と Cluster Mesh TLS 証明書生成 (`clustermesh-ca.yml`) タスクはスキップされます。パッケージインストール, ディレクトリ作成, サービス設定タスクのみが実行されます。 |
| `k8s_cilium_shared_ca_enabled: false` | このロールは Secret を変更しません。何も実行されません。 |
| `k8s_cilium_shared_ca_enabled: true` かつ `k8s_cilium_shared_ca_reuse_k8s_ca: true` | k8s-shared-ca ロールが生成した共通CAを使用します。k8s-shared-ca ロールが未実行の場合はタスクが失敗します。 |
| `k8s_cilium_shared_ca_enabled: true` かつ `k8s_cilium_shared_ca_auto_create: true` | CA ファイルが存在しない場合, openssl で共通CAを自動生成します。既存ファイルがある場合は上書きせずに利用します。 |
| `k8s_cilium_shared_ca_enabled: true` かつ `k8s_cilium_shared_ca_auto_create: false` | CA ファイルが存在しない場合, タスクが失敗します。既存の CA ファイルを使用する前提で動作します。 |
| `k8s_cilium_clustermesh_secret_enabled: false` | Cluster Mesh 用 Secret は生成されません。cilium-ca Secret のみが作成, 更新されます。 |
| `k8s_cilium_clustermesh_secret_enabled: true` | Cluster Mesh 用 TLS 証明書を生成し, cilium-clustermesh Secret (`type: kubernetes.io/tls`) を作成, 更新します。 |
| `k8s_cilium_shared_ca_cert_path` / `k8s_cilium_shared_ca_key_path` が指定されている | これらのパスが優先され, `output_dir` と `*_filename` の組み合わせは無視されます。 |

## テンプレート・ファイル

本ロールでは以下のテンプレートを使用して Secret Manifest と OpenSSL 設定ファイルを生成します:

| テンプレートファイル名 | 用途 | 出力先 |
| --- | --- | --- |
| `cilium-ca-secret.yaml.j2` | cilium-ca Secret Manifest を生成します。`type: Opaque`, `data.ca.crt`, `data.ca.key` を含みます。 | `/tmp` に一時生成後, `kubectl apply` 実行後に削除 |
| `cilium-clustermesh-secret.yaml.j2` | cilium-clustermesh Secret Manifest を生成します。`type: kubernetes.io/tls`, `data.ca.crt`, `data.tls.crt`, `data.tls.key` を含みます。 | `/tmp` に一時生成後, `kubectl apply` 実行後に削除 |
| `cilium-clustermesh-openssl.cnf.j2` | Cluster Mesh TLS 証明書生成用の OpenSSL 設定ファイルを生成します。`k8s_cilium_clustermesh_tls_san_dns` の DNS 名を Subject Alternative Name (SAN) に埋め込みます。 | `k8s_cilium_shared_ca_output_dir` 配下に一時生成 |
| `dummy.j2` | ダミーテンプレートです (実際の処理では使用されません)。 | - |

**重要な注意事項**:
- Secret Manifest ファイルは一時的に `/tmp` に生成され, `kubectl apply` 実行後に直ちに削除されます。ディスク上に機密情報が残留しないよう配慮されています。
- OpenSSL 設定ファイル (`cilium-clustermesh-openssl.cnf.j2`) は証明書生成時に使用され, 生成後も `k8s_cilium_shared_ca_output_dir` 配下に保持されます。SAN の設定内容を確認する際に参照できます。

## 共通CAを流用する場合

`k8s_cilium_shared_ca_reuse_k8s_ca` を `true` に設定すると, 同一ホストで事前に実行した `k8s-shared-ca` ロールが展開した共通CA (`k8s_shared_ca_cert_path` / `k8s_shared_ca_key_path`) を利用します。これらの設定値が存在しない場合はタスクが失敗するため, `k8s_cilium_shared_ca_reuse_k8s_ca` を有効にする際は必ず `k8s-shared-ca` ロールを先に適用してください。

## Cilium Cluster Mesh 用の共通CAを自動生成する場合

`k8s_cilium_shared_ca_auto_create` を `true` に設定すると, Cilium Cluster Mesh 用の共通CAを自動生成します。

`k8s_cilium_shared_ca_output_dir` と `k8s_cilium_shared_ca_cert_filename` / `k8s_cilium_shared_ca_key_filename` で指定したファイルが存在しない場合のみ `openssl` を用いて証明書と鍵を生成します。指定したファイルが既に存在する場合は上書きせず, 共通CAと秘密鍵をそのまま利用します。
Cluster Mesh 用 Transport Layer Security (`TLS`) 証明書 (`k8s_cilium_clustermesh_secret_enabled: true` のとき) も同じ共通CAで署名され, Subject Alternative Name (`SAN`) に指定した Service 名を利用してクライアント検証が行われます。

`k8s_cilium_shared_ca_auto_create` を `false` に設定すると, ロールは `*_filename` で指定したファイルに対して書き込みを行わず, 既存ファイルが存在する前提で動作します。

`k8s_cilium_shared_ca_cert_path` / `k8s_cilium_shared_ca_key_path` を指定した場合は, `k8s_cilium_shared_ca_auto_create` の値に関わらずこれらのファイルを使用します。`*_filename` に指定したファイルが存在しない状態で `k8s_cilium_shared_ca_auto_create: false` として実行すると, 共通CAの入力が不足するためプレイブックはエラーで終了します。

## CA を明示的に指定する場合

独自に作成した CA を使用したい場合は, 証明書と鍵をあらかじめ `k8s_cilium_shared_ca_output_dir` に配置するか, `k8s_cilium_shared_ca_cert_path` / `k8s_cilium_shared_ca_key_path` にフルパスを設定してください。必要に応じて `k8s_cilium_shared_ca_auto_create` を `false` に切り替え, 共通CAを明示的に指定します。

## 機密情報保持リソース(`Secret`) 適用時の注意

- `k8s_cilium_shared_ca_enabled` が `false` の場合, このロールは 機密情報保持リソース(`Secret`) を変更しません。
- Manifest は `/tmp` に一時的に生成し, `kubectl apply` 実行後に削除します。
- `kubectl` コマンドは `become: true` で実行するため, 対象ホストで sudo 実行が可能である必要があります。
- 既定では `cilium_shared_ca_kubeconfig: /etc/kubernetes/admin.conf` を参照し, コントロールプレーン上の管理者権限 kubeconfig を利用します。機密情報保持リソース(`Secret`) は etcd に保存され, すべてのコントロールプレーンへ同期されます。
- 別の kubeconfig を利用したい場合は, `cilium_shared_ca_kubeconfig` を目的のパスに上書きしてください。
- `k8s_cilium_shared_ca_output_dir` と `k8s_cilium_shared_ca_cert_filename` / `k8s_cilium_shared_ca_key_filename` は自動生成時の保存先を指定する変数です。`*_path` を空文字にしている場合は, これらの組み合わせを自動で利用します。
- `k8s_cilium_shared_ca_cert_path` / `k8s_cilium_shared_ca_key_path` は既存ディレクトリや任意ファイル名をそのまま利用したい場合に設定します。これらを指定した場合, `output_dir` と `*_filename` の組み合わせより優先されます。
- `k8s_cilium_shared_ca_reuse_k8s_ca: false` かつ `k8s_cilium_shared_ca_auto_create: true` の場合, `openssl` で証明書と鍵を自動生成します。生成先は `k8s_cilium_shared_ca_output_dir` で, 既存ファイルがあれば上書きせずに利用します。自動生成を無効化したい場合は `k8s_cilium_shared_ca_auto_create: false` を指定してください。
- 先に `k8s-shared-ca` ロールを適用しておくと, 同じ証明書と鍵のパスがそのまま引き継がれるため, 追加設定なしで共通CAを再利用できます。
- Cluster Mesh 用 Secret は `kubectl -n kube-system get secret {{ k8s_cilium_clustermesh_secret_name }}` で存在を確認できます。`data.{{ k8s_cilium_clustermesh_secret_tls_cert_key }}`, `data.{{ k8s_cilium_clustermesh_secret_tls_key_key }}`, `data.{{ k8s_cilium_clustermesh_secret_cert_key }}` がすべて非空であることを検証してください。

## Cluster Mesh 用 TLS 資材

Cluster Mesh 向け Transport Layer Security (`TLS`) 資材は `k8s_cilium_shared_ca_output_dir` に保存されます。既定値 `/etc/kubernetes/pki/cilium-shared-ca` の配下には次のファイルが配置されます。

| ファイル名 | 生成元と用途 |
| --- | --- |
| `cilium-ca.crt` | 共通CAの証明書です。`k8s_cilium_shared_ca_reuse_k8s_ca` が `true` の場合は `k8s-shared-ca` ロールと同一ファイルを参照します。 |
| `cilium-ca.key` | 共通CAの秘密鍵です。既存ファイルがあれば上書きせずに流用します。 |
| `cilium-clustermesh.crt` | Cluster Mesh 用 Transport Layer Security (`TLS`) サーバ証明書です。`k8s_cilium_clustermesh_tls_san_dns` を Subject Alternative Name (`SAN`) に埋め込んだ状態で共通CAが署名します。 |
| `cilium-clustermesh.key` | Cluster Mesh 用 Transport Layer Security (`TLS`) サーバ秘密鍵です。`k8s_cilium_clustermesh_tls_key_size` で鍵長を制御します。 |
| `cilium-clustermesh.srl` | `openssl x509` の連番管理ファイルです。証明書を再発行するたびにシリアル番号が更新されます。 |

Cluster Mesh 用 Secret には既定で `app.kubernetes.io/managed-by: Helm` ラベルと `meta.helm.sh/*` アノテーションを付与しています。Helm が管理する `cilium` リリースに Secret を組み込む場合も, 追加の手動操作は不要です。

`k8s_cilium_clustermesh_secret_enabled: true` の場合, これらのファイルから読み込んだ base64 データを `cilium-clustermesh` 機密情報保持リソース(`Secret`) に格納します。Secret の内容を検証したい場合は, 次のコマンド例で展開すると証明書と秘密鍵を確認できます。

```bash
kubectl --context <context> -n kube-system get secret {{ k8s_cilium_clustermesh_secret_name }} \
    -o go-template='{{ range $k, $v := .data }}{{$k}}{{"\t"}}{{ $v | base64decode }}{{"\n"}}{{ end }}'
```

TLS 資材の再発行が必要な場合は, 対象ファイルを一時退避または削除したうえで `ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml --limit <hostname> -t k8s-cilium-shared-ca` を再実行してください。ロールは欠落している証明書や秘密鍵のみを生成し, 既存の共通CAを再利用します。証明書の SAN を変更したい場合は `k8s_cilium_clustermesh_tls_san_dns` を更新してから同じ手順で Secret を再生成します。

## 検証

### 検証方法の概要

本ロールでは以下の3つの主要な構成パターンがあり, それぞれで検証手順が異なります。各パターンで確認すべきポイントを以下に示します。

| 構成パターン | 設定変数 | 検証対象 |
| --- | --- | --- |
| パターン1: CA再利用構成 | `k8s_cilium_shared_ca_reuse_k8s_ca: true` | k8s-shared-ca ロールとの CA 共有状態, Secret 適用状態 |
| パターン2: 独立CA自動生成構成 | `k8s_cilium_shared_ca_auto_create: true` | 自動生成された CA ファイル, Secret 適用状態, Cluster Mesh TLS 証明書 |
| パターン3: Cluster Mesh無効化構成 | `k8s_cilium_clustermesh_secret_enabled: false` | cilium-ca Secret のみの適用状態, cilium-clustermesh Secret の非存在 |

### パターン1: CA再利用構成の検証

#### 設定例

```yaml
k8s_cilium_shared_ca_enabled: true
k8s_cilium_shared_ca_reuse_k8s_ca: true
k8s_cilium_clustermesh_secret_enabled: true
```

**前提条件**: `k8s-shared-ca` ロールが事前に実行され, k8s-shared-ca ロールの変数 `k8s_shared_ca_cert_path` と `k8s_shared_ca_key_path` が定義されている必要があります。

#### 手順1: k8s-shared-ca ロールの CA ファイル存在確認

本ロールが k8s-shared-ca ロールの CA を再利用する場合, 以下のファイルが存在することを確認します。

```bash
sudo ls -lh /etc/kubernetes/pki/k8s-shared-ca/
```

**期待される出力例**:

```
total 8.0K
-rw-r--r-- 1 root root 1.9K Dec  1 10:00 k8s-shared-ca.crt
-rw------- 1 root root 3.2K Dec  1 10:00 k8s-shared-ca.key
```

**確認ポイント**:
- `k8s-shared-ca.crt` と `k8s-shared-ca.key` が存在する
- `k8s-shared-ca.key` のパーミッションが `600` (root のみ読み取り可能)
- ファイルサイズが 0 バイトではない

#### 手順2: cilium-ca Secret の適用確認

```bash
kubectl -n kube-system get secret cilium-ca
```

**期待される出力例**:

```
NAME        TYPE     DATA   AGE
cilium-ca   Opaque   2      5m30s
```

**確認ポイント**:
- Secret の `TYPE` が `Opaque`
- `DATA` が `2` (ca.crt と ca.key の2つのキー)
- エラーメッセージが表示されない

#### 手順3: cilium-ca Secret の内容確認

```bash
kubectl -n kube-system get secret cilium-ca -o yaml
```

**期待される出力例**:

```yaml
apiVersion: v1
kind: Secret
metadata:
  annotations:
    meta.helm.sh/release-name: cilium
    meta.helm.sh/release-namespace: kube-system
  creationTimestamp: "2024-12-01T10:00:00Z"
  labels:
    app.kubernetes.io/managed-by: Helm
  name: cilium-ca
  namespace: kube-system
  resourceVersion: "12345"
  uid: abcd1234-5678-90ef-ghij-klmnopqrstuv
type: Opaque
data:
  ca.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUZhekNDQTFP...
  ca.key: LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlKS0FJ...
```

**確認ポイント**:
- `labels` に `app.kubernetes.io/managed-by: Helm` が存在する
- `annotations` に `meta.helm.sh/release-name` と `meta.helm.sh/release-namespace` が存在する
- `data.ca.crt` と `data.ca.key` が両方とも base64 エンコードされた値を持つ
- `data.ca.crt` が k8s-shared-ca ロールの CA 証明書と一致する (次のステップで確認)

#### 手順4: Secret の CA と k8s-shared-ca の CA の一致確認

```bash
# Secret から CA 証明書を抽出してハッシュを計算
kubectl -n kube-system get secret cilium-ca -o jsonpath='{.data.ca\.crt}' | base64 -d | sha256sum

# k8s-shared-ca から CA 証明書のハッシュを計算
sudo cat /etc/kubernetes/pki/k8s-shared-ca/k8s-shared-ca.crt | sha256sum
```

**期待される出力例**:

```
# Secret からの出力
a1b2c3d4e5f6789012345678901234567890123456789012345678901234  -

# k8s-shared-ca からの出力
a1b2c3d4e5f6789012345678901234567890123456789012345678901234  -
```

**確認ポイント**:
- 両方のハッシュが完全に一致する
- ハッシュが異なる場合は, CA の再利用が正しく機能していない

#### 手順5: cilium-clustermesh Secret の適用確認

`k8s_cilium_clustermesh_secret_enabled: true` の場合, Cluster Mesh 用 Secret も作成されます。

```bash
kubectl -n kube-system get secret cilium-clustermesh
```

**期待される出力例**:

```
NAME                TYPE                DATA   AGE
cilium-clustermesh  kubernetes.io/tls   3      5m30s
```

**確認ポイント**:
- Secret の `TYPE` が `kubernetes.io/tls`
- `DATA` が `3` (ca.crt, tls.crt, tls.key の3つのキー)
- エラーメッセージが表示されない

#### 手順6: cilium-clustermesh Secret の内容確認

```bash
kubectl -n kube-system get secret cilium-clustermesh -o jsonpath='{.data}'
```

**期待される出力例**:

```json
{"ca.crt":"LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUZh...","tls.crt":"LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUZk...","tls.key":"LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlK..."}
```

**確認ポイント**:
- `ca.crt`, `tls.crt`, `tls.key` の3つのキーがすべて存在する
- 各キーの値が空文字列 (`""`) ではなく, base64 エンコードされた証明書データを含む
- `ca.crt` が cilium-ca Secret の `ca.crt` と一致する (次のステップで確認)

#### 手順7: Cluster Mesh TLS 証明書の CA 一致確認

```bash
# cilium-clustermesh Secret の CA 証明書ハッシュ
kubectl -n kube-system get secret cilium-clustermesh -o jsonpath='{.data.ca\.crt}' | base64 -d | sha256sum

# cilium-ca Secret の CA 証明書ハッシュ
kubectl -n kube-system get secret cilium-ca -o jsonpath='{.data.ca\.crt}' | base64 -d | sha256sum
```

**期待される出力例**:

```
# cilium-clustermesh からの出力
a1b2c3d4e5f6789012345678901234567890123456789012345678901234  -

# cilium-ca からの出力
a1b2c3d4e5f6789012345678901234567890123456789012345678901234  -
```

**確認ポイント**:
- 両方のハッシュが完全に一致する
- Cluster Mesh TLS 証明書が正しい CA で署名されている

#### 手順8: Cluster Mesh TLS 証明書の SAN 確認

Subject Alternative Name (SAN) に期待する DNS 名が含まれているか確認します。

```bash
kubectl -n kube-system get secret cilium-clustermesh \
  -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -text | grep -A 2 "Subject Alternative Name"
```

**期待される出力例**:

```
            X509v3 Subject Alternative Name:
                DNS:clustermesh-apiserver.kube-system.svc.cluster.local, DNS:clustermesh-apiserver.kube-system.svc
```

**確認ポイント**:
- `k8s_cilium_clustermesh_tls_san_dns` で指定した DNS 名がすべて含まれている
- DNS 名が正しい Service 名と一致している
- SAN が欠落している場合は, `k8s_cilium_clustermesh_tls_san_dns` を確認してから Secret を再生成する

### パターン2: 独立CA自動生成構成の検証

#### 設定例

```yaml
k8s_cilium_shared_ca_enabled: true
k8s_cilium_shared_ca_reuse_k8s_ca: false
k8s_cilium_shared_ca_auto_create: true
k8s_cilium_clustermesh_secret_enabled: true
```

**前提条件**: `k8s-shared-ca` ロールに依存せず, 本ロール独自の CA を自動生成します。

#### 手順1: 自動生成された CA ファイルの存在確認

```bash
sudo ls -lh /etc/kubernetes/pki/cilium-shared-ca/
```

**期待される出力例**:

```
total 20K
-rw-r--r-- 1 root root 2.0K Dec  1 10:05 cilium-ca.crt
-rw------- 1 root root 3.2K Dec  1 10:05 cilium-ca.key
-rw-r--r-- 1 root root 2.1K Dec  1 10:05 cilium-clustermesh.crt
-rw------- 1 root root 3.2K Dec  1 10:05 cilium-clustermesh.key
-rw-r--r-- 1 root root   41 Dec  1 10:05 cilium-clustermesh.srl
```

**確認ポイント**:
- `cilium-ca.crt` と `cilium-ca.key` が存在する (共通CA)
- `cilium-clustermesh.crt` と `cilium-clustermesh.key` が存在する (Cluster Mesh TLS 証明書と秘密鍵)
- `cilium-clustermesh.srl` が存在する (openssl の連番管理ファイル)
- 秘密鍵ファイルのパーミッションが `600`
- すべてのファイルサイズが 0 バイトではない

#### 手順2: CA 証明書の内容確認

```bash
sudo openssl x509 -in /etc/kubernetes/pki/cilium-shared-ca/cilium-ca.crt -noout -text
```

**期待される出力例**:

```
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number:
            3a:2f:9e:87:d1:4c:5b:22:a3:b4:7e:65:8f:3d:12:45
        Signature Algorithm: sha256WithRSAEncryption
        Issuer: CN = Cilium Cluster Mesh CA
        Validity
            Not Before: Dec  1 10:05:00 2024 GMT
            Not After : Nov 28 10:05:00 2034 GMT
        Subject: CN = Cilium Cluster Mesh CA
        Subject Public Key Info:
            Public Key Algorithm: rsaEncryption
                RSA Public-Key: (4096 bit)
                Modulus:
                    00:ab:cd:...
                Exponent: 65537 (0x10001)
        X509v3 extensions:
            X509v3 Basic Constraints: critical
                CA:TRUE
            X509v3 Key Usage: critical
                Certificate Sign, CRL Sign
    Signature Algorithm: sha256WithRSAEncryption
         12:34:56:...
```

**確認ポイント**:
- `Issuer` と `Subject` が `CN = Cilium Cluster Mesh CA` (または `k8s_cilium_shared_ca_subject` で指定した値)
- `Validity` の `Not After` が `k8s_cilium_shared_ca_valid_days` で指定した日数後 (既定値: 3650日 = 10年)
- `RSA Public-Key` が `k8s_cilium_shared_ca_key_size` で指定したビット長 (既定値: 4096 bit)
- `X509v3 Basic Constraints` に `CA:TRUE` が含まれる
- `X509v3 Key Usage` に `Certificate Sign, CRL Sign` が含まれる

#### 手順3: Cluster Mesh TLS 証明書の署名確認

```bash
sudo openssl verify -CAfile /etc/kubernetes/pki/cilium-shared-ca/cilium-ca.crt \
  /etc/kubernetes/pki/cilium-shared-ca/cilium-clustermesh.crt
```

**期待される出力例**:

```
/etc/kubernetes/pki/cilium-shared-ca/cilium-clustermesh.crt: OK
```

**確認ポイント**:
- 出力が `OK` である
- エラーメッセージが表示されない
- 証明書が正しい CA で署名されている

#### 手順4: Cluster Mesh TLS 証明書の SAN 確認

```bash
sudo openssl x509 -in /etc/kubernetes/pki/cilium-shared-ca/cilium-clustermesh.crt \
  -noout -text | grep -A 2 "Subject Alternative Name"
```

**期待される出力例**:

```
            X509v3 Subject Alternative Name:
                DNS:clustermesh-apiserver.kube-system.svc.cluster.local, DNS:clustermesh-apiserver.kube-system.svc
```

**確認ポイント**:
- `k8s_cilium_clustermesh_tls_san_dns` で指定した DNS 名がすべて含まれている
- DNS 名が正しい Service 名と一致している

#### 手順5: cilium-ca Secret の適用確認

パターン1の手順2〜4と同じ手順で確認します。

```bash
kubectl -n kube-system get secret cilium-ca
kubectl -n kube-system get secret cilium-ca -o yaml
```

**確認ポイント**:
- Secret が正しく作成されている
- `data.ca.crt` がローカルファイル `/etc/kubernetes/pki/cilium-shared-ca/cilium-ca.crt` と一致する

#### 手順6: cilium-clustermesh Secret の適用確認

パターン1の手順5〜7と同じ手順で確認します。

```bash
kubectl -n kube-system get secret cilium-clustermesh
kubectl -n kube-system get secret cilium-clustermesh -o jsonpath='{.data}'
```

**確認ポイント**:
- Secret が正しく作成されている
- `data.tls.crt` がローカルファイル `/etc/kubernetes/pki/cilium-shared-ca/cilium-clustermesh.crt` と一致する

### パターン3: Cluster Mesh無効化構成の検証

#### 設定例

```yaml
k8s_cilium_shared_ca_enabled: true
k8s_cilium_shared_ca_reuse_k8s_ca: false
k8s_cilium_shared_ca_auto_create: true
k8s_cilium_clustermesh_secret_enabled: false
```

**前提条件**: Cluster Mesh 機能を使用しない場合は, `k8s_cilium_clustermesh_secret_enabled: false` を設定します。

#### 手順1: cilium-ca Secret の適用確認

パターン1の手順2〜4またはパターン2の手順5と同じ手順で確認します。

```bash
kubectl -n kube-system get secret cilium-ca
```

**確認ポイント**:
- cilium-ca Secret が正しく作成されている
- `TYPE` が `Opaque`, `DATA` が `2`

#### 手順2: cilium-clustermesh Secret の非存在確認

```bash
kubectl -n kube-system get secret cilium-clustermesh
```

**期待される出力例**:

```
Error from server (NotFound): secrets "cilium-clustermesh" not found
```

**確認ポイント**:
- `Error from server (NotFound)` が表示される
- Secret が存在しない
- `k8s_cilium_clustermesh_secret_enabled: false` が正しく機能している

#### 手順3: ローカル CA ファイルの存在確認

```bash
sudo ls -lh /etc/kubernetes/pki/cilium-shared-ca/
```

**期待される出力例**:

```
total 8.0K
-rw-r--r-- 1 root root 2.0K Dec  1 10:10 cilium-ca.crt
-rw------- 1 root root 3.2K Dec  1 10:10 cilium-ca.key
```

**確認ポイント**:
- `cilium-ca.crt` と `cilium-ca.key` のみが存在する
- `cilium-clustermesh.crt`, `cilium-clustermesh.key`, `cilium-clustermesh.srl` などの Cluster Mesh 関連ファイルが存在しない
- `k8s_cilium_clustermesh_secret_enabled: false` の場合は Cluster Mesh TLS 資材が生成されない

## トラブルシューティング (CA 不一致時)

1. 両Kubernetesクラスタで `cilium-ca` 機密情報保持リソース(`Secret`) が存在するかを確認します。

    ```bash
    kubectl --context <context> -n kube-system get secret cilium-ca
    ```

    機密情報保持リソース(`Secret`) が片側で欠落している場合は, 該当コントロールプレーンノードに対して `k8s-ctrl-plane` プレイブックを再実行し, `k8s-shared-ca` => `k8s-cilium-shared-ca` の順にロールを適用してください。

2. 機密情報保持リソース(`Secret`) が存在していても内容が一致しない場合は, `ca.crt` のハッシュを比較します。

    ```bash
    kubectl --context <context> -n kube-system get secret cilium-ca -o jsonpath='{.data.ca\.crt}' | base64 -d | sha256sum
    ```

    ハッシュが揃わない場合は, 一致していないKubernetesクラスタ側で `kubectl delete secret cilium-ca` を実行した後に, `ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml --limit <hostname> -t k8s-shared-ca,k8s-cilium-shared-ca` を実行して 機密情報保持リソース(`Secret`) を再生成してください。

3. 機密情報保持リソース(`Secret`) を更新した後は, 両Kubernetesクラスタで Cilium DaemonSet を再起動し, 新しい CA を読み込ませます。

    ```bash
    kubectl --context <context> -n kube-system rollout restart ds cilium
    ```

4. `cilium clustermesh status` でKubernetesクラスタ間接続を確認し, 全Kubernetes ノードが接続済みであれば復旧完了です。NodePort に関する警告が気になる場合は ServiceType を LoadBalancer などへ変更することも検討してください。

5. Cluster Mesh 用 Secret (`k8s_cilium_clustermesh_secret_enabled: true`) を更新した場合は, `cilium-clustermesh` 機密情報保持リソース(`Secret`) の内容を確認します。

    ```bash
    kubectl --context <context> -n kube-system get secret cilium-clustermesh -o jsonpath='{.data.{{ k8s_cilium_clustermesh_secret_tls_cert_key }}{"\n"}}{.data.{{ k8s_cilium_clustermesh_secret_tls_key_key }}{"\n"}}{.data.{{ k8s_cilium_clustermesh_secret_cert_key }}{"\n"}}'
    ```

    各キーの値が空 (`""`) の場合は Secret が正しく適用されていないため, `ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml --limit <hostname> -t k8s-cilium-shared-ca` を再実行して Cluster Mesh 用 TLS 資材を再生成してください。

6. Cluster Mesh 接続が確立しない場合は, `cilium clustermesh connectivity test` を実行して TLS 証明書検証エラーや Service 名の不一致などを確認します。Subject Alternative Name (`SAN`) の DNS 名がKubernetesクラスタの Service 名と一致しない場合は, `k8s_cilium_clustermesh_tls_san_dns` を調整した上で再度 Secret の再生成を実施してください。

## 留意事項

### セキュリティに関する留意事項

#### CA秘密鍵の保護

共通CAの秘密鍵 (`cilium-ca.key`) およびCluster Mesh TLS秘密鍵 (`cilium-clustermesh.key`) は, Cluster Mesh全体のセキュリティの根幹となる重要な資産です。必要に応じて, 以下の対策を実施してください。

- **ファイルパーミッションの厳格化**: 秘密鍵ファイルのパーミッションは `600` (rootのみ読み取り可能) に設定し, 不正アクセスを防止します。本ロールは自動的にこの設定を行いますが, 手動でファイルを配置する場合は必ず確認してください。
- **不要なコピーの削除**: 実運用環境など, セキュリティが重視される場合, 秘密鍵をバックアップする際は暗号化して保管し, 平文のコピーは削除することが推奨されます。共通CAを複製して配布する場合も, 秘密鍵は必要最小限のホストにのみ配置してください。
- **アクセスログの監視**: 実運用環境など, セキュリティが重視される場合, 秘密鍵ファイルへのアクセスログを監視し, 不正な読み取り試行を検出する作業を運用に組み入れることが推奨されます (auditdやAIDEなどのツールを活用)。

#### kubeconfigファイルのアクセス制限

本ロールはkubectlを使用してSecretをKubernetesクラスタに適用するため, `cilium_shared_ca_kubeconfig` で指定したkubeconfigファイルに適切なアクセス制限を実施してください。

実運用環境など, セキュリティが重視される場合, 以下の運用が推奨されます:

- **パーミッションの確認**: kubeconfigファイルのパーミッションは `600` または `640` に設定し, 不要なユーザからのアクセスを防止します。
- **認証情報の保護**: kubeconfigに含まれるクライアント証明書や認証トークンも機密情報です。ファイルの内容が平文で保管される場合は, ディスク暗号化やSecure Boot等の追加対策を検討してください。
- **最小権限の原則**: kubeconfigが持つ権限は, Secretの作成と更新に必要な最小限に留めます。可能であれば, 名前空間 `kube-system` への `secrets` リソースに対する `get`, `create`, `update`, `patch` 権限のみを持つServiceAccountを作成し, 専用のkubeconfigを使用することを推奨します。

#### Secretのetcd暗号化

KubernetesのSecretはデフォルトではetcdに平文で保存されます。実運用環境など, セキュリティが重視される場合, Cluster MeshのCA秘密鍵やTLS秘密鍵が含まれるSecretを保護するため, etcdの暗号化を有効化することを推奨します。

- **Encryption at Restの設定**: Kubernetes 1.13以降ではEncryption Configuration機能を使用してetcd内のSecretを暗号化できます。`EncryptionConfiguration` リソースを作成し, kube-apiserverの `--encryption-provider-config` フラグで指定してください。
- **暗号化キーの管理**: 暗号化に使用するキーはKMS (Key Management Service) やHardware Security Module (HSM) で管理することを推奨します。
- **定期的なキーローテーション**: 暗号化キーを定期的にローテーションし, 万が一の漏洩時の影響を最小化します。

### 運用上の留意事項

#### CA更新時の影響範囲

共通CA証明書 (`cilium-ca.crt`) を更新する場合, **Cluster Mesh全体に影響が及びます**。以下の手順を慎重に実施してください。

1. **計画的な更新**: CA証明書の有効期限が切れる前に, 十分な時間的余裕を持って更新計画を立てます。既定値は10年 (`k8s_cilium_shared_ca_valid_days: 3650`) ですが, 実運用環境など, セキュリティが重視される場合, より短い期間で定期的に更新することも検討してください。
2. **全Kubernetesクラスタへの同時適用**: CA証明書を更新する際は, Cluster Meshに参加する全Kubernetesクラスタで同時に新しいCAを適用します。一部のKubernetesクラスタだけが古いCAを使用している状態では, Kubernetesクラスタ間のTLS検証が失敗し, Cluster Mesh接続が切断されます。
3. **Cilium Podの再起動**: CA証明書を更新した後は, 全Kubernetesクラスタで `kubectl -n kube-system rollout restart ds cilium` を実行し, Cilium DaemonSetを再起動します。これにより, 新しいCA証明書がメモリに読み込まれます。
4. **接続状態の確認**: `cilium clustermesh status` でKubernetesクラスタ間接続が正常に復旧したことを確認します。接続エラーが発生した場合は, すべてのKubernetesクラスタでCA証明書のハッシュが一致しているかを確認してください。

#### Secretの手動削除に関する留意事項

`cilium-ca` および `cilium-clustermesh` Secretを手動で削除すると, Cilium がCA証明書やTLS証明書を読み込めなくなり, Cluster Mesh接続が切断されます。Secret を再生成する場合は, 以下の手順を推奨します。

1. **Ansible経由の再適用**: `kubectl delete secret` を実行せず, `ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml --limit <hostname> -t k8s-cilium-shared-ca` を実行します。本ロールは既存のSecretを検出して更新 (`kubectl apply`) するため, ダウンタイムを最小化できます。
2. **やむを得ず削除する場合**: Secretを削除した場合は, 直ちにAnsibleプレイブックを再実行してSecretを再作成します。削除から再作成までの間, CiliumはCA証明書を読み込めないため, Cluster Mesh接続が一時的に切断されます。
3. **バックアップの取得**: Secret削除前に `kubectl get secret cilium-ca -o yaml > cilium-ca-backup.yaml` でバックアップを取得しておくと, 誤削除時に迅速に復旧できます。

#### Cilium Podの再起動

CA証明書やTLS証明書を更新した後は, **必ずCilium Podを再起動**してください。Cilium は起動時にSecretを読み込んでメモリにキャッシュするため, Secretを更新しただけではPodに反映されません。

```bash
kubectl -n kube-system rollout restart ds cilium
```

- **全Kubernetesクラスタで実行**: Cluster Meshに参加する全Kubernetesクラスタで再起動を実行します。
- **ローリングアップデート**: DaemonSetのローリングアップデートにより, ノード単位で順次Podが再起動されます。全Podの再起動完了までに数分かかる場合があります。
- **ステータス確認**: `kubectl -n kube-system rollout status ds cilium` で再起動の進行状況を確認できます。

#### 証明書有効期限の監視

共通CAおよびCluster Mesh TLS証明書の有効期限を監視し, 期限切れ前に更新します。既定値では以下の有効期限が設定されています。

- 共通CA: 10年 (`k8s_cilium_shared_ca_valid_days: 3650`)
- Cluster Mesh TLS証明書: 10年 (`k8s_cilium_clustermesh_tls_valid_days: 3650`)

以下の方法で有効期限を確認できます。

```bash
# 共通CA証明書の有効期限確認
sudo openssl x509 -in /etc/kubernetes/pki/cilium-shared-ca/cilium-ca.crt \
  -noout -enddate

# Cluster Mesh TLS証明書の有効期限確認
sudo openssl x509 -in /etc/kubernetes/pki/cilium-shared-ca/cilium-clustermesh.crt \
  -noout -enddate
```

実運用環境など, セキュリティが重視される場合の推奨事項を以下に示します:

- **定期的な確認**: 四半期ごとに証明書の有効期限を確認します。
- **自動監視**: Prometheus + Alertmanager や cert-manager など監視ツールを導入し, 有効期限が近づいたら自動でアラートを発報するようにします。
- **更新猶予期間**: 有効期限の6ヶ月前から更新作業を開始し, 十分な検証期間を確保します。

## 設定例

### 設定例1: 基本設定 (k8s-shared-ca再利用)

`vars/all-config.yml` で以下のように設定します。`k8s-shared-ca` ロールが生成した共通CAを再利用し, Cluster Mesh用Secretまで適用する最小限の構成です。

```yaml
k8s_cilium_shared_ca_enabled: true
k8s_cilium_shared_ca_reuse_k8s_ca: true
k8s_cilium_clustermesh_secret_enabled: true
```

**適用条件**:
- `k8s-shared-ca` ロールが事前に実行済みである
- `k8s_shared_ca_cert_path` および `k8s_shared_ca_key_path` が定義されている

**動作**:
- `k8s-shared-ca` ロールが配置した共通CAファイルを読み込む
- `cilium-ca` Secret (`type: Opaque`) を作成または更新
- Cluster Mesh TLS証明書を自動生成 (共通CAで署名)
- `cilium-clustermesh` Secret (`type: kubernetes.io/tls`) を作成または更新

### 設定例2: 独立CA自動生成設定

`k8s-shared-ca` ロールに依存せず, 本ロール独自の共通CAを自動生成する構成です。

```yaml
k8s_cilium_shared_ca_enabled: true
k8s_cilium_shared_ca_reuse_k8s_ca: false
k8s_cilium_shared_ca_auto_create: true
k8s_cilium_shared_ca_output_dir: "/etc/kubernetes/pki/cilium-shared-ca"
k8s_cilium_shared_ca_key_size: 4096
k8s_cilium_shared_ca_valid_days: 3650
k8s_cilium_clustermesh_secret_enabled: true
```

**適用条件**:
- openssl コマンドが利用可能である
- `k8s_cilium_shared_ca_output_dir` に書き込み権限がある

**動作**:
- `k8s_cilium_shared_ca_output_dir` 配下に共通CAファイルを自動生成 (既存ファイルがあれば上書きせず再利用)
- `cilium-ca` Secret を作成または更新
- Cluster Mesh TLS証明書を自動生成
- `cilium-clustermesh` Secret を作成または更新

### 設定例3: 既存CA指定設定

既に作成済みのCA証明書と秘密鍵を明示的に指定する構成です。

```yaml
k8s_cilium_shared_ca_enabled: true
k8s_cilium_shared_ca_reuse_k8s_ca: false
k8s_cilium_shared_ca_auto_create: false
k8s_cilium_shared_ca_cert_path: "/path/to/custom/ca.crt"
k8s_cilium_shared_ca_key_path: "/path/to/custom/ca.key"
k8s_cilium_clustermesh_secret_enabled: true
```

**適用条件**:
- 指定したパスにCA証明書と秘密鍵が存在する
- 秘密鍵ファイルに読み取り権限がある

**動作**:
- 指定したCA証明書と秘密鍵を使用 (自動生成は実行されない)
- `cilium-ca` Secret を作成または更新
- 指定したCAでCluster Mesh TLS証明書を署名
- `cilium-clustermesh` Secret を作成または更新

### 設定例4: Cluster Mesh無効化設定

Cluster Mesh機能を使用せず, `cilium-ca` Secretのみを作成する構成です。

```yaml
k8s_cilium_shared_ca_enabled: true
k8s_cilium_shared_ca_reuse_k8s_ca: true
k8s_cilium_clustermesh_secret_enabled: false
```

**適用条件**:
- `k8s-shared-ca` ロールが事前に実行済みである (または独自のCA指定)

**動作**:
- 共通CAを読み込む (reuse_k8s_caがtrueの場合はk8s-shared-caから, falseの場合は自動生成または明示的指定)
- `cilium-ca` Secret のみを作成または更新
- Cluster Mesh TLS証明書は生成されない
- `cilium-clustermesh` Secret は作成されない

### 設定例5: カスタムSAN設定

Kubernetesクラスタごとに異なる Service ドメイン名を使用する場合の構成例です。

```yaml
k8s_cilium_shared_ca_enabled: true
k8s_cilium_shared_ca_reuse_k8s_ca: true
k8s_cilium_clustermesh_secret_enabled: true
k8s_cilium_clustermesh_tls_san_dns:
  - "clustermesh-apiserver.cilium.svc.cluster.local"
  - "clustermesh-apiserver.cilium.svc"
  - "custom-domain.example.org"
```

**適用条件**:
- Cluster Mesh APIServerが既定の `kube-system` 名前空間以外にデプロイされている
- カスタムドメイン名でCluster Mesh APIServerにアクセスする必要がある

**動作**:
- 指定したDNS名をSubject Alternative Name (SAN) に含むTLS証明書を生成
- クライアント側のTLS検証で, リスト内のいずれかのドメイン名にマッチすれば接続を許可
