# Debian / Ubuntu リポジトリ設定ロール

- Debian では **デフォルトリポジトリを deb822 形式で宣言**し, `ansible.builtin.deb822_repository` を利用。
- Ubuntu では **`ubuntu.sources` をテンプレート生成**し, Canonical 既定の複数エントリを集約して管理。
- **署名鍵は `/usr/share/keyrings/*.gpg` に配置し, `signed-by=` で明示的に紐付け** (ansibleの`apt_key` モジュールは非推奨のため使用しない)。
- **APT Pinning で優先度を制御** (主要レポジトリの優先度を高くするため `pin_main` を 1001 に設定し, 外部レポジトリは `pin_external` で低優先度に抑制)。
- **外部レポ導入時は鍵  =>  リポジトリ  =>  pinning の順で適用し, 更新後はハンドラで `apt-get update` と代表パッケージ検証を実施。**
- **プロキシや社内ミラーへの切替を想定し, URI や SSL 検証の ON/OFF (`apt_sslverify`) を変数化。**
- **vars/packages-*.yml で定義した `common_packages` を対象に `apt-cache policy` と `apt-get -s install` を実行してメタデータ整合性をチェック。**

## 変数一覧

Ubuntu ノードでは `ubuntu.sources` をテンプレート生成して APT ソースを集約します。主な制御変数は以下の通りで, `group_vars` や `host_vars` から上書きできます。

| 変数 | 規定値 | 説明 |
| ---- | ------ | ---- |
| `ubuntu_sources_suite` | `{{ ansible_distribution_release }}` | `ubuntu.sources` に記載する基準スイート (例: `noble`)。 |
| `ubuntu_sources_components` | `['main', 'universe']` | `/etc/apt/sources.list.d/ubuntu.sources` の `Components:` 行で展開するコンポーネント一覧。必要に応じて `restricted` などを追加します。 |
| `repo_enable_updates` | `true` | true の場合, `Suites:` に `<suite>-updates` を含めます。false で除外。 |
| `repo_enable_backports` | `false` | true の場合, `Suites:` に `<suite>-backports` を含めます。`ubuntu_backports_uris` を独自ミラーに切り替えると別 stanza として出力されます。 |
| `repo_enable_security` | `true` | true の場合, `/etc/apt/sources.list.d/ubuntu.sources` に `<suite>-security` 用の stanza を生成します。 |
| `apt_sslverify` | `true` | `apt-get` 実行時に TLS 証明書検証を行うか否か。内部ミラー等で自己署名証明書を利用する場合は false に変更します。 |
| `repo_enable_main` | `true` | Debian/Ubuntu 共通: メイン (base) リポジトリを有効化するかどうか。 |
| `debian_archive_uris` | `['http://deb.debian.org/debian/']` | Debian ホスト向け base リポジトリの URI。独自ミラーを使う場合に変更します。 |
| `debian_security_uris` | `['http://security.debian.org/debian-security/']` | Debian のセキュリティリポジトリ URI。 独自ミラーを使う場合に変更します。 |
| `debian_backports_uris` | `['http://deb.debian.org/debian-backports/']` | Debian backports リポジトリの URI。 独自ミラーを使う場合に変更します。 |
| `debian_archive_keyring` | `/usr/share/keyrings/debian-archive-keyring.gpg` | Debian リポジトリの署名鍵配置先。 |
| `ubuntu_archive_uris` | `['http://archive.ubuntu.com/ubuntu/']` | Ubuntu base リポジトリの URI。独自ミラーを使う場合に変更します。  |
| `ubuntu_security_uris` | `['http://security.ubuntu.com/ubuntu/']` | Ubuntu セキュリティリポジトリの URI。 独自ミラーを使う場合に変更します。 |
| `ubuntu_backports_uris` | `['http://archive.ubuntu.com/ubuntu/']` | Ubuntu backports 用 URI。独自ミラーを使う場合に変更します。 |
| `ubuntu_archive_keyring` | `/usr/share/keyrings/ubuntu-archive-keyring.gpg` | Ubuntu リポジトリ署名鍵の配置先。 |
| `repo_enable_docker` | `true` | Docker APT リポジトリ (`docker_apt_*`) を登録する。 |
| `docker_apt_keyring_url` | `https://download.docker.com/linux/{{ 'debian' if ansible_distribution == 'Debian' else 'ubuntu' }}/gpg` | Docker APT リポジトリ用鍵を取得する URL。 |
| `docker_apt_keyring` | `/usr/share/keyrings/docker-archive-keyring.gpg` | Docker リポジトリ鍵の配置先。 |
| `docker_apt_uri` | `https://download.docker.com/linux/debian`または, `https://download.docker.com/linux/ubuntu` | Docker リポジトリ URI。Debian/Ubuntu で切り替えて指定されます。 |
| `docker_apt_suite` | `{{ repo_codename_debian }}` | Docker リポジトリで使用する suite 名。通常は OS のコードネームが指定されます。 |
| `docker_apt_components` | `stable` | Docker リポジトリのコンポーネント。 |
| `docker_arch_apt` | `amd64` | Docker リポジトリの対象アーキテクチャ。 |
| `repo_enable_kubernetes` | `true` | Kubernetes (pkgs.k8s.io) リポジトリ (`k8s_apt_*`) を登録するか。 |
| `k8s_major_minor` | `1.31` | Kubernetes リポジトリのメジャー/マイナーバージョン。 |
| `k8s_apt_keyring_url` | `https://pkgs.k8s.io/core:/stable:/v{{ k8s_major_minor }}/deb/Release.key` | Kubernetes リポジトリ鍵の取得 URL。 |
| `k8s_apt_keyring` | `/usr/share/keyrings/kubernetes-apt-keyring.gpg` | Kubernetes リポジトリ鍵の配置先。 |
| `k8s_apt_uri` | `https://pkgs.k8s.io/core:/stable:/v{{ k8s_major_minor }}/deb/` | Kubernetes APT リポジトリ URI。 |
| `k8s_apt_suites` | `/` | Kubernetes リポジトリの suite 指定。既定で `/` を利用する。 |
| `k8s_apt_components` | *(空文字)* | Kubernetes リポジトリのコンポーネント。リポジトリから導入しないため空で定義している。 |
| `k8s_arch_apt` | *(空文字)* | Kubernetes リポジトリのアーキテクチャ指定。必要に応じて `amd64` 等を設定する。 |
| `repo_enable_chrome` | `true` | Google Chrome リポジトリ (`chrome_*`) を登録する。 |
| `chrome_keyring_url` | `https://dl.google.com/linux/linux_signing_key.pub` | Chrome リポジトリ鍵の取得 URL。 |
| `chrome_keyring_path` | `/usr/share/keyrings/google-chrome-archive-keyring.gpg` | Chrome リポジトリ鍵の配置先。 |
| `chrome_apt_uri` | `https://dl.google.com/linux/chrome/deb/` | Chrome APT リポジトリ URI。 |
| `chrome_apt_suite` | `stable` | Chrome リポジトリの suite。Chromeリポジトリの仕様上, Ubuntu コード名ではなく `stable` 固定にする必要がある。 |
| `chrome_apt_components` | `main` | Chrome リポジトリのコンポーネント。 |
| `chrome_arch_apt` | `amd64` | Chrome リポジトリの対象アーキテクチャ。 |
