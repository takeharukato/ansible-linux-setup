# go-k8s-client-local ロール

本ロールは, Go 言語版 Kubernetes client (client-go) を対象ノード上で直接 `go get` せずに, 構築ホスト上のコンテナでローカルパッケージ (deb/rpm) を生成して配布, 導入するロールです。

## 目次

- [go-k8s-client-local ロール](#go-k8s-client-local-ロール)
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
| Application Programming Interface | API | API の正式名称。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `grep` | - | テキストから条件に一致する行を抽出するコマンド。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| オフライン | - | ネットワーク未接続で動作する状態。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| オフライン開発キット | - | 外部ネットワーク接続なしで開発や検証を行うために必要な資材一式。 |
| ローカルパッケージ | - | 外部配布元ではなく, 手元環境で作成または保管した導入用パッケージ。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| 構築ホスト | - | パッケージや実行資材を生成するビルド処理を担当するホスト。 |

## 概要

本ロールは, Go 言語版 Kubernetes client (client-go) を対象ノード上で直接 `go get` せずに, 構築ホスト上のコンテナでローカルパッケージ (deb/rpm) を生成して配布, 導入するロールです。

- 入力として `go_k8s_client_version` (例: `v0.31.0`) を受け取り, オフライン開発キット (`go.mod`, `go.sum`, `vendor/`) を含むローカルパッケージを作成します。
- ローカルパッケージの転送経路は, 構築ホスト -> 制御ノード -> 対象ホストです。
- 導入後に, `go.mod` 内の `k8s.io/client-go` 版数を検証します。

## 前提条件

- 対象 OS: Debian/Ubuntu系, RHEL系。
- 構築ホストでコンテナランタイム (`docker` など) が利用可能であること。
- 対象ホスト側では Go 言語パッケージ (`golang`/`golang-go`/`go-lang`) が導入済みであること。
- `go_k8s_client_version` は `vX.Y.Z` 形式で指定すること。

## 実行方法

制御ホストで以下のコマンドを実行します:
```bash
make run_k8s_devel
```
または,
```bash
ansible-playbook -i inventory/hosts site.yml --tags "go-k8s-client-local"
```

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `go_k8s_client_version` | `""` | client-go の版数。`vX.Y.Z` 形式で指定します。 |
| `go_k8s_client_module_domain` | `dns_domain` または `"example.org"` | `go mod init` で使用するドメイン。 |
| `go_k8s_client_install_dir` | `"/opt/k8s-devel/go-client"` | オフラインキット導入先。 |
| `go_k8s_client_build_host` | `"localhost"` | 構築ホスト。 |
| `go_k8s_client_deb_package_name` | `"go-k8s-client"` | Debian系ローカルパッケージ名。 |
| `go_k8s_client_rpm_package_name` | `"go-k8s-client"` | RHEL系ローカルパッケージ名。 |

構築ワークスペースは入力変数ではなく, タスク内で実行ユーザごとに `/tmp/go-k8s-client-build-<USER>` を自動選択します。

## テンプレートと生成ファイル

本ロールでは以下のテンプレート / ファイルを出力します:
主な展開先ホストは, 構築ホスト , 制御ホスト です。

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `build-k8s-client-go-deb.sh.j2` | `/tmp/go-k8s-client-build-<実行ユーザ名>/build-k8s-client-go-deb.sh` (既定: `/tmp/go-k8s-client-build-<実行ユーザ名>/build-k8s-client-go-deb.sh`) | 対象ソフトウェアをソースからビルドし, ローカルパッケージを生成する実行スクリプトです。 |
| `Dockerfile.ubuntu.j2` | `/tmp/go-k8s-client-build-<実行ユーザ名>/Dockerfile.go-k8s-client-deb` (既定: `/tmp/go-k8s-client-build-<実行ユーザ名>/Dockerfile.go-k8s-client-deb`) | ローカルパッケージを再現可能にビルドするためのコンテナイメージ定義です。 |
| `build-k8s-client-go-rpm.sh.j2` | `/tmp/go-k8s-client-build-<実行ユーザ名>/build-k8s-client-go-rpm.sh` (既定: `/tmp/go-k8s-client-build-<実行ユーザ名>/build-k8s-client-go-rpm.sh`) | 対象ソフトウェアをソースからビルドし, ローカルパッケージを生成する実行スクリプトです。 |
| `Dockerfile.almalinux.j2` | `/tmp/go-k8s-client-build-<実行ユーザ名>/Dockerfile.go-k8s-client-rpm` (既定: `/tmp/go-k8s-client-build-<実行ユーザ名>/Dockerfile.go-k8s-client-rpm`) | ローカルパッケージを再現可能にビルドするためのコンテナイメージ定義です。 |

## 実行フロー

1. `load-params.yml` で OS別/共通変数を読み込む。
2. `package.yml` で版数形式を検証します。
3. Debian系では `build-client-go-source-deb.yml` でコンテナ内ビルドを行い, `install-client-go-local-deb.yml` で導入します。
4. RHEL系では `build-client-go-source-rpm.yml` でコンテナ内ビルドを行い, `install-client-go-local-rpm.yml` で導入します。
5. 導入後に `go.mod`, `go.sum`, `vendor/` の存在と, `k8s.io/client-go` 版数一致を確認します。

## 検証ポイント

以下の検証コマンドを実行します:

```bash
ls -la /opt/k8s-devel/go-client
test -f /opt/k8s-devel/go-client/go.mod
echo $?
test -f /opt/k8s-devel/go-client/go.sum
echo $?
test -d /opt/k8s-devel/go-client/vendor
echo $?
```

実行結果の例:
```bash
$ ls -la /opt/k8s-devel/go-client
合計 20
drwxr-xr-x 3 root root 4096  7月 31 22:44 .
drwxr-xr-x 3 root root 4096  7月 31 22:44 ..
-rw-r--r-- 1 root root  103  7月 31 22:44 go.mod
-rw-r--r-- 1 root root  153  7月 31 22:44 go.sum
drwxr-xr-x 2 root root 4096  7月 31 22:44 vendor
$ test -f /opt/k8s-devel/go-client/go.mod
$ echo $?
0
$ test -f /opt/k8s-devel/go-client/go.sum
$ echo $?
0
$ test -d /opt/k8s-devel/go-client/vendor
$ echo $?
0
```

実行結果から以下の内容を確認します:

- `ls -la /opt/k8s-devel/go-client` の出力に `go.mod`, `go.sum`, `vendor` が表示されること。
- `test -f /opt/k8s-devel/go-client/go.mod` の直後の `echo $?` が `0` であること。
- `test -f /opt/k8s-devel/go-client/go.sum` の直後の `echo $?` が `0` であること。
- `test -d /opt/k8s-devel/go-client/vendor` の直後の `echo $?` が `0` であること。

## トラブルシューティング

代表的なトラブルと対処を以下に示します。

| 想定トラブル | 主な原因 | 対処方法 |
| --- | --- | --- |
| `Validate go k8s client version format` で失敗する | `go_k8s_client_version` が `vX.Y.Z` 形式になっていない |  `go_k8s_client_version` を `v0.31.0` のような形式へ修正して再実行します。 |
| パッケージビルド処理がタイムアウトする | 構築ホストの性能不足, イメージ取得遅延, ネットワーク遅延により待機時間を超過している |  `build-*.log` で停止箇所を確認し, 必要に応じて `go_k8s_client_build_timeout_seconds` を延長して再実行します。 |
| `Go k8s client ... package was not generated` で失敗する | コンテナ内ビルドは実行されたが, 指定パターンに合致する deb/rpm 成果物が出力されていない | 構築ホスト上の `/tmp/go-k8s-client-build-<実行ユーザ名>/output` を確認し, パッケージ名設定 (`go_k8s_client_deb_package_name` / `go_k8s_client_rpm_package_name`) と build スクリプトの出力を見直して再実行します。 |
| `No go k8s client deb/rpm file found ...` または `Fetched ... package is missing on controller` で失敗する | 構築ホストから制御ホストへの回収に失敗している, または中間ファイルが削除されている | 構築ホスト上の成果物存在と読み取り権限を確認し, 制御ホストの `~/.ansible/tmp` 配下に回収されることを確認して再実行します。 |
| 導入後の `go.mod` / `go.sum` / `vendor` 存在確認で失敗する | パッケージ導入は完了したが, `go_k8s_client_install_dir` の内容が欠落している | 対象ホストで `/opt/k8s-devel/go-client` 配下を確認し, 既存ファイル競合の有無を確認した上で再導入します。必要に応じて導入先ディレクトリを退避して再実行します。 |
| `Installed client-go module version mismatch` で失敗する | 導入済みの `k8s.io/client-go` 版数が `go_k8s_client_version` と一致していない | 対象ホストで `go list -m k8s.io/client-go` の結果を確認し, 指定版数と一致するように `go_k8s_client_version` を修正するか, 既存導入物の影響を除去して再実行します。 |
| `--check` 実行で成果物が作成されない | チェックモードでは構築/導入処理をスキップする仕様 | 動作確認時に通常実行 (check モードなし) で再実行します。 |


## 注意事項

- 本ロールは client-go の導入ロジックのみを扱う。Go 本体の導入ロジックは `go-lang-local` ロールで扱う。
- `--check` 実行時は, パッケージ構築/導入処理をスキップします。

## 参考資料

### 公式ドキュメント

- [Go Programming Language](https://go.dev/doc/)
- [Go言語版 Kubernetes Clientライブラリ](https://github.com/kubernetes/client-go)
- [Kubernetes API Reference](https://kubernetes.io/docs/reference/generated/kubernetes-api/)
