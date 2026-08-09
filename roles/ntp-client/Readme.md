# ntp-client ロール

本ロールは, Debian系およびRHEL系ホストでNTPクライアント設定を適用するロールです。

## 目次

- [ntp-client ロール](#ntp-client-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
    - [構成要素](#構成要素)
    - [ディレクトリ構成](#ディレクトリ構成)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
    - [Makefileを使用した実行](#makefileを使用した実行)
    - [直接 ansible-playbook で実行](#直接-ansible-playbook-で実行)
  - [主要変数](#主要変数)
    - [基本設定](#基本設定)
    - [パッケージ/サービス設定](#パッケージサービス設定)
    - [設定ファイルパス](#設定ファイルパス)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
    - [ハンドラ](#ハンドラ)
    - [OS差異](#os差異)
  - [検証ポイント](#検証ポイント)
    - [前提条件確認](#前提条件確認)
    - [検証ステップ](#検証ステップ)
      - [Step 1: 有効化サービスの相互排他確認](#step-1-有効化サービスの相互排他確認)
      - [Step 2: 設定ファイル反映確認](#step-2-設定ファイル反映確認)
      - [Step 3: 同期状態確認](#step-3-同期状態確認)
      - [Step 4: ログ確認](#step-4-ログ確認)
  - [トラブルシューティング](#トラブルシューティング)
  - [注意事項](#注意事項)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)


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
| Internet Protocol | IP | ネットワーク上で宛先を識別し, データを届けるための通信手順。 |
| Structured Query Language | SQL | データベースを操作するための記述言語。 |
| Hypertext Transfer Protocol | HTTP | World Wide Webで情報をやり取りする通信手順。 |
| Hypertext Transfer Protocol Secure | HTTPS | 通信内容を暗号化してWorld Wide Web通信を行う方式。 |
| RPM Package Manager | RPM | RPM形式パッケージの導入, 更新, 削除, 情報参照を行う仕組み。 |
| Virtual Machine | VM | 物理計算機上で動作する仮想的な計算機。 |
| localhost | - | 同一機器自身を指す名前。 |
| root | - | Unix 系システムの最上位権限を持つ管理者識別子。 |
| ソフトウェア | - | 情報処理システムで使用するプログラム, 手順, 規則及び関連文書の全体又は一部分。 |
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| アプリケーション | - | 利用者の目的を実現するために動作するソフトウェア。 |
| パッケージ | - | ソフトウェア導入に必要なファイルをまとめた配布単位。 |
| リポジトリ | - | ソフトウェアや設定情報を保管し, 取得できるようにした管理場所。 |
| コマンド | - | 実行者が計算機へ処理を指示するための命令。 |
| ホスト | - | 管理対象として識別される個別の計算機。 |
| サーバ | - | 他の機器や利用者へ機能やデータを提供する計算機, 又はその役割。 |
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
| ネットワーク | - | 機器同士を接続してデータをやり取りする仕組み。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
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
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| Network Time Protocol | NTP | 時刻同期の仕組み。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Red Hat Enterprise Linux | RHEL | Red Hatが提供する企業向けLinuxディストリビューション。 |
| Ansible | Ansible | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| Yet Another Markup Language | YAML | 設定ファイル形式です。 |
| Ansible Playbook | playbook | 自動化処理の実行手順を順序付きで記述したファイル。 |
| role | role | 特定の名前空間内で有効な権限の集合。 |
| template | template | 変数展開して出力する雛形ファイルです。 |
| handler | handler | 通知時に実行する再処理です。 |
| tag | tag | Ansibleで実行対象を絞るラベルです。 |
| systemd | - | Linux システムの初期化とサービス管理を行う仕組み。 |
| systemd-timesyncd | - | systemdに含まれる時刻同期クライアントサービスです。 |
| chrony | - | NTPクライアント/サーバ機能を提供する時刻同期ソフトウェアです。 |
| Simple Network Time Protocol | SNTP | NTPの簡易版プロトコルです。 |
| drop-in configuration | drop-in | 既存設定本体とは別ファイルで追加設定を適用する方式です。 |
| systemctl | - | systemd 管理下のサービスを起動, 停止, 状態確認するコマンド。 |
| journalctl | - | systemd ジャーナルのログを参照するコマンド。 |
| timedatectl | - | Linuxの時刻設定と同期状態を表示, 設定するコマンドです。 |
| chronyc | - | chronyの状態確認と制御を行うコマンドです。 |
| Internet Protocol version 4 | IPv4 | 32 ビットアドレス空間を持つインターネットプロトコル。現在最も広く使用されているバージョン。 |
| Internet Protocol version 6 | IPv6 | 128 ビットアドレス空間を持つ次世代インターネットプロトコル。IPv4 アドレス枯渇問題を解決します。 |
| Red Hat Enterprise Linux 9 | RHEL9 | Red Hat Enterprise Linux の第9系統版。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `grep` | - | テキストから条件に一致する行を抽出するコマンド。 |
| makeコマンド | make | Makefile に定義された処理を実行するコマンド。 |
| サービス | - | 機能を利用者や他システムへ提供する仕組み。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| ログイン | - | 利用者認証を行って利用を開始する操作。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |
## 概要
このロールは, Debian系およびRHEL系ホストでNTPクライアント設定を適用するロールです。`ntp_client_choice`により`chrony`と`systemd-timesyncd`を切り替え, OS差異は`vars/cross-distro.yml`で吸収します。`ntp_servers_list`はテンプレート処理で空要素と重複を除去して反映します。

### 構成要素

このロールは以下を構成します。

1. NTPクライアントパッケージの導入。
- Debian系では`ntp_client_choice`に応じて`chrony`または`systemd-timesyncd`を導入します。
- RHEL系では`chrony`を導入します。

2. NTPクライアント設定の反映。
- `systemd-timesyncd`選択時は`95-timesyncd.conf.j2`を配置します。
- `chrony`選択時は`99-chrony.conf.j2`をdrop-in設定として配置します。

3. サービス有効状態の反映。
- 選択した実装側サービスのみ有効化し, 非選択側サービスは無効化します。

### ディレクトリ構成

主要な設定対象は以下です。

```plaintext
/etc/systemd/timesyncd.conf.d/95-timesyncd.conf
/etc/chrony/chrony.conf (Debian系)
/etc/chrony.conf (RHEL系)
/etc/chrony/conf.d/99-custom.conf (Debian系)
/etc/chrony.d/99-custom.conf (RHEL系)
```

## 前提条件

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- Ansible 2.15 以降, ansibleメタパッケージをディストリビューションから導入していることを想定
- 対象ノードで管理者権限が利用できること。
- `ntp_client_choice`が`chrony`または`systemd-timesyncd`であること。
- `ntp_servers_list`が時刻同期先として妥当な値で定義されていること。

## 実行方法

### Makefileを使用した実行

```bash
cd /path/to/ubuntu-setup/ansible
make run_ntp_client
```

### 直接 ansible-playbook で実行

```bash
# basic.yml をタグ指定で実行
ansible-playbook -i inventory/hosts basic.yml --tags "ntp-client"

# site.yml をタグ指定で実行
ansible-playbook -i inventory/hosts site.yml --tags "ntp-client"

# 対象ホストを限定して実行
ansible-playbook -i inventory/hosts site.yml --tags "ntp-client" -l <対象ホスト>
```

`devel.yml`, `k8s-ctrl-plane.yml`, `k8s-worker.yml`, `rancher.yml` でも同じ `--tags "ntp-client"` で再利用できます。

## 主要変数

### 基本設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `ntp_servers_list` | `[]` | NTPサーバの候補一覧です。テンプレートで空要素と重複を除去して反映します。 |
| `ntp_client_choice` | `chrony` | 使用するNTPクライアント実装です (`chrony` / `systemd-timesyncd`)。 |
| `ntp_client_is_chrony` | `{{ ntp_client_choice == 'chrony' }}` | `chrony`選択判定です。 |
| `ntp_client_is_systemd_timesyncd` | `{{ ntp_client_choice == 'systemd-timesyncd' }}` | `systemd-timesyncd`選択判定です。 |

### パッケージ/サービス設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `ntp_client_packages_debian` | `{{ ntp_client_is_chrony \| ternary(['chrony'], ['systemd-timesyncd']) }}` | Debian系で導入するパッケージ一覧です。 |
| `ntp_client_packages_rhel` | `['chrony']` | RHEL系で導入するパッケージ一覧です。 |
| `ntp_client_packages` | Debian系: `['chrony']` または `['systemd-timesyncd']`, RHEL系: `['chrony']` | 実際に導入するパッケージ一覧です。 |
| `ntp_client_chrony_service_debian` | `chrony` | Debian系のchronyサービス名です。 |
| `ntp_client_chrony_service_rhel` | `chronyd` | RHEL系のchronyサービス名です。 |
| `ntp_client_chrony_service` | Debian系: `chrony`, RHEL系: `chronyd` | 実際に使用するchronyサービス名です。 |
| `ntp_client_systemd_timesyncd_service` | `systemd-timesyncd` | systemd-timesyncdサービス名です。 |

### 設定ファイルパス

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `ntp_client_systemd_timesyncd_conf_path` | `/etc/systemd/timesyncd.conf.d/95-timesyncd.conf` | systemd-timesyncd設定の出力先です。 |
| `ntp_client_chrony_conf_path_debian` | `/etc/chrony/chrony.conf` | Debian系のchrony本体設定ファイルです。 |
| `ntp_client_chrony_conf_path_rhel` | `/etc/chrony.conf` | RHEL系のchrony本体設定ファイルです。 |
| `ntp_client_chrony_conf_path` | Debian系: `/etc/chrony/chrony.conf`, RHEL系: `/etc/chrony.conf` | 実際に参照するchrony本体設定ファイルです。 |
| `ntp_client_chrony_conf_drop_in_dir` | Debian系: `/etc/chrony/conf.d`, RHEL系: `/etc/chrony.d` | chrony drop-inディレクトリです。 |
| `ntp_client_chrony_conf_drop_in_path` | Debian系は`/etc/chrony/conf.d/99-custom.conf`, RHEL系は`/etc/chrony.d/99-custom.conf` | chrony drop-in設定の出力先です。 |

## テンプレートと生成ファイル

本ロールでは以下のテンプレート / ファイルを出力します:
主な展開先ホストは, 対象ホスト(既定) です。

| テンプレートファイル名 | 出力先パス (規定値) | 説明 |
| --- | --- | --- |
| `templates/95-timesyncd.conf.j2` | `/etc/systemd/timesyncd.conf.d/95-timesyncd.conf` | systemd-timesyncd用のNTPサーバ設定を出力します。 |
| `templates/99-chrony.conf.j2` | Debian系: `/etc/chrony/conf.d/99-custom.conf`, RHEL系: `/etc/chrony.d/99-custom.conf` | chrony用のNTPサーバ設定をdrop-inとして出力します。 |

## 実行フロー

ロールは以下の6フェーズで処理します。

1. **Load Params**。
- Debian系では`vars/packages-ubuntu.yml`を読み込みます。
- RHEL系では`vars/packages-rhel.yml`を読み込みます。
- 共通で`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`を読み込みます。

2. **Package**。
- `ntp_client_packages`をインストールします。

3. **Config**。
- `service_facts`でサービス一覧を取得します。
- `systemd-timesyncd`選択時は`95-timesyncd.conf`を配置し, `systemd-timesyncd`を有効化, `chrony`を無効化します (Debian系かつ対象サービスが存在する場合)。
- `chrony`選択時はdrop-inディレクトリ作成, `chrony.conf`へ`confdir`追記, `99-custom.conf`配置, `chrony`有効化, `systemd-timesyncd`無効化を実施します。

4. **Directory**。
- `/etc/systemd/timesyncd.conf.d`を作成します。

### ハンドラ

| ハンドラ名 | listen名 | 処理内容 | 呼び出し元 |
| --- | --- | --- | --- |
| Restart_timesyncd | `restart_timesyncd` | `systemd-timesyncd`を再起動し有効化します。 | `tasks/config.yml` |
| Restart_chrony | `restart_chrony` | Debian系では`chrony`, RHEL系では`chronyd`を再起動し有効化します。 | `tasks/config.yml` |

### OS差異

| 項目 | Debian系 | RHEL系 |
| --- | --- | --- |
| `ntp_client_choice=chrony`時のパッケージ | `chrony` | `chrony` |
| `ntp_client_choice=systemd-timesyncd`時のパッケージ | `systemd-timesyncd` | 該当なし |
| chronyサービス名 | `chrony` | `chronyd` |
| chrony本体設定ファイル | `/etc/chrony/chrony.conf` | `/etc/chrony.conf` |
| chrony drop-inディレクトリ | `/etc/chrony/conf.d` | `/etc/chrony.d` |
| systemd-timesyncd利用 | 利用可 | 通常利用しない |

## 検証ポイント

### 前提条件確認

- ロール実行が正常終了していること。
- NTPクライアントノードへログイン可能であること。
- `ntp_client_choice`の設定値を把握していること。

### 検証ステップ

#### Step 1: 有効化サービスの相互排他確認

**実施ノード**: NTPクライアントノード

**コマンド**:
```bash
systemctl is-enabled systemd-timesyncd || true
systemctl is-enabled chrony || true
systemctl is-enabled chronyd || true
```

**期待される出力例**:
```plaintext
# chrony選択時の例
not-found
enabled
alias

# systemd-timesyncd選択時の例
enabled
disabled
alias

# RHEL系(chronyd)の例
not-found
disabled
enabled
```

**確認ポイント**:
- `ntp_client_choice`に対応するサービスだけが`enabled`であること。
- 非選択側サービスが`enabled`になっていないこと。

#### Step 2: 設定ファイル反映確認

**実施ノード**: NTPクライアントノード

**コマンド**:
```bash
# systemd-timesyncd選択時
sudo grep -E '^NTP=' /etc/systemd/timesyncd.conf.d/95-timesyncd.conf

# chrony選択時(Debian系)
sudo grep -E '^confdir[[:space:]]+/etc/chrony/conf.d' /etc/chrony/chrony.conf
sudo grep -E '^server ' /etc/chrony/conf.d/99-custom.conf

# chrony選択時(RHEL系)
sudo grep -E '^confdir[[:space:]]+/etc/chrony.d' /etc/chrony.conf
sudo grep -E '^server ' /etc/chrony.d/99-custom.conf
```

**期待される出力例**:
```plaintext
# systemd-timesyncd選択時の例
NTP=192.168.20.11 ntp.nict.jp

# chrony選択時(Debian系)の例
confdir /etc/chrony/conf.d
server 192.168.20.11 iburst
server ntp.nict.jp iburst
```

**確認ポイント**:
- 設定ファイルが作成されていること。
- `ntp_servers_list`が空要素/重複を除去した形で反映されていること。
- chrony選択時に`confdir`行が存在すること。
- テンプレート先頭コメントの`last update`が直近実行時刻になっていること。

#### Step 3: 同期状態確認

**実施ノード**: NTPクライアントノード

**コマンド**:
```bash
# systemd-timesyncd選択時
timedatectl show-timesync --all

# chrony選択時
chronyc tracking
chronyc sources -v
```

**期待される出力例**:
```plaintext
# chrony選択時の例 (chronyc tracking)
Reference ID    : 85F3EEF4 (ntp-a3.nict.go.jp)
Stratum         : 2
System time     : 0.000020180 seconds fast of NTP time
Leap status     : Normal

# chrony選択時の例 (chronyc sources -v)
^+ 192.168.20.11                 2   8   377    16   -211us[ -211us] +/- 3668us
^* ntp-a3.nict.go.jp             1   9   377   184   -281us[ -296us] +/- 2773us

# systemd-timesyncd選択時の例 (timedatectl show-timesync --all)
ServerName=ntp.ubuntu.com
ServerAddress=185.125.190.57
PollIntervalUSec=32s
```

**確認ポイント**:
- `timedatectl`または`chronyc`で同期先情報が取得できること。
- `ntp_servers_list`に含まれるサーバが参照候補として表示されること。

#### Step 4: ログ確認

**実施ノード**: NTPクライアントノード

**コマンド**:
```bash
# systemd-timesyncd選択時
journalctl -u systemd-timesyncd -n 50 --no-pager

# chrony選択時
journalctl -u chrony -n 50 --no-pager || true
journalctl -u chronyd -n 50 --no-pager || true
```

**期待される出力例**:
```plaintext
# systemd-timesyncd選択時の例
3月 02 03:09:29 vmlinux3 systemd[1]: Started systemd-timesyncd.service - Network Time Synchronization.
3月 02 03:10:30 vmlinux3 systemd-timesyncd[700]: Contacted time server 185.125.190.58:123 (ntp.ubuntu.com).

# chrony選択時の例
3月 03 04:11:43 vmlinux3 systemd[1]: Started chrony.service - chrony, an NTP client/server.
3月 03 04:12:57 vmlinux3 chronyd[1049]: Selected source 133.243.238.244 (ntp.nict.jp)
```

**確認ポイント**:
- 直近ログに致命的な設定エラーがないこと。
- 選択したサービスが起動済みであること。

## トラブルシューティング

エラー発生時に build-*.log と対象ホストの systemd ジャーナルを確認し, 失敗した task 名と選択した実装(`chrony` / `systemd-timesyncd`)を突き合わせて原因を特定します。代表的なトラブルと対処を以下に示します。

| 想定トラブル | 主な原因 | 対処方法 |
| --- | --- | --- |
| `ntp_client_choice` の値が不正でロールの意図どおりに設定されない | `ntp_client_choice` が `chrony` または `systemd-timesyncd` 以外になっている |  vars/all-config.yml または host_vars で `ntp_client_choice` を `chrony` もしくは `systemd-timesyncd` に修正し, ロールを再実行します。 |
| `systemd-timesyncd` を選択したのに設定ファイルが生成されない | Debian系以外では timesyncd 設定タスクが実行条件に合致しない | 実装仕様として正常です。RHEL系では `chrony` を使用します。RHEL系で時刻同期を行う場合は `ntp_client_choice: chrony` を指定して再実行します。 |
| chrony 選択時に `/etc/chrony*.conf` への追記で失敗する | 対象ファイルが破損, 権限不足, 既存設定の手編集不整合 |  `journalctl -u chrony -n 50 --no-pager` または `journalctl -u chronyd -n 50 --no-pager` を確認し, 設定ファイルの文法を修正してロールを再実行します。必要に応じてバックアップファイルから復旧します。 |
| chrony と systemd-timesyncd が同時に有効になっている | 過去設定の残存, 手動操作で相互排他状態が崩れた |  `systemctl is-enabled systemd-timesyncd`, `systemctl is-enabled chrony`, `systemctl is-enabled chronyd` を確認し, 選択した実装のみ `enabled` になるようロールを再実行します。 |
| 同期先が反映されない, または一部しか反映されない | `ntp_servers_list` に空要素, 重複, 到達不能ホストが含まれる |  `ntp_servers_list` を見直して有効なホスト名/IPのみを設定し, 再実行します。その後 `chronyc sources -v` または `timedatectl show-timesync --all` で参照先を確認します。 |
| `chronyc` で同期先が `^?` のまま変化しない | 上位NTPへの到達不可, DNS解決失敗, ファイアウォール制限 | 対象ホストの名前解決と UDP/123 到達性を確認します。到達性を改善後, サービス再起動して同期状態を再確認します。 |
| ハンドラが呼ばれず再起動されない | 設定内容に差分がなく notify が発火していない | Ansibleの仕様として正常です。即時反映が必要な場合は `systemctl restart systemd-timesyncd` または `systemctl restart chrony/chronyd` を実行し, 状態を確認します。 |

## 注意事項

- `ntp_client_choice`を切り替えることで, `chrony`と`systemd-timesyncd`のどちらにも移行できます。
- 追加のchrony設定 (例: `makestep`や`allow`) は `templates/99-chrony.conf.j2` の編集, または上位ロールからの追加drop-in投入で拡張できます。
- NTPサーバ候補はIPv4/IPv6混在で指定できます。
- 大規模環境で上位NTPへのアクセス制御が必要な場合は, ファイアウォール設定との組み合わせを検討してください。

## 参考資料

### 公式ドキュメント

- [chrony project](https://chrony-project.org/)
- [systemd-timesyncd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd-timesyncd.service.html)
- [NTP Pool Project](https://www.pool.ntp.org/)
