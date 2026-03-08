# dns-server ロール

BIND を用いた権威兼キャッシュ DNS サーバーを構成するロールです。対象 OS に応じて Debian 系と RHEL 系の差異を吸収の上, ゾーンファイルと `named.conf`/`named.conf.options` をテンプレートから生成します。

また, クライアントからのホスト名, IPアドレス登録を受け付けるためのDynamic DNS 更新用 Transaction SIGnature (TSIG) キーを組み込み, IPv4/IPv6 双方の順引き, 逆引きゾーンを作成します。

必要に応じて systemd, Security-Enhanced Linux (SELinux), Firewall の周辺設定も行います。

## 用語

| 正式名称 | 略称 | 意味 |
|---------|------|------|
| Berkeley Internet Name Domain | BIND | 最も広く使われる DNS サーバーの実装。インターネット標準の DNS プロトコルを実装したオープンソースソフトウエア。 |
| Domain Name System | DNS | ドメイン名と IP アドレスを対応付ける仕組み。 |
| named | - | BIND の DNS サーバープロセス名。 |
| ゾーン | - | DNS で管理される特定のドメインの範囲。 |
| 順引き (正引き) | - | ドメイン名から IP アドレスを検索する方向の名前解決。 |
| 逆引き | - | IP アドレスからドメイン名を検索する方向の名前解決。 |
| Transaction SIGnature | TSIG | DNS 更新時に使う共有鍵署名方式。Dynamic DNS の更新を認証するために使用される。 |
| nsupdate | - | Dynamic DNS を更新するためのコマンドラインツール。TSIG キーを使用して認証を行う。 |
| rndc | - | BIND の管理コマンド (Remote Name Daemon Control の略)。named プロセスの制御, ゾーンリロード, 統計表示などに使用。 |
| Dynamic DNS | DDNS | IP アドレスの変化に合わせて DNS レコードを動的に更新する仕組み。 |
| Security-Enhanced Linux | SELinux | RHEL 系で使用される強制アクセス制御の仕組み。 |
| firewalld | - | RHEL 系のファイアウォール管理デーモン。 |
| Uncomplicated Firewall | UFW | Debian/Ubuntu 系のファイアウォール管理ツール。 |
| systemd drop-in | - | systemd サービスの設定を上書き, 追加するための設定ファイル。`/etc/systemd/system/<サービス名>.service.d/` 配下に配置。 |

## 前提条件

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- Ansible 2.15 以降
  - `ansible.posix` コレクションがインストールされていること
- リモートホストへの SSH 接続が確立されていること
- `sudo` による管理者権限でのコマンド実行が可能であること
- DNS ポート (53/tcp, 53/udp) の開放権限 (Firewall 有効時)
- SELinux 設定権限 (RHEL 系のみ)
- インターネット接続 (パッケージ取得用)

## 実行方法

### Makefile を使用

```bash
make run_dns_server
```

### Ansible コマンド直接実行

```bash
# 全対象ホストに適用
ansible-playbook -i inventory/hosts server.yml --tags dns-server

# 特定ホストのみ適用
ansible-playbook -i inventory/hosts server.yml --tags dns-server -l <hostname>

# Firewall 設定をスキップ
ansible-playbook -i inventory/hosts server.yml --tags dns-server --skip-tags config-firewall
```

対象プレイブックでこのロールが含まれていればタグ省略でも適用されます。

## 実行フロー

本ロールは以下の順序で処理を実行します:

1. **パラメータ読み込み** (`load-params.yml`): OS ファミリー別パッケージ定義と共通変数を読み込み, ドメインやネットワーク関連変数を構成。

2. **パッケージインストール** (`package.yml`): `dns_bind_packages` を最新化。変更があれば systemd のデフォルトターゲットを `multi-user.target` に設定。

3. **設定ファイル配置とゾーンファイル生成** (`config.yml`): 設定, ゾーン格納ディレクトリをサイズの所有者とパーミッションで作成。OS ごとの `named.conf.options` テンプレートを配置し, フォワーダーや ACL を反映。`named.conf.zones.j2` と各ゾーンテンプレートを展開し, レコードを生成。複数ネットワーク対応時は追加の逆引きゾーンファイルをループで生成。RHEL 系では rndc.key 生成, SELinux fcontext 設定, 暗号ポリシーのコメントアウトを実施。

4. **DNS応答をIPv4に限定するための設定** (`config-systemd-ipv4-only.yml`): `dns_bind_ipv4_only: true` の場合, systemd drop-in を生成し IPv4 応答に限定 (デフォルトは両方対応)。

5. **Firewall 設定** (`config-firewall.yml`): `enable_firewall: true` のときに firewalld または UFW を自動判別し, DNS ポート(既定: 53) の TCP/UDP を開放。

6. **ハンドラ実行**: 構成変更に応じて systemd リスタート, ゾーンリロード等を実行。

## 主要変数

### ロール固有変数

| 変数名 | 既定値 | 説明 |
|-------|--------|------|
| `dns_ddns_key_name` | `"ddns-clients"` | Dynamic DNS update key 名 (クライアント側とサーバ側で共通)。 |
| `dns_bind_user` | Debian: `"bind"`, RHEL: `"named"` | BIND 実行ユーザ名。 |
| `dns_bind_group` | Debian: `"bind"`, RHEL: `"named"` | BIND 実行グループ名。 |
| `dns_bind_service` | `"named"` | BIND systemd サービス名。 |
| `dns_bind_conf_dir` | Debian: `"/etc/bind"`, RHEL: `"/etc/named"` | BIND 設定ディレクトリ。 |
| `dns_bind_main_conf` | Debian: `"/etc/bind/named.conf"`, RHEL: `"/etc/named.conf"` | BIND メイン設定ファイル。 |
| `dns_bind_zone_dir` | Debian: `"/var/lib/bind"`, RHEL: `"/var/named/zone"` | ゾーンファイル格納ディレクトリ。 |
| `dns_bind_run_dir` | `"/run/named"` | PID ファイルなどのランタイムディレクトリ。 |
| `dns_bind_cache_dir` | Debian: `"/var/cache/bind"`, RHEL: `"/var/named"` | キャッシュファイル格納ディレクトリ。 |
| `dns_bind_options_conf_path` | Debian: `"/etc/bind/named.conf.options"`, RHEL: `"/etc/named/named.conf.options"` | オプション設定ファイルパス。 |
| `dns_bind_systemd_dropin_dir` | `"/etc/systemd/system/named.service.d"` | systemd drop-in ディレクトリ。 |
| `dns_bind_systemd_dropin_file` | `"90-override.conf"` | systemd drop-in ファイル名。 |
| `dns_bind_selinux_type` | `"named_zone_t"` | SELinux ゾーン用タイプ (RHEL 系のみ使用)。 |
| `dns_bind_selinux_target` | `"/var/named(/.*)?"` | SELinux fcontext を適用するパス (RHEL 系のみ使用)。 |
| `dns_bind_keyfile` | Debian: `"/usr/share/dns/root.key"`, RHEL: `"/etc/named.root.key"` | DNSSEC ルート鍵ファイルパス。 |
| `dns_bind_port` | `53` | DNS ポート番号。 |
| `dns_bind_ipv4_only` | `false` | IPv4 のみに限定する場合に `true` (systemd drop-in で ExecStart に `-4` を付与)。 |
| `dns_bind_firewall_zone` | `null` | firewalld のゾーン名 (`null` の場合はデフォルトゾーンを使用)。 |
| `dns_bind_forwarders` | `["1.1.1.1", "8.8.8.8"]` | 上位 DNS へのフォワーダー一覧。空にすると forward 設定を省略。 |

### OS 差異吸収変数

| 変数名 | 既定値 | 説明 |
|-------|--------|------|
| `dns_bind_packages` | Debian: `["bind9", "bind9-utils"]`, RHEL: `["bind", "bind-utils"]` | OS 別 BIND パッケージ一覧。 |
| `dns_rndc_key_name` | `"rndc-key"` | rndc 制御用 TSIG キー名。 |
| `dns_rndc_key_path` | Debian: `"/etc/bind/rndc.key"`, RHEL: `"/etc/rndc.key"` | rndc 制御用 TSIG キーファイルパス。 |

### サイト全体共通変数

| 変数名 | 既定値 | 説明 |
|-------|--------|------|
| `dns_domain` | `""` | 正引きゾーン名。ゾーンファイルの SOA, NS レコードを決定。 |
| `dns_server` | `""` | SOA ホスト名 (FQDN)。**この変数が空の場合, パッケージインストール, ディレクトリ作成, ユーザ/グループ作成, サービス設定, 設定ファイル生成の各タスクはスキップされます**。 |
| `dns_network` | `""` | IPv4 ACL とゾーン内 A レコードのベースアドレス。 |
| `dns_network_ipv4_prefix` | `""` | ネットワークプレフィクス (IPv4, 例: `"192.168.20.0"`)。 |
| `dns_network_ipv4_prefix_len` | `""` | IPv4 ネットワークプレフィクス長 (例: `24`)。 |
| `dns_network_ipv6_prefix` | `""` | IPv6 ACL や逆引きゾーンの生成に使用するプレフィクス (例: `"fd00:1234:5678:1::"`)。 |
| `dns_network_ipv6_prefix_len` | `""` | IPv6 ネットワークプレフィクス長 (例: `64`)。 |
| `dns_host_list` | `[]` | 順引き/逆引きレコードを生成するためのホスト定義リスト。 |
| `dns_ipv4_reverse` | `""` | IPv4 逆引きゾーン名 (例: `"20.168.192"`  =>  `"20.168.192.in-addr.arpa"`)。 |
| `dns_ipv6_reverse` | `""` | IPv6 逆引きゾーン名 (ニブル形式)。 |
| `dns_ddns_key_secret` | `""` | Dynamic DNS update key のシークレット。**バージョン管理外に保管してください**。 |
| `internal_network_list` | `[]` | 複数ネットワーク逆引きゾーン対応: 追加ネットワークのリスト。各要素は `{ipv4: "...", ipv6: "..."}` 形式。 |
| `enable_firewall` | `false` | Firewall 設定の有効化フラグ (roles/common/defaults/main.yml で定義)。 |

## デフォルト動作

| 条件 | 結果 |
|-----|------|
| `dns_server` が未定義または空文字列 | パッケージインストール, ディレクトリ作成, ユーザ/グループ作成, サービス設定, 設定ファイル生成の各タスクはスキップされます。 |
| `dns_host_list` が未定義または空リスト | テンプレート展開は失敗せず, A/PTR の静的レコードは生成されません。 |
| `enable_firewall: false` | Firewall 設定はスキップされます。 |
| `dns_bind_ipv4_only: false` (デフォルト) | named は IPv4 と IPv6 の両方でリッスンします。 |
| `dns_bind_ipv4_only: true` | systemd drop-in で ExecStart に `-4` フラグが付与され, IPv4 のみに限定。 |
| `dns_bind_forwarders` が空リスト | 上位 DNS へのフォワード設定を省略 (再帰問い合わせを直接ルートサーバに送信)。 |
| `internal_network_list` が未定義または空 | 追加の逆引きゾーンは生成されません (単一ネットワーク構成)。 |
| SELinux が有効 (RHEL 系) | `dns_bind_zone_dir` に `named_zone_t` コンテキストを自動適用。 |
| SELinux が無効 (RHEL 系) | SELinux 関連タスクがスキップされます。 |

## テンプレート, ファイル

本ロールでは以下のテンプレート/ファイルを出力します:

| テンプレートファイル名 | 出力先 | 説明 |
|------|--------|------|
| `rhel-named.conf.j2` | `/etc/named.conf` (RHEL) | 最小クリーン版 named.conf (既存ファイルをバックアップ後に置換)。 |
| `named.conf.options.j2` | `/etc/bind/named.conf.options` (Debian) | ACL, options, forwarders を定義。 |
| `rhel-named.conf.options.j2` | `/etc/named/named.conf.options` (RHEL) | ACL, options, forwarders, rndc controls セクション, rndc.key の include を定義。 |
| `named.conf.zones.j2` | `/etc/bind/named.conf.zones` / `/etc/named/named.conf.zones` | 順引き/逆引きゾーン定義 (単一ネットワーク + 複数ネットワーク対応)。 |
| `db.forward.conf.j2` | `/var/lib/bind/db.<DNS_domain>` / `/var/named/zone/db.<DNS_domain>` | 順引きゾーンファイル (A/AAAA レコード)。 |
| `db.reverse.j2` | `/var/lib/bind/db.<reverse_zone>` / `/var/named/zone/db.<reverse_zone>` | IPv4 逆引きゾーンファイル (PTR レコード)。 |
| `db.reverse.ipv6.j2` | `/var/lib/bind/db.<reverse_zone_ipv6>` / `/var/named/zone/db.<reverse_zone_ipv6>` | IPv6 逆引きゾーンファイル (PTR レコード)。 |
| `db.reverse.additional.j2` | `/var/lib/bind/db.<reverse_zone>` / `/var/named/zone/db.<reverse_zone>` | 追加 IPv4 逆引きゾーンファイル (スケルトン: SOA + NS のみ)。 |
| `db.reverse.additional.ipv6.j2` | `/var/lib/bind/db.<reverse_zone_ipv6>` / `/var/named/zone/db.<reverse_zone_ipv6>` | 追加 IPv6 逆引きゾーンファイル (スケルトン: SOA + NS のみ)。 |
| `90-override.conf.j2` | `/etc/systemd/system/named.service.d/90-override.conf` | IPv4 限定用 systemd drop-in (ExecStart に `-4` を追加)。 |

## OS 差異

RHEL 系 (Rocky Linux, AlmaLinux 等) と Debian 系 (Debian, Ubuntu) の主な差異を以下に示します:

| 項目 | Debian 系 | RHEL 系 | 備考 |
|-----|---------|--------|------|
| **BIND パッケージ** | `bind9`, `bind9-utils` | `bind`, `bind-utils` | パッケージ名が異なる。 |
| **実行ユーザ/グループ** | `bind:bind` | `named:named` | ファイル所有者が異なる。 |
| **設定ディレクトリ** | `/etc/bind` | `/etc/named` | 設定ファイルの配置場所が異なる。 |
| **ゾーンファイルディレクトリ** | `/var/lib/bind` | `/var/named/zone` | ゾーンファイルの配置場所が異なる。 |
| **キャッシュディレクトリ** | `/var/cache/bind` | `/var/named` | キャッシュファイルの配置場所が異なる。 |
| **named.conf 構造** | 既存ファイルに include 行のみ追加 | 既存ファイルをバックアップ後, 最小クリーン版に置換 | RHEL では既存設定を完全にリセット。 |
| **rndc.key 生成** | bind9 パッケージの postinst が自動生成 | ロール内で `rndc-confgen` を明示的に実行 | Debian では自動, RHEL では手動生成が必要。 |
| **controls セクション** | 未定義 (rndc.key が存在すれば自動有効) | `named.conf.options` に明示的に定義 | RHEL では明示的な設定が必要。 |
| **暗号ポリシー** | 該当なし | `/etc/crypto-policies/back-ends/bind.config` の include をコメントアウト | RHEL で docker.io などの検証で弾かれる問題を回避。 |
| **SELinux** | 該当なし | 有効時に `semanage fcontext` と `restorecon` を実行 | RHEL のみ SELinux コンテキスト設定が必要。 |
| **Firewall バックエンド** | UFW | firewalld | Debian では UFW, RHEL では firewalld を優先。 |

### RHEL 系専用処理の詳細

RHEL 系では以下の専用処理を実施します:

1. **rndc.key 生成**: `rndc-confgen -a -c {{ dns_rndc_key_path }}` を実行し, `/etc/rndc.key` に TSIG キーを生成 (Debian では bind9 パッケージの postinst が自動生成)。

2. **named.conf 置換**: 既存の `/etc/named.conf` を `/etc/named.conf.orig` にバックアップ後, `rhel-named.conf.j2` テンプレートで最小クリーン版を配置 (include 行のみを含む簡潔な構成)。Debian では既存ファイルに include 行のみを追加。

3. **controls セクションと rndc.key の include**: `rhel-named.conf.options.j2` に以下を追加:
   ```bind
   include "{{ dns_rndc_key_path }}";
   controls {
       inet 127.0.0.1 port 953 allow { 127.0.0.1; } keys { "{{ dns_rndc_key_name }}"; };
   };
   ```
   Debian では controls セクションが未定義でも, rndc.key が所定パスに存在すれば自動的に有効化。

4. **暗号ポリシー無効化**: `rhel-named.conf.options.j2` の options セクション内で, `/etc/crypto-policies/back-ends/bind.config` の include をコメントアウト (RSASHA1 / SHA-1 禁止による検証失敗回避)。

5. **SELinux fcontext 設定**: SELinux が有効な場合, `semanage fcontext -a -t named_zone_t '{{ dns_bind_selinux_target }}'` を実行し, `restorecon -Rv {{ dns_bind_zone_dir }}` でゾーンディレクトリに `named_zone_t` コンテキストを適用。Debian には SELinux が存在しないため, この処理は不要。

## 設定例

### 基本設定 (単一ネットワーク)

`vars/all-config.yml`:

```yaml
dns_domain: "example.org"
dns_server: "ns1.example.org"
dns_server_ipv4_address: "192.168.20.1"
dns_network: "192.168.20.0"
dns_network_ipv4_prefix_len: 24
dns_network_ipv6_prefix: "fd00:1234:5678:1::"
dns_network_ipv6_prefix_len: 64
dns_ipv4_reverse: "20.168.192"
dns_ipv6_reverse: "1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f"
dns_host_list:
  - { name: "host1", ipv4_addr: "10", ipv6_addr: "::10" }
  - { name: "host2", ipv4_addr: "11", ipv6_addr: "::11" }
dns_ddns_key_secret: "YOUR_BASE64_ENCODED_SECRET_HERE"
```

### IPv4 限定設定

`host_vars/<hostname>/main.yml`:

```yaml
dns_bind_ipv4_only: true
```

この設定により, systemd drop-in で `ExecStart` に `-4` フラグが追加され, named は IPv4 のみでリッスンします。

### 複数ネットワーク逆引き設定

`group_vars/all/all.yml`:

```yaml
internal_network_list:
  # ネットワーク1: IPv4 + IPv6 双方指定
  - ipv4: "192.168.30.0/24"
    ipv6: "fd69:6684:61a:2::/64"
  # ネットワーク2: IPv4 のみ
  - ipv4: "192.168.40.0/25"
  # ネットワーク3: IPv6 のみ
  - ipv6: "fd69:6684:61a:3::/64"
```

## 検証

ロール適用後, DNS サーバーの動作を検証します。検証パターンは構成に応じて実施してください。

### パターン1: デュアルスタック対応 ( 標準構成 )

以下は IPv4/IPv6 デュアルスタック構成での具体的な検証手順です。

#### 前提条件

本例で使用する設定値:

- 検証対象 DNS サーバー: `mgmt-server.local` (または任意のホスト名)
- DNS ドメイン: `example.org`
- DNS サーバー IPv4 アドレス: `192.168.20.1`
- DNS サーバー IPv6 アドレス: `fd00:1234:5678:1::1`
- ネットワーク IPv4: `192.168.20.0/24`
- ネットワーク IPv6: `fd00:1234:5678:1::/64`
- 逆引きゾーン IPv4: `20.168.192.in-addr.arpa`
- 逆引きゾーン IPv6: `1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f.ip6.arpa`
- 登録ホスト例:
  - `host1.example.org`: `192.168.20.10`, `fd00:1234:5678:1::10`
  - `host2.example.org`: `192.168.20.11`, `fd00:1234:5678:1::11`
- TSIG キー名: `ddns-clients`
- Firewall: 有効 (`enable_firewall: true`)

#### 1. サービス状態の確認

**実施ノード**: DNS サーバー (`mgmt-server.local`)

```bash
# RHEL 系
systemctl status named

# Debian 系
systemctl status bind9
```

**期待される出力例 (RHEL 系)**:

```
● named.service - Berkeley Internet Name Domain (DNS)
     Loaded: loaded (/usr/lib/systemd/system/named.service; enabled; preset: disabled)
    Drop-In: /etc/systemd/system/named.service.d
             └─90-override.conf
     Active: active (running) since Thu 2026-03-06 10:30:15 JST; 2h 15min ago
   Main PID: 1234 (named)
      Tasks: 5 (limit: 23456)
     Memory: 45.2M
        CPU: 2.345s
     CGroup: /system.slice/named.service
             └─1234 /usr/sbin/named -u named -c /etc/named.conf

Mar 06 10:30:15 mgmt-server.local named[1234]: zone example.org/IN: loaded serial 2026030601
Mar 06 10:30:15 mgmt-server.local named[1234]: zone 20.168.192.in-addr.arpa/IN: loaded serial 2026030601
Mar 06 10:30:15 mgmt-server.local named[1234]: zone 1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f.ip6.arpa/IN: loaded serial 2026030601
Mar 06 10:30:15 mgmt-server.local named[1234]: all zones loaded
Mar 06 10:30:15 mgmt-server.local named[1234]: running
```

**期待される出力例 (Debian 系)**:

```
● bind9.service - BIND Domain Name Server
     Loaded: loaded (/lib/systemd/system/bind9.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2026-03-06 10:30:15 JST; 2h 15min ago
       Docs: man:named(8)
   Main PID: 1234 (named)
      Tasks: 5 (limit: 23456)
     Memory: 42.1M
        CPU: 2.123s
     CGroup: /system.slice/bind9.service
             └─1234 /usr/sbin/named -f -u bind

Mar 06 10:30:15 mgmt-server named[1234]: zone example.org/IN: loaded serial 2026030601
Mar 06 10:30:15 mgmt-server named[1234]: zone 20.168.192.in-addr.arpa/IN: loaded serial 2026030601
Mar 06 10:30:15 mgmt-server named[1234]: zone 1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f.ip6.arpa/IN: loaded serial 2026030601
Mar 06 10:30:15 mgmt-server named[1234]: all zones loaded
Mar 06 10:30:15 mgmt-server named[1234]: running
```

**確認ポイント**:

1. **Loaded 行**: `enabled` が表示されていることを確認 (システム起動時に自動起動が有効)
2. **Active 行**: `active (running)` が表示されていることを確認 (サービスが正常に起動中)
3. **ログ出力**: 各ゾーン (`example.org`, `20.168.192.in-addr.arpa`, IPv6 逆引きゾーン) が `loaded serial` と表示されていることを確認 (全ゾーンファイルが正常に読み込まれている)
4. **最終メッセージ**: `all zones loaded` と `running` が表示されていることを確認 (named が正常に動作中)

#### 2. 設定構文検証

**実施ノード**: DNS サーバー (`mgmt-server.local`)

```bash
named-checkconf -z
```

**期待される出力例 (単一ネットワーク構成)**:

```
zone example.org/IN: loaded serial 2026030601
zone 20.168.192.in-addr.arpa/IN: loaded serial 2026030601
zone 1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f.ip6.arpa/IN: loaded serial 2026030601
zone localhost/IN: loaded serial 0
zone 127.in-addr.arpa/IN: loaded serial 0
zone 0.in-addr.arpa/IN: loaded serial 0
zone 255.in-addr.arpa/IN: loaded serial 0
```

**期待される出力例 (複数ネットワーク構成)**:

```
zone example.org/IN: loaded serial 2026030601
zone 20.168.192.in-addr.arpa/IN: loaded serial 2026030601
zone 1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f.ip6.arpa/IN: loaded serial 2026030601
zone 30.168.192.in-addr.arpa/IN: loaded serial 2026030601
zone 2.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f.ip6.arpa/IN: loaded serial 2026030601
zone 40.168.192.in-addr.arpa/IN: loaded serial 2026030601
zone localhost/IN: loaded serial 0
zone 127.in-addr.arpa/IN: loaded serial 0
```

**確認ポイント**:

1. **エラーメッセージの有無**: コマンド実行後にエラーメッセージが表示されないことを確認 (構文エラーがない)
2. **順引きゾーン**: `zone example.org/IN: loaded serial` が表示されることを確認 (順引きゾーンが正常に読み込まれている)
3. **IPv4 逆引きゾーン**: `zone 20.168.192.in-addr.arpa/IN: loaded serial` が表示されることを確認 (IPv4 逆引きゾーンが正常に読み込まれている)
4. **IPv6 逆引きゾーン**: `zone 1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f.ip6.arpa/IN: loaded serial` が表示されることを確認 (IPv6 逆引きゾーンが正常に読み込まれている)
5. **複数ネットワーク構成の場合**: `internal_network_list` で定義した追加ネットワークの逆引きゾーン (例: `30.168.192.in-addr.arpa`, `2.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f.ip6.arpa`) も `loaded serial` と表示されることを確認
6. **シリアル番号**: 各ゾーンのシリアル番号が表示されていることを確認 (日付ベース形式: `2026030601` など)

#### 3. 順引き解決確認 (IPv4/IPv6)

**実施ノード**: DNS サーバー (`mgmt-server.local`) または任意のクライアントノード

```bash
dig @localhost host1.example.org
```

**期待される出力例**:

```
; <<>> DiG 9.18.24 <<>> @localhost host1.example.org
; (2 servers found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 12345
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 2, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
; COOKIE: abcdef0123456789 (good)
;; QUESTION SECTION:
;host1.example.org.             IN      A

;; ANSWER SECTION:
host1.example.org.      86400   IN      A       192.168.20.10
host1.example.org.      86400   IN      AAAA    fd00:1234:5678:1::10

;; Query time: 0 msec
;; SERVER: ::1#53(localhost) (UDP)
;; WHEN: Thu Mar 06 12:45:30 JST 2026
;; MSG SIZE  rcvd: 98
```

**確認ポイント**:

1. **status**: `status: NOERROR` が表示されることを確認 (クエリが正常に処理された)
2. **flags**: `aa` (Authoritative Answer) フラグが含まれていることを確認 (権威サーバーとして応答している)
3. **ANSWER SECTION**: 2つのレコードが返されることを確認
   - **A レコード**: `host1.example.org. 86400 IN A 192.168.20.10` が表示されることを確認 (IPv4 アドレスが正しく返される)
   - **AAAA レコード**: `host1.example.org. 86400 IN AAAA fd00:1234:5678:1::10` が表示されることを確認 (IPv6 アドレスが正しく返される)
4. **TTL**: 86400 (1日) が設定されていることを確認 (デフォルト TTL が適用されている)
5. **アドレスの正確性**: `dns_host_list` で定義した IPv4/IPv6 アドレスと一致していることを確認

#### 4. 逆引き解決確認 (IPv4)

**実施ノード**: DNS サーバー (`mgmt-server.local`) または任意のクライアントノード

```bash
dig @localhost -x 192.168.20.10
```

**期待される出力例**:

```
; <<>> DiG 9.18.24 <<>> @localhost -x 192.168.20.10
; (2 servers found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 23456
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
; COOKIE: 0123456789abcdef (good)
;; QUESTION SECTION:
;10.20.168.192.in-addr.arpa.    IN      PTR

;; ANSWER SECTION:
10.20.168.192.in-addr.arpa. 86400 IN    PTR     host1.example.org.

;; Query time: 0 msec
;; SERVER: ::1#53(localhost) (UDP)
;; WHEN: Thu Mar 06 12:46:45 JST 2026
;; MSG SIZE  rcvd: 95
```

**確認ポイント**:

1. **status**: `status: NOERROR` が表示されることを確認 (クエリが正常に処理された)
2. **flags**: `aa` (Authoritative Answer) フラグが含まれていることを確認 (権威サーバーとして応答している)
3. **QUESTION SECTION**: `10.20.168.192.in-addr.arpa. IN PTR` が表示されることを確認 (IPv4 アドレスが正しく逆引き形式に変換されている)
4. **ANSWER SECTION**: `10.20.168.192.in-addr.arpa. 86400 IN PTR host1.example.org.` が表示されることを確認
   - PTR レコードが返されている
   - ホスト名が FQDN 形式 (末尾にドット `.` 付き) で返される
   - `dns_host_list` で定義したホスト名と一致している
5. **TTL**: 86400 (1日) が設定されていることを確認

#### 5. 逆引き解決確認 (IPv6)

**実施ノード**: DNS サーバー (`mgmt-server.local`) または任意のクライアントノード

```bash
dig @localhost -x fd00:1234:5678:1::10
```

**期待される出力例**:

```
; <<>> DiG 9.18.24 <<>> @localhost -x fd00:1234:5678:1::10
; (2 servers found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 34567
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
; COOKIE: fedcba9876543210 (good)
;; QUESTION SECTION:
;0.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f.ip6.arpa. IN PTR

;; ANSWER SECTION:
0.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f.ip6.arpa. 86400 IN PTR host1.example.org.

;; Query time: 1 msec
;; SERVER: ::1#53(localhost) (UDP)
;; WHEN: Thu Mar 06 12:47:30 JST 2026
;; MSG SIZE  rcvd: 145
```

**確認ポイント**:

1. **status**: `status: NOERROR` が表示されることを確認 (クエリが正常に処理された)
2. **flags**: `aa` (Authoritative Answer) フラグが含まれていることを確認 (権威サーバーとして応答している)
3. **QUESTION SECTION**: IPv6 アドレスがニブル形式の逆引き表現に変換されていることを確認
   - `fd00:1234:5678:1::10` が `0.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f.ip6.arpa.` に変換されている
4. **ANSWER SECTION**: PTR レコードが返されていることを確認
   - `0.1.0.0...d.f.ip6.arpa. 86400 IN PTR host1.example.org.` が表示される
   - ホスト名が FQDN 形式 (末尾にドット `.` 付き) で返される
   - `dns_host_list` で定義したホスト名と一致している
5. **TTL**: 86400 (1日) が設定されていることを確認

#### 6. SELinux コンテキスト確認 (RHEL 系のみ)

**実施ノード**: DNS サーバー (`mgmt-server.local`, RHEL 系のみ)

**前提条件**: SELinux が有効 (`getenforce` コマンドで `Enforcing` または `Permissive` が返される)

```bash
ls -Z /var/named/zone/
```

**期待される出力例**:

```
unconfined_u:object_r:named_zone_t:s0 db.1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f
unconfined_u:object_r:named_zone_t:s0 db.20.168.192
unconfined_u:object_r:named_zone_t:s0 db.example.org
```

**複数ネットワーク構成の場合の出力例**:

```
unconfined_u:object_r:named_zone_t:s0 db.1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f
unconfined_u:object_r:named_zone_t:s0 db.2.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f
unconfined_u:object_r:named_zone_t:s0 db.20.168.192
unconfined_u:object_r:named_zone_t:s0 db.30.168.192
unconfined_u:object_r:named_zone_t:s0 db.40.168.192
unconfined_u:object_r:named_zone_t:s0 db.example.org
```

**確認ポイント**:

1. **SELinux タイプ**: 全ゾーンファイルのコンテキストに `named_zone_t` が含まれていることを確認
   - 形式: `<ユーザー>:object_r:named_zone_t:s0 <ファイル名>`
2. **順引きゾーンファイル**: `db.example.org` に `named_zone_t` コンテキストが設定されていることを確認
3. **IPv4 逆引きゾーンファイル**: `db.20.168.192` (メインネットワーク), `db.30.168.192`, `db.40.168.192` (追加ネットワーク) に `named_zone_t` コンテキストが設定されていることを確認
4. **IPv6 逆引きゾーンファイル**: `db.1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f` (メインネットワーク), `db.2.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f` (追加ネットワーク) に `named_zone_t` コンテキストが設定されていることを確認
5. **named プロセスのアクセス権**: SELinux が Enforcing モードでも named プロセスがゾーンファイルにアクセスできる状態であることを確認 (コンテキスト不一致による Permission denied エラーが発生しない)

**SELinux が無効の場合**:

```bash
getenforce
```

出力が `Disabled` の場合, このステップはスキップしてください (SELinux 関連タスクは実行されていない)。

#### 7. Firewall 設定確認

**実施ノード**: DNS サーバー (`mgmt-server.local`)

##### RHEL 系 (firewalld)

```bash
firewall-cmd --list-services
```

**期待される出力例**:

```
dhcpv6-client dns ssh
```

または

```bash
firewall-cmd --list-all
```

**期待される出力例**:

```
public (active)
  target: default
  icmp-block-inversion: no
  interfaces: eth0
  sources:
  services: dhcpv6-client dns ssh
  ports:
  protocols:
  forward: yes
  masquerade: no
  forward-ports:
  source-ports:
  icmp-blocks:
  rich rules:
```

**確認ポイント (firewalld)**:

1. **dns サービス**: `services:` 行に `dns` が含まれていることを確認 (DNS ポート 53/tcp, 53/udp が許可されている)
2. **ゾーン**: デフォルトゾーン (通常は `public`) に設定されていることを確認 (`dns_bind_firewall_zone` を明示的に設定した場合は指定ゾーンに設定されている)
3. **インターフェース**: `interfaces:` 行に DNS サービスを提供するネットワークインターフェースが含まれていることを確認

##### Debian 系 (UFW)

```bash
sudo ufw status
```

**期待される出力例**:

```
Status: active

To                         Action      From
--                         ------      ----
53/tcp                     ALLOW       Anywhere
53/udp                     ALLOW       Anywhere
22/tcp                     ALLOW       Anywhere
53/tcp (v6)                ALLOW       Anywhere (v6)
53/udp (v6)                ALLOW       Anywhere (v6)
22/tcp (v6)                ALLOW       Anywhere (v6)
```

または

```bash
sudo ufw status verbose
```

**期待される出力例**:

```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
53/tcp                     ALLOW IN    Anywhere
53/udp                     ALLOW IN    Anywhere
22/tcp                     ALLOW IN    Anywhere
53/tcp (v6)                ALLOW IN    Anywhere (v6)
53/udp (v6)                ALLOW IN    Anywhere (v6)
22/tcp (v6)                ALLOW IN    Anywhere (v6)
```

**確認ポイント (UFW)**:

1. **Status**: `Status: active` が表示されていることを確認 (UFW が有効である)
2. **53/tcp**: `53/tcp ALLOW Anywhere` が表示されていることを確認 (DNS TCP ポートが許可されている)
3. **53/udp**: `53/udp ALLOW Anywhere` が表示されていることを確認 (DNS UDP ポートが許可されている)
4. **IPv6 対応**: `53/tcp (v6)` と `53/udp (v6)` が `ALLOW Anywhere (v6)` で表示されていることを確認 (IPv6 でも DNS ポートが許可されている)

**Firewall が無効の場合**:

`enable_firewall: false` に設定した場合, Firewall 関連タスクはスキップされています。この場合, リモートホストからの DNS クエリが OS レベルのファイアウォールでブロックされないことを別途確認する必要があります。

#### 8. Dynamic DNS 更新確認

**実施ノード**: DNS サーバー (`mgmt-server.local`) または任意のクライアントノード

```bash
# DDNS レコード追加
nsupdate -k /etc/bind/rndc.key << EOF
server 192.168.20.1
zone example.org.
update add test-host.example.org. 300 A 192.168.20.100
send
EOF

# 追加したレコードの確認
dig @localhost test-host.example.org
```

**期待される出力例 (nsupdate)**:

```
(出力なし, または空行のみ)
```

**nsupdate が成功した場合**: エラーメッセージが表示されず, プロンプトが戻る。

**nsupdate が失敗した場合の例**:

```
update failed: REFUSED
```

**期待される出力例 (dig)**:

```
; <<>> DiG 9.18.24 <<>> @localhost test-host.example.org
; (2 servers found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 45678
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
; COOKIE: 1234567890abcdef (good)
;; QUESTION SECTION:
;test-host.example.org.         IN      A

;; ANSWER SECTION:
test-host.example.org.  300     IN      A       192.168.20.100

;; Query time: 0 msec
;; SERVER: ::1#53(localhost) (UDP)
;; WHEN: Thu Mar 06 12:50:15 JST 2026
;; MSG SIZE  rcvd: 78
```

**確認ポイント**:

1. **nsupdate の実行**: エラーメッセージが表示されないことを確認 (TSIG 認証が成功し, レコード追加が許可されている)
2. **status**: `status: NOERROR` が表示されることを確認 (クエリが正常に処理された)
3. **ANSWER SECTION**: `test-host.example.org. 300 IN A 192.168.20.100` が表示されることを確認
   - 動的に追加したレコードが正しく返される
   - TTL が nsupdate で指定した 300 秒になっている
   - IP アドレスが指定した `192.168.20.100` と一致している
4. **flags**: `aa` (Authoritative Answer) フラグが含まれていることを確認

**追加確認: ゾーンファイルへの永続化**

```bash
# ゾーンファイルの保存状態確認 (RHEL 系)
cat /var/named/zone/db.example.org

# ゾーンファイルの保存状態確認 (Debian 系)
cat /var/lib/bind/db.example.org
```

動的に追加されたレコードは, named の再起動後も保持されます (BIND の動的ゾーン機能により, `.jnl` ジャーナルファイルに記録され, 定期的にゾーンファイルに反映されます)。

**レコード削除 (後片付け)**:

```bash
nsupdate -k /etc/bind/rndc.key << EOF
server 192.168.20.1
zone example.org.
update delete test-host.example.org. A
send
EOF
```

#### 9. ゾーンファイル内容確認

**実施ノード**: DNS サーバー (`mgmt-server.local`)

```bash
# Debian 系
cat /var/lib/bind/db.example.org

# RHEL 系
cat /var/named/zone/db.example.org
```

**期待される出力例**:

```
$TTL 86400
@       IN      SOA     mgmt-server.example.org. root.example.org. (
        2026030601 ;Serial
        3600            ;Refresh
        1800            ;Retry
        604800          ;Expire
        86400           ;Minimum TTL
)

       IN      NS       mgmt-server.example.org.

; === A レコード ===
host1                   IN      A       192.168.20.10
host2                   IN      A       192.168.20.11

; === AAAA レコード ===
host1                   IN      AAAA    fd00:1234:5678:1::10
host2                   IN      AAAA    fd00:1234:5678:1::11
```

**確認ポイント**:

1. **TTL 設定**: ファイル冒頭に `$TTL 86400` (1日) が定義されていることを確認
2. **SOA レコード**: `@  IN  SOA  <DNSサーバーFQDN>  <管理者メール>` 形式で定義されていることを確認
   - プライマリネームサーバー: `mgmt-server.example.org.` (FQDN 末尾にドット `.` 付き)
   - 管理者メール: `root.example.org.` (@ を . に置換した形式)
   - シリアル番号: 日付ベース形式 (例: `2026030601` = 2026年3月6日 01版) が設定されている
   - Refresh, Retry, Expire, Minimum TTL が適切に設定されている
3. **NS レコード**: `IN  NS  mgmt-server.example.org.` が定義されていることを確認 (ネームサーバー自身を NS レコードとして登録)
4. **A レコード**: `dns_host_list` で定義した各ホストの IPv4 アドレスが正しく登録されていることを確認
   - 形式: `<ホスト名>  IN  A  <IPv4アドレス>`
   - 例: `host1  IN  A  192.168.20.10`
5. **AAAA レコード**: `dns_host_list` で定義した各ホストの IPv6 アドレスが正しく登録されていることを確認
   - 形式: `<ホスト名>  IN  AAAA  <IPv6アドレス>`
   - 例: `host1  IN  AAAA  fd00:1234:5678:1::10`
6. **コメント**: セクション区切りのコメント (`; === A レコード ===` など) が含まれていることを確認 (可読性向上)

**逆引きゾーンファイルの確認 (IPv4)**:

```bash
# Debian 系
cat /var/lib/bind/db.20.168.192

# RHEL 系
cat /var/named/zone/db.20.168.192
```

**期待される出力例**:

```
$TTL 86400
@       IN      SOA     mgmt-server.example.org. root.example.org. (
        2026030601 ;Serial
        3600            ;Refresh
        1800            ;Retry
        604800          ;Expire
        86400           ;Minimum TTL
)

       IN      NS       mgmt-server.example.org.

; === PTR レコード ===
10                      IN      PTR     host1.example.org.
11                      IN      PTR     host2.example.org.
```

**確認ポイント (IPv4 逆引き)**:

1. **PTR レコード**: 各 IPv4 アドレスの最終オクテットに対する PTR レコードが定義されていることを確認
   - 形式: `<最終オクテット>  IN  PTR  <ホスト名FQDN>.`
   - 例: `10  IN  PTR  host1.example.org.` (192.168.20.10 の逆引き)
   - ホスト名の末尾にドット `.` が付いている (FQDN 形式)

**逆引きゾーンファイルの確認 (IPv6)**:

```bash
# Debian 系
cat /var/lib/bind/db.1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f

# RHEL 系
cat /var/named/zone/db.1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f
```

**期待される出力例**:

```
$TTL 86400
@       IN      SOA     mgmt-server.example.org. root.example.org. (
        2026030601 ;Serial
        3600            ;Refresh
        1800            ;Retry
        604800          ;Expire
        86400           ;Minimum TTL
)

       IN      NS       mgmt-server.example.org.

; === PTR レコード ===
0.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0       IN      PTR     host1.example.org.
1.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0       IN      PTR     host2.example.org.
```

**確認ポイント (IPv6 逆引き)**:

1. **PTR レコード**: 各 IPv6 アドレスのホスト部がニブル形式で定義されていることを確認
   - 形式: `<ニブル表現>  IN  PTR  <ホスト名FQDN>.`
   - 例: `0.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0  IN  PTR  host1.example.org.` (`fd00:1234:5678:1::10` の逆引き)
   - ホスト名の末尾にドット `.` が付いている (FQDN 形式)

### パターン2: IPv4 限定構成

IPv4 のみでの運用時に, `dns_bind_ipv4_only: true` を設定した場合の検証:

- ステップ1-4, 7-9 を実施
- ステップ5 (IPv6 逆引き) と ステップ6 (SELinux, 該当環境のみ) をスキップ

**特別な確認**:

```bash
systemctl cat named.service | grep ExecStart
```

**確認ポイント**: ExecStart に `-4` フラグが付与されていること

### パターン3: 複数ネットワーク対応

`internal_network_list` で複数ネットワークを構成した場合の検証:

- ステップ1-9 をすべて実施
- **追加ステップ**: 複数ネットワークゾーンの確認

#### 追加ステップ: 複数ネットワークゾーン確認

```bash
# 複数ネットワークの逆引きゾーン確認
named-checkconf -z 2>&1 | grep "in-addr.arpa\|ip6.arpa"

# 複数ネットワークのゾーンファイル内容確認
cat /var/lib/bind/db.30.168.192  # 追加 IPv4 逆引きゾーン例
cat /var/lib/bind/db.2.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f  # 追加 IPv6 逆引きゾーン例
```

**期待出力**: 複数ネットワークの逆引きゾーンが定義されていること

**確認ポイント**: スケルトンゾーン (SOA + NS のみ) が生成されていること (PTR レコードは nsupdate で動的登録)

## トラブルシューティング

### 問題1: named が起動しない

**症状**: `systemctl status named` (または `bind9`) で `failed` 状態

**診断方法**:

```bash
journalctl -u named -n 50  # RHEL
journalctl -u bind9 -n 50  # Debian
```

**原因と解決**:

1. **設定構文エラー**: `named-checkconf -z` でエラー確認 => 修正 => `systemctl restart named`

2. **ポート競合**: `ss -tulpn | grep :53` で確認 => `systemctl stop systemd-resolved` 等で対象サービス停止

3. **パーミッション問題**: ゾーンファイル所有者を確認 => `chown {{ dns_bind_user }}:{{ dns_bind_group }}` で修正

### 問題2: ゾーン読み込みエラー

**症状**: `named-checkconf -z` で `zone ... loading from master file ... failed` / journalctl に `zone transfer ... failed`

**診断方法**:

```bash
named-checkzone example.org /var/lib/bind/db.example.org  # Debian
named-checkzone example.org /var/named/zone/db.example.org  # RHEL
```

**原因と解決**:

1. **ゾーンファイル構文エラー**: `named-checkzone` 出力でエラー行を特定 => 修正 (特に FQDN 末尾のドット (`.`) 忘れに注意)

2. **シリアル番号問題**: `bind_serial` が未指定なら自動生成; 手動設定時は更新時にシリアル番号を増加

3. **ファイルパーミッション**: `chmod 644 /var/lib/bind/db.*` と `chown` で修正

### 問題3: SELinux 阻止 (RHEL 系のみ)

**症状**: named 起動時に Permission denied / ゾーンファイル読み込み失敗

**診断方法**:

```bash
ausearch -m avc -ts recent
```

**解決方法**:

```bash
semanage fcontext -a -t named_zone_t '/var/named/zone(/.*)?'
restorecon -Rv /var/named/zone/
ls -Z /var/named/zone/  # 確認
```

### 問題4: Dynamic DNS 更新失敗

**症状**: nsupdate で `update failed: REFUSED` / journalctl に `update denied`

**診断方法**:

```bash
rndc status
```

**原因と解決**:

1. **TSIG キーパス間違い**: `dns_rndc_key_path` を確認 => nsupdate で正しいパス指定

2. **TSIG キー名不一致**: `dns_ddns_key_name` と `named.conf.zones` の `grant` 行が一致か確認

3. **rndc controls が無効 (RHEL 系)**: `rhel-named.conf.options.j2` に `controls { ... }` が存在か確認 => 未生成なら `rndc-confgen -a -c /etc/rndc.key` 手動実行

### 問題5: Firewall 疎通不可

**症状**: リモートホストから DNS クエリが応答しない / `dig` でタイムアウト

**診断方法**:

```bash
firewall-cmd --list-all  # RHEL
ufw status verbose  # Debian
```

**原因と解決**:

1. **Firewall ルール未設定**: `enable_firewall: false` の場合 => `enable_firewall: true` に設定 => ロール再実行

2. **Firewall デーモン停止中**: `systemctl status firewalld` (RHEL) または `ufw status` (Debian) 確認 => 停止中なら手動でポート開放

3. **ゾーン指定ミス (firewalld)**: `dns_bind_firewall_zone` を明示的に指定 (例: `"public"`) => デフォルトゾーン確認 `firewall-cmd --get-default-zone`

### 問題6: 複数ネットワーク逆引きゾーンの重複定義

**症状**: `named-checkconf -z` で `zone "..." already defined` エラー / named が起動失敗

**診断方法**:

```bash
named-checkconf -z 2>&1 | grep "already defined"
```

**原因**: `dns_ipv4_reverse` と `internal_network_list` の IPv4 ネットワークが重複

**解決方法**:

- `dns_ipv4_reverse` で定義したネットワークと `internal_network_list` のネットワークを完全に分離
- 例: `dns_ipv4_reverse: "20.168.192"` (192.168.20.0/24) の場合 => `internal_network_list` には `192.168.30.0/24`, `192.168.40.0/24` のみ定義
- `internal_network_list` から重複するネットワーク定義を削除
- `named-checkconf -z` でエラー解消確認

## 複数ネットワーク逆引きゾーン対応

本ロールは複数ネットワークの逆引きゾーン ( IPv4 PTR / IPv6 PTR6 ) を自動生成できます。

### 機能概要

- **単一ネットワーク**: 既存の `dns_ipv4_reverse`, `dns_ipv6_reverse`, `dns_host_list` による逆引きゾーン生成は **変更なし**で引き続き利用可能。
- **複数ネットワーク**: `internal_network_list` を定義することで, 追加ネットワークの逆引きゾーンを自動生成。各ネットワークはカスタムフィルター ( `ipv4_reverse_zone`, `ipv6_reverse_zone` ) で CIDR ノーテーションから自動的にゾーン名を計算。
- **動的登録対応**: 追加ネットワークのゾーンファイルはスケルトン ( SOA + NS のみ ) で生成。PTR/PTR6 レコードはクライアント側の `nsupdate` で動的に登録する運用を想定。

### 設定例

#### `group_vars/all/all.yml` または `host_vars/<hostname>/main.yml`

```yaml
# === 複数ネットワーク逆引きゾーン ===
internal_network_list:
  # ネットワーク1: IPv4 + IPv6 双方指定
  - ipv4: "192.168.30.0/24"
    ipv6: "fd69:6684:61a:2::/64"
  # ネットワーク2: IPv4 のみ
  - ipv4: "192.168.40.0/25"
  # ネットワーク3: IPv6 のみ
  - ipv6: "fd69:6684:61a:3::/64"
```

#### 生成されるゾーン定義 (named.conf.zones)

```bind
// === 複数ネットワーク逆引きゾーン ===
zone "30.168.192.in-addr.arpa" IN {
        type    master;
        file    "/var/lib/bind/db.30.168.192";
        update-policy {
                grant ddns-clients zonesub ANY PTR;
        };
};

zone "2.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f.ip6.arpa" IN {
        type    master;
        file    "/var/lib/bind/db.2.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f";
        update-policy {
                grant ddns-clients zonesub ANY PTR;
        };
};

// ... (ネットワーク2, 3 も同様)
```

#### 生成されるゾーンファイル

ファイル `/var/lib/bind/db.30.168.192` (IPv4 逆引きゾーン例):

```dns
$TTL 86400
@       IN      SOA     mgmt-server.example.org. root.example.org. (
        202601201200 ;Serial
        3600            ;Refresh
        1800            ;Retry
        604800          ;Expire
        86400           ;Minimum TTL
)

       IN      NS       mgmt-server.example.org.

; === 動的 DNS (nsupdate) レコード登録ゾーン ===
; 以下のネットワークアドレス範囲の逆引きレコード(PTR)は
; nsupdateで動的に登録してください。
;
; 登録対象ネットワーク: 192.168.30.0/24
;
; 登録例:
; nsupdate -k /etc/bind/ddns.key
; > server 192.168.30.1
; > zone 30.168.192.in-addr.arpa.
; > update add 100.30.168.192.in-addr.arpa 3600 PTR hostname.example.org.
; > send
;
```

### クライアント側の nsupdate 使用例

```bash
#!/bin/bash
# クライアント側で動的に PTR を登録

DNS_SERVER="192.168.30.1"
REVERSE_ZONE="30.168.192.in-addr.arpa"
DDNS_KEY="/etc/bind/ddns.key"
HOSTNAME="client01.example.org"
IPADDR="192.168.30.100"
TTL=3600

# IPv4 逆引きレコード登録
nsupdate -k "$DDNS_KEY" <<EOF
server $DNS_SERVER
zone $REVERSE_ZONE
update add ${IPADDR##*.}.${IPADDR%.*} $TTL PTR $HOSTNAME.
send
EOF

# IPv6 の場合 ( 例 )
# IPv6 PTR の計算: fd69:6684:61a:2::100  =>  0.0.1.0.0.0.0.0.0.0.0.0.2.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f.ip6.arpa
```

### カスタムフィルターの詳細

#### `ipv4_reverse_zone` フィルター

IPv4 CIDR ネットワークを逆引きゾーン名に変換します。

| 入力 | 出力 | 用途 |
|------|------|------|
| `192.168.30.0/24` | `30.168.192` | zone "30.168.192.in-addr.arpa" |
| `192.168.0.0/16` | `168.192` | zone "168.192.in-addr.arpa" |
| `10.0.0.0/8` | `10` | zone "10.in-addr.arpa" |
| `192.168.30.128/25` | `30.168.192` | /24 未満は最初の 3 オクテット |

**エラーハンドリング**: CIDR 形式不正 ( 例：`192.168.30` など ) の場合, AnsibleFilterError 例外を発生させ, タスク失敗となります。

#### `ipv6_reverse_zone` フィルター

IPv6 プレフィクスとプレフィクス長を逆引きゾーン名 ( ニブル形式 ) に変換します。

| 入力 | 出力 | 用途 |
|------|------|------|
| `fd69:6684:61a:2::/64` | `2.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f` | zone "2.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f.ip6.arpa" |
| `fd69:6684:61a:3::/64` | `3.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f` | zone "3.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f.ip6.arpa" |
| `2001:db8::/32` | `8.b.d.0.1.0.0.2` | zone "8.b.d.0.1.0.0.2.ip6.arpa" |

**エラーハンドリング**:
- IPv6 形式不正 ( 例：`gggg::` )  =>  AnsibleFilterError
- プレフィクス長が 0-128 範囲外  =>  AnsibleFilterError

### 注意事項

1. **CIDR 形式必須**: `ipv4` キーは必ず CIDR ノーテーション ( プレフィクス長付き ) で指定してください。例：`"192.168.30.0/24"`

2. **重複定義回避**: 同一ネットワークを `internal_network_list` 内で重複定義しないでください。
   - **問題**: リスト内で同一ネットワーク CIDR が複数回現れると, ループで複数の同一ゾーンファイルが生成され, `named.conf.zones` に同じゾーン定義が複数記載されます。

3. **プレフィクス長の妥当性**:
   - IPv4: `/8` ～ `/32` 推奨 ( その他は動作しますが, 逆引きゾーン規模に注意 )
   - IPv6: `/48` ～ `/128` 推奨

4. **既存ネットワークとの分離**: `dns_ipv4_reverse` と `internal_network_list` の IPv4 ネットワークは重複させないでください。
   - **重複時の問題**:
     - `named-checkconf -z` でゾーン定義の重複エラーが発生：`zone "...".*arpa" already defined`
     - named サービスが起動失敗し, DNS 機能が利用不可
     - Ansible タスク実行時に `named_check_conf` ハンドラでエラー検出 ( RHEL 系 )
     - クライアント側の nsupdate で PTR 登録時に, どちらのゾーンに登録すべきか不明になり, レコード登録失敗のリスク

   **対策**:
   - `dns_ipv4_reverse` で定義したネットワーク ( 例：`192.168.20.0/24`  =>  `dns_ipv4_reverse: "20.168.192"` ) と `internal_network_list` の IPv4 ネットワークを完全に分離してください。
   - 例：既に `192.168.20.0/24` が単一ネットワーク定義の場合, `internal_network_list` には `192.168.30.0/24`, `192.168.40.0/24` など別のネットワークのみ定義します。
   - 確認コマンド：`named-checkconf -z` が実行時にエラー無しで完了すれば, ゾーン定義重複がないことを保証します。

5. **`bind_serial` の更新**: テンプレート生成時に シリアルが自動更新されるため, 複数回実行しても問題ありません。

テンプレートは `templates/` 配下にあり, 環境に合わせて `named.conf.*` や `db.*` を生成します。特に `named.conf.zones.j2` では `grant ddns-clients zonesub` によりサブゾーン単位の Dynamic DNS を許可します。`bind_serial` を事前に指定すると SOA シリアルを固定できます。

## 留意事項

### セキュリティ

- **TSIG シークレット管理**: `dns_ddns_key_secret` は機密情報を含むファイルであるため, セキュリティ方針に応じて適切に管理してください。
- **Firewall 無効化時のリスク**: `enable_firewall: false` に設定すると, DNS ポートが外部に開放されたままになります。セキュリティ方針に応じて適切に設定してください。

### 運用上の留意事項

- **IPv4 限定設定の適用範囲**: IPv6 で外部と到達できない検証環境だけで `dns_bind_ipv4_only: true` に設定し, `templates/90-override.conf.j2` が生成する systemd の追加設定ファイルで `ExecStart` に `-4` を付与して IPv4 のみに限定します。IPv6 を提供したい場合はデフォルトの `false` のままにしてください。
- **ゾーンファイルの管理**: ゾーンファイルはテンプレート生成のため, 手動編集ではなく `dns_host_list` や関連変数を更新してロールを再実行する運用を前提としています。手動編集した内容は次回のロール実行時に上書きされます。
- **Dynamic DNS クライアントとの統合**: Dynamic DNS クライアントスクリプト (`roles/common/templates/ddns-client-update.sh.j2` 等) と組み合わせる場合, FQDN 末尾のドット (`.`) やゾーン名の整合性に注意してください。
- **複数ネットワーク逆引きゾーンの重複チェック**: 重複定義の自動検出機能がないため, `named-checkconf -z` を手動で実行して重複がないことを運用者側で確認してください。特に `dns_ipv4_reverse` と `internal_network_list` のネットワークが重複しないように注意してください。
- **シリアル番号の自動更新**: `bind_serial` が未指定の場合, テンプレート生成時に日付ベースのシリアル番号が自動生成されます。シリアル番号を固定したい場合は明示的に `bind_serial`変数 を設定してください。
