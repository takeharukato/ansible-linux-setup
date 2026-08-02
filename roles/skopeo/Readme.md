# skopeo ロール

本ロールは, skopeo を OS 標準パッケージから導入し, bash/zsh の補完ファイルを配置します。

## 目次

- [skopeo ロール](#skopeo-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
    - [主な処理](#主な処理)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
    - [makeターゲットから実行](#makeターゲットから実行)
    - [ansible-playbook で実行](#ansible-playbook-で実行)
    - [変数を上書きしてansible-playbook で実行](#変数を上書きしてansible-playbook-で実行)
  - [主要変数](#主要変数)
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
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
    - [OS 差異](#os-差異)
  - [検証ポイント](#検証ポイント)
    - [導入されたskopeoの版数確認方法](#導入されたskopeoの版数確認方法)
      - [skopeoコマンドの版数確認方法](#skopeoコマンドの版数確認方法)
      - [OSディストリビューションから導入されたパッケージの導入状態の確認方法](#osディストリビューションから導入されたパッケージの導入状態の確認方法)
    - [シェル補完スクリプトの導入確認方法](#シェル補完スクリプトの導入確認方法)
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
| ノード | - | ネットワークに接続された機器または処理単位。 |
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
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
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Application Programming Interface | API | アプリケーション同士がやり取りする方法を定めた仕様。 |
| Uniform Resource Locator | URL | WWW 上の資源の場所を示す文字列。 |
| Secure Open Container Initiative Operations | skopeo | コンテナレジストリ間コピーやイメージ検査を行う CLI ツール。 |
| Red Hat Enterprise Linux | RHEL | Red Hat 社が提供する商用 Linux ディストリビューション。 |
| Extra Packages for Enterprise Linux | EPEL | Red Hat Enterprise Linux 系向けの追加パッケージ提供元。 |
| Domain Name System | DNS | 名前と IP アドレスを対応付ける仕組み。 |
| Command Line Interface | CLI | 文字入力で操作する利用者向け操作方式。 |
| Yet Another Markup Language | YAML | 設定ファイル形式です。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Application Programming Interface | API | API の正式名称。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Ansible Playbook | playbook | 自動化処理の実行手順を順序付きで記述したファイル。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `crontab` | - | 定期実行設定を登録, 表示, 削除するコマンド。 |
| `curl` | - | URL を指定してデータ送受信を行うコマンド。 |
| `dpkg` | - | Debian パッケージの情報参照や導入確認を行うコマンド。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| `make` | - | Makefile に定義された処理を実行するコマンド。 |
| rpmコマンド | - | RPM パッケージの情報参照や導入確認を行うコマンド。 |
| `tar` | - | 複数ファイルを一つにまとめる, 展開するコマンド。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
| ポート | - | 通信の出入口を識別する番号または接点。 |
| ローカル | - | 実行中の装置や同一環境の内部。 |
| ローカルマウントポイント | - | 実行中ホスト内で保存領域を接続するためのディレクトリ。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |

## 概要
このロールは, skopeo を OS 標準パッケージから導入し, bash/zsh の補完ファイルを配置します。さらに, レジストリ内のコンテナイメージを tar 形式で保存し, イメージ名/タグのディレクトリ構造でまとめたうえで バックアップアーカイブを作成して, バックアップ/リストアを行うスクリプトを導入します。

### 主な処理

1. **skopeo の導入**
	- Debian/Ubuntu は `apt` で `skopeo` を導入します。
	- RHEL 系は `dnf` で導入を試み, パッケージ解決失敗時のみ `epel-release` を導入して再試行します。
2. **shell 補完の配置**
	- [roles/opengrok-server/tasks/config.yml](../opengrok-server/tasks/config.yml) と同方式で, 先に配置先ディレクトリを作成し, template で補完ファイルを配置します。
3. **バックアップ/リストアスクリプトの配置**
	- [roles/redmine-server/tasks/directory.yml](../redmine-server/tasks/directory.yml) と同方式で, template から実行スクリプトを配置します。

## 前提条件

- 対象ホストがインターネットまたは内部ミラーへ接続できること。
- `skopeo_enabled: true` を設定してロールを有効化していること。
- レジストリバックアップ機能を使う場合, `skopeo_enable_backup_script: true` を設定していること。
- `daily-backup-skopeo-images` を非rootで実行する場合, `sudo` コマンドが利用可能で, mount/umount/mkdir/chmod/cp を実行できる権限があること。
- バックアップ対象レジストリ一覧は `/opt/skopeo/etc/registry-backup-restore.yml` (`registry_endpoints`) に設定すること。
- レジストリ API (`/v2/_catalog`, `/v2/<repo>/tags/list`) へ匿名アクセス可能であること。匿名アクセス不可環境では `skopeo_backup_image_list` を明示すること。

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

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `skopeo_enabled` | `false` | ロール有効化フラグ。 |
| `skopeo_completion_enabled` | `true` | bash/zsh 補完導入有効化フラグ。 |
| `skopeo_bash_completion_path` | `/etc/bash_completion.d/skopeo` | bash 補完配置先。 |
| `skopeo_zsh_completion_path` | Debian/Ubuntu: `/usr/share/zsh/vendor-completions/_skopeo`, RHEL 系: `/usr/share/zsh/site-functions/_skopeo` | zsh 補完配置先。 |
| `skopeo_enable_backup_script` | `false` | バックアップ/リストアスクリプト生成有効化フラグ。 |
| `skopeo_registry_endpoints` | `[{'endpoint': 'registry1.local:5000', 'scheme': 'http', 'skip_verify': true}]` | バックアップ対象レジストリエンドポイント一覧。各要素は `endpoint`, `scheme`, `skip_verify` の辞書。実行時は設定ファイル (`registry_endpoints`) を参照。 |
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
| `skopeo_backup_command_path` | `/usr/local/bin/backup-skopeo-images` | バックアップ実行コマンドシンボリックリンク。 |
| `skopeo_restore_command_path` | `/usr/local/bin/restore-skopeo-images` | リストア実行コマンドシンボリックリンク。 |
| `skopeo_daily_backup_command_path` | `/usr/local/bin/daily-backup-skopeo-images` | 日次バックアップ実行コマンドシンボリックリンク。 |
| `skopeo_backup_nfs_server` | `""` | 日次バックアップコピー先のNFSサーバホスト名。 |
| `skopeo_backup_nfs_dir` | `/share` | 日次バックアップコピー先のNFS共有ディレクトリ。 |
| `skopeo_backup_mount_point` | `/mnt` | 日次バックアップ時にNFSをマウントするローカルマウントポイント。 |
| `skopeo_backup_dir_on_nfs` | `/skopeo-backup` | NFSマウントポイント配下のバックアップ配置先サブディレクトリ。 |
| `skopeo_backup_output_dir` | `/mnt/skopeo-backup` | NFS上のバックアップコピー先ディレクトリ。 |

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

## テンプレートと生成ファイル

本ロールでは以下のテンプレート / ファイルを出力します:
主な展開先ホストは, 対象ホスト(既定) です。

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `skopeo.bash-completion.j2` | `/etc/bash_completion.d/skopeo` | skopeo コマンドのシェル補完設定で, 運用時の入力ミスを抑えるための補助ファイルです。 |
| `_skopeo.zsh-completion.j2` | Debian/Ubuntu: `/usr/share/zsh/vendor-completions/_skopeo`, RHEL 系: `/usr/share/zsh/site-functions/_skopeo` | skopeo コマンドのシェル補完設定で, 運用時の入力ミスを抑えるための補助ファイルです。 |
| `skopeo-backup-restore-config.yml.j2` | `/opt/skopeo/etc/registry-backup-restore.yml` | レジストリ一覧, 保存先, 認証方式を定義するバックアップ/リストア共通設定です。 |
| `backup-skopeo-images.py.j2` | `/opt/skopeo/scripts/backup-skopeo-images.py` | バックアップ対象の収集とアーカイブ生成を行う自動化スクリプトです。 |
| `restore-skopeo-images.py.j2` | `/opt/skopeo/scripts/restore-skopeo-images.py` | バックアップ済みデータを検証しながら復元する自動化スクリプトです。 |
| `backup-skopeo-images.sh.j2` | `/opt/skopeo/scripts/backup-skopeo-images.sh` | バックアップ/リストア処理を定期運用に組み込むための実行ラッパスクリプトです。 |
| `restore-skopeo-images.sh.j2` | `/opt/skopeo/scripts/restore-skopeo-images.sh` | バックアップ/リストア処理を定期運用に組み込むための実行ラッパスクリプトです。 |
| `daily-backup-skopeo-images.sh.j2` | `/opt/skopeo/scripts/daily-backup-skopeo-images.sh` | バックアップ/リストア処理を定期運用に組み込むための実行ラッパスクリプトです。 |

## 実行フロー

1. [tasks/load-params.yml](tasks/load-params.yml) で OS 別パッケージ変数を読み込みます。
2. [tasks/package.yml](tasks/package.yml) で skopeo を導入します。
3. [tasks/directory.yml](tasks/directory.yml) でスクリプト/バックアップ用ディレクトリを作成し, 設定ファイル, Python本体, backup/restore/daily スクリプトを配置します。
  あわせて, `backup-skopeo-images`, `restore-skopeo-images`, `daily-backup-skopeo-images` のコマンドシンボリックリンクを `skopeo_command_dir` 配下へ作成します。
4. [tasks/user_group.yml](tasks/user_group.yml) は現状 no-op です。
5. [tasks/service.yml](tasks/service.yml) は現状 no-op です。
6. [tasks/config.yml](tasks/config.yml) で bash/zsh 補完ファイルを配置します。

### OS 差異

| 項目 | Debian/Ubuntu | RHEL 系 |
| --- | --- | --- |
| パッケージ導入 | `apt` | `dnf` |
| EPEL 対応 | 不要 | `skopeo` 解決失敗時のみ `epel-release` を導入して再試行 |
| zsh 補完配置先 | `/usr/share/zsh/vendor-completions/_skopeo` | `/usr/share/zsh/site-functions/_skopeo` |

## 検証ポイント

本節では, 導入されたskopeoの動作確認手順を説明します。本節では, 以下の内容を検証する:

1. 導入されたskopeoの版数確認
2. シェル補完スクリプトの導入確認

### 導入されたskopeoの版数確認方法

本節では, 導入されたskopeoの版数確認方法について記載します。

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

それぞれのファイルが存在し, 読み取り可能となっていることを確認します。

## トラブルシューティング

代表的なトラブルと対処を以下に示します。

| 想定トラブル | 主な原因 | 対処方法 |
| --- | --- | --- |
| ロール実行後も skopeo が導入されない | `skopeo_enabled` が `false` のままで, `tasks/package.yml` 以降がすべてスキップされている | 実行者は `vars/all-config.yml` または `host_vars` で `skopeo_enabled: true` を設定し, 対象ホストに対して再実行します。Ansible 出力で `Package`, `Directory`, `Config` が `skipping` になっていないことを確認します。 |
| RHEL 系で skopeo パッケージ導入に失敗する | 標準リポジトリで `skopeo` が解決できず, `epel-release` 導入後の再試行も失敗している | 実行者は `dnf info skopeo` と `dnf repolist` を確認し, EPEL が有効かどうかを確認します。必要に応じて [roles/repo-rpm/Readme.md](roles/repo-rpm/Readme.md) の設定を先に適用し, 再度ロールを実行します。 |
| backup / restore コマンドが配置されない | `skopeo_enable_backup_script` が `false` のため, 設定ファイル, Python スクリプト, ラッパスクリプト, シンボリックリンク作成が全てスキップされている | 実行者は `skopeo_enable_backup_script: true` を設定し, `/opt/skopeo/scripts` と `/usr/local/bin/backup-skopeo-images` などが生成されることを確認します。 |
| `/opt/skopeo/etc/registry-backup-restore.yml` の内容を変更しても再実行で更新されない | 設定ファイル生成タスクが `force: false` のため, 初回作成後はユーザ編集を保持する実装になっている | 実行者は既存ファイルを直接見直すか, 必要であれば対象ファイルを退避・削除してからロールを再実行します。ロールの再実行だけでは既存設定ファイルは上書きされません。 |
| `backup-skopeo-images` が `registry_endpoints is empty` や `no valid entries found in registry_endpoints` で失敗する | `registry_endpoints` が空, または `endpoint` / `scheme` / `skip_verify` の形式が不正 | 実行者は `/opt/skopeo/etc/registry-backup-restore.yml` の `registry_endpoints` を確認し, `endpoint`, `scheme`, `skip_verify` を持つ辞書の配列に修正します。少なくとも1件の有効なエントリが必要です。 |
| `restore-skopeo-images` が最新アーカイブを見つけられない | `/opt/skopeo/backup` 配下に `.tar.gz` が存在しない, または `backup_dir` 設定が不正 | 実行者は `/opt/skopeo/backup` の内容と `/opt/skopeo/etc/registry-backup-restore.yml` の `backup_dir` を確認します。必要に応じてバックアップを先に実行するか, 復元元アーカイブを第2引数で明示指定します。 |
| `daily-backup-skopeo-images` が NFS マウントで失敗する | `skopeo_backup_nfs_server` が空, NFS 到達不可, 非 root 実行で `sudo` 不可 | 実行者は `skopeo_backup_nfs_server`, `skopeo_backup_nfs_dir`, `skopeo_backup_output_dir` を確認し, `mount -t nfs <server>:<dir> /mnt` が成功することを手動で確認します。非 root 実行時は `sudo` が利用可能であることも確認します。 |

## 注意事項

- コンテナレジストリ内のコンテナイメージのバックアップtarファイルは大容量になりえます。保存領域のストレージサイズやバックアップ方針を十分に検討の上, バックアップ, リストア処理を実施することを推奨します。
- `/opt/skopeo/etc/registry-backup-restore.yml` は初回作成後, ロール再実行では上書きしません。設定変更が必要な場合は, 当該ファイルを直接更新するか, 退避・削除してから再生成する運用としてください。
- `restore.default_destination_registry` の既定値は空文字です。`restore-skopeo-images` 実行時に復元先引数を省略する場合は, 事前に設定ファイルへ復元先レジストリを明示してください。
- `skopeo_backup_image_list` を空にした場合, バックアップ対象イメージの列挙はレジストリの catalog API への匿名アクセス可否に依存します。匿名アクセスを許可しないレジストリでは, バックアップ対象イメージ一覧を明示設定してください。
- `daily-backup-skopeo-images` は NFS 共有先のコピー先ディレクトリに `0777` を設定します。共有先の権限方針と整合することを確認してから運用してください。
- `/opt/skopeo/backup` と `/opt/skopeo/work` は `1777` で作成されます。複数利用者が操作するホストでは, 保存先のアクセス制御方針が適切であることを検討の上, 利用してください。
- `registry_endpoints` に不正な要素がある場合, スクリプトは警告を出して当該要素を読み飛ばします。実行後は想定したレジストリ数が実際に処理されていることを確認してください。

## 参考資料

### 公式ドキュメント

- [skopeo](https://github.com/containers/skopeo)
