# Docker Composeを使用したOpenLDAP管理サーバ

本ロールは, Docker Composeを使用して, OpenLDAPサーバとphpLDAPadmin(Webベースの管理画面)を構築するロールです。

## 目次

- [Docker Composeを使用したOpenLDAP管理サーバ](#docker-composeを使用したopenldap管理サーバ)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
    - [構成要素](#構成要素)
    - [導入後のディレクトリ構成](#導入後のディレクトリ構成)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
    - [Makefile を使用した実行(推奨)](#makefile-を使用した実行推奨)
    - [直接 ansible-playbook で実行](#直接-ansible-playbook-で実行)
  - [主要変数](#主要変数)
    - [LDAP基本設定](#ldap基本設定)
    - [ディレクトリ設定](#ディレクトリ設定)
    - [コンテナ設定](#コンテナ設定)
    - [待機設定](#待機設定)
    - [ネットワーク設定](#ネットワーク設定)
  - [設定例](#設定例)
    - [group\_vars/all での設定](#group_varsall-での設定)
    - [host\_vars/mgmt-server.local での設定](#host_varsmgmt-serverlocal-での設定)
  - [バックアップ方法](#バックアップ方法)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
    - [ハンドラ](#ハンドラ)
    - [OS差異](#os差異)
  - [検証ポイント](#検証ポイント)
    - [前提条件確認](#前提条件確認)
    - [検証ステップ](#検証ステップ)
      - [Step 1: Docker Compose ファイル確認](#step-1-docker-compose-ファイル確認)
      - [Step 2: コンテナ起動状態確認](#step-2-コンテナ起動状態確認)
      - [Step 3: OpenLDAP サービス接続確認](#step-3-openldap-サービス接続確認)
      - [Step 4: phpLDAPadmin Web UI ログイン確認](#step-4-phpldapadmin-web-ui-ログイン確認)
      - [Step 5: LDAP エントリ作成テスト](#step-5-ldap-エントリ作成テスト)
      - [Step 6: sysctl 設定確認](#step-6-sysctl-設定確認)
      - [Step 7: バックアップスクリプト動作確認](#step-7-バックアップスクリプト動作確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. docker compose 実行時にコマンドエラーとなる場合](#1-docker-compose-実行時にコマンドエラーとなる場合)
    - [2. OpenLDAP / phpLDAPadmin コンテナが起動しない場合](#2-openldap--phpldapadmin-コンテナが起動しない場合)
    - [3. ロール実行後に LDAP 接続できない場合](#3-ロール実行後に-ldap-接続できない場合)
    - [4. phpLDAPadmin へログインできない場合](#4-phpldapadmin-へログインできない場合)
    - [5. バックアップ/リストアスクリプトが失敗する場合](#5-バックアップリストアスクリプトが失敗する場合)
    - [6. LDAP データが再起動後に消える場合](#6-ldap-データが再起動後に消える場合)
    - [7. sysctl 設定が反映されず通信が不安定な場合](#7-sysctl-設定が反映されず通信が不安定な場合)
  - [注意事項](#注意事項)
    - [Docker Compose v2 について](#docker-compose-v2-について)
    - [ボリューム永続化について](#ボリューム永続化について)
    - [セキュリティ考慮事項](#セキュリティ考慮事項)
    - [バージョン管理](#バージョン管理)
    - [運用推奨事項](#運用推奨事項)
  - [付録: `backup-ldap-data.sh`スクリプトの内容](#付録-backup-ldap-datashスクリプトの内容)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)


## 用語

LDAP関連の標準用語については本セクションで定義します。一般的なネットワーク・システム管理用語は `roles/common/Readme.md` を参照してください。

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
| サービスアカウント (Service Account) | - | 自動処理中でサービスを呼び出す側のプログラムを識別するための識別情報。 |
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
| アプリケーション | - | 利用者の目的を実現するために動作するソフトウェア。 |
| パッケージ | - | ソフトウェア導入に必要なファイルをまとめた配布単位。 |
| リポジトリ | - | ソフトウェアや設定情報を保管し, 取得できるようにした管理場所。 |
| コマンド | - | 実行者が計算機へ処理を指示するための命令。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| ホスト | - | 管理対象として識別される個別の計算機。 |
| サーバ | - | 他の機器や利用者へ機能やデータを提供する計算機, 又はその役割。 |
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
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| Lightweight Directory Access Protocol | LDAP | 階層型ディレクトリサービスへのアクセスプロトコル, ユーザやグループ情報を集中管理する際に使用される標準プロトコル |
| Common Name | CN | ディレクトリエントリの一般名, ユーザ名やグループ名として使用される属性 |
| Domain Component | DC | LDAP 識別名 ( Distinguished Name ) を構成するドメイン要素。 |
| Organizational Unit | OU | 組織内の部門や部署を表すディレクトリ階層要素 |
| Distinguished Name | DN | ディレクトリエントリを一意に識別する完全修挙名, CN+OU+DCの組み合わせで構成される |
| PHP: Hypertext Preprocessor | PHP | サーバサイドWebスクリプト言語, phpLDAPadminで使用される |
| User Interface | UI | 利用者がソフトウェアを操作するための見た目と操作方法。 |
| Identifier | ID | 対象を一意に識別するための値。 |
| Docker Compose | - | 複数のコンテナ定義をまとめて作成, 起動, 停止, 更新する仕組み。 |
| Docker Compose 定義ファイル | - | Docker Compose が参照するコンテナ構成の定義ファイル。 |
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
| イメージ | - | Dockerコンテナを起動するためのテンプレートファイル。osixia/openldap, osixia/phpldapadminはコンテナイメージ |
| ボリューム | - | Dockerコンテナ内のディレクトリやファイルシステムをホスト側と共有するためのマウント機構。ローカルディレクトリまたはDocker管理下のボリュームをマウント可能 |
| マウント | - | Dockerコンテナ内に, 外部(ホストやネットワークストレージ)のディレクトリやボリュームを接続する処理 |
| ネットワーク | - | Dockerコンテナ同士が通信するための仮想ネットワーク。docker-compose.ymlで明示的に定義可能 |
| ポートマッピング | - | Dockerコンテナ内のプロセスがリスニングするポート(例えばLDAPなら389)をホスト側のポート(例えば389やカスタムポート)に割り当てる機構 |
| 環境変数 | - | 実行時の動作を調整するために外部から渡す設定値。 |
| daemon, スタンドアロンデーモン | slapd | OpenLDAPのメインプロセス。ポート389(デフォルト)でLDAPクライアント接続を受け付け, LDAP操作を処理する |
| tar | - | 複数ファイルを一つにまとめる, 展開するコマンド。 |
| Red Hat Enterprise Linux | RHEL | Red Hatが提供する企業向けLinuxディストリビューション。 |
| Secure Sockets Layer | SSL | 通信を暗号化する旧来方式の名称。現在は主に TLS を使用する。 |
| Transmission Control Protocol | TCP | 通信相手との接続を確立してからデータを送受信する通信方式。 |
| Transport Layer Security | TLS | 通信経路でデータを暗号化して保護する仕組み。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Playbook | playbook | 自動化処理の実行手順を順序付きで記述したファイル。 |
| systemd | - | Linux システムの初期化とサービス管理を行う仕組み。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| Community Edition | CE | 商用版と区別する無償版の製品区分。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| composeコマンド | compose | Docker Compose v2 の操作を実行するコマンド。 |
| `cat` | - | ファイル内容を標準出力へ表示するコマンド。 |
| `docker` | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| `ldapadd` | - | LDAP サーバへエントリを追加するコマンド。 |
| `ldapsearch` | - | LDAP サーバ内のエントリを検索するコマンド。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| makeコマンド | make | Makefile に定義された処理を実行するコマンド。 |
| `sysctl` | - | カーネル動作パラメタを参照, 変更するコマンド。 |
| サイト | - | 情報や機能を公開する場所。 |
| サービス | - | 機能を利用者や他システムへ提供する仕組み。 |
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| ディスク | - | 永続的にデータを保存する記憶装置。 |
| データベース | - | 検索や更新ができるよう整理した情報の集合。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| ポート | - | 通信の出入口を識別する番号または接点。 |
| ログイン | - | 利用者認証を行って利用を開始する操作。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |
## 概要

本ロールは, Docker Composeを使用して, OpenLDAPサーバとphpLDAPadmin(Webベースの管理画面)を構築するロールです。osixia/openldapとosixia/phpldapadminのコンテナイメージを使用し, 2つのコンテナを`docker compose up -d`で起動して, ユーザ, グループ情報を集中管理するLDAP(Lightweight Directory Access Protocol)ディレクトリサービスを提供します。

### 構成要素

このロールは以下の2つのコンテナを管理します:

1. **OpenLDAPコンテナ** (`osixia/openldap`) — LDAPディレクトリサービスの本体です。ユーザ, グループ, その他のディレクトリエントリを階層型で管理し, ldapsearchやldapmodifyなどのLDAPユーティリティで直接アクセス可能にします。内部的にはslapd(stand-alone LDAP daemon)プロセスがLDAPリスナーとして動作し, ポート389(標準的なLDAPポート)またはカスタムポート(group_vars/all.ymlの`openldap_service_port`)でクライアント接続を受け付けます。

2. **phpLDAPadminコンテナ** (`osixia/phpldapadmin`) — OpenLDAPの設定, 管理のためのWebベースのユーザインターフェースです。PHPで実装されており, ブラウザからhttps://ホスト名:10443(デフォルト)でアクセスして, LDAP DNの検索, 参照, 編集が可能です。管理者認証にはOpenLDAP管理者の認証情報(cn=admin,...)を使用します。

### 導入後のディレクトリ構成

ロール実行後, 対象ホスト上に以下のディレクトリ, ファイルが生成されます:

```
/data/openldap/
  ├─ docker/
  │  └─ docker-compose.yml         # Docker Compose 定義ファイル(テンプレートから生成)
  ├─ scripts/
  │  ├─ backup-ldap-data.sh        # バックアップスクリプト(テンプレートから生成)
  │  └─ restore-ldap-data.sh       # リストアスクリプト(テンプレートから生成)
  └─ slapd/
     ├─ database/                  # OpenLDAPデータベースボリューム(Dockerマウント)
     └─ config/                    # OpenLDAP設定ファイルボリューム(Dockerマウント)
```

OpenLDAPコンテナは`/data/openldap/slapd/{database,config}`をボリュームマウントして, 永続データ保存と設定共有を実現します。

## 前提条件

このロール実行前に以下の環境前提条件を満たす必要があります。

1. **対象OS**: Debian系(Ubuntu 20.04 LTS以降)またはRHEL系(9.x以降)が動作するホスト
2. **Ansible**: 2.15以降がインストール済みの管理ノード
3. **Docker CE**: ターゲットホストにDocker CE(Community Edition)がインストール済みであること。Docker Compose v2(docker compose コマンド)で動作可能な状態が必須。
4. **ポート利用可能性**: ターゲットホストで以下のポートが外部から到達可能またはファイアウォールで許可されていること。
   - ポート389(TCP, LDAP標準ポート)
   - ポート10443(TCP, phpLDAPadmin用HTTPS, デフォルト設定の場合)
5. **ディレクトリ権限**: `/data`直下にディレクトリ作成可能な権限をroot(またはsudo)で保持していること。
6. **ディスク容量**: LDAPデータベースボリュームとして最低1GB以上の空き容量を確保していること(環境に応じて拡張必要)
7. **必須変数の設定**: 以下の変数を`group_vars/all`または`host_vars/`で必ず設定すること。設定されていない場合, ロール実行時にfailで停止。
   - `ldap_organization`: LDAP組織名(例: `my-organization`, 空文字列不可)
   - `ldap_domain`: LDAPドメイン名(例: `example.org`, 空文字列不可)

## 実行方法

ロール実行は Makefile またはタグ指定による ansible-playbook 実行で実施。

### Makefile を使用した実行(推奨)

```bash
cd /path/to/ubuntu-setup/ansible
make run_ldap_server
```

### 直接 ansible-playbook で実行

全ホストで実行(タグ指定):
```bash
ansible-playbook -i inventory/hosts site.yml --tags "ldap-server"
```

特定ホストのみ実行:
```bash
ansible-playbook -i inventory/hosts site.yml --tags "ldap-server" -l mgmt-server.local
```

特定タスク(例: Service タスクのみ)実行:
```bash
ansible-playbook -i inventory/hosts site.yml --tags "ldap-server" --tags "service"
```

## 主要変数

このロールで使用される主要な変数を以下にカテゴリー分けして記載します。`vars/all-config.yml`, `group_vars/all`, `host_vars/`で値を上書き可能です。

### LDAP基本設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `ldap_organization` | `""` | LDAP組織名。OpenLDAPコンテナの`LDAP_ORGANISATION`環境変数として設定されます。**未定義または空文字列の場合, パッケージインストール, ユーザ/グループ作成, ディレクトリ作成, sysctl設定, サービス起動, 設定ファイル生成の各タスクはスキップされます** |
| `ldap_domain` | `""` | LDAPドメイン名。OpenLDAPコンテナの`LDAP_DOMAIN`環境変数として設定され, DC構成要素に使用されます。**未定義または空文字列の場合, 主要タスクはスキップされます** |
| `ldap_admin_password` | `""` | LDAP管理者(cn=admin)のパスワード。OpenLDAPコンテナの`LDAP_ADMIN_PASSWORD`環境変数として設定されます。**未定義または空文字列の場合, 主要タスクはスキップされます** |
| `ldap_admin_port` | `10443` | phpLDAPadmin Web UI のHTTPS公開ポート番号。**0または未定義の場合, 主要タスクはスキップされます** |

### ディレクトリ設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `openldap_docker_dir` | `/data/openldap/docker` | Docker Compose 定義ファイル (`docker-compose.yml`) の配置先ディレクトリ |
| `openldap_scripts_dir` | `/data/openldap/scripts` | バックアップ, リストアスクリプトの配置先ディレクトリ |
| `openldap_database_dir` | `/data/openldap/slapd/database` | LDAPデータベースの永続化ディレクトリ。Dockerボリュームとしてマウント |
| `openldap_config_dir` | `/data/openldap/slapd/config` | LDAP設定ファイルの永続化ディレクトリ。Dockerボリュームとしてマウント |

### コンテナ設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `openldap_server_user` | `911` | OpenLDAPコンテナ内で使用するユーザID。osixia/openldapイメージの openldapユーザに対応 |
| `openldap_server_grp` | `911` | OpenLDAPコンテナ内で使用するグループID。osixia/openldapイメージの openldapグループに対応 |
| `openldap_service_port` | `389` | OpenLDAPサービスポート番号。外部LDAP接続が必要な場合はポートフォワーディング設定で調整 |

### 待機設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `openldap_wait_host_stopped` | `127.0.0.1` | OpenLDAPサービス停止を待ち合わせる接続先ホスト名またはIPアドレス |
| `openldap_wait_host_started` | `{{ inventory_hostname }}` | OpenLDAPサービス開始を待ち合わせる接続先ホスト名またはIPアドレス。デフォルトはインベントリホスト名 |
| `openldap_wait_timeout` | `600` | OpenLDAPサービス待ち合わせ時間(単位:秒)。コンテナ起動に時間要する場合は増加 |
| `openldap_wait_delay` | `5` | OpenLDAPサービス待ち合わせ開始までの遅延時間(単位:秒)。コンテナ起動完了の待機用 |
| `openldap_wait_sleep` | `2` | OpenLDAPサービス待ち合わせ中の再試行間隔(単位:秒)。短いほど応答性向上, 長いほどリソース消費削減 |
| `openldap_wait_retries` | `5` | OpenLDAPサービス待ち合わせの再試行回数。 |
| `openldap_wait_delegate_to` | `localhost` | OpenLDAPサービス待ち合わせ時の接続元ホスト名またはIPアドレス |

### ネットワーク設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `mgmt_nic` | (環境依存) | 管理用ネットワークインターフェース名。sysctl設定でIPv6 RA受信を有効化する際に使用。ansible_facts から自動検出(VMware:ens160, xcp-ng:enX0, その他:eth0) |
| `openldap_enable_ipv6` | `true` | IPv6フォワーディング有効化フラグ。trueの場合, IPv6フォワーディングとRA受信がmgmt_nicで有効化 |

## 設定例

### group_vars/all での設定

`group_vars/all/all.yml` でロール全体の共通設定を定義:

```yaml
# LDAP 基本設定
ldap_organization: "MyOrganization"    # 組織名 ( 必須 )
ldap_domain: "example.org"             # ドメイン名 ( 必須 )
ldap_admin_password: "admin"           # 管理者パスワード ( デフォルト値 )
ldap_admin_port: 10443                 # phpLDAPadmin Web UI ポート

# ディレクトリ設定
openldap_docker_dir: "/data/openldap/docker"
openldap_scripts_dir: "/data/openldap/scripts"
openldap_database_dir: "/data/openldap/slapd/database"
openldap_config_dir: "/data/openldap/slapd/config"

# 待機設定
openldap_wait_timeout: 600             # サービス待機時間(秒)
openldap_wait_delay: 5
openldap_wait_sleep: 2
```

### host_vars/mgmt-server.local での設定

ホスト固有の設定を `host_vars/mgmt-server.local` に記載します。ここで設定した値は `group_vars` での設定を上書きします:

```yaml
# 管理サーバ固有設定
ldap_organization: "TechDepartment"    # 組織名を上書き
ldap_domain: "ldap.example.org"        # ドメイン名を上書き ( オプション )
ldap_admin_password: "secure_password" # 管理者パスワードを上書き ( セキュリティ上, 環境変数推奨 )
openldap_service_port: 389             # LDAPポート
openldap_enable_ipv6: true             # IPv6 有効化
```

以下のリストアスクリプトを実行すると, LDAP (Lightweight Directory Access Protocol, 軽量ディレクトリアクセスプロトコル) の設定, データベースをカレントディレクトリのconfig-backup.tar, data-backup.tar, phpadmin-backup.tar からリストアします。

事前に,

```
cd /data/openldap/docker
docker compose pause
```

を実行してコンテナ内のプロセスを停止してから
`/data/openldap/scripts/restore-ldap-data.sh`スクリプトを実行します。
`restore-ldap-data.sh`スクリプトは, 以下の処理を行います。

- カレントディレクトリをコンテナの/backupディレクトリにマウント
- busyboxのコンテナを起動
- tar コマンドで/etc/ldap/slapd.d, /var/lib/ldapディレクトリを, それぞれ, config-backup.tar, data-backup.tar, phpadmin-backup.tarから展開
- コンテナを破棄

```:restore-ldap-data.sh
#!/bin/sh
#  -*- coding:utf-8 mode:bash -*-
# This file is generated by ansible.
{# 日付の取得 #}
# last update: {{ '%Y-%m-%d %H:%M:%S %Z' | strftime(ansible_date_time.epoch) }}
#
# busyboxのコンテナイメージを使用して, ホスト上のカレントディレクトリにあるtarファイルの
# 内容をopenldapコンテナ内で定義されているボリュームに展開する
#

# 1) openldapのコンテナIDを取得する
container_id=`docker ps|grep osixia/openldap:|awk -F ' ' '{print $1;}'`

# 2) phpldapadminのコンテナIDを取得する
phpadmin_container_id=`docker ps|grep osixia/phpldapadmin:|awk -F ' ' '{print $1;}'`

# 3) ホストのカレントディレクトリをコンテナ内の/backupディレクトリにマウントした上で,
# openldapコンテナのボリュームを参照可能にして, busyboxのコンテナを生成し,
# カレントディレクトリにあるconfig-backup.tarの内容をopenldapのコンテナ内に展開する
docker run --rm --volumes-from "${container_id}" -v `pwd`:/backup busybox tar xvf /backup/config-backup.tar -C /

# 4) ホストのカレントディレクトリをコンテナ内の/backupディレクトリにマウントした上で,
# openldapコンテナのボリュームを参照可能にして, busyboxのコンテナを生成し,
# カレントディレクトリにあるdata-backup.tarの内容をopenldapのコンテナ内に展開する
docker run --rm --volumes-from "${container_id}" -v `pwd`:/backup busybox tar xvf /backup/data-backup.tar -C /

# 4) ホストのカレントディレクトリをコンテナ内の/backupディレクトリにマウントした上で,
# phpldapadminコンテナのボリュームを参照可能にして, busyboxのコンテナを生成し,
# カレントディレクトリにあるphpadmin-backup.tarの内容をopenldapのコンテナ内に展開する
docker run --rm --volumes-from "${phpadmin_container_id}" -v `pwd`:/backup busybox tar xvf /backup/phpadmin-backup.tar -C /
```

上記が完了したら以下のコマンドを実行して, コンテナを再開します。

```
cd /data/openldap/docker
docker compose unpause
```

インストール先ホストに WEBブラウザから以下のようにアクセスします。
ポート番号は, `group_vars/all.yml`に記載されている`ldap_admin_port`の値(デフォルトは, `10443`)を指定します。

```
https://ホスト名:10443/
```

ログイン時は, CN (Common Name, 共通名) に`admin`を指定し, ドメイン名を元に DC (Domain Component, ドメイン構成要素) を指定します。

'.' で区切られたドメイン名の各要素をdc=要素名,dc=要素名として並べてDC (Domain Component, ドメイン構成要素) を指定します。
ドメイン名がexample.comの場合, 以下を`login`名に入力します。
```
cn=admin,dc=example,dc=com
```

パスワードは, `group_vars/all.yml`に記載されている`ldap_admin_password`の値(デフォルトは, `ldap`)を入力します。

## バックアップ方法

以下のバックアップスクリプトを実行すると, LDAP の設定, データベースをカレントディレクトリにバックアップします。

- config-backup.tar LDAP の設定
- data-backup.tar   LDAP のデータベース
- phpadmin-backup.tar phpldapadminのデータ

事前に, 以下のコマンドを実行してコンテナ内のプロセスを停止させます:
```
cd /data/openldap/docker
docker compose pause
```

コンテナ内のプロセスが停止したことを確認後, `/data/openldap/scripts/backup-ldap-data.sh`スクリプトを実行します。`backup-ldap-data.sh`スクリプトは, 以下の処理を行います:

- カレントディレクトリをコンテナの/backupディレクトリにマウント
- busyboxのコンテナを起動
- tar コマンドで/etc/ldap/slapd.d, /var/lib/ldapディレクトリを, それぞれ, config-backup.tar, data-backup.tar, phpadmin-backup.tarに保存
- コンテナを破棄

`backup-ldap-data.sh`スクリプトの処理が完了したら以下のコマンドを実行して, コンテナを再開します:

```
cd /data/openldap/docker
docker compose unpause
```

## テンプレートと生成ファイル

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `docker-compose.yml.j2` | `/data/openldap/docker/docker-compose.yml` (既定: `/data/openldap/docker/docker-compose.yml`) | OpenLDAP と phpLDAPadmin の Docker Compose 定義ファイル。services セクションで各コンテナの環境変数(LDAP_ORGANISATION, LDAP_DOMAIN, LDAP_ADMIN_PASSWORD等), ports セクションでポートマッピング(389:389, 10443:443), volumes セクションでホストディレクトリマウント(/data/openldap/slapd/*)を記載 |
| `90-ldap-forwarding.conf.j2` | `/etc/sysctl.d/90-ldap-forwarding.conf` (既定: `/etc/sysctl.d/90-ldap-forwarding.conf`) | IPv4フォワーディング(net.ipv4.ip_forward=1), IPv6フォワーディング(net.ipv6.conf.all.forwarding=1), RA受信(net.ipv6.conf.{{ mgmt_nic }}.accept_ra=2)を記載するsysctl設定ファイル。Dockerネットワーク通信の正常動作に必須 |
| `backup-ldap-data.sh.j2` | `/data/openldap/scripts/backup-ldap-data.sh` (既定: `/data/openldap/scripts/backup-ldap-data.sh`) | LDAP設定(/etc/ldap/slapd.d)とデータベース(/var/lib/ldap), phpLDAPadminデータ(/var/www/phpldapadmin)をtar形式でバックアップするシェルスクリプト。busybox コンテナを用いてボリュームをアーカイブ化し, config-backup.tar, data-backup.tar, phpadmin-backup.tar を生成 |
| `restore-ldap-data.sh.j2` | `/data/openldap/scripts/restore-ldap-data.sh` (既定: `/data/openldap/scripts/restore-ldap-data.sh`) | バックアップアーカイブから LDAP設定, データベース, phpLDAPadminデータをリストアするシェルスクリプト。busybox コンテナを用いてアーカイブを展開, コンテナボリューム内に復元 |

## 実行フロー

ロールは以下の7つのタスク実行フェーズを順序立てて実施します:

1. **Load Params** — `group_vars/all`, `host_vars/`から変数を読み込み, デフォルト値を上書き
2. **Package** — LDAPクライアントユーティリティ(ldap-utils(Debian)/openldap-clients(RHEL)), Docker CE関連パッケージをインストール
3. **User Group** — OpenLDAPコンテナ実行ユーザ(openldap, uid 911, gid 911)をホスト上に事前作成. ボリュームマウント時のディレクトリ所有権を設定するため必須
4. **Directory** — `/data/openldap/docker`, `/data/openldap/scripts`, `/data/openldap/slapd/{database,config}`の各ディレクトリを作成し, 所有権とパーミッション(755)を設定
5. **Sysctl** — IPv4/IPv6フォワーディングとRA受信を有効化する設定ファイル(`/etc/sysctl.d/90-ldap-forwarding.conf`)を配置し, sysctl -pのリロード処理を実行. Dockerネットワーク通信の正常動作に必須
6. **Service** — Docker Compose 定義ファイル (`docker-compose.yml`) をテンプレートから生成してディレクトリに配置し, `docker compose up -d`でOpenLDAPコンテナとphpLDAPadminコンテナを起動. 起動待機(デフォルト600秒)処理を実行
7. **Config** — バックアップスクリプト(`backup-ldap-data.sh`, `restore-ldap-data.sh`)をテンプレートから生成して配置, 実行権限(755)を設定. sysctl設定リロード用ハンドラ(`ldap_server_reload_sysctl`)をトリガー

### ハンドラ

本ロールは以下のハンドラを設定します:

| ハンドラ名 | トリガー条件 | 処理内容 |
| --- | --- | --- |
| ldap_server_reload_sysctl | sysctl設定ファイル(/etc/sysctl.d/90-ldap-forwarding.conf)が更新された場合 | `sysctl --system`を実行し, カーネルパラメータの設定ファイル群を再読み込み。IPv4/IPv6フォワーディング, RA受信設定を即座に反映し, Dockerネットワーク通信を即座に有効化 |

### OS差異

Debian系(Ubuntu等)とRHEL系(RHEL 9.x等)の環境でパッケージ名やサービス名が異なります。本ロールは ansible.builtin.package モジュールにより, OS別の設定値を自動選択します。

| 項目 | Debian/Ubuntu系 | RHEL 9系 |
| --- | --- | --- |
| **LDAPクライアント パッケージ** | ldap-utils | openldap-clients |
| **Docker CE パッケージ** | docker-ce, docker-ce-cli, containerd.io | docker-ce, docker-ce-cli, containerd.io |
| **Docker Composeコマンド** | docker compose(v2, pip3 install via docker.io) | docker compose(v2, pip3 install via docker.io) |
| **パッケージマネージャー** | apt/apt-get | dnf/yum |
| **Docker デーモン管理** | systemctl(systemd) | systemctl(systemd) |

## 検証ポイント

以下の検証コマンドを実行し, 構文検査が成功することを確認します。

```bash
ansible-playbook -i inventory/hosts site.yml --syntax-check
```

期待結果: エラーが出力されず, syntax check が成功します。

ロール実行完了後, 以下の前提条件確認と7つの検証ステップでセットアップ成功を確認します。

### 前提条件確認

実行開始前に, ターゲットホストで以下の条件を確認:

1. **Docker CE がインストール済み**: `docker --version && docker compose version`が正常応答
2. **ポート 389, 10443 が利用可能**: `netstat -tlnp | grep -E :(389|10443)`で他プロセスが使用していないこと確認
3. **ディスク空き容量**: `df -h /data`で最低1GB以上の空き容量確認

### 検証ステップ

#### Step 1: Docker Compose ファイル確認

**実施ノード**: LDAPサーバコンテナ動作ホスト

**コマンド**:
```bash
cat /data/openldap/docker/docker-compose.yml
```

**期待される出力例**:
```yaml
version: '3'
services:
  openldap:
    image: osixia/openldap:...
    environment:
      LDAP_ORGANISATION: "MyOrganization"
      LDAP_DOMAIN: "example.org"
      LDAP_ADMIN_PASSWORD: "admin"
    ports:
      - "389:389"
    volumes:
      - /data/openldap/slapd/database:/var/lib/ldap
      - /data/openldap/slapd/config:/etc/ldap/slapd.d
  phpldapadmin:
    image: osixia/phpldapadmin:...
    ports:
      - "10443:443"
```

**確認ポイント**: テンプレート変数が展開され, 環境変数(`LDAP_ORGANISATION`, `LDAP_DOMAIN`)とポートマッピング(389:389, 10443:443)が記載されていることを確認します。

#### Step 2: コンテナ起動状態確認

**実施ノード**: LDAPサーバコンテナ動作ホスト

**コマンド**:
```bash
docker ps
```

**期待される出力例**:
```
CONTAINER ID   IMAGE                    COMMAND                  CREATED        STATUS       PORTS                                             NAMES
abcd1234efgh   osixia/openldap:...      "/container/tool/run"   5 minutes ago  Up 5 minutes 0.0.0.0:389->389/tcp                openldap
ijkl5678mnop   osixia/phpldapadmin:...  "/container/tool/run"   5 minutes ago  Up 5 minutes 0.0.0.0:10443->443/tcp              phpldapadmin
```

**確認ポイント**: 以下の項目が確認できることを確認します:
- osixia/openldap コンテナが Up 状態で動作していること
- osixia/phpldapadmin コンテナが Up 状態で動作していること
- ポート 389 がマッピングされていること
- ポート 10443 がマッピングされていること

#### Step 3: OpenLDAP サービス接続確認

**実施ノード**: LDAPサーバコンテナ動作ホスト

**コマンド**:
```bash
ldapsearch -x -H ldap://localhost:389 -b "dc=example,dc=com" -s base
```

**期待される出力例**:
```
# extended LDIF
#
# LDAPv3
# base <dc=example,dc=com> with scope baseObject
# filter: (objectclass=*)
# requesting: ALL
#

# example.org
dn: dc=example,dc=com

searchResult: success
resultCode: 0 (Success)
```

**確認ポイント**: 以下の項目が確認できることを確認します:
- LDAPサーバがポート389で応答していること (resultCode: 0 Success)
- ベース DN(dc=example,dc=com)が正しく返されていること
- 検索コマンドがエラーなく完了していること

#### Step 4: phpLDAPadmin Web UI ログイン確認

**実施ノード**: クライアントPC

**アクセスURL**:
```
https://mgmt-server.local:10443/
```

**ログイン情報**:
- Login DN: `cn=admin,dc=example,dc=com`
- Password: `admin`

**期待される状態**: ログイン成功後, phpLDAPadminのダッシュボードが表示され, ディレクトリツリーが左パネルに表示されます。

**確認ポイント**: 以下の項目が確認できることを確認します:
- HTTPS接続でWebサイトにアクセスできること
- ログイン画面が表示されること
- 入力したログイン情報で認証成功すること
- ディレクトリツリーが表示され, ディレクトリエントリの検索・参照・編集操作が可能なこと

#### Step 5: LDAP エントリ作成テスト

**実施ノード**: LDAPサーバコンテナ動作ホスト

**テスト手順**: phpLDAPadmin Web UI またはコマンドラインから新規 OU エントリを作成します。

**作成コマンド例**:
```bash
ldapadd -x -D "cn=admin,dc=example,dc=com" -w admin <<EOF
dn: ou=testunit,dc=example,dc=com
objectClass: organizationalUnit
ou: testunit
EOF
```

**確認コマンド**:
```bash
ldapsearch -x -H ldap://localhost:389 -b "ou=testunit,dc=example,dc=com" -s base
```

**期待される出力例**:
```
# extended LDIF
# base <ou=testunit,dc=example,dc=com> with scope baseObject

dn: ou=testunit,dc=example,dc=com
objectClass: organizationalUnit
ou: testunit

searchResult: success
resultCode: 0 (Success)
```

**確認ポイント**: 以下の項目が確認できることを確認します:
- ldapadd コマンドがエラーなく完了していること (または Web UI で作成成功)
- ldapsearch で新規作成したエントリが検索結果に表示されていること (resultCode: 0 Success)
- LDAP ディレクトリへの書き込みと読み取り機能が正常に動作していること

#### Step 6: sysctl 設定確認

**実施ノード**: LDAPサーバコンテナ動作ホスト

**コマンド**:
```bash
sysctl net.ipv4.ip_forward net.ipv6.conf.all.forwarding
```

**期待される出力例**:
```
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
```

**確認ポイント**: 以下の項目が確認できることを確認します:
- `net.ipv4.ip_forward` が `1`(有効)に設定されていること
- `net.ipv6.conf.all.forwarding` が `1`(有効)に設定されていること
- これらの設定により, Dockerネットワーク通信が正常に動作することが保証されます

#### Step 7: バックアップスクリプト動作確認

**実施ノード**: LDAPサーバコンテナ動作ホスト

**テスト手順**:
```bash
cd /tmp
/data/openldap/scripts/backup-ldap-data.sh
ls -la config-backup.tar data-backup.tar phpadmin-backup.tar
```

**期待される出力例**:
```
-rw-r--r-- 1 root root  10240 Mar  7 10:30 config-backup.tar
-rw-r--r-- 1 root root  20480 Mar  7 10:31 data-backup.tar
-rw-r--r-- 1 root root  51200 Mar  7 10:32 phpadmin-backup.tar
```

**確認ポイント**: 以下の項目が確認できることを確認します:
- バックアップスクリプト (`/data/openldap/scripts/backup-ldap-data.sh`) がエラーなく完了していること
- `config-backup.tar` (LDAP設定)が生成されていること
- `data-backup.tar` (LDAPデータベース)が生成されていること
- `phpadmin-backup.tar` (phpLDAPadminデータ)が生成されていること
- 全ファイルがサイズを持つ正常なアーカイブファイルとして生成されていること

## トラブルシューティング

### 1. docker compose 実行時にコマンドエラーとなる場合

**実施対象ホスト**: LDAPサーバコンテナ動作ホスト

**実行するコマンド**:

```bash
docker --version
docker compose version
sudo systemctl status docker --no-pager
```

**確認ポイント**:

- Docker Compose v2 が利用可能であること。
- Docker デーモンが起動中であること。
- 停止している場合は Docker デーモンを起動してから再実行すること。

### 2. OpenLDAP / phpLDAPadmin コンテナが起動しない場合

**実施対象ホスト**: LDAPサーバコンテナ動作ホスト

**実行するコマンド**:

```bash
cat /data/openldap/docker/docker-compose.yml
docker ps -a
docker compose -f /data/openldap/docker/docker-compose.yml logs
ss -ltnp | grep -E ':(389|10443) '
```

**確認ポイント**:

- Docker Compose 定義ファイル (`docker-compose.yml`) の定義が想定どおりであること。
- コンテナログに起動失敗原因が出ていないこと。
- ポート競合がないこと。

### 3. ロール実行後に LDAP 接続できない場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
grep -nE '^(ldap_organization|ldap_domain|ldap_admin_password):' vars/all-config.yml group_vars/all/all.yml host_vars/*.yml
```

**確認ポイント**:

- ldap_organization, ldap_domain, ldap_admin_password が定義済みであること。
- 3変数が空文字列ではないこと。
- 未設定の場合は設定後にロールを再実行すること。

### 4. phpLDAPadmin へログインできない場合

**実施対象ホスト**: LDAPサーバコンテナ動作ホスト

**実行するコマンド**:

```bash
docker compose -f /data/openldap/docker/docker-compose.yml ps
docker compose -f /data/openldap/docker/docker-compose.yml logs phpldapadmin
```

**確認ポイント**:

- Login DN が cn=admin,dc=... 形式であること。
- Login DN が ldap_domain と整合すること。
- 管理者パスワードが ldap_admin_password と一致すること。

### 5. バックアップ/リストアスクリプトが失敗する場合

**実施対象ホスト**: LDAPサーバコンテナ動作ホスト

**実行するコマンド**:

```bash
docker ps
ls -l /data/openldap/scripts/*.sh
ls -l config-backup.tar data-backup.tar phpadmin-backup.tar
```

**確認ポイント**:

- 対象コンテナが起動していること。
- スクリプトに実行権限が付与されていること。
- リストア時は必要な tar ファイルが存在すること。

### 6. LDAP データが再起動後に消える場合

**実施対象ホスト**: LDAPサーバコンテナ動作ホスト

**実行するコマンド**:

```bash
grep -n 'volumes:' -A20 /data/openldap/docker/docker-compose.yml
ls -ld /data/openldap/slapd/database /data/openldap/slapd/config
```

**確認ポイント**:

- volume 定義と実ディレクトリが一致していること。
- /data/openldap/slapd/database と /data/openldap/slapd/config が存在すること。
- UID/GID 911 の所有権設定が運用方針と一致すること。

### 7. sysctl 設定が反映されず通信が不安定な場合

**実施対象ホスト**: LDAPサーバコンテナ動作ホスト

**実行するコマンド**:

```bash
sysctl net.ipv4.ip_forward net.ipv6.conf.all.forwarding
cat /etc/sysctl.d/90-ldap-forwarding.conf
sudo sysctl --system
```

**確認ポイント**:

- net.ipv4.ip_forward と net.ipv6.conf.all.forwarding が想定値であること。
- /etc/sysctl.d/90-ldap-forwarding.conf の設定値が手動変更と競合していないこと。
- 再読込後に設定値が維持されること。

## 注意事項

このセクションでは, ldap-serverロールの運用や拡張の際に参考となる追加情報を記載します。

### Docker Compose v2 について

本ロールはDocker Compose v2(Composeコマンド)を使用することを前提としています。Docker Engine 20.10以上の環境で`docker compose`コマンド(ハイフンなし)で実行します。

```bash
docker compose -f docker-compose.yml up -d
docker compose -f docker-compose.yml down
docker compose -f docker-compose.yml ps
```

### ボリューム永続化について

OpenLDAPデータベースとphpLDAPadmin設定データを専用ボリュームに保存する仕様とした背景配下の通り:

- **コンテナのリサイクル**: コンテナを削除, 再作成しても, ボリューム内のデータは永続化される
- **バックアップの簡素化**: ボリューム内のファイルをホスト側からアクセス可能なため, バックアップスクリプトで容易に抽出できる
- **パフォーマンス**: ボリュームを適切に設定することで, コンテナ間のI/O性能が向上する可能性がある

### セキュリティ考慮事項

OpenLDAPサーバ部に関してセキュリティ要件に応じて以下の点を検討することが推奨されます:

- **ネットワークセグメンテーション**: LDAPサーバは内部ネットワークのみに公開し, 外部からの直接接続は避ける
- **TLS/SSL通信**: 本番環境ではTLS/SSL(Secure Sockets Layer, 安全なソケットレイヤ)を有効にしたLDAPS(LDAP over SSL, SSL/TLS経由のLDAP)通信を推奨
- **認証情報の管理**: bind DNやパスワードは環境変数や秘密管理ツールで管理し, Readmeや設定ファイルにハードコードしない

### バージョン管理

OpenLDAPコンテナイメージは osixia/openldap GitHub リポジトリで複数バージョンが公開されています。本ロール実装時のイメージバージョンは以下から確認可能です。

- `roles/ldap-server/defaults/main.yml` の `ldap_image_version` 変数
- `roles/ldap-server/templates/docker-compose.yml.j2` のimage定義

### 運用推奨事項

以下の運用が推奨されます。

- **定期的なバックアップ**: 少なくとも月1回程度の頻度でバックアップスクリプトを実行し, ディレクトリエントリの保護を確保する
- **ログ監視**: Docker コンテナのログを定期的に確認し, エラーやトラブルシューティング情報を収集する
- **セキュリティアップデート**: osixia/openldap イメージの新バージョンリリース情報を追跡し, セキュリティアップデートが公開された際は迅速に適用する
- **ディレクトリ設計**: LDAPディレクトリツリー構造の設計段階で, エントリの検索性能やメンテナンス性を考慮する

## 付録: `backup-ldap-data.sh`スクリプトの内容

```bash
#!/bin/sh
#  -*- coding:utf-8 mode:bash -*-
#
# busyboxのコンテナイメージを使用して, 以下の内容をopenldapコンテナ内
# の以下のファイルをカレントディレクトリにtar形式で保存する
#
# a) openldapの設定ファイル(openldapのコンテナ中の/etc/ldap/slapd.d ディレクトリの内容)
# b) openldapのデータベース(openldapのコンテナ中の/var/lib/ldap ディレクトリの内容)
# c) phpldapadminの設定 (phpldapadminのコンテナ中の/var/www/phpldapadmin ディレクトリの内容)
#

# 1) openldapのコンテナIDを取得する
ldap_container_id=`docker ps|grep osixia/openldap:|awk -F ' ' '{print $1;}'`

# 2) phpldapadminのコンテナIDを取得する
phpadmin_container_id=`docker ps|grep osixia/phpldapadmin:|awk -F ' ' '{print $1;}'`

# 3) ホストのカレントディレクトリをコンテナ内の/backupディレクトリにマウントして
# busyboxのコンテナを生成, openldapコンテナ内のボリュームを参照し,
# openldapの設定ファイルディレクトリ(/etc/ldap/slapd.d)の内容をカレントディ
# レクトリのconfig-backup.tarにtar形式で保存する
docker run --rm --volumes-from "${ldap_container_id}" -v `pwd`:/backup busybox tar cvf /backup/config-backup.tar /etc/ldap/slapd.d

# 4) ホストのカレントディレクトリをコンテナ内の/backupディレクトリにマウントして
# busyboxのコンテナを生成, openldapコンテナ内のボリュームを参照し,
# openldapのデータベースディレクトリ(/var/lib/ldap)の内容をカレントディ
# レクトリのconfig-backup.tarにtar形式で保存する
docker run --rm --volumes-from "${ldap_container_id}" -v `pwd`:/backup busybox tar cvf /backup/data-backup.tar /var/lib/ldap

# 5) ホストのカレントディレクトリをコンテナ内の/backupディレクトリにマウントして
# busyboxのコンテナを生成, phpldapadminコンテナ内のボリュームを参照し,
# phpladpadminの設定ファイルディレクトリ(/var/www/phpldapadmin)の内容をカレントディ
# レクトリのphpadmin-backup.tarにtar形式で保存する
docker run --rm --volumes-from "${phpadmin_container_id}" -v `pwd`:/backup busybox tar cvf /backup/phpadmin-backup.tar /var/www/phpldapadmin
```

## 参考資料

### 公式ドキュメント

- [OpenLDAP Official Documentation](https://www.openldap.org/doc/) OpenLDAPの公式ドキュメント, 設定リファレンス, トラブルシューティング等を提供
- [osixia/openldap GitHub Repository](https://github.com/osixia/docker-openldap) 本ロールで使用しているopenldapのDockerイメージのソースコード, 設定例, 既知の問題等を提供
- [osixia/phpldapadmin GitHub Repository](https://github.com/osixia/docker-phpldapadmin) phpLDAPadminのDockerイメージのソースコード, 使用方法, トラブルシューティング情報を提供
