# VMの自動設定isoファイル生成

- [VMの自動設定isoファイル生成](#vmの自動設定isoファイル生成)
  - [ファイル構成](#ファイル構成)
  - [使用手順](#使用手順)
    - [ESXi環境の場合](#esxi環境の場合)
      - [Ubuntuの自動インストール](#ubuntuの自動インストール)
      - [RHELの自動インストール](#rhelの自動インストール)
    - [設定内容](#設定内容)
    - [インストール後の処理](#インストール後の処理)
      - [RHEL環境でのupdate-hostname.shの動作について](#rhel環境でのupdate-hostnameshの動作について)
      - [RHELインストール時のKickstartのログについて](#rhelインストール時のkickstartのログについて)
      - [update-hostname.shの実行例](#update-hostnameshの実行例)
      - [`/etc/hosts`の`127.0.1.1`のエントリについて](#etchostsの127011のエントリについて)
      - [インストール後の処理をhostnamectlコマンドで実施する場合](#インストール後の処理をhostnamectlコマンドで実施する場合)

## ファイル構成

以下のファイルが含まれる。

.
|-- Makefile   ISOイメージ作成用Makefile
|-- Readme.md  本文書
|-- scripts
|   |-- rhel
|   |   `-- mk-rhel-image.sh RHELのISOイメージ作成スクリプト
|   `-- ubuntu
|       `-- update-hostname.sh Ubuntu VM上に展開されるホスト名更新スクリプト
`-- tmpl
    |-- rhel
    |   `-- ks.cfg.tmpl RHELインストール時に使用するKickstartの設定ファイルのテンプレート
    `-- ubuntu
        |-- meta-data.tmpl Ubuntuインストール時に使用するcloud-initのmeta-dataファイルのテンプレート
        `-- user-data.tmpl Ubuntuインストール時に使用するcloud-initのuser-dataファイルのテンプレート

Makefile中の変数を変更することで, カスタマイズが可能。
詳細は, Makefile内のコメントを参照。

## 使用手順

Ubuntuの場合は, `make` (または, `make generate`を実行すると) `seed.iso`ファイルができるので, これをVMの2nd CD-ROMイメージとしてマウントする.

RHELの起動イメージの作成は, イメージ作成スクリプト中で, Dockerコマンドを使用するため, 事前にdockerコマンドを導入しておく必要がある。
Dockerコマンドのインストール手順は, [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/) などを参照 。

RHELの場合は, `make build-rhel-image`を実行すると, RHELのイメージファイルが作成される.
これをVMの起動CD-ROMイメージとしてマウントする.
本稿執筆時は, AlmaLinux-9.6-x86_64-minimal.isoを元にAlmaLinux-9.6-x86_64-minimal-ks.isoが作成される。カスタマイズする場合は, Makefile内の変数を修正する。

### ESXi環境の場合

#### Ubuntuの自動インストール

1. Datastore ISO fileにUbuntuのISOイメージと`seed.iso`を登録
2. 「Edit Settings」->「CD/DVD Drive 1」に UbuntuのISOイメージ, 「CD/DVD Drive 2」に `seed.iso`を指定
3. 両方 `起動時にConnect(起動時に接続)`にチェックを入れ, `Connect(接続)` を無効化(チェックを外す)してOKを押下
4. VMをPower Onする

#### RHELの自動インストール

1. Datastore ISO fileに生成されたRHELのイメージファイルを登録
2. 「Edit Settings」->「CD/DVD Drive 1」に生成されたRHELのイメージファイルを指定
3. `起動時にConnect(起動時に接続)`にチェックを入れ, `Connect(接続)` を無効化(チェックを外す)してOKを押下
4. VMをPower Onする

### 設定内容

以下の内容で自動インストールを行う。

インストール後は, ansibleユーザでコンソールおよびssh経由でログイン可能となる。
sudoグループに所属するユーザは, パスワード無しでsudoコマンドを実行可能となるように
設定される。
sshサーバは, パスワードログインを禁止した状態に設定される。

- ホスト名:
  - Ubuntuの場合: ubuntu-vm
  - RHELの場合: rhel-vm
- ロケール: ja_JP.UTF-8
- キーボードレイアウト: us
- 全ローカルディスク領域を使用(direct)
- タイムゾーン: Asia/Tokyo (RTCはUTCに設定)
- ユーザ:
  - ユーザ名: ansible
    - プライマリグループ: ansible
    - 所属グループ:
      - Ubuntuの場合: adm, cdrom, sudo, dip, plugdev, lxd, systemd-journal, ansible
      - RHELの場合: wheel
    - 初期パスワード: ansible
    - ログイン用ssh公開鍵: GitHubからインポート(デフォルトはユーザ名:sampleuser)
- 追加パッケージ: avahi daemonによるMulticast DNS (mDNS), open-vm-toolsによるVMWare連携機能が導入される。また, githubからの公開鍵取得のためcurlが導入される。
  - Ubuntuの場合:
    - avahi-daemon
    - avahi-utils
    - open-vm-tools
    - curl
  - RHELの場合:
    - avahi
    - open-vm-tools
    - curl

### インストール後の処理

以下のようにansibleユーザでログインし, ホスト名を, `sudo hostnamectl set-hostname ホスト名`によって変更する。

Ubuntuの場合:

```:shell
ssh ansible@ubuntu-vm.local
```

RHELの場合:

```:shell
ssh ansible@rhel-vm.local
```

ansibleユーザのホームディレクトリに, `update-hostname.sh`が作成される。

```:shell
ansible@ubuntu-vm:~$ ls -l
total 4
-rwxr-xr-x 1 ansible ansible 1609 10月  7 23:00 update-hostname.sh
```

本スクリプトを以下のように実行することで, ホスト名を更新することができる。

```:shell
sudo ./update-hostname.sh new-hostname
```

これにより, ホスト名を変更し, `/etc/hosts`の`127.0.1.1`のエントリを修正のうえ,
ホスト名が変更されていることを確認するまでの処理を行うことができる。

上記実行後, `ansible@new-hostname.local`を指定して, ssh経由でログインすることが可能となる。

#### RHEL環境でのupdate-hostname.shの動作について


kickstart動作不良時への対策として, 以下のパッケージが導入されていない場合は,
本スクリプト内からの導入を試み, `avahi-daemon`, `vmtoolsd.service` ( open-vm-tools )サービスを有効化の上, `avahi-daemon`サービスを起動する。

- avahi
- open-vm-tools

#### RHELインストール時のKickstartのログについて

RHEL自動インストールに使用するKickstartの動作はおおよそ以下の順で実行される。
本スクリプトでは, %post --nochroot, %post工程のログとシェルの実行トレースを記録している。

1. ブート・カーネル起動 ( カーネル引数や ks= で Kickstart 読み込み )
2. %pre ( あれば ) ：ディスクやミラー選択を前処理で動的に決めたいとき
3. インストール元の決定 ( cdrom / url / nfs など )
4. ストレージ設定 ( zerombr, clearpart, autopart など )
5. パッケージ選択・展開 ( %packages )
6. %post 系：記述順に実行
  6.1. **%post --nochroot** ( インストーラ環境, ターゲットは /mnt/sysimage )
  6.2. **%post** ( chroot 済み, ターゲットを / として実行 )
7. ブートローダ設定・仕上げから再起動 ( reboot )

RHELインストール時のログは, /rootディレクトリ以下のファイルに記録される。

|ファイル名|内容|
|---|---|
|anaconda-ks.cfg|anacondaインストーラのログ, pykickstartが生成したks.cfgの内容が入っている|
|original-ks.cfg|ISOイメージ内に埋め込まれたks.cfgの内容が入っている|
|ks-post.nochroot.log|`%post --nochroot`工程 ( インストール先にchrootする前に実行した内容 ) のログが入っている|
|ks-post.nochroot.trace|`%post --nochroot`工程 ( インストール先にchrootする前に実行した内容 ) のシェルのトレースログが入っている|
|ks-post.log|`%post`工程 ( インストール先にchrootした後に, 実行した実行した内容 ) のログが入っている|
|ks-post.trace|`%post`工程 ( インストール先にchrootした後に, 実行した内容 ) のシェルのトレースログが入っている|

#### update-hostname.shの実行例

`update-hostname.sh`の実行例を以下に示す。

```:shell
ansible@ubuntu-vm:~$ sudo ./update-hostname.sh vmlinux1
Changing hostname: ubuntu-vm to vmlinux1
Restarting avahi-daemon...
=== Hostname ===
 Static hostname: vmlinux1
       Icon name: computer-vm
         Chassis: vm 🖴

=== IP Addresses (global) ===
IPv4: 192.168.20.114/24 dev scope
IPv6: fd69:6684:61a:1:20c:29ff:fe01:ef16/64 dev noprefixroute

=== mDNS resolution via Avahi ===
vmlinux1.local  192.168.20.114
vmlinux1.local  fd69:6684:61a:1:20c:29ff:fe01:ef16

Done. Try:  ssh ansible@vmlinux1.local
```

上記の表示後, 別のマシンから`ansible`ユーザでssh経由でのログインを行う例を以下に示す。

```:shell
$ ssh ansible@vmlinux1.local
Warning: Permanently added 'vmlinux1.local' (ED25519) to the list of known hosts.
Welcome to Ubuntu 24.04.3 LTS (GNU/Linux 6.8.0-85-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of 2025年 10月  7日 火曜日 23:19:19 JST
略
ansible@vmlinux1:~$
```

#### `/etc/hosts`の`127.0.1.1`のエントリについて

Debian/Ubuntu では, 恒久的なIPを持たないマシンでも myhost を常に自分自身に解決させるため, インストーラが`/etc/hosts`に以下のような`127.0.1.1`のエントリを追加する。

```:text
127.0.1.1  myhost
```

Debian/Ubuntu では,恒久的なIPを持たないマシンでも自ホストを常に自分自身に解決させるため, 本エントリを追加する。 固定IPが無いワークステーションを想定したエントリである。以下の通り, 本エントリは, `127.0.0.1` (localhost)と異なる目的, アドレスを持ったエントリである。

- 127.0.0.1 はlocalhost ( ループバックの標準アドレス )
- 127.0.1.1 は, Debian/Ubuntu 系の慣例で, 自ホスト名 ( myhost など ) を“ローカルで必ず解決できるように”ループバックに割り当てるためのエントリ

`update-hostname.sh`は, `127.0.1.1`のエントリが, `/etc/hosts`内にある場合, 対象のエントリのホスト名を, 第1引数で指定されたホスト名に置換する。Domain Name Server (DNS)が存在する環境の場合は, 使用されないエントリではあるが, Debian/Ubuntu 系の慣例に従って, 本処理を行っている。

詳細は, [Chapter 5. Network setup](https://www.debian.org/doc/manuals/debian-reference/ch05.en.html)参照。

#### インストール後の処理をhostnamectlコマンドで実施する場合

インストール後の処理をhostnamectlコマンドで実施する場合,
以下のコマンドを入力する。
`update-hostname.sh`では, Ubuntuの慣習に従って,
`/etc/hosts`の`127.0.1.1`のエントリがある場合, ホスト名を書き換えるが,
以下の手順では省略している。

```:shell
sudo hostnamectl set-hostname new-hostname
sudo systemctl restart avahi-daemon
hostname
avahi-resolve-host-name `hostname`.local
ip addr
```

ログイン後のホスト名設定処理例(以下では, `vmlinux1`に設定)は以下の通り.

```:shell
$ sudo hostnamectl set-hostname vmlinux1
$ sudo systemctl restart avahi-daemon
$ hostname
vmlinux1
$ avahi-resolve-host-name vmlinux1.local
vmlinux1.local  192.168.20.113
$ ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host noprefixroute
       valid_lft forever preferred_lft forever
2: ens160: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000    link/ether 00:50:56:01:ef:16 brd ff:ff:ff:ff:ff:ff
    altname enp3s0
    inet 192.168.20.113/24 metric 100 brd 192.168.20.255 scope global dynamic ens160
       valid_lft 258915sec preferred_lft 258915sec
    inet6 fe80::20c:29ff:fe01:ef16/64 scope link
       valid_lft forever preferred_lft forever
$ sudo reboot
```
