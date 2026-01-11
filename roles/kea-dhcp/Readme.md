# kea-dhcp ロール

このロールは Kea DHCPv4 サーバーをインストールし, Jinja2 テンプレートで `/etc/kea/kea-dhcp4.conf` を生成してサービスを有効化します。Kubernetes 管理ネットワーク向けのプール/ゲートウェイ/DNS 設定をローカル変数から組み立て, 設定変更時はハンドラで `kea-dhcp4` サービスを再起動します。

## 変数一覧

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `kea_dhcp_interface` | `{{ gpm_mgmt_if \| default(mgmt_nic, true) }}` | Kea がバインドするインターフェース名。管理 NIC が未指定の場合は `mgmt_nic` を使用。 |
| `kea_dhcp_config_file` | `/etc/kea/kea-dhcp4.conf` | 生成する設定ファイルの配置先。 |
| `kea_reclaim_timer_wait_time` | `10` | リース回収確認周期 (秒)。 |
| `kea_flush_reclaimed_timer_wait_time` | `25` | 回収済みリースのフラッシュ周期 (秒)。 |
| `kea_hold_reclaimed_time` | `3600` | 回収済みリースの保持期間 (秒)。 |
| `kea_max_reclaim_leases` | `100` | 回収処理 1 回あたりの最大リース数。 |
| `kea_max_reclaim_time` | `250` | 回収処理の最大実行時間 (ミリ秒)。 |
| `kea_unwarned_reclaim_cycles` | `5` | 警告なしで許容する連続回収サイクル数。 |
| `kea_renew_timer_wait_time` | `600` | クライアントのリース更新開始までの時間 (秒)。 |
| `kea_rebind_timer_wait_time` | `1800` | リバインド開始までの時間 (秒)。 |
| `kea_valid_lifetime` | `14400` | リース有効期限 (秒)。 |
| `kea_dns_servers` | `["{{dns_server_ipv4_address}}"]` | DHCP で配布する DNS サーバー一覧。 |
| `kea_domain_name` | `{{ dns_domain }}` | 配布するドメイン名。 |
| `kea_domain_search` | `["{{ dns_domain }}"]` | サーチドメインリスト。 |
| `kea_subnet` | `{{ gpm_mgmt_ipv4_network_cidr}}` | DHCP を提供するサブネット (CIDR)。 |
| `kea_pool` | `{{ gpm_mgmt_ipv4_prefix }}.100 - {{ gpm_mgmt_ipv4_prefix }}.254` | アドレスプール範囲。 |
| `kea_gateway` | `{{ gpm_mgmt_ipv4_network_gateway }}` | デフォルトゲートウェイ。 |
| `kea_dhcp_log_file` | `/var/log/kea/kea-dhcp4.log` | Kea ログファイル出力先。 |
| `kea_dhcp_log_maxsize` | `2048000` | ログローテート前の最大サイズ (バイト)。 |
| `kea_dhcp_log_maxver` | `4` | ログローテート世代数。 |
| `kea_lease_db_type` | `memfile` | リース DB 種別 (`memfile` / `mysql` / `pgsql`)。 |
| `kea_lease_db_name` | OS 依存 | リース DB パス。Debian 系: `/var/lib/kea/kea-leases4.csv`, RHEL 系: `/var/lib/kea/kea-dhcp4.leases` (`vars/cross-distro.yml`で切替)。 |
| `kea_dhcp4_server_packages` | OS 依存 | インストールする Kea パッケージ。Debian 系: `kea-dhcp4-server`, RHEL 系: `kea-dhcp4`。 |
| `kea_dhcp4_server_service` | OS 依存 | 有効化/起動するサービス名。Debian 系: `kea-dhcp4-server`, RHEL 系: `kea-dhcp4`。 |

## ロール内の動作

共通のネットワーク/パッケージ変数は [vars/cross-distro.yml](vars/cross-distro.yml) および [vars/all-config.yml](vars/all-config.yml) を参照します。

1. [tasks/load-params.yml](roles/kea-dhcp/tasks/load-params.yml#L8-L23) で OS ごとのパッケージ名, クロスディストロ変数, 共通ネットワーク設定, Kubernetes API 広告アドレス設定を読み込みます。
2. [tasks/package.yml](roles/kea-dhcp/tasks/package.yml#L8-L13) で `kea_dhcp4_server_packages` をインストールします。
3. [tasks/config.yml](roles/kea-dhcp/tasks/config.yml#L8-L28) で [templates/kea-dhcp4.conf.j2](roles/kea-dhcp/templates/kea-dhcp4.conf.j2) を `/etc/kea/kea-dhcp4.conf` に展開し, 変更時はハンドラ `restart_kea_dhcp4_server` を通知します。
4. 同タスクで `kea_dhcp4_server_service` を `enabled: true` で有効化し, `state: started` で起動します。ハンドラは [handlers/restart_dhcp4_server.yml](roles/kea-dhcp/handlers/restart_dhcp4_server.yml#L8-L15) でサービスを再起動します。

## 利用の流れ

1. 管理ネットワークの CIDR/ゲートウェイ/DNS (`gpm_mgmt_*`, `dns_*`) を [vars/all-config.yml](vars/all-config.yml) などで定義します。
2. `ansible-playbook -i inventory/hosts server.yml --tags kea-dhcp` などでロールを実行します (プレイブックに付与されたタグに合わせて指定してください)。

## 検証ポイント

- 制御対象ノードに `/etc/kea/kea-dhcp4.conf` が生成され, `interfaces`, `subnet4`, `option-data` が期待どおりに設定されていること。
- `systemctl status {{ kea_dhcp4_server_service }}` でサービスが `active (running)` かつ `enabled` になっていること。
- ログファイル `{{ kea_dhcp_log_file }}` が指定サイズでローテートされていること。
- クライアントに配布されるアドレスが `kea_pool` の範囲に入り, ルータ/DNS オプションが意図した値になっていること。
