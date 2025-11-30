# k8s-common ロール

Kubernetes ノード共通の前提条件を整えるロールです。制御プレーン / ワーカーノードを問わず、コンテナランタイム (containerd)・kubeadm/kubelet/kubectl の導入、ネットワークモジュールと sysctl の調整、swap 無効化、kubelet の NIC 設定、ファイアウォールの開放、オペレータ用ユーザ作成、証明書埋め込み kubeconfig の補助ツール配布などを一括で実施します。最後に containerd の設定変更を反映させるためリブートを伴う構成となっており、再実行にも対応しています。

## 実行フロー

1. `load-params.yml` で OS ごとのパッケージ名や共通設定値 (`vars/cross-distro.yml` など) を読み込みます。
2. `directory.yml` が kubeadm 設定ディレクトリや `/opt/k8snodes` 配下のツール格納パスを作成します。
3. `config-sudoer-path.yml` で `/etc/sudoers.d` の `secure_path` を `/usr/local/sbin` まで拡張し、sudo 実行時に Helm などのツールが参照できるようにします。
4. `package.yml` で containerd・kubelet・kubeadm・kubectl を最新化し、前提パッケージを導入します。
5. `config-firewall-common.yml` が `enable_firewall` / `firewall_backend` に応じて UFW または firewalld を設定し、`k8s_common_ports` や Pod CIDR を許可します (Red Hat 系では rpfilter バイパス用ユニットも展開)。
6. `config-disable-swap.yml` で `/etc/fstab` の swap 項目をコメントアウトし、zram swap を停止、`vm.swappiness=0` を設定します。
7. `config-kubelet.yml` が kubelet の使用 NIC を `k8s_kubelet_nic` または `mgmt_nic` から決定し、静的 IP を検証したうえで `/etc/default/kubelet` を生成します。
8. `config-cpu-shielding.yml` (任意) は `k8s_reserved_system_cpus_default` が定義されている場合に kubepods スライスの cpuset を調整します。
9. `config-common-kubeconfig-tools.yml` で `create-uniq-kubeconfig.py` と日本語 README を `/opt/k8snodes` に配布します。
10. `config.yml` がカーネルモジュール・sysctl・containerd 設定を反映し、SystemdCgroup を有効化した後に containerd を再起動、ホストをリブートします。
11. `user_group.yml` で Kubernetes オペレータユーザを作成し、GitHub から公開鍵を取得して `authorized_keys` を整備します。
12. `service.yml` (現時点では処理なし) を経てロールが終了します。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_operator_user` | `kube` | オペレータ用ユーザ名。`user_group.yml` で作成し、`authorized_keys` を整備します。|
| `k8s_operator_home` | `/home/kube` | オペレータホームディレクトリ。kubeconfig や ssh 鍵を配置します。|
| `k8s_operator_groups_list` | `{{ adm_groups }}` | 追加で所属させるグループ。sudo 実行権限などを付与します。|
| `k8s_node_setup_tools_prefix` | `/opt/k8snodes` | kubeconfig ツール類を格納するベースパス。|
| `k8s_node_setup_tools_dir` | `{{ k8s_node_setup_tools_prefix }}/sbin` | `create-uniq-kubeconfig.py` などのスクリプト配置先。|
| `k8s_embed_kubeconfig_script_path` | `{{ k8s_node_setup_tools_dir }}/create-embedded-kubeconfig.py` | 証明書埋め込み kubeconfig 生成スクリプトのパス。|
| `k8s_create_unique_kubeconfig_script_path` | `{{ k8s_node_setup_tools_dir }}/create-uniq-kubeconfig.py` | 複数クラスタの kubeconfig を結合するスクリプトのパス。|
| `k8s_kubeadm_config_store` | `{{ ansible_home_dir }}/kubeadm` | `kubeadm init/join` 用設定ファイルを配置するディレクトリ。|
| `k8s_kubelet_extra_args_common` | `--cgroup-driver=systemd` | `/etc/default/kubelet` に書き込む共通追加引数。|
| `k8s_common_ports` | `[]` | UFW/firewalld で開放するポートまたはポートレンジ (`6443`, `30000-32767` など)。|
| `k8s_pod_cidrs` | IPv4/IPv6 の Pod CIDR リスト | Pod ネットワーク許可ルールに利用。|
| `k8s_use_kubepods_cpuset` | `false` | `true` で kubepods スライスの cpuset をアプリケーション CPU に固定します。|

その他、`firewall_backend`・`enable_firewall`・`k8s_reserved_system_cpus_default`・`k8s_operator_github_key_list` などの変数がロールの挙動を制御します。詳細は `defaults/main.yml` と `vars/` 配下のファイルを参照してください。

## 主な処理

- **ディレクトリ／ツール整備**: `/opt/k8snodes` 配下を作成し、`create-uniq-kubeconfig.py` とその README を配布して kubeconfig マージ作業を補助します。
- **sudo 経路の調整**: `/etc/sudoers.d/99-secure-path` を設け、sudo 実行時にも `/usr/local/sbin` 等を PATH に含めます。
- **パッケージ導入**: containerd, kubeadm, kubelet, kubectl および OS 依存の前提パッケージを最新化します。
- **ファイアウォール**: Debian 系は UFW、RHEL 系は firewalld を前提に Pod CIDR とサービスポートを許可し、Red Hat 系では rpfilter バイパス用 systemd ユニットを設置します。
- **swap 無効化**: `/etc/fstab` の swap 行をコメント化し、`swapoff -a`、zram ユニット停止、`vm.swappiness=0` で再発防止します。
- **kubelet 設定**: `k8s_kubelet_nic` もしくは `mgmt_nic` に紐づく静的 IP を検証し、`/etc/default/kubelet` を生成して `--node-ip` を構成します。
- **CPU シールド (任意)**: `k8s_reserved_system_cpus_default` がある場合に kubepods 用 systemd drop-in を配置し、不要なら削除します。
- **containerd 調整**: kernel モジュール・sysctl を適用し、`containerd config default` から生成した設定で `SystemdCgroup=true` を強制した上でリスタートします。override ユニットで追加オプションを反映します。
- **リブート制御**: containerd 設定変更後にホストを再起動し、`wait_for_connection` で復帰を待ちます。`apply_sysctl` ハンドラは必要に応じて `sysctl --system` を再実行します。
- **ユーザ管理**: オペレータユーザの作成と `.ssh/authorized_keys` 整備、指定された GitHub アカウントからの鍵取り込みを自動化します。

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

- `/opt/k8snodes/sbin` にスクリプトと README が配置され、実行権限が付与されている。
- `sudo -l` 実行時に `secure_path` に `/usr/local/sbin` が含まれる。
- `containerd`, `kubelet`, `kubeadm`, `kubectl` が期待するバージョンでインストールされ、`systemctl status containerd` / `kubelet` が `active (running)` を示す。
- `ufw status` または `firewall-cmd --list-ports` に `k8s_common_ports` が反映され、Pod CIDR 許可ルールが投入されている。
- `/etc/fstab` の swap 行がコメントアウトされ、`swapon --show` が空である。
- `/etc/default/kubelet` に `--node-ip=<静的 IP>` が設定され、`journalctl -u kubelet -n 20` に IP 解決エラーが出ていない。
- 再起動後にノードへ SSH 接続でき、`sysctl net.ipv4.ip_forward` 等が想定値になっている。
- `sudo -u {{ k8s_operator_user }} kubectl version --client` など、オペレータユーザでの操作が可能である。

## 補足

- `firewall_backend` を空にするか `enable_firewall: false` を指定するとファイアウォール設定タスクをスキップできます。
- containerd 設定を変更せず再起動だけ行いたい場合は `k8s-common` ロールを再実行し、`reboot` ハンドラを `--skip-tags` で除外する等の運用を検討してください。
- `k8s_operator_github_key_list` に GitHub アカウントを追加すると、公開鍵が自動で `authorized_keys` に反映されます。削除時は手動で除外するか、テンプレート側を更新してください。
