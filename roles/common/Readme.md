# common ロール

他のすべてのロールの前提となる環境を整えるためのロールです。Ubuntu 24.04, Red Hat Enterprise Linux (RHEL) 9 系 (AlmaLinux9.6を想定)を対象とします。

本playbookで構築されるインフラノード(共通的に使用される機能を提供するための管理ノード, ソフトウエア開発環境を提供する開発ノード, 仮想化環境内部ネットワークと外部ネットワークとを接続するルータノードなど), Kubernetes クラスタを構成するノード (コントロールプレーン, ワーカー) および データセンター(DC)代表 Free Range Routing (FRR, ルーティングソフト) ルータノードを構築するために必要な, 基礎的なシステム設定を行います。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Operating System | OS | 基本ソフトウエア。 |
| Secure Shell | SSH | 暗号化されたリモート接続の仕組み。 |
| Advanced Package Tool | APT | Debian 系のパッケージ管理ツール。 |
| Network Interface Card | NIC | ネットワーク接続のためのインターフェース。 |
| Internet Protocol | IP | 通信で使う規約と識別方式。 |
| Domain Name System | DNS | ドメイン名と IP アドレスを対応付ける仕組み。 |
| Dynamic DNS | DDNS | IP アドレスの変化に合わせて DNS を更新する仕組み。 |
| Multicast DNS | mDNS | 同一ネットワーク内の名前解決方式。 |
| Dynamic Host Configuration Protocol | DHCP | IP アドレスを自動配布する仕組み。 |
| Stateless Address Autoconfiguration | SLAAC | IPv6 の自動設定方式。 |
| Transaction SIGnature | TSIG | DNS 更新時に使う共有鍵署名方式。 |
| Security-Enhanced Linux | SELinux | 強制アクセス制御の仕組み。 |
| Uncomplicated Firewall | UFW | Ubuntu のファイアウォール管理ツール。 |
| Network Time Protocol | NTP | 時刻同期の仕組み。 |
| Container Network Interface | CNI | Kubernetes のネットワークプラグイン仕様。 |
| Yet Another Markup Language | YAML | 設定ファイル形式。 |
| systemd | - | Linux の初期化とサービス管理を行う仕組み。 |
| Media Access Control アドレス | MAC | ネットワーク機器の識別子。 |
| Network Attached Storage | NAS | ネットワーク接続の共有ストレージ。 |
| Cloud-Init | - | 起動時の初期設定を自動化する仕組み。 |
| snap | - | Ubuntu のアプリ配布, 実行基盤。 |
| DNS Service Discovery | DNS-SD | DNS を使ったサービス検出方式。 |
| Universally Unique Identifier | UUID | 一意な識別子。 |
| Intelligent Platform Management Interface | IPMI | 物理機の遠隔管理インターフェース。 |
| Hewlett Packard Enterprise | HPE | 企業向け IT 製品を提供するベンダ名。 |
| Integrated Lights-Out | iLO | HPE の遠隔管理機能。 |
| Xen Cloud Platform next generation | XCP-ng | 仮想化基盤。 |

## 前提条件

- 対象 OS: Ubuntu 22.04/24.04, RHEL 9 系 (Rocky Linux, AlmaLinux 等)
- Ansible 2.15 以降
- `ansible.posix` コレクションがインストールされていること
- リモートホストへの SSH 接続が確立されていること
- 管理者権限 (sudo) が利用可能であること

## 実行フロー

本ロールは以下の順序で処理を実行します:

1. **APT Lock 管理** (Debian 系のみ): `apt-get` による自動更新等がロックを保持している場合, 最大 1800 秒 (既定値) 待機して apt frontend lock を取得します。後続の `apt update` 失敗を防止します。
2. **パラメータ読み込み**: OS 別パッケージ定義 (`vars/packages-ubuntu.yml`, `vars/packages-rhel.yml`) とクラスタ共通変数 (`vars/cross-distro.yml`, `vars/all-config.yml`) を読み込みます。
3. **設定前チェック**: `mgmt_nic` 変数の正規化と検証を行います。未定義時は `common_default_nic` (既定: `ens160`) で補完します。
4. **タイムゾーン設定**: `common_timezone` (既定: `Asia/Tokyo`) を設定します。
5. **ファイアウォール無効化**: `enable_firewall` が `false` (既定) の場合, firewalld (RHEL) または UFW (Debian) を停止, 無効化し, nftables の rpfix テーブルを削除します。
6. **NetworkManager 準備**: NetworkManager をインストール, 有効化し, systemd-networkd を無効化します。
7. **マルチネットワークインターフェース設定**:
   - `netif_list` 変数から複数ネットワークインターフェースの設定を行います。
   - RHEL 系: NetworkManager keyfiles (`/etc/NetworkManager/system-connections/*.nmconnection`) を配置します。
   - Debian 系: netplan 設定 (`/etc/netplan/99-netcfg.yaml`) を配置します。
   - systemd .link ファイル (`/etc/systemd/network/10-*.link`) で MAC アドレス固定化を行います。
   - 不要な旧接続を削除し, 設定適用後に再起動します。
8. **Sudoers 設定**: `sudo_nopasswd_groups_extra` で指定されたグループ (`adm`, `sudo`, `wheel` 等) に対してパスワード無し sudo を設定します (`/etc/sudoers.d/` drop-in files)。
9. **Sysctl 設定**:
   - `kernel.yama.ptrace_scope` = 0 (一般ユーザの ptrace 有効化)
   - `kernel.dmesg_restrict` = 0 (一般ユーザの dmesg 有効化)
   - `fs.inotify.max_user_watches` = 524288 (ファイル監視数上限)
10. **Cron 設定**: `common_disable_cron_mails` が `true` の場合, `/etc/crontab` に `MAILTO=""` を設定してメール送信を無効化します。
11. **パッケージインストール**:
    - Kubernetes 前提パッケージ (`ca-certificates`, `curl`, `apt-transport-https` 等)
    - 共通パッケージ (基本コマンド群: `bash`, `vim`, `emacs`, `tmux`, `kubectl`, `ansible` 等)
    - yq コマンド (YAML processor, GitHub からバイナリを直接取得)
    - 言語パッケージ (`language-pack-ja` 等)
    - mDNS (Avahi) - `mdns_enabled` が `true` の場合
    - VMware tools - `use_vmware` が `true` の場合
    - XCP-NG guest utilities - `use_xcpng` が `true` の場合
12. **ディレクトリ作成**: `/usr/local/sbin`, NAS mount スクリプト用ディレクトリを作成します。
13. **DNS Client スクリプト配置** (オプション): `use_nm_ddns_update_scripts` が `true` の場合, Dynamic DNS update scripts, NetworkManager dispatcher scripts, Router Advertisement address watch service を配置します。
14. **再起動**: `/var/run/reboot-required` が存在する場合に再起動します。

## 主要変数

### 基本設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `reboot_timeout_sec` | `600` | 再起動後の応答待ちタイムアウト時間 (秒)。 |
| `common_timezone` | `"Asia/Tokyo"` | システムタイムゾーン。 |
| `common_selinux_state` | `"permissive"` | SELinux の状態 (`enforcing`, `permissive`, `disabled` のいずれか)。 |
| `enable_firewall` | `false` | ファイアウォール有効化フラグ。`false` の場合は無効化します。 |
| `common_disable_cron_mails` | `false` | cron からのメール送信を無効化する場合は `true` に設定します。 |

### APT Lock 管理 (Debian 系のみ)

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `apt_lock_wait_timeout` | `1800` | apt ロック待機の最大時間 (秒)。 |
| `apt_lock_check_interval` | `5` | apt ロックファイル確認間隔 (秒)。 |
| `apt_lock_files` | (リスト) | 監視対象の apt ロックファイルパス。 |

### ネットワーク設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `common_default_nic` | `"ens160"` | 管理用 NIC のデフォルト名。 |
| `mgmt_nic` | `""` | 管理用 NIC 名。未指定時は `common_default_nic` で補完されます。 |
| `netif_list` | DHCP/SLACCにより管理系 NIC のみを構成するよう設定(`vars/cross-distro.yml`で定義) | ネットワークインターフェース定義のリスト (後述の設定例を参照)。 |
| `gateway4` | `""` | IPv4 デフォルトゲートウェイのフォールバック値。 |
| `gateway6` | `""` | IPv6 デフォルトゲートウェイのフォールバック値。 |
| `ipv4_name_server1` | `""` | IPv4 DNS サーバ 1 のフォールバック値。 |
| `ipv4_name_server2` | `""` | IPv4 DNS サーバ 2 のフォールバック値。 |
| `ipv6_name_server1` | `""` | IPv6 DNS サーバ 1 のフォールバック値。 |
| `ipv6_name_server2` | `""` | IPv6 DNS サーバ 2 のフォールバック値。 |

### Sysctl 設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `common_sysctl_user_ptrace_enable` | `true` | 一般ユーザによる ptrace を有効化するか。 |
| `common_sysctl_user_dmesg_enable` | `true` | 一般ユーザによる dmesg を有効化するか。 |
| `common_sysctl_inotify_max_user_watches` | `524288` | ファイル監視数の上限値。 |

### Sudoers 設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `sudo_nopasswd_groups_extra` | `['adm', 'cdrom', 'sudo', 'dip', 'plugdev', 'lxd', 'systemd-journal']` | パスワード無し sudo を許可するグループのリスト。 |
| `sudo_nopasswd_groups_autodetect` | `true` | `sudo` / `wheel` グループの自動検出を有効化するか。 |
| `sudo_nopasswd_absent` | `false` | `true` に設定すると sudoers drop-in ファイルを削除 (ロールバック) します。 |
| `sudo_dropin_prefix` | `"99-nopasswd"` | 生成する drop-in ファイル名の接頭辞。 |

### 仮想化環境設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `use_vmware` | `false` | VMware 環境で使用する場合は `true` に設定します (`open-vm-tools` をインストール)。 |
| `use_xcpng` | `false` | XCP-NG 環境で使用する場合は `true` に設定します (xe-guest-utilities をインストール)。 |

### multicast DNS/Dynamic DNS 設定 (オプション)

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `mdns_enabled` | `false` | Avahi マルチキャスト DNS サービスを導入する場合は `true` に設定します。 |
| `use_nm_ddns_update_scripts` | `false` | NetworkManager 経由で Dynamic DNS にホスト名と IP アドレスを自動登録する場合は `true` に設定します。 |
| `dns_ddns_key_name` | `"ddns-clients"` | Dynamic DNS update key の名前。 |
| `dns_ddns_key_file` | `"/etc/nsupdate/ddns-clients.key"` | Dynamic DNS update key ファイルのパス。 |
| `ddns_client_update_sh_dest_dir` | `"/usr/local/sbin"` | ddns-client-update.sh の配置先ディレクトリ。 |
| `nm_ra_addr_watch_dest_dir` | `"/usr/local/libexec"` | nm-ra-addr-watch の配置先ディレクトリ。 |
| `nm_ra_addr_watch_interval` | `10` | Router Advertisement アドレス監視間隔 (秒)。 |
| `nm_ns_update_log_level` | `2` | NetworkManager DNS update スクリプトのログレベル (0-5)。 |

## 主な処理

- **APT ロック待機**: Debian 系で apt frontend lock を取得できるまで待機し, 後続タスクの失敗を防止します。
- **ファイアウォール無効化**: firewalld, UFW, nftables の rpfix テーブルを無効化します。Kubernetes の CNI (Container Network Interface) が独自にネットワークポリシーを管理するため, ホストレベルのファイアウォールは無効化します。
- **NetworkManager 優先設定**: systemd-networkd を無効化し, NetworkManager を有効化します。一貫したネットワーク管理インターフェースを提供します。
- **マルチネットワークインターフェース設定**: 複数の NIC に対して静的 IP アドレス, ゲートウェイ, DNS サーバを設定します。RHEL 系では NetworkManager keyfiles, Debian 系では netplan を使用します。
- **MAC アドレス固定化**: systemd .link ファイルで NIC 名と MAC アドレスを紐付け, 再起動後も同じデバイス名を維持します。
- **Sudoers 設定**: `/etc/sudoers.d/` に drop-in ファイルを配置し, 指定グループのユーザがパスワード無しで sudo を実行可能にします。既存の `/etc/sudoers` を変更しないため, 安全に設定を追加, 削除できます。
- **Sysctl 設定**: 一般ユーザによる ptrace / dmesg を有効化し, ファイル監視数の上限を引き上げます。開発環境での利便性向上を目的とします。
- **パッケージインストール**: Kubernetes クラスタ構築に必要なパッケージ群, 基本コマンド, 言語パッケージをインストールします。
- **Dynamic DNS 自動登録** (オプション): NetworkManager の dispatcher 機能を利用し, IP アドレス変更時に自動的に DNS サーバへ nsupdate を送信します。DHCP 環境や IPv6 SLAAC 環境でのホスト名解決を自動化します。

## テンプレート / ファイル

本ロールでは以下のテンプレート / ファイルを出力します:

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `templates/10-netif.link.j2` | `{{ netif_nm_link_dir }}/10-{{ item.netif }}.link` (既定: `/etc/systemd/network/10-<ネットワークインターフェース名>.link`) | systemd .link ファイル。NIC 名と MAC アドレスの紐付けを設定します。 |
| `templates/rhel9-multi-netif.nmconnection.j2` | `/etc/NetworkManager/system-connections/{{ item.netif }}.nmconnection` | NetworkManager keyfile (RHEL 系)。IP アドレス, ゲートウェイ, DNS サーバを設定します。 |
| `templates/99-netcfg-multi.yaml.j2` | `/etc/netplan/99-netcfg.yaml` | netplan 設定ファイル (Debian 系)。IP アドレス, ゲートウェイ, DNS サーバを設定します。 |
| `templates/nopasswd-group.sudoers.j2` | `/etc/sudoers.d/{{ sudo_dropin_prefix }}-group-{{ item }}` (既定: `/etc/sudoers.d/99-nopasswd-group-<グループ名>`) | グループ単位のパスワード無し sudo 設定。 |
| `templates/nopasswd-user.sudoers.j2` | `/etc/sudoers.d/{{ sudo_dropin_prefix }}-user-{{ item }}` (既定: `/etc/sudoers.d/99-nopasswd-user-<ユーザ名>`) | ユーザ単位のパスワード無し sudo 設定。 |
| `templates/mount-nas.sh.j2` | `/usr/local/sbin/mount-nas.sh` | NAS マウント用スクリプト。 |
| `templates/ddns-client-update.sh.j2` | `{{ ddns_client_update_sh_path }}` (既定: `/usr/local/sbin/ddns-client-update.sh`) | Dynamic DNS update スクリプト (`use_nm_ddns_update_scripts` が `true` の場合)。 |
| `templates/ddns-clients-key-file.j2` | `{{ dns_ddns_key_file }}` (既定: `/etc/nsupdate/ddns-clients.key`) | Dynamic DNS update key ファイル (`use_nm_ddns_update_scripts` が `true` の場合)。 |
| `templates/nm-ra-addr-watch.j2` | `{{ nm_ra_addr_watch_path }}` (既定: `/usr/local/libexec/nm-ra-addr-watch`) | Router Advertisement アドレス監視スクリプト (`use_nm_ddns_update_scripts` が `true` の場合)。 |
| `templates/nm-ra-addr-watch.service.j2` | `/etc/systemd/system/nm-ra-addr-watch.service` | nm-ra-addr-watch systemd サービスユニット (`use_nm_ddns_update_scripts` が `true` の場合)。 |
| `templates/90-nm-ns-update.j2` | `{{ nm_ns_update_path }}` (既定: `/etc/NetworkManager/dispatcher.d/90-nm-ns-update`) | NetworkManager dispatcher スクリプト (`use_nm_ddns_update_scripts` が `true` の場合)。IP アドレス変更時に DNS を更新します。 |
| `templates/sysconfig-ddns-update-client.j2` | `{{ ddns_client_update_sh_sysconfig_path }}` (既定: `/etc/default/ddns-client-update` または `/etc/sysconfig/ddns-client-update`) | ddns-client-update.sh 環境ファイル (`use_nm_ddns_update_scripts` が `true` の場合)。 |
| `templates/sysconfig-nm-ns-update.j2` | `{{ nm_ns_update_sysconfig_path }}` (既定: `/etc/default/nm-ns-update` または `/etc/sysconfig/nm-ns-update`) | 90-nm-ns-update 環境ファイル (`use_nm_ddns_update_scripts` が `true` の場合)。 |
| `templates/sysconfig-nm-ra-addr-watch.j2` | `{{ nm_ra_addr_watch_sysconfig_path }}` (既定: `/etc/default/nm-ra-addr-watch` または `/etc/sysconfig/nm-ra-addr-watch`) | nm-ra-addr-watch 環境ファイル (`use_nm_ddns_update_scripts` が `true` の場合)。 |

## OS 差異

本ロールは RHEL 系 (Rocky Linux, AlmaLinux 等) と Debian 系 (Ubuntu) の両方をサポートしますが, 一部の動作に差異があります。

### ネットワーク設定の差異

| 項目 | RHEL 系 | Debian 系 |
| --- | --- | --- |
| ネットワーク管理ツール | NetworkManager | NetworkManager + netplan |
| 設定ファイル形式 | NetworkManager keyfiles (`*.nmconnection`) | netplan YAML (`*.yaml`) |
| 設定ファイル配置先 | `/etc/NetworkManager/system-connections/` | `/etc/netplan/` |
| 設定適用方法 | `nmcli connection reload` + `nmcli connection up` | `netplan apply` |
| 設定ファイルパーミッション | `0600` (root のみ読み書き可) | `0644` (全ユーザ読み取り可) |
| Cloud-Init 無効化 | 必要 (設定無効化と udev ルールのマスク) | 必要 (netplan 自動設定ファイルのリネーム) |

**RHEL 系の特徴**:
- NetworkManager keyfiles を直接配置します (`rhel9-multi-netif.nmconnection.j2`)。
- `nmcli connection load` で構文検証を行い, エラーがあればタスクを停止します。
- Cloud-Init のネットワーク設定とインターフェース名変更を無効化します。
- udev ルールはバックアップ後に空ファイルを配置してマスクし, NetworkManager の動作を保証します。
- 旧形式の ifcfg ファイルを削除します。
- SELinux コンテキストの復元が必要な場合があります (`restorecon`)。

**Debian 系の特徴**:
- netplan 設定ファイルを配置し (`99-netcfg-multi.yaml.j2`), `netplan apply` で反映します。
- netplan が NetworkManager をバックエンドとして使用します (`renderer: NetworkManager`)。
- Cloud-Init の自動ネットワーク設定ファイル (例: `/etc/netplan/50-cloud-init.yaml`) に `.old` 拡張子を付けてリネームし無効化します。

### パッケージマネージャの差異

| 項目 | RHEL 系 | Debian 系 |
| --- | --- | --- |
| パッケージマネージャ | `dnf` | `apt` |
| ロックファイル待機 | 不要 | 必要 (`apt_lock_wait_timeout`) |
| 環境ファイル配置先 | `/etc/sysconfig/` | `/etc/default/` |
| Admin グループ名 | `wheel` | `sudo` |

### ファイアウォールの差異

| 項目 | RHEL 系 | Debian 系 |
| --- | --- | --- |
| ファイアウォールサービス | `firewalld` | `ufw` |
| 無効化コマンド | `systemctl stop/disable/mask firewalld` | `systemctl stop/disable/mask ufw` |

### その他の差異

- **SELinux**: RHEL 系のみ有効, `common_selinux_state` で制御します。
- **言語パッケージ**: Ubuntu は `language-pack-ja`, RHEL は `glibc-langpack-ja` を使用します。
- **systemd .link ファイル配置先**: 両 OS とも `/etc/systemd/network/` を使用します (差異なし)。

## 設定例

### 単一 NIC 構成 (IPv4 のみ)

最もシンプルな構成です。管理用 NIC に静的 IPv4 アドレスを設定します。

```yaml
# host_vars/example-host.local
mgmt_nic: "ens160"

netif_list:
  - netif: "ens160"
    mac: "00:50:56:12:34:56"
    ipv4_addr: "192.168.1.10"
    ipv4_cidr: "24"
    ipv4_gw: "192.168.1.1"
    ipv4_dns1: "192.168.1.1"
    ipv4_dns2: "8.8.8.8"
```

### デュアル NIC 構成 (管理系 + K8s ネットワーク)

管理系ネットワークと Kubernetes ネットワークを分離する構成です。

```yaml
# host_vars/k8sworker0101.local
mgmt_nic: "ens160"

netif_list:
  - netif: "ens160"
    mac: "00:50:56:12:34:56"
    ipv4_addr: "192.168.30.42"
    ipv4_cidr: "24"
    ipv4_gw: "192.168.30.1"
    ipv4_dns1: "192.168.30.1"
    ipv4_dns2: "8.8.8.8"
  - netif: "ens192"
    mac: "00:50:56:12:34:57"
    ipv4_addr: "192.168.40.42"
    ipv4_cidr: "24"
```

**ポイント**:
- `mgmt_nic` で管理系 NIC を明示的に指定します。
- 2 番目の NIC (`ens192`) にはゲートウェイと DNS サーバを設定しません (管理系のみで使用)。

### デュアルスタック構成 (IPv4 + IPv6)

IPv4 と IPv6 の両方を設定する構成です。

```yaml
# host_vars/k8sworker0101.local
mgmt_nic: "ens160"

netif_list:
  - netif: "ens160"
    mac: "00:50:56:12:34:56"
    ipv4_addr: "192.168.30.42"
    ipv4_cidr: "24"
    ipv4_gw: "192.168.30.1"
    ipv4_dns1: "192.168.30.1"
    ipv4_dns2: "8.8.8.8"
    ipv6_addr: "fd69:6684:61a:1::42"
    ipv6_cidr: "64"
    ipv6_gw: "fd69:6684:61a:1::1"
    ipv6_dns1: "fd69:6684:61a:1::1"
    ipv6_dns2: "2001:4860:4860::8888"
  - netif: "ens192"
    mac: "00:50:56:12:34:57"
    ipv4_addr: "192.168.40.42"
    ipv4_cidr: "24"
    ipv6_addr: "fd69:6684:61a:2::42"
    ipv6_cidr: "64"
```

### トリプル NIC 構成 (管理系 + K8s ネットワーク + ストレージ)

管理系, Kubernetes ネットワーク, ストレージネットワークを分離する構成です。

```yaml
# host_vars/k8sworker0101.local
mgmt_nic: "ens160"

netif_list:
  - netif: "ens160"
    mac: "00:50:56:12:34:56"
    ipv4_addr: "192.168.30.42"
    ipv4_cidr: "24"
    ipv4_gw: "192.168.30.1"
    ipv4_dns1: "192.168.30.1"
  - netif: "ens192"
    mac: "00:50:56:12:34:57"
    ipv4_addr: "192.168.40.42"
    ipv4_cidr: "24"
  - netif: "ens224"
    mac: "00:50:56:12:34:58"
    ipv4_addr: "10.0.0.42"
    ipv4_cidr: "24"
```

### Dynamic DNS 自動登録を有効化した構成

NetworkManager 経由で DNS サーバに IP アドレスを自動登録する構成です。

```yaml
# host_vars/k8sworker0101.local
use_nm_ddns_update_scripts: true
dns_ddns_key_name: "ddns-clients"

mgmt_nic: "ens160"

netif_list:
  - netif: "ens160"
    mac: "00:50:56:12:34:56"
    ipv4_addr: "192.168.30.42"
    ipv4_cidr: "24"
    ipv4_gw: "192.168.30.1"
    ipv4_dns1: "192.168.30.1"
    ipv6_addr: "fd69:6684:61a:1::42"
    ipv6_cidr: "64"
    ipv6_gw: "fd69:6684:61a:1::1"
    ipv6_dns1: "fd69:6684:61a:1::1"
```

**必要な追加設定**:
- DNS サーバ側で Dynamic DNS を有効化し, TSIG キーを生成しておく必要があります。
- `templates/ddns-clients-key-file.j2` テンプレート内で TSIG キーの内容を設定します。

## 検証ポイント

本節では, `common` ロール実行後にシステムが正しく設定されているかを確認する手順を示します。

### 前提条件

- `common` ロールが正常に完了していること (`changed` または `ok` の状態)。
- リモートホストへ SSH で接続可能であること。
- sudo 権限が利用可能であること。

### 1. タイムゾーン設定の確認

タイムゾーンが正しく設定されているかを確認します。

```bash
timedatectl
```

**期待される出力例**:

```
               Local time: Sun 2026-02-23 10:30:00 JST
           Universal time: Sun 2026-02-23 01:30:00 UTC
                 RTC time: Sun 2026-02-23 01:30:00
                Time zone: Asia/Tokyo (JST, +0900)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no
```

**確認ポイント**:
- `Time zone` が `Asia/Tokyo` (または `common_timezone` で指定した値) になっていること。

Debian 系では以下のコマンドでも確認できます:

```bash
cat /etc/timezone
```

**期待される出力**:

```
Asia/Tokyo
```

### 2. ファイアウォール無効化の確認

#### RHEL 系

```bash
sudo systemctl status firewalld
```

**期待される出力例**:

```
○ firewalld.service
     Loaded: masked (Reason: Unit firewalld.service is masked.)
     Active: inactive (dead)
```

**確認ポイント**:
- `Loaded: masked` となっていること。
- `Active: inactive (dead)` となっていること。

#### Debian 系

```bash
sudo systemctl status ufw
```

**期待される出力例**:

```
○ ufw.service
     Loaded: masked (Reason: Unit ufw.service is masked.)
     Active: inactive (dead)
```

または:

```bash
sudo ufw status
```

**期待される出力**:

```
Status: inactive
```

#### nftables rpfix テーブルの確認

```bash
sudo nft list tables
```

**期待される状態**:
- `rpfix` テーブルが表示されないこと (削除されているため)。

### 3. ネットワーク設定の確認

#### NetworkManager の状態確認

```bash
sudo systemctl status NetworkManager
```

**期待される出力例**:

```
● NetworkManager.service - Network Manager
     Loaded: loaded (/lib/systemd/system/NetworkManager.service; enabled; vendor preset: enabled)
     Active: active (running) since ...
```

**確認ポイント**:
- `Active: active (running)` となっていること。
- `enabled` となっていること。

#### systemd-networkd の無効化確認

```bash
sudo systemctl status systemd-networkd
```

**期待される出力例**:

```
○ systemd-networkd.service - Network Service
     Loaded: loaded (/lib/systemd/system/systemd-networkd.service; disabled; vendor preset: enabled)
     Active: inactive (dead)
```

**確認ポイント**:
- `disabled` となっていること。
- `Active: inactive (dead)` となっていること。

#### ネットワークインターフェース設定の確認 (RHEL 系)

NetworkManager keyfile が正しく配置されているかを確認します:

```bash
ls -l /etc/NetworkManager/system-connections/
```

**期待される出力例**:

```
-rw------- 1 root root  456 Feb 23 10:00 ens160.nmconnection
-rw------- 1 root root  423 Feb 23 10:00 ens192.nmconnection
```

**確認ポイント**:
- `netif_list` で定義した各 NIC の `.nmconnection` ファイルが存在すること。
- パーミッションが `0600` (root のみ読み書き可) であること。

接続状態を確認します:

```bash
nmcli connection show
```

**期待される出力例**:

```
NAME     UUID                                  TYPE      DEVICE
ens160   a1b2c3d4-e5f6-7890-abcd-ef1234567890  ethernet  ens160
ens192   b2c3d4e5-f678-90ab-cdef-123456789012  ethernet  ens192
```

**確認ポイント**:
- `netif_list` で定義した各 NIC が表示されること。
- `DEVICE` 列に対応する NIC 名が表示されること。

接続の詳細を確認します:

```bash
nmcli connection show ens160
```

**期待される出力に含まれる項目**:
- `ipv4.method: manual`
- `ipv4.addresses: 192.168.30.42/24` (設定した IP アドレス)
- `ipv4.gateway: 192.168.30.1` (設定したゲートウェイ)
- `ipv4.dns: 192.168.30.1,8.8.8.8` (設定した DNS サーバ)

#### ネットワークインターフェース設定の確認 (Debian 系)

netplan 設定ファイルが正しく配置されているかを確認します:

```bash
ls -l /etc/netplan/
```

**期待される出力例**:

```
-rw-r--r-- 1 root root 512 Feb 23 10:00 99-netcfg.yaml
```

netplan 設定の内容を確認します:

```bash
cat /etc/netplan/99-netcfg.yaml
```

**期待される出力例**:

```yaml
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    ens160:
      dhcp4: false
      dhcp6: false
      addresses:
        - 192.168.30.42/24
      gateway4: 192.168.30.1
      nameservers:
        addresses:
          - 192.168.30.1
          - 8.8.8.8
    ens192:
      dhcp4: false
      dhcp6: false
      addresses:
        - 192.168.40.42/24
```

netplan の状態を確認します:

```bash
sudo netplan status
```

または:

```bash
networkctl list
```

#### IP アドレス設定の確認

```bash
ip addr show
```

**期待される出力例** (一部抜粋):

```
2: ens160: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 00:50:56:12:34:56 brd ff:ff:ff:ff:ff:ff
    inet 192.168.30.42/24 brd 192.168.30.255 scope global noprefixroute ens160
       valid_lft forever preferred_lft forever
    inet6 fd69:6684:61a:1::42/64 scope global noprefixroute
       valid_lft forever preferred_lft forever
    inet6 fe80::250:56ff:fe12:3456/64 scope link
       valid_lft forever preferred_lft forever
3: ens192: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 00:50:56:12:34:57 brd ff:ff:ff:ff:ff:ff
    inet 192.168.40.42/24 brd 192.168.40.255 scope global noprefixroute ens192
       valid_lft forever preferred_lft forever
```

**確認ポイント**:
- 各 NIC に設定した IP アドレスが割り当てられていること。
- MAC アドレスが `netif_list` で指定した値と一致していること。
- `state UP` となっていること (インターフェースが有効)。

#### デフォルトルートの確認

```bash
ip route
```

**期待される出力例**:

```
default via 192.168.30.1 dev ens160 proto static metric 100
192.168.30.0/24 dev ens160 proto kernel scope link src 192.168.30.42 metric 100
192.168.40.0/24 dev ens192 proto kernel scope link src 192.168.40.42 metric 101
```

IPv6 の場合:

```bash
ip -6 route
```

**期待される出力例**:

```
fd69:6684:61a:1::/64 dev ens160 proto kernel metric 100 pref medium
fd69:6684:61a:2::/64 dev ens192 proto kernel metric 101 pref medium
default via fd69:6684:61a:1::1 dev ens160 proto static metric 100 pref medium
```

**確認ポイント**:
- デフォルトルートが管理系 NIC (`mgmt_nic`) を経由していること。
- 各ネットワークの経路が正しく設定されていること。

#### DNS 設定の確認

```bash
resolvectl status
```

または:

```bash
cat /etc/resolv.conf
```

**期待される出力例** (`resolvectl` の場合):

```
Global
       Protocols: -LLMNR -mDNS -DNSOverTLS DNSSEC=no/unsupported
resolv.conf mode: stub

Link 2 (ens160)
    Current Scopes: DNS
         Protocols: +DefaultRoute +LLMNR -mDNS -DNSOverTLS DNSSEC=no/unsupported
Current DNS Server: 192.168.30.1
       DNS Servers: 192.168.30.1 8.8.8.8
```

**確認ポイント**:
- `netif_list` で設定した DNS サーバが表示されること。

#### systemd .link ファイルの確認

```bash
ls -l /etc/systemd/network/
```

**期待される出力例**:

```
-rw-r--r-- 1 root root 123 Feb 23 10:00 10-ens160.link
-rw-r--r-- 1 root root 123 Feb 23 10:00 10-ens192.link
```

.link ファイルの内容を確認します:

```bash
cat /etc/systemd/network/10-ens160.link
```

**期待される出力例**:

```
[Match]
MACAddress=00:50:56:12:34:56

[Link]
Name=ens160
```

**確認ポイント**:
- `MACAddress` が `netif_list` で指定した値と一致していること。
- `Name` が NIC 名と一致していること。

### 4. Sudoers 設定の確認

#### Drop-in ファイルの存在確認

```bash
ls -l /etc/sudoers.d/
```

**期待される出力例**:

```
-r--r----- 1 root root 56 Feb 23 10:00 99-nopasswd-group-adm
-r--r----- 1 root root 57 Feb 23 10:00 99-nopasswd-group-sudo
-r--r----- 1 root root 58 Feb 23 10:00 99-nopasswd-group-wheel
```

**確認ポイント**:
- `sudo_nopasswd_groups_extra` および自動検出されたグループ (`sudo`, `wheel`) の drop-in ファイルが存在すること。
- パーミッションが `0440` (root とグループのみ読み取り可) であること。

#### Drop-in ファイルの内容確認

```bash
sudo cat /etc/sudoers.d/99-nopasswd-group-sudo
```

**期待される出力例**:

```
%sudo ALL=(ALL:ALL) NOPASSWD: ALL
```

#### Sudo 権限の動作確認

一般ユーザで以下を実行します:

```bash
sudo -l
```

**期待される出力例**:

```
User youruser may run the following commands on hostname:
    (ALL : ALL) NOPASSWD: ALL
```

**確認ポイント**:
- `NOPASSWD: ALL` が表示されること (パスワード無しで sudo 実行可能)。

パスワードなしで sudo が実行できることを確認します:

```bash
sudo whoami
```

**期待される出力**:

```
root
```

パスワードの入力を求められないことを確認してください。

### 5. Sysctl 設定の確認

#### Ptrace 設定の確認

```bash
sysctl kernel.yama.ptrace_scope
```

**期待される出力**:

```
kernel.yama.ptrace_scope = 0
```

**確認ポイント**:
- 値が `0` であること (一般ユーザによる ptrace が有効)。

#### Dmesg 設定の確認

```bash
sysctl kernel.dmesg_restrict
```

**期待される出力**:

```
kernel.dmesg_restrict = 0
```

**確認ポイント**:
- 値が `0` であること (一般ユーザによる dmesg が有効)。

一般ユーザで dmesg が実行できることを確認します:

```bash
dmesg | head
```

エラーなく出力されることを確認してください。

#### ファイル監視数の確認

```bash
sysctl fs.inotify.max_user_watches
```

**期待される出力**:

```
fs.inotify.max_user_watches = 524288
```

**確認ポイント**:
- 値が `524288` (または `common_sysctl_inotify_max_user_watches` で指定した値) であること。

設定ファイルの確認:

```bash
cat /etc/sysctl.d/90-inotify.conf
```

(または該当する sysctl 設定ファイル)

### 6. パッケージインストールの確認

#### 基本パッケージの確認 (Debian 系)

```bash
dpkg -l | grep -E '(bash|vim|emacs|tmux|kubectl|ansible)'
```

**期待される出力例**:

```
ii  ansible         2.15.8-1~ubuntu22.04.1         all          Configuration management...
ii  bash            5.1-6ubuntu1                   amd64        GNU Bourne Again SHell
ii  emacs           1:27.1+1-3ubuntu5              all          GNU Emacs editor
ii  kubectl         1.29.2-1.1                     amd64        Kubernetes command-line tool
ii  tmux            3.2a-4ubuntu0.2                amd64        terminal multiplexer
ii  vim             2:8.2.3995-1ubuntu2.15         amd64        Vi IMproved - enhanced vi editor
```

#### 基本パッケージの確認 (RHEL 系)

```bash
rpm -qa | grep -E '(bash|vim|emacs|tmux|kubectl|ansible)'
```

#### Kubernetes 前提パッケージの確認

Debian 系:

```bash
dpkg -l | grep -E '(ca-certificates|curl|apt-transport-https)'
```

RHEL 系:

```bash
rpm -qa | grep -E '(ca-certificates|curl)'
```

#### yq コマンドの確認

```bash
which yq
yq --version
```

**期待される出力例**:

```
/usr/local/bin/yq
yq (https://github.com/mikefarah/yq/) version v4.40.5
```

**確認ポイント**:
- `yq` コマンドが `/usr/local/bin/yq` にインストールされていること。
- バージョン情報が表示されること。

#### 言語パッケージの確認 (Debian 系)

```bash
dpkg -l | grep -E 'language-pack-ja'
```

**期待される出力例**:

```
ii  language-pack-ja              1:22.04+20220818  all          translation updates for language Japanese
ii  language-pack-ja-base         1:22.04+20220818  all          translations for language Japanese
```

#### mDNS パッケージの確認 (`mdns_enabled: true` の場合)

```bash
sudo systemctl status avahi-daemon
```

**期待される出力例**:

```
● avahi-daemon.service - Avahi mDNS/DNS-SD Stack
     Loaded: loaded (/lib/systemd/system/avahi-daemon.service; enabled; vendor preset: enabled)
     Active: active (running) since ...
```

#### VMware Tools の確認 (`use_vmware: true` の場合)

```bash
dpkg -l | grep open-vm-tools
```

または:

```bash
rpm -qa | grep open-vm-tools
```

#### XCP-NG Guest Utilities の確認 (`use_xcpng: true` の場合)

```bash
dpkg -l | grep xe-guest-utilities
```

または:

```bash
rpm -qa | grep xe-guest-utilities
```

### 7. Dynamic DNS Client Scripts の確認 (`use_nm_ddns_update_scripts: true` の場合)

#### スクリプトファイルの存在確認

```bash
ls -l /usr/local/sbin/ddns-client-update.sh
ls -l /usr/local/libexec/nm-ra-addr-watch
ls -l /etc/NetworkManager/dispatcher.d/90-nm-ns-update
```

**期待される出力例**:

```
-rwxr-xr-x 1 root root 4567 Feb 23 10:00 /usr/local/sbin/ddns-client-update.sh
-rwxr-xr-x 1 root root 5678 Feb 23 10:00 /usr/local/libexec/nm-ra-addr-watch
-rwxr-xr-x 1 root root 3456 Feb 23 10:00 /etc/NetworkManager/dispatcher.d/90-nm-ns-update
```

**確認ポイント**:
- 各スクリプトが実行可能 (`0755`) であること。

#### DNS Update Key ファイルの確認

```bash
ls -l /etc/nsupdate/ddns-clients.key
```

**期待される出力例**:

```
-rw------- 1 root root 234 Feb 23 10:00 /etc/nsupdate/ddns-clients.key
```

**確認ポイント**:
- パーミッションが `0600` (root のみ読み書き可) であること。

#### nm-ra-addr-watch サービスの確認

```bash
sudo systemctl status nm-ra-addr-watch.service
```

**期待される出力例**:

```
● nm-ra-addr-watch.service - NetworkManager RA Address Watcher
     Loaded: loaded (/etc/systemd/system/nm-ra-addr-watch.service; enabled; vendor preset: enabled)
     Active: active (running) since ...
```

**確認ポイント**:
- `Active: active (running)` となっていること。
- `enabled` となっていること。

#### NetworkManager Dispatcher の動作確認

NetworkManager dispatcher が IP アドレス変更時にスクリプトを実行することを確認します:

```bash
sudo journalctl -u NetworkManager -n 50 | grep dispatcher
```

または:

```bash
sudo journalctl -u nm-dispatcher -n 50
```

接続を再起動してログを確認します:

```bash
sudo nmcli connection down ens160 && sudo nmcli connection up ens160
sudo journalctl -u NetworkManager -n 100 | grep -E '(dispatcher|90-nm-ns-update)'
```

**期待される出力例**:

```
Feb 23 10:30:00 hostname NetworkManager[1234]: <info>  [1234567890.1234] policy: set 'ens160' (ens160) as default for IPv4 routing and DNS
Feb 23 10:30:01 hostname NetworkManager[1234]: <info>  [1234567890.2345] dispatcher: (90-nm-ns-update) dispatched
```

## トラブルシューティング

### APT Lock タイムアウト時の対処

**症状**: Debian 系で `apt_lock_wait_timeout` (既定: 1800 秒) を超えてもロックが解放されず, タスクが失敗する。

**原因**: 他のプロセス (unattended-upgrades, apt-daily 等) が長時間ロックを保持している。

**対処方法**:

1. ロックを保持しているプロセスを特定します:

```bash
sudo lsof /var/lib/dpkg/lock-frontend
sudo lsof /var/lib/apt/lists/lock
```

2. 該当プロセスが自動更新の場合, 完了を待つか, 緊急時は以下で停止します:

```bash
sudo systemctl stop unattended-upgrades
sudo systemctl stop apt-daily.timer
sudo systemctl stop apt-daily-upgrade.timer
```

3. ロックファイルを手動で削除します (最終手段):

```bash
sudo rm /var/lib/dpkg/lock-frontend
sudo rm /var/lib/dpkg/lock
sudo rm /var/cache/apt/archives/lock
sudo rm /var/lib/apt/lists/lock
sudo dpkg --configure -a
```

4. `apt_lock_wait_timeout` を延長します:

```yaml
# group_vars/all/all.yml
apt_lock_wait_timeout: 3600  # 1 時間
```

### NetworkManager 設定が適用されない場合 (RHEL 系)

**症状**: `.nmconnection` ファイルを配置したが, `nmcli connection show` で接続が表示されない, または IP アドレスが設定されない。


1. 構文検証を行います:
**補足**:
固定 IP アドレスは `mac` 指定なしでも設定可能ですが, NIC 名が変わる環境を想定し, 固定 IP アドレスを設定する場合は `mac` 指定を推奨します。

```bash
sudo nmcli connection load /etc/NetworkManager/system-connections/ens160.nmconnection
```

エラーメッセージが表示された場合, 該当箇所を修正します。

2. パーミッションを確認します:

```bash
ls -l /etc/NetworkManager/system-connections/
```

`0600` でない場合は修正します:

```bash
sudo chmod 0600 /etc/NetworkManager/system-connections/*.nmconnection
```

3. NetworkManager を再起動します:

```bash
sudo systemctl restart NetworkManager
```

4. 接続を手動で有効化します:

```bash
sudo nmcli connection up ens160
```

5. SELinux コンテキストを確認, 修復します (RHEL 系):

```bash
sudo ls -Z /etc/NetworkManager/system-connections/
sudo restorecon -Rv /etc/NetworkManager/system-connections/
```

### netplan 適用失敗時の対処 (Debian 系)

**症状**: `netplan apply` が失敗し, ネットワーク設定が反映されない。

**原因**:
- netplan 設定ファイルの YAML 構文エラー。
- インデントの誤り。
- 存在しない NIC 名を指定している。

**対処方法**:

1. netplan 設定ファイルの構文検証を行います:

```bash
sudo netplan --debug generate
```

エラーメッセージが表示された場合, 該当箇所を修正します。

2. YAML の構文を確認します:

```bash
sudo yamllint /etc/netplan/99-netcfg.yaml
```

3. Dry-run で動作確認します:

```bash
sudo netplan try
```

120 秒以内に確認し, 問題なければ Enter を押して適用します。問題がある場合は自動的にロールバックされます。

4. NetworkManager のログを確認します:

```bash
sudo journalctl -u NetworkManager -n 50
```

5. NIC 名を確認します:

```bash
ip link show
```

設定ファイル内の NIC 名が実際のデバイス名と一致しているか確認します。

### 再起動後にネットワーク接続が失われる場合

**症状**: `common` ロール実行後の再起動後, SSH 接続ができなくなる。

**原因**:
- デフォルトゲートウェイの設定ミス。
- 管理系 NIC (`mgmt_nic`) の設定ミス。
- MAC アドレスと NIC 名のマッピングミス。

**対処方法**:

1. **事前予防**: playbook 実行前にコンソールアクセス (IPMI, iLO, vSphere コンソール等) を確保しておきます。

2. コンソールから以下を確認します:

```bash
ip addr show
ip route
```

3. `mgmt_nic` が正しく設定されているか確認します:

```yaml
# host_vars/hostname.local
mgmt_nic: "ens160"  # 実際の管理系 NIC 名を指定
```

4. `netif_list` の最初のエントリがデフォルトゲートウェイを持つ管理系 NIC になっているか確認します:

```yaml
netif_list:
  - netif: "ens160"  # mgmt_nic と一致させる
    mac: "00:50:56:12:34:56"
    ipv4_addr: "192.168.30.42"
    ipv4_cidr: "24"
    ipv4_gw: "192.168.30.1"  # ゲートウェイを必ず指定
```

5. MAC アドレスが正しいか確認します:

```bash
ip link show ens160
```

6. 一時的に DHCP で復旧します (緊急時):

RHEL 系:

```bash
sudo nmcli connection modify ens160 ipv4.method auto
sudo nmcli connection up ens160
```

Debian 系:

```bash
sudo dhclient ens160
```

7. 設定を修正してロールを再実行します。

### Dynamic DNS Update が動作しない場合

**症状**: `use_nm_ddns_update_scripts: true` を設定したが, DNS サーバに IP アドレスが登録されない。

**原因**:
- DNS サーバ側で Dynamic DNS が有効化されていない。
- TSIG キーが正しくない。
- NetworkManager dispatcher が実行されていない。

**対処方法**:

1. DNS サーバ側の設定を確認します (BIND の例):

```bash
# DNS サーバで確認
sudo cat /etc/bind/named.conf.local
```

`allow-update` ディレクティブが正しく設定されているか確認します。

2. TSIG キーを確認します:

```bash
# クライアント側
sudo cat /etc/nsupdate/ddns-clients.key
```

DNS サーバ側のキーと一致しているか確認します。

3. 手動で nsupdate を実行してテストします:

```bash
sudo nsupdate -k /etc/nsupdate/ddns-clients.key <<EOF
server 192.168.30.1
zone example.com
update delete hostname.example.com A
update add hostname.example.com 300 A 192.168.30.42
send
EOF
```

成功する場合は, スクリプト側の問題です。失敗する場合は, DNS サーバ側の設定を確認します。

4. NetworkManager dispatcher のログを確認します:

```bash
sudo journalctl -u NetworkManager | grep -E '(dispatcher|90-nm-ns-update)'
```

5. スクリプトを手動で実行してデバッグします:

```bash
sudo /usr/local/sbin/ddns-client-update.sh ens160 up
```

エラーメッセージを確認します。

6. ログレベルを上げて詳細なログを確認します:

```yaml
# host_vars/hostname.local
nm_ns_update_log_level: 4  # Debug レベル
```

ロールを再実行後, ログを確認します:

```bash
sudo journalctl -u NetworkManager | grep nm-ns-update
```

### Sudoers 設定が反映されない場合

**症状**: sudo 実行時にパスワードを求められる。

**原因**:
- `/etc/sudoers` が `/etc/sudoers.d/` を読み込んでいない。
- Drop-in ファイルのパーミッションが正しくない。
- ユーザが該当グループに所属していない。

**対処方法**:

1. `/etc/sudoers` が `/etc/sudoers.d/` を読み込んでいるか確認します:

```bash
sudo grep -E 'includedir.*sudoers.d' /etc/sudoers
```

`#@includedir /etc/sudoers.d` または `@includedir /etc/sudoers.d` が存在することを確認します。

2. Drop-in ファイルのパーミッションを確認します:

```bash
ls -l /etc/sudoers.d/
```

`0440` または `0400` であることを確認します。 `0644` 等の場合, sudoers が無視します:

```bash
sudo chmod 0440 /etc/sudoers.d/99-nopasswd-group-sudo
```

3. ユーザのグループ所属を確認します:

```bash
groups
```

または:

```bash
id
```

`sudo` または `wheel` グループに所属しているか確認します。所属していない場合は追加します:

```bash
sudo usermod -aG sudo username  # Debian 系
sudo usermod -aG wheel username  # RHEL 系
```

4. 設定ファイルの構文を検証します:

```bash
sudo visudo -cf /etc/sudoers.d/99-nopasswd-group-sudo
```

エラーがある場合は修正します。

5. 再ログインして反映を確認します (グループ変更を行った場合):

```bash
exit
# SSH で再接続
sudo whoami
```

## 補足

### ハンドラ

本ロールは以下のハンドラを定義しています:

- **avahi**: Avahi (mDNS) サービスを再起動します (`mdns_enabled: true` の場合)。
- **disable_gui**: GUI を無効化し, multi-user.target に設定します (サーバ環境用)。
- **auto_remove** / **pkg-autoremove**: 不要なパッケージを自動削除します (apt autoremove / dnf autoremove)。
- **nm_reload_and_activate**: NetworkManager 設定をリロードし, 接続を有効化します (RHEL 系)。
- **netplan_apply**: netplan 設定を適用します (Debian 系)。
- **common_reload_sysctl**: sysctl 設定をリロードします。

### 他ロールとの依存関係

`common` ロールは他のすべてのロールの基盤となるため, playbook の最初に実行されます。典型的なノード設定作業ロール実行順序は以下のようになります:

1. 共通設定処理 (`common` ロール (本ロール) )
2. ユーザ設定ファイルスケルトンの作成 (`user-settings` ロール)
3. ユーザ作成 (`create-users` ロール)
4. ユーザ作成後に実施するユーザ固有設定 (`post-user-create` ロール)
5. 時刻同期関連設定 (`ntp-client` ロール, `ntp-server` ロール )
6. デーモン/サーバ設定 (`dns-server` ロール など)
7. Kubernetes 共通設定 (`k8s-common` ロール, Kubernetesクラスタを構成するノードの場合)
8. Kubernetes クラスタ構築 (`k8s-ctrlplane` ロール, `k8s-worker` ロール 等, Kubernetesクラスタを構成するノードの場合)
9. Kubernetes クラスタ構築後の設定 (`k8s-hubble-ui` ロール 等, Kubernetesクラスタを構成するノードの場合)

### DNS Client Scripts の詳細

`use_nm_ddns_update_scripts: true` を設定すると, 以下の機能が有効になります:

#### ddns-client-update.sh

NetworkManager の IP アドレス変更イベントを受けて, DNS サーバに nsupdate を送信するスクリプトです。IPv4 と IPv6 の両方に対応します。

**主な機能**:
- NetworkManager dispatcher から呼び出され, IP アドレスが変更されたときに実行されます。
- TSIG キーを使用して安全に DNS レコードを更新します。
- A レコード (IPv4) と AAAA レコード (IPv6) を自動的に登録, 更新します。
- 古い IP アドレスのレコードを削除し, 新しい IP アドレスを追加します。

#### nm-ra-addr-watch

IPv6 Router Advertisement (RA) で配布される IP アドレスを監視し, 変更を検出するスクリプトです。

**主な機能**:
- 定期的に (既定: 10 秒間隔) ネットワークインターフェースの IPv6 アドレスを監視します。
- RA で配布される一時アドレス (temporary address) ではなく, 永続的なアドレスを使用します。
- アドレス変更を検出すると, `ddns-client-update.sh` を呼び出して DNS を更新します。
- デバウンス機能により, 短時間での連続更新を防止します。

#### 90-nm-ns-update

NetworkManager dispatcher スクリプトです。ネットワークインターフェースの up / down イベント時に実行されます。

**主な機能**:
- インターフェース起動時に `ddns-client-update.sh` を呼び出します。
- allow / deny 正規表現によるインターフェースフィルタリング機能を持ちます。
- ログレベル (`nm_ns_update_log_level`) により出力の詳細度を調整できます。

**注意事項**:
- DNS サーバ側で Dynamic DNS (nsupdate) を有効化し, TSIG キーを設定しておく必要があります。
- `templates/ddns-clients-key-file.j2` テンプレート内で TSIG キーの内容を設定します。
- セキュリティのため, TSIG キーファイルのパーミッションは `0600` に設定されます。

### 再起動に関する注意事項

本ロールはネットワーク設定を変更するため, 以下のタイミングで自動的に再起動します:

- `/var/run/reboot-required` ファイルが存在する場合 (Debian 系パッケージ更新後)。
- ネットワーク設定変更後 (`config-network-multi.yml` 内)。

**再起動時の注意点**:
- `reboot_timeout_sec` (既定: 600 秒) 以内にシステムが起動することを想定しています。起動が遅い環境では延長してください。
- 再起動により SSH 接続が一時的に切断されます。Ansible はホストの応答を待機します。
- 管理系 NIC の設定ミスにより, 再起動後に SSH 接続できなくなる可能性があります。事前にコンソールアクセスを確保してください。

### netif_list 変数の詳細

`netif_list` は複数のネットワークインターフェースを定義するリスト変数です。各エントリは以下の属性を持ちます:

| 属性名 | 必須 | 説明 | 例 |
| --- | --- | --- | --- |
| `netif` | 必須 | NIC 名 | `"ens160"` |
| `mac` | 条件付き | systemd の .link 機能で NIC 名を固定化する場合に必須となる MAC アドレス | `"00:50:56:12:34:56"` |
| `ipv4_addr` | 条件付き | 固定 IPv4 アドレスを設定する場合に必須となる IPv4 アドレス | `"192.168.30.42"` |
| `ipv4_cidr` | 条件付き | 固定 IPv4 アドレスを設定する場合に必須となる IPv4 プレフィックス長 | `"24"` |
| `ipv4_gw` | 任意 | IPv4 ゲートウェイ (管理系 NIC のみ推奨) | `"192.168.30.1"` |
| `ipv4_dns1` | 任意 | IPv4 DNS サーバ 1 | `"192.168.30.1"` |
| `ipv4_dns2` | 任意 | IPv4 DNS サーバ 2 | `"8.8.8.8"` |
| `ipv6_addr` | 条件付き | 固定 IPv6 アドレスを設定する場合に必須となる IPv6 アドレス | `"fd69:6684:61a:1::42"` |
| `ipv6_cidr` | 条件付き | 固定 IPv6 アドレスを設定する場合に必須となる IPv6 プレフィックス長 | `"64"` |
| `ipv6_gw` | 任意 | IPv6 ゲートウェイ (管理系 NIC のみ推奨) | `"fd69:6684:61a:1::1"` |
| `ipv6_dns1` | 任意 | IPv6 DNS サーバ 1 | `"fd69:6684:61a:1::1"` |
| `ipv6_dns2` | 任意 | IPv6 DNS サーバ 2 | `"2001:4860:4860::8888"` |

**補足**:
固定 IP アドレスは `mac` 指定なしでも設定可能ですが, NIC 名が変わる環境を想定し, 固定 IP アドレスを設定する場合は `mac` を指定することを推奨します。

**デフォルト動作**:
- `netif_list` が未定義または空リストの場合, `mgmt_nic` を含む単一エントリのリストが自動生成されます。
- 最初のエントリが管理系 NIC (`mgmt_nic`) として扱われます。
- ゲートウェイは管理系 NIC のみに設定することを推奨します (複数ゲートウェイによるルーティング競合を防止)。

**デフォルト設定での具体的な動作**:
- `netif_list` が未定義かつ `gateway4`, `gateway6` も未定義（空文字列）の場合, 管理系 NIC は **DHCP（IPv4）と SLAAC（IPv6）による自動構成** で機能します。NIC に対してゲートウェイやルート設定は出力されません (DHCP/SLAAC で取得したルートを使用)。
- `netif_list` が未定義の場合, `gateway4` や `gateway6`で指定されたゲートウエイアドレスは使用されず, DHCP（IPv4） や SLAAC（IPv6）による自動構成に従って, ゲートウエイアドレスを設定します。固定ゲートウェイアドレスを指定する場合は, 必ず `netif_list` で固定IP アドレスを設定してください(固定IPアドレス設定がない場合, テンプレート処理時に ゲートウェイ設定を無視する仕様です)。

### SELinux に関する注意事項 (RHEL 系)

`common_selinux_state` で SELinux のモードを制御できます:

- `enforcing`: SELinux を強制モードで有効化 (本番環境推奨)。
- `permissive`: SELinux を警告のみのモードで有効化 (デバッグ用)。
- `disabled`: SELinux を完全に無効化 (非推奨)。

**ファイルコンテキストの復元**:

NetworkManager keyfiles 配置後, SELinux コンテキストを復元します:

```bash
sudo restorecon -Rv /etc/NetworkManager/system-connections/
```

**注意**: `disabled` から `enforcing` / `permissive` への変更, または逆の変更には再起動が必要です。

### Cloud-Init との共存

RHEL 系では, Cloud-Init が作成する udev ルールが NetworkManager の動作を妨げる場合があります。本ロールは以下の対処を行います:

- `/etc/cloud/cloud.cfg.d/99-disable-network-config.cfg` を作成し, Cloud-Init のネットワーク設定を無効化します。
- `/etc/cloud/cloud.cfg.d/99-disable-network-rename.cfg` を作成し, Cloud-Init のネットワークインターフェース名変更を無効化します。
- `/etc/udev/rules.d/75-persistent-net-generator.rules`, `/lib/udev/rules.d/75-persistent-net-generator.rules`, `/usr/lib/udev/rules.d/75-persistent-net-generator.rules` が存在する場合, `.orig` を付けてバックアップしたうえで, `/etc/udev/rules.d/75-persistent-net-generator.rules` に空ファイルを配置して udev の生成ルールをマスクします。
- `/etc/udev/rules.d/70-persistent-net.rules`, `/lib/udev/rules.d/70-persistent-net.rules`, `/usr/lib/udev/rules.d/70-persistent-net.rules` が存在する場合, `.orig` を付けてバックアップしたうえで, `/etc/udev/rules.d/70-persistent-net.rules` に空ファイルを配置して永続化ルールをマスクします。
- `udevadm control --reload-rules && udevadm trigger` を実行して更新した udev ルールを反映します。
- `/etc/sysconfig/network-scripts/` 配下の `ifcfg-*` ファイルを削除し, 旧形式の設定が残存しないようにします。
- NetworkManager 設定適用後に再起動し, 変更を反映します。

これらの対処により, Cloud-Init や udev のフォールバック処理が NIC 名や, ネットワークインターフェースが認識される順番とそれに紐づく NIC 名の順序の変更を引き起こし, systemd .link によるインターフェース名固定化が無効化される事象を抑止します。

Debian 系では Cloud-Init の自動ネットワーク設定ファイル (`/etc/netplan/50-cloud-init.yaml`) に `.old` 拡張子を付けてリネームし無効化します。

### yq コマンドについて

yq は YAML ファイルを操作するコマンドラインツールです。本ロールでは GitHub から最新バイナリを直接ダウンロードしてインストールします。Debian/Ubuntu では, RHEL 9 搭載の yq パッケージ相当の yq を導入する場合, snap (Ubuntu のアプリ配布, 実行基盤) を用いたインストールが必要になります。しかし, snap を用いると yq コマンドがコンテナ内で実行され, 特権ユーザ (`root` ユーザ) で実行できないなど, 本 playbook が行うノードやゲスト OS の設定作業に不向きなため, 直接ダウンロードする方式を採用しています。

**インストール先**: `/usr/local/bin/yq`

**バージョン確認**:

```bash
yq --version
```

**用途**: Kubernetes マニフェストの編集, Ansible 変数ファイルの操作等に使用します。
