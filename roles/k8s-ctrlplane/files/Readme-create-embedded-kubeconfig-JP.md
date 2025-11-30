# クラスタ証明書付きkubeconfigファイル生成ツール (create-embedded-kubeconfig.py)仕様

## 概要

`create-embedded-kubeconfig.py` は 管理者用 kubeconfig ファイル(`admin.conf`)から取得したクラスタ証明書を kubeconfig に埋め込み, 単一ファイルで配布可能な設定を生成するユーティリティです。`kubectl config view --raw --flatten` の結果を基に, 証明書ファイルを base64 形式で取り込み, `Cilium Cluster Mesh` などの相互接続環境で利用しやすい kubeconfig を作成します。また, `--shared-ca` オプションを指定した場合は共通 CA 証明書を最優先で埋め込み, クラスタ間で 使用される CA 証明書を`--shared-ca` オプションで指定された共通 CS 証明書に統一します。管理者用 kubeconfig ファイル(`admin.conf`)の読み取りに sudo が必要な場合は, 自動的に `sudo` 付きで `kubectl` を実行します。

## 必要環境

本ツールの実行に必要な環境は以下の通りです:

- Python 3.8 以上
- `kubectl` が実行可能で, 対象クラスタの管理者用 kubeconfig ファイル(`admin.conf`)へアクセスできること
- 依存パッケージ: `PyYAML` バージョン6.0以上

依存パッケージの導入手順例を以下に示します:

```bash
pip install PyYAML
```

## 使い方

生成する kubeconfig のクラスタ名を位置引数 `cluster_name` に指定してコマンドを実行します。指定したクラスタ名はコンテキストやクラスタ名の書き換え, および出力ファイル名の既定プレフィックスに利用されます。

```bash
create-embedded-kubeconfig.py cluster1
```

- 出力先ディレクトリを変えたい場合は `-o`, `--output-dir` で明示します。省略時はカレントディレクトリに出力されます。
- 出力ファイル名は `<file_prefix><file_postfix>` で構成され, `.kubeconfig` 拡張子が付与されます ( 必要に応じて自動追記されます )。

```bash
create-embedded-kubeconfig.py cluster1 \
  --admin-conf /etc/kubernetes/admin.conf \
  --output-dir dest/k8sctrlplane01.local/home/kube/.kube \
  --file-prefix cluster1- \
  --file-postfix embedded
```

このコマンド例では `cluster1-embedded.kubeconfig` が指定ディレクトリに生成されます。

本ツールは, 実行ユーザで対象クラスタの管理者用 kubeconfig ファイル(`admin.conf`)を参照可能であることを確認し, `sudo` が必要な場合はスクリプト内で, `sudo`を自動付与して管理者用 kubeconfig ファイル(`admin.conf`)を参照します。
`sudo` を使いたくない場合は, 実行ユーザーへの読み取り権限を, 管理者用 kubeconfig ファイル(`admin.conf`)に付与してください。

共通 CA 証明書を埋め込みたい場合は, `--shared-ca` に PEM 形式の証明書パスを指定してください。

```bash
create-embedded-kubeconfig.py cluster1 \
   --shared-ca /etc/kubernetes/pki/shared-ca/cluster-mesh-ca.crt
```

## 書式

```:plaintext
create-embedded-kubeconfig.py [-h]
                              [-c ADMIN_CONF | --admin-conf ADMIN_CONF]
                              [-o OUTPUT_DIR | --output-dir OUTPUT_DIR]
                              [-p FILE_PREFIX | --file-prefix FILE_PREFIX]
                              [-P FILE_POSTFIX | --file-postfix FILE_POSTFIX]
                              [--shared-ca SHARED_CA]
                              [-v | --verbose]
                              cluster_name
```

## オプション

| オプション | 説明 |
| --- | --- |
| `cluster_name` | **位置引数**。生成した kubeconfig に登録するクラスタ名を指定します。ログ出力やファイル名にも利用されます。 |
| `-c`, `--admin-conf` | 参照する `admin.conf` のパスを指定します。既定値は `/etc/kubernetes/admin.conf` です。 |
| `-o`, `--output-dir` | 出力ディレクトリを指定します。省略時はコマンド実行時のカレントディレクトリに書き込みます。 |
| `-p`, `--file-prefix` | 出力ファイル名のプレフィックスを明示します。省略時は `cluster_name` を利用します。 |
| `-P`, `--file-postfix` | 出力ファイル名のサフィックスを指定します。既定値は `-embedded.kubeconfig` です。`.kubeconfig` が含まれない場合は自動で付与されます。 |
| `--shared-ca` | 共有 CA 証明書 (PEM) のパスを指定します。指定された証明書を最優先で埋め込みます。省略時は管理者用 kubeconfig 内の CA を利用します。 |
| `-v` | ログを INFO レベルで表示します。 |
| `-vv` | ログを DEBUG レベルまで表示します。 |

## ログ出力

ログ出力は, python標準の`logger`モジュールの仕様に従って出力されます。

- 既定では WARNING レベル以上を表示します。`-v` を付与すると INFO ログが, `-vv` を付与すると DEBUG ログが追加されます。
- 生成前後の kubeconfig について, クラスタ, コンテキスト, ユーザーの一覧, `sha256` ハッシュ, `certificate-authority-data` の有無などを INFO ログで確認できます。

### 出力メッセージと条件

以下の表は, 本プログラムが標準出力 / 標準エラー出力に表示する代表的なメッセージをまとめたものです。メッセージ中の `<path>` や `<cluster>` などは実際の値に置き換わります。
以下では, 証明書の発行主体である認証局 (`Certificate Authority`)を`CA`と記載します。

| メッセージ | 区分 | 出力条件 | 推奨対応 |
| --- | --- | --- | --- |
| `Cluster name is required to derive file prefix` | ERROR | `_resolve_file_prefix` が `cluster_name` を決定できなかったときに出力されます。 | 位置引数 `cluster_name` を正しく指定し, 必要に応じて `--file-prefix` も指定してください。 |
| `cluster name is required for file prefix` | ERROR | `_resolve_file_prefix` がクラスタ名を決定できず kubeconfig 処理エラー(`KubeconfigError`)を送出した際に再度表示されます。 | `cluster_name` の指定を見直し, 正しい値で再実行してください。 |
| `No cluster name specified, exit.` | ERROR | 位置引数が空のままコマンドを実行した場合に表示されます。 | コマンドラインでクラスタ名を必ず指定してください。 |
| `Running command: <cmd>` | DEBUG | `-vv` 指定時に, `kubectl` 実行直前で表示されます。 | 実行予定のコマンド文字列(`<cmd>`)を確認し, 想定どおりであることを確認してください。 |
| `kubectl failed: <stderr>` | ERROR | `kubectl` が非ゼロ終了したときに表示されます (`<stderr>` には標準エラー出力の要約が入ります)。 | 権限, ネットワーク, 対象クラスタの状態などを確認し, エラーメッセージ(`<stderr>`)を参考に問題を解消してから再実行してください。 |
| `Cannot create output directory: <path>` | ERROR | 出力ディレクトリ(`<path>`)の作成に失敗したときに表示されます。 | 親ディレクトリの存在と書き込み権限を確認し, 対象ディレクトリ(`<path>`)を作成または権限を修正してください。 |
| `cannot create output directory` | ERROR | 出力ディレクトリの作成に失敗し kubeconfig 処理エラー(`KubeconfigError`)が伝播した際に表示されます。 | 出力ディレクトリのパス(`<path>`)と権限を整えてから再実行してください。 |
| `Cannot open file: <path>` | ERROR | 管理者用 kubeconfig ファイル(`admin.conf`)の参照に失敗した場合に表示されます。 | 指定したファイルパス(`<path>`)が正しく, 読み取り権限が付与されていることを確認してください。 |
| `admin.conf not found` | ERROR | 管理者用 kubeconfig ファイル(`admin.conf`)が存在しない場合に kubeconfig 処理エラー(`KubeconfigError`)として表示されます。 | 対象ノードで管理者用 kubeconfig ファイル(`admin.conf`)が配置されていることを確認し, 必要なら `--admin-conf` でパスを指定してください。 |
| `failed to access admin.conf` | ERROR | 管理者用 kubeconfig ファイル(`admin.conf`)の読み取りで I/O 例外が発生したときに表示されます。 | ファイル権限や SELinux / AppArmor ポリシーを確認し, 管理者用 kubeconfig ファイル(`admin.conf`)へアクセス可能な状態に調整してください。 |
| `admin.conf requires sudo: <path>` | INFO | 管理者用 kubeconfig ファイル(`admin.conf`)の読み取りに sudo が必要と判定した場合に表示されます。 | sudo を許容する場合はそのまま継続してください。sudo を避けたい場合は 管理者用 kubeconfig ファイル(`admin.conf`)のパーミッションを実行ユーザーに付与してください。 |
| `Saved kubeconfig snapshot to <path>` | INFO | `kubectl` の結果をそのまま保存した段階で表示されます。 | 一次出力先のファイル(`<path>`)が生成され, 続く処理で同じファイルが証明書付きで上書きされることを確認してください。 |
| `Wrote embedded kubeconfig to <path>` | INFO | 証明書を埋め込んだ後で保存した段階に表示されます。 | 生成済みの配布用 kubeconfig ファイル(`<path>`)が適切な保存場所であることを確認してください。 |
| `===== kubeconfig summary (<label>) =====` | INFO | `-v` 以上指定時に, 要約表示の開始時に出力されます。 | ラベル (`<label>`) を見て処理段階 ( 例: `before embed` / `after embed` )を把握してください。 |
| `file-path: <path>` | INFO | サマリ表示中に対象ファイルのパスを示します。 | 表示されたファイルの保存先(`<path>`)が期待どおりであることを確認してください。 |
| `sha256: <digest>` | INFO | サマリ表示で計算されたファイルの SHA256 を示します。 | 算出されたハッシュ値(`<digest>`)を控え, 配布後の整合性チェックに利用してください。 |
| `contexts: <list>` | INFO | サマリで含まれる context 名の一覧を示します。 | 表示されたコンテキスト一覧(`<list>`)に必要な項目が揃っていることを確認してください。 |
| `clusters: <list>` | INFO | サマリで含まれる cluster 名の一覧を示します。 | 表示されたクラスタ一覧(`<list>`)が想定と一致していることを確認してください。 |
| `users: <list>` | INFO | サマリで利用者エントリの一覧を示します。 | 表示されたユーザー一覧(`<list>`)に不要なエントリが含まれていないことを確認してください。 |
| `current-context: <name>` | INFO | 現在のコンテキスト名が空の場合は自動補完後の値を示します。 | 既定コンテキストとして設定される値(`<name>`)が適切であることを確認してください。 |
| `context.cluster: <name>` | INFO | 現在のコンテキストが参照するクラスタ名を示します。 | 現在のコンテキストが参照するクラスタ名(`<name>`)が意図どおりであることを確認してください。 |
| `context.user: <name>` | INFO | 現在のコンテキストが参照するユーザー名を示します。 | 使用する認証情報のユーザー名(`<name>`)が正しいことを確認してください。 |
| `cluster.server: <url>` | INFO | API サーバーのエンドポイント URL を示します。 | 表示されたエンドポイント URL(`<url>`)が到達可能であることを確認してください。 |
| `cluster.certificate-authority-data: present (len=<n>, head='<head...>')` | INFO | 埋め込み CA データが存在するときに表示されます。 | データ長(`<n>`)や先頭部分(`<head>`)を記録し, CA データが埋め込まれていることを確認してください。 |
| `cluster.certificate-authority: file='<path>' (exists)` | INFO | CA ファイルパスが存在する場合に表示されます。 | 参照されている証明書ファイルのパス(`<path>`)が期待するファイルであることを確認してください。 |
| `cluster.certificate-authority: file='<path>' (NOT found)` | WARNING | CA ファイルパスが存在しない場合に表示されます。 | 指定された証明書ファイルのパス(`<path>`)の存在, マウント状態, シンボリックリンク有効性などを確認し, 必要なら再配置してください。 |
| `cluster.certificate-authority: file='<path>' (permission denied)` | WARNING | CA ファイルの読み取り権限が不足している場合に表示されます。 | 読み取り権限が不足している証明書ファイルのパス(`<path>`)に対してパーミッションを調整し, 再度ツールを実行してください。 |
| `cluster.certificate-authority: file='<path>' (error: <err>)` | WARNING | CA ファイルアクセスでその他の I/O 例外が発生した場合に表示されます。 | 発生したエラー内容(`<err>`)に従い, デバイス状態やパス設定を確認してください。 |
| `Using shared CA certificate from <path> (len=<n>, head='<head...>')` | INFO | `--shared-ca` で指定した CA 証明書を読み込み, 埋め込む際に表示されます。 | 表示された CA のパス(`<path>`)が想定どおりであることを確認し, データ長(`<n>`)や先頭(`<head>`)が期待する値であることをチェックしてください。 |
| `Failed to read shared CA certificate '<path>': <err>` | ERROR | `--shared-ca` で指定した CA ファイルを読み取れなかった場合に表示されます。 | パス(`<path>`)の存在や権限, `<err>` の内容を確認し, 読み取り可能な状態に整えて再実行してください。 |
| `Shared CA certificate '<path>' is empty` | ERROR | `--shared-ca` で指定した CA ファイルの内容が空だった場合に表示されます。 | 正しい PEM ファイルを配置し, 再度コマンドを実行してください。 |
| `shared CA data is invalid base64` | ERROR | `--shared-ca` で読み込んだ証明書が Base64 として解釈できない場合に表示されます。 | 指定したファイルが PEM 形式であることを確認し, 必要なら内容を修正または別ファイルを指定してください。 |
| `certificate-authority-data is masked (DATA+OMITTED / REDACTED)` | WARNING | マスクされた `certificate-authority-data` を検出した場合に表示されます。 | `sudo kubectl config view --raw --kubeconfig=/etc/kubernetes/admin.conf > ~/admin.conf.clean` を実行し, マスクされていない kubeconfig ファイル(`~/admin.conf.clean`)を再取得してから `--admin-conf ~/admin.conf.clean` で再実行してください。 |
| `No CA found (neither data nor file)` | WARNING | CA データもファイルも見つからない場合に表示されます。 | 管理者用 kubeconfig ファイル(`admin.conf`)のクラスタ定義を見直し, CA 情報が含まれるよう修正してから再実行してください。 |
| `raw file contains masked fields (saved without --raw?)` | WARNING | 生成済みファイル内にマスク文字列を検出した場合に表示されます。 | `sudo kubectl config view --raw --kubeconfig=/etc/kubernetes/admin.conf > ~/admin.conf.clean` でマスクされていない kubeconfig ファイル(`~/admin.conf.clean`)を作り直し, `--admin-conf ~/admin.conf.clean` で再実行してください。 |
| `===== end of summary (<label>) =====` | INFO | サマリ表示の終了時に出力されます。 | 特別な対応は不要です。ラベル (`<label>`) を見て処理段階 ( 例: `before embed` / `after embed` )を把握してください。サマリ内容を確認し終えたら次の作業に進んでください。 |
| `No CA found; falling back to --insecure-skip-tls-verify` | WARNING | 埋め込み対象の CA を取得できなかった際に, TLS 検証をスキップしたことを示します。 | CA 情報を整備し, 可能な限り TLS 検証を有効化した状態で再生成してください。 |
| `Updated contexts referencing '<old>' to new cluster '<new>'` | INFO | 既存コンテキストが新しいクラスタ名に書き換わった際に表示されます。 | 新しいクラスタ名(`<new>`)が期待どおりであることを確認してください。 |
| `Cluster '<name>' not found` | ERROR | 現在のコンテキストが参照するクラスタを管理者用 kubeconfig ファイル(`admin.conf`)から取得できなかった場合に表示されます。 | 管理者用 kubeconfig ファイル(`admin.conf`)内のクラスタ名(`<name>`)と `cluster_name` の対応を確認し, 修正後に再実行してください。 |
| `No contexts found in kubeconfig` | ERROR | 管理者用 kubeconfig ファイル(`admin.conf`)にコンテキスト定義が含まれていない場合に表示されます。 | 入力 kubeconfig を `kubectl config view --raw` などで確認し, コンテキストを定義してから再実行してください。 |
| `Unable to determine current context` | ERROR | `current-context` を特定できなかった場合に表示されます。 | 管理者用 kubeconfig ファイル(`admin.conf`)に設定項目(`current-context`)または少なくとも 1 つのコンテキストが定義されていることを確認してください。 |
| `Context name is missing` | ERROR | コンテキストの `name` フィールドが空の場合に表示されます。 | 管理者用 kubeconfig ファイル(`admin.conf`)の該当エントリを修正し, 正しい名前を設定してください。 |
| `Context spec is missing` | ERROR | コンテキストの `context` フィールドが欠落している場合に表示されます。 | kubeconfig のコンテキスト定義を修正し, クラスタとユーザーを指定してください。 |
| `No clusters defined in kubeconfig` | ERROR | `clusters` 配列が空の場合に表示されます。 | 入力 kubeconfig にクラスタ定義を追加してから再実行してください。 |
| `Current context does not reference a cluster` | ERROR | 現在のコンテキストが `cluster` を指さない場合に表示されます。 | コンテキスト定義に `cluster` を設定し, 再実行してください。 |
| `Cluster server endpoint is missing` | ERROR | クラスタ定義から `server` URL が欠落している場合に表示されます。 | 管理者用 kubeconfig ファイル(`admin.conf`)のクラスタ定義に API サーバー URL を追記してください。 |
| `Unexpected kubeconfig structure` | ERROR | YAML 解析結果が辞書形式でなかった場合に表示されます。 | 管理者用 kubeconfig ファイル(`admin.conf`)を `kubectl config view --raw` で再生成し, 形式が破損していないことを確認してください。 |

### エラーメッセージ発生時の対処方針

- `kubectl` 実行失敗時は標準エラー出力の内容をログ出力します。クラスタへの到達性, 認証, RBAC ポリシー, ネットワークの状態を確認してください。
- 出力ディレクトリ作成に失敗する場合は, 親ディレクトリの存在と書き込み権限を確認します。
- 証明書が埋め込めない場合は, 管理者用 kubeconfig ファイル(`admin.conf`)内の `certificate-authority-data` がマスクされていないか, 参照される `certificate-authority` ファイルが存在するかを確認してください。

## 出力ファイルの確認手順

生成した kubeconfig を検証する手順例を以下に示します。ここでは出力ファイル名を `cluster1-embedded.kubeconfig` と仮定します。

1. ファイルの存在と更新時刻を確認:

   ```bash
   ls -l cluster1-embedded.kubeconfig
   ```

2. YAML の内容を整形表示して確認:

   ```bash
   kubectl config view --raw --kubeconfig=cluster1-embedded.kubeconfig
   ```

3. コンテキストが意図したクラスタ, ユーザーと紐づいていることを確認:

   ```bash
   kubectl config get-contexts --kubeconfig=cluster1-embedded.kubeconfig
   ```

4. 必要に応じて, 生成ファイルに含まれる証明書情報を `sha256` などのハッシュで検証します。ログに出力される `sha256: <digest>` と照合すると, 配布途中の改ざん検知に利用できます。

## ライセンス

本スクリプトは 2 条項 BSD ライセンスで配布されています。ライセンス条文はスクリプト冒頭のコメントを参照してください。

## 参考資料

- [kubectl Reference](https://kubernetes.io/docs/reference/kubectl/) `kubectl config` サブコマンドの詳細。
- [PyYAML](https://pyyaml.org/) YAML パーサのドキュメント。
