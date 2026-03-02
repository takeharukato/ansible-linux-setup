# k8s-hubble-ui ロール

Cilium Hubble UI を Kubernetes クラスタに導入するロールです。Hubble UI は Cilium が提供する可観測性機能 (Observability) の Web UI であり, クラスタ内のネットワークフローやサービス依存関係をグラフィカルに可視化します。このロールは既存の Cilium Helm リリースを `helm upgrade --install` でアップグレードし, `hubble.ui.enabled: true` を適用することで Hubble UI コンポーネントを有効化します。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Application Programming Interface | API | アプリケーション同士がやり取りする方法を定めた仕様。 |
| Custom Resource Definition | CRD | Kubernetes APIを拡張してユーザ独自のリソース種別を定義する仕組み。 |
| Role-Based Access Control | RBAC | ユーザやサービスアカウントが実行可能な操作を役割(Role)で制限する仕組み。 |
| Service Account | - | Kubernetes内部でPodが他のリソースにアクセスする際に用いる仮想的なアカウント。 |
| ClusterRole | - | クラスタ全体に適用される権限の集合。 |
| ClusterRoleBinding | - | ClusterRoleをユーザやサービスアカウントに紐付ける仕組み。 |
| Role | - | 特定の名前空間内で有効な権限の集合。 |
| RoleBinding | - | Roleをユーザやサービスアカウントに紐付ける仕組み。 |
| Namespace | - | Kubernetes内部でリソースを論理的に分離する単位。 |
| Pod | - | Kubernetes上で動作するコンテナの最小単位。 |
| レプリカ ( Replica ) | - | Podの複製。DeploymentなどのリソースがPodの高可用性や負荷分散のために複数のレプリカを作成, 管理する。指定されたレプリカ数に基づいて同一の仕様を持つPodが複数実行される。 |
| DaemonSet | - | クラスタ内の全ノード(または指定した一部のノード)で必ずPodを1つずつ起動させるリソース。 |
| Deployment | - | 指定した数のPodを維持し, ローリングアップデート等を管理するリソース。 |
| StatefulSet | - | 状態を持つアプリケーションのPodを順序付けて管理するリソース。 |
| Service | - | Podへのアクセスを抽象化し, 負荷分散やサービスディスカバリを提供するリソース。 |
| Ingress | - | クラスタ外部からHTTP/HTTPS通信を受け付け, 内部のServiceへルーティングする仕組み。 |
| ConfigMap | - | 設定情報を保持し, Podへ環境変数やファイルとして注入するリソース。 |
| Secret | - | 機密情報を保持し, Podへ安全に注入するリソース。 |
| PersistentVolume | PV | クラスタ内で利用可能なストレージリソースを表すオブジェクト。 |
| PersistentVolumeClaim | PVC | ユーザがPVを要求する際に利用するリソース。 |
| StorageClass | - | 動的にPVをプロビジョニングする際のストレージ種別を定義するリソース。 |
| Node | - | Kubernetesクラスタを構成する物理マシンまたは仮想マシン。 |
| Control Plane | - | クラスタ全体を管理, 制御する中枢ノード群。kube-apiserver, kube-controller-manager, kube-schedulerなどが動作する。 |
| Worker Node | - | 実際にアプリケーションのPodを実行するノード。 |
| kube-apiserver | - | KubernetesのAPIリクエストを受け付け, etcdへの読み書きを仲介するコンポーネント。 |
| kube-controller-manager | - | Deployment, ReplicaSetなど各種コントローラを実行し, クラスタの状態を監視, 調整するコンポーネント。 |
| kube-scheduler | - | 新規作成されたPodを適切なNodeへ配置するコンポーネント。 |
| kubelet | - | 各Node上で動作し, Podの起動, 停止, 監視を行うエージェント。 |
| kube-proxy | - | 各Node上でServiceのネットワークルールを管理するコンポーネント。 |
| etcd | - | Kubernetesのクラスタ状態を保存する分散Key-Valueストア。 |
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
| Taint | - | Nodeに設定する特殊なマークで, 特定の条件を満たさないPodの配置を拒否する。 |
| Toleration | - | PodがTaintを持つNodeへ配置されることを許可する設定。 |

## 前提条件

- Kubernetes Kubernetesクラスタが稼働していること
- Cilium が Helm 経由でインストール済みであること (`k8s-ctrlplane` ロール実行済み)
- **Hubble Relay が有効化されている必要があります**
  - Hubble Relay が無効な場合, 以下の警告メッセージが表示されます:
    - `WARNING: Hubble Relay is not enabled. Hubble UI requires Hubble Relay to function properly.`
  - Cilium インストール時に `hubble.relay.enabled: true` が設定されていることを確認してください
- `kubectl` および `helm` コマンドが利用可能であること
- `yq` コマンドが利用可能であること (マージ機能使用時)

## 実行フロー

1. `load-params.yml` で変数を読み込みます。
2. `config.yml` で以下を実行します:
   - kube-apiserverの起動を待機
   - Cilium CRD の存在確認 (最大 30 回リトライ, 10 秒間隔)
   - Hubble Relay Deployment の存在確認 (無効な場合は警告表示)
   - Hubble UI 用 Helm values ファイルを生成 (`{{ k8s_cilium_config_dir }}/hubble-ui-values.yml`)
   - `hubble_ui_merge_existing_values: true` の場合, 既存 Helm values を取得してマージ
   - `helm upgrade --install` で Cilium をアップグレード
   - Hubble UI Deployment の起動を確認 (`kubectl wait`)

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_api_wait_host` | "{{ k8s_ctrlplane_endpoint }}" | kube-apiserverの待ち合わせ先(接続先)ホスト名/IPアドレス。|
| `k8s_api_wait_port` | "{{ k8s_ctrlplane_port }}" | kube-apiserverの待ち合わせ先ポート番号。 (規定: `6443`)|
| `k8s_api_wait_timeout` | `600` | kube-apiserver待ち合わせ時間(単位: 秒)。|
| `k8s_api_wait_delay` | `2` | kube-apiserver待ち合わせる際の開始遅延時間(単位: 秒)。|
| `k8s_api_wait_sleep` | `1` | kube-apiserver待ち合わせる際の待機間隔(単位: 秒)。|
| `k8s_api_wait_delegate_to` | "localhost" | kube-apiserver待ち合わせる際の接続元ホスト名/IPアドレス。|
| `k8s_hubble_ui_config_dir` | `"{{ k8s_kubeadm_config_store }}/hubble-ui"` | Hubble UI 設定ファイル格納ディレクトリパスを指定します。Helm values ファイルなどがここに保存されます。 |
| `hubble_ui_enabled` | `false` | Hubble UI を有効化するかどうかを指定します。`true` に設定すると Hubble UI がインストールされます。 |
| `hubble_ui_version` | `""` (自動設定) | Hubble UI のバージョンを指定します。空文字列の場合は `k8s_cilium_version` の値を使用します。Cilium Helm Chart のバージョンと一致させる必要があります。 |
| `hubble_ui_service_type` | `"NodePort"` | Hubble UI Service の公開方法を指定します。`NodePort`, `LoadBalancer`, `ClusterIP` から選択できます。 |
| `hubble_ui_nodeport` | `31234` | `hubble_ui_service_type` が `NodePort` の場合に使用するポート番号を指定します。 |
| `hubble_ui_replicas` | `1` | Hubble UI Deployment のレプリカ数を指定します。 |
| `hubble_ui_merge_existing_values` | `true` | 既存の Cilium Helm values とマージするかどうかを指定します。`true` の場合, `helm get values` で取得した既存値と新規設定を `yq` でマージします。**既存の Cilium 設定を保護するため, デフォルトで有効化されています。** |
| `hubble_ui_ingress_enabled` | `false` | (将来対応予定) Ingress を有効化するかどうかを指定します。現在の実装では未サポートです。 |
| `hubble_ui_ingress_hosts` | `[]` | (将来対応予定) Ingress のホスト名リストを指定します。現在の実装では未サポートです。 |
| `hubble_ui_ingress_class_name` | `""` | (将来対応予定) Ingress の Class Name を指定します。現在の実装では未サポートです。 |

## 生成されるファイル

このロールは `{{ k8s_hubble_ui_config_dir }}` (既定値: `{{ k8s_kubeadm_config_store }}/hubble-ui`, 通常は `~/kubeadm/hubble-ui`) に以下のファイルを生成します:

| ファイル名 | 説明 |
| --- | --- |
| `hubble-ui-values.yml` | Hubble UI 設定のみを含む Helm values ファイルです。`hubble.ui` セクションのみを上書きする最小限の構成です。 |
| `hubble-ui-values-merged.yml` | `hubble_ui_merge_existing_values: true` の場合にのみ生成されます。既存 Cilium Helm values と `hubble-ui-values.yml` を `yq` でマージした結果を格納します。 |
| `cilium-existing-values.yml` | `hubble_ui_merge_existing_values: true` の場合にのみ生成されます。`helm get values cilium -n kube-system` で取得した既存値を一時保存します。 |

**既定の動作ではマージ機能が有効**になっており, `hubble-ui-values-merged.yml` が Helm upgrade に使用されます。これにより既存の Cilium 設定が保護されます。マージ機能を無効にした場合 (`hubble_ui_merge_existing_values: false`) は `hubble-ui-values.yml` のみが生成されますが, **既存の Cilium 設定が失われる可能性があるため推奨されません**。

## アクセス方法

### NodePort 経由でのアクセス (既定)

`hubble_ui_service_type: "NodePort"` の場合, 以下の URL でアクセスできます:

```text
http://<node-ip>:31234
```

- `<node-ip>`: Kubernetesクラスタ内の任意のノードの IP アドレス
- ポート番号は `hubble_ui_nodeport` 変数で変更可能です

ブラウザで上記 URL にアクセスすると, Hubble UI のダッシュボードが表示されます。

### LoadBalancer 経由でのアクセス

`hubble_ui_service_type: "LoadBalancer"` に設定した場合, クラウドプロバイダまたはオンプレミス LoadBalancer (MetalLB など) が External IP を割り当てます。

```bash
kubectl --kubeconfig /etc/kubernetes/admin.conf get svc -n kube-system hubble-ui
```

上記コマンドで `EXTERNAL-IP` を確認し, `http://<external-ip>` でアクセスします。

### ClusterIP 経由でのアクセス

`hubble_ui_service_type: "ClusterIP"` に設定した場合, Kubernetesクラスタ内部からのみアクセス可能です。Kubernetesクラスタ外部からアクセスする場合は `kubectl port-forward` を使用します:

```bash
kubectl --kubeconfig /etc/kubernetes/admin.conf port-forward -n kube-system svc/hubble-ui 8080:80
```

その後, `http://localhost:8080` でアクセスします。

## 留意事項

### Cilium Pod の再起動について

**このロールは `helm upgrade` を実行するため, 既存 Cilium Pod が再起動される可能性があります。** Cilium DaemonSet や Operator の再起動により, 一時的なネットワーク断が発生する場合があります。本番環境での実行時は適切なメンテナンスウィンドウを設定してください。

### Helm values ファイルの永続化

生成された Helm values ファイルは `{{ k8s_hubble_ui_config_dir }}` に永続的に保存されます。これにより, 後続の Cilium アップグレードやトラブルシューティング時に設定内容を参照できます。

### マージ機能について

**このロールはデフォルトでマージ機能が有効**になっています (`hubble_ui_merge_existing_values: true`)。マージ機能では以下の処理が実行されます:

1. `helm get values cilium -n kube-system` で現在の Helm values を取得
2. 取得した値と `hubble-ui-values.yml` を `yq eval-all 'select(fileIndex==0) * select(fileIndex==1)'` でマージ
3. マージ結果を `hubble-ui-values-merged.yml` に保存
4. Helm upgrade 時にマージ結果を使用

既存の Cilium Helm リリースが存在しない場合や `helm get values` が失敗した場合は, マージ処理をスキップして `hubble-ui-values.yml` のみを使用します。

### Helm upgrade と既存設定の保持について

このロールは `helm upgrade --install` コマンドを使用して Hubble UI を有効化します。Helm の `upgrade` コマンドは `--reuse-values` フラグを指定しない限り, **values ファイルに記載されていない設定は Cilium Helm Chart のデフォルト値に戻ります**。

これは Hubble UI に限らず, Cilium 全体の設定に影響します。例えば:

- 元の Cilium インストール時に設定した `ipam.mode: kubernetes`
- `routingMode: native` や `autoDirectNodeRoutes: true`
- `bgpControlPlane.enabled: true` などの BGP 設定
- `kubeProxyReplacement: true` などの kube-proxy 置換設定

これらの設定が Hubble UI 用の values ファイルに記載されていない場合, Helm upgrade 実行時にチャートのデフォルト値に戻り, **Kubernetesクラスタのネットワーク機能が正常に動作しなくなる可能性があります**。

#### 対策方法

**このロールはデフォルトでマージ機能が有効**になっており, 既存の Cilium 設定を自動的に保護します。特別な設定は不要です。

マージ機能 (`hubble_ui_merge_existing_values: true`) により, 既存の Helm values を取得してマージします。これにより, 既存の Cilium 設定を保持したまま Hubble UI 設定のみを追加できます。

```yaml
hubble_ui_enabled: true
# hubble_ui_merge_existing_values は既定で true なので設定不要
```

何らかの理由でマージを無効化する場合は `hubble_ui_merge_existing_values: false` を設定できますが, **既存の Cilium 設定が失われる可能性があるため推奨されません**。

#### Hubble Relay 設定について

本ロールでは, Hubble UI 用 values ファイル (`hubble-ui-values.yml.j2`) に `hubble.relay.enabled: true` を明示的に含めています。これは以下の理由によります:

1. Hubble UI は Hubble Relay に依存しており, Relay が無効化されると UI は正常に動作しない
2. 元の Cilium インストール時に `hubble.relay.enabled: true` が設定されていても, マージ機能を使用しない場合はデフォルト値 (`false`) に戻ってしまう
3. マージ機能の有効/無効に関わらず, Hubble Relay が確実に有効化された状態を維持する

**このロールはデフォルトでマージ機能が有効**になっているため, `hubble.relay.enabled: true` を含むすべての既存 Cilium 設定が自動的に保護されます。

### Hubble Relay の依存関係

Hubble UI は Hubble Relay を経由してKubernetesクラスタ内のフロー情報を取得します。Hubble Relay が無効化されている場合, Hubble UI は正常に動作しません。事前に `k8s-ctrlplane` ロールで Cilium をインストールする際に `hubble.relay.enabled: true` が設定されていることを確認してください。

## 検証手順

### 1. Hubble UI Deployment の確認

```bash
kubectl --kubeconfig /etc/kubernetes/admin.conf get deployment -n kube-system hubble-ui
```

`READY` 列が `1/1` (または設定したレプリカ数) になっていることを確認します。

### 2. Hubble UI Pod の確認

```bash
kubectl --kubeconfig /etc/kubernetes/admin.conf get pods -n kube-system -l k8s-app=hubble-ui
```

Pod のステータスが `Running` になっていることを確認します。

### 3. Hubble UI Service の確認

```bash
kubectl --kubeconfig /etc/kubernetes/admin.conf get svc -n kube-system hubble-ui
```

`TYPE` が設定した `hubble_ui_service_type` (NodePort/LoadBalancer/ClusterIP) になっていることを確認します。

### 4. Web UI へのアクセス確認

ブラウザで `http://<node-ip>:31234` (NodePort の場合) にアクセスし, Hubble UI のダッシュボードが表示されることを確認します。

### 5. Helm values の確認

```bash
helm get values cilium -n kube-system | grep -A 5 "ui:"
```

`ui.enabled: true` が設定されていることを確認します。

## トラブルシューティング

### Hubble UI Pod が起動しない

1. Pod のログを確認します:

   ```bash
   kubectl --kubeconfig /etc/kubernetes/admin.conf logs -n kube-system -l k8s-app=hubble-ui
   ```

2. Hubble Relay が正常に動作しているか確認します:

   ```bash
   kubectl --kubeconfig /etc/kubernetes/admin.conf get pods -n kube-system -l k8s-app=hubble-relay
   ```

3. Hubble Relay が存在しない場合は, `k8s-ctrlplane` ロールで Cilium を再インストールし, `hubble.relay.enabled: true` を設定します。

### Web UI にアクセスできない

1. Service の状態を確認します:

   ```bash
   kubectl --kubeconfig /etc/kubernetes/admin.conf get svc -n kube-system hubble-ui -o wide
   ```

2. NodePort の場合, ファイアウォールでポートが開放されているか確認します。

3. LoadBalancer の場合, External IP が正しく割り当てられているか確認します。

### Helm upgrade が失敗する

1. Cilium Helm リリースが存在するか確認します:

   ```bash
   helm list -n kube-system
   ```

2. `hubble_ui_merge_existing_values: false` に設定して, マージ機能を無効化してから再実行します。

3. 既存の Helm values に構文エラーがないか確認します:

   ```bash
   helm get values cilium -n kube-system -o yaml
   ```

## 設定例

### 基本設定 (NodePort)

`vars/all-config.yml` または `host_vars/<hostname>` で以下のように設定します:

```yaml
hubble_ui_enabled: true
hubble_ui_service_type: "NodePort"
hubble_ui_nodeport: 31234
hubble_ui_replicas: 1
# hubble_ui_version はデフォルトで k8s_cilium_version の値を使用
# hubble_ui_merge_existing_values はデフォルトで true (既存の Cilium 設定を自動保護)
```

### LoadBalancer を使用する場合

```yaml
hubble_ui_enabled: true
hubble_ui_service_type: "LoadBalancer"
hubble_ui_replicas: 2
```

### マージを無効化する場合 (非推奨)

```yaml
hubble_ui_enabled: true
hubble_ui_service_type: "NodePort"
hubble_ui_nodeport: 31234
hubble_ui_merge_existing_values: false  # 非推奨: 既存の Cilium 設定が失われる可能性
```

**注意**: マージを無効化すると, 既存の Cilium 設定 (ipam, routing, bgp, kube-proxy置換など) がチャートのデフォルト値に戻り, Kubernetesクラスタのネットワーク機能が正常に動作しなくなる可能性があります。特別な理由がない限り, デフォルトのマージ有効状態を維持してください。

### 特定のバージョンを指定する場合

```yaml
hubble_ui_enabled: true
hubble_ui_version: "1.16.0"
hubble_ui_service_type: "NodePort"
hubble_ui_nodeport: 31234
```

`hubble_ui_version` を明示的に指定することで, Cilium のバージョンを制御できます。通常は `k8s_cilium_version` と同じ値を使用してください。
