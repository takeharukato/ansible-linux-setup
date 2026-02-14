# RHEL / Alma Linux / Rocky Linux リポジトリ設定ロール

RHEL/AlmaLinux/Rocky Linux のパッケージリポジトリを設定するためのロールです。以下の方針で作成しています:

- テンプレートファイルを避け, `ansible.builtin.yum_repository` モジュールを使用してリポジトリを宣言的に管理。
- 署名鍵は `/etc/pki/rpm-gpg/` に配置し, `ansible.builtin.rpm_key` でインポート ( RPM パッケージ管理システムの標準的な鍵管理方法 ) 。
- 二段検証を実施: `gpgcheck=1` ( パッケージ署名検証 ) と `repo_gpgcheck=1` ( メタデータ署名検証 ) を原則有効化。
- リポジトリ優先度を制御 ( `dnf-plugins-core` の priority 機能を使用。数値が小さいほど優先度が高い ) 。主要リポジトリ ( BaseOS: 1, AppStream: 2 ) は高優先度, 外部リポジトリ ( EPEL: 90, Kubernetes: 80 ) は低優先度に設定。
- Ubuntu/Debianのリポジトリ処理方針に合わせ, 外部リポジトリの登録プロセスを以下のように実施:
  1. 鍵取得
  2. 鍵インポート
  3. リポジトリ登録
  4. メタデータキャッシュ再生成
- 重複キー混入を防止のため, EPEL の健全化処理を以下のように実施:
  1. 既存の epel*.repo を削除
  2. epel-release をインストール
  3. 再度 epel*.repo を削除
  4. ansible.builtin.yum_repository でリポジトリを新規生成
- プロキシや社内ミラーへの切替を想定し, URL や SSL 検証 ( `repo_sslverify` ) を変数化。
- 変更時ハンドラ: `dnf clean all` と `dnf makecache` を実行し, 代表パッケージで到達性を検証 ( `repoquery` コマンドによる RPM パッケージ管理システムの到達性確認 ) 。

## リポジトリの優先度制御仕様

本ロールでは, RPM パッケージ管理システムのリポジトリ優先度制御機能 ( RHEL/AlmaLinux/Rocky Linux では dnf-plugins-core の priority プラグインと呼ばれる ) を使用して, 同一パッケージが複数のリポジトリから導入可能な場合に使用するリポジトリの優先度を設定します。

本ロールでは, 以下の方針で優先度を設定しています:

 - 主要リポジトリ ( BaseOS/AppStream ) を高優先度に設定 (優先度の設定値を小さい数値 ( `priority_baseos`: 1, `priority_appstream`: 2 ) に設定)
 - 外部リポジトリを必要時のみ使用するよう低優先度に設定 (優先度の設定値を主要リポジトリより大きい数値 ( `priority_epel`: 90, `priority_kubernetes`: 80, `priority_docker_ce`: 70 ) に設定)

## 本ロールでの EPEL 健全化処理

本ロールでは, 以下の場合に発生しうるEPEL ( Extra Packages for Enterprise Linux ) のキーが重複登録される問題を防止するためにEPELリポジトリの健全化処理を実施します。

- cloud-init (クラウドや仮想環境でLinuxインスタンスの初回起動時に, ホスト名, ユーザー, ネットワーク, パッケージのインストールなどの初期設定を自動化するツール)による自動初期設定
- Kickstart(設定ファイル(ks.cfg)を使用してRHELのインストールプロセスを自動化する仕組み)によるインストールの自動化

本ロールでは, 以下の手順でEPELの健全化処理を実施します:

1. 既存の `/etc/yum.repos.d/epel*.repo` を完全に削除
2. `/etc/dnf/dnf.conf` から `repo_gpgcheck=` 行を削除 ( EPEL で失敗の原因となるため )
3. CodeReady Builder ( RHEL ) または CodeReady Linux Builder ( AlmaLinux/Rocky ) を有効化
4. `epel-release` パッケージを EPEL リポジトリを参照せずにインストール
5. `epel-release` が作成した `epel.repo` を再度削除 ( 重複キー混入を防止 )
6. `ansible.builtin.yum_repository` で EPEL を新規生成 ( `gpgcheck=1`, `repo_gpgcheck=0` として設定 )
7. メタデータキャッシュを再生成

## 変数一覧

主な制御変数は以下の通りで, `group_vars` や `host_vars` から上書きできます。

| 変数 | 規定値 | 説明 |
| ---- | ------ | ---- |
| `repo_enable_base` | `true` | BaseOS ( 基本 OS パッケージ群 ) リポジトリを有効化するか。 |
| `repo_enable_appstream` | `true` | AppStream ( アプリケーションストリーム ) リポジトリを有効化するか。 |
| `repo_enable_crb` | `true` | CodeReady Builder ( 開発者向けパッケージ群 ) リポジトリを有効化するか。 |
| `repo_enable_epel` | `true` | EPEL ( Extra Packages for Enterprise Linux ) リポジトリを有効化するか。 |
| `repo_enable_kubernetes` | `true` | Kubernetes ( `pkgs.k8s.io` ) リポジトリを有効化するか。 |
| `repo_enable_chrome` | `true` | Google Chrome リポジトリを有効化するか。 |
| `repo_enable_docker_ce` | `true` | Docker CE ( Community Edition ) リポジトリを有効化するか。 |
| `repo_sslverify` | `true` | パッケージ取得時に TLS 証明書検証を行うか否か。内部ミラー等で自己署名証明書を利用する場合は `false` に変更します。 |
| `repo_gpgcheck` | `true` | パッケージ署名検証 ( GPG 署名による完全性確認 ) を行うか否か。 |
| `repo_repogpgcheck` | `true` | リポジトリメタデータ署名検証 ( repomd.xml の GPG 署名検証 ) を行うか否か。 |
| `priority_baseos` | `1` | BaseOS リポジトリの優先度 ( 数値が小さいほど優先度が高い ) 。 |
| `priority_appstream` | `2` | AppStream リポジトリの優先度。 |
| `priority_crb` | `5` | CodeReady Builder リポジトリの優先度。 |
| `priority_epel` | `90` | EPEL リポジトリの優先度 ( 低い優先度で必要時のみ使用 ) 。 |
| `priority_kubernetes` | `80` | Kubernetes リポジトリの優先度。 |
| `priority_chrome` | `85` | Google Chrome リポジトリの優先度。 |
| `priority_docker_ce` | `70` | Docker CE リポジトリの優先度。 |
| `almalinux_mirror_baseos` | `https://mirrors.almalinux.org/mirrorlist/...` | AlmaLinux BaseOS リポジトリの mirrorlist URL。 |
| `almalinux_mirror_appstream` | `https://mirrors.almalinux.org/mirrorlist/...` | AlmaLinux AppStream リポジトリの mirrorlist URL。 |
| `almalinux_mirror_crb` | `https://mirrors.almalinux.org/mirrorlist/...` | AlmaLinux CodeReady Builder の mirrorlist URL。 |
| `almalinux_gpgkey_file` | `/etc/pki/rpm-gpg/RPM-GPG-KEY-AlmaLinux-9` | AlmaLinux リポジトリの署名鍵配置先。 |
| `epel_gpgkey_url` | `https://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-...` | EPEL リポジトリ鍵の取得 URL。 |
| `epel_gpgkey_file` | `/etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-...` | EPEL リポジトリ鍵の配置先。 |
| `epel_mirrorlist` | `https://mirrors.fedoraproject.org/metalink?repo=epel-...` | EPEL リポジトリの metalink URL ( HTTP の固定 baseurl ではなく metalink を使用 ) 。 |
| `k8s_major_minor` | `1.31` | Kubernetes リポジトリのメジャー/マイナーバージョン。 |
| `k8s_repo_name` | `kubernetes` | Kubernetes リポジトリの識別名。 |
| `k8s_baseurl` | `https://pkgs.k8s.io/core:/stable:/v1.31/rpm/` | Kubernetes RPM リポジトリ URL。 |
| `k8s_gpgkey_url` | `https://pkgs.k8s.io/core:/stable:/v1.31/rpm/repodata/repomd.xml.key` | Kubernetes リポジトリ鍵の取得 URL。 |
| `k8s_gpgkey_file` | `/etc/pki/rpm-gpg/RPM-GPG-KEY-kubernetes` | Kubernetes リポジトリ鍵の配置先。 |
| `chrome_keyring_url` | `https://dl.google.com/linux/linux_signing_key.pub` | Chrome リポジトリ鍵の取得 URL。 |
| `chrome_rpm_baseurl` | `https://dl.google.com/linux/chrome/rpm/stable/$basearch` | Chrome RPM リポジトリ URL。 |
| `chrome_rpm_gpg_file` | `/etc/pki/rpm-gpg/google-chrome-archive-keyring.gpg` | Chrome リポジトリ鍵の配置先。 |
| `docker_ce_keyring_url` | `https://download.docker.com/linux/centos/gpg` | Docker CE リポジトリ鍵の取得 URL。 |
| `docker_ce_rpm_baseurl` | `https://download.docker.com/linux/centos/$releasever/$basearch/stable` | Docker CE RPM リポジトリ URL。 |
| `docker_ce_rpm_gpg_file` | `/etc/pki/rpm-gpg/docker-archive-keyring.gpg` | Docker CE リポジトリ鍵の配置先。 |
| `docker_ce_includepkgs` | `['docker-ce', 'docker-ce-cli', 'containerd.io', ...]` | Docker CE リポジトリから導入を許可するパッケージの白リスト ( 競合防止のため限定 ) 。 |
| `validate_packages_rpm` | `['bash', 'coreutils', 'containerd.io', ...]` | リポジトリ到達性検証用の代表パッケージリスト ( `repoquery` コマンドで確認 ) 。 |

## 参考リンク

### DNF リポジトリ管理と優先度制御

RHEL/AlmaLinux/Rocky Linux のパッケージ管理システムで使用される DNF リポジトリ管理と優先度制御の詳細については, 以下を参照してください:

- Red Hat Customer Portal - dnf.conf(5): https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/managing_software_with_the_dnf_tool/index
  DNF の設定ファイル形式とリポジトリ優先度 ( priority ) の仕組みについて説明

- Fedora Project - DNF System Upgrade: https://docs.fedoraproject.org/en-US/quick-docs/dnf/
  DNF コマンドの基本的な使用方法とリポジトリ管理について説明

- AlmaLinux Wiki - Package Management: https://wiki.almalinux.org/documentation/
  AlmaLinux でのパッケージ管理とリポジトリ設定について説明

- Rocky Linux Documentation: https://docs.rockylinux.org/
  Rocky Linux でのパッケージ管理とリポジトリ設定について説明

### RHEL/AlmaLinux/Rocky Linux リポジトリシステムの用語

このロール内で使用される RHEL/AlmaLinux/Rocky Linux 固有の用語について:

- BaseOS: Red Hat Enterprise Linux およびその互換ディストリビューションにおける基本 OS パッケージ群のリポジトリ。カーネル, 基本システムツール, ライブラリなどを含む

- AppStream: アプリケーションストリームリポジトリ。複数バージョンのアプリケーション, ランタイム, 開発ツールを提供。モジュール形式でバージョン管理される

- CodeReady Builder (CRB) / CodeReady Linux Builder: 開発者向けのパッケージ群を提供するリポジトリ。ヘッダファイル, 開発ライブラリなど。RHEL では CodeReady Builder, AlmaLinux/Rocky では CodeReady Linux Builder と呼ばれる

- EPEL (Extra Packages for Enterprise Linux): Fedora Project が提供する, Enterprise Linux 向けの追加パッケージ群。RHEL 標準リポジトリに含まれない便利なツールやライブラリを提供

- Priority: DNF パッケージマネージャにおけるリポジトリ優先度制御機能。`dnf-plugins-core` パッケージの priority プラグインで実装される。数値が小さいほど優先度が高く, 同じパッケージが複数のリポジトリにある場合, priority 値が小さいリポジトリから優先的にインストールされる

- gpgcheck: RPM パッケージの GPG 署名検証機能。パッケージが改ざんされていないことを確認する

- repo_gpgcheck: リポジトリメタデータ ( `repomd.xml` ) の GPG 署名検証機能。リポジトリ自体が改ざんされていないことを確認する

- metalink / mirrorlist: 複数のミラーサーバーリストを提供する仕組み。固定 URL ( baseurl ) ではなく metalink を使用することで, 障害時の耐性向上と負荷分散が可能になる

詳細は以下を参照:

- Red Hat Documentation - Managing software with the DNF tool: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/managing_software_with_the_dnf_tool/index
  RHEL のパッケージ管理システム全般について

- Fedora Project - EPEL: https://docs.fedoraproject.org/en-US/epel/
  EPEL の概要と使用方法について
