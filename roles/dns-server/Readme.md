# dns-server ロール

このロールは BIND を用いた権威兼キャッシュ DNS サーバーを構成します。対象 OS のファクトに応じて Debian 系と RHEL 系の差異を吸収し, ゾーンファイルと `named.conf`/`named.conf.options` をテンプレートで生成します。Dynamic DNS 更新用の TSIG キーを組み込み, IPv4/IPv6 双方の順引き・逆引きゾーンを作成し, 必要に応じて systemd・SELinux・Firewall の周辺設定も行います。

## 主な処理

- `tasks/load-params.yml` で OS ファミリー別パッケージ (`vars/packages-ubuntu.yml` / `vars/packages-rhel.yml`) と `vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml` を読み込み, ドメインやネットワーク関連変数を構成します。
- `tasks/package.yml` が `dns_bind_packages` を最新化し, 変更があれば `disable_gui` ハンドラ ( `systemctl set-default multi-user.target` )を通知します。
- `tasks/config.yml` が以下を順に実施します。
  - 設定・ゾーン格納ディレクトリを所定の所有者とパーミッションで作成。
  - RHEL 系では既存の `named.conf` をバックアップしたうえで `rhel-named.conf.j2` を適用し, Debian 系では `lineinfile` でゾーン include のみ挿入します。
  - OS ごとの `named.conf.options` テンプレートを配置し, フォワーダー (`dns_bind_forwarders`) や ACL (`dns_network` / `dns_network_ipv6_prefix`) を反映します。
  - `named.conf.zones.j2` と各ゾーンテンプレートを展開し, `dns_host_list`・`bind_serial` から順引き/逆引きレコードを生成します。`bind_serial` が未指定なら日付ベースで設定します。
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
