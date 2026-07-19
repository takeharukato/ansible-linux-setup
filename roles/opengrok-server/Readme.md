# OpenGrok

OpenGrok 導入ロール。
本ロールを適用すると,

```text
http://ホスト名:28080/
```

で OpenGrok サーバにアクセス可能となる。

以下, {{と}}で囲んだ文字列はansible playbookの変数名を表す。
実行例中, `$`は一般ユーザのシェルプロンプト, `#`は`root`ユーザのシェルプロンプトを意味する。

- [OpenGrok](#opengrok)
  - [用語定義](#用語定義)
  - [実行方法](#実行方法)
  - [ロール内変数一覧](#ロール内変数一覧)
  - [ロール内の動作](#ロール内の動作)
  - [導入されるファイル](#導入されるファイル)
  - [テンプレート/出力ファイル](#テンプレート出力ファイル)
  - [ポートマッピング(ホストとコンテナ間)定義一覧](#ポートマッピングホストとコンテナ間定義一覧)
  - [環境変数一覧](#環境変数一覧)
    - [`opengrok` サービス](#opengrok-サービス)
  - [ボリューム実体パスについて](#ボリューム実体パスについて)
    - [事前条件](#事前条件)
    - [Mountpoint の確認](#mountpoint-の確認)
  - [ソース同期スクリプト(`opengrok-source-sync`)を用いたソース同期処理手順](#ソース同期スクリプトopengrok-source-syncを用いたソース同期処理手順)
    - [ソース同期スクリプト(`opengrok-source-sync`)のコマンドラインオプション](#ソース同期スクリプトopengrok-source-syncのコマンドラインオプション)
    - [同期対象リポジトリ定義ファイル(`source-urls.yml`)](#同期対象リポジトリ定義ファイルsource-urlsyml)
  - [ソース同期処理の定期実行手順](#ソース同期処理の定期実行手順)
  - [手動でのインデクス更新手順](#手動でのインデクス更新手順)
    - [手動でのインデクス更新処理用のREST API(`/reindex` エンドポイント)に関する留意事項:](#手動でのインデクス更新処理用のrest-apireindex-エンドポイントに関する留意事項)
  - [検証ポイント](#検証ポイント)
    - [`/opt/opengrok` 以下に docker, etc, scripts, src ディレクトリが作成されていることの確認](#optopengrok-以下に-docker-etc-scripts-src-ディレクトリが作成されていることの確認)
    - [`docker compose -f /opt/opengrok/docker/docker-compose.yml ps` で OpenGrok コンテナが稼働していることの確認](#docker-compose--f-optopengrokdockerdocker-composeyml-ps-で-opengrok-コンテナが稼働していることの確認)
    - [OpenGrok サービスが `http://ホスト名:28080/` でアクセス可能なことの確認](#opengrok-サービスが-httpホスト名28080-でアクセス可能なことの確認)
    - [`/usr/local/bin/opengrok-source-sync --dry-run` が正常終了すること](#usrlocalbinopengrok-source-sync---dry-run-が正常終了すること)
    - [`crontab -l` に手動登録したエントリが反映されていること](#crontab--l-に手動登録したエントリが反映されていること)
  - [参考リンク](#参考リンク)

## 用語定義

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| OpenGrok | - | ソースコード検索およびクロスリファレンス生成ツール。 |
| Docker Compose | - | 複数コンテナ構成を YAML で定義し一括実行するツール。 |
| ソース同期 | - | Git リポジトリの clone/pull により, 解析対象のソースを更新する処理。 |
|インデクス更新処理|-|OpenGrokのソースコードディレクトリ中のファイル更新有無を確認し, OpenGrok内部のインデクス情報を更新する処理。|

## 実行方法

本ロールの実行方法は以下の通り:

```bash
make run_opengrok_server
```

または,

```bash
# OpenGrok タスクのみ実行
ansible-playbook --tags "opengrok-server" -i inventory/hosts site.yml
```

## ロール内変数一覧

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `opengrok_enabled` | `false` | OpenGrokの導入制御変数。導入する場合は, `true`に設定する。|
| `opengrok_root_dir` | `/opt/opengrok` | OpenGrok 関連ファイルのベースディレクトリ。 |
| `opengrok_docker_dir` | `{{ opengrok_root_dir }}/docker` | docker-compose.yml 配置先。 |
| `opengrok_etc_dir` | `{{ opengrok_root_dir }}/etc` | source-urls.yml 配置先。 |
| `opengrok_scripts_dir` | `{{ opengrok_root_dir }}/scripts` | 同期スクリプト配置先。 |
| `opengrok_source_dir` | `{{ opengrok_root_dir }}/src` | OpenGrok が参照するソース配置先。 |
| `opengrok_sync_group_name` | `opengrok` | ソース同期ディレクトリへ書き込むためのローカルグループ名。 |
| `opengrok_sync_user_name` | `opengrok` | コンテナ実行IDに合わせて作成するローカルユーザ名。 |
| `opengrok_sync_user_list` | `[]` | ソース同期を実行するユーザの一覧。ここに指定したユーザをソースコード格納先ディレクトリのグループ(OpenGrokの公式コンテナイメージ内で設定されているアプリケーション実行グループ(appgroup)のGIDに対応するグループ)へ追加することでソースコードの更新許可を与える。 |
| `opengrok_image_version` | `1.14` | OpenGrok コンテナイメージのバージョン。 |
| `opengrok_service` | `opengrok` | OpenGrok サービス名 (docker compose)。 |
| `opengrok_service_port` | `28080` | OpenGrok 公開ポート (ホスト側)。 |
| `opengrok_reindex_service_port` | `25000` | 手動再インデクスREST公開ポート (ホスト側)。 |
| `opengrok_data_volume` | `opengrok_data` | OpenGrok データ用 Docker ボリューム名。 |
| `opengrok_java_opts` | `-Xms512m -Xmx2g` | Java オプション。 |
| `opengrok_sync_period_minutes` | `10` | OpenGrok のインデックス更新周期(分)。 |
| `opengrok_wait_timeout` | `300` | サービス待ち合わせ時間(秒)。 |
| `opengrok_wait_delay` | `5` | サービス待ち合わせ開始遅延(秒)。 |
| `opengrok_wait_sleep` | `2` | サービス待ち合わせ間隔(秒)。 |
| `opengrok_wait_delegate_to_waitnode` | `localhost` | サービス待ち合わせ実行元ホスト(対象ホスト外, 制御ノード側)。 |
| `opengrok_source_urls_file` | `{{ opengrok_etc_dir }}/source-urls.yml` | 同期対象リポジトリ定義ファイル。 |
| `opengrok_sync_script_path` | `{{ opengrok_scripts_dir }}/opengrok-source-sync.py` | Python 同期スクリプト配置先。 |
| `opengrok_sync_wrapper_path` | `{{ opengrok_scripts_dir }}/opengrok-source-sync.sh` | 同期処理用シェルスクリプト(Python 同期スクリプトを呼び出すラッパシェルスクリプト)配置先。 |
| `opengrok_daily_sync_script_path` | `{{ opengrok_scripts_dir }}/daily-sync-opengrok-sources.sh` | 日次同期処理用シェルスクリプト配置先。 |
| `opengrok_reindex_script_path` | `{{ opengrok_scripts_dir }}/opengrok-reindex.sh` | 手動再インデクス実行用シェルスクリプト配置先。 |
| `opengrok_sync_command_path` | `/usr/local/bin/opengrok-source-sync` | 同期処理用シェルスクリプト(Python 同期スクリプトを呼び出すラッパシェルスクリプト)への実行コマンドシンボリックリンク先。 |
| `opengrok_reindex_command_path` | `/usr/local/bin/opengrok-reindex` | 手動再インデクス実行用シェルスクリプトへの実行コマンドシンボリックリンク先。 |
| `opengrok_sync_log_file` | `/var/log/opengrok-source-sync.log` | 同期ログ出力先。 |
| `opengrok_python_command` | `/usr/bin/python3` | Python 実行コマンド。環境変数PATHに依存しないよう, 絶対パスで指定する。 |
| `opengrok_daily_sync_extra_args` | `""` | 日次同期スクリプトへ渡す追加引数。 |
| `opengrok_completion_enabled` | `true` | bash/zsh 補完導入有効化フラグ。 |

## ロール内の動作

1. [tasks/load-params.yml](tasks/load-params.yml) で OS 別パッケージ名や共通変数を読み込む。
2. [tasks/package.yml](tasks/package.yml) で Python 依存を含む前提パッケージを導入する。
3. [tasks/directory.yml](tasks/directory.yml) で Docker ボリューム作成, 主要ディレクトリ作成, [templates/docker-compose.yml.j2](templates/docker-compose.yml.j2) を配置する。あわせて [templates/source-urls.yml.j2](templates/source-urls.yml.j2), [templates/opengrok-source-sync.py.j2](templates/opengrok-source-sync.py.j2), [templates/opengrok-source-sync.sh.j2](templates/opengrok-source-sync.sh.j2), [templates/daily-sync-opengrok-sources.sh.j2](templates/daily-sync-opengrok-sources.sh.j2), [templates/opengrok-reindex.sh.j2](templates/opengrok-reindex.sh.j2) を配置する。
4. [tasks/user_group.yml](tasks/user_group.yml) で 以下の処理を実施する:
   1. OpenGrok公式コンテナイメージ内で設定されているグループIDを基準に, 対象ホスト側で使用するグループを決定する(競合時は既存アカウントを優先利用)。
   2. `{{ opengrok_source_dir }}` の所有者は `root` のまま, グループを OpenGrok公式コンテナイメージ内で設定されているグループIDに対応するグループID(`1111`)に設定する。
   3. 以下のようにアクセス権を設定(8進数で, `2775`に設定):
      1. グループIDを継承するよう指定(`setgid`ビットを設定)
      2. 所有者/所有グループに対して, 読み書き実行可能
      3. その他に対して読み取りと実行可能
   4. `opengrok_sync_user_list` に列挙されたユーザを当該グループに追加する。
5. [tasks/service.yml](tasks/service.yml) で `docker compose down` / `docker compose up -d` を実行し, `{{ opengrok_service_port }}` の起動待ち合わせを2段階で実施する。第1段階で対象ホスト内 (localhost) の待受を確認し, 第2段階で制御ノードから inventory ホスト名への到達性を確認する。
6. [tasks/config.yml](tasks/config.yml) で bash/zsh 補完を導入する。

## 導入されるファイル

本ロールを適用すると, `/opt/opengrok` 配下に以下のファイルが作られる。

- docker ディレクトリ
  - docker-compose.yml OpenGrok サーバを起動するための docker compose ファイル。
- etc ディレクトリ
  - source-urls.yml 同期対象リポジトリ定義ファイル。
- scripts ディレクトリ
  - opengrok-source-sync.py リポジトリ同期を実行する Python スクリプト。
  - opengrok-source-sync.sh Python スクリプト呼び出し用ラッパシェルスクリプト。
  - daily-sync-opengrok-sources.sh 日次同期実行用シェルスクリプト。crontab からの呼び出しを想定。
  - opengrok-reindex.sh 手動再インデクス実行用シェルスクリプト。
- src ディレクトリ
  - source-urls.yml 記述に従って clone/pull されるソースを展開する先となるディレクトリ。

## テンプレート/出力ファイル

| テンプレート名 | 出力先ファイル (既定値) | 説明 |
| --- | --- | --- |
| `docker-compose.yml.j2` | `/opt/opengrok/docker/docker-compose.yml` | OpenGrok の Docker Compose 定義ファイル。コンテナ実行ユーザはOpenGrok公式コンテナイメージの既定値(ユーザID/グループID共に1111)を使用する。 |
| `source-urls.yml.j2` | `/opt/opengrok/etc/source-urls.yml` | 同期対象リポジトリ定義ファイル。 |
| `opengrok-source-sync.py.j2` | `/opt/opengrok/scripts/opengrok-source-sync.py` | source-urls.yml を読み取り clone/pull を行うスクリプト。 |
| `opengrok-source-sync.sh.j2` | `/opt/opengrok/scripts/opengrok-source-sync.sh` | Python 同期スクリプトを呼び出すラッパシェルスクリプト。 |
| `daily-sync-opengrok-sources.sh.j2` | `/opt/opengrok/scripts/daily-sync-opengrok-sources.sh` | 日次同期実行用ラッパシェルスクリプト。 |
| `opengrok-reindex.sh.j2` | `/opt/opengrok/scripts/opengrok-reindex.sh` | 手動再インデクス実行用 処理用スクリプト。 |
| `opengrok-source-sync.bash-completion.j2` | `/etc/bash_completion.d/opengrok-source-sync` | bash 補完定義。 |
| `_opengrok-source-sync.zsh-completion.j2` | `{{ opengrok_sync_zsh_completion_path }}` | zsh 補完定義。 |

## ポートマッピング(ホストとコンテナ間)定義一覧

| サービス名 | ホスト側ポート | コンテナ側ポート | プロトコル | 厳密な用途 |
|---|---:|---:|---|---|
| `opengrok` | `{{ opengrok_service_port }}` | `8080` | TCP | OpenGrok Web UI/API の HTTP 待受。 |
| `opengrok` | `{{ opengrok_reindex_service_port }}` | `5000` | TCP | 手動再インデクス用 `/reindex` REST 待受。 |

## 環境変数一覧

### `opengrok` サービス

| 変数名 | 値 | 意味 |
|---|---|---|
| `JAVA_OPTS` | `{{ opengrok_java_opts }}` | OpenGrok コンテナ JVM オプション。 |
| `SYNC_PERIOD_MINUTES` | `{{ opengrok_sync_period_minutes }}` | OpenGrok コンテナ内でのインデックス更新周期(分)。 |

## ボリューム実体パスについて

### 事前条件

ホスト上の既存のボリュームを使用する設定(`external: true`) で, docker composeのボリュームを定義しているため, 外部ボリュームは docker compose 実行前に存在している必要がある。

本ロールでは, 以下の手順でボリューム実体パスを作成する:

```bash
docker volume create {{ opengrok_data_volume }}
```

規定値の場合は, 以下のようにコマンドを実行する:
```bash
docker volume create opengrok_data
```

### Mountpoint の確認

各ボリュームの Mountpoint 確認方法は以下の通り。

```bash
docker volume inspect -f '{{ .Mountpoint }}' {{ opengrok_data_volume }}
```

規定値の場合は, 以下のようにコマンドを実行する:
```bash
docker volume inspect -f '{{ .Mountpoint }}' opengrok_data
```

## ソース同期スクリプト(`opengrok-source-sync`)を用いたソース同期処理手順

本ロールでは, ソース同期スクリプト(`opengrok-source-sync` コマンド)を用意している。
`opengrok_sync_user_list`に含まれるユーザで, 以下のように `opengrok-source-sync` コマンドを実行することで, Githubなどのソースリポジトリからソースコードをダウンロードし, OpenGrokから検索可能にする:

```shell
/usr/local/bin/opengrok-source-sync --config /opt/opengrok/etc/source-urls.yml --src-root /opt/opengrok/src
```

### ソース同期スクリプト(`opengrok-source-sync`)のコマンドラインオプション

ソース同期スクリプト(`opengrok-source-sync`)のコマンドラインオプションは, 以下の通り:

|オプション|意味|指定例|
|---|---|---|
|--config|同期対象リポジトリ定義ファイルへのパスを指定する。規定値は, `opengrok_etc_dir`変数で指定したディレクトリ配下の`source-urls.yml`となる。|--config /opt/opengrok/etc/source-urls.yml|
|--src-root|ソース展開先ディレクトリを指定する。既定値は, `opengrok_source_dir` で指定したディレクトリとなる。|--src-root /opt/opengrok/src|

### 同期対象リポジトリ定義ファイル(`source-urls.yml`)

同期対象リポジトリ定義ファイル(`source-urls.yml`)は, 調査対象ソースコード取得元となるGitHubのURLとタグ名の一覧を定義する設定ファイルである。同期対象リポジトリ定義ファイルには, 以下の形式の辞書のリストを設定することで, ソースコードを展開するディレクトリと調査対象ソースコード取得元となるGitHubのURLとの対応関係を定義する:

|キー|値|記載例|
|---|---|---|
|title|ソースコード格納先サブディレクトリを表すタイトル|linux|
|url|ソースコード取得元URL|https://github.com/torvalds/linux.git|
|tag|取得するソースコードのタグを固定する場合は, タグ名を記載する。未指定時は default branch の最新版を取得する。|v6.12|
|token|このエントリで使用するアクセストークンを直接指定する。未指定時は認証ヘッダを付与せずにアクセスする。|ghp_xxxxxxxxxxxxxxxxxxxx|

記載例は, 以下の通り:

```yaml
sources:
  - title: linux
    url: https://github.com/torvalds/linux.git
    tag: v6.12
    token: ghp_xxxxxxxxxxxxxxxxxxxx
  - title: opengrok
    url: https://github.com/oracle/opengrok.git
    token: ghp_yyyyyyyyyyyyyyyyyyyy
    # tag 未指定時は default branch の最新版を同期
```

## ソース同期処理の定期実行手順

定期的にソースコードを同期する場合は, `opengrok_sync_user_list`に含まれるユーザで, `crontab -e` コマンドを実行し, 以下の crontab エントリを手動作成する:

```text
0 3 * * * /opt/opengrok/scripts/daily-sync-opengrok-sources.sh >> /var/log/opengrok-source-sync.log 2>&1
```

なお, 本ロールは crontab エントリを自動作成しない。

## 手動でのインデクス更新手順

OpenGrokには, 手動でのインデクス更新処理用のREST APIとして, `/reindex` エンドポイントを提供している。

`/reindex` エンドポイントは, コンテナ内の REST ポート(5000)で要求を待ち受ける。本ロールの既定構成では, OpenGrokのRESTポート(コンテナ側ポート: `5000`番)をホスト側 ポート `25000` 番に公開する。

本ロールが導入するOpenGrok導入ホスト上で, 以下のコマンドを実行することで本REST APIを通した手動でのインデクス更新処理を実施することが可能である:

```bash
opengrok-reindex
```

正常にインデクス更新処理を呼び出した場合は, 端末上に`Reindex triggered`という出力が得られる。

実行例:
```bash
$ /usr/local/bin/opengrok-reindex
Reindex triggered
```

本コマンドは内部的に下記相当の `curl` を実行し, 必須の Authorization ヘッダを付与した上で, 手動でのインデクス更新処理用のREST APIを呼び出す:

```bash
curl -H "Authorization: Bearer trigger" http://127.0.0.1:25000/reindex
```

### 手動でのインデクス更新処理用のREST API(`/reindex` エンドポイント)に関する留意事項:

ブラウザから `http://mgmt-server.local:25000/reindex` を直接開くと, Authorization ヘッダが付かないため `Unauthorized Access` になりうるため, OpenGrok動作ホスト上で, `/opt/opengrok/scripts/opengrok-reindex.sh`を実行することを推奨する。OpenGrok公式のコンテナイメージの仕様上, 環境変数 `REST_TOKEN` を未設定にしても, `/reindex` 呼び出し時は `Authorization: Bearer <任意文字列>` ヘッダ自体が必要となる。 `REST_TOKEN` 未設定時はトークン値の一致検証は行われないため, 任意の値でよい。

## 検証ポイント

- `/opt/opengrok` 以下に docker, etc, scripts, src ディレクトリが作成されていること。
- `docker compose -f /opt/opengrok/docker/docker-compose.yml ps` で OpenGrok コンテナが稼働していること。
- OpenGrok サービスが `http://ホスト名:28080/` でアクセス可能なこと。
- `/usr/local/bin/opengrok-source-sync --dry-run` が正常終了すること。
- `crontab -l` に手動登録したエントリが反映されていること。

### `/opt/opengrok` 以下に docker, etc, scripts, src ディレクトリが作成されていることの確認

本作業は, 本ロールを適用したホスト上で実施する。実行するコマンドは以下の通り:
```bash
ls -l /opt/opengrok
```

実行例:
```bash
$ ls -l /opt/opengrok
合計 16K
drwxr-xr-x 2 root     root     4096  7月 19 16:33 docker
drwxr-xr-x 2 root     root     4096  7月 19 16:09 etc
drwxr-xr-x 2 root     root     4096  7月 19 16:47 scripts
drwxrwsr-x 3 opengrok opengrok 4096  7月 19 16:48 src
```

docker, etc, scripts, src ディレクトリが作成されていること, `src` ディレクトリの所有者が `root` であること, グループがコンテナ内規定の実行グループGID(`1111`)に対応するグループであること, パーミッションが `2775` であることを確認する。

### `docker compose -f /opt/opengrok/docker/docker-compose.yml ps` で OpenGrok コンテナが稼働していることの確認

本作業は, 本ロールを適用したホスト上で実施する。実行するコマンドは以下の通り:
```bash
docker compose -f /opt/opengrok/docker/docker-compose.yml ps
```

実行例:
```bash
$ docker compose -f /opt/opengrok/docker/docker-compose.yml ps

NAME                  IMAGE                        COMMAND                   SERVICE       CREATED         STATUS         PORTS
opengrok              opengrok/docker:1.14         "/scripts/entrypoint…"   opengrok      6 minutes ago   Up 6 minutes   0.0.0.0:25000->5000/tcp, [::]:25000->5000/tcp, 0.0.0.0:28080->8080/tcp, [::]:28080->8080/tcp
```

以下の項目を確認する:
- `NAME`の列にopengrokという名前のコンテナが含まれること
- `IMAGE`の列のコンテナイメージのタグ名部分が`opengrok_image_version`変数での指定値と一致すること
- PORTSの項目に以下の項目が含まれること
  - `0.0.0.0:25000->5000/tcp`
  - `[::]:25000->5000/tcp`
  - `0.0.0.0:28080->8080/tcp`
  - `[::]:28080->8080/tcp`

### OpenGrok サービスが `http://ホスト名:28080/` でアクセス可能なことの確認

本作業は, 本ロールを適用したホストに接続可能なホスト上で実施する。実行するコマンドは以下の通り:
```bash
curl -I http://ホスト名:28080/
```

実行例:
```bash
$ curl -I http://mgmt-server.local:28080/
HTTP/1.1 200
Set-Cookie: JSESSIONID=1CD3D328266E6160A6535AC0694A0296; Path=/; HttpOnly; Secure; SameSite=Strict
Set-Cookie: OpenGrokProject=VirtualCluster; Secure; SameSite=Strict
Content-Type: text/html;charset=UTF-8
Date: Sun, 19 Jul 2026 08:01:08 GMT

```

以下の項目を確認する:
- 応答コードが, 正常系の応答(`200`など)となっていること

### `/usr/local/bin/opengrok-source-sync --dry-run` が正常終了すること

本作業は, 本ロールを適用したホスト上で実施する。実行するコマンドは以下の通り:
```bash
/usr/local/bin/opengrok-source-sync --dry-run
```

実行例:
```bash
$ /usr/local/bin/opengrok-source-sync --dry-run
2026-07-19 17:04:40 INFO [VirtualCluster] synchronized default branch=main
2026-07-19 17:04:40 INFO Synchronization completed successfully
```

以下の項目を確認する:
- 端末上の出力結果に`Synchronization completed successfully`という文字列が含まれること

### `crontab -l` に手動登録したエントリが反映されていること

本作業は, 本ロールを適用したホスト上で, かつ, crontabに登録する際に使用したユーザアカウントで実施する。実行するコマンドは以下の通り:

```bash
crontab -l
```

実行例:
```bash
$ crontab -l
# Edit this file to introduce tasks to be run by cron.
#
# Each task to run has to be defined through a single line
# indicating with different fields when the task will be run
# and what command to run for the task
#
# To define the time you can provide concrete values for
# minute (m), hour (h), day of month (dom), month (mon),
# and day of week (dow) or use '*' in these fields (for 'any').
#
# Notice that tasks will be started based on the cron's system
# daemon's notion of time and timezones.
#
# Output of the crontab jobs (including errors) is sent through
# email to the user the crontab file belongs to (unless redirected).
#
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
#
# For more information see the manual pages of crontab(5) and cron(8)
#
# m h  dom mon dow   command
0 3 * * * /opt/opengrok/scripts/daily-sync-opengrok-sources.sh >> /var/log/opengrok-source-sync.log 2>&1
```

以下の項目を確認する:
- 端末上の出力結果に`/opt/opengrok/scripts/daily-sync-opengrok-sources.sh`という文字列が含まれること, 当該文字列を含む行の実行時刻やコマンドラインが意図通りに設定されていること


## 参考リンク

- [OpenGrok Docker image](https://hub.docker.com/r/opengrok/docker)
- [OpenGrok project](https://github.com/oracle/opengrok)
