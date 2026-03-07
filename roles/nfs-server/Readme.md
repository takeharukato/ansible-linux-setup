# nfs-server ロール

このロールは, Debian系およびRHEL系ホストに対してNFSサーバを構築するためのロールです。公開ディレクトリ作成, `idmapd`設定, `exports`設定, `nfs-server`サービス再起動までを実行します。

## 概要

### 構成要素

このロールは以下を構成します。

1. NFSパッケージの導入。
- Debian系では`nfs-kernel-server`, RHEL系では`nfs-utils`を導入します。

2. 公開ディレクトリの作成。
- `nfs_export_directory`を作成し, 権限`1777`で設定します。

3. 設定ファイルの更新。
- `/etc/idmapd.conf`の`Domain`を更新します。
- `/etc/exports`へ公開設定を追加または更新します。

4. NFSサービスの反映。
- `nfs-server`を再起動し, 自動起動を有効化します。

### 実装の流れ

ロール実行時には以下の順で処理します。

1. 変数読み込み (`load-params.yml`)。
2. パッケージ導入 (`package.yml`)。
3. 共有ディレクトリ作成 (`directory.yml`)。
4. ユーザ/グループ処理 (`user_group.yml`, 現状は空実装)。
5. サービス処理 (`service.yml`, 現状は空実装)。
6. 設定反映 (`config.yml`)。

### ディレクトリ構成

主要な設定対象は以下です。

```plaintext
/etc/idmapd.conf
/etc/exports
{{ nfs_export_directory }} (既定: /home/nfsshare)
```

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Network File System | NFS | ネットワーク越しにファイル共有を行う仕組み。 |
| Network File System version 4 | NFSv4 | NFSの第4版です。 |
| Domain Name System | DNS | ドメイン名と IP アドレスを対応付ける分散型名前解決システム。人間が読みやすいドメイン名をコンピュータが扱える IP アドレスに変換する。 |
| Classless Inter-Domain Routing | CIDR | IP アドレスとネットワークプレフィックス長を組み合わせた表記法 (例: 192.168.1.0/24)。柔軟なネットワーク分割を可能にする。 |
| User Identifier | UID | Unix/Linux システムでユーザを一意に識別するための数値。ファイル所有者やプロセス実行者の特定に使用される。 |
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
| system journal viewer | journalctl | systemd管理サービスのログ確認コマンドです。 |
| Red Hat Enterprise Linux | RHEL | Red Hat系の企業向けLinuxディストリビューションです。 |
| Ansible | Ansible | インフラストラクチャの構成管理と自動化を行うオープンソースツール。YAML 形式のプレイブックでシステム構成を記述し, SSH を使用して複数のリモートホストに対して冪等な変更を実行できる。 |
| playbook | playbook | Ansibleの実行手順ファイルです。 |
| role | role | Ansibleで機能単位にまとめた構成です。 |
| tag | tag | Ansibleで実行対象を絞るラベルです。 |

## 前提条件

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- Ansible 2.15 以降, ansibleメタパッケージをディストリビューションから導入していることを想定
- 対象ノードで管理者権限が利用できること。
- `dns_domain`, `network_ipv4_network_address`, `network_ipv4_prefix_len`は, 実運用値で上書きすること。
- `dns_domain`または`network_ipv4_network_address`が空文字, もしくは`network_ipv4_prefix_len`が0/空の場合, `package.yml`, `directory.yml`, `service.yml`, `config.yml`は実行されません。

## 実行フロー

ロールは以下の6フェーズで処理します。

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

4. **User Group**。
- 現在の実装では有効な処理はありません。

5. **Service**。
- 現在の実装では有効な処理はありません。
- `dns_domain`, `network_ipv4_network_address`, `network_ipv4_prefix_len`がすべて有効値の場合のみ実行します。

6. **Config**。
- `/etc/idmapd.conf`の`Domain`を更新します。
- `/etc/exports`へ公開設定を追記または更新します。
- `nfs-server`を再起動し, `enabled: true`を設定します。
- `dns_domain`, `network_ipv4_network_address`, `network_ipv4_prefix_len`がすべて有効値の場合のみ実行します。

## 主要変数

### NFS設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `nfs_export_directory` | `/home/nfsshare` | NFSで公開するディレクトリです。 |
| `nfs_network` | `{{ network_ipv4_network_address }}/{{ network_ipv4_prefix_len }}` | NFS公開を許可するクライアント側ネットワークです。 |
| `nfs_options` | `rw,no_root_squash,sync,no_subtree_check,no_wdelay` | `/etc/exports`へ書き込むNFS公開オプションです。 |

### 依存変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `nfs_server_packages` | OS依存 | Debian系は`nfs-kernel-server`, RHEL系は`nfs-utils`です。 |
| `dns_domain` | `""` | `/etc/idmapd.conf`へ設定するドメインです。空文字のままでは主要処理を実行しません。 |
| `network_ipv4_network_address` | `""` | クライアントネットワークアドレスです。空文字のままでは主要処理を実行しません。 |
| `network_ipv4_prefix_len` | `0` | クライアントネットワークのプレフィックス長です。`0`または空値では主要処理を実行しません。 |

## 主な処理

- NFSパッケージを導入します。
- 共有ディレクトリを作成します。
- `idmapd`の`Domain`設定を反映します。
- `/etc/exports`へ公開設定を反映します。
- `nfs-server`を再起動して設定を有効化します。
- `disable_gui`ハンドラにより`multi-user.target`を適用できます。

## テンプレート / 出力ファイル

### 出力ファイル

| 種別 | 出力先 | 説明 |
| --- | --- | --- |
| ディレクトリ | `{{ nfs_export_directory }}` | NFS公開ディレクトリを作成します。 |
| 設定更新 | `/etc/idmapd.conf` | `Domain = {{ dns_domain }}`を反映します。 |
| 設定更新 | `/etc/exports` | `{{ nfs_export_directory }} {{ nfs_network }}({{ nfs_options }})`を反映します。 |

## ハンドラ

| ハンドラ名 | listen名 | 処理内容 | 呼び出し元 |
| --- | --- | --- | --- |
| Disable_gui | `disable_gui` | `systemctl set-default multi-user.target`を実行します。 | `tasks/package.yml` |
| Restart_nfs | `restart_nfs` | `nfs-server`を再起動し有効化します。 | 現在はnotify元なし |

## OS差異

| 項目 | Debian系 | RHEL系 |
| --- | --- | --- |
| NFSパッケージ | `nfs-kernel-server` | `nfs-utils` |
| 変数ファイル読込 | `vars/packages-ubuntu.yml` | `vars/packages-rhel.yml` |
| NFS設定反映処理 | 共通 | 共通 |

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

## 検証

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

## 補足

- `user_group.yml`と`service.yml`は現状では空実装です。
- `restart_nfs`ハンドラは定義されていますが, 現在のタスク構成ではnotifyで呼び出されていません。
- `nfs_options`で`no_root_squash`を使用する場合は, セキュリティ要件に応じて`root_squash`への変更を検討してください。
- より強い保護が必要な場合は`sec=krb5p`の利用を検討してください。
- 高負荷環境では`rpcbind`やNFS関連サービスのパラメータ調整が必要になる場合があります。
- 複数エクスポートを管理する場合は, `/etc/exports.d/`利用を含む拡張方針を検討してください。

## 参考リンク

- [NFS Howto and Documentation](https://nfs.sourceforge.net/)
- [nfs-utils project](https://github.com/stefanha/nfs-utils)
- [systemd documentation](https://www.freedesktop.org/wiki/Software/systemd/)
