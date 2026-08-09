# go-lang-local ロール

本ロールは, 特定の版数のGo言語ソースを公式サイトからダウンロードし, Go 言語パッケージを構築, 導入するロールです。

## 目次

- [go-lang-local ロール](#go-lang-local-ロール)
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
    - [OSディストリビューション標準のパッケージから導入した場合の確認方法](#osディストリビューション標準のパッケージから導入した場合の確認方法)
      - [Ubuntu24.04環境での実行例](#ubuntu2404環境での実行例)
      - [AlmaLinux9.6環境での実行例](#almalinux96環境での実行例)
    - [公式のソースからDebian/Ubuntu用パッケージ(debパッケージ)を構築して導入した場合の確認方法](#公式のソースからdebianubuntu用パッケージdebパッケージを構築して導入した場合の確認方法)
    - [公式のソースからRHEL/Alma Linux用パッケージ(RPMパッケージ)を構築して導入した場合の確認方法](#公式のソースからrhelalma-linux用パッケージrpmパッケージを構築して導入した場合の確認方法)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. Go導入が実行されず, 警告だけ出て終了する場合](#1-go導入が実行されず-警告だけ出て終了する場合)
    - [2. Go 公式 API 取得で失敗する場合](#2-go-公式-api-取得で失敗する場合)
    - [3. 構築ホストでコンテナイメージ作成/パッケージ構築が失敗する場合](#3-構築ホストでコンテナイメージ作成パッケージ構築が失敗する場合)
    - [4. Go deb/rpm package was not generated for requested version で停止する場合](#4-go-debrpm-package-was-not-generated-for-requested-version-で停止する場合)
    - [5. No go deb/rpm file found in both host and localhost scopes で停止する場合](#5-no-go-debrpm-file-found-in-both-host-and-localhost-scopes-で停止する場合)
    - [6. Fetched go deb/rpm package is missing on controller で停止する場合](#6-fetched-go-debrpm-package-is-missing-on-controller-で停止する場合)
    - [7. Installed Go version mismatch で停止する場合](#7-installed-go-version-mismatch-で停止する場合)
    - [8. チェックモードで導入確認が進まない場合](#8-チェックモードで導入確認が進まない場合)
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
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 構築ホスト | - | パッケージや実行資材を生成するビルド処理を担当するホスト。 |
| Go Programming Language | Go | Google が開発したプログラミング言語。 |
| End Of Life | EOL | サポート終了。公式APIから旧系列版数が返らない場合がある。 |
| Debian package | deb | Debian/Ubuntu 系で使用するパッケージ形式。 |
| RPM Package Manager | RPM | RPM形式パッケージの導入, 更新, 削除, 情報参照を行う仕組み。 |
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Red Hat Enterprise Linux | RHEL | Red Hatが提供する企業向けLinuxディストリビューション。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| Path | PATH | ファイルや実行ファイルの参照先を示す文字列。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `dpkg` | - | Debian パッケージの情報参照や導入確認を行うコマンド。 |
| rpmコマンド | - | RPM パッケージの情報参照や導入確認を行うコマンド。 |
| サイト | - | 情報や機能を公開する場所。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| ローカル | - | 実行中の装置や同一環境の内部。 |
| ローカルパッケージ | - | 外部配布元ではなく, 手元環境で作成または保管した導入用パッケージ。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |

## 概要

本ロールは, 特定の版数のGo言語ソースを公式サイトからダウンロードし, Go 言語パッケージを構築, 導入するロールです。
Go 言語版 Kubernetes client のローカルパッケージ配布は本ロールでは実施せず, `go-k8s-client-local` ロールで実施します。

## 本ロールの動作仕様

本ロールの役割, 動作仕様は以下の通り:

- `go_lang_version` が空文字または未定義: Go の追加導入は行わず, `go_command` を `go_command_package` に設定します。
- `go_lang_version` が指定されている場合: Go 公式 API から導入版数を解決し, `go_build_host` で指定した構築ホスト上のコンテナ内で指定版数の Go をソースビルドしてローカル成果物(deb/rpm)を対象ホストへ配布して導入します。
- 指定版数とビルド結果, さらに導入後の版数が一致しない場合は `fail` で停止します。
- 版数指定形式が, 'x.y'形式の場合, `go_lang_version` が不正形式, または API から解決不能でフォールバックもない場合は, 警告を出してソース導入処理をスキップします。
- 版数指定形式が, 'x.y.z'形式の場合, 無条件に, 指定した版数のダウンロードを試みる(指定版数のソース取得に失敗した場合は, ダウンロード処理失敗によりplaybookの動作が停止する)。
- 本ロールは実行ユーザごとの実効作業ディレクトリ(`/tmp/go-build-<USER>`)を内部で選択して利用します。
- 実効作業ディレクトリへの書き込み確認に失敗した場合は, フォールバック先(`/tmp/go-build-fallback-<USER>`)へ切り替えて継続します。
- 成果物出力先は入力変数で受け取らず, 実効作業ディレクトリ配下の `output` を内部で使用します。

### 本ロールでの処理内容

本ロールでは, `go_lang_version` 指定の有無により以下の処理を行う:

- `go_lang_version` 未指定時: Go の追加導入は行わず, `go_command` を `go_command_package` に設定します。
- `go_lang_version` 指定時: Go 版数を API で解決し, コンテナ内でパッケージを構築後, 制御ノード経由で対象ホストに転送して導入します。

### パッケージ構築～導入までの流れ

`go_lang_version` 指定時の流れは以下の通り:

1. Go 公式 API から版数情報を取得し, 指定形式に応じて導入版数を解決します。
2. 必要に応じて既存の Go パッケージを削除します。
3. 制御ノード上で実効作業ディレクトリを決定し, 書き込み確認を行う(失敗時はフォールバック先へ切り替える)。
4. ビルド用コンテナイメージを Dockerfile から作成します。
5. コンテナ内で Go パッケージ(deb/rpm)を構築します。
6. 成果物の存在確認と版数確認を行う。
7. 構築済みパッケージを構築ホストから制御ノードに回収します。
8. 制御ノードから対象ホストへコピーして導入します。
9. 導入後の `go version` で版数一致を確認します。

`go_lang_version` 未指定時は, 上記のソース導入処理を行わず, `go_command` を `go_command_package` に設定します。

### 導入版数確認方針

`go_lang_version` を指定した場合, 本ロールは以下を確認し, どれか 1 つでも不一致なら失敗で停止する:

1. 解決された版数が指定形式(`x.y` または `x.y.z`)の期待と一致すること。
2. 生成パッケージ(deb/rpm)の版数が解決版数と一致すること。
3. 導入後の `go version` から取得した版数が解決版数と一致すること。

## 前提条件

- 対象ホストが inventory に登録済みであること
- 関連する共通変数が vars/all-config.yml または host_vars に定義済みであること

## 実行方法

制御ホストで以下のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts site.yml --tags "go-lang-local"
```

## 主要変数

本ロールの動作パラメタとなる変数を以下に示す。

| 変数名 | 意味 | 規定値 |
| --- | --- | --- |
| `go_lang_version` | 導入する Go 版数。空/未定義時は Go の追加導入を行わず, 既存環境の `go` コマンドを利用します。指定時は `x.y` または `x.y.z` 形式を想定。 | `""` |
| `go_package_name` | OS 標準 Go パッケージ名。現行の本ロール実装では未使用で, 呼び出し元ロール側の導入処理で利用します。 | `"golang"` |
| `go_lang_remove_existing_package` | 公式のソースから作成したパッケージを導入する前に既存 Go パッケージを削除する指示。 `true`に設定した場合は, パッケージ導入前に既存 Go パッケージを削除します。| `true` |
| `go_build_host` | 公式のソースを元にパッケージ構築処理を実施する際に使用するホスト(構築ホスト)。 | `"localhost"` |
| `go_pkg_build_timeout_seconds` | コンテナイメージ作成/パッケージ構築処理の最大待機時間(単位:秒)。 | `3600` |
| `go_pkg_build_loop_delay_seconds` | 非同期ジョブ監視時のポーリング間隔(単位:秒)。 | `5` |
| `go_install_deb_lock_wait_seconds` | Debian系で dpkg ロック解放を待機する時間(単位:秒)。 | `600` |
| `go_build_container_runtime` | 公式のソースを元にパッケージ構築処理を実施する際に使用するコンテナランタイム。 | `"docker"` |
| `go_build_container_network_mode` | コンテナ実行時のネットワークモード。 | `"host"` |
| `go_build_container_image_debian` | Debian/Ubuntu 向けパッケージ構築作業用コンテナイメージ名。 | `"go-build-ubuntu:24.04"` |
| `go_build_container_image_rhel` | RHEL/AlmaLinux 向けパッケージ構築作業用コンテナイメージ名。 | `"go-build-almalinux:9.6"` |

以下は `vars/cross-distro.yml` から読み込まれる主な関連変数です:

| 変数名 | 意味 | 規定値 |
| --- | --- | --- |
| `go_versions_api` | Go 公式版数 API エンドポイント。 | `"https://go.dev/dl/?mode=json&include=all"` |
| `go_base_url` | Go 公式ダウンロードベース URL。 | `"https://go.dev/dl"` |
| `go_install_dir` | 公式のソースを元にパッケージ構築処理を実施した場合のGo言語導入先ディレクトリのパス。 | `"/usr/local/go"` |
| `go_profile_script` | PATH 付与用の profile.d スクリプト導入先ファイルパス。 | `"/etc/profile.d/golang.sh"` |
| `go_deb_package_name` | ソース導入時の deb パッケージ名。 | `"go-lang"` |
| `go_rpm_package_name` | ソース導入時の rpm パッケージ名。 | `"go-lang"` |
| `go_command_package` | OS 標準パッケージ導入時の go コマンドパス。 | `"/usr/bin/go"` |
| `go_command_from_tarball_path` | 公式のソースを元にパッケージ構築処理を実施した場合の go コマンドパス。`/usr/local/bin/go` (シンボリックリンク)の実体となるコマンド。 | `"/usr/local/go/bin/go"` |
| `go_series_fallback_versions` | End of Life (EOL) 系列向けフォールバック版数マップ。 | `{ "1.25": "1.25.11" }` |

## パッケージ構築関連ファイル一覧

パッケージ構築処理, パッケージ導入処理に関連するファイルは以下の通り:

| ロール内での相対パス | 処理内容 |
| --- | --- |
| `tasks/main.yml` | エントリポイント。本ロールの処理を定義したyamlファイルを読み込む。|
| `tasks/load-params.yml` | OS別/共通変数(`vars/packages-*.yml`, `vars/cross-distro.yml`, `vars/all-config.yml`)を読み込む。 |
| `tasks/package.yml` | Go 導入メイン処理。`go_lang_version` 指定時はソースから構築したパッケージを導入し, 未指定時は `go_command` のみ設定します。 |
| `tasks/resolve-go-version.yml` | Go API 版数解決。`x.y` 系列解決, EOL フォールバック, 不正形式スキップ判定。 |
| `tasks/build-go-source-deb.yml` | Debian/Ubuntu 向け deb パッケージ構築処理。 |
| `tasks/build-go-source-rpm.yml` | RHEL/AlmaLinux 向け rpm パッケージ構築処理。 |
| `tasks/install-go-local-deb.yml` | 構築済み deb の回収, 転送, 導入, 導入版数確認。 |
| `tasks/install-go-local-rpm.yml` | 構築済み rpm の回収, 転送, 導入, 導入版数確認。 |
| `files/resolve_go_latest_patch.py` | API payload から `x.y` 系列の最新 `x.y.z` を抽出する Python スクリプト。 |
| `templates/build-go-deb.sh.j2` | コンテナ内で実行される deb 構築スクリプト。 |
| `templates/build-go-rpm.sh.j2` | コンテナ内で実行される rpm 構築スクリプト。 |
| `templates/Dockerfile.ubuntu.j2` | Debian/Ubuntu 向けパッケージ構築作業用コンテナ定義テンプレート。 |
| `templates/Dockerfile.almalinux.j2` | RHEL/AlmaLinux 向けパッケージ構築作業用コンテナ定義テンプレート。 |

## テンプレートと生成ファイル

本ロールでは以下のテンプレート / ファイルを出力します:
主な展開先ホストは, 構築ホスト , 制御ホスト です。

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `build-go-deb.sh.j2` | 通常: `/tmp/go-build-<実行ユーザ名>/build-go-deb.sh`, フォールバック時: `/tmp/go-build-fallback-<実行ユーザ名>/build-go-deb.sh` | 対象ソフトウェアをソースからビルドし, ローカルパッケージを生成する実行スクリプトです。 |
| `Dockerfile.ubuntu.j2` | 通常: `/tmp/go-build-<実行ユーザ名>/Dockerfile.go-deb`, フォールバック時: `/tmp/go-build-fallback-<実行ユーザ名>/Dockerfile.go-deb` | ローカルパッケージを再現可能にビルドするためのコンテナイメージ定義です。 |
| `build-go-rpm.sh.j2` | 通常: `/tmp/go-build-<実行ユーザ名>/build-go-rpm.sh`, フォールバック時: `/tmp/go-build-fallback-<実行ユーザ名>/build-go-rpm.sh` | 対象ソフトウェアをソースからビルドし, ローカルパッケージを生成する実行スクリプトです。 |
| `Dockerfile.almalinux.j2` | 通常: `/tmp/go-build-<実行ユーザ名>/Dockerfile.go-rpm`, フォールバック時: `/tmp/go-build-fallback-<実行ユーザ名>/Dockerfile.go-rpm` | ローカルパッケージを再現可能にビルドするためのコンテナイメージ定義です。 |

## 実行フロー

1. `load-params.yml` を実行し, OS別パッケージ変数, 共通変数, クロスディストリビューション変数を読み込みます。
2. `go_lang_version` が空文字または未定義の場合は, 追加導入を行わず `go_command` を `go_command_package` に設定して終了します。
3. `go_lang_version` が指定されている場合は `resolve-go-version.yml` を実行し, `x.y` または `x.y.z` 形式に応じて導入版数を解決します。`x.y` 形式で API 解決不能かつフォールバック未定義の場合, または不正形式の場合は警告を出して導入をスキップします。
4. 導入継続時は必要に応じて既存 Go パッケージを削除し, チェックモード時は構築/導入をスキップします。
5. 通常実行時は制御ホスト上で実効作業ディレクトリ(`/tmp/go-build-<実行ユーザ名>`)を決定し, 書き込み不可ならフォールバック先(`/tmp/go-build-fallback-<実行ユーザ名>`)へ切り替えます。
6. 制御ホストで build スクリプトを生成し, `pkgbld-common` を介して構築ホスト上のコンテナで deb/rpm パッケージを構築します。成果物は構築ホスト -> 制御ホスト -> 対象ホストの順で配布して導入します。
7. 導入後は版数検証を実行し, 期待版数と不一致の場合は失敗で停止します。一致時は `go_command` を `go_command_from_tarball_path` に設定します。
8. `directory.yml`, `user_group.yml`, `service.yml`, `config.yml` を順に実行します。現行実装ではこれらのタスクに追加処理定義はありません。

## 検証ポイント

- `go version` の出力版数が期待版数と一致すること。
- `go`コマンドの導入先が期待したパス名と一致すること。
  - `go_lang_version` 未指定時は, `/usr/bin/go` が利用可能であることを確認します。
  - 公式のソースからパッケージを構築して導入している場合は, `/usr/local/go/bin/go`に導入されていることを確認します。
- `dpkg -l` または `rpm -q` 中にGo言語パッケージが含まれ, かつ, 導入されている版数が期待版数と一致すること。
  - OSディストリビューション標準のパッケージから導入した場合は, パッケージ名に`golang`を指定して確認します。
  - 公式のソースからパッケージを構築して導入している場合は, パッケージ名に`go-lang`を指定して確認します。

### OSディストリビューション標準のパッケージから導入した場合の確認方法

`go_lang_version` を未指定で利用する場合は, 呼び出し元ロールで OSディストリビューション標準のパッケージから導入済みである前提となるため,
以下のコマンドを実行し, `go`コマンドの導入先, `go`コマンドの版数, 導入されている`golang` パッケージの版数を確認します。

```shell
which go
go version
dpkg -l | egrep golang  # Ubuntu
# または
rpm -qa | egrep golang   # RHEL
```

#### Ubuntu24.04環境での実行例

Ubuntu24.04環境での実行例を以下に示す:

```shell
$ which go
/usr/bin/go
$ go version
go version go1.22.2 linux/amd64
$ dpkg -l|egrep golang
ii  golang:amd64                                     2:1.22~2build1                                   amd64        Go programming language compiler - metapackage
ii  golang-1.22                                      1.22.2-2ubuntu0.4                                all          Go programming language compiler - metapackage
ii  golang-1.22-doc                                  1.22.2-2ubuntu0.4                                all          Go programming language - documentation
ii  golang-1.22-go                                   1.22.2-2ubuntu0.4                                amd64        Go programming language compiler, linker, compiled stdlib
ii  golang-1.22-src                                  1.22.2-2ubuntu0.4                                all          Go programming language - source files
ii  golang-doc                                       2:1.22~2build1                                   all          Go programming language - documentation
ii  golang-go:amd64                                  2:1.22~2build1                                   amd64        Go programming language compiler, linker, compiled stdlib
ii  golang-src                                       2:1.22~2build1                                   all          Go programming language - source files
```

#### AlmaLinux9.6環境での実行例

AlmaLinux9.6環境での実行例を以下に示す:

```shell
$ which go
/usr/bin/go
$ go version
go version go1.26.3 (Red Hat 1.26.3-1.el9_8) linux/amd64
$ rpm -qa|egrep golang
golang-src-1.26.3-1.el9_8.noarch
golang-bin-1.26.3-1.el9_8.x86_64
golang-race-1.26.3-1.el9_8.x86_64
golang-1.26.3-1.el9_8.x86_64
```

### 公式のソースからDebian/Ubuntu用パッケージ(debパッケージ)を構築して導入した場合の確認方法

公式のソースからdebパッケージを構築して導入している場合は,
以下のコマンドを実行し, `go`コマンドの導入先, `go`コマンドの版数, 導入されている`go-lang` パッケージの版数を確認します。

```shell
which go
/usr/local/go/bin/go version
dpkg -l|egrep go-lang
```

実行例を以下に示す:

```shell
$ which go
/usr/local/go/bin/go
$ /usr/local/go/bin/go version
go version go1.25.11 linux/amd64
$ dpkg -l|egrep go-lang
ii  go-lang                                          1.25.11-1                                  amd64        Go language toolchain 1.25.11
```

### 公式のソースからRHEL/Alma Linux用パッケージ(RPMパッケージ)を構築して導入した場合の確認方法

公式のソースからRPMパッケージを構築して導入している場合は,
以下のコマンドを実行し, `go`コマンドの導入先, `go`コマンドの版数, 導入されている`go-lang` パッケージの版数を確認します。

```shell
which go
/usr/local/go/bin/go version
rpm -qa|egrep go-lang
```

実行例を以下に示す:

```shell
$ which go
/usr/local/go/bin/go
$ /usr/local/go/bin/go version
go version go1.25.11 linux/amd64
$ rpm -qa|egrep go-lang
go-lang-1.25.11-1.el9.x86_64
```

## トラブルシューティング

### 1. Go導入が実行されず, 警告だけ出て終了する場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
grep -n "go_lang_version\|go_series_fallback_versions" vars/cross-distro.yml vars/all-config.yml host_vars/*/main.yml
```

**確認ポイント**:

- `go_lang_version` が `x.y` または `x.y.z` 形式であること。
- `x.y` 形式で API 解決不能の場合, `go_series_fallback_versions` に対象系列が定義されていること。

### 2. Go 公式 API 取得で失敗する場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
curl -fsS "https://go.dev/dl/?mode=json&include=all" | head -c 300
getent hosts go.dev
```

**確認ポイント**:

- 制御ホストから `https://go.dev/dl/?mode=json&include=all` へ到達できること。
- `go.dev` の名前解決ができること。
- プロキシ環境の場合, Playbook 実行環境へプロキシ設定を反映していること。

### 3. 構築ホストでコンテナイメージ作成/パッケージ構築が失敗する場合

**実施対象ホスト**: 構築ホスト, 制御ホスト

**実行するコマンド**:

```bash
docker version
ansible -i inventory/hosts <go_build_host> -m ping
grep -n "go_build_host\|go_build_container_runtime" vars/all-config.yml host_vars/*/main.yml
```

**確認ポイント**:

- 構築ホストでコンテナランタイムが動作すること。
- `go_build_host` が到達可能であること。
- `go_build_container_runtime` と実行可能コマンドが一致していること。

### 4. Go deb/rpm package was not generated for requested version で停止する場合

**実施対象ホスト**: 構築ホスト, 制御ホスト

**実行するコマンド**:

```bash
ls -la /tmp/go-build-*/output
ls -1 build-*.log
grep -n "Go deb/rpm package was not generated for requested version" build-*.log
```

**確認ポイント**:

- `/tmp/go-build-<実行ユーザ名>/output` とフォールバック先 `output` に成果物が生成されていること。
- `build-*.log` の該当 task で失敗工程を特定できること。
- ダウンロード, 展開, ビルドのいずれで失敗したか切り分けていること。

### 5. No go deb/rpm file found in both host and localhost scopes で停止する場合

**実施対象ホスト**: 構築ホスト, 制御ホスト

**実行するコマンド**:

```bash
ls -la /tmp/go-build-*/output
grep -n "No go deb/rpm file found in both host and localhost scopes" build-*.log
grep -n "go_build_host" vars/all-config.yml host_vars/*/main.yml
```

**確認ポイント**:

- 構築ホストの成果物ディレクトリに対象版数のファイルが存在すること。
- 成果物回収前にファイルが消えていないこと。
- `go_build_host` が意図したホスト名と一致していること。

### 6. Fetched go deb/rpm package is missing on controller で停止する場合

**実施対象ホスト**: 制御ホスト, 構築ホスト

**実行するコマンド**:

```bash
ls -la ~/.ansible/tmp
df -h
grep -n "Fetched go deb/rpm package is missing on controller" build-*.log
```

**確認ポイント**:

- 制御ホストの `~/.ansible/tmp` 配下に一時ディレクトリが作成されていること。
- 制御ホストのディスク空き容量と書き込み権限に問題がないこと。
- 構築ホストから制御ホストへの `fetch` 失敗がログで確認できること。

### 7. Installed Go version mismatch で停止する場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
/usr/local/go/bin/go version
which go
go version
```

**確認ポイント**:

- 生成パッケージ版数と導入後バイナリ版数が一致していること。
- `which go` の参照先が意図した導入先であること。
- 旧版が優先参照される場合は `go_lang_remove_existing_package: true` で再実行して解消できること。

### 8. チェックモードで導入確認が進まない場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
ansible-playbook -i inventory/hosts devel.yml --tags go-lang-local --check -vv
```

**確認ポイント**:

- `--check` 実行時は仕様としてビルド/導入処理をスキップすること。
- 成果物生成, 導入, 版数一致確認を行う場合は `--check` を外して通常実行していること。

## 注意事項

- ソースビルドは `go_build_host` で指定した構築ホスト上でコンテナランタイム(Docker)が利用可能であることを前提とします。
- 本ロールから構築したパッケージに対する署名付与は行わない。
- `go_lang_version` を指定する場合, 制御ノードから `go_versions_api` で指定したへGo 公式サイト (`https://go.dev/dl/`) へのネットワークアクセスが必須となる。
- `--check` 実行時は版数解決のみ行い, ビルド/導入はスキップします。

## 参考資料

### 公式ドキュメント

- [Go Programming Language](https://go.dev/doc/)
