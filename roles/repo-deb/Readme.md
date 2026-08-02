# Debian / Ubuntu リポジトリ設定ロール

本ロールは, Debian/Ubuntuのパッケージリポジトリを設定するためのロールです。

## 目次

- [Debian / Ubuntu リポジトリ設定ロール](#debian--ubuntu-リポジトリ設定ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
  - [トラブルシューティング](#トラブルシューティング)
  - [注意事項](#注意事項)
    - [リポジトリの優先度制御仕様](#リポジトリの優先度制御仕様)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)
    - [Deb822 仕様](#deb822-仕様)
      - [Debian/Ubuntu リポジトリシステムの用語](#debianubuntu-リポジトリシステムの用語)

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
| Internet Protocol | IP | インターネットプロトコルの略称。 |
| Structured Query Language | SQL | データベースを操作するための記述言語。 |
| Hypertext Transfer Protocol | HTTP | WWW で情報をやり取りする通信手順。 |
| Hypertext Transfer Protocol Secure | HTTPS | 通信内容を暗号化して WWW 通信を行う方式。 |
| RPM Package Manager | RPM | RHEL 系で使用するパッケージ形式。 |
| Virtual Machine | VM | 物理機器上で動作する仮想的な計算機。 |
| localhost | - | 同一機器自身を指す名前。 |
| root | - | Unix 系システムの最上位権限を持つ管理者識別子。 |
| ソフトウェア | - | 情報処理システムで使用するプログラム, 手順, 規則及び関連文書の全体又は一部分。 |
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
| Pod | - | Kubernetes でコンテナをまとめて管理する最小単位。 |
| Linux | - | 多くの機器で使われる, 基本ソフトウェアの系統。 |
| Debian | - | コミュニティ主導で開発される Linux ディストリビューション。 |
| Ubuntu | - | Canonical が提供する Debian 系の Linux ディストリビューション。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Application Programming Interface | API | アプリケーション同士がやり取りする方法を定めた仕様。 |
| Uniform Resource Locator | URL | WWW 上の資源の場所を示す文字列。 |
| Advanced Package Tool | APT | Debian 系のパッケージ管理ツール。 |
| Debian Package | DEB | Debian/Ubuntu 系で使用するパッケージ形式。 |
| Deb822 | DEB822 | Debian系のパッケージ管理情報を構造化された形式で記述するための記述形式。 |
| GNU Privacy Guard | GPG | 公開鍵暗号方式でデータを保護するためのソフトウェア。 |
| Transport Layer Security | TLS | 通信経路でデータを暗号化して保護する仕組み。 |
| Secure Sockets Layer | SSL | 通信を暗号化する旧来方式の名称。現在は主に TLS を使用する。 |
| Uniform Resource Identifier | URI | インターネット上のリソースを識別する統一的な識別子体系 |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウェア。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Uniform Resource Locator | URL | URL の正式名称。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| Off | OFF | 無効状態を示す値。 |
| On | ON | 有効状態を示す値。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |

## 概要
Debian/Ubuntuのパッケージリポジトリを設定するためのロールです。本ロールは, 以下の方針で作成しています:
- UbuntuとDebianの双方の環境に適用可能とするようリポジトリの宣言形式を導入先のOSディストリビューションに基づいて切り替え。
  - Debian では デフォルトリポジトリを Deb822 で宣言し, `ansible.builtin.deb822_repository` を利用。
  - Ubuntu では `ubuntu.sources` をテンプレート生成し, Canonical社既定の複数エントリを集約して管理。
- 署名鍵は `/usr/share/keyrings/*.gpg` に配置し, `signed-by=` で明示的に紐付け (Ansibleの古い`apt_key`モジュールは非推奨のため使用しない)。
- 主要リポジトリ (Debian/Ubuntu標準リポジトリ)とDocker Community Edition, Kubernetes, Chromeなどの導入に使用する外部リポジトリ間の優先度を制御するように設定。
- 外部リポジトリの登録を以下の手順で実施し, 古い形式である `.list` ファイルと新しい形式である `.sources` ファイルとの間で発生しうる重複登録を防止。
  1. 古い形式ファイルを削除
  2. 鍵配置
  3. リポジトリ登録
  4. 優先度設定
- Ansible 2.15 以上の版数を使用している場合は, Deb822 (`ansible.builtin.deb822_repository`), Ansible 2.15未満の版数を使用している場合は, `ansible.builtin.apt_repository` を使用し, ansible制御ノードにRHEL9系のOSを使用する場合に対応。
- プロキシや社内ミラーへの切替を想定し, URI や SSL 検証の ON/OFF (`apt_sslverify`) を変数により制御。
- vars/packages-*.yml で定義した `common_packages` を対象に `apt-cache policy` (Debian/Ubuntu のリポジトリパッケージ確認コマンド) と `apt-get -s install` (Debian/Ubuntu の予行演習インストールコマンド) を実行してメタデータ整合性をチェック。

本ロールは, repo-deb に関する設定処理を実施します。

## 前提条件

- 対象ホストが inventory に登録済みであること
- 関連する共通変数が vars/all-config.yml または host_vars に定義済みであること

## 実行方法

実行者は制御ホストで以下のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts site.yml --tags "repo-deb"
```

## 主要変数

Ubuntu ノードでは `ubuntu.sources` をテンプレート生成してリポジトリソースを集約します。主な制御変数は以下の通りで, `vars/all-config.yml` や `host_vars` から上書きできます。

| 変数 | 規定値 | 説明 |
| ---- | ------ | ---- |
| `ubuntu_sources_suite` | `noble` | `ubuntu.sources` に記載する基準リリースバージョン (Deb822 では suite と呼ばれる)。 |
| `ubuntu_sources_components` | `['main', 'universe']` | `/etc/apt/sources.list.d/ubuntu.sources` の `Components:` 行で展開するパッケージカテゴリー一覧 (Deb822 では components と呼ばれる)。必要に応じて `restricted` などを追加します。 |
| `repo_enable_updates` | `true` | true の場合, `Suites:` に `<suite>-updates` を含めます。false で除外。 |
| `repo_enable_backports` | `false` | true の場合, `Suites:` に `<suite>-backports` を含めます。`ubuntu_backports_uris` を独自ミラーに切り替えると, ファイル内で独立した別のセクションとして物理的に分離されて出力されます (Deb822 の stanza として扱う)。 |
| `repo_enable_security` | `true` | true の場合, `/etc/apt/sources.list.d/ubuntu.sources` に `<suite>-security` 用の独立したセクションを生成します (Deb822 の stanza として扱う)。 |
| `apt_sslverify` | `true` | パッケージ取得時に TLS 証明書検証を行う設定の可否。内部ミラー等で自己署名証明書を利用する場合は false に変更します。 |
| `repo_enable_main` | `true` | Debian/Ubuntu 共通: メイン (base) リポジトリを有効化する可否。 |
| `debian_archive_uris` | `['http://deb.debian.org/debian/']` | Debian ホスト向け base リポジトリの URI。独自ミラーを使う場合に変更します。 |
| `debian_security_uris` | `['http://security.debian.org/debian-security/']` | Debian のセキュリティリポジトリ URI。 独自ミラーを使う場合に変更します。 |
| `debian_backports_uris` | `['http://deb.debian.org/debian-backports/']` | Debian backports リポジトリの URI。 独自ミラーを使う場合に変更します。 |
| `debian_archive_keyring` | `/usr/share/keyrings/debian-archive-keyring.gpg` | Debian リポジトリの署名鍵配置先。 |
| `ubuntu_archive_uris` | `['http://archive.ubuntu.com/ubuntu/']` | Ubuntu base リポジトリの URI。独自ミラーを使う場合に変更します。  |
| `ubuntu_security_uris` | `['http://security.ubuntu.com/ubuntu/']` | Ubuntu セキュリティリポジトリの URI。 独自ミラーを使う場合に変更します。 |
| `ubuntu_backports_uris` | `['http://archive.ubuntu.com/ubuntu/']` | Ubuntu backports 用 URI。独自ミラーを使う場合に変更します。 |
| `ubuntu_archive_keyring` | `/usr/share/keyrings/ubuntu-archive-keyring.gpg` | Ubuntu リポジトリ署名鍵の配置先。 |
| `repo_enable_docker` | `true` | Docker APT リポジトリ (`docker_apt_*`) を登録します。登録前に古い形式の `/etc/apt/sources.list.d/docker.list` を削除し, 重複登録を防止。 |
| `docker_apt_keyring_url` | Debian: `https://download.docker.com/linux/debian/gpg`, Ubuntu: `https://download.docker.com/linux/ubuntu/gpg` | Docker APT リポジトリ用鍵を取得する URL。 |
| `docker_apt_keyring` | `/usr/share/keyrings/docker-archive-keyring.gpg` | Docker リポジトリ鍵の配置先。 |
| `docker_apt_uri` | `https://download.docker.com/linux/debian`または, `https://download.docker.com/linux/ubuntu` | Docker リポジトリ URI。Debian/Ubuntu で切り替えて指定されます。 |
| `docker_apt_suite` | Debian: `bookworm`, Ubuntu: `noble` | Docker リポジトリで使用するリリースバージョン名 (Deb822 では suite と呼ばれる)。 |
| `docker_apt_components` | `stable` | Docker リポジトリのコンポーネント。 |
| `docker_arch_apt` | `amd64` | Docker リポジトリの対象アーキテクチャ。 |
| `repo_enable_kubernetes` | `true` | Kubernetes (pkgs.k8s.io) リポジトリ (`k8s_apt_*`) の登録可否。登録前に古い形式の `/etc/apt/sources.list.d/kubernetes.list` を削除し, 重複登録を防止。 |
| `k8s_major_minor` | `1.31` | Kubernetes リポジトリのメジャー/マイナーバージョン。 |
| `k8s_apt_keyring_url` | `https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key` | Kubernetes リポジトリ鍵の取得 URL。 |
| `k8s_apt_keyring` | `/usr/share/keyrings/kubernetes-apt-keyring.gpg` | Kubernetes リポジトリ鍵の配置先。 |
| `k8s_apt_uri` | `https://pkgs.k8s.io/core:/stable:/v1.31/deb/` | Kubernetes APT リポジトリ URI。 |
| `k8s_apt_suites` | `/` | Kubernetes リポジトリの suite 指定。既定で `/` を利用します。 |
| `k8s_apt_components` | *(空文字)* | Kubernetes リポジトリのコンポーネント。リポジトリから導入しないため空で定義している。 |
| `k8s_arch_apt` | *(空文字)* | Kubernetes リポジトリのアーキテクチャ指定。必要に応じて `amd64` 等を設定します。 |
| `repo_enable_chrome` | `true` | Google Chrome リポジトリ (`chrome_*`) を登録します。登録前に古い形式の `/etc/apt/sources.list.d/google-chrome.list` を削除し, 重複登録を防止。 |
| `chrome_keyring_url` | `https://dl.google.com/linux/linux_signing_key.pub` | Chrome リポジトリ鍵の取得 URL。 |
| `chrome_keyring_path` | `/usr/share/keyrings/google-chrome-archive-keyring.gpg` | Chrome リポジトリ鍵の配置先。 |
| `chrome_apt_uri` | `https://dl.google.com/linux/chrome/deb/` | Chrome APT リポジトリ URI。 |
| `chrome_apt_suite` | `stable` | Chrome リポジトリのリリースバージョン (Deb822 では suite と呼ばれる)。Chromeリポジトリの仕様上, Ubuntu コード名ではなく `stable` 固定にする必要がある。 |
| `chrome_apt_components` | `main` | Chrome リポジトリのパッケージカテゴリー (Deb822 では component と呼ばれる)。 |
| `chrome_arch_apt` | `amd64` | Chrome リポジトリの対象アーキテクチャ。 |

## テンプレートと生成ファイル

本ロールでは以下のテンプレート / ファイルを出力します:
主な展開先ホストは, 対象ホスト(既定) です。

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `ubuntu.sources.j2` | `/etc/apt/sources.list.d/ubuntu.sources` (既定) | Ubuntu の APT 参照先, コンポーネント, 署名鍵を統一する Deb822 リポジトリ設定です。 |

## 実行フロー

1. [tasks/load-params.yml](tasks/load-params.yml) で OS 別パッケージ変数と共通変数を読み込みます。
2. [tasks/repositories.yml](tasks/repositories.yml) で基本依存パッケージを導入し, Debian/Ubuntu と Ansible 版数条件に応じて [tasks/debian.yml](tasks/debian.yml), [tasks/debian-on-rhel9.yml](tasks/debian-on-rhel9.yml), [tasks/ubuntu.yml](tasks/ubuntu.yml), [tasks/ubuntu-on-rhel9.yml](tasks/ubuntu-on-rhel9.yml), [tasks/external.yml](tasks/external.yml), [tasks/external-on-rhel9.yml](tasks/external-on-rhel9.yml) を切り替えてリポジトリ設定を適用し, `apt-get update` を実行します。
3. [tasks/package.yml](tasks/package.yml), [tasks/directory.yml](tasks/directory.yml), [tasks/user_group.yml](tasks/user_group.yml), [tasks/service.yml](tasks/service.yml), [tasks/config.yml](tasks/config.yml) を順に実行し, 最後に検証コマンドで期待結果を確認します。

## 検証ポイント

以下の検証コマンドを実行し, 構文検査が成功することを確認します。

```bash
ansible-playbook -i inventory/hosts site.yml --syntax-check
```

期待結果: エラーが出力されず, syntax check が成功します。

## トラブルシューティング

実行者はエラー発生時に build-*.log を確認し, 失敗した task 名と不足変数を特定します。代表的なトラブルと対処を以下に示します。

| 想定トラブル | 主な原因 | 対処方法 |
| --- | --- | --- |
| `apt-get update` が失敗する | ミラー到達不可, 名前解決失敗, TLS証明書検証エラー | 実行者は対象ホストで `apt-get update` を実行して失敗メッセージを確認します。社内ミラーや自己署名証明書を利用する場合は `apt_sslverify: false` を設定し, `ubuntu_archive_uris` または `debian_archive_uris` を到達可能なURIに変更して再実行します。 |
| Docker / Kubernetes / Chrome の鍵取得で失敗する | 外部サイト到達不可, プロキシ未設定, `curl` / `gpg` 実行失敗 | 実行者は `curl -fsSL <鍵URL>` の単体実行で到達性を確認します。不要な外部リポジトリは `repo_enable_docker`, `repo_enable_kubernetes`, `repo_enable_chrome` を `false` に設定して無効化できます。 |
| Debian でリポジトリ設定が期待と異なる | Ansible 2.15 未満経路で `debian_suite_on_ansible_lt_2_15` が対象OSと不一致 | 実行者は `ansible --version` を確認し, 2.15未満で実行する場合は `debian_suite_on_ansible_lt_2_15` を対象のDebian版数に合わせます。既定値は `bookworm` です。 |
| Ubuntu で `.sources` と `.list` の混在により重複警告が出る | 旧形式設定の残存, 別ロールや手動設定との競合 | 実行者は `/etc/apt/sources.list.d/` 配下で `docker.list`, `kubernetes.list`, `google-chrome.list` や重複する `ubuntu-*.sources` の残存を確認し, 不要ファイルを整理して再実行します。 |
| `Apt_validate_repo_deb` が失敗する | `common_packages` の未定義, 追加したリポジトリに対象パッケージが存在しない | 実行者は `vars/packages-ubuntu.yml` と `vars/packages-rhel.yml` の `common_packages` を確認し, 対象パッケージに対して `apt-cache policy <package>` が成功することを確認します。必要に応じてミラー設定またはパッケージ一覧を修正します。 |
| ピン優先度が意図どおりにならない | `pin_main` / `pin_external` の値不整合, 優先度設定ファイルの上書き | 実行者は `/etc/apt/preferences.d/99-external.pref` の内容を確認し, `pin_external: 90` が適用されていることを確認します。主要リポジトリを優先したい場合は `pin_main: 1001` と併せて設定を見直します。 |

## 注意事項

### リポジトリの優先度制御仕様

本ロールでは, Debian/Ubuntu パッケージ管理システムの優先度制御機能である`APT Pinning`を使用して, 同一パッケージが複数のリポジトリから導入可能な場合に使用するリポジトリの優先度を設定します。

本ロールでは、以下の方針で優先度を設定しています:

 - 主要リポジトリの優先度（`pin_main`）を 高い優先度 (設定値:1001) に設定
 - 外部リポジトリの優先度（`pin_external`）は, 必要時のみ使用するよう低い優先度(設定値:90)に設定

## 参考資料

### 公式ドキュメント

- [Debian Repository Format](https://wiki.debian.org/DebianRepository/Format)

### Deb822 仕様

Debian/Ubuntu のパッケージ管理情報を構造化された形式で記述するための記述形式 Deb822 の詳細については, 以下を参照してください：

- [Debian Wiki - SourcesList Format](https://wiki.debian.org/SourcesList) Deb822 ( `.sources` ファイル ) の仕様, キー-値ペア, stanza の区切り方について説明
- [Ubuntu マニュアル - sources.list (5)](https://manpages.ubuntu.com/manpages/noble/man5/sources.list.5.html) Ubuntu でのリポジトリリスト形式 ( 従来の1行形式と Deb822 の両方 ) について説明

#### Debian/Ubuntu リポジトリシステムの用語

このロール内で使用されるDebian/Ubuntu リポジトリシステムの用語の意味は以下の通り:

- Suite: リリースバージョンを指す用語。Debian/Ubuntu のパッケージ管理システムで使用される。Ubuntu では `noble`, `focal` 等のコードネームに対応し, Debian では `bookworm`, `stable` 等の識別子として使用される

- Component: パッケージカテゴリーを分類する概念。Debian/Ubuntu のリポジトリ管理における区分方法。例：`main` ( 公式サポート対象 ) , `universe` ( コミュニティサポート ) , `restricted` ( プロプライエタリドライバ )

- Stanza: Deb822 ファイル内で複数の設定項目を定義する際の独立したセクション。空白行で区切られた単位。同じ URI, Suite, Component を持つ設定は同一の stanza に集約される

- APT Pinning: Debian/Ubuntu パッケージ管理システムで複数のリポジトリから同じパッケージがある場合に, 優先度を設定して取得元リポジトリを制御する機能

詳細は以下を参照ください:

- [Debian Wiki - Repositories](https://wiki.debian.org/DebianRepository) Debian リポジトリシステムの構造と用語について
- [Ubuntu Help - Repositories](https://help.ubuntu.com/stable/ubuntu-help/software-sources.html) Ubuntu でのリポジトリ管理 ( Suite, Component, Archive の説明を含む )
