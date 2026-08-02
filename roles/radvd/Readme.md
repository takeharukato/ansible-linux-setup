# radvd ロール

本ロールは Router Advertisement Daemon (radvd) を導入し, 管理ネットワーク向けに IPv6 ルーター広告 (Router Advertisement - RA) を配布します。

## 目次

- [用語](#用語)
- [概要](#概要)
- [前提条件](#前提条件)
- [実行方法](#実行方法)
- [主要変数](#主要変数)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
- [実行フロー](#実行フロー)
- [検証ポイント](#検証ポイント)
- [注意事項](#注意事項)
- [参考資料](#参考資料)

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| ユーザ | - | 機能を利用する人, 又は識別された利用主体。 |
| ツール | - | 特定作業を実行するための機能や道具。 |
| リソース | - | 処理に必要な計算機資源やデータ。 |
| クラスタ | - | 複数の機器を連携させて一体運用する構成。 |
| ディストリビューション | - | 基本ソフトウェアと関連部品をまとめた配布形態。 |
| コンテナイメージ | - | コンテナ実行に必要な内容をまとめた保存形式。 |
| プログラム | - | 計算機に処理をさせるための命令列。 |
| コミュニティ | - | 共通目的のもとで継続的に活動する利用者集団。 |
| プラグイン | - | 既存機能へ追加機能を組み込むための拡張部品。 |
| サービスアカウント | - | 自動処理向けに用意する利用主体の識別情報。 |
| コンテナランタイム | - | コンテナを起動, 停止, 管理する実行基盤。 |
| リクエスト | - | 処理実行や情報取得を要求する操作。 |
| コントローラ | - | 対象状態を監視し, 期待状態へ調整する制御機能。 |
| メタデータ | - | 対象データの属性や説明を示す付加情報。 |
| バックエンド | - | 利用者画面の背後で処理を実行する側。 |
| ストレージ | - | データを保存する仕組み。 |
| インストール | - | ソフトウェアを導入して利用可能にする作業。 |
| マシン | - | 処理を実行する計算機。 |
| プロビジョニング | - | 利用開始に必要な設定や資源を準備する作業。 |
| ルーティング | - | 宛先までの経路を選択して転送する処理。 |
| オブジェクト | - | ひとかたまりとして扱うデータ単位。 |
| エージェント | - | 指示に従って処理を代行する構成要素。 |
| ストア | - | データや成果物を保存する場所。 |
| ジャーナル | - | 時系列の記録を保持する仕組み。 |
| アカウント | - | 利用者や処理主体を識別する登録情報。 |
| エンドポイント | - | 通信の接続先を表す識別点。 |
| パターン | - | 繰り返し現れる構造や記述形式。 |
| パケット | - | ネットワークで転送するデータ単位。 |
| カーネル | - | 基本ソフトウェアの中核機能。 |
| シェル | - | コマンド入力で計算機を操作する仕組み。 |
| Playbook | - | 自動化処理の実行手順を記述したファイル。 |
| Canonical | - | Ubuntu を提供する組織名。 |
| Key-Value | - | キーと値の組で情報を表す方式。 |
| IP | - | インターネットプロトコルの略称。 |
| SQL | - | データベースを操作するための記述言語。 |
| HTTP | - | WWW で情報をやり取りする通信手順。 |
| HTTPS | - | 通信内容を暗号化して WWW 通信を行う方式。 |
| RPM | - | RHEL 系で使用するパッケージ形式。 |
| VM | - | 物理機器上で動作する仮想的な計算機。 |
| localhost | - | 同一機器自身を指す名前。 |
| root | - | Unix 系システムの最上位権限を持つ管理者識別子。 |
| ソフトウェア | - | 情報処理システムで使用するプログラム, 手順, 規則及び関連文書の全体又は一部分。 |
| アプリケーション | - | 利用者の目的を実現するために動作するソフトウェア。 |
| パッケージ | - | ソフトウェア導入に必要なファイルをまとめた配布単位。 |
| リポジトリ | - | ソフトウェアや設定情報を保管し, 取得できるようにした管理場所。 |
| コマンド | - | 実行者が計算機へ処理を指示するための命令。 |
| ホスト | - | 管理対象として識別される個別の計算機。 |
| サーバ | - | 他の機器や利用者へ機能やデータを提供する計算機, 又はその役割。 |
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
| ネットワーク | - | 機器同士を接続してデータをやり取りする仕組み。 |
| プロトコル | - | 通信やデータ交換の手順を定めた取り決め。 |
| ディレクトリ | - | ファイルを階層的に整理するための入れ物。 |
| ログ | - | 処理の結果や状態を時系列で記録した情報。 |
| コード | - | 処理内容を記述した文字列。 |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウェア。 |
| Pod | - | Kubernetes でコンテナをまとめて管理する最小単位。 |
| Linux | - | 多くの機器で使われる, 基本ソフトウェアの系統。 |
| Debian | - | コミュニティ主導で開発される Linux ディストリビューション。 |
| Ubuntu | - | Canonical が提供する Debian 系の Linux ディストリビューション。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| API | - | アプリケーション同士がやり取りする方法を定めた仕様。 |
| URL | - | WWW 上の資源の場所を示す文字列。 |
| Router Advertisement | RA | IPv6 で経路情報を通知する仕組み。 |
| Stateless Address Autoconfiguration | SLAAC | IPv6 の自動設定方式。 |
| Recursive DNS Server | RDNSS | ルーター広告で配布されるDNSサーバアドレス情報 |
| DNS Search List | DNSSL | ルーター広告で配布されるDNS検索ドメインリスト |
| Internet Protocol version 6 | IPv6 | 128 ビットアドレス空間を持つ次世代インターネットプロトコル。IPv4 アドレス枯渇問題を解決します。 |
| Internet Control Message Protocol version 6 | ICMPv6 | IPv6ネットワークでの制御メッセージプロトコル, RA送信に使用 |
| Domain Name System | DNS | 名前と IP アドレスを対応付ける仕組み。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Network Interface | - | ホストがネットワークに接続するための物理的または仮想的なインターフェース, ens192やeth0などの名前で識別 |
| Prefix (IPv6) | - | IPv6アドレスのネットワーク部。記法: `2001:db8::/32` の`/32`がプレフィックス長 |
| Lifetime | - | IPv6アドレスやプレフィックスの有効期期間 ( 秒 ) 。有効期限(ValidLifetime)と推奨期限(PreferredLifetime)がある |
| Handler | - | 通知時に実行する再処理です。 |
| Template | - | 変数展開して出力する雛形ファイルです。 |
| Link-local Address | - | IPv6の自動割り当てアドレス。fe80::で始まる, ローカルネットワーク内でのみ有効 |
| Internet Protocol | IP | ネットワーク上で宛先を識別し, データを届けるための通信手順。 |
| Process Identifier | PID | 実行中の処理を識別する番号。 |
| Request for Comments | RFC | インターネット技術の仕様を公開する文書体系。 |
| Red Hat Enterprise Linux | RHEL | Red Hat 社が提供する商用 Linux ディストリビューション。 |
| Ansible Playbook | playbook | 自動化処理の実行手順を順序付きで記述したファイル。 |
| systemd | - | Linux システムの初期化とサービス管理を行う仕組み。 |
| IPv6 Link-Local Prefix | FE80 | 同一リンク内通信で使う IPv6 接頭辞。 |
| Layer 2 | L2 | 同一ネットワーク内で装置間転送を扱う通信層。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `cat` | - | ファイル内容を標準出力へ表示するコマンド。 |
| `getent` | - | システムの名前解決データベースを参照するコマンド。 |
| ipコマンド | - | ネットワーク設定や経路情報の確認, 変更を行うコマンド。 |
| `journalctl` | - | systemd ジャーナルのログを参照するコマンド。 |
| `make` | - | Makefile に定義された処理を実行するコマンド。 |
| `systemctl` | - | systemd 管理下のサービスを起動, 停止, 状態確認するコマンド。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
| サービス | - | 機能を利用者や他システムへ提供する仕組み。 |
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| ログイン | - | 利用者認証を行って利用を開始する操作。 |
| ローカルアドレス | - | 実行中ホスト上で利用するアドレス。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |

## 概要
このロールは Router Advertisement Daemon (radvd) を導入し, 管理ネットワーク向けに IPv6 ルーター広告 (Router Advertisement - RA) を配布します。Stateless Address Autoconfiguration (SLAAC) 用プレフィックスとデフォルトルート, RDNSS/DNSSL (DNS サーバ, サーチドメイン) 情報を RA で広告し, 設定ファイル `/etc/radvd.conf` から生成します。設定変更時は radvd を再起動します。

本ロールは, radvd に関する設定処理を実施します。

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

## 前提条件

このロールを実行する前に, 以下の前提条件を満たしていることを確認してください。

- **ホスト用途**: radvd はルータノード上で実行されることを想定しています。IPv6 通信を行うネットワークセグメントへの物理的な接続またはその代替が必要です。
- **IPv6 管理ネットワーク**: ロールで配布する IPv6 プレフィックス (`radvd_router_advertisement_prefix`) は事前に定義されている必要があります。通常は `vars/all-config.yml` や `host_vars/<hostname>` で `gpm_mgmt_ipv6_prefix`/`gpm_mgmt_ipv6_addr_prefix_len` として定義します。
- **ネットワークインターフェース**: `radvd_nic` パラメータに指定するネットワークインターフェース ( 例: `ens192`, `eth0` ) は対象ホストに存在する必要があります。
- **Ansible の権限**: ロール実行にはルート権限 ( `become: true` ) が必要です。パッケージ管理, 設定ファイル配置, サービス制御を行うため。

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

## テンプレートと生成ファイル

本ロールでは以下のテンプレート / ファイルを出力します:
主な展開先ホストは, 対象ホスト(既定) です。

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `radvd.conf.j2` | `{{ radvd_config_file_path }}` (既定: `{{ radvd_config_file_path }}`) | IPv6 Router Advertisement のプレフィックス, DNS 配布, 有効期限を定義する radvd 設定です。 |

## 実行フロー

このロールは以下の 6 つのステップで逐次処理をします。

1. **Load Params** (`tasks/load-params.yml`): `vars/cross-distro.yml` から OS 別パッケージ名, サービス名を読み込みます。
2. **Package** (`tasks/package.yml`): radvd パッケージをインストールします。既にインストール済みの場合はスキップします。
3. **Directory** (`tasks/directory.yml`): radvd の補助ディレクトリが必要な場合は作成します。 ( 現在のテンプレート実装では空 )
4. **User Group** (`tasks/user_group.yml`): radvd 実行ユーザー, グループの管理が必要な場合は設定します。 ( 現在のテンプレート実装では空 )
5. **Config** (`tasks/config.yml`): テンプレート [templates/radvd.conf.j2](templates/radvd.conf.j2) から設定ファイルを生成し, `/etc/radvd.conf` に配置します。ファイルが変更された場合, `restart_radvd` ハンドラを通知します。
6. **Service** (`tasks/service.yml`): ハンドラ [handlers/restart-radvd.yml](handlers/restart-radvd.yml) で radvd サービスを再起動し, `enabled: true` で起動時の自動起動を有効化します。

各ステップは **`radvd_nic` が定義されており, かつ対象ホストのインターフェース一覧に存在する場合にのみ実行**されます。

## 検証ポイント

実行者は以下の検証コマンドを実行し, 構文検査が成功することを確認します。

```bash
ansible-playbook -i inventory/hosts site.yml --syntax-check
```

期待結果: エラーが出力されず, syntax check が成功します。

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

## 注意事項

実行者は既存の実行順依存を崩さないことを確認した上で本ロールを実行します。

## OS 差異

radvd パッケージ, サービス名は OS によって異なります。`vars/cross-distro.yml` で以下のように定義されています。

| 項目 | Debian/Ubuntu | RHEL/CentOS | 説明 |
| --- | --- | --- | --- |
| パッケージ名 | `radvd` | `radvd` | 両 OS で共通 |
| サービス名 | `radvd` | `radvd` | 両 OS で共通 |
| 設定ファイルパス | `/etc/radvd.conf` | `/etc/radvd.conf` | 両 OS で共通 |

## 補足

### SLAAC と DHCPv6 の使い分け

このロールは SLAAC のみの設定です。`AdvManagedFlag` と `AdvOtherConfigFlag` は `off` に設定されており, クライアントは SLAAC でアドレスを自動設定します。DHCPv6 が必要な場合は, 別途 Kea などの DHCPv6 サーバを用意し, フラグを `on` に変更してください。

### デフォルトルートの配布制御

`AdvDefaultLifetime` で設定値を制御します。
- `AdvDefaultLifetime 0;` — デフォルトルートを配布しない。
- `AdvDefaultLifetime 300;` — デフォルトルータの有効期限を 300 秒に設定 ( 推奨: `MaxRtrAdvInterval` の 3 倍 ) 。

### トラブルシューティング

- **RA が受信されない**: radvd サービスが起動していること, およびインターフェースが正しくバインドされていることを確認。`systemctl status radvd` と `/etc/radvd.conf` の `interface` セクションを確認。
- **クライアント側にアドレスが付与されない**: SLAAC が有効化されていることを確認 ( `AdvAutonomous on;` ) 。クライアント側の IPv6 設定を確認 ( `ip -6 addr` ) 。
- **DNS が解決されない**: RDNSS/DNSSL がテンプレートに正しく展開されていることを確認 ( Step 2 ) 。クライアント側の `/etc/resolv.conf` または `systemd-resolved` を確認 ( Step 5 ) 。
## 参考資料

### 公式ドキュメント

- radvd: https://www.litech.org/radvd/

- [radvd - Router Advertisement Daemon](https://linux.die.net/man/8/radvd) — manページ ( 英語 ) 。
- [RFC 4861 - Neighbor Discovery for IP version 6 (IPv6)](https://tools.ietf.org/html/rfc4861) — ルーター広告の仕様 ( 英語 ) 。
- [RFC 6106 - IPv6 Router Advertisement Flags Option](https://tools.ietf.org/html/rfc6106) — RDNSS/DNSSL オプション仕様 ( 英語 ) 。
- [Debian/Ubuntu manページ: resolvconf](https://manpages.debian.org/resolvconf.5) — resolv.conf の設定方法 ( 英語 ) 。
- [systemd-resolved](https://www.freedesktop.org/wiki/Software/systemd/resolved/) — systemd によるDNS 管理 ( 英語 ) 。
