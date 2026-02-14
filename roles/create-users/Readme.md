# create-users ロール

このロールは `vars/all-config.yml` などで定義した `users_list` を基に, Linux ユーザおよび関連設定を一括で整備します。具体的には以下を自動化します。

- プライマリグループの作成とユーザ作成, ホーム・シェル・パスワードの設定
- GitHub からの公開鍵取得と `users_authorized_keys` による追加鍵登録
- `.gitconfig` テンプレートの配布と管理系グループへの所属付与

Ansible の再実行に耐えるよう idempotent に構成されており, 既存ファイルや鍵がある場合はソート・重複排除後に権限を再調整します。

## タスク構成

1. **load-params.yml**: OS ごとの追加変数 ( `vars/cross-distro.yml` )と共通設定 (`vars/all-config.yml`), kube API アドレス ( 他ロールと共用 )などを読み込みます。Debian 系では `adm`/`sudo` を, RHEL 系では `wheel` を `adm_groups` として扱う等, 後続の汎用ロジックに必要な値がここで定義されます。
1. **package.yml / directory.yml / service.yml / config.yml**: 現状はプレースホルダです。将来的に依存パッケージや補助ディレクトリが必要になった場合に備え, include の位置づけだけを確保しています。
1. **user_group.yml**: ロールの中心となる処理です。

    - `users_list` に含まれる各要素を利用してプライマリグループとユーザを作成し, 必要な初期ファイルを整えます。主なパラメータは以下の通りです。
        - `name`: ログイン名。`getent passwd` で確認できるユーザ名に相当します。
        - `group`: プライマリグループ名。存在しない場合は本ロールが作成します。
        - `password`: `/etc/shadow` 互換のハッシュ化済みパスワード文字列。`"{{ 'passwd'|password_hash('sha512') }}"` などを想定しています。
        - `update_password`: パスワード更新タイミング。通常は `on_create` を指定して初回作成時のみ更新します。
        - `home`: ホームディレクトリの絶対パス。既存ディレクトリがある場合も尊重します。
        - `shell`: ログインシェル。`/bin/bash` や `/bin/zsh` など。
        - `comment`: GECOS フィールドに設定するフルネームや備考。
        - `email`: Git 設定や通知に利用するメールアドレス。
        - `github`: 公開鍵を取得する GitHub アカウント名。`https://github.com/<github>.keys` から鍵を取得します。

    - GitHub から `https://github.com/<github>.keys` を取得し, `authorized_keys` に追記, ソート / 重複除去 / 権限整備を行います。
    - `_gitconfig.j2` テンプレートを展開し, `user.name` と `user.email` を `users_list` の `comment` / `email` で設定します。
    - `adm_groups` の各グループを `state=present` で用意し, 対象ユーザ全員を `append: yes` で所属させます。これにより sudoers 側で許可した管理グループへの紐づけが行われます。

1. **authorized_keys.yml**: `users_authorized_keys` に明示した追加公開鍵を, 対象ユーザの `authorized_keys` に追記します。`users_list` への登録有無に依らず動作し, `getent` モジュールでユーザ存在を確認した上で, `authorized_key` モジュールを使用して鍵を追加します。最後に `slurp` と `copy` モジュールでソート / 重複排除と権限調整を行います。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `users_list` | `[]` | 作成するユーザの定義リスト。`name`, `group`, `password`, `update_password`, `home`, `shell`, `comment`, `email`, `github` をキーとして持つ辞書のリストとして定義する。|
| `users_authorized_keys` | `{}` | ユーザ毎に追記したい公開鍵のマッピング。`users_list` への登録有無に依らず動作します。未設定なら追加処理はスキップされます。|
| `auto_user_add_for_users_authorized_keys` | `false` | `users_authorized_keys` に記載されたユーザがホスト上に存在しない場合の動作制御。`true` の場合はデフォルトパラメータ (shell=/bin/bash, home=/home/<username>) でユーザを自動作成し, `false` の場合は公開鍵追加をスキップします。|
| `adm_groups` | Debian 系は `['adm','sudo']`, RHEL 系は `['wheel']` | 管理系グループ一覧。|

## `users_authorized_keys`によって自動追加されるユーザの設定と想定する使用法

`auto_user_add_for_users_authorized_keys`が`true`の場合で, かつ, `users_authorized_keys`のキーに含まれるユーザが対象ホストにない場合, 対象のユーザを新規作成し, `.ssh/authorized_keys`ファイルを作成の上, `users_authorized_keys`で指定された公開鍵を追加します。

新規作成されるユーザは, セキュリティ上の観点から, 以下の条件で使用することを前提に, パスワードなしで作成される。

- パスワード認証でのログイン不可
- suコマンドでのユーザ切り替え不可
- SSH公開鍵認証のみでログイン可能

## テンプレート/出力ファイル

| テンプレート名 | 出力先ディレクトリ | 説明 |
| --- | --- | --- |
| `_gitconfig.j2` | `~<user>/.gitconfig` | `git` の push/pull 設定と `user.name`/`user.email` をユーザ情報に合わせて生成します。 |
| `dummy.j2` | - | 予備テンプレート。現状未使用ですが, テンプレートディレクトリ構成維持のために配置されています。 |

## 実行時の留意事項

- GitHub から鍵を取得する処理では `curl` コマンドを使用します。HTTP プロキシ環境では事前に `proxy_*` 変数や環境設定を整えてください。
- `users_list` で指定する `password` はハッシュ化済みの値を前提としています。`vars/all-config.yml` の例では `password_hash('sha512')` を使用し, `update_password: 'on_create'` を組み合わせる想定です。
- ロールの再実行時には `authorized_keys` をソートし重複排除するため, 手動追記が必要な鍵は `users_authorized_keys` に登録して管理してください。

## 検証ポイント

- 対象ホストで `getent passwd <user>` / `id <user>` を確認し, ユーザ・グループが意図通り作成されていること。
- `ls -la ~<user>/.ssh/authorized_keys` で権限が `600`, 所有者が `<user>:<group>` であること。
- `sudo -U <user> -l` で `adm_groups` 経由の sudo 権限が付与されているかを確認します ( sudoers 設定による )。
- `groups <user>` に `adm_groups` の項目が含まれていること。

## 留意事項

1. `users_list` や `users_authorized_keys` を更新したら, `make run_create_users`, または, `ansible-playbook -i inventory/hosts site.yml --tags create-users` でロールを再実行します。
1. 新規ユーザ追加時は, ホームディレクトリの既存内容と衝突しないよう事前に確認してください。`force` オプションは使用していないため, 既存ユーザのパラメータ変更は Ansible 側が上書き可能な項目に限定されます。
1. 公開鍵の追加は `users_authorized_keys` の置き換え後に, ロールを再実行することで対応できます。GitHub 側の鍵が更新された場合も同様にロールを再実行してください。
1. オペレーションミスにより, 対象アカウントへのログイン不可に陥らないようにするため, 既存の登録済み公開鍵の削除は行わない仕様としています。 鍵削除については手動にて対応が必要です。
