# create-users ロール

## 概要

このロールは, ユーザとグループを作成し, SSH 公開鍵を authorized_keys に登録します。GitHub 公開鍵の取り込みと, users_authorized_keys による個別鍵の追加に対応します。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Operating System | OS | 基本ソフトウエア。 |
| Secure Shell | SSH | 暗号化されたリモート接続の仕組み。 |
| GitHub | - | ソースコードの共有や課題管理を行える開発者向けの公開サービス。本ロールでは公開鍵取得機能を利用します。 |
| authorized_keys | - | SSH の公開鍵を登録するファイル。 |

## 前提条件

- 対象 OS: Debian/Ubuntu 系 (Ubuntu24.04を想定), RHEL 系 (AlmaLinux9.6を想定)
- Ansible 2.15 以降が制御ノード(ansibleコマンドを実行するノード)にインストールされていること
  - `ansible.posix` コレクションがインストールされていること
- リモートホストへの SSH 接続が確立されていること
- `sudo`コマンドによる管理者権限によるコマンド実行が可能であること

## 実行フロー

1. `load-params.yml` でリポジトリ直下の vars を読み込みます。
2. `users_list` に従ってグループとユーザを作成します。
3. `.ssh` と `authorized_keys` を作成し, GitHub 公開鍵を取り込みます。
4. `users_authorized_keys` に従って公開鍵を追加し, ソートと重複排除を行います。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `users_list` | `[]` | 作成するユーザの定義リスト。空の場合は作成しません。 |
| `users_authorized_keys` | `{}` | ユーザ別の公開鍵追加定義。空の場合は処理しません。 |
| `auto_user_add_for_users_authorized_keys` | `false` | `users_authorized_keys` に記載された未作成ユーザを自動作成するか。 |

## ユーザ定義の詳細

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

## 公開鍵追加の詳細

`users_authorized_keys` は以下の形式で定義します。

```yaml
users_authorized_keys:
  "ユーザ名":
    - "ssh-ed25519 AAAA... コメント"
    - "ssh-rsa AAAA... コメント"
```

## デフォルト動作

- `users_list` が空の場合, ユーザ作成は行われません。
- `users_authorized_keys` が空の場合, 公開鍵追加は行われません。
- `auto_user_add_for_users_authorized_keys` が `false` の場合, 存在しないユーザへの公開鍵追加はスキップします。

## 注意事項

- `users_list.password` を省略した場合, ユーザ名を SHA-512 でハッシュ化した値が設定されます。意図したパスワードにする場合は明示的に指定してください。
- `auto_user_add_for_users_authorized_keys: true` はパスワード無しのユーザを作成します。SSH 公開鍵認証のみでログイン可能であり, パスワード認証や su での切り替えはできません。
- GitHub 公開鍵の取得には `github.com` への外部通信が必要です。

## パスワードハッシュの作成方法

`users_list.password` に設定する SHA-512 ハッシュは, 制御ノードで以下の方法で作成できます。

### OpenSSL を使う方法

```bash
openssl passwd -6
```

表示されたハッシュ文字列を `users_list.password` に指定します。

### mkpasswd を使う方法

```bash
mkpasswd --method=sha-512
```

出力されたハッシュ文字列を `users_list.password` に指定します。

### Ansible の password_hash('sha512') を使う方法

Ansible のフィルタで平文パスワードをハッシュ化し, `users_list.password` に指定できます。

```yaml
users_list:
  - name: "alice"
    password: "{{ 'PlainTextPassword' | password_hash('sha512') }}"
```

## テンプレート/ファイル

現時点でテンプレートから出力されるファイルはありません。
一方で, 本ロールはテンプレートを用いずに以下のファイルを作成/更新します。

| ファイル | 作成条件 | 説明 |
| --- | --- | --- |
| `/home/<ユーザ名>/.ssh` | `users_list` または `users_authorized_keys` に該当ユーザがある場合 | SSH 公開鍵配置用ディレクトリ。 |
| `/home/<ユーザ名>/.ssh/authorized_keys` | `users_list` または `users_authorized_keys` に該当ユーザがある場合 | 公開鍵を追記するファイル。 |

## 設定例

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
    email: "alice@example.com"
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
| `email` | 連絡先メールです。 | `alice@example.com` | `.gitconfig` 用の情報として保持します。 |
| `github` | GitHub アカウント名です。 | `alice-gh` | `https://github.com/<ユーザ名>.keys` から公開鍵が追加されます。 |

## 検証ポイント

本節では, `create-users` ロール実行後にユーザと公開鍵が反映されているかを確認します。

### 前提条件

- `create-users` ロールが正常に完了していること(`changed` または `ok` の状態)。
- リモートホストへ SSH で接続可能であること。
- sudo 権限が利用可能であること。

### 1. ユーザ作成の確認

作成したユーザが存在するかを確認します。

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

公開鍵が登録されているかを確認します。

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

GitHub から取得した公開鍵が登録されているかを確認します。

```bash
sudo grep -E "alice-gh" /home/alice/.ssh/authorized_keys
```

**期待される出力例**:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExampleKey alice-gh@users.noreply.github.com
```
