# k8s-hubble-ui ロール

Cilium Hubble UI を Kubernetes クラスタへ導入するロールです。

主な機能:

- **Helm チャート統合**: 既存の Cilium Helm リリースを `helm upgrade --install` でアップグレードし, `hubble.ui.enabled: true` を追加設定します。
- **既存設定保護 (マージ機能)**: デフォルトで有効な `yq` ベースのマージ機能により, 既存 Cilium 設定を完全に保護しながら Hubble UI 設定を追加できます。
- **CRD 確認と待ち合わせ**: デプロイ前に Cilium CRD の存在確認と kube-apiserver の起動待ち合わせを自動実行します。
- **Service 公開方法の選択**: NodePort/LoadBalancer/ClusterIP を変数で切り替え, 運用環境に応じたアクセス方法を提供します。
- **Hubble Relay 依存性確認**: Hubble UI 動作に必須の Hubble Relay 有効化を事前確認し, 問題を早期に検出します。
- **Deployment 起動確認**: Helm upgrade 後, Hubble UI Deployment が正常に Ready 状態になるまで待ち合わせます。

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
| 名前空間 ( namespace ) | - | Kubernetes内部でリソースを論理的に分離する単位。 |
| ポッド ( Pod ) | - | Kubernetes上で動作するコンテナの最小単位。 |
| レプリカ ( Replica ) | - | Podの複製。DeploymentなどのリソースがPodの高可用性や負荷分散のために複数のレプリカを作成, 管理する。指定されたレプリカ数に基づいて同一の仕様を持つPodが複数実行される。 |
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

- Kubernetes クラスタの全ノード（コントロールプレーンノードとワーカーノード）が稼働し, Cilium によるクラスタ内ネットワークが正常に構成されていること - Hubble UI はクラスタ内のネットワークトラフィックを観測するため, Kubernetes ノードの稼働と Cilium CNI による通信確立が必須です
- Cilium が Helm 経由でインストール済みであること (`k8s-ctrlplane` ロール実行済み)
- Hubble Relay が有効化されていること - Hubble UI は Hubble Relay に依存します (`hubble.relay.enabled: true` を確認)
- `kubectl` コマンドが利用可能であること (Kubernetes リソース操作用)
- `helm` コマンドが利用可能であること (Cilium Helm リリース管理用)
- `yq` コマンドが利用可能であること - マージ機能使用時に必須 (既存設定保護)
- Ansible 実行ホストから kube-apiserver へのネットワークアクセスが可能であること

## 実行フロー

本ロールは以下の順序で処理を実行します:

1. **パラメータ読み込み** (`load-params.yml`): OS 別パッケージ定義 (`vars/packages-ubuntu.yml`, `vars/packages-rhel.yml`), クロスディストロ変数 (`vars/cross-distro.yml`), 共通変数 (`vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込みます。

2. **変数検証** (`validate.yml`): `k8s_hubble_ui_enabled` の型チェック (true/false のいずれか), `hubble_ui_version` が空文字列の場合は `k8s_cilium_version` に自動設定します。

3. **パッケージ・ディレクトリ・ユーザ・サービス準備** (`package.yml`, `directory.yml`, `user_group.yml`, `service.yml`): 現在プレースホルダ (実処理なし)。

4. **メイン処理: 設定生成と Helm upgrade** (`config.yml`): 以下の処理を実行します:
   - **kube-apiserver 待ち合わせ**: `k8s_api_wait_*` パラメータで接続確認 (タイムアウト: 600秒デフォルト)
   - **Cilium CRD 確認**: Cilium が正常にインストールされていることを確認 (最大 30回リトライ, 10秒間隔)
   - **Hubble Relay Deployment 確認**: Hubble Relay が有効化されているか確認 (無効時は警告表示)
   - **Hubble UI values ファイル生成**: `hubble-ui-values.yml.j2` テンプレートを展開し, `{{ k8s_hubble_ui_config_dir }}/hubble-ui-values.yml` を生成
   - **既存設定マージ (オプション)**: `hubble_ui_merge_existing_values: true` の場合, `helm get values cilium -n kube-system` で既存値を取得し, `yq` で新規設定とマージ（既存設定保護）
   - **Helm upgrade 実行**: `helm upgrade --install cilium <chart> -n kube-system -f <values-file>` を実行
   - **Deployment 起動確認**: `kubectl wait --for=condition=available` で Hubble UI Deployment が Ready 状態になるまで待機

## 主要変数

## 主要変数

本ロールで扱う主な変数と用途を示します。変数は `group_vars`, `host_vars`, または `vars/all-config.yml` で上書きできます。

### API 待ち合わせ設定

| 変数名 | 既定値 | 説明 |
| ------ | ------ | ---- |
| `k8s_api_wait_host` | `"{{ k8s_ctrlplane_endpoint }}"` | kube-apiserver の待ち合わせ先ホスト名/IP アドレス。 |
| `k8s_api_wait_port` | `"{{ k8s_ctrlplane_port }}"` | kube-apiserver の待ち合わせ先ポート番号 (規定: `6443`)。 |
| `k8s_api_wait_timeout` | `600` | kube-apiserver 待ち合わせ時間 (単位: 秒)。 |
| `k8s_api_wait_delay` | `2` | kube-apiserver 待ち合わせ開始遅延時間 (単位: 秒)。 |
| `k8s_api_wait_sleep` | `1` | kube-apiserver 待ち合わせ時の待機間隔 (単位: 秒)。 |
| `k8s_api_wait_delegate_to` | `"localhost"` | kube-apiserver 待ち合わせ実行ホスト名/IP アドレス。 |

### Hubble UI 設定

| 変数名 | 既定値 | 説明 |
| ------ | ------ | ---- |
| `k8s_hubble_ui_config_dir` | `"{{ k8s_kubeadm_config_store }}/hubble-ui"` | Hubble UI 設定ファイル格納ディレクトリ。Helm values ファイル等を保存。 |
| `k8s_hubble_ui_enabled` | `false` | Hubble UI を有効化するか (true/false)。`true` でインストール。 |
| `hubble_ui_version` | `""` (自動設定) | Hubble UI バージョン。空文字列時は `k8s_cilium_version` を使用。 |
| `hubble_ui_service_type` | `"NodePort"` | Service 公開方法 (NodePort/LoadBalancer/ClusterIP)。 |
| `hubble_ui_nodeport` | `31234` | NodePort 使用時のポート番号。 |
| `hubble_ui_replicas` | `1` | Hubble UI Deployment レプリカ数。 |

### マージ・ネットワーク・Ingress 設定

| 変数名 | 既定値 | 説明 |
| ------ | ------ | ---- |
| `hubble_ui_merge_existing_values` | `true` | 既存 Cilium Helm values とマージするか。**既存設定保護のため, デフォルト有効**。 |
| `hubble_ui_service_ipFamilyPolicy` | `"PreferDualStack"` | Service IP ファミリーポリシー (IPv4 優先/IPv6 優先/デュアル)。 |
| `hubble_ui_ingress_enabled` | `false` | (将来対応予定) Ingress を有効化するか。現在未サポート。 |
| `hubble_ui_ingress_hosts` | `[]` | (将来対応予定) Ingress ホスト名リスト。現在未サポート。 |
| `hubble_ui_ingress_class_name` | `""` | (将来対応予定) Ingress Class Name。現在未サポート。 |

## テンプレートとファイル

このロールは `{{ k8s_hubble_ui_config_dir }}` (既定値: `{{ k8s_kubeadm_config_store }}/hubble-ui`, 通常は `~/kubeadm/hubble-ui`) に以下のファイルを生成します。`~`は, `ansible_user` (規定値: `"ansible"`) のホームディレクトリ (規定値: `"/home/ansible"`)を意味します:

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

- `<node-ip>`: Kubernetesクラスタ内の任意のKubernetes ノードの IP アドレス
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
k8s_hubble_ui_enabled: true
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

## 設定内容の検証

Ansible 実行後, 以下の項目を確認することで, Hubble UI が正しく導入されているか検証できます。

### 1. Hubble UI Deployment の起動状態確認

**実施ホスト:** コントロールプレーンノード

**コマンド:**

```bash
kubectl --kubeconfig /etc/kubernetes/admin.conf get deployment -n kube-system hubble-ui
```

**期待される出力:**

```plaintext
NAME        READY   UP-TO-DATE   AVAILABLE   AGE
hubble-ui   1/1     1            1           2m34s
```

**確認ポイント:**
- `READY` 列が `1/1` (または `vars/all-config.yml` で設定した `hubble_ui_replicas` 値) になっていること
- `AVAILABLE` 列が `READY` 値と同じであること (全 Pod が稼働中)
- `AGE` が数分以内であること (最近デプロイされたことを示す)

### 2. Hubble UI Pod の稼働確認

**実施ホスト:** コントロールプレーンノード

**コマンド:**

```bash
kubectl --kubeconfig /etc/kubernetes/admin.conf get pods -n kube-system -l k8s-app=hubble-ui
```

**期待される出力:**

```plaintext
NAME                        READY   STATUS    RESTARTS   AGE
hubble-ui-b8d9f7f5c-xyz12   1/1     Running   0          2m30s
```

**確認ポイント:**
- `STATUS` 列が `Running` であること
- `READY` 列が `1/1` であること (コンテナが完全に起動)
- `RESTARTS` 列が `0` であること (Pod が再起動されていない)
- Pod が起動失敗している場合は, 名前を控えて `kubectl logs -n kube-system <pod-name>` でログを確認

### 3. Hubble UI Service の設定確認

**実施ホスト:** コントロールプレーンノード

**コマンド:**

```bash
kubectl --kubeconfig /etc/kubernetes/admin.conf get svc -n kube-system hubble-ui
```

**期待される出力 (NodePort 設定時):**

```plaintext
NAME        TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
hubble-ui   NodePort   10.96.234.56    <none>        80:31234/TCP     2m
```

**期待される出力 (LoadBalancer 設定時):**

```plaintext
NAME        TYPE           CLUSTER-IP      EXTERNAL-IP    PORT(S)        AGE
hubble-ui   LoadBalancer   10.96.234.56    192.0.2.100    80:31234/TCP   2m
```

**確認ポイント:**
- `TYPE` 列が `vars/all-config.yml` で設定した `hubble_ui_service_type` (NodePort/LoadBalancer/ClusterIP) と一致していること
- NodePort の場合, `PORT(S)` 列に `<内部ポート>:<公開ポート>/TCP` の形式でマッピング表示されること
- LoadBalancer の場合, `EXTERNAL-IP` に外部 IP が割り当てられていること (初期状態は `<pending>` の場合がある)

### 4. Hubble UI Web インターフェースアクセス確認

**実施ホスト:** コントロールプレーンノード (またはクライアントマシン)

**コマンド (NodePort の場合):**

```bash
curl -s http://<node-ip>:31234/ | head -n 20
```

[Node IP を確認する場合]
```bash
kubectl --kubeconfig /etc/kubernetes/admin.conf get nodes -o wide | head -n 2
```

**期待される出力:**

```plaintext
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Hubble</title>
  <script src="/api/v1/ui/openapi.json"></script>
  <script src="/dist/js/app.js"></script>
  <link href="/dist/css/app.css" rel="stylesheet">
</head>
<body>
  <div id="app"></div>
</body>
</html>
```

**確認ポイント:**
- HTTP ステータスが 200 であること（curl が特にエラーを出さない）
- HTML ドキュメントが返されること
- ブラウザでアクセスした場合, Hubble UI ダッシュボード（グラフ表示, Pod リスト等）が表示されること
- Web UI が表示されない場合は, Service のポートマッピングと Node のファイアウォール設定を確認

### 5. Helm values の構成確認

**実施ホスト:** コントロールプレーンノード

**コマンド:**

```bash
helm get values cilium -n kube-system | grep -A 10 "^ui:"
```

**期待される出力:**

```plaintext
ui:
  enabled: true
  replicas: 1
  service:
    type: NodePort
    nodePort: 31234
    ipFamilyPolicy: PreferDualStack
```

**確認ポイント:**
- `ui.enabled: true` が設定されていること
- `ui.replicas` が `vars/all-config.yml` の `hubble_ui_replicas` 値と一致していること
- `ui.service.type` が `hubble_ui_service_type` と一致していること
- NodePort 利用時は `ui.service.nodePort` が設定値と一致していること

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
k8s_hubble_ui_enabled: true
hubble_ui_service_type: "NodePort"
hubble_ui_nodeport: 31234
hubble_ui_replicas: 1
```

この設定で, Hubble UI が NodePort 経由で公開されます。以下は自動設定されるため, 省略可能です:

- `hubble_ui_version`: デフォルトで `k8s_cilium_version` の値を使用
- `hubble_ui_merge_existing_values`: デフォルトで `true`（既存の Cilium 設定を自動保護）

### LoadBalancer を使用する場合

クラウドプロバイダまたはオンプレミス環境で LoadBalancer サポートがある場合, 以下のように設定します:

```yaml
k8s_hubble_ui_enabled: true
hubble_ui_service_type: "LoadBalancer"
hubble_ui_replicas: 2
```

この場合, Kubernetes クラスタの外部から `EXTERNAL-IP` でアクセス可能になります。LoadBalancer の IP が割り当てられるまで数分待機する場合があります。`kubectl get svc -n kube-system hubble-ui` で `EXTERNAL-IP` を確認してください。

### マージを無効化する場合 (非推奨)

マージ機能を意図的に無効化する場合は, 以下のように設定します。ただし, この設定は推奨されません:

```yaml
k8s_hubble_ui_enabled: true
hubble_ui_service_type: "NodePort"
hubble_ui_nodeport: 31234
hubble_ui_merge_existing_values: false
```

**注意 - マージを無効化すると, 既存の Cilium 設定が失われます**

マージを無効化すると, 既存の Cilium 設定 (ipam, routing, bgp, kube-proxy置換など) が Helm Chart のデフォルト値に戻ります。その結果, Kubernetesクラスタのネットワーク機能が正常に動作しなくなる可能性があります。特別な理由がない限り, デフォルトのマージ有効状態 (`hubble_ui_merge_existing_values: true`) を維持してください。

### 特定のバージョンを指定する場合

Hubble UI のバージョンを `k8s_cilium_version` と異なる値で指定する場合:

```yaml
k8s_hubble_ui_enabled: true
hubble_ui_version: "1.16.0"
hubble_ui_service_type: "NodePort"
hubble_ui_nodeport: 31234
```

`hubble_ui_version` を明示的に指定することで, Helm Chart のバージョンを制御できます。通常は `k8s_cilium_version` と同じ値を使用してください。バージョン不一致の場合, Cilium と Hubble UI 間で互換性の問題が生じる可能性があります。
