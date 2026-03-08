# Docker Composeを使用したOpenLDAP管理サーバ

このロールは, Docker Composeを使用して, OpenLDAPサーバとphpLDAPadmin(Webベースの管理画面)を構築するロールです。osixia/openldapとosixia/phpldapadminのコンテナイメージを使用し, 2つのコンテナを`docker compose up -d`で起動して, ユーザ, グループ情報を集中管理するLDAP(Lightweight Directory Access Protocol)ディレクトリサービスを提供します。

## 概要

### 構成要素

このロールは以下の2つのコンテナを管理します:

1. **OpenLDAPコンテナ** (`osixia/openldap`) — LDAPディレクトリサービスの本体です。ユーザ, グループ, その他のディレクトリエントリを階層型で管理し, ldapsearchやldapmodifyなどのLDAPユーティリティで直接アクセス可能にします。内部的にはslapd(stand-alone LDAP daemon)プロセスがLDAPリスナーとして動作し, ポート389(標準的なLDAPポート)またはカスタムポート(group_vars/all.ymlの`openldap_service_port`)でクライアント接続を受け付けます。

2. **phpLDAPadminコンテナ** (`osixia/phpldapadmin`) — OpenLDAPの設定, 管理のためのWebベースのユーザインターフェースです。PHPで実装されており, ブラウザからhttps://ホスト名:10443(デフォルト)でアクセスして, LDAP DNの検索, 参照, 編集が可能です。管理者認証にはOpenLDAP管理者の認証情報(cn=admin,...)を使用します。

### 実装の流れ

ロール実行時には以下の処理フローを実施します:

1. パラメータ読み込み — `group_vars`, `host_vars`から変数を読み込む
2. パッケージインストール — ldapクライアントユーティリティ, Docker CE関連パッケージをインストール
3. ユーザ/グループ作成 — OpenLDAPコンテナ実行ユーザ(uid 911, gid 911)をホスト上に事前作成
4. ディレクトリ作成 — `/data/openldap/docker`, `/data/openldap/scripts`, `/data/openldap/slapd/{database,config}`ディレクトリを作成
5. sysctl設定配置 — IPv4/IPv6フォワーディング, RA受信設定を`/etc/sysctl.d/90-ldap-forwarding.conf`に配置
6. コンテナ起動 — `docker-compose.yml`をテンプレートから生成し, `docker compose up -d`で2コンテナを起動
7. 設定調整 — コンテナ起動待機, バックアップスクリプト配置, sysctl再読み込み

### ディレクトリ構成

ロール実行後, ホスト上に以下のディレクトリ構成が生成されます:

```
/data/openldap/
  ├─ docker/
  │  └─ docker-compose.yml         # 2コンテナ定義ファイル(テンプレートから生成)
  ├─ scripts/
  │  ├─ backup-ldap-data.sh        # バックアップスクリプト(テンプレートから生成)
  │  └─ restore-ldap-data.sh       # リストアスクリプト(テンプレートから生成)
  └─ slapd/
     ├─ database/                  # OpenLDAPデータベースボリューム(Dockerマウント)
     └─ config/                    # OpenLDAP設定ファイルボリューム(Dockerマウント)
```

OpenLDAPコンテナは`/data/openldap/slapd/{database,config}`をボリュームマウントして, 永続データ保存と設定共有を実現します。

## 用語

LDAP関連の標準用語については本セクションで定義します。一般的なネットワーク・システム管理用語は `roles/common/Readme.md` を参照してください。

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Lightweight Directory Access Protocol | LDAP | 階層型ディレクトリサービスへのアクセスプロトコル, ユーザやグループ情報を集中管理する際に使用される標準プロトコル |
| Common Name | CN | ディレクトリエントリの一般名, ユーザ名やグループ名として使用される属性 |
| Domain Component | DC | DNSドメインをディレクトリツリーに対応付ける構成要素 |
| Organizational Unit | OU | 組織内の部門や部署を表すディレクトリ階層要素 |
| Distinguished Name | DN | ディレクトリエントリを一意に識別する完全修挙名, CN+OU+DCの組み合わせで構成される |
| PHP: Hypertext Preprocessor | PHP | サーバサイドWebスクリプト言語, phpLDAPadminで使用される |
| User Interface | UI | ユーザがシステムと対話する画面やインターフェース |
| Identifier | ID | 対象を一意に識別するための識別子, ユーザIDやグループIDなど |
| Docker Compose | - | 複数のコンテナからなるマルチコンテナアプリケーション(docker-compose.yml)を一括管理, 起動するツール |
| コンテナ | - | オペレーティングシステムレベルの軽量仕想化技術を用いた独立した実行環境。Dockerコンテナは, Dockerイメージから起動される |
| イメージ | - | Dockerコンテナを起動するためのテンプレートファイル。osixia/openldap, osixia/phpldapadminはコンテナイメージ |
| ボリューム | - | Dockerコンテナ内のディレクトリやファイルシステムをホスト側と共有するためのマウント機構。ローカルディレクトリまたはDocker管理下のボリュームをマウント可能 |
| マウント | - | Dockerコンテナ内に, 外部(ホストやネットワークストレージ)のディレクトリやボリュームを接続する処理 |
| ネットワーク | - | Dockerコンテナ同士が通信するための仮想ネットワーク。docker-compose.ymlで明示的に定義可能 |
| ポートマッピング | - | Dockerコンテナ内のプロセスがリスニングするポート(例えばLDAPなら389)をホスト側のポート(例えば389やカスタムポート)に割り当てる機構 |
| 環境変数 | - | コンテナ起動時に渡される設定情報。docker-compose.ymlの`environment`セクションで指定。OpenLDAPコンテナは環境変数(LDAP_ORGANISATION, LDAP_DOMAIN等)で初期化される |
| daemon, スタンドアロンデーモン | slapd | OpenLDAPのメインプロセス。ポート389(デフォルト)でLDAPクライアント接続を受け付け, LDAP操作を処理する |
| tar | - | ファイルやディレクトリをテープアーカイブ形式に圧縮, 展開するコマンド。LDAPバックアップで設定とデータベースをアーカイブ化 |

## 前提条件

このロール実行前に以下の環境前提条件を満たす必要があります。

1. **対象OS**: Debian系(Ubuntu 20.04 LTS以降)またはRHEL系(9.x以降)が動作するホスト
2. **Ansible**: 2.15以降がインストール済みの管理ノード
3. **Docker CE**: ターゲットホストにDocker CE(Community Edition)がインストール済みであること。Docker Compose v2(docker compose コマンド)で動作可能な状態が必須。
4. **ポート利用可能性**: ターゲットホストで以下のポートが外部から到達可能またはファイアウォールで許可されていること。
   - ポート389(TCP, LDAP標準ポート)
   - ポート10443(TCP, phpLDAPadmin用HTTPS, デフォルト設定の場合)
5. **ディレクトリ権限**: `/data`直下にディレクトリ作成可能な権限をroot(またはsudo)で保持していること。
6. **ディスク容量**: LDAPデータベースボリュームとして最低1GB以上の空き容量を確保していること(環境に応じて拡張必要)
7. **必須変数の設定**: 以下の変数を`group_vars/all`または`host_vars/`で必ず設定すること。設定されていない場合, ロール実行時にfailで停止。
   - `ldap_organization`: LDAP組織名(例: `my-organization`, 空文字列不可)
   - `ldap_domain`: LDAPドメイン名(例: `example.org`, 空文字列不可)

## 実行フロー

ロールは以下の7つのタスク実行フェーズを順序立てて実施します:

1. **Load Params** — `group_vars/all`, `host_vars/`から変数を読み込み, デフォルト値を上書き
2. **Package** — LDAPクライアントユーティリティ(ldap-utils(Debian)/openldap-clients(RHEL)), Docker CE関連パッケージをインストール
3. **User Group** — OpenLDAPコンテナ実行ユーザ(openldap, uid 911, gid 911)をホスト上に事前作成. ボリュームマウント時のディレクトリ所有権を設定するため必須
4. **Directory** — `/data/openldap/docker`, `/data/openldap/scripts`, `/data/openldap/slapd/{database,config}`の各ディレクトリを作成し, 所有権とパーミッション(755)を設定
5. **Sysctl** — IPv4/IPv6フォワーディングとRA受信を有効化する設定ファイル(`/etc/sysctl.d/90-ldap-forwarding.conf`)を配置し, sysctl -pのリロード処理を実行. Dockerネットワーク通信の正常動作に必須
6. **Service** — `docker-compose.yml`をテンプレートから生成してディレクトリに配置, `docker compose up -d`でOpenLDAPコンテナとphpLDAPadminコンテナを起動. 起動待機(デフォルト600秒)処理を実行
7. **Config** — バックアップスクリプト(`backup-ldap-data.sh`, `restore-ldap-data.sh`)をテンプレートから生成して配置, 実行権限(755)を設定. sysctl設定リロード用ハンドラ(`ldap_server_reload_sysctl`)をトリガー



## 主要変数

このロールで使用される主要な変数を以下にカテゴリー分けして記載します。`vars/all-config.yml`, `group_vars/all`, `host_vars/`で値を上書き可能です。

### LDAP基本設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `ldap_organization` | `""` | LDAP組織名。OpenLDAPコンテナの`LDAP_ORGANISATION`環境変数として設定されます。**未定義または空文字列の場合, パッケージインストール, ユーザ/グループ作成, ディレクトリ作成, sysctl設定, サービス起動, 設定ファイル生成の各タスクはスキップされます** |
| `ldap_domain` | `""` | LDAPドメイン名。OpenLDAPコンテナの`LDAP_DOMAIN`環境変数として設定され, DC構成要素に使用されます。**未定義または空文字列の場合, 主要タスクはスキップされます** |
| `ldap_admin_password` | `""` | LDAP管理者(cn=admin)のパスワード。OpenLDAPコンテナの`LDAP_ADMIN_PASSWORD`環境変数として設定されます。**未定義または空文字列の場合, 主要タスクはスキップされます** |
| `ldap_admin_port` | `10443` | phpLDAPadmin Web UI のHTTPS公開ポート番号。**0または未定義の場合, 主要タスクはスキップされます** |

### ディレクトリ設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `openldap_docker_dir` | `/data/openldap/docker` | Docker Compose定義ファイル(docker-compose.yml)の配置先ディレクトリ |
| `openldap_scripts_dir` | `/data/openldap/scripts` | バックアップ, リストアスクリプトの配置先ディレクトリ |
| `openldap_database_dir` | `/data/openldap/slapd/database` | LDAPデータベースの永続化ディレクトリ。Dockerボリュームとしてマウント |
| `openldap_config_dir` | `/data/openldap/slapd/config` | LDAP設定ファイルの永続化ディレクトリ。Dockerボリュームとしてマウント |

### コンテナ設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `openldap_server_user` | `911` | OpenLDAPコンテナ内で使用するユーザID。osixia/openldapイメージの openldapユーザに対応 |
| `openldap_server_grp` | `911` | OpenLDAPコンテナ内で使用するグループID。osixia/openldapイメージの openldapグループに対応 |
| `openldap_service_port` | `389` | OpenLDAPサービスポート番号。外部LDAP接続が必要な場合はポートフォワーディング設定で調整 |

### 待機設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `openldap_wait_host_stopped` | `127.0.0.1` | OpenLDAPサービス停止を待ち合わせる接続先ホスト名またはIPアドレス |
| `openldap_wait_host_started` | `{{ inventory_hostname }}` | OpenLDAPサービス開始を待ち合わせる接続先ホスト名またはIPアドレス。デフォルトはインベントリホスト名 |
| `openldap_wait_timeout` | `600` | OpenLDAPサービス待ち合わせ時間(単位:秒)。コンテナ起動に時間要する場合は増加 |
| `openldap_wait_delay` | `5` | OpenLDAPサービス待ち合わせ開始までの遅延時間(単位:秒)。コンテナ起動完了の待機用 |
| `openldap_wait_sleep` | `2` | OpenLDAPサービス待ち合わせ中の再試行間隔(単位:秒)。短いほど応答性向上, 長いほどリソース消費削減 |
| `openldap_wait_delegate_to` | `localhost` | OpenLDAPサービス待ち合わせ時の接続元ホスト名またはIPアドレス |

### ネットワーク設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `mgmt_nic` | (環境依存) | 管理用ネットワークインターフェース名。sysctl設定でIPv6 RA受信を有効化する際に使用。ansible_facts から自動検出(VMware:ens160, xcp-ng:enX0, その他:eth0) |
| `openldap_enable_ipv6` | `true` | IPv6フォワーディング有効化フラグ。trueの場合, IPv6フォワーディングとRA受信がmgmt_nicで有効化 |





## 主な処理

ロール実行時に以下の主要な処理が実行されます:

1. **パッケージインストール** — ldap-utils(Debian系)またはopenldap-clients(RHEL系)などのLDAPクライアントユーティリティをインストール。Docker CE環境の確保も実施
2. **ユーザ, グループ作成** — OpenLDAPコンテナ実行ユーザ(openldap, uid/gid 911)をホスト側に事前作成。ボリュームマウント時のファイル所有権設定に必須
3. **ディレクトリ初期化** — `/data/openldap/docker`, `/data/openldap/scripts`, `/data/openldap/slapd/{database,config}`ディレクトリを作成し, 所有権をopenldap:openldapに設定, パーミッション755で保護
4. **sysctl設定配置** — `/etc/sysctl.d/90-ldap-forwarding.conf`にIPv4フォワーディング(net.ipv4.ip_forward=1), IPv6フォワーディング(net.ipv6.conf.all.forwarding=1), RA受信設定(net.ipv6.conf.{{ mgmt_nic }}.accept_ra=2)を記載し, `sysctl -p`で反映
5. **Docker Composefile生成** — `docker-compose.yml.j2`テンプレートから`/data/openldap/docker/docker-compose.yml`を生成。2つのコンテナ定義(osixia/openldap, osixia/phpldapadmin), 環境変数, ポートマッピング, ボリュームマウント設定を含む
6. **コンテナ起動** — `docker compose up -d`で2つのコンテナを起動。OpenLDAPコンテナはLDAPリスナーをポート389で起動(カスタムポート設定可能), phpLDAPadminコンテナはWeb UIをポート10443(デフォルト)で起動
7. **サービス待機** — `ansible.builtin.wait_for`タスクでOpenLDAPサービス(ポート389)をpoll。デフォルト600秒以内のサービス応答を確認
8. **バックアップスクリプト配置** — `backup-ldap-data.sh.j2`, `restore-ldap-data.sh.j2`テンプレートから`/data/openldap/scripts/`に生成し, 実行権限(755)を付与。運用期間中のバックアップ, リストア実行をサポート

## テンプレート/出力ファイル

| テンプレート名 | 出力先ファイル(既定値) | 説明 |
| --- | --- | --- |
| `docker-compose.yml.j2` | `/data/openldap/docker/docker-compose.yml` | 2つのコンテナ(osixia/openldap, osixia/phpldapadmin)定義。services セクションで各コンテナの環境変数(LDAP_ORGANISATION, LDAP_DOMAIN, LDAP_ADMIN_PASSWORD等), ports セクションでポートマッピング(389:389, 10443:443), volumes セクションでホストディレクトリマウント(/data/openldap/slapd/*)を記載 |
| `90-ldap-forwarding.conf.j2` | `/etc/sysctl.d/90-ldap-forwarding.conf` | IPv4フォワーディング(net.ipv4.ip_forward=1), IPv6フォワーディング(net.ipv6.conf.all.forwarding=1), RA受信(net.ipv6.conf.{{ mgmt_nic }}.accept_ra=2)を記載するsysctl設定ファイル。Dockerネットワーク通信の正常動作に必須 |
| `backup-ldap-data.sh.j2` | `/data/openldap/scripts/backup-ldap-data.sh` | LDAP設定(/etc/ldap/slapd.d)とデータベース(/var/lib/ldap), phpLDAPadminデータ(/var/www/phpldapadmin)をtar形式でバックアップするシェルスクリプト。busybox コンテナを用いてボリュームをアーカイブ化し, config-backup.tar, data-backup.tar, phpadmin-backup.tar を生成 |
| `restore-ldap-data.sh.j2` | `/data/openldap/scripts/restore-ldap-data.sh` | バックアップアーカイブから LDAP設定, データベース, phpLDAPadminデータをリストアするシェルスクリプト。busybox コンテナを用いてアーカイブを展開, コンテナボリューム内に復元 |

## OS差異

Debian系(Ubuntu等)とRHEL系(RHEL 9.x等)の環境でパッケージ名やサービス名が異なります。本ロールは ansible.builtin.package モジュールにより, OS別の設定値を自動選択します。

| 項目 | Debian/Ubuntu系 | RHEL 9系 |
| --- | --- | --- |
| **LDAPクライアント パッケージ** | ldap-utils | openldap-clients |
| **Docker CE パッケージ** | docker-ce, docker-ce-cli, containerd.io | docker-ce, docker-ce-cli, containerd.io |
| **Docker Composeコマンド** | docker compose(v2, pip3 install via docker.io) | docker compose(v2, pip3 install via docker.io) |
| **パッケージマネージャー** | apt/apt-get | dnf/yum |
| **Docker デーモン管理** | systemctl(systemd) | systemctl(systemd) |

## 実行方法

ロール実行は Makefile またはタグ指定による ansible-playbook 実行で実施。

### Makefile を使用した実行(推奨)

```bash
cd /path/to/ubuntu-setup/ansible
make run_ldap_server
```

### 直接 ansible-playbook で実行

全ホストで実行(タグ指定):
```bash
ansible-playbook -i inventory/hosts site.yml --tags "ldap-server"
```

特定ホストのみ実行:
```bash
ansible-playbook -i inventory/hosts site.yml --tags "ldap-server" -l mgmt-server.local
```

特定タスク(例: Service タスクのみ)実行:
```bash
ansible-playbook -i inventory/hosts site.yml --tags "ldap-server" --tags "service"
```

## ハンドラ

| ハンドラ名 | トリガー条件 | 処理内容 |
| --- | --- | --- |
| ldap_server_reload_sysctl | sysctl設定ファイル(/etc/sysctl.d/90-ldap-forwarding.conf)が更新された場合 | `sysctl --system`を実行し, カーネルパラメータの設定ファイル群を再読み込み。IPv4/IPv6フォワーディング, RA受信設定を即座に反映し, Dockerネットワーク通信を即座に有効化 |

インストール先ホストに WEBブラウザから以下のようにアクセスします。
ポート番号は, `group_vars/all.yml`に記載されている`ldap_admin_port`の値(デフォルトは, `10443`)を指定します。

```
https://ホスト名:10443/
```

ログイン時は, CN (Common Name, 共通名) に`admin`を指定し, ドメイン名を元に DC (Domain Component, ドメイン構成要素) を指定します。

'.' で区切られたドメイン名の各要素をdc=要素名,dc=要素名として並べてDC (Domain Component, ドメイン構成要素) を指定します。

ドメイン名がelliptic-curve.netの場合, 以下を`login`名に入力します。
```
cn=admin,dc=elliptic-curve,dc=net
```

パスワードは, `group_vars/all.yml`に記載されている`ldap_admin_password`の値(デフォルトは, `ldap`)を入力します。

## 検証

ロール実行完了後, 以下の前提条件確認と7つの検証ステップでセットアップ成功を確認します。

### 前提条件確認

実行開始前に, ターゲットホストで以下の条件を確認:

1. **Docker CE がインストール済み**: `docker --version && docker compose version`が正常応答
2. **ポート 389, 10443 が利用可能**: `netstat -tlnp | grep -E :(389|10443)`で他プロセスが使用していないこと確認
3. **ディスク空き容量**: `df -h /data`で最低1GB以上の空き容量確認

### 検証ステップ

#### Step 1: Docker Compose ファイル確認

**実施ノード**: LDAPサーバコンテナ動作ホスト

**コマンド**:
```bash
cat /data/openldap/docker/docker-compose.yml
```

**期待される出力例**:
```yaml
version: '3'
services:
  openldap:
    image: osixia/openldap:...
    environment:
      LDAP_ORGANISATION: "MyOrganization"
      LDAP_DOMAIN: "example.org"
      LDAP_ADMIN_PASSWORD: "admin"
    ports:
      - "389:389"
    volumes:
      - /data/openldap/slapd/database:/var/lib/ldap
      - /data/openldap/slapd/config:/etc/ldap/slapd.d
  phpldapadmin:
    image: osixia/phpldapadmin:...
    ports:
      - "10443:443"
```

**確認ポイント**: テンプレート変数が展開され, 環境変数(`LDAP_ORGANISATION`, `LDAP_DOMAIN`)とポートマッピング(389:389, 10443:443)が記載されていることを確認します。

#### Step 2: コンテナ起動状態確認

**実施ノード**: LDAPサーバコンテナ動作ホスト

**コマンド**:
```bash
docker ps
```

**期待される出力例**:
```
CONTAINER ID   IMAGE                    COMMAND                  CREATED        STATUS       PORTS                                             NAMES
abcd1234efgh   osixia/openldap:...      "/container/tool/run"   5 minutes ago  Up 5 minutes 0.0.0.0:389->389/tcp                openldap
ijkl5678mnop   osixia/phpldapadmin:...  "/container/tool/run"   5 minutes ago  Up 5 minutes 0.0.0.0:10443->443/tcp              phpldapadmin
```

**確認ポイント**: 以下の項目が確認できることを確認します:
- osixia/openldap コンテナが Up 状態で動作していること
- osixia/phpldapadmin コンテナが Up 状態で動作していること
- ポート 389 がマッピングされていること
- ポート 10443 がマッピングされていること

#### Step 3: OpenLDAP サービス接続確認

**実施ノード**: LDAPサーバコンテナ動作ホスト

**コマンド**:
```bash
ldapsearch -x -H ldap://localhost:389 -b "dc=example,dc=com" -s base
```

**期待される出力例**:
```
# extended LDIF
#
# LDAPv3
# base <dc=example,dc=com> with scope baseObject
# filter: (objectclass=*)
# requesting: ALL
#

# example.org
dn: dc=example,dc=com

searchResult: success
resultCode: 0 (Success)
```

**確認ポイント**: 以下の項目が確認できることを確認します:
- LDAPサーバがポート389で応答していること (resultCode: 0 Success)
- ベース DN(dc=example,dc=com)が正しく返されていること
- 検索コマンドがエラーなく完了していること

#### Step 4: phpLDAPadmin Web UI ログイン確認

**実施ノード**: クライアントPC

**アクセスURL**:
```
https://mgmt-server.local:10443/
```

**ログイン情報**:
- Login DN: `cn=admin,dc=example,dc=com`
- Password: `admin`

**期待される状態**: ログイン成功後, phpLDAPadminのダッシュボードが表示され, ディレクトリツリーが左パネルに表示されます。

**確認ポイント**: 以下の項目が確認できることを確認します:
- HTTPS接続でWebサイトにアクセスできること
- ログイン画面が表示されること
- 入力したログイン情報で認証成功すること
- ディレクトリツリーが表示され, ディレクトリエントリの検索・参照・編集操作が可能なこと

#### Step 5: LDAP エントリ作成テスト

**実施ノード**: LDAPサーバコンテナ動作ホスト

**テスト手順**: phpLDAPadmin Web UI またはコマンドラインから新規 OU エントリを作成します。

**作成コマンド例**:
```bash
ldapadd -x -D "cn=admin,dc=example,dc=com" -w admin <<EOF
dn: ou=testunit,dc=example,dc=com
objectClass: organizationalUnit
ou: testunit
EOF
```

**確認コマンド**:
```bash
ldapsearch -x -H ldap://localhost:389 -b "ou=testunit,dc=example,dc=com" -s base
```

**期待される出力例**:
```
# extended LDIF
# base <ou=testunit,dc=example,dc=com> with scope baseObject

dn: ou=testunit,dc=example,dc=com
objectClass: organizationalUnit
ou: testunit

searchResult: success
resultCode: 0 (Success)
```

**確認ポイント**: 以下の項目が確認できることを確認します:
- ldapadd コマンドがエラーなく完了していること (または Web UI で作成成功)
- ldapsearch で新規作成したエントリが検索結果に表示されていること (resultCode: 0 Success)
- LDAP ディレクトリへの書き込みと読み取り機能が正常に動作していること

#### Step 6: sysctl 設定確認

**実施ノード**: LDAPサーバコンテナ動作ホスト

**コマンド**:
```bash
sysctl net.ipv4.ip_forward net.ipv6.conf.all.forwarding
```

**期待される出力例**:
```
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
```

**確認ポイント**: 以下の項目が確認できることを確認します:
- `net.ipv4.ip_forward` が `1`(有効)に設定されていること
- `net.ipv6.conf.all.forwarding` が `1`(有効)に設定されていること
- これらの設定により, Dockerネットワーク通信が正常に動作することが保証されます

#### Step 7: バックアップスクリプト動作確認

**実施ノード**: LDAPサーバコンテナ動作ホスト

**テスト手順**:
```bash
cd /tmp
/data/openldap/scripts/backup-ldap-data.sh
ls -la config-backup.tar data-backup.tar phpadmin-backup.tar
```

**期待される出力例**:
```
-rw-r--r-- 1 root root  10240 Mar  7 10:30 config-backup.tar
-rw-r--r-- 1 root root  20480 Mar  7 10:31 data-backup.tar
-rw-r--r-- 1 root root  51200 Mar  7 10:32 phpadmin-backup.tar
```

**確認ポイント**: 以下の項目が確認できることを確認します:
- バックアップスクリプト (`/data/openldap/scripts/backup-ldap-data.sh`) がエラーなく完了していること
- `config-backup.tar` (LDAP設定)が生成されていること
- `data-backup.tar` (LDAPデータベース)が生成されていること
- `phpadmin-backup.tar` (phpLDAPadminデータ)が生成されていること
- 全ファイルがサイズを持つ正常なアーカイブファイルとして生成されていること

## バックアップ方法

以下のバックアップスクリプトを実行すると, LDAP の設定, データベースをカレントディレクトリにバックアップします。

- config-backup.tar LDAP の設定
- data-backup.tar   LDAP のデータベース
- phpadmin-backup.tar phpldapadminのデータ

事前に,

```
cd /data/openldap/docker
docker compose pause
```

を実行してコンテナ内のプロセスを停止してから
`/data/openldap/scripts/backup-ldap-data.sh`スクリプトを実行します。
`backup-ldap-data.sh`スクリプトは, 以下の処理を行います。

- カレントディレクトリをコンテナの/backupディレクトリにマウント
- busyboxのコンテナを起動
- tar コマンドで/etc/ldap/slapd.d, /var/lib/ldapディレクトリを, それぞれ, config-backup.tar, data-backup.tar, phpadmin-backup.tarに保存
- コンテナを破棄

```:backup-ldap-data.sh
#!/bin/sh
#  -*- coding:utf-8 mode:bash -*-
#
# busyboxのコンテナイメージを使用して, 以下の内容をopenldapコンテナ内
# の以下のファイルをカレントディレクトリにtar形式で保存する
#
# a) openldapの設定ファイル(openldapのコンテナ中の/etc/ldap/slapd.d ディレクトリの内容)
# b) openldapのデータベース(openldapのコンテナ中の/var/lib/ldap ディレクトリの内容)
# c) phpldapadminの設定 (phpldapadminのコンテナ中の/var/www/phpldapadmin ディレクトリの内容)
#

# 1) openldapのコンテナIDを取得する
ldap_container_id=`docker ps|grep osixia/openldap:|awk -F ' ' '{print $1;}'`

# 2) phpldapadminのコンテナIDを取得する
phpadmin_container_id=`docker ps|grep osixia/phpldapadmin:|awk -F ' ' '{print $1;}'`

# 3) ホストのカレントディレクトリをコンテナ内の/backupディレクトリにマウントして
# busyboxのコンテナを生成, openldapコンテナ内のボリュームを参照し,
# openldapの設定ファイルディレクトリ(/etc/ldap/slapd.d)の内容をカレントディ
# レクトリのconfig-backup.tarにtar形式で保存する
docker run --rm --volumes-from "${ldap_container_id}" -v `pwd`:/backup busybox tar cvf /backup/config-backup.tar /etc/ldap/slapd.d

# 4) ホストのカレントディレクトリをコンテナ内の/backupディレクトリにマウントして
# busyboxのコンテナを生成, openldapコンテナ内のボリュームを参照し,
# openldapのデータベースディレクトリ(/var/lib/ldap)の内容をカレントディ
# レクトリのconfig-backup.tarにtar形式で保存する
docker run --rm --volumes-from "${ldap_container_id}" -v `pwd`:/backup busybox tar cvf /backup/data-backup.tar /var/lib/ldap

# 5) ホストのカレントディレクトリをコンテナ内の/backupディレクトリにマウントして
# busyboxのコンテナを生成, phpldapadminコンテナ内のボリュームを参照し,
# phpladpadminの設定ファイルディレクトリ(/var/www/phpldapadmin)の内容をカレントディ
# レクトリのphpadmin-backup.tarにtar形式で保存する
docker run --rm --volumes-from "${phpadmin_container_id}" -v `pwd`:/backup busybox tar cvf /backup/phpadmin-backup.tar /var/www/phpldapadmin
```

上記が完了したら以下のコマンドを実行して, コンテナを再開します。

```
cd /data/openldap/docker
docker compose unpause
```

## 設定例

### group_vars/all での設定

`group_vars/all/all.yml` でロール全体の共通設定を定義:

```yaml
# LDAP 基本設定
ldap_organization: "MyOrganization"    # 組織名 ( 必須 )
ldap_domain: "example.org"             # ドメイン名 ( 必須 )
ldap_admin_password: "admin"           # 管理者パスワード ( デフォルト値 )
ldap_admin_port: 10443                 # phpLDAPadmin Web UI ポート

# ディレクトリ設定
openldap_docker_dir: "/data/openldap/docker"
openldap_scripts_dir: "/data/openldap/scripts"
openldap_database_dir: "/data/openldap/slapd/database"
openldap_config_dir: "/data/openldap/slapd/config"

# 待機設定
openldap_wait_timeout: 600             # サービス待機時間(秒)
openldap_wait_delay: 5
openldap_wait_sleep: 2
```

### host_vars/mgmt-server.local での設定

ホスト固有の設定を `host_vars/mgmt-server.local` に記載します。ここで設定した値は `group_vars` での設定を上書きします:

```yaml
# 管理サーバ固有設定
ldap_organization: "TechDepartment"    # 組織名を上書き
ldap_domain: "ldap.example.org"        # ドメイン名を上書き ( オプション )
ldap_admin_password: "secure_password" # 管理者パスワードを上書き ( セキュリティ上, 環境変数推奨 )
openldap_service_port: 389             # LDAPポート
openldap_enable_ipv6: true             # IPv6 有効化
```

以下のリストアスクリプトを実行すると, LDAP (Lightweight Directory Access Protocol, 軽量ディレクトリアクセスプロトコル) の設定, データベースをカレントディレクトリのconfig-backup.tar, data-backup.tar, phpadmin-backup.tar からリストアします。

事前に,

```
cd /data/openldap/docker
docker compose pause
```

を実行してコンテナ内のプロセスを停止してから
`/data/openldap/scripts/restore-ldap-data.sh`スクリプトを実行します。
`restore-ldap-data.sh`スクリプトは, 以下の処理を行います。

- カレントディレクトリをコンテナの/backupディレクトリにマウント
- busyboxのコンテナを起動
- tar コマンドで/etc/ldap/slapd.d, /var/lib/ldapディレクトリを, それぞれ, config-backup.tar, data-backup.tar, phpadmin-backup.tarから展開
- コンテナを破棄

```:restore-ldap-data.sh
#!/bin/sh
#  -*- coding:utf-8 mode:bash -*-
# This file is generated by ansible.
{# 日付の取得 #}
# last update: {{ '%Y-%m-%d %H:%M:%S %Z' | strftime(ansible_date_time.epoch) }}
#
# busyboxのコンテナイメージを使用して, ホスト上のカレントディレクトリにあるtarファイルの
# 内容をopenldapコンテナ内で定義されているボリュームに展開する
#

# 1) openldapのコンテナIDを取得する
container_id=`docker ps|grep osixia/openldap:|awk -F ' ' '{print $1;}'`

# 2) phpldapadminのコンテナIDを取得する
phpadmin_container_id=`docker ps|grep osixia/phpldapadmin:|awk -F ' ' '{print $1;}'`

# 3) ホストのカレントディレクトリをコンテナ内の/backupディレクトリにマウントした上で,
# openldapコンテナのボリュームを参照可能にして, busyboxのコンテナを生成し,
# カレントディレクトリにあるconfig-backup.tarの内容をopenldapのコンテナ内に展開する
docker run --rm --volumes-from "${container_id}" -v `pwd`:/backup busybox tar xvf /backup/config-backup.tar -C /

# 4) ホストのカレントディレクトリをコンテナ内の/backupディレクトリにマウントした上で,
# openldapコンテナのボリュームを参照可能にして, busyboxのコンテナを生成し,
# カレントディレクトリにあるdata-backup.tarの内容をopenldapのコンテナ内に展開する
docker run --rm --volumes-from "${container_id}" -v `pwd`:/backup busybox tar xvf /backup/data-backup.tar -C /

# 4) ホストのカレントディレクトリをコンテナ内の/backupディレクトリにマウントした上で,
# phpldapadminコンテナのボリュームを参照可能にして, busyboxのコンテナを生成し,
# カレントディレクトリにあるphpadmin-backup.tarの内容をopenldapのコンテナ内に展開する
docker run --rm --volumes-from "${phpadmin_container_id}" -v `pwd`:/backup busybox tar xvf /backup/phpadmin-backup.tar -C /
```

上記が完了したら以下のコマンドを実行して, コンテナを再開します。

```
cd /data/openldap/docker
docker compose unpause
```

## 補足

このセクションでは, ldap-serverロールの運用や拡張の際に参考となる追加情報を記載します。

### Docker Compose v2 について

本ロールはDocker Compose v2(Composeコマンド)を使用することを前提としています。Docker Engine 20.10以上の環境で`docker compose`コマンド(ハイフンなし)で実行します。

```bash
docker compose -f docker-compose.yml up -d
docker compose -f docker-compose.yml down
docker compose -f docker-compose.yml ps
```

### ボリューム永続化について

OpenLDAPデータベースとphpLDAPadmin設定データを専用ボリュームに保存する仕様とした背景配下の通り:

- **コンテナのリサイクル**: コンテナを削除, 再作成しても, ボリューム内のデータは永続化される
- **バックアップの簡素化**: ボリューム内のファイルをホスト側からアクセス可能なため, バックアップスクリプトで容易に抽出できる
- **パフォーマンス**: ボリュームを適切に設定することで, コンテナ間のI/O性能が向上する可能性がある

### セキュリティ考慮事項

OpenLDAPサーバ部に関してセキュリティ要件に応じて以下の点を検討することが推奨されます:

- **ネットワークセグメンテーション**: LDAPサーバは内部ネットワークのみに公開し, 外部からの直接接続は避ける
- **TLS/SSL通信**: 本番環境ではTLS/SSL(Secure Sockets Layer, 安全なソケットレイヤ)を有効にしたLDAPS(LDAP over SSL, SSL/TLS経由のLDAP)通信を推奨
- **認証情報の管理**: bind DNやパスワードは環境変数や秘密管理ツールで管理し, Readmeや設定ファイルにハードコードしない

### スケーリングに関する補足事項

複数ホストへの展開や高可用性実現時の検討項目は以下の通り:

- **レプリケーション**: OpenLDAPマスター/スレーブ構成でレプリケーション実装が可能です。詳細はOpenLDAP公式ドキュメントを参照してください
- **ロードバランシング**: 複数のLDAPサーバを配置し, ロードバランサー経由でアクセス可能にすることで, 耐障害性を向上できます
- **ホット/コールドスタンバイ**: 予備マシンを待機させ, 障害時切り替えを実現する構成が可能です

### バージョン管理

OpenLDAPコンテナイメージは osixia/openldap GitHub リポジトリで複数バージョンが公開されています。本ロール実装時のイメージバージョンは以下から確認可能です。

- `roles/ldap-server/defaults/main.yml` の `ldap_image_version` 変数
- `roles/ldap-server/templates/docker-compose.yml.j2` のimage定義

### 運用推奨事項

以下の運用が推奨されます。

- **定期的なバックアップ**: 少なくとも月1回程度の頻度でバックアップスクリプトを実行し, ディレクトリエントリの保護を確保する
- **ログ監視**: Docker コンテナのログを定期的に確認し, エラーやトラブルシューティング情報を収集する
- **セキュリティアップデート**: osixia/openldap イメージの新バージョンリリース情報を追跡し, セキュリティアップデートが公開された際は迅速に適用する
- **ディレクトリ設計**: LDAPディレクトリツリー構造の設計段階で, エントリの検索性能やメンテナンス性を考慮する

## 参考リンク

OpenLDAP サーバとphpLDAPadminの運用管理に関する公開リソースを以下に記載します:

- **OpenLDAP Official Documentation**: https://www.openldap.org/doc/
  - OpenLDAPの公式ドキュメント, 設定リファレンス, トラブルシューティング等を提供

- **osixia/openldap GitHub Repository**: https://github.com/osixia/docker-openldap
  - 本ロールで使用しているopenldapのDockerイメージのソースコード, 設定例, 既知の問題等を提供

- **osixia/phpldapadmin GitHub Repository**: https://github.com/osixia/docker-phpldapadmin
  - phpLDAPadminのDockerイメージのソースコード, 使用方法, トラブルシューティング情報を提供
