# k8s-ctrlplane ロール

Kubernetes コントロールプレーンノードを構築するロールです。`k8s-common` で整えた共通前提の上に, kubeadm 設定の生成と実行, Cilium の導入, Cluster Mesh 用 kubeconfig 生成ツールの配布, Helm/Cilium CLI 環境整備を行います。IPv4/IPv6 デュアルスタックを前提にしており, 再実行にも対応するよう設計されています。

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

- **Linux OS**: Debian/Ubuntu 系 (Ubuntu 24.04を想定) または RHEL9系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- **前段ロール**: `k8s-common` を先に実行済みであること
- **実行権限**: root または sudo 実行権限
- **クラスタ変数**: `k8s_ctrlplane_endpoint`, `k8s_ctrlplane_port`, `k8s_cilium_version`, Pod/Service CIDR 変数を定義済みであること
- **ネットワーク**: 複数 NIC 構成では API 到達先 NIC と `k8s_ctrlplane_endpoint` の整合を確認すること

`config.yml` は `kubeadm reset` を含むため, 既存クラスタへ適用する場合は停止計画とバックアップ計画を事前に準備してください。

## 実行方法

### Makefile を使用

```bash
make run_k8s_ctrlplane
```

### Ansible コマンド直接実行

```bash
# すべての対象ホストに適用
ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml

# 特定ホストだけ実行
ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml --limit <hostname>

# 主要タグのみ実行
ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml -t k8s-ctrlplane
```

## 実行フロー

### ステップ1: 変数読み込み

1. `load-params.yml` が OS別パッケージ変数 (`vars/packages-*.yml`) と共通変数 (`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込みます。

### ステップ2: ディレクトリ準備

2. `directory.yml` が `k8s_cilium_config_dir`, `k8s_multus_config_dir`, `k8s_whereabouts_config_dir` を作成します (Multus/Whereabouts は本ロールでは作成のみ)。

### ステップ3: 予約タスク読み込み

3. `package.yml`, `user_group.yml`, `service.yml` を読み込みます (現時点では処理なしのプレースホルダ)。

### ステップ4: ファイアウォール構成

4. `config-k8sctrlplane-firewall.yml` が `enable_firewall` と `firewall_backend` に応じて UFW または firewalld を構成し, 6443/tcp, 10250/tcp, 10257/tcp, 10259/tcp, 2379-2380/tcp を開放します。

### ステップ5: Helm/Cilium CLI と補完構成

5. `config-helm.yml` が Helm と Cilium CLI を導入します。`k8s_helm_version` が未定義または `latest` なら公式スクリプト経由, 明示バージョン指定時はアーカイブを取得して配置します。
6. 同タスクで既存 Helm リポジトリを全削除し, `cilium` リポジトリを root と `k8s_operator_user` の双方に再登録します。
7. `config-k8s-helm-shell-completion.yml` が `k8s_helm_cli_completion_enabled: true` のとき Helm 補完を配置します。
8. `config-k8s-cilium-shell-completion.yml` が `k8s_cilium_cli_completion_enabled: true` のとき Cilium CLI 補完を配置します。

### ステップ6: kubeadm 初期化

9. `config.yml` が API ファミリ (IPv4/IPv6) を判定し, Pod/Service CIDR を API ファミリ順に並べ替えて `ctrlplane-kubeadm.config.yml` を生成します。
10. 同タスクが `kubeadm reset -f` 後に `kubelet` 停止, `/etc/kubernetes/manifests` 削除, `/var/lib/kubelet/cpu_manager_state` 削除を実行します。
11. `k8s_shared_ca_*` 変数が定義されている場合は共有CAを復元し, `k8s_shared_ca_replace_kube_ca: true` のとき `/etc/kubernetes/pki/ca.crt` と `/etc/kubernetes/pki/ca.key` を置換します。
12. `kubeadm init --config ...` を実行し, containerd/kubelet を有効化します。その後 `admin.conf` を root, ansible, `k8s_operator_user` に配布して再起動します。

### ステップ7: Cilium 導入

13. `config-cilium.yml` が API サーバ起動を待機し, `kubernetes-admin` へ cluster-admin 権限を付与します。
14. 同タスクが kube-proxy のデーモンセット/コンフィグマップと関連 iptables ルールを削除し, `cilium-install.yml` を生成して `helm install cilium` を実行します。
15. `k8s_cilium_shared_ca_enabled: true` の場合は `k8s-cilium-shared-ca` ロールを実行して Cluster Mesh 用 Secret を整備します。

### ステップ8: Cilium BGP Control Plane (任意)

16. `config-cilium-bgp-cplane.yml` は `k8s_bgp.enabled: true` のホストだけで実行されます。
17. 同タスクは `k8s-common/templates/cilium-bgp-resources.yml.j2` を参照してマニフェストを生成し, Cilium BGP関連CRD (Advertisement/PeerConfig/ClusterConfig) の出現を待ってから `kubectl apply` します。

### ステップ9: Cluster Mesh ツール配布

18. `config-cluster-mesh-tools.yml` が `create-embedded-kubeconfig.py` と手順書を配布します。
19. `k8s_cilium_cm_cluster_name` と `k8s_cilium_cm_cluster_id` が有効な場合, 共有CAファイルの存在を確認し, 埋め込み kubeconfig を生成して所有者を `k8s_operator_user` に調整します。

## 主要変数

### API待機・kubeadm関連

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_ctrlplane_endpoint` | host_vars で指定 | Control Plane API の広告アドレス。 |
| `k8s_api_wait_host` | `{{ k8s_ctrlplane_endpoint }}` | API サーバ待機先ホスト。 |
| `k8s_api_wait_port` | `{{ k8s_ctrlplane_port }}` | API サーバ待機先ポート。 |
| `k8s_api_wait_timeout` | `600` | API 待機タイムアウト(秒)。 |
| `k8s_api_wait_delay` | `2` | API 待機開始遅延(秒)。 |
| `k8s_api_wait_sleep` | `1` | API 待機ポーリング間隔(秒)。 |
| `k8s_api_wait_delegate_to` | `localhost` | API 待機を実行する接続元ホスト。 |
| `k8s_kubeadm_config_store` | `{{ ansible_home_dir }}/kubeadm` | kubeadm/Cilium 設定生成の基点ディレクトリ。 |
| `k8s_kubeadm_ignore_preflight_errors_arg` | `--ignore-preflight-errors=all` | `kubeadm init` 実行時の preflight 制御。 |
| `k8s_pod_ipv4_network_cidr` / `k8s_pod_ipv6_network_cidr` | 必須 | Pod ネットワーク CIDR。 |
| `k8s_pod_ipv4_service_subnet` / `k8s_pod_ipv6_service_subnet` | 必須 | Service CIDR。 |

### Cilium/Helm関連

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_helm_version` | 未定義 | 未定義または `latest` で最新版を導入。 |
| `k8s_helm_cli_completion_enabled` | `true` | Helm 補完の生成有効化。 |
| `k8s_cilium_version` | 必須 | Cilium ベースバージョン。 |
| `k8s_cilium_helm_chart_version` | `{{ k8s_cilium_version }}` | Cilium Helm Chart バージョン。 |
| `k8s_cilium_image_version` | `v{{ k8s_cilium_version }}` | Cilium イメージタグ。 |
| `k8s_cilium_helm_repo_url` | `https://helm.cilium.io/` | Cilium Helm リポジトリURL。 |
| `k8s_cilium_config_dir` | `{{ k8s_kubeadm_config_store }}/cilium` | Cilium values 出力先。 |
| `k8s_cilium_cli_completion_enabled` | `true` | Cilium CLI 補完の生成有効化。 |
| `k8s_cilium_shared_ca_enabled` | `false` | `k8s-cilium-shared-ca` を実行するか。 |
| `k8s_cilium_bgp_control_plane_enabled` | 未定義 | Helm values の `bgpControlPlane.enabled` を明示制御。未定義時は `k8s_bgp.enabled` に連動。 |

### Cilium BGP/Cluster Mesh関連

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_bgp` | (未定義) | BGP Control Plane 設定マッピング。`enabled: true` のとき `neighbors` が必須。 |
| `k8s_cilium_cm_cluster_name` | 未定義 | Cluster Mesh クラスタ名。 |
| `k8s_cilium_cm_cluster_id` | 未定義 | Cluster Mesh クラスタID。 |
| `k8s_embed_kubeconfig_script_path` | `{{ k8s_node_setup_tools_dir }}/create-embedded-kubeconfig.py` | 埋め込み kubeconfig 生成スクリプト配置先。 |
| `k8s_embed_kubeconfig_output_dir` | `{{ k8s_operator_home }}/.kube` | 埋め込み kubeconfig 出力先。 |
| `k8s_embed_kubeconfig_file_postfix` | `-embedded.kubeconfig` | 埋め込み kubeconfig の接尾辞。 |

### 共有CA関連

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_shared_ca_replace_kube_ca` | `false` | `kubeadm reset` 後に `/etc/kubernetes/pki/ca.*` を置換するか。 |
| `k8s_shared_ca_source_cert` / `k8s_shared_ca_source_key` | 未定義 | 共有CAの入力ソース。 |
| `k8s_shared_ca_cert_path` / `k8s_shared_ca_key_path` | 未定義 | 共有CAの配置先。 |
| `k8s_shared_ca_output_dir` | 未定義 | 共有CA配置ディレクトリ。 |

### firewall/補完/オペレータ関連

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `enable_firewall` | `false` | `true` で firewall 構成を実行。 |
| `firewall_backend` | OS 既定 | `ufw` または `firewalld`。 |
| `k8s_control_plane_ports` | 6443,10250,10257,10259,2379-2380 | 開放ポート一覧。 |
| `k8s_operator_user` | `kube` | オペレータユーザ。 |
| `k8s_operator_home` | `/home/kube` | オペレータホーム。 |
| `k8s_node_setup_tools_prefix` | `/opt/k8snodes` | ツール類ベースパス。 |
| `k8s_node_setup_tools_dir` | `{{ k8s_node_setup_tools_prefix }}/sbin` | ツール配置ディレクトリ。 |
| `k8s_node_setup_tools_docs_dir` | `{{ k8s_node_setup_tools_prefix }}/docs` | ドキュメント配置ディレクトリ。 |
| `reboot_timeout_sec` | `600` | 再起動待機タイムアウト(秒)。 |

## デフォルト動作

| 条件 | 結果 |
| --- | --- |
| `enable_firewall: false` | `config-k8sctrlplane-firewall.yml` をスキップします。 |
| `k8s_helm_version` 未定義 | Helm は最新版を導入します。 |
| `k8s_helm_cli_completion_enabled: true` | Helm 補完ファイルを生成・配置します。 |
| `k8s_cilium_cli_completion_enabled: true` | Cilium CLI 補完ファイルを生成・配置します。 |
| `k8s_bgp` が未定義 | `config-cilium-bgp-cplane.yml` をスキップします。 |
| `k8s_bgp.enabled: true` | BGP マニフェストを生成し, CRD待機後に `kubectl apply` を実行します。 |
| `k8s_cilium_cm_cluster_name` または `k8s_cilium_cm_cluster_id` が未定義 | 埋め込み kubeconfig 生成をスキップします。 |
| `k8s_shared_ca_replace_kube_ca: true` | `kubeadm reset` 後に `/etc/kubernetes/pki/ca.*` を共有CAで置換します。 |

## テンプレート / ファイル

本ロールでは以下のテンプレート / ファイルを出力します:

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `templates/ctrlplane-kubeadm.config.j2` | `{{ k8s_kubeadm_config_store }}/ctrlplane-kubeadm.config.yml` (既定: `/home/ansible/kubeadm/ctrlplane-kubeadm.config.yml`) | kubeadm 初期化設定。APIファミリに応じた Pod/Service CIDR 並び替え結果を反映します。 |
| `templates/cilium-install.yml.j2` | `{{ k8s_cilium_config_dir }}/cilium-install.yml` (既定: `/home/ansible/kubeadm/cilium/cilium-install.yml`) | Cilium Helm values。kube-proxy 置換, native routing, dual-stack 設定を出力します。 |
| `templates/create-embedded-kubeconfig.py.j2` | `{{ k8s_embed_kubeconfig_script_path }}` (既定: `/opt/k8snodes/sbin/create-embedded-kubeconfig.py`) | Cluster Mesh 用の証明書埋め込み kubeconfig 生成スクリプト。 |
| `files/Readme-create-embedded-kubeconfig-JP.md` | `{{ k8s_node_setup_tools_docs_dir }}/Readme-create-embedded-kubeconfig-JP.md` (既定: `/opt/k8snodes/docs/Readme-create-embedded-kubeconfig-JP.md`) | 上記スクリプトの利用手順書。 |
| `../k8s-common/templates/cilium-bgp-resources.yml.j2` | `{{ k8s_cilium_config_dir }}/bgp/cilium-bgp-resources-<node>.yml` (既定) | Cilium BGP Control Plane マニフェスト。`k8s-ctrlplane` 側実装は `k8s-common` 側テンプレートに依存します。 |

## OS 差異

| 項目 | Debian/Ubuntu 系 | RHEL 系 |
| --- | --- | --- |
| パッケージマネージャー | `apt` | `yum` / `dnf` |
| firewall 実装 | UFW (`ufw allow`) | firewalld (`firewall-cmd --permanent --add-port`) |
| firewall 再読込 | `ufw reload` | `firewall-cmd --reload` |
| Helm zsh 補完パス | `/usr/share/zsh/vendor-completions/_helm` | `/usr/share/zsh/site-functions/_helm` |
| Cilium zsh 補完パス | `/usr/share/zsh/vendor-completions/_cilium` | `/usr/share/zsh/site-functions/_cilium` |
| `etc_default_dir` | `/etc/default` | `/etc/sysconfig` |

## 主な処理

- **kubeadm 設定と再初期化**: APIファミリに合わせて Pod/Service CIDR を並べ替え, `kubeadm reset` と `kubeadm init` を実行します。`service IP family ... must match public address family ...` の不整合を回避するための処理です。
- **Cilium 導入**: `kubeProxyReplacement=true`, `routingMode=native`, `autoDirectNodeRoutes=true`, `ipv4NativeRoutingCIDR`, `ipv6NativeRoutingCIDR` を values に反映し, kube-proxy を削除して Cilium を導入します。
- **Cluster Mesh 連携**: 条件を満たす場合, 共有CAの存在を検証して埋め込み kubeconfig を生成します。不足時は明示的に失敗させます。
- **BGP Control Plane**: `k8s_bgp.enabled=true` の場合に限り, BGP関連CRDの利用可能状態を待機してからマニフェストを適用します。
- **補完/運用ツール**: Helm/Cilium 補完ファイルと Cluster Mesh 用運用ツールを配布します。

## 設定例

### パターン 1: IPv4優先デュアルスタック (基本)

```yaml
# host_vars/k8sctrlplane01.local
k8s_ctrlplane_endpoint: 192.168.20.41
k8s_ctrlplane_port: 6443
k8s_cilium_version: "1.16.0"
k8s_pod_ipv4_network_cidr: "10.244.0.0/16"
k8s_pod_ipv6_network_cidr: "fdb6:6e92:3cfb::/56"
k8s_pod_ipv4_service_subnet: "10.254.0.0/16"
k8s_pod_ipv6_service_subnet: "fdb6:6e92:3cfb:feed::/112"
enable_firewall: true
firewall_backend:
  - ufw
```

### パターン 2: IPv6優先デュアルスタック

```yaml
# host_vars/k8sctrlplane01.local
k8s_ctrlplane_endpoint: "fdb6:6e92:3cfb:1::41"
k8s_ctrlplane_port: 6443
k8s_cilium_version: "1.16.0"
k8s_pod_ipv4_network_cidr: "10.244.0.0/16"
k8s_pod_ipv6_network_cidr: "fdb6:6e92:3cfb::/56"
k8s_pod_ipv4_service_subnet: "10.254.0.0/16"
k8s_pod_ipv6_service_subnet: "fdb6:6e92:3cfb:feed::/112"
```

### パターン 3: Cluster Mesh 用埋め込み kubeconfig を生成

```yaml
# host_vars/k8sctrlplane01.local
k8s_cilium_cm_cluster_name: cluster1
k8s_cilium_cm_cluster_id: 1
k8s_embed_kubeconfig_shared_ca_path: /etc/kubernetes/pki/ca.crt
k8s_cilium_shared_ca_enabled: true
```

### パターン 4: Cilium BGP Control Plane を有効化

```yaml
# host_vars/k8sctrlplane01.local
k8s_bgp:
  enabled: true
  node_name: k8sctrlplane01
  local_asn: 65011
  kubeconfig: /etc/kubernetes/admin.conf
  export_pod_cidr: true
  advertise_services: false
  neighbors:
    - peer_address: 192.168.30.49/32
      peer_asn: 65011
      peer_port: 179
      hold_time_seconds: 90
      connect_retry_seconds: 15
```

## 検証

### パターン A: 基本構成

**目的**: kubeadm, Cilium, Helm, firewall, kubeconfig 配布の基本動作が正常であることを確認します。

**実行コマンド**:

```bash
# 1. コントロールプレーン状態
kubectl --kubeconfig /etc/kubernetes/admin.conf get nodes -o wide

# 2. Cilium 状態
kubectl -n kube-system get ds cilium
cilium status

# 3. Helm リリース
helm list -n kube-system

# 4. kubeconfig 配布
ls -la /root/.kube/config
ls -la /home/ansible/.kube/config
ls -la /home/kube/.kube/config
```

**コマンド出力例**:

```text
# 1. コントロールプレーン状態
NAME             STATUS   ROLES           AGE   VERSION    INTERNAL-IP
k8sctrlplane01   Ready    control-plane   18h   v1.31.14   fdad:ba50:248b:1::41

# 2. Cilium 状態
NAME     DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE
cilium   3         3         3       3            3

# 3. Helm リリース
NAME            NAMESPACE     STATUS    CHART         APP VERSION
cilium          kube-system   deployed  cilium-1.16.0 1.16.0
multus-cni      kube-system   deployed  multus-cni-4.2.3 v4.2.3
whereabouts     kube-system   deployed  whereabouts-chart-0.9.2 v0.9.2

# 4. kubeconfig 配布
-rw------- 1 root    root    ... /root/.kube/config
-rw-r--r-- 1 ansible ansible ... /home/ansible/.kube/config
lrwxrwxrwx 1 root    root    ... /home/kube/.kube/config -> merged-kubeconfig.conf
```

**確認ポイント**:

- k8sctrlplane01 の STATUS が Ready であること
- cilium デーモンセットの DESIRED/CURRENT/READY が一致すること
- helm list に cilium が deployed で存在すること
- /root, /home/ansible, /home/kube の kubeconfig が存在すること

### パターン B: デュアルスタック順序確認 (IPv4優先デュアルスタック / IPv6優先デュアルスタック)

**目的**: デュアルスタック環境で, APIエンドポイントで指定されたIPアドレスファミリを優先し, Pod CIDRおよびService CIDRが正しい順序で適用されていることを確認します。

**実行コマンド**:

```bash
kubectl get nodes -o custom-columns=NAME:.metadata.name,POD-CIDRS:.spec.podCIDRs
kubectl cluster-info dump | grep service-cluster-ip-range
```

**コマンド出力例**:

```text
# Node podCIDRs の確認 (IPv6優先デュアルスタック)
NAME             POD-CIDRS
k8sctrlplane01   [fdb6:6e92:3cfb:200::/64 10.244.0.0/24]

# Node podCIDRs の確認 (IPv4優先デュアルスタック)
NAME             POD-CIDRS
k8sctrlplane01   [10.244.0.0/24 fdb6:6e92:3cfb:200::/64]

# service-cluster-ip-range の確認 (IPv6優先デュアルスタック)
--service-cluster-ip-range=fdb6:6e92:3cfb:feed::/112,10.254.0.0/16

# service-cluster-ip-range の確認 (IPv4優先デュアルスタック)
--service-cluster-ip-range=10.254.0.0/16,fdb6:6e92:3cfb:feed::/112
```

**確認ポイント**:

- IPv6優先デュアルスタックでは POD-CIDRS が IPv6,IPv4 の順序であること
- IPv4優先デュアルスタックでは POD-CIDRS が IPv4,IPv6 の順序であること
- IPv6優先デュアルスタックでは service-cluster-ip-range が IPv6,IPv4 の順序であること
- IPv4優先デュアルスタックでは service-cluster-ip-range が IPv4,IPv6 の順序であること

### パターン C: Cluster Mesh ツール生成

**前提**: `k8s_cilium_cm_cluster_name` と `k8s_cilium_cm_cluster_id` を定義済み。

**実行コマンド**:

```bash
# 1. スクリプトとドキュメントの配置
ls -la /opt/k8snodes/sbin/create-embedded-kubeconfig.py
ls -la /opt/k8snodes/docs/Readme-create-embedded-kubeconfig-JP.md

# 2. 生成結果
ls -la /home/kube/.kube/*-embedded.kubeconfig

# 3. 生成 kubeconfig の利用
kubectl --kubeconfig /home/kube/.kube/<cluster>-embedded.kubeconfig cluster-info
```

**コマンド出力例**:

```text
# 1. スクリプトとドキュメントの配置
-rwxr-xr-x 1 root root ... /opt/k8snodes/sbin/create-embedded-kubeconfig.py
-rw-r--r-- 1 root root ... /opt/k8snodes/docs/Readme-create-embedded-kubeconfig-JP.md

# 2. 生成結果
-rw------- 1 kube kube ... /home/kube/.kube/cluster1-embedded.kubeconfig
```

**確認ポイント**:

- create-embedded-kubeconfig.py と手順書が所定パスに存在すること
- cluster1-embedded.kubeconfig が生成済みであること
- 必要に応じて kubectl --kubeconfig /home/kube/.kube/cluster1-embedded.kubeconfig cluster-info が成功すること

### パターン D: Cilium BGP Control Plane 適用時確認

**実行コマンド**:

```bash
# 1. BGP 関連 CRD の存在確認
sudo -n kubectl --kubeconfig /etc/kubernetes/admin.conf get crd | \
  grep -E 'ciliumbgpadvertisements|ciliumbgppeerconfigs|ciliumbgpclusterconfigs'

# 2. BGP マニフェスト出力先確認
sudo -n ls -la /home/ansible/kubeadm/cilium/bgp
```

**確認ポイント**:

- `ciliumbgpadvertisements.cilium.io`, `ciliumbgppeerconfigs.cilium.io`, `ciliumbgpclusterconfigs.cilium.io` が表示されること
- `/home/ansible/kubeadm/cilium/bgp/` 配下に `cilium-bgp-resources-<node>.yml` が存在すること
- 必要に応じて `kubectl get ciliumbgpclusterconfigs -A` / `kubectl get ciliumbgppeerconfigs -A` / `kubectl get ciliumbgpadvertisements -A` を追加実行し, BGP リソースが作成済みであること

## トラブルシューティング

### kubeadm init が失敗する

**症状**: `kubeadm init` が `service IP family ... must match public address family ...` で失敗する。

**確認**:

```bash
cat {{ k8s_kubeadm_config_store }}/ctrlplane-kubeadm.config.yml
```

**原因**: APIエンドポイントのファミリと Service CIDR の順序が不一致。

**対処**: `k8s_ctrlplane_endpoint` と Pod/Service CIDR 変数を見直して再実行する。

### Cilium が起動しない

**症状**: `kubectl -n kube-system get pods` で cilium Pod が `CrashLoopBackOff`。

**確認**:

```bash
kubectl -n kube-system get pods -l k8s-app=cilium
kubectl -n kube-system logs ds/cilium --tail=200
cat {{ k8s_cilium_config_dir }}/cilium-install.yml
```

**原因**: `k8sServiceHost`, native routing CIDR, kube-proxy 削除順序の不整合。

**対処**: values と API 到達性を確認し, 必要なら `helm delete cilium -n kube-system` 後に再実行する。

### firewall 設定が反映されない

**症状**: 6443/tcp などが外部から到達しない。

**確認**:

```bash
# Debian/Ubuntu
sudo ufw status verbose

# RHEL
sudo firewall-cmd --list-ports
```

**原因**: `enable_firewall` が `false` または `firewall_backend` の指定不整合。

**対処**: 変数設定を修正し, ロールを再実行する。

### Cluster Mesh 用埋め込み kubeconfig 生成に失敗する

**症状**: `Abort when shared CA certificate is missing` で失敗する。

**確認**:

```bash
ls -la {{ k8s_embed_kubeconfig_shared_ca_path }}
```

**原因**: 共有CAファイル未生成, もしくは読み取り不可。

**対処**: `k8s-shared-ca` / `k8s-cilium-shared-ca` 側の生成結果を確認して再実行する。

### BGP マニフェスト適用で失敗する

**症状**: `k8s_bgp.neighbors must not be empty` や CRD未検出で失敗する。

**確認**:

```bash
kubectl get crd ciliumbgpadvertisements.cilium.io
kubectl get crd ciliumbgppeerconfigs.cilium.io
kubectl get crd ciliumbgpclusterconfigs.cilium.io
```

**期待される結果**:

```
NAME                                 CREATED AT
ciliumbgpadvertisements.cilium.io    2026-03-05T10:30:15Z
```

```
NAME                              CREATED AT
ciliumbgppeerconfigs.cilium.io    2026-03-05T10:30:15Z
```

```
NAME                                CREATED AT
ciliumbgpclusterconfigs.cilium.io   2026-03-05T10:30:15Z
```

**確認ポイント**:

- 各CRD (`ciliumbgpadvertisements.cilium.io`, `ciliumbgppeerconfigs.cilium.io`, `ciliumbgpclusterconfigs.cilium.io`) が存在すること
- これらのCRDが存在しない場合は, Cilium がBGP Control Plane機能を有効化していないか, Ciliumのバージョンが古い可能性があります

**原因**: `k8s_bgp` 設定不足, もしくは Cilium 側 CRD の未準備。

**対処**: `k8s_bgp.neighbors` を含む設定を修正し, Cilium が CRD を作成したことを確認して再実行する。

## 留意事項

- **破壊的操作**: `config.yml` は `kubeadm reset` を実行します。既存クラスタ適用時は必ず停止計画を立ててください。
- **Helm リポジトリの再構成**: `config-helm.yml` は既存 Helm リポジトリを全削除して `cilium` を再登録します。既存運用がある場合は事前に退避してください。
- **再実行時の Cilium**: `helm install cilium` は同名リリースが残っていると失敗します。必要に応じて `helm delete cilium -n kube-system` を実施してください。
- **ロール依存**: 本ロールは `k8s-common` 実行後を前提にしています。
- **テンプレート依存**: Cilium BGP Control Plane のマニフェスト生成は, `k8s-common/templates/cilium-bgp-resources.yml.j2` を参照する実装です。`k8s-ctrlplane` 側実装は `k8s-common` 側テンプレートに依存しています。
- **共有CA依存**: `k8s_cilium_shared_ca_enabled: true` の場合, `k8s-cilium-shared-ca` の実行結果が前提になります。
- **補完無効化**: `k8s_helm_cli_completion_enabled: false` または `k8s_cilium_cli_completion_enabled: false` でシェル用補完ファイル生成をスキップできます。