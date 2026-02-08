# Redmine

- [Redmine](#redmine)
  - [ロール内変数一覧](#ロール内変数一覧)
  - [ロール内の動作](#ロール内の動作)
  - [導入されるファイル](#導入されるファイル)
    - [バックアップスクリプト](#バックアップスクリプト)
    - [リストアスクリプト](#リストアスクリプト)
    - [定期バックアップ](#定期バックアップ)
    - [PostgreSQLの論理バックアップの内容について](#postgresqlの論理バックアップの内容について)
  - [用語定義](#用語定義)
  - [ポートマッピング(ホストとコンテナ間)定義一覧 ( 本ファイル )](#ポートマッピングホストとコンテナ間定義一覧--本ファイル-)
    - [ボリューム名,コンテナ外(外部ボリューム実体名),コンテナ内マウント先ディレクトリの対応表](#ボリューム名コンテナ外外部ボリューム実体名コンテナ内マウント先ディレクトリの対応表)
  - [環境変数一覧](#環境変数一覧)
    - [`redmine` サービス](#redmine-サービス)
    - [`redmine-db` サービス](#redmine-db-サービス)
  - [ボリューム実体パスについて](#ボリューム実体パスについて)
    - [事前条件](#事前条件)
    - [Mountpoint の確認](#mountpoint-の確認)
    - [実体パスの変動要因](#実体パスの変動要因)
    - [コンテナ内マウントポイントとの突合確認手順](#コンテナ内マウントポイントとの突合確認手順)
  - [docker volume inspect を用いたバックアップ, リストア, 権限整合確認手順](#docker-volume-inspect-を用いたバックアップ-リストア-権限整合確認手順)
    - [Redmineの添付ファイル ( {{redmine\_files\_volume}} )](#redmineの添付ファイル--redmine_files_volume-)
      - [バックアップ](#バックアップ)
      - [リストア](#リストア)
      - [権限整合 (Redmine添付ファイル)](#権限整合-redmine添付ファイル)
    - [PostgreSQL データ ( {{redmine\_database\_volume}} )](#postgresql-データ--redmine_database_volume-)
      - [論理バックアップ](#論理バックアップ)
      - [論理リストア](#論理リストア)
      - [オフラインボリュームコピー](#オフラインボリュームコピー)
      - [権限整合 (PostgreSQLデータ)](#権限整合-postgresqlデータ)
  - [参考リンク](#参考リンク)

Redmine導入ロール。
本ロールを適用すると,

```:text
http://ホスト名:8080/
```

でRedmineサーバにアクセス可能となる。

以下, {{と}}で囲んだ文字列はansible playbookの変数名を表す。
実行例中, `$`は一般ユーザのシェルプロンプト, `#`は`root`ユーザのシェルプロンプトを意味する。

## ロール内変数一覧

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
| `redmine_db_image` | `postgres:15.1-bullseye` | PostgreSQL コンテナイメージ。 |
| `redmine_db_service` | `redmine-db` | PostgreSQL サービス名 (docker compose)。 |
| `redmine_db_name` | `redmine` | PostgreSQL データベース名。 |
| `redmine_db_user` | `redmine_user` | PostgreSQL ユーザ名。 |
| `redmine_db_password` | `redmine_password` | PostgreSQL パスワード。 |
| `redmine_backup_rotation` | `7` | デイリーバックアップの保持世代数。 |
| `redmine_backup_mount_point` | `/mnt` | NFS マウントポイント。 |
| `redmine_backup_dir_on_nfs` | `/redmine-backup` | NFS 配下のバックアップ配置先ディレクトリ。 |
| `redmine_backup_output_dir` | `{{redmine_backup_mount_point}}{{ redmine_backup_dir_on_nfs }}` | NFS 上のバックアップ出力先フルパス。 |
| `redmine_backup_nfs_server` | `localhost` | デイリーバックアップ先の NFS サーバ。 |

## ロール内の動作

1. [tasks/load-params.yml](roles/redmine-server/tasks/load-params.yml#L8-L23) で OS 別パッケージ名や共通変数を読み込み。
2. [tasks/directory.yml](roles/redmine-server/tasks/directory.yml#L8-L78) で Docker ボリューム作成, 主要ディレクトリ作成, テンプレート ([templates/docker-compose.yml.j2](roles/redmine-server/templates/docker-compose.yml.j2), [templates/backup-redmine-data.sh.j2](roles/redmine-server/templates/backup-redmine-data.sh.j2), [templates/restore-redmine-data.sh.j2](roles/redmine-server/templates/restore-redmine-data.sh.j2), [templates/daily-backup-redmine.sh.j2](roles/redmine-server/templates/daily-backup-redmine.sh.j2)) を配置。
3. [tasks/service.yml](roles/redmine-server/tasks/service.yml#L7-L25) で `docker compose down` / `docker compose up -d` を実行し, `{{ redmine_service_port }}` の起動待ち合わせを実施。
4. [tasks/service.yml](roles/redmine-server/tasks/service.yml#L27-L37) で Redmine 管理者のパスワードを `redmine_admin_password`変数の設定値に従って設定する。`redmine_admin_password`変数が未定義の場合, または, 設定値が空文字列の場合は, `admin`を管理者パスワード(RedmineのDockerHubコンテナのデフォルト設定値)として設定する。

## 導入されるファイル

本ロールを適用すると, `/data/redmine`配下に以下のファイルが作られる

- backup ディレクトリ デイリーバックアップファイル保存ディレクトリ
  - redmine.dump.gz Redmineデータベースのバックアップ ( PostgreSQLの論理バックアップ )ファイルのgzip形式圧縮ファイル
  - redmine_files.tgz Redmineに登録されたファイル(添付ファイルなど)をバックアップしたtar.gz形式の圧縮ファイル
- docker ディレクトリ
  - docker-compose.yml Redmineサーバを立てるためのdocker composeファイル
- scripts ディレクトリ
  - backup-redmine-data.sh Redmineのデータベース, Redmineに登録されたファイル(添付ファイルなど)をバックアップするためのスクリプト
  - restore-redmine-data.sh バックアップファイルの内容をRedmineに反映するためのスクリプト
  - daily-backup-redmine.sh backup-redmine-data.shを用いて, `backup` ディレクトリにバックアップファイルを作成するためのスクリプト。crontabに登録することで定期バックアップを採取するために使用する。

### バックアップスクリプト

本ロールでは, `backup-redmine-data.sh`というバックアップスクリプトを用意している。

本バックアップスクリプトは, 以下のように実行する。

```:shell
backup-redmine-data.sh
```

実行を完了すると, `/data/redmine/backup`にバックアップファイル, `redmine.dump.gz`,`redmine_files.tgz`が生成される。

### リストアスクリプト

本ロールでは, `restore-redmine-data.sh`というリストアスクリプトを用意している。

`/data/redmine/backup`に, 各バックアップファイルを, 前節で記載したファイル名(`redmine.dump.gz`, `redmine_files.tgz`)で配置してから, 以下のように, `restore-redmine-data.sh`を実行することで, Redmineの状態を復元することができる。

```:shell
restore-redmine-data.sh
```

### 定期バックアップ

`crontab -e`コマンドで以下のcrontabエントリを作成する。
以下の設定では, 毎日午前3時に`/data/redmine/backup`にバックアップファイルを生成後,
`{{redmine_backup_nfs_server}}:{{redmine_backup_nfs_dir}}`をマウントポイントに指定して,
NFSサーバをマウントし, バックアップファイルを当該ディレクトリにコピーする。

```:text
0 3 * * * /data/redmine/scripts/daily-backup-redmine.sh
```

NFSサーバ上に配置されるバックアップファイルには, 以下のような世代番号が付けられる。

- redmine.dump-世代番号.gz Redmineデータベースのバックアップ ( PostgreSQLの論理バックアップ )ファイルのgzip形式圧縮ファイル
- redmine_files-世代番号.tgz Redmineに登録されたファイル(添付ファイルなど)をバックアップしたtar.gz形式の圧縮ファイル

世代番号を除いた形式にこれらのファイルの名前を変更し, `/data/redmine/backup`にファイルを配置して, `restore-redmine-data.sh`を実行することで, Redmineの状態を復元することができる。

### PostgreSQLの論理バックアップの内容について

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

## 用語定義

- Docker Compose サービス ( 以下, サービスと記す ) : docker-compose.yml の services: 直下に定義する構成単位。サービスは1つの機能役割 ( 例 : アプリケーション, データベース ) を実行するコンテナの実行仕様を記述する。
  - 機能役割の粒度: Web アプリケーション用 ( 例 : redmine ), データベース用 ( 例 : redmine-db ) という役割ごとに分離。
  - 実行仕様 : 使用するコンテナイメージ ( Docker イメージ ) , ポート公開, ボリュームマウント, 環境変数, 再起動ポリシー等, コンテナ実行に必要な完全な設定集合。
  - スケール単位 : Compose では通常 1 コンテナだが, 同一サービスを複数個起動 ( スケール ) することで冗長化や水平分散が可能 ( docker compose up --scale サービス名=レプリカ数 ) 。

- ポート ( Port ) : TCP ( Transmission Control Protocol, 以下, TCP と記す ) または UDP ( User Datagram Protocol, 以下, UDP と記す ) の通信終端識別子 ( 0 から 65535 ) 。
- ポート公開 ( Port Publishing, 以下, ポート公開と記す ) : `ports:` による `ホスト側ポート:コンテナ側ポート[/プロトコル]` の転送設定。プロトコル未指定時は TCP 。
- Docker ボリューム ( Volume, 以下, ボリュームと記す ) : Docker が管理する 永続ストレージ機構 。コンテナのライフサイクルと独立してデータを保持。
- 外部ボリューム ( External Volume, 以下, 外部ボリュームと記す ) : Docker Compose サービス外で事前作成されているボリューム。`external: true` で新規作成しない。
- 内部 DNS ( Domain Name System, 以下, DNS と記す ) : Docker Compose サービス名 から IP アドレス の名前解決機構。
- ネットワーク識別子 : Compose 内部 DNS ( Domain Name System, 以下, DNS と記す ) により, サービス名がホスト名として解決される ( 例 : redmine-db  から  DB コンテナの IP ) 。
- コンテナ ( Container, 以下, コンテナと記す ) : コンテナイメージ の実行インスタンス。Linuxカーネルの名前空間 ( Namespaces ) と Control Groups ( 以下, cgroups と記す ) によってプロセスリソースが隔離される。
  - Linuxカーネルの名前空間 : 名前空間は, Linux カーネルがリソースの可視範囲をプロセス集合ごとに分離するための機構のこと。特定種類のリソースについて. プロセスの属する名前空間単位で互いに独立させ, 互いのリソースの可視性を制御することで, リソースの相互干渉を抑制する環境を構成するために用いられる。
  - Control Groups : Linux カーネルが提供する資源管理機構のこと。プロセスの集合に対して CPU, メモリ, 入出力 ( I/O ), プロセス数 などの使用量制御・優先度制御・計測を行うための機能を提供する。

## ポートマッピング(ホストとコンテナ間)定義一覧 ( 本ファイル )

| サービス名 | ホスト側ポート | コンテナ側ポート | プロトコル | 厳密な用途 |
|---|---:|---:|---|---|
| `redmine` | `{{redmine_service_port}}` | `3000` | TCP | Redmine ( Ruby on Rails アプリケーション ) の HTTP 待受。ホスト `{{redmine_service_port}}/TCP` への接続がコンテナ `3000/TCP` へ転送される。 |
| `redmine-db` | `5432` | `5432` | TCP | PostgreSQL 既定ポートの外部公開。 内部接続のみで足りる場合は `ports:` を削除 する。 |

### ボリューム名,コンテナ外(外部ボリューム実体名),コンテナ内マウント先ディレクトリの対応表

| 論理ボリューム名 | 外部ボリューム実体名 | コンテナ内マウント先 | 対象サービス | コンテナ内データの意味 |
|---|---|---|---|---|
| `vol_redmine` | `{{redmine_files_volume}}` | `/usr/src/redmine/files` | `redmine` | Redmine の添付ファイルなどの永続データ。 |
| `vol_redmine_db` | `{{redmine_database_volume}}` | `/var/lib/postgresql/data` | `redmine-db` | PostgreSQL のデータクラスタ。 |

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

## ボリューム実体パスについて

### 事前条件

本設定では, `external: true` のため, 外部ボリュームは Compose 起動前に存在している必要がある。事前作成手順は以下の通り。

```bash
docker volume create {{redmine_files_volume}}
docker volume create {{redmine_database_volume}}
```

### Mountpoint の確認

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

### 実体パスの変動要因

本設定では, 以下の要因により, ボリュームの実体パスが変動しうる。

- Docker のデータルート ( `data-root` ) 設定。
- rootless Docker ( 例 : `~/.local/share/docker/volumes/.../_data` ) 。
- Docker Desktop / WSL2 / macOS などでは VM 内配置。

コンテナ外から確認する場合は, いずれの場合も `docker volume inspect` 出力が唯一の正確な情報となる。

### コンテナ内マウントポイントとの突合確認手順

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

## 参考リンク

- [redmine Docker Official Image](https://hub.docker.com/_/redmine)
- [DockerでRedmine(プロジェクト管理ソフトウェア)を動かす](https://zenn.dev/isi00141/articles/c8c883f7e33647)