# k8s-whereabouts ロール

Kubernetes コントロールプレーンノード上に Whereabouts を導入し, NetworkAttachmentDefinition (NAD) を適用するロールです。`k8s-common`, `k8s-ctrlplane`, `k8s-multus` で整えた共通前提の上に, Whereabouts の Helm チャート導入と NAD の適用を行います。再実行にも対応するよう設計されています。

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
| Taint | - | Nodeに設定する特殊なマークで, 特定の条件を満たさないPodの配置を拒否する。 |
| Toleration | - | PodがTaintを持つNodeへ配置されることを許可する設定。 |

## 実行フロー

1. `load-params.yml` で OS 別パッケージ定義 (`vars/packages-*.yml`) とKubernetesクラスタ共通変数 (`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込みます。
2. `package.yml` を読み込みます (現状はタスクなしのプレースホルダです)。
3. `directory.yml` が Whereabouts 用の設定ディレクトリ (既定では `{{ k8s_kubeadm_config_store }}/whereabouts`) を作成します。
4. `user_group.yml` と `service.yml` は将来の拡張用に読み込まれます (現状はタスクなし)。
5. `config-whereabouts.yml` は `k8s_multus_enabled` と `k8s_whereabouts_enabled` が有効で, かつ IPv4 または IPv6 のアドレス範囲が揃っている場合に発動します。kube-apiserverの起動を待機後, Whereabouts Helm チャートを導入し, `ipvlan-wb-nad.yml.j2` から生成した NAD を `kubectl apply` します。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_ctrlplane_endpoint` | 各ホストの `host_vars` で指定 | Control Plane API の広告アドレス (IPv4/IPv6)。待機処理で使用。|
| `k8s_api_wait_host` | "{{ k8s_ctrlplane_endpoint }}" | kube-apiserverの待ち合わせ先(接続先)ホスト名/IPアドレス。|
| `k8s_api_wait_port` | "{{ k8s_ctrlplane_port }}" | kube-apiserverの待ち合わせ先ポート番号。 (規定: `6443`)|
| `k8s_api_wait_timeout` | `600` | kube-apiserver待ち合わせ時間(単位: 秒)。|
| `k8s_api_wait_delay` | `2` | kube-apiserver待ち合わせる際の開始遅延時間(単位: 秒)。|
| `k8s_api_wait_sleep` | `1` | kube-apiserver待ち合わせる際の待機間隔(単位: 秒)。|
| `k8s_api_wait_delegate_to` | "localhost" | kube-apiserver待ち合わせる際の接続元ホスト名/IPアドレス。|
| `k8s_kubeadm_config_store` | `{{ ansible_home_dir }}/kubeadm` | Whereabouts 設定ファイルのルートディレクトリ。|
| `k8s_whereabouts_config_dir` | `{{ k8s_kubeadm_config_store }}/whereabouts` | NAD 設定ファイルの生成先ディレクトリ。|
| `k8s_multus_enabled` | `false` | Multus が有効な場合のみ Whereabouts を導入します。|
| `k8s_whereabouts_enabled` | `false` | Whereabouts 関連タスクを実行するかどうか。|
| `k8s_whereabouts_version` | `0.9.2` | Whereabouts のベースバージョン。|
| `k8s_whereabouts_helm_chart_version` | `{{ k8s_whereabouts_version }}` | Whereabouts チャートバージョン。|
| `k8s_whereabouts_image_version` | `{{ k8s_whereabouts_version }}` | Whereabouts コンテナイメージのタグ (テンプレート内で参照)。|
| `k8s_whereabouts_chart_url` | `oci://ghcr.io/k8snetworkplumbingwg/whereabouts-chart` | Whereabouts Helm チャートの OCI URL。|
| `k8s_whereabouts_ipv4_range_start` / `k8s_whereabouts_ipv4_range_end` | `""` | NAD で使用する IPv4 プール範囲。適用前に要設定。|
| `k8s_whereabouts_ipv6_range_start` / `k8s_whereabouts_ipv6_range_end` | `""` | NAD で使用する IPv6 プール範囲。|
| `network_ipv4_cidr` | `vars/all-config.yml` 由来 | NAD で使用する IPv4 CIDR。|
| `network_ipv6_cidr` | `vars/all-config.yml` 由来 | NAD で使用する IPv6 CIDR。|
| `mgmt_nic` | `group_vars/all/all.yml` 由来 | NAD の `master` インタフェース名。|

その他, `vars/cross-distro.yml` と `vars/all-config.yml` に含まれる共通変数は, NAD テンプレート生成に利用されます。

## 主な処理

- **Whereabouts 導入**: OCI Helm チャートを `helm upgrade --install` で導入します。
- **NAD 適用**: `templates/ipvlan-wb-nad.yml.j2` から生成した NAD を `kubectl apply` します。

## テンプレート／ファイル

| テンプレート/ファイル | 用途 | インストール先パス |
| --- | --- | --- |
| `templates/ipvlan-wb-nad.yml.j2` | Whereabouts + IPvLAN 用 NetworkAttachmentDefinition。 | `{{ k8s_whereabouts_config_dir }}/ipvlan-wb-nad.yml` (既定: `/home/ansible/kubeadm/whereabouts/ipvlan-wb-nad.yml`) |

## 検証ポイント

- `helm list -n kube-system` に `whereabouts` が想定通りのバージョンで存在する。
- `kubectl get networkattachmentdefinition` で `ipvlan-wb` が登録されている。
- `{{ k8s_whereabouts_config_dir }}/ipvlan-wb-nad.yml` が生成されている。

### NAD 動作確認

`ipvlan-wb` の NAD が生成されていることを確認します:

```bash
kubectl get networkattachmentdefinition ipvlan-wb -o yaml
```

## 補足

- `k8s_multus_enabled: true` と `k8s_whereabouts_enabled: true` の両方が必要です。
- `k8s_whereabouts_ipv4_range_start` / `k8s_whereabouts_ipv4_range_end` を事前に設定してください (IPv4 を使う場合)。
- `k8s_whereabouts_ipv6_range_start` / `k8s_whereabouts_ipv6_range_end` を事前に設定してください (IPv6 を使う場合)。
- IPv4/IPv6 のいずれかが揃っていない場合, `config-whereabouts.yml` は実行されません。

### IPv6 範囲を有効化する手順

1. 変数を設定します。

```yaml
k8s_whereabouts_ipv6_range_start: "<IPv6の開始アドレス>"
k8s_whereabouts_ipv6_range_end: "<IPv6の終了アドレス>"
```

2. ロールを再実行して NAD を再生成・再適用します。

3. IPv6 アドレスが付与されていることを確認します。

```bash
kubectl get networkattachmentdefinition ipvlan-wb -o yaml
kubectl exec demo-net1 -it -- ip -6 addr
```

### NAD の namespace を変更する手順

`templates/ipvlan-wb-nad.yml.j2` の `metadata.namespace` を変更します。

1. 例: `default` から `kube-system` に変更する場合

```yaml
metadata:
	name: ipvlan-wb
	namespace: kube-system
```

2. 既存の NAD を削除し, 再適用します。

```bash
kubectl delete networkattachmentdefinition ipvlan-wb -n default
kubectl apply -f "{{ k8s_whereabouts_config_dir }}/ipvlan-wb-nad.yml"
```

3. 参照側 (Pod/CRD) の `k8s.v1.cni.cncf.io/networks` が namespace 指定を含む場合は合わせて更新します。
