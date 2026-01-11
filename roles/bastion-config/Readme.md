# bastion-config ロール

このロールは踏み台サーバ (ゲートウェイサーバー) のネットワーク設定を行います。具体的には, IPv4/IPv6 パケット転送の有効化, Reverse Path Filtering (RPF) の設定, NAT ルール (iptables/ip6tables) の設定, および sysctl 設定ファイルの生成・配置を実施します。複合ネットワーク環境で管理ネットワークと外部ネットワーク間のトラフィック中継を実現します。

## 前提条件

ロールの実行には以下の変数が必須です：

- `gpm_mgmt_nic` - 仮想環境内部管理ネットワークのインターフェース名
- `mgmt_nic` - 物理サーバ/管理用ネットワークのインターフェース名
- `gpm_mgmt_ipv4_network_cidr` - 管理ネットワークの IPv4 CIDR
- `gpm_mgmt_ipv6_network_cidr` - 管理ネットワークの IPv6 CIDR

これらが未定義またはシステムに存在しないインターフェースの場合, ロールは実行されません。

## 変数一覧

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `iptables_persistent_package` | OS 依存 | インストールする iptables 永続化パッケージ。Debian 系: `iptables-persistent`, RHEL 系: `iptables-services`。 |
| `iptables_persistent_service` | OS 依存 | 有効化する iptables サービス名。Debian 系: `netfilter-persistent`, RHEL 系: `iptables`。 |
| `iptables_persistent_ipv6_service` | OS 依存 | 有効化する ip6tables サービス名。RHEL 系のみ: `ip6tables`。 |
| `mgmt_nic` | (必須) | 物理サーバ/管理ネットワークのインターフェース名。 |
| `gpm_mgmt_nic` | (必須) | 仮想環境内部管理ネットワークのインターフェース名。 |
| `gpm_mgmt_ipv4_network_cidr` | (必須) | 管理ネットワークの IPv4 CIDR (例: `192.168.30.0/24`)。 |
| `gpm_mgmt_ipv6_network_cidr` | (必須) | 管理ネットワークの IPv6 CIDR (例: `fdad:ba50:248b:1::/64`)。 |

OS 別の詳細は [vars/cross-distro.yml](../../vars/cross-distro.yml) を参照してください。

## ロール内の動作

1. [tasks/load-params.yml](tasks/load-params.yml) で OS ごとのパッケージ名, ディストロ差異吸収変数, 共通ネットワーク設定を読み込みます。
2. 以降のタスク実行は `gpm_mgmt_nic` と `mgmt_nic` が定義済みかつシステムに存在するという条件で進みます。
3. [tasks/package.yml](tasks/package.yml) で `iptables_persistent_package` をインストールします。
4. [tasks/config-sysctl.yml](tasks/config-sysctl.yml) で [templates/95-ipfoward.j2](templates/95-ipfoward.j2) を `/etc/sysctl.d/95-ipfoward.conf` に展開します。テンプレートは以下の設定を行います：
   - IPv4 パケット転送の有効化 (`net.ipv4.ip_forward=1`)
   - IPv4 Reverse Path Filtering をルーズモードに設定 (`net.ipv4.conf.all.rp_filter=2`, `.default.rp_filter=2`)
   - IPv6 パケット転送の有効化 (`net.ipv6.conf.all.forwarding=1`, `.default.forwarding=1`)
   - 管理インターフェースでのルーター広告受け入れ (`net.ipv6.conf.{{ mgmt_nic }}.accept_ra=2`)
5. 設定変更時はハンドラ `bastion_config_reload_sysctl` で `sysctl --system` を実行します。
6. [tasks/config-nat.yml](tasks/config-nat.yml) で iptables/ip6tables ルールを設定します：
   - **IPv4 NAT**: 管理ネットワークから外部ネットワークへのトラフィックを MASQUERADE で変換
   - **IPv4 FORWARD**: 管理 => 外部, 外部 => 管理のパケット転送を許可 ( conntrack による既確立接続判定 )
   - **IPv6 FORWARD**: 管理↔外部の双方向パケット転送を許可
   - OS ごとの永続化: Debian/Ubuntu は `netfilter-persistent save`, RHEL/CentOS は `iptables-save` / `ip6tables-save` を実行
7. [tasks/service.yml](tasks/service.yml) でサービスを有効化します ( RHEL 系のみ, Debian 系は netfilter-persistent が自動処理 ) 。

## 利用の流れ

1. 仮想環境と物理ネットワークのインターフェース名およびネットワーク CIDR を [vars/all-config.yml](../../vars/all-config.yml) で定義します。
2. `make run_bastion_config` などでロールを実行します。
3. sysctl 設定は即座に反映され, iptables ルール, iptables/ip6tables サービス設定は有効化されます。

## 検証ポイント

- `/etc/sysctl.d/95-ipfoward.conf` が正しく生成され, パケット転送およびフォワーディング設定が期待どおりか。
- `sysctl net.ipv4.ip_forward` などで現在のカーネル設定が `1` になっているか。
- `iptables -t nat -L POSTROUTING` で MASQUERADE ルールが登録されているか。
- `iptables -L FORWARD` で ACCEPT ルールが登録されているか。
- `ip6tables -L FORWARD` で IPv6 パケット転送ルールが登録されているか。
- Debian 系: `sudo iptables-save > /etc/iptables/rules.v4` など永続化コマンドが実行されているか。
- RHEL 系: `systemctl status iptables` および `systemctl status ip6tables` でサービスが `enabled` かつ `active` か。
- 仮想環境内部管理ネットワーク内のクライアントが外部ネットワークへ到達でき, かつ応答パケットが返ってくるか。
