# Docker composeを使用したOpenLDAPサーバ

osixia/openldapを使用してOpenLDAPサーバを構築します。

以下の処理を実施します:

- `/data/openldap` 配下に設定, データベース, スクリプト用ディレクトリを作成
- IPv4/IPv6 フォワーディングを有効化し, 管理インターフェースで RA (Router Advertisement, ルータ広告) を受け入れる sysctl 設定を配置
- `docker-compose.yml` をテンプレートから生成し, OpenLDAP 本体と phpLDAPadmin (PHP: Hypertext Preprocessor ベースのLDAP管理ツール) のコンテナを `docker compose up -d` で起動
- `backup-ldap-data.sh` / `restore-ldap-data.sh` を `/data/openldap/scripts/` に展開してバックアップ運用を支援

## 変数一覧

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `ldap_organization` | `tkato-home` | LDAP (Lightweight Directory Access Protocol, 軽量ディレクトリアクセスプロトコル) の組織名。OpenLDAP コンテナの `LDAP_ORGANISATION` 環境変数として設定されます。|
| `ldap_domain` | `elliptic-curve.net` | LDAP のドメイン名。OpenLDAP コンテナの `LDAP_DOMAIN` 環境変数として設定され, DC (Domain Component, ドメイン構成要素) の構成に使用されます。|
| `ldap_admin_password` | `ldap` | LDAP 管理者 (`cn=admin`) のパスワード。OpenLDAP コンテナの `LDAP_ADMIN_PASSWORD` 環境変数として設定されます。|
| `ldap_admin_port` | `10443` | phpLDAPadmin Web UI (User Interface, ユーザインターフェース) の HTTPS (Hypertext Transfer Protocol Secure) 公開ポート番号。|
| `openldap_server_user` | `911` | OpenLDAP コンテナ内で使用するユーザ ID (Identifier, 識別子)。osixia/openldap イメージの openldap ユーザに対応します。|
| `openldap_server_grp` | `911` | OpenLDAP コンテナ内で使用するグループ ID。osixia/openldap イメージの openldap グループに対応します。|
| `openldap_docker_dir` | `/data/openldap/docker` | Docker Compose 定義ファイルの配置先ディレクトリ。|
| `openldap_scripts_dir` | `/data/openldap/scripts` | バックアップ / リストア用スクリプトの配置先ディレクトリ。|
| `openldap_database_dir` | `/data/openldap/slapd/database` | LDAP データベースの永続化ディレクトリ。Docker ボリュームとしてマウントされます。|
| `openldap_config_dir` | `/data/openldap/slapd/config` | LDAP 設定ファイルの永続化ディレクトリ。Docker ボリュームとしてマウントされます。|
| `openldap_service_port` | `389` | OpenLDAP サービスポート番号。|
| `openldap_wait_host_stopped` | `"127.0.0.1"` | OpenLDAPサービス停止を待ち合わせる(接続先)ホスト名/IPアドレス。|
| `openldap_wait_host_started` | `"{{ inventory_hostname }}"` | OpenLDAPサービス開始を待ち合わせる(接続先)ホスト名/IPアドレス。|
| `openldap_wait_timeout` | `600` | OpenLDAPサービス待ち合わせ時間(単位: 秒)。|
| `openldap_wait_delay` | `5` | OpenLDAPサービス待ち合わせる際の開始遅延時間(単位: 秒)。|
| `openldap_wait_sleep` | `2` | OpenLDAPサービス待ち合わせる際の待機間隔(単位: 秒)。|
| `openldap_wait_delegate_to` | `"localhost"` | OpenLDAPサービス待ち合わせる際の接続元ホスト名/IPアドレス。|
| `mgmt_nic` | (環境依存) | 管理用ネットワークインターフェース名。sysctl 設定で RA (Router Advertisement, ルータ広告) 受信を有効化する際に使用します。|

必要に応じて `group_vars` / `host_vars` で上記変数を上書きし, ロールの挙動を調整します。

## テンプレート/出力ファイル

| テンプレート名 | 出力先ファイル (既定値) | 説明 |
| --- | --- | --- |
| `docker-compose.yml.j2` | `/data/openldap/docker/docker-compose.yml` | OpenLDAP 本体と phpLDAPadmin の Docker Compose 定義ファイル。コンテナの環境変数, ポートマッピング, ボリューム設定を含みます。|
| `backup-ldap-data.sh.j2` | `/data/openldap/scripts/backup-ldap-data.sh` | LDAP の設定とデータベースを tar アーカイブとしてバックアップするスクリプト。busybox コンテナを使用してボリュームをアーカイブ化します。|
| `restore-ldap-data.sh.j2` | `/data/openldap/scripts/restore-ldap-data.sh` | バックアップアーカイブから LDAP の設定とデータベースをリストアするスクリプト。busybox コンテナを使用してアーカイブを展開します。|
| `90-ldap-forwarding.conf.j2` | `/etc/sysctl.d/90-ldap-forwarding.conf` | IPv4/IPv6 フォワーディングと RA 受信を有効化する sysctl 設定ファイル。Docker ネットワークの正常動作に必要です。|

## phpLDAPadminでのログイン

インストール先ホストに WEB (World Wide Web) ブラウザから以下のようにアクセスする
ポート番号は, `group_vars/all.yml`に記載されている`ldap_admin_port`の値(デフォルトは, `10443`)を指定する。

```
https://ホスト名:10443/
```

ログイン時は, CN (Common Name, 共通名) に`admin`を指定, ドメイン名を元に DC (Domain Component, ドメイン構成要素) を指定する。

'.' で区切られたドメイン名の各要素をdc=要素名,dc=要素名として並べてDC (Domain Component, ドメイン構成要素) を指定する。

ドメイン名がexample.orgの場合, 以下を`login`名に入力する
```
cn=admin,dc=example,dc=net
```

パスワードは, `group_vars/all.yml`に記載されている`ldap_admin_password`の値(デフォルトは, `ldap`)を入力する。

## バックアップ方法

以下のバックアップスクリプトを実行すると, LDAP (Lightweight Directory Access Protocol, 軽量ディレクトリアクセスプロトコル) の設定・データベースをカレントディレクトリにバックアップする。

- config-backup.tar LDAP の設定
- data-backup.tar   LDAP のデータベース
- phpadmin-backup.tar phpldapadminのデータ

事前に,

```
cd /data/openldap/docker
docker-compose pause
```

を実行してコンテナ内のプロセスを停止してから
`/data/openldap/scripts/backup-ldap-data.sh`スクリプトを実行する。
`backup-ldap-data.sh`スクリプトは, 以下の処理を行う。

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

上記が完了したら以下のコマンドを実行して, コンテナを再開する。

```
cd /data/openldap/docker
docker-compose unpause
```

## リストア方法

以下のリストアスクリプトを実行すると, LDAP (Lightweight Directory Access Protocol, 軽量ディレクトリアクセスプロトコル) の設定・データベースをカレントディレクトリのconfig-backup.tar, data-backup.tar, phpadmin-backup.tar からリストアする。

事前に,

```
cd /data/openldap/docker
docker-compose pause
```

を実行してコンテナ内のプロセスを停止してから
`/data/openldap/scripts/restore-ldap-data.sh`スクリプトを実行する。
`restore-ldap-data.sh`スクリプトは, 以下の処理を行う。

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


上記が完了したら以下のコマンドを実行して, コンテナを再開する。

```
cd /data/openldap/docker
docker-compose unpause
```

## 検証ポイント

- `/data/openldap` 以下に設定, データベース, スクリプト用ディレクトリが作成されていること。
- `/etc/sysctl.d/90-ldap-forwarding.conf` が配備され, `sysctl net.ipv4.ip_forward`, `sysctl net.ipv6.conf.all.forwarding` が `1` に設定されていること。
- `docker compose -f /data/openldap/docker/docker-compose.yml ps` で OpenLDAP と phpLDAPadmin コンテナが稼働していること。
- LDAP (Lightweight Directory Access Protocol, 軽量ディレクトリアクセスプロトコル) サービスが 389 番ポートで応答すること。
- phpLDAPadmin の Web UI (User Interface, ユーザインターフェース) が `https://ホスト名:10443/` でアクセス可能なこと。
- バックアップスクリプト実行時に config-backup.tar, data-backup.tar, phpadmin-backup.tar が生成されること。
- リストアスクリプト実行後にバックアップしたディレクトリエントリが復元されていること。
