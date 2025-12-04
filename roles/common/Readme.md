# 共通処理

- [共通処理](#共通処理)
  - [ロールの目的 ( 要約 )](#ロールの目的--要約-)
  - [実行フロー ( 主たる tasks )](#実行フロー--主たる-tasks-)
    - [基本設定 ( `tasks/config.yml` )](#基本設定--tasksconfigyml-)
    - [sudoers 管理 ( `tasks/config-sudoer.yml` )](#sudoers-管理--tasksconfig-sudoeryml-)
    - [sysctl 調整 ( `tasks/sysctl.yml` )](#sysctl-調整--taskssysctlyml-)
    - [cron メール抑止 ( `tasks/cron-setting.yml` )](#cron-メール抑止--taskscron-settingyml-)
    - [パッケージとリポジトリ ( `tasks/package.yml` / `tasks/kubectl-repositories.yml` / `tasks/common-packages.yml` )](#パッケージとリポジトリ--taskspackageyml--taskskubectl-repositoriesyml--taskscommon-packagesyml-)
    - [DDNS 連携 ( ディレクトリ・テンプレート・サービス一式 )](#ddns-連携--ディレクトリテンプレートサービス一式-)
    - [サービス ( `tasks/service.yml` )](#サービス--tasksserviceyml-)
    - [ユーザ/グループ操作 ( `tasks/user_group.yml` )](#ユーザグループ操作--tasksuser_groupyml-)
    - [再起動 ( `tasks/reboot.yml` )](#再起動--tasksrebootyml-)
  - [ハンドラ ( `handlers/` )](#ハンドラ--handlers-)
  - [主要テンプレートと変数](#主要テンプレートと変数)
    - [ネットワーク ( netplan )](#ネットワーク--netplan-)
    - [sudoers](#sudoers)
    - [DDNS / Dispatcher / RA 監視](#ddns--dispatcher--ra-監視)
  - [使い方 ( 変数定義の置き所 )](#使い方--変数定義の置き所-)
  - [IPアドレスのDNSへの登録処理 (tasks/directory-dns-clients.yml)](#ipアドレスのdnsへの登録処理-tasksdirectory-dns-clientsyml)
    - [nm-ra-addr-watch / NetworkManager Dispatcher / DDNS 更新の確認手順](#nm-ra-addr-watch--networkmanager-dispatcher--ddns-更新の確認手順)
      - [事前前提・用語](#事前前提用語)
      - [nm-ra-addr-watch ( 常駐ワーカー )の基本確認](#nm-ra-addr-watch--常駐ワーカー-の基本確認)
      - [NetworkManager Dispatcher ( 90-nm-ns-update )の確認](#networkmanager-dispatcher--90-nm-ns-update-の確認)
      - [DDNS スクリプト ( ddns-client-update.sh )の確認](#ddns-スクリプト--ddns-client-updatesh-の確認)
      - [DNS の正/逆引き確認 ( 外部ホストからの参照含む )](#dns-の正逆引き確認--外部ホストからの参照含む-)
      - [DNS サーバ側の更新ログ確認](#dns-サーバ側の更新ログ確認)
      - [総合 E2E ( 端末操作, ワーカー, Dispatcher, Dynamic DNS, DNS 応答 )](#総合-e2e--端末操作-ワーカー-dispatcher-dynamic-dns-dns-応答-)
      - [典型トラブルと対処チェックリスト](#典型トラブルと対処チェックリスト)
      - [後片付け ( テスト後の復元 )](#後片付け--テスト後の復元-)
      - [付録: 期待ログ例 ( 抜粋 )](#付録-期待ログ例--抜粋-)

## ロールの目的 ( 要約 )

Ubuntu 系サーバの初期セットアップを一括で行うベースロールです。主な役割は以下です。

- タイムゾーン設定
- 既存の自動ネットワーク設定の退避および **NetworkManager レンダラ**での netplan 生成 ( DHCP/固定 IP 両対応 )
- **sudoers** の NOPASSWD 設定を安全にドロップイン管理 ( 変更前後に `visudo -cf` で構文検証 )
- 監視・デバッグ用途の `sysctl` 調整 ( `ptrace` / `dmesg` / `inotify` )
- `/etc/crontab` の `MAILTO` 抑止 ( オプション )
- APT の前提・共通パッケージ導入, Kubernetes リポジトリ登録, `apt-file update`
- mDNS ( Avahi )導入と GUI 無効化 ( サーバ用途 )
- **Dynamic DNS 連携一式** ( TSIG 鍵, 更新スクリプト, NM dispatcher, RA/SLAAC 監視サービス )
- 再起動が必要な場合の安全なリブート ( SSH 復帰待ちを含む )

---

## 実行フロー ( 主たる tasks )

### 基本設定 ( `tasks/config.yml` )

- `timedatectl set-timezone "{ common_timezone }"` でタイムゾーン設定。
- `common_autonetconfig_prefix` 配下の既存 **自動ネットワーク設定** ファイル ( `common_autonetconfig_files` )を検出し, `*.old` へリネーム退避。
- **netplan 生成**：
  - レンダラは **NetworkManager** 固定。
  - DHCP 用 ( `templates/99-netcfg-dhcp.yaml.j2` )と固定 IP 用 ( `templates/99-netcfg.yaml.j2` )を条件分岐。
  - NIC は `mgmt_nic` が未定義なら `common_default_nic` ( 既定 `ens160` )。
  - `ipv4_name_server1/2`, `dns_search`, 固定時は `static_ipv4_addr` / `network_ipv4_prefix_len` / `static_ipv6_addr` / `network_ipv6_prefix` を反映。

### sudoers 管理 ( `tasks/config-sudoer.yml` )

- `/etc/sudoers.d` の存在と適正パーミッションを保証。
- `/etc/sudoers` が `/etc/sudoers.d` を `#includedir` しているかの **確認のみ** ( 変更はしない )。
- ドロップイン変更の **前後で `visudo -cf /etc/sudoers`** を実行し, 構文を検証。
- NOPASSWD ドロップインをテンプレート生成：
  - ユーザ: `sudo_nopasswd_users`
  - グループ: `sudo_nopasswd_groups_autodetect` ( `sudo`/`wheel` 自動検出 )＋ `sudo_nopasswd_groups_extra`
  - 削除方針: `sudo_nopasswd_absent` が真なら既存ドロップインを除去。
  - ファイル名は `{ sudo_dropin_prefix }-user-<name>`, `{ sudo_dropin_prefix }-group-<name>`。

### sysctl 調整 ( `tasks/sysctl.yml` )

- `common_sysctl_user_ptrace_enable` が真なら `/etc/sysctl.d/10-ptrace.conf` (`sysctl_ptrace_conf_path`変数で定義) に `kernel.yama.ptrace_scope = 0` を書き込み, ユーザの `ptrace` を許可します。
- `common_sysctl_user_dmesg_enable` が真なら `/etc/sysctl.d/10-kernel-hardening.conf` (`sysctl_dmesg_conf_path`変数で定義) に `kernel.dmesg_restrict = 0` を書き込み, 一般ユーザによる `dmesg` 実行を許可します。
- `common_sysctl_inotify_max_user_watches` の値を `/etc/sysctl.d/90-sysctl-inotify.conf` (`sysctl_inotify_conf_path`変数で定義) に反映し, `fs.inotify.max_user_watches` を既定 524288 へ引き上げます。

### cron メール抑止 ( `tasks/cron-setting.yml` )

- `common_disable_cron_mails` が真の場合, `/etc/crontab` の `MAILTO=` を除去し, 未設定なら `MAILTO=""` を追記。

### パッケージとリポジトリ ( `tasks/package.yml` / `tasks/kubectl-repositories.yml` / `tasks/common-packages.yml` )

- 事前パッケージ ( `k8s_common_prerequisite_packages` )導入。
- Kubernetes の GPG キーをキーファイルとして保存し, `kubernetes.list` を配置, `apt-get update` 実施。
- 共通パッケージ群 ( `common_packages` )導入。ハンドラで GUI 無効化 ( `disable_gui` )と `apt autoremove -y` を通知。
- `apt-file update` の実行。
- 言語パック ( `common_langpack_packages` ), mDNS ( `common_mdns_packages` ), VMware 用 ( `common_vmware_packages` )を導入 ( 必要に応じてハンドラ起動 )。
- Docker 関連はコメントアウト済みで, このロールでは導入しない方針。

### DDNS 連携 ( ディレクトリ・テンプレート・サービス一式 )

- `/etc/nsupdate` を作成し, **TSIG 鍵** ( `ddns-clients-key-file.j2` )を配置。
- **更新スクリプト**：`/usr/local/sbin/ddns-client-update.sh` ( `ddns-client-update.sh.j2` )。
- **NetworkManager dispatcher**：`/etc/NetworkManager/dispatcher.d/90-nm-ns-update` ( `90-nm-ns-update.j2` )。
- **RA/SLAAC 監視**：ワーカ `/usr/local/libexec/nm-ra-addr-watch` と **systemd unit** ( `nm-ra-addr-watch.j2`, `nm-ra-addr-watch.service.j2`, 環境ファイル `sysconfig-nm-ra-addr-watch.j2` )。
  - `nm_ra_addr_watch_*` 変数で監視インターフェース, デバウンス, LOG_LEVEL, インターバルなどを調整可能。
- `nm-ra-addr-watch` と `NetworkManager-dispatcher` を **enabled**。
- ディスパッチャ構成を更新した場合は, SSH ポートを特定して安全に **再起動**。

### サービス ( `tasks/service.yml` )

- 現時点では拡張用のフック ( 空 or 近い構成 )。

### ユーザ/グループ操作 ( `tasks/user_group.yml` )

- 今はコメント例 ( 例: `docker` グループ追加の雛形 )。

### 再起動 ( `tasks/reboot.yml` )

- `/var/run/reboot-required` がある場合：
  - GUI 無効化ハンドラ通知
  - SSH ポート特定 から `sleep 2 && reboot` を非同期実行
  - シャットダウン待ち から 起動待ち ( SSH 復帰まで )

---

## ハンドラ ( `handlers/` )

- **disable_gui.yml**：`systemctl set-default multi-user.target`
- **auto-remove.yml**：`apt autoremove -y`
- **avahi.yml**：`avahi-daemon` の restart + enable

---

## 主要テンプレートと変数

### ネットワーク ( netplan )

- テンプレート：`99-netcfg-dhcp.yaml.j2` / `99-netcfg.yaml.j2`
- 主な変数：
  - `mgmt_nic` ( 未定義時は `common_default_nic` )
  - `ipv4_name_server1`, `ipv4_name_server2`, `dns_search`
  - 固定 IP 時：`static_ipv4_addr`, `network_ipv4_prefix_len`, `static_ipv6_addr`, `network_ipv6_prefix`

### sudoers

- `sudo_nopasswd_users`: NOPASSWD を付与するユーザの一覧
- `sudo_nopasswd_groups_autodetect`: `sudo` / `wheel` グループを自動検出して NOPASSWD 付与
- `sudo_nopasswd_groups_extra`: 追加で NOPASSWD を付与するグループ
- `sudo_dropin_prefix`: ドロップインファイルの接頭辞
- `sudo_nopasswd_absent`: 真なら既存ドロップインを削除

### DDNS / Dispatcher / RA 監視

- 鍵：`dns_ddns_key_name`, `dns_ddns_key_secret`
- スクリプトパス：`ddns_client_update_sh_path` ( 既定 `/usr/local/sbin/ddns-client-update.sh` )
- Dispatcher：`nm_ns_update_path` ( 既定 `/etc/NetworkManager/dispatcher.d/90-nm-ns-update` )
- 監視ワーカ：`nm_ra_addr_watch_*` ( IF 名, デバウンス, ログレベル, インターバル, 環境ファイルパスなど )

---

## 使い方 ( 変数定義の置き所 )

- **共通設定**：`group_vars/all.yml` に集約 ( 例：`common_timezone`, `common_default_nic`, `dns_search` など )。
- **ホスト固有**：`host_vars/<hostname>.yml` で上書き ( 例：固定 IP のみ特定ホストで指定 )。
- **DDNS 鍵**：機微情報は Ansible Vault で暗号化 ( `dns_ddns_key_secret` など )。

---

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
   dig +short A   <host.example.com> @<dns-server>
   dig +short AAAA <host.example.com> @<dns-server>
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

#### 総合 E2E ( 端末操作, ワーカー, Dispatcher, Dynamic DNS, DNS 応答 )

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

#### 後片付け ( テスト後の復元 )

- 変更した LOG_LEVEL を `2` に戻す。
- 一時的に down/up した通信を復元, 必要なら `systemctl restart NetworkManager`。

---

#### 付録: 期待ログ例 ( 抜粋 )

```:text
[Info] start (DISPATCHER_PATH=/etc/NetworkManager/dispatcher.d/90-nm-ns-update ALLOW=^ens160$ DENY=^(docker|br-).* DEBOUNCE_MS=800)
[Info] event captured -> dispatcher (IFACE=ens160 state=ra-addr-change)
[Warning] dispatcher returned non-zero (IFACE=ens160, dispatcher=/etc/NetworkManager/dispatcher.d/90-nm-ns-update)
```

- 運用時は LOG_LEVEL=2 ( Error のみ )を推奨。調査時は 4 or 5。
