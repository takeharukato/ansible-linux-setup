# docker-ce ロール

このロールは Docker Community Edition (Docker CE) のインストール, サービス初期化, ブリッジネットワークの sysctl 調整, 利用ユーザのグループ設定, およびコンテナボリュームのバックアップ環境を一括で整備します。Debian 系と RHEL 系の差異は `ansible_facts.os_family` を基準に変数を切り替えることで吸収しており, ロール単体での再実行にも耐えられる構成です。

## 主な処理

- `tasks/load-params.yml` で OS ファミリー別パッケージ (`vars/packages-ubuntu.yml` / `vars/packages-rhel.yml`) と共通変数 (`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込み, パッケージ一覧やバックアップ先, ユーザ設定を初期化します。
- `tasks/package.yml` が以下を順番に行います。
  - 旧来の Docker / containerd 関連パッケージ (`docker_ce_remove_packages`) を削除します。
  - HTTPS (Hypertext Transfer Protocol Secure) リポジトリ利用に必要な前提パッケージ (`docker_ce_prereq_packages`) を導入します。
  - 公式リポジトリから Docker CE 本体 (`docker_ce_packages`) を最新化し, 変更があれば `docker_restarted` ハンドラを通知します。
- `tasks/service.yml` では `templates/docker-bridge.conf.j2` を `/etc/modules-load.d/99-docker-bridge.conf` に配置し, `net.bridge.bridge-nf-call-*`, IPv4/IPv6フォワーディング (`net.ipv4.ip_forward`, `net.ipv6.conf.all.forwarding`, `net.ipv6.conf.default.forwarding`), 管理IFのRA (Router Advertisement, ルータ広告) 受信 (`net.ipv6.conf.<mgmt_nic>.accept_ra`), `rp_filter` を調整します。配置時は `apply_sysctl` ハンドラを通知しつつ, 即時に `sysctl --system` を実行して値を反映します。続けて `docker` サービスを `state: restarted` かつ `enabled: true` で起動します。
- `tasks/directory.yml` がバックアップ用のスクリプトと Dockerfile を展開します。
  - `/usr/local/bin` と `/usr/local/share/docker-backup` を作成し, `backup-containers` / `restore-container` スクリプト, `Dockerfile.j2`, `backup.sh.j2` を配置します。
  - 最後に `docker build -t "{{ docker_ce_backup_container_image_name }}" .` を実行して boombatower/docker-backup ベースの独自バックアップイメージを構築します。`docker` サービスを先に起動する理由はこのビルド処理に依存するためです。
- `tasks/user_group.yml` は `docker` グループの存在を保証し, `ansible` ユーザ, `docker_ce_users`, および `users_list` に列挙されたアカウントを順次追加します。
- `tasks/config.yml` は将来の拡張用プレースホルダーです。追加設定が必要になった際にここへ追記します。
- ハンドラは `handlers/docker.yml` (`docker_restarted`) と `handlers/sysctl.yml` (`apply_sysctl`) を提供し, サービス再起動と `sysctl --system` の再適用を担います。

## バックアップ関連の流れ

`templates/backup-containers.j2` は `/usr/local/bin/backup-containers` として展開され, 日次ジョブを想定して全コンテナのボリュームを boombatower/docker-backup 等のバックアップ用ユーティリティコンテナでアーカイブし, `tar.xz` としてバックアップストレージへ退避します。

1. `nc_command` で `docker_ce_backup_nfs_server` への NFS (Network File System) ポート疎通を確認します。
2. `docker_ce_backup_nfs_dir` を `docker_ce_backup_mount_point` へマウントし, 年間通算日 (`date +%j`) を `docker_ce_backup_rotation` で割った余りを世代番号として算出します。
3. 稼働中コンテナを列挙し, コンテナ毎に `{{ docker_ce_backup_output_dir }}/<コンテナ名>/<コンテナ名>-<世代>.tar.xz` を生成します。
4. パーミッションを緩和 (`chmod -R o+rwX`) した後, NFS をアンマウントします。

復旧は `/usr/local/bin/restore-container` が担い, 停止中コンテナとアーカイブを指定して `docker run --rm --volumes-from ... backup_image restore <archive>` を実行します。どちらのスクリプトもビルド済み `{{ docker_ce_backup_container_image }}` を利用します。

## 利用する主な変数

| 変数名 | 定義場所 (初期値) | 用途 |
| ------ | ----------------- | ---- |
| `docker_ce_remove_packages` | `vars/cross-distro.yml` | 旧 Docker / containerd 系パッケージの削除対象一覧。|
| `docker_ce_prereq_packages` | `vars/cross-distro.yml` | リポジトリ利用に必要な前提パッケージ。|
| `docker_ce_packages` | `vars/cross-distro.yml` | インストールする Docker CE コンポーネント (buildx / compose plugin を含む)。|
| `docker_ce_users` | `vars/all-config.yml` | `docker` グループへ追加する利用者一覧。|
| `users_list` | 他ロールとの共有変数 | 追加で `docker` グループに所属させるユーザ。空なら処理をスキップ。|
| `docker_ce_backup_rotation` | `defaults/main.yml` | バックアップ世代数 (cron で日次実行を前提としたリングバッファ)。|
| `docker_ce_backup_nfs_server` / `docker_ce_backup_nfs_dir` / `docker_ce_backup_mount_point` | `vars/all-config.yml` | バックアップ格納用の NFS サーバ, エクスポート, マウントポイント。|
| `docker_ce_backup_dir_on_nfs` | `vars/all-config.yml` | マウントポイント配下でアーカイブを保存する相対パス。|
| `docker_ce_backup_container_image_name` | `defaults/main.yml` | 自前でビルドするバックアップ用コンテナイメージ名。|
| `nc_command` | `vars/cross-distro.yml` | NFS 疎通確認に利用する netcat コマンド名。|
|`build_docker_ce_backup_container_image`|`roles/docker-ce/defaults/main.yml`|バックアップ用コンテナイメージを作成しない場合は, `false` を設定する(規定値は, `true`)。|

必要に応じて `group_vars` / `host_vars` で上記変数を上書きし, ロールの挙動を調整します。

## 実行方法

```bash
ansible-playbook -i inventory/hosts server.yml --tags docker-ce
```

Docker を再設定したいホストを限定する場合は `-l <hostname>` を併用してください。`--tags docker-ce` を省略しても該当プレイブックでロールが含まれている場合は自動適用されます。

## 検証ポイント

- `docker --version` および `docker info` がエラーなく実行でき, `Server Version` が期待通りになっている。
- `/etc/modules-load.d/99-docker-bridge.conf` が配備され, `sysctl net.bridge.bridge-nf-call-iptables`, `sysctl net.ipv4.ip_forward`, `sysctl net.ipv6.conf.all.forwarding` などが `1` に設定されている。
- `systemctl is-enabled docker` と `systemctl is-active docker` がいずれも `enabled` / `active` を返す。
- `getent group docker` に `docker_ce_users` や `users_list` のユーザが含まれている。
- `/usr/local/share/docker-backup/` に `Dockerfile` と `backup.sh` があり, `docker images` に `{{ docker_ce_backup_container_image }}` が存在する。
- バックアップスクリプトを実行すると NFS がマウントされ, `{{ docker_ce_backup_output_dir }}` 配下に `<コンテナ名>-<世代>.tar.xz` が生成される。

## 留意事項

- NFS (Network File System) バックアップはネットワーク到達性に依存するため, `nc_command` が失敗した際のリトライや監視を別途検討してください。
- `backup-containers` は稼働中コンテナをそのまま対象にするため, 一貫性が必要なアプリケーションは停止手順を組み合わせるか, エクスポート対象がボリュームのみで安全に取得できる構成かを確認してください。
- Docker CE バージョン固定が必要な場合は `docker_ce_packages` をピン留めするか, 上位で APT (Advanced Package Tool) / YUM (Yellowdog Updater Modified) のバージョンロックを設定してください。
- `templates/docker-bridge.conf.j2` は IPv4/IPv6 フォワーディングを有効化し, 管理インターフェースで RA (Router Advertisement, ルータ広告) を受け入れる設定を含みます。また, `rp_filter` を無効化します。セキュリティポリシー上問題となる環境では値を見直し, 必要に応じてテンプレートを修正してください。
- router-config ロールで設定されるiptablesルールを阻害しないようにDockerのiptables管理を無効化するように設定しています。セキュリティポリシー上問題となる環境では値を見直し, 必要に応じてテンプレートを修正してください。
