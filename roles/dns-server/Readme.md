# dns-server ロール

BIND を用いた権威兼キャッシュ DNS サーバーを構成するロールです。対象 OS のファクトに応じて Debian 系と RHEL 系の差異を吸収し, ゾーンファイルと `named.conf`/`named.conf.options` をテンプレートで生成します。Dynamic DNS 更新用の TSIG キーを組み込み, IPv4/IPv6 双方の順引き・逆引きゾーンを作成し, 必要に応じて systemd, SELinux, Firewall の周辺設定も行います。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
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

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系(Rocky Linux, AlmaLinuxなど, Alma Linux9.6を想定)
- Ansible 2.15 以降
  - `ansible.posix` コレクションがインストールされていること
- リモートホストへの SSH 接続が確立されていること
- `sudo`による管理者権限でのコマンド実行が可能であること
- DNS ポート (53/tcp, 53/udp) の開放権限 (Firewall 有効時)
- SELinux 設定権限 (RHEL 系のみ)
- インターネット接続 (パッケージ取得用)

## 実行フロー

本ロールは以下の順序で処理を実行します:

1. **パラメータ読み込み** (`load-params.yml`): OS ファミリー別パッケージ定義 (`vars/packages-ubuntu.yml`, `vars/packages-rhel.yml`) と共通変数 (`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込み, ドメインやネットワーク関連変数を構成します。
2. **パッケージインストール** (`package.yml`): `dns_bind_packages` を最新化します。変更があれば `disable_gui` ハンドラを通知し, systemd のデフォルトターゲットを `multi-user.target` に設定します。
3. **設定ファイル配置とゾーンファイル生成** (`config.yml`):
   - 設定・ゾーン格納ディレクトリを所定の所有者とパーミッションで作成
   - **RHEL 系**: 既存の `named.conf` をバックアップし, `rhel-named.conf.j2` で最小クリーン版に置換
   - **Debian 系**: `lineinfile` でゾーン定義の include 行のみ挿入
   - OS ごとの `named.conf.options` テンプレートを配置し, フォワーダー (`dns_bind_forwarders`) や ACL (`dns_network`, `dns_network_ipv6_prefix`) を反映
   - `named.conf.zones.j2` と各ゾーンテンプレートを展開し, `dns_host_list` と `bind_serial` から順引き/逆引きレコードを生成 (`bind_serial` が未指定なら日付ベースで設定)
   - **複数ネットワーク対応**: `internal_network_list` が定義かつ非空の場合, カスタムフィルター (`ipv4_reverse_zone`, `ipv6_reverse_zone`) でネットワーク CIDR から逆引きゾーン名を自動計算し, 追加の IPv4/IPv6 逆引きゾーンファイル (`db.reverse.additional.j2`, `db.reverse.additional.ipv6.j2`) をループで生成 (ゾーンはスケルトン: SOA + NS のみ, PTR レコードは nsupdate で動的登録を前提)
   - **RHEL 系専用**: `rndc.key` を `rndc-confgen` で生成し `/etc/rndc.key` に配置, `named.conf.options` に controls セクションと rndc.key の include を追加
   - **RHEL 系専用**: 暗号ポリシーの include をコメントアウト (docker.io などの検証で弾かれる問題を回避)
   - **RHEL 系専用**: SELinux 有効時, zone ディレクトリの fcontext を `semanage` で登録し `restorecon` を実行
   - `named_check_conf` と `Reload systemd & restart named` ハンドラを通知
   - `named-checkconf -z` と `systemd` リスタート, `rndc reload` を順に実行
4. **DNS応答をIPv4 に限定するための設定** (`config-systemd-ipv4-only.yml`): `dns_bind_ipv4_only` が `true` の場合, `systemctl show` で取得した ExecStart に `-4` フラグが無い場合のみ systemd drop-in (`templates/90-override.conf.j2`) を生成し, IPv4 応答に限定します (デフォルトでは IPv6 での応答にも対応)。
5. **Firewall 設定** (`config-firewall.yml`): `enable_firewall` が `true` のときに firewalld または UFW を自動判別し, `dns_bind_port` (既定: 53) の TCP/UDP を開放します。バックエンドが検出されない場合は通知のみを実施します。
6. **ハンドラ実行**: 構成変更に応じて `Reload systemd & restart named`, `named_check_conf`, `reload_zone`, `disable_gui` を実行します。

## 主要変数

### ロール固有変数 (defaults/main.yml)

| 変数名 | 既定値 | 定義場所 | 説明 |
| --- | --- | --- | --- |
| `dns_ddns_key_name` | `"ddns-clients"` | defaults/main.yml | Dynamic DNS update key 名 (クライアント側とサーバ側で共通)。 |
| `dns_bind_user` | Debian: `"bind"`, RHEL: `"named"` | defaults/main.yml | BIND 実行ユーザ名。 |
| `dns_bind_group` | Debian: `"bind"`, RHEL: `"named"` | defaults/main.yml | BIND 実行グループ名。 |
| `dns_bind_service` | `"named"` | defaults/main.yml | BIND systemd サービス名。 |
| `dns_bind_conf_dir` | Debian: `"/etc/bind"`, RHEL: `"/etc/named"` | defaults/main.yml | BIND 設定ディレクトリ。 |
| `dns_bind_main_conf` | Debian: `"/etc/bind/named.conf"`, RHEL: `"/etc/named.conf"` | defaults/main.yml | BIND メイン設定ファイル。 |
| `dns_bind_zone_dir` | Debian: `"/var/lib/bind"`, RHEL: `"/var/named/zone"` | defaults/main.yml | ゾーンファイル格納ディレクトリ。 |
| `dns_bind_run_dir` | `"/run/named"` | defaults/main.yml | PID ファイルなどのランタイムディレクトリ。 |
| `dns_bind_cache_dir` | Debian: `"/var/cache/bind"`, RHEL: `"/var/named"` | defaults/main.yml | キャッシュファイル格納ディレクトリ。 |
| `dns_bind_options_conf_path` | Debian: `"/etc/bind/named.conf.options"`, RHEL: `"/etc/named/named.conf.options"` | defaults/main.yml | オプション設定ファイルパス。 |
| `dns_bind_systemd_dropin_dir` | `"/etc/systemd/system/named.service.d"` | defaults/main.yml | systemd drop-in ディレクトリ。 |
| `dns_bind_systemd_dropin_file` | `"90-override.conf"` | defaults/main.yml | systemd drop-in ファイル名。 |
| `dns_bind_selinux_type` | `"named_zone_t"` | defaults/main.yml | SELinux ゾーン用タイプ (RHEL 系のみ使用)。 |
| `dns_bind_selinux_target` | `"/var/named(/.*)?"` | defaults/main.yml | SELinux fcontext を適用するパス (RHEL 系のみ使用)。 |
| `dns_bind_keyfile` | Debian: `"/usr/share/dns/root.key"`, RHEL: `"/etc/named.root.key"` | defaults/main.yml | DNSSEC ルート鍵ファイルパス。 |
| `dns_bind_port` | `53` | defaults/main.yml | DNS ポート番号。 |
| `dns_bind_ipv4_only` | `false` | defaults/main.yml | IPv4 のみに限定する場合に `true` (systemd drop-in で ExecStart に `-4` を付与)。 |
| `dns_bind_firewall_zone` | `null` | defaults/main.yml | firewalld のゾーン名 ( `null` の場合はデフォルトゾーンを使用)。 |
| `dns_bind_forwarders` | `["1.1.1.1", "8.8.8.8"]` | defaults/main.yml | 上位 DNS へのフォワーダー一覧。空にすると forward 設定を省略します。 |


### OS 差異吸収変数 (vars/cross-distro.yml)

| 変数名 | 既定値 | 定義場所 | 説明 |
| --- | --- | --- | --- |
| `dns_bind_packages` | Debian: `["bind9", "bind9-utils"]`, RHEL: `["bind", "bind-utils"]` | vars/cross-distro.yml | OS 別 BIND パッケージ一覧。 |
| `dns_rndc_key_name` | `"rndc-key"` | vars/cross-distro.yml | rndc 制御用 TSIG キー名。 |
| `dns_rndc_key_path` | Debian: `"/etc/bind/rndc.key"`, RHEL: `"/etc/rndc.key"` | vars/cross-distro.yml | rndc 制御用 TSIG キーファイルパス。 |

### サイト全体共通変数 (vars/all-config.yml)

| 変数名 | 既定値 | 定義場所 | 説明 |
| --- | --- | --- | --- |
| `dns_domain` | (サイト固有) | vars/all-config.yml | 正引きゾーン名。ゾーンファイルの SOA・NS レコードを決定します。 |
| `dns_server` | (サイト固有) | vars/all-config.yml | SOA ホスト名 (FQDN)。 |
| `dns_network` | (サイト固有) | vars/all-config.yml | IPv4 ACL とゾーン内 A レコードのベースアドレス。 |
| `dns_network_ipv4_prefix_len` | (サイト固有) | vars/all-config.yml | IPv4 ネットワークプレフィクス長。 |
| `dns_network_ipv6_prefix` | (サイト固有) | vars/all-config.yml | IPv6 ACL や逆引きゾーンの生成に使用するプレフィクス。 |
| `dns_network_ipv6_prefix_len` | (サイト固有) | vars/all-config.yml | IPv6 ネットワークプレフィクス長。 |
| `dns_host_list` | (サイト固有) | vars/all-config.yml | 順引き/逆引きレコードを生成するためのホスト定義リスト。 |
| `dns_ipv4_reverse` | (サイト固有) | vars/all-config.yml | IPv4 逆引きゾーン名 (例: `"20.168.192"`  =>  `"20.168.192.in-addr.arpa"`)。 |
| `dns_ipv6_reverse` | (サイト固有) | vars/all-config.yml | IPv6 逆引きゾーン名 (ニブル形式)。 |
| `dns_ddns_key_secret` | (サイト固有, セキュアに管理) | vars/all-config.yml | Dynamic DNS update key のシークレット。**バージョン管理外に保管してください**。 |
| `internal_network_list` | `[]` | group_vars/all/all.yml | 複数ネットワーク逆引きゾーン対応: 追加ネットワークのリスト。各要素は `{ipv4: "...", ipv6: "..."}` 形式。 |
| `enable_firewall` | `false` | roles/common/defaults/main.yml | Firewall 設定の有効化フラグ。 |

## デフォルト動作

変数が未設定または既定値の場合, 以下の動作となります:

- **Firewall**: `enable_firewall: false` の場合, Firewall 設定はスキップされます (`config-firewall.yml` は実行されません)。
- **IPv4/IPv6 デュアルスタック**: `dns_bind_ipv4_only: false` の場合, named は IPv4 と IPv6 の両方でリッスンします。
- **フォワーダー**: `dns_bind_forwarders` が空リストの場合, 上位 DNS へのフォワード設定を省略します (再帰問い合わせを直接ルートサーバに送信)。
- **複数ネットワーク逆引きゾーン**: `internal_network_list` が未定義または空の場合, 追加の逆引きゾーンは生成されません (単一ネットワーク構成として動作)。
- **SELinux**: RHEL 系で SELinux が有効な場合, `dns_bind_zone_dir` に `named_zone_t` コンテキストを自動適用します。SELinux が無効な場合は SELinux 関連タスクをスキップします。
- **GUI 無効化**: パッケージインストール時に `disable_gui` ハンドラが発火し, systemd のデフォルトターゲットを `multi-user.target` に設定します。

## テンプレート・ファイル

本ロールでは以下のテンプレート/ファイルを出力します:

| テンプレートファイル名 | 出力先パス | OS | 説明 |
| --- | --- | --- | --- |
| `rhel-named.conf.j2` | `/etc/named.conf` | RHEL | 最小クリーン版 named.conf (既存ファイルをバックアップ後に置換)。 |
| `named.conf.options.j2` | `/etc/bind/named.conf.options` | Debian | ACL, options, forwarders を定義。 |
| `rhel-named.conf.options.j2` | `/etc/named/named.conf.options` | RHEL | ACL, options, forwarders, rndc controls セクション, rndc.key の include を定義。 |
| `named.conf.zones.j2` | Debian: `/etc/bind/named.conf.zones`, RHEL: `/etc/named/named.conf.zones` | 両方 | 順引き/逆引きゾーン定義 (単一ネットワーク + 複数ネットワーク)。 |
| `db.forward.conf.j2` | Debian: `/var/lib/bind/db.<DNSドメイン名>`, RHEL: `/var/named/zone/db.<DNSドメイン名>` | 両方 | 順引きゾーンファイル (A/AAAA レコード)。 |
| `db.reverse.j2` | Debian: `/var/lib/bind/db.<DNSゾーンのIPv4アドレスを逆順に記載した文字列>`, RHEL: `/var/named/zone/db.<DNSゾーンのIPv4アドレスを逆順に記載した文字列>` | 両方 | 逆引き IPv4 ゾーンファイル (PTR レコード)。 |
| `db.reverse.ipv6.j2` | Debian: `/var/lib/bind/db.<DNSゾーンのIPv6アドレスを逆順に記載した文字列>`, RHEL: `/var/named/zone/db.<DNSゾーンのIPv6アドレスを逆順に記載した文字列>` | 両方 | 逆引き IPv6 ゾーンファイル (PTR レコード)。 |
| `db.reverse.additional.j2` | Debian: `/var/lib/bind/db.<DNSゾーンのIPv4アドレスを逆順に記載した文字列>`, RHEL: `/var/named/zone/db.<DNSゾーンのIPv4アドレスを逆順に記載した文字列>` | 両方 | 追加逆引き IPv4 ゾーンファイル (スケルトン: SOA + NS のみ)。 |
| `db.reverse.additional.ipv6.j2` | Debian: `/var/lib/bind/db.<DNSゾーンのIPv6アドレスを逆順に記載した文字列>`, RHEL: `/var/named/zone/db.<DNSゾーンのIPv6アドレスを逆順に記載した文字列>` | 両方 | 追加逆引き IPv6 ゾーンファイル (スケルトン: SOA + NS のみ)。 |
| `90-override.conf.j2` | `/etc/systemd/system/named.service.d/90-override.conf` | 両方 | IPv4 限定用 systemd drop-in (ExecStart override オプションに `-4` を追加)。 |

## OS 差異

RHEL 系 (Rocky Linux, AlmaLinux 等) と Debian 系 (Debian, Ubuntu) の主な差異を以下に示します:

| 項目 | Debian 系 | RHEL 系 | 備考 |
| --- | --- | --- | --- |
| **BIND パッケージ** | `bind9`, `bind9-utils` | `bind`, `bind-utils` | パッケージ名が異なる。 |
| **実行ユーザ/グループ** | `bind:bind` | `named:named` | ファイル所有者が異なる。 |
| **設定ディレクトリ** | `/etc/bind` | `/etc/named` | 設定ファイルの配置場所が異なる。 |
| **ゾーンファイルディレクトリ** | `/var/lib/bind` | `/var/named/zone` | ゾーンファイルの配置場所が異なる。 |
| **キャッシュディレクトリ** | `/var/cache/bind` | `/var/named` | キャッシュファイルの配置場所が異なる。 |
| **named.conf 構造** | 既存ファイルに include 行のみ追加 | 既存ファイルをバックアップ後, 最小クリーン版に置換 | RHEL では既存設定を完全にリセット。 |
| **rndc.key 生成** | bind9 パッケージの postinst が自動生成 | ロール内で `rndc-confgen` を明示的に実行 | Debian では自動, RHEL では手動生成が必要。 |
| **controls セクション** | 未定義 (rndc.key が存在すれば自動有効化) | `named.conf.options` に明示的に定義 | RHEL では明示的な設定が必要。 |
| **暗号ポリシー** | 該当なし | `/etc/crypto-policies/back-ends/bind.config` の include をコメントアウト | RHEL で docker.io などの検証で弾かれる問題を回避。 |
| **SELinux** | 該当なし | 有効時に `semanage fcontext` と `restorecon` を実行 | RHEL のみ SELinux コンテキスト設定が必要。 |
| **Firewall バックエンド** | UFW | firewalld | Debian では UFW, RHEL では firewalld を優先。 |

### RHEL 専用処理の詳細

RHEL 系では以下の専用処理を実施します:

1. **rndc.key 生成**:
   - `rndc-confgen -a -c {{ dns_rndc_key_path }}` を実行し, `/etc/rndc.key` に TSIG キーを生成します。
   - Debian 系では bind9 パッケージの postinst が自動生成するため, この処理は不要です。

2. **named.conf 置換**:
   - 既存の `/etc/named.conf` を `/etc/named.conf.orig` にバックアップします。
   - `rhel-named.conf.j2` テンプレートで最小クリーン版の named.conf を配置します (include 行のみを含む簡潔な構成)。
   - Debian 系では既存ファイルに include 行のみを追加します。

3. **controls セクションと rndc.key の include**:
   - `rhel-named.conf.options.j2` に以下を追加:
     ```bind
     include "{{ dns_rndc_key_path }}";
     controls {
         inet 127.0.0.1 port 953 allow { 127.0.0.1; } keys { "{{ dns_rndc_key_name }}"; };
     };
     ```
   - Debian 系では controls セクションが未定義でも, rndc.key が所定パスに存在すれば自動的に有効化されます。

4. **暗号ポリシー無効化**:
   - `rhel-named.conf.options.j2` の options セクション内で, `/etc/crypto-policies/back-ends/bind.config` の include をコメントアウトします:
     ```bind
     // 以下をコメントにしている
     //include "/etc/crypto-policies/back-ends/bind.config";
     ```
   - 理由: RHEL の暗号ポリシーは RSASHA1 / SHA-1 を禁止していますが, これを禁止すると docker.io などの検証で弾かれる問題があります。

5. **SELinux fcontext 設定**:
   - SELinux が有効な場合, `semanage fcontext -a -t named_zone_t '{{ dns_bind_selinux_target }}'` を実行します。
   - `restorecon -Rv {{ dns_bind_zone_dir }}` でゾーンディレクトリに `named_zone_t` コンテキストを適用します。
   - Debian 系には SELinux が存在しないため, この処理は不要です。

## 設定例

### 基本設定 (単一ネットワーク)

`vars/all-config.yml`:

```yaml
dns_domain: "example.com"
dns_server: "ns1.example.com"
dns_server_ipv4_address: "192.168.20.1"
dns_network: "192.168.20.0"
dns_network_ipv4_prefix_len: 24
dns_network_ipv6_prefix: "fd00:1234:5678:1::"
dns_network_ipv6_prefix_len: 64
dns_ipv4_reverse: "20.168.192"
dns_ipv6_reverse: "1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f"
dns_host_list:
  - { name: "host1", ipv4: "192.168.20.10", ipv6: "fd00:1234:5678:1::10" }
  - { name: "host2", ipv4: "192.168.20.11", ipv6: "fd00:1234:5678:1::11" }
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

## Firewall 周辺の挙動

| enable_firewall | firewalld 動作状況 | UFW 利用可否 | 実行される処理 |
| --- | --- | --- | --- |
| `false` | 無関係 | 無関係 | `config-firewall.yml` はスキップされます。 |
| `true` | 実行中 | 任意 | `firewall-cmd` で DNS サービスまたは `dns_bind_port` (既定: 53) を永続/ランタイム双方に開放します (`dns_bind_firewall_zone` が空ならデフォルトゾーン)。 |
| `true` | 非稼働 | 利用可 | `ufw allow {{ dns_bind_port }}/tcp` と `ufw allow {{ dns_bind_port }}/udp` を既存ルールを見ながら追加します。 |
| `true` | 非稼働 | 利用不可 | いずれのバックエンドも検出できず, スキップメッセージのみを出力します。 |

**セキュリティ上の注意**:

- `enable_firewall: false` に設定すると, DNS ポートが外部に開放されたままになります。信頼されたネットワーク内でのみ設定してください。
- firewalld, UFW が両方とも無効な環境で `enable_firewall: true` を設定すると, スキップメッセージのみが出力され, ポート開放が行われません。この場合, Ansible 実行後に手動で iptables / nftables ルールを追加する必要があります。

## 検証ポイント

ロール適用後, 以下の手順で DNS サーバーの動作を検証します。

### 前提条件

- DNS 設定が反映済み (Ansible ロール実行完了)
- named サービスが起動中

### 手順1: サービス状態確認

**RHEL 系**:

```bash
systemctl status named
```

**Debian 系**:

```bash
systemctl status bind9
```

**期待出力**:

```plaintext
● named.service - Berkeley Internet Name Domain (DNS)
   Loaded: loaded (/usr/lib/systemd/system/named.service; enabled; preset: disabled)
   Active: active (running) since ...
```

または

```plaintext
● bind9.service - BIND Domain Name Server
   Loaded: loaded (/lib/systemd/system/bind9.service; enabled; preset: enabled)
   Active: active (running) since ...
```

**確認ポイント**:

- `Active: active (running)` が表示されること
- `enabled` 状態であること (自動起動が有効)

### 手順2: 設定構文検証

```bash
named-checkconf -z
```

**期待出力**:

```plaintext
zone example.com/IN: loaded serial 2026022301
zone 20.168.192.in-addr.arpa/IN: loaded serial 2026022301
zone 1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f.ip6.arpa/IN: loaded serial 2026022301
```

**確認ポイント**:

- 全ゾーンが `loaded serial` と表示されること
- エラーメッセージが出力されないこと
- 複数ネットワーク逆引きゾーンが設定されている場合, 追加ゾーンも `loaded serial` と表示されること

### 手順3: 順引き解決確認

```bash
dig @localhost host1.example.com
```

**期待出力**:

```plaintext
;; ANSWER SECTION:
host1.example.com.     86400   IN      A       192.168.20.10
host1.example.com.     86400   IN      AAAA    fd00:1234:5678:1::10

;; Query time: 0 msec
;; SERVER: ::1#53(localhost) (UDP)
;; WHEN: ...
;; MSG SIZE  rcvd: ...
``  `

**確認ポイント**:

- ANSWER セクションに A レコード (192.168.20.10) が表示されること
- ANSWER セクションに AAlocal レコード (fd00:1234:5678:1::10) が表示されること (IPv6 有効時)
- `ANSWER: 1` 以上が表示されること

### 手順4: 逆引き解決確認 (IPv4)

```bash
dig @localhost -x 192.168.20.10
```

**期待出力**:

```plaintext
;; ANSWER SECTION:
10.20.168.192.in-addr.arpa. 86400 IN   PTR     host1.example.com.

;; Query time: 0 msec
```;

**確認ポイント**:

- ANSWER セクションに PTR レコード (host1.example.com.) が表示されること

### 手順5: 逆引き解決確認 (IPv6)

```bash
dig @localhost -x fd00:1234:5678:1::10
```

**期待出力**:

```plaintext
;; ANSWER SECTION:
0.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f.ip6.arpa. 86400 IN PTR host1.example.com.

;; Query time: 0 msec
```

**確認ポイント**:

- ANSWER セクションに PTR レコード (host1.example.com.) が表示されること

### 手順6: SELinux コンテキスト確認 (RHEL 系のみ)

```bash
ls -Z /var/named/zone/
```

**期待出力**:

```plaintext
unconfined_u:object_r:named_zone_t:s0 db.example.com
unconfined_u:object_r:named_zone_t:s0 db.20.168.192
unconfined_u:object_r:named_zone_t:s0 db.1.0.0.0.8.7.6.5.4.3.2.1.0.0.d.f
```

**確認ポイント**:

- 全ゾーンファイルのコンテキストが `named_zone_t` であること

### 手順7: Firewall 設定確認

**firewalld (RHEL 系)**:

```bash
firewall-cmd --list-services
firewall-cmd --list-ports
```

**期待出力**:

```plaintext
dns dhcpv6-client ssh
```

または

```plaintext
53/tcp 53/udp
```

**UFW (Debian 系)**:

```bash
ufw status
```

**期待出力**:

```plaintext
Status: active

To                         Action      From
--                         ------      ----
53/tcp                     ALLOW       Anywhere
53/udp                     ALLOW       Anywhere
```

**確認ポイント**:

- DNS サービスまたは 53/tcp, 53/udp が許可されていること

### 手順8: Dynamic DNS 更新確認


```bash
# TSIG キーファイルを使用
nsupdate -k /etc/bind/rndc.key << EOF
server 192.168.20.1
zone example.com.
update add test-host.example.com. 300 A 192.168.20.100
send
EOF

# 更新されたレコードを確認
dig @localhost test-host.example.com
```

**期待出力**:

```plaintext
;; ANSWER SECTION:
test-host.example.com. 300 IN   A       192.168.20.100
```

**確認ポイント**:

- nsupdate が成功すること (エラーメッセージが出力されないこと)
- dig で新規追加したレコードが取得できること

### 手順9: ゾーンファイル内容確認

```bash
cat /var/lib/bind/db.example.com  # Debian 系
cat /var/named/zone/db.example.com  # RHEL 系
```

**期待出力**:

```dns
$TTL 86400
@       IN      SOA     ns1.example.com. root.example.com. (
        2026022301 ;Serial
        3600            ;Refresh
        1800            ;Retry
        604800          ;Expire
        86400           ;Minimum TTL
)

       IN      NS       ns1.example.com.

host1   IN      A        192.168.20.10
host1   IN      AAAA     fd00:1234:5678:1::10
host2   IN      A        192.168.20.11
host2   IN      AAAA     fd00:1234:5678:1::11
```

**確認ポイント**:

- SOA レコードが正しく設定されていること
- NS レコードが存在すること
- A/AAAA レコードが `dns_host_list` の定義通りに生成されていること

## トラブルシューティング

### 問題1: named が起動しない

**症状**:

- `systemctl status named` で `failed` 状態
- `systemctl status bind9` で `failed` 状態

**診断方法**:

```bash
# RHEL 系
journalctl -u named -n 50

# Debian 系
journalctl -u bind9 -n 50
```

**原因と解決方法**:

1. **設定ファイルの構文エラー**:
   - `named-checkconf -z` を実行してエラー箇所を特定
   - エラーメッセージに従って `named.conf.options` や `named.conf.zones` を修正
   - 修正後 `systemctl restart named` (または `bind9`) を実行

2. **ポート競合**:
   - `ss -tulpn | grep :53` でポート 53 が既に使用されているか確認
   - 他の DNS サーバー (dnsmasq, systemd-resolved 等) が起動している場合は停止
   - `systemctl stop systemd-resolved` など

3. **パーミッション問題**:
   - ゾーンファイルの所有者を確認: `ls -l /var/lib/bind/` (Debian) または `ls -l /var/named/zone/` (RHEL)
   - `chown {{ dns_bind_user }}:{{ dns_bind_group }} /var/lib/bind/db.*` で修正

### 問題2: ゾーン読み込みエラー

**症状**:

- `named-checkconf -z` で `zone ... loading from master file ... failed`
- journalctl に `zone transfer ... failed` などのエラー

**診断方法**:

```bash
named-checkzone example.com /var/lib/bind/db.example.com  # Debian 系
named-checkzone example.com /var/named/zone/db.example.com  # RHEL 系
```

**原因と解決方法**:

1. **ゾーンファイルの構文エラー**:
   - `named-checkzone` の出力でエラー行を特定
   - SOA レコード, NS レコードの記述ミスを修正
   - 特に FQDN 末尾のドット (`.`) 忘れに注意

2. **シリアル番号の問題**:
   - `bind_serial` を手動設定している場合, 更新時にシリアル番号を増やす必要があります
   - 自動生成 (日付ベース) を使用する場合は `bind_serial` を未定義にします

3. **パーミッション問題**:
   - `chmod 644 /var/lib/bind/db.*` でファイルパーミッションを修正
   - `chown {{ dns_bind_user }}:{{ dns_bind_group }}` で所有者を修正

### 問題3: SELinux 阻止 (RHEL 系のみ)

**症状**:

- named 起動時に Permission denied エラー
- ゾーンファイル読み込み失敗

**診断方法**:

```bash
ausearch -m avc -ts recent
```

**期待出力** (SELinux 拒否ログ):

```plaintext
type=AVC msg=audit(...): avc:  denied  { read } for  pid=... comm="named" name="db.example.com" dev="dm-0" ino=... scontext=system_u:system_r:named_t:s0 tcontext=unconfined_u:object_r:var_t:s0 tclass=file permissive=0
```

**解決方法**:

```bash
# fcontext を設定
semanage fcontext -a -t named_zone_t '/var/named/zone(/.*)?'

# コンテキストを適用
restorecon -Rv /var/named/zone/

# 設定確認
ls -Z /var/named/zone/
```

**確認ポイント**:

- 全ゾーンファイルのコンテキストが `named_zone_t` に変更されること

### 問題4: Dynamic DNS 更新失敗

**症状**:

- nsupdate で `update failed: REFUSED` エラー
- journalctl に `update denied` などのログ

**診断方法**:

```bash
# rndc 接続確認
rndc status
```

**期待出力**:

```plaintext
version: BIND 9.18.x (...)
server is up and running
```

**原因と解決方法**:

1. **TSIG キーパス間違い**:
   - `dns_rndc_key_path` (Debian: `/etc/bind/rndc.key`, RHEL: `/etc/rndc.key`) を確認
   - nsupdate で `-k` オプションに正しいパスを指定

2. **TSIG キー名間違い**:
   - `dns_ddns_key_name` (既定: `"ddns-clients"`) と `named.conf.zones` の `grant` 行が一致しているか確認
   - `named.conf.zones` で `grant ddns-clients zonesub ANY;` が定義されているか確認

3. **rndc controls が無効 (RHEL 系)**:
   - `rhel-named.conf.options.j2` に `controls { ... }` セクションが存在するか確認
   - `/etc/rndc.key` が生成されているか確認: `ls -l /etc/rndc.key`
   - 未生成の場合: `rndc-confgen -a -c /etc/rndc.key` を手動実行

### 問題5: Firewall 疎通不可

**症状**:

- リモートホストから DNS クエリが応答しない
- `dig @<dns_server_ip> ...` でタイムアウト

**診断方法**:

**firewalld (RHEL 系)**:

```bash
firewall-cmd --list-all
```

**UFW (Debian 系)**:

```bash
ufw status verbose
```

**原因と解決方法**:

1. **Firewall ルール未設定**:
   - `enable_firewall` 変数が `false` の場合, `config-firewall.yml` がスキップされます
   - `enable_firewall: true` に設定してロールを再実行

2. **firewalld / UFW が停止中**:
   - `systemctl status firewalld` (RHEL) または `ufw status` (Debian) で状態確認
   - 停止中の場合, 手動でポート開放:
     - firewalld: `firewall-cmd --permanent --add-service=dns && firewall-cmd --reload`
     - UFW: `ufw allow 53/tcp && ufw allow 53/udp`

3. **ゾーン指定ミス (firewalld)**:
   - `dns_bind_firewall_zone` を明示的に指定 (例: `"public"`, `"internal"`)
   - デフォルトゾーンを確認: `firewall-cmd --get-default-zone`

### 問題6: 複数ネットワーク逆引きゾーンの重複定義

**症状**:

- `named-checkconf -z` で `zone "..." already defined` エラー
- named が起動しない

**診断方法**:

```bash
named-checkconf -z 2>&1 | grep "already defined"
```

**原因**:

- `dns_ipv4_reverse` と `internal_network_list` の IPv4 ネットワークが重複
- `internal_network_list` 内で同一ネットワークを複数回定義

**解決方法**:

1. **既存ネットワークとの分離**:
   - `dns_ipv4_reverse` で定義したネットワーク (例: `192.168.20.0/24`) と `internal_network_list` のネットワークを完全に分離
   - 例: `dns_ipv4_reverse: "20.168.192"`  =>  `internal_network_list` には `192.168.30.0/24`, `192.168.40.0/24` のみ定義

2. **重複削除**:
   - `internal_network_list` から重複するネットワーク定義を削除
   - `named-checkconf -z` でエラーが解消されることを確認

## 複数ネットワーク逆引きゾーン対応

本ロールは複数ネットワークの逆引きゾーン（IPv4 PTR / IPv6 PTR6）を自動生成できます。

### 機能概要

- **単一ネットワーク**: 既存の `dns_ipv4_reverse`, `dns_ipv6_reverse`, `dns_host_list` による逆引きゾーン生成は **変更なし**で引き続き利用可能。
- **複数ネットワーク**: `internal_network_list` を定義することで、追加ネットワークの逆引きゾーンを自動生成。各ネットワークはカスタムフィルター（`ipv4_reverse_zone`, `ipv6_reverse_zone`）で CIDR ノーテーションから自動的にゾーン名を計算。
- **動的登録対応**: 追加ネットワークのゾーンファイルはスケルトン（SOA + NS のみ）で生成。PTR/PTR6 レコードはクライアント側の `nsupdate` で動的に登録する運用を想定。

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

# IPv6 の場合（例）
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

**エラーハンドリ**: CIDR 形式不正（例：`192.168.30` など）の場合、AnsibleFilterError 例外を発生させ、タスク失敗となります。

#### `ipv6_reverse_zone` フィルター

IPv6 プレフィクスとプレフィクス長を逆引きゾーン名（ニブル形式）に変換します。

| 入力 | 出力 | 用途 |
|------|------|------|
| `fd69:6684:61a:2::/64` | `2.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f` | zone "2.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f.ip6.arpa" |
| `fd69:6684:61a:3::/64` | `3.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f` | zone "3.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f.ip6.arpa" |
| `2001:db8::/32` | `8.b.d.0.1.0.0.2` | zone "8.b.d.0.1.0.0.2.ip6.arpa" |

**エラーハンドリング**:
- IPv6 形式不正（例：`gggg::`） =>  AnsibleFilterError
- プレフィクス長が 0-128 範囲外  =>  AnsibleFilterError

### 注意事項

1. **CIDR 形式必須**: `ipv4` キーは必ず CIDR ノーテーション（プレフィクス長付き）で指定してください。例：`"192.168.30.0/24"`

2. **重複定義回避**: 同一ネットワークを `internal_network_list` 内で重複定義しないでください。
   - **問題**: リスト内で同一ネットワーク CIDR が複数回現れると、ループで複数の同一ゾーンファイルが生成され、`named.conf.zones` に同じゾーン定義が複数記載されます。

3. **プレフィクス長の妥当性**:
   - IPv4: `/8` ～ `/32` 推奨（その他は動作しますが、逆引きゾーン規模に注意）
   - IPv6: `/48` ～ `/128` 推奨

4. **既存ネットワークとの分離**: `dns_ipv4_reverse` と `internal_network_list` の IPv4 ネットワークは重複させないでください。
   - **重複時の問題**:
     - `named-checkconf -z` でゾーン定義の重複エラーが発生：`zone "...".*arpa" already defined`
     - named サービスが起動失敗し、DNS 機能が利用不可
     - Ansible タスク実行時に `named_check_conf` ハンドラでエラー検出（RHEL 系）
     - クライアント側の nsupdate で PTR 登録時に、どちらのゾーンに登録すべきか不明になり、レコード登録失敗のリスク

   **対策**:
   - `dns_ipv4_reverse` で定義したネットワーク（例：`192.168.20.0/24`  =>  `dns_ipv4_reverse: "20.168.192"`）と `internal_network_list` の IPv4 ネットワークを完全に分離してください。
   - 例：既に `192.168.20.0/24` が単一ネットワーク定義の場合、`internal_network_list` には `192.168.30.0/24`, `192.168.40.0/24` など別のネットワークのみ定義します。
   - 確認コマンド：`named-checkconf -z` が実行時にエラー無しで完了すれば、ゾーン定義重複がないことを保証します。

5. **`bind_serial` の更新**: テンプレート生成時に シリアルが自動更新されるため, 複数回実行しても問題ありません。

テンプレートは `templates/` 配下にあり, 環境に合わせて `named.conf.*` や `db.*` を生成します。特に `named.conf.zones.j2` では `grant ddns-clients zonesub` によりサブゾーン単位の Dynamic DNS を許可します。`bind_serial` を事前に指定すると SOA シリアルを固定できます。

## ロール実行方法

```bash
make run_dns_server
```

または,

```bash
ansible-playbook -i inventory/hosts server.yml --tags dns-server
```

対象プレイブックでこのロールが含まれていればタグ省略でも適用されます。Zone 更新のみ再適用したい場合は `--tags dns-server -l <hostname>` で対象ホストを絞り, 必要に応じて `--skip-tags config-firewall` などを併用してください。

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
