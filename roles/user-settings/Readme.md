# user-settings ロール

このロールは新規ユーザ作成時に複製される `/etc/skel` 以下のスケルトン環境と, 既存ユーザのエディタ／補助スクリプト環境を共通化します。プロキシ設定やシェル初期化ファイル, Emacs 関連ファイルをテンプレートとして配布し, `vars/all-config.yml` に定義した `users_list` / `create_user_emacs_package_list` を基にホームディレクトリへ追加セットアップを行います。すべてのタスクは再実行可能で, 既存ファイルがある場合は整形・追記のみを行い冪等性を維持します。

主な処理は次の通りです。

- **load-params.yml**: Debian/RHEL の差分を吸収するために `vars/cross-distro.yml` や共通設定 (`vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込みます。
- **directory.yml**: `/etc/skel` 配下に `.bashrc` / `.zshrc` 系のテンプレート, `.ssh` ディレクトリと既定の `authorized_keys`・`config`, `.gitconfig`・`.tmux.conf` などの基本ファイルを展開します。加えて `/etc/skel/.emacs.d` ツリーを作成し, 必要な Lisp ファイル群を `emacs-setting.yml` で配置します。
- **home-command.yml**: `/etc/skel/bin` を作成し, `install-emacs-packages.sh`・`clean-all-docker-images.sh`・`run-docker.sh` といった運用スクリプトをテンプレートから配布します。これにより `create-users` ロールでホームディレクトリが生成される際に同じ構成が複製されます。
- **emacs-package.yml / emacs-package-install.yml**: `users_list` をループし, ユーザホームに `install-emacs-packages.sh` が存在する場合のみ `create_user_emacs_package_list` の各パッケージを当該ユーザ権限でインストールします。

## 変数一覧

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `users_list` | `[]` | ロールが処理対象とするユーザ情報。`name`, `home`, `shell` などを参照し, Emacs パッケージインストール時のアカウントとホームディレクトリを決定します。|
| `create_user_emacs_package_list` | `[]` | 各ユーザに `install-emacs-packages.sh` で導入する Emacs パッケージ名のリスト。空もしくは未定義の場合はインストール処理をスキップします。|
| `proxy_server` | `""` | HTTP/HTTPS プロキシのホスト名。`_bshrc.proxy.j2`、`_curlrc.j2`、`_ssh__config.j2` などで利用します。|
| `proxy_port` | `""` | プロキシサーバの待ち受けポート番号。各プロキシ関連テンプレートで参照されます。|
| `proxy_user` | `""` | プロキシ認証が必要な場合のユーザ名。`_bshrc.proxy.j2` や `_curlrc.j2` で資格情報として展開されます。|
| `proxy_password` | `""` | プロキシ認証パスワード。認証が不要な場合は空文字にします。|
| `no_proxy` | `""` | プロキシ経由させないホスト/ドメインの一覧。curl/wget/シェル環境の設定に反映されます。|

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
| `_gitignore.j2` | `/etc/skel/.gitignore` | Git 無視ルール雛形 |
| `_screenrc.j2` | `/etc/skel/.screenrc` | GNU Screen 設定 |
| `_tmux.conf.j2` | `/etc/skel/.tmux.conf` | tmux 設定 |
| `_wgetrc.j2` | `/etc/skel/.wgetrc` | wget の既定オプション |
| `_zprofile.j2` | `/etc/skel/.zprofile` | zsh ログイン設定 |
| `_zshrc.j2` | `/etc/skel/.zshrc` | zsh メイン設定 |
| `_zshrc_common.j2` | `/etc/skel/.zshrc.common` | zsh 共通設定 |
| `_zshrc.mine.sample.j2` | `/etc/skel/.zshrc.mine.sample` | zsh ユーザ個別設定サンプル |
| `_ssh__authorized_keys.j2` | `/etc/skel/.ssh/authorized_keys` | authorized_keys 雛形 |
| `_ssh__config.j2` | `/etc/skel/.ssh/config` | OpenSSH 共通設定 |
| `backup-home.j2` | `/usr/local/bin/backup-home` | ホームバックアップスクリプト |
| `install-emacs-packages.sh.j2` | `/etc/skel/bin/install-emacs-packages.sh` | Emacs パッケージ導入スクリプト |
| `clean-all-docker-images.sh.j2` | `/etc/skel/bin/clean-all-docker-images.sh` | Docker イメージ一括削除スクリプト |
| `run-docker.sh.j2` | `/etc/skel/bin/run-docker.sh` | Docker コンテナ起動補助スクリプト |
| `_emacs_d__init.el.j2` | `/etc/skel/.emacs.d/init.el` | Emacs 初期化ファイル |

### Emacsパッケージ

| テンプレート名 | 展開先ファイル | 説明 |
| --- | --- | --- |
| `_emacs_d__aspell-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/aspell-settings.el` | aspell 連携設定 |
| `_emacs_d__auctex-mode-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/auctex-mode-settings.el` | AUCTeX モード設定 |
| `_emacs_d__basic-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/basic-settings.el` | 基本 UI/編集設定 |
| `_emacs_d__bsdc-mode-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/bsdc-mode-settings.el` | BSD C モード調整 |
| `_emacs_d__c-mode-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/c-mode-settings.el` | C モード共通設定 |
| `_emacs_d__c-sharp-mode-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/c-sharp-mode-settings.el` | C# モード設定 |
| `_emacs_d__cmake-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/cmake-settings.el` | CMake モード設定 |
| `_emacs_d__docker-compose-mode-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/docker-compose-mode-settings.el` | docker-compose モード設定 |
| `_emacs_d__docker-tramp-mode-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/docker-tramp-mode-settings.el` | Docker TRAMP 連携設定 |
| `_emacs_d__dockerfile-mode-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/dockerfile-mode-settings.el` | Dockerfile モード設定 |
| `_emacs_d__gnu-global-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/gnu-global-settings.el` | GNU Global 連携設定 |
| `_emacs_d__gud-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/gud-settings.el` | GUD デバッガ設定 |
| `_emacs_d__hos-c-mode-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/hos-c-mode-settings.el` | Hyper Operating System開発用 C モード設定 |
| `_emacs_d__japanese-environment.el.j2` | `/etc/skel/.emacs.d/user_settings/japanese-environment.el` | 日本語環境設定 |
| `_emacs_d__linux-c-mode-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/linux-c-mode-settings.el` | Linux C コーディングスタイル |
| `_emacs_d__markdown-mode-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/markdown-mode-settings.el` | Markdown モード設定 |
| `_emacs_d__package-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/package-settings.el` | package.el 初期化 |
| `_emacs_d__proxy-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/proxy-settings.el` | Emacs プロキシ設定 |
| `_emacs_d__python3-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/python3-settings.el` | Python3 モード設定 |
| `_emacs_d__rust-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/rust-settings.el` | Rust モード設定 |
| `_emacs_d__screen-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/screen-settings.el` | screen 連携設定 |
| `_emacs_d__yaml-mode-settings.el.j2` | `/etc/skel/.emacs.d/user_settings/yaml-mode-settings.el` | YAML モード設定 |
| `_emacs_d__yatex-mode-setting.el.j2` | `/etc/skel/.emacs.d/user_settings/yatex-mode-setting.el` | YaTeX モード設定 |

## 実行フロー

1. `ansible-playbook -i inventory/hosts site.yml --tags user-settings` などでロールを実行し, `/etc/skel` 配下のスケルトンと補助スクリプトが生成されることを確認します。

### 留意事項

1. 既存ユーザに対して Emacs パッケージを導入する場合は, 同じプレイブックで `create-users` ロールの後段に `user-settings` を配置するか, `--tags user-settings` で単体実行してください。
2. `create_user_emacs_package_list` を更新した際はロールを再実行し, 各ユーザホームの `~/bin/install-emacs-packages.sh` が新しいパッケージを取り込むことを確認してください。

## 検証ポイント

- `/etc/skel` に `.bashrc.proxy`, `.zshrc`, `.ssh/authorized_keys`, `.emacs.d/init.el` などテンプレート由来のファイルが所有者 `root:root`・適切なパーミッションで配置されていること。
- `/etc/skel/bin/install-emacs-packages.sh` 等のスクリプトが `0755` で作成され, 新規ユーザホームにも複製されること。
- 既存ユーザホームで `~/bin/install-emacs-packages.sh` が存在する場合, `create_user_emacs_package_list` に記載したパッケージが Emacs 環境へ追加され, ログにエラーが出力されていないこと。
- プロキシや個別設定テンプレートに使用する変数 (`proxy_*` など) が意図通り展開されているか `grep` 等で確認してください。

ロールは `/etc/skel` を基点とした標準環境を提供します。運用ポリシーに応じてテンプレートを拡張し, `group_vars` や `host_vars` で必要な変数を上書きして利用してください。
