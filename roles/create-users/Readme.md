# create-users ロール

本ロールは, ユーザとグループを作成し, SSH 公開鍵を authorized_keys に登録します。

## 目次

- [create-users ロール](#create-users-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
    - [ユーザ定義の詳細](#ユーザ定義の詳細)
    - [公開鍵追加の詳細](#公開鍵追加の詳細)
    - [デフォルト動作](#デフォルト動作)
    - [パスワードハッシュの作成方法](#パスワードハッシュの作成方法)
      - [OpenSSL を使う方法](#openssl-を使う方法)
      - [mkpasswd を使う方法](#mkpasswd-を使う方法)
      - [Ansible の password\_hash('sha512') を使う方法](#ansible-の-password_hashsha512-を使う方法)
    - [設定例](#設定例)
    - [注意事項](#注意事項)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [前提条件](#前提条件-1)
    - [1. ユーザ作成の確認](#1-ユーザ作成の確認)
    - [2. authorized\_keys の確認](#2-authorized_keys-の確認)
    - [3. GitHub 公開鍵の確認](#3-github-公開鍵の確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. `users_list` が空, または未定義である場合](#1-users_list-が空-または未定義である場合)
    - [2. `name` が未定義, または空である場合](#2-name-が未定義-または空である場合)
    - [3. 管理者権限で実行できない場合](#3-管理者権限で実行できない場合)
    - [4. ユーザ属性が不正である場合](#4-ユーザ属性が不正である場合)
  - [注意事項](#注意事項-1)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| ユーザ | - | 機能を利用する人, 又は識別された利用主体。 |
| ツール | - | 特定作業を実行するための機能や道具。 |
| リソース | - | 処理に必要な計算機資源やデータ。 |
| クラスタ | - | 複数の機器を連携させて一体運用する構成。 |
| ディストリビューション | - | 基本ソフトウェアと関連部品をまとめた配布形態。 |
| コンテナイメージ | - | コンテナ実行に必要な内容をまとめた保存形式。 |
| プログラム | - | 計算機に処理をさせるための命令列。 |
| コミュニティ | - | 共通目的のもとで継続的に活動する利用者集団。 |
| プラグイン | - | 既存機能へ追加機能を組み込むための拡張部品。 |
| サービスアカウント | - | 自動処理向けに用意する利用主体の識別情報。 |
| コンテナランタイム | - | コンテナを起動, 停止, 管理する実行基盤。 |
| リクエスト | - | 処理実行や情報取得を要求する操作。 |
| コントローラ | - | 対象状態を監視し, 期待状態へ調整する制御機能。 |
| メタデータ | - | 対象データの属性や説明を示す付加情報。 |
| バックエンド | - | 利用者画面の背後で処理を実行する側。 |
| ストレージ | - | データを保存する仕組み。 |
| インストール | - | ソフトウェアを導入して利用可能にする作業。 |
| マシン | - | 処理を実行する計算機。 |
| プロビジョニング | - | 利用開始に必要な設定や資源を準備する作業。 |
| ルーティング | - | 宛先までの経路を選択して転送する処理。 |
| オブジェクト | - | ひとかたまりとして扱うデータ単位。 |
| エージェント | - | 指示に従って処理を代行する構成要素。 |
| ストア | - | データや成果物を保存する場所。 |
| ジャーナル | - | 時系列の記録を保持する仕組み。 |
| アカウント | - | 利用者や処理主体を識別する登録情報。 |
| エンドポイント | - | 通信の接続先を表す識別点。 |
| パターン | - | 繰り返し現れる構造や記述形式。 |
| パケット | - | ネットワークで転送するデータ単位。 |
| カーネル | - | 基本ソフトウェアの中核機能。 |
| シェル | - | コマンド入力で計算機を操作する仕組み。 |
| Playbook | - | 自動化処理の実行手順を記述したファイル。 |
| Canonical | - | Ubuntu を提供する組織名。 |
| Key-Value | - | キーと値の組で情報を表す方式。 |
| Internet Protocol | IP | ネットワーク上で宛先を識別し, データを届けるための通信手順。 |
| Structured Query Language | SQL | データベースを操作するための記述言語。 |
| Hypertext Transfer Protocol | HTTP | World Wide Webで情報をやり取りする通信手順。 |
| Hypertext Transfer Protocol Secure | HTTPS | 通信内容を暗号化してWorld Wide Web通信を行う方式。 |
| RPM Package Manager | RPM | RPM形式パッケージの導入, 更新, 削除, 情報参照を行う仕組み。 |
| Virtual Machine | VM | 物理計算機上で動作する仮想的な計算機。 |
| localhost | - | 同一機器自身を指す名前。 |
| root | - | Unix 系システムの最上位権限を持つ管理者識別子。 |
| ソフトウェア | - | 情報処理システムで使用するプログラム, 手順, 規則及び関連文書の全体又は一部分。 |
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| アプリケーション | - | 利用者の目的を実現するために動作するソフトウェア。 |
| パッケージ | - | ソフトウェア導入に必要なファイルをまとめた配布単位。 |
| リポジトリ | - | ソフトウェアや設定情報を保管し, 取得できるようにした管理場所。 |
| コマンド | - | 実行者が計算機へ処理を指示するための命令。 |
| ホスト | - | 管理対象として識別される個別の計算機。 |
| サーバ | - | 他の機器や利用者へ機能やデータを提供する計算機, 又はその役割。 |
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
| ネットワーク | - | 機器同士を接続してデータをやり取りする仕組み。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
| プロトコル | - | 通信やデータ交換の手順を定めた取り決め。 |
| ディレクトリ | - | ファイルを階層的に整理するための入れ物。 |
| ログ | - | 処理の結果や状態を時系列で記録した情報。 |
| コード | - | 処理内容を記述した文字列。 |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウェア。 |
| Pod | - | Kubernetes でコンテナをまとめて管理する最小単位。 |
| Linux | - | 多くの機器で使われる, 基本ソフトウェアの系統。 |
| Debian | - | コミュニティ主導で開発される Linux ディストリビューション。 |
| Ubuntu | - | Canonical が提供する Debian 系の Linux ディストリビューション。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Secure Shell | SSH | 遠隔の計算機へ安全に接続して操作する方式。 |
| GitHub | - | ソースコードの共有や課題管理を行える開発者向けの公開サービス。本ロールでは公開鍵取得機能を利用します。 |
| authorized_keys | - | SSH の公開鍵を登録するファイル。 |
| Red Hat Enterprise Linux 9 | RHEL9 | Red Hat Enterprise Linux の第9系統版。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| Secure Hash Algorithm 512 | SHA-512 | Secure Hash Algorithm 512 ( SHA-512 ) に基づくハッシュ方式。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `cat` | - | ファイル内容を標準出力へ表示するコマンド。 |
| `getent` | - | システムの名前解決データベースを参照するコマンド。 |
| `grep` | - | テキストから条件に一致する行を抽出するコマンド。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| `openssl` | - | 証明書, 鍵, 暗号関連データを生成, 参照, 検証するコマンド。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| ログイン | - | 利用者認証を行って利用を開始する操作。 |
| リモートホスト | - | ネットワーク越しに接続して操作する別ホスト。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |

## 概要

このロールは, ユーザとグループを作成し, SSH 公開鍵を authorized_keys に登録します。GitHub 公開鍵の取り込みと, users_authorized_keys による個別鍵の追加に対応します。

## 前提条件

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- Ansible 2.15 以降が制御ノード(ansibleコマンドを実行するノード)にインストールされていること
  - `ansible.posix` コレクションがインストールされていること
- リモートホストへの SSH 接続が確立されていること
- `sudo`コマンドによる管理者権限によるコマンド実行が可能であること

## 実行方法

制御ホストで以下のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts site.yml --tags "create-users"
```

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `users_list` | `[]` | 作成するユーザの定義リスト。空の場合は作成しません。 |
| `users_authorized_keys` | `{}` | ユーザ別の公開鍵追加定義。空の場合は処理しません。 |
| `auto_user_add_for_users_authorized_keys` | `false` | `users_authorized_keys` に記載された未作成ユーザの自動作成可否。 |

### ユーザ定義の詳細

`users_list` の各要素は以下のキーを持ちます。

| キー | 必須 | 説明 |
| --- | --- | --- |
| `name` | 必須 | ユーザ名。 |
| `group` | 任意 | 所属グループ名。省略時はユーザ名と同一。 |
| `password` | 任意 | ハッシュ化済みパスワード。省略時はユーザ名のハッシュを使用。 |
| `update_password` | 任意 | `on_create` または `always`。省略時は `on_create`。 |
| `shell` | 任意 | ログインシェル。省略時は `/bin/bash`。 |
| `home` | 任意 | ホームディレクトリ。省略時は `/home/<ユーザ名>`。 |
| `comment` | 任意 | コメント。省略時はユーザ名。 |
| `email` | 任意 | 連絡先メールアドレス。 |
| `github` | 任意 | GitHub アカウント名。指定時に公開鍵を取得。 |

### 公開鍵追加の詳細

`users_authorized_keys` は以下の形式で定義します。

```yaml
users_authorized_keys:
  "ユーザ名":
    - "ssh-ed25519 AAAA... コメント"
    - "ssh-rsa AAAA... コメント"
```

### デフォルト動作

- `users_list` が空の場合, ユーザ作成は行われません。
- `users_authorized_keys` が空の場合, 公開鍵追加は行われません。
- `auto_user_add_for_users_authorized_keys` が `false` の場合, 存在しないユーザへの公開鍵追加はスキップします。

### パスワードハッシュの作成方法

`users_list.password` に設定する SHA-512 ハッシュは, 制御ノードで以下の方法で作成できます。

#### OpenSSL を使う方法

```bash
openssl passwd -6
```

表示されたハッシュ文字列を `users_list.password` に指定します。

#### mkpasswd を使う方法

```bash
mkpasswd --method=sha-512
```

出力されたハッシュ文字列を `users_list.password` に指定します。

#### Ansible の password_hash('sha512') を使う方法

Ansible のフィルタで平文パスワードをハッシュ化し, `users_list.password` に指定できます。

```yaml
users_list:
  - name: "alice"
    password: "{{ 'PlainTextPassword' | password_hash('sha512') }}"
```

### 設定例

ユーザ作成と GitHub 公開鍵の取り込みを行う例です。記載先は, 変数ファイルです。

**記載先**:
- host_vars/ホスト名.yml または group_vars/all/all.yml

**記載例**:

```yaml
users_list:
  - name: "alice"
    group: "developers"
    password: "sha512$rounds=656000$EXAMPLE$HASH"
    update_password: "on_create"
    shell: "/bin/bash"
    home: "/home/alice"
    comment: "Alice Example"
    email: "alice@example.org"
    github: "alice-gh"
```

**各項目の意味**:

| 項目 | 説明 | 記載例での値 | 動作 |
| --- | --- | --- | --- |
| `users_list` | 作成するユーザ定義のリストです。 | `[{...}]` | 指定したユーザが作成されます。 |
| `name` | ユーザ名です。 | `alice` | ユーザと同名グループが作成されます。 |
| `group` | 所属グループです。 | `developers` | 指定グループを主グループとして設定します。 |
| `password` | ハッシュ化済みパスワードです。 | `sha512$...` | 指定値がパスワードとして設定されます。 |
| `update_password` | パスワード更新条件です。 | `on_create` | 新規作成時のみパスワードを設定します。 |
| `shell` | ログインシェルです。 | `/bin/bash` | 指定シェルが設定されます。 |
| `home` | ホームディレクトリです。 | `/home/alice` | 指定パスでホームが作成されます。 |
| `comment` | コメントです。 | `Alice Example` | コメント欄に反映されます。 |
| `email` | 連絡先メールです。 | `alice@example.org` | `.gitconfig` 用の情報として保持します。 |
| `github` | GitHub アカウント名です。 | `alice-gh` | `https://github.com/<ユーザ名>.keys` から公開鍵が追加されます。 |

### 注意事項

- `users_list.password` を省略した場合, ユーザ名を SHA-512 でハッシュ化した値が設定されます。意図したパスワードにする場合は明示的に指定してください。
- `auto_user_add_for_users_authorized_keys: true` はパスワード無しのユーザを作成します。SSH 公開鍵認証のみでログイン可能であり, パスワード認証や su での切り替えはできません。
- GitHub 公開鍵の取得には `github.com` への外部通信が必要です。

## テンプレートと生成ファイル

現時点でテンプレートから出力されるファイルはありません。
一方で, 本ロールはテンプレートを用いずに以下のファイルを作成/更新します。

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `テンプレート未使用 (ランタイム生成)` | `/home/<ユーザ名>/.ssh` (既定: `/home/<ユーザ名>/.ssh`) | SSH 公開鍵配置用ディレクトリ。 条件: `users_list` または `users_authorized_keys` に該当ユーザがある場合。 |
| `テンプレート未使用 (ランタイム生成)` | `/home/<ユーザ名>/.ssh/authorized_keys` (既定: `/home/<ユーザ名>/.ssh/authorized_keys`) | 公開鍵を追記するファイル。 条件: `users_list` または `users_authorized_keys` に該当ユーザがある場合。 |

## 実行フロー

- `tasks/load-params.yml` で OS 別のパッケージ定義と共通変数を読み込み, 単体実行時でも必要な設定値を揃えます。
- `tasks/package.yml`, `tasks/directory.yml`, `tasks/service.yml`, `tasks/config.yml` を順に読み込みます。現時点ではこれらは空タスクで, 実処理は後続のタスクに集約されています。
- `tasks/user_group.yml` で `users_list` に基づきグループとユーザを作成し, 必要に応じてホームディレクトリやログインシェル, パスワード属性を整えます。
- `tasks/authorized_keys.yml` で `users_authorized_keys` に基づき `.ssh` ディレクトリと `authorized_keys` を準備し, GitHub 公開鍵の取り込み, 個別鍵の追記, ソート, 重複排除を行います。

## 検証ポイント

本節では, `create-users` ロール実行後にユーザと公開鍵が反映されていることを確認します。

### 前提条件

- `create-users` ロールが正常に完了していること(`changed` または `ok` の状態)。
- リモートホストへ SSH で接続可能であること。
- sudo 権限が利用可能であること。

### 1. ユーザ作成の確認

作成したユーザが存在することを確認します。

```bash
getent passwd alice
id alice
```

**期待される出力例**:

```
alice:x:1001:1001:Alice Example:/home/alice:/bin/bash
uid=1001(alice) gid=1001(alice) groups=1001(alice)
```

**確認ポイント**:
- `users_list` で指定したユーザが存在すること。

### 2. authorized_keys の確認

公開鍵が登録されていることを確認します。

```bash
sudo ls -l /home/alice/.ssh/authorized_keys
sudo cat /home/alice/.ssh/authorized_keys
```

**期待される出力例**:

```
-rw------- 1 alice alice  1234 Feb 23 10:00 /home/alice/.ssh/authorized_keys
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExampleKey alice@example
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQExampleKey alice@example
```

**確認ポイント**:
- `authorized_keys` が存在し, 公開鍵が登録されていること。

### 3. GitHub 公開鍵の確認

GitHub から取得した公開鍵が登録されていることを確認します。

```bash
sudo grep -E "alice-gh" /home/alice/.ssh/authorized_keys
```

**期待される出力例**:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExampleKey alice-gh@users.noreply.github.com
```

## トラブルシューティング

### 1. `users_list` が空, または未定義である場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
grep -n "users_list" host_vars/*.yml group_vars/all/all.yml vars/all-config.yml
grep -n "Create group\|Create user\|skipping" build-*.log
```

**確認ポイント**:

- `users_list` が定義され, かつ1件以上のユーザ定義があること。
- `build-*.log` に `Create group` と `Create user` のスキップ記録が出ている場合は, 入力変数が空であること。

### 2. `name` が未定義, または空である場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
grep -n "users_list\|name:" host_vars/*.yml group_vars/all/all.yml vars/all-config.yml
grep -n "Create user\|name\|undefined\|empty" build-*.log
```

**確認ポイント**:

- `users_list` の各要素に `name` が設定され, 空文字列でないこと。
- `name` 欠落時はユーザ作成タスクが失敗又はスキップするため, ログ上の該当メッセージを確認できること。

### 3. 管理者権限で実行できない場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
ansible -i inventory/hosts all -m ping -b
grep -n "permission denied\|sudo\|become" build-*.log
```

**確認ポイント**:

- 制御ホストから対象ホストへ `become` 付きでコマンド実行できること。
- `permission denied` 又は `sudo` 関連エラーが出る場合は, 対象ホスト側の sudo 権限設定を見直すこと。

### 4. ユーザ属性が不正である場合

**実施対象ホスト**: 制御ホスト, 対象ホスト

**実行するコマンド**:

```bash
grep -n "Create user\|failed\|invalid\|group\|shell\|password" build-*.log
ansible -i inventory/hosts all -m shell -a "getent group developers" -b
ansible -i inventory/hosts all -m shell -a "test -x /bin/bash && echo ok || echo ng" -b
```

**確認ポイント**:

- `group`, `shell`, `home`, `password` の各属性値が対象OSで有効な値であること。
- `shell` は対象ホスト上に存在する実行可能ファイルであること。
- `password` は SHA-512 形式のハッシュであること。
- `build-*.log` で失敗した task 名と例外メッセージを確認し, 対応する変数を修正できること。

## 注意事項

- `users_list.password` を省略した場合はユーザ名由来の SHA-512 ハッシュが設定されるため, 意図しない認証情報になる場合があります。運用で使用する認証情報を適用する場合は, 事前にハッシュを生成して `users_list.password` を明示してください。
- `auto_user_add_for_users_authorized_keys: true` を指定した場合は, パスワード未設定のユーザが作成されます。パスワード認証や su 切替が必要な運用では, 事前に `users_list` 側で該当ユーザを定義してパスワードハッシュを設定してください。
- GitHub 公開鍵取得は `github.com` への外部通信に依存するため, ネットワーク制限時に鍵登録が失敗する場合があります。外部通信を許可できない環境では, `users_authorized_keys` に公開鍵を直接記載してください。
- `users_authorized_keys` に同一鍵を重複登録した場合は, 実行後の整形処理で重複排除されます。鍵の追加漏れと誤認しないように, 適用後は `authorized_keys` の実体を確認してください。
- `shell` や `home` に対象ホスト上で無効な値を指定した場合は, ユーザ作成タスクが失敗する場合があります。対象 OS 上に実在するシェルパスと, 作成可能なディレクトリパスを指定してください。

## 参考資料

### 公式ドキュメント

- [authorized_keys](https://man.openbsd.org/authorized_keys.5) : OpenSSH の authorized_keys 形式の説明。
- [Adding a new SSH key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account) : GitHub で SSH 公開鍵を登録する手順の説明。
