# user-settings ロール

本ロールは新規ユーザ作成時に複製される `/etc/skel` 以下のスケルトン環境を構築します。プロキシ設定やシェル初期化ファイル, Emacs 関連ファイルをテンプレートとして配布し, `/etc/skel` にスケルトン環境を整備します。すべてのタスクは再実行可能で, 既存ファイルがある場合は整形, 追記のみを行い冪等性を維持します。

## 概要

本ロールは `/etc/skel` を基点とした標準環境を提供します。運用ポリシーに応じて, `vars/all-config.yml`, `group_vars` や `host_vars` で必要な変数を上書きして利用してください。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Ansible | - | インフラストラクチャの構成管理と自動化を行うオープンソースツール。YAML 形式のプレイブックでシステム構成を記述し, SSH を使用して複数のリモートホストに対して冪等な変更を実行できる。 |
| aspell | - | スペルチェッカープログラム, テキストファイルの綴字をチェック |
| Bash | - | GNU Bourne Again Shell, Linuxで標準的に使用されるシェル |
| cron | - | スケジューラデーモン, 定期的にコマンドやスクリプトを実行 |
| crontab | - | cron テーブル, ユーザごとのスケジューリング設定ファイル |
| curl | - | コマンドラインHTTPクライアント, URLでデータ転送をサポート |
| Debian | - | コミュニティ主導のLinuxディストリビューション, Ubuntu の基盤 |
| Docker | - | コンテナ型仮想化技術を実装したオープンソースのプラットフォーム。アプリケーションとその実行環境を軽量な仮想コンテナとしてパッケージ化し, ホストOS上で隔離して実行する。仮想マシンと異なり, ゲストOSを必要とせず, ホストOSのカーネルを共有することで高速起動と低オーバーヘッドを実現する。コンテナイメージの作成, 配布, 実行を管理する Docker Engine と, イメージを保管・共有する Docker Hub などのレジストリから構成される。 |
| Emacs | - | テキスト編集機能が豊富な高機能テキストエディタ, 拡張可能な設定で開発環境として利用 |
| Environment Modules | - | 環境管理システム, 複数のバージョンのツールと依存関係を管理 |
| Git | - | 分散バージョン管理システム, ソースコード変更の履歴管理と協業を支援 |
| GNU Debugger | GDB | GNU プロジェクトのデバッガ, C/C++ などのプログラムのデバッグに使用 |
| GNU Screen | - | 画面マルチプレクサ, 複数のシェルセッションを単一の接続で管理 |
| Grand Unified Debugger | GUD | Emacs に統合されたデバッガインターフェース, gdb など外部デバッガと連携 |
| Hypertext Transfer Protocol | HTTP | Webでのデータ転送プロトコル, クライアントとサーバ間の通信規約 |
| Hypertext Transfer Protocol Secure | HTTPS | HTTPの暗号化版, SSL/TLSでデータを保護 |
| multicast DNS | mDNS | ローカルネットワーク内でホスト名解決を行うプロトコル |
| Network FileSystem | NFS | ネットワークファイルシステム, リモートのファイルシステムをマウント |
| proxy | - | ネットワーク中継サーバ, クライアントとサーバの間で通信を仲介 |
| Red Hat Enterprise Linux | RHEL | Red Hat 社が提供する Linux ディストリビューション。RHEL9 はそのメジャーバージョン 9 を指す。 |
| root | - | Unix系システムの最高権限ユーザ, すべてのファイルとプロセスへのアクセス権を持つ |
| Secure Shell | SSH | リモートコンピュータへの安全なログインと通信を可能にするプロトコル。ネットワーク接続を暗号化することで, ユーザ認証と通信内容の機密性を確保する。 |
| sudo | - | 別のユーザ (通常は root) の権限で指定されたコマンドを実行することを可能にする Unix 系システムのプログラム。管理者以外のユーザが管理作業を行うときに使用される。 |
| tar | - | テープアーカイブユーティリティ, ファイルをまとめてアーカイブ化 |
| tmux | - | Terminal multiplexer, 複数のシェルセッションを管理するターミナル分割ツール |
| vars | - | 変数定義ファイル, Ansible で共通設定値を記載 |
| wget | - | GNU Wget, コマンドラインダウンロードツール, ネットワークファイル取得に使用 |
| xz | - | 高圧縮率のテキストおよびバイナリ圧縮フォーマット, .xz 拡張子で使用 |
| zsh | - | Z Shell, 強力な対話的シェル, プログラミング機能が豊富 |

## 前提条件

- Ansible 2.15 以降
- リモートホストへの SSH 接続が確立されていること
- 管理者権限 (sudo) が利用可能であること（バックアップスクリプト配置時のみ必須）
## 実行フロー

本ロールは以下の順序で処理を実行します:

1. **パラメータ読み込み** (load-params.yml): Debian/RHEL の差分を吸収するために `vars/cross-distro.yml` や共通設定を読み込みます。
2. **パッケージ管理** (package.yml): パッケージインストール関連の処理（将来的な拡張に予約）。
3. **共通ディレクトリ作成** (directory.yml): `/usr/local/bin` の作成とホームディレクトリバックアップスクリプトを配置します。
4. **Bash設定展開** (directory-bash.yml): Bash用の設定ファイル (`.bashrc`, `.bashrc.proxy` など) を `/etc/skel` に展開（`user_settings_create_bash_skel` で制御）。
5. **zsh設定展開** (directory-zsh.yml): zsh用の設定ファイル (`.zshrc`, `.zprofile` など) を `/etc/skel` に展開（`user_settings_create_zsh_skel` で制御）。
6. **SSH設定展開** (directory-ssh.yml): SSH用の設定ファイル (`.ssh/config`, `.ssh/authorized_keys`) を `/etc/skel` に展開（`user_settings_create_ssh_skel` で制御）。
7. **curl設定展開** (directory-curl.yml): curl用の設定ファイル (`.curlrc`) を `/etc/skel` に展開（`user_settings_create_curl_skel` で制御）。
8. **wget設定展開** (directory-wget.yml): wget用の設定ファイル (`.wgetrc`) を `/etc/skel` に展開（`user_settings_create_wget_skel` で制御）。
9. **screen設定展開** (directory-screen.yml): screen用の設定ファイル (`.screenrc`) を `/etc/skel` に展開（`user_settings_create_screen_skel` で制御）。
10. **tmux設定展開** (directory-tmux.yml): tmux用の設定ファイル (`.tmux.conf`) を `/etc/skel` に展開（`user_settings_create_tmux_skel` で制御）。
11. **aspell設定展開** (directory-aspell.yml): aspell用の設定ファイル (`.aspell.conf`) を `/etc/skel` に展開（`user_settings_create_aspell_skel` で制御）。
12. **Git無視ルール展開** (directory-gitignore.yml): Git用の無視ファイルリスト (`.gitignore`) を `/etc/skel` に展開（`user_settings_create_git_skel` および `user_settings_create_gitignore_on_homedir_skel` で制御）。
13. **GDB設定展開** (directory-gdb.yml): GDB用の設定ファイル (`.gdbinit`) を `/etc/skel` に展開（`user_settings_create_gdb_skel` で制御）。
14. **Emacs設定ツリー構築** (directory-emacs.yml): `/etc/skel/.emacs.d` ツリーを作成し, `init.el` と必須設定ファイル（`proxy-settings.el`, `basic-settings.el`, `japanese-environment.el`）を展開（`user_settings_create_emacs_skel` で制御）。
15. **バックアップスクリプト配置** (directory-home-backup-script.yml): ホームディレクトリバックアップスクリプトを `/usr/local/bin/backup-home` に配置（`user_settings_backup_home_script_enabled` および関連変数で制御）。
16. **ホームコマンド配置** (home-command.yml): `/etc/skel/bin` を作成し, `clean-all-docker-images.sh`, `run-docker.sh` などの運用スクリプトをテンプレートから配布。
17. **設定関連処理** (config.yml): その他の設定関連処理。
18. **サービス管理** (service.yml): サービス関連処理（将来的な拡張に予約）。
19. **ユーザ・グループ管理** (user_group.yml): ユーザ・グループ関連処理（将来的な拡張に予約）。

## 主要変数

本ロールではスケルトン環境 (`/etc/skel`) の構築までを行います。ユーザ作成後の既存ユーザホームへの操作は, `post-user-create` ロール ( `create-users` ロール直後に実行 ) で実行され, 以下の処理を行います:

- `users_list` をループし, 各ユーザの `~/bin/` に `install-emacs-packages.sh` が存在しない場合は `/etc/skel/bin/` からコピー
- `create_user_emacs_package_list` で指定されたパッケージを当該ユーザ権限でインストール
- オプションの Emacs 設定ファイル ( aspell-settings.el, auctex-mode-settings.el など ) を `~/.emacs.d/user_settings/` 配下に配布

Emacs パッケージの管理 ( インストール対象パッケージの指定 ) は `post-user-create` ロールで一元管理されます。詳細は `post-user-create` ロールの Readme.md を参照してください。

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
| `user_settings_backup_bin_dir` | `"/usr/local/bin"` | backup-homeスクリプトを配置するディレクトリ。規定値での配置先は `/usr/local/bin/backup-home`。 |
| `user_settings_backup_share_dir` | `"/usr/local/share/backup-home"` | crontab例など関連ファイルを配置するディレクトリ。規定値での配置先は `/usr/local/share/backup-home/backup-home.cron.example`。 |

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

#### `.ssh/config`ファイルにmulticast DNSホストを登録するための設定

`mdns_host_list`変数に以下の要素からなる辞書のリストを記述することで, ユーザの.ssh/configファイルに`ホスト名.local`のホスト情報を追記することができます:

|キー名|設定値|設定値の例|
|---|---|---|
|name|mDNSのホスト名(`.local`を除去したホスト名)。|'vmlinux1'|

記載例は以下の通りです:

```yaml
mdns_host_list:
   - { name: 'vmlinux1' }
   - { name: 'vmlinux2' }
```

## テンプレート/ファイル

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
| `backup-home.j2` | `{{ user_settings_backup_bin_dir }}/backup-home` | ホームバックアップスクリプト。規定値での配置先は `/usr/local/bin/backup-home`。 |
| `backup-home.cron.example.j2` | `{{ user_settings_backup_share_dir }}/backup-home.cron.example` | ホームバックアップスクリプト用 crontab 例。規定値での配置先は `/usr/local/share/backup-home/backup-home.cron.example`。 |
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

## バックアップスクリプト詳細

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

#### 手動実行の場合:

手動実行の場合, 以下のように特権ユーザで実行してください ( 以下の例では, 配置先ディレクトリを規定値に基づいて記載しています ):

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
3. Git 設定: `.gitconfig` は `post-user-create` ロールで各ユーザのホームディレクトリに作成されます (`post_user_create_gitconfig_enabled: true` の場合)。本ロールでは `/etc/skel/.gitignore` のみを管理します。
4. ホームディレクトリバックアップスクリプトの導入処理を有効化する場合は, 以下の条件をすべて満たす必要があります:
   - `user_settings_backup_home_script_enabled: true`
   - `user_settings_backup_home_nfs_server` が空でない
   - `user_settings_backup_home_nfs_dir` が空でない
   - `user_settings_backup_home_mount_point` が空でない
   - `user_settings_backup_dir_on_nfs` が空でない
   - `user_settings_backup_users_list` が空でない
   - `user_settings_backup_home_rotation` が1以上

## 実行方法

```bash
make run_user_settings
```

または,

```bash
# user-settings ロールのみ実行
ansible-playbook -i inventory/hosts site.yml -t user-settings

# 特定ホストのみ対象
ansible-playbook -i inventory/hosts site.yml -l ubuntu-server.local

# 特定ホストで user-settings ロールのみ実行
ansible-playbook -i inventory/hosts site.yml -l ubuntu-server.local -t user-settings

# 変数を上書きして user-settings ロールを実行 (例: Bash 設定を有効化)
ansible-playbook -i inventory/hosts site.yml -t user-settings -e "user_settings_create_bash_skel=true"
```

## 検証ポイント

### 1. ロール実行結果の確認

確認コマンド:

```bash
ansible-playbook -i inventory/hosts site.yml --tags user-settings
```

期待する出力例:

```text
PLAY RECAP *********************************************************************
devlinux1.local            : ok=49   changed=0    unreachable=0    failed=0    skipped=28   rescued=0    ignored=0
devlinux4.local            : ok=48   changed=1    unreachable=0    failed=0    skipped=29   rescued=0    ignored=0
```

検証ポイント:

- `PLAY RECAP` で `failed=0` かつ `unreachable=0` であることを確認します。

### 2. /etc/skel 基本ファイルの配置確認

確認コマンド:

```bash
sudo -n ls -l /etc/skel/.bashrc /etc/skel/.zshrc /etc/skel/.ssh/config /etc/skel/.tmux.conf /etc/skel/.screenrc
```

期待する出力例:

```text
-rw-r--r-- 1 root root ... /etc/skel/.bashrc
-rw-r--r-- 1 root root ... /etc/skel/.zshrc
-rw------- 1 root root ... /etc/skel/.ssh/config
-rw-r--r-- 1 root root ... /etc/skel/.tmux.conf
-rw-r--r-- 1 root root ... /etc/skel/.screenrc
```

検証ポイント:

- 各ファイルが存在し, 所有者が `root root` であることを確認します。
- `.ssh/config` が機密性に応じた制限付きパーミッションになっていることを確認します。

### 3. .gitignore 生成条件の確認

確認コマンド:

```bash
test -f /etc/skel/.gitignore; echo $?
```

期待する出力例:

```text
0
```

検証ポイント:

- `user_settings_create_gitignore_on_homedir_skel: true` の場合は, testコマンドの終了コードが`0` (存在) となることを確認します。
- `user_settings_create_gitignore_on_homedir_skel: false` の場合は, testコマンドの終了コードが`1` (非存在) となることを確認します。

### 4. Emacs 必須設定ファイルの確認

確認コマンド:

```bash
sudo -n ls -l /etc/skel/.emacs.d/init.el \
   /etc/skel/.emacs.d/user_settings/proxy-settings.el \
   /etc/skel/.emacs.d/user_settings/basic-settings.el \
   /etc/skel/.emacs.d/user_settings/japanese-environment.el
```

期待する出力例:

```text
-rw-r--r-- 1 root root 2616 ... /etc/skel/.emacs.d/init.el
-rw-r--r-- 1 root root 698  ... /etc/skel/.emacs.d/user_settings/proxy-settings.el
-rw-r--r-- 1 root root 1085 ... /etc/skel/.emacs.d/user_settings/basic-settings.el
-rw-r--r-- 1 root root 2012 ... /etc/skel/.emacs.d/user_settings/japanese-environment.el
```

検証ポイント:

- `user_settings_create_emacs_skel: true` の場合に, 4ファイルがすべて存在することを確認します。

### 5. Docker 補助スクリプトの確認

確認コマンド:

```bash
ls -l /etc/skel/bin/clean-all-docker-images.sh /etc/skel/bin/run-docker.sh
```

期待する出力例:

```text
-rwxr-xr-x 1 root root 1250 ... /etc/skel/bin/clean-all-docker-images.sh
-rwxr-xr-x 1 root root 1400 ... /etc/skel/bin/run-docker.sh
```

検証ポイント:

- `create_docker_image_operation_script: true` の場合に両ファイルが存在し, 実行権限 (`x`) があることを確認します。

### 6. backup-home スクリプトの確認

確認コマンド:

```bash
ls -l /usr/local/bin/backup-home
test -x /usr/local/bin/backup-home; echo $?
```

期待する出力例:

```text
-rwxr-xr-x 1 root root 6501 ... /usr/local/bin/backup-home
0
```

検証ポイント:

- バックアップスクリプト有効時にファイルが存在し, 実行可能 (testコマンドの終了コードが`0`) であることを確認します。

### 7. プロキシ関連テンプレート展開確認

確認コマンド:

```bash
sudo -n grep -E "proxy|ProxyCommand|no_proxy|NO_PROXY" /etc/skel/.bashrc.proxy /etc/skel/.curlrc /etc/skel/.ssh/config
```

期待する出力例:

```text
/etc/skel/.bashrc.proxy:# proxy_server  プロキシサーバ (例: proxy_server="proxy.com")
/etc/skel/.bashrc.proxy:# proxy_port    プロキシポート (例: proxy_port="8080")
/etc/skel/.bashrc.proxy:# proxy_user    プロキシユーザ (例: proxy_user="alice")
/etc/skel/.bashrc.proxy:# proxy_password  プロキシパスワード (例: proxy_password="passw0rd")
```

検証ポイント:

- 既定状態では `proxy_server`, `proxy_port`, `proxy_user`, `proxy_password`, `no_proxy` の設定行がコメントアウトされた形で記載されていることを確認します。


## 補足

### 既存ユーザに対する Emacs パッケージインストールおよびオプション設定ファイル配布の検証について

既存ユーザに対する Emacs パッケージインストールおよびオプション設定ファイル配布の検証は, `post-user-create` ロールの Readme.md の検証ポイントを参照してください。
