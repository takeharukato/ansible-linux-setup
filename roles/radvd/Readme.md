# radvd ロール

このロールは Router Advertisement Daemon (radvd) を導入し, 管理ネットワーク向けに IPv6 ルーター広告 (RA) を配布する設定ファイル `/etc/radvd.conf` を生成します。SLAAC 用プレフィックス, デフォルトルート, RDNSS/DNSSL ( DNS サーバ・サーチドメイン ) を広告し, 設定変更時は radvd を再起動します。

## 変数一覧

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `radvd_nic` | `{{ gpm_mgmt_nic \| default(mgmt_nic, true) }}` | RA を配布するインターフェース。 |
| `radvd_router_advertisement_min_interval` | `30` | RA 送信最小間隔 (秒)。 |
| `radvd_router_advertisement_max_interval` | `100` | RA 送信最大間隔 (秒)。 |
| `radvd_router_advertisement_prefix` | `{{ gpm_mgmt_ipv6_prefix }}/{{ gpm_mgmt_ipv6_addr_prefix_len }}` | 広告する IPv6 プレフィックス。 |
| `radvd_router_advertisement_reachable_time` | `3000` | AdvReachableTime (ms)。 |
| `radvd_router_advertisement_retrans_timer` | `1000` | AdvRetransTimer (ms)。 |
| `radvd_router_advertisement_default_lifetime` | `300` | デフォルトルータの lifetime (秒)。0 でデフォルトルート無効。 |
| `radvd_router_advertisement_prefix_valid_lifetime` | `'infinity'` | プレフィックスの有効期限。 |
| `radvd_router_advertisement_prefix_preferred_lifetime` | `'infinity'` | プレフィックスの推奨期限。 |
| `radvd_dns_servers` | `[ "{{ ipv6_name_server1 }}", "{{ ipv6_name_server2 }}" ]` | RDNSS に広告する DNS サーバ。 |
| `radvd_search_domains` | `[ "{{ dns_domain }}" ]` | DNSSL に広告する検索ドメイン。 |
| `radvd_package` | OS 依存 (`radvd`) | インストールするパッケージ名。`vars/cross-distro.yml` で解決。 |
| `radvd_service_name` | OS 依存 | 起動・再起動するサービス名。`vars/cross-distro.yml` で解決。 |
| `radvd_config_file_path` | `/etc/radvd.conf` | 生成する設定ファイルのパス。 |

## ロール内の動作

1. [tasks/load-params.yml](roles/radvd/tasks/load-params.yml#L8-L23) で OS 別パッケージ名や共通変数を読み込み。
2. [tasks/package.yml](roles/radvd/tasks/package.yml#L8-L13) で radvd パッケージを導入。
3. [tasks/config.yml](roles/radvd/tasks/config.yml#L8-L17) でテンプレート [templates/radvd.conf.j2](roles/radvd/templates/radvd.conf.j2#L1-L39) を `{{ radvd_config_file_path }}` へ配置し, 変更時にハンドラを通知。
4. ハンドラ [handlers/restart-radvd.yml](roles/radvd/handlers/restart-radvd.yml#L8-L16) で radvd を再起動 (`enabled: true`)。サービス有効化はハンドラ内で実施。

## テンプレートで設定される主な項目

- RA 関連: `AdvSendAdvert on;`, `MinRtrAdvInterval`, `MaxRtrAdvInterval`, `AdvReachableTime`, `AdvRetransTimer`, `AdvDefaultLifetime`
- SLAAC 用プレフィックス: `prefix {{ radvd_router_advertisement_prefix }}` 配下で `AdvValidLifetime`, `AdvPreferredLifetime`, `AdvAutonomous on`, `AdvOnLink on`
- DNS 配布: `RDNSS` で DNS サーバ, `DNSSL` で検索ドメインを空白区切りで広告

## 利用の流れ

1. `radvd_nic`, `radvd_router_advertisement_prefix`, `radvd_dns_servers`, `radvd_search_domains` などを必要に応じて `group_vars/host_vars` で上書き。
2. `make run_radvd` などでロールを実行 ( プレイブックのタグに合わせて指定 ) 。
3. 配置後, `radvd` が起動し, クライアントは SLAAC アドレス・デフォルトルート・DNS 情報を RA で取得。

## 検証ポイント

- `systemctl status {{ radvd_service_name }}` で `active (running)` / `enabled` を確認。
- クライアントで `ip -6 addr` に SLAAC アドレスが付与され, `ip -6 route` にデフォルトルートが追加されているか。
- `rdisc6 {{ radvd_nic }}` や `radvdump` で RA 内容に DNS (RDNSS/DNSSL), A/L フラグ付きプレフィックスが含まれるか。
- RA の送信間隔が `MinRtrAdvInterval`から`MaxRtrAdvInterval` に収まるか, `AdvDefaultLifetime` に応じた期限が付与されているか。
