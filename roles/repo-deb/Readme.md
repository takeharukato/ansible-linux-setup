# Debian / Ubuntu リポジトリ設定ロール

Debian/Ubuntuのパッケージリポジトリを設定するためのロールです。本ロールは, 以下の方針で作成しています:

- UbuntuとDebianの双方の環境に適用可能とするようリポジトリの宣言形式を導入先のOSディストリビューションに基づいて切り替え。
  - Debian では デフォルトリポジトリを deb822 形式で宣言し, `ansible.builtin.deb822_repository` を利用。
  - Ubuntu では `ubuntu.sources` をテンプレート生成し, Canonical社既定の複数エントリを集約して管理。
- 署名鍵は `/usr/share/keyrings/*.gpg` に配置し, `signed-by=` で明示的に紐付け (Ansibleの古い`apt_key`モジュールは非推奨のため使用しない)。
- 主要リポジトリ (Debian/Ubuntu標準リポジトリ)とDocker Community Edition, Kubernetes, Chromeなどの導入に使用する外部リポジトリ間の優先度を制御するように設定。
- 外部リポジトリの登録を以下の手順で実施し, 古い形式である `.list` ファイルと新しい形式である `.sources` ファイルとの間で発生しうる重複登録を防止。
  1. 古い形式ファイルを削除
  2. 鍵配置
  3. リポジトリ登録
  4. 優先度設定
- Ansible 2.15 以上の版数を使用している場合は, deb822 形式 (`ansible.builtin.deb822_repository`), Ansible 2.15未満の版数を使用している場合は, `ansible.builtin.apt_repository` を使用し, ansible制御ノードにRHEL9系のOSを使用する場合に対応。
- プロキシや社内ミラーへの切替を想定し, URI や SSL 検証の ON/OFF (`apt_sslverify`) を変数により制御。
- vars/packages-*.yml で定義した `common_packages` を対象に `apt-cache policy` (Debian/Ubuntu のリポジトリパッケージ確認コマンド) と `apt-get -s install` (Debian/Ubuntu の予行演習インストールコマンド) を実行してメタデータ整合性をチェック。

## リポジトリの優先度制御仕様

本ロールでは, Debian/Ubuntu パッケージ管理システムの優先度制御機能である`APT Pinning`を使用して, 同一パッケージが複数のリポジトリから導入可能な場合に使用するリポジトリの優先度を設定します。

本ロールでは、以下の方針で優先度を設定しています:

 - 主要リポジトリの優先度（`pin_main`）を 高い優先度 (設定値:1001) に設定
 - 外部リポジトリの優先度（`pin_external`）は, 必要時のみ使用するよう低い優先度(設定値:90)に設定


## 変数一覧

Ubuntu ノードでは `ubuntu.sources` をテンプレート生成してリポジトリソースを集約します。主な制御変数は以下の通りで, `group_vars` や `host_vars` から上書きできます。

| 変数 | 規定値 | 説明 |
| ---- | ------ | ---- |
| `ubuntu_sources_suite` | `{{ ansible_distribution_release }}` | `ubuntu.sources` に記載する基準リリースバージョン (例: `noble`) (DEB822形式ではsuiteと呼ばれる)。 |
| `ubuntu_sources_components` | `['main', 'universe']` | `/etc/apt/sources.list.d/ubuntu.sources` の `Components:` 行で展開するパッケージカテゴリー一覧 (DEB822形式ではcomponentsと呼ばれる)。必要に応じて `restricted` などを追加します。 |
| `repo_enable_updates` | `true` | true の場合, `Suites:` に `<suite>-updates` を含めます。false で除外。 |
| `repo_enable_backports` | `false` | true の場合, `Suites:` に `<suite>-backports` を含めます。`ubuntu_backports_uris` を独自ミラーに切り替えると, ファイル内で独立した別のセクションとして物理的に分離されて出力されます (DEB822形式のstanzaとして扱う)。 |
| `repo_enable_security` | `true` | true の場合, `/etc/apt/sources.list.d/ubuntu.sources` に `<suite>-security` 用の独立したセクションを生成します (DEB822形式のstanzaとして扱う)。 |
| `apt_sslverify` | `true` | パッケージ取得時に TLS 証明書検証を行うか否か。内部ミラー等で自己署名証明書を利用する場合は false に変更します。 |
| `repo_enable_main` | `true` | Debian/Ubuntu 共通: メイン (base) リポジトリを有効化するかどうか。 |
| `debian_archive_uris` | `['http://deb.debian.org/debian/']` | Debian ホスト向け base リポジトリの URI。独自ミラーを使う場合に変更します。 |
| `debian_security_uris` | `['http://security.debian.org/debian-security/']` | Debian のセキュリティリポジトリ URI。 独自ミラーを使う場合に変更します。 |
| `debian_backports_uris` | `['http://deb.debian.org/debian-backports/']` | Debian backports リポジトリの URI。 独自ミラーを使う場合に変更します。 |
| `debian_archive_keyring` | `/usr/share/keyrings/debian-archive-keyring.gpg` | Debian リポジトリの署名鍵配置先。 |
| `ubuntu_archive_uris` | `['http://archive.ubuntu.com/ubuntu/']` | Ubuntu base リポジトリの URI。独自ミラーを使う場合に変更します。  |
| `ubuntu_security_uris` | `['http://security.ubuntu.com/ubuntu/']` | Ubuntu セキュリティリポジトリの URI。 独自ミラーを使う場合に変更します。 |
| `ubuntu_backports_uris` | `['http://archive.ubuntu.com/ubuntu/']` | Ubuntu backports 用 URI。独自ミラーを使う場合に変更します。 |
| `ubuntu_archive_keyring` | `/usr/share/keyrings/ubuntu-archive-keyring.gpg` | Ubuntu リポジトリ署名鍵の配置先。 |
| `repo_enable_docker` | `true` | Docker APT リポジトリ (`docker_apt_*`) を登録する。登録前に古い形式の `/etc/apt/sources.list.d/docker.list` を削除し, 重複登録を防止。 |
| `docker_apt_keyring_url` | `https://download.docker.com/linux/{{ 'debian' if ansible_distribution == 'Debian' else 'ubuntu' }}/gpg` | Docker APT リポジトリ用鍵を取得する URL。 |
| `docker_apt_keyring` | `/usr/share/keyrings/docker-archive-keyring.gpg` | Docker リポジトリ鍵の配置先。 |
| `docker_apt_uri` | `https://download.docker.com/linux/debian`または, `https://download.docker.com/linux/ubuntu` | Docker リポジトリ URI。Debian/Ubuntu で切り替えて指定されます。 |
| `docker_apt_suite` | `{{ repo_codename_debian }}` | Docker リポジトリで使用するリリースバージョン名 (DEB822形式ではsuiteと呼ばれる)。通常は OS のコードネームが指定されます。 |
| `docker_apt_components` | `stable` | Docker リポジトリのコンポーネント。 |
| `docker_arch_apt` | `amd64` | Docker リポジトリの対象アーキテクチャ。 |
| `repo_enable_kubernetes` | `true` | Kubernetes (pkgs.k8s.io) リポジトリ (`k8s_apt_*`) を登録するか。登録前に古い形式の `/etc/apt/sources.list.d/kubernetes.list` を削除し, 重複登録を防止。 |
| `k8s_major_minor` | `1.31` | Kubernetes リポジトリのメジャー/マイナーバージョン。 |
| `k8s_apt_keyring_url` | `https://pkgs.k8s.io/core:/stable:/v{{ k8s_major_minor }}/deb/Release.key` | Kubernetes リポジトリ鍵の取得 URL。 |
| `k8s_apt_keyring` | `/usr/share/keyrings/kubernetes-apt-keyring.gpg` | Kubernetes リポジトリ鍵の配置先。 |
| `k8s_apt_uri` | `https://pkgs.k8s.io/core:/stable:/v{{ k8s_major_minor }}/deb/` | Kubernetes APT リポジトリ URI。 |
| `k8s_apt_suites` | `/` | Kubernetes リポジトリの suite 指定。既定で `/` を利用する。 |
| `k8s_apt_components` | *(空文字)* | Kubernetes リポジトリのコンポーネント。リポジトリから導入しないため空で定義している。 |
| `k8s_arch_apt` | *(空文字)* | Kubernetes リポジトリのアーキテクチャ指定。必要に応じて `amd64` 等を設定する。 |
| `repo_enable_chrome` | `true` | Google Chrome リポジトリ (`chrome_*`) を登録する。登録前に古い形式の `/etc/apt/sources.list.d/google-chrome.list` を削除し, 重複登録を防止。 |
| `chrome_keyring_url` | `https://dl.google.com/linux/linux_signing_key.pub` | Chrome リポジトリ鍵の取得 URL。 |
| `chrome_keyring_path` | `/usr/share/keyrings/google-chrome-archive-keyring.gpg` | Chrome リポジトリ鍵の配置先。 |
| `chrome_apt_uri` | `https://dl.google.com/linux/chrome/deb/` | Chrome APT リポジトリ URI。 |
| `chrome_apt_suite` | `stable` | Chrome リポジトリのリリースバージョン (DEB822形式ではsuiteと呼ばれる)。Chromeリポジトリの仕様上, Ubuntu コード名ではなく `stable` 固定にする必要がある。 |
| `chrome_apt_components` | `main` | Chrome リポジトリのパッケージカテゴリー (DEB822形式ではcomponentと呼ばれる)。 |
| `chrome_arch_apt` | `amd64` | Chrome リポジトリの対象アーキテクチャ。 |

## 参考リンク

### DEB822 形式仕様

Debian/Ubuntu のパッケージ管理システムで使用される DEB822 形式でのリポジトリセクション定義 ( stanza ) の詳細については, 以下を参照してください：

- Debian Wiki - SourcesList Format: https://wiki.debian.org/SourcesList
  DEB822 形式 ( `.sources` ファイル ) の仕様, キー-値ペア, stanza の区切り方について説明

- Ubuntu マニュアル - sources.list (5): https://manpages.ubuntu.com/manpages/noble/man5/sources.list.5.html
  Ubuntu でのリポジトリリスト形式 ( 従来の1行形式と DEB822 形式の両方 ) について説明

### Debian/Ubuntu リポジトリシステムの用語

このロール内で使用される Debian/Ubuntu 固有の用語について：

- Suite: リリースバージョンを指す用語。Debian/Ubuntu のパッケージ管理システムで使用される。Ubuntu では `noble`, `focal` 等のコードネームに対応し, Debian では `bookworm`, `stable` 等の識別子として使用される

- Component: パッケージカテゴリーを分類する概念。Debian/Ubuntu のリポジトリ管理における区分方法。例：`main` ( 公式サポート対象 ) , `universe` ( コミュニティサポート ) , `restricted` ( プロプライエタリドライバ )

- Stanza: DEB822 形式ファイル内で複数のリポジトリソースを定義する際の独立したセクション。空白行で区切られた単位。同じ URI, Suite, Component を持つソースは同一の stanza に集約される

- APT Pinning: Debian/Ubuntu パッケージ管理システムで複数のリポジトリから同じパッケージがある場合に, 優先度を設定してどのリポジトリから取得するかを制御する機能

詳細は以下を参照：

- Debian Wiki - Repositories: https://wiki.debian.org/DebianRepository
  Debian リポジトリシステムの構造と用語について

- Ubuntu Help - Repositories: https://help.ubuntu.com/stable/ubuntu-help/software-sources.html
  Ubuntu でのリポジトリ管理 ( Suite, Component, Archive の説明を含む )
