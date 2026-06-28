# frr-common ロール

このロールは Free Range Routing (FRR) の導入処理を共通化し, `frr-basic` と `k8s-worker-frr` から `include_role` で呼び出して使うためのロールである。

- [frr-common ロール](#frr-common-ロール)
  - [用語](#用語)
  - [本ロールの動作仕様](#本ロールの動作仕様)
  - [主要変数](#主要変数)
  - [本ロールでの処理内容](#本ロールでの処理内容)
    - [パッケージ構築関連ファイル一覧](#パッケージ構築関連ファイル一覧)
    - [パッケージ構築～導入までの流れ](#パッケージ構築導入までの流れ)
    - [導入版数確認方針](#導入版数確認方針)
  - [注意事項](#注意事項)
  - [検証ポイント](#検証ポイント)
    - [Debian/Ubuntuパッケージの場合の確認方法](#debianubuntuパッケージの場合の確認方法)
    - [RHEL/Alma Linux (RPMパッケージ)の場合の確認方法](#rhelalma-linux-rpmパッケージの場合の確認方法)

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Free Range Routing | FRR | BGP, OSPF, RIP などの動的ルーティングプロトコルを実装したオープンソースのルーティングソフトウェア。Quagga の後継プロジェクト。 |
| Border Gateway Protocol | BGP | インターネット上の自律システム間でルーティング情報を交換するための外部ゲートウェイプロトコル。経路制御の標準プロトコル。 |
| Autonomous System Number | ASN | インターネット上で各組織や管理ドメインを識別するために割り当てられる一意の番号。BGP でルーティング情報を交換する際の識別子として使用される。 |
| Internal BGP | iBGP | 同一自律システム内の BGP ルータ間で経路情報を交換するための BGP の動作モード。AS 番号が同じルータ間で使用される。 |
| External BGP | eBGP | 異なる自律システム間で経路情報を交換するための BGP の動作モード。AS 番号が異なるルータ間で使用される。 |

## 本ロールの動作仕様

本ロールの役割, 動作仕様は以下の通り:

- `frr_version` が空文字または未定義: ディストリビューション標準の FRR パッケージを導入。
- `frr_version` が指定されている場合: 指定版数の FRR をソースを導入対象ディストリビューション環境を内包するコンテナ内でビルドし, ローカル成果物 (deb/rpm) を対象ホストへ直接配布して導入。
- 指定版数とビルド結果, さらに導入後の版数が一致しない場合は `fail` で停止。

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
| `frr_build_output_dir` | 構築ノード側の成果物出力先。 | `"{{ frr_build_workspace }}/output"` |
| `frr_source_git_url` | FRR ソース取得先。 | `"https://github.com/FRRouting/frr.git"` |
| `frr_source_git_ref_prefix` | Git checkout 時の版数プレフィックス。 | `"frr-"` |
| `frr_libyang_git_url` | Ubuntu 24.04向けlibyangのソース取得先。 | `"https://github.com/CESNET/libyang.git"` |
| `frr_libyang_version` | Ubuntu 24.04向けに先行導入するlibyang版数。 | `"2.1.148"` |
| `frr_libyang_git_ref_prefix` | libyangのGitタグ接頭辞。 | `"v"` |

## 本ロールでの処理内容

本ロールは, パッケージ構築からパッケージ導入までを実施する:

1. `frr_version` が空/未定義時は `frr_packages`変数で指定されたOSディストリビューション標準のパッケージを導入する。
2. `frr_version` 指定時は OS ごとにパッケージ構築処理, パッケージ導入処理を順次実行する。

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


### パッケージ構築～導入までの流れ

1. 構築ホスト上にFRRをビルドするためのディレクトリを作成する
2. 構築ホスト上にFRR パッケージ構築用のコンテナ環境をDockerfileから生成する
3. FRRパッケージ構築用コンテナ環境の生成が構築ホスト上で完了することを待機する
4. FRRパッケージを構築ホスト上のコンテナ内で構築する
5. FRRパッケージ構築が構築ホスト上で完了することを待ち合わせる
6. FRRパッケージの構築に失敗, または, 生成されたパッケージの版数が`frr_version`で指定された版数と異なる場合は, 処理を中断してplaybookの動作を停止する。
7. 生成したFRRパッケージを構築ホストから制御ホストに転送する
8. 生成したFRRパッケージを制御ホストからパッケージ導入先ホストに転送する
9. 生成したFRRパッケージをパッケージ導入先ホストに導入する
10. 導入されたパッケージの版数が`frr_version`で指定された版数と異なる場合は, 処理を中断してplaybookの動作を停止する。

### 導入版数確認方針

`frr_version`変数により, 導入版数を明示的に指定した場合, 本ロールは以下の内容を確認し, どれか 1 つでも不一致なら, ロールを失敗で停止させる:

1. 指定版数タグからソース取得に成功すること。
2. 生成されたパッケージ版数が指定版数と一致すること。
3. 導入後にホスト上で取得した版数が指定版数と一致すること。

## 注意事項

- ソースビルドは制御ノード上でコンテナランタイム(Docker)が利用可能であることを前提とする。
- 構築したパッケージに対する署名付与は行わない。

## 検証ポイント

- `dpkg-query` または `rpm -q` の結果が指定版数と一致すること。

### Debian/Ubuntuパッケージの場合の確認方法

以下のコマンドを実行し, 各パッケージの版数が, `frr_version`で指定された版数と一致することを確認する。

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

以下のコマンドを実行し, 各パッケージの版数(`Version:`)が, `frr_version`で指定された版数と一致することを確認する。

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