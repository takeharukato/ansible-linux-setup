# k8s-common ロール

Kubernetesの各ノード共通の前提条件を整えるロールです。制御プレーン / ワーカーノードを問わず, コンテナランタイム (containerd), kubeadm/kubelet/kubectl の導入, ネットワークモジュールと sysctl の調整, swap 無効化, kubelet の NIC 設定, ファイアウォールの開放, オペレータ用ユーザ作成, 証明書埋め込み kubeconfig の補助ツール配布などを一括で実施します。最後に containerd の設定変更を反映させるためリブートを伴う構成となっており, 再実行にも対応しています。

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
| 名前空間 ( namespace )  | - | Kubernetes内部でリソースを論理的に分離する単位。 |
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
| Border Gateway Protocol | BGP | インターネット上の自律システム間でルーティング情報を交換するための外部ゲートウェイプロトコル。Kubernetes環境ではCilium BGP Control Planeによるネットワーク経路制御に使用される。 |

なお, Cilium BGP Control Plane 用リソースの生成と適用は `k8s-ctrlplane` / `k8s-worker` ロール側の `config-cilium-bgp-cplane.yml` で, `k8s_bgp` 変数が有効化されているホストに対して, Cilium BGP Control Plane 用リソースを定義するCustom Resource Definition (CRD) を適用します。
コントロールプレーン構築処理とワーカーノード構築処理の双方から使用される共通テンプレートファイルを一元管理するため, Cilium BGP Control Plane 用リソースを定義するためのmanifestを生成するテンプレートファイルを本ロール配下の`templates/cilium-bgp-resources.yml.j2`に配置しています。

## 前提条件

- **Linux OS**: Debian/Ubuntu 系 (Ubuntu 24.04を想定) または RHEL9系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- **実装言語**: Python 3.8 以上, Bash
- **パッケージマネージャー**: apt (Ubuntu) または yum/dnf (RHEL 系)
- **実行権限**: root または sudo 実行権限
- **ネットワーク**: 複数の NIC がある場合は `k8s_kubelet_nic` または `mgmt_nic` で kubelet がバインドする NIC を指定

本ロールは**リブートを前提**としており, containerd の設定変更を反映させるためホスト再起動を実施します。

## 実行方法

### Makefile を使用

```bash
make run_k8s_common
```

### Ansible コマンド直接実行

```bash
# すべてのホストに適用
ansible-playbook -i inventory/hosts k8s-base.yml

# 特定の tag を指定して実行
ansible-playbook -i inventory/hosts k8s-base.yml -t k8s-common

# 特定ホストのみに適用
ansible-playbook -i inventory/hosts k8s-base.yml --limit <hostname>
```

## 実行フロー

### ステップ1: パラメータと設定読み込み

1. `load-params.yml` で OS ごとのパッケージ名や共通設定値 (`vars/cross-distro.yml` など) を読み込みます。

### ステップ2: ディレクトリ, ファイルシステム準備

2. `directory.yml` が kubeadm 設定ディレクトリや `/opt/k8snodes` 配下のツール格納パスを作成します。
3. `config-sudoer-path.yml` で `/etc/sudoers.d` の `secure_path` を `/usr/local/sbin` まで拡張し, sudo 実行時に Helm などのツールが参照できるようにします。

### ステップ3: パッケージインストール

4. `package.yml` で containerd, kubelet, kubeadm, kubectl を最新化し, 前提パッケージを導入します。
5. `packages-k8s-python.yml` で K8s 用 Python パッケージを導入します (`k8s_python_packages_enabled` が `true` かつ `k8s_python_devel_packages_enabled` に応じて開発環境パッケージも導入)。

### ステップ4: ネットワーク, ファイアウォール, 補完設定

6. `config-k8s-shell-completion.yml` が `kubectl completion bash` / `kubectl completion zsh` の出力を各 OS 既定パスへ展開し, bash/zsh 補完を有効化します (`kubectl_completion_enabled` が `true` かつ `kubectl` バイナリが存在する場合のみ)。
7. `config-firewall-common.yml` が `enable_firewall` / `firewall_backend` に応じて UFW または firewalld を設定し, `k8s_common_ports` や Pod CIDR を許可します (Red Hat 系では rpfilter バイパス用ユニットも展開)。
8. `config-disable-swap.yml` で `/etc/fstab` の swap 項目をコメントアウトし, zram swap を停止, `vm.swappiness=0` を設定します。

### ステップ5: kubelet と CPU シールディング設定

9. `config-kubelet.yml` が kubelet の使用 NIC を `k8s_kubelet_nic` または `mgmt_nic` から決定し, 静的 IP を検証したうえで `/etc/default/kubelet` を生成します。
10. `config-cpu-shielding.yml` (任意) は `k8s_reserved_system_cpus_default` が定義されている場合に kubepods スライスの cpuset を調整します。

### ステップ6: kubeconfig ツール配布

11. `config-common-kubeconfig-tools.yml` で `create-uniq-kubeconfig.py` と日本語 README を `/opt/k8snodes` に配布します。

### ステップ7: カーネル, sysctl, containerd 設定とリブート

12. `config.yml` がカーネルモジュール, sysctl, containerd 設定を反映し, SystemdCgroup を有効化した後に containerd を再起動, ホストをリブートします。

### ステップ8: ユーザ, グループ管理

13. `user_group.yml` で Kubernetes オペレータユーザとホームディレクトリを作成したあと, `config-k8s-operator-authorized_keys.yml` が `.ssh` ディレクトリ生成, テンプレート初期化, GitHub からの鍵取得に加えて `k8s_operator_authorized_key_list` で指定した鍵も追記し, ソート, 重複排除, 所有者/パーミッション調整まで実施し, `authorized_keys` を更新します。
14. `service.yml` (現時点では処理なし) を経てロールが終了します。

## 主要変数

### オペレータユーザ設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_operator_user` | `kube` | オペレータ用ユーザ名。`user_group.yml` がユーザ本体とホームディレクトリを作成します。|
| `k8s_operator_home` | `/home/kube` | オペレータホームディレクトリ。kubeconfig や ssh 鍵を配置します。|
| `k8s_operator_groups_list` | `{{ adm_groups }}` | 追加で所属させるグループ。sudo 実行権限などを付与します。|
| `k8s_operator_shell` | `/bin/bash` | オペレータユーザのデフォルトシェル。|

### 公開鍵設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_operator_github_key_list` | `[]` | 公開鍵を取得したい GitHub アカウントのマッピングのリストです。`[ { github: '<アカウント名>' } ]` のようにリスト指定すると `https://github.com/<account>.keys` から鍵を取得し, `authorized_keys` に追記します。|
| `k8s_operator_authorized_key_list` | `[]` | 追加で登録したい公開鍵のリスト。各要素は `ansible.builtin.authorized_key` タスクで追記され, GitHub 取得分と合わせてソート, 重複排除した結果が `authorized_keys` に反映されます。|

### kubeconfig ツール設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_node_setup_tools_prefix` | `/opt/k8snodes` | kubeconfig ツール類を格納するベースパス。|
| `k8s_node_setup_tools_dir` | `{{ k8s_node_setup_tools_prefix }}/sbin` | `create-uniq-kubeconfig.py` などのスクリプト配置先。|
| `k8s_embed_kubeconfig_script_path` | `{{ k8s_node_setup_tools_dir }}/create-embedded-kubeconfig.py` | 証明書埋め込み kubeconfig 生成スクリプトのパス。|
| `k8s_create_unique_kubeconfig_script_path` | `{{ k8s_node_setup_tools_dir }}/create-uniq-kubeconfig.py` | 複数クラスタの kubeconfig を結合するスクリプトのパス。|
| `k8s_kubeadm_config_store` | `{{ ansible_home_dir }}/kubeadm` | `kubeadm init/join` 用設定ファイルを配置するディレクトリ。|

### ネットワーク設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_common_ports` | `[]` | UFW/firewalld で開放するポートまたはポートレンジ (`6443`, `30000-32767` など)。|
| `k8s_pod_cidrs` | IPv4/IPv6 の Pod CIDR リスト | Pod ネットワーク許可ルールに利用。|
| `k8s_kubelet_nic` | (未定義) | kubelet がバインドする NIC の名前。未定義の場合は `mgmt_nic` を使用。|

### kubelet 設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_kubelet_extra_args_common` | `--cgroup-driver=systemd` | `/etc/default/kubelet` に書き込む共通追加引数。|
| `k8s_use_kubepods_cpuset` | `false` | `true` で kubepods スライスの cpuset をアプリケーション CPU に固定します。|

### ファイアウォール設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `enable_firewall` | `false` | ファイアウォール設定の有効化 (true/false)。|
| `firewall_backend` | `ufw` / `firewalld` | Debian 系は UFW, RHEL 系は firewalld を自動選択。|

### Python パッケージ設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_python_packages_enabled` | `true` | K8s 用の Python ランタイムパッケージを導入します。|
| `k8s_python_devel_packages_enabled` | `false` | K8s 用の Python 開発環境パッケージ (ヘッダファイル等) を導入します。|

### kubectl 補完設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `kubectl_completion_enabled` | `true` | `kubectl completion` の出力を bash/zsh 補完ディレクトリへ展開します。`false` にすると補完関連タスク一式をスキップします。|

### その他ディレクトリ設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_node_setup_tools_docs_dir` | `{{ k8s_node_setup_tools_prefix }}/docs` | 環境セットアップ時のスクリプト関連文書格納先ディレクトリ。|
| `reboot_timeout_sec` | `600` | 再起動後の応答待ちのタイムアウト時間 (秒)。|

### Cilium BGP設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_bgp` | (未定義) | Cilium BGP Control Plane の設定を行うマッピング。未定義がデフォルトで, BGP 関連設定はスキップされます。`host_vars` で明示的に定義した場合のみ有効になります。詳細は「Cilium BGP Control Planeの設定」セクションを参照。|

## デフォルト動作

| 条件 | 結果 |
| --- | --- |
| `enable_firewall: false` | ファイアウォール設定タスク (`config-firewall-common.yml`) をスキップします。Pod CIDR や Kubernetes ポートは UFW/firewalld で管理されません。|
| `k8s_reserved_system_cpus_default` が未定義 | CPU シールディング設定タスク (`config-cpu-shielding.yml`) をスキップします。kubepods スライスの cpuset 調整は実施されません。|
| `k8s_python_packages_enabled: true` | Python ランタイムパッケージを導入します。|
| `k8s_python_devel_packages_enabled: true` | Python 開発環境パッケージ (ヘッダ, gcc 等) も併せて導入します。|
| `kubectl_completion_enabled: false` | bash/zsh 補完ファイルの生成, 配置をスキップします。|
| `k8s_bgp` が未定義 | Cilium BGP Control Plane 設定をスキップします。本ロールはテンプレートファイル `templates/cilium-bgp-resources.yml.j2` のみを提供し, マニフェスト生成処理は実施されません。|
| host_vars で `k8s_bgp.enabled: true` を定義した場合 | k8s-ctrlplane/k8s-worker ロール側で Cilium BGP Control Plane リソース を生成, 適用します。本ロールはテンプレートファイル `templates/cilium-bgp-resources.yml.j2` を提供します。|

## OS 差異

### Ubuntu (Debian 系)

- **パッケージマネージャー**: apt
- **ファイアウォール**: UFW (`firewall_backend: ufw`)
- **bash 補完パス**: `/usr/share/bash-completion/completions/`
- **zsh 補完パス**: `/usr/share/zsh/vendor-completions/`
- **sysctl ファイル**: `/etc/sysctl.d/99-k8s-cri.conf`

### Red Hat 系 (CentOS/RHEL)

- **パッケージマネージャー**: yum / dnf
- **ファイアウォール**: firewalld (`firewall_backend: firewalld`)
- **bash 補完パス**: `/usr/share/bash-completion/completions/`
- **zsh 補完パス**: `/usr/share/zsh/site-functions/`
- **sysctl ファイル**: `/etc/sysctl.d/99-k8s-cri.conf`
- **rpfilter バイパス**: firewalld 使用時に `systemd-rpfilter-bypass-ensure.service` を展開

## Cilium BGP Control Planeの設定

本ロールでは, Cilium に組み込まれた BGP デーモン ( Cilium-BGP Control Plane Custom Resource Definition (CRD) )を使い, Kubernetesの各ノードが外部ルータ (FRRouting など)と BGP セッションを張り, Cilium が管理するルーティング情報を外部に直接広告する機能であるCilium BGP Control Plane機能の設定を行います。

### Cilium BGP Control Plane設定関連変数

Cilium BGP Control Planeの設定は, `host_vars`配下のK8sクラスタを構成するコントロールプレーンノード, ワーカーノードの各設定ファイルに`k8s_bgp`変数を定義することで行います。
`k8s_bgp`変数は, Cilium BGP Control Plane の動作を制御するマッピング(辞書)です。`k8s_bgp`変数のキーと設定値の型,設定値の説明, 設定値の例は, 以下の通りです:

| キー | 型 | 説明 | 設定例 |
| --- | --- | --- | --- |
| `enabled` | bool | BGP Control Plane を有効化します。 | `true` |
| `node_name` | string | CiliumNode Custom Resource (各Kubernetes ノードにおける Cilium の動作設定) に登録するKubernetes ノード名。実機の `k8s_node_name` (kubectl get nodes で確認できる NAME 列の文字列) を指定します。 | `"k8sctrlplane01"` |
| `local_asn` | int | 当該Kubernetes ノードが用いるローカル自律システム番号 (`Autonomous System Number` 以下, `ASN`)。| `65011` |
| `kubeconfig` | string (ファイルパス文字列) | Cilium が Kubernetes API に接続するための `kubeconfig` ファイルのパス名を指定します。 | `"/etc/kubernetes/admin.conf"` |
| `export_pod_cidr` | bool | Pod CIDR (当該Kubernetes ノードが所属する K8s クラスタ内の Pod 仮想ネットワークのアドレス帯) を BGP で広告します。 | `true` |
| `advertise_services` | bool | Service CIDR (当該Kubernetes ノードが所属する K8s クラスタ内のサービスネットワーク上の仮想 IP アドレス帯) を BGP で広告します。 | `false` |
| `address_families` | list[string / dict] | 各 BGP ピアに共通で適用するアドレスファミリ設定のリストです。リストの要素が文字列の場合は `ipv4` / `ipv6` などの BGPが扱うアドレス体系識別子(`Address Family Identifier` (`AFI`) )を指定します。リストの要素を文字列として指定した場合は, 後続アドレスファミリ識別子(`Subsequent Address Family Identifier` (`SAFI`))に`unicast`を指定したものとして扱い, 既定の広告ラベルを紐づけます。リストの要素を辞書として指定する場合の指定方法は, 「`k8s_bgp`変数の`address_families`の要素を辞書として指定する場合の指定方法」を参照してください。| `["ipv4", {"afi": "ipv6", "safi": "unicast"}]` |
| `neighbors` | list[dict] | 接続先 BGP ピアのリスト。各要素は下記のサブキーを持つ辞書です。 | `[...]` |
| `neighbors[].peer_address` | string (CIDR文字列) | BGP ピアのアドレス (CIDR 形式)。 `/32` や `/128` で単一ホストを指定します。 | `"192.168.30.49/32"` |
| `neighbors[].peer_asn` | int | 対向 BGP ピアの ASN。 | `65011` |
| `neighbors[].peer_port` | int | BGP ピアと接続するポート番号。通常は `179` を指定します。 | `179` |
| `neighbors[].hold_time_seconds` | int | BGP Hold Timer。ピアからの Keepalive (ピア間で TCP セッションの有効性確認を行う処理) を待つ最大秒数です。 | `90` |
| `neighbors[].connect_retry_seconds` | int | ピアへの接続失敗時の再接続までの待ち時間を秒単位で指定します。 | `15` |

#### `k8s_bgp`変数の`address_families`の要素を辞書として指定する場合の指定方法

`k8s_bgp`変数の`address_families`の要素を辞書として指定する場合, 以下のキーと設定値からなる辞書として設定値を記述してください。

| キー | 型 | 説明 |
| --- | --- | --- |
| `afi` | string | アドレス体系識別子を指定します。省略時は `ipv4` を使用します。 |
| `safi` | string | 後続アドレスファミリ識別子を指定します。省略時は `unicast` を使用します。 |
| `attributes` | dict | BGP 属性を指定します。辞書の内容は `attributes` セクションとしてそのまま出力されます。 |
| `advertisements` | dict | 当該 AFI/SAFI に適用する広告設定を指定します。CiliumBGPPeerConfig の `families[].advertisements` にそのまま展開されるため, `matchLabels` や `matchExpressions` などのラベルセレクタを含む辞書を記述します (例: `{ "matchLabels": { "bgp.cilium.io/advertisement-group": "custom" } }`)。 |
| `disable_default_advertisements` | bool | 既定の広告ラベルを無効化します。`true` を指定すると既定ラベルを付与しません。 |

## 主な処理

- **ディレクトリ / ツール整備**: `/opt/k8snodes` 配下を作成し, `create-uniq-kubeconfig.py` とその README を配布して kubeconfig マージ作業を補助します。
- **sudo 経路の調整**: `/etc/sudoers.d/99-secure-path` を設け, sudo 実行時にも `/usr/local/sbin` 等を PATH に含めます。
- **パッケージ導入**: containerd, kubeadm, kubelet, kubectl および OS 依存の前提パッケージを最新化します。
- **kubectl 補完**: `kubectl completion` コマンドの出力を OS 別の既定パス (`/usr/share/bash-completion/completions/kubectl`, `/usr/share/zsh/vendor-completions/_kubectl` 等) に配置し, bash/zsh で補完を使用できるようにします。
- **ファイアウォール**: Debian 系は UFW, RHEL 系は firewalld を前提に Pod CIDR とサービスポートを許可し, Red Hat 系では rpfilter バイパス用 systemd ユニットを設置します。
- **swap 無効化**: `/etc/fstab` の swap 行をコメント化し, `swapoff -a`, zram ユニット停止, `vm.swappiness=0` で再発防止します。
- **kubelet 設定**: `k8s_kubelet_nic` もしくは `mgmt_nic` に紐づく静的 IP を検証し, `/etc/default/kubelet` を生成して `--node-ip` を構成します。
- **CPU シールド (任意)**: `k8s_reserved_system_cpus_default` がある場合に kubepods 用 systemd drop-in を配置し, 不要なら削除します。
- **containerd 調整**: kernel モジュール, sysctl を適用し, `containerd config default` から生成した設定で `SystemdCgroup=true` を強制した上でリスタートします。override ユニットで追加オプションを反映します。
- **リブート制御**: containerd 設定変更後にホストを再起動し, `wait_for_connection` で復帰を待ちます。`apply_sysctl` ハンドラは必要に応じて `sysctl --system` を再実行します。
- **ユーザ管理**: `user_group.yml` が認証用ユーザを追加してホームディレクトリを用意し, その後 `config-k8s-operator-authorized_keys.yml` が (1) `.ssh` ディレクトリ新規作成, (2) テンプレートで初期 `authorized_keys` を配置 (テンプレート: `_ssh__authorized_keys.j2`), (3) `k8s_operator_github_key_list` に列挙された GitHub アカウントから公開鍵を取得して追記, (4) `k8s_operator_authorized_key_list` に定義した鍵も追加し, (5) ファイルをソートして重複排除, (6) 所有者とパーミッションを再設定する――という一連の鍵管理処理を自動実行します。

## テンプレート / ファイル

本ロールでは以下のテンプレート / ファイルを出力します:

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `templates/default-kubelet-config.j2` | `/etc/default/kubelet` | kubelet の追加引数 (`KUBELET_EXTRA_ARGS`) を含む `/etc/default/kubelet` のひな型。kubelet がバインドする NIC を指定します。 |
| `templates/containerd-override.conf.j2` | `/etc/systemd/system/containerd.service.d/override.conf` | containerd サービスの systemd drop-in。追加の起動オプション等を指定します。 |
| `templates/99-k8s-cri.conf.j2` | `/etc/sysctl.d/99-k8s-cri.conf` | `net.bridge.bridge-nf-call-iptables=1` などの sysctl 設定。IP フォワーディングとブリッジフィルタリングを有効化します。 |
| `templates/modules-k8s.conf.j2` | `/etc/modules-load.d/k8s.conf` | `overlay` `br_netfilter` を自動ロードするための modules-load ファイル。 |
| `templates/systemd-kubepod-cpuset.conf.j2` | `/etc/systemd/system/kubepods.slice.d/40-cpuset.conf` (条件付き) | kubepods スライス用 cpuset drop-in。`k8s_reserved_system_cpus_default` が定義されている場合のみ出力します。 |
| `templates/rpfilter-bypass-ensure.sh.j2` | `/usr/local/sbin/rpfilter-bypass-ensure.sh` (条件付き) | firewalld 使用時に rpfilter を先行 ACCEPT で回避するシェルスクリプト。`firewall_backend: firewalld` かつ `enable_firewall: true` の場合のみ出力します。 |
| `templates/rpfilter-bypass.service.j2` | `/etc/systemd/system/rpfilter-bypass.service` (条件付き) | rpfilter 回避用 systemd サービスユニット。`firewall_backend: firewalld` かつ `enable_firewall: true` の場合のみ出力します。 |
| `templates/create-uniq-kubeconfig.py.j2` | `{{ k8s_node_setup_tools_dir }}/create-uniq-kubeconfig.py` (既定: `/opt/k8snodes/sbin/create-uniq-kubeconfig.py`) | 複数クラスタの kubeconfig を結合するための Python スクリプト。 |
| `templates/cilium-bgp-resources.yml.j2` | (テンプレートのみ提供) | Cilium BGP Control Plane 用 Custom Resource Definition (CRD) リソースを定義するマニフェストのテンプレート。実際の出力は `k8s-ctrlplane` / `k8s-worker` ロール側で実施されます。 |
| `files/Readme-uniq-kubeconfig-JP.md` | `{{ k8s_node_setup_tools_docs_dir }}/Readme-uniq-kubeconfig-JP.md` (既定: `/opt/k8snodes/docs/Readme-uniq-kubeconfig-JP.md`) | kubeconfig 結合スクリプトの利用手順書 (日本語)。 |

## 設定例

### パターン 1: 基本的な設定 (UFW, 補完有効, ファイアウォール有効)

```yaml
# group_vars/k8s_common/all.yml
enable_firewall: true
firewall_backend: ufw
kubectl_completion_enabled: true
k8s_common_ports:
  - 6443
  - 10250
  - 30000:32767
k8s_operator_user: kube
k8s_operator_home: /home/kube
k8s_operator_groups_list:
  - sudo
  - docker
k8s_python_packages_enabled: true
k8s_python_devel_packages_enabled: false
```

### パターン 2: Cilium BGP Control Plane 有効化

```yaml
# host_vars/k8sctrlplane01.local
---
k8s_bgp:
  enabled: true
  node_name: k8sctrlplane01
  local_asn: 65011
  kubeconfig: /etc/kubernetes/admin.conf
  export_pod_cidr: true
  advertise_services: false
  address_families:
    - ipv4
    - afi: ipv6
      safi: unicast
  neighbors:
    - peer_address: 192.168.30.49/32
      peer_asn: 65011
      peer_port: 179
      hold_time_seconds: 90
      connect_retry_seconds: 15
```

### パターン 3: RHEL/CentOS 系向け (firewalld, Python開発環境有効)

```yaml
# group_vars/rhel_nodes/all.yml
enable_firewall: true
firewall_backend: firewalld
kubectl_completion_enabled: true
k8s_common_ports:
  - 6443/tcp
  - 10250/tcp
  - 30000-32767/tcp
k8s_operator_user: kuberneteadm
k8s_operator_home: /home/kuberneteadm
k8s_python_packages_enabled: true
k8s_python_devel_packages_enabled: true
k8s_kubelet_extra_args_common: "--cgroup-driver=systemd --container-runtime-cgroup-driver=systemd"
reboot_timeout_sec: 900
```

### パターン 4: 複数 NIC 構成, CPU シールディング有効

```yaml
# host_vars/k8sworker0101.local
---
k8s_kubelet_nic: eth1
mgmt_nic: eth0
k8s_reserved_system_cpus_default: 0-3
k8s_use_kubepods_cpuset: true
enable_firewall: true
firewall_backend: ufw
kubectl_completion_enabled: true
k8s_operator_authorized_key_list:
  - "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC... user@workstation"
k8s_operator_github_key_list:
  - github: your-github-username
```

## 検証

### パターン A: 基本的な環境検証

**目的**: containerd, kubelet, kubeadm, kubectl のインストール, ネットワーク, ファイアウォール設定, ユーザ設定が正常に完了していることを確認。

**実行コマンド**:

```bash
# 1. ツール確認
which kubectl kubeadm kubelet
kubectl version --client
kubelet --version
kubeadm version

# 2. containerd 確認
systemctl status containerd
systemctl is-active containerd
containerd --version

# 3. ディレクトリ確認
ls -la /opt/k8snodes/sbin/
file /opt/k8snodes/sbin/create-uniq-kubeconfig.py
cat /opt/k8snodes/sbin/Readme-uniq-kubeconfig-JP.md | head -20

# 4. sudo 設定確認
sudo -l | grep secure_path

# 5. オペレータユーザ確認
id kube
ls -la /home/kube/.ssh/

# 6. kubelet 設定確認
cat /etc/default/kubelet
systemctl status kubelet
journalctl -u kubelet -n 10 --no-pager
```

**期待結果**:

```
$ which kubectl
/usr/bin/kubectl

$ kubectl version --client
Client Version: v1.29.0

$ systemctl is-active containerd
active

$ ls -la /opt/k8snodes/sbin/
total 50
-rwxr-xr-x 1 root root 12345 Nov 15 10:30 create-uniq-kubeconfig.py

$ sudo -l | grep secure_path
Defaults    secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

$ id kube
uid=1001(kube) gid=1001(kube) groups=1001(kube),4(adm),27(sudo)

$ cat /etc/default/kubelet
KUBELET_EXTRA_ARGS="--cgroup-driver=systemd --node-ip=192.168.1.100"
```

### パターン B: ファイアウォール, ネットワーク検証

**目的**: Pod CIDR, Kubernetes ポート, ノード間通信がファイアウォール経由で許可されている。

**実行コマンド** (UFW の場合):

```bash
# UFW の状態確認
sudo ufw status verbose

# Pod CIDR 許可ルール確認
sudo ufw status | grep -i pod
sudo ufw status | grep -i 10.244

# Kubernetes ポート確認
sudo ufw status | grep -i 6443
sudo ufw status | grep -i 10250

# ネットワーク一般確認
sysctl net.ipv4.ip_forward
sysctl net.bridge.bridge-nf-call-iptables
sysctl net.bridge.bridge-nf-call-ip6tables
```

**実行コマンド** (firewalld の場合):

```bash
# firewalld の状態確認
sudo firewall-cmd --list-all

# Pod CIDR 許可確認
sudo firewall-cmd --list-sources | grep -i 10.244

# ポート確認
sudo firewall-cmd --list-ports | grep 6443
sudo firewall-cmd --list-ports | grep 10250

# rpfilter バイパス確認
systemctl status systemd-rpfilter-bypass-ensure.service
```

**期待結果** (UFW):

```
$ sudo ufw status verbose
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), deny (routed)
...
6443/tcp  ALLOW IN    Anywhere
10250/tcp ALLOW IN    Anywhere
10.244.0.0/16 ALLOW IN    Anywhere

$ sysctl net.ipv4.ip_forward
net.ipv4.ip_forward = 1
```

### パターン C: kubectl 補完, bash/zsh 設定確認

**目的**: kubectl コマンド補完が有効化され, 新しいシェルで補完が利用可能。

**実行手順**:

```bash
# 補完ファイルの存在確認
ls -la /usr/share/bash-completion/completions/kubectl
ls -la /usr/share/zsh/vendor-completions/_kubectl

# bash での補完テスト (新しいシェルを起動)
bash
kubectl get <TAB><TAB>  # pods, nodes, services などが表示される
exit

# zsh での補完テスト (新しいシェルを起動)
zsh
kubectl get <TAB><TAB>  # 同様に補完が表示される
exit
```

**期待結果**:

```
$ ls -la /usr/share/bash-completion/completions/kubectl
-rw-r--r-- 1 root root 45678 Nov 15 10:30 /usr/share/bash-completion/completions/kubectl

$ kubectl get <TAB>
pod      pods       podsecuritypolicy
node     nodes
service  services
```

### パターン D: Cilium BGP Control Plane 環境での検証

**前提**: `k8s_bgp.enabled: true` が設定されているホスト。

**実行コマンド**:

```bash
# k8s_bgp 変数値の確認
grep -r "k8s_bgp" host_vars/k8sctrlplane01.local

# CiliumBGPPeeringPolicy が適用されているか確認
kubectl get ciliumbgppeeringpolicy -A
kubectl get ciliumbgppeeringpolicy -A -o yaml | grep -A 20 "node_name\|localAsn\|neighbors"

# Cilium Node リソース確認
kubectl get ciliumnodes

# ノード上での BGP デーモン確認 (control-plane/worker ロール実行後)
kubectl exec -n kube-system -it cilium-<POD_NAME> -- cilium bgp routes ipv4
```

**期待結果**:

```yaml
$ kubectl get ciliumbgppeeringpolicy -A -o yaml
apiVersion: cilium.io/v2alpha1
kind: CiliumBGPPeeringPolicy
metadata:
  name: my-bgp-policy
spec:
  nodeSelectors:
  - matchLabels:
      bgp.cilium.io/peering-policy: "true"
  virtualRouters:
  - localAsn: 65011
    exportPodCIDR: true
    neighbors:
    - peerAddress: 192.168.30.49/32
      peerAsn: 65011

$ kubectl get ciliumnodes
NAME              AGE
k8sctrlplane01    5m
k8sworker0101     4m
```

### パターン E: ユーザ, 公開鍵管理確認

**目的**: オペレータユーザの作成, GitHub 鍵取得, カスタム鍵追加が正常に完了。

**実行コマンド**:

```bash
# ユーザ確認
id kube
groups kube

# ホームディレクトリ確認
ls -la /home/kube
ls -la /home/kube/.ssh

# authorized_keys が正しくソート, 重複排除されているか確認
wc -l /home/kube/.ssh/authorized_keys
sort -u /home/kube/.ssh/authorized_keys > /tmp/sorted.keys
diff /tmp/sorted.keys /home/kube/.ssh/authorized_keys  # 出力なし = 正常

# 各鍵の形式確認
head -3 /home/kube/.ssh/authorized_keys
grep -c "^ssh-rsa\|^ssh-ed25519" /home/kube/.ssh/authorized_keys

# kubeconfig ツール実行テスト
sudo -u kube /opt/k8snodes/sbin/create-uniq-kubeconfig.py --help
```

**期待結果**:

```
$ id kube
uid=1001(kube) gid=1001(kube) groups=1001(kube),4(adm),27(sudo)

$ ls -la /home/kube/.ssh
total 10
-rw-r--r-- 1 kube kube 4567 Nov 15 10:35 authorized_keys

$ wc -l /home/kube/.ssh/authorized_keys
15 /home/kube/.ssh/authorized_keys

$ diff /tmp/sorted.keys /home/kube/.ssh/authorized_keys
$  # 出力なし = ソート, 重複排除が完了

$ sudo -u kube /opt/k8snodes/sbin/create-uniq-kubeconfig.py --help
usage: create-uniq-kubeconfig.py [-h] [-d] [-o OUTPUT]
                                  kubeconfig [kubeconfig ...]
...
```

## トラブルシューティング

### kubelet が起動しない / ステータスが failed

**症状**: `systemctl status kubelet` が `inactive (failed)` または `activating`。

**確認コマンド**:

```bash
journalctl -u kubelet -n 50 --no-pager
systemctl restart kubelet
sleep 5
systemctl status kubelet
```

**原因と対処**:

1. **Node IP が解決できない**: `/etc/default/kubelet` に `--node-ip=<IP>` が正しく設定されているか確認。未設定の場合, `k8s_kubelet_nic` の NIC に割り当てられた IP を `host_vars` に指定。
2. **containerd が未起動**: `systemctl status containerd` を確認。containerd が起動するまで待つ。
3. **ポートが既に使用中**: `netstat -tlnp | grep 10250` で 10250 ポートの使用状況を確認。

### swap が有効のままになっている

**症状**: `swapon --show` で swap パーティション/デバイスが表示される。

**確認, 回復**:

```bash
swapon --show  # 有効な swap を表示
free -h        # メモリ, swap の使用状況を表示

# 緊急対処
sudo swapoff -a
sysctl vm.swappiness  # 0 であることを確認
```

**原因**: 1. ロール再実行後, zram swap ユニットが未停止。
2. `/etc/fstab` のコメント化が不完全。

**対処**: `config-disable-swap.yml` タスクをスキップしていないか確認し, ロール全体を再実行。

### kubectl 補完が機能しない

**症状**: bash/zsh で `kubectl <TAB>` が反応しない。

**確認, 回復**:

```bash
ls -la /usr/share/bash-completion/completions/kubectl
source /usr/share/bash-completion/bash_completion
source /usr/share/bash-completion/completions/kubectl
kubectl <TAB><TAB>
```

**原因**: 1. 補完ファイルが未生成。
2. シェルの rc ファイルで補完スクリプトをロードしていない。

**対処**: ロール全体を再実行し, 新しいシェルを起動して検証。

### Cilium BGP neighbors が接続できない

**前提**: `k8s_bgp.enabled: true` で Cilium BGP が有効。

**確認コマンド**:

```bash
# BGP ピアの状態確認
kubectl get ciliumbgppeeringpolicy -A -o yaml | grep -i neigh

# ノード上での BGP ピア状態
kubectl -n kube-system exec cilium-<POD> -- cilium bgp peers

# ルート確認
kubectl -n kube-system exec cilium-<POD> -- cilium bgp routes ipv4
```

**原因と対処**:

1. **ピアアドレスが到達不可**: `ping <peer_address>` で通信を確認。ネットワーク, ファイアウォール設定を見直し。
2. **ASN の不一致**: `host_vars` の `k8s_bgp.local_asn` と対向ピアの ASN を確認。
3. **kubeconfig ファイルが未存在**: `/etc/kubernetes/admin.conf` が存在し, かつ Cilium が読み取れるか確認。

## 留意事項

- **リブート必須**: 本ロール実行後, `containerd` 設定変更と sysctl 反映のため**必ずホストをリブートしてください**。再実行時でもリブートが実施されます。
- **複数 NIC 環境**: `k8s_kubelet_nic` を明示的に指定しない場合, `mgmt_nic` に紐づく IP が使用されます。複数 NIC がある場合は必ず指定してください。
- **GitHub 鍵取得失敗**: ネットワーク遅延等で GitHub からの鍵取得がタイムアウトする場合, `k8s_operator_authorized_key_list` で事前に鍵を登録するか, ロール実行後に手動で `~/.ssh/authorized_keys` に追記してください。
- **Cilium BGP**: `k8s_bgp` 変数は本ロール側では検証されず, `k8s-ctrlplane` / `k8s-worker` ロール側で CRD を適用する際に検証されます。必ず制御プレーン側で設定を確認してください。
- **テンプレートの共有**: `templates/cilium-bgp-resources.yml.j2` は本ロール (k8s-common) で定義され, `k8s-ctrlplane` / `k8s-worker` ロール側での実装が本ロールに依存する構成になっています。設定の一貫性を重視し, このテンプレートファイルは k8s-common ロール配下で一元管理されています。`k8s-ctrlplane` / `k8s-worker` ロール側で `templates/cilium-bgp-resources.yml.j2` を参照・利用する際は, 本ロールの実装に基づいて実施してください。
- **パッケージマネージャー** (APT / Yum / Dnf): 本ロール内でパッケージ更新を実施するため, パッケージマネージャーのロック状態 (別プロセスが apt/yum を実行中) がないか確認してください。
