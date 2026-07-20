# skopeo ロール

このロールは, skopeo を OS 標準パッケージから導入し, bash/zsh の補完ファイルを配置します。さらに, レジストリ内のコンテナイメージを tar 形式で保存し, イメージ名/タグのディレクトリ構造でまとめたうえで バックアップアーカイブを作成して, バックアップ/リストアを行うスクリプトを導入します。

- [skopeo ロール](#skopeo-ロール)
  - [用語](#用語)
  - [前提条件](#前提条件)
  - [本ロールの主な処理](#本ロールの主な処理)
  - [実行方法](#実行方法)
    - [makeターゲットから実行](#makeターゲットから実行)
    - [ansible-playbook で実行](#ansible-playbook-で実行)
    - [変数を上書きしてansible-playbook で実行](#変数を上書きしてansible-playbook-で実行)
  - [実行フロー](#実行フロー)
  - [主要変数](#主要変数)
  - [テンプレートと出力](#テンプレートと出力)
  - [レジストリ内のコンテナイメージのバックアップ/リストア手順](#レジストリ内のコンテナイメージのバックアップリストア手順)
    - [バックアップスクリプト](#バックアップスクリプト)
      - [バックアップコマンド(`backup-skopeo-images`)のコマンドライン仕様](#バックアップコマンドbackup-skopeo-imagesのコマンドライン仕様)
    - [リストアスクリプト](#リストアスクリプト)
      - [リストアコマンド(`restore-skopeo-images`)のコマンドライン仕様](#リストアコマンドrestore-skopeo-imagesのコマンドライン仕様)
    - [レジストリバックアップ・リストア設定ファイル(`registry-backup-restore.yml`)](#レジストリバックアップリストア設定ファイルregistry-backup-restoreyml)
      - [バックアップ関連設定辞書形式](#バックアップ関連設定辞書形式)
      - [リストア関連設定辞書形式](#リストア関連設定辞書形式)
      - [レジストリバックアップ・リストア設定ファイル(`/opt/skopeo/etc/registry-backup-restore.yml`)記載例](#レジストリバックアップリストア設定ファイルoptskopeoetcregistry-backup-restoreyml記載例)
    - [コンテナレジストリにリストアされたコンテナイメージの確認手順](#コンテナレジストリにリストアされたコンテナイメージの確認手順)
      - [レジストリのカタログを取得することでレジストリ内に登録されているコンテナイメージの一覧を取得する手順](#レジストリのカタログを取得することでレジストリ内に登録されているコンテナイメージの一覧を取得する手順)
      - [登録されている特定イメージのタグ一覧を取得する手順](#登録されている特定イメージのタグ一覧を取得する手順)
    - [定期バックアップ](#定期バックアップ)
      - [crontabを用いた日次バックアップ設定](#crontabを用いた日次バックアップ設定)
    - [バックアップされる内容](#バックアップされる内容)
  - [ハンドラ](#ハンドラ)
  - [OS 差異](#os-差異)
  - [検証方法](#検証方法)
    - [導入されたskopeoの版数確認方法](#導入されたskopeoの版数確認方法)
      - [skopeoコマンドの版数確認方法](#skopeoコマンドの版数確認方法)
      - [OSディストリビューションから導入されたパッケージの導入状態の確認方法](#osディストリビューションから導入されたパッケージの導入状態の確認方法)
    - [シェル補完スクリプトの導入確認方法](#シェル補完スクリプトの導入確認方法)

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Secure Open Container Initiative Operations | skopeo | コンテナレジストリ間コピーやイメージ検査を行う CLI ツール。 |
| Red Hat Enterprise Linux | RHEL | Red Hat 系 Linux ディストリビューション。 |
| Extra Packages for Enterprise Linux | EPEL | RHEL 系向け追加パッケージリポジトリ。 |
| Domain Name System | DNS | ドメイン名と IP アドレスを対応付ける名前解決システム。 |
| Command Line Interface | CLI | 文字ベースのコマンド実行インターフェース。 |
| YAML Ain't Markup Language | YAML | 人間可読なデータシリアライゼーション形式, 設定ファイルで広く使用 |
| Docker | - | コンテナ仮想化技術を用いたアプリケーション実行環境 |

## 前提条件

- 対象ホストがインターネットまたは内部ミラーへ接続できること。
- `skopeo_enabled: true` を設定してロールを有効化していること。
- レジストリバックアップ機能を使う場合, `skopeo_enable_backup_script: true` を設定していること。
- `daily-backup-skopeo-images` を非rootで実行する場合, `sudo` コマンドが利用可能で, mount/umount/mkdir/chmod/cp を実行できる権限があること。
- バックアップ対象レジストリ一覧は `/opt/skopeo/etc/registry-backup-restore.yml` (`registry_endpoints`) に設定すること。
- レジストリ API (`/v2/_catalog`, `/v2/<repo>/tags/list`) へ匿名アクセス可能であること。匿名アクセス不可環境では `skopeo_backup_image_list` を明示すること。

## 本ロールの主な処理

1. **skopeo の導入**
	- Debian/Ubuntu は `apt` で `skopeo` を導入します。
	- RHEL 系は `dnf` で導入を試み, パッケージ解決失敗時のみ `epel-release` を導入して再試行します。
2. **shell 補完の配置**
	- [roles/opengrok-server/tasks/config.yml](../opengrok-server/tasks/config.yml) と同方式で, 先に配置先ディレクトリを作成し, template で補完ファイルを配置します。
3. **バックアップ/リストアスクリプトの配置**
	- [roles/redmine-server/tasks/directory.yml](../redmine-server/tasks/directory.yml) と同方式で, template から実行スクリプトを配置します。

## 実行方法

### makeターゲットから実行

```bash
make run_skopeo
```

### ansible-playbook で実行

```bash
ansible-playbook -i inventory/hosts site.yml --tags "skopeo"
```

### 変数を上書きしてansible-playbook で実行

```bash
ansible-playbook -i inventory/hosts site.yml --tags "skopeo" \
  -e "skopeo_enabled=true" \
  -e "skopeo_enable_backup_script=true" \
  -e 'skopeo_registry_endpoints=[{"endpoint":"registry1.example.local:5000","scheme":"http","skip_verify":true},{"endpoint":"registry2.example.local:5000","scheme":"http","skip_verify":true}]'
```

## 実行フロー

1. [tasks/load-params.yml](tasks/load-params.yml) で OS 別パッケージ変数を読み込みます。
2. [tasks/package.yml](tasks/package.yml) で skopeo を導入します。
3. [tasks/directory.yml](tasks/directory.yml) でスクリプト/バックアップ用ディレクトリを作成し, 設定ファイル, Python本体, backup/restore/daily スクリプトを配置します。
  あわせて, `backup-skopeo-images`, `restore-skopeo-images`, `daily-backup-skopeo-images` のコマンドシンボリックリンクを `skopeo_command_dir` 配下へ作成します。
4. [tasks/user_group.yml](tasks/user_group.yml) は現状 no-op です。
5. [tasks/service.yml](tasks/service.yml) は現状 no-op です。
6. [tasks/config.yml](tasks/config.yml) で bash/zsh 補完ファイルを配置します。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `skopeo_enabled` | `false` | ロール有効化フラグ。 |
| `skopeo_completion_enabled` | `true` | bash/zsh 補完導入有効化フラグ。 |
| `skopeo_bash_completion_path` | `/etc/bash_completion.d/skopeo` | bash 補完配置先。 |
| `skopeo_zsh_completion_path` | OS 依存 | zsh 補完配置先。Debian 系は `vendor-completions`, RHEL 系は `site-functions`。 |
| `skopeo_enable_backup_script` | `false` | バックアップ/リストアスクリプト生成有効化フラグ。 |
| `skopeo_registry_endpoints` | `{{ container_registry_endpoints \| default([], true) }}` | バックアップ対象レジストリエンドポイント一覧。各要素は `endpoint`, `scheme`, `skip_verify` の辞書。実行時は設定ファイル (`registry_endpoints`) を参照。 |
| `skopeo_backup_image_list` | `[]` | バックアップ対象リポジトリ一覧。空なら catalog API で自動列挙。 |
| `skopeo_scripts_dir` | `/opt/skopeo/scripts` | スクリプト配置先。 |
| `skopeo_config_dir` | `/opt/skopeo/etc` | 設定ファイル配置先。 |
| `skopeo_backup_restore_config_path` | `/opt/skopeo/etc/registry-backup-restore.yml` | backup/restore 共通設定ファイル。 |
| `skopeo_python_command` | `/usr/bin/python3` | backup/restore 実体スクリプトを実行する Python コマンド。 |
| `skopeo_backup_dir` | `/opt/skopeo/backup` | バックアップ成果物配置先。 |
| `skopeo_backup_work_dir` | `/opt/skopeo/work` | 一時作業ディレクトリ。 |
| `skopeo_backup_archive_prefix` | `skopeo-images` | 出力するバックアップアーカイブのファイル名につけられる接頭辞。 |
| `skopeo_backup_rotation` | `7` | 保持世代数。 |
| `skopeo_command_dir` | `/usr/local/bin` | `.sh` 拡張子なしコマンドシンボリックリンク配置先。 |
| `skopeo_backup_command_path` | `{{ skopeo_command_dir }}/backup-skopeo-images` | バックアップ実行コマンドシンボリックリンク。 |
| `skopeo_restore_command_path` | `{{ skopeo_command_dir }}/restore-skopeo-images` | リストア実行コマンドシンボリックリンク。 |
| `skopeo_daily_backup_command_path` | `{{ skopeo_command_dir }}/daily-backup-skopeo-images` | 日次バックアップ実行コマンドシンボリックリンク。 |
| `skopeo_backup_nfs_server` | `""` | 日次バックアップコピー先のNFSサーバホスト名。 |
| `skopeo_backup_nfs_dir` | `/share` | 日次バックアップコピー先のNFS共有ディレクトリ。 |
| `skopeo_backup_mount_point` | `/mnt` | 日次バックアップ時にNFSをマウントするローカルマウントポイント。 |
| `skopeo_backup_dir_on_nfs` | `/skopeo-backup` | NFSマウントポイント配下のバックアップ配置先サブディレクトリ。 |
| `skopeo_backup_output_dir` | `{{ skopeo_backup_mount_point }}{{ skopeo_backup_dir_on_nfs }}` | NFS上のバックアップコピー先ディレクトリ。 |

## テンプレートと出力

| テンプレート名 | 出力先ファイル (既定値) | 説明 |
| --- | --- | --- |
| `skopeo-backup-restore-config.yml.j2` | `/opt/skopeo/etc/registry-backup-restore.yml` | backup/restore 共通設定。`force: false` で初回のみ生成。 |
| `backup-skopeo-images.py.j2` | `/opt/skopeo/scripts/backup-skopeo-images.py` | バックアップ本体 (Python)。 |
| `restore-skopeo-images.py.j2` | `/opt/skopeo/scripts/restore-skopeo-images.py` | リストア本体 (Python)。 |
| `skopeo.bash-completion.j2` | `/etc/bash_completion.d/skopeo` | bash 補完定義。 |
| `_skopeo.zsh-completion.j2` | `{{ skopeo_zsh_completion_path }}` | zsh 補完定義。 |
| `backup-skopeo-images.sh.j2` | `/opt/skopeo/scripts/backup-skopeo-images.sh` | バックアップ Python 本体を呼び出すラッパ。 |
| `restore-skopeo-images.sh.j2` | `/opt/skopeo/scripts/restore-skopeo-images.sh` | リストア Python 本体を呼び出すラッパ。 |
| `daily-backup-skopeo-images.sh.j2` | `/opt/skopeo/scripts/daily-backup-skopeo-images.sh` | 日次バックアップ実行ラッパ。 |

## レジストリ内のコンテナイメージのバックアップ/リストア手順

### バックアップスクリプト

本ロールでは, コンテナレジストリからコンテナイメージを取得して, バックアップアーカイブファイルを作成するバックアップコマンドとして, `backup-skopeo-images` を導入します。本コマンドの動作概要は以下の通りです:

1. 共通設定ファイル (`/opt/skopeo/etc/registry-backup-restore.yml`) を読み込みます。
2. バックアップ対象リポジトリを列挙します。
3. 各リポジトリのタグ一覧を取得します。
4. `イメージ名/タグ/image.tar` の形式で `skopeo copy` によりコンテナイメージを作業ディレクトリ上に保存します。
5. 各レジストリごとに, レジストリ内のコンテナイメージをバックアップアーカイブに格納します(アーカイブファイル名は,  `skopeo-images-<registry-key>-YYYYmmdd-HHMMSS.tar.gz`となります。`<registry-key>`には, コンテナイメージを取得したコンテナレジストリのエンドポイントを意味する文字列が入ります。 `YYYYmmdd-HHMMSS`はローカル時刻でのバックアップ生成日時です。YYYYは西暦4桁の年, mmは2桁での月, ddは2桁での日, HHは24時間制での時間, MMは2桁での分, SSは2桁での秒を表します。)。
6. 設定ファイルで指定された保持世代数 (`skopeo_backup_rotation`) をレジストリ単位で適用し, 古いアーカイブを削除します。

コマンドラインの例:
```bash
/usr/local/bin/backup-skopeo-images
```

実行例:
```bash
$ /usr/local/bin/backup-skopeo-images
Backup completed for registry1.local:5000: /opt/skopeo/backup/skopeo-images-registry1.local_5000-20260721-022426.tar.gz
Backup completed for reachable registries
```

正常終了すると, `Backup completed for reachable registries`が出力されます。

`Backup completed for`という文字列の後に, 処理対象となるコンテナレジストリ, バックアップファイル名が出力されていることを確認してください。

また, 必要に応じて, 出力されたバックアップファイルが存在することを(`ls -l`や`tar ztvf`などのコマンドを用いて)確認してください。

#### バックアップコマンド(`backup-skopeo-images`)のコマンドライン仕様

バックアップコマンドの書式は以下の通りです:

```plaintext
backup-skopeo-images [オプション]
```

バックアップコマンド(`backup-skopeo-images`)のオプションは, 以下の通りです(なお, 本コマンドには位置引数はありません。):

|オプション|意味|指定例|
|---|---|---|
|--config|バックアップ/リストア共通設定ファイルへのパスを指定します。既定値は `skopeo_backup_restore_config_path` で指定した `/opt/skopeo/etc/registry-backup-restore.yml` です。|--config /opt/skopeo/etc/registry-backup-restore.yml|

### リストアスクリプト

本ロールでは, コンテナイメージをコンテナレジストリに再登録するリストアコマンドとして, `restore-skopeo-images` を導入します。以下の動作を行います。

1. 引数で指定された復元先レジストリと バックアップアーカイブ を優先して使用します。
2. アーカイブ引数未指定時は設定ファイル の`backup_dir`で指定されたディレクトリ配下から最新の バックアップアーカイブ を選択します。
3. バックアップアーカイブ を展開し, `イメージ名/タグ/image.tar` を走査してイメージ名とタグを復元します。
4. `skopeo copy docker-archive:... docker://...` で指定した復元先レジストリへ復元します。

**指定レジストリ復元する場合**:
以下のコマンドを実行してください:
```bash
/usr/local/bin/restore-skopeo-images <コンテナレジストリのエンドポイント> <バックアップアーカイブへのパス>
```

実行例:

```bash
$ /usr/local/bin/restore-skopeo-images registry1.local:5000 /opt/skopeo/backup/skopeo-images-registry1.local_5000-20260721-022426.tar.gz
Restore completed to registry1.local:5000 from: /opt/skopeo/backup/skopeo-images-registry1.local_5000-20260721-022426.tar.gz
```

**引数を省略して設定ファイル既定値で復元する場合**:
```bash
/usr/local/bin/restore-skopeo-images
```

実行例:

```bash
$ /usr/local/bin/restore-skopeo-images
Restore completed to registry1.local:5000 from: /opt/skopeo/backup/skopeo-images-registry1.local_5000-20260721-022426.tar.gz
```

いずれの場合も, `Restore completed to <レジストリのエンドポイント> from: <リストアに使用したバックアップアーカイブファイルへのパス>`という形式のメッセージが出力されていることを確認してください。

#### リストアコマンド(`restore-skopeo-images`)のコマンドライン仕様

リストアコマンドの書式は以下の通りです:

```plaintext
restore-skopeo-images [オプション] [<復元先コンテナレジストリのエンドポイント>] [<復元元バックアップアーカイブへのパス>]
```

第1位置引数`<復元先コンテナレジストリのエンドポイント>`には, 復元先コンテナレジストリのエンドポイントを`<コンテナレジストリのホスト名, または, IPアドレス>:<コンテナレジストリのポート番号>`形式で指定します(`registry1.local:5000`)。未指定時は設定ファイルの `restore.default_destination_registry` を使用します。

第2位置引数`<復元元バックアップアーカイブへのパス>`には, 復元元バックアップアーカイブへのパスを指定します(例:`/opt/skopeo/backup/skopeo-images-registry1.local_5000-20260721-022426.tar.gz`)。
未指定時は設定ファイルの `backup_dir` 配下から最新の バックアップアーカイブを検索して使用します。

リストアコマンド(`restore-skopeo-images`)のオプションは, 以下の通りです:

|オプション|意味|指定例|
|---|---|---|
|--config|バックアップ/リストア共通設定ファイルへのパスを指定します。既定値は `skopeo_backup_restore_config_path` で指定した `/opt/skopeo/etc/registry-backup-restore.yml` です。|--config /opt/skopeo/etc/registry-backup-restore.yml|

### レジストリバックアップ・リストア設定ファイル(`registry-backup-restore.yml`)

レジストリバックアップ・リストア設定ファイル(規定では, `/opt/skopeo/etc/registry-backup-restore.yml`に配置されます)には, 以下の項目をYAML形式で記載します:

|キー|値|意味|記載例|
|---|---|---|---|
|registry_endpoints|バックアップ/リストア対象となるコンテナレジストリ設定のリストです。各要素は `endpoint`, `scheme`, `skip_verify` を持つ辞書です。|同左|[{"endpoint":"registry1.local:5000","scheme":"http","skip_verify":true}]|
|backup_dir|バックアップアーカイブ格納先ディレクトリ。バックアップ保存先, 及びリストア時の最新アーカイブ探索先として共通利用します。|同左|/opt/skopeo/backup|
|backup|バックアップ関連設定を辞書形式で指定します。|[バックアップ関連設定辞書形式](#バックアップ関連設定辞書形式)参照|[バックアップ関連設定辞書形式](#バックアップ関連設定辞書形式)参照|
|restore|リストア関連設定を辞書形式で指定します。|[リストア関連設定辞書形式](#リストア関連設定辞書形式)参照|[リストア関連設定辞書形式](#リストア関連設定辞書形式)|

#### バックアップ関連設定辞書形式

バックアップ関連設定に記載する項目は, 以下のキーと値からなる辞書として記載します:

|キー|値|記載例|
|---|---|---|
|work_dir|バックアップアーカイブ作成処理で一時的に使用するディレクトリです。|/opt/skopeo/work|
|archive_prefix|バックアップアーカイブファイルのプレフィクス名です。|skopeo-images|
|rotation|バックアップ世代数を指定します。本項目に指定された世代を超えた場合, 古いバックアップファイルは, 削除されます。|7|
|image_list|バックアップ対象となるイメージを表す文字列のリストです。空リストを指定した場合は, コンテナレジストリサーバーの v2 系イメージ(`registry:2`)のカタログAPI(`v2/_catalog`)を使用して自動的にイメージ名の一覧を取得します。|`[]`|

#### リストア関連設定辞書形式

リストア関連設定に記載する項目は, 以下のキーと値からなる辞書として記載します:

|キー|値|記載例|
|---|---|---|
|default_destination_registry|オプション省略時に使用するリストア対象となるコンテナレジストリのエンドポイントを指定します。|registry1.example.local:5000|

#### レジストリバックアップ・リストア設定ファイル(`/opt/skopeo/etc/registry-backup-restore.yml`)記載例

レジストリバックアップ・リストア設定ファイル(`/opt/skopeo/etc/registry-backup-restore.yml`)の記載例は, 以下の通りです:

```yaml
registry_endpoints:
  - endpoint: "registry1.example.local:5000"
    scheme: "http"
    skip_verify: true
  - endpoint: "registry2.example.local:5000"
    scheme: "http"
    skip_verify: true
backup_dir: "/opt/skopeo/backup"

backup:
  work_dir: "/opt/skopeo/work"
  archive_prefix: "skopeo-images"
  rotation: 7
  image_list: []

restore:
  default_destination_registry: "registry1.example.local:5000"
```

### コンテナレジストリにリストアされたコンテナイメージの確認手順

必要に応じて, バックアップアーカイブに保存されたコンテナイメージをコンテナレジストリにリストア後, 適切にコンテナイメージがレジストリに登録されていることを確認してください。本節では, コンテナレジストリに登録されたイメージの基本的な確認手順を記載します。

#### レジストリのカタログを取得することでレジストリ内に登録されているコンテナイメージの一覧を取得する手順

以下のコマンドを実行して, レジストリのカタログを取得することでレジストリ内に登録されているコンテナイメージの一覧を取得します:
```bash
curl -fsSL http://<コンテナレジストリのエンドポイント>/v2/_catalog
```

実行例:
```bash
$ curl -fsSL http://registry1.local:5000/v2/_catalog
{"repositories":["netshoot","vc-tenant-dns"]}
```

#### 登録されている特定イメージのタグ一覧を取得する手順

以下のコマンドを実行して, 登録されている特定イメージのタグの一覧を取得します:
```bash
curl -fsSL http://<コンテナレジストリのエンドポイント>/v2/<イメージ名>/tags/list
```

実行例:
```bash
$ curl -fsSL http://registry1.local:5000/v2/netshoot/tags/list
{"name":"netshoot","tags":["v0.16"]}
```

### 定期バックアップ

`daily-backup-skopeo-images` は日次実行向けコマンドです。以下の処理を順に実行します。

1. `backup-skopeo-images` を実行してローカルにバックアップアーカイブを作成します。
2. `skopeo_backup_nfs_server:skopeo_backup_nfs_dir` を `skopeo_backup_mount_point` へNFSマウントします。
3. `skopeo_backup_dir` 配下で最新のバックアップアーカイブを1つ選択します。
4. 選択したバックアップアーカイブを `skopeo_backup_output_dir` へコピーします。
5. NFSマウントをアンマウントします。

`daily-backup-skopeo-images` は NFSマウントおよびNFS上への書き込みのために特権操作を行います。root 実行でない場合は, スクリプト内部で `sudo` を使用します。

#### crontabを用いた日次バックアップ設定

`crontab -e`コマンドでcrontabエントリを作成することで, 日次バックアップを実施することが可能です。以下の設定では, 毎日午前3時に`skopeo_backup_dir`変数で指定されたディレクトリ(規定の場合, `/opt/skopeo/backup`)`/data/redmine/backup`にバックアップファイルを生成後, NFSサーバと共有ディレクトリに`{{skopeo_backup_nfs_server}}:{{skopeo_backup_nfs_dir}}`を指定してマウントし, バックアップアーカイブを当該ディレクトリにコピーします:

```text
0 3 * * * /usr/local/bin/daily-backup-skopeo-images
```

### バックアップされる内容

本スクリプトから生成されるバックアップアーカイブには, 各レジストリ毎に, リポジトリ名, タグ名のサブディレクトリを作成の上, 対応するコンテナイメージのtarファイルが格納されます。アーカイブ内のディレクトリ構造を以下に示します:


```text
skopeo-images-<registry-key>-YYYYmmdd-HHMMSS/
  <repository-name>/
	 <tag>/
		image.tar
```

`image.tar` は `skopeo copy` で作成した docker-archive 形式イメージです。リストア時はこの構造からリポジトリ名とタグを復元します。

## ハンドラ

現時点では, 本ロールで使用するハンドラはありません。

## OS 差異

| 項目 | Debian/Ubuntu | RHEL 系 |
| --- | --- | --- |
| パッケージ導入 | `apt` | `dnf` |
| EPEL 対応 | 不要 | `skopeo` 解決失敗時のみ `epel-release` を導入して再試行 |
| zsh 補完配置先 | `/usr/share/zsh/vendor-completions/_skopeo` | `/usr/share/zsh/site-functions/_skopeo` |

## 検証方法

本節では, 導入されたskopeoの動作確認手順を説明する。本節では, 以下の内容を検証する:

1. 導入されたskopeoの版数確認
2. シェル補完スクリプトの導入確認

### 導入されたskopeoの版数確認方法

本節では, 導入されたskopeoの版数確認方法について記載する。

#### skopeoコマンドの版数確認方法

skopeoコマンドの版数を確認する場合, 以下のコマンドを実行する:
```bash
skopeo --version
```

実行結果例:
```bash
$ skopeo --version
skopeo version 1.13.3
```

#### OSディストリビューションから導入されたパッケージの導入状態の確認方法

以下のように, OSディストリビューションからskopeoパッケージが導入されていることを確認する:

- Debian/Ubuntu (Ubuntu24.04など)の場合: ` dpkg -l|grep skopeo`
- RHEL (AlmaLinux9.6など)の場合: `rpm -qi skopeo`

Debian/Ubuntu (Ubuntu24.04など)でのパッケージ導入状況確認結果の例:
```bash
$ dpkg -l|grep skopeo
ii  skopeo                                1.13.3+ds1-2ubuntu0.24.04.3                      amd64        Tooling to work with remote images registries
```

RHEL (AlmaLinux9.6など)でのパッケージ導入状況確認結果の例:
```bash
 rpm -qi skopeo
Name        : skopeo
Epoch       : 2
Version     : 1.22.2
Release     : 7.el9_8
Architecture: x86_64
Install Date: Tue 21 Jul 2026 04:52:11 AM JST
Group       : Unspecified
Size        : 29344992
License     : Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND ISC AND MIT AND MPL-2.0
Signature   : RSA/SHA256, Wed 08 Jul 2026 04:11:20 PM JST, Key ID d36cb86cb86b3716
Source RPM  : skopeo-1.22.2-7.el9_8.src.rpm
Build Date  : Wed 08 Jul 2026 03:36:19 AM JST
Build Host  : x64-builder02.almalinux.org
Packager    : AlmaLinux Packaging Team <packager@almalinux.org>
Vendor      : AlmaLinux
URL         : https://github.com/containers/skopeo
Summary     : Inspect container images and repositories on registries
Description :
Command line utility to inspect images and repositories directly on Docker
registries without the need to pull them.
```

### シェル補完スクリプトの導入確認方法

以下のコマンドを実行する:


```bash
ls -l /etc/bash_completion.d/skopeo
ls -l /usr/share/zsh/vendor-completions/_skopeo
```

実行結果例:
```bash
$ ls -l /etc/bash_completion.d/skopeo
-rw-r--r-- 1 root root 1017  7月 21 01:24 /etc/bash_completion.d/skopeo
$ ls -l /usr/share/zsh/vendor-completions/_skopeo
-rw-r--r-- 1 root root 841  7月 21 01:24 /usr/share/zsh/vendor-completions/_skopeo
```

それぞれのファイルが存在し, 読み取り可能となっていることを確認する。