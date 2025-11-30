# Debian / Ubuntu リポジトリ設定ロール

- **デフォルトリポジトリは deb822 形式で宣言**し, テンプレート直書きを避けて `ansible.builtin.deb822_repository` を利用。
- **署名鍵は `/usr/share/keyrings/*.gpg` に配置し, `signed-by=` で明示的に紐付け** (`apt_key` は使用しない)。
- **APT Pinning で優先度を制御** (`pin_main` を高優先度 1001, 外部レポは `pin_external` で抑制)。
- **外部レポ導入時は鍵  =>  リポジトリ  =>  pinning の順で適用し, 更新後はハンドラで `apt-get update` と代表パッケージ検証を実施。**
- **プロキシや社内ミラーへの切替を想定し, URI や SSL 検証の ON/OFF (`apt_sslverify`) を変数化**。
- **`validate_packages_apt` により `apt-cache policy` と `apt-get -s install` を実行してメタデータ整合性をチェック。**

```bash
ansible-playbook -i inventory/hosts base.yml --tags repo-deb
```
