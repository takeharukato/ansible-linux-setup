# devel-packages ロール

このロールは開発環境をセットアップするために必要なパッケージ群を各ノードへ導入し, グラフィカルターゲットを無効化してコンソールモードに固定します。ロール単体でも実行できるよう, 冒頭で共通変数ファイルを読み込み, 対象ディストリビューションに応じたパッケージ定義を選択します。

## 主な処理

- `tasks/load-params.yml` で以下の変数ファイルを読み込みます。
  - `vars/packages-ubuntu.yml` または `vars/packages-rhel.yml` を `ansible_facts.os_family` に応じて選択し, `devel_packages` を定義します。
  - 追加の共通設定として `vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml` を読み込みます。
- `tasks/package.yml` で `devel_packages` の全パッケージを最新化 (`state: latest`) し, 変更があった場合は `disable_gui` ハンドラを通知します。
- `handlers/disable-gui.yml` が通知を受け取ると `systemctl set-default multi-user.target` を実行し, GUI ターゲットを停止して再起動後もテキストログインを維持します。
- `tasks/directory.yml` / `user_group.yml` / `service.yml` / `config.yml` は拡張用のプレースホルダーとなっており, 追加の開発用途が発生した際に追記できます。

## 利用する変数

- `devel_packages`: インストール対象のパッケージ一覧。既定値はリポジトリ直下の `vars/packages-ubuntu.yml`, `vars/packages-rhel.yml` に定義されており, 必要に応じて `group_vars` / `host_vars` で上書きします。

## 実行方法

```bash
ansible-playbook -i inventory/hosts devel.yml --tags devel-packages
```

タグ指定を省略してもプレイブック内でこのロールが呼び出される場合は自動的に適用されます。大量の開発パッケージを導入するため, 事前に `apt update` や `yum makecache` 相当の操作が実行されるよう, 上位プレイブックの処理順を確認してください。

## 検証ポイント

- 対象ホストで `ansible_facts.os_family` に応じたパッケージ群がインストールされている (`dpkg -l` や `rpm -q` で確認)。
- `systemctl get-default` の結果が `multi-user.target` に切り替わっている。
- 既存の GUI ログイン要求がないワークロードであることを確認し, 必要な場合はハンドラ通知を抑制するために `notify` を外す, もしくはホスト変数で条件分岐を追加します。
