# Ansible 管理ファイル監査ツール (`ansible_backup_audit.py`) 仕様

- [Ansible 管理ファイル監査ツール (`ansible_backup_audit.py`) 仕様](#ansible-管理ファイル監査ツール-ansible_backup_auditpy-仕様)
  - [用語](#用語)
  - [概要](#概要)
  - [必要環境](#必要環境)
  - [使い方](#使い方)
    - [基本的な実行](#基本的な実行)
  - [書式](#書式)
  - [オプション](#オプション)
  - [環境変数](#環境変数)
  - [監査対象](#監査対象)
    - [対象 Module](#対象-module)
    - [解析する制御処理](#解析する制御処理)
  - [出力](#出力)
    - [CSV](#csv)
    - [標準エラー出力](#標準エラー出力)
    - [終了コード](#終了コード)
  - [テンプレートの取り扱いと生成ファイル](#テンプレートの取り扱いと生成ファイル)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [検証の前提条件](#検証の前提条件)
    - [検証環境の設定](#検証環境の設定)
    - [検証コマンドと期待結果](#検証コマンドと期待結果)
  - [トラブルシューティング](#トラブルシューティング)
    - [終了コードが `2` になる](#終了コードが-2-になる)
    - [Facts の取得に失敗する](#facts-の取得に失敗する)
    - [Playbook 又は Inventory が見つからない](#playbook-又は-inventory-が見つからない)
    - [`Role` で指定したロール中にタスクファイルが見つからない](#role-で指定したロール中にタスクファイルが見つからない)
    - [CSV を表計算ソフトウェアで正しく読めない](#csv-を表計算ソフトウェアで正しく読めない)
    - [一時ファイルのパスに `*` が含まれる](#一時ファイルのパスに--が含まれる)
    - [必要なファイルが CSV に含まれない](#必要なファイルが-csv-に含まれない)
  - [注意事項](#注意事項)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)


## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Python | - | 本ツールを実行するためのプログラム言語及び実行環境です。 |
| Ansible | - | 複数の対象ホストに対する設定作業を定義し, 実行するソフトウェアです。 |
| Ansible Playbook | Playbook | Ansible で実行する処理と対象ホストを YAML 形式で記載したファイルです。 |
| Ansible Inventory | Inventory | Ansible が処理する対象ホストとホストの集まりを記載したファイル又はディレクトリです。 |
| Ansible Role | Role | Ansible の処理, 変数及び関連ファイルを目的別にまとめた構成単位です。 |
| Ansible Module | Module | Ansible の各処理を実行する機能単位です。 |
| Ansible Facts | Facts | Ansible が対象ホストから取得するオペレーティングシステムなどの情報です。 |
| Fully Qualified Collection Name | FQCN | Ansible Module を所属先まで含めて一意に示す名前です。 |
| YAML Ain't Markup Language | YAML | Playbook や変数を階層構造で記載するためのデータ記述形式です。 |
| JavaScript Object Notation | JSON | 名前と値の組を用いてデータを表す記述形式です。 |
| Comma-Separated Values | CSV | 項目をコンマで区切って表す表形式のデータです。 |
| JavaScript Template Engine 2 | Jinja2 | Playbook 内の変数式及び条件式を値へ置き換える仕組みです。 |
| PyYAML | - | Python で YAML ファイルを読み取るためのソフトウェアです。 |
| `ansible-backup-audit`コマンド | - | 本書では, `ansible_backup_audit.py` を実行した際のコマンド名の意味で使用します。 |
| `ansible`コマンド | - | 対象ホストの選択と Facts の取得に使用する Ansible のコマンドです。 |
| `ansible-inventory`コマンド | - | Inventory のホスト及び変数を取得する Ansible のコマンドです。 |
| `python3`コマンド | - | Python で本ツールを実行するコマンドです。 |
| `pip`コマンド | - | Python で使用するソフトウェアを導入するコマンドです。 |
| `head`コマンド | - | ファイルの先頭部分を表示するコマンドです。 |
| `printf`コマンド | - | 指定した書式で文字列を表示するコマンドです。 |
| `awk`コマンド | - | CSV の指定列を検査するために使用するコマンドです。 |
| 標準出力 | - | 本ツールが CSV を書き出す出力先です。 |
| 標準エラー出力 | - | 本ツールが警告及びエラーを表示する出力先です。 |
| 終了コード | - | コマンドの終了理由を呼び出し元へ伝える整数値です。 |
| ホストパターン | - | Ansible で対象ホストを名前又はホストの集まりにより選択する記法です。 |
| 環境変数 | - | コマンドを実行する環境から本ツールへ設定値を渡す仕組みです。 |
| glob 表現 | - | 実行時に決まる文字列部分を `*` で表したパスの表記です。 |

## 概要

`ansible_backup_audit.py` は, Playbook を解析し, Role が対象ホスト上で作成, 変更又は削除するファイルの一覧を CSV 形式で出力する監査用ツールです。

本ツールは Inventory のホスト変数と対象ホストから取得した Facts を使用して, Playbook の変数式, 条件式及び繰り返し処理をホストごとに評価します。`include_tasks`, `import_tasks`, `include_role`, `import_role`, `include_vars` 及び `set_fact` も, 静的に値を解決できる範囲で追跡します。

本ツールは Playbook 自体を実行しません。ただし, 解析に必要な 情報 (Facts) を取得するため, `ansible`コマンドで対象ホストへ接続します(対象ホストに対して, ansibleの`ansible.builtin.setup` を実行します)。

実行時にのみ決まる値を静的に解決できない場合でも, 解決済みの監査結果を標準出力へ出力します。未解決のタスクは標準エラー出力へ表示し, 終了コード `2` で終了し, 結果が不完全であることを通知します。

## 必要環境

本ツールの実行に必要な環境は次のとおりです。

- Python 3.10 以上が利用できること。
- `ansible`コマンド及び `ansible-inventory`コマンドが利用できること。
- Python から Ansible, PyYAML 及び Jinja2 を読み込めること。
- 解析対象の Playbook と, Playbook と同じディレクトリ直下の `roles` ディレクトリを参照できること。
- 指定する Inventory を参照できること。
- Inventory で選択される対象ホストへ Ansible で接続し, Facts を取得できること。
- Playbook 及び Role が参照する変数ファイルとタスクファイルを読み取れること。

Ansible の導入手順例を次に示します。Ansible を導入すると, 本ツールが直接利用する PyYAML と Jinja2 も依存関係として導入されます。

```bash
python3 -m pip install ansible-core
```

導入後は, 次のコマンドで利用可否を確認します。

```bash
python3 --version
ansible --version
ansible-inventory --version
```

## 使い方

### 基本的な実行

Playbook を位置引数に指定して, Ansible プロジェクトのルートディレクトリで実行します。
以下の例では, 標準出力は結果ファイル ( `result.csv` ) へ, 標準エラー出力は診断ファイル ( `error.log` ) へ分けて保存します。

```bash
python3 ansible_backup_audit.py site.yml \
  > result.csv \
  2> error.log
```

Inventory の既定パス `inventory/hosts` 以外を使用する場合は, `-i` 又は `--inventory` を指定します。

```bash
python3 ansible_backup_audit.py site.yml \
  --inventory inventory/production \
  > result.csv \
  2> error.log
```

対象ホストを限定する場合は `-l` 又は `--limit` にホストパターンを指定します。

```bash
python3 ansible_backup_audit.py site.yml \
  --inventory inventory/hosts \
  --limit 'k8s_ctrl_plane:&production' \
  > result.csv \
  2> error.log
```

特定の Role のみを解析する場合は `-r` 又は `--role` を指定します。複数の Role を指定する場合は, オプションを繰り返します。

```bash
python3 ansible_backup_audit.py site.yml \
  --role common \
  --role k8s-ctrlplane \
  > result.csv \
  2> error.log
```

実行直後に終了コードを確認します。

```bash
status=$?
printf '%s\n' "$status"
```

終了コード `0` の場合は, 全対象を静的に解決できています。終了コード `2` の場合は, `result.csv` と `error.log` の両方を確認してください。

## 書式

```plaintext
ansible-backup-audit [-h]
                     [-i INVENTORY | --inventory INVENTORY]
                     [-l LIMIT | --limit LIMIT]
                     [-r ROLE | --role ROLE]
                     [-v | --verbose]
                     playbook
```

Python ファイルを直接指定する場合の書式は次のとおりです。

```plaintext
python3 ansible_backup_audit.py [-h]
                                [-i INVENTORY | --inventory INVENTORY]
                                [-l LIMIT | --limit LIMIT]
                                [-r ROLE | --role ROLE]
                                [-v | --verbose]
                                playbook
```

## オプション

| オプション | 説明 |
| --- | --- |
| `playbook` | **位置引数**。解析する Playbook のパスを指定します。Playbook の親ディレクトリを Ansible プロジェクトのルートとして扱います。 |
| `-h`, `--help` | 書式とオプションの説明を表示して終了します。 |
| `-i`, `--inventory` | 使用する Inventory のファイル又はディレクトリを指定します。既定値は, コマンド実行時のカレントディレクトリを基準とする `inventory/hosts` です。 |
| `-l`, `--limit` | Ansible のホストパターンで対象ホストを限定します。省略時は Playbook の各 Play が指定する全対象ホストを解析します。 |
| `-r`, `--role` | 指定した Role のみを解析します。複数回指定できます。省略時は Playbook の `roles` に記載された全 Role を解析します。 |
| `-v`, `--verbose` | 未解決のタスクを検出した時点で標準エラー出力へ表示します。解析終了時にも未解決タスクの一覧を表示するため, 同じメッセージが再度表示される場合があります。 |

## 環境変数

外部コマンドの時間制限と再試行は, 次の環境変数で設定します。

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `ANSIBLE_BACKUP_AUDIT_TIMEOUT` | 1 回の外部コマンド実行に対する時間制限を秒で指定します。0 より大きい数値を指定します。 | `120.0` | `ANSIBLE_BACKUP_AUDIT_TIMEOUT=300` |
| `ANSIBLE_BACKUP_AUDIT_RETRIES` | 外部コマンドが失敗した後の再試行回数を指定します。0 以上の整数を指定します。初回実行は回数に含みません。 | `2` | `ANSIBLE_BACKUP_AUDIT_RETRIES=3` |
| `ANSIBLE_BACKUP_AUDIT_RETRY_INTERVAL` | 再試行までの待機時間を秒で指定します。0 以上の数値を指定します。 | `1.0` | `ANSIBLE_BACKUP_AUDIT_RETRY_INTERVAL=2` |

設定例を次に示します。

```bash
1: ANSIBLE_BACKUP_AUDIT_TIMEOUT=300 \
2: ANSIBLE_BACKUP_AUDIT_RETRIES=3 \
3: ANSIBLE_BACKUP_AUDIT_RETRY_INTERVAL=2 \
4: python3 ansible_backup_audit.py site.yml > result.csv 2> error.log
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `ANSIBLE_BACKUP_AUDIT_TIMEOUT=300` | 外部コマンド 1 回の時間制限を 300 秒にします。 | 対象ホスト数が多い環境で既定値を超える処理を完了させるためです。0 以下又は数値以外を指定すると解析開始前に終了します。 |
| 2 | `ANSIBLE_BACKUP_AUDIT_RETRIES=3` | 初回失敗後に最大 3 回再試行します。 | 一時的な接続失敗から回復できる回数を増やすためです。負数又は整数以外を指定すると解析開始前に終了します。 |
| 3 | `ANSIBLE_BACKUP_AUDIT_RETRY_INTERVAL=2` | 再試行の間を 2 秒空けます。 | 短時間に再実行を集中させないためです。負数又は数値以外を指定すると解析開始前に終了します。 |
| 4 | `python3 ansible_backup_audit.py ...` | 指定した設定で監査を実行し, CSV と診断を別々に保存します。 | 出力先を分けない場合は, CSV と診断を用途別に確認できないためです。 |

この設定例の検証方法は, 「検証ポイント」の「検証コマンドと期待結果」を参照してください。

## 監査対象

### 対象 Module

本ツールがファイルパスを抽出する Module と操作の判定方法を次に示します。本ツールは, Playbook 中のFQCN と短縮名の両方を調査します。

| Module | 参照する主な引数 | CSV の `OP` |
| --- | --- | --- |
| `ansible.builtin.template` | `dest` | `create_or_modify` |
| `ansible.builtin.copy` | `dest` | `create_or_modify` |
| `ansible.builtin.lineinfile` | `path`, `dest` | `create_or_modify` |
| `ansible.builtin.blockinfile` | `path` | `create_or_modify` |
| `ansible.builtin.replace` | `path` | `modify` |
| `ansible.builtin.get_url` | `dest` | `create_or_modify` |
| `ansible.builtin.patch`, `ansible.posix.patch` | `dest` | `modify` |
| `ansible.posix.authorized_key` | `path` | `create_or_modify` |
| `ansible.posix.sysctl` | `sysctl_file` | `create_or_modify` |
| `ansible.builtin.file` | `path`, `dest`, `name` | `state: absent` は `delete`, その他は `create_or_modify` |
| `ansible.builtin.tempfile` | `path`, `prefix`, `suffix` | `create_or_modify` |
| `ansible.builtin.apt_repository` | `filename` | `state: absent` は `delete`, その他は `create_or_modify` |
| `ansible.builtin.deb822_repository` | `name` | `state: absent` は `delete`, その他は `create_or_modify` |
| `ansible.builtin.yum_repository` | `reposdir`, `file`, `name` | `state: absent` は `delete`, その他は `create_or_modify` |

`ansible.builtin.file` と `ansible.builtin.tempfile` で `state: directory` を指定した処理は, ファイル監査の対象外です。

`ansible.builtin.tempfile` で生成される実際のファイル名は実行前に確定できないため, `path`, `prefix` 及び `suffix` から glob 表現を生成します。例えば, `/tmp/ansible.*-secret.yaml` のように出力し, 同じ内容を警告として標準エラー出力へ表示します。

### 解析する制御処理

本ツールは, 監査対象ファイルを検出するために, 次の Module を解析します。

- `ansible.builtin.include_tasks`
- `ansible.builtin.import_tasks`
- `ansible.builtin.include_role`
- `ansible.builtin.import_role`
- `ansible.builtin.include_vars`
- `ansible.builtin.set_fact`

Playbook の `import_playbook` は, 参照先を再帰的に展開します。Role の `defaults/main.yml`, `vars/main.yml`, `tasks/main.yml` 又は `tasks_from` で指定したタスクファイルを読み取ります。

`when`, `loop` 及び `with_items` は, 静的に値を解決できる範囲で評価します。`delegate_to` が現在の対象ホスト以外を示すタスクは, 現在の対象ホストの監査結果へ含めません。

## 出力

### CSV

標準出力には, 見出しを含む CSV を出力します。レコードは `HOST`, `ROLE`, `OP`, `PATH` の順で並べ替え, 同じ組み合わせの重複を除きます。

```csv
HOST,ROLE,OP,PATH
extgw.local,common,create_or_modify,/etc/NetworkManager/NetworkManager.conf
extgw.local,common,create_or_modify,/etc/crontab
extgw.local,common,delete,/etc/example.conf
```

| 列名 | 内容 |
| --- | --- |
| `HOST` | ファイル操作の対象ホスト名です。 |
| `ROLE` | ファイル操作を定義した Role 名です。 |
| `OP` | 操作種別です。`create_or_modify`, `modify`, `delete` のいずれかです。 |
| `PATH` | 対象ホスト上のファイルパスです。実行時に名前が決まる一時ファイルは glob 表現になる場合があります。 |

`create_or_modify` は, 対象ファイルが存在しない場合にファイルを新規作成し, 存在する場合は, 既存ファイルを変更する処理を示します。`modify` は既存ファイルの変更を, `delete` は削除を示します。

### 標準エラー出力

標準エラー出力には, 一時ファイルの glob 表現に関する警告, 出力先ファイルが特定できなかった場合のタスク(未解決のタスク)について解析失敗時の情報を表示します。標準出力と標準エラー出力を同じファイルへ保存すると CSV として読み取れなくなるため, 出力先を分けてください。

代表的なメッセージを次に示します。`<path>`, `<host>` 及び `<reason>` は実際の値へ置き換わります。

| メッセージ | 出力条件 | 推奨対応 |
| --- | --- | --- |
| `Warning: tempfile runtime path is represented as a glob: <path>` | 一時ファイルの実パスを glob 表現で出力した場合です。 | CSV の `<path>` を推定範囲として扱い, 必要に応じて Playbook 実行後の実パスを確認してください。 |
| `Unresolved task: host=<host> role=<role> source=<path>:<line> module=<module>: <reason>` | 実行時値, 未定義変数又は未解決の条件に依存し, タスクを静的に評価できない場合です。 | `source` のファイルと行番号, Module 及び `<reason>` を確認し, CSV に不足する可能性があるファイルを手動で確認してください。 |
| `Playbook file is missing: <path>` | 指定した Playbook が通常ファイルとして存在しない場合です。 | Playbook のパスと実行場所を確認してください。 |
| `Inventory source is missing: <path>` | 指定した Inventory が存在しない場合です。 | Inventory のパスと実行場所を確認してください。 |
| `Analysis failed: Runtime control environment variable must be numeric` | 環境変数へ数値以外を指定した場合です。 | 3 個の実行制御用環境変数を数値で指定してください。 |
| `Analysis failed: Command failed after retries: <command>: <reason>` | `ansible`コマンド又は `ansible-inventory`コマンドが全試行で失敗した場合です。 | `<command>` と `<reason>` を確認し, 接続, 認証, Inventory 又は時間制限の設定を修正してください。 |
| `Analysis failed: ansible-inventory returned invalid JSON` | `ansible-inventory`コマンドの出力を JSON として読み取れない場合です。 | Inventory の構文と `ansible-inventory --list` の出力を確認してください。 |
| `Analysis failed: Role task file is missing: <role>/<tasks_from>` | Role の開始タスクファイルが存在しない場合です。 | Role 名及び `tasks_from` の指定と対象ファイルを確認してください。 |

### 終了コード

| 終了コード | 意味 | CSV 出力 |
| --- | --- | --- |
| `0` | 解析が完了し, 未解決タスクがありません。 | 見出しと解析結果を出力します。結果が 0 件の場合は見出しだけを出力します。 |
| `1` | Playbook 又は Inventory が存在しません。 | 出力しません。 |
| `2` | 解析を継続しましたが, 静的に解決できないタスクがあります。 | 解決できたレコードを出力します。完全な一覧とは限りません。 |
| `3` | 入力内容, 外部コマンド又は環境変数の問題により解析を完了できません。 | 出力しません。 |

引数の書式が不正な場合は, 引数解析機能が使用方法を標準エラー出力へ表示し, 終了コード `2` で終了します。この `2` は, 本ツールが解析中に未解決タスクを検出した場合と同じ値ですが, CSV の有無と標準エラー出力の内容で区別できます。

## テンプレートの取り扱いと生成ファイル

本ツール自体が使用するテンプレートはありません。Playbook 内の Jinja2 式は監査対象の値を確定するために評価しますが, `ansible.builtin.template` の `src` で指定したファイル内容は解析しません。

本ツールが標準出力へ生成するデータは CSV です。ファイル名は本ツールが決定しないため, 実行者が標準出力の転送先として `result.csv` などを指定します。診断も同様に, 標準エラー出力の転送先として `error.log` などを指定します。

Facts の取得時に作成する一時ディレクトリは処理終了時に削除します。本ツールは対象ホスト上のファイルを作成, 変更又は削除しません。

## 実行フロー

1. コマンドライン引数と実行制御用の環境変数を検証します。
2. Playbook と Inventory の存在を確認します。
3. Playbook と `import_playbook` の参照先を読み取ります。
4. `ansible`コマンドで各 Play の対象ホストを選択し, `--limit` の指定を反映します。
5. `ansible-inventory`コマンドでホスト変数とホストの集まりを取得します。
6. `ansible`コマンドの `ansible.builtin.setup` で対象ホストの Facts を取得します。
7. ホストごとに Playbook の変数, 条件, 繰り返し処理及び Role を解析します。
8. 対象 Module の引数から操作種別とファイルパスを抽出します。
9. 解決済みレコードを並べ替え, 重複を除いて標準出力へ CSV を出力します。
10. 警告又は未解決タスクを標準エラー出力へ表示し, 状態に応じた終了コードで終了します。

## 検証ポイント

### 検証の前提条件

検証を始める前に, 次の条件が満たされていることを確認します。

- Python 3.10 以上を利用できること。
- `ansible`コマンド及び `ansible-inventory`コマンドを利用できること。
- `ansible_backup_audit.py` を読み取れること。
- 検証対象の `site.yml` と `inventory/hosts` が存在すること。
- Inventory の対象ホストへ Ansible で接続し, Facts を取得できること。
- カレントディレクトリに `result.csv` と `error.log` を作成できること。

### 検証環境の設定

本節では, 検証用の設定内容について説明します。

外部コマンドが 120 秒以内に完了する環境では, 環境変数の設定は不要です。対象ホスト数が多い環境では, 「環境変数」の設定例を参考に適切な値に変更ください。

検証では, Playbook に記載した全 Role と全対象ホストを解析します。影響範囲を限定して先に確認する場合は, `--limit` と `--role` を指定してください。

### 検証コマンドと期待結果

**書式の確認**:

```bash
python3 ansible_backup_audit.py --help
```

期待結果は, `playbook`, `--inventory`, `--limit`, `--role` 及び `--verbose` の説明が表示され, 終了コードが `0` になることです。

**Inventory の確認**:

```bash
ansible-inventory -i inventory/hosts --list > /tmp/ansible-inventory.json
```

期待結果は, `/tmp/ansible-inventory.json` に Inventory の JSON が出力され, 終了コードが `0` になることです。

**対象ホストへの接続確認**:

```bash
ansible -i inventory/hosts 'all' --list-hosts
ansible -i inventory/hosts 'all' -m ansible.builtin.setup -a 'gather_subset=!all,min'
```

期待結果は, 1 個目のコマンドに対象ホスト名が表示され, 2 個目のコマンドで各対象ホストの Facts が表示され, 両方の終了コードが `0` になることです。実際の Playbook の対象が `all` ではない場合は, `all` を対象のホストパターンへ置き換えてください。

**監査結果の確認**:

```bash
python3 ansible_backup_audit.py site.yml \
  --inventory inventory/hosts \
  > result.csv \
  2> error.log
status=$?
head -n 5 result.csv
printf 'exit=%s\n' "$status"
```

期待結果は, `result.csv` の先頭行が `HOST,ROLE,OP,PATH` であることです。全タスクを解決できた場合は `exit=0` となり, 未解決タスクがある場合は `exit=2` となって `error.log` に `Unresolved task:` で始まる行が記録されます。

**Role を限定した結果の確認**:

```bash
python3 ansible_backup_audit.py site.yml \
  --inventory inventory/hosts \
  --role common \
  > result-common.csv \
  2> error-common.log
awk -F, 'NR > 1 && $2 != "common" { print; exit 1 }' result-common.csv
```

期待結果は, `result-common.csv` の `ROLE` 列がすべて `common` となり, `awk`コマンドの終了コードが `0` になることです。

## トラブルシューティング

### 終了コードが `2` になる

`error.log` の `Unresolved task:` を確認してください。`source` に示されたファイルと行番号で, `register` による実行結果, 実行時に生成される値, 未定義変数又は未解決の条件へ依存している可能性があります。

解決済みのレコードは `result.csv` に出力されていますが, 結果は完全とは限りません。未解決タスクが操作するファイルを Playbook から手動で確認し, 監査結果へ補完してください。

### Facts の取得に失敗する

標準エラー出力の `Command failed after retries` に含まれる `ansible`コマンドと理由を確認してください。Inventory, 接続先, 認証情報, 権限及びネットワークを確認します。対象ホストが一時的に応答しない場合は, 環境変数`ANSIBLE_BACKUP_AUDIT_TIMEOUT`, `ANSIBLE_BACKUP_AUDIT_RETRIES` 及び `ANSIBLE_BACKUP_AUDIT_RETRY_INTERVAL` を増やして再実行してください。

### Playbook 又は Inventory が見つからない

Playbook と Inventory のパスは, コマンド実行時のカレントディレクトリを基準に解決されます。`--inventory` を省略した場合は, カレントディレクトリの `inventory/hosts` を使用します。実行場所を確認し, 必要に応じて両方のパスを明示してください。

### `Role` で指定したロール中にタスクファイルが見つからない

本ツールは, 指定した Playbook の親ディレクトリを Ansible プロジェクトのルートとし, その直下の `roles/<Role名>` を参照します。外部の Role 探索パスや Ansible Galaxy の導入先を探索しません。`-r <Role名>`指定時に, 正しいRole名を指定するようにしてください。

### CSV を表計算ソフトウェアで正しく読めない

標準出力と標準エラー出力を別々のファイルへ保存してください。`2>&1` で統合すると, 警告と未解決タスクが CSV に混入します。CSV は UTF-8 で出力され, 行区切りには改行文字を使用します。

### 一時ファイルのパスに `*` が含まれる

`ansible.builtin.tempfile` の実ファイル名は Playbook 実行時に決まるためです。`*` を任意の文字列として扱い, `path`, `prefix` 及び `suffix` から推定した範囲でバックアップ対象を設定してください。

### 必要なファイルが CSV に含まれない

対象 Module 表にない Module, コマンド実行で間接的に操作するファイル, テンプレート内容から参照するファイル, ハンドラーだけに記載された処理及び対象ホスト以外への `delegate_to` は抽出対象外です。終了コード `2` の場合は未解決タスク ( `error.log` の `Unresolved task:` ) も確認してください。

## 注意事項

- 本ツールの結果は, 静的に解析できる明示的なファイル操作を対象とします。Playbook 実行後の状態を保証するものではありません。
- Facts の取得では対象ホストへ接続して `ansible.builtin.setup` を実行します。監査前に対象環境への接続が許可されていることを確認してください。
- 本ツールは, Playbook の通常タスクは実行しないため, 対象ホストのファイルを変更しません。
- `shell`, `command`, 独自 Module 又はスクリプトが操作するファイルは抽出しません。
- `handlers` ディレクトリの処理は解析しません。
- Playbook 直下の `tasks`, `pre_tasks` 及び `post_tasks` は解析せず, `roles/` ディレクトリ配下に記載された Role を解析します。
- `ansible.builtin.template` は出力先 `dest` を記録しますが, `src` の内容とテンプレートから参照される別ファイルは解析しません。
- ディレクトリ操作はバックアップ対象ファイルとして出力しません。
- `ansible.posix.authorized_key` の `path` を省略した処理は, 利用者別の既定パスを静的に確定できないため未解決になる場合があります。
- `ansible.posix.sysctl` は `sysctl_file` に明示されたパスを対象とします。引数を省略した処理は未解決になる場合があります。
- `--role` は Role 名の完全一致で選択します。存在しない名前を指定した場合は, CSV の見出しだけが出力される場合があります。
- `--verbose` の指定時は未解決タスクを検出時と解析終了時に表示するため, 同じ診断が 2 回表示される場合があります。
- CSV の `PATH` は対象ホスト上のパスです。監査を実行するホスト上のパスではありません。
- 終了コード `2` でも CSV は生成されます。CSV の存在だけで成功と判定せず, 終了コードと標準エラー出力も確認してください。

## 参考資料

### 公式ドキュメント

- [Python Documentation](https://docs.python.org/3/): Python, 標準出力, 標準エラー出力, 終了コード及び環境変数の参照資料です。
- [Ansible documentation](https://docs.ansible.com/ansible/latest/): Ansible, Playbook, Inventory, Role, Module, Facts, FQCN, ホストパターン, `ansible`コマンド及び `ansible-inventory`コマンドの参照資料です。
- [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/installing-packages/): `pip`コマンドの参照資料です。
- [GNU Coreutils Manual](https://www.gnu.org/software/coreutils/manual/coreutils.html): `head`コマンド及び `printf`コマンドの参照資料です。
- [YAML specification](https://yaml.org/spec/1.2.2/): YAML の参照資料です。
- [JSON](https://www.json.org/json-en.html): JSON の参照資料です。
- [RFC 4180: Common Format and MIME Type for Comma-Separated Values Files](https://www.rfc-editor.org/rfc/rfc4180): CSV の参照資料です。
- [Jinja documentation](https://jinja.palletsprojects.com/): Jinja2 の参照資料です。
- [PyYAML documentation](https://pyyaml.org/wiki/PyYAMLDocumentation): PyYAML の参照資料です。
- [Python glob documentation](https://docs.python.org/3/library/glob.html): glob 表現の参照資料です。
- [GNU Awk User's Guide](https://www.gnu.org/software/gawk/manual/): `awk`コマンドの参照資料です。
