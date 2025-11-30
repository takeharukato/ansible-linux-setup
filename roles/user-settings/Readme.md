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
| `users_list` | `vars/all-config.yml` | ロールが処理対象とするユーザ情報。`name`, `home`, `shell` などを参照し, Emacs パッケージインストール時のアカウントとホームディレクトリを決定します。|
| `create_user_emacs_package_list` | `vars/all-config.yml` | 各ユーザに `install-emacs-packages.sh` で導入する Emacs パッケージ名のリスト。空もしくは未定義の場合はインストール処理をスキップします。|
| `proxy_*`, `env_*` など | `group_vars` / `host_vars` | `_bashrc.proxy.j2` などのテンプレートで参照される環境変数。必要に応じてホスト／グループ単位で上書きしてください。|

## 実行フロー

1. `ansible-playbook -i inventory/hosts site.yml --tags user-settings` などでロールを実行し, `/etc/skel` 配下のスケルトンと補助スクリプトが生成されることを確認します。
2. 既存ユーザに対して Emacs パッケージを導入する場合は, 同じプレイブックで `create-users` ロールの後段に `user-settings` を配置するか, `--tags user-settings` で単体実行してください。
3. `create_user_emacs_package_list` を更新した際はロールを再実行し, 各ユーザホームの `~/bin/install-emacs-packages.sh` が新しいパッケージを取り込むことを確認します。

## 検証ポイント

- `/etc/skel` に `.bashrc.proxy`, `.zshrc`, `.ssh/authorized_keys`, `.emacs.d/init.el` などテンプレート由来のファイルが所有者 `root:root`・適切なパーミッションで配置されていること。
- `/etc/skel/bin/install-emacs-packages.sh` 等のスクリプトが `0755` で作成され, 新規ユーザホームにも複製されること。
- 既存ユーザホームで `~/bin/install-emacs-packages.sh` が存在する場合, `create_user_emacs_package_list` に記載したパッケージが Emacs 環境へ追加され, ログにエラーが出力されていないこと。
- プロキシや個別設定テンプレートに使用する変数 (`proxy_*` など) が意図通り展開されているか `grep` 等で確認してください。

ロールは `/etc/skel` を基点とした標準環境を提供します。運用ポリシーに応じてテンプレートを拡張し, `group_vars` や `host_vars` で必要な変数を上書きして利用してください。
