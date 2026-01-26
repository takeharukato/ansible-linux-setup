# common ロール

このロールは Debian/Ubuntu 系および RHEL 系ホストの初期セットアップを共通化する土台ロールです。`roles/common/tasks/main.yml` が記述順に各サブタスクを実行し, ネットワーク基盤の置き換え, sudoers 管理, sysctl 追加, Dynamic DNS 連携, 共通パッケージ導入, 必要に応じた再起動までを一括で適用します。

## タスク構成

- **load-params.yml**: `roles/common/vars/*.yml` を順に取り込み, OS 別パッケージ名 (`packages-*.yml`), クロスディストロ変数 (`cross-distro.yml`), 共通設定 (`all-config.yml`), Kubernetes API 情報 (`k8s-api-address.yml`) を確定します。
- **config-pre-check.yml**: `mgmt_nic` が未指定の場合は `common_default_nic` で補完し, 0 文字のままなら失敗させます。ネットワーク処理の前提をここで固めます。
- **config-timezone.yml**: `common_timezone` が非空なら `timezone` モジュールで恒久設定します。
- **config-disable-firewall.yml**: `ansible_facts.services` を収集し, RHEL 系では `firewalld`, Debian 系では `ufw` を完全停止・マスクします。`rpfilter-bypass.service` の停止, `nft` で作成済みの `rpfix` テーブル削除, `ufw --force disable` 実行も包含します。
- **config-prepare-nm.yml**: OS ごとに NetworkManager を導入・起動し, Debian 系では `systemd-networkd-wait-online` と `systemd-networkd` を無効化します。RHEL 系では `/etc/NetworkManager/NetworkManager.conf` に `no-auto-default=*` を挿入し, `nm_reload_and_activate` ハンドラを通知します。NetworkManager へ切り替えた直後に無条件の再起動を要求します。
- **config-network-multi.yml**: `_netif_list_effective` を展開して systemd `.link` ファイル (`/etc/systemd/network/10-<if>.link`) を配備し, RHEL 系は `/etc/NetworkManager/system-connections/<if>.nmconnection` をテンプレート出力後 `nmcli connection load` と `restorecon` を実施, Debian 系は `/etc/netplan/99-netcfg.yaml` を生成して `netplan generate` に成功した場合だけ `netplan_apply` を通知します。既存の不要な 802-3-ethernet 接続を UUID 単位で削除し, 最後に再起動してデバイス名と接続構成を確実に確定させます。
- **config-sudoer.yml**: `sudo` を確保し, `/etc/sudoers.d` を `0755` で作成します。`visudo -cf /etc/sudoers` を前後で実行しつつ, `sudo_nopasswd_users` と `sudo_nopasswd_groups_autodetect`/`sudo_nopasswd_groups_extra` を突き合わせてドロップイン (`/etc/sudoers.d/{{ sudo_dropin_prefix }}-user-*` / `-group-*`) をテンプレート生成します。`sudo_nopasswd_absent: true` の場合は同ファイルを削除します。
- **sysctl.yml**: `common_sysctl_user_ptrace_enable` が真なら `kernel.yama.ptrace_scope=0` を `sysctl_ptrace_conf_path` (既定 `/etc/sysctl.d/10-ptrace.conf`) に書き込み, `common_sysctl_user_dmesg_enable` が真なら `kernel.dmesg_restrict=0` を `sysctl_dmesg_conf_path` (既定 `/etc/sysctl.d/10-kernel-hardening.conf`) に保存します。`common_sysctl_inotify_max_user_watches` を `/etc/sysctl.d/90-sysctl-inotify.conf` に `lineinfile` で反映し, `common_reload_sysctl` ハンドラを通知して `sysctl --system` を実行させます。
- **cron-setting.yml**: `common_disable_cron_mails` が真の場合に `/etc/crontab` の `MAILTO` 行を `MAILTO=""` へ統一, 欠如していれば挿入します。
- **package.yml**: `common_mdns_packages` を更新後 `avahi_restarted_and_enabled` を通知し, `common_langpack_packages` を導入して `disable_gui` ハンドラを呼び出します。`use_vmware: true` 時は `common_vmware_packages` を導入し, `disable_gui` と `pkg-autoremove` を通知します。
- **kubectl-repositories.yml**: `k8s_common_prerequisite_packages` (例: `ca-certificates`, `curl`, `gnupg`) を最新化し, Kubernetes リポジトリ登録の前提を整えます。
- **common-packages.yml**: RHEL 系で SELinux ツール (`policycoreutils-python-utils`) を必須化し, `common_packages` を導入します。Debian 系は追加で `apt-file update` を実行し, 双方で `disable_gui` と `pkg_autoremove_handler` (`pkg-autoremove`) を通知します。
- **directory.yml**: `ddns_client_update_sh_dest_dir` (既定 `/usr/local/sbin`) を作成し, `templates/mount-nas.sh.j2` を `/usr/local/sbin/mount-nas.sh` へ配置します。
- **directory-dns-client.yml** (`use_nm_ddns_update_scripts: true` のみ):
  - `/etc/nsupdate` 以下に `dns_ddns_key_file`・`ddns-client-update.sh`・環境ファイルを展開し, `nm_ra_addr_watch` サービスユニット (`/etc/systemd/system/nm-ra-addr-watch.service`) と本体 (`/usr/local/libexec/nm-ra-addr-watch`) を生成します。
  - NetworkManager dispatcher スクリプト `{{ nm_ns_update_path }}` (既定 `/etc/NetworkManager/dispatcher.d/90-nm-ns-update`) と環境ファイルを配備し, `nm-ra-addr-watch` と `NetworkManager-dispatcher` を有効化します。
  - Dispatcher を差し替えた直後に再起動し, Dispatcher/サービスの読み直しを保証します。
- **service.yml / user_group.yml**: いずれも将来拡張用の空タスクで, 現時点では副作用はありません。
- **reboot.yml**: `/var/run/reboot-required` が存在する場合に `systemctl set-default multi-user.target` を再適用し, 再起動と SSH 復帰待機を行います。

## ハンドラの挙動

- `common_reload_sysctl` (`handlers/reload-sysctl.yml`): `sysctl --system` を root で実行し, `changed_when: false` で冪等に読み込みます。
- `nm_reload_and_activate` (`handlers/nm-handlers-rhel.yml`): RHEL 系のみで発火し, `nmcli connection reload`, 既知デバイスの再管理, 残留アドレスの flush, `nmcli connection up` までを安全に実施します。タスク側で `_netif_items` が定義されていることが前提です。
- `netplan_apply` (`handlers/netplan-handlers-debian.yml`, `handlers/netplan.yml`): Debian 系で `netplan generate`→`netplan apply`→`ip -br addr`/ルート確認を順に実行します。`handlers/netplan.yml` の単純な `netplan apply` は互換用のリスナーです。
- `avahi_restarted_and_enabled`, `disable_gui`, `pkg-autoremove`: それぞれ avahi の再起動, `systemctl set-default multi-user.target` の適用, `apt autoremove -y` (Debian) / `dnf autoremove -y` (RHEL) を行います。

## 変数一覧

| 変数名 | 既定値 | 説明 |
| ------ | ------ | ---- |
| `common_timezone` | `"Asia/Tokyo"` | 適用するタイムゾーン名。空文字列の場合は変更しません。 |
| `use_vmware` | `false` | VMware 用追加パッケージを導入するかを制御します。 |
| `use_xcpng` | `false` | xcp-ng 用追加パッケージを導入するかを制御します。 |
| `xcpng_xe_guest_utilities_version` | `"8.4.0"` | xcp-ngゲストエージェントの版数 |
| `xcpng_xe_guest_utilities_release` | `"1"` | xcp-ngゲストエージェントのリリース版数 |
| `enable_firewall` | `false` | true の場合は既存ファイアウォールを停止しません。false で `config-disable-firewall.yml` が動作します。 |
| `common_selinux_state` | `"permissive"` | SELinux の望ましい状態を指定します。 |
| `common_disable_cron_mails` | `false` | true で `/etc/crontab` の `MAILTO` を空文字へ統一します。 |
| `common_envdir` | `/etc/default` ( Debian系の場合 ), `/etc/sysconfig` ( RHEL系の場合 ) | 環境ファイルを配置するディレクトリを OS に応じて切り替えます。 |
| `common_iface_deny_regex` | `"^(docker\|br-\|veth\|virbr\|vboxnet\|vmnet\|vnet\|tun\|tap\|wg\|tailscale\|zt\|lo)"` | DNS 更新対象から除外したいインターフェース名の正規表現。 |
| `common_autonetconfig_prefix` | `{{ netconfig_prefix }}` | 既存自動ネットワーク設定を退避するパスのプレフィックスです。 |
| `use_nm_ddns_update_scripts` | `false` | Dynamic DNS 連携スクリプト一式を展開する。 |
| `common_sysctl_user_ptrace_enable` | `true` | true で `kernel.yama.ptrace_scope` を 0 に設定しユーザ ptrace を許可します。 |
| `common_sysctl_user_dmesg_enable` | `true` | true で `kernel.dmesg_restrict` を 0 に設定し一般ユーザの `dmesg` を許可します。 |
| `common_sysctl_inotify_max_user_watches` | `524288` | `fs.inotify.max_user_watches` に適用する上限値。 |
| `sudo_nopasswd_groups_extra` | `['adm', 'cdrom', 'sudo', 'dip', 'plugdev', 'lxd', 'systemd-journal']` | NOPASSWD を付与する追加グループ。 |
| `sudo_nopasswd_groups_autodetect` | `true` | `sudo` / `wheel` の自動検出を有効にします。 |
| `sudo_nopasswd_absent` | `false` | true でドロップインを削除 (ロールバック) します。 |
| `sudo_dropin_prefix` | `"99-nopasswd"` | `/etc/sudoers.d` に生成するファイル名の接頭辞。 |
| `common_default_nic` | `"ens160"` | 管理用 NIC の既定名。 |
| `netif_nm_link_dir_rhel` | `"/etc/systemd/network"` | RHEL 系の systemd `.link` 配置ディレクトリ。 |
| `netif_nm_link_dir_debian` | `"/etc/systemd/network"` | Debian 系の systemd `.link` 配置ディレクトリ。 |
| `netif_nm_link_dir` | `/etc/systemd/network` | 実際に使用する `.link` 配置先。 |
| `mgmt_nic` | `""` | 管理用 NIC を明示するための変数。空の場合は後続タスクが `common_default_nic` で補完します。 |
| `gateway4` | `""` | IPv4 デフォルトゲートウェイのフォールバック値。 |
| `gateway6` | `""` | IPv6 デフォルトゲートウェイのフォールバック値。 |
| `ipv4_name_server1` | `""` | IPv4 DNS サーバ 1 のフォールバック値。 |
| `ipv4_name_server2` | `""` | IPv4 DNS サーバ 2 のフォールバック値。 |
| `ipv6_name_server1` | `""` | IPv6 DNS サーバ 1 のフォールバック値。 |
| `ipv6_name_server2` | `""` | IPv6 DNS サーバ 2 のフォールバック値。 |
| `_mgmt_ignore_auto_ipv4_dns` | `ipv4_name_server1`または`ipv4_name_server2`が定義されている場合は真 | IPv4 DNS を自動取得から除外する。 |
| `_mgmt_ignore_auto_ipv6_dns` | `ipv6_name_server1`または`ipv6_name_server2`が定義されている場合は真 | IPv6 DNS を自動取得から除外する。 |
| `_common_network_iface` | `mgmt_nic`変数の設定値, `mgmt_nic`変数未定義の場合, `common_default_nic`変数の設定値(`ens160`)。 | 各種スクリプトが参照する代表 NIC 名。 |
| `ddns_client_update_base` | `"ddns-client-update"` | DDNS 更新スクリプトのベース名。 |
| `ddns_client_update_sh_basename` | `{{ddns_client_update_base}}.sh` | `ddns-client-update.sh` のファイル名。 |
| `ddns_client_update_sh_dest_dir` | `"/usr/local/sbin"` | `ddns-client-update.sh` を配置するディレクトリ。 |
| `ddns_client_update_sh_path` | `{{ ddns_client_update_sh_dest_dir }}/{{ ddns_client_update_sh_basename }}` | スクリプト本体のフルパス。 |
| `ddns_client_update_sh_sysconfig_path` | `{{ common_envdir }}/{{ ddns_client_update_base }}` | スクリプト用環境ファイルの配置先。 |
| `dns_ddns_key_file` | `"/etc/nsupdate/ddns-clients.key"` | TSIG 鍵の配置先。 |
| `dns_ddns_key_name` | `"ddns-clients"` | TSIG 鍵のキー名。 |
| `nm_ra_addr_watch_base` | `"nm-ra-addr-watch"` | RA 監視ワーカーのベース名。 |
| `nm_ra_addr_watch_basename` | `{{ nm_ra_addr_watch_base }}` | ワーカ実体のファイル名。 |
| `nm_ra_addr_watch_dest_dir` | `"/usr/local/libexec"` | ワーカスクリプトを配置するディレクトリ。 |
| `nm_ra_addr_watch_path` | `{{ nm_ra_addr_watch_dest_dir }}/{{ nm_ra_addr_watch_basename }}` | ワーカのフルパス。 |
| `nm_ra_addr_watch_interval` | `10` | RA 監視ワーカーのポーリング間隔 (秒)。 |
| `nm_ra_addr_watch_iface_allow_regex` | `"^{{ _common_network_iface }}$"` | 監視対象インターフェースの正規表現。 |
| `nm_ra_addr_watch_iface_deny_regex` | `{{ common_iface_deny_regex }}` | 監視除外インターフェースの正規表現。 |
| `nm_ra_addr_watch_debounce_ms` | `800` | Dispatcher 通知前のデバウンス時間 (ミリ秒)。 |
| `nm_ra_addr_watch_sysconfig_path` | `{{ common_envdir }}/{{ nm_ra_addr_watch_basename }}` | ワーカー環境ファイルの配置先。 |
| `nm_dispatcher_path` | `"/etc/NetworkManager/dispatcher.d"` | Dispatcher スクリプトを格納するディレクトリ。 |
| `nm_ns_update_base` | `"nm-ns-update"` | NetworkManager dispatcher スクリプトのベース名。 |
| `nm_ns_update_num` | `"90"` | Dispatcher スクリプトの連番接頭辞。 |
| `nm_ns_update_basename` | `{{ nm_ns_update_num }}-{{ nm_ns_update_base }}` | Dispatcher スクリプトのファイル名。 |
| `nm_ns_update_path` | `{{ nm_dispatcher_path }}/{{ nm_ns_update_basename }}` | Dispatcher スクリプトのフルパス。 |
| `nm_ns_update_sysconfig_path` | `{{ common_envdir }}/{{ nm_ns_update_base }}` | Dispatcher 用環境ファイルの配置先。 |
| `nm_ns_update_iface_allow_regex` | `"^{{ _common_network_iface }}$"` | Dispatcher が処理する IF の正規表現。 |
| `nm_ns_update_iface_deny_regex` | `{{ common_iface_deny_regex }}` | Dispatcher が除外する IF の正規表現。 |

## 再起動発生ポイント

- `config-prepare-nm.yml`, `config-network-multi.yml`, `directory-dns-client.yml` はタスク末尾で無条件に再起動します。ネットワーク構成・Dispatcher を即時反映させる意図によるものです。
- `reboot.yml` は `/var/run/reboot-required` が存在するときのみ追加で再起動します。複数回の再起動が発生しうるため, ロール実行時間に余裕を持たせてください。

## 検証ポイント

- NetworkManager 切り替え後に `nmcli device status` で不要な legacy 接続が残存していないこと, `ip -br addr` でテンプレート通りの IP が得られていること。
- `/etc/sysctl.d/10-ptrace.conf`, `/etc/sysctl.d/10-kernel-hardening.conf`, `/etc/sysctl.d/90-sysctl-inotify.conf` に意図した値が書き込まれ, `sysctl --system` 後に `sysctl kernel.yama.ptrace_scope` などが反映されていること。
- `sudo -l` で `sudo_dropin_prefix` 付きのドロップインが読み込まれていること。`visudo -cf /etc/sudoers` が成功すること。
- `use_nm_ddns_update_scripts: true` の場合, `systemctl status nm-ra-addr-watch` と `journalctl -u NetworkManager-dispatcher` で Dispatcher が正しく実行され, `/usr/local/sbin/ddns-client-update.sh --update-now` で DNS 更新が成功すること。
- Debian 系では `netplan get` と `netplan try` で設定内容を確認し, RHEL 系では `nmcli connection show <netif>` でテンプレート値が反映されていること。

## 再実行時の注意

- ネットワーク関連タスクはインターフェースを数十秒単位で切り替えるため, 管理セッションが中断される可能性があります。再実行は安全なメンテナンス時間に限定してください。
- `directory-dns-client.yml` は既存の TSIG 鍵・Dispatcher を上書きします。差し替え後は速やかに DNS 側での疎通確認を行ってください。
- 初回実行で生成されたテンプレート (例: `/etc/NetworkManager/system-connections/*.nmconnection`) を手修正した場合, 再実行時にテンプレート内容へ戻されます。変更は変数側へ反映する前提で運用してください。

## IPアドレスのDNSへの登録処理 (tasks/directory-dns-clients.yml)

### nm-ra-addr-watch / NetworkManager Dispatcher / DDNS 更新の確認手順

本節では, 以下の項目を確認する手順を示す。

- SLAAC/RA による IPv6 アドレス変化を netlink で検知し, NetworkManager Dispatcher に独自ステート `ra-addr-change` で通知するワーカー **nm-ra-addr-watch** が正しく常駐・通知できているかを確認する。
- Dispatcher スクリプト **90-nm-ns-update** が通知を受けて DDNS 更新スクリプトを起動できること, ならびに systemd・NetworkManager の設定が適正であることを確認する。
- **ddns-client-update.sh** により DNS の正/逆引きが更新・参照できること, state ファイルと起動時刻の整合性, DNS サーバ側のログで更新が記録されていることを確認する。

---

#### 事前前提・用語

- 以降のコマンドは原則 root で実行 ( `sudo -i` など )。
- 主要ファイル/パス:
  - ワーカー: `/usr/local/libexec/nm-ra-addr-watch`
  - Dispatcher: `/etc/NetworkManager/dispatcher.d/90-nm-ns-update`
  - 環境ファイル ( OS別 ):
    - Debian/Ubuntu: `/etc/default/nm-ra-addr-watch`
    - RHEL系: `/etc/sysconfig/nm-ra-addr-watch`
  - systemd ユニット: `/etc/systemd/system/nm-ra-addr-watch.service`
  - DDNS ステート: `/var/lib/ddns/ipv4-published`, `/var/lib/ddns/ipv6-published`
  - DDNS スクリプト: `/usr/local/sbin/ddns-client-update.sh`

---

#### nm-ra-addr-watch ( 常駐ワーカー )の基本確認

1. 実体と実行権

   ```bash
   ls -l /usr/local/libexec/nm-ra-addr-watch
   file /usr/local/libexec/nm-ra-addr-watch
   bash --version | head -1
   ```

   - `-rwxr-xr-x` など実行権があること。
   - bash 4.3+ 推奨 ( 出力例: `GNU bash, version 5.x` )。

2. systemd ユニットと EnvironmentFile の解決

   ```bash
   systemctl cat nm-ra-addr-watch
   systemctl show nm-ra-addr-watch -p EnvironmentFiles -p ExecStart
   ```

   - `EnvironmentFiles=` に OS に応じた環境ファイルが表示されること。
   - `ExecStart=` が **余計な引用符なし** or systemd 的に正しく解決されていること ( 本ロールは `{{ nm_ra_addr_watch_path | to_json }}` で安全化済 )。

3. 環境ファイルの内容 ( いずれか存在 )

   ```bash
   cat /etc/default/nm-ra-addr-watch 2>/dev/null || cat /etc/sysconfig/nm-ra-addr-watch
   ```

   - `IFACE_ALLOW_REGEX` / `IFACE_DENY_REGEX` / `DEBOUNCE_MS` / `DISPATCHER_PATH` / `LOG_LEVEL` が期待値。

4. サービス状態とログ

   ```bash
   systemctl status -l --no-pager nm-ra-addr-watch
   journalctl -t nm-ra-addr-watch -b        # タグで追う
   journalctl -u nm-ra-addr-watch -b        # unit で追う
   ```

   - `Active: active (running)`。
   - 起動時に `[Info] start (DISPATCHER_PATH=... ALLOW=... DENY=... DEBOUNCE_MS=...)` が出る ( `LOG_LEVEL>=4`時 )。
   - 何らかの RA に伴うイベントで `event captured -> dispatcher (IFACE=... state=ra-addr-change)` が出力。

5. 手動トリガテスト ( ネットワーク変化を作る )

   - IPv6 アドレス再生成を誘発 ( どちらかの例 ):

     ```bash
     # 一時的に IPv6 を揺らす例 ( IF は環境に合わせる )
     nmcli con down "ansible-managed" && sleep 1 && nmcli con up "ansible-managed"
     # もしくは
     sudo ip -6 addr flush dev <IFACE>; sleep 2; sudo systemctl restart NetworkManager
     ```

   - 直後のログ:

     ```bash
     journalctl -t nm-ra-addr-watch -b -n 50 -f
     ```

   - `dispatcher returned non-zero` が出る場合は, Dispatcher のパスや実行権, スクリプト内のエラーを確認 ( 次章参照 )。

---

#### NetworkManager Dispatcher ( 90-nm-ns-update )の確認

1. 実体・実行権

   ```bash
   ls -l /etc/NetworkManager/dispatcher.d/90-nm-ns-update
   file /etc/NetworkManager/dispatcher.d/90-nm-ns-update
   ```

   - 実行可能であること。shebang が妥当であること ( `/bin/bash` 等 )。

2. 単体実行テスト ( nm-ra-addr-watch 経由と同等の引数 )

   ```bash
   IFACE=$(nmcli -t -f DEVICE con show --active | head -1)
   /etc/NetworkManager/dispatcher.d/90-nm-ns-update "$IFACE" ra-addr-change || echo "non-zero"
   ```

   - 非ゼロ終了時は当該スクリプトのログ/標準エラーを確認。
     ※ 本ワーカーは非ゼロでも継続する設計。

3. NetworkManager 側のフック/環境
   - `90-nm-ns-update` が **/etc/NetworkManager/dispatcher.d/** 直下にあり, `no-wait.d` 配下ではないこと。
   - スクリプト内部で必要なコマンド ( `ip`, `logger`, `nsupdate` 等 )PATH を明示するか, 絶対パスを利用。

---

#### DDNS スクリプト ( ddns-client-update.sh )の確認

1. 実体・実行権・依存コマンド

   ```bash
   ls -l /usr/local/sbin/ddns-client-update.sh
   file /usr/local/sbin/ddns-client-update.sh
   which nsupdate || command -v nsupdate
   which dig || command -v dig
   ```

2. 単体実行テスト ( dry-run もしくは安全な更新先 )

   ```bash
   /usr/local/sbin/ddns-client-update.sh --help 2>&1 | head -20
   # 実更新テスト ( 環境に応じて )
   /usr/local/sbin/ddns-client-update.sh --update-now -v
   ```

   - 失敗時は Exit code とエラーログで原因特定 ( 権限, 鍵, サーバ到達性など )。

3. ステートファイルの存在と内容

   ```bash
   ls -l /var/lib/ddns
   cat /var/lib/ddns/ipv4-published
   cat /var/lib/ddns/ipv6-published
   ```

   - IPv4/IPv6 共に「現在系」の公開値になっていること。

4. ステートファイルの時刻と uptime の整合

   ```bash
   stat -c '%y %n' /var/lib/ddns/ipv*-published
   uptime -s
   ```

   - **初回起動直後に更新が走る設計**であれば, 少なくともブート後のタイムスタンプであること。
   - 直近で RA/再起動試験を行ったなら, その時刻付近で更新されていること。

5. サービス状態とログ

```bash
  systemctl status -l --no-pager NetworkManager-dispatcher.service
  journalctl -t ns-update -b # タグで追う
```

- `enabled;`になっていること(イベント発生にD-BUS経由で呼ばれるため, `Active: inactive (dead)`になるは, 問題ない)。
- `Started NetworkManager-dispatcher.service - Network Manager Script Dispatcher Service.`がでること。
- 起動時に `[Info] start ...` が出ること ( `LOG_LEVEL>=4`時 )。

- 運用時は LOG_LEVEL=2 ( Error のみ )を推奨。調査時は 4 or 5。

---

#### DNS の正/逆引き確認 ( 外部ホストからの参照含む )

1. 名前解決 ( 正引き )

   ```bash
   dig +short A   <host.example.org> @<dns-server>
   dig +short AAAA <host.example.org> @<dns-server>
   nslookup <hostname> <dns-server>
   ```

   - 期待する `A` / `AAAA` が応答。

2. 逆引き ( IPv4 / IPv6 )

   ```bash
   nslookup <ipv4-addr> <dns-server>
   nslookup <ipv6-addr> <dns-server>
   ```

   - PTR がホスト名を返す。

3. キャッシュ/伝播の注意
   - 変更直後はキャッシュ影響あり。`+trace` や直接権威サーバに問合せて切り分け。

---

#### DNS サーバ側の更新ログ確認

- BIND の例 ( 権威サーバ ):

  ```bash
  # 更新系ログ ( 設定に応じてファイルは異なる )
  sudo grep -i 'update' /var/log/named/named.log /var/log/messages /var/log/syslog 2>/dev/null | grep 'named' | tail -n 50
  ```

- `nsupdate` による `UPDATE` 要求が対象ゾーンに到達・許可されていること ( `update: info: client ... updating ...` など )。
- 鍵 ( TSIG 等 )の検証失敗や ACL 拒否がないこと。

---

#### 検証作業例 ( 端末操作, ワーカー, Dispatcher, Dynamic DNS, DNS 応答 )

1. ネットワーク変化を発生 ( RA による IPv6 変化を狙う )

   ```bash
   sudo ip -6 addr flush dev <IFACE>
   sleep 2
   sudo systemctl restart NetworkManager
   ```

2. ワーカーのログで `ra-addr-change` 通知, Dispatcher 実行を確認。
3. ステートファイル `ipv6-published` が更新されることを確認。
4. 権威 DNS で AAAA/PTR が更新され, 別ホストからの `nslookup` が最新を返すこと。

---

#### 典型トラブルと対処チェックリスト

- **`dispatcher returned non-zero`**
  - `/etc/NetworkManager/dispatcher.d/90-nm-ns-update` の実行権, shebang, 依存コマンド PATH, 不正なリダイレクト/改行 ( テンプレ展開ミスで行末にコメントがくっつく等 )がないか。
- **`No such file or directory` ( Dispatcher パス関連 )**
  - 環境ファイルの `DISPATCHER_PATH=` と実ファイルのパスが一致しているか。systemd の EnvironmentFile が正しく読まれているか。
- **systemd の `ExecStart` 引用符問題**
  - 余計なダブルクォートは避ける。`to_json` フィルタにより空白を含む場合でも systemd 的に妥当な記法に整形済 ( さらに空白を含まないパス運用が無難 )。
- **IPv6 アドレスイベントが拾えない**
  - `IFACE_ALLOW_REGEX` / `IFACE_DENY_REGEX` の見直し。`should_handle_iface` の判定 ( 物理 NIC 前提 )に引っかかっていないか。`/sys/class/net/<if>/device` の有無で物理扱いか確認。
- **DDNS 更新が成功しない**
  - `nsupdate` 到達性, TSIG 鍵, ゾーン設定, ACL, SELinux/AppArmor ( 必要に応じてルール調整 )。
- **ジャーナルが少ない**
  - `LOG_LEVEL=4` ( Info )または `5` ( Debug )に一時的に上げ, `journalctl -t nm-ra-addr-watch -f` で追跡。

---

#### テスト後の環境復元

- 変更した LOG_LEVEL を `2` に戻す。
- 一時的に down/up した通信を復元, 必要なら `systemctl restart NetworkManager`。

---

#### 付録: 期待ログ例 ( 抜粋 )

```:text
[Info] start (DISPATCHER_PATH=/etc/NetworkManager/dispatcher.d/90-nm-ns-update ALLOW=^ens160$ DENY=^(docker|br-).* DEBOUNCE_MS=800)
[Info] event captured -> dispatcher (IFACE=ens160 state=ra-addr-change)
[Warning] dispatcher returned non-zero (IFACE=ens160, dispatcher=/etc/NetworkManager/dispatcher.d/90-nm-ns-update)
```

- 運用時は LOG_LEVEL=2 ( Error のみ )を推奨。調査時は, `4` または, `5`に設定。
