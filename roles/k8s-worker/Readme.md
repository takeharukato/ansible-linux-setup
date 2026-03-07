# k8s-worker ロール

Kubernetes ワーカーノードを Kubernetes クラスタへ参加させるためのロールです。`k8s-common` で整えた前提の上に, 低遅延化向けの OS チューニング, ワーカーノードを Kubernetes クラスタへ参加させる設定, ワーカーノードで必要な通信を許可するファイアウォール設定 (NodePort を使う場合の設定を含む), Cilium BGP Control Plane の設定をまとめて適用します。既存ワーカーノードのスケジュール停止 (`kubectl cordon`), Pod退避 (`kubectl drain`), Kubernetes クラスタからの削除 (`kubectl delete node`) まで一括で扱います。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Application Programming Interface | API | アプリケーション同士がやり取りする方法を定めた仕様。 |
| Custom Resource Definition | CRD | Kubernetes APIを拡張してユーザ独自のリソース種別を定義する仕組み。 |
| Role-Based Access Control | RBAC | ユーザやサービスアカウントが実行可能な操作を役割(Role)で制限する仕組み。 |
| Service Account | - | Kubernetes内部でPodが他のリソースにアクセスする際に用いる仮想的なアカウント。 |
| ClusterRole | - | Kubernetes クラスタ全体に適用される権限の集合。 |
| ClusterRoleBinding | - | ClusterRoleをユーザやサービスアカウントに紐付ける仕組み。 |
| Role | - | 特定の名前空間内で有効な権限の集合。 |
| RoleBinding | - | Roleをユーザやサービスアカウントに紐付ける仕組み。 |
| 名前空間 ( namespace )  | - | Kubernetes内部でリソースを論理的に分離する単位。 |
| ポッド ( Pod ) | - | Kubernetes上で動作するコンテナの最小単位。 |
| デーモンセット ( DaemonSet ) | - | Kubernetes クラスタ内の全 Kubernetes ノード(または指定した一部の Kubernetes ノード)で必ずPodを1つずつ起動させるリソース。 |
| デプロイメント ( Deployment ) | - | 指定した数のPodを維持し, ローリングアップデート等を管理するリソース。 |
| StatefulSet | - | 状態を持つアプリケーションのPodを順序付けて管理するリソース。 |
| サービス ( Service ) | - | Podへのアクセスを抽象化し, 負荷分散やサービスディスカバリを提供するリソース。 |
| Ingress | - | Kubernetes クラスタ外部からHTTP/HTTPS通信を受け付け, 内部のServiceへルーティングする仕組み。 |
| コンフィグマップ ( ConfigMap ) | - | 設定情報を保持し, Podへ環境変数やファイルとして注入するリソース。 |
| シークレット ( Secret ) | - | 機密情報を保持し, Podへ安全に注入するリソース。 |
| PersistentVolume | PV | Kubernetes クラスタ内で利用可能なストレージリソースを表すオブジェクト。 |
| PersistentVolumeClaim | PVC | ユーザがPVを要求する際に利用するリソース。 |
| StorageClass | - | 動的にPVをプロビジョニングする際のストレージ種別を定義するリソース。 |
| Kubernetes ノード ( Kubernetes Node ) | - | Kubernetes クラスタを構成する物理マシンまたは仮想マシン。 |
| コントロールプレーンノード ( Control Plane Node ) | - | Kubernetes クラスタ全体を管理, 制御する中枢ノード群。kube-apiserver, kube-controller-manager, kube-schedulerなどが動作する。 |
| ワーカーノード ( Worker Node ) | - | 実際にアプリケーションのPodを実行する Kubernetes ノード。 |
| kube-apiserver | - | KubernetesのAPIリクエストを受け付け, etcdへの読み書きを仲介するコンポーネント。 |
| kube-controller-manager | - | Deployment, ReplicaSetなど各種コントローラを実行し, Kubernetes クラスタの状態を監視, 調整するコンポーネント。 |
| kube-scheduler | - | 新規作成されたPodを適切な Kubernetes ノードへ配置するコンポーネント。 |
| kubelet | - | 各 Kubernetes ノード上で動作し, Podの起動, 停止, 監視を行うエージェント。 |
| kube-proxy | - | 各 Kubernetes ノード上でServiceのネットワークルールを管理するコンポーネント。 |
| etcd | - | Kubernetes の Kubernetes クラスタ状態を保存する分散Key-Valueストア。 |
| Container Network Interface | CNI | コンテナ間のネットワーク接続を標準化するプラグイン仕様。 |
| Cilium | - | eBPFを活用した高性能なCNIプラグイン。ネットワークポリシーやサービスメッシュ機能を提供する。 |
| Serviceエンドポイント ( Service Endpoint ) | - | Serviceのバックエンドとして通信を受けるPod, または, 当該の通信を受けるPodに加え, 当該の通信を受けるPodへ通信を届けるためのネットワーク上の転送先情報全体を指す。 |
| Serviceエンドポイント情報 ( Service Endpoint Information ) | - | Serviceエンドポイントを特定して転送先を決めるための情報。主にバックエンドPodのIPアドレス, ポート番号, プロトコル, 所属 Kubernetes クラスタ名(またはクラスタ識別子)で構成される。 |
| Multus | - | 複数のCNIプラグインを同時に使用できるようにするメタCNIプラグイン。 |
| Container Runtime Interface | CRI | Kubernetesがコンテナランタイムと通信するための標準インターフェース。 |
| containerd | - | Dockerから分離された軽量なコンテナランタイム。 |
| kubeadm | - | Kubernetes クラスタの初期構築と管理を支援する公式ツール。 |
| kubectl | - | Kubernetes クラスタを操作するためのコマンドラインツール。 |
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
| Toleration | - | PodがTaintを持つ Kubernetes ノードへ配置されることを許可する設定。 |
| Uncomplicated Firewall | UFW | Ubuntu向けの簡易ファイアウォール管理ツール。iptablesのフロントエンドとして動作し, 直感的なコマンドでルール設定が可能。 |
| Border Gateway Protocol | BGP | インターネット上の自律システム間でルーティング情報を交換するための外部ゲートウェイプロトコル。Kubernetes環境ではCilium BGP Control Planeによるネットワーク経路制御に使用される。 |
| Cilium BGP Control Plane | - | Cilium が提供する BGP 連携機能。Kubernetes ノード情報や Service 情報に基づく経路広告を外部ルータへ配布するために利用する。 |
| CiliumBGPAdvertisement | - | Cilium BGP Control Plane で広告対象のプレフィックスや属性を定義するカスタムリソース。 |
| CiliumBGPPeerConfig | - | Cilium BGP Control Plane で BGP ピアとのセッション設定を定義するカスタムリソース。 |
| CiliumBGPClusterConfig | - | Cilium BGP Control Plane で Kubernetes ノード単位の BGP 構成を定義するカスタムリソース。 |
| NodePort | - | Service の公開方式の一つで, 各 Kubernetes ノードの特定ポートを開放して Kubernetes クラスタ外部からのアクセスを受け付ける仕組み。 |
| Classless Inter-Domain Routing | CIDR | IP アドレス範囲をプレフィックス長で表現する記法。ネットワーク経路や許可範囲の指定に利用される。 |
| ReplicaSet | - | 指定した数の Pod レプリカを維持する Kubernetes リソース。通常は Deployment が内部的に管理する。 |
| kubeconfig | - | kubectlや他のツールが Kubernetes クラスタにアクセスするための設定ファイル。接続先 Kubernetes クラスタ情報, 認証情報, コンテキストを含む。 |
| Extended Berkeley Packet Filter | eBPF | Linux カーネル内で安全にプログラムを実行する仕組み。高性能なパケット処理や観測機能の実装に利用される。 |
| Hypertext Transfer Protocol | HTTP | Web 通信で利用されるアプリケーション層プロトコル。 |
| Hypertext Transfer Protocol Secure | HTTPS | TLS により暗号化された HTTP 通信。 |
| Internet Protocol | IP | ネットワーク機器間でパケットを配送するための基盤プロトコル。 |
| Operating System | OS | ハードウェア資源の管理とアプリケーション実行基盤を提供する基本ソフトウェア。 |
| systemd スライス ( systemd slice ) | - | Linux の systemd でプロセスを階層的にまとめて管理するための単位。CPU やメモリなどの資源制御に利用する。 |
| Red Hat Enterprise Linux | RHEL | Red Hat 社が提供する Linux ディストリビューション。RHEL9 はそのメジャーバージョン 9 を指す。 |
| Secure Shell | SSH | 暗号化されたリモート接続とコマンド実行を提供するプロトコル。 |
| Certificate Authority | CA | デジタル証明書を発行し, 署名する信頼された機関。Kubernetesでは各種コンポーネント間の通信を保護するために使用される。 |
| Basic Input/Output System | BIOS | 起動時にハードウェア初期化とブート処理を実行するファームウェア方式。 |
| Unified Extensible Firmware Interface | UEFI | BIOS を拡張, 置換するファームウェア方式。 |
| Central Processing Unit | CPU | 命令実行と演算処理を担う主要な計算装置。 |
| Interrupt Request | IRQ | ハードウェアの一部からプロセッサーに直ちに送信されるシグナル。IRQ は Interrupt ReQuest の略。 |
| GNU GRand Unified Bootloader | GRUB | Linux 系 OS で広く利用されるブートローダ。カーネル起動引数の設定を管理する。 |

## 前提条件

- 対象 OS: Debian/Ubuntu 系 (Ubuntu 24.04 を想定), RHEL9 系 (AlmaLinux 9.6 等を想定)
- `roles/k8s-common` の実行が完了していること (`kubeadm`, `kubelet`, `containerd` が導入済みであること)
- コントロールプレーンノードで `kubectl`, `kubeadm`, `openssl` が実行可能であること
- 対象ホストで管理者権限 (sudo) が利用可能であること
- `k8s_ctrlplane_endpoint`, `k8s_ctrlplane_port`, `k8s_ctrlplane_host` が適切に設定済みであること

## 実行フロー

1. [roles/k8s-worker/tasks/load-params.yml](roles/k8s-worker/tasks/load-params.yml#L8-L23) で OS ファミリ別パッケージ情報と共通変数 (`cross-distro.yml`, `all-config.yml`, `k8s-api-address.yml`) を読み込みます。
2. [roles/k8s-worker/tasks/main.yml](roles/k8s-worker/tasks/main.yml#L12-L15) で `package.yml`, `directory.yml`, `user_group.yml`, `service.yml` を include します (現状はプレースホルダ)。
3. [roles/k8s-worker/tasks/config-k8sworker-firewall.yml](roles/k8s-worker/tasks/config-k8sworker-firewall.yml#L8-L195) で `enable_firewall` と `firewall_backend` に応じたファイアウォール設定を行います。
4. [roles/k8s-worker/tasks/config-irq-balance.yml](roles/k8s-worker/tasks/config-irq-balance.yml) で低遅延構成時に `irq balance`パッケージ(`irq_balance_package`変数で定義) を削除します。
5. [roles/k8s-worker/tasks/config-shielding.yml](roles/k8s-worker/tasks/config-shielding.yml#L8-L27) で `k8s_systemd_slices` 配下に CPU割り当て設定ファイルを生成します。
6. [roles/k8s-worker/tasks/config-worker-node.yml](roles/k8s-worker/tasks/config-worker-node.yml#L11-L354) で CPU レンジ算出, GRUBのOSカーネル起動パラメタを設定, CPU割り当てスクリプト配置, 初回リブートを実施します。
7. [roles/k8s-worker/tasks/config.yml](roles/k8s-worker/tasks/config.yml#L8-L186) で kube-apiserver 待機, Kubernetes クラスタ参加設定生成, 既存ワーカーノード整理, ワーカーノード構成リセット (`kubeadm reset`), Kubernetes クラスタへ参加 (`kubeadm join`), `containerd` と `kubelet` の自動起動有効化 (`enabled: true`), 二度目のリブートを実施します。
8. [roles/k8s-worker/tasks/config-cilium-bgp-cplane.yml](roles/k8s-worker/tasks/config-cilium-bgp-cplane.yml#L8-L105) で `k8s_bgp.enabled: true` の場合に Cilium BGP Control Plane マニフェストを生成, CRD 確認後に適用します。

## 主要変数

### API 待機設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_ctrlplane_endpoint` | 各 `host_vars` | コントロールプレーン API の到達先アドレス。本ロールでは, kubelet 側で優先される Pod CIDR のIPアドレスファミリと Kubernetes API エンドポイント広告アドレスのアドレスファミリ整合を確実にするため, IPアドレスを指定します。 |
| `k8s_api_wait_host` | `{{ k8s_ctrlplane_endpoint }}` | kube-apiserver 待機先ホスト。 |
| `k8s_api_wait_port` | `{{ k8s_ctrlplane_port }}` | kube-apiserver 待機先ポート。`k8s_ctrlplane_endpoint` にポート番号を含めた場合はその値を使用し, ポート指定がない場合は `6443` を使用します。 |
| `k8s_api_wait_timeout` | `600` | kube-apiserver 待機タイムアウト (秒)。 |
| `k8s_api_wait_delay` | `2` | 待機開始前ディレイ (秒)。 |
| `k8s_api_wait_sleep` | `1` | 待機リトライ間隔 (秒)。 |
| `k8s_api_wait_delegate_to` | `localhost` | 待機処理を実行する接続元ホスト。 |

補足 (未定義時の動作):
- `k8s_ctrlplane_endpoint` または `k8s_ctrlplane_host` が未定義, もしくは空文字列の場合, `roles/k8s-worker/tasks/main.yml` のガード条件により `k8s-worker` の実処理タスクはスキップされます。
- `k8s_ctrlplane_port` は通常 `k8s_ctrlplane_endpoint` から自動算出されるため, 個別に定義しなくても動作します。
- `k8s_ctrlplane_endpoint` にポート番号を含めない場合は, `k8s_ctrlplane_port` として `6443` が自動的に使われます。

### containerd 待機設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_containerd_wait_timeout` | `60` | containerd ソケット待機タイムアウト (秒)。 |
| `k8s_containerd_wait_delegate_to` | `localhost` | containerd 待機処理を実行する接続元ホスト。 |

### Kubernetes オペレータユーザ設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_operator_user` | `kube` | Kubernetes 操作用ユーザ名。 |
| `k8s_operator_home` | `/home/kube` | Kubernetes 操作用ユーザのホームディレクトリ。 |
| `k8s_operator_shell` | `/bin/bash` | Kubernetes 操作用ユーザのシェル。 |
| `k8s_operator_groups_list` | `{{ adm_groups }}` | Kubernetes 操作用ユーザが所属するグループ一覧。 |

### セットアップツール配置先

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_node_setup_tools_prefix` | `/opt/k8snodes` | ツール配置プレフィックス。 |
| `k8s_node_setup_tools_dir` | `{{ k8s_node_setup_tools_prefix }}/sbin` | CPU割り当てスクリプト等の配置先。 |
| `k8s_node_setup_tools_docs_dir` | `{{ k8s_node_setup_tools_prefix }}/docs` | ドキュメント配置先。 |
| `k8s_embed_kubeconfig_script_path` | `{{ k8s_node_setup_tools_dir }}/create-embedded-kubeconfig.py` | kubeconfig 生成スクリプト配置先。 |
| `k8s_embed_kubeconfig_output_dir` | `{{ k8s_operator_home }}/.kube` | kubeconfig 出力先。 |

### ワーカーノード固有設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_ctrlplane_host` | 各 `host_vars` | `delegate_to` で `kubeadm`, `kubectl` を実行するコントロールプレーンノード。 |
| `k8s_kubeadm_config_store` | `/home/ansible/kubeadm` | `kubeadm.config.yml` や Cilium BGP Control Plane マニフェスト保存先。 |
| `k8s_kubeadm_ignore_preflight_errors_arg` | `--ignore-preflight-errors=all` | `kubeadm join` に渡す preflight オプション。 |
| `k8s_drain_timeout_minutes` | `5` | Pod退避 (`kubectl drain`) のタイムアウト (分)。 |
| `k8s_worker_delete_wait_sec` | `5` | ワーカーノード削除 (`kubectl delete node`) 後の待機時間 (秒)。 |
| `reboot_timeout_sec` | `600` | 再起動後の復帰待ちタイムアウト (秒)。 |

### ファイアウォール / NodePort 設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `enable_firewall` | `false` (`vars/all-config.yml`) | `true` の場合にファイアウォール設定を有効化。 |
| `firewall_backend` | OS 判定で `['ufw']` または `['firewalld']` | 使用するファイアウォール実装。 |
| `k8s_worker_enable_nodeport` | `false` | NodePort 範囲の開放有無。 |
| `k8s_worker_nodeport_range` | `30000-32767` | NodePort 開放範囲。 |
| `k8s_worker_node_ports_from_ctrlplane` | `['10250/tcp']` | コントロールプレーンから許可するポート。 |

### CPU / systemd スライス設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_reserved_system_cpus_default` | 未定義 | システム処理向け CPU 範囲。 |
| `k8s_systemd_slices` | `['init.scope.d', 'system.slice.d', 'user.slice.d', 'user-.slice.d']` | CPU割り当て設定ファイルの対象スライス一覧。 |

### Cilium BGP Control Plane 設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_bgp.enabled` | 未定義 | `true` 時に Cilium BGP Control Plane マニフェストを生成, 適用。 |
| `k8s_bgp.neighbors` | 未定義 | BGP ピア定義。`k8s_bgp.enabled: true` の場合は必須。 |
| `k8s_bgp.node_name` | `ansible_hostname` | BGP リソース名生成に利用するワーカーノード名。 |
| `k8s_bgp.apply_delegate` | `{{ k8s_ctrlplane_host }}` | BGP マニフェストを適用するホスト。 |

補足 (未定義時の動作):
- `k8s_bgp.node_name` が未定義, もしくは空文字列の場合は `ansible_hostname` が自動的に使われます。
- `k8s_bgp.neighbors` 配下の `peer_address` または `peer_asn` が未定義, もしくは空文字列のエントリは, マニフェスト生成時に当該ピア設定を出力しません。
- `k8s_bgp.neighbors` の全エントリが上記条件に該当する場合は, BGP ピア設定が空になります。意図した経路広告を行うため, 有効な `peer_address` と `peer_asn` を少なくとも 1 組設定してください。

## 主な処理

- **ファイアウォール構成**: `enable_firewall` が有効な環境で UFW/firewalld を初期化し, 10250/tcp などの制御プレーン向けポートと NodePort 範囲を恒久的に開放します。
- **CPU シールドの準備**: systemd スライス単位で使用可能CPU範囲 (`AllowedCPUs`) を固定します。これにより, IRQを受け付けるCPUを固定するスクリプトを実行できる状態にします。
- **GRUB と低遅延調整**: `k8s_reserved_system_cpus_default` に基づき `nohz_full` や `isolcpus` などのカーネルパラメータを更新し, ワーカースレッドと IRQ をアプリケーション向け / システム処理向けに分離します。
- **Kubernetes クラスタ参加処理**: 既存ワーカーノードのスケジュール停止 (`kubectl cordon`), Pod退避 (`kubectl drain`), Kubernetes クラスタからの削除 (`kubectl delete node`), ワーカーノード構成リセット (`kubeadm reset`), Kubernetes クラスタへ参加 (`kubeadm join --config`) を自動化し, `containerd` は起動 (`state: started`) と自動起動有効化 (`enabled: true`), `kubelet` は自動起動有効化 (`enabled: true`) と再起動を実施します。
- **Cilium BGP Control Plane**: Kubernetes ノード固有の識別子で CRD マニフェストを生成し, CiliumBGPAdvertisement / CiliumBGPPeerConfig / CiliumBGPClusterConfig を適用して Pod/Service CIDR をルータへ広告します。
- **再起動とユーティリティ登録**: CPU割り当てサービス (`pin-worker-queue`, `pin-irqs`) を `enabled` 登録し, OS チューニング後と Kubernetes クラスタ参加後にそれぞれリブートします。

## テンプレート／ファイル

| テンプレート | 生成ファイル | 説明 |
| --- | --- | --- |
| [roles/k8s-worker/templates/worker-kubeadm.config.j2](roles/k8s-worker/templates/worker-kubeadm.config.j2) | kubeadm.config.yml ( 対象ホストの `k8s_kubeadm_config_store` 配下, 規定値: `/home/ansible/kubeadm/kubeadm.config.yml` ) | Kubernetes クラスタ参加 (`kubeadm join`) に渡す設定をまとめ, トークンと CA ハッシュを組み込んだ構成ファイルを生成します。 |
| [roles/k8s-worker/templates/systemd-cpuset.conf.j2](roles/k8s-worker/templates/systemd-cpuset.conf.j2) | 40-cpuset.conf ( 対象ホストの各 systemd スライス配下, 規定値: `/etc/systemd/system/{init.scope.d\|system.slice.d\|user.slice.d\|user-.slice.d}/40-cpuset.conf` ) | CPU シールド向けに使用可能CPU範囲 (`AllowedCPUs`) を固定し, k8s_systemd_slices の各ドロップインで共有する設定を作成します。 |
| [roles/k8s-worker/templates/pin-worker-queue.sh.j2](roles/k8s-worker/templates/pin-worker-queue.sh.j2) | pin-worker-queue.sh ( 対象ホストの `k8s_node_setup_tools_dir` 配下, 規定値: `/opt/k8snodes/sbin/pin-worker-queue.sh` ) | workqueue のアンバウンドスレッドをアプリケーション向け CPU に割り当てるセットアップスクリプトを配置します。 |
| [roles/k8s-worker/templates/pin-worker-queue.service.j2](roles/k8s-worker/templates/pin-worker-queue.service.j2) | pin-worker-queue.service ( 対象ホストの systemd ユニットディレクトリ, 規定値: `/etc/systemd/system/pin-worker-queue.service` ) | pin-worker-queue.sh を1回だけ実行し, ブート後に CPU割り当てを適用する systemd ユニットを登録します。 |
| [roles/k8s-worker/templates/pin-irqs.py.j2](roles/k8s-worker/templates/pin-irqs.py.j2) | pin-irqs.py ( 対象ホストの `k8s_node_setup_tools_dir` 配下, 規定値: `/opt/k8snodes/sbin/pin-irqs.py` ) | 割込みをシステム処理向け CPU へ割り当てる Python スクリプトを配備します。 |
| [roles/k8s-worker/templates/pin-irqs.service.j2](roles/k8s-worker/templates/pin-irqs.service.j2) | pin-irqs.service ( 対象ホストの systemd ユニットディレクトリ, 規定値: `/etc/systemd/system/pin-irqs.service` ) | pin-irqs.py を起動して IRQ アフィニティを適用する systemd ユニットを登録します。 |
| [roles/k8s-common/templates/cilium-bgp-resources.yml.j2](roles/k8s-common/templates/cilium-bgp-resources.yml.j2) | Cilium BGP Control Plane マニフェスト ( 対象ホストの `cilium_bgp_manifest_dir` 配下, 規定値: `/home/ansible/kubeadm/cilium/bgp/` ) | Kubernetes ノード固有の識別子を含む CiliumBGP* リソースをまとめたマニフェストを生成し, apply_delegate で指定したホストに保存します。 |

## ハンドラ

| ハンドラ | トリガー | 説明 |
| --- | --- | --- |
| [roles/k8s-worker/handlers/kubelet.yml](roles/k8s-worker/handlers/kubelet.yml) | `notify: kubelet_restarted_and_enabled` | kubelet の daemon-reload と再起動, enable をまとめて実施し, Kubernetes クラスタ参加後のサービス状態を整えます。 |
| [roles/k8s-worker/handlers/reload-firewall.yml](roles/k8s-worker/handlers/reload-firewall.yml) | `notify: reload firewalld` / `notify: reload ufw` | firewall_backend に応じて firewalld もしくは UFW を再読み込みし, NodePort などのポート開放設定を反映させます。 |
| [roles/k8s-worker/handlers/reboot-node.yml](roles/k8s-worker/handlers/reboot-node.yml) | `notify: reboot_node_handler` | リブートを実行し, GRUBのOSカーネル起動パラメタ設定や Kubernetes クラスタ参加 (`kubeadm join`) 後の状態を確定させます。 |

## OS 差異

### ファイアウォール設定の差異

| 項目 | RHEL 系 | Debian/Ubuntu 系 |
| --- | --- | --- |
| バックエンド | firewalld | UFW |
| ルール適用方法 | 条件を細かく指定するルール (rich rule)とポート開放 | allow ルール |
| 反映方法 | `firewall-cmd --reload` | `ufw reload` |
| NodePort 範囲表記 | `30000-32767/tcp` | `30000:32767/tcp` |

### GRUB 更新方法の差異

| 項目 | RHEL 系 | Debian/Ubuntu 系 |
| --- | --- | --- |
| 更新コマンド | `grub2-mkconfig` | `update-grub` |
| 出力先 | BIOS/UEFI を判別して `/boot/grub2/grub.cfg` または `/boot/efi/EFI/*/grub.cfg` | 既定の GRUB 設定先 |

## 設定例

本節では, `host_vars`ディレクトリ配下に配置するワーカーノードの設定内容を例を用いて説明します。

### 基本設定

Kubernetesクラスタのワーカーノードの基本設定項目の設定例を以下に示します。これらの設定項目は, 低遅延構成, Cilium BGP Control Plane機能の使用有無に依らず共通です:

```yaml
# host_vars/k8sworker0101.local
k8s_ctrlplane_endpoint: "192.168.40.11"
k8s_ctrlplane_port: 6443
k8s_ctrlplane_host: "k8sctrlplane01.local"
```

ポイント:
- `k8s_ctrlplane_endpoint`: ワーカーノードが接続する Kubernetes API の宛先アドレスを指定します。kubelet 側で優先される Pod CIDR のIPアドレスファミリと Kubernetes API エンドポイント広告アドレスのアドレスファミリを一致させる必要があるため, IPアドレスで宛先を設定してください。
- `k8s_ctrlplane_port`: Kubernetes API の待受ポート番号を指定します。標準構成では `6443` を設定します。
- `k8s_ctrlplane_host`: Ansible の `delegate_to` で `kubeadm` や `kubectl` を実行するコントロールプレーンノードのインベントリ名を指定します。`inventory/hosts` と `host_vars` に定義したホスト名を設定してください。

### 低遅延構成

低遅延処理を行うKubernetesクラスタのワーカーノード設定例を以下に示します:

```yaml
# 低遅延構成用の設定
k8s_reserved_system_cpus_default: "0-3"
k8s_systemd_slices:
  - init.scope.d
  - system.slice.d
  - user.slice.d
  - "user-.slice.d"
```

ポイント:
- 例えば, 論理CPU番号0番から3番までのCPUをシステム処理向けCPUとして設定する場合, `k8s_reserved_system_cpus_default`を, `k8s_reserved_system_cpus_default: "0-3"` のように指定します。
  - `0-3` は論理CPU番号 `0,1,2,3` を意味します。Linux の論理CPU番号は通常 `0` から始まります。
  - 論理CPU番号は `lscpu -e=CPU,CORE,SOCKET,NODE` や `cat /sys/devices/system/cpu/online` で確認してから, 実機のトポロジに合わせて範囲を決めてください。
- `k8s_systemd_slices:` に `init.scope.d`, `system.slice.d`, `user.slice.d`, `user-.slice.d` を列挙して, CPU 割り当て対象の systemd スライスを指定します。
- 低遅延化の確認では CPU割り当てサービス (`pin-worker-queue`, `pin-irqs`) の状態確認を必ず行ってください。

### Cilium BGP Control Plane 有効構成

Cilium BGP Control Planeを有効にしたコントロールプレインノード配下のKubernetesクラスタを構成するワーカーノードの設定例を以下に示します:


```yaml
# Cilium BGP Control Plane機能有効時の設定
k8s_bgp:
  enabled: true
  node_name: "k8sworker0102"
  neighbors:
    - peer_address: "192.168.40.49"
      peer_asn: 65011
```

ポイント:
- `k8s_bgp.enabled: true` を指定して Cilium BGP Control Plane 機能を有効化するよう指示します。
- `k8s_bgp.node_name: "k8sworker0102"` のようにノード識別子を指定します。
- `k8s_bgp.neighbors:` 配下には次の項目を必ず指定します。
  - `peer_address`: ワーカーノードからBGPセッションを張る相手 (外部ルータやL3スイッチ) のIPアドレスを指定します。
  - `peer_asn`: `peer_address` で指定した相手装置側のAS番号 (Autonomous System Number) を指定します。

なお, Cilium BGP Control Plane マニフェストの生成, 適用は `k8s_bgp.apply_delegate` で指定したホスト (規定値: `k8s_ctrlplane_host`の設定値) で実施されます。

## 設定内容の検証

### 前提条件

- ロール実行が成功していることを確認してください。
- コントロールプレーンノードから `kubectl` が実行可能であることを確認してください。
- 対象ワーカーノードへ SSH 接続できることを確認してください。

### 1. Kubernetes ノード登録状態の確認

**実施Kubernetes ノード種別**: コントロールプレーンノード

**コマンド**:

```bash
kubectl get nodes -o wide
```

**実行例**:

```plaintext
NAME             STATUS   ROLES           AGE   VERSION    INTERNAL-IP                EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION      CONTAINER-RUNTIME
k8sctrlplane01   Ready    control-plane   26h   v1.31.14   fdad:ba50:248b:1::41       <none>        Ubuntu 24.04.3 LTS   6.8.0-101-generic   containerd://1.7.28
k8sworker0101    Ready    <none>          25h   v1.31.14   fdad:ba50:248b:1::42       <none>        Ubuntu 24.04.3 LTS   6.8.0-101-generic   containerd://1.7.28
k8sworker0102    Ready    <none>          25h   v1.31.14   fdad:ba50:248b:1::43       <none>        Ubuntu 24.04.3 LTS   6.8.0-101-generic   containerd://1.7.28
```

**確認ポイント**:
- 対象ワーカーノードの `STATUS`列が`Ready`となっていることを確認してください。

### 2. kubelet サービス状態の確認

**実施Kubernetes ノード種別**: ワーカーノード

**コマンド**:

```bash
systemctl status kubelet
```

**実行例**:

```plaintext
● kubelet.service - kubelet: The Kubernetes Node Agent
     Loaded: loaded (/usr/lib/systemd/system/kubelet.service; enabled; preset: enabled)
     Active: active (running) since Fri 2026-03-06 02:50:03 JST; 1 day 1h ago
   Main PID: 1027 (kubelet)
```

**確認ポイント**:
- `active (running)` であることを確認してください。
- `enabled;` が付いていることを確認してください。

### 3. kubelet ログの確認

**実施Kubernetes ノード種別**: ワーカーノード

**コマンド**:

```bash
journalctl -u kubelet -n 50 --no-pager
```

**実行例**:

```plaintext
3月 07 04:30:44 k8sworker0101 kubelet[1027]: E0307 ... "Unable to read config path" ... path="/etc/kubernetes/manifests"
```

**確認ポイント**:
- `failed`, `error` が連続して出力されていないことを確認してください。
- Kubernetes ノード登録に関する正常ログが含まれることを確認してください。

### 4. CPU 予約設定の確認 (低遅延構成時)

**実施Kubernetes ノード種別**: 低遅延構成を適用したワーカーノード

**コマンド**:

```bash
cat /etc/systemd/system/*/40-cpuset.conf
cat /proc/cmdline
```

**実行例**:

```plaintext
# /etc/systemd/system/init.scope.d/40-cpuset.conf
[Slice]
AllowedCPUs="0-1"

# /proc/cmdline
BOOT_IMAGE=/boot/vmlinuz-6.8.0-101-generic ... nohz_full=2-3 isolcpus=managed,2-3 rcu_nocbs=2-3 irqaffinity=0-1 workqueue.unbound_cpus=0-1 ...
```

**確認ポイント**:
- 使用可能CPU範囲 (`AllowedCPUs`) が期待値になっていることを確認してください。
- カーネルパラメータに CPU 分離のためのオプションが含まれることを確認してください。

### 5. CPU 割り当て固定サービスの確認 (低遅延構成時)

**実施Kubernetes ノード種別**: 低遅延構成を適用したワーカーノード

**コマンド**:

```bash
systemctl status pin-worker-queue pin-irqs
```

**実行例 (先頭抜粋)**:

```plaintext
○ pin-worker-queue.service - Pin all unbounded worker queues to system CPUs
  Loaded: loaded (/etc/systemd/system/pin-worker-queue.service; enabled; preset: enabled)
  Active: inactive (dead) since Fri 2026-03-06 02:50:09 JST; 1 day 1h ago

○ pin-irqs.service - Pin all IRQs to housekeeping CPUs
  Loaded: loaded (/etc/systemd/system/pin-irqs.service; enabled; preset: enabled)
  Active: inactive (dead) since Fri 2026-03-06 02:50:09 JST; 1 day 1h ago
```

**確認ポイント**:
- 1回だけ起動するサービス (systemdのone-shotサービス)として実行された後に, `inactive (dead)` で終了していることを確認してください。
- `enabled;` が付いていることを確認してください。
- 直近の実行が失敗していないことを確認してください。

### 6. Cilium BGP Control Plane リソースの確認 (Cilium BGP Control Plane 有効構成時)

**実施Kubernetes ノード種別**: コントロールプレーンノード

**コマンド**:

```bash
kubectl get ciliumbgpclusterconfigs.cilium.io -A
kubectl get ciliumbgppeerconfigs.cilium.io -A
kubectl get ciliumbgpadvertisements.cilium.io -A
```

**実行例 (Cilium BGP Control Plane 有効時)**:

```plaintext
$ kubectl get ciliumbgpclusterconfigs.cilium.io -A
NAMESPACE   NAME                 AGE
default     k8sworker0102-bgp    2m

$ kubectl get ciliumbgppeerconfigs.cilium.io -A
NAMESPACE   NAME                           AGE
default     k8sworker0102-peer-65011       2m

$ kubectl get ciliumbgpadvertisements.cilium.io -A
NAMESPACE   NAME                               AGE
default     k8sworker0102-podcidr-service      2m
```

**実行例 (Cilium BGP Control Plane 無効時, CRD 導入済み)**:

```plaintext
$ kubectl get ciliumbgpclusterconfigs.cilium.io -A
No resources found

$ kubectl get ciliumbgppeerconfigs.cilium.io -A
No resources found

$ kubectl get ciliumbgpadvertisements.cilium.io -A
No resources found
```

**実行例 (CRD 未導入時)**:

```plaintext
error: the server doesn't have a resource type "ciliumbgpclusterconfigs"
```

**確認ポイント**:
- Cilium BGP Control Plane を有効化した環境では, BGP 関連リソースが表示されることを確認してください。
- Cilium BGP Control Plane を無効化し, CRD が導入済みの環境では `No resources found` が表示されることを確認してください。
- `resource type` が存在しない場合は, Cilium BGP Control Plane の Custom Resource Definition (CRD) が未導入であることを示します。

### 7. ファイアウォール設定の確認 (`enable_firewall: true` の場合)

**実施Kubernetes ノード種別**: ワーカーノード

**コマンド (Ubuntu)**:

```bash
sudo ufw status verbose
```

**コマンド (RHEL)**:

```bash
sudo firewall-cmd --list-ports --zone=public
sudo firewall-cmd --list-rich-rules --zone=public
```

**実行例**:

```plaintext
sudo: ufw: コマンドが見つかりません
```

**確認ポイント**:
- `10250/tcp` が開放されていることを確認してください。
- NodePort を有効化している場合, 範囲ルールが反映されていることを確認してください。
- `ufw` コマンドが見つからない場合は, UFW 未導入または firewalld 利用環境です。OS と `firewall_backend` の設定に合わせて確認コマンドを使い分けてください。

## 補足と注意事項

- 本ロールは `config-worker-node.yml` と `config.yml` の両方でリブートを実行します。
- `config.yml` には ワーカーノード構成リセット (`kubeadm reset`) が含まれるため, 稼働中 Kubernetes クラスタへ適用する際は事前に Pod 退避や停止計画を準備してください。Pod退避 (`kubectl drain --ignore-daemonsets --delete-emptydir-data`) は DaemonSet を退避しないため, 必要に応じて対象ワーカーノードで稼働する各 DaemonSet Pod の停止, 再スケジューリング手順を整備し, Local Persistent Volume のデータは退避やアンマウントを含む保全策を講じてから実行してください。
- コントロールプレーン側でトークン生成 (`kubeadm token create`) や `kubectl` を実行するため, `k8s_ctrlplane_host` では Ansible の権限昇格 (`become: true`) が成功するように設定してください。権限昇格に失敗すると Kubernetes クラスタ参加用トークン取得が失敗します。
- Cilium BGP Control Plane のマニフェストは `k8s_bgp.apply_delegate` で指定したホスト ( 既定は `k8s_ctrlplane_host` )上で生成・適用されます。
- NodePort を有効化する場合は必要なサービスのみが公開されるよう, 上位ネットワーク機器側のアクセス制御リストも合わせて確認してください。
- ファイアウォールタスクはデフォルトで無効化されています。現状は動作検証が十分でないため, `enable_firewall` は `false` を推奨します。
