# k8s-common ロール

Kubernetes ノード共通の前提条件を整えるロールです。制御プレーン / ワーカーノードを問わず, コンテナランタイム (containerd)・kubeadm/kubelet/kubectl の導入, ネットワークモジュールと sysctl の調整, swap 無効化, kubelet の NIC 設定, ファイアウォールの開放, オペレータ用ユーザ作成, 証明書埋め込み kubeconfig の補助ツール配布などを一括で実施します。最後に containerd の設定変更を反映させるためリブートを伴う構成となっており, 再実行にも対応しています。

なお, Cilium BGP Control Plane 用リソースの生成と適用は `k8s-ctrlplane` / `k8s-worker` ロール側の `config-cilium-bgp-cplane.yml` で, `k8s_bgp` 変数が有効化されているホストに対して, Cilium BGP Control Plane 用リソースを定義するCustom Resource Definition (CRD) を適用します。
コントロールプレイン構築処理とワーカーノード構築処理の双方から使用される共通テンプレートファイルを一元管理するため, Cilium BGP Control Plane 用リソースを定義するためのmanifestを生成するテンプレートファイルを本ロール配下の`templates/cilium-bgp-resources.yml.j2`に配置しています。

## 実行フロー

1. `load-params.yml` で OS ごとのパッケージ名や共通設定値 (`vars/cross-distro.yml` など) を読み込みます。
2. `directory.yml` が kubeadm 設定ディレクトリや `/opt/k8snodes` 配下のツール格納パスを作成します。
3. `config-sudoer-path.yml` で `/etc/sudoers.d` の `secure_path` を `/usr/local/sbin` まで拡張し, sudo 実行時に Helm などのツールが参照できるようにします。
4. `package.yml` で containerd・kubelet・kubeadm・kubectl を最新化し, 前提パッケージを導入します。
5. `config-k8s-shell-completion.yml` が `kubectl completion bash` / `kubectl completion zsh` の出力を各 OS 既定パスへ展開し, bash/zsh 補完を有効化します (`kubectl_completion_enabled` が `true` かつ `kubectl` バイナリが存在する場合のみ)。
6. `config-firewall-common.yml` が `enable_firewall` / `firewall_backend` に応じて UFW または firewalld を設定し, `k8s_common_ports` や Pod CIDR を許可します (Red Hat 系では rpfilter バイパス用ユニットも展開)。
7. `config-disable-swap.yml` で `/etc/fstab` の swap 項目をコメントアウトし, zram swap を停止, `vm.swappiness=0` を設定します。
8. `config-kubelet.yml` が kubelet の使用 NIC を `k8s_kubelet_nic` または `mgmt_nic` から決定し, 静的 IP を検証したうえで `/etc/default/kubelet` を生成します。
9. `config-cpu-shielding.yml` (任意) は `k8s_reserved_system_cpus_default` が定義されている場合に kubepods スライスの cpuset を調整します。
10. `config-common-kubeconfig-tools.yml` で `create-uniq-kubeconfig.py` と日本語 README を `/opt/k8snodes` に配布します。
11. `config.yml` がカーネルモジュール・sysctl・containerd 設定を反映し, SystemdCgroup を有効化した後に containerd を再起動, ホストをリブートします。
12. `user_group.yml` で Kubernetes オペレータユーザとホームディレクトリを作成したあと, `config-k8s-operator-authorized_keys.yml` が `.ssh` ディレクトリ生成・テンプレート初期化・GitHub からの鍵取得に加えて `k8s_operator_authorized_key_list` で指定した鍵も追記し, ソート・重複排除・所有者/パーミッション調整まで実施し, `authorized_keys` を更新します。
13. `service.yml` (現時点では処理なし) を経てロールが終了します。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_operator_user` | `kube` | オペレータ用ユーザ名。本ロールでは, `user_group.yml` がユーザ本体とホームディレクトリを作成し, その後 `config-k8s-operator-authorized_keys.yml` がホーム直下に `.ssh` ディレクトリを作成, テンプレート ( `_ssh__authorized_keys.j2` ) で初期鍵を書き込み, GitHub から取得した鍵と `k8s_operator_authorized_key_list` で定義した鍵を追記し, ソート・重複排除と所有者/パーミッション調整まで行います。|
| `k8s_operator_home` | `/home/kube` | オペレータホームディレクトリ。kubeconfig や ssh 鍵を配置します。|
| `k8s_operator_groups_list` | `{{ adm_groups }}` | 追加で所属させるグループ。sudo 実行権限などを付与します。|
| `k8s_operator_authorized_key_list` | `[]` | 追加で登録したい公開鍵のリスト。各要素は `config-k8s-operator-authorized_keys.yml` 内の `ansible.builtin.authorized_key` タスクで追記され, GitHub 取得分と合わせてソート・重複排除した結果が `authorized_keys` に反映されます。|
| `kubectl_completion_enabled` | `true` | `kubectl completion` の出力を bash/zsh 補完ディレクトリへ展開します。`false` にすると補完関連タスク一式をスキップします。|
| `kubectl_completion_enabled`| `true` | `true` の場合, kubectl` の bash / zsh 補完ファイルを生成・配置します。|
| `k8s_operator_github_key_list` | `[]` | 公開鍵を取得したい GitHub アカウントのマッピングのリストです。環境ごとに `[ { github: '<アカウント名>' } ]` のようなリストへ上書きすると `https://github.com/<account>.keys` から鍵を取得し, `authorized_keys` に追記します。将来的に別サイト由来の鍵取得へ拡張できるよう, サイトとアカウント名のマッピングを記述する構造です。|
| `k8s_node_setup_tools_prefix` | `/opt/k8snodes` | kubeconfig ツール類を格納するベースパス。|
| `k8s_node_setup_tools_dir` | `{{ k8s_node_setup_tools_prefix }}/sbin` | `create-uniq-kubeconfig.py` などのスクリプト配置先。|
| `k8s_embed_kubeconfig_script_path` | `{{ k8s_node_setup_tools_dir }}/create-embedded-kubeconfig.py` | 証明書埋め込み kubeconfig 生成スクリプトのパス。|
| `k8s_create_unique_kubeconfig_script_path` | `{{ k8s_node_setup_tools_dir }}/create-uniq-kubeconfig.py` | 複数クラスタの kubeconfig を結合するスクリプトのパス。|
| `k8s_kubeadm_config_store` | `{{ ansible_home_dir }}/kubeadm` | `kubeadm init/join` 用設定ファイルを配置するディレクトリ。|
| `k8s_kubelet_extra_args_common` | `--cgroup-driver=systemd` | `/etc/default/kubelet` に書き込む共通追加引数。|
| `k8s_common_ports` | `[]` | UFW/firewalld で開放するポートまたはポートレンジ (`6443`, `30000-32767` など)。|
| `k8s_pod_cidrs` | IPv4/IPv6 の Pod CIDR リスト | Pod ネットワーク許可ルールに利用。|
| `k8s_use_kubepods_cpuset` | `false` | `true` で kubepods スライスの cpuset をアプリケーション CPU に固定します。|

その他, `firewall_backend`・`enable_firewall`・`k8s_reserved_system_cpus_default`・`k8s_operator_github_key_list` などの変数がロールの挙動を制御します。詳細は `defaults/main.yml` と `vars/` 配下のファイルを参照してください。

## Cilium BGP Control Planeの設定

本ロールでは, Cilium に組み込まれた BGP デーモン ( Cilium-BGP Control Plane Custom Resource Definition (CRD) )を使い, Kubernetes ノードが外部ルータ (FRRouting など)と BGP セッションを張り, Cilium が管理するルーティング情報を外部に直接広告する機能であるCilium BGP Control Plane機能の設定を行います。

### Cilium BGP Control Plane設定関連変数

Cilium BGP Control Planeの設定は, `host_vars`配下のK8sクラスタを構成するコントロールプレイン, ワーカーノードの各設定ファイルに`k8s_bgp`変数を定義することで行います。
`k8s_bgp`変数は, Cilium BGP Control Plane の動作を制御するマッピング(辞書)です。`k8s_bgp`変数のキーと設定値の型,設定値の説明, 設定値の例は, 以下の通りです:

| キー | 型 | 説明 | 設定例 |
| --- | --- | --- | --- |
| `enabled` | bool | BGP Control Plane を有効化します。 | `true` |
| `node_name` | string | CiliumNode Custom Resource (各ノードにおける Cilium の動作設定) に登録するノード名。実機の `k8s_node_name` (kubectl get nodes で確認できる NAME 列の文字列) を指定します。 | `"k8sctrlplane01"` |
| `local_asn` | int | 当該ノードが用いるローカル自律システム番号 (`Autonomous System Number` 以下, `ASN`)。| `65011` |
| `kubeconfig` | string (ファイルパス文字列) | Cilium が Kubernetes API に接続するための `kubeconfig` ファイルのパス名を指定します。 | `"/etc/kubernetes/admin.conf"` |
| `export_pod_cidr` | bool | Pod CIDR (当該ノードが所属する K8s クラスタ内の Pod 仮想ネットワークのアドレス帯) を BGP で広告します。 | `true` |
| `advertise_services` | bool | Service CIDR (当該ノードが所属する K8s クラスタ内のサービスネットワーク上の仮想 IP アドレス帯) を BGP で広告します。 | `false` |
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

- **ディレクトリ／ツール整備**: `/opt/k8snodes` 配下を作成し, `create-uniq-kubeconfig.py` とその README を配布して kubeconfig マージ作業を補助します。
- **sudo 経路の調整**: `/etc/sudoers.d/99-secure-path` を設け, sudo 実行時にも `/usr/local/sbin` 等を PATH に含めます。
- **パッケージ導入**: containerd, kubeadm, kubelet, kubectl および OS 依存の前提パッケージを最新化します。
- **kubectl 補完**: `kubectl completion` コマンドの出力を OS 別の既定パス (`/usr/share/bash-completion/completions/kubectl`, `/usr/share/zsh/vendor-completions/_kubectl` 等) に配置し, bash/zsh で補完を使用できるようにします。
- **ファイアウォール**: Debian 系は UFW, RHEL 系は firewalld を前提に Pod CIDR とサービスポートを許可し, Red Hat 系では rpfilter バイパス用 systemd ユニットを設置します。
- **swap 無効化**: `/etc/fstab` の swap 行をコメント化し, `swapoff -a`, zram ユニット停止, `vm.swappiness=0` で再発防止します。
- **kubelet 設定**: `k8s_kubelet_nic` もしくは `mgmt_nic` に紐づく静的 IP を検証し, `/etc/default/kubelet` を生成して `--node-ip` を構成します。
- **CPU シールド (任意)**: `k8s_reserved_system_cpus_default` がある場合に kubepods 用 systemd drop-in を配置し, 不要なら削除します。
- **containerd 調整**: kernel モジュール・sysctl を適用し, `containerd config default` から生成した設定で `SystemdCgroup=true` を強制した上でリスタートします。override ユニットで追加オプションを反映します。
- **リブート制御**: containerd 設定変更後にホストを再起動し, `wait_for_connection` で復帰を待ちます。`apply_sysctl` ハンドラは必要に応じて `sysctl --system` を再実行します。
- **ユーザ管理**: `user_group.yml` が認証用ユーザを追加してホームディレクトリを用意し, その後 `config-k8s-operator-authorized_keys.yml` が (1) `.ssh` ディレクトリ新規作成, (2) テンプレートで初期 `authorized_keys` を配置 (テンプレート: `_ssh__authorized_keys.j2`), (3) `k8s_operator_github_key_list` に列挙された GitHub アカウントから公開鍵を取得して追記, (4) `k8s_operator_authorized_key_list` に定義した鍵も追加し, (5) ファイルをソートして重複排除, (6) 所有者とパーミッションを再設定する――という一連の鍵管理処理を自動実行します。

## テンプレート／ファイル

- `templates/default-kubelet-config.j2`: kubelet の追加引数 (`KUBELET_EXTRA_ARGS`) を含む `/etc/default/kubelet` のひな型。
- `templates/containerd-override.conf.j2`: containerd サービスの systemd drop-in。
- `templates/99-k8s-cri.conf.j2`: `net.bridge.bridge-nf-call-iptables=1` などの sysctl 設定。
- `templates/modules-k8s.conf.j2`: `overlay` `br_netfilter` を自動ロードするための modules-load ファイル。
- `templates/systemd-kubepod-cpuset.conf.j2`: kubepods スライス用 cpuset drop-in。
- `templates/rpfilter-bypass-ensure.sh.j2` / `.service.j2`: firewalld 使用時に rpfilter を先行 ACCEPT で回避するユニット。
- `templates/_ssh__authorized_keys.j2`: オペレータユーザの既定公開鍵セット。
- `files/Readme-uniq-kubeconfig-JP.md`: kubeconfig 結合スクリプトの利用手順書 (日本語)。

## 検証ポイント

- `/opt/k8snodes/sbin` にスクリプトと README が配置され, 実行権限が付与されている。
- `sudo -l` 実行時に `secure_path` に `/usr/local/sbin` が含まれる。
- `containerd`, `kubelet`, `kubeadm`, `kubectl` が期待するバージョンでインストールされ, `systemctl status containerd` / `kubelet` が `active (running)` を示す。
- `/usr/share/bash-completion/completions/kubectl` や `/usr/share/zsh/vendor-completions/_kubectl` (RHEL 系は `/usr/share/zsh/site-functions/_kubectl`) が生成され, 新しいシェルで `kubectl` の補完が有効になっている。
- `ufw status` または `firewall-cmd --list-ports` に `k8s_common_ports` が反映され, Pod CIDR 許可ルールが投入されている。
- `/etc/fstab` の swap 行がコメントアウトされ, `swapon --show` が空である。
- `/etc/default/kubelet` に `--node-ip=<静的 IP>` が設定され, `journalctl -u kubelet -n 20` に IP 解決エラーが出ていない。
- 再起動後にノードへ SSH 接続でき, `sysctl net.ipv4.ip_forward` 等が想定値になっている。
- `sudo -u {{ k8s_operator_user }} kubectl version --client` など, オペレータユーザでの操作が可能である。

## 補足

- `firewall_backend` を空にするか `enable_firewall: false` を指定するとファイアウォール設定タスクをスキップできます。
- containerd 設定を変更せず再起動だけ行いたい場合は `k8s-common` ロールを再実行し, `reboot` ハンドラを `--skip-tags` で除外する等の運用を検討してください。
- `k8s_operator_github_key_list` に GitHub アカウントを追加すると, GitHubから取得した公開鍵が自動で `authorized_keys` に反映されます。
- `k8s_operator_authorized_key_list`に記載された公開鍵が自動で `authorized_keys` に反映されます。
