# frr-common ロール

本ロールは Free Range Routing (FRR) の導入処理を共通化し, `frr-basic` と `k8s-worker-frr` から `include_role` で呼び出して使うためのロールです。

## 目次
- [frr-common ロール](#frr-common-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [本ロールの動作仕様](#本ロールの動作仕様)
  - [本ロールでの処理内容](#本ロールでの処理内容)
    - [パッケージ構築～導入までの流れ](#パッケージ構築導入までの流れ)
    - [導入版数確認方針](#導入版数確認方針)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
    - [パッケージ構築関連ファイル一覧](#パッケージ構築関連ファイル一覧)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [Debian/Ubuntuパッケージの場合の確認方法](#debianubuntuパッケージの場合の確認方法)
    - [RHEL/Alma Linux (RPMパッケージ)の場合の確認方法](#rhelalma-linux-rpmパッケージの場合の確認方法)
  - [トラブルシューティング](#トラブルシューティング)
  - [注意事項](#注意事項)
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
| Internet Protocol | IP | インターネットプロトコルの略称。 |
| Structured Query Language | SQL | データベースを操作するための記述言語。 |
| Hypertext Transfer Protocol | HTTP | WWW で情報をやり取りする通信手順。 |
| Hypertext Transfer Protocol Secure | HTTPS | 通信内容を暗号化して WWW 通信を行う方式。 |
| RPM Package Manager | RPM | RHEL 系で使用するパッケージ形式。 |
| Virtual Machine | VM | 物理機器上で動作する仮想的な計算機。 |
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
| Application Programming Interface | API | アプリケーション同士がやり取りする方法を定めた仕様。 |
| Uniform Resource Locator | URL | WWW 上の資源の場所を示す文字列。 |
| Free Range Routing | FRR | 複数の経路制御方式を実装したオープンソースの経路制御ソフトウェア。 |
| Border Gateway Protocol | BGP | 自律システム間で経路情報を交換する経路制御方式。 |
| Autonomous System Number | ASN | インターネット上で各組織や管理ドメインを識別するために割り当てられる一意の番号。BGP でルーティング情報を交換する際の識別子として使用される。 |
| Internal BGP | iBGP | 同一自律システム内の BGP ルータ間で経路情報を交換するための BGP の動作モード。AS 番号が同じルータ間で使用される。 |
| External BGP | eBGP | 異なる自律システム間で経路情報を交換するための BGP の動作モード。AS 番号が異なるルータ間で使用される。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Red Hat Enterprise Linux | RHEL | Red Hat 社が提供する商用 Linux ディストリビューション。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| rpmコマンド | - | RPM パッケージの情報参照や導入確認を行うコマンド。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| ローカル | - | 実行中の装置や同一環境の内部。 |
| ローカルパッケージ | - | 外部配布元ではなく, 手元環境で作成または保管した導入用パッケージ。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| 構築ホスト | - | パッケージや実行資材を生成するビルド処理を担当するホスト。 |

## 概要
このロールは Free Range Routing (FRR) の導入処理を共通化し, `frr-basic` と `k8s-worker-frr` から `include_role` で呼び出して使うためのロールです。

## 本ロールの動作仕様

本ロールの役割, 動作仕様は以下の通り:

- `frr_version` が空文字または未定義: ディストリビューション標準の FRR パッケージを導入。
- `frr_version` が指定されている場合: 指定版数の FRR をソースを導入対象ディストリビューション環境を内包するコンテナ内でビルドし, ローカル成果物 (deb/rpm) を対象ホストへ直接配布して導入。
- 指定版数とビルド結果, さらに導入後の版数が一致しない場合は `fail` で停止。

## 本ロールでの処理内容

本ロールは, パッケージ構築からパッケージ導入までを実施します:

1. `frr_version` が空/未定義時は `frr_packages`変数で指定されたOSディストリビューション標準のパッケージを導入します。
2. `frr_version` 指定時は OS ごとにパッケージ構築処理, パッケージ導入処理を順次実行します。

### パッケージ構築～導入までの流れ

1. 構築ホスト上にFRRをビルドするためのディレクトリを作成する
2. 構築ホスト上にFRR パッケージ構築用のコンテナ環境をDockerfileから生成する
3. FRRパッケージ構築用コンテナ環境の生成が構築ホスト上で完了することを待機する
4. FRRパッケージを構築ホスト上のコンテナ内で構築する
5. FRRパッケージ構築が構築ホスト上で完了することを待ち合わせる
6. FRRパッケージの構築に失敗, または, 生成されたパッケージの版数が`frr_version`で指定された版数と異なる場合は, 処理を中断してplaybookの動作を停止します。
7. 生成したFRRパッケージを構築ホストから制御ホストに転送する
8. 生成したFRRパッケージを制御ホストからパッケージ導入先ホストに転送する
9. 生成したFRRパッケージをパッケージ導入先ホストに導入する
10. 導入されたパッケージの版数が`frr_version`で指定された版数と異なる場合は, 処理を中断してplaybookの動作を停止します。

### 導入版数確認方針

`frr_version`変数により, 導入版数を明示的に指定した場合, 本ロールは以下の内容を確認し, どれか 1 つでも不一致なら, ロールを失敗で停止させる:

1. 指定版数タグからソース取得に成功すること。
2. 生成されたパッケージ版数が指定版数と一致すること。
3. 導入後にホスト上で取得した版数が指定版数と一致すること。

## 前提条件

- 対象ホストが inventory に登録済みであること
- 関連する共通変数が vars/all-config.yml または host_vars に定義済みであること

## 実行方法

本ロールは `frr-basic` または `k8s-worker-frr` から `include_role` で呼び出される内部ロールであるため, 原則として単体実行しません。
実行者は制御ホストで呼び出し元ロールのタグを指定して実行します。

FRR 専用ノード向け (`frr.yml`) の例:

```bash
ansible-playbook -i inventory/hosts frr.yml --tags "frr-basic"
```

Kubernetes ワーカーノード向け (`k8s-worker.yml`) の例:

```bash
ansible-playbook -i inventory/hosts k8s-worker.yml --tags "k8s-worker-frr"
```

## 主要変数

本ロールの動作パラメタとなる変数を以下に示す。

| 変数名 | 意味 | 規定値 |
| --- | --- | --- |
| `frr_version` | 導入する FRR 版数。空/未定義時はOSディストリビューション標準パッケージを導入。 設定する場合は, `frr-basic`, `k8s-worker-frr`ロールから参照可能とするため, `vars/all-config.yml`で定義することを推奨。| `""` |
| `frr_build_container_runtime` | ソースビルドに使用するコンテナランタイム。 | `"docker"` |
| `frr_build_host` | ソースビルドを実行するホスト。 | `"localhost"` |
| `frr_build_timeout_seconds` | ソースビルド処理全体の最大待機時間(秒)。 | `7200` |
| `frr_build_loop_delay_seconds` | 非同期ジョブ監視時のポーリング間隔(秒)。 | `5` |
| `frr_install_deb_lock_wait_seconds` | Debian系でdpkgロック解放を待つ最大時間(秒)。 | `3600` |
| `frr_build_container_network_mode` | ソースビルド用コンテナのネットワークモード。 | `"host"` |
| `frr_build_container_image_debian` | Debian 系ビルドに使うコンテナイメージ。 | `"ubuntu:24.04"` |
| `frr_build_container_image_rhel` | RHEL 系ビルドに使うコンテナイメージ。 | `"almalinux:9.6"` |
| `frr_build_workspace` | 構築ノード側のビルド作業ディレクトリ。 | `"/tmp/frr-build"` |
| `frr_build_output_dir` | 構築ノード側の成果物出力先。 | `"/tmp/frr-build/output"` |
| `frr_source_git_url` | FRR ソース取得先。 | `"https://github.com/FRRouting/frr.git"` |
| `frr_source_git_ref_prefix` | Git checkout 時の版数プレフィックス。 | `"frr-"` |
| `frr_libyang_git_url` | Ubuntu 24.04向けlibyangのソース取得先。 | `"https://github.com/CESNET/libyang.git"` |
| `frr_libyang_version` | Ubuntu 24.04向けに先行導入するlibyang版数。 | `"2.1.148"` |
| `frr_libyang_git_ref_prefix` | libyangのGitタグ接頭辞。 | `"v"` |

### パッケージ構築関連ファイル一覧

パッケージ構築処理, パッケージ導入処理に関連するファイルは以下の通り:

|ロール内での相対パス|処理内容|
|---|---|
|tasks/package.yml|FRRパッケージ導入メイン処理タスク群の定義(OSディストリビューション標準パッケージからの導入, Ubuntu/Debian/RHEL(Alma Linux)用パッケージ構築・導入処理タスクの呼び出し|
|tasks/build-source-deb.yml|Ubuntu/Debian用debパッケージ構築処理タスク群の定義|
|tasks/build-source-rpm.yml|RHEL用rpmパッケージ構築処理タスク群の定義|
|tasks/install-local-deb.yml|Ubuntu/Debian用debパッケージインストール処理タスク群の定義|
|tasks/install-local-rpm.yml|RHEL用rpmパッケージインストール処理タスク群の定義|
|templates/build-frr-deb.sh.j2|コンテナ内で実行されるUbuntu/Debian用debパッケージ構築用シェルスクリプト。|
|templates/build-frr-rpm.sh.j2|コンテナ内で実行されるRHEL用rpmパッケージ構築用シェルスクリプト|
|templates/install-libyang.sh.j2|frr-10系で必要となるlibyangのUbuntu/Debian用debパッケージ構築用を構築するシェルスクリプト|
|templates/install-libyang-dev.control.j2|frr-10系で必要となるlibyang開発関連ファイルのUbuntu/Debian用debパッケージ構築用controlファイル|
|templates/install-libyang-runtime.control.j2|frr-10系で必要となるlibyangのUbuntu/Debian用debパッケージ構築用controlファイル|
|templates/Dockerfile.almalinux.j2|RHEL(AlmaLinux9.6)用rpmパッケージ構築に使用するコンテナ環境作成用Dockerfile生成テンプレート|
|templates/Dockerfile.ubuntu.j2|Ubuntu/Debian(Ubuntu24.04)用debパッケージ構築に使用するコンテナ環境作成用Dockerfile生成テンプレート|

## テンプレートと生成ファイル

本ロールでは以下のテンプレート / ファイルを出力します:
主な展開先ホストは, 構築ホスト です。

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `Dockerfile.ubuntu.j2` | `/tmp/frr-build/Dockerfile.frr-deb` | ローカルパッケージを再現可能にビルドするためのコンテナイメージ定義です。 |
| `build-frr-deb.sh.j2` | `/tmp/frr-build/build-frr-deb.sh` | 対象ソフトウェアをソースからビルドし, ローカルパッケージを生成する実行スクリプトです。 |
| `Dockerfile.almalinux.j2` | `/tmp/frr-build/Dockerfile.frr-rpm` | ローカルパッケージを再現可能にビルドするためのコンテナイメージ定義です。 |
| `build-frr-rpm.sh.j2` | `/tmp/frr-build/build-frr-rpm.sh` | 対象ソフトウェアをソースからビルドし, ローカルパッケージを生成する実行スクリプトです。 |

## 実行フロー

本ロールは以下の順序で処理を実行します。

1. `load-params.yml` を実行し, OS種別ごとのパッケージ変数, 共通変数, Kubernetes API 広告アドレス変数を読み込みます。
2. `package.yml` を実行し, `frr_version` が空文字または未定義の場合はディストリビューション標準の FRR パッケージを導入します。Debian 系では libyang シンボル検査と必要時の修復処理を実行します。
3. `package.yml` 内で `frr_version` が指定されている場合は, OSファミリ別ターゲットを算出し, 構築ワークスペース準備, build スクリプト生成, Debian 系または RHEL 系のコンテナイメージ構築, `pkgbld-common` を介したローカルパッケージ生成/配布/導入, 版数一致検証を実行します。
4. `frr_version` が指定され, かつ OS ファミリが Debian/RedHat 以外の場合は, サポート対象外として明示的に処理を停止します。

## 検証ポイント

- `dpkg-query` または `rpm -q` の結果が指定版数と一致すること。

### Debian/Ubuntuパッケージの場合の確認方法

以下のコマンドを実行し, 各パッケージの版数が, `frr_version`で指定された版数と一致することを確認します。

```shell
dpkg-query -l|grep frr
```

実行例を以下に示す:

```shell
$ dpkg-query -l|grep frr
ii  frr                                   10.4.1-0                                amd64        FRRouting suite of internet protocols (BGP, OSPF, IS-IS, ...)
ii  frr-doc                               10.4.1-0                                all          FRRouting suite - user manual
ii  frr-pythontools                       10.4.1-0                                all          FRRouting suite - Python tools
ii  frr-rpki-rtrlib                       10.4.1-0                                amd64        FRRouting suite - BGP RPKI support (rtrlib)
ii  frr-snmp                              10.4.1-0                                amd64        FRRouting suite - SNMP support
ii  frr-test-tools                        10.4.1-0                                amd64        FRRouting suite - Testing Tools
```

### RHEL/Alma Linux (RPMパッケージ)の場合の確認方法

以下のコマンドを実行し, 各パッケージの版数(`Version:`)が, `frr_version`で指定された版数と一致することを確認します。

```shell
rpm -qi frr frr-contrib frr-devel frr-pythontools frr-snmp
```

実行例を以下に示す:

```
$ rpm -qi frr frr-contrib frr-devel frr-pythontools frr-snmp
Name        : frr
Version     : 10.4.1
Release     : 01.el9
Architecture: x86_64
Install Date: Mon 22 Jun 2026 01:28:05 PM JST
Group       : System Environment/Daemons
Size        : 38342049
License     : GPLv2+
Signature   : (none)
Source RPM  : frr-10.4.1-01.el9.src.rpm
Build Date  : Mon 22 Jun 2026 01:24:24 PM JST
Build Host  : localhost
URL         : https://www.frrouting.org
Summary     : Routing daemon
Description :
FRRouting is a free software that manages TCP/IP based routing
protocol. It takes multi-server and multi-thread approach to resolve
the current complexity of the Internet.

FRRouting supports BGP4, OSPFv2, OSPFv3, ISIS, RIP, RIPng, PIM, LDP
NHRP, Babel, PBR, EIGRP and BFD.

FRRouting is a fork of Quagga.
Name        : frr-contrib
Version     : 10.4.1
Release     : 01.el9
Architecture: x86_64
Install Date: Mon 22 Jun 2026 01:28:06 PM JST
Group       : System Environment/Daemons
Size        : 1753472
License     : GPLv2+
Signature   : (none)
Source RPM  : frr-10.4.1-01.el9.src.rpm
Build Date  : Mon 22 Jun 2026 01:24:24 PM JST
Build Host  : localhost
URL         : https://www.frrouting.org
Summary     : contrib tools for frr
Description :
Contributed/3rd party tools which may be of use with frr.
Name        : frr-devel
Version     : 10.4.1
Release     : 01.el9
Architecture: x86_64
Install Date: Mon 22 Jun 2026 01:28:05 PM JST
Group       : System Environment/Daemons
Size        : 1214899
License     : GPLv2+
Signature   : (none)
Source RPM  : frr-10.4.1-01.el9.src.rpm
Build Date  : Mon 22 Jun 2026 01:24:24 PM JST
Build Host  : localhost
URL         : https://www.frrouting.org
Summary     : Header and object files for frr development
Description :
The frr-devel package contains the header and object files necessary for
developing OSPF-API and frr applications.
Name        : frr-pythontools
Version     : 10.4.1
Release     : 01.el9
Architecture: x86_64
Install Date: Mon 22 Jun 2026 01:28:06 PM JST
Group       : System Environment/Daemons
Size        : 274182
License     : GPLv2+
Signature   : (none)
Source RPM  : frr-10.4.1-01.el9.src.rpm
Build Date  : Mon 22 Jun 2026 01:24:24 PM JST
Build Host  : localhost
URL         : https://www.frrouting.org
Summary     : python tools for frr
Description :
Contributed python 2.7 tools which may be of use with frr.
Name        : frr-snmp
Version     : 10.4.1
Release     : 01.el9
Architecture: x86_64
Install Date: Mon 22 Jun 2026 01:28:05 PM JST
Group       : System Environment/Daemons
Size        : 949222
License     : GPLv2+
Signature   : (none)
Source RPM  : frr-10.4.1-01.el9.src.rpm
Build Date  : Mon 22 Jun 2026 01:24:24 PM JST
Build Host  : localhost
URL         : https://www.frrouting.org
Summary     : SNMP support
Description :
Adds SNMP support to FRR's daemons by attaching to net-snmp's snmpd
through the AgentX protocol.  Provides read-only access to current
routing state through standard SNMP MIBs.
```

## トラブルシューティング

代表的なトラブルと対処を以下に示します。

| 想定トラブル | 主な原因 | 対処方法 |
| --- | --- | --- |
| FRR が導入されない | `frr-common` は内部ロールであり, `--tags "frr-common"` では実行対象にならない | 実行者は呼び出し元ロールのタグを指定します。FRR ノードは `--tags "frr-basic"`, Kubernetes ワーカーノードは `--tags "k8s-worker-frr"` を指定して再実行します。 |
| `Strict FRR source build is supported only on Debian and RedHat families` で停止する | `frr_version` を指定しているが, 対象ホストの OS ファミリが Debian/RedHat 以外である | 実行者は OS ファミリを確認し, 対応 OS へ切り替えるか `frr_version` を空文字にしてディストリビューション標準パッケージ導入へ切り替えます。 |
| コンテナイメージ構築またはパッケージ構築で失敗する | 構築ホストでコンテナランタイム未導入, イメージ取得失敗, ネットワーク制限, または待機時間超過 | 実行者は構築ホストで `docker --version` と `ubuntu:24.04` / `almalinux:9.6` の取得可否を確認します。必要に応じて `frr_build_timeout_seconds` を延長し, `build-*.log` で停止箇所を確認して再実行します。 |
| `Installed libyang still misses ... lyd_parent symbol` で停止する | Debian 系で FRR 実行時に必要な libyang シンボルが不足し, 再構築後も改善しない | 実行者は対象ホストの `libyang2` 関連パッケージ競合を解消し, 再実行します。必要に応じて既存の libyang 関連パッケージ状態を整理してから FRR 導入を再試行します。 |
| 版数検証で失敗する (`Built FRR ... version mismatch`) | 指定した `frr_version` と生成パッケージ版数, または導入後版数が一致しない | 実行者は `frr_version` の値と, 構築成果物の版数, 導入後の `dpkg-query` または `rpm -q --qf '%{VERSION}' frr` の結果を突き合わせて不一致原因を解消して再実行します。 |
| Debian/Ubuntu 系でロック待ち関連の失敗が発生する | 他プロセスの `apt`/`dpkg` 処理が継続し, ロック待機時間を超過する | 実行者は対象ホストで競合するパッケージ処理を停止し, 必要に応じて `frr_install_deb_lock_wait_seconds` を延長して再実行します。 |

## 注意事項

- ソースビルドは制御ノード上でコンテナランタイム(Docker)が利用可能であることを前提とします。
- 構築したパッケージに対する署名付与は行いません。

## 参考資料

### 公式ドキュメント

- [FRRouting](https://docs.frrouting.org/en/latest/)
