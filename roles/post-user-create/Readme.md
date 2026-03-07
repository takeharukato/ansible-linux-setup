# post-user-create ロール

## 概要

本ロールは `create-users` ロール実行後にユーザホーム関連の後処理を行うロールです。

ユーザスケルトン環境の準備 ( `user-settings` ロール ) を完了した後, 実際のユーザ作成 ( `create-users` ロール ) が実行されます。その直後に本ロールが実行され, 作成済みユーザのホームディレクトリに対する操作を行います。

以下のようにユーザ作成ロール間の責務を分離しています:

1. user-settings ロール: `/etc/skel` にスケルトン環境を構築 ( ユーザ作成前 ) -- 必須 Emacs 設定ファイル (4個) のみ配置
2. create-users ロール: 新規ユーザの作成
3. post-user-create ロール: 作成済みユーザのホームディレクトリに対して個別処理を実行 -- Emacs パッケージ管理 (インストールスクリプト作成とパッケージインストール), オプション Emacs 設定ファイル (20個) をテンプレートから直接配置

本ロールは, `make run_post_user_create` により, 単体での実行が可能です。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Ansible | - | インフラストラクチャ自動化ツール, 構成管理と自動デプロイメントに使用 |
| Role | - | Ansible の再利用可能なタスク定義の集合, タスク・ハンドラ・テンプレートをまとめたもの |
| Task | - | Ansible における単一の操作単位, 一つのアクション (パッケージインストール, ファイル配置など) を表現 |
| Template | - | Ansible で使用される Jinja2 ベースのテンプレート, 変数埋め込みにより設定ファイルなどを動的生成 |
| Playbook | - | Ansible の実行内容を定義するYAML形式のファイル, 複数のロールやタスクを組み合わせて記述 |
| include_tasks | - | Ansible タスク内で別のタスクファイルを読み込む指定 |
| with_items | - | Ansible でリスト内の複数アイテムに対して同じタスクを反復実行するループ制御 |
| loop_control | - | Ansible ループの動作を制御するオプション, ループ変数名の変更など |
| Emacs | - | テキスト編集機能が豊富な高機能テキストエディタ, 拡張可能な設定で開発環境として利用 |
| Emacs Lisp | - | Emacs の拡張に使用されるプログラミング言語, .el 拡張子のファイルで記述 |
| MELPA | - | Emacs Lisp Package Archive, Emacs パッケージの主要リポジトリ |
| package.el | - | Emacs のパッケージ管理システム, リモートリポジトリからパッケージをダウンロード・インストール |
| .emacs.d | - | Emacs ユーザ設定ディレクトリ, ホームディレクトリ直下に配置され, 初期化ファイルと設定ファイルを格納 |
| /etc/skel | - | 新規ユーザ作成時にホームディレクトリへ自動コピーされるテンプレートファイルの保管ディレクトリ |
| スケルトン環境 | - | /etc/skel 配下に構築される，新規ユーザ作成時に自動複製される初期設定ファイルとディレクトリの集合．プロキシ設定，シェル初期化ファイル，Emacs設定などを含む |
| ホームディレクトリ | HOME directory | ユーザが所有する個人用ディレクトリ, /home/<ユーザ名> など |
| 所有者 | owner | ファイルやディレクトリを所有するユーザ, ファイルパーミッションで制御 |
| グループ | group | ファイルやディレクトリに割り当てられたグループ属性, 複数ユーザの権限グループ化に使用 |
| 実行権限 | executable permission | ファイルが実行可能かどうかを設定するパーミッション, シェルスクリプトやバイナリを実行するために必要 |
| passwd データベース | - | OS のユーザ情報を保管するシステムデータベース, ユーザ名, UID, GID, GECOS などを格納 |
| getent | - | OS のシステムデータベース (passwd, group など) から情報を取得するコマンド |
| General Electric Comprehensive Operating System | GECOS | Unixパスワードファイルのユーザ情報フィールド, フルネームやオフィス情報を格納 |
| Git | - | 分散バージョン管理システム, ソースコード変更の履歴管理と協業を支援 |
| .gitconfig | - | Git の設定ファイル, ユーザの個人設定 (user.name, user.email など) を格納 |
| Shell script | - | シェル (コマンドラインインタプリタ) で実行可能なスクリプト, テキストファイルで複数のコマンドを記述 |
| YAML Ain't Markup Language | YAML | 人間可読なデータシリアライゼーション形式, 設定ファイルで広く使用 |
| AUCTeX | - | Emacs 上で LaTeX を編集・コンパイルするための拡張機能 |
| TRAMP | - | Transparent Remote Access, Multiple Protocol, Emacs でリモート機上のファイルをシームレスに編集 |
| CMake | - | クロスプラットフォーム対応のビルドシステム, C/C++ などのプロジェクト構築を自動化 |
| GNU Global | - | ソースコード検索とナビゲーション用ツール, 大規模プロジェクトの関数・シンボルを迅速に位置付け |
| Grand Unified Debugger | GUD | Emacs に統合されたデバッガインターフェース, gdb など外部デバッガと連携 |
| YaTeX | - | Emacs 上で日本語 LaTeX を編集するためのモード |
| Docker | - | コンテナ型の仮想化プラットフォーム, アプリケーションの配置と実行環境を標準化 |

## 前提条件

- `create-users` ロールが事前に実行済みであること
- Ansible 2.15 以降
- リモートホストへの SSH 接続が確立されていること
- 管理者権限 (sudo) が利用可能であること

## 実行フロー

本ロールは以下の順序で処理を実行します:

1. **パラメータ読み込み** (load-params.yml): ロール単独実行時のために, `vars/all-config.yml` などの変数を再読み込みします。
2. **パッケージ管理** (package.yml): 現在は空実装です。将来的にパッケージインストールが必要な場合に使用します。
3. **ディレクトリ作成** (directory.yml): 現在は空実装です。将来的にディレクトリ作成が必要な場合に使用します。
4. **ユーザ・グループ管理** (user_group.yml): 現在は空実装です。将来的にユーザ・グループ操作が必要な場合に使用します。
5. **サービス管理** (service.yml): 現在は空実装です。将来的にサービス管理が必要な場合に使用します。
6. **設定ファイル配置** (config.yml): `/etc/skel/bin/install-emacs-packages.sh` をテンプレートから生成します。
7. **Emacsパッケージ管理** (emacs-package.yml, 条件付き): `create_emacs_package_install_script` が `true` で `create_user_emacs_package_list` に1要素以上定義されている場合に実行されます。
8. **Git設定ファイル作成** (gitconfig.yml, 条件付き): `post_user_create_gitconfig_enabled` が `true` の場合に実行されます。

## 主要変数

本ロールで使用される変数は以下の通りです。これらの変数は `vars/all-config.yml` または `host_vars` で上書き可能です。

### Git関連変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `post_user_create_gitconfig_enabled` | `false` | 各ユーザのホームディレクトリに `.gitconfig` を作成する場合は `true` を指定します。 |
| `post_user_create_gitconfig_use_login_name` | `true` | `.gitconfig` の `user.name` にログイン名を使用する場合は `true` を指定します。`false` の場合はシステムのユーザエントリからGECOSフィールドを取得して使用します。 |

### Emacs関連変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `create_user_emacs_package_list` | `[]` | 各ユーザに `install-emacs-packages.sh` で導入するEmacsパッケージ名のリスト。空もしくは未定義の場合はインストール処理をスキップします。 |
| `create_emacs_package_install_script` | `"{{ create_user_emacs_package_list \| length > 0 }}"` | Emacsパッケージインストールスクリプト生成の要否を自動判定します。`create_user_emacs_package_list` に1要素以上含まれる場合, 自動的に `true` になります。 |
| `emacs_optional_settings_files` | [20個のリスト] | post-user-createロールがテンプレートから各ユーザホームに配置するオプション設定ファイルのリスト。defaults/main.ymlで定義され, tasks/emacs-package-el-setting.ymlの自動生成に使用されます。詳細は [テンプレート/ファイル](#テンプレートファイル) 節を参照してください。 |

### ユーザ情報変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `users_list` | `[]` | ロールが処理対象とするユーザ情報 (`vars/all-config.yml` で定義)。`name`, `home`, `shell` などを参照し, Emacsパッケージインストール時のアカウントとホームディレクトリを決定します。 |

## 主な処理

本ロールは以下の処理を実行します。

### パラメータ読み込み (load-params.yml)

ロール単独実行時のために, `vars/all-config.yml` などの変数を再読み込みします。

### パッケージ管理 (package.yml)

現在は空実装です。将来的にパッケージインストールが必要な場合に使用します。

### ディレクトリ作成 (directory.yml)

現在は空実装です。将来的にディレクトリ作成が必要な場合に使用します。

### ユーザ・グループ管理 (user_group.yml)

現在は空実装です。将来的にユーザ・グループ操作が必要な場合に使用します。

### サービス管理 (service.yml)

現在は空実装です。将来的にサービス管理が必要な場合に使用します。

### 設定ファイル配置 (config.yml)

`create_emacs_package_install_script` が `true` の場合, `/etc/skel/bin/install-emacs-packages.sh` をテンプレートから生成します。このスクリプトは, 新規ユーザ作成時にホームディレクトリにコピーされます。

### Emacsパッケージ管理 (emacs-package.yml)

`create_emacs_package_install_script` が `true` で, `create_user_emacs_package_list` に1要素以上定義されている場合に実行されます。

#### インストールスクリプトの配布 (emacs-package-install.yml)

- 既存ユーザのホームディレクトリに `~/bin/install-emacs-packages.sh` が存在するかを確認
- 存在しない場合, `/etc/skel/bin/install-emacs-packages.sh` からコピー
- ユーザ権限でスクリプトを実行し, 指定されたEmacsパッケージをインストール

#### オプション設定ファイルの配布 (emacs-package-el-setting.yml)

- `emacs_optional_settings_files` で定義された20個のファイルを, テンプレートから各ユーザの `~/.emacs.d/user_settings/` に配置
- このタスクファイルは `generate-emacs-settings.sh` により自動生成されます

### Git設定ファイル作成 (gitconfig.yml)

`post_user_create_gitconfig_enabled` が `true` の場合に実行されます。

1. `ansible.builtin.getent` でシステムのpasswdデータベースからユーザ情報を取得 (GECOSフィールド取得のため)
2. `users_list` の各ユーザのホームディレクトリに `.gitconfig` をテンプレートから配置
3. `post_user_create_gitconfig_use_login_name` の設定に応じて, `user.name` にログイン名またはGECOSフィールドを使用

## テンプレート/ファイル

### Emacs設定ファイル

#### 必須設定ファイル (user-settings ロールで配布)

以下の設定ファイルは, `user-settings` ロール内で `/etc/skel/.emacs.d/user_settings/` に配置されます。
新規ユーザ作成時は, スケルトン環境からユーザホームに自動的にコピーされます。

| ファイル名 | 説明 |
| --- | --- |
| `init.el` | Emacs初期化ファイル (基本的な設定) |
| `proxy-settings.el` | プロキシ設定 |
| `basic-settings.el` | UI・基本設定 |
| `japanese-environment.el` | 日本語対応設定 |

#### オプション設定ファイル (post-user-create ロールで配布)

以下の設定ファイルは本ロール内のテンプレートとして定義されており, 本ロール実行時に各ユーザの `~/.emacs.d/user_settings/` に直接配置されます。
これらのファイルは, Emacsの各種モードや機能を有効化するためのサンプルです。一部のファイルは, MELPAなどから別途インストールする外部Emacsパッケージを必要とする場合があります。外部パッケージの導入は利用者に任せており, `install-emacs-packages.sh` スクリプトと `create_user_emacs_package_list` 変数を使用して, 必要なパッケージを自動インストールすることも可能です。

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

### その他のテンプレート

| テンプレート名 | 出力先 | 説明 |
| --- | --- | --- |
| `install-emacs-packages.sh.j2` | `/etc/skel/bin/install-emacs-packages.sh` | Emacsパッケージインストールスクリプト, `create_user_emacs_package_list` で指定されたパッケージをインストール |
| `_gitconfig.j2` | `~/.gitconfig` | Gitユーザ設定ファイル, user.name と user.email を設定 |

## 実行方法

```bash
make run_post_user_create
```

または,

```bash
# site.yml 全体から post-user-create タグのみ実行
ansible-playbook -i inventory/hosts site.yml --tags "post-user-create"

# 特定ホストのみ対象
ansible-playbook -i inventory/hosts site.yml --tags "post-user-create" -l hostname
```

**注:** 本ロールは `create-users` ロールが事前に実行済みであることを前提としています。

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

### 1. Git設定ファイルの存在確認

**実施ノード:** 対象ホスト

**条件:** `post_user_create_gitconfig_enabled: true` の場合

**コマンド:**
```bash
ls -la /home/username/.gitconfig
```

**期待される出力例:**
```
-rw-r--r-- 1 username username 123  3月  7 10:30 /home/username/.gitconfig
```

**確認ポイント:**
- `.gitconfig` が存在すること
- 所有者 (3列目) とグループ (4列目) が当該ユーザ (`username`) であること
- パーミッションが `-rw-r--r--` (8進数で `0644`) であること

### 2. Git設定内容の確認

**実施ノード:** 対象ホスト

**条件:** `post_user_create_gitconfig_enabled: true` の場合

**コマンド:**
```bash
cat /home/username/.gitconfig
```

**期待される出力例 (post_user_create_gitconfig_use_login_name: true の場合):**
```ini
[user]
	name = username
	email = username@example.com
```

**期待される出力例 (post_user_create_gitconfig_use_login_name: false の場合):**
```ini
[user]
	name = Taro Yamada
	email = username@example.com
```

**確認ポイント:**
- `[user]` セクションが存在すること
- `name` が設定されていること:
  - `post_user_create_gitconfig_use_login_name: true` の場合, ログイン名 (`username`) と一致
  - `post_user_create_gitconfig_use_login_name: false` の場合, GECOSフィールドの内容 (例: `Taro Yamada`) と一致
- `email` が設定されていること (通常は `username@ホスト名` の形式)

### 3. インストールスクリプトの存在確認

**実施ノード:** 対象ホスト

**条件:** `create_user_emacs_package_list` が空でない場合

**コマンド:**
```bash
ls -la /home/username/bin/install-emacs-packages.sh
```

**期待される出力例:**
```
-rwxr-xr-x 1 username username 1080  3月  7 10:30 /home/username/bin/install-emacs-packages.sh
```

**確認ポイント:**
- スクリプトが存在すること
- 所有者 (3列目) とグループ (4列目) が当該ユーザ (`username`) であること
- パーミッションが `-rwxr-xr-x` (8進数で `0755`) であること
  - 先頭の `x` は所有者に実行権限があることを示す
  - 中央の `x` はグループに実行権限があることを示す
  - 末尾の `x` はその他のユーザに実行権限があることを示す

### 4. インストールスクリプトの内容確認

**実施ノード:** 対象ホスト

**条件:** `create_user_emacs_package_list` が空でない場合

**コマンド:**
```bash
head -15 /home/username/bin/install-emacs-packages.sh
```

**期待される出力例:**
```bash
#!/bin/bash
# -*- coding:utf-8 mode:bash -*-
#
# emacsのパッケージをインストールする
# install-emacs-packages.sh パッケージ名
#
# 実行例: install-emacs-packages.sh dockerfile-mode
# 参考:
# https://gist.github.com/knishioka/4578f62e82f90f958fb30da4db557078
#
# This file is generated by ansible.
# last update: 2026-03-07 10:30:15 JST

template=`mktemp`.sh
script=`mktemp`.sh
```

**確認ポイント:**
- スクリプトが正常に生成されていること (shebang `#!/bin/bash` で始まる)
- Ansibleによって生成されたことを示すコメント "This file is generated by ansible." が含まれていること
- 注: このスクリプトは引数でパッケージ名を受け取り, `create_user_emacs_package_list` で指定された各パッケージに対して実行されます

### 5. Emacsオプション設定ファイルの配置確認

**実施ノード:** 対象ホスト

**コマンド:**
```bash
ls -la /home/username/.emacs.d/user_settings/
```

**期待される出力例 (一部抜粋):**
```
合計 112
drwxr-xr-x 2 username username 4096  3月  7 10:30 .
drwxr-xr-x 4 username username 4096  3月  7 10:30 ..
-rw-r--r-- 1 username username  456  3月  7 10:30 aspell-settings.el
-rw-r--r-- 1 username username  512  3月  7 10:30 auctex-mode-settings.el
-rw-r--r-- 1 username username  384  3月  7 10:30 basic-settings.el
-rw-r--r-- 1 username username  423  3月  7 10:30 bsdc-mode-settings.el
-rw-r--r-- 1 username username  398  3月  7 10:30 c-mode-settings.el
...(中略)...
-rw-r--r-- 1 username username  445  3月  7 10:30 yaml-mode-settings.el
-rw-r--r-- 1 username username  467  3月  7 10:30 yatex-mode-setting.el
```

**確認ポイント:**
- `emacs_optional_settings_files` で定義された20個のファイルが配置されていること:
  - aspell-settings.el, auctex-mode-settings.el, bsdc-mode-settings.el, c-mode-settings.el, c-sharp-mode-settings.el, cmake-settings.el, docker-compose-mode-settings.el, docker-tramp-mode-settings.el, dockerfile-mode-settings.el, gnu-global-settings.el, gud-settings.el, hos-c-mode-settings.el, linux-c-mode-settings.el, markdown-mode-settings.el, package-settings.el, python3-settings.el, rust-settings.el, screen-settings.el, yaml-mode-settings.el, yatex-mode-setting.el
- 各ファイルの所有者 (3列目) とグループ (4列目) が当該ユーザ (`username`) であること
- パーミッションが `-rw-r--r--` (8進数で `0644`) であること

### 6. Emacsパッケージのインストール確認 (オプション)

**実施ノード:** 対象ホスト

**条件:** `create_user_emacs_package_list` が空でない場合 (手動確認)

**コマンド:**
```bash
# パッケージディレクトリを直接確認
ls -1 /home/username/.emacs.d/elpa/
```

**期待される出力例 (例: dockerfile-mode, markdown-mode, yaml-mode を指定した場合):**
```
archives
dockerfile-mode-20231130.1801
gnupg
markdown-mode-20240318.1449
yaml-mode-20231211.732
```

**確認ポイント:**
- `create_user_emacs_package_list` で指定したパッケージがインストールされていること
  - パッケージ名にバージョン番号が付加された形式 (例: `dockerfile-mode-20231130.1801`) でディレクトリが存在
- 注: スクリプト実行までは本ロールの責務外だが, ユーザが手動で `~/bin/install-emacs-packages.sh` を実行した後に確認可能

## 補足

### GECOSフィールド取得について

Git設定ファイル作成時に `post_user_create_gitconfig_use_login_name: false` を指定すると, システムのpasswdデータベースからGECOSフィールドを取得して `user.name` に設定します。

GECOSフィールドのインデックスは `vars/cross-distro.yml` の `getent_passwd_field_gecos` 変数で定義されています。将来的に, ディストリビューション間で乖離が発生した場合は, 以下の変数を修正してください:

```yaml
getent_passwd_field_gecos_debian: 3
getent_passwd_field_gecos_rhel:   3
```

現在は両ディストリビューションとも, フィールドインデックス `3` でGECOS情報を取得しています。
