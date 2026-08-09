# nfs-server ロール

本ロールは, Debian系およびRHEL系ホストに対してNFSサーバを構築するためのロールです。

## 目次

- [nfs-server ロール](#nfs-server-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
    - [主な処理](#主な処理)
    - [ディレクトリ構成](#ディレクトリ構成)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
    - [Makefileを使用した実行](#makefileを使用した実行)
    - [直接 ansible-playbook で実行](#直接-ansible-playbook-で実行)
  - [主要変数](#主要変数)
    - [NFS設定](#nfs設定)
    - [依存変数](#依存変数)
  - [実行フロー](#実行フロー)
    - [ハンドラ](#ハンドラ)
    - [OS差異](#os差異)
  - [検証ポイント](#検証ポイント)
    - [前提条件確認](#前提条件確認)
    - [検証ステップ](#検証ステップ)
      - [Step 1: NFSサービス状態確認](#step-1-nfsサービス状態確認)
      - [Step 2: idmapd設定確認](#step-2-idmapd設定確認)
      - [Step 3: exports設定確認](#step-3-exports設定確認)
      - [Step 4: 公開状態確認](#step-4-公開状態確認)
      - [Step 5: ログ確認](#step-5-ログ確認)
      - [Step 6: マウント動作確認(任意)](#step-6-マウント動作確認任意)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. 主要タスクが実行されず, 変更が入らない場合](#1-主要タスクが実行されず-変更が入らない場合)
    - [2. nfs-server サービスが active にならない場合](#2-nfs-server-サービスが-active-にならない場合)
    - [3. idmapd の Domain が意図値にならない場合](#3-idmapd-の-domain-が意図値にならない場合)
    - [4. /etc/exports が期待どおりに更新されない場合](#4-etcexports-が期待どおりに更新されない場合)
    - [5. クライアントからマウントできない場合](#5-クライアントからマウントできない場合)
    - [6. mount 時に access denied が出る場合](#6-mount-時に-access-denied-が出る場合)
    - [7. GUI 無効化が期待どおりに反映されない場合](#7-gui-無効化が期待どおりに反映されない場合)
    - [8. restart\_nfs ハンドラが動かない場合](#8-restart_nfs-ハンドラが動かない場合)
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
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| Network File System | NFS | ネットワーク越しにファイル共有を行う仕組み。 |
| Network File System version 4 | NFSv4 | NFSの第4版です。 |
| Domain Name System | DNS | 名前と IP アドレスを対応付ける仕組み。 |
| Classless Inter-Domain Routing | CIDR | IP アドレスとネットワークプレフィックス長を組み合わせた表記法。 |
| User Identifier | UID | 利用者を識別する番号。 |
| Group Identifier | GID | Unix/Linux システムでグループを一意に識別するための数値。ファイルのグループ所有権やアクセス制御に使用される。 |
| Graphical User Interface | GUI | 画面操作中心の利用形態です。 |
| Remote Procedure Call | RPC | ネットワーク越しに処理を呼び出す仕組みです。 |
| RPC bind service | rpcbind | RPCサービスの待受情報を管理するサービスです。 |
| identity mapping daemon | idmapd | NFSv4でユーザ名とUID/GID対応を扱うデーモンです。 |
| sticky bit | sticky bit | 共有ディレクトリで削除権限を制御する属性です。 |
| root squash option | root_squash | クライアント側root権限を制限するNFSオプションです。 |
| no root squash option | no_root_squash | クライアント側root権限を制限しないNFSオプションです。 |
| Kerberos version 5 privacy mode | sec=krb5p | NFS通信の認証と暗号化を有効化するオプションです。 |
| system and service manager | systemd | Linuxのサービス起動と状態管理を行う仕組みです。 |
| multi-user target | multi-user.target | GUIを使わないサーバ向けのsystemd起動状態です。 |
| export table manager command | exportfs | NFS公開設定を表示, 更新するコマンドです。 |
| NFS export list viewer | showmount | NFSサーバの公開一覧を確認するコマンドです。 |
| journalctl | journalctl | systemd ジャーナルのログを参照するコマンド。 |
| Red Hat Enterprise Linux | RHEL | Red Hatが提供する企業向けLinuxディストリビューション。 |
| Ansible | Ansible | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| Ansible Playbook | playbook | 自動化処理の実行手順を順序付きで記述したファイル。 |
| role | role | 特定の名前空間内で有効な権限の集合。 |
| tag | tag | Ansibleで実行対象を絞るラベルです。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Red Hat Enterprise Linux 9 | RHEL9 | Red Hat Enterprise Linux の第9系統版。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `grep` | - | テキストから条件に一致する行を抽出するコマンド。 |
| makeコマンド | make | Makefile に定義された処理を実行するコマンド。 |
| `mkdir` | - | ディレクトリを作成するコマンド。 |
| `systemctl` | - | systemd 管理下のサービスを起動, 停止, 状態確認するコマンド。 |
| サービス | - | 機能を利用者や他システムへ提供する仕組み。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| ログイン | - | 利用者認証を行って利用を開始する操作。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |

## 概要

このロールは, Debian系およびRHEL系ホストに対してNFSサーバを構築するためのロールです。公開ディレクトリ作成, `idmapd`設定, `exports`設定, `nfs-server`サービス再起動までを実行します。


### 主な処理

本ロールの処理内容の概要は以下の通りです:

1. NFSパッケージの導入。
- Debian系では`nfs-kernel-server`, RHEL系では`nfs-utils`を導入します。

2. 公開ディレクトリの作成。
- `nfs_export_directory`を作成し, 権限`1777`で設定します。

3. 設定ファイルの更新。
- `/etc/idmapd.conf`の`Domain`を更新します。
- `/etc/exports`へ公開設定を追加または更新します。

4. NFSサービスの反映。
- `nfs-server`を再起動し, 自動起動を有効化します。

### ディレクトリ構成

主要な設定対象ファイルは以下の通りです:

```plaintext
/etc/idmapd.conf
/etc/exports
{{ nfs_export_directory }} (既定: /home/nfsshare)
```

## 前提条件

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- Ansible 2.15 以降, ansibleメタパッケージをディストリビューションから導入していることを想定
- 対象ノードで管理者権限が利用できること。
- `dns_domain`, `network_ipv4_network_address`, `network_ipv4_prefix_len`は, 実運用値で上書きすること。
- `nfs_export_directory`, `dns_domain`, `nfs_network`のいずれかが空文字の場合, `package.yml`, `directory.yml`, `service.yml`, `config.yml`は実行されません。

## 実行方法

### Makefileを使用した実行

```bash
cd /path/to/ubuntu-setup/ansible
make run_nfs_server
```

### 直接 ansible-playbook で実行

```bash
# site.yml をタグ指定で実行
ansible-playbook -i inventory/hosts site.yml --tags "nfs-server"

# 対象ホストを限定して実行
ansible-playbook -i inventory/hosts site.yml --tags "nfs-server" -l <対象ホスト>

# server.yml を直接実行する例
ansible-playbook -i inventory/hosts server.yml --tags "nfs-server"
```

## 主要変数

### NFS設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `nfs_export_directory` | `/home/nfsshare` | NFSで公開するディレクトリです。 |
| `nfs_network` | `""` | NFS公開を許可するクライアント側ネットワークです (例: `"192.168.20.0/24"`)。**空文字のままでは主要処理を実行しません**。 |
| `nfs_options` | `""` | `/etc/exports`へ書き込むNFS公開オプションです。空文字または未定義時はNFSのデフォルト動作を使用します。 |

### 依存変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `nfs_server_packages` | OS依存 | Debian系は`nfs-kernel-server`, RHEL系は`nfs-utils`です。 |
| `dns_domain` | `""` | `/etc/idmapd.conf`へ設定するドメインです。**空文字のままでは主要処理を実行しません**。 |

## 実行フロー

本ロールは以下の6フェーズで処理します。

1. **Load Params**。
- Debian系では`vars/packages-ubuntu.yml`を読み込みます。
- RHEL系では`vars/packages-rhel.yml`を読み込みます。
- 共通で`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`を読み込みます。

2. **Package**。
- `nfs_server_packages`をインストールします。
- 変更があれば`disable_gui`ハンドラを通知します。
- `dns_domain`, `network_ipv4_network_address`, `network_ipv4_prefix_len`がすべて有効値の場合のみ実行します。

3. **Directory**。
- `nfs_export_directory`を`root:root`, `1777`で作成します。
- `dns_domain`, `network_ipv4_network_address`, `network_ipv4_prefix_len`がすべて有効値の場合のみ実行します。

4. **Config**。
- `/etc/idmapd.conf`の`Domain`を更新します。
- `/etc/exports`へ公開設定を追記または更新します。
- `nfs-server`を再起動し, `enabled: true`を設定します。
- `dns_domain`, `network_ipv4_network_address`, `network_ipv4_prefix_len`がすべて有効値の場合のみ実行します。

### ハンドラ

本ロールでは, 以下のハンドラを登録します:

| ハンドラ名 | listen名 | 処理内容 | 呼び出し元 |
| --- | --- | --- | --- |
| Disable_gui | `disable_gui` | `systemctl set-default multi-user.target`を実行し, GUIログインを無効化します。 | `tasks/package.yml` |
| Restart_nfs | `restart_nfs` | `nfs-server`を再起動し有効化します。 | 将来予約, 現状は, ハンドラのnotify元はなし, 再起動は config.yml の通常タスクで実行 |

### OS差異

OS間での動作の差異を以下に示します:

| 項目 | Debian系 | RHEL系 |
| --- | --- | --- |
| NFSパッケージ | `nfs-kernel-server` | `nfs-utils` |
| 変数ファイル読込 | `vars/packages-ubuntu.yml` | `vars/packages-rhel.yml` |
| NFS設定反映処理 | 共通 | 共通 |

## 検証ポイント

### 前提条件確認

- ロール実行が正常終了していること。
- NFSサーバノードへログイン可能であること。
- クライアント検証を行う場合は, NFSクライアントノードからNFSサーバノードへ到達可能であること。

### 検証ステップ

#### Step 1: NFSサービス状態確認

**実施ノード**: NFSサーバノード

**コマンド**:
```bash
systemctl is-active nfs-server
systemctl is-enabled nfs-server
```

**期待される出力例**:
```plaintext
active
enabled
```

**確認ポイント**:
- `nfs-server`が`active`であること。
- `nfs-server`が`enabled`であること。

#### Step 2: idmapd設定確認

**実施ノード**: NFSサーバノード

**コマンド**:
```bash
grep -E '^\s*Domain\s*=\s*' /etc/idmapd.conf
```

**期待される出力例**:
```plaintext
Domain = example.local
```

**確認ポイント**:
- `Domain`行が存在すること。
- 値が`dns_domain`と一致すること。

#### Step 3: exports設定確認

**実施ノード**: NFSサーバノード

**コマンド**:
```bash
grep -F '{{ nfs_export_directory }}' /etc/exports
```

**期待される出力例**:
```plaintext
/home/nfsshare 192.168.1.0/24(rw,no_root_squash,sync,no_subtree_check,no_wdelay)
```

**確認ポイント**:
- `nfs_export_directory`, `nfs_network`, `nfs_options`が反映されていること。

#### Step 4: 公開状態確認

**実施ノード**: NFSサーバノード

**コマンド**:
```bash
exportfs -v
showmount -e localhost
```

**期待される出力例**:
```plaintext
/home/nfsshare  192.168.1.0/24(...)
Export list for localhost:
/home/nfsshare 192.168.1.0/24
```

**確認ポイント**:
- 対象ディレクトリが公開一覧に表示されること。
- ネットワーク制限が意図どおりであること。

#### Step 5: ログ確認

**実施ノード**: NFSサーバノード

**コマンド**:
```bash
journalctl -u nfs-server -n 50 --no-pager
```

**期待される出力例**:
```plaintext
... Started NFS server and services.
```

**確認ポイント**:
- 直近ログに致命的なエラーがないこと。

#### Step 6: マウント動作確認(任意)

**実施ノード**: NFSクライアントノード

**コマンド**:
```bash
sudo mkdir -p /mnt/nfs-test
sudo mount -t nfs <nfs-server-ip>:{{ nfs_export_directory }} /mnt/nfs-test
mount | grep /mnt/nfs-test
```

**期待される出力例**:
```plaintext
<nfs-server-ip>:/home/nfsshare on /mnt/nfs-test type nfs4 (...)
```

**確認ポイント**:
- NFSクライアントノードからマウントできること。
- ファイルシステムタイプが`nfs`または`nfs4`であること。

## トラブルシューティング

### 1. 主要タスクが実行されず, 変更が入らない場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
grep -nE '^(nfs_export_directory|dns_domain|nfs_network):' group_vars/all/all.yml host_vars/*.yml
grep -nE 'Package|Directory|Config' build*.log
```

**確認ポイント**:

- nfs_export_directory, dns_domain, nfs_network の3変数が空文字でないこと。
- 実行ログで Package, Directory, Config が skipped ではないこと。

### 2. nfs-server サービスが active にならない場合

**実施対象ホスト**: NFSサーバノード

**実行するコマンド**:

```bash
systemctl status nfs-server --no-pager
journalctl -u nfs-server -n 100 --no-pager
```

**確認ポイント**:

- サービス状態が active (running) であること。
- ログに起動失敗や依存サービス不足が出ていないこと。
- 不足パッケージ又は設定不整合を修正後に systemctl restart nfs-server で再確認すること。

### 3. idmapd の Domain が意図値にならない場合

**実施対象ホスト**: NFSサーバノード

**実行するコマンド**:

```bash
grep -E '^\s*Domain\s*=\s*' /etc/idmapd.conf
```

**確認ポイント**:

- Domain 行が存在すること。
- Domain の値が dns_domain と一致すること。
- 値を修正した場合はロール再実行後に反映状態を再確認すること。

### 4. /etc/exports が期待どおりに更新されない場合

**実施対象ホスト**: NFSサーバノード

**実行するコマンド**:

```bash
grep -n '/etc/exports\|{{ nfs_export_directory }}' /etc/exports
exportfs -v
```

**確認ポイント**:

- /etc/exports の対象行に nfs_export_directory, nfs_network, nfs_options が反映されていること。
- nfs_network が CIDR 形式であること。
- nfs_options が有効なカンマ区切り書式であること。

### 5. クライアントからマウントできない場合

**実施対象ホスト**: NFSサーバノード, NFSクライアントノード

**実行するコマンド**:

```bash
showmount -e localhost
exportfs -v
```

**確認ポイント**:

- 公開ディレクトリが showmount の一覧に表示されること。
- クライアント側の接続元アドレスが nfs_network に含まれること。
- サーバ到達性とファイアウォール設定が運用要件と一致すること。

### 6. mount 時に access denied が出る場合

**実施対象ホスト**: NFSサーバノード

**実行するコマンド**:

```bash
exportfs -v
exportfs -ra
```

**確認ポイント**:

- exportfs -v の公開先ネットワークがクライアント接続元と一致すること。
- exports の再読込後も失敗する場合は nfs_network の設定値を見直すこと。

### 7. GUI 無効化が期待どおりに反映されない場合

**実施対象ホスト**: NFSサーバノード

**実行するコマンド**:

```bash
systemctl get-default
systemctl status nfs-server --no-pager
```

**確認ポイント**:

- package タスクが changed にならない場合は disable_gui ハンドラが通知されないこと。
- 即時反映が必要な場合は systemctl set-default multi-user.target 実行後に default target を再確認すること。

### 8. restart_nfs ハンドラが動かない場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
grep -n 'notify\|restart_nfs' roles/nfs-server/tasks/*.yml roles/nfs-server/handlers/*.yml
```

**確認ポイント**:

- 現行実装では restart_nfs の notify 元が未定義であること。
- NFS 再起動は Config フェーズの通常 task で実行される設計であること。
- ハンドラ経由へ統一する場合は notify と handler の設計追加が必要であること。


## 注意事項

- `restart_nfs`ハンドラは定義されていますが, 現在のタスク構成ではnotifyで呼び出されていません。
- `nfs_options`で`no_root_squash`を使用する場合は, セキュリティ要件に応じて`root_squash`への変更を検討してください。
- より強い保護が必要な場合は`sec=krb5p`の利用を検討してください。
- 高負荷環境では`rpcbind`やNFS関連サービスのパラメータ調整が必要になる場合があります。
- 複数エクスポートを管理する場合は, `/etc/exports.d/`利用を含む拡張方針を検討してください。

## 参考資料

### 公式ドキュメント

- [NFS Howto and Documentation](https://nfs.sourceforge.net/)
- [nfs-utils project](https://github.com/stefanha/nfs-utils)
- [systemd documentation](https://www.freedesktop.org/wiki/Software/systemd/)
