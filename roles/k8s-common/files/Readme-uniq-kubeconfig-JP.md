# kubeconfigファイル結合ツール (create-uniq-kubeconfig.py)仕様

## 概要

`create-uniq-kubeconfig.py` は複数の kubeconfig ファイルを結合し, クラスタ, コンテキスト, ユーザー名の重複を解消した単一の kubeconfig を生成するユーティリティです。
Cilium Cluster Mesh など, 複数クラスタを扱うために,
統合済みの設定ファイルを用意する目的で使用することを想定しています。

## 必要環境

本ツールの実行に必要な環境は以下の通りです:

- Python 3.8 以上
- `kubectl` が実行可能で, 統合対象クラスタへアクセスできること
- 依存パッケージ: `PyYAML` バージョン6.0以上

依存パッケージの導入手順例を以下に示します:

```bash
pip install PyYAML
```

## 使い方

1. 任意の `kubeconfig` ファイルを用意します。
2. 統合対象となる`kubeconfig`ファイルへのパスを位置引数に指定して, コマンドを実行します。指定した順番に処理されるため, 優先したい設定を前に配置してください。

```bash
python create-uniq-kubeconfig.py kube1.config kube2.config kube3.config
```

`-o/--output` を指定しない場合, 出力ファイルは `merged-kubeconfig.config` になります。出力ファイル名を指定する場合は, 以下のように, `-o` オプションで出力ファイル名を明示します。

```bash
python create-uniq-kubeconfig.py -o my-mesh.config kube1.config kube2.config
```

## オプション

| オプション | 説明 |
| --- | --- |
| `-h`, `--help` | ヘルプメッセージを出力します。|
| `-o, --output` | 出力ファイルのパス名を指定します。省略時は `merged-kubeconfig.config` を使用します。 |
| `-v` | ログを INFO レベルで表示します。 |
| `-vv` | ログを DEBUG レベルまで表示します。 |

ログ出力は, python標準の`logger`モジュールの仕様に従って出力されます。

## ログ出力

- `-v` を付与すると結合したクラスタ数などの進捗が INFO ログで表示されます。
- 統合後のファイルパスは `Merged <count> kubeconfig files into <path>` というログで確認できます。`<path>`に出力ファイルへのパスが表示されます。

### 出力メッセージと条件

以下の表は, 本プログラムが標準出力・標準エラー・プロンプトとして発するメッセージを網羅し, 発生条件と推奨対応を整理したものです。ログの表示レベルは `-v`（INFO）/`-vv`（DEBUG）で切り替わります。

| メッセージ | 区分 | 出力条件 | 推奨対応 |
| --- | --- | --- | --- |
| `Running command: <cmd>` | DEBUG | `-vv` 指定時に, `kubectl` 実行直前に出力します。 | 実行されるコマンドを表すメッセージです。実行されるコマンドに問題がないことを確認ください。 |
| `kubectl failed: <stderr>` | ERROR | `kubectl` が非ゼロ終了したときに表示されます。 | ステータスや認証情報をご確認のうえ, 環境を整えてから再実行してください。 |
| `Loaded <path>: clusters=<n> contexts=<n> users=<n>` | DEBUG | `-vv` 指定時に, `kubeconfig` 読み込み直後に表示されます。 | 読み込まれたファイルのパス(`<path>`), ファイル内に定義されているクラスタ数(`<clusters>`), コンテキスト数(`<contexts>`), ユーザ数(`<users>`)が, 想定どおりであることを確認ください。差異があった場合は入力ファイルを調査ください。 |
| `Skipping malformed cluster entry in <path>` | DEBUG | `-vv` 指定時, かつ, クラスタ項目が不正だった場合に表示されます。 | 入力ファイル (`<path>`) の該当要素を修正し, 再実行してください。 |
| `Skipping malformed user entry in <path>` | DEBUG | `-vv` 指定時, かつ, ユーザー項目が不正だった場合に表示されます。 | 上記クラスタ項目と同様に, 入力ファイル (`<path>`) の該当箇所を修正ください。 |
| `Skipping malformed context entry in <path>` | DEBUG | `-vv` 指定時, かつ, コンテキスト項目が不正だった場合に表示されます。 | 上記と同様に, 入力ファイル (`<path>`) の該当コンテキストを整えてから再実行してください。 |
| `Processed <path> (clusters=<n>, contexts=<n>, users=<n>)` | INFO | `-v` 以上指定時に, 各入力ファイルの処理完了時に表示されます。 | 処理が順調に進んでいることを示します。 必要に応じて, 読み込まれたファイルのパス(`<path>`), クラスタ数(`<clusters>`), コンテキスト数(`<contexts>`), ユーザ数(`<users>`)が, 想定どおりであることを確認ください。|
| `No clusters found in <path>` | WARNING | クラスタ項目が 1 つも無いときに表示されます。 | 入力ファイル (`<path>`)の内容を確認し, 必要に応じて順序や定義を調整ください。 |
| `Merged <count> kubeconfig files into <path>` | INFO | `-v` 以上指定時に, 全統合完了時に表示されます。 | 処理したファイルの数 (`<count>`), 出力ファイル (`<path>`)を確認し, 後続作業に進んでください。 |
| `Input kubeconfig not found: <path>` | ERROR | 指定した入力ファイル (`<path>`)が存在しない場合に表示されます。 | 指定パスが正しいことを確認し, 修正後に再実行してください。 |
| `Aborted: output file already exists` | WARNING | 既存出力ファイルへの上書きを拒否した際に表示されます。 | 出力先を変更, または, 再実行時に上書きを許可してください。 |
| `Failed to parse kubeconfig from <path>: <error>` | ERROR | YAML 解析に失敗したときに表示されます。 | YAML解析エラーメッセージ (`<error>`)の内容を元に, `kubectl config view` などで入力ファイル (`<path>`)の内容を確認し, ファイルの形式を修正してください。 |
| `Unexpected kubeconfig structure from <path>` | ERROR | 入力ファイルの構造が, 本ツールの想定外の構造だったときに表示されます。 | 入力ファイル (`<path>`)が `kubeconfig` 形式に準拠していることを確認ください。 |
| `<path> already exists. Overwrite? [y/N]:` | PROMPT | 出力先ファイル (`<path>`)が既に存在する場合に表示される上書き確認メッセージです。 | 上書きして問題なければ `y` / `yes` を入力してください。既存のファイルを保持したい場合は `n` を入力し, 出力先ファイル名に別名を指定ください。 |

### エラーメッセージ発生時の対処方針

- 入力ファイルが存在しない場合はエラーになります。指定パスを再確認してください。
- `kubectl` が非ゼロ終了した場合は実行ログを確認し, 権限やネットワーク状態を見直してください。
- YAML 解析エラーには, `pyYAML`の`YAMLError`例外の出力内容を出力します。`pyYAML`のドキュメントを参照し, エラー内容を確認してください。本エラー発生時は, 入力ファイルが壊れている可能性があります。対象の `kubeconfig` を検証してください。

## 出力ファイルの確認手順

出力ファイルの確認手順の例を以下に示します:

1. ファイルの存在と更新時刻を確認:

   ```bash
   ls -l merged-kubeconfig.config
   ```

2. YAML の内容を整形表示して確認:

   ```bash
   yq e . merged-kubeconfig.config
   # yq がない場合は kubectl を利用
   kubectl config view --raw --kubeconfig=merged-kubeconfig.config
   ```

3. 統合されたコンテキスト一覧の確認:

   ```bash
   kubectl config get-contexts --kubeconfig=merged-kubeconfig.config
   ```

## ライセンス

本スクリプトは 2 条項 BSD ライセンスで配布されています。
ライセンス条文はスクリプト中のコメントを参照ください。

## 参考資料

- [pyYAML](https://pyyaml.org/) 本ツールで使用しているYAML (YAML Ain't Markup Language) パーサです。
