# jd ロール

本ロールは, JavaScript Object Notation (JSON) および Yet Another Markup Language (YAML) の差分比較とパッチ適用を行うコマンドラインツールである jd コマンドをソースコードから構築し, ローカルパッケージ(deb/rpm)として対象ホストへ導入します。

## 目次

- [jd ロール](#jd-ロール)
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
| API | - | アプリケーション同士がやり取りする方法を定めた仕様。 |
| URL | - | WWW 上の資源の場所を示す文字列。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 構築ホスト | - | パッケージや実行資材を生成するビルド処理を担当するホスト。 |
| Debian package | deb | Debian/Ubuntu 系で使用するパッケージ形式。 |
| RPM Package Manager | RPM | RHEL/AlmaLinux 系で使用するパッケージ形式。 |
| JavaScript Object Notation | JSON | 人間が読みやすいテキスト形式のデータ交換フォーマット。キーと値のペアで構成され, 設定ファイルやAPI レスポンスに広く使用される。 |
| Yet Another Markup Language | YAML | 設定ファイル形式です。 |
| Red Hat Enterprise Linux | RHEL | Red Hat 社が提供する商用 Linux ディストリビューション。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `dpkg` | - | Debian パッケージの情報参照や導入確認を行うコマンド。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| `make` | - | Makefile に定義された処理を実行するコマンド。 |
| rpmコマンド | - | RPM パッケージの情報参照や導入確認を行うコマンド。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| ローカルパッケージ | - | 外部配布元ではなく, 手元環境で作成または保管した導入用パッケージ。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |

## 概要
本ロールでは, JavaScript Object Notation (JSON) および Yet Another Markup Language (YAML) の差分比較とパッチ適用を行うコマンドラインツールである jd コマンドをソースコードから構築し, ローカルパッケージ(deb/rpm)として対象ホストへ導入します。

## 動作仕様

- `jd_enabled` が `false` の場合, 本ロールは導入処理をスキップします。
- `jd_enabled` が `true` の場合, `jd_version` の値を使って導入処理を実行します。
- `jd_version` が指定されている場合, `vX.Y.Z` または `X.Y.Z` を受け付ける。
- `jd_completion_enabled` が `true` の場合, パッケージに bash/zsh 補完ファイルを同梱して導入します。
- 版数指定時は, `pkgbld-common` を使って以下を実施します。
  - 構築ホスト上のコンテナ内で jd ソースビルド
  - deb/rpm パッケージ生成
  - 制御ノード経由で対象ホストへ配布して導入
  - `jd --version` の結果が指定版数と一致することを検証

## 前提条件

- 対象ホストが inventory に登録済みであること
- 関連する共通変数が vars/all-config.yml または host_vars に定義済みであること

## 実行方法

1. `vars/all-config.yml` などで `jd_enabled`, `jd_version` を指定します:
    ```yaml
    jd_enabled: true
    jd_version: "v2.5.0"
    ```
2. 制御ホストで以下のコマンドを実行します。
    ```bash
    make run_jd
    ```
    または,
    ```bash
    ansible-playbook -i inventory/hosts site.yml --tags "jd"
    ```

## 主要変数

| 変数名 | 意味 | 規定値 |
| --- | --- | --- |
| `jd_enabled` | jd ロール実行フラグ。`true` の場合に導入処理を実行します。 | `false` |
| `jd_version` | 導入する jd 版数。`vメジャー版数.マイナー版数.リビジョン` または `メジャー版数.マイナー版数.リビジョン` 形式。 | `"v2.5.0"` |
| `jd_completion_enabled` | bash/zsh 補完ファイル同梱有無。`true` の場合に補完を同梱します。 | `true` |
| `jd_build_host` | パッケージ構築ホスト。 | `"localhost"` |
| `jd_build_container_runtime` | コンテナランタイム。 | `"docker"` |
| `jd_build_container_network_mode` | コンテナネットワークモード。 | `"host"` |
| `jd_build_container_image_debian` | Debian向けビルド用コンテナイメージ。 | `"ubuntu:24.04"` |
| `jd_build_container_image_rhel` | RHEL向けビルド用コンテナイメージ。 | `"almalinux:9.6"` |
| `jd_pkg_build_timeout_seconds` | ビルド待機タイムアウト秒数。 | `3600` |
| `jd_pkg_build_loop_delay_seconds` | ビルド監視ポーリング間隔秒数。 | `5` |
| `jd_install_deb_lock_wait_seconds` | Debian系導入時のロック待機秒数。 | `600` |
| `jd_remove_existing_package` | 既存 jd パッケージ削除有無。 | `true` |

## テンプレートと生成ファイル

本ロールでは以下のテンプレート / ファイルを出力します:

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `build-jd-deb.sh.j2` | 一時ファイル(制御ホスト): 通常 `/tmp/jd-build-実行ユーザ名/build-jd-deb.sh`, 代替 `/tmp/jd-build-fallback-実行ユーザ名/build-jd-deb.sh` | Debian系ローカルパッケージ生成スクリプトです。対象ホストへの最終展開先はありません(構築ホストでパッケージ生成時のみ使用)。 |
| `build-jd-rpm.sh.j2` | 一時ファイル(制御ホスト): 通常 `/tmp/jd-build-実行ユーザ名/build-jd-rpm.sh`, 代替 `/tmp/jd-build-fallback-実行ユーザ名/build-jd-rpm.sh` | RHEL系ローカルパッケージ生成スクリプトです。対象ホストへの最終展開先はありません(構築ホストでパッケージ生成時のみ使用)。 |
| `jd.bash-completion.j2` | 一時ファイル(制御ホスト): 通常 `/tmp/jd-build-実行ユーザ名/jd.bash-completion`, 代替 `/tmp/jd-build-fallback-実行ユーザ名/jd.bash-completion` | 構築ホストへ同名で一時転送後, 対象ホストへ `/usr/share/bash-completion/completions/jd` として導入されます。 |
| `jd.zsh-completion.j2` | 一時ファイル(制御ホスト): 通常 `/tmp/jd-build-実行ユーザ名/jd.zsh-completion`, 代替 `/tmp/jd-build-fallback-実行ユーザ名/jd.zsh-completion` | 構築ホストへ同名で一時転送後, 対象ホストへ Debian/Ubuntu では `/usr/share/zsh/vendor-completions/_jd`, RHEL/AlmaLinux では `/usr/share/zsh/site-functions/_jd` として導入されます。 |

## 実行フロー

1. 実行者が load-params.yml により変数を読み込む。
2. 実行者が本ロール固有の task を順次実行します。
3. 実行者が検証コマンドを実行して期待結果を確認します。

## 検証ポイント

以下を対象ホスト上で確認します。

- 導入されたjdの格納パスと版数
- 導入されたjdのパッケージ(jd-local)の導入状態
- シェル補完ファイルの格納先

### Debian/Ubuntu環境での確認方法

Debian/Ubuntu環境の場合, 以下のコマンドを実行する:

```bash
which jd
jd --version
dpkg -l | grep jd-local
ls -l /usr/share/bash-completion/completions/jd
ls -l /usr/share/zsh/vendor-completions/_jd
```

実行結果の例:
```bash
$ which jd
/usr/local/bin/jd
$ jd --version
jd version 2.5.0
$ dpkg -l | grep jd-local
ii  jd-local                              2.5.0-1                                 amd64        jd command line JSON/YAML diff and patch tool v2.5.0
$ ls -l /usr/share/bash-completion/completions/jd
-rw-r--r-- 1 root root 875  7月 31 19:43 /usr/share/bash-completion/completions/jd
$ ls -l /usr/share/zsh/vendor-completions/_jd
-rw-r--r-- 1 root root 831  7月 31 19:43 /usr/share/zsh/vendor-completions/_jd
```

### RHEL/AlmaLinux環境での確認方法

RHEL/AlmaLinux環境の場合, 以下のコマンドを実行する:

```bash
which jd
jd --version
rpm -qa | grep jd-local
ls -l /usr/share/bash-completion/completions/jd
ls -l /usr/share/zsh/site-functions/_jd
```

実行結果の例:
```bash
$ which jd
/usr/local/bin/jd
$ jd --version
jd version 2.5.0
$ rpm -qa | grep jd-local
jd-local-2.5.0-1.el9.x86_64
$ ls -l /usr/share/bash-completion/completions/jd
-rw-r--r--. 1 root root 875 Jul 31 19:44 /usr/share/bash-completion/completions/jd
$ ls -l /usr/share/zsh/site-functions/_jd
-rw-r--r--. 1 root root 831 Jul 31 19:44 /usr/share/zsh/site-functions/_jd
```

## トラブルシューティング

代表的なトラブルと対処を以下に示します。

| 想定トラブル | 主な原因 | 対処方法 |
| --- | --- | --- |
| ロール実行後も `jd` が導入されない | `jd_enabled` が `false` のままで, `package.yml` がスキップされている | 実行者は `vars/all-config.yml` または `host_vars` で `jd_enabled: true` を設定し, Ansible 出力で `Package` タスクが `skipping` になっていないことを確認して再実行します。 |
| `Validate jd version format` で失敗する | `jd_version` が `vX.Y.Z` または `X.Y.Z` 形式ではない | 実行者は `jd_version` を `v2.5.0` のような形式へ修正して再実行します。 |
| ローカルパッケージ構築でタイムアウトする | 構築ホストの性能不足, ネットワーク遅延, イメージ取得遅延により `jd_pkg_build_timeout_seconds` 内で完了しない | 実行者は `build-*.log` を確認して停滞箇所を特定し, 必要に応じて `jd_pkg_build_timeout_seconds` を増やした上で再実行します。 |
| `Build and install jd local packages via pkgbld-common` で失敗する | `jd_build_host` への接続不可, `jd_build_container_runtime` コマンド未導入, ビルド用イメージ取得失敗 | 実行者は構築ホストで `docker --version` などランタイムの動作確認と, `ubuntu:24.04` / `almalinux:9.6` の取得可否を確認します。必要に応じてランタイム, イメージ, 接続設定を見直して再実行します。 |
| Debian/Ubuntu 系でパッケージ導入がロック待ち失敗する | `apt` ロック競合が `jd_install_deb_lock_wait_seconds` (既定: `600`) を超えて継続している | 実行者は対象ホストで他の `apt` 実行を終了させ, `jd_install_deb_lock_wait_seconds` を必要に応じて延長して再実行します。 |
| 補完ファイルが配置されない | `jd_completion_enabled` が `false` で補完同梱が無効になっている, または構築ホストへの補完ファイル転送に失敗している | 実行者は `jd_completion_enabled: true` を設定し, 構築ホスト上の `/tmp/jd-build-実行ユーザ名/jd.bash-completion` と `/tmp/jd-build-実行ユーザ名/jd.zsh-completion` の存在を確認して再実行します。 |
| `jd --version` 検証で版数不一致になる | 既存の別バイナリが優先されている, または構築版数と `jd_version` 指定値が一致していない | 実行者は `which jd` と `jd --version` を確認し, 既存導入物の影響がある場合は `jd_remove_existing_package: true` のまま再実行します。必要に応じて `PATH` 上の重複バイナリを整理します。 |


## 注意事項

- Debian/Ubuntu系とRHEL系で同じバイナリを導入するため, 公式ソースコードからバイナリを構築してパッケージ化しています。
- 構築ホストではコンテナランタイム(`docker`)が動作し, `ubuntu:24.04` と `almalinux:9.6` の取得が可能であることを事前に確認してください。
- 補完ファイルは jd 本体から自動生成するのではなく, ロール内テンプレート(`jd.bash-completion.j2`, `jd.zsh-completion.j2`)を同梱しています。テンプレートを更新する場合は LF 改行を維持し, CRLF にしないでください。
- `--check` 実行時はローカルパッケージの構築/導入をスキップします。導入可否の最終確認は通常実行で行ってください。


## 参考資料

### 公式ドキュメント

- [josephburnett/jd Githubサイト](https://github.com/josephburnett/jd)
