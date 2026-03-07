# radvd ロール

このロールは Router Advertisement Daemon (radvd) を導入し, 管理ネットワーク向けに IPv6 ルーター広告 (Router Advertisement - RA) を配布します。Stateless Address Autoconfiguration (SLAAC) 用プレフィックスとデフォルトルート, RDNSS/DNSSL (DNS サーバ, サーチドメイン) 情報を RA で広告し, 設定ファイル `/etc/radvd.conf` から生成します。設定変更時は radvd を再起動します。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Router Advertisement | RA | IPv6ネットワークでルータが送信するICMPv6メッセージ, プレフィックスやDNS情報を配布 |
| Stateless Address Autoconfiguration | SLAAC | ルーター広告を用いたIPv6アドレス自動設定機構, DHCPサーバ不要 |
| Recursive DNS Server | RDNSS | ルーター広告で配布されるDNSサーバアドレス情報 |
| DNS Search List | DNSSL | ルーター広告で配布されるDNS検索ドメインリスト |
| Internet Protocol version 6 | IPv6 | 128ビットアドレス空間を持つ次世代インターネットプロトコル |
| Internet Control Message Protocol version 6 | ICMPv6 | IPv6ネットワークでの制御メッセージプロトコル, RA送信に使用 |
| Domain Name System | DNS | ドメイン名とIPアドレスを対応付ける名前解決システム |
| Operating System | OS | コンピュータのハードウェアとソフトウェアを管理する基本ソフトウェア |
| Network Interface | — | ホストがネットワークに接続するための物理的または仮想的なインターフェース, ens192やeth0などの名前で識別 |
| Prefix (IPv6) | — | IPv6アドレスのネットワーク部。記法: `2001:db8::/32` の`/32`がプレフィックス長 |
| Lifetime | — | IPv6アドレスやプレフィックスの有効期期間 ( 秒 ) 。有効期限(ValidLifetime)と推奨期限(PreferredLifetime)がある |
| Handler | — | Ansibleで, タスク実行後に条件付きで実行される処理。ファイル変更時の再起動などに使用 |
| Template | — | Ansibleで, 変数を埋め込む設定ファイルのひな形。Jinja2形式で記述 |
| Link-local Address | — | IPv6の自動割り当てアドレス。fe80::で始まる, ローカルネットワーク内でのみ有効 |

## 前提条件

このロールを実行する前に, 以下の前提条件を満たしていることを確認してください。

- **ホスト用途**: radvd はルータノード上で実行されることを想定しています。IPv6 通信を行うネットワークセグメントへの物理的な接続またはその代替が必要です。
- **IPv6 管理ネットワーク**: ロールで配布する IPv6 プレフィックス (`radvd_router_advertisement_prefix`) は事前に定義されている必要があります。通常は `vars/all-config.yml` や `host_vars/<hostname>` で `gpm_mgmt_ipv6_prefix`/`gpm_mgmt_ipv6_addr_prefix_len` として定義します。
- **ネットワークインターフェース**: `radvd_nic` パラメータに指定するネットワークインターフェース ( 例: `ens192`, `eth0` ) は対象ホストに存在する必要があります。
- **Ansible の権限**: ロール実行にはルート権限 ( `become: true` ) が必要です。パッケージ管理, 設定ファイル配置, サービス制御を行うため。

## 実行フロー

このロールは以下の 6 つのステップで逐次処理をします。

1. **Load Params** (`tasks/load-params.yml`): `vars/cross-distro.yml` から OS 別パッケージ名, サービス名を読み込みます。
2. **Package** (`tasks/package.yml`): radvd パッケージをインストールします。既にインストール済みの場合はスキップします。
3. **Directory** (`tasks/directory.yml`): radvd の補助ディレクトリが必要な場合は作成します。 ( 現在のテンプレート実装では空 )
4. **User Group** (`tasks/user_group.yml`): radvd 実行ユーザー, グループの管理が必要な場合は設定します。 ( 現在のテンプレート実装では空 )
5. **Config** (`tasks/config.yml`): テンプレート [templates/radvd.conf.j2](templates/radvd.conf.j2) から設定ファイルを生成し, `/etc/radvd.conf` に配置します。ファイルが変更された場合, `restart_radvd` ハンドラを通知します。
6. **Service** (`tasks/service.yml`): ハンドラ [handlers/restart-radvd.yml](handlers/restart-radvd.yml) で radvd サービスを再起動し, `enabled: true` で起動時の自動起動を有効化します。

各ステップは **`radvd_nic` が定義されており, かつ対象ホストのインターフェース一覧に存在する場合にのみ実行**されます。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `radvd_nic` | `{{ gpm_mgmt_nic \| default(mgmt_nic, true) }}` | RA を配布するインターフェース。 |
| `radvd_router_advertisement_min_interval` | `30` | RA 送信最小間隔 (秒)。 |
| `radvd_router_advertisement_max_interval` | `100` | RA 送信最大間隔 (秒)。 |
| `radvd_router_advertisement_prefix` | `{{ gpm_mgmt_ipv6_prefix }}/{{ gpm_mgmt_ipv6_addr_prefix_len }}` | 広告する IPv6 プレフィックス。 |
| `radvd_router_advertisement_reachable_time` | `3000` | AdvReachableTime (ms)。 |
| `radvd_router_advertisement_retrans_timer` | `1000` | AdvRetransTimer (ms)。 |
| `radvd_router_advertisement_default_lifetime` | `300` | デフォルトルータの lifetime (秒)。0 でデフォルトルート無効。 |
| `radvd_router_advertisement_prefix_valid_lifetime` | `'infinity'` | プレフィックスの有効期限。 |
| `radvd_router_advertisement_prefix_preferred_lifetime` | `'infinity'` | プレフィックスの推奨期限。 |
| `radvd_dns_servers` | `[ "{{ ipv6_name_server1 }}", "{{ ipv6_name_server2 }}" ]` | RDNSS に広告する DNS サーバ。 |
| `radvd_search_domains` | `[ "{{ dns_domain }}" ]` | DNSSL に広告する検索ドメイン。 |
| `radvd_package` | OS 依存 (`radvd`) | インストールするパッケージ名。`vars/cross-distro.yml` で解決。 |
| `radvd_service_name` | OS 依存 | 起動, 再起動するサービス名。`vars/cross-distro.yml` で解決。 |
| `radvd_config_file_path` | `/etc/radvd.conf` | 生成する設定ファイルのパス。 |

## 主な処理

このロールで実行される主要な処理は以下の通りです。

1. **OS 別パッケージ, サービス情報の読み込み** (`tasks/load-params.yml`)
   - `vars/cross-distro.yml` から Debian/RHEL のパッケージ名, サービス名を取得します。

2. **radvd パッケージの導入** (`tasks/package.yml`)
   - `radvd_package` 変数 ( 既定値: `radvd` ) で指定されたパッケージをインストールします。

3. **設定ファイルの生成と配置** (`tasks/config.yml`)
   - テンプレート [templates/radvd.conf.j2](templates/radvd.conf.j2) を用いて `/etc/radvd.conf` を生成します。
   - ファイルの内容が変更された場合, `restart_radvd` ハンドラを通知します。

4. **ハンドラによる再起動** (`handlers/restart-radvd.yml`)
   - systemd を使用して radvd サービスを再起動します。
   - `enabled: true` により起動時の自動起動を有効化します。

## テンプレートと出力

テンプレート [templates/radvd.conf.j2](templates/radvd.conf.j2) で以下の項目が設定されます。

### ルーター広告 ( RA ) の基本設定
- `AdvSendAdvert on;` — ルーター広告を有効化。
- `MinRtrAdvInterval {{ radvd_router_advertisement_min_interval|default(30, true) }};` — RA 送信最小間隔 ( 秒 ) 。既定値 30 秒。
- `MaxRtrAdvInterval {{ radvd_router_advertisement_max_interval|default(100, true) }};` — RA 送信最大間隔 ( 秒 ) 。既定値 100 秒。
- `AdvReachableTime {{ radvd_router_advertisement_reachable_time|default(3000, true) }};` — 可到達時間 ( ミリ秒 ) 。既定値 3000ms。
- `AdvRetransTimer {{ radvd_router_advertisement_retrans_timer|default(1000, true) }};` — 再送時間 ( ミリ秒 ) 。既定値 1000ms。
- `AdvDefaultLifetime {{ radvd_router_advertisement_default_lifetime|default(300, true) }};` — デフォルトルータの有効期限 ( 秒 ) 。既定値 300 秒。デフォルトルート無効の場合は 0 に設定。

### SLAAC とプレフィックス設定
- `AdvManagedFlag off;`, `AdvOtherConfigFlag off;` — DHCPv6 不使用を示し, SLAAC のみで自動設定。
- `prefix {{ radvd_router_advertisement_prefix }} { ... }` — 広告するプレフィックス。
  - `AdvValidLifetime {{ radvd_router_advertisement_prefix_valid_lifetime|default('infinity', true) }};` — プレフィックスの有効期限。既定値 `infinity` ( 無期限 ) 。
  - `AdvPreferredLifetime {{ radvd_router_advertisement_prefix_preferred_lifetime|default('infinity', true) }};` — プレフィックスの推奨期限。既定値 `infinity`。
  - `AdvAutonomous on;` — プレフィックスのオートノマスフラグ有効化 ( A フラグ ) 。
  - `AdvOnLink on;` — プレフィックスの on-link フラグ有効化 ( L フラグ ) 。

### DNS 情報配布 (RDNSS/DNSSL)
- `RDNSS {{ radvd_dns_servers | default([], true) | join(' ') }} { };` — DNS サーバアドレスを空白区切りで広告。
- `DNSSL {{ radvd_search_domains | default([], true) | join(' ') }} { };` — DNS サーチドメインリストを空白区切りで広告。

## ハンドラ

### restart-radvd (handlers/restart-radvd.yml)

設定ファイル `/etc/radvd.conf` が変更された場合に実行されます。

- **動作**: systemd サービス `{{ radvd_service_name }}` を restart します。
- **自動起動**: `enabled: true` により, システム起動時に radvd が自動的に起動されるよう設定します。

## OS 差異

radvd パッケージ, サービス名は OS によって異なります。`vars/cross-distro.yml` で以下のように定義されています。

| 項目 | Debian/Ubuntu | RHEL/CentOS | 説明 |
| --- | --- | --- | --- |
| パッケージ名 | `radvd` | `radvd` | 両 OS で共通 |
| サービス名 | `radvd` | `radvd` | 両 OS で共通 |
| 設定ファイルパス | `/etc/radvd.conf` | `/etc/radvd.conf` | 両 OS で共通 |

## 実行方法

### 前提条件

- ロール実行前に, ansible インベントリファイル (`inventory/hosts`) で対象ホストを指定してください。
- 対象ホストへのログイン権限とルート実行 ( `become: true` ) の権限が必要です。

### Make を使用した実行

Makefile に `run_radvd` ターゲットが定義されている場合：

```bash
make run_radvd
```

このコマンドは以下の ansible-playbook 実行と同等です。

### ansible-playbook を使用した直接実行

```bash
# site.yml (全ロール) を実行
ansible-playbook -i inventory/hosts site.yml

# radvd ロールのみを実行 ( タグ指定 )
ansible-playbook -i inventory/hosts site.yml --tags "radvd"

# 特定ホストのみを実行
ansible-playbook -i inventory/hosts site.yml --tags "radvd" -l router.local

# Playbook を検証モードで実行 ( 実際は変更しない )
ansible-playbook -i inventory/hosts site.yml --tags "radvd" --check
```

### 主要なオプション

- `-i inventory/hosts` — インベントリファイルを指定。
- `--tags "radvd"` — radvd ロールのみを実行 ( 他のロールはスキップ ) 。
- `-l router.local` — 特定ホストのみをターゲット ( 複数指定可: `-l router.local,router2.local` ) 。
- `--check` — dry-run モード ( 実際に変更を加えない ) 。

### 変数の上書き

ロール実行時に変数を上書きする場合：

```bash
# コマンドラインで指定
ansible-playbook -i inventory/hosts site.yml --tags "radvd" \
  -e "radvd_router_advertisement_min_interval=60" \
  -e "radvd_router_advertisement_max_interval=200"

# 外部変数ファイルで指定
ansible-playbook -i inventory/hosts site.yml --tags "radvd" -e @vars/custom-radvd.yml
```

または, `group_vars/all/all.yml` や `host_vars/<hostname>` で事前に設定してください。

## 検証

このセクションでは, ロール実行後に radvd が正常に動作していることを確認する検証手順を記載します。

### 検証前提条件

- ロール実行が正常に完了していること。
- radvd が実行されているルータノードへのアクセス権限があること。
- IPv6 を設定されたクライアント ( またはテストホスト ) へのアクセス権限があること。
- 必要なコマンド ( `systemctl`, `radvdump`, `tcpdump`, `journalctl` など ) が利用可能であること。

### Step 1: radvd サービスの起動状態確認

**実施ノード**: radvd が実行されているルータノード

**コマンド**:
```bash
systemctl status radvd
systemctl is-enabled radvd
```

**期待される出力例**:
```
● radvd.service - IPv6 Router Advertisement Daemon
     Loaded: loaded (/lib/systemd/system/radvd.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2025-01-20 10:30:00 UTC; 2 days ago
   Main PID: 1234 (radvd)
      Tasks: 1 (limit: 4672)
     Memory: 1.5M
        CPU: 0ms
     CGroup: /system.slice/radvd.service
             └─1234 /usr/sbin/radvd -u radvd -p /var/run/radvd/radvd.pid
```

**確認ポイント**:
- 状態が `active (running)` であること。
- `Loaded: loaded` でサービスが読み込まれていること。`enabled` により起動時に自動起動。
- PID が割り当てられており, radvd プロセスが実行中であること。

### Step 2: 設定ファイルの内容確認

**実施ノード**: radvd が実行されているルータノード

**コマンド**:
```bash
cat /etc/radvd.conf | grep -E "(interface|MinRtrAdvInterval|MaxRtrAdvInterval|prefix|RDNSS|DNSSL|AdvDefaultLifetime)"
```

**期待される出力例**:
```
interface ens192 {
        AdvSendAdvert on;
        MinRtrAdvInterval 30;
        MaxRtrAdvInterval 100;
        AdvDefaultLifetime 300;
        AdvManagedFlag off;
        AdvOtherConfigFlag off;
        prefix fd00:1234:5678:1::/64 {
                AdvValidLifetime infinity;
                AdvPreferredLifetime infinity;
                AdvAutonomous on;
                AdvOnLink on;
        };
        RDNSS 2001:4860:4860::8888 2001:4860:4860::8844 {
        };
        DNSSL example.local {
        };
};
```

**確認ポイント**:
- `interface` セクションが正しいインターフェース名と共に定義されていること。
- `MinRtrAdvInterval`, `MaxRtrAdvInterval`, `AdvDefaultLifetime` が期待値に一致していること。
- `prefix` セクションでプレフィックス, `AdvValidLifetime`, `AdvPreferredLifetime` が設定されていること。
- `RDNSS` に DNS サーバアドレス, `DNSSL` にサーチドメインが記載されていること。

### Step 3: ルーター広告送信の確認

**実施ノード**: IPv6 ネットワーク内の任意のクライアント ( テストホスト )

**前提**: クライアントが同じ IPv6 ネットワークセグメント上にあり, ルータとの L2 通信が可能であること。

**コマンド** (方法 A: `radvdump` を使用):
```bash
# radvdump コマンドで RA メッセージをキャプチャ ( 数秒間 )
timeout 5 radvdump
```

**期待される出力例** (方法 A):
```
-----
Router Advertisement from fe80::1234:5678:9abc (hoplimit=255, flags=none, pkt icmpv6 len=104, interval=100000ms):
         Flags: ..., checksum: abcd (unverified), code: 0
         Reachable time: 3000ms, Retrans time: 1000ms, Hop Limit: 64
         Router Lifetime: 300s, Flags: ..., Preference: medium
         Prefix fd00:1234:5678:1::/64
         Valid time: infinity, Preferred time: infinity
         Flags: A L, MTU: unspecified
         RDNSS option (otype=25): lifetime=1800, rdnss=2001:4860:4860::8888, 2001:4860:4860::8844
         DNSSL option (otype=31): lifetime=1800, dnssl=example.local
```

**確認ポイント**:
- RA メッセージが周期的に受信されること ( `MaxRtrAdvInterval` 秒未満ごと ) 。
- プレフィックス情報が含まれていること ( `A`フラグと`L`フラグ両方がセット ) 。
- RDNSS と DNSSL オプションが含まれていること。
- `Router Lifetime` が 0 でないこと ( デフォルトルート有効 ) 。

**コマンド** (方法 B: `tcpdump` を使用):
```bash
sudo tcpdump -i <interface> -nn 'icmp6 and ip6[40]=134'
```

この方法では RA メッセージ ( ICMPv6 Type 134 ) がキャプチャされます。

### Step 4: クライアント側での SLAAC アドレス取得確認

**実施ノード**: IPv6 クライアントノード

**コマンド**:
```bash
ip -6 addr show | grep -E "(inet6|scope)"
ip -6 route show
```

**期待される出力例**:
```
1: lo: <LOOPBACK,UP,LOWER_UP>
    inet6 ::1/128 scope host
3: ens192: <BROADCAST,MULTICAST,UP,LOWER_UP>
    inet6 fd00:1234:5678:1:1a2b:3c4d:5e6f:7890/64 scope global dynamic
    inet6 fe80::1234:5678:abcd:ef01/10 scope link
    inet6 2001:db8::1/64 scope global

fe80::/10 dev ens192 proto kernel metric 256 pref medium
fd00:1234:5678:1::/64 dev ens192 proto kernel metric 256 expires 4294967295sec pref medium
default via fe80::1234:5678:9abc:1 dev ens192 proto kernel metric 1024 pref medium
```

**確認ポイント**:
- radvd で設定されたプレフィックス ( 例: `fd00:1234:5678:1::/64` ) から自動生成された IPv6 アドレスが付与されていること。
- アドレスのスコープが `global` であること ( `scope link` ではなく ) 。
- デフォルトルートが FE80:: で始まるリンクローカルアドレス ( ルータのリンクローカルアドレス ) を経由して設定されていること。
- プレフィックスの `expires` が十分大きい値 ( 通常は無期限 ) であること。

### Step 5: DNS 設定情報の確認

**実施ノード**: IPv6 クライアントノード

**コマンド**:
```bash
cat /etc/resolv.conf
systemctl status systemd-resolved
resolvectl status
```

**期待される出力例**:
```
# /etc/resolv.conf
nameserver 2001:4860:4860::8888
nameserver 2001:4860:4860::8844
search example.local
```

または systemd-resolved を使用している場合：
```
systemctl status systemd-resolved
● systemd-resolved.service - systemd DNS resolver
   Loaded: loaded (/lib/systemd/system/systemd-resolved.service; enabled; ...)
   Active: active (running)

resolvectl status
Global
       Protocols: -LLMNR -mDNS +DNSSECvalidating
resolv.conf mode: stub
       DNS Servers: 2001:4860:4860::8888 2001:4860:4860::8844
Search Domains: example.local
```

**確認ポイント**:
- DNS サーバが RDNSS で配布されたアドレスと一致していること。
- サーチドメインが DNSSL で配布されたドメインと一致していること。
- DNS 解決が正常に機能していることを確認 ( 例: `getent hosts example.local` ) 。

### Step 6: ログの確認

**実施ノード**: radvd が実行されているルータノード

**コマンド**:
```bash
journalctl -u radvd -n 20 --no-pager
journalctl -u radvd --since "10 minutes ago" | grep -i "ra\|advert\|error\|warning"
```

**期待される出力例**:
```
Jan 20 10:30:00 router systemd[1]: Started IPv6 Router Advertisement Daemon.
Jan 20 10:30:00 router radvd[1234]: version 2.19 started
Jan 20 10:30:00 router radvd[1234]: Listening on ens192
Jan 20 10:30:05 router radvd[1234]: Sending RA on ens192
Jan 20 10:30:10 router radvd[1234]: Sending RA on ens192
```

**確認ポイント**:
- radvd が正常に起動していることを確認 ( `version ... started` ) 。
- 設定対象のインターフェースをリッスンしていること ( `Listening on ens192` ) 。
- 定期的に RA を送信していること ( `Sending RA on ens192` が周期的に出力 ) 。
- エラーやワーニングがないこと。

## 補足

### SLAAC と DHCPv6 の使い分け

このロールは SLAAC のみの設定です。`AdvManagedFlag` と `AdvOtherConfigFlag` は `off` に設定されており, クライアントは SLAAC でアドレスを自動設定します。DHCPv6 が必要な場合は, 別途 Kea などの DHCPv6 サーバを用意し, フラグを `on` に変更してください。

### デフォルトルートの配布制御

`AdvDefaultLifetime` で設定値を制御します。
- `AdvDefaultLifetime 0;` — デフォルトルートを配布しない。
- `AdvDefaultLifetime 300;` — デフォルトルータの有効期限を 300 秒に設定 ( 推奨: `MaxRtrAdvInterval` の 3 倍 ) 。

### トラブルシューティング

- **RA が受信されない**: radvd サービスが起動しているか, インターフェースが正しくバインドされているか確認。`systemctl status radvd` と `/etc/radvd.conf` の `interface` セクションを確認。
- **クライアント側にアドレスが付与されない**: SLAAC が有効化されているか確認 ( `AdvAutonomous on;` ) 。クライアント側の IPv6 設定を確認 ( `ip -6 addr` ) 。
- **DNS が解決されない**: RDNSS/DNSSL がテンプレートに正しく展開されているか確認 ( Step 2 ) 。クライアント側の `/etc/resolv.conf` または `systemd-resolved` を確認 ( Step 5 ) 。

## 参考リンク

- [radvd - Router Advertisement Daemon](https://linux.die.net/man/8/radvd) — manページ ( 英語 ) 。
- [RFC 4861 - Neighbor Discovery for IP version 6 (IPv6)](https://tools.ietf.org/html/rfc4861) — ルーター広告の仕様 ( 英語 ) 。
- [RFC 6106 - IPv6 Router Advertisement Flags Option](https://tools.ietf.org/html/rfc6106) — RDNSS/DNSSL オプション仕様 ( 英語 ) 。
- [Debian/Ubuntu manページ: resolvconf](https://manpages.debian.org/resolvconf.5) — resolv.conf の設定方法 ( 英語 ) 。
- [systemd-resolved](https://www.freedesktop.org/wiki/Software/systemd/resolved/) — systemd によるDNS 管理 ( 英語 ) 。
