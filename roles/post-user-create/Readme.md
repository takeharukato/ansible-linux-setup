# post-user-create ロール

## 概要

本ロールは `create-users` ロール実行後にユーザホーム関連の後処理を行うロールです。

ユーザ骨組み環境の準備 ( `user-settings` ロール ) を完了した後, 実際のユーザ作成 ( `create-users` ロール ) が実行されます。その直後に本ロールが実行され, 作成済みユーザのホームディレクトリに対する操作を行います。

以下のようにユーザ作成ロール間の責務を分離しています:

1. user-settings ロール: `/etc/skel` に骨組み環境を構築 ( ユーザ作成前 ) -- 必須 Emacs 設定ファイル（4個）のみ配置
2. create-users ロール: 新規ユーザの作成
3. post-user-create ロール: 作成済みユーザのホームディレクトリに対して個別処理を実行 -- Emacs パッケージ管理（インストールスクリプト作成とパッケージインストール）、オプション Emacs 設定ファイル（20個）をテンプレートから直接配置

本ロールは, `make run_post_user_create`により, 単体での実行が可能です。

## 機能

### Git 設定ファイル作成

`post_user_create_gitconfig_enabled` が `true` の場合, `users_list` に定義された各ユーザのホームディレクトリに `.gitconfig` を作成します。

- `post_user_create_gitconfig_use_login_name` が `true` (既定) の場合, `user.name` にログイン名を使用します。
- `false` の場合は, システムのユーザエントリから GECOS フィールドを取得して使用します。

#### 補足事項: ディストリビューション別 GECOS フィールド取得用変数について

GECOS フィールドのインデックスは `vars/cross-distro.yml` の `getent_passwd_field_gecos` 変数で定義されています。将来的に, ディストリビューション間で乖離が発生した場合は, `vars/cross-distro.yml` の以下の変数を修正してください:

```yaml
getent_passwd_field_gecos_debian: 3
getent_passwd_field_gecos_rhel:   3
```

### Emacs パッケージ導入

`create_emacs_package_install_script` が `true` で, `create_user_emacs_package_list` に1要素以上定義されている場合, 以下の処理を実行します:

1. `/etc/skel/bin/install-emacs-packages.sh` を本ロールのテンプレートから目的地に生成（パッケージリスト定義がある場合のみ）
2. 既存ユーザのホームが存在する場合、 `/etc/skel/bin/install-emacs-packages.sh` がユーザの `~/bin/` に存在することを確認
3. スクリプトが存在しない場合, `/etc/skel/bin/install-emacs-packages.sh` からコピー
4. ユーザの権限でスクリプトを実行し, 指定された Emacs パッケージをインストール

## 関連変数

本ロールで使用される変数は以下の通りです。これらの変数は `group_vars/all/all.yml` または `host_vars` で上書き可能です。

### Git関連変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `post_user_create_gitconfig_enabled` | `false` | 各ユーザのホームディレクトリに `.gitconfig` を作成する場合は `true` を指定します。 |
| `post_user_create_gitconfig_use_login_name` | `true` | `.gitconfig` の `user.name` にログイン名を使用する場合は `true` を指定します。`false` の場合はシステムのユーザエントリから GECOS フィールドを取得して使用します。 |


### Emacs関連変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `create_emacs_package_install_script` | `"{{ create_user_emacs_package_list \| length > 0 }}"` | Emacsパッケージインストールスクリプト生成の要否を自動判定します。`create_user_emacs_package_list` に1要素以上含まれる場合、自動的に `true` になります。 |
| `create_user_emacs_package_list` | `[]` | 各ユーザに `install-emacs-packages.sh` で導入する Emacs パッケージ名のリスト。空もしくは未定義の場合はインストール処理をスキップします。 |

### ユーザ情報変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `users_list` | `[]` | ロールが処理対象とするユーザ情報 (`vars/all-config.yml` で定義)。`name`, `home`, `shell` などを参照し、Emacs パッケージインストール時のアカウントとホームディレクトリを決定します。 |

## Emacs設定ファイルについて

### 必須設定ファイル（user-settings ロールで配布）

以下の設定ファイルは、`user-settings` ロール内で `/etc/skel/.emacs.d/user_settings/` に配置されます。
新規ユーザ作成時は、スケルトン環境から始めのユーザホームに自動的にコピーされます。

| ファイル名 | 説明 |
| --- | --- |
| `init.el` | Emacs初期化ファイル（基本的な設定） |
| `proxy-settings.el` | プロキシ設定 |
| `basic-settings.el` | UI・基本設定 |
| `japanese-environment.el` | 日本語対応設定 |

### オプション設定ファイル（post-user-create ロールで配布）

以下の設定ファイルは本ロール内のテンプレートとして定義されており、本ロール実行時に各ユーザの `~/.emacs.d/user_settings/` に直接配置されます。
これらのファイルは、Emacsの各種モードや機能を有効化するためのサンプルです。一部のファイルは、MELPAなどから別途インストールする外部Emacsパッケージを必要とする場合があります。外部パッケージの導入は利用者に任せており、`install-emacs-packages.sh` スクリプトと `create_user_emacs_package_list` 変数を使用して、必要なパッケージを自動インストールすることも可能です。

| テンプレート名 | ファイル名 | 説明 | 外部パッケージ |
| --- | --- | --- | --- |
| `_emacs_d__aspell-settings.el.j2` | `aspell-settings.el` | aspell 連携設定 | - |
| `_emacs_d__auctex-mode-settings.el.j2` | `auctex-mode-settings.el` | AUCTeX モード設定 | 必要 |
| `_emacs_d__bsdc-mode-settings.el.j2` | `bsdc-mode-settings.el` | BSD C モード調整 | - |
| `_emacs_d__c-mode-settings.el.j2` | `c-mode-settings.el` | C モード共通設定 | - |
| `_emacs_d__c-sharp-mode-settings.el.j2` | `c-sharp-mode-settings.el` | C# モード設定 | 必要 |
| `_emacs_d__cmake-settings.el.j2` | `cmake-settings.el` | CMake モード設定 | 必要 |
| `_emacs_d__docker-compose-mode-settings.el.j2` | `docker-compose-mode-settings.el` | docker-compose モード設定 | 必要 |
| `_emacs_d__docker-tramp-mode-settings.el.j2` | `docker-tramp-mode-settings.el` | Docker TRAMP 連携設定 | 必要 |
| `_emacs_d__dockerfile-mode-settings.el.j2` | `dockerfile-mode-settings.el` | Dockerfile モード設定 | 必要 |
| `_emacs_d__gnu-global-settings.el.j2` | `gnu-global-settings.el` | GNU Global 連携設定 | 必要 |
| `_emacs_d__gud-settings.el.j2` | `gud-settings.el` | GUD デバッガ設定 | - |
| `_emacs_d__hos-c-mode-settings.el.j2` | `hos-c-mode-settings.el` | Hyper Operating System開発用 C モード設定 | - |
| `_emacs_d__linux-c-mode-settings.el.j2` | `linux-c-mode-settings.el` | Linux C コーディングスタイル | - |
| `_emacs_d__markdown-mode-settings.el.j2` | `markdown-mode-settings.el` | Markdown モード設定 | 必要 |
| `_emacs_d__package-settings.el.j2` | `package-settings.el` | package.el 初期化 | - |
| `_emacs_d__python3-settings.el.j2` | `python3-settings.el` | Python3 モード設定 | - |
| `_emacs_d__rust-settings.el.j2` | `rust-settings.el` | Rust モード設定 | 必要 |
| `_emacs_d__screen-settings.el.j2` | `screen-settings.el` | 画面表示・色設定 | - |
| `_emacs_d__yaml-mode-settings.el.j2` | `yaml-mode-settings.el` | YAML モード設定 | 必要 |
| `_emacs_d__yatex-mode-setting.el.j2` | `yatex-mode-setting.el` | YaTeX モード設定 | 必要 |

## Emacs パッケージのセットアップ

本ロールでは Emacs パッケージをインストールする際、`user-settings` ロールが提供する設定ファイルのサンプルを利用します。必須設定ファイルは新規ユーザのスケルトンに含まれ、オプション設定ファイルは本ロール実行時に既存ユーザに配布されます。

外部Emacsパッケージの導入は利用者に任せており、`install-emacs-packages.sh` スクリプトと `create_user_emacs_package_list` 変数を使用して必要なパッケージを自動インストールできます。

## オプション設定ファイルの更新手順

オプション Emacs 設定ファイル（auctex-mode-settings.el, cmake-settings.el 等）は `defaults/main.yml` で定義されている `emacs_optional_settings_files` リストから、自動的に `tasks/emacs-package-el-setting.yml` を生成します。

### 生成手順

1. `defaults/main.yml` の `emacs_optional_settings_files` にファイルを追加・削除
2. 次のコマンドを実行してタスクファイルを再生成:

```bash
cd roles/post-user-create/tasks
bash generate-emacs-settings.sh ..
```

または、ansible ディレクトリから実行する場合:

```bash
bash roles/post-user-create/tasks/generate-emacs-settings.sh roles/post-user-create
```

3. 生成結果を確認:

```bash
git diff tasks/emacs-package-el-setting.yml
```

### 例: 新しい Emacs モードを追加する場合

1. テンプレートを作成: `templates/_emacs_d__new-mode-settings.el.j2`
2. `defaults/main.yml` の `emacs_optional_settings_files` に `new-mode-settings.el` を追加
3. 以下のいずれかの方法でタスクファイルを再生成:

```bash
# 方法1: role の tasks/ ディレクトリから実行
cd roles/post-user-create/tasks
bash generate-emacs-settings.sh ..

# 方法2: ansible ディレクトリから実行
bash roles/post-user-create/tasks/generate-emacs-settings.sh roles/post-user-create
```

すると新しいタスク「Deploy new-mode-settings.el from template to user home」が自動生成されます。

## 検証ポイント

- `post_user_create_gitconfig_enabled: true` の場合, `users_list` に定義された各ユーザのホームディレクトリに `.gitconfig` が存在し, 所有者が適切（ユーザ自身）であること。
- `.gitconfig` の `user.name` が `post_user_create_gitconfig_use_login_name` の設定に応じて正しく設定されていること（ログイン名またはシステムの GECOS フィールド）。
- `create_user_emacs_package_list` を更新した際はロールを再実行し，各ユーザホームの `~/bin/install-emacs-packages.sh` が新しいパッケージを取り込むことを確認してください。
- 既存ユーザで `create_user_emacs_package_list` にパッケージが記載されている場合、`~/bin/install-emacs-packages.sh` が自動的にコピーされること。
- スクリプトが実行可能（`0755`）で、当該ユーザ権限で実行されることを確認すること。
- `create_user_emacs_package_list` で指定したパッケージが Emacs 環境へ追加されていることを確認すること。
- ユーザホームディレクトリの所有者が正しく設定されていることを確認すること。
