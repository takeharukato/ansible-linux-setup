# pkgbld-common ロール

本ロールは, ディストリビューション用パッケージ構築から導入までの処理をロール間で共通化して使用可能にするためのロールです。

## 目次

- [pkgbld-common ロール](#pkgbld-common-ロール)
  - [用語](#用語)
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
  - [トラブルシューティング](#トラブルシューティング)
  - [注意事項](#注意事項)
  - [検証項目](#検証項目)

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
| IP | - | インターネットプロトコルの略称。 |
| SQL | - | データベースを操作するための記述言語。 |
| HTTP | - | WWW で情報をやり取りする通信手順。 |
| HTTPS | - | 通信内容を暗号化して WWW 通信を行う方式。 |
| RPM | - | RHEL 系で使用するパッケージ形式。 |
| VM | - | 物理機器上で動作する仮想的な計算機。 |
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
| API | - | アプリケーション同士がやり取りする方法を定めた仕様。 |
| URL | - | WWW 上の資源の場所を示す文字列。 |
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
| Red Hat Enterprise Linux | RHEL | Red Hat 社が提供する商用 Linux ディストリビューション。 |
| RPM Package Manager | RPM | RHEL/AlmaLinux 系で使用するパッケージ形式。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `docker` | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |

## 概要
本ロールは, ディストリビューション用パッケージ構築から導入までの処理をロール間で共通化して使用可能にするためのロールです。
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

1. 実行者が load-params.yml により変数を読み込む。
2. 実行者が本ロール固有の task を順次実行します。
3. 実行者が検証コマンドを実行して期待結果を確認します。

## 検証ポイント

実行者は以下の検証コマンドを実行し, 構文検査が成功することを確認します。

```bash
ansible-playbook -i inventory/hosts site.yml --syntax-check
```

期待結果: エラーが出力されず, syntax check が成功します。

## トラブルシューティング

主なトラブルの症状, 原因, 確認項目, 対処方法を以下に示す:

| 症状 | 主な原因 | 確認項目 | 対処 |
| --- | --- | --- | --- |
| 必須変数不足で停止する | 必須変数未設定 | package_build_host, pkgbld_build_script_src_debian/rhel, package_targets などの必須変数値 | 呼び出し側の必須変数設定値を見直す。実行メッセージ例: Validate required variables。 |
| 成果物作成用シェルスクリプトが見つからない | スクリプト未生成, パス不整合 | pkgbld_build_script_src_debian / pkgbld_build_script_src_rhel が指す成果物作成用シェルスクリプトファイル | 成果物作成用シェルスクリプト生成処理を先に実行し, 成果物作成用シェルスクリプトファイルの絶対パスを統一します。実行メッセージ例: Build script source does not exist。 |
| パッケージ成果物が見つからない | 成果物パターン不一致 | pkgbld_package_file_patterns_* と実ファイル名 | パッケージ成果物探索パターンを実ファイル名に合わせる。実行メッセージ例: No package artifact was generated。 |
| 成果物回収で失敗する | 構築ホストの権限不足, パス不整合 | package_build_output_dir と成果物権限 | パッケージ成果物出力先ディレクトリと成果物ファイルの読み取り権限を確認します。実行メッセージ例: Fetch built packages ...。 |
| Debian系統で待機時間を超過する | 他プロセスがパッケージ管理処理の排他制御を保持 | `apt` / `dpkg` の排他制御状態 | 排他制御待機時間パラメタ `pkgbld_install_deb_lock_wait_seconds` を延長します。実行メッセージ例: lock timeout。 |
| Red Hat系統で `chkconfig` 導入時に失敗する (`error: unpacking of archive failed on file /etc/init.d...`) | `/etc/init.d` の型不整合 (ディレクトリ/不正リンク/不正ファイル) | `ls -ld /etc/init.d /etc/rc.d/init.d` の結果, `pkgbld-common` 実行ログの `Normalize /etc/init.d compatibility path on Red Hat family hosts` タスク結果 | `pkgbld-common` は導入前に `/etc/init.d` を自動正規化します。失敗が継続する場合は `/etc/init.d` が通常ファイルや特殊ファイルになっていないことを確認します。 |
| Red Hat系統で署名検証に失敗する | 署名未設定の rpm ファイルを導入 | `dnf` エラーメッセージ | 署名検証方針パラメタ `pkgbld_disable_gpg_check` を調整します。実行メッセージ例: GPG error。 |
| 版数照合で不一致になる | 版数照合用コマンド, 版数抽出式, 期待版数の不整合 | 版数照合コマンド出力, 版数抽出式, 期待版数 | 版数抽出式と期待版数を見直し, Debianで付加版番号差分がある場合は `pkgbld_verify_strip_after_hyphen` の設定値を検討します。実行メッセージ例: version mismatch。 |

## 注意事項

- パッケージ作成用コンテナイメージ作成処理はロール外で実施します。例えばDockerを使用する場合, パッケージ作成用コンテナイメージ作成処理とは, `Dockerfile`の作成, 構築ホスト上での`docker build`コマンドによるコンテナイメージの構築処理, コンテナイメージの読み込み作業のことを意味します。
- 成果物作成用シェルスクリプト生成処理はロール外で実施します。
- `pkgbld_container_env_args` は環境変数引数配列を実行引数へそのまま連結するため, 引数値の引用符付与方針を呼び出し元で統一します。
- `package_targets` は1回だけ実行する処理(run_onceタスク)でのOS判定用ホスト配列として必須であり, 空配列は指定できない。
- `pkgbld_package_type` は入力検証に使用する値であり, 実行時のOS分岐は `ansible_facts.os_family` に従う。
- Red Hat系統では導入前に `/etc/init.d` 正規化処理を実施し, 必要に応じて既存の `/etc/init.d` ディレクトリを `/etc/init.d.ansible-backup` として退避します。既存運用で `/etc/init.d` を直接管理している場合は, 退避先の扱いを運用手順に含めること。

## 参考資料

### 公式ドキュメント

- Debian New Maintainers Guide: https://www.debian.org/doc/manuals/maint-guide/
- RPM Packaging Guide: https://rpm-packaging-guide.github.io/
