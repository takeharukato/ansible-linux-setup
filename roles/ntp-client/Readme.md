# ntp-client ロール

このロールは Debian 系・Red Hat 系ホストにおける NTP クライアント設定を再現性高く適用します。`ntp_client_choice` で `systemd-timesyncd` と `chrony` を切り替えられるようにしつつ, `ansible_facts.os_family` に応じてパスやサービス名の差異を `vars/cross-distro.yml` で吸収する設計です。`ntp_servers_list` へ列挙した上位サーバーをテンプレート処理で正規化し, 冪等に展開します。

## 主な処理

- `tasks/load-params.yml` が OS 別パッケージ定義 (`vars/packages-ubuntu.yml` / `vars/packages-rhel.yml`) と共通変数 (`vars/cross-distro.yml` / `vars/all-config.yml` / `vars/k8s-api-address.yml`) を読み込み, サービス名や設定ファイルパス, `ntp_servers_list` などの実行パラメーターを初期化します。
- `tasks/package.yml` が `ntp_client_packages` を `package` モジュールで導入し, `chrony` または `systemd-timesyncd` を確実にインストールします。
- `tasks/config.yml` では `service_facts` を取得したうえで, 選択した実装に応じた設定を適用します。
  - `ntp_client_is_systemd_timesyncd` の場合, `templates/99-timesyncd.conf.j2` を `ntp_client_systemd_timesyncd_conf_path` (`/etc/systemd/timesyncd.conf.d/99-timesyncd.conf`) に配置し, `systemd-timesyncd` を有効化しつつ `chrony` を無効化します。
  - `ntp_client_is_chrony` の場合, `ntp_client_chrony_conf_drop_in_dir` (Debian: `/etc/chrony/chrony.d`, RHEL: `/etc/chrony.d`) を確保し, `lineinfile` で `chrony.conf` に `confdir` 行を追記してから `templates/99-chrony.conf.j2` を `ntp_client_chrony_conf_drop_in_path` に展開, `systemd-timesyncd` を無効化します。
- `tasks/directory.yml` が `/etc/systemd/timesyncd.conf.d` を作成し, `systemd-timesyncd` 用 drop-in 配置先を事前に準備します。
- ハンドラ (`handlers/restart-timesyncd.yml` / `handlers/restart-chrony.yml`) が該当サービスを再起動・有効化し, 設定差分の反映を保証します。

## 変数一覧

- `ntp_servers_list`: 上位 NTP サーバーの候補。空要素や重複はテンプレート側で除去されます。`roles/ntp-client/defaults/main.yml` で空配列, `vars/all-config.yml` で実値を定義。
- `ntp_client_choice`: 使用する実装 (`systemd-timesyncd` / `chrony`)。既定値は `chrony` (`vars/cross-distro.yml`)。
- `ntp_client_is_chrony` / `ntp_client_is_systemd_timesyncd`: 上記選択肢を判定するブール値。条件付きタスクやハンドラで利用。
- `ntp_client_packages`: 導入するパッケージ集合。Debian 系は選択肢に応じて `chrony` または `systemd-timesyncd` を選択し, RHEL 系は `chrony` 固定。
- `ntp_client_chrony_conf_path` / `ntp_client_chrony_conf_drop_in_dir` / `ntp_client_chrony_conf_drop_in_path`: chrony の設定ファイルと drop-in の展開先を示すパス。`lineinfile` やテンプレート展開で参照。
- `ntp_client_systemd_timesyncd_conf_path` / `ntp_client_systemd_timesyncd_service`: `systemd-timesyncd` の設定ファイルとサービス名。Debian 系のみに適用。

## 実行方法

```bash
ansible-playbook -i inventory/hosts basic.yml --tags ntp-client
```

他のプレイブック (`devel.yml` / `k8s-ctrl-plane.yml` / `k8s-worker.yml` / `rancher.yml`) でも同タグで再利用できます。特定ホストに限定する場合は `-l <hostname>` を併用してください。

## 検証ポイント

- `timedatectl show-timesync --all` で `SystemNTPServers=` に `ntp_servers_list` が反映され, `service` が `systemd-timesyncd` になっている (timesyncd 選択時)。
- `chronyc tracking` / `chronyc sources -v` が成功し, `sources` に `ntp_servers_list` のホストが列挙される (chrony 選択時)。
- `/etc/systemd/timesyncd.conf.d/99-timesyncd.conf` または `{{ ntp_client_chrony_conf_drop_in_path }}` が Ansible 実行直後のタイムスタンプで更新され, テンプレートのコメントに記録された `last update` が現在時刻になっている。
- `systemctl is-enabled systemd-timesyncd` と `systemctl is-enabled {{ ntp_client_chrony_service }}` の片方のみが `enabled` になっている (選択肢に応じた相互排他制御が効いている)。
- `journalctl -u systemd-timesyncd` または `journalctl -u {{ ntp_client_chrony_service }}` に設定エラーが出ていない。

## 運用メモ

- `ntp_client_choice` を切り替えるだけで chrony と systemd-timesyncd のどちらにも移行できるため, メンテナンス前にサービス再起動の影響範囲を把握してください。
- 追加の chrony 設定 (例: `makestep` パラメーターの変更や `allow` 追加) は `templates/99-chrony.conf.j2` を編集するか, 別 drop-in を上位ロールで投入して拡張できます。
- NTP サーバー候補は IPv4/IPv6 を混在させても問題ありません。テンプレート処理で空行や重複が除去されます。
- 大規模環境で上位 NTP へのアクセス制御が必要な場合は, ファイアウォール (例: `firewalld` / `ufw`) と組み合わせた運用を検討してください。
