# k8s-worker ロール

Kubernetes ワーカーノードをクラスタへ再参加させるためのロールです。`k8s-common` で整えた前提の上に, 低遅延化向けの OS チューニング, `kubeadm join` の再実行, NodePort を含む防火壁構成, Cilium BGP Control Plane の設定をまとめて適用します。再実行を想定し, 既存Kubernetes ノードの cordon / drain / delete まで一括で扱います。

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

1. [roles/k8s-worker/tasks/load-params.yml](roles/k8s-worker/tasks/load-params.yml#L8-L23) が OS ファミリ別のパッケージ定義と `vars/` 配下の共通変数 (`cross-distro.yml` / `all-config.yml` / `k8s-api-address.yml`) を読み込みます。
2. [roles/k8s-worker/tasks/main.yml](roles/k8s-worker/tasks/main.yml#L12-L15) で `package.yml` / `directory.yml` / `user_group.yml` / `service.yml` を include し, 将来の拡張に備えたタスク構造を維持します ( 現状は実処理なし )。
3. [roles/k8s-worker/tasks/config-k8sworker-firewall.yml](roles/k8s-worker/tasks/config-k8sworker-firewall.yml#L8-L195) は `enable_firewall` と `firewall_backend` に応じて UFW もしくは firewalld を整備し, 6443 側からの kubelet アクセスや NodePort 範囲の開放, 状態確認を行います。
4. [roles/k8s-worker/tasks/config-shielding.yml](roles/k8s-worker/tasks/config-shielding.yml#L8-L27) が `k8s_systemd_slices` 向けに cpuset ドロップイン (`systemd-cpuset.conf.j2`) を生成し, CPU シールドの前提を整えます。
5. [roles/k8s-worker/tasks/config-worker-node.yml](roles/k8s-worker/tasks/config-worker-node.yml#L11-L354) が `irq_balance_package` の削除, `k8s_reserved_system_cpus_default` を基にしたアプリケーション用 CPU レンジ算出, GRUB コマンドラインの最適化, pin スクリプトと systemd サービスの展開, 初回リブートと待機をまとめて実施します。
6. [roles/k8s-worker/tasks/config.yml](roles/k8s-worker/tasks/config.yml#L8-L186) が kube-apiserver の起動待ちとトークン／CA ハッシュ取得, `worker-kubeadm.config.j2` の生成, 既存Kubernetes ノードの cordon / drain / delete, `kubeadm reset` と再 join, サービス有効化, 二度目のリブートを実行します。
7. [roles/k8s-worker/tasks/config-cilium-bgp-cplane.yml](roles/k8s-worker/tasks/config-cilium-bgp-cplane.yml#L8-L105) は `k8s_bgp.enabled` が true の場合にのみ発動し, マニフェスト出力ディレクトリを整備して `roles/k8s-common/templates/cilium-bgp-resources.yml.j2` をレンダリングし, 関連 CRD の存在確認後に適用します。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_ctrlplane_endpoint` | 各 `host_vars` | コントロールプレーン API 広告アドレス。API 待機, firewall 設定, `kubeadm join` に使用します。|
| `k8s_api_wait_host` | "{{ k8s_ctrlplane_endpoint }}" | kube-apiserverの待ち合わせ先(接続先)ホスト名/IPアドレス。|
| `k8s_api_wait_port` | "{{ k8s_ctrlplane_port }}" | kube-apiserverの待ち合わせ先ポート番号。|
| `k8s_api_wait_timeout` | `600` | kube-apiserver待ち合わせ時間(単位: 秒)。|
| `k8s_api_wait_delay` | `2` | kube-apiserver待ち合わせる際の開始遅延時間(単位: 秒)。|
| `k8s_api_wait_sleep` | `1` | kube-apiserver待ち合わせる際の待機間隔(単位: 秒)。|
| `k8s_api_wait_delegate_to` | "localhost" | kube-apiserver待ち合わせる際の接続元ホスト名/IPアドレス。|
| `k8s_containerd_wait_timeout` | `60` | containerdソケット待ち合わせ時間(単位: 秒)。|
| `k8s_containerd_wait_delegate_to` | `"localhost"` | containerdソケット待ち合わせる際の接続元ホスト名/IPアドレス。|
| `k8s_ctrlplane_host` | 各 `host_vars` | `delegate_to` で kubeadm/kubectl を実行するコントロールプレーンノード。|
| `enable_firewall` | `false` (`vars/all-config.yml`) | true の場合に firewall タスクを有効化します。|
| `firewall_backend` | OS 判定で `['ufw']` または `['firewalld']` | firewall 実装の選択。複数指定時はループで順次処理します。|
| `k8s_worker_enable_nodeport` | `false` | NodePort の開放を行うかどうか。|
| `k8s_worker_nodeport_range` | `30000-32767` | NodePort 開放レンジ。UFW ではコロン区切りに変換されます。|
| `k8s_kubeadm_config_store` | `{{ ansible_home_dir }}/kubeadm` | `kubeadm.config.yml` や BGP マニフェストを保存するディレクトリ。|
| `k8s_kubeadm_ignore_preflight_errors_arg` | `--ignore-preflight-errors=all` | `kubeadm join` に渡す preflight 無視オプション。|
| `k8s_drain_timeout_minutes` / `k8s_worker_delete_wait_sec` | `5` / `5` | cordon/drain/delete のタイムアウトと削除待機時間。|
| `k8s_reserved_system_cpus_default` | 未定義 | システム系に割り当てる CPU レンジ。CPU シールドや GRUB 設定がこの値を参照します。|
| `k8s_systemd_slices` | `['init.scope.d', 'system.slice.d', 'user.slice.d', 'user-.slice.d']` | cpuset ドロップインを配置する systemd スライス一覧。|
| `k8s_node_setup_tools_dir` | `/opt/k8snodes/sbin` | pin スクリプトやユーティリティの配置先。|
| `k8s_bgp.enabled` | 未定義 | true 時に Cilium BGP Control Plane マニフェストを生成・適用します。|
| `k8s_bgp.neighbors` | 未定義 | BGP ピア定義。`k8s_bgp.enabled: true` の場合は空であってはなりません。|

## 主な処理

- **Firewall 構成**: `enable_firewall` が有効な環境で UFW/firewalld を初期化し, 10250/tcp などの制御プレーン向けポートと NodePort 範囲を恒久的に開放します。
- **CPU シールドの準備**: systemd スライス単位で AllowedCPUs を固定し, IRQ 片寄せスクリプトと連携する前提を整備します。
- **GRUB と低遅延調整**: `k8s_reserved_system_cpus_default` に基づき `nohz_full` や `isolcpus` などのカーネルパラメータを更新し, ワーカースレッドと IRQ をアプリケーション用 / システム用に分離します。
- **kubeadm 再 join**: 既存ワーカーの cordon / drain / delete, `kubeadm reset`, `kubeadm join --config` を自動化し, containerd / kubelet を有効化して再起動します。
- **Cilium BGP Control Plane**: Kubernetes ノード固有の識別子で CRD マニフェストを生成し, CiliumBGPAdvertisement / CiliumBGPPeerConfig / CiliumBGPClusterConfig を適用して Pod/Service CIDR をルータへ広告します。
- **再起動とユーティリティ登録**: pin-worker-queue / pin-irqs の systemd サービスを enabled 登録し, OS チューニング後と join 後にそれぞれリブートします。

## テンプレート／ファイル

| テンプレート | 生成ファイル | 説明 |
| --- | --- | --- |
| [roles/k8s-worker/templates/worker-kubeadm.config.j2](roles/k8s-worker/templates/worker-kubeadm.config.j2) | kubeadm.config.yml ( 対象ホストの k8s_kubeadm_config_store 配下 ) | kubeadm join に渡す設定をまとめ, トークンと CA ハッシュを組み込んだ構成ファイルを生成します。 |
| [roles/k8s-worker/templates/systemd-cpuset.conf.j2](roles/k8s-worker/templates/systemd-cpuset.conf.j2) | 40-cpuset.conf ( 対象ホストの各 systemd スライス配下 ) | CPU シールド用に AllowedCPUs を固定し, k8s_systemd_slices の各ドロップインで共有する設定を作成します。 |
| [roles/k8s-worker/templates/pin-worker-queue.sh.j2](roles/k8s-worker/templates/pin-worker-queue.sh.j2) | pin-worker-queue.sh ( 対象ホストの k8s_node_setup_tools_dir 配下 ) | workqueue のアンバウンドスレッドをアプリ用 CPU に寄せるセットアップスクリプトを配置します。 |
| [roles/k8s-worker/templates/pin-worker-queue.service.j2](roles/k8s-worker/templates/pin-worker-queue.service.j2) | pin-worker-queue.service ( 対象ホストの systemd ユニットディレクトリ ) | pin-worker-queue.sh をワンショット実行し, ブート後に CPU ピニングを適用する systemd ユニットを登録します。 |
| [roles/k8s-worker/templates/pin-irqs.py.j2](roles/k8s-worker/templates/pin-irqs.py.j2) | pin-irqs.py ( 対象ホストの k8s_node_setup_tools_dir 配下 ) | 割込みをシステム用 CPU へ片寄せる Python スクリプトを配備します。 |
| [roles/k8s-worker/templates/pin-irqs.service.j2](roles/k8s-worker/templates/pin-irqs.service.j2) | pin-irqs.service ( 対象ホストの systemd ユニットディレクトリ ) | pin-irqs.py を起動して IRQ アフィニティを適用する systemd ユニットを登録します。 |
| [roles/k8s-common/templates/cilium-bgp-resources.yml.j2](roles/k8s-common/templates/cilium-bgp-resources.yml.j2) | Cilium BGP マニフェスト ( 対象ホストの cilium_bgp_manifest_dir 配下 ) | Kubernetes ノード固有の識別子を含む CiliumBGP* リソースをまとめたマニフェストを生成し, apply_delegate で指定したホストに保存します。 |

## ハンドラ

| ハンドラ | トリガー | 説明 |
| --- | --- | --- |
| [roles/k8s-worker/handlers/kubelet.yml](roles/k8s-worker/handlers/kubelet.yml) | `notify: kubelet_restarted_and_enabled` | kubelet の daemon-reload と再起動, enable をまとめて実施し, join 後のサービス状態を整えます。 |
| [roles/k8s-worker/handlers/reload-firewall.yml](roles/k8s-worker/handlers/reload-firewall.yml) | `notify: reload firewalld` / `notify: reload ufw` | firewall_backend に応じて firewalld もしくは UFW を再読み込みし, NodePort などのポート開放設定を反映させます。 |
| [roles/k8s-worker/handlers/reboot-node.yml](roles/k8s-worker/handlers/reboot-node.yml) | `notify: reboot_node_handler` | リブートを実行し, GRUB 変更や kubeadm 再 join 後の状態を確定させます。 |

## 検証ポイント

- control-plane で `kubectl get nodes` を実行し, 対象ワーカーが `Ready` になっているか確認します。
- `journalctl -u kubelet` で kubelet の再起動後にエラーが出ていないことを確認します。
- `/etc/systemd/system/*/40-cpuset.conf` が生成され, 期待する CPU レンジが書き込まれていることを確認します。
- `systemctl status pin-worker-queue pin-irqs` が `loaded (enabled)` でワンショット実行後に正常終了していることを確認します。
- `k8s_bgp.enabled: true` の場合は `kubectl get ciliumbgpclusterconfigs.cilium.io -A` 等でマニフェストが適用されていることを確認します。
- firewall を有効化した場合は `ufw status verbose` または `firewall-cmd --list-ports --zone=public` で想定ポートが開放されているか確認します。

## 補足と注意事項

- 本ロールは `config-worker-node.yml` と `config.yml` の両方でリブートを実行します。
- `config.yml` には `kubeadm reset` が含まれるため, 稼働中Kubernetesクラスタへ適用する際は事前に Pod 退避や停止計画を準備してください。`kubectl drain --ignore-daemonsets --delete-emptydir-data` は DaemonSet を退避しないため, 必要に応じて, 対象Kubernetes ノードで稼働する各 DaemonSet Pod の停止／再スケジューリング手順を整備し, Local Persistent Volume に格納されたデータは退避やアンマウントを含めた保全策を講じてから実行してください。
- control-plane 側で `kubeadm token create` や `kubectl` を実行するため, `k8s_ctrlplane_host` ではパスワードレス sudo などの権限を整備しておいてください。設定を誤ると join 用トークン取得が失敗します。
- Cilium BGP Control Plane のマニフェストは `k8s_bgp.apply_delegate` で指定したホスト ( 既定は `k8s_ctrlplane_host` )上で生成・適用されます。
- NodePort を有効化する場合は必要なサービスのみが公開されるよう, 上位ネットワーク機器側のアクセス制御リストも合わせて確認してください。
- firewall タスクはデフォルトで無効化されています。現状は動作検証が十分でないため, `enable_firewall` は `false` を推奨します。
