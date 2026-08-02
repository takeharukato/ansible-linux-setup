# Redmine

本ロールは, Redmine を導入するロールです。

## 目次

- [Redmine](#redmine)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
    - [主な処理](#主な処理)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
  - [ポートマッピング(ホストとコンテナ間)定義一覧](#ポートマッピングホストとコンテナ間定義一覧)
  - [ボリューム名,コンテナ外(外部ボリューム実体名),コンテナ内マウント先ディレクトリの対応表](#ボリューム名コンテナ外外部ボリューム実体名コンテナ内マウント先ディレクトリの対応表)
    - [ボリューム実体パスについて](#ボリューム実体パスについて)
      - [事前条件](#事前条件)
      - [Mountpoint の確認](#mountpoint-の確認)
      - [実体パスの変動要因](#実体パスの変動要因)
      - [コンテナ内マウントポイントとの突合確認手順](#コンテナ内マウントポイントとの突合確認手順)
  - [環境変数一覧](#環境変数一覧)
    - [`redmine` サービス](#redmine-サービス)
    - [`redmine-db` サービス](#redmine-db-サービス)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
    - [バックアップスクリプト](#バックアップスクリプト)
    - [リストアスクリプト](#リストアスクリプト)
    - [定期バックアップ](#定期バックアップ)
  - [docker volume inspect を用いたバックアップ, リストア, 権限整合確認手順](#docker-volume-inspect-を用いたバックアップ-リストア-権限整合確認手順)
    - [Redmineの添付ファイル ( {{redmine\_files\_volume}} )](#redmineの添付ファイル--redmine_files_volume-)
      - [バックアップ](#バックアップ)
      - [リストア](#リストア)
      - [権限整合 (Redmine添付ファイル)](#権限整合-redmine添付ファイル)
    - [PostgreSQL データ ( {{redmine\_database\_volume}} )](#postgresql-データ--redmine_database_volume-)
      - [論理バックアップ](#論理バックアップ)
      - [論理リストア](#論理リストア)
      - [PostgreSQLの論理バックアップの内容について](#postgresqlの論理バックアップの内容について)
      - [オフラインボリュームコピー](#オフラインボリュームコピー)
      - [権限整合 (PostgreSQLデータ)](#権限整合-postgresqlデータ)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
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
| アプリケーション | - | 利用者の目的を実現するために動作するソフトウェア。 |
| パッケージ | - | ソフトウェア導入に必要なファイルをまとめた配布単位。 |
| リポジトリ | - | ソフトウェアや設定情報を保管し, 取得できるようにした管理場所。 |
| コマンド | - | 実行者が計算機へ処理を指示するための命令。 |
| ホスト | - | 管理対象として識別される個別の計算機。 |
| サーバ | - | 他の機器や利用者へ機能やデータを提供する計算機, 又はその役割。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
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
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| API | - | アプリケーション同士がやり取りする方法を定めた仕様。 |
| URL | - | WWW 上の資源の場所を示す文字列。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Docker Compose | - | 複数のコンテナからなるマルチコンテナアプリケーション(docker-compose.yml)を一括管理, 起動するツール |
| サービス | - | 機能を利用者や他システムへ提供する仕組み。 |
| ポート | - | 通信の出入口を識別する番号または接点。 |
| Port publishing | ポート公開 | ホスト側のポート番号を, コンテナ側のポート番号に結び付ける設定。 |
| Docker volume | ボリューム | コンテナを再作成しても残る保存領域。 |
| External volume | 外部ボリューム | Compose 実行前に作成済みのボリューム。 |
| Domain Name System | DNS | 名前と IP アドレスを対応付ける仕組み。 |
| Container | コンテナ | コンテナの英語表記。 |
| Database | DB | データを整理して保存し, 検索や更新を行う仕組み。 |
| Hypertext Transfer Protocol | HTTP | HTTP の正式名称。 |
| Network File System | NFS | ネットワーク越しにファイル共有を行う仕組み。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Transmission Control Protocol | TCP | 通信相手との接続を確立してからデータを送受信する通信方式。 |
| Virtual Machine | VM | 1台の物理計算機上で動作する仮想的な計算機。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| Interface | IF | 装置や機能の接続点。 |
| On | ON | 有効状態を示す値。 |
| Router Advertisement | RA | IPv6 で経路情報を通知する仕組み。 |
| Data Definition Language | DDL | データ構造を定義するための SQL 命令群。 |
| Data Manipulation Language | DML | データの追加, 更新, 削除を行う SQL 命令群。 |
| Foreign Data Wrapper | FDW | 外部データ源をデータベース表のように扱う仕組み。 |
| Write-Ahead Logging | WAL | 障害復旧のために更新内容を先に記録する仕組み。 |
| Windows Subsystem for Linux 2 | WSL2 | Windows 上で Linux 環境を実行する仕組み。 |
| Structured Query Language CREATE Statement | CREATE | データベース要素を新規作成する SQL 命令。 |
| Structured Query Language ALTER Statement | ALTER | 既存のデータベース要素を変更する SQL 命令。 |
| Structured Query Language ADD Clause | ADD | 列や制約を追加する SQL 句。 |
| Structured Query Language COMMENT Statement | COMMENT | データベース要素へ説明文を付与する SQL 命令。 |
| Structured Query Language CONSTRAINT Clause | CONSTRAINT | データ整合性を保つ制約を定義する SQL 句。 |
| Structured Query Language DOMAIN | DOMAIN | 利用可能な値の集合を定義するデータ型定義。 |
| Structured Query Language EVENT | EVENT | 特定条件で起動する処理を扱う定義要素。 |
| Structured Query Language EXTENSION | EXTENSION | 機能拡張を提供する追加モジュール。 |
| Structured Query Language FUNCTION | FUNCTION | 入力値に応じた計算結果を返す定義済み処理。 |
| Structured Query Language GRANT Statement | GRANT | 利用権限を付与する SQL 命令。 |
| Structured Query Language INDEX | INDEX | 検索を高速化する補助データ構造。 |
| Structured Query Language INSERT Statement | INSERT | 行を追加する SQL 命令。 |
| Structured Query Language MATERIALIZED VIEW | MATERIALIZED | 結果を保存するビューの種類。 |
| Structured Query Language NULL | NULL | 値が未設定であることを示す特殊値。 |
| Structured Query Language OWNER | OWNER | データベースオブジェクトの所有者を示す属性。 |
| Structured Query Language PROCEDURE | PROCEDURE | 副作用を伴う処理を実行する定義済み手続き。 |
| Structured Query Language REVOKE Statement | REVOKE | 利用権限を取り消す SQL 命令。 |
| Structured Query Language SCHEMA | SCHEMA | データベース要素を論理的にまとめる名前空間。 |
| Structured Query Language SELECT Statement | SELECT | 条件に合うデータを取得する SQL 命令。 |
| Structured Query Language SEQUENCE | SEQUENCE | 連番を生成するためのオブジェクト。 |
| Structured Query Language SET Statement | SET | 設定値を変更する SQL 命令。 |
| Structured Query Language TABLE | TABLE | 行と列で構成されるデータ格納構造。 |
| Structured Query Language TRIGGER | TRIGGER | 特定操作時に自動実行する処理定義。 |
| Structured Query Language TYPE | TYPE | データの型を定義する要素。 |
| Structured Query Language UNIQUE Constraint | UNIQUE | 重複値を禁止する制約。 |
| Structured Query Language VIEW | VIEW | 問い合わせ結果を仮想表として扱う仕組み。 |
| Structured Query Language LO | LO | 大きなバイナリデータを保持する領域。 |
| Structured Query Language NOT | NOT | 条件の否定を表す演算子。 |
| Structured Query Language TO Clause | TO | 適用先を指定する SQL 句。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `chown` | - | ファイルやディレクトリの所有者, 所有グループを変更するコマンド。 |
| `crontab` | - | 定期実行設定を登録, 表示, 削除するコマンド。 |
| `docker` | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| `sysctl` | - | カーネル動作パラメタを参照, 変更するコマンド。 |
| `tar` | - | 複数ファイルを一つにまとめる, 展開するコマンド。 |
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| データベース | - | 検索や更新ができるよう整理した情報の集合。 |
| ブロック | - | ひとかたまりとして扱う処理単位や領域。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |

## 概要
Redmine導入ロール。
本ロールを適用すると,
```:text
http://ホスト名:8080/
```
でRedmineサーバにアクセス可能となる。
以下, {{と}}で囲んだ文字列はansible playbookの変数名を表す。
実行例中, `$`は一般ユーザのシェルプロンプト, `#`は`root`ユーザのシェルプロンプトを意味します。

本ロールは, redmine-server に関する設定処理を実施します。

### 主な処理

本ロールは, 以下の処理を行います。

1. Redmineを公式コンテナイメージから導入
2. Redmineのバックアップ/リストア作業スクリプトの導入

## 前提条件

本ロールの実行者は, 対象ホストが inventory に登録済みであることを確認します。
本ロールの実行者は, 関連する共通変数が vars/all-config.yml または host_vars に定義済みであることを確認します。

## 実行方法

実行者は制御ホストで以下のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts site.yml --tags "redmine-server"
```

## 主要変数

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| (該当なし) | 本ロール実装にはロール全体の実行可否を切り替える `*_enabled` 変数はありません。 | - | - |
| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `redmine_dir_prefix` | `/data/redmine` | Redmine サーバ用ディレクトリのベースパス。 |
| `redmine_docker_dir` | `{{redmine_dir_prefix}}/docker` | docker-compose.yml の配置先ディレクトリ。 |
| `redmine_scripts_dir` | `{{redmine_dir_prefix}}/scripts` | バックアップ/リストア用スクリプトの配置先。 |
| `redmine_backup_dir` | `{{redmine_dir_prefix}}/backup` | バックアップファイル保存先ディレクトリ。 |
| `redmine_files_volume` | `redmine_vol_files` | 添付ファイル用 Docker ボリューム名。 |
| `redmine_database_volume` | `redmine_vol_pgdata` | PostgreSQL データ用 Docker ボリューム名。 |
| `redmine_files_base_name` | `redmine_files` | 添付ファイルバックアップのベース名。 |
| `redmine_files_backup_name` | `{{redmine_files_base_name}}.tgz` | 添付ファイルバックアップのファイル名。 |
| `redmine_dbdata_backup_name` | `redmine.dump` | PostgreSQL 論理バックアップのファイル名。 |
| `redmine_dbdata_backup_gzip` | `{{redmine_dbdata_backup_name}}.gz` | PostgreSQL 論理バックアップの gzip 圧縮名。 |
| `redmine_image` | `redmine:5.0.4-bullseye` | Redmine コンテナイメージ。 |
| `redmine_service` | `redmine` | Redmine サービス名 (docker compose)。 |
| `redmine_service_port` | `8080` | Redmine 公開ポート (ホスト側)。 |
| `redmine_admin_password` | `admin` | Redmine 管理者パスワード (未定義/空の場合は `admin`)。 |
| `redmine_wait_host_stopped` | `"127.0.0.1"` | Redmineサービス停止を待ち合わせる(接続先)ホスト名/IPアドレス。 |
| `redmine_wait_host_started` | `"{{ inventory_hostname }}"` | Redmineサービス開始を待ち合わせる(接続先)ホスト名/IPアドレス。 |
| `redmine_wait_timeout` | `300` | Redmineサービス待ち合わせ時間(単位: 秒)。 |
| `redmine_wait_delay` | `5` | Redmineサービス待ち合わせる際の開始遅延時間(単位: 秒)。 |
| `redmine_wait_sleep` | `2` | Redmineサービス待ち合わせる際の待機間隔(単位: 秒)。 |
| `redmine_wait_delegate_to` | `"localhost"` | Redmineサービス待ち合わせる際の接続元ホスト名/IPアドレス。 |
| `redmine_db_image` | `postgres:15.1-bullseye` | PostgreSQL コンテナイメージ。 |
| `redmine_db_service` | `redmine-db` | PostgreSQL サービス名 (docker compose)。 |
| `redmine_db_name` | `redmine` | PostgreSQL データベース名。 |
| `redmine_db_user` | `redmine_user` | PostgreSQL ユーザ名。 |
| `redmine_db_password` | `redmine_password` | PostgreSQL パスワード。 |
| `redmine_backup_rotation` | `7` | デイリーバックアップの保持世代数。 |
| `redmine_backup_mount_point` | `/mnt` | NFS マウントポイント。 |
| `redmine_backup_dir_on_nfs` | `/redmine-backup` | NFS 配下のバックアップ配置先ディレクトリ。 |
| `redmine_backup_output_dir` | `{{redmine_backup_mount_point}}{{ redmine_backup_dir_on_nfs }}` | NFS 上のバックアップ出力先フルパス。 |
| `redmine_backup_nfs_server` | `""` | デイリーバックアップ先の NFS サーバ。 |
| `redmine_backup_nfs_dir` | `/share` | デイリーバックアップ用 NFS 共有ディレクトリ。 |
| `redmine_enable_backup_script` | `false` | バックアップスクリプト生成有効化フラグ。`true` に設定すると, backup-redmine-data.sh と restore-redmine-data.sh が配置されます。daily-backup-redmine.sh を配置するには, さらに `redmine_backup_nfs_server` と `redmine_backup_nfs_dir` が非空である必要があります。不要な環境では `false` に設定するとスクリプト生成をスキップできます。 |
| `mgmt_nic` | (環境依存) | 管理用ネットワークインターフェース名。sysctl 設定で RA (Router Advertisement, ルータ広告) 受信を有効化する際に使用します。|

## ポートマッピング(ホストとコンテナ間)定義一覧

| サービス名 | ホスト側ポート | コンテナ側ポート | プロトコル | 厳密な用途 |
|---|---:|---:|---|---|
| `redmine` | `{{redmine_service_port}}` | `3000` | TCP | Redmine ( Ruby on Rails アプリケーション ) の HTTP 待受。ホスト `{{redmine_service_port}}/TCP` への接続がコンテナ `3000/TCP` へ転送される。 |
| `redmine-db` | `5432` | `5432` | TCP | PostgreSQL 既定ポートの外部公開。 内部接続のみで足りる場合は `ports:` を削除 します。 |

## ボリューム名,コンテナ外(外部ボリューム実体名),コンテナ内マウント先ディレクトリの対応表

| 論理ボリューム名 | 外部ボリューム実体名 | コンテナ内マウント先 | 対象サービス | コンテナ内データの意味 |
|---|---|---|---|---|
| `vol_redmine` | `{{redmine_files_volume}}` | `/usr/src/redmine/files` | `redmine` | Redmine の添付ファイルなどの永続データ。 |
| `vol_redmine_db` | `{{redmine_database_volume}}` | `/var/lib/postgresql/data` | `redmine-db` | PostgreSQL のデータクラスタ。 |

### ボリューム実体パスについて

#### 事前条件

本設定では, `external: true` のため, 外部ボリュームは Compose 起動前に存在している必要がある。事前作成手順は以下の通り。

```bash
docker volume create {{redmine_files_volume}}
docker volume create {{redmine_database_volume}}
```

#### Mountpoint の確認

各ボリュームのMountpoint確認方法は以下の通り。

```bash
# ボリューム一覧
docker volume ls

# 各ボリュームの実体パスを取得
docker volume inspect -f '{{ .Mountpoint }}' {{redmine_files_volume}}
docker volume inspect -f '{{ .Mountpoint }}' {{redmine_database_volume}}
```

実行例を以下に示す:

```shell
$ docker volume ls
DRIVER    VOLUME NAME
local     0f119a8323fd1f2d01c4d49d75196a21c2c89255c018d321c3afc32e10051cf7
local     2b277adb15dc900b1d3e019b2ec6eb03918a9a1287b3a295991c65366a122537
local     04e42fa6ed66dafc05d403770563afcaba1cd71cedea2870c5bc35e02a684a1b
local     6a6d02d1f4a26c556c31f6fd55c2099e25cdcb020f9c71f291e9c1549930589b
local     9ab10dd3f99ac486a2bf715c9bd27af944f11f1ccb132c69bb011aa98646a72a
local     34d41cb63e26d198c15de7eafc55cf1ab916d0eb03fde74e1d4a87b33b5c4804
local     57da73d71b5f521f67f9454d74356d2279b0f8495248ef375d2a950bc2434d36
local     9986275e7581f612e4295d74d31f985597e55521c7dd07470028f1cb92720a70
local     b2e249b8810b87af11979e1a08dc0a0467b0496478522fcbcfe235e0a88b2ae4
local     bf4df454fb68e09bf9e90242a27970168e5d9383f6f8e8e40ad445d5244ad7f1
local     docker_config
local     docker_data
local     docker_phpadmin_data
local     f738e3ef355b6a1e7685ae4a158cc1b19347ac453e849562f155e13ce7b95d40
local     redmine_vol_files
local     redmine_vol_pgdata
$ docker volume inspect -f '{{ .Mountpoint }}' redmine_vol_files
/var/lib/docker/volumes/redmine_vol_files/_data
$ docker volume inspect -f '{{ .Mountpoint }}' redmine_vol_pgdata
/var/lib/docker/volumes/redmine_vol_pgdata/_data
```

#### 実体パスの変動要因

本設定では, 以下の要因により, ボリュームの実体パスが変動しうる。

- Docker のデータルート ( `data-root` ) 設定。
- rootless Docker ( 例 : `~/.local/share/docker/volumes/.../_data` ) 。
- Docker Desktop / WSL2 / macOS などでは VM 内配置。

コンテナ外から確認する場合は, いずれの場合も `docker volume inspect` 出力が唯一の正確な情報となる。

#### コンテナ内マウントポイントとの突合確認手順

コンテナ内マウントポイントとの突合確認する手順は以下の通り。

```bash
cd /data/redmine/docker
RID=$(docker compose ps -q redmine)
DBID=$(docker compose ps -q redmine-db)

docker exec -it "$RID" sh -lc 'mount | grep "/usr/src/redmine/files"'
docker exec -it "$DBID" sh -lc 'mount | grep "/var/lib/postgresql/data"'
```

実行例を以下に示す:

```shell
$ cd /data/redmine/docker
$ RID=$(docker compose ps -q redmine)
DBID=$(docker compose ps -q redmine-db)

$ docker exec -it "$RID" sh -lc 'mount | grep "/usr/src/redmine/files"'
/dev/xvda2 on /usr/src/redmine/files type ext4 (rw,relatime)
$ docker exec -it "$DBID" sh -lc 'mount | grep "/var/lib/postgresql/data"'
/dev/xvda2 on /var/lib/postgresql/data type ext4 (rw,relatime)
```

## 環境変数一覧

### `redmine` サービス

| 変数名 | 値 | 意味 |
|---|---|---|
| `REDMINE_DB_POSTGRES` | `redmine-db` | DB 接続先ホスト名。内部 DNS 解決される。 |
| `REDMINE_DB_DATABASE` | `redmine` | データベース名。 |
| `REDMINE_DB_USERNAME` | `redmine_user` | DB 認証ユーザ名。 |
| `REDMINE_DB_PASSWORD` | `redmine_password` | DB パスワード。秘匿情報のため平文管理は不適切。 |
| `REDMINE_SECRET_KEY_BASE` | `supersecretkey` | Rails の暗号鍵。長くランダムな値であることが望ましい。 |
| `REDMINE_DB_PORT` | `5432` | DB 接続ポート番号。PostgreSQL 既定。 |

### `redmine-db` サービス

| 変数名 | 値 | 意味 |
|---|---|---|
| `POSTGRES_DB` | `redmine` | 初回起動時に作成するデータベース名。 |
| `POSTGRES_USER` | `redmine_user` | 初回起動時に作成するロール／ユーザ。 |
| `POSTGRES_PASSWORD` | `redmine_password` | 上記ユーザのパスワード。秘匿情報であり平文管理は不適切。 |

## テンプレートと生成ファイル

本ロールを適用すると, `/data/redmine`配下に以下のファイルが作られる

- backup ディレクトリ デイリーバックアップファイル保存ディレクトリ
  - redmine.dump.gz Redmineデータベースのバックアップ ( PostgreSQLの論理バックアップ )ファイルのgzip形式圧縮ファイル
  - redmine_files.tgz Redmineに登録されたファイル(添付ファイルなど)をバックアップしたtar.gz形式の圧縮ファイル
- docker ディレクトリ
  - docker-compose.yml Redmineサーバを立てるためのdocker composeファイル
- scripts ディレクトリ
  - backup-redmine-data.sh Redmineのデータベース, Redmineに登録されたファイル(添付ファイルなど)をバックアップするためのスクリプト
  - restore-redmine-data.sh バックアップファイルの内容をRedmineに反映するためのスクリプト
  - daily-backup-redmine.sh backup-redmine-data.shを用いて, `backup` ディレクトリにバックアップファイルを作成するためのスクリプト。crontabに登録することで定期バックアップを採取するために使用します。

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `docker-compose.yml.j2` | `/data/redmine/docker/docker-compose.yml` (既定: `/data/redmine/docker/docker-compose.yml`) | Redmine 本体と PostgreSQL (ポストグレスキューエル, リレーショナルデータベース管理システム) の Docker Compose 定義ファイル。コンテナの環境変数, ポートマッピング, ボリューム設定を含みます。 |
| `backup-redmine-data.sh.j2` | `/data/redmine/scripts/backup-redmine-data.sh` (既定: `/data/redmine/scripts/backup-redmine-data.sh`) | Redmine のデータベースと添付ファイルをバックアップするスクリプト。PostgreSQL の論理バックアップ (`pg_dump`) と添付ファイルの tar アーカイブを作成します。 |
| `restore-redmine-data.sh.j2` | `/data/redmine/scripts/restore-redmine-data.sh` (既定: `/data/redmine/scripts/restore-redmine-data.sh`) | バックアップアーカイブから Redmine のデータベースと添付ファイルをリストアするスクリプト。PostgreSQL の論理リストア (`pg_restore`) と tar 展開を実行します。 |
| `daily-backup-redmine.sh.j2` | `/data/redmine/scripts/daily-backup-redmine.sh` (既定: `/data/redmine/scripts/daily-backup-redmine.sh`) | デイリーバックアップを NFS (Network File System, ネットワークファイルシステム) サーバにコピーするスクリプト。crontab に登録して定期バックアップを実行します。 |
| `90-redmine-forwarding.conf.j2` | `/etc/sysctl.d/90-redmine-forwarding.conf` (既定: `/etc/sysctl.d/90-redmine-forwarding.conf`) | IPv4/IPv6 フォワーディングと RA 受信を有効化する sysctl 設定ファイル。Docker ネットワークの正常動作に必要です。 |

### バックアップスクリプト

本ロールでは, `backup-redmine-data.sh`というバックアップスクリプトを用意している。

本バックアップスクリプトは, 以下のように実行します。

```:shell
backup-redmine-data.sh
```

実行を完了すると, `/data/redmine/backup`にバックアップファイル, `redmine.dump.gz`,`redmine_files.tgz`が生成される。

### リストアスクリプト

本ロールでは, `restore-redmine-data.sh`というリストアスクリプトを用意している。

`/data/redmine/backup`に, 各バックアップファイルを, 前節で記載したファイル名(`redmine.dump.gz`, `redmine_files.tgz`)で配置してから, 以下のように, `restore-redmine-data.sh`を実行することで, Redmineの状態を復元することができます。

```:shell
restore-redmine-data.sh
```

### 定期バックアップ

`crontab -e`コマンドで以下のcrontabエントリを作成します。
以下の設定では, 毎日午前3時に`/data/redmine/backup`にバックアップファイルを生成後,
`{{redmine_backup_nfs_server}}:{{redmine_backup_nfs_dir}}`をマウントポイントに指定して,
NFSサーバをマウントし, バックアップファイルを当該ディレクトリにコピーします。

```:text
0 3 * * * /data/redmine/scripts/daily-backup-redmine.sh
```

NFSサーバ上に配置されるバックアップファイルには, 以下のような世代番号が付けられる。

- redmine.dump-世代番号.gz Redmineデータベースのバックアップ ( PostgreSQLの論理バックアップ )ファイルのgzip形式圧縮ファイル
- redmine_files-世代番号.tgz Redmineに登録されたファイル(添付ファイルなど)をバックアップしたtar.gz形式の圧縮ファイル

世代番号を除いた形式にこれらのファイルの名前を変更し, `/data/redmine/backup`にファイルを配置して, `restore-redmine-data.sh`を実行することで, Redmineの状態を復元することができます。
## docker volume inspect を用いたバックアップ, リストア, 権限整合確認手順

本節では, docker volume inspect を用いたバックアップ手順, リストア手順, 権限の整合性を確認する手順を示す。

### Redmineの添付ファイル ( {{redmine_files_volume}} )

本節では, Redmineの添付ファイルのバックアップ手順, リストア手順, 権限の整合性を確認する手順を示す。

#### バックアップ

本節では, Redmineの添付ファイルのバックアップ手順を示す。

```bash
cd /data/redmine/docker
mp=$(docker volume inspect -f '{{ .Mountpoint }}' {{redmine_files_volume}})
tar -C "$mp" -cf redmine-files-$(date +%F).tar .
```

実行例を以下に示す:

```shell
# cd /data/redmine/docker
# mp=$(docker volume inspect -f '{{ .Mountpoint }} ' redmine_vol_files)
# tar -C "$mp" -cf redmine-files-$(date +%F).tar .
#
```

#### リストア

本節では, Redmineの添付ファイルのリストア手順を示す。

```bash
cd /data/redmine/docker
docker compose stop redmine
mp=$(docker volume inspect -f '{{ .Mountpoint }}' {{redmine_files_volume}})
tar -C "$mp" -xf redmine-files-YYYY-MM-DD.tar
docker compose start redmine
```

実行例を以下に示す:

```shell
# cd /data/redmine/docker
# docker compose stop redmine
[+] stop 1/1
 ✔ Container docker-redmine-1 Stopped                                                 0.1s
# mp=$(docker volume inspect -f '{{ .Mountpoint }}' redmine_vol_files)
# tar -C "$mp" -xf redmine-files-2026-02-08.tar
# docker compose start redmine
[+] start 1/1
 ✔ Container docker-redmine-1 Started
```

#### 権限整合 (Redmine添付ファイル)

本節では, Redmineの添付ファイルの権限の整合性を確認し, 設定する手順を示す。

```bash
cd /data/redmine/docker
RID=$(docker compose ps -q redmine)

uid=$(docker exec -it "$RID" sh -lc 'id -u' | tr -d '\r')
gid=$(docker exec -it "$RID" sh -lc 'id -g' | tr -d '\r')
mp=$(docker volume inspect -f '{{ .Mountpoint }}' {{redmine_files_volume}})
chown -R "$uid:$gid" "$mp"
```

実行例を以下に示す:

```shell
# cd /data/redmine/docker
# RID=$(docker compose ps -q redmine)
# uid=$(docker exec -it "$RID" sh -lc 'id -u' | tr -d '\r')
# gid=$(docker exec -it "$RID" sh -lc 'id -g' | tr -d '\r')
# mp=$(docker volume inspect -f '{{ .Mountpoint }}' redmine_vol_files)
# chown -R "$uid:$gid" "$mp"
#
```

### PostgreSQL データ ( {{redmine_database_volume}} )

本節では, PostgreSQL データのバックアップ手順, リストア手順, 権限の整合性を確認する手順を示す。

#### 論理バックアップ

本節では, PostgreSQL データのバックアップ手順(論理バックアップ)手順を示す。

```bash
cd /data/redmine/docker
DBID=$(docker compose ps -q redmine-db)

docker exec -t "$DBID" pg_dump -U redmine_user -d redmine -F c -f /tmp/redmine.dump
docker cp "$DBID":/tmp/redmine.dump ./redmine.dump
```

実行例を以下に示す。

```shell
# cd /data/redmine/docker
# DBID=$(docker compose ps -q redmine-db)
# docker exec -t "$DBID" pg_dump -U redmine_user -d redmine -F c -f /tmp/redmine.dump
# docker cp "$DBID":/tmp/redmine.dump ./redmine.dump
Successfully copied 1.2MB to /data/redmine/docker/redmine.dump
```

#### 論理リストア

本節では, PostgreSQL データのリストア ( 論理バックアップからのリストア ) 手順を示す。

```bash
cd /data/redmine/docker
DBID=$(docker compose ps -q redmine-db)

docker cp ./redmine.dump "$DBID":/tmp/redmine.dump
docker exec -it "$DBID" bash -lc 'pg_restore -U {{redmine_db_user}} -d redmine -c /tmp/redmine.dump'
```

実行例を以下に示す。

```shell
# cd /data/redmine/docker
# DBID=$(docker compose ps -q redmine-db)
# docker cp ./redmine.dump "$DBID":/tmp/redmine.dump
# docker exec -it "$DBID" bash -lc 'pg_restore -U redmine_user -d redmine -c /tmp/redmine.dump'
Successfully copied 1.2MB to 5ed265abcb0a95b5311c6f440552054899c3ed4965c9eaf9dcdd8dbdf7f4d2c7:/tmp/redmine.dump
```

#### PostgreSQLの論理バックアップの内容について

pg_dump が出力する ( または出力可能な ) 主な内容は次のとおり。

- スキーマ定義 ( DDL : Data Definition Language )
  - データベース作成 : -C / --create 指定時に CREATE DATABASE と \connect を含められる ( 未指定時は含めない ) 。
  - スキーマ/検索パス : CREATE SCHEMA, 必要に応じた SET search_path。
  - テーブル : CREATE TABLE ( 列定義, デフォルト値, NOT NULL 等 ) 。
  - インデックス : CREATE INDEX, CREATE UNIQUE INDEX。
  - 制約 : 主キー, 外部キー, ユニーク, チェック制約 ( ALTER TABLE ... ADD CONSTRAINT ) 。
  - ビュー/マテリアライズドビュー : CREATE VIEW / CREATE MATERIALIZED VIEW と依存オブジェクト。
  - シーケンス : CREATE SEQUENCE と後述の現在値設定。
  - 関数/プロシージャ/トリガ : CREATE FUNCTION / CREATE PROCEDURE, CREATE TRIGGER, CREATE EVENT TRIGGER。
  - 型/ドメイン : CREATE TYPE, CREATE DOMAIN。
  - 拡張 : CREATE EXTENSION ( 拡張のインストール宣言。拡張の内部オブジェクトは原則拡張が再作成するため個別には dump されない ) 。
  - コメント : COMMENT ON ... ( コメントを含めるのが既定。--no-comments で除外可 ) 。
  - 所有権/権限 : ALTER ... OWNER TO ..., GRANT/REVOKE ( --no-owner 等で調整可 ) 。
- データ ( DML : Data Manipulation Language ) : プレーンSQL形式 ( -Fp ) では INSERT 文で出力,カスタム形式 ( -Fc ) や ディレクトリ形式 ( -Fd ) ではバイナリ/圧縮ブロックとして格納 ( pg_restore で展開 ) 。
  - シーケンスの現在値 :
ダンプの末尾等で SELECT pg_catalog.setval('schema.seq', <last_value>, <is_called>); を出力し, 自動採番の継続性を担保。
  - ラージオブジェクト ( Large Object, 以下, LO と記す ) :
既定では含まれない。-b / --blobs を指定した場合のみ, lo オブジェクトと参照のダンプを追加。

以下の情報は, 含まれない。

- ロール ( ユーザ/グループ ) , データベース自体の作成権限, テーブルスペース定義などのクラスタ全体のグローバルオブジェクト ( pg_dumpall -g 使用時に採取される ) 。
- Write-Ahead Logging, (以下, WAL と記す)WAL, 物理ページ, 統計情報, 設定ファイル ( postgresql.conf など ) 。
- 外部に依存する実体 ( 例 : 外部ファイル Foreign Data Wrapper (以下, FDW と記す) の実体データ ) は, 定義は出るが中身は対象外。

#### オフラインボリュームコピー

PostgreSQLのボリュームの内容をコピーする手順は以下の通り。

```bash
cd /data/redmine/docker
docker compose stop redmine-db
mp=$(docker volume inspect -f '{{ .Mountpoint }}' {{redmine_database_volume}})
tar -C "$mp" -cf redmine-db-raw-$(date +%F).tar .
docker compose start redmine-db
```

本方式でボリュームの内容をコピーした場合, 異なる版数のPostgreSQLデータベース間でのバックアップ, リストア可能性が保証されないため, 原則以下の手順でのバックアップは行わず, 論理バックアップを使用すること。

#### 権限整合 (PostgreSQLデータ)

本節では, PostgreSQLデータの権限の整合性を確認し, 設定する手順を示す。

```bash
cd /data/redmine/docker
DBID=$(docker compose ps -q redmine-db)
uid=$(docker exec -it "$DBID" bash -lc 'id -u postgres' | tr -d '\r')
gid=$(docker exec -it "$DBID" bash -lc 'id -g postgres' | tr -d '\r')
mp=$(docker volume inspect -f '{{ .Mountpoint }}' {{redmine_database_volume}})
chown -R "$uid:$gid" "$mp"
```

実行例を以下に示す:

```shell
# cd /data/redmine/docker
# DBID=$(docker compose ps -q redmine-db)
# uid=$(docker exec -it "$DBID" bash -lc 'id -u postgres' | tr -d '\r')
# gid=$(docker exec -it "$DBID" bash -lc 'id -g postgres' | tr -d '\r')
# mp=$(docker volume inspect -f '{{ .Mountpoint }}' redmine_vol_pgdata)
# chown -R "$uid:$gid" "$mp"
#
```

## 実行フロー


1. [tasks/load-params.yml](tasks/load-params.yml) で OS 別パッケージ名や共通変数を読み込み。
2. [tasks/directory.yml](tasks/directory.yml) で Docker ボリューム作成, 主要ディレクトリ作成, [templates/docker-compose.yml.j2](templates/docker-compose.yml.j2) を配置します。`redmine_enable_backup_script` が有効な場合, backup-redmine-data.sh ([templates/backup-redmine-data.sh.j2](templates/backup-redmine-data.sh.j2)) と restore-redmine-data.sh ([templates/restore-redmine-data.sh.j2](templates/restore-redmine-data.sh.j2)) を配置します。さらに `redmine_backup_nfs_server` と `redmine_backup_nfs_dir` が非空の場合のみ, daily-backup-redmine.sh ([templates/daily-backup-redmine.sh.j2](templates/daily-backup-redmine.sh.j2)) を配置します。
3. [tasks/sysctl.yml](tasks/sysctl.yml) が `templates/90-redmine-forwarding.conf.j2` を `/etc/sysctl.d/90-redmine-forwarding.conf` に配置し, IPv4/IPv6 フォワーディング (`net.ipv4.ip_forward`, `net.ipv6.conf.all.forwarding`, `net.ipv6.conf.default.forwarding`), 管理 IF (Interface, インターフェース) の RA (Router Advertisement, ルータ広告) 受信 (`net.ipv6.conf.<mgmt_nic>.accept_ra`) を有効化します。配置時は `redmine_reload_sysctl` ハンドラを通知し, `sysctl --system` で設定を反映します。
4. [tasks/service.yml](tasks/service.yml) で `docker compose down` / `docker compose up -d` を実行し, `{{ redmine_service_port }}` の起動待ち合わせを実施。
5. [tasks/service.yml](tasks/service.yml) で Redmine 管理者のパスワードを `redmine_admin_password`変数の設定値に従って設定します。`redmine_admin_password`変数が未定義の場合, または, 設定値が空文字列の場合は, `admin`を管理者パスワード(RedmineのDockerHubコンテナのデフォルト設定値)として設定します。

## 検証ポイント

- `/data/redmine` 以下に docker, scripts, backup ディレクトリが作成されていること。
- `/etc/sysctl.d/90-redmine-forwarding.conf` が配備され, `sysctl net.ipv4.ip_forward`, `sysctl net.ipv6.conf.all.forwarding` が `1` に設定されていること。
- `docker compose -f /data/redmine/docker/docker-compose.yml ps` で Redmine と PostgreSQL (ポストグレスキューエル, リレーショナルデータベース管理システム) コンテナが稼働していること。
- Redmine サービスが `http://ホスト名:8080/` でアクセス可能なこと。
- バックアップスクリプト実行時に `/data/redmine/backup/redmine.dump.gz`, `/data/redmine/backup/redmine_files.tgz` が生成されること。
- リストアスクリプト実行後にバックアップしたプロジェクトやチケットが復元されていること。

## トラブルシューティング

実行者はエラー発生時に build-*.log を確認し, 失敗した task 名と不足変数を特定します。

## 注意事項

実行者は既存の実行順依存を崩さないことを確認した上で本ロールを実行します。

## 参考資料

### 公式ドキュメント

- Redmine: https://www.redmine.org/guide
- PostgreSQL: https://www.postgresql.org/docs/
