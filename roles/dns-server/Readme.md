# dns-server ロール

このロールは BIND を用いた権威兼キャッシュ DNS サーバーを構成します。対象 OS のファクトに応じて Debian 系と RHEL 系の差異を吸収し, ゾーンファイルと `named.conf`/`named.conf.options` をテンプレートで生成します。Dynamic DNS 更新用の TSIG キーを組み込み, IPv4/IPv6 双方の順引き・逆引きゾーンを作成し, 必要に応じて systemd, SELinux, Firewall の周辺設定も行います。

## 主な処理

- `tasks/load-params.yml` で OS ファミリー別パッケージ (`vars/packages-ubuntu.yml` / `vars/packages-rhel.yml`) と `vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml` を読み込み, ドメインやネットワーク関連変数を構成します。
- `tasks/package.yml` が `dns_bind_packages` を最新化し, 変更があれば `disable_gui` ハンドラ ( `systemctl set-default multi-user.target` )を通知します。
- `tasks/config.yml` が以下を順に実施します。
  - 設定・ゾーン格納ディレクトリを所定の所有者とパーミッションで作成。
  - RHEL 系では既存の `named.conf` をバックアップしたうえで `rhel-named.conf.j2` を適用し, Debian 系では `lineinfile` でゾーン include のみ挿入します。
  - OS ごとの `named.conf.options` テンプレートを配置し, フォワーダー (`dns_bind_forwarders`) や ACL (`dns_network` / `dns_network_ipv6_prefix`) を反映します。
  - `named.conf.zones.j2` と各ゾーンテンプレートを展開し, `dns_host_list`・`bind_serial` から順引き/逆引きレコードを生成します。`bind_serial` が未指定なら日付ベースで設定します。
  - 複数ネットワーク対応: `internal_network_list` が定義かつ非空の場合, カスタムフィルター (`ipv4_reverse_zone`, `ipv6_reverse_zone`) でネットワーク CIDR から逆引きゾーン名を自動計算し, 追加の IPv4/IPv6 逆引きゾーンファイル (`db.reverse.additional.j2`, `db.reverse.additional.ipv6.j2`) をループで生成します。生成されるゾーンはスケルトン（SOA + NS のみ）で, PTR/PTR6 レコードは nsupdateで動的登録を前提としています。
  - `dns_bind_options_conf_path` の include 行を保証し, `named_check_conf` と `Reload systemd & restart named` ハンドラを通知します。
  - SELinux 有効な RHEL 系では zone ディレクトリの fcontext を `semanage` で登録し `restorecon` を実行します。
  - 最後に `named-checkconf -z` と `systemd` リスタート, `rndc reload` を順に行います。
- `dns_bind_ipv4_only` が true の場合に `tasks/config-systemd-ipv4-only.yml` が `systemctl show` で取得した ExecStart に `-4` フラグが無い場合のみ drop-in (`templates/90-override.conf.j2`) を生成し, IPv4 応答に限定します (デフォルトでは IPv6 も LISTEN)。
- `tasks/config-firewall.yml` は `enable_firewall` が真のときに firewalld または UFW を自動判別し, `dns_bind_port` の TCP/UDP を開放します。バックエンドが検出されない場合は通知のみを実施します。
- ハンドラは `Reload systemd & restart named`／`named_check_conf`／`reload_zone`／`disable_gui` を提供し, 構成変更に応じた再読み込みとランレベル固定を行います。

## Firewall 周辺の挙動

| enable_firewall | firewalld 動作状況 | UFW 利用可否 | 実行される処理 |
| ---------------- | ------------------ | ------------ | -------------- |
| false            | 無関係             | 無関係       | `config-firewall.yml` はスキップされます。|
| true             | 実行中             | 任意         | `firewall-cmd` で DNS サービスまたは `dns_bind_port` を永続/ランタイム双方に開放します (`dns_bind_firewall_zone` が空ならデフォルトゾーン)。|
| true             | 非稼働             | 利用可       | `ufw allow {{ dns_bind_port }}/tcp,udp` を既存ルールを見ながら追加します。|
| true             | 非稼働             | 利用不可     | いずれのバックエンドも検出できず, スキップメッセージのみを出力します。|

## 利用する主な変数

| 変数名 | 定義場所 (初期値) | 用途 |
| ------ | ----------------- | ---- |
| `dns_bind_packages` | `vars/cross-distro.yml` | OS 別 BIND パッケージ一覧。必要に応じてホスト/グループ変数で追加します。|
| `dns_domain` / `dns_server` | `vars/all-config.yml` | 正引きゾーン名と SOA ホスト名。ゾーンファイルの SOA・NS レコードを決定します。|
| `dns_network` / `dns_network_ipv4_prefix_len` | `vars/all-config.yml` | IPv4 ACL とゾーン内 A レコードのベースアドレス。|
| `dns_network_ipv6_prefix` / `dns_network_ipv6_prefix_len` | `vars/all-config.yml` | IPv6 ACL や逆引きゾーンの生成に使用します。|
| `dns_host_list` | `vars/all-config.yml` | テンプレート化された順引き/逆引きレコードを生成するためのホスト定義。|
| `dns_bind_forwarders` | `roles/dns-server/defaults/main.yml` | 上位 DNS へのフォワーダー一覧。空にすると forward 設定を省略します。|
| `dns_ddns_key_name` / `dns_ddns_key_secret` | `defaults/main.yml` / `vars/all-config.yml` | TSIG キー名とシークレット。Dynamic DNS クライアントと共有し, `named.conf.zones` の update-policy に使用します。|
| `dns_bind_selinux_target` | `defaults/main.yml` | RHEL 系で `semanage fcontext` に適用するパス。デフォルトは `/var/named(/.*)?`。|
| `dns_bind_ipv4_only` | `defaults/main.yml` (false) | true で IPv4 のみ応答させる systemd drop-in を適用します。IPv6 を利用する環境では false のままにします。|
| `dns_bind_systemd_dropin_dir` | `defaults/main.yml` | IPv4 限定用 drop-in を配置するディレクトリ。|
| `enable_firewall` / `dns_bind_firewall_zone` | `roles/common/defaults/main.yml` / `defaults/main.yml` | Firewall 設定の有効化と対象ゾーン (firewalld のみ)。|
| `internal_network_list` | `group_vars/all/all.yml` (デフォルト: `[]`) | 複数ネットワーク逆引きゾーン対応: 追加ネットワークのリスト。各要素は `{ipv4: "...", ipv6: "..."}` 形式。後述の「複数ネットワーク逆引きゾーン対応」を参照。|
| `has_additional_networks` | `defaults/main.yml` (計算値) | `internal_network_list` が定義かつ非空かどうかを示す共通変数。テンプレート・タスク双方で条件判定に使用します。|

テンプレートは `templates/` 配下にあり, 環境に合わせて `named.conf.*` や `db.*` を生成します。特に `named.conf.zones.j2` では `grant ddns-clients zonesub` によりサブゾーン単位の Dynamic DNS を許可します。`bind_serial` を事前に指定すると SOA シリアルを固定できます。

## 複数ネットワーク逆引きゾーン対応

本ロールは複数ネットワークの逆引きゾーン（IPv4 PTR / IPv6 PTR6）を自動生成できます。

### 機能概要

- **単一ネットワーク**: 既存の `dns_ipv4_reverse`, `dns_ipv6_reverse`, `dns_host_list` による逆引きゾーン生成は **変更なし**で引き続き利用可能。
- **複数ネットワーク**: `internal_network_list` を定義することで、追加ネットワークの逆引きゾーンを自動生成。各ネットワークはカスタムフィルター（`ipv4_reverse_zone`, `ipv6_reverse_zone`）で CIDR ノーテーションから自動的にゾーン名を計算。
- **動的登録対応**: 追加ネットワークのゾーンファイルはスケルトン（SOA + NS のみ）で生成。PTR/PTR6 レコードはクライアント側の `nsupdate` で動的に登録する運用を想定。

### 設定例

#### `group_vars/all/all.yml` または `host_vars/<hostname>/main.yml`

```yaml
# === 複数ネットワーク逆引きゾーン ===
internal_network_list:
  # ネットワーク1: IPv4 + IPv6 双方指定
  - ipv4: "192.168.30.0/24"
    ipv6: "fd69:6684:61a:2::/64"
  # ネットワーク2: IPv4 のみ
  - ipv4: "192.168.40.0/25"
  # ネットワーク3: IPv6 のみ
  - ipv6: "fd69:6684:61a:3::/64"
```

#### 生成されるゾーン定義 (named.conf.zones)

```bind
// === 複数ネットワーク逆引きゾーン ===
zone "30.168.192.in-addr.arpa" IN {
        type    master;
        file    "/var/lib/bind/db.30.168.192";
        update-policy {
                grant ddns-clients zonesub ANY PTR;
        };
};

zone "2.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f.ip6.arpa" IN {
        type    master;
        file    "/var/lib/bind/db.2.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f";
        update-policy {
                grant ddns-clients zonesub ANY PTR;
        };
};

// ... (ネットワーク2, 3 も同様)
```

#### 生成されるゾーンファイル

ファイル `/var/lib/bind/db.30.168.192` (IPv4 逆引きゾーン例):

```dns
$TTL 86400
@       IN      SOA     mgmt-server.elliptic-curve.net. root.elliptic-curve.net. (
        202601201200 ;Serial
        3600            ;Refresh
        1800            ;Retry
        604800          ;Expire
        86400           ;Minimum TTL
)

       IN      NS       mgmt-server.elliptic-curve.net.

; === 動的 DNS (nsupdate) レコード登録ゾーン ===
; 以下のネットワークアドレス範囲の逆引きレコード(PTR)は
; nsupdateで動的に登録してください。
;
; 登録対象ネットワーク: 192.168.30.0/24
;
; 登録例:
; nsupdate -k /etc/bind/ddns.key
; > server 192.168.30.1
; > zone 30.168.192.in-addr.arpa.
; > update add 100.30.168.192.in-addr.arpa 3600 PTR hostname.example.com.
; > send
;
```

### クライアント側の nsupdate 使用例

```bash
#!/bin/bash
# クライアント側で動的に PTR を登録

DNS_SERVER="192.168.30.1"
REVERSE_ZONE="30.168.192.in-addr.arpa"
DDNS_KEY="/etc/bind/ddns.key"
HOSTNAME="client01.example.com"
IPADDR="192.168.30.100"
TTL=3600

# IPv4 逆引きレコード登録
nsupdate -k "$DDNS_KEY" <<EOF
server $DNS_SERVER
zone $REVERSE_ZONE
update add ${IPADDR##*.}.${IPADDR%.*} $TTL PTR $HOSTNAME.
send
EOF

# IPv6 の場合（例）
# IPv6 PTR の計算: fd69:6684:61a:2::100 → 0.0.1.0.0.0.0.0.0.0.0.0.2.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f.ip6.arpa
```

### カスタムフィルターの詳細

#### `ipv4_reverse_zone` フィルター

IPv4 CIDR ネットワークを逆引きゾーン名に変換します。

| 入力 | 出力 | 用途 |
|------|------|------|
| `192.168.30.0/24` | `30.168.192` | zone "30.168.192.in-addr.arpa" |
| `192.168.0.0/16` | `168.192` | zone "168.192.in-addr.arpa" |
| `10.0.0.0/8` | `10` | zone "10.in-addr.arpa" |
| `192.168.30.128/25` | `30.168.192` | /24 未満は最初の 3 オクテット |

**エラーハンドリ**: CIDR 形式不正（例：`192.168.30` など）の場合、AnsibleFilterError 例外を発生させ、タスク失敗となります。

#### `ipv6_reverse_zone` フィルター

IPv6 プレフィクスとプレフィクス長を逆引きゾーン名（ニブル形式）に変換します。

| 入力 | 出力 | 用途 |
|------|------|------|
| `fd69:6684:61a:2::/64` | `2.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f` | zone "2.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f.ip6.arpa" |
| `fd69:6684:61a:3::/64` | `3.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f` | zone "3.0.0.0.a.1.6.0.4.8.6.6.9.6.d.f.ip6.arpa" |
| `2001:db8::/32` | `8.b.d.0.1.0.0.2` | zone "8.b.d.0.1.0.0.2.ip6.arpa" |

**エラーハンドリング**:
- IPv6 形式不正（例：`gggg::`）→ AnsibleFilterError
- プレフィクス長が 0-128 範囲外 → AnsibleFilterError

### 注意事項

1. **CIDR 形式必須**: `ipv4` キーは必ず CIDR ノーテーション（プレフィクス長付き）で指定してください。例：`"192.168.30.0/24"`

2. **重複定義回避**: 同一ネットワークを `internal_network_list` 内で重複定義しないでください。
   - **問題**: リスト内で同一ネットワーク CIDR が複数回現れると、ループで複数の同一ゾーンファイルが生成され、`named.conf.zones` に同じゾーン定義が複数記載されます。

3. **プレフィクス長の妥当性**:
   - IPv4: `/8` ～ `/32` 推奨（その他は動作しますが、逆引きゾーン規模に注意）
   - IPv6: `/48` ～ `/128` 推奨

4. **既存ネットワークとの分離**: `dns_ipv4_reverse` と `internal_network_list` の IPv4 ネットワークは重複させないでください。
   - **重複時の問題**:
     - `named-checkconf -z` でゾーン定義の重複エラーが発生：`zone "...".*arpa" already defined`
     - named サービスが起動失敗し、DNS 機能が利用不可
     - Ansible タスク実行時に `named_check_conf` ハンドラでエラー検出（RHEL 系）
     - クライアント側の nsupdate で PTR 登録時に、どちらのゾーンに登録すべきか不明になり、レコード登録失敗のリスク

   **対策**:
   - `dns_ipv4_reverse` で定義したネットワーク（例：`192.168.20.0/24` → `dns_ipv4_reverse: "20.168.192"`）と `internal_network_list` の IPv4 ネットワークを完全に分離してください。
   - 例：既に `192.168.20.0/24` が単一ネットワーク定義の場合、`internal_network_list` には `192.168.30.0/24`, `192.168.40.0/24` など別のネットワークのみ定義します。
   - 確認コマンド：`named-checkconf -z` が実行時にエラー無しで完了すれば、ゾーン定義重複がないことを保証します。

5. **`bind_serial` の更新**: テンプレート生成時に シリアルが自動更新されるため, 複数回実行しても問題ありません。

テンプレートは `templates/` 配下にあり, 環境に合わせて `named.conf.*` や `db.*` を生成します。特に `named.conf.zones.j2` では `grant ddns-clients zonesub` によりサブゾーン単位の Dynamic DNS を許可します。`bind_serial` を事前に指定すると SOA シリアルを固定できます。

## 実行方法

```bash
ansible-playbook -i inventory/hosts server.yml --tags dns-server
```

対象プレイブックでこのロールが含まれていればタグ省略でも適用されます。Zone 更新のみ再適用したい場合は `--tags dns-server -l <hostname>` で対象ホストを絞り, 必要に応じて `--skip-tags config-firewall` などを併用してください。

## 検証ポイント

- `named-checkconf -z` がエラー無しで完了し, `rndc status` が `server is up and running` を返す。
- `/etc/bind` または `/etc/named` 配下に `named.conf.*` と `db.*` が展開され, 所有者が `dns_bind_user:dns_bind_group` に設定されている。
- `systemctl get-default` が `multi-user.target` に切り替わっている (GUI を維持したい場合は `disable_gui` 通知を抑制してください)。
- RHEL 系で SELinux を有効にしている場合, `semanage fcontext -l | grep {{ dns_bind_selinux_target }}` に新規ルールが登録され, `restorecon -Rv /var/named` 実行時にコンテキストが期待通り変更される。
- `dig @<dns_server_ipv4_address> <host>.{{ dns_domain }}` で期待する A/PTR レコードが参照でき, Dynamic DNS クライアントからの更新が TSIG で許可される。
- Firewall を有効化した場合, `firewall-cmd --list-services` または `ufw status` に DNS ポートが追加されている。

## 運用メモ

- TSIG シークレット (`dns_ddns_key_secret`) はバージョン管理外に保管してください。
- IPv6 で外部と到達できない検証環境だけで `dns_bind_ipv4_only: true` に設定し, `templates/90-override.conf.j2` が生成する systemd の追加設定ファイルで `ExecStart` に `-4` を付与して IPv4 のみに限定します。IPv6 を提供したい場合はデフォルトの false のままにしてください。
- ゾーンファイルはテンプレート生成のため, 手動編集ではなく `dns_host_list` や関連変数を更新してロールを再実行する運用を前提としています。
- Dynamic DNS クライアントスクリプト (`roles/common/templates/ddns-client-update.sh.j2` 等) と組み合わせる場合, FQDN 末尾のドットやゾーン名の整合性に注意してください。
