# kea-dhcp ロール

このロールは Kea DHCPv4 サーバーをインストールし, Jinja2 テンプレートで `/etc/kea/kea-dhcp4.conf` を生成してサービスを有効化します。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Dynamic Host Configuration Protocol | DHCP | ネットワーク上のコンピュータに IP アドレスやサブネットマスク, デフォルトゲートウェイ, DNS サーバーなどのネットワーク設定を自動的に割り当てるプロトコル。 |
| Domain Name System | DNS | ドメイン名と IP アドレスを対応付ける分散型名前解決システム。人間が読みやすいドメイン名をコンピュータが扱える IP アドレスに変換する。 |
| Classless Inter-Domain Routing | CIDR | IP アドレスとネットワークプレフィックス長を組み合わせた表記法 (例: 192.168.1.0/24)。柔軟なネットワーク分割を可能にする。 |
| Internet Protocol version 4 | IPv4 | 32 ビットアドレス空間を持つインターネットプロトコル。現在最も広く使用されているバージョン。 |
| Internet Protocol version 6 | IPv6 | 128 ビットアドレス空間を持つ次世代インターネットプロトコル。IPv4 アドレス枯渇問題を解決する。 |
| Network Interface Card | NIC | コンピュータをネットワークに接続するための物理的または仮想的なインターフェース。イーサネットカードや無線 LAN アダプタなど。 |
| User Identifier | UID | Unix/Linux システムでユーザを一意に識別するための数値。ファイル所有者やプロセス実行者の特定に使用される。 |
| Group Identifier | GID | Unix/Linux システムでグループを一意に識別するための数値。ファイルのグループ所有権やアクセス制御に使用される。 |
| Jinja2 | - | Python で広く使用されるテンプレートエンジン。変数展開, 条件分岐, ループ処理などを備え, Ansible でも設定ファイル生成に使用される。 |
| User Datagram Protocol | UDP | インターネットプロトコルスイートを構成するトランスポート層プロトコル。TCP と異なり, 接続確立なしでデータグラムを送受信する。DHCP はこのプロトコルを使用する。 |
| JavaScript Object Notation | JSON | 人間が読みやすいテキスト形式のデータ交換フォーマット。キーと値のペアで構成され, 設定ファイルやAPI レスポンスに広く使用される。 |
| Comma-Separated Values | CSV | テーブル形式のデータを表現するテキスト形式。カンマで区切られたカラムと改行で区切られた行で構成される。リースデータベースもこの形式で管理できる。 |
| Secure Shell | SSH | リモートコンピュータへの安全なログインと通信を可能にするプロトコル。ネットワーク接続を暗号化することで, ユーザ認証と通信内容の機密性を確保する。 |
| sudo | - | 別のユーザ (通常は root) の権限で指定されたコマンドを実行することを可能にする Unix 系システムのプログラム。管理者以外のユーザが管理作業を行うときに使用される。 |
| Ansible | - | インフラストラクチャの構成管理と自動化を行うオープンソースツール。YAML 形式のプレイブックでシステム構成を記述し, SSH を使用して複数のリモートホストに対して冪等な変更を実行できる。 |
| netplan | - | Ubuntu および Debian ベースのシステムで使用されるネットワーク設定ツール。YAML 形式の設定ファイルを読み込み, systemd-networkd または NetworkManager に設定を反映させる。 |
| dhclient | - | Unix/Linux システムで DHCP クライアント機能を提供するツール。`dhclient` コマンドでインターフェースに対して IP アドレスやネットワーク設定を DHCP サーバーに要求する。 |
| Operating System | OS | ハードウェア資源の管理とアプリケーション実行基盤を提供する基本ソフトウェア。 |
| Red Hat Enterprise Linux | RHEL | Red Hat 社が提供する Linux ディストリビューション。RHEL9 はそのメジャーバージョン 9 を指す。 |
| systemctl | - | systemd を使用する Linux システムでサービスやシステムの状態を管理するコマンド。サービスの起動, 停止, 再起動, 状態確認などを行う。 |
| Process Identifier | PID | Unix/Linux システムで各プロセスを一意に識別するための数値。システムがプロセスを追跡, 管理するために使用する。 |
| Media Access Control アドレス | MAC アドレス | ネットワーク機器の識別子。 |
| リース | - | DHCP サーバーがクライアントに IP アドレスを一時的に貸し出す仕組み。有効期限が設定され, 期限切れ後は回収されて再利用される。 |
| バインド | - | ネットワークプログラムが特定のネットワークインターフェースやポート番号に接続して通信可能な状態にすること。サーバーがクライアントからの接続を待ち受ける際に使用する。 |
| サブネット | - | 大きなネットワークを複数の小さなネットワークに分割したもの。ネットワークを効率的に管理し, トラフィックを制御するために使用される。 |
| ゲートウェイ | - | 異なるネットワーク間でデータを中継する機器またはそのアドレス。ローカルネットワークから外部ネットワークへの出口となる。 |
| Yet Another Markup Language | YAML | 設定ファイル形式。 |
| systemd-resolved | - | systemd の一部として提供される DNS リゾルバサービス。ローカル DNS キャッシュと名前解決機能を提供し, ネットワーク設定を統合的に管理する。 |
| resolvectl | - | systemd-resolved を制御するコマンドラインツール。DNS サーバーの設定確認, 名前解決のテスト, 統計情報の取得などを行う。 |
| Kea | - | ISC (Internet Systems Consortium) が開発する高性能でモジュラーな DHCP サーバーソフトウェア。ISC DHCP の後継として設計され, JSON 形式の設定ファイルを使用する。 |
| Transmission Control Protocol | TCP | インターネットプロトコルスイートを構成するトランスポート層プロトコル。UDP と異なり, 接続確立, 信頼性の高いデータ転送, 順序保証を提供する。 |
| systemd | - | Linux の初期化とサービス管理を行う仕組み。 |
| ログローテーション | - | ログファイルが肥大化することを防ぐため, 定期的に古いログファイルをアーカイブし, 新しいログファイルを作成する仕組み。ディスク容量の管理とログの保守性向上に役立つ。 |
| 冪等性 | - | 同じ操作を何度実行しても結果が変わらない性質。Ansible では, プレイブックを複数回実行しても同じ最終状態になることを保証する重要な特性。 |
| プレイブック | - | Ansible で使用される YAML 形式の設定ファイル。複数のタスクやロールを組み合わせて, システムの構成や操作手順を定義する。 |
| systemd-networkd | - | systemd の一部として提供されるネットワーク管理デーモン。ネットワークインターフェースの設定, ルーティング, DHCP クライアント機能などを提供する。 |
| NetworkManager | - | Linux デスクトップ環境で広く使用されるネットワーク管理サービス。有線, 無線, VPN などの接続を自動的に管理し, GUI での設定変更を可能にする。 |

## 前提条件

本ロールは以下の前提条件を満たす環境での使用を想定しています。

- **対象 OS**: Debian/Ubuntu 系 (Ubuntu 24.04 を想定), RHEL9 系 (AlmaLinux 9.6 等を想定)
- **Ansible**: Ansible 2.15 以降
- **リモートホストへのアクセス**: SSH 接続確立済み
- **管理者権限**: sudo 権限が利用可能
- **管理ネットワークの設定済み**: `gpm_mgmt_*` 変数または個別の `kea_*` 変数が定義されていること
- **DNS 設定済み**: `dns_server_ipv4_address` および `dns_domain` 変数が定義されていること

## 主要変数

本ロールで使用する主要な変数を以下のカテゴリ別に説明します。

### 基本設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `kea_dhcp_interface` | `{{ gpm_mgmt_nic \| default(mgmt_nic, true) }}` | Kea がバインドするインターフェース名。管理 NIC が未指定の場合は `mgmt_nic` を使用。 |
| `kea_dhcp_config_file` | `/etc/kea/kea-dhcp4.conf` | 生成する設定ファイルの配置先。 |

### タイマー設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `kea_reclaim_timer_wait_time` | `10` | リース回収確認周期 (秒)。 |
| `kea_flush_reclaimed_timer_wait_time` | `25` | 回収済みリースのフラッシュ周期 (秒)。 |
| `kea_hold_reclaimed_time` | `3600` | 回収済みリースの保持期間 (秒)。 |
| `kea_max_reclaim_leases` | `100` | 回収処理 1 回あたりの最大リース数。 |
| `kea_max_reclaim_time` | `250` | 回収処理の最大実行時間 (ミリ秒)。 |
| `kea_unwarned_reclaim_cycles` | `5` | 警告なしで許容する連続回収サイクル数。 |
| `kea_renew_timer_wait_time` | `600` | クライアントのリース更新開始までの時間 (秒)。 |
| `kea_rebind_timer_wait_time` | `1800` | リバインド開始までの時間 (秒)。 |
| `kea_valid_lifetime` | `14400` | リース有効期限 (秒)。 |

### ネットワーク設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `kea_dns_servers` | `["{{dns_server_ipv4_address}}"]` | DHCP で配布する DNS サーバー一覧。 |
| `kea_domain_name` | `{{ dns_domain }}` | 配布するドメイン名。 |
| `kea_domain_search` | `["{{ dns_domain }}"]` | サーチドメインリスト。 |
| `kea_subnet` | `{{ gpm_mgmt_ipv4_network_cidr}}` | DHCP を提供するサブネット (CIDR)。 |
| `kea_pool` | `{{ gpm_mgmt_ipv4_prefix }}.100 - {{ gpm_mgmt_ipv4_prefix }}.254` | アドレスプール範囲。 |
| `kea_gateway` | `{{ gpm_mgmt_ipv4_network_gateway }}` | デフォルトゲートウェイ。 |

### ログ設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `kea_dhcp_log_file` | `/var/log/kea/kea-dhcp4.log` | Kea ログファイル出力先。 |
| `kea_dhcp_log_maxsize` | `2048000` | ログローテート前の最大サイズ (バイト)。 |
| `kea_dhcp_log_maxver` | `4` | ログローテート世代数。 |

### データベース設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `kea_lease_db_type` | `memfile` | リース DB 種別 (`memfile` / `mysql` / `pgsql`)。 |
| `kea_lease_db_name` | OS 依存 | リース DB パス。Debian 系: `/var/lib/kea/kea-leases4.csv`, RHEL 系: `/var/lib/kea/kea-dhcp4.leases` (`vars/cross-distro.yml`で切替)。 |

### その他の関連変数 (OS 依存)

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `kea_dhcp4_server_packages` | OS 依存 | インストールする Kea パッケージ。Debian 系: `kea-dhcp4-server`, RHEL 系: `kea-dhcp4`。 |
| `kea_dhcp4_server_service` | OS 依存 | 有効化/起動するサービス名。Debian 系: `kea-dhcp4-server`, RHEL 系: `kea-dhcp4`。 |

## ロール内の動作

## 実行フロー

本ロールは以下の 6 ステップで実行されます。

共通のネットワーク/パッケージ変数は [vars/cross-distro.yml](vars/cross-distro.yml) および [vars/all-config.yml](vars/all-config.yml) を参照します。

1. **load-params.yml**: OS ごとのパッケージ名, クロスディストロ変数, 共通ネットワーク設定, Kubernetes API 広告アドレス設定を読み込みます。
   - [vars/packages-ubuntu.yml](../../vars/packages-ubuntu.yml) (Ubuntu の場合)
   - [vars/packages-rhel.yml](../../vars/packages-rhel.yml) (RHEL の場合)
   - [vars/cross-distro.yml](../../vars/cross-distro.yml)
   - [vars/all-config.yml](../../vars/all-config.yml)
   - [vars/k8s-api-address.yml](../../vars/k8s-api-address.yml)

2. **package.yml**: `kea_dhcp4_server_packages` をインストールします。 OS による差異は変数で吸収されます。

3. **directory.yml**: 現在はプレースホルダです (将来の拡張用)。

4. **user_group.yml**: 現在はプレースホルダです (将来の拡張用)。

5. **service.yml**: 現在はプレースホルダです (将来の拡張用)。

6. **config.yml**: 以下の処理を実施します。
   - [templates/kea-dhcp4.conf.j2](templates/kea-dhcp4.conf.j2) を `/etc/kea/kea-dhcp4.conf` に展開します。
   - 設定ファイルの変更時は `restart_kea_dhcp4_server` ハンドラを通知します。
   - `kea_dhcp4_server_service` を `enabled: true` で有効化し, `state: started` で起動します。

## 主な処理

本ロールの主な処理は以下の通りです。

- **Kea パッケージのインストール**: OS に応じた適切なパッケージ (`kea-dhcp4-server` / `kea-dhcp4`) をインストール。
- **設定ファイルの生成**: [templates/kea-dhcp4.conf.j2](templates/kea-dhcp4.conf.j2) から `/etc/kea/kea-dhcp4.conf` を生成。
- **インターフェース設定**: `kea_dhcp_interface` で指定されたインターフェースにバインド。
- **サブネット/プール設定**: IPv4 サブネット (`kea_subnet`), アドレスプール (`kea_pool`), デフォルトゲートウェイ (`kea_gateway`) を設定。
- **DHCP オプション設定**: DNS サーバー (`kea_dns_servers`), ドメイン名 (`kea_domain_name`), ドメインサーチ (`kea_domain_search`) を配布。
- **リース回収設定**: 期限切れリースの再利用メカニズム (`expired-leases-processing`) を設定。
- **ログ設定**: ローテーション付きログファイル出力 (`kea_dhcp_log_file`, `kea_dhcp_log_maxsize`, `kea_dhcp_log_maxver`) を設定。
- **サービス管理**: サービスの有効化, 起動, 及び設定変更時の自動再起動。

## テンプレート / ファイル

本ロールでは以下のテンプレートファイルを使用します。

| テンプレート名 | 出力先 | 説明 |
| --- | --- | --- |
| `templates/kea-dhcp4.conf.j2` | `/etc/kea/kea-dhcp4.conf` | Kea DHCPv4 メイン設定ファイル。インターフェース, サブネット, アドレスプール, DHCP オプション, リース回収設定, ログ設定を含む JSON 形式の設定ファイル。 |

## ハンドラ

本ロールは以下のハンドラを使用します。

| ハンドラ名 | 説明 | トリガー条件 |
| --- | --- | --- |
| `restart_kea_dhcp4_server` | Kea DHCPv4 サービスを再起動します。Debian/Ubuntu系では `systemctl restart kea-dhcp4-server`, RHEL系では `systemctl restart kea-dhcp4` で実行されます。 | `/etc/kea/kea-dhcp4.conf` が変更されたとき。 |

## OS 差異

本ロールが対応する異なるオペレーティングシステム間の差異を以下に示します。

| 項目 | Debian/Ubuntu 系 (Ubuntu 24.04) | RHEL 系 (AlmaLinux 9.6 等) |
| --- | --- | --- |
| ロールパッケージ名 | `kea-dhcp4-server` | `kea-dhcp4` |
| サービス名 | `kea-dhcp4-server` | `kea-dhcp4` |
| リース DB パス (既定) | `/var/lib/kea/kea-leases4.csv` | `/var/lib/kea/kea-dhcp4.leases` |
| 設定ファイルパス | `/etc/kea/kea-dhcp4.conf` | `/etc/kea/kea-dhcp4.conf` |
| ログファイルパス | `/var/log/kea/kea-dhcp4.log` | `/var/log/kea/kea-dhcp4.log` |

## 実行方法

```bash
make run_kea_dhcp
```

または,

```bash
# site.yml を実行
ansible-playbook -i inventory/hosts site.yml

# 特定ホストのみ対象
ansible-playbook -i inventory/hosts site.yml -l dhcp-server.local

# kea-dhcp ロールのみ実行
ansible-playbook -i inventory/hosts site.yml --tags kea-dhcp
```

注意: 管理ネットワークの CIDR/ゲートウェイ/DNS (`gpm_mgmt_*`, `dns_*`) を [vars/all-config.yml](vars/all-config.yml) などで事前に定義してください。

## 検証

本ロール実行後, 以下の手順で正常な動作を確認できます。

### 前提条件

- ロール実行が完了していること
- DHCPクライアントとなるテストノードを用意できること
- DHCPサーバノードにSSHアクセス可能であること

### 検証ステップ

#### 1. サービス状態の確認

**実施ノード**: DHCPサーバノード

**コマンド** (Debian/Ubuntu 系の場合):
```bash
sudo systemctl status kea-dhcp4-server
```

**コマンド** (RHEL 系の場合):
```bash
sudo systemctl status kea-dhcp4
```

**期待される出力例**:
```
● kea-dhcp4.service - Kea DHCPv4 Server
     Loaded: loaded (/usr/lib/systemd/system/kea-dhcp4.service; enabled; preset: enabled)
     Active: active (running) since Sat 2026-03-07 13:45:23 JST; 5h 45m ago
   Main PID: 260959 (kea-dhcp4)
      Tasks: 6 (limit: 4575)
     Memory: 18.2M
        CPU: 1min 34.562s
     CGroup: /system.slice/kea-dhcp4.service
             └─260959 /usr/sbin/kea-dhcp4 -c /etc/kea/kea-dhcp4.conf

Mar 07 06:31:43 router.local kea-dhcp4[260959]: INFO  [kea-dhcp4.leases] DHCP4_LEASE_ALLOC ...
```

**確認ポイント**:
- `Loaded` 行で `enabled` が表示されている (enabled; preset: enabled)
- `Active` 行で `active (running)` と表示されている
- `Main PID` に Kea プロセスの PID (260959 等) が表示されている
- `/usr/sbin/kea-dhcp4 -c /etc/kea/kea-dhcp4.conf` コマンドで実行されている
- エラーメッセージがない

#### 2. 設定ファイルの確認

**実施ノード**: DHCPサーバノード

**コマンド**:
```bash
sudo cat /etc/kea/kea-dhcp4.conf | head -40
```

**期待される出力例**:
```json
#
#  -*- coding:utf-8 mode:bash -*-
# This file is generated by ansible.
# last update: 2026-03-01 15:19:44 JST

#
# kea-dhcp4 configuration
# 参考) https://www.server-world.info/query?os=Ubuntu_24.04&p=kea&f=1
{
"Dhcp4": {
    "interfaces-config": {
        # listenするインターフェースを指定
        "interfaces": [ "ens192" ]
    },
    # 期限切れリースの各設定
    "expired-leases-processing": {
        "reclaim-timer-wait-time": 10,
        "flush-reclaimed-timer-wait-time": 25,
        "hold-reclaimed-time": 3600,
        "max-reclaim-leases": 100,
        "max-reclaim-time": 250,
        "unwarned-reclaim-cycles": 5
    },
    # 更新プロセスを開始する間隔 (秒)
    "renew-timer": 600,
    # 再バインドプロセスを開始する間隔 (秒)
    "rebind-timer": 1800,
    # リースの有効期間 (秒)
    "valid-lifetime": 14400,
    "option-data": [
```

**確認ポイント**:
- `"interfaces-config"` にバインドするインターフェース (`ens192` など) が設定されている
- `"expired-leases-processing"` で回収設定が記載されている
- `"renew-timer"`, `"rebind-timer"`, `"valid-lifetime"` が設定されている
- `"option-data"` セクションが開始されている (DNS等はその下に続く)
- JSON 構文が正しい (ダブルクォート, カッコの対応等)
- Ansible により生成されたコメントが記載されている

#### 3. インターフェースバインド確認

**実施ノード**: DHCPサーバノード

**コマンド**:
```bash
sudo ss -ulnp | grep kea
```

**期待される出力例**:
```
UNCONN     0      0      192.168.30.10:67         0.0.0.0:*    users:(("kea-dhcp4",pid=260959,fd=12))
```

**確認ポイント**:
- `UNCONN` (UDP接続,リッスン中) の状態
- UDP ポート `67` でバインドされている (`192.168.30.10:67`)
- プロセス名が `kea-dhcp4` である
- PID が表示されている (260959)
- サーバーがすべてのインターフェース (`0.0.0.0`) でリッスンしているか, または特定インターフェース (192.168.30.10) でバインドされている

#### 4. DHCP リース動作確認

**実施ノード**: DHCPクライアントノード

**コマンド**:
```bash
# Ubuntu/Debian の場合
sudo dhclient -v <interface>

# または (netplan を使用している場合)
sudo netplan apply

# 割り当てられたアドレスを確認
ip addr show <interface>
```

**期待される出力例**:
```
3: ens192: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 32:ff:36:15:d5:ea brd ff:ff:ff:ff:ff:ff
    inet 192.168.30.114/24 brd 192.168.30.255 scope global dynamic noprefixroute ens192
       valid_lft 13867sec preferred_lft 13867sec
```

**確認ポイント**:
- インターフェース状態が `UP` に変わっている
- **inet 行** に IPv4 アドレスが割り当たっている (192.168.30.114)
- アドレスが `kea_pool` 範囲内である (192.168.30.100 - 192.168.30.254)
- ネットマスクが正しい (/24 = kea_subnet の 192.168.30.0/24)
- `dynamic` フラグが設定されている (DHCP で動的割り当て)
- `valid_lft` (有効期限) が秒単位で表示されている (13867 秒 ≈ 14400 秒のカウントダウン)
- MAC アドレスがクライアント側と一致している (32:ff:36:15:d5:ea)

#### 5. DHCP オプション配布確認

**実施ノード**: DHCPクライアントノード

**コマンド**:
```bash
# DNS 設定の詳細確認 (systemd-resolved を使用している場合)
resolvectl status

# または従来の resolv.conf を確認
cat /etc/resolv.conf

# ルーティング設定を確認
ip route show
```

**期待される出力例**:
```
# resolvectl status の出力
Link 3 (ens192)
    Current Scopes: DNS
         Protocols: +DefaultRoute -LLMNR -mDNS -DNSOverTLS DNSSEC=no/unsupported
Current DNS Server: 192.168.20.11
       DNS Servers: 192.168.20.11 fd69:6684:61a:1::11 2606:4700:4700::1111
        DNS Domain: elliptic-curve.net

# ip route show の出力
default via 192.168.30.10 dev ens192 proto dhcp src 192.168.30.114 metric 101
192.168.30.0/24 dev ens192 proto kernel scope link src 192.168.30.114 metric 101
```

**確認ポイント**:
- **DNS Servers** (dnssrv1, dnssrv2 等) が配布した DNS サーバーと一致している (`kea_dns_servers` で指定した値)
- **DNS Domain** が配布したドメイン名と一致している (`kea_domain_name` で指定した値)
- **default via** の行で指定した `kea_gateway` (192.168.30.10) に向かっていること
- ルーティングエントリが `proto dhcp` で記載されている (DHCP により配布されたことを示す)
- ソース IP が割り当たられたアドレス (192.168.30.114) と一致している
- サブネット経路 (192.168.30.0/24) が正常に存在している

#### 6. ログ出力確認

**実施ノード**: DHCPサーバノード

**コマンド**:
```bash
sudo tail -20 /var/log/kea/kea-dhcp4.log
```

**期待される出力例**:
```
2026-03-07 06:31:43.751 INFO  [kea-dhcp4.leases/260959.140637152286400] DHCP4_LEASE_ALLOC [hwtype=1 32:ff:36:15:d5:ea], cid=[01:32:ff:36:15:d5:ea], tid=0x2109a5b: lease 192.168.30.114 has been allocated for 14400 seconds
2026-03-07 06:41:43.749 INFO  [kea-dhcp4.leases/260959.140637143893696] DHCP4_LEASE_ALLOC [hwtype=1 32:ff:36:15:d5:ea], cid=[01:32:ff:36:15:d5:ea], tid=0xdf1902d8: lease 192.168.30.114 has been allocated for 14400 seconds
2026-03-07 06:51:43.748 INFO  [kea-dhcp4.leases/260959.140637152286400] DHCP4_LEASE_ALLOC [hwtype=1 32:ff:36:15:d5:ea], cid=[01:32:ff:36:15:d5:ea], tid=0xe4066ad5: lease 192.168.30.114 has been allocated for 14400 seconds
2026-03-07 07:08:08.168 INFO  [kea-dhcp4.dhcpsrv/260959.140637216340416] DHCPSRV_MEMFILE_LFC_START starting Lease File Cleanup
2026-03-07 07:08:08.168 INFO  [kea-dhcp4.dhcpsrv/260959.140637216340416] DHCPSRV_MEMFILE_LFC_EXECUTE executing Lease File Cleanup using: /usr/sbin/kea-lfc -4 -x /var/lib/kea/kea-leases4.csv.2 ...
```

**確認ポイント**:
- `DHCP4_LEASE_ALLOC` メッセージでリース割り当てが記録されている (`lease 192.168.30.114 has been allocated for 14400 seconds`)
- リース割り当て時刻が正常に記録されている (例: `2026-03-07 06:31:43.751`)
- クライアントの MAC アドレス (`hwtype=1 32:ff:36:15:d5:ea`) が記録されている
- リース期間 (14400 秒) が `kea_valid_lifetime` と一致している
- `DHCPSRV_MEMFILE_LFC_*` メッセージで定期的なリース回収処理が実行されている
- エラーメッセージや警告がない (`ERROR` や `WARN` がない)

#### 7. リースデータベース確認

**実施ノード**: DHCPサーバノード

**コマンド** (Debian/Ubuntu 系):
```bash
sudo cat /var/lib/kea/kea-leases4.csv | head -5
```

**コマンド** (RHEL 系の場合):
```bash
sudo cat /var/lib/kea/kea-dhcp4.leases | head -5
```

**期待される出力例**:
```csv
address,hwaddr,client_id,valid_lifetime,expire,subnet_id,fqdn_fwd,fqdn_rev,hostname,state,user_context,pool_id
192.168.30.114,32:ff:36:15:d5:ea,01:32:ff:36:15:d5:ea,14400,1772845903,1,0,0,vmlinux3,0,,0
192.168.30.114,32:ff:36:15:d5:ea,01:32:ff:36:15:d5:ea,14400,1772846503,1,0,0,vmlinux3,0,,0
192.168.30.114,32:ff:36:15:d5:ea,01:32:ff:36:15:d5:ea,14400,1772847103,1,0,0,vmlinux3,0,,0
```

**確認ポイント**:
- ファイル形式が CSV (カンマ区切り) である (Debian/Ubuntu 系) またはテキスト形式 (RHEL 系)
- 1 行目に列名が記載されている (address, hwaddr, client_id, valid_lifetime, expire 等) (CSV 形式の場合)
- 2 行目以降にリース情報が記録されている
- **address 列/フィールド** に割り当たったクライアント IP (192.168.30.114) が記録されている
- **hwaddr 列/フィールド** にクライアントの MAC アドレス (32:ff:36:15:d5:ea) が記録されている
- **client_id 列/フィールド** に DHCP Client ID (01:32:ff:36:15:d5:ea) が記録されている
- **valid_lifetime 値** がリース有効期限秒数 (14400 = `kea_valid_lifetime`) として記録されている
- **expire 値** がリース期限の UNIX タイムスタンプとして記録されている (1772845903 等)
- **hostname 情報** (利用可能な場合) がクライアント名として記録されている (vmlinux3 等)
- 複数クライアントのリースレコードが累積されて記録されている

## 設定例

### group_vars/all での共通設定

```yaml
# Kea DHCP 設定
# 仮想化基盤内部管理ネットワークのインターフェース名に
# 合わせて変更してください
kea_dhcp_interface: "ens192"
# DHCPv4によるアドレス配布対象ネットワークアドレスのCIDR
kea_subnet: "192.168.100.0/24"
# DHCPv4によるアドレス配布範囲
kea_pool: "192.168.100.100 - 192.168.100.200"
# ゲートウェイアドレス
kea_gateway: "192.168.100.1"
# DNSサーバのアドレス
kea_dns_servers:
  - "192.168.100.10"
  - "8.8.8.8"
# ドメイン名
kea_domain_name: "example.local"
# ドメインサーチリスト
kea_domain_search:
  - "example.local"

# タイマー設定 (デフォルト値から変更する場合)
# リース有効期限秒数 ( 7200秒 = 2 時間 )
kea_valid_lifetime: 7200
# クライアントのリース更新までの時間 ( 3600秒 = 1 時間 )
kea_renew_timer_wait_time: 3600
```

### host_vars/dhcp-server.local での個別設定

```yaml
# Kea DHCP 設定 (特定サーバー向け)
kea_dhcp_interface: "ens192"
# DHCPv4によるアドレス配布対象ネットワークアドレスのCIDR
kea_subnet: "10.0.0.0/24"
# DHCPv4によるアドレス配布範囲
kea_pool: "10.0.0.50 - 10.0.0.150"
# ゲートウェイアドレス
kea_gateway: "10.0.0.1"
# DNSサーバのアドレス
kea_dns_servers:
  - "10.0.0.2"

# ログ設定
# 最大ログファイルサイズ (単位:バイト, 10485760 バイト = 10 MB )
kea_dhcp_log_maxsize: 10485760
# ログファイル保持世代数 ( 10 世代 )
kea_dhcp_log_maxver: 10
```

## 補足

運用時に注意すべき事項を以下に示します。

- **リース回収メカニズム**: Kea は期限切れリースを自動的に回収し再利用します。`kea_reclaim_timer_wait_time` で回収周期を調整できます。
- **ログローテーション**: Kea は内部ログローテーション機能を持ち, `kea_dhcp_log_maxsize` と `kea_dhcp_log_maxver` で制御されます。logrotate 等の外部ツールとの併用は推奨されません。
- **リースデータベースのバックアップ**: memfile 形式の場合, `kea_lease_db_name` で指定されたファイルを定期的にバックアップすることを推奨します。
- **設定ファイルの検証**: 設定変更前に `kea-dhcp4 -t /etc/kea/kea-dhcp4.conf` で構文検証を行うことができます。
- **サービス再起動のタイミング**: 設定ファイル変更時はハンドラが自動的にサービスを再起動しますが, アクティブなリースには影響しません。
- **マルチサブネット構成**: 本ロールは単一サブネット構成を想定しています。複数サブネットを扱う場合はテンプレートのカスタマイズが必要です。

## 参考リンク

- [Kea Administrator Reference Manual](https://kea.readthedocs.io/)
- [Kea DHCPv4 Configuration](https://kea.readthedocs.io/en/latest/arm/dhcp4-srv.html)
- [ISC Kea GitHub Repository](https://github.com/isc-projects/kea)
