# AnsibleによるDebian (Ubuntu) / RHEL (Alma Linux)環境構築

- [AnsibleによるDebian (Ubuntu) / RHEL (Alma Linux)環境構築](#ansibleによるdebian-ubuntu--rhel-alma-linux環境構築)
  - [ディレクトリ構成](#ディレクトリ構成)
  - [設定方法](#設定方法)
    - [広域設定ファイル (vars/all-config.yml) の設定値](#広域設定ファイル-varsall-configyml-の設定値)
      - [広域設定ファイル基本設定](#広域設定ファイル基本設定)
      - [users\_list定義](#users_list定義)
      - [ネットワーク設定](#ネットワーク設定)
      - [クライアントのDomain Name Server関連設定](#クライアントのdomain-name-server関連設定)
      - [multicast Domain Name Server (mDNS)関連設定](#multicast-domain-name-server-mdns関連設定)
      - [NTPクライアントの設定](#ntpクライアントの設定)
      - [DNSサーバの設定](#dnsサーバの設定)
      - [NFSサーバの設定](#nfsサーバの設定)
      - [プロキシ設定](#プロキシ設定)
      - [Rancher 関連設定](#rancher-関連設定)
      - [Docker Community Edition関連設定](#docker-community-edition関連設定)
        - [コンテナイメージのバックアップ設定](#コンテナイメージのバックアップ設定)
      - [ホームディレクトリのバックアップ](#ホームディレクトリのバックアップ)
      - [Lightweight Directory Access Protocol (LDAP) サーバ関連設定](#lightweight-directory-access-protocol-ldap-サーバ関連設定)
      - [Redmine関連設定](#redmine関連設定)
      - [Emacsパッケージ関連設定](#emacsパッケージ関連設定)
      - [Kubernetes関連設定](#kubernetes関連設定)
        - [Cilum CNI](#cilum-cni)
        - [Multus メタCNI](#multus-メタcni)
        - [Whereabouts CNI](#whereabouts-cni)
    - [Netgauge](#netgauge)
    - [host\_vars/ ディレクトリ配下のホスト設定ファイル](#host_vars-ディレクトリ配下のホスト設定ファイル)
      - [ホスト設定ファイル中でのネットワークインターフェース設定](#ホスト設定ファイル中でのネットワークインターフェース設定)
  - [参考サイト](#参考サイト)

## ディレクトリ構成

```:text
.
|-- Makefile      playbook実行, アーカイブ作成用Makefile
|-- Readme.md     本文書
|-- ansible.cfg   playbook実行時の設定
|-- basic.yml     基本サーバ実施ロール定義
|-- devel.yml     開発サーバ実施ロール定義
|-- group_vars    グループ固有の変数
|-- host_vars     ホスト固有の変数定義
|-- inventory/hosts    サーバ種別単位とホスト名の対応関係定義
|-- k8s-ctrl-plane.yml Kubernetes コントロールプレイン実施ロール定義
|-- k8s-worker.yml     Kubernetes ワーカーノード実施ロール定義
|-- kitting            VMイメージ作成関連スクリプト格納ディレクトリ
|-- rancher.yml        Rancherノード実施ロール定義
|-- roles              各種ロール定義
|-- server.yml         管理サーバノード実施ロール定義
|-- site.yml           メインサイト定義
`-- vars               設定関連変数定義
```

## 設定方法

本playbookでは, 以下のファイルに設定項目を記載する。

1. vars/all-config.yml  広域設定ファイル
2. host_vars/ ディレクトリ配下のホスト設定ファイル
3. vars/packages-rhel.yml RedHat系(AlmaLinuxを想定)パッケージ名定義ファイル
4. vars/packages-ubuntu.yml Debian系(Ubuntuを想定)パッケージ名定義ファイル

本稿では, 上記の内, 1., 2.について述べる。

### 広域設定ファイル (vars/all-config.yml) の設定値

本節では, 広域設定ファイル (vars/all-config.yml) の設定項目について述べる。
広域設定ファイルは, 各ロールのdefaults/main.ymlに記載されているデフォルト値の定義に使用される設定値やそれらのファイル中に記載されているデフォルト値を上書きするための設定値を記載する。

各ロールのdefaults/main.ymlに記載されているデフォルトの設定値を修正する場合は,
**defaults/main.ymlの設定値を変更せず**, vars/all-config.ymlに設定を転記の上,
設定値をvars/all-config.yml側で更新することを推奨する。

#### 広域設定ファイル基本設定

|変数名|意味|設定値の例|
|---|---|---|
|use_vmware|VMWare環境上のゲストOSを設定する場合はtureを指定|true|
|force_reboot|設定作業完了後にリブートする場合はtrueを指定|false|
|common_timezone|タイムゾーンの名前|"Asia/Tokyo"|
|common_disable_cron_mails|CRONジョブ完了後のメール送信を抑止する|true|
|common_selinux_state|SE Linuxの動作モード('enforcing', 'permissive', 'disabled' のいずれかを指定)|"permissive"|
|enable_firewall|Firewall (firewalld/ufw) を使用する場合はtrueを指定|false|
|users_list|作成するユーザのリスト|users_list定義参照|
|sudo_nopasswd_users|パスワード入力なしに, sudoコマンドを実行可能なユーザのリストを指定する|['user1']|
|sudo_nopasswd_groups_extra|パスワード入力なしに, sudoコマンドを実行可能なユーザグループのリストを指定する| ['adm', 'cdrom', 'sudo', 'dip', 'plugdev', 'lxd', 'systemd-journal']|
|sudo_nopasswd_groups_autodetect|sudoユーザグループを自動検出する場合はtrueを指定|true|
|sudo_nopasswd_absent|sudoのdrop inファイルを削除する場合はtrueを指定|false|

#### users_list定義

users_listには, 以下の要素からなる辞書のリストを記述する.

- name ログイン名を指定する。
- group プライマリグループ名を指定する。
- password ログインパスワードのパスワードハッシュ(/etc/shadow 互換の SHA-512-crypt 方式)を指定する。 "{{ パスワード文字列'\|password_hash('sha512') }}"と記載する。
- update_password パスワード設定タイミングを指定する。通常, 'on\_create'を指定する。
- shell ログインシェルを指定する (/bin/bash など)。
- home ホームディレクトリ名を指定する。
- comment GECOSフィールドに書き込むフルネームやコメントを記載する。
- email 電子メールアドレスを記載する。
- github GitHubのアカウント名を記載する。アカウント名を記載すると, 本項目に記載されたGitHubアカウントから公開鍵を取り込み, 作成したユーザのssh公開鍵として使用する。

記載例は以下の通り。

```:yaml
  - { name: 'user1', group: 'user1', password: "{{ 'user1'|password_hash('sha512') }}", update_password: 'on_create', shell: "/bin/zsh", home: "/home/user1", comment: 'Sample User', email: "user1@example.com", github: 'sampleuser' }
```

#### ネットワーク設定

以下で管理サーバは, NTPサーバ, DNSサーバ, LDAPサーバなどを担うホストを表す。
これらの役割を別のホストに割り当てる場合は, それぞれのサーバごとに個別のアドレスやホスト名を設定する。

|変数名|意味|設定値の例|
|---|---|---|
|router_host|ルータのホスト名を指定する|'router'|
|router_ipv4_address|ルータのIPv4アドレスを指定する|"192.168.20.1"|
|router_ipv6_address|ルータのIPv6アドレスを指定する|"fd69:6684:61a:1::1"|
|devserver_ipv4_address|管理サーバのIPv4アドレスを指定する|"192.168.20.11"|
|devserver_ipv6_address|管理サーバのIPv6アドレスを指定する|"192.168.20.11"|
|network_ipv4_prefix_len|物理サーバ/管理用VMネットワークのIPv4ネットワークプレフィクス長|24|
|network_ipv6_prefix_len|物理サーバ/管理用VMネットワークのIPv6ネットワークプレフィクス長|64|
|network_ipv4_prefix|物理サーバ/管理用VMネットワークのIPv4ネットワークのプレフィクスアドレス|"{{router_ipv4_prefix}}"|
|network_ipv6_prefix|物理サーバ/管理用VMネットワークのIPv6ネットワークのプレフィクスアドレス|"{{router_ipv6_prefix}}"|
|network_ipv6_prefix_extra|物理サーバ/運用系用VMネットワークのIPv6ネットワークのプレフィクス|"fd69:6684:61a:2::"|
|network_ipv4_network_address|物理サーバ/管理用VMネットワークのIPv4ネットワークアドレス|"{{router_ipv4_prefix}}.0"|
|network_ipv6_network_address|物理サーバ/管理用VMネットワークのIPv6ネットワークアドレス|"{{router_ipv6_prefix}}"|
|gateway4|IPv4ゲートウエイアドレス|"{{router_ipv4_address}}"|
|gateway6|IPv6ゲートウエイアドレス|"{{router_ipv6_address}}"|
|mgmt_nic|デフォルトの管理用ネットワークインターフェース名|"ens160"|

#### クライアントのDomain Name Server関連設定

|変数名|意味|設定値の例|
|---|---|---|
|ipv4_name_server1|DNSサーバのIPv4アドレス1|"{{devserver_ipv4_address}}"|
|ipv4_name_server2|DNSサーバのIPv4アドレス2|"{{router_ipv4_address}}"|
|ipv6_name_server1|DNSサーバのIPv6アドレス1|"{{devserver_ipv6_address}}"|
|ipv6_name_server2|DNSサーバのIPv6アドレス2|"2606:4700:4700::1111"|
|dns_search|DNSサーチドメインを;で区切って指定する|"example.com;sub.example.com"|

ipv4_name_server1, ipv4_name_server2の両方を設定した場合は両方設定される。ipv4_name_server1, ipv4_name_server2のいずれか一方のみを設定した場合は, その1つのみ設定される。ipv4_name_server1, ipv4_name_server2のいずれも設定しなかった場合は, DHCPで取得したDNSサーバが設定される。

実装上は, dns_searchには, DNSサーチドメインをセミコロン(;)またはカンマ(,)で区切って指定するほか, リストで指定することも可能だが, 仕様としては, セミコロン(;)で区切るものとする。

注意:systemd-resolvedがLAN内のドメイン名を外部のDNS(フォールバックDNS)に問い合わせに行かないようにするためipv4_name_server1, ipv4_name_server2にはLAN内のDNSサーバを設定する。

dns_host_listに以下の要素からなる辞書のリストを記述することで,
静的IPv4アドレスを持つホストのホスト名とIPv4アドレスをDNSのゾーン情報に記録することが
できる。
ユーザの.ssh/configファイルに`ホスト名.{{dns_domain}}`のホスト情報を追記する。

- name ホスト名 (例:"devserver")
- ipv4_addr IPv4アドレスのプレフィクスを除いた値 (例:192.168.20.11/24の場合, '11')

記載例は以下の通り:

```:yaml
dns_host_list
  - { name: 'devserver', ipv4_addr: '11'}
  - { name: 'nas', ipv4_addr: '31'}
```

#### multicast Domain Name Server (mDNS)関連設定

mdns_host_listに以下の要素からなる辞書のリストを記述することで,
ユーザの.ssh/configファイルに`ホスト名.local`のホスト情報を追記する。

記載例は以下の通り:

```:yaml
mdns_host_list:
  - { name: 'vmlinux1'}
  - { name: 'vmlinux2'}
```

#### NTPクライアントの設定

ntp_servers_listにNTPクライアントから参照するNTPサーバのIPアドレス, または, ホスト名をリスト形式で指定する。

記載例は以下の通り:

```:yaml
ntp_servers_list:
  - "{{devserver_ipv4_address}}"
  - "ntp.nict.jp"
```

#### DNSサーバの設定

以下の項目を設定する。

|変数名|意味|設定値の例|
|---|---|---|
|dns_server|DNSサーバのドメイン名|"devserver.example.com"|
|dns_server_ipv4_address|DNSサーバのIPv4アドレス|"{{devserver_ipv4_address}}"|
|dns_server_ipv6_address|DNSサーバのIPv6アドレス|"{{devserver_ipv6_address}}"|
|dns_domain|DNSドメイン名(末尾のドットを除いて指定)|"example.com"|
|dns_network_ipv4_prefix|IPv4ネットワークプレフィクス(末尾のドットを除いて指定)|"{{ network_ipv4_prefix }}"|
|dns_network|DNSサーバにアクセス可能なホストのIPv4ネットワークアドレス|"{{ network_ipv4_network_address }}"|
|dns_network_ipv4_prefix_len|DNSサーバの所属するネットワークのIPv4アドレスのプレフィクス長|"{{ network_ipv4_prefix_len }}"|
|dns_network_ipv6_prefix|DNSサーバにアクセス可能なホストのIPv6ネットワークアドレス|"{{ network_ipv6_network_address }}"|
|dns_network_ipv6_prefix_len|DNSサーバの所属するネットワークのIPv6アドレスのプレフィクス長|"{{ network_ipv6_prefix_len }}"|
|dns_network_ipv6_prefix_filename|IPv6逆引きゾーンファイル名|"fd69-6684-61a-1"|
|dns_ipv4_reverse|IPv4逆引きゾーンファイル名/ゾーン名|"20.168.192"|
|dns_ipv6_reverse|IPv6逆引きゾーン名|"1.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f"|
|dns_ddns_key_secret|Dynamic DNS updateで使用する。共通鍵(`ddns-confgen -a hmac-sha256 -k ddns-clients`で生成された値を指定)|"Kdi362s+dCkToqo4F+JfwMK6yILQyn1mrqI1xfGqDfk="|
|use_nm_ddns_update_scripts|ip monitorコマンドでIPv6アドレス変更を監視する機能とNetwork Manager dispatcher経由でDynamic DNSでホスト名とIPアドレスをDNSに自動登録する機能を有効にする場合はtrueに設定。|true|

#### NFSサーバの設定

以下の項目を設定する。

|変数名|意味|設定値の例|
|---|---|---|
|nfs_export_directory|NFSで公開するディレクトリ|"/home/nfsshare"|
|nfs_network|NFSのクライアントアドレス(ネットワークアドレスを指定)|"{{ network_ipv4_network_address }}/{{ network_ipv4_prefix_len }}"|
|nfs_options|NFS exportのオプション|"rw,no_root_squash,sync,no_subtree_check,no_wdelay"|
|ntp_allow|NTPサーバにアクセス可能なホストが所属するネットワークのネットワークアドレス|"{{ network_ipv4_network_address }}/{{ network_ipv4_prefix_len }}"|

上記の他に, external_ntp_servers_listに参照する外部NTPサーバをリスト形式で指定する。

```:yaml
external_ntp_servers_list:
  - ntp.nict.jp
  - jp.pool.ntp.org
  - ntp.jst.mfeed.ad.jp
  - ntp.ring.gr.jp
  - time.google.com
  - time.aws.com
  - ats1.e-timing.ne.jp
  - s2csntp.miz.nao.ac.jp
```

#### プロキシ設定

将来対応予定。

|変数名|意味|設定値の例|
|---|---|---|
|no_proxy|プロキシを使用しないサイトを指定|""|
|proxy_server|プロキシサーバ|""|
|proxy_port|プロキシポート|""|
|proxy_user|プロキシユーザ|""|
|proxy_password|プロキシパスワード|""|

#### Rancher 関連設定

以下の項目を設定する。

|変数名|意味|設定値の例|
|---|---|---|
|rancher_host|Rancherのホスト名|"rancher01"|
|rancher_cert_domain_name|Rancherのドメイン名|"example.com"|
|rancher_cert_subject_country|Rancher証明書の国|"JP"|
|rancher_cert_subject_state|Rancher証明書の州|"XXXX"|
|rancher_cert_subject_locality|Rancher証明書の市町村|"YYYY"|
|rancher_cert_subject_org|Rancher証明書の組織名|"example-org"|

#### Docker Community Edition関連設定

docker_ce_usersにdocker利用ユーザをリスト形式で指定する。

記載例

```:yaml
docker_ce_users:
  - user1
```

##### コンテナイメージのバックアップ設定

コンテナイメージをバックアップするスクリプトが`/usr/local/bin/backup-containers`に作成される。

NFSマウントは以下のように行われる。

```:shell
   mount -t nfs {{docker_ce_backup_nfs_server}}:{{docker_ce_backup_nfs_dir}} {{ docker_ce_backup_mount_point }}
```

以下の設定の場合

- docker_ce_backup_nfs_server: "nas.example.com"
- docker_ce_backup_nfs_dir: "/share"
- docker_ce_backup_mount_point: "/mnt"

以下のようにマウントされる:
`mount -t nfs nas.example.com:/share /mnt`

その後, コンテナイメージのバックアップは, マウントポイント配下の
バックアップ配置先ディレクトリ`{{ docker_ce_backup_mount_point }}{{ docker_ce_backup_dir_on_nfs }}`に保存される。

- docker_ce_backup_mount_point: "/mnt"
- docker_ce_backup_dir_on_nfs: "/Linux/containers"

の場合は, /mnt/Linux/containers 配下にバックアップされる

他の設定項目は以下の通り:

|変数名|意味|設定値の例|
|---|---|---|
|docker_ce_backup_rotation|デイリーバックアップの世代数|"5"|
|docker_ce_backup_nfs_server|コンテナイメージのデイリーバックアップ時にマウントするNFSサーバ|"nas.example.com"|
|docker_ce_backup_nfs_dir|マウントする共有ディレクトリ|"/share"|
|docker_ce_backup_mount_point|デイリーバックアップ時のNFSマウントポイント(NFSのマウント/アンマウント時に使用)|"/mnt"|
|docker_ce_backup_dir_on_nfs|デイリーバックアップ時のNFSマウントポイント配下のバックアップ配置先ディレクトリ|"/Linux/containers"|

#### ホームディレクトリのバックアップ

指定したユーザのホームディレクトリをNFSサーバ上にバックアップするためのスクリプトを
`/usr/local/bin/backup-home`として作成する。また, NFSマウントを行うためのスクリプトが,
`/usr/local/sbin/mount-nfs.sh`に作成される。

NFSマウントは以下のように行われる。

```:shell
   mount -t nfs {{user_settings_backup_home_nfs_server}}:{{user_settings_backup_home_nfs_dir}} {{ user_settings_backup_home_mount_point }}
```

以下の設定の場合

- user_settings_backup_home_nfs_server: "nas.example.com"
- user_settings_backup_home_nfs_dir: "/share"
- user_settings_backup_home_mount_point: "/mnt"

以下のようにマウントされる:
`mount -t nfs nas.example.com:/share /mnt`

その後, ホームディレクトリのバックアップは, マウントポイント配下の
以下のバックアップ配置先ディレクトリに保存される。

```:yaml
 {{ user_settings_backup_home_mount_point }}{{ user_settings_backup_dir_on_nfs }}
```

以下の設定の場合, /mnt/Linux/Devel 配下にバックアップされる。

- user_settings_backup_home_mount_point: "/mnt"
- user_settings_backup_dir_on_nfs: "/Linux/Devel"

バックアップファイル名は, home-{{ user_settings_backup_users_list.item }}-ホスト名-世代数.tar.xz となる。例えば,
ユーザ user1, ホスト名 devserver, 世代数 0の場合, `home-user1-devserver-0.tar.xz`というファイル名でバックアップファイルが作られる。

他の設定項目は以下の通り:

|変数名|意味|設定値の例|
|---|---|---|
|user_settings_backup_home_rotation|バックアップ世代数|2|
|user_settings_backup_home_nfs_server|マウントするNFSサーバ|"nas.example.org"|
|user_settings_backup_home_nfs_dir|マウントする共有ディレクトリ|"/share"|
|user_settings_backup_home_mount_point|デイリーバックアップ時のNFSマウントポイント (NFSのマウント/アンマウント時に使用)|"/mnt"|
|user_settings_backup_dir_on_nfs|デイリーバックアップ時のNFSマウントポイント配下のバックアップ配置先ディレクトリ|"/Linux/Devel"|

バックアップ対象ユーザは, `user_settings_backup_users_list`変数にユーザ名をリストとして指定する。

記載例は以下の通り:

```:yaml
user_settings_backup_users_list:
    - user1
```

#### Lightweight Directory Access Protocol (LDAP) サーバ関連設定

以下の項目を設定する。

|変数名|意味|設定値の例|
|---|---|---|
|ldap_organization|LDAPの組織名|"user1-private"|
|ldap_domain|LDAPのドメイン名|"example.org"|
|ldap_admin_password|LDAP管理者のパスワード|"ldap"|
|ldap_admin_port|LDAP管理WEB画面ポート番号|10443|

#### Redmine関連設定

Redmineのデイリーバックアップ関連の設定を記載する。
Redmineのデイリーバックアップについては, `roles/redmine-server/Readme.md`参照。

|変数名|意味|設定値の例|
|---|---|---|
|redmine_backup_rotation|バックアップ世代数|7|
|redmine_backup_nfs_server|マウントするNFSサーバ|"nas.example.com"|
|redmine_backup_nfs_dir|マウントする共有ディレクトリ|"/share"|
|redmine_backup_mount_point|デイリーバックアップ時のNFSマウントポイント(NFSのマウント/アンマウント時に使用)|"/mnt"|
|redmine_backup_dir_on_nfs|NFSマウントポイント配下のRedmineバックアップ配置先ディレクトリ|"/Linux/Redmine"|

#### Emacsパッケージ関連設定

ユーザ作成時に導入されるEmacsパッケージのパッケージ名を`create_user_emacs_package_list`にリスト形式で指定する。

記載例は以下の通り:

```:yaml
create_user_emacs_package_list:
  - docker
  - dockerfile-mode
  - docker-compose-mode
  - tramp-container
  - counsel-tramp
  - rust-mode
  - csharp-mode
  - auctex
  - cmake-mode
  - migemo
  - plantuml-mode
  - yaml-mode
```

#### Kubernetes関連設定

Kubernetes (以下K8sと記す)関連の設定を以下に記載する。

|変数名|意味|設定値の例|
|---|---|---|
|k8s_major_minor|Kubernetes バージョン (先頭にvをつけないことに注意)|"1.31"|
|k8s_pod_ipv4_service_subnet|K8sのIPv4サービスネットワークのCIDR|"10.245.0.0/16"|
|k8s_pod_ipv6_service_subnet|K8sのIPv6サービスネットワークのCIDR|"fdb6:6e92:3cfb:feed::/112"|
|k8s_reserved_system_cpus_default|K8sのシステムCPU予約範囲。未定義時は, システム用CPUを予約しない。|"0-1"|
|k8s_worker_enable_nodeport|NodePortによるサービスネットワーク公開を行う場合は, tureに設定(将来対応)|false|
|k8s_worker_nodeport_range|NodePortの範囲|"30000-32767"|

k8s_operator_github_key_listにk8sの各ノードへログインするために使用する公開鍵を得るためのgithubアカウントのリストをリスト形式で指定する。

記載例は以下の通り:

```:yaml
k8s_operator_github_key_list:
  - { github: 'sampleuser' }
```

その他, Cilum CNI, Multus メタCNI, Whereabouts IPアドレスマネージャの
バージョン, Helmのチャートバージョン, イメージバージョンなどを指定できる。

##### Cilum CNI

Cilum CNI関連の設定を以下に記載する。

|変数名|意味|設定値の例|
|---|---|---|
|k8s_cilium_version|Cilium CNIのバージョン|"1.16.0"|
|k8s_cilium_helm_chart_version|Cilium Helm Chartのバージョン|"{{ k8s_cilium_version }}"|
|k8s_cilium_image_version|Ciliumコンテナイメージのバージョン|"v{{ k8s_cilium_version }}"|

##### Multus メタCNI

Multus メタCNI関連の設定を以下に記載する。

|変数名|意味|設定値の例|
|---|---|---|
|k8s_multus_version|Multus CNIのバージョン|"4.2.2"|
|k8s_multus_helm_chart_version|Multus Helm Chartのバージョン|"1.0.1"|
|k8s_multus_image_version|Multusコンテナイメージのバージョン|"{{ k8s_multus_version }}"|

##### Whereabouts CNI

Whereabouts CNI関連の設定を以下に記載する。

|変数名|意味|設定値の例|
|---|---|---|
|k8s_whereabouts_version|Whereabouts CNIのバージョン|"0.9.2"|
|k8s_whereabouts_helm_chart_version|Whereabouts Helm Chartのバージョン|"{{ k8s_whereabouts_version }}"|
|k8s_whereabouts_image_version|Whereaboutsコンテナイメージのバージョン|"{{ k8s_whereabouts_version }}"|

### Netgauge

ネットワーク性能測定ツールであるNetgauge関連の設定を以下に記載する。

|変数名|意味|設定値の例|
|---|---|---|
|netgauge_version|Netgaugeのバージョン|"2.4.6"|
|netgauge_dir|Netgaugeインストールディレクトリ|"/opt/netgauge"|
|netgauge_configure|Netgauge configureオプション|"--with-mpi=no --prefix={{ netgauge_dir }}"|

### host_vars/ ディレクトリ配下のホスト設定ファイル

host_varsには主にネットワークインターフェースの設定やK8s関連の設定を記載する。

host_varsに記載がないホストについては, dhcpv4によるアドレス割り当て, vars/all-config.ymlに記載されているDNS関連情報に基づいてネットワークの設定が行われる。

K8sノードは, 管理用ネットワークと運用ネットワーク(K8sのPod, サービスを動かすための
ネットワーク)の2つのネットワークに接続されたマルチホーム構成であることを想定している。

|変数名|意味|設定値の例|
|---|---|---|
|mgmt_nic|管理用のネットワークインターフェース名|"ens160"|
|k8s_ctrlplane_host|Kubernetes コントロールプレインのホスト名|"k8sctrlplane01.local"|
|k8s_ctrlplane_endpoint|K8sコントロールプレインのAPI広告エンドポイントアドレス|"fd69:6684:61a:1::41"|
|k8s_kubelet_nic|K8sのkubeletが使用するNICを指定, 未指定時はmgmt_nicが使用される。運用ネットワーク(K8sネットワーク)内でK8s間の通信を閉じるなら, K8sネットワーク側のNICを指定する。|"ens194"|
|k8s_pod_ipv4_network_cidr|K8s IPv4 PodネットワークアドレスのCIDR|"10.244.0.0/16"|
|k8s_pod_ipv6_network_cidr|K8s IPv6 PodネットワークアドレスのCIDR|"fdb6:6e92:3cfb:0100::/56"|
|k8s_cilium_cm_cluster_name|Clium Cluster Meshのクラスタ名|"cluster1"|
|k8s_cilium_cm_cluster_id|Clium Cluster MeshのクラスタID|1|
|k8s_whereabouts_ipv4_range_start|Whereaboutsのセカンダリネットワークのアドレスレンジ開始アドレス(IPv4)。 コントロールプレイン用ホスト設定ファイルで設定する。|"192.168.20.100"|
|k8s_whereabouts_ipv4_range_end|Whereaboutsのセカンダリネットワークのアドレスレンジ終了アドレス(IPv4)。 コントロールプレイン用ホスト設定ファイルで設定する。|"192.168.20.254"|
|k8s_whereabouts_ipv6_range_start|Whereaboutsのセカンダリネットワークのアドレスレンジ開始アドレス(IPv6)。 コントロールプレイン用ホスト設定ファイルで設定する。|"fd69:6684:61a:3::100"|
|k8s_whereabouts_ipv6_range_end|Whereaboutsのセカンダリネットワークのアドレスレンジ終了アドレス(IPv6)。 コントロールプレイン用ホスト設定ファイルで設定する。|"fd69:6684:61a:3::254"|

#### ホスト設定ファイル中でのネットワークインターフェース設定

複数のNICを持ったマシンにおける各NICの設定値をnetif_list変数に設定する。
netif_list変数は, 以下の要素からなる辞書のリストである。

|キー名|設定値|設定値の例|
|---|---|---|
|netif|インターフェース名|"ens194"|
|mac|インターフェースのMAC アドレス(省略可)。インターフェースのMAC アドレスを指定すると, インターフェース名を対象のNICに対して固定するよう設定される。|"00:0c:29:57:36:71"|
|static_ipv4_addr|静的 IPv4 アドレス(省略可)|"192.168.20.41"|
|network_ipv4_prefix_len|IPv4 プレフィックス長(省略可)|24|
|gateway4|IPv4 デフォルトゲートウェイ (省略可)|"192.168.20.1"|
|static_ipv6_addr|静的 IPv6 アドレス (省略可) |"fd69:6684:61a:1::41"|
|network_ipv6_prefix_len|IPv6 プレフィックス長 (省略可)|64|
|gateway6|IPv6 デフォルトゲートウェイ(省略可)|"fd69:6684:61a:1::1"|
|ignore_auto_ipv4_dns|DHCPから自動取得した IPv4 DNS サーバを無視する(true/false) (省略可)|true|
|ignore_auto_ipv6_dns|DHCPから自動取得した IPv6 DNS サーバを無視する(true/false) (省略可)|true|
|name_server_ipv4_1|優先 IPv4 DNS サーバ (省略可)|"1.1.1.1"|
|name_server_ipv4_2|セカンダリ IPv4 DNS サーバ (省略可)|"8.8.8.8"|
|name_server_ipv6_1|優先 IPv6 DNS サーバ (省略可)|"2606:4700:4700::1111"|
|name_server_ipv6_2|セカンダリ IPv6 DNS サーバ (省略可)|"2001:4860:4860::8888"|
|dns_search|DNS サーチドメイン ( セミコロン区切りの文字列 )(省略可)|"example.com;sub.example.com"|
|route_metric_ipv4|IPv4の経路メトリック|300|
|route_metric_ipv6|IPv6の経路メトリック|300|

- 静的 IP アドレスが設定されていないインターフェースは DHCP で取得する
- DNS サーバが指定されていない場合は自動取得した DNS サーバを使用する
- DNS サーチドメインが指定されていない場合は自動取得したサーチドメインを使用する
- グローバル変数 ipv4_name_server1, ipv4_name_server2, ipv6_name_server1, ipv6_name_server2 が
  定義されている場合は、各インターフェースの DNS サーバ指定がない場合に使用する
- DNSサーバ項目の出力有無については, 以下のロジックで決定する。
   1. 各インターフェースの ignore_auto_ipv4_dns, ignore_auto_ipv6_dns フラグを確認する
   2. フラグが true の場合は、name_server_ipv4_1, name_server_ipv4_2,
      name_server_ipv6_1, name_server_ipv6_2 の値を確認し、設定されていれば
      それらをDNSサーバのリストに追加する
   3. DNSサーバのリストを事前に算出し, ネームサーバの項目出力要否を判断の上, DNSサーバの設定を出力する。IPv4DNSサーバが一切設定されていない場合, ignore_auto_ipv4_dnsの設定に関わらず, dhcpから取得したDNSサーバの使用を受け入れるよう設定する。同様に, IPv4DNSサーバが一切設定されていない場合, ignore_auto_ipv6_dnsの設定に関わらず, ルータ広告やdhcpv6から取得したDNSサーバの使用を受け入れるよう設定する。
- DNS サーチドメインの決定ロジック
  netif_listのdns_searchを優先し, 無ければvars/all-config.ymlで設定された
  dns_search変数の値を採用する。どちらも無ければ設定しない。

ルートメトリックについては, ネットワークの設計方針に応じて適切に設定する。
例えば, 運用系ネットワークを通して外部ネットワークにつなぐ場合は, 運用系NIC以外のNICのメトリックを高めに設定する。

## 参考サイト

- [【Ansible】メンテナンスしやすいPlaybookの書き方](https://densan-hoshigumi.com/server/playbook-maintainability)
- [Ansible 変数の優先順位と書き方をまとめてみた](https://qiita.com/answer_d/items/b8a87aff8762527fb319)
- [[Ansible] service モジュールの基本的な使い方 ( サービスの起動・停止・
  自動起動の有効化など）](https://tekunabe.hatenablog.jp/entry/2019/02/24/ansible_service_intro)
- [【Ansible】with_itemsループまとめ](https://qiita.com/Tocyuki/items/3efdf4cfcfd9bea056d9)
- [Jinja2: Check If Variable ? Empty | Exists | Defined | True](https://www.shellhacks.com/jinja2-check-if-variable-empty-exists-defined-true/)
jinja2で変数定義の有無の確認と中身が空で無いことの確認方法
- [Ansible UNIX タイムスタンプを任意の日付時刻フォーマットに変換する strftime](https://tekunabe.hatenablog.jp/entry/2021/01/11/ansible_ts_datetime)
テンプレート中での時刻取得 ( roles/common/templates/_bshrc.proxy.j2 な
どの記述の参考にした )
