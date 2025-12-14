# gitlab-server ロール

このロールは GitLab Omnibus の公式 Docker イメージと GitLab Runner をホスト上で運用するための基盤を構築します。`docker compose` によるコンテナ起動 / 停止, 永続化ディレクトリの準備, バックアップ / リストア補助スクリプトの展開を自動化し, 再実行可能な手順で GitLab サービスを維持します。

以下の処理を実施します:

- 公式 Docker イメージ用のホームディレクトリ（`/srv/gitlab`）配下に設定, ログ, データ, バックアップ用ディレクトリを作成
- `docker-compose.yml` をテンプレートから生成し, GitLab 本体と GitLab Runner のコンテナを `docker compose up -d` で起動
- `gitlab-backup.py` / `gitlab-restore.py` を `/srv/gitlab/scripts/` に展開してバックアップ運用を支援（`GITLAB_ASSUME_YES=1` を利用した非対話リストアに対応）
- 運用前に `gitlab-ctl stop puma/sidekiq` を行い PostgreSQL を停止させずにリストアできるよう制御
- クリーンインストール指定時には既存の設定, データ, コンテナイメージを削除して初期状態から再構築

GitLab の初期ルートパスワードファイルや公開 URL, 通信ポートもロールの変数で一元管理します。

## 変数一覧

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `gitlab_hostname` | `""` | GitLab WEB UI/Container Registryの公開URL中のホスト名部分を指定します。本変数が, 未設定または空文字列の場合, gitlabの導入を行いません。|
| `gitlab_https_port` | `9443` | GitLab Web UI (HTTPS) 公開ポート。|
| `gitlab_ssh_port` | `2224` | GitLab SSH (リポジトリ操作用) 公開ポート。|
| `gitlab_registry_port` | `5050` | コンテナレジストリ公開ポート。|
| `gitlab_external_url` | `https://{{ gitlab_hostname }}:{{ gitlab_https_port }}` | Web UI へアクセスする外部 URL。|
| `gitlab_docker_image` | `gitlab/gitlab-ce:18.6.2-ce.0` | GitLab Omnibus Docker イメージ。公式の推奨に従って, バージョン名を明示してイメージを指定してください。|
| `gitlab_runner_docker_image` | `gitlab/gitlab-runner:ubuntu-v18.6.6` | GitLab Runner Docker イメージ。GitLab 本体とメジャーバージョン, マイナーバージョンを合わせてください。|
| `gitlab_home_dir` | `/srv/gitlab` | GitLab 導入先ディレクトリ。|
| `gitlab_config_dir` | `/srv/gitlab/config` | 設定ファイル格納ディレクトリ。|
| `gitlab_logs_dir` | `/srv/gitlab/logs` | ログ格納ディレクトリ。|
| `gitlab_data_dir` | `/srv/gitlab/data` | データ格納ディレクトリ。|
| `gitlab_backup_dir` | `/srv/gitlab/data/backups` | GitLab 標準バックアップの出力先。|
| `gitlab_daily_backup_dir` | `/srv/gitlab/daily-backups` | デイリーバックアップ用のバックアップバンドルファイル保存先ディレクトリ。|
| `gitlab_scripts_dir` | `/srv/gitlab/scripts` | バックアップ関連スクリプト配置先。|
| `gitlab_docker_compose_file` | `/srv/gitlab/docker-compose.yml` | Gitlabのdocker compose 定義ファイル。|
| `gitlab_clean_install` | `false` | `true` の場合は既存設定, データ, ホームディレクトリを削除してクリーンインストールします。|
| `gitlab_remove_container_images` | `false` | `true` の場合は, 既存の GitLab / Runner イメージを削除してからインストールを開始します。|

## ロール内の動作

1. [tasks/load-params.yml](tasks/load-params.yml) で OS ごとのパッケージ定義や共通パラメータを取り込みます。
2. `gitlab_clean_install` や `gitlab_remove_container_images` が有効な場合, [tasks/config-clean-install.yml](tasks/config-clean-install.yml) が既存ディレクトリと Docker イメージを削除します。
3. [tasks/directory-gitlab.yml](tasks/directory-gitlab.yml) が GitLab 用ユーザ / グループを確認し, ホーム, 設定, データ, バックアップ各ディレクトリを所有権付きで作成します。
4. 同タスク内で `docker-compose.yml`, `gitlab-backup.py`, `gitlab-restore.py` を配置します。
5. [tasks/service.yml](tasks/service.yml) が `docker compose up -d` で GitLab / Runner コンテナを起動し, HTTPS / SSH / Registry ポートが開くまで待機します。その後, アクセス URL や初期パスワードファイルパスを表示します。
6. ロール再実行時には既存の compose ファイルや永続化ディレクトリを再利用し, 冪等に整備を行います。停止したい場合は [tasks/stop-service.yml](tasks/stop-service.yml) を参照してください。

## Gitlabコンテナについて

本ロールでは, 以下の2つのコンテナからなるDocker composeを生成します:

|コンテナ名|用途|
|---|---|
|gitlab|gitlab本体|
|gitlab-runner|gitlabのCI/CDで使用するgitlab-runner|

Docker composeファイルは, `{{ gitlab_home_dir }}/docker-compose.yml` (規定値は, `/srv/gitlab/docker-compose.yml` )に生成されます。

### ポートマッピング

コンテナ起動後, コンテナ内の以下のポートがホストのポートにマップされます。
Gitlabの既定の設定の場合, `8080`ポートや`2222`番ポートが他の用途に使用されている
可能性があるため, 公開ポート番号を変更しています。
GitLab Web UI (HTTPS)ポートやGitLab Container Registryのポートは, Gitlabの`external_url`, `registry_external_url`との整合性を保つようにする必要があります。
変更時は, `templates/docker-compose.yml.j2`の内容との整合性についても確認してください。

なお, コンテナ内ポートは, Gitlabコンテナ内で固定で使用されるため設定変数はありません。

|ホストポート|規定値|コンテナポート|用途|
|---|---|---|---|
|`{{ gitlab_https_port }}`|`9443`|`443`|GitLab Web UI (HTTPS)|
|`{{ gitlab_ssh_port }}`|`2224`|`22`|Gitリポジトリ操作用 SSH|
|`{{ gitlab_registry_port }}`|`5050`|`5050`|GitLab Container Registry|

### ボリュームの設定

Gitlabで使用する各種データの永続化のため, コンテナ起動後, 以下に示すホスト上のパスが
コンテナ内のパスにマウント(バインドマウント)され, コンテナ内からの操作がホスト上の
対象パス内のファイルに反映されます。

|ホスト上のパス|規定値|コンテナ内のパス|用途|
|---|---|---|---|
|`{{ gitlab_config_dir }}`|`/srv/gitlab/config`|`/etc/gitlab`|GitLab Omnibus 設定ファイル一式|
|`{{ gitlab_logs_dir }}`|`/srv/gitlab/logs`|`/var/log/gitlab`|GitLab ログ永続化|
|`{{ gitlab_data_dir }}`|`/srv/gitlab/data`|`/var/opt/gitlab`|GitLab データ永続化 (repositories, uploads など)|
|`{{ gitlab_runner_config_dir }}`|`/srv/gitlab/gitlab-runner/config`|`/etc/gitlab-runner`|GitLab Runner 設定ファイル|
|`{{ gitlab_runner_docker_sock_dir }}`|`/var/run/docker.sock`|`/var/run/docker.sock`|Runner からホスト Docker へのアクセス|

#### Gitlabの初期パスワード参照方法

`{{ gitlab_config_dir }}`(規定値は, `/srv/gitlab/config`)に, コンテナ内の`/etc/gitlab`ディレクトリがマウントされます。このため, 初期パスワードは, ホスト上の`{{ gitlab_config_dir }}/initial_root_password` (規定値は, `/srv/gitlab/config/initial_root_password` )を参照することで確認可能です。

#### Gitlab関連ファイルの所有者, グループIDについて

Gitlabの公式コンテナイメージでは, Gitlab関連ファイルの所有者, グループIDが`1000`番であることを前提に構成されています。このため, 本ロールでは, ユーザID, グループIDを`1000`に設定して, Gitlab関連のディレクトリ, ファイルを生成します。

ユーザID, グループID が `1000` 番のユーザやグループがない場合は, `gitlab`ユーザ, `gitlab`グループを`1000`番のユーザ, グループとして作成します。

## バックアップ / リストアについて

本ロールでは, [公式のGitlabバックアップ手順](https://docs.gitlab.com/administration/backup_restore/)に従って, バックアップ, リストアを行う処理を自動化するスクリプトを生成します。

### バックアップの内容

Gitlabの公式手順に従って, バックアップを生成, 復元するため, 以下の内容が含まれます
(詳細は, [Data included in a backup
](https://docs.gitlab.com/administration/backup_restore/backup_gitlab/#data-included-in-a-backup) 参照):

- Gitリポジトリ
- LFS
- Job artifacts
- Snippets
- Container registry metadata ( registry データ本体は対象外)
- PostgreSQL データ (データベース)
- Uploads
- CI/CD pipeline data

### バックアップに含まれない内容

公式手順のバックアップ処理では, 以下の内容はバックアップに含まれないため,
必要に応じて別途バックアップを取ってください。詳細は, [Data not included in a backup
](https://docs.gitlab.com/administration/backup_restore/backup_gitlab/#data-not-included-in-a-backup) を参照ください。

- コンテナ内のGitlabの設定 (`/etc/gitlab`), ホスト上の`{{ gitlab_config_dir }}`(規定値: `/srv/gitlab/config`)の内容
- Container Registryの実イメージ
- TLS証明書

### バックアップ手順

 バックアップは `{{ gitlab_scripts_dir }}/gitlab-backup.py` を root 権限で実行することで行います。
バックアップスクリプトは GitLab の `gitlab-backup` コマンドのラッパーで, アーカイブとメタデータをまとめたバンドルを`{{ gitlab_daily_backup_dir }}`ディレクトリ配下に, `gitlab-backup.tar.gz`という名前で生成します。

バックアップバンドルファイルは, バックアップの生成日時やGitlab公式のリストア処理時に使用する`.tar`アーカイブと, 当該の`.tar`アーカイブのIDなどのリストア処理に必要な情報を格納したメタ情報ファイルを`.tar.gz`形式のアーカイブにまとめたファイルです。

`{{ gitlab_scripts_dir }}/gitlab-backup.py` が正常終了すると,

```shell
Backup stored: <バックアップバンドルファイルのパス>
```

という形式で, 生成したバックアップバンドルファイルのパスを表示します。

実行例を以下に示します:

```shell
# /srv/gitlab/scripts/gitlab-backup.py
Backup stored: /srv/gitlab/daily-backups/gitlab-backup.tar.gz
```

#### バックアップ処理の内容

バックアップ処理の内容は以下の通りです:

1. 指定されたGitLabコンテナ内で`gitlab-backup create`コマンドを実行して
   GitLab公式のバックアップアーカイブを生成します。
2. 生成されたバックアップアーカイブと, メタ情報をまとめたtar.gz形式の
   バックアップバンドルファイルを作成します。

### リストア手順

root権限で, `{{ gitlab_scripts_dir }}/gitlab-restore.py --verbose <bundle.tar.gz>` を実行します。
`gitlab-restore.py`を実行すると, バックアップバンドルファイル内のGitlab公式のバックアップファイル(`.tar`アーカイブ)をGitlab公式手順に従って, リストアします。

リストアスクリプトは 環境変数`GITLAB_ASSUME_YES`に, `GITLAB_ASSUME_YES=1` を指定し, 非対話実行により, リストア処理を行います。公式手順の指示に従い, リストア前に, `puma`, `sidekiq` を停止してリストア処理を行います(リストア処理に必要なPostgreSQLは, 稼働させたまま復元を進めます)。

リストア処理の実行例を以下に示します:

```shell
 # /srv/gitlab/scripts/gitlab-restore.py --verbose /srv/gitlab/daily-backups/gitlab-backup.tar.gz
 Staged backup archive: /srv/gitlab/data/backups/1765706413_2025_12_14_18.6.2_gitlab_backup.tar
 Stopping puma and sidekiq services...
 Detected puma state 'down' via 'down: puma:'
 Detected sidekiq state 'down' via 'down: sidekiq:'
 Restoring backup ID 1765706413_2025_12_14_18.6.2...
 Reconfiguring and starting GitLab...
 Waiting for puma and sidekiq services to be running...
 Detected puma state 'run' via 'run: puma:'
 Detected sidekiq state 'run' via 'run: sidekiq:'
 Restore completed successfully
```

#### リストア処理の内容

リストア処理の内容は以下の通りです:

1. バックアップバンドルファイルを展開し, メタ情報とバックアップアーカイブを取得する。
2. バックアップアーカイブをGitLabバックアップディレクトリに配置する。
3. pumaとsidekiqサービスを停止する。
4. gitlab-backup restore コマンドを実行して復元処理を行う。
5. gitlab-ctl reconfigure と gitlab-ctl start を実行してGitLabを再構成し起動する。
6. pumaとsidekiqサービスが稼働状態になるのを待機する。

## 検証ポイント

- `/srv/gitlab` 以下に設定, ログ, データ, バックアップ, scripts ディレクトリが期待した所有者（`gitlab_user_id` / `gitlab_group_id`）で作成されている。
- `docker compose -f /srv/gitlab/docker-compose.yml ps` で GitLab と GitLab Runner コンテナが稼働している。
- Web UI, SSH, Container Registry が指定したポートで応答する。
- `gitlab-backup.py` がメタ情報付きのバンドルを生成し, `gitlab-restore.py --verbose` で `puma/sidekiq` の停止, 復旧ログが確認できる。
- クリーンインストール実施時は既存ディレクトリや Docker イメージが削除され, 再実行で初期状態から構築される。

## 参考URL

- [公式GitLab Omnibus のコンテナイメージを用いたインストール手順](https://docs.gitlab.com/install/docker/installation/)
- [Gitlabのバックアップ手順](https://docs.gitlab.com/install/docker/backup/)
- [コンテナレジストリ設定手順](https://docs.gitlab.com/ja-jp/administration/packages/container_registry/)