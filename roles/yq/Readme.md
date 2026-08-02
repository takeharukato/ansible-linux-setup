# yq ロール

本ロールは, Yet Another Markup Language (YAML), JavaScript Object Notation (JSON), Extensible Markup Language (XML)などを処理するためのコマンドラインツールである yq コマンドをソースコードから構築し, ローカルパッケージ(deb/rpm)として対象ホストへ導入します。

## 目次

- [yq ロール](#yq-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [動作仕様](#動作仕様)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
      - [Debian/Ubuntu環境での確認方法](#debianubuntu環境での確認方法)
      - [RHEL/AlmaLinux環境での確認方法](#rhelalmalinux環境での確認方法)
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
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 構築ホスト | - | パッケージや実行資材を生成するビルド処理を担当するホスト。 |
| Debian package | deb | Debian/Ubuntu 系で使用するパッケージ形式。 |
| RPM Package Manager | RPM | RHEL/AlmaLinux 系で使用するパッケージ形式。 |
| コンテナ ( Container ) | - | アプリケーションと依存関係を一つのパッケージ化したもの。軽量で, どの環境でも一貫して実行可能。 |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウェア。 |
| Yet Another Markup Language | YAML | 設定ファイル形式です。 |
| JavaScript Object Notation | JSON | 人間が読みやすいテキスト形式のデータ交換フォーマット。キーと値のペアで構成され, 設定ファイルやAPI レスポンスに広く使用される。 |
| Extensible Markup Language | XML | 構造を持ったデータを記述するための拡張可能なマークアップ言語のこと。 |
| Red Hat Enterprise Linux | RHEL | Red Hat 社が提供する商用 Linux ディストリビューション。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `dpkg` | - | Debian パッケージの情報参照や導入確認を行うコマンド。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| `make` | - | Makefile に定義された処理を実行するコマンド。 |
| rpmコマンド | - | RPM パッケージの情報参照や導入確認を行うコマンド。 |
| `yq` | - | YAML を抽出, 変換, 更新するコマンド。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| ローカルパッケージ | - | 外部配布元ではなく, 手元環境で作成または保管した導入用パッケージ。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |

## 概要
本ロールでは, Yet Another Markup Language (YAML), JavaScript Object Notation (JSON), Extensible Markup Language (XML)などを処理するためのコマンドラインツールである yq コマンドをソースコードから構築し, ローカルパッケージ(deb/rpm)として対象ホストへ導入します。

本ロールは, yq に関する設定処理を実施します。

## 動作仕様

- `yq_enabled` が `false` の場合, 本ロールは導入処理をスキップします。
- `yq_enabled` が `true` の場合, `yq_version` の値を使って導入処理を実行します。
- `yq_version` が指定されている場合, `vX.Y.Z` または `X.Y.Z` を受け付ける。
- `yq_completion_enabled` が `true` の場合, パッケージに bash/zsh 補完ファイルを同梱して導入します。
- 版数指定時は, `pkgbld-common` を使って以下を実施します。
	- 構築ホスト上のコンテナ内で yq ソースビルド
	- deb/rpm パッケージ生成
	- 制御ノード経由で対象ホストへ配布して導入
	- `yq --version` の結果が指定版数と一致することを検証

## 前提条件

- 対象ホストが inventory に登録済みであること
- 関連する共通変数が vars/all-config.yml または host_vars に定義済みであること

## 実行方法

1. `vars/all-config.yml` などで `yq_enabled`, `yq_version` を指定します:
    ```yaml
    yq_enabled: true
    yq_version: "v4.47.1"
    ```
2. 制御ホストで以下のコマンドを実行します:
    ```bash
    make run_yq
    ```
    または,
    ```bash
    ansible-playbook -i inventory/hosts site.yml --tags "yq"
    ```

## 主要変数

| 変数名 | 意味 | 規定値 |
| --- | --- | --- |
| `yq_enabled` | yq ロール実行フラグ。`true` の場合に導入処理を実行します。 | `false` |
| `yq_version` | 導入する yq 版数。 `vメジャー版数.マイナー版数.リビジョン` または `メジャー版数.マイナー版数.リビジョン` 形式。 | `"v4.47.1"` |
| `yq_completion_enabled` | bash/zsh 補完ファイル同梱有無。`true` の場合に補完を同梱します。 | `true` |
| `yq_build_host` | パッケージ構築ホスト。 | `"localhost"` |
| `yq_build_container_runtime` | コンテナランタイム。 | `"docker"` |
| `yq_build_container_network_mode` | コンテナネットワークモード。 | `"host"` |
| `yq_build_container_image_debian` | Debian向けビルド用コンテナイメージ。 | `"ubuntu:24.04"` |
| `yq_build_container_image_rhel` | RHEL向けビルド用コンテナイメージ。 | `"almalinux:9.6"` |
| `yq_pkg_build_timeout_seconds` | ビルド待機タイムアウト秒数。 | `3600` |
| `yq_pkg_build_loop_delay_seconds` | ビルド監視ポーリング間隔秒数。 | `5` |
| `yq_install_deb_lock_wait_seconds` | Debian系導入時のロック待機秒数。 | `600` |
| `yq_remove_existing_package` | 既存 yq パッケージ削除有無。 | `true` |
| `yq_bash_completion_path` | bash 補完配置先。Debian/RHEL 共通。 | `"/usr/share/bash-completion/completions/yq"` |
| `yq_zsh_completion_path` | zsh 補完配置先。Debian は vendor-completions, RHEL は site-functions。 | Debian: `"/usr/share/zsh/vendor-completions/_yq"`, RHEL: `"/usr/share/zsh/site-functions/_yq"` |

## テンプレートと生成ファイル

本ロールでは以下のテンプレート / ファイルを出力します:
主な展開先ホストは, 制御ホスト です。

| テンプレートファイル名 | 出力先パス (規定) | 説明 |
| --- | --- | --- |
| `build-yq-deb.sh.j2` | 一時ファイル(制御ホスト): 通常 `/tmp/yq-build-実行ユーザ名/build-yq-deb.sh`, 代替 `/tmp/yq-build-fallback-実行ユーザ名/build-yq-deb.sh` | Debian系ローカルパッケージ生成スクリプトです。|
| `build-yq-rpm.sh.j2` | 一時ファイル(制御ホスト): 通常 `/tmp/yq-build-実行ユーザ名/build-yq-rpm.sh`, 代替 `/tmp/yq-build-fallback-実行ユーザ名/build-yq-rpm.sh` | RHEL系ローカルパッケージ生成スクリプトです。|

## 実行フロー

本ロールは以下の順序で処理を実行します。`yq_enabled: true` でない場合, `load-params.yml` を除くタスクをスキップします。

1. **パラメータ読み込み**(`load-params.yml`): ディストリビューション別パッケージ定義, 共通設定, クロスディストリビューション設定を読み込みます。
2. **パッケージ処理**(`package.yml`): `yq_version` 形式を検証し, 既存パッケージ削除, 構築ワークスペース準備, `build-yq-deb.sh` / `build-yq-rpm.sh` 生成, `pkgbld-common` によるローカルパッケージ構築と導入, `yq --version` 検証を実行します。
3. **ファイル/ディレクトリ処理**(`directory.yml`): 現在の実装では追加処理を定義していないため, 実行時の変更は発生しません。
4. **ユーザ/グループ処理**(`user_group.yml`): 現在の実装では追加処理を定義していないため, 実行時の変更は発生しません。
5. **サービス処理**(`service.yml`): 現在の実装では追加処理を定義していないため, 実行時の変更は発生しません。
6. **設定処理**(`config.yml`): 現在の実装では追加処理を定義していないため, 実行時の変更は発生しません。


## 検証ポイント

以下の点を確認する:

- 導入されたyqの格納パスと版数
- 導入されたyqのパッケージ(yq-local)の導入状態
- シェル補完ファイルの格納先

#### Debian/Ubuntu環境での確認方法

Debian/Ubuntu環境の場合, 以下のコマンドを実行する:

```bash
which yq
yq --version
dpkg -l | grep yq-local
ls -l /usr/share/bash-completion/completions/yq
ls -l /usr/share/zsh/vendor-completions/_yq
```

Debian/Ubuntu環境での実行例:
```bash
$ which yq
/usr/local/bin/yq
$ yq --version
yq (https://github.com/mikefarah/yq/) version v4.47.1
$ dpkg -l | grep yq-local
ii  yq-local                              4.47.1-1                                amd64        yq command line YAML processor v4.47.1
$ ls -l /usr/share/bash-completion/completions/yq
-rw-r--r-- 1 root root 15913  7月 31 12:08 /usr/share/bash-completion/completions/yq
$ ls -l /usr/share/zsh/vendor-completions/_yq
-rw-r--r-- 1 root root 7604  7月 31 12:08 /usr/share/zsh/vendor-completions/_yq
```

#### RHEL/AlmaLinux環境での確認方法

RHEL/AlmaLinux環境の場合, 以下のコマンドを実行する:

```bash
which yq
yq --version
rpm -qa | grep yq-local
ls -l /usr/share/bash-completion/completions/yq
ls -l /usr/share/zsh/site-functions/_yq
```

RHEL/AlmaLinux環境での実行例:
```bash
$ which yq
/usr/local/bin/yq
$ yq --version
yq (https://github.com/mikefarah/yq/) version v4.47.1
$ rpm -qa | grep yq-local
yq-local-4.47.1-1.el9.x86_64
$ ls -l /usr/share/bash-completion/completions/yq
-rw-r--r--. 1 root root 15913 Jul 31 12:09 /usr/share/bash-completion/completions/yq
$ ls -l /usr/share/zsh/site-functions/_yq
-rw-r--r--. 1 root root 7604 Jul 31 14:23 /usr/share/zsh/site-functions/_yq
```

## トラブルシューティング

代表的なトラブルと対処を以下に示します。

| 想定トラブル | 主な原因 | 対処方法 |
| --- | --- | --- |
| ロール実行後も `yq` が導入されない | `yq_enabled` が `false` のままで, `package.yml` がスキップされている | 実行者は `vars/all-config.yml` または `host_vars` で `yq_enabled: true` を設定し, Ansible 出力で `Package` タスクが `skipping` になっていないことを確認して再実行します。 |
| `Validate yq version format` で失敗する | `yq_version` が `vX.Y.Z` または `X.Y.Z` 形式ではない | 実行者は `yq_version` を `v4.47.1` のような形式へ修正して再実行します。 |
| ローカルパッケージ構築でタイムアウトする | 構築ホストの性能不足, ネットワーク遅延, イメージ取得遅延により `yq_pkg_build_timeout_seconds` 内で完了しない | 実行者は `build-*.log` を確認して停滞箇所を特定し, 必要に応じて `yq_pkg_build_timeout_seconds` を増やした上で再実行します。 |
| `Build and install yq local packages via pkgbld-common` で失敗する | `yq_build_host` への接続不可, `yq_build_container_runtime` コマンド未導入, ビルド用イメージ取得失敗 | 実行者は構築ホストで `docker --version` などランタイムの動作確認と, `ubuntu:24.04` / `almalinux:9.6` の取得可否を確認します。必要に応じてランタイム, イメージ, 接続設定を見直して再実行します。 |
| Debian/Ubuntu 系でパッケージ導入がロック待ち失敗する | `apt` ロック競合が `yq_install_deb_lock_wait_seconds` (既定: `600`) を超えて継続している | 実行者は対象ホストで他の `apt` 実行を終了させ, `yq_install_deb_lock_wait_seconds` を必要に応じて延長して再実行します。 |
| 補完ファイルが配置されない | `yq_completion_enabled` が `false` で補完同梱が無効になっている | 実行者は `yq_completion_enabled: true` を設定して再実行し, Debian では `/usr/share/zsh/vendor-completions/_yq`, RHEL では `/usr/share/zsh/site-functions/_yq` を確認します。 |
| `yq --version` 検証で版数不一致になる | 既存の別バイナリが優先されている, または構築版数と `yq_version` 指定値が一致していない | 実行者は `which yq` と `yq --version` を確認し, 既存導入物の影響がある場合は `yq_remove_existing_package: true` のまま再実行します。必要に応じて `PATH` 上の重複バイナリを整理します。 |

## 注意事項

- Debian/Ubuntu系とRHEL系とで同じバイナリを導入するため, 公式のソースコードからバイナリファイルを構築して, パッケージを生成しています。このため, RHEL系では, RHEL固有のパッチなどが適用されていないことを留意してください。
- 構築ホストではコンテナランタイム(`docker`)が動作し, `ubuntu:24.04` と `almalinux:9.6` の取得が可能であることを事前に確認してください。

## 参考資料

### 公式ドキュメント

- [yq](https://github.com/mikefarah/yq)
