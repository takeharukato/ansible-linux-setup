# pkgbld-common ロール

本ロールは, ディストリビューション用パッケージ構築から導入までの処理をロール間で共通化して使用可能にするためのロールです。

## 目次

- [pkgbld-common ロール](#pkgbld-common-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [本ロールの動作仕様](#本ロールの動作仕様)
  - [呼び出し元ロールからの使用方法](#呼び出し元ロールからの使用方法)
    - [呼び出し元ロール作成者が実施する作業](#呼び出し元ロール作成者が実施する作業)
    - [呼び出し元ロールでのパラメタの設定手順](#呼び出し元ロールでのパラメタの設定手順)
    - [呼び出し元ロールから本ロールを呼び出すansibleタスクの記載方法](#呼び出し元ロールから本ロールを呼び出すansibleタスクの記載方法)
    - [各パラメタ変数に設定する値](#各パラメタ変数に設定する値)
      - [パッケージ作成用コンテナの実行方式に指定可能な値](#パッケージ作成用コンテナの実行方式に指定可能な値)
      - [ネットワーク共有方式に指定可能な値](#ネットワーク共有方式に指定可能な値)
    - [go-lang-local ロールでの設定パラメタの例](#go-lang-local-ロールでの設定パラメタの例)
      - [Debian/Ubuntuホスト用の呼び出し例](#debianubuntuホスト用の呼び出し例)
      - [RHEL(AlmaLinuxなど)ホスト用の呼び出し例](#rhelalmalinuxなどホスト用の呼び出し例)
  - [検証項目](#検証項目)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [検証の前提条件](#検証の前提条件)
    - [検証環境の設定](#検証環境の設定)
    - [検証コマンドと期待結果](#検証コマンドと期待結果)
      - [1. Playbook 実行結果の確認](#1-playbook-実行結果の確認)
      - [2. 構築ホスト上の成果物生成確認](#2-構築ホスト上の成果物生成確認)
      - [3. 導入対象ホスト上の導入状態確認](#3-導入対象ホスト上の導入状態確認)
      - [4. 版数照合結果の確認](#4-版数照合結果の確認)
    - [異常時の確認項目](#異常時の確認項目)
      - [1. 必須変数不足による停止確認](#1-必須変数不足による停止確認)
      - [2. 成果物探索失敗時の確認](#2-成果物探索失敗時の確認)
      - [3. Red Hat 系導入前互換パス確認](#3-red-hat-系導入前互換パス確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. 必須変数不足で停止する場合](#1-必須変数不足で停止する場合)
    - [2. 成果物作成用シェルスクリプトが見つからない場合](#2-成果物作成用シェルスクリプトが見つからない場合)
    - [3. パッケージ成果物が見つからない場合](#3-パッケージ成果物が見つからない場合)
    - [4. 成果物回収で失敗する場合](#4-成果物回収で失敗する場合)
    - [5. Debian系統で待機時間を超過する場合](#5-debian系統で待機時間を超過する場合)
    - [6. Red Hat系統で chkconfig 導入時に失敗する場合](#6-red-hat系統で-chkconfig-導入時に失敗する場合)
    - [7. Red Hat系統で署名検証に失敗する場合](#7-red-hat系統で署名検証に失敗する場合)
    - [8. 版数照合で不一致になる場合](#8-版数照合で不一致になる場合)
  - [注意事項](#注意事項)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)

## 用語

この節では, 本文で使用する用語を定義します。

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
| Internet Protocol | IP | ネットワーク上で宛先を識別し, データを届けるための通信手順。 |
| Structured Query Language | SQL | データベースを操作するための記述言語。 |
| Hypertext Transfer Protocol | HTTP | World Wide Webで情報をやり取りする通信手順。 |
| Hypertext Transfer Protocol Secure | HTTPS | 通信内容を暗号化してWorld Wide Web通信を行う方式。 |
| RPM Package Manager | RPM | RPM形式パッケージの導入, 更新, 削除, 情報参照を行う仕組み。 |
| Virtual Machine | VM | 物理計算機上で動作する仮想的な計算機。 |
| localhost | - | 同一機器自身を指す名前。 |
| root | - | Unix 系システムの最上位権限を持つ管理者識別子。 |
| ソフトウェア | - | 情報処理システムで使用するプログラム, 手順, 規則及び関連文書の全体又は一部分。 |
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| アプリケーション | - | 利用者の目的を実現するために動作するソフトウェア。 |
| リポジトリ | - | ソフトウェアや設定情報を保管し, 取得できるようにした管理場所。 |
| コマンド | - | 実行者が計算機へ処理を指示するための命令。 |
| ホスト | - | 管理対象として識別される個別の計算機。 |
| サーバ | - | 他の機器や利用者へ機能やデータを提供する計算機, 又はその役割。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| ネットワーク | - | 機器同士を接続してデータをやり取りする仕組み。 |
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
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| ロール | - | Ansible における処理のまとまり。 |
| 変数 | - | 実行時に値を切り替えるための設定項目。 |
| 実行メッセージ | - | 実行中または失敗時に表示される文字列。 |
| 変数分類 | - | 同じ目的の変数をまとめた区分。 |
| 構築ホスト | - | パッケージや実行資材を生成するビルド処理を担当するホスト。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 導入対象ホスト | - | 生成した deb/rpm を導入するホスト。 |
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
| パッケージ | - | ソフトウェア導入に必要なファイルをまとめた配布単位。 |
| `.deb` | - | Debian系統で使うパッケージファイルの拡張子。 |
| `.rpm` | - | Red Hat系統で使うパッケージファイルの拡張子。 |
| パッケージ成果物 | - | パッケージ作成処理の結果として出力された .deb / .rpm ファイル。 |
| Debian系統 | - | Debian や Ubuntu のように apt/dpkg を使う系統のOSディストリビューション。 |
| Red Hat系統 | - | RHEL や AlmaLinux のように dnf/rpm を使う系統のOSディストリビューション。 |
| `apt` | - | Debian 系でパッケージを導入, 更新, 削除するコマンド。 |
| `dpkg` | - | Debian パッケージの情報参照や導入確認を行うコマンド。 |
| rpmコマンド | - | RPM パッケージの情報参照や導入確認を行うコマンド。 |
| `dnf` | - | RHEL 系でパッケージを導入, 更新, 削除するコマンド。 |
| パッケージ作成用コンテナイメージ | - | パッケージ作成処理で使うコンテナイメージ。 |
| 成果物作成用シェルスクリプト | - | パッケージ作成を実行するシェルスクリプト。 |
| テンプレート | - | 値を埋め込んで生成するためのひな型ファイル。 |
| コンテナ実行方式 | - | `pkgbld_container_runtime` に設定する実行コマンド。現在は `docker` を想定します。 |
| ネットワーク共有方式 | - | `pkgbld_container_network_mode` に設定するネットワーク方式。`host` はホスト側ネットワークを共有する設定値。 |
| 版数抽出式 | - | コマンド出力から版数文字列を取り出すための正規表現。 |
| 環境変数引数 | - | コンテナに対して環境変数経由で引き渡すパラメタを`docker`コマンドのオプション形式(`-e KEY=VALUE` 形式)で表記した引数パラメタ。 |
| 期待版数 | - | 版数照合で一致を期待する版数文字列。 |
| 付加版番号 | - | Debianパッケージで版数の末尾に付く `-1` などの追記部分。 |
| 署名検証 | - | パッケージに付与された署名を導入時に確認する処理。 |
| 排他制御待機 | - | パッケージ管理コマンドの同時実行を避けるための待ち合わせ処理のこと。 |
| GNU Privacy Guard | GPG | 公開鍵暗号方式でデータを保護するためのソフトウェア。 |
| Red Hat Enterprise Linux | RHEL | Red Hatが提供する企業向けLinuxディストリビューション。 |
| RPM Package Manager | RPM | RPM形式パッケージの導入, 更新, 削除, 情報参照を行う仕組み。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `docker` | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |

## 概要

本ロールでは, 以下の機能を実現するための他のロールから呼び出し可能なロールを定義する:

1. deb/rpm 形式のパッケージを構築ホスト上のコンテナ環境で作成
2. 作成されたパッケージをAnsible 制御ホストにダウンロード
3. Ansible 制御ホストから導入先ホストへのパッケージの配布
4. 導入先ホストでのパッケージの導入(インストール)
5. 導入先ホストでのパッケージの検証

本ロールは, pkgbld-common に関する設定処理を実施します。

## 本ロールの動作仕様

- 呼び出し元から受け取った入力パラメタに基づき, 本ロールはパッケージ作成処理を構築ホストで実行します。
- 本ロールは, 呼び出し元が準備した成果物作成用シェルスクリプトとパッケージ作成用コンテナイメージを利用し, それらの新規作成処理は実行しない。
- `pkgbld_builder_image_debian` と `pkgbld_builder_image_rhel` には, Dockerfile のパスではなく, 実行時に指定するコンテナイメージ名(例: `example-build-ubuntu:24.04`)を設定します。
- 本ロールは, 指定されたコンテナイメージ名を `docker run` などのコンテナ実行コマンドへ渡して利用します。コンテナイメージの作成処理やコンテナイメージの読み込み処理は本ロールでは実行しない。
- 本ロールは, 成果物探索パラメタを使ってパッケージ成果物を特定し, そのパッケージ成果物を構築ホストから制御ホストへ回収します。
- 本ロールは, 配布/導入パラメタを使ってパッケージ成果物を制御ホストから play の実行対象ホストへ配布し, OS系統に応じた導入コマンドでそのパッケージ成果物を導入します。
- Red Hat系統への導入時は, `chkconfig` 導入時の `cpio` 展開失敗を防ぐため, `dnf` 実行前に `/etc/init.d` を互換 symlink (`/etc/rc.d/init.d` へのリンク) へ正規化します。
- 本ロールは, 検証パラメタを使って導入済み状態と版数照合結果を検証します。

## 呼び出し元ロールからの使用方法

本節では, 呼び出し元ロール作成者が 本ロール を利用する際の使用法について述べる。

### 呼び出し元ロール作成者が実施する作業

呼び出し元ロール作成者が 本ロール を利用する際に設定する変数と設定値の概要は以下の通り:

1. 構築実行に必要な値として以下の変数を設定する:
   1. `package_build_host` : 構築ホスト(パッケージ構築に使用するホスト)のホスト名, または, IPアドレス
   2. `package_build_workspace` : パッケージ構築作業を行う際に使用する作業ディレクトリの構築ホスト上でのパス名
   3. `package_build_output_dir` : 生成されたパッケージを配置するディレクトリの構築ホスト上でのパス名
2. コンテナ実行条件として以下の変数を設定する:
  1. `pkgbld_container_runtime` : コンテナ実行コマンド名(`docker`など)
  2. `pkgbld_container_network_mode` : コンテナ実行時のネットワーク共有方式(`host`など)
  3. `pkgbld_builder_image_debian` : Debian系統向けパッケージ作成用コンテナイメージ名
  4. `pkgbld_builder_image_rhel` : Red Hat系統向けパッケージ作成用コンテナイメージ名
  5. `pkgbld_container_workdir` : コンテナ内でパッケージ構築作業を行う作業ディレクトリ
  6. `pkgbld_container_output_dir` : コンテナ内で生成パッケージを出力するディレクトリ。
   なお, `pkgbld_builder_image_debian` と `pkgbld_builder_image_rhel` には Dockerfile のパスではなくコンテナイメージ名を指定します。
3. 成果物作成処理に必要な値として以下の変数を設定する:
  1. `pkgbld_build_script_src_debian` : Debian系統向け成果物作成用シェルスクリプトの配置元ファイルパス
  2. `pkgbld_build_script_name_debian` : Debian系統向けコンテナ内実行スクリプト名
  3. `pkgbld_build_script_src_rhel` : Red Hat系統向け成果物作成用シェルスクリプトの配置元ファイルパス
  4. `pkgbld_build_script_name_rhel` : Red Hat系統向けコンテナ内実行スクリプト名
  5. `pkgbld_build_script_src` / `pkgbld_build_script_name` : 互換用途の共通指定値(未指定時のフォールバック)
  6. `pkgbld_build_script_args` : 成果物作成用シェルスクリプトに渡す引数配列
  7. `pkgbld_container_env_args` : 成果物作成用シェルスクリプトへ渡す環境変数引数配列
4. 成果物探索条件として以下の変数を設定する:
  1. `pkgbld_package_type` : 入力検証用のパッケージ形式(`deb`または`rpm`)。実行時のOS分岐は `ansible_facts.os_family` で判定します。
  2. `pkgbld_package_name` : 導入対象として扱うパッケージ名
  3. `pkgbld_package_file_patterns_debian` : Debian系統向け成果物探索パターン配列
  4. `pkgbld_package_file_patterns_rhel` : Red Hat系統向け成果物探索パターン配列
5. 配布/導入条件として以下の変数を設定する:
  1.  `package_targets` : 1回だけ実行する処理(run_onceタスク)で Debian 系/Red Hat 系ターゲット有無を判定するためのホスト名配列
  2.  `pkgbld_install_dest_dir` : 導入対象ホストでパッケージを一時配置するディレクトリ
  3.  `pkgbld_install_deb_lock_wait_seconds` : Debian系統での排他制御待機時間(秒)
  4.  `pkgbld_disable_gpg_check` : Red Hat系統で署名検証を無効化する可否の真偽値
  5.  `pkgbld_common_cleanup_build_workspace` : 構築後に作業ディレクトリを削除する可否の真偽値
6. 版数検証条件として以下の変数を設定する:
  1.  `pkgbld_verify_version_enabled` : 版数照合処理を有効化する可否の真偽値
  2.  `pkgbld_verify_version_command` : 導入済みパッケージの版数を取得するコマンド配列
  3.  `pkgbld_verify_version_regex` : コマンド出力から版数文字列を抽出する正規表現
  4.  `pkgbld_verify_version_expected` : 一致を期待する版数文字列
  5.  `pkgbld_verify_strip_after_hyphen` : Debian系統で版数末尾の付加版番号を除外して比較する可否の真偽値

### 呼び出し元ロールでのパラメタの設定手順

1. 呼び出し元ロールで, 成果物作成用シェルスクリプトとパッケージ作成用コンテナイメージを事前準備します。
2. 呼び出し元ロールで, 本ロールに渡す入力パラメタを目的ごとの分類で設定します。
	 - 構築実行: パッケージ構築処理
	 - 成果物探索: 生成されたパッケージを検索する処理
	 - 配布/導入: 生成されたパッケージを導入先ホストに配布し, 導入先ホストに導入(インストール)する処理
	 - 検証: 導入されたパッケージの版数を確認する処理
3. include_role で `pkgbld-common` を呼び出し, 設定した入力パラメタを渡す。
4. 実行結果で, パッケージ成果物の回収処理, 配布処理, 導入処理, 検証処理が意図どおり完了したことを確認します。

### 呼び出し元ロールから本ロールを呼び出すansibleタスクの記載方法

本節では, 呼び出し元ロールから本ロールを呼び出す際のansibleタスクの記載方法を例示する:

```yaml
1: - name: Build and install package via pkgbld-common
2: ansible.builtin.include_role:
3: name: pkgbld-common
4: vars:
5: package_build_host: "localhost"
6: package_build_workspace: "/tmp/example-build"
7: package_build_output_dir: "/tmp/example-build/output"
8: pkgbld_container_runtime: "docker"
9: pkgbld_container_network_mode: "host"
10: pkgbld_builder_image_debian: "example-build-ubuntu:24.04"
11: pkgbld_builder_image_rhel: "example-build-almalinux:9.6"
12: pkgbld_container_workdir: "/work"
13: pkgbld_container_output_dir: "/work/output"
14: pkgbld_build_script_src_debian: "/tmp/example-build/build-example-deb.sh"
15: pkgbld_build_script_name_debian: "build-example-deb.sh"
16: pkgbld_build_script_src_rhel: "/tmp/example-build/build-example-rpm.sh"
17: pkgbld_build_script_name_rhel: "build-example-rpm.sh"
18: pkgbld_build_script_args: []
19: pkgbld_container_env_args: []
20: pkgbld_package_type: "deb"
21: pkgbld_package_name: "example"
22: pkgbld_package_file_patterns_debian:
23: - "example_*.deb"
24: pkgbld_package_file_patterns_rhel:
25: - "example-*.rpm"
26: package_targets:
27: - "target-host-01.example.local"
28: - "target-host-02.example.local"
29: pkgbld_install_dest_dir: "/tmp"
```

上記例の各行での記載内容は以下の通り:

- 1-3 行目: は, `pkgbld-common` ロール呼び出し処理を実施するための記載です。
- 5-7 行目: は, 構築ホスト, 作業ディレクトリ, パッケージ成果物出力ディレクトリを指定するための設定です。
- 8-13 行目: は, コンテナ実行方式, ネットワーク共有方式, パッケージ作成用コンテナイメージ, コンテナ内作業ディレクトリを指定するための設定です。
- 14-19 行目: は, OS別の成果物作成用シェルスクリプト設定, 実行引数, 環境変数引数を指定するための設定です。
- 20-25 行目: は, パッケージ形式, パッケージ名, パッケージ成果物探索パターンを指定するための設定です。
- 26-29 行目: は, OSターゲット有無判定用のホスト配列と導入先ディレクトリを指定するための設定です。

### 各パラメタ変数に設定する値

| 分類 | 変数 | 設定する値 |
| --- | --- | --- |
| 構築実行 | package_build_host, package_build_workspace, package_build_output_dir | 構築ホスト, 作業ディレクトリ, パッケージ成果物出力ディレクトリを指定します。 |
| 構築実行 | pkgbld_container_runtime, pkgbld_container_network_mode | パッケージ作成用コンテナの実行方式とネットワーク共有方式を指定します。 |
| 構築実行 | pkgbld_builder_image_debian, pkgbld_builder_image_rhel | Debian系統向けパッケージ作成用コンテナイメージ名, Red Hat系統向けパッケージ作成用コンテナイメージ名を指定します。本ロールでは, 指定されたイメージを`pkgbld_container_runtime`変数で指定されたコンテナランタイム(`docker`など)を用いて起動し, コンテナ内でパッケージの構築を行う。|
| 構築実行 | pkgbld_build_script_src_debian, pkgbld_build_script_name_debian, pkgbld_build_script_src_rhel, pkgbld_build_script_name_rhel | 呼び出し側が生成したOS別の成果物作成用シェルスクリプトの配置元とスクリプト名を指定します。 |
| 構築実行 | pkgbld_build_script_src, pkgbld_build_script_name | 互換用途の共通指定値。OS別変数未指定時のフォールバックとして使う。 |
| 構築実行 | pkgbld_container_env_args | 成果物作成用シェルスクリプトへ渡す環境変数引数を配列で明示します。 |
| 成果物探索 | pkgbld_package_file_patterns_debian, pkgbld_package_file_patterns_rhel | パッケージ成果物探索パターンを実際の生成ファイル名規則に厳密に合わせる。 |
| 配布/導入 | package_targets, pkgbld_install_dest_dir | `package_targets` は1回だけ実行する処理(run_onceタスク)のOS判定用ホスト配列であり, 配布先の実行制御は play の実行対象ホストに従う。 |
| 配布/導入 | pkgbld_disable_gpg_check | Red Hat系統で配布済み rpm ファイルを導入する場合の署名検証方針を指定します。 |
| 後始末 | pkgbld_common_cleanup_build_workspace | 構築ホスト上の作業ディレクトリ削除可否を指定します。 |
| 検証 | pkgbld_package_name | `dpkg-query` または `rpm -q` が参照するパッケージ名を一致させる。 |
| 検証 | pkgbld_verify_version_enabled, pkgbld_verify_version_command, pkgbld_verify_version_regex, pkgbld_verify_version_expected | 版数照合処理の有効化条件と照合条件を指定します。 |
| 検証 | pkgbld_verify_strip_after_hyphen | Debian で版数照合時に無視する付加版番号の扱いを指定します。 |

#### パッケージ作成用コンテナの実行方式に指定可能な値

パッケージ作成用コンテナの実行方式に指定可能な設定値を以下に示す:

| 設定値 | 意味 | 補足 |
| --- | --- | --- |
| `docker` | Docker を使ってコンテナを実行します。 | 既定値。|
| `podman` | Podman を使ってコンテナを実行します。 | |

本ロールでは, 指定されたコマンドが, `docker`コマンドと互換性のあるサブコマンド`run`を実行可能であることを前提としている。

指定したコマンドが構築ホスト上に導入済みであることの確認, 指定したコマンドが`docker`コマンドと互換性のあるコマンドライン仕様を持っていることを呼び出し元で保証すること。

#### ネットワーク共有方式に指定可能な値

ネットワーク共有方式に指定可能な設定値を以下に示す:

| 設定値 | 意味 | 補足 |
| --- | --- | --- |
| `host` | コンテナから構築ホストのネットワークを共有利用します。 | 既定値。|
| `bridge` | コンテナ専用の仮想ネットワークを利用します。 | 外部到達性や名前解決条件を呼び出し元で確認します。 |
| `none` | コンテナのネットワーク通信を使わない。 | 作成処理で外部取得が不要な場合に限定して使う。 |

本ロールは 設定された値を `pkgbld_container_runtime`(コンテナランタイム実行コマンド名)で指定されたコマンド(規定: `docker`)の`--network` 引数に引き渡す。`pkgbld_container_runtime`(コンテナランタイム実行コマンド名)に指定したコマンドでの引数, 指定パラメタの有効性は, 呼び出し元で保証すること。

### go-lang-local ロールでの設定パラメタの例

本節では, 具体的な設定例として, go-lang-local ロールでの設定パラメタの指定値を示す。なお, 本節での`<解決済み版数>`, `<Go言語のアーキテクチャ名>`, `<RPMのアーキテクチャ名>`の各項目は, 呼び出し元でそれぞれ以下の内容を指定している:

- `<解決済み版数>`: Go言語のバージョン番号 (Major.Minor.Patch版数形式, 例: 1.25.12など)
- `<Go言語のアーキテクチャ名>`: Go言語のアーキテクチャ種別を表す文字列(例: `amd64`など)
- `<RPMのアーキテクチャ名>`: RPMのアーキテクチャ種別を表す文字列(例: `x86_64`など)

| 入力パラメタ | go-lang-localでの設定値 | 備考 |
| --- | --- | --- |
| package_build_host | localhost | 構築実行ホスト。 |
| package_build_workspace | /tmp/go-build | 作業ディレクトリ。 |
| package_build_output_dir | /tmp/go-build/output | 成果物出力先。 |
| pkgbld_container_runtime | docker | 通常値。 |
| pkgbld_container_network_mode | host | 通常値。 |
| pkgbld_builder_image_debian | go-build-ubuntu:24.04 | Debian系統向けパッケージ作成用コンテナイメージ。 |
| pkgbld_builder_image_rhel | go-build-almalinux:9.6 | Red Hat系統向けパッケージ作成用コンテナイメージ。 |
| pkgbld_container_workdir | /work | コンテナ内作業ディレクトリ。 |
| pkgbld_build_script_src_debian / pkgbld_build_script_src_rhel | /tmp/go-build/build-go-deb.sh / /tmp/go-build/build-go-rpm.sh | Debian系統とRed Hat系統で切り替える。 |
| pkgbld_build_script_name_debian / pkgbld_build_script_name_rhel | `build-go-deb.sh` / `build-go-rpm.sh` | Debian系統とRed Hat系統で切り替える。 |
| pkgbld_package_type | Debian: deb / RHEL: rpm | 入力検証用。実行時のOS分岐は `ansible_facts.os_family` を使用します。 |
| pkgbld_package_name | Debian: go-lang / RHEL: go-lang | Debian系統とRed Hat系統で切り替える。 |
| pkgbld_package_file_patterns_debian | go-lang_<解決済み版数>-1_*.deb | 成果物探索。 |
| pkgbld_package_file_patterns_rhel | go-lang-<解決済み版数>-1.*.rpm | 成果物探索。 |
| package_targets | ["target-host-01.example.local", "target-host-02.example.local"] | 1回だけ実行する処理(run_onceタスク)でOS判定に使うホスト配列。 |
| pkgbld_install_deb_lock_wait_seconds | 600 | Debian系統での排他制御待機時間。 |
| pkgbld_build_timeout_seconds | 3600 | 作成処理の待機上限。 |
| pkgbld_build_loop_delay_seconds | 5 | 状態確認の間隔。 |
| pkgbld_container_env_args | -e GO_VERSION=<解決済み版数>, -e GO_BASE_URL=https://go.dev/dl, -e GO_ARCH=<Go言語のアーキテクチャ名>, -e GO_DEB_ARCH=<Go言語のアーキテクチャ名>/-e GO_RPM_ARCH=<RPMのアーキテクチャ名>, -e GO_PACKAGE_NAME=go-lang, -e GO_INSTALL_DIR=/usr/local/go, -e GO_PROFILE_SCRIPT=/etc/profile.d/golang.sh | 成果物作成用シェルスクリプトへ渡す環境変数引数。 |
| pkgbld_verify_version_* | command=/usr/local/go/bin/go version, regex=go([0-9]+\\.[0-9]+\\.[0-9]+), expected=<解決済み版数> | 導入版数を照合します。 |

#### Debian/Ubuntuホスト用の呼び出し例

Debian/Ubuntuホストに対し, 前掲のパラメタで本ロールを呼び出す際の指定例を示す:

```yaml
- name: Build and install package via pkgbld-common (Debian/Ubuntu)
  ansible.builtin.include_role:
    name: pkgbld-common
  vars:
    package_build_host: "localhost"
    package_build_workspace: "/tmp/go-build"
    package_build_output_dir: "/tmp/go-build/output"
    pkgbld_container_runtime: "docker"
    pkgbld_container_network_mode: "host"
    pkgbld_builder_image_debian: "go-build-ubuntu:24.04"
    pkgbld_builder_image_rhel: "go-build-almalinux:9.6"
    pkgbld_container_workdir: "/work"
    pkgbld_container_output_dir: "/work/output"
    pkgbld_build_script_src_debian: "/tmp/go-build/build-go-deb.sh"
    pkgbld_build_script_name_debian: "build-go-deb.sh"
    pkgbld_build_script_src_rhel: "/tmp/go-build/build-go-rpm.sh"
    pkgbld_build_script_name_rhel: "build-go-rpm.sh"
    pkgbld_build_script_args: []
    pkgbld_container_env_args:
      - "-e"
      - "GO_VERSION=1.25.12"
      - "-e"
      - "GO_BASE_URL=https://go.dev/dl"
      - "-e"
      - "GO_ARCH=amd64"
      - "-e"
      - "GO_DEB_ARCH=amd64"
      - "-e"
      - "GO_PACKAGE_NAME=go-lang"
      - "-e"
      - "GO_INSTALL_DIR=/usr/local/go"
      - "-e"
      - "GO_PROFILE_SCRIPT=/etc/profile.d/golang.sh"
    pkgbld_package_type: "deb"
    pkgbld_package_name: "go-lang"
    pkgbld_package_file_patterns_debian:
      - "go-lang_1.25.12-1_*.deb"
    pkgbld_package_file_patterns_rhel:
      - "go-lang-1.25.12-1.*.rpm"
    package_targets:
      - "target-host-01.example.local"
      - "target-host-02.example.local"
    pkgbld_install_dest_dir: "/tmp"
    pkgbld_install_deb_lock_wait_seconds: 600
    pkgbld_build_timeout_seconds: 3600
    pkgbld_build_loop_delay_seconds: 5
    pkgbld_verify_version_enabled: true
    pkgbld_verify_version_command:
      - "/usr/local/go/bin/go"
      - "version"
    pkgbld_verify_version_regex: "go([0-9]+\\.[0-9]+\\.[0-9]+)"
    pkgbld_verify_version_expected: "1.25.12"
    pkgbld_verify_strip_after_hyphen: false
```

#### RHEL(AlmaLinuxなど)ホスト用の呼び出し例

RHEL(AlmaLinuxなど)ホストに対し, 前掲のパラメタで本ロールを呼び出す際の指定例を示す:

```yaml
- name: Build and install package via pkgbld-common (RHEL/AlmaLinux)
  ansible.builtin.include_role:
    name: pkgbld-common
  vars:
    package_build_host: "localhost"
    package_build_workspace: "/tmp/go-build"
    package_build_output_dir: "/tmp/go-build/output"
    pkgbld_container_runtime: "docker"
    pkgbld_container_network_mode: "host"
    pkgbld_builder_image_debian: "go-build-ubuntu:24.04"
    pkgbld_builder_image_rhel: "go-build-almalinux:9.6"
    pkgbld_container_workdir: "/work"
    pkgbld_container_output_dir: "/work/output"
    pkgbld_build_script_src_debian: "/tmp/go-build/build-go-deb.sh"
    pkgbld_build_script_name_debian: "build-go-deb.sh"
    pkgbld_build_script_src_rhel: "/tmp/go-build/build-go-rpm.sh"
    pkgbld_build_script_name_rhel: "build-go-rpm.sh"
    pkgbld_build_script_args: []
    pkgbld_container_env_args:
      - "-e"
      - "GO_VERSION=1.25.12"
      - "-e"
      - "GO_BASE_URL=https://go.dev/dl"
      - "-e"
      - "GO_ARCH=amd64"
      - "-e"
      - "GO_RPM_ARCH=x86_64"
      - "-e"
      - "GO_PACKAGE_NAME=go-lang"
      - "-e"
      - "GO_INSTALL_DIR=/usr/local/go"
      - "-e"
      - "GO_PROFILE_SCRIPT=/etc/profile.d/golang.sh"
    pkgbld_package_type: "rpm"
    pkgbld_package_name: "go-lang"
    pkgbld_package_file_patterns_debian:
      - "go-lang_1.25.12-1_*.deb"
    pkgbld_package_file_patterns_rhel:
      - "go-lang-1.25.12-1.*.rpm"
    package_targets:
      - "target-host-01.example.local"
      - "target-host-02.example.local"
    pkgbld_install_dest_dir: "/tmp"
    pkgbld_disable_gpg_check: true
    pkgbld_install_deb_lock_wait_seconds: 600
    pkgbld_build_timeout_seconds: 3600
    pkgbld_build_loop_delay_seconds: 5
    pkgbld_verify_version_enabled: true
    pkgbld_verify_version_command:
      - "/usr/local/go/bin/go"
      - "version"
    pkgbld_verify_version_regex: "go([0-9]+\\.[0-9]+\\.[0-9]+)"
    pkgbld_verify_version_expected: "1.25.12"
    pkgbld_verify_strip_after_hyphen: false
```

## 検証項目

- 構築ホストの `package_build_output_dir` にパッケージ成果物ファイルが存在すること。
- 導入対象ホストの `pkgbld_install_dest_dir` に配布済みパッケージ成果物ファイルが存在すること。
- Red Hat系統では導入後に `/etc/init.d` が `/etc/rc.d/init.d` を参照する互換 symlink であること。
- Debian系統では `dpkg-query`, Red Hat系統では `rpm -q` が導入済みパッケージ名を返すこと。
- 版数検証を有効化した場合, 版数抽出式で抽出した版数文字列が期待版数 (`pkgbld_verify_version_expected`) と一致すること。

## 前提条件

本ロールの実行者は, 対象ホストが inventory に登録済みであることを確認します。
本ロールの実行者は, 関連する共通変数が vars/all-config.yml または host_vars に定義済みであることを確認します。

## 実行方法

実行者は制御ホストで以下のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts site.yml --tags "pkgbld-common"
```

## 主要変数

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| pkgbld_verify_version_enabled | 版数照合処理の実行可否を制御します。 | false | true |

## 実行フロー

1. [tasks/main.yml](tasks/main.yml) の `Load Params` で [tasks/load-params.yml](tasks/load-params.yml) を読み込み, ロール単独実行時に必要な変数を再読込します。
2. [tasks/main.yml](tasks/main.yml) の `Package` で [tasks/package.yml](tasks/package.yml) を実行し, パッケージ作成から導入までの本処理を開始します。
3. [tasks/package.yml](tasks/package.yml) の `Validate` で [tasks/validate.yml](tasks/validate.yml) を実行し, 必須変数, OS系統別ビルダーイメージ, 成果物探索パターン, build スクリプト存在を検証します。
4. [tasks/package.yml](tasks/package.yml) の `Prepare build workdir` と `Run build container` で [tasks/prepare-build-workdir.yml](tasks/prepare-build-workdir.yml), [tasks/run-build-container.yml](tasks/run-build-container.yml) を実行し, 構築ホスト上で作業ディレクトリ準備とコンテナ内ビルドを実施します。
5. [tasks/package.yml](tasks/package.yml) の `Collect artifacts` と `Distribute artifacts` で [tasks/collect.yml](tasks/collect.yml), [tasks/distribute.yml](tasks/distribute.yml) を実行し, 構築ホストから制御ホスト, 制御ホストから導入対象ホストへ成果物を配布します。
6. [tasks/package.yml](tasks/package.yml) の `Install local packages` で [tasks/install.yml](tasks/install.yml) を実行し, OS系統に応じて `.deb` 又は `.rpm` を導入します。
7. [tasks/package.yml](tasks/package.yml) の `Verify installation` で [tasks/verify.yml](tasks/verify.yml) を実行し, 導入済み状態と版数照合条件を検証します。
8. [tasks/package.yml](tasks/package.yml) の `Cleanup build workspace` で [tasks/cleanup-build-workdir.yml](tasks/cleanup-build-workdir.yml) を実行し, 設定に応じて構築ホスト上の作業ディレクトリを削除します。
9. [tasks/main.yml](tasks/main.yml) で `Directory`, `User Group`, `Service`, `Config` の各 include を順に評価します。現行実装ではそれぞれ [tasks/directory.yml](tasks/directory.yml), [tasks/user_group.yml](tasks/user_group.yml), [tasks/service.yml](tasks/service.yml), [tasks/config.yml](tasks/config.yml) は空実装です。

## 検証ポイント

### 検証の前提条件

検証を始める前に, 次の条件が満たされていることを確認します。

- 構築ホストで `pkgbld_container_runtime` に指定したコンテナ実行コマンドが利用可能であること。
- 呼び出し元ロールで成果物作成用シェルスクリプトとコンテナイメージが準備済みであること。
- `package_targets` に導入対象ホストが1台以上設定されていること。
- 構築ホスト, 制御ホスト, 導入対象ホスト間で成果物配布に必要な通信が可能であること。
- 版数照合を有効化する場合は `pkgbld_verify_version_command`, `pkgbld_verify_version_regex`, `pkgbld_verify_version_expected` が定義済みであること。

### 検証環境の設定

検証用の host_vars と vars/all-config.yml を次の値で設定します:

```yaml
1: package_build_host: "localhost"
2: package_build_workspace: "/tmp/go-build"
3: package_build_output_dir: "/tmp/go-build/output"
4: pkgbld_install_dest_dir: "/tmp"
5: pkgbld_package_name: "go-lang"
6: pkgbld_verify_version_enabled: true
7: pkgbld_verify_version_expected: "1.25.12"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | package_build_host: "localhost" | パッケージ作成処理の実行先を指定します。 | 構築ホスト未指定の場合は run_once 処理で成果物回収元を特定できず失敗するためです。 |
| 2-3 | package_build_workspace, package_build_output_dir | 構築作業ディレクトリと成果物出力先を指定します。 | パス不整合の場合は成果物探索と回収処理で失敗するためです。 |
| 4 | pkgbld_install_dest_dir: "/tmp" | 導入対象ホスト上の成果物一時配置先を指定します。 | 配置先未指定の場合は配布処理のコピー先を解決できないためです。 |
| 5 | pkgbld_package_name: "go-lang" | 導入済み判定と版数照合対象のパッケージ名を指定します。 | パッケージ名不一致の場合は導入済み確認が誤検知になるためです。 |
| 6-7 | pkgbld_verify_version_enabled, pkgbld_verify_version_expected | 版数照合処理を有効化し, 期待版数を指定します。 | 期待版数未指定又は不一致の場合は照合結果が失敗となるためです。 |

### 検証コマンドと期待結果

#### 1. Playbook 実行結果の確認

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
ansible-playbook -i inventory/hosts site.yml --tags "pkgbld-common"
```

**期待される出力**:

```plaintext
failed=0
```

**確認ポイント**:

- 実行結果が `failed=0` で完了すること。
- `Validate required variables for pkgbld-common` が成功していること。

#### 2. 構築ホスト上の成果物生成確認

**実施対象ホスト**: 構築ホスト

**実行するコマンド**:

```bash
ls -l /tmp/go-build/output
find /tmp/go-build/output -maxdepth 1 -type f \( -name '*.deb' -o -name '*.rpm' \)
```

**期待される出力**:

```plaintext
...go-lang_*.deb
または
...go-lang-*.rpm
```

**確認ポイント**:

- `package_build_output_dir` 配下に成果物ファイルが存在すること。
- 生成された成果物名が `pkgbld_package_file_patterns_*` の規則と一致すること。

#### 3. 導入対象ホスト上の導入状態確認

**実施対象ホスト**: 導入対象ホスト

**実行するコマンド**:

```bash
dpkg-query -W -f='${Status} ${Version}\n' go-lang || true
rpm -q go-lang || true
```

**期待される出力**:

```plaintext
install ok installed
または
go-lang-<version>
```

**確認ポイント**:

- Debian系統では `dpkg-query` が導入済み状態を返すこと。
- Red Hat系統では `rpm -q` が導入済みパッケージ名を返すこと。

#### 4. 版数照合結果の確認

**実施対象ホスト**: 導入対象ホスト

**実行するコマンド**:

```bash
/usr/local/go/bin/go version
```

**期待される出力**:

```plaintext
go version go1.25.12 ...
```

**確認ポイント**:

- コマンド出力から抽出された版数が `pkgbld_verify_version_expected` と一致すること。
- Debian系統で付加版番号差分がある場合は `pkgbld_verify_strip_after_hyphen` の設定意図と一致すること。

### 異常時の確認項目

#### 1. 必須変数不足による停止確認

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
grep -n 'package_build_host\|pkgbld_build_script_src_debian\|pkgbld_build_script_src_rhel\|package_targets' vars/all-config.yml host_vars/*.yml
```

**確認ポイント**:

- 必須変数が未定義又は空文字列になっていないこと。
- `package_targets` が空配列でないこと。

#### 2. 成果物探索失敗時の確認

**実施対象ホスト**: 構築ホスト, 制御ホスト

**実行するコマンド**:

```bash
ls -l /tmp/go-build/output
```

**確認ポイント**:

- 成果物ファイル名が `pkgbld_package_file_patterns_debian` 又は `pkgbld_package_file_patterns_rhel` と一致していること。
- 成果物出力先ディレクトリと探索対象ディレクトリが同一であること。

#### 3. Red Hat 系導入前互換パス確認

**実施対象ホスト**: Red Hat系統の導入対象ホスト

**実行するコマンド**:

```bash
ls -ld /etc/init.d /etc/rc.d/init.d
```

**確認ポイント**:

- `/etc/init.d` が `/etc/rc.d/init.d` を参照する互換 symlink であること。
- `/etc/init.d.ansible-backup` が存在する場合は, 既存運用との整合を確認済みであること。


## トラブルシューティング

### 1. 必須変数不足で停止する場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
grep -n 'package_build_host\|pkgbld_build_script_src_debian\|pkgbld_build_script_src_rhel\|package_targets' vars/all-config.yml host_vars/*.yml
```

**確認ポイント**:

- package_build_host, pkgbld_build_script_src_debian, pkgbld_build_script_src_rhel が定義済みであること。
- package_targets が空配列ではないこと。
- 実行ログに Validate required variables の失敗が出る場合は, 呼び出し元の変数値を見直すこと。

### 2. 成果物作成用シェルスクリプトが見つからない場合

**実施対象ホスト**: 構築ホスト

**実行するコマンド**:

```bash
ls -l "${pkgbld_build_script_src_debian}" "${pkgbld_build_script_src_rhel}"
```

**確認ポイント**:

- 成果物作成用シェルスクリプトファイルが存在すること。
- 呼び出し元ロールが成果物作成用シェルスクリプト生成処理を先に完了していること。
- 実行ログに Build script source does not exist が出る場合は, 成果物作成用シェルスクリプトファイルの絶対パスを統一すること。

### 3. パッケージ成果物が見つからない場合

**実施対象ホスト**: 構築ホスト

**実行するコマンド**:

```bash
ls -l /tmp/go-build/output
find /tmp/go-build/output -maxdepth 1 -type f \( -name '*.deb' -o -name '*.rpm' \)
```

**確認ポイント**:

- package_build_output_dir 配下に成果物ファイルが存在すること。
- 成果物ファイル名が pkgbld_package_file_patterns_debian 又は pkgbld_package_file_patterns_rhel と一致すること。
- 実行ログに No package artifact was generated が出る場合は, パターンと実ファイル名の差分を解消すること。

### 4. 成果物回収で失敗する場合

**実施対象ホスト**: 構築ホスト, 制御ホスト

**実行するコマンド**:

```bash
ls -ld /tmp/go-build /tmp/go-build/output
find /tmp/go-build/output -maxdepth 1 -type f -ls
```

**確認ポイント**:

- package_build_output_dir が構築ホスト上で参照可能であること。
- 成果物ファイルに制御ホストから読取可能な権限が付与されていること。
- 実行ログに Fetch built packages の失敗が出る場合は, パス不整合と権限を優先確認すること。

### 5. Debian系統で待機時間を超過する場合

**実施対象ホスト**: Debian系統の導入対象ホスト

**実行するコマンド**:

```bash
sudo fuser /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock || true
ps -ef | grep -E 'apt|dpkg' | grep -v grep
```

**確認ポイント**:

- apt 又は dpkg の排他制御を他プロセスが保持していないこと。
- lock timeout が出る場合は, pkgbld_install_deb_lock_wait_seconds の値を延長すること。

### 6. Red Hat系統で chkconfig 導入時に失敗する場合

**実施対象ホスト**: Red Hat系統の導入対象ホスト

**実行するコマンド**:

```bash
ls -ld /etc/init.d /etc/rc.d/init.d /etc/init.d.ansible-backup
```

**確認ポイント**:

- /etc/init.d が /etc/rc.d/init.d を参照する互換 symlink であること。
- /etc/init.d が通常ファイル又は特殊ファイルになっていないこと。
- 実行ログの Normalize /etc/init.d compatibility path on Red Hat family hosts タスク結果に失敗がないこと。

### 7. Red Hat系統で署名検証に失敗する場合

**実施対象ホスト**: Red Hat系統の導入対象ホスト

**実行するコマンド**:

```bash
dnf -y install /tmp/go-lang-*.rpm
```

**確認ポイント**:

- dnf 実行結果に GPG error が含まれる場合は署名検証失敗であること。
- 署名未設定の rpm を導入する運用の場合は pkgbld_disable_gpg_check の設定値を見直すこと。

### 8. 版数照合で不一致になる場合

**実施対象ホスト**: 導入対象ホスト

**実行するコマンド**:

```bash
/usr/local/go/bin/go version
```

**確認ポイント**:

- 版数照合コマンド出力から抽出される版数が pkgbld_verify_version_expected と一致すること。
- Debianで付加版番号差分がある場合は pkgbld_verify_strip_after_hyphen の設定値を見直すこと。
- version mismatch が出る場合は, 版数抽出式と期待版数の両方を確認すること。

## 注意事項

- パッケージ作成用コンテナイメージ作成処理はロール外で実施します。例えばDockerを使用する場合, パッケージ作成用コンテナイメージ作成処理とは, `Dockerfile`の作成, 構築ホスト上での`docker build`コマンドによるコンテナイメージの構築処理, コンテナイメージの読み込み作業のことを意味します。
- 成果物作成用シェルスクリプト生成処理はロール外で実施します。
- `pkgbld_container_env_args` は環境変数引数配列を実行引数へそのまま連結するため, 引数値の引用符付与方針を呼び出し元で統一します。
- `package_targets` は1回だけ実行する処理(run_onceタスク)でのOS判定用ホスト配列として必須であり, 空配列は指定できない。
- `pkgbld_package_type` は入力検証に使用する値であり, 実行時のOS分岐は `ansible_facts.os_family` に従う。
- Red Hat系統では導入前に `/etc/init.d` 正規化処理を実施し, 必要に応じて既存の `/etc/init.d` ディレクトリを `/etc/init.d.ansible-backup` として退避します。既存運用で `/etc/init.d` を直接管理している場合は, 退避先の扱いを運用手順に含めること。

## 参考資料

### 公式ドキュメント

- [Debian New Maintainers Guide](https://www.debian.org/doc/manuals/maint-guide/)
- [RPM Packaging Guide](https://rpm-packaging-guide.github.io/)
