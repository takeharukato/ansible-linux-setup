# gitlab-server ロール

- [gitlab-server ロール](#gitlab-server-ロール)
  - [変数一覧](#変数一覧)
  - [ロール内の動作](#ロール内の動作)
  - [Gitlabコンテナの構成](#gitlabコンテナの構成)
    - [Gitlabの公開URL, SSHポート, コンテナレジストリ](#gitlabの公開url-sshポート-コンテナレジストリ)
    - [ポートマッピング](#ポートマッピング)
    - [ボリュームの設定](#ボリュームの設定)
    - [Gitlabの初期管理者パスワード参照方法](#gitlabの初期管理者パスワード参照方法)
    - [Gitlab管理者パスワードの変更方法](#gitlab管理者パスワードの変更方法)
    - [Gitlab関連ファイルの所有者, グループIDについて](#gitlab関連ファイルの所有者-グループidについて)
  - [バックアップ / リストアについて](#バックアップ--リストアについて)
    - [バックアップの内容](#バックアップの内容)
    - [バックアップに含まれない内容](#バックアップに含まれない内容)
    - [バックアップ手順](#バックアップ手順)
      - [バックアップ処理の内容](#バックアップ処理の内容)
    - [リストア手順](#リストア手順)
      - [リストア処理の内容](#リストア処理の内容)
    - [定期バックアップ](#定期バックアップ)
  - [検証ポイント](#検証ポイント)
  - [付録) 本ロールから導入されるバックアップ, リストア用スクリプトのコマンドライン仕様](#付録-本ロールから導入されるバックアップ-リストア用スクリプトのコマンドライン仕様)
    - [gitlab-backup.pyスクリプトのコマンドラインオプション](#gitlab-backuppyスクリプトのコマンドラインオプション)
    - [gitlab-restore.pyスクリプトのコマンドラインオプション](#gitlab-restorepyスクリプトのコマンドラインオプション)
  - [参考URL](#参考url)


このロールは GitLab Omnibus の公式 Docker イメージと GitLab Runner をホスト上で運用するための基盤を構築します。`docker compose` によるコンテナ起動 / 停止, 永続化ディレクトリの準備, バックアップ / リストア補助スクリプトの展開を自動化し, 再実行可能な手順で GitLab サービスを維持します。

以下の処理を実施します:

- 公式 Docker イメージ用のホームディレクトリ ( `/srv/gitlab` ) 配下に設定, ログ, データ, バックアップ用ディレクトリを作成
- IPv4/IPv6 フォワーディングを有効化し, 管理インターフェースで RA (Router Advertisement, ルータ広告) を受け入れる sysctl 設定を配置
- `docker-compose.yml` をテンプレートから生成し, GitLab 本体と GitLab Runner のコンテナを `docker compose up -d` で起動
- `gitlab-backup.py` / `gitlab-restore.py` を `/srv/gitlab/scripts/` に展開してバックアップ運用を支援 ( `GITLAB_ASSUME_YES=1` を利用した非対話リストアに対応 )
- 運用前に `gitlab-ctl stop puma/sidekiq` を行い PostgreSQL (ポストグレスキューエル, リレーショナルデータベース管理システム) を停止させずにリストアできるよう制御
- クリーンインストール指定時には既存の設定, データ, コンテナイメージを削除して初期状態から再構築

GitLab の初期ルートパスワードファイルや公開 URL, 通信ポートもロールの変数で一元管理します。

## 変数一覧

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `gitlab_hostname` | `""` | GitLab WEB UI/Container Registryの公開URL中のホスト名部分を指定します。本変数が, 未設定または空文字列の場合, gitlabの導入を行いません。|
| `gitlab_https_port` | `9443` | GitLab Web UI (HTTPS) 公開ポート。|
| `gitlab_ssh_port` | `2224` | GitLab SSH (リポジトリ操作用) 公開ポート。|
| `gitlab_registry_port` | `5050` | コンテナレジストリ公開ポート。|
| `gitlab_wait_host_stopped` | `"127.0.0.1"` | GitLabサービス停止を待ち合わせる(接続先)ホスト名/IPアドレス。|
| `gitlab_wait_host_started` | `"{{ inventory_hostname }}"` | GitLabサービス開始を待ち合わせる(接続先)ホスト名/IPアドレス。|
| `gitlab_wait_timeout` | `600` | GitLabサービス待ち合わせ時間(単位: 秒)。|
| `gitlab_wait_delay` | `5` | GitLabサービス待ち合わせる際の開始遅延時間(単位: 秒)。|
| `gitlab_wait_sleep` | `2` | GitLabサービス待ち合わせる際の待機間隔(単位: 秒)。|
| `gitlab_wait_delegate_to` | `"localhost"` | GitLabサービス待ち合わせる際の接続元ホスト名/IPアドレス。|
| `gitlab_external_url` | `https://{{ gitlab_hostname }}:{{ gitlab_https_port }}` | Web UI へアクセスする外部 URL。|
| `gitlab_docker_image` | `gitlab/gitlab-ce:18.6.2-ce.0` | GitLab Omnibus Docker イメージ。公式の推奨に従って, バージョン名を明示してイメージを指定してください。|
| `gitlab_runner_docker_image` | `gitlab/gitlab-runner:ubuntu-v18.6.6` | GitLab Runner Docker イメージ。GitLab 本体とメジャーバージョン, マイナーバージョンを合わせてください。|
| `gitlab_home_dir` | `/srv/gitlab` | GitLab 導入先ディレクトリ。|
| `gitlab_config_dir` | `/srv/gitlab/config` | 設定ファイル格納ディレクトリ。|
| `gitlab_logs_dir` | `/srv/gitlab/logs` | ログ格納ディレクトリ。|
| `gitlab_data_dir` | `/srv/gitlab/data` | データ格納ディレクトリ。|
| `gitlab_backup_dir` | `/srv/gitlab/data/backups` | GitLab 標準バックアップの出力先。|
| `gitlab_daily_backup_dir` | `/srv/gitlab/daily-backup` | デイリーバックアップ用のバックアップバンドルファイル保存先ディレクトリ。|
| `gitlab_scripts_dir` | `/srv/gitlab/scripts` | バックアップ関連スクリプト配置先。|
| `gitlab_docker_compose_file` | `/srv/gitlab/docker-compose.yml` | Gitlabのdocker compose 定義ファイル。|
| `gitlab_clean_install` | `false` | `true` の場合は既存設定, データ, ホームディレクトリを削除してクリーンインストールします。|
| `gitlab_remove_container_images` | `false` | `true` の場合は, 既存の GitLab / Runner イメージを削除してからインストールを開始します。|
| `gitlab_daily_backup_script_file` | `daily-backup-gitlab.sh` | Cronに登録するデイリーバックアップスクリプトファイル名 |
| `gitlab_backup_rotation` | `7` | デイリーバックアップのローテーション世代数 |
| `gitlab_backup_nfs_server` | `nfs.example.org` | Gitlabのバックアップバンドルファイルを保存するNFSサーバ|
| `gitlab_backup_nfs_dir` | `share` | Gitlabのバックアップバンドルファイルを保存するNFSサーバのマウント時に指定する共有ディレクトリ名|
| `gitlab_backup_mount_point` | `/mnt` | デイリーバックアップ時のNFSマウントポイント(NFSのマウント/アンマウント時に使用) |
| `gitlab_backup_dir_on_nfs` | `/gitlab-backups` | デイリーバックアップ時のNFSマウントポイント配下のバックアップ配置先ディレクトリ |

## ロール内の動作

1. [tasks/load-params.yml](tasks/load-params.yml) で OS ごとのパッケージ定義や共通パラメータを取り込みます。
2. `gitlab_clean_install` や `gitlab_remove_container_images` が有効な場合, [tasks/config-clean-install.yml](tasks/config-clean-install.yml) が既存ディレクトリと Docker イメージを削除します。
3. [tasks/directory-gitlab.yml](tasks/directory-gitlab.yml) が GitLab 用ユーザ / グループを確認し, ホーム, 設定, データ, バックアップ各ディレクトリを所有権付きで作成します。
4. 同タスク内で `docker-compose.yml`, `gitlab-backup.py`, `gitlab-restore.py` を配置します。
5. [tasks/sysctl.yml](tasks/sysctl.yml) が `templates/90-gitlab-forwarding.conf.j2` を `/etc/sysctl.d/90-gitlab-forwarding.conf` に配置し, IPv4/IPv6 フォワーディング (`net.ipv4.ip_forward`, `net.ipv6.conf.all.forwarding`, `net.ipv6.conf.default.forwarding`), 管理 IF (Interface, インターフェース) の RA (Router Advertisement, ルータ広告) 受信 (`net.ipv6.conf.<mgmt_nic>.accept_ra`) を有効化します。配置時は `gitlab_reload_sysctl` ハンドラを通知し, `sysctl --system` で設定を反映します。
6. [tasks/service.yml](tasks/service.yml) が `docker compose up -d` で GitLab / Runner コンテナを起動し, HTTPS (Hypertext Transfer Protocol Secure) / SSH (Secure Shell) / Registry ポートが開くまで待機します。その後, アクセス URL や初期パスワードファイルパスを表示します。
7. ロール再実行時には既存の compose ファイルや永続化ディレクトリを再利用し, 冪等に整備を行います。停止したい場合は [tasks/stop-service.yml](tasks/stop-service.yml) を参照してください。

## Gitlabコンテナの構成

本ロールでは, 以下の2つのコンテナからなるDocker composeを生成します:

|コンテナ名|用途|
|---|---|
|gitlab|gitlab本体|
|gitlab-runner|gitlabのCI/CDで使用するgitlab-runner|

Docker composeファイルは, `{{ gitlab_home_dir }}/docker-compose.yml` (規定値は, `/srv/gitlab/docker-compose.yml` )に生成されます。

### Gitlabの公開URL, SSHポート, コンテナレジストリ

例えば, `gitlab_hostname`に, `devserver.example.org`, `gitlab_https_port`に, `9443`, `gitlab_ssh_port`に, `2224`, `gitlab_registry_port`に`5050`をそれぞれ指定して,
本ロールを適用すると, 以下のようにGitlabのリポジトリサービスとコンテナレジストリサービスが構成されます:

|用途|URL/コンテナレジストリ|URL/コンテナレジストリの例|
|---|---|---|
|Gitlab WEB UIのURL|https://`gitlab_hostname`:`gitlab_https_port`|`https://devserver.example.org:9443`|
|Gitlabリポジトリ操作用SSH|ssh://`gitlab_hostname`:`gitlab_ssh_port`|`ssh://devserver.example.org:2224`|
|Gitlab Container Registry|`gitlab_hostname`:`gitlab_registry_port`|`devserver.example.org:5050`|

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

### Gitlabの初期管理者パスワード参照方法

`{{ gitlab_config_dir }}`(規定値は, `/srv/gitlab/config`)に, コンテナ内の`/etc/gitlab`ディレクトリがマウントされます。このため, 初期パスワードは, ホスト上の`{{ gitlab_config_dir }}/initial_root_password` (規定値は, `/srv/gitlab/config/initial_root_password` )を参照することで確認可能です。

上記ファイルは, **Gitlab構築後24時間で自動的に消去**されます。

### Gitlab管理者パスワードの変更方法

Gitlab構築後24時間経過し, 初期管理者パスワードを参照不能になった場合など, Gitlabの管理者パスワードを実行中に変更する必要が生じた場合は, `gitlab`コンテナ内に入り, `gitlab-rake "gitlab:password:reset[root]"`コマンドを実行します。

具体的なコマンドラインは, 以下の通りです:

```shell
docker exec -it gitlab gitlab-rake "gitlab:password:reset[root]"
```

実行例を以下に示します:

```shell
$ docker exec -it gitlab gitlab-rake "gitlab:password:reset[root]"
Enter password: <設定するパスワード文字列>
Confirm password: <設定するパスワード文字列>
Password successfully updated for user with username root.
```

上記で`<設定するパスワード文字列>`には, 新たに設定するパスワード文字列を入力します。
なお, 実際の実行画面では, 入力したパスワード文字列は画面に表示されません(エコーバックされません)。

設定するパスワードは, [Gitlabのパスワード要件](https://docs.gitlab.com/ja-jp/user/profile/user_passwords/#password-requirements)を満たしている必要があります。

### Gitlab関連ファイルの所有者, グループIDについて

本稿執筆時点では, Gitlabの公式コンテナイメージでは, Gitlab関連ファイルの所有者, グループIDが`998`番であることを前提に構成されています。
このため, 本ロールでは, ユーザID, グループIDを`998`に設定して, Gitlab関連のディレクトリ, ファイルを生成します。

ユーザID, グループID が `998` 番のユーザやグループがない場合は, `gitlab`ユーザ, `gitlab`グループを`998`番のユーザ, グループとして作成します。

これらのユーザID, グループIDは, `roles/gitlab-server/vars/main.yml`内の`gitlab_user_id`, `gitlab_group_id`変数で定義されています。

## バックアップ / リストアについて

本ロールでは, [公式のGitlabバックアップ手順](https://docs.gitlab.com/administration/backup_restore/)に従って, バックアップ, リストアを行う処理を自動化するスクリプトを生成します。

### バックアップの内容

Gitlabの公式手順に従って, バックアップを生成, 復元するため, 以下の内容が含まれます
(詳細は, [Data included in a backup](https://docs.gitlab.com/administration/backup_restore/backup_gitlab/#data-included-in-a-backup) 参照):

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
必要に応じて別途バックアップを取ってください。詳細は, [Data not included in a backup](https://docs.gitlab.com/administration/backup_restore/backup_gitlab/#data-not-included-in-a-backup) を参照ください。

- コンテナ内のGitlabの設定 (`/etc/gitlab`, ホスト上の`{{ gitlab_config_dir }}`(規定値: `/srv/gitlab/config`)の内容
- Container Registryの実イメージ
- TLS証明書

公式のバックアップアーカイブには, コンテナ内のGitlabの設定ディレクトリ (`/etc/gitlab`, ホスト上の`{{ gitlab_config_dir }}`, 規定値: `/srv/gitlab/config`)の内容は含まれません。

本ロールから導入されるバックアップスクリプト, リストアスクリプトでは, バックアップバンドルアーカイブ中に, Gitlabの主要設定ファイル(`/srv/gitlab/config/gitlab.rb`ファイル), Gitlabの機密情報を格納したjsonファイル(`/srv/gitlab/config/gitlab-secrets.json`ファイル)を同梱し, リストア時に復元するようにしています。

これら以外のコンテナ内のGitlabの設定ディレクトリ (`/etc/gitlab`, ホスト上の`{{ gitlab_config_dir }}`, 規定値: `/srv/gitlab/config`)配下のファイルをバックアップ, リストアする場合は, 手動で実施してください。

また, 後方互換のため, Gitlabの主要設定ファイル(`/srv/gitlab/config/gitlab.rb`ファイル), Gitlabの機密情報を格納したjsonファイル(`/srv/gitlab/config/gitlab-secrets.json`ファイル)が含まれないバックアップバンドルファイルからリストア処理を行った場合もエラー終了せず, リストア処理を継続します。

### バックアップ手順

 バックアップは `{{ gitlab_scripts_dir }}/gitlab-backup.py` を root 権限で実行することで行います。
バックアップスクリプトは GitLab の `gitlab-backup` コマンドのラッパーで, アーカイブとメタデータをまとめたバンドルを`{{ gitlab_daily_backup_dir }}`ディレクトリ配下に, `gitlab-backup.tar.gz`という名前で生成します。

本スクリプトで作成するバックアップバンドルファイルは, 以下の情報が含まれた`.tar.gz`形式のアーカイブです。

- バックアップの生成日時やGitlab公式のリストア処理時に使用する`.tar`アーカイブ
- 当該の`.tar`アーカイブのIDなどのリストア処理に必要な情報を格納したメタ情報ファイル
- Gitlabの設定 (`/etc/gitlab/gitlab.rb`, ホスト上の`{{ gitlab_config_dir }}/gitlab.rb`(規定値: `/srv/gitlab/config/gitlab.rb`)の内容)
- Gitlabの機密情報ファイル`/etc/gitlab/gitlab-secrets.json`, ホスト上の`{{ gitlab_config_dir }}/gitlab-secrets.json`(規定値: `/srv/gitlab/config/gitlab-secrets.json`)の内容

本バックアップスクリプトは, スクリプト実行中にコンテナ内のgitアカウントのUID/GID番号を取得し, コンテナ内からアクセス可能なユーザ権, グループ権を設定して, バックアップバンドルファイル内のGitlab公式のバックアップファイル(`.tar`アーカイブ)のUID/GID番号を設定します。
UID/GID番号を取得できなかった場合は, `gitlab_user_id`, `gitlab_group_id`変数の設定値に従って, ユーザID, グループIDを設定します。


`{{ gitlab_scripts_dir }}/gitlab-backup.py` が正常終了すると,

```shell
Backup stored: <バックアップバンドルファイルのパス>
```

という形式で, 生成したバックアップバンドルファイルのパスを表示します。

実行例を以下に示します:

```shell
$ sudo /srv/gitlab/scripts/gitlab-backup.py --verbose
Detected git user from container: uid=998, gid=998
Creating GitLab backup...
2026-02-07 16:09:52 UTC -- Dumping database ...
2026-02-07 16:09:52 UTC -- Dumping PostgreSQL database gitlabhq_production ...
2026-02-07 16:09:54 UTC -- [DONE]
2026-02-07 16:09:54 UTC -- Dumping database ... done
2026-02-07 16:09:54 UTC -- Dumping repositories ...
2026-02-07 16:09:54 UTC -- Dumping repositories ... done
2026-02-07 16:09:54 UTC -- Dumping uploads ...
2026-02-07 16:09:54 UTC -- Dumping uploads ... done
2026-02-07 16:09:54 UTC -- Dumping builds ...
2026-02-07 16:09:54 UTC -- Dumping builds ... done
2026-02-07 16:09:54 UTC -- Dumping artifacts ...
2026-02-07 16:09:54 UTC -- Dumping artifacts ... done
2026-02-07 16:09:54 UTC -- Dumping pages ...
2026-02-07 16:09:54 UTC -- Dumping pages ... done
2026-02-07 16:09:54 UTC -- Dumping lfs objects ...
2026-02-07 16:09:54 UTC -- Dumping lfs objects ... done
2026-02-07 16:09:54 UTC -- Dumping terraform states ...
2026-02-07 16:09:54 UTC -- Dumping terraform states ... done
2026-02-07 16:09:54 UTC -- Dumping container registry images ...
2026-02-07 16:09:54 UTC -- Dumping container registry images ... done
2026-02-07 16:09:54 UTC -- Dumping packages ...
2026-02-07 16:09:54 UTC -- Dumping packages ... done
2026-02-07 16:09:54 UTC -- Dumping ci secure files ...
2026-02-07 16:09:54 UTC -- Dumping ci secure files ... done
2026-02-07 16:09:54 UTC -- Dumping external diffs ...
2026-02-07 16:09:54 UTC -- Dumping external diffs ... done
2026-02-07 16:09:54 UTC -- Creating backup archive: 1770480592_2026_02_07_18.6.2_gitlab_backup.tar ...
2026-02-07 16:09:54 UTC -- Creating backup archive: 1770480592_2026_02_07_18.6.2_gitlab_backup.tar ... done
2026-02-07 16:09:54 UTC -- Uploading backup archive to remote storage  ... [SKIPPED]
2026-02-07 16:09:54 UTC -- Deleting old backups ... [SKIPPED]
2026-02-07 16:09:54 UTC -- Deleting tar staging files ...
2026-02-07 16:09:54 UTC -- Cleaning up /var/opt/gitlab/backups/backup_information.yml
2026-02-07 16:09:54 UTC -- Cleaning up /var/opt/gitlab/backups/db
2026-02-07 16:09:54 UTC -- Cleaning up /var/opt/gitlab/backups/repositories
2026-02-07 16:09:54 UTC -- Cleaning up /var/opt/gitlab/backups/uploads.tar.gz
2026-02-07 16:09:54 UTC -- Cleaning up /var/opt/gitlab/backups/builds.tar.gz
2026-02-07 16:09:54 UTC -- Cleaning up /var/opt/gitlab/backups/artifacts.tar.gz
2026-02-07 16:09:54 UTC -- Cleaning up /var/opt/gitlab/backups/pages.tar.gz
2026-02-07 16:09:54 UTC -- Cleaning up /var/opt/gitlab/backups/lfs.tar.gz
2026-02-07 16:09:54 UTC -- Cleaning up /var/opt/gitlab/backups/terraform_state.tar.gz
2026-02-07 16:09:54 UTC -- Cleaning up /var/opt/gitlab/backups/registry.tar.gz
2026-02-07 16:09:54 UTC -- Cleaning up /var/opt/gitlab/backups/packages.tar.gz
2026-02-07 16:09:54 UTC -- Cleaning up /var/opt/gitlab/backups/ci_secure_files.tar.gz
2026-02-07 16:09:54 UTC -- Cleaning up /var/opt/gitlab/backups/external_diffs.tar.gz
2026-02-07 16:09:54 UTC -- Deleting tar staging files ... done
2026-02-07 16:09:54 UTC -- Deleting backups/tmp ...
2026-02-07 16:09:54 UTC -- Deleting backups/tmp ... done
2026-02-07 16:09:54 UTC -- Warning: Your gitlab.rb and gitlab-secrets.json files contain sensitive data
and are not included in this backup. You will need these files to restore a backup.
Please back them up manually.
2026-02-07 16:09:54 UTC -- Backup 1770480592_2026_02_07_18.6.2 is done.
2026-02-07 16:09:54 UTC -- Deleting backup and restore PID file at [/opt/gitlab/embedded/service/gitlab-rails/tmp/backup_restore.pid] ... done

Collecting configuration files from /srv/gitlab/config...
  Found: gitlab.rb
  Found: gitlab-secrets.json
Creating backup bundle: /srv/gitlab/daily-backup/gitlab-backup.tar.gz
Adding 1770480592_2026_02_07_18.6.2_gitlab_backup.tar with uid=998, gid=998
Adding metadata.json with uid=998, gid=998
Adding config/gitlab.rb with uid=998, gid=998
Adding config/gitlab-secrets.json with uid=998, gid=998

Bundle contents: /srv/gitlab/daily-backup/gitlab-backup.tar.gz
Name                                                       Size    UID    GID Owner      Group
----------------------------------------------------------------------------------------------------
1770480592_2026_02_07_18.6.2_gitlab_backup.tar           972800    998    998 gitlab     gitlab
metadata.json                                               405    998    998 gitlab     gitlab
config/gitlab.rb                                         160138    998    998 gitlab     gitlab
config/gitlab-secrets.json                                16499    998    998 gitlab     gitlab
Backup stored: /srv/gitlab/daily-backup/gitlab-backup.tar.gz
```

#### バックアップ処理の内容

バックアップ処理の内容は以下の通りです:

1. 指定されたGitLabコンテナ内で`gitlab-backup create`コマンドを実行して
   GitLab公式のバックアップアーカイブを生成します。
2. 生成されたバックアップアーカイブ, Gitlabの設定, Gitlabの機密情報, および, メタ情報をまとめたtar.gz形式のバックアップバンドルファイルを作成します。

### リストア手順

root権限で, `{{ gitlab_scripts_dir }}/gitlab-restore.py --verbose <bundle.tar.gz>` を実行します。
`gitlab-restore.py`を実行すると, バックアップバンドルファイル内のGitlab公式のバックアップファイル(`.tar`アーカイブ)をGitlab公式手順に従って, リストアします。

本リストアスクリプトは, スクリプト実行中にコンテナ内のgitアカウントのUID/GID番号を取得し, コンテナ内からアクセス可能なユーザ権, グループ権を設定して, バックアップバンドルファイル内のGitlab公式のバックアップファイル(`.tar`アーカイブ)を配置します。コンテナ内のgitアカウントのUID/GID番号を取得できなかった場合は, `gitlab_user_id`, `gitlab_group_id`変数の設定値に従って, ユーザID, グループIDを設定します。

リストアスクリプトは 環境変数`GITLAB_ASSUME_YES`に, `GITLAB_ASSUME_YES=1` を指定し, 非対話実行により, リストア処理を行います。公式手順の指示に従い, リストア前に, `puma`, `sidekiq` を停止してリストア処理を行います(リストア処理に必要なPostgreSQLは, 稼働させたまま復元を進めます)。

リストア処理の実行例を以下に示します:

```shell
$ sudo /srv/gitlab/scripts/gitlab-restore.py --verbose /srv/gitlab/daily-backup/gitlab-backup.tar.gz
Detected git user from container: uid=998, gid=998
Restoring configuration files...
Restoring configuration files to /srv/gitlab/config...
  Restored: gitlab-secrets.json with uid=998, gid=998
  Restored: gitlab.rb with uid=998, gid=998
Restored 2 configuration file(s)
Staged backup archive: /srv/gitlab/data/backups/1770480592_2026_02_07_18.6.2_gitlab_backup.tar
Stopping puma and sidekiq services...
Detected puma state 'down' via 'down: puma:'
Detected sidekiq state 'down' via 'down: sidekiq:'
Restoring backup ID 1770480592_2026_02_07_18.6.2...
Reconfiguring and starting GitLab...
Waiting for puma and sidekiq services to be running...
Detected puma state 'run' via 'run: puma:'
Detected sidekiq state 'run' via 'run: sidekiq:'
Restore completed successfully
```

Gitlabの設定 (`gitlab.rb`), Gitlabの機密情報ファイル(`gitlab-secrets.json`)を含まないバックアップバンドルファイルからリストアした場合の例を以下に示します。

```shell
 $ sudo /srv/gitlab/scripts/gitlab-restore.py --verbose /srv/gitlab/daily-backup/gitlab-backup.tar.gz
Detected git user from container: uid=998, gid=998
Restoring configuration files...
No configuration files found in backup bundle
Staged backup archive: /srv/gitlab/data/backups/1770477278_2026_02_07_18.6.2_gitlab_backup.tar
Stopping puma and sidekiq services...
Detected puma state 'down' via 'down: puma:'
Detected sidekiq state 'down' via 'down: sidekiq:'
Restoring backup ID 1770477278_2026_02_07_18.6.2...
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

### 定期バックアップ

本ロールでは, `{{ gitlab_scripts_dir }}` (規定値: `/srv/gitlab/scripts`) 配下に, `{{ gitlab_daily_backup_script_file }}` (規定値: `daily-backup-gitlab.sh`)という名前で
定期バックアップ処理を行うシェルスクリプトを導入します。

本スクリプトは, NFS (Network File System) サーバ上に`gitlab-backup-世代番号.tgz`ように世代番号を付加し,
Gitlabバックアップのバックアップバンドルファイルをコピーします。

本スクリプトは, **Gitlab導入先のディレクトリを参照可能な権限で実行**する必要があります。
このため, 本スクリプトは, `sudo`コマンドなどにより`root`権限で本スクリプトを実行することを想定しています。

`crontab -e`コマンドで以下のcrontabエントリを作成することで定期バックアップを行うことができます。

```:text
0 3 * * * sudo /srv/gitlab/scripts/daily-backup-gitlab.sh
```

上記の設定の場合, 毎日午前3時に`{{ gitlab_daily_backup_dir }}`にバックアップファイルを生成後,
`{{gitlab_backup_nfs_server}}:{{gitlab_backup_nfs_dir}}`をマウントポイントに指定して,
NFS (Network File System) サーバをマウントし, バックアップファイルを当該ディレクトリにコピーします。

## 検証ポイント

- `/srv/gitlab` 以下に設定, ログ, データ, バックアップ, scripts ディレクトリが期待した所有者 ( `gitlab_user_id` / `gitlab_group_id` ) で作成されていること。
- `/etc/sysctl.d/90-gitlab-forwarding.conf` が配備され, `sysctl net.ipv4.ip_forward`, `sysctl net.ipv6.conf.all.forwarding` が `1` に設定されていること。
- `docker compose -f /srv/gitlab/docker-compose.yml ps` で GitLab と GitLab Runner コンテナが稼働していること。
- Web UI (User Interface, ユーザインターフェース), SSH (Secure Shell), Container Registry が指定したポートで応答すること。
- `gitlab-backup.py` 実行時にメタ情報付きのバンドルが生成されること。
- `gitlab-restore.py --verbose <バックアップバンドルファイル>` 実行時に, `puma/sidekiq` の停止, 復旧ログが確認できること。
- `gitlab-restore.py --verbose <バックアップバンドルファイル>` 実行後にバックアップしたリポジトリやユーザ情報が復元されていること。
- クリーンインストール実施時は既存ディレクトリや Docker イメージが削除され, 再実行で初期状態から構築されていること。

## 付録) 本ロールから導入されるバックアップ, リストア用スクリプトのコマンドライン仕様

本節では, 本ロールから導入されるバックアップ, リストア用スクリプトのコマンドライン仕様について説明します。

### gitlab-backup.pyスクリプトのコマンドラインオプション

本節では, 本ロールから導入されるgitlab-backup.pyスクリプトのコマンドラインオプション仕様を以下に示します:

```plaintext
名前:
  gitlab-backup.py - Gitlabのバックアップバンドルファイルを作成する
書式:
  gitlab-backup.py [-h]
                   [--docker-cli DOCKER_CLI]
                   [--container CONTAINER]
                   [--backup-dir BACKUP_DIR]
                   [--daily-dir DAILY_DIR]
                   [--config-dir CONFIG_DIR]
                   [--verbose]

GitLabのバックアップを作成およびアーカイブする

オプション:
  -h, --help ヘルプメッセージを表示して終了する
  --docker-cli DOCKER_CLI dockerコマンドのコマンド名を指定する(規定値は, `docker`)
  --container CONTAINER GitlabコンテナのコンテナIDを指定する (規定値は, `gitlab`)
  --backup-dir BACKUP_DIR Gitlab公式バックアップtarアーカイブ配置先ディレクトリを指定する。未指定時は, `gitlab_backup_dir`変数の内容に従って設定される。 規定値は, `/srv/gitlab/data/backups`となる。
  --daily-dir DAILY_DIR バックアップバンドルアーカイブの格納先ディレクトリを指定する。未指定時は, `gitlab_daily_backup_dir` 変数の内容に従って設定される。 規定値は, `/srv/gitlab/daily-backup` となる。
  --config-dir CONFIG_DIR GitLab設定ディレクトリを指定する。未指定時は, `gitlab_config_dir`  変数の内容に従って設定される。 規定値は,  `/srv/gitlab/config` となる。
  --verbose バックアップ作成中に詳細ログを有効化 (規定値は, `false`, 詳細ログを表示しない)
```

### gitlab-restore.pyスクリプトのコマンドラインオプション

本節では, 本ロールから導入されるgitlab-restore.pyスクリプトのコマンドラインオプション仕様を以下に示します:

```plaintext
名前:
  gitlab-restore.py - GitlabのバックアップバンドルファイルからGitlabの設定を復元する
書式:
  gitlab-restore.py [-h]
                    [--docker-cli DOCKER_CLI]
                    [--container CONTAINER]
                    [--backup-dir BACKUP_DIR]
                    [--config-dir CONFIG_DIR]
                    [--check-interval CHECK_INTERVAL]
                    [--timeout TIMEOUT]
                    [--skip-config]
                    [--skip-reconfigure]
                    [--verbose]
                    bundle

バックアップバンドルからGitLabを復元する
位置引数:
  bundle バックアップバンドル tar.gz のパス

オプション:
  -h, --help 本ヘルプメッセージを表示して終了
  --docker-cli DOCKER_CLI dockerコマンドのコマンド名を指定する(規定値は, `docker`)
  --container CONTAINER GitlabコンテナのコンテナIDを指定する (規定値は, `gitlab`)
  --backup-dir BACKUP_DIR Gitlab公式バックアップtarアーカイブ配置先ディレクトリを指定する。未指定時は, `gitlab_backup_dir`変数の内容に従って設定される。 規定値は, `/srv/gitlab/data/backups`となる。
  --config-dir CONFIG_DIR GitLab設定ディレクトリを指定する。未指定時は, `gitlab_config_dir` 変数の内容に従って設定される。 規定値は, `/srv/gitlab/config` となる。
  --check-interval CHECK_INTERVAL サービス状態チェック間隔 ( 単位:秒, 規定値は, 3 秒 )
  --timeout TIMEOUT サービス状態遷移待機時間 ( 単位:秒, 規定値は, 120 秒)
  --skip-config 設定ファイル ( gitlab.rb), Gitlabの機密情報ファイル(gitlab-secrets.json ) の復元をスキップする
  (規定値は, `false`, 設定ファイル ( gitlab.rb), Gitlabの機密情報ファイル(gitlab-secrets.json ) の復元を試みる)
  --skip-reconfigure (`gitlab-ctl reconfigure`による)再設定処理(設定ファイル(gitlab.rb)を反映する処理)をスキップする(規定値は, `false`, 再設定処理 (`gitlab-ctl reconfigure`)を実行する)。
    gitlab.rbを永続化しない運用(キャッシュ内の設定のみで動作し, gitlab.rbへの書き戻しを行わない設定で動作する環境)の場合で, かつ, DBの内容に変更がない場合, 例えば, gitlab-secrets.jsonのみの変更の場合に使用することを想定したオプションである。
    本ロールでは, `docker-compose.yml`内で, 環境変数を用いて, Gitlabの動作オプションを指定しているため, 本オプションを使用する必要はない, また, Gitlabの公式手順でもDB更新後の再構築を行うことが推奨されているため, 通常運用では使用しないオプションであるため, 規定値は, `false`となっている。
  --verbose リストア動作中の詳細ログ出力を有効化 (規定値は, `false`, 詳細ログを表示しない)
```

## 参考URL

- [公式GitLab Omnibus のコンテナイメージを用いたインストール手順](https://docs.gitlab.com/install/docker/installation/)
- [Gitlabのバックアップ手順](https://docs.gitlab.com/install/docker/backup/)
- [Storing configuration files](https://docs.gitlab.com/administration/backup_restore/backup_gitlab/#storing-configuration-files) Gitlabの設定ファイル, 機密情報ファイルに関する説明
- [When the secrets file is lost](https://docs.gitlab.com/administration/backup_restore/troubleshooting_backup_gitlab/#when-the-secrets-file-is-lost) 機密情報ファイル紛失時の対処法に関する説明
- [コンテナレジストリ設定手順](https://docs.gitlab.com/ja-jp/administration/packages/container_registry/)
- [Gitlabのパスワード要件](https://docs.gitlab.com/ja-jp/user/profile/user_passwords/#password-requirements)
