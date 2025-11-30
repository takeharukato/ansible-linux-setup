# ntp-server ロール

このロールは chrony を用いた NTP サーバーを構成し, 外部上位サーバーとの同期と LAN 内クライアントへの時刻配信を管理します。OS ファクト (`ansible_facts.os_family`) を基に Debian 系と Red Hat 系の差異を吸収し, 再実行可能な設計になっています。

## 主な処理

- `tasks/load-params.yml` で OS 別変数 (`vars/packages-ubuntu.yml` / `vars/packages-rhel.yml`) と共通設定 (`vars/cross-distro.yml` / `vars/all-config.yml` / `vars/k8s-api-address.yml`) を読み込み, `external_ntp_servers_list` や `ntp_allow`, サービス名 (`ntp_server_chrony_service`) などを初期化します。
- `tasks/package.yml` が chrony (`ntp_server_packages`) を最新化し, 変更があれば GUI 無効化ハンドラ `disable_gui` を通知します (サーバをマルチユーザターゲットに固定するため)。
- `tasks/directory.yml` は drop-in 用ディレクトリ (`ntp_server_chrony_conf_drop_in_dir`, Debian: `/etc/chrony/chrony.d`, RHEL: `/etc/chrony.d`) を作成します。
- `tasks/config.yml` が `templates/99-ntp-servers.conf.j2` を同ディレクトリへ配置し, 以下を設定します。
  - `external_ntp_servers_list` に列挙された上位 NTP を `pool ... iburst` 形式で登録。
  - `ntp_allow` で指定された CIDR からのアクセスを許可 (`allow` ディレクティブ)。
  - 配置後は `restart_chrony` ハンドラを通知します。
- ハンドラ (`handlers/restart-chrony.yml`) は `systemd` モジュールで chrony サービスを再起動・有効化します。

## 変数一覧

- `external_ntp_servers_list`: 上位 NTP サーバーリスト。空の場合はテンプレート内ループがスキップされます。`vars/all-config.yml` やホスト変数で指定。
- `ntp_allow`: Chrony の `allow` に渡す CIDR。既定は `{{ network_ipv4_network_address }}/{{ network_ipv4_prefix_len }}`。
- `ntp_server_chrony_service`: OS ごとの chrony サービス名 (`chrony` or `chronyd`)。`vars/cross-distro.yml` で定義。
- `ntp_server_chrony_conf_drop_in_dir`: drop-in 配置ディレクトリ。Debian 系 `/etc/chrony/chrony.d`, RHEL 系 `/etc/chrony.d`。
- `ntp_server_packages`: chrony のパッケージ名リスト。Debian/RHEL の差異を `vars/cross-distro.yml` で吸収。
- `validate_packages_apt`: (Debian 系) リポジトリ整合性検証に使用されるパッケージ集合。`handlers/main.yml` で利用。

## 実行方法

```bash
ansible-playbook -i inventory/hosts server.yml --tags ntp-server
```

対象ホストを限定する場合は `-l <hostname>` を併用してください。chrony 再起動が発生するため, メンテナンス時間内での実行を推奨します。

## 検証ポイント

- `systemctl is-active {{ ntp_server_chrony_service }}` が `active` を返し, `systemctl is-enabled ...` が `enabled` になっている。
- `/etc/chrony/chrony.d/99-ntp-servers.conf` (または RHEL の `/etc/chrony.d/`) に上位サーバーと `allow` セクションが出力されている。
- `chronyc sources -v` で外部サーバーに同期し, `chronyc sourcestats` で統計が取得できる。
- クライアント側から `chronyc ntpdata` もしくは `ntpq -p <ntp-server>` などで応答を確認し, `ntp_allow` で許可した範囲外からのアクセスは拒否される。
- 変更後に `journalctl -u {{ ntp_server_chrony_service }}` を確認し, 設定エラーが出ていない。

## 運用メモ

- 外部 NTP サーバーが複数ある場合は `external_ntp_servers_list` に複数エントリを追加し, テンプレートで重複を自動除去します。
- `allow` で指定する範囲は最小限に留め, 不要なネットワークからのアクセスを防止してください。IPv6 を併用する場合は追記事項の検討が必要です。
- GUI を無効化したくない環境では `disable_gui` ハンドラを通知しないよう上位ロールで制御するか, `notify` を条件付きに変更してください。
- Chrony のパフォーマンスや偏差が問題になる場合, `makestep` や `local stratum` など追加パラメータを drop-in テンプレートに拡張する運用が可能です。
