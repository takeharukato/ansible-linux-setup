# ntp-server ロール

本ロールは, chrony を用いた NTP サーバを構成するロールです。

## 目次

- [ntp-server ロール](#ntp-server-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
    - [主な処理](#主な処理)
    - [ディレクトリ構成](#ディレクトリ構成)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
    - [Makefileを使用した実行](#makefileを使用した実行)
    - [直接 ansible-playbook で実行](#直接-ansible-playbook-で実行)
  - [主要変数](#主要変数)
    - [基本設定](#基本設定)
    - [サービス/パス設定](#サービスパス設定)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
    - [ハンドラ](#ハンドラ)
    - [OS差異](#os差異)
  - [検証ポイント](#検証ポイント)
    - [前提条件確認](#前提条件確認)
    - [検証ステップ](#検証ステップ)
      - [Step 1: chrony サービス状態確認](#step-1-chrony-サービス状態確認)
      - [Step 2: 設定ファイル反映確認](#step-2-設定ファイル反映確認)
      - [Step 3: 上位 NTP サーバ同期状態確認](#step-3-上位-ntp-サーバ同期状態確認)
      - [Step 4: NTP サーバ統計情報確認](#step-4-ntp-サーバ統計情報確認)
      - [Step 5: サービスログ確認](#step-5-サービスログ確認)
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
| IP | - | インターネットプロトコルの略称。 |
| SQL | - | データベースを操作するための記述言語。 |
| HTTP | - | WWW で情報をやり取りする通信手順。 |
| HTTPS | - | 通信内容を暗号化して WWW 通信を行う方式。 |
| RPM | - | RHEL 系で使用するパッケージ形式。 |
| VM | - | 物理機器上で動作する仮想的な計算機。 |
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
| API | - | アプリケーション同士がやり取りする方法を定めた仕様。 |
| URL | - | WWW 上の資源の場所を示す文字列。 |
| Network Time Protocol | NTP | 時刻同期の仕組み。 |
| Classless Inter-Domain Routing | CIDR | IP アドレスとネットワークプレフィックス長を組み合わせた表記法。 |
| Local Area Network | LAN | 限定された範囲内で構成するネットワーク。 |
| Graphical User Interface | GUI | 画面操作中心の利用形態です。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Red Hat Enterprise Linux | RHEL | Red Hat 社が提供する商用 Linux ディストリビューション。 |
| Ansible | Ansible | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| Yet Another Markup Language | YAML | 設定ファイル形式です。 |
| Ansible Playbook | playbook | 自動化処理の実行手順を順序付きで記述したファイル。 |
| role | role | 特定の名前空間内で有効な権限の集合。 |
| template | template | 変数展開して出力する雛形ファイルです。 |
| handler | handler | 通知時に実行する再処理です。 |
| tag | tag | Ansibleで実行対象を絞るラベルです。 |
| systemd | - | Linux システムの初期化とサービス管理を行う仕組み。 |
| chrony | - | NTPクライアント/サーバ機能を提供する時刻同期ソフトウェアです。 |
| drop-in configuration | drop-in | 既存設定本体とは別ファイルで追加設定を適用する方式です。 |
| iburst | - | NTP 初期同期を高速化する chrony のオプションです。 |
| pool directive | pool | chrony で上位 NTP サーバ群を指定する設定行です。 |
| allow directive | allow | chrony でクライアントアクセスを許可するネットワーク範囲指定です。 |
| multi-user target | multi-user.target | GUIを使わないサーバ向けのsystemd起動状態です。 |
| localhost loopback address | 127.0.0.1/32 | 同一ホスト内通信だけを許可する IPv4 ループバック CIDR です。 |
| systemctl | - | systemd 管理下のサービスを起動, 停止, 状態確認するコマンド。 |
| journalctl | - | systemd ジャーナルのログを参照するコマンド。 |
| chronyc | - | chronyの状態確認と制御を行うコマンドです。 |
| Red Hat Enterprise Linux 9 | RHEL9 | Red Hat Enterprise Linux の第9系統版。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| International Atomic Time | TAI | 国際原子時に基づく時刻系。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `grep` | - | テキストから条件に一致する行を抽出するコマンド。 |
| `make` | - | Makefile に定義された処理を実行するコマンド。 |
| サービス | - | 機能を利用者や他システムへ提供する仕組み。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| ログイン | - | 利用者認証を行って利用を開始する操作。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |

## 概要
このロールは, chrony を用いた NTP サーバを構成するロールです。外部上位サーバとの同期, LAN 内クライアントへの時刻配信, ならびにアクセス制御を実施します。`ansible_facts.os_family` により Debian 系と RHEL 系の差異を吸収します。

本ロールは以下を構成します。

1. chrony パッケージの導入。
- `ntp_server_packages` を導入します。

2. chrony drop-in ディレクトリの作成。
- `ntp_server_chrony_conf_drop_in_dir` を作成します。

3. NTP サーバ設定の反映。
- `99-ntp-servers.conf.j2` から `99-ntp-servers.conf` を生成します。
- `external_ntp_servers_list` から `pool ... iburst` を生成します。
- `ntp_allow` を `allow` ディレクティブへ反映します。

4. chrony サービスの反映。
- 設定変更時に `restart_chrony` ハンドラでサービスを再起動, 有効化します。

### 主な処理

- `external_ntp_servers_list` から `pool ... iburst` 行を生成します。
- `ntp_allow` を `allow` 行として反映します。
- `ntp_allow` が未定義または空文字列の場合, テンプレート側で `127.0.0.1/32` へフォールバックします。
- 設定変更時は `restart_chrony` ハンドラでサービスを再起動, 有効化します。
- `external_ntp_servers_list` が空の場合は `pool` 行は生成されません。

### ディレクトリ構成

主要な設定対象は以下です。

```plaintext
/etc/chrony/conf.d/99-ntp-servers.conf (Debian系)
/etc/chrony.d/99-ntp-servers.conf (RHEL系)
```

## 前提条件

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- Ansible 2.15 以降, ansibleメタパッケージをディストリビューションから導入していることを想定
- 対象ノードで管理者権限が利用できること。
- `external_ntp_servers_list` が上位 NTP サーバとして妥当な値で定義されていること。
- `network_ipv4_network_address` および `network_ipv4_prefix_len` を利用する場合は, 適切な値が設定されていること。

## 実行方法

### Makefileを使用した実行

```bash
cd /path/to/ubuntu-setup/ansible
make run_ntp_server
```

### 直接 ansible-playbook で実行

```bash
# server.yml をタグ指定で実行
ansible-playbook -i inventory/hosts server.yml --tags "ntp-server"

# site.yml をタグ指定で実行
ansible-playbook -i inventory/hosts site.yml --tags "ntp-server"

# 対象ホストを限定して実行
ansible-playbook -i inventory/hosts site.yml --tags "ntp-server" -l <対象ホスト>
```

## 主要変数

### 基本設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `external_ntp_servers_list` | `[]` | 上位 NTP サーバ一覧です。空要素, 空文字, 重複はテンプレートで除去されます。 |
| `network_ipv4_network_address` | `""` | 許可対象ネットワークの IPv4 アドレスです。 |
| `network_ipv4_prefix_len` | `0` | 許可対象ネットワークのプレフィックス長です。 |
| `ntp_allow` | 条件式 | `network_ipv4_network_address` と `network_ipv4_prefix_len` が有効な場合は `<address>/<prefix>` を使用します。未設定, 空文字, 0 の場合は `127.0.0.1/32` を使用します。 |

### サービス/パス設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `ntp_server_service_debian` | `chrony` | Debian系の chrony サービス名です。 |
| `ntp_server_service_rhel` | `chronyd` | RHEL系の chrony サービス名です。 |
| `ntp_server_chrony_service` | OS依存 | 実際に使用する chrony サービス名です。 |
| `ntp_server_chrony_conf_drop_in_dir` | OS依存 | 設定ファイル配置先です。Debian系は `/etc/chrony/conf.d`, RHEL系は `/etc/chrony.d` です。 |
| `ntp_server_packages` | OS依存 | インストール対象パッケージ一覧です。Debian系, RHEL系ともに `chrony` です。 |

## テンプレートと生成ファイル

本ロールでは以下のテンプレート / ファイルを出力します:
主な展開先ホストは, 対象ホスト(既定) です。

| テンプレートファイル名 | 出力先パス (規定) | 説明 |
| --- | --- | --- |
| `99-ntp-servers.conf.j2` | Debian系: `/etc/chrony/conf.d/99-ntp-servers.conf`, RHEL系: `/etc/chrony.d/99-ntp-servers.conf` | chrony の参照 NTP サーバ, 同期ポリシー, サービス動作を定義する設定です。 |

## 実行フロー

ロールは以下の6フェーズで処理します。

1. **Load Params**。
- Debian系では `vars/packages-ubuntu.yml` を読み込みます。
- RHEL系では `vars/packages-rhel.yml` を読み込みます。
- 共通で `vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml` を読み込みます。

2. **Package**。
- `ntp_server_packages` を導入します。
- 変更があれば `disable_gui` を通知します。

3. **Directory**。
- `ntp_server_chrony_conf_drop_in_dir` を作成します。

4. **Config**。
- `99-ntp-servers.conf` を配置します。
- 変更があれば `restart_chrony` を通知します。


### ハンドラ

| ハンドラ名 | listen名 | 処理内容 | 呼び出し元 |
| --- | --- | --- | --- |
| Restart_chrony | `restart_chrony` | `{{ ntp_server_chrony_service }}` を再起動し, 有効化します。 | `tasks/config.yml` |

### OS差異

| 項目 | Debian系 | RHEL系 |
| --- | --- | --- |
| chrony サービス名 | `chrony` | `chronyd` |
| drop-in ディレクトリ | `/etc/chrony/conf.d` | `/etc/chrony.d` |
| NTP サーバパッケージ | `chrony` | `chrony` |

## 検証ポイント

実行者は以下の検証コマンドを実行し, 構文検査が成功することを確認します。

```bash
ansible-playbook -i inventory/hosts site.yml --syntax-check
```

期待結果: エラーが出力されず, syntax check が成功します。

### 前提条件確認

- ロール実行が正常終了していること。
- NTPサーバノードへログイン可能であること。
- クライアント検証を行う場合は, NTPクライアントノードからNTPサーバノードへ到達可能であること。

### 検証ステップ

#### Step 1: chrony サービス状態確認

**実施ノード**: NTPサーバノード

**コマンド**:
```bash
sudo systemctl is-active chrony || true
sudo systemctl is-enabled chrony || true
sudo systemctl is-active chronyd || true
sudo systemctl is-enabled chronyd || true
```

**期待される出力例**:
```plaintext
# Debian系の例
active
enabled

# RHEL系の例
inactive
disabled
active
enabled
```

**出力解釈**:
- `systemctl is-active` が `active` を返す: chrony サービスが起動状態であること。
- `systemctl is-enabled` が `enabled` を返す: chrony サービスが始動時に自動起動するよう設定されていること。

**確認ポイント**:
- Debian系では `chrony` サービスが `active` かつ `enabled` であること。
- RHEL系では `chronyd` サービスが `active` かつ `enabled` であること。
- いずれかが `inactive` または `disabled` の場合は, ロール実行に失敗している可能性, またはサービスが手動で停止されている可能性があります。

#### Step 2: 設定ファイル反映確認

**実施ノード**: NTPサーバノード

**コマンド**:
```bash
# Debian系
sudo grep -E '^(pool|allow) ' /etc/chrony/conf.d/99-ntp-servers.conf

# RHEL系
sudo grep -E '^(pool|allow) ' /etc/chrony.d/99-ntp-servers.conf
```

**期待される出力例**:
```plaintext
pool ntp.nict.jp iburst
pool jp.pool.ntp.org iburst
pool ntp.jst.mfeed.ad.jp iburst
pool ntp.ring.gr.jp iburst
pool time.google.com iburst
pool time.aws.com iburst
pool ats1.e-timing.ne.jp iburst
pool s2csntp.miz.nao.ac.jp iburst
allow 192.168.20.0/24
```

**出力解釈**:
- `pool ... iburst` 行: `external_ntp_servers_list` で定義された上位NTPサーバが `pool` ディレクティブで登録されていることを示します。各行の最後に `iburst` が付加されている点に注意してください。これによりNTP初期同期が高速化されます。
- `allow` 行: `ntp_allow` 変数で指定されたネットワーク範囲からのクライアント接続を許可する設定です。この例では `192.168.20.0/24` が許可対象ネットワークです。

**確認ポイント**:
- `pool ... iburst` 行の数が `external_ntp_servers_list` の要素数と一致していること (空要素は除去されるため, テンプレート内で `reject or default('') != ''` で判定)。
- `allow` 行が存在し, ネットワークアドレスとプレフィックス長が CIDR 形式で記載されていること。
- `network_ipv4_network_address` または `network_ipv4_prefix_len` が未設定の場合は, `allow 127.0.0.1/32` になっていることを確認。
- ファイルが存在しない場合は, ロール実行が失敗したか, テンプレート配置タスクが実行されていない可能性があります。

#### Step 3: 上位 NTP サーバ同期状態確認

**実施ノード**: NTPサーバノード

**コマンド**:
```bash
chronyc sources -v
```

**期待される出力例**:
```plaintext
MS Name/IP address         Stratum Poll Reach LastRx Last sample
===============================================================================
^+ ntp-b2.nict.go.jp             1   9   377   263   -694us[ -694us] +/- 3067us
^+ ntp-k1.nict.jp                1  10   377   143   -484us[ -484us] +/- 7513us
^+ ntp-b3.nict.go.jp             1  10   377   980   -391us[ -391us] +/- 2984us
^* ntp-a2.nict.go.jp             1  10   377   997   -222us[ -392us] +/- 2821us
...
```

**出力解釈**:
- 各行の先頭の記号:
  - `^*`: 現在同期している最良のソース。
  - `^+`: 同期候補で精度が良い複合ソース。
  - `^-`: 同期候補だが精度が低いもの。
  - `^?`: 到達不可能または未検証のソース。
- `Stratum`: NTP階層番号。1が最高精度 (GPS等)。
- `Last sample`: 最測定値 (正の値は遅延, 負の値は進んでいることを示す)。
- 括弧内の値 `[-392us]`: 調整後のオフセット。
- `+/- 2821us`: 推定誤差範囲。

**確認ポイント**:
- `^*` または `^+` の行が存在すること (同期中のソースがあること)。
- 少なくとも3個以上のソースと通信できていること (複数ソース選択によって精度が向上)。
- `Last sample` が秒単位 (ms 以下) に収まっていること。
- `Reach` の値が377 (8進数) であること。これは直近8回の送信で全て到達したことを示します。
- `^?` のみでは同期していないため, 設定またはネットワーク接続を確認。

#### Step 4: NTP サーバ統計情報確認

**実施ノード**: NTPサーバノード

**コマンド**:
```bash
chronyc sourcestats
```

**期待される出力例**:
```plaintext
Name/IP Address            NP  NR  Span  Frequency  Freq Skew  Offset  Std Dev
==============================================================================
ntp-b2.nict.go.jp           6   5   42m     -0.211      0.409   -512us    93us
ntp-k1.nict.jp             21  10  344m     -0.073      0.059   -708us   419us
ntp-b3.nict.go.jp          14   8  138m     +0.061      0.088    +14us   192us
ntp-a2.nict.go.jp           6   3   86m     -0.012      0.423    +36us   186us
...
```

**出力解釈**:
- `NP`: サンプル数 (measurements processed)。
- `NR`: 実際に使用されたサンプル数 (still in use)。
- `Span`: 観測期間 (例: `344m` は344分)。
- `Frequency`: 時刻周波数の偏差 (ppm)。理想は 0。
- `Freq Skew`: 周波数偏差の推定誤差。小さいほど信頼性が高い。
- `Offset`: 平均時刻オフセット (例: `-512us` は512マイクロ秒遅れている)。
- `Std Dev`: 標準偏差 (ノイズレベル, 小さいほど安定)。

**確認ポイント**:
- 複数のサーバに対して統計情報があること。
- `Offset` が ±1ms 程度に収まっていること。
- `Std Dev` が ±1000us (1ms) 以下であること。
- 有効な `NR` (still in use) が1以上であること。
- `Freq Skew` が 2000 未満であること (2000は未検証ソース)。

#### Step 5: サービスログ確認

**実施ノード**: NTPサーバノード

**コマンド**:
```bash
sudo journalctl -u chrony -n 30 --no-pager || true
sudo journalctl -u chronyd -n 30 --no-pager || true
```

**期待される出力例**:
```plaintext
2月 23 18:26:24 mgmt-server systemd[1]: Starting chrony.service - chrony, an NTP client/server...
2月 23 18:26:24 mgmt-server chronyd[1061]: chronyd version 4.5 starting ...
2月 23 18:26:24 mgmt-server chronyd[1061]: Loaded 0 symmetric keys
2月 23 18:26:24 mgmt-server chronyd[1061]: Frequency -0.411 +/- 0.026 ppm read from /var/lib/chrony/chrony.drift
2月 23 18:26:24 mgmt-server chronyd[1061]: Using right/UTC timezone to obtain leap second data
2月 23 18:26:24 mgmt-server chronyd[1061]: Loaded seccomp filter (level 1)
2月 23 18:26:24 mgmt-server systemd[1]: Started chrony.service - chrony, an NTP client/server.
2月 23 18:26:45 mgmt-server chronyd[1061]: Selected source 133.243.238.163 (ntp.nict.jp)
2月 23 18:26:45 mgmt-server chronyd[1061]: System clock TAI offset set to 37 seconds
2月 23 23:21:35 mgmt-server chronyd[1061]: Selected source 133.243.238.243 (ntp.nict.jp)
```

**出力解釈**:
- `chronyd version X.X starting`: chrony デーモン起動ログ。バージョン情報と起動時刻が表示されます。
- `Frequency ... ppm`: 前回実行時に測定された周波数オフセット。`/var/lib/chrony/chrony.drift` から読み込まれます。
- `Using right/UTC timezone`: TAI (国際原子時) オフセット情報の読み込み。
- `Loaded seccomp filter`: セキュリティサンドボックス有効化。
- `Starting ... Started`: systemd による起動・停止の通知ログ。
- `Selected source IP (hostname)`: 同期対象として選択されたNTPサーバ。
- `System clock TAI offset set to 37 seconds`: TAI オフセット更新。

**確認ポイント**:
- `Starting ... Started` でサービス起動に成功していること。
- `Selected source ... (hostname)` が表示されていること (NTPサーバが同步に成功しつつあることを示す)。
- `Error`, `Failed`, `denied` など致命的なエラーメッセージが無いこと。
- `Configuration error` や `parse error` が無いこと。設定ファイルの文法エラーがあればここに出力されます。
- RHEL系の場合は `chronyd` プロセスのログが出力されること。Debian系の場合は `chrony` へのプロキシメッセージが出力されることもあります。

## トラブルシューティング

エラー発生時に build-*.log を確認し, 失敗した task 名と不足変数を特定します。代表的なトラブルと対処を以下に示します。

| 想定トラブル | 主な原因 | 対処方法 |
| --- | --- | --- |
| chrony サービスが `active` にならない | パッケージ導入失敗, 設定ファイル文法エラー, サービス名の取り違え | 実行者は `systemctl status chrony` または `systemctl status chronyd` と `journalctl -u chrony -n 50 --no-pager` / `journalctl -u chronyd -n 50 --no-pager` を確認し, エラー内容を修正後にロールを再実行します。 |
| `/etc/chrony/conf.d/99-ntp-servers.conf` または `/etc/chrony.d/99-ntp-servers.conf` が生成されない | Config タスク失敗, 事前タスクの権限不備, OS 判定と期待パスの不一致 | 実行者は build-*.log で `Setup ntp server configuration` タスク結果を確認し, Debian系では `/etc/chrony/conf.d`, RHEL系では `/etc/chrony.d` に出力されることを確認します。必要に応じて対象ホスト権限を見直して再実行します。 |
| `chronyc sources -v` が `^?` のみで同期しない | 上位NTPサーバへの到達不可, DNS解決失敗, ファイアウォール制限 | 実行者は `external_ntp_servers_list` のホスト名/IPを見直し, 名前解決と UDP/123 の到達性を確認します。到達性改善後にサービスを再起動して再確認します。 |
| `allow` が意図と異なる値になる | `network_ipv4_network_address` または `network_ipv4_prefix_len` が未設定/不正で `ntp_allow` がフォールバックした | 実行者は `network_ipv4_network_address` と `network_ipv4_prefix_len` の値を見直します。未設定時は `allow 127.0.0.1/32` になる実装であるため, LAN公開が必要な場合は正しい CIDR 値を設定して再実行します。 |
| `pool` 行が出力されない | `external_ntp_servers_list` が空, または空要素のみ | 実行者は `external_ntp_servers_list` に有効な上位NTPサーバを設定します。重複や空要素はテンプレートで除去されるため, 実際に必要な値が残るように定義して再実行します。 |
| 設定変更後にサービスが再起動されない | テンプレート差分がなく notify が発火していない | Ansible の仕様として正常です。即時反映が必要な場合は実行者が `systemctl restart chrony` または `systemctl restart chronyd` を実行し, 状態を確認します。 |

## 注意事項


- `external_ntp_servers_list` が空の場合, テンプレート内ループはスキップされます。
- `allow` で指定する範囲は最小限にしてください。
- IPv6 のアクセス制御を併用する場合は, 別途設定追加が必要です。
- `disable_gui` 通知が不要な環境では, 上位ロール側で制御する運用を検討してください。
- chrony の同期挙動チューニングが必要な場合は, `makestep` などを追加する拡張方針を検討してください。
- chrony 再起動が発生するため, メンテナンス時間内での実行を推奨します。

## 参考資料

### 公式ドキュメント

- [chrony project](https://chrony-project.org/)
- [chrony.conf manual](https://chrony-project.org/doc/4.5/chrony.conf.html)
- [NTP Pool Project](https://www.pool.ntp.org/)
