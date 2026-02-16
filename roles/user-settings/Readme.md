# user-settings ロール

本ロールは新規ユーザ作成時に複製される `/etc/skel` 以下のスケルトン環境を構築します。プロキシ設定やシェル初期化ファイル, Emacs 関連ファイルをテンプレートとして配布し, `/etc/skel` に必須の骨組み環境を整備します。すべてのタスクは再実行可能で, 既存ファイルがある場合は整形, 追記のみを行い冪等性を維持します。

本ロールは `/etc/skel` を基点とした標準環境を提供します。運用ポリシーに応じて, `vars/all-config.yml`, `group_vars` や `host_vars` で必要な変数を上書きして利用してください。

主な処理は次の通りです。

- load-params.yml: Debian/RHEL の差分を吸収するために `vars/cross-distro.yml` や共通設定 (`vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込みます。
- directory.yml: 共通ディレクトリ (`/usr/local/bin`) の作成とホームディレクトリバックアップスクリプトの配置を行います。
- directory-bash.yml: Bash用の設定ファイル (`.bashrc`, `.bashrc.proxy` など) を `/etc/skel` に展開します (`user_settings_create_bash_skel` で制御)。
- directory-zsh.yml: zsh用の設定ファイル (`.zshrc`, `.zprofile` など) を `/etc/skel` に展開します (`user_settings_create_zsh_skel` で制御)。
- directory-ssh.yml: SSH用の設定ファイル (`.ssh/config`, `.ssh/authorized_keys`) を `/etc/skel` に展開します (`user_settings_create_ssh_skel` で制御)。
- directory-curl.yml: curl用の設定ファイル (`.curlrc`) を `/etc/skel` に展開します (`user_settings_create_curl_skel` で制御)。
- directory-wget.yml: wget用の設定ファイル (`.wgetrc`) を `/etc/skel` に展開します (`user_settings_create_wget_skel` で制御)。
- directory-screen.yml: screen用の設定ファイル (`.screenrc`) を `/etc/skel` に展開します (`user_settings_create_screen_skel` で制御)。
- directory-tmux.yml: tmux用の設定ファイル (`.tmux.conf`) を `/etc/skel` に展開します (`user_settings_create_tmux_skel` で制御)。
- directory-aspell.yml: aspell用の設定ファイル (`.aspell.conf`) を `/etc/skel` に展開します (`user_settings_create_aspell_skel` で制御)。
- directory-gitignore.yml: Git用の無視ファイルリスト (`.gitignore`) を `/etc/skel` に展開します (`user_settings_create_git_skel` および `user_settings_create_gitignore_on_homedir_skel` で制御)。
- directory-gdb.yml: GDB用の設定ファイル (`.gdbinit`) を `/etc/skel` に展開します (`user_settings_create_gdb_skel` で制御)。
- directory-home-backup-script.yml: ホームディレクトリバックアップスクリプトを `/usr/local/bin/backup-home` に配置します (`user_settings_backup_home_script_enabled` および関連変数で制御)。
- directory-emacs.yml: `/etc/skel/.emacs.d` ツリーを作成し, `init.el` と必須設定ファイル (`proxy-settings.el`, `basic-settings.el`, `japanese-environment.el`) を展開します (`user_settings_create_emacs_skel` で制御)。

- home-command.yml: `/etc/skel/bin` を作成し, `clean-all-docker-images.sh` / `run-docker.sh` といった運用スクリプトをテンプレートから配布します。これらのスクリプトは新規ユーザのホームディレクトリ生成時に自動的に複製されます。

### ユーザホーム操作ロール ( post-user-create ロール )との関係

本ロールではスケルトン環境 (`/etc/skel`) の構築までを行います。ユーザ作成後の既存ユーザホームへの操作は, `post-user-create` ロール ( `create-users` ロール直後に実行 ) で実行され, 以下の処理を行います:

- `users_list` をループし, 各ユーザの `~/bin/` に `install-emacs-packages.sh` が存在しない場合は `/etc/skel/bin/` からコピー
- `create_user_emacs_package_list` で指定されたパッケージを当該ユーザ権限でインストール
- オプションの Emacs 設定ファイル ( aspell-settings.el, auctex-mode-settings.el など ) を `~/.emacs.d/user_settings/` 配下に配布

Emacs パッケージの管理 ( インストール対象パッケージの指定 ) は `post-user-create` ロールで一元管理されます。詳細は `post-user-create` ロールの Readme.md を参照してください。

## 変数一覧

### スケルトン設定ファイル制御変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `user_settings_create_bash_skel` | `false` | Bash用の設定ファイルを作成する場合は `true` を指定します。 |
| `user_settings_create_zsh_skel` | `false` | zsh用の設定ファイルを作成する場合は `true` を指定します。 |
| `user_settings_create_ssh_skel` | `false` | SSH用の設定ファイルを作成する場合は `true` を指定します。 |
| `user_settings_create_curl_skel` | `false` | curl用の設定ファイルを作成する場合は `true` を指定します。 |
| `user_settings_create_wget_skel` | `false` | wget用の設定ファイルを作成する場合は `true` を指定します。 |
| `user_settings_create_screen_skel` | `false` | screen用の設定ファイルを作成する場合は `true` を指定します。 |
| `user_settings_create_tmux_skel` | `false` | tmux用の設定ファイルを作成する場合は `true` を指定します。 |
| `user_settings_create_aspell_skel` | `false` | aspell用の設定ファイルを作成する場合は `true` を指定します。 |
| `user_settings_create_git_skel` | `false` | Git用の設定ファイル (`.gitignore`) を `/etc/skel` に作成する場合は `true` を指定します。 |
| `user_settings_create_gitignore_on_homedir_skel` | `false` | デフォルトの `.gitignore` をホームディレクトリ直下 (`/etc/skel/.gitignore`) に作成する場合は `true` を指定します。 |
| `user_settings_create_gdb_skel` | `false` | GDB用の設定ファイルを作成する場合は `true` を指定します。 |
| `user_settings_create_emacs_skel` | `false` | Emacs用の基本設定ファイルを作成する場合は `true` を指定します。 |

### ホームディレクトリバックアップ関連変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `user_settings_backup_home_script_enabled` | `false` | ホームディレクトリのバックアップスクリプトを作成する場合は `true` を指定します。 |
| `user_settings_backup_home_rotation` | `2` | バックアップ世代数。0以下の場合はスクリプト生成をスキップします。 |
| `user_settings_backup_home_nfs_server` | `""` | マウントするNFSサーバのホスト名。空の場合はスクリプト生成をスキップします。 |
| `user_settings_backup_home_nfs_dir` | `""` | マウントするNFS共有ディレクトリ。空の場合はスクリプト生成をスキップします。 |
| `user_settings_backup_home_mount_point` | `"/mnt"` | NFSマウントポイント。空の場合はスクリプト生成をスキップします。 |
| `user_settings_backup_dir_on_nfs` | `""` | NFSマウントポイント配下のバックアップ配置先ディレクトリ。空の場合はスクリプト生成をスキップします。 |
| `user_settings_backup_output_dir` | `"{{ user_settings_backup_home_mount_point }}{{ user_settings_backup_dir_on_nfs }}"` | 最終的なバックアップ出力先ディレクトリ (計算値)。 |
| `user_settings_backup_users_list` | `[]` | バックアップ対象ユーザのリスト。空の場合はスクリプト生成をスキップします。 |
| `user_settings_backup_bin_dir` | `"/usr/local/bin"` | backup-homeスクリプトを配置するディレクトリ。 |
| `user_settings_backup_share_dir` | `"/usr/local/share/backup-home"` | crontab例など関連ファイルを配置するディレクトリ。 |

### Docker関連変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `create_docker_image_operation_script` | `false` | Dockerイメージ操作用スクリプト作成する場合は `true` を指定します。 |

### プロキシ設定変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `proxy_server` | `""` | HTTP/HTTPS プロキシのホスト名。`_bshrc.proxy.j2`, `_curlrc.j2`, `_ssh__config.j2` などで利用します。 |
| `proxy_port` | `""` | プロキシサーバの待ち受けポート番号。各プロキシ関連テンプレートで参照されます。 |
| `proxy_user` | `""` | プロキシ認証が必要な場合のユーザ名。`_bshrc.proxy.j2` や `_curlrc.j2` で資格情報として展開されます。 |
| `proxy_password` | `""` | プロキシ認証パスワード。認証が不要な場合は空文字にします。 |
| `no_proxy` | `""` | プロキシ経由させないホスト/ドメインの一覧。curl/wget/シェル環境の設定に反映されます。 |

### SSH関連変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `ssh_legacy_key_hosts` | `[]` | 旧形式の鍵を許可するホスト名の一覧。対象ホスト名のみ指定します (FQDNはテンプレート側で付与)。空の場合は設定を出力しません。 |

## テンプレート一覧

| テンプレート名 | 展開先ファイル | 説明 |
| --- | --- | --- |
| `_aspell.conf.j2` | `/etc/skel/.aspell.conf` | aspell 用辞書設定 |
| `_bshrc.lmod.j2` | `/etc/skel/.bashrc.lmod` | Bash で環境モジュール (`Environment Modules`)を有効化 |
| `_bshrc.proxy.j2` | `/etc/skel/.bashrc.proxy` | Bash 向けプロキシ設定 |
| `_bshrc.proxy.j2` | `/etc/skel/.zshrc.proxy` | zsh 向けプロキシ設定 |
| `_curlrc.j2` | `/etc/skel/.curlrc` | curl の既定オプション |
| `_gdbinit.j2` | `/etc/skel/.gdbinit` | GDB 初期化設定 |
| `_gitconfig.j2` | `/etc/skel/.gitconfig` | Git 共通設定 |
| `_gitignore.j2` | `/etc/skel/.gitignore` | Git 無視ルール雛形 (オプション。`user_settings_create_gitignore_on_homedir_skel` で制御) |
| `_screenrc.j2` | `/etc/skel/.screenrc` | GNU Screen 設定 |
| `_tmux.conf.j2` | `/etc/skel/.tmux.conf` | tmux 設定 |
| `_wgetrc.j2` | `/etc/skel/.wgetrc` | wget の既定オプション |
| `_zprofile.j2` | `/etc/skel/.zprofile` | zsh ログイン設定 |
| `_zshrc.j2` | `/etc/skel/.zshrc` | zsh メイン設定 |
| `_zshrc_common.j2` | `/etc/skel/.zshrc.common` | zsh 共通設定 |
| `_zshrc.mine.sample.j2` | `/etc/skel/.zshrc.mine.sample` | zsh ユーザ個別設定サンプル |
| `_ssh__authorized_keys.j2` | `/etc/skel/.ssh/authorized_keys` | authorized_keys 雛形 |
| `_ssh__config.j2` | `/etc/skel/.ssh/config` | OpenSSH 共通設定 |
| `backup-home.j2` | `{{ user_settings_backup_bin_dir }}/backup-home` | ホームバックアップスクリプト |
| `backup-home.cron.example.j2` | `{{ user_settings_backup_share_dir }}/backup-home.cron.example` | ホームバックアップスクリプト用 crontab 例 |
| `clean-all-docker-images.sh.j2` | `/etc/skel/bin/clean-all-docker-images.sh` | Docker イメージ一括削除スクリプト |
| `run-docker.sh.j2` | `/etc/skel/bin/run-docker.sh` | Docker コンテナ起動補助スクリプト |

### Emacs スケルトン配置ファイル

以下のファイルは `/etc/skel/.emacs.d/` ツリー下に配置され, 新規ユーザ作成時に自動的にホームディレクトリにコピーされます。
init.el は Emacs 初期化ファイルで, proxy-settings.el, basic-settings.el, japanese-environment.el はコメント化されていない状態で初期化ファイルから読み込まれます。

| テンプレート名 | 展開先ファイル | 説明 |
| --- | --- | --- |
| `_emacs_d__init.el.j2` | `/etc/skel/.emacs.d/init.el` | Emacs 初期化ファイル ( 必須 )  |
| `_emacs_d__proxy-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/proxy-settings.el` | Emacs プロキシ設定 ( init.el 内で使用 )  |
| `_emacs_d__basic-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/basic-settings.el` | 基本 ロードパス, キーバインド, 編集設定 ( init.el 内で使用 )  |
| `_emacs_d__japanese-environment.el.j2` | `/etc/skel/.emacs.d/user_settings/japanese-environment.el` | 日本語環境設定 ( init.el 内で使用 )  |

オプションの Emacs 設定ファイル ( auctex-mode-settings.el, cmake-settings.el など, init.el でコメント化されているもの ) については, `post-user-create` ロール ( テンプレートから直接各ユーザのホームディレクトリにEmacs設定ファイルに配置するタスクを実施するロール ) の Readme.md を参照してください。

## ホームディレクトリバックアップスクリプトを用いたディレクトリバックアップ

backup-home スクリプト (`/usr/local/bin/backup-home`) は, 指定されたユーザのホームディレクトリを NFS サーバにバックアップするbashスクリプトです。

### 機能

- NFS 接続確認・マウント・アンマウント
- tar コマンドによるアーカイブ化 (xz 圧縮)
- 古いバックアップの自動削除 (`user_settings_backup_home_rotation` で指定した世代数まで保持)
- エラー発生時の自動クリーンアップ (マウントポイント削除, プロセス終了)
- root 権限の自動検出 (root で実行時は sudo 不要、通常ユーザ実行時は自動的に sudo を使用)

### crontabの記載例

このロールは `{{ user_settings_backup_share_dir }}/backup-home.cron.example` (規定値は, `/usr/local/share/backup-home/backup-home.cron.example` ) に crontab サンプルを自動配置します。
このファイルを修正し, `/etc/cron.daily/backup-home` に配置してください:

より詳細な crontab エントリが必要な場合は, crontabのマニュアルに従って, サンプルファイルを修正の上, `/etc/cron.d/backup-home` などに配置してください。

### 実行方法

#### 手動実行の場合 ( 配置先ディレクトリは規定値で記載 ):

手動実行の場合, 以下のように特権ユーザで実行してください:

```bash
sudo /usr/local/bin/backup-home
```

#### 定期実行 (毎日深夜) の場合

提供されるcrontab例 (`backup-home.cron.example`) を適宜修正の上, `/etc/cron.daily/backup-home` に配置してください。
提供されるcrontab例 (`backup-home.cron.example`)は以下の設定になっています:

1. `/usr/local/bin/backup-home` を毎日深夜 (cron.daily の規定実行時刻) に呼び出し
2. 指定されたバックアップ世代数を保持
3. エラーログはシステムのcronログ（`/var/log/syslog` など）に記録

### 留意事項

1. ユーザ作成フロー: 本ロール,  `create-users` ロール,  `post-user-create` ロール の順序で実行されます。既存ユーザに対する Emacs パッケージ導入は `post-user-create` ロールで行われるため, 同じプレイブックで適切な順序に配置してください。詳細は `post-user-create` ロールの Readme.md を参照してください。
2. 各スケルトン設定ファイルの作成要否は `user_settings_create_*_skel` 変数で個別に制御できます。不要な設定ファイルは `false` に設定してスキップしてください。
3. Git 設定: 2026-02-16以降, `.gitconfig` は `post-user-create` ロールで各ユーザのホームディレクトリに作成されます (`post_user_create_gitconfig_enabled: true` の場合)。本ロールでは `/etc/skel/.gitignore` のみを管理します。
4. ホームディレクトリバックアップスクリプトを有効化する場合は, 以下の条件をすべて満たす必要があります:
   - `user_settings_backup_home_script_enabled: true`
   - `user_settings_backup_home_nfs_server` が空でない
   - `user_settings_backup_home_nfs_dir` が空でない
   - `user_settings_backup_home_mount_point` が空でない
   - `user_settings_backup_dir_on_nfs` が空でない
   - `user_settings_backup_users_list` が空でない
   - `user_settings_backup_home_rotation` が1以上

## 検証ポイント

`make run_user_settings` などでロールを実行し, `/etc/skel` 配下のスケルトンと補助スクリプトが生成されることを確認します:

- `/etc/skel` に各種設定ファイル (`.bashrc`, `.zshrc`, `.ssh/config`, `.tmux.conf`, `.screenrc` など) がテンプレート由来で配置され, 所有者 `root:root`・適切なパーミッションになっていること。
- `/etc/skel/.gitignore` は `user_settings_create_gitignore_on_homedir_skel: true` の場合のみ作成されること。
- `/etc/skel/.emacs.d/init.el` および `/etc/skel/.emacs.d/user_settings/` に必須設定ファイル ( `proxy-settings.el`, `basic-settings.el`, `japanese-environment.el` ) が存在すること (`user_settings_create_emacs_skel: true` の場合)。
- `/etc/skel/bin/clean-all-docker-images.sh` と `/etc/skel/bin/run-docker.sh` が `0755` で作成され, 新規ユーザホームにも複製されること (`create_docker_image_operation_script: true` の場合)。
- バックアップスクリプトを有効化した場合, `/usr/local/bin/backup-home` が存在し実行可能になっていること。
- プロキシや個別設定テンプレートに使用する変数 (`proxy_*` など) が意図通り展開されているか `grep` 等で確認してください。
- 各スケルトン設定ファイルの作成を無効化した場合, 該当ファイルが `/etc/skel` に作成されないことを確認してください。

既存ユーザに対する Emacs パッケージインストールおよびオプション設定ファイル配布に関する検証については, `post-user-create` ロールの Readme.md の検証ポイントを参照してください。

## 参考リンク

### cron・crontab マニュアル

#### Ubuntu

- [cron - Linux Man Pages Online (Ubuntu)](https://manpages.ubuntu.com/manpages/focal/man8/cron.8.html) - cron デーモンマニュアル
- [crontab - Linux Man Pages Online (Ubuntu)](https://manpages.ubuntu.com/manpages/focal/man5/crontab.5.html) - crontab ファイルフォーマット
- [crontab(1) - Linux Man Pages Online (Ubuntu)](https://manpages.ubuntu.com/manpages/focal/man1/crontab.1.html) - crontab コマンドマニュアル

#### RHEL/AlmaLinux/CentOS

- [cron(8) - Linux Manual Pages](https://linux.die.net/man/8/cron) - cron デーモンマニュアル
- [crontab(5) - Linux Manual Pages](https://linux.die.net/man/5/crontab) - crontab ファイルフォーマット
- [crontab(1) - Linux Manual Pages](https://linux.die.net/man/1/crontab) - crontab コマンドマニュアル
