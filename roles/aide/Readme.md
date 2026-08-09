# Advanced Intrusion Detection Environment (AIDE)導入ロール

本ロールは, Advanced Intrusion Detection Environment (AIDE) を,
RHEL と Ubuntu のパッケージから導入します。

## 目次

- [Advanced Intrusion Detection Environment (AIDE)導入ロール](#advanced-intrusion-detection-environment-aide導入ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. `aide: command not found` が表示される場合](#1-aide-command-not-found-が表示される場合)
    - [2. `aide --version` が失敗する場合](#2-aide---version-が失敗する場合)
    - [3. `sudo aide --check` でデータベース未存在エラーが出る場合](#3-sudo-aide---check-でデータベース未存在エラーが出る場合)
    - [4. 設定ファイルが見つからない場合](#4-設定ファイルが見つからない場合)
    - [5. `aide --check` 実行時に権限エラーが出る場合](#5-aide---check-実行時に権限エラーが出る場合)
  - [注意事項](#注意事項)
    - [AIDEの設定ファイルに対するドロップインディレクトリの扱いについて](#aideの設定ファイルに対するドロップインディレクトリの扱いについて)
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
| サービスアカウント (Service Account) | - | 自動処理中でサービスを呼び出す側のプログラムを識別するための識別情報。 |
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
| ノード | - | ネットワークに接続された機器または処理単位。 |
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
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| Advanced Intrusion Detection Environment | AIDE | ファイルシステムの改ざん検知を行うホスト型侵入検知システム, ファイルハッシュでの整合性確認 |
| Red Hat Enterprise Linux | RHEL | Red Hatが提供する企業向けLinuxディストリビューション。 |
| Debian | - | コミュニティ主導で開発される Linux ディストリビューション。 |
| Ubuntu | - | Canonical が提供する Debian 系の Linux ディストリビューション。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| makeコマンド | make | Makefile に定義された処理を実行するコマンド。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
## 概要

本ロールでは, Advanced Intrusion Detection Environment (AIDE) を,
RHEL と Ubuntu のパッケージから導入します。

本ロールは, AIDE に関する設定処理を実施します。

## 前提条件

対象ホストが inventory に登録済みであることを確認します。
関連する共通変数が vars/all-config.yml または host_vars に定義済みであることを確認します。

## 実行方法

制御ホストで以下のコマンドを実行します。

```bash
make run_aide
```
または,
```bash
ansible-playbook -i inventory/hosts site.yml --tags "aide"
```

## 主要変数

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `aide_packages` | AIDE のパッケージ名。 | OS 依存 | `aide_packages: "aide"` |
| `aide_config_path` | AIDE の設定ファイルのパス。 | OS 依存 | `aide_config_path: "/etc/aide/aide.conf"` |
| `aide_database_path` | AIDE のデータベースのパス。 | `"/var/lib/aide/aide.db.gz"` | `aide_database_path: "/var/lib/aide/aide.db.gz"` |
| `aide_config_dropin_dir` | AIDE の設定ファイルのドロップイン用ディレクトリのパス。 | Debian/Ubuntu 系では `"/etc/aide/aide.conf.d"`, RHEL 系では未使用 | `aide_config_dropin_dir: "/etc/aide/aide.conf.d"` |

## 実行フロー

1. [tasks/load-params.yml](tasks/load-params.yml) で OS ごとのパッケージ定義, クロスディストリビューション定義, 共通定義を取り込みます。
2. [tasks/package.yml](tasks/package.yml) が `aide_packages` で定義されたパッケージ (`aide`) を `state: present` で導入します。
3. [tasks/directory.yml](tasks/directory.yml) を実行します。現行実装では, RHEL 系のドロップイン運用差異に関する注記のみで, 追加の作成処理は定義していません。
4. [tasks/user_group.yml](tasks/user_group.yml), [tasks/service.yml](tasks/service.yml), [tasks/config.yml](tasks/config.yml) を順に実行します。現行実装ではこれらのタスクに追加処理定義はありません。

## 検証ポイント

導入後の `aide` コマンドの検証は, 対象ホストで以下の順に実施します。

1. 実行ファイルの配置確認。
2. パッケージ導入状態の確認。
3. `aide --version` によるコマンド実行確認。
4. 設定ファイルパスの存在確認。

Ubuntu/Debian と RHEL 系の両方で共通して, 以下のコマンドを実行します。

```bash
command -v aide
aide --version
```

実行結果の例:
```bash
$ command -v aide
/usr/bin/aide
$ aide --version
AIDE 0.18.6

Compile-time options:
use pcre2: mandatory
use pthread: yes
use zlib compression: yes
use POSIX ACLs: yes
use SELinux: yes
use xattr: yes
use POSIX 1003.1e capabilities: yes
use e2fsattrs: yes
use cURL: no
use Mhash: yes
use GNU crypto library: no
use Linux Auditing Framework: yes
use locale: no
syslog ident: aide
syslog logopt: LOG_CONS
syslog priority: LOG_NOTICE
default syslog facility: LOG_LOCAL0

Default config values:
config file: <none>
database_in: <none>
database_out: <none>

Available compiled-in attributes:
acl: yes
xattrs: yes
selinux: yes
e2fsattrs: yes
caps: yes

Available hashsum attributes:
md5: yes
sha1: yes
sha256: yes
sha512: yes
rmd160: yes
tiger: yes
crc32: yes
crc32b: yes
haval: yes
whirlpool: yes
gost: yes
stribog256: no
stribog512: no

Default compound groups:
R: l+p+u+g+s+c+m+i+n+md5+acl+selinux+xattrs+ftype+e2fsattrs+caps
L: l+p+u+g+i+n+acl+selinux+xattrs+ftype+e2fsattrs+caps
>: l+p+u+g+s+i+n+acl+selinux+xattrs+ftype+e2fsattrs+caps+growing
H: md5+sha1+rmd160+tiger+crc32+haval+gost+crc32b+sha256+sha512+whirlpool
X: acl+selinux+xattrs+e2fsattrs+caps
$ echo $?
0
```

期待結果は以下の通りです。

- `command -v aide` が `/usr/bin/aide` を返すこと。
- `aide --version` が終了コード 0 で完了(`echo $?`の結果が0となること)し, 版数文字列を表示すること。

Ubuntu/Debian 系では, 追加で以下のコマンドを実行し, aideパッケージが導入されていることを確認します:

```bash
dpkg -l | grep -E '^ii\s+aide\b'
```

Ubuntu/Debian 系での実行結果の例:
```bash
dpkg -l | grep -E '^ii\s+aide\b'
ii  aide                                             0.18.6-2ubuntu0.1                                amd64        Advanced Intrusion Detection Environment - dynamic binary
ii  aide-common                                      0.18.6-2ubuntu0.1                                all          Advanced Intrusion Detection Environment - Common files
```

RHEL/AlmaLinux 系では, 追加で以下のコマンドを実行し, aideパッケージが導入されていることを確認します:
```bash
rpm -q aide
```
RHEL 系での実行結果の例:
```bash
$ rpm -q aide
aide-0.19.2-5.el9_8.1.x86_64
```

初回運用前に整合性データベースを作成するために以下を実行します:

```bash
sudo aide --init
sudo cp /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz
```

上記実行後, `sudo aide --check` が実行可能であることを確認します。

実行結果の例:
```bash
$ sudo aide --init
Start timestamp: 2026-08-02 11:00:14 +0900 (AIDE 0.19.2)
AIDE successfully initialized database.
New AIDE database written to /var/lib/aide/aide.db.new.gz

Number of entries:      138746

---------------------------------------------------
The attributes of the (uncompressed) database(s):
---------------------------------------------------

/var/lib/aide/aide.db.new.gz
 SHA256    : RU5N9z8gAL6K2lxwcT3hU3/+Tb14M6u5
             mXVQ+cVkq2A=
 SHA512    : OF0ReXVtC6bSvJQiLeRTI7S5OkcbO6gI
             lU/DipYnzx+7t+aBPwDugeWcy3OuX8he
             df4SOGwM5+fiKnOBCDBOaA==
 STRIBOG256: /ICeSUPmgNNcL1YkLV/8Vt+FPUSDIbGE
             nlxvcTJZZEE=
 STRIBOG512: BqKNV+HXUAwaJ66awLjTJ/mBQNNbtsWh
             j57FSzoRBizmr54hz4YMh5x7RbWwd+b2
             mpeyW5Md3E/L0NQWWIxKRw==
 SHA512/256: D+A17iIwQFPM+fSRkJHgWogIVNtvQfaP
             Ivil9Xg7+7s=
 SHA3-256  : zBFECdhNya7Dp8Q84sXRYB8k7xhNlt/V
             aJJeGNmnkvU=
 SHA3-512  : fOqQlcWQV8/C0mrc7X+8W5BDnTftF5vS
             H70IjZDz0Bo2oCrN5ee3Fbs7YsVJze17
             Wxt1hsZWQdxTaEQ+zD5FYQ==


End timestamp: 2026-08-02 11:02:31 +0900 (run time: 2m 17s)
$ sudo cp /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz
$ sudo aide --check
Start timestamp: 2026-08-02 11:03:54 +0900 (AIDE 0.19.2)
AIDE found NO differences between database and filesystem. Looks okay!!

Number of entries:      138746

---------------------------------------------------
The attributes of the (uncompressed) database(s):
---------------------------------------------------

/var/lib/aide/aide.db.gz
 SHA256    : RU5N9z8gAL6K2lxwcT3hU3/+Tb14M6u5
             mXVQ+cVkq2A=
 SHA512    : OF0ReXVtC6bSvJQiLeRTI7S5OkcbO6gI
             lU/DipYnzx+7t+aBPwDugeWcy3OuX8he
             df4SOGwM5+fiKnOBCDBOaA==
 STRIBOG256: /ICeSUPmgNNcL1YkLV/8Vt+FPUSDIbGE
             nlxvcTJZZEE=
 STRIBOG512: BqKNV+HXUAwaJ66awLjTJ/mBQNNbtsWh
             j57FSzoRBizmr54hz4YMh5x7RbWwd+b2
             mpeyW5Md3E/L0NQWWIxKRw==
 SHA512/256: D+A17iIwQFPM+fSRkJHgWogIVNtvQfaP
             Ivil9Xg7+7s=
 SHA3-256  : zBFECdhNya7Dp8Q84sXRYB8k7xhNlt/V
             aJJeGNmnkvU=
 SHA3-512  : fOqQlcWQV8/C0mrc7X+8W5BDnTftF5vS
             H70IjZDz0Bo2oCrN5ee3Fbs7YsVJze17
             Wxt1hsZWQdxTaEQ+zD5FYQ==


End timestamp: 2026-08-02 11:05:56 +0900 (run time: 2m 2s)
```

## トラブルシューティング

### 1. `aide: command not found` が表示される場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
command -v aide
echo "$PATH"
dpkg -l | grep -E '^ii\s+aide\b' || rpm -q aide
```

**確認ポイント**:

- `command -v aide` が `/usr/bin/aide` を返すこと。
- パッケージ導入状態を確認できること。
- 未導入の場合はロールを再実行し, 導入後に再確認すること。

### 2. `aide --version` が失敗する場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
aide --version
rpm -V aide 2>/dev/null || true
```

**確認ポイント**:

- `aide --version` が終了コード 0 で完了すること。
- 失敗する場合はパッケージ破損や依存関係不整合を疑い, パッケージ再導入を検討すること。

### 3. `sudo aide --check` でデータベース未存在エラーが出る場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
sudo aide --init
sudo cp /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz
sudo aide --check
```

**確認ポイント**:

- 初期化後に `/var/lib/aide/aide.db.gz` が存在すること。
- `sudo aide --check` が実行可能になること。

### 4. 設定ファイルが見つからない場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
ls -l /etc/aide/aide.conf /etc/aide.conf
```

**確認ポイント**:

- Ubuntu/Debian 系は `/etc/aide/aide.conf` を参照すること。
- RHEL 系は `/etc/aide.conf` を参照すること。
- 実環境の `aide_config_path` 定義値が OS と一致すること。

### 5. `aide --check` 実行時に権限エラーが出る場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
sudo aide --check
```

**確認ポイント**:

- root 権限での実行が必要であること。
- sudo 実行権限が不足する場合は対象ホスト側の権限設定を見直すこと。

## 注意事項

### AIDEの設定ファイルに対するドロップインディレクトリの扱いについて

本来は, AIDE の設定ファイルに対するドロップインディレクトリを Ubuntu と Debian 系に寄せて, `/etc/aide/aide.conf.d` ディレクトリを作成するよう RHEL 系でも処理を追加し, 統一した運用を行えることが望ましい。

しかし, 本ロール作成時点での RHEL 9 系ディストリビューションに標準で搭載されている AIDE のバージョンは 0.16 であり, ワイルドカード指定での設定ファイルのインクルードや `@@x_include` ディレクティブがサポートされていない。

このため, ドロップインディレクトリの自動読み込みを Ubuntu と Debian 環境と同様には行えないことから, RHEL 系ではドロップインディレクトリを作成しないようにした。

本ロール作成時の Ubuntu と Debian 系, RHEL 系における AIDE の差異は以下の通り。

- Debian と Ubuntu: `/etc/aide/aide.conf.d` ディレクトリはパッケージにより自動作成され, 標準でドロップインディレクトリとしてサポートされている。
- RHEL と AlmaLinux: AIDE 0.16 ではワイルドカードや `@@x_include` をサポートしていないため, ドロップインディレクトリの自動読み込みができない。インクルード対象ファイルごとに `@@include` ディレクティブを追記する必要がある。

## 参考資料

### 公式ドキュメント

- [AIDE](https://aide.github.io/)
- [Red Hat Enterprise Linux 9 の AIDE 解説](https://docs.redhat.com/ja/documentation/red_hat_enterprise_linux/9/html/security_hardening/checking-integrity-with-aide_security-hardening)
