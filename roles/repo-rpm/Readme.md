# RHEL / Alma Linux / Rocky Linux リポジトリ設定ロール

本ロールは, RHEL/AlmaLinux/Rocky Linux のパッケージリポジトリを設定するためのロールです。

## 目次

- [RHEL / Alma Linux / Rocky Linux リポジトリ設定ロール](#rhel--alma-linux--rocky-linux-リポジトリ設定ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
  - [トラブルシューティング](#トラブルシューティング)
  - [注意事項](#注意事項)
    - [リポジトリの優先度制御仕様](#リポジトリの優先度制御仕様)
    - [本ロールでの EPEL 健全化処理](#本ロールでの-epel-健全化処理)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)
    - [DNF リポジトリ管理と優先度制御](#dnf-リポジトリ管理と優先度制御)
    - [RHEL/AlmaLinux/Rocky Linux リポジトリシステムの用語](#rhelalmalinuxrocky-linux-リポジトリシステムの用語)

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| ユーザ | - | 機能を利用する人, 又は識別された利用主体。 |
| ツール | - | 特定作業を実行するための機能や道具。 |
| リソース | - | 処理に必要な計算機資源やデータ。 |
| クラスタ | - | 複数の機器を連携させて一体運用する構成。 |
| ディストリビューション | - | 基本ソフトウェアと関連部品をまとめた配布形態。 |
| コンテナイメージ | - | コンテナ実行に必要な内容をまとめた保存形式。 |
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
| ノード | - | ネットワークに接続された機器または処理単位。 |
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
| プロトコル | - | 通信やデータ交換の手順を定めた取り決め。 |
| ディレクトリ | - | ファイルを階層的に整理するための入れ物。 |
| ログ | - | 処理の結果や状態を時系列で記録した情報。 |
| コード | - | 処理内容を記述した文字列。 |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウェア。 |
| Pod | - | Kubernetes でコンテナをまとめて管理する最小単位。 |
| Debian | - | コミュニティ主導で開発される Linux ディストリビューション。 |
| Ubuntu | - | Canonical が提供する Debian 系の Linux ディストリビューション。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Application Programming Interface | API | アプリケーション同士がやり取りする方法を定めた仕様。 |
| Uniform Resource Locator | URL | WWW 上の資源の場所を示す文字列。 |
| ソフトウェア | - | 情報処理システムで使用するプログラム, 手順, 規則及び関連文書の全体又は一部分。 |
| 基本ソフトウェア | - | 応用ソフトウェアの実行を支援する, 応用に依存しないソフトウェア。 |
| オペレーティングシステム | OS | プログラムの実行を制御し, 入出力制御とデータ管理を行う基本ソフトウェア。 |
| プログラム | - | 計算機に処理をさせるための命令列。 |
| ファイル | - | 一つの名前で管理するデータのまとまり。 |
| テキスト | - | 文字, 記号, 語, 句, 段落, 文などの文字配置で表したデータ。 |
| ネットワーク | - | 機器同士を接続してデータをやり取りする仕組み。 |
| リポジトリ | - | ソフトウェアや設定情報を保管し, 取得できるようにした管理場所。 |
| パッケージ | - | ソフトウェア導入に必要なファイルをまとめた配布単位。 |
| コマンド | - | 実行者が計算機へ処理を指示するための命令。 |
| サーバ | - | 他の機器や利用者へ機能やデータを提供する計算機, 又はその役割。 |
| ホスト | - | 管理対象として識別される個別の計算機。 |
| アプリケーション | - | 利用者の目的を実現するために動作するソフトウェア。 |
| Linux | - | 多くの機器で使われる, 基本ソフトウェアの系統。 |
| Red Hat | - | Linux 関連製品を提供する企業名。 |
| AlmaLinux | - | RHEL と互換性を持つ Linux の配布形態。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| RPM Package Manager | RPM | RHEL/AlmaLinux 系で使用するパッケージ形式。 |
| Dandified YUM | DNF | YUM の後継として利用するパッケージ管理ツール。 |
| Yellowdog Updater Modified | YUM | RPM パッケージの導入, 更新, 削除を行う管理ツール。 |
| GNU Privacy Guard | GPG | 公開鍵暗号方式でデータを保護するためのソフトウェア。 |
| Extra Packages for Enterprise Linux | EPEL | Red Hat Enterprise Linux 系向けの追加パッケージ提供元。 |
| Red Hat Enterprise Linux | RHEL | Red Hat 社が提供する商用 Linux ディストリビューション。 |
| BaseOS | - | RHEL 系の基本パッケージを提供するリポジトリ。 |
| AppStream | - | RHEL 系の追加パッケージを提供するリポジトリ。 |
| cloud-init | - | 起動時の初期設定を自動化する仕組み。 |
| Kickstart | - | 設定ファイルを用いて RHEL 導入手順を自動化する仕組み。 |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| Ansible Playbook | playbook | 自動化処理の実行手順を順序付きで記述したファイル。 |
| Uniform Resource Locator | URL | URL の正式名称。 |
| Secure Sockets Layer | SSL | 通信を暗号化する旧来方式の名称。現在は主に TLS を使用する。 |
| Hypertext Transfer Protocol | HTTP | HTTP の正式名称。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Transport Layer Security | TLS | 通信経路でデータを暗号化して保護する仕組み。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| Community Edition | CE | 商用版と区別する無償版の製品区分。 |
| CodeReady Builder | CRB | RHEL 系追加パッケージ提供リポジトリ。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `dnf` | - | RHEL 系でパッケージを導入, 更新, 削除するコマンド。 |
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |

## 概要
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

## 前提条件

- 対象ホストが inventory に登録済みであること
- 関連する共通変数が vars/all-config.yml または host_vars に定義済みであること

## 実行方法

制御ホストで以下のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts site.yml --tags "repo-rpm"
```

## 主要変数

主な制御変数は以下の通りで, `vars/all-config.yml` や `host_vars` から上書きできます:

| 変数 | 規定値 | 説明 |
| ---- | ------ | ---- |
| `repo_enable_base` | `true` | BaseOS ( 基本 OS パッケージ群 ) リポジトリの有効化可否。 |
| `repo_enable_appstream` | `true` | AppStream ( アプリケーションストリーム ) リポジトリの有効化可否。 |
| `repo_enable_crb` | `true` | CodeReady Builder ( 開発者向けパッケージ群 ) リポジトリの有効化可否。 |
| `repo_enable_epel` | `true` | EPEL ( Extra Packages for Enterprise Linux ) リポジトリの有効化可否。 |
| `repo_enable_kubernetes` | `true` | Kubernetes ( `pkgs.k8s.io` ) リポジトリの有効化可否。 |
| `repo_enable_chrome` | `true` | Google Chrome リポジトリの有効化可否。 |
| `repo_enable_docker_ce` | `true` | Docker CE ( Community Edition ) リポジトリの有効化可否。 |
| `repo_sslverify` | `true` | パッケージ取得時に TLS 証明書検証を行う設定の可否。内部ミラー等で自己署名証明書を利用する場合は `false` に変更します。 |
| `repo_gpgcheck` | `true` | パッケージ署名検証 ( GPG 署名による完全性確認 ) を行う設定の可否。 |
| `repo_repogpgcheck` | `true` | リポジトリメタデータ署名検証 ( repomd.xml の GPG 署名検証 ) を行う設定の可否。 |
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

## 実行フロー

1. [tasks/load-params.yml](tasks/load-params.yml) で OS 別パッケージ変数と共通変数を読み込みます。
2. [tasks/repositories.yml](tasks/repositories.yml) で EPEL 健全化処理と `dnf-plugins-core` 導入を実施し, ディストリビューション条件に応じて [tasks/redhat.yml](tasks/redhat.yml) または [tasks/alma_rocky.yml](tasks/alma_rocky.yml) を切り替えて主要リポジトリ設定を適用した後, [tasks/external.yml](tasks/external.yml) で外部リポジトリ設定を適用します。
3. [tasks/package.yml](tasks/package.yml), [tasks/directory.yml](tasks/directory.yml), [tasks/user_group.yml](tasks/user_group.yml), [tasks/service.yml](tasks/service.yml), [tasks/config.yml](tasks/config.yml) を順に実行し, 最後に検証コマンドで期待結果を確認します。

## 検証ポイント

実行者は以下の検証コマンドを実行し, 構文検査が成功することを確認します。

```bash
ansible-playbook -i inventory/hosts site.yml --syntax-check
```

期待結果: エラーが出力されず, syntax check が成功します。

## トラブルシューティング

実行者はエラー発生時に build-*.log を確認し, 失敗した task 名と不足変数を特定します。代表的なトラブルと対処を以下に示します。

| 想定トラブル | 主な原因 | 対処方法 |
| --- | --- | --- |
| RHEL で BaseOS/AppStream/CRB の有効化に失敗する | `subscription-manager` 未登録, または対象サブスクリプション未付与 | 実行者は対象ホストで `subscription-manager status` と `subscription-manager repos --list-enabled` を確認します。未登録の場合は登録とアタッチを実施し, `codeready-builder-for-rhel-<major>-<arch>-rpms` を有効化してから再実行します。 |
| AlmaLinux/Rocky で `dnf config-manager --set-enabled crb` に失敗する | `dnf-plugins-core` 未導入, CRB 名称不一致, ミラー到達不可 | 実行者は `dnf -y install dnf-plugins-core` を確認し, `dnf repolist all | grep -Ei 'crb|codeready'` で利用可能なリポジトリ名を確認します。必要に応じて `repo_enable_crb` を見直し, 再実行します。 |
| EPEL 設定後に `dnf makecache` が失敗する | 既存 `epel*.repo` の競合, `repo_gpgcheck` 強制設定, ネットワーク到達不可 | 実行者は `/etc/yum.repos.d/epel*.repo` の重複有無と `/etc/dnf/dnf.conf` の `repo_gpgcheck` 行を確認します。その後, `dnf clean all && dnf makecache` を実行して復旧可否を確認します。 |
| Kubernetes/Chrome/Docker CE の鍵取得に失敗する | 外部 URL 到達不可, HTTPS 経路不安定, プロキシ未設定 | 実行者は `curl -fsSL <鍵URL>` の単体実行で到達性を確認します。HTTPS 経路問題がある環境では URL プローブ結果により curl 回避処理へ自動切替されるため, `ansible_url_module_https_workaround_enabled` が `true` になっていることを確認します。 |
| Docker CE リポジトリが作成されない | 条件変数の不一致 (`repo_enable_docker_ce` と `repo_enable_docker`) | 本ロール既定値は `repo_enable_docker_ce: true` ですが, 外部リポジトリ処理では `repo_enable_docker` 条件も参照します。実行者は `vars/all-config.yml` または `host_vars` で `repo_enable_docker` の定義有無を確認し, 必要に応じて両方を整合させます。 |
| 優先度が意図どおりに反映されない | priority 値の上書き, 既存 `.repo` ファイル競合 | 実行者は `/etc/yum.repos.d/*.repo` を確認し, `priority_baseos: 1`, `priority_appstream: 2`, `priority_epel: 90`, `priority_kubernetes: 80`, `priority_docker_ce: 70` が反映されていることを確認します。競合定義を整理後に再実行します。 |

## 注意事項

### リポジトリの優先度制御仕様

本ロールでは, RPM パッケージ管理システムのリポジトリ優先度制御機能 ( RHEL/AlmaLinux/Rocky Linux では dnf-plugins-core の priority プラグインと呼ばれる ) を使用して, 同一パッケージが複数のリポジトリから導入可能な場合に使用するリポジトリの優先度を設定します。

本ロールでは, 以下の方針で優先度を設定しています:

 - 主要リポジトリ ( BaseOS/AppStream ) を高優先度に設定 (優先度の設定値を小さい数値 ( `priority_baseos`: 1, `priority_appstream`: 2 ) に設定)
 - 外部リポジトリを必要時のみ使用するよう低優先度に設定 (優先度の設定値を主要リポジトリより大きい数値 ( `priority_epel`: 90, `priority_kubernetes`: 80, `priority_docker_ce`: 70 ) に設定)

### 本ロールでの EPEL 健全化処理

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


## 参考資料

### 公式ドキュメント

- [createrepo_c](https://github.com/rpm-software-management/createrepo_c) RPMパッケージのリポジトリを生成するコマンド(createrepoコマンド)のGithubリポジトリ
- [DNF, the next-generation replacement for YUM](https://dnf.readthedocs.io/en/latest/) DNFの公式サイト

### DNF リポジトリ管理と優先度制御

RHEL/AlmaLinux/Rocky Linux のパッケージ管理システムで使用される DNF リポジトリ管理と優先度制御の詳細については, 以下を参照してください:

- [Red Hat Customer Portal - dnf.conf(5)](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/managing_software_with_the_dnf_tool/index) DNF の設定ファイル形式とリポジトリ優先度 ( priority ) の仕組みについて説明
- [Fedora Project - DNF System Upgrade](https://docs.fedoraproject.org/en-US/quick-docs/dnf/) DNF コマンドの基本的な使用方法とリポジトリ管理について説明
- [AlmaLinux Wiki - Package Management](https://wiki.almalinux.org/documentation/) AlmaLinux でのパッケージ管理とリポジトリ設定について説明
- [Rocky Linux Documentation](https://docs.rockylinux.org/) Rocky Linux でのパッケージ管理とリポジトリ設定について説明

### RHEL/AlmaLinux/Rocky Linux リポジトリシステムの用語

このロール内で使用される RHEL/AlmaLinux/Rocky Linux 固有の用語の意味は以下の通りです:

- BaseOS: Red Hat Enterprise Linux およびその互換ディストリビューションにおける基本 OS パッケージ群のリポジトリ。カーネル, 基本システムツール, ライブラリなどを含む
- AppStream: アプリケーションストリームリポジトリ。複数バージョンのアプリケーション, ランタイム, 開発ツールを提供。モジュール形式でバージョン管理される
- CodeReady Builder (CRB) / CodeReady Linux Builder: 開発者向けのパッケージ群を提供するリポジトリ。ヘッダファイル, 開発ライブラリなど。RHEL では CodeReady Builder, AlmaLinux/Rocky では CodeReady Linux Builder と呼ばれる
- EPEL (Extra Packages for Enterprise Linux): Fedora Project が提供する, Enterprise Linux 向けの追加パッケージ群。RHEL 標準リポジトリに含まれない便利なツールやライブラリを提供
- Priority: DNF パッケージマネージャにおけるリポジトリ優先度制御機能。`dnf-plugins-core` パッケージの priority プラグインで実装される。数値が小さいほど優先度が高く, 同じパッケージが複数のリポジトリにある場合, priority 値が小さいリポジトリから優先的にインストールされる
- gpgcheck: RPM パッケージの GPG 署名検証機能。パッケージが改ざんされていないことを確認する
- repo_gpgcheck: リポジトリメタデータ ( `repomd.xml` ) の GPG 署名検証機能。リポジトリ自体が改ざんされていないことを確認する
- metalink / mirrorlist: 複数のミラーサーバーリストを提供する仕組み。固定 URL ( baseurl ) ではなく metalink を使用することで, 障害時の耐性向上と負荷分散が可能になる

詳細は以下を参照ください:

- [Red Hat Documentation - Managing software with the DNF tool](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/managing_software_with_the_dnf_tool/index) RHEL のパッケージ管理システム全般について
- [Fedora Project - EPEL](https://docs.fedoraproject.org/en-US/epel/) EPEL の概要と使用方法について
