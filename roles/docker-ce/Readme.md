# docker-ce ロール

Docker Community Edition (Docker CE) を導入し, サービス初期化, sysctl の調整, 利用ユーザのグループ設定, およびコンテナボリュームのバックアップ環境を一括で整備するロールです。Debian 系と RHEL 系の差異は `ansible_facts.os_family` を基準に変数を切り替えることで吸収しています。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Docker Community Edition | Docker CE | Docker のコミュニティ版。Docker Engine と関連ツールで構成される。 |
| Docker Engine | - | コンテナの実行基盤。 `dockerd` とその API を含む。 |
| containerd | - | Docker が利用するコンテナランタイム。 |
| Network File System | NFS | ネットワーク越しにファイル共有を行う仕組み。 |
| Hypertext Transfer Protocol Secure | HTTPS | 暗号化された HTTP 通信。リポジトリ取得に使用。 |
| Router Advertisement | RA | IPv6 でルータ情報を通知する仕組み。 |
| Reverse Path Filtering | rp_filter | 逆引きパスフィルタリングの設定。 |
| sysctl | - | Linux カーネルパラメータを設定する仕組み。 |
| netcat | nc | ネットワーク到達性を確認するコマンド。RHEL 系では `ncat` を使用。 |

## 前提条件

- 対象 OS: Debian/Ubuntu 系 (Ubuntu24.04想定), RHEL 9 系 (Rocky Linux, AlmaLinux 等) (AlmaLinux9.6想定)
- Ansible 2.15 以降
- リモートホストへの SSH 接続が確立されていること
- `sudo` による管理者権限でのコマンド実行が可能であること
- Docker CE 公式リポジトリが設定済みであること (site.yml の実行時に repo-deb ロール(Debian系)または repo-rpm ロール(RHEL系)で設定される)
- netcat コマンドが利用可能であること (Debian 系: `nc`, RHEL 系: `ncat`)
- NFS クライアント機能が利用可能であること (バックアップを使用する場合)

## 実行方法

### make ターゲット

```bash
make run_docker_ce
```

### ansible-playbook

```bash
ansible-playbook -i inventory/hosts site.yml --tags docker-ce
```

対象ホストを限定する場合は `-l <hostname>` を併用してください。

## 実行フロー

本ロールは以下の順序で処理を実行します:

1. **パラメータ読み込み** (`load-params.yml`): OS 別パッケージ定義と共通変数を読み込みます。
2. **パッケージ操作** (`package.yml`): 旧パッケージ削除, 前提パッケージ導入, Docker CE パッケージ導入を行います。
3. **サービス設定** (`service.yml`): sysctl 設定ファイルを配置し, `sysctl --system` を実行後に docker サービスを再起動します。
4. **ディレクトリ作成** (`directory.yml`): `/usr/local/bin` と `/usr/local/share` を作成します。
5. **バックアップ用ファイル配置とイメージ作成** (`docker-backup-image.yml`): `build_docker_ce_backup_container_image` が `true` の場合のみ, バックアップ・復旧スクリプトと Dockerfile を配置します。`docker_ce_enable_backup_script` が有効な場合, restore-container.j2, Dockerfile.j2, backup.sh.j2 を配置し, さらに `docker_ce_backup_nfs_server` と `docker_ce_backup_nfs_dir` が非空の場合にのみ backup-containers.j2 を配置します。その後, バックアップ用イメージをビルドします。
6. **ユーザとグループ設定** (`user_group.yml`): docker グループを作成し, `ansible_user`, `docker_ce_users`, `users_list` のユーザを追加します。
7. **Docker 設定** (`config.yml`): `/etc/docker/daemon.json` を作成し, iptables 管理の無効化などを設定します。

## 主要変数

### ロール固有変数 (defaults/main.yml)

| 変数名 | 既定値 | 定義場所 | 説明 |
| --- | --- | --- | --- |
| `docker_ce_log_driver` | `"json-file"` | defaults/main.yml | Docker ログドライバ。 |
| `docker_ce_log_opts` | `{max-size: "10m", max-file: "3"}` | defaults/main.yml | ログローテーション設定。 |
| `docker_ce_users` | `[]` | defaults/main.yml | docker グループへ追加する利用者一覧。 `host_vars`や`vars/all-config.yml`で定義されることを想定し, 本ロールでは, 空リストで規定値を定義している。|
| `docker_ce_backup_rotation` | `"5"` | defaults/main.yml | バックアップ世代数。 |
| `docker_ce_backup_nfs_server` | `""` | defaults/main.yml | NFS サーバー名。 `host_vars`や`vars/all-config.yml`で定義されることを想定し, 本ロールでは, 空文字列で規定値を定義している。|
| `docker_ce_backup_mount_point` | `"/mnt"` | defaults/main.yml | NFS マウントポイント。 |
| `docker_ce_backup_nfs_dir` | `"/share"` | defaults/main.yml | NFS 側の共有ディレクトリ。 |
| `docker_ce_backup_dir_on_nfs` | `"/containers/docker-ce/daily-backup"` | defaults/main.yml | NFS マウントポイント配下の保存ディレクトリ。 |
| `docker_ce_backup_output_dir` | `"/mnt/containers/docker-ce/daily-backup"` | defaults/main.yml | バックアップ出力先。 |
| `docker_ce_backup_container_image_name` | `"local-boombatower-docker-backup"` | defaults/main.yml | バックアップ用コンテナイメージ名。 |
| `docker_ce_backup_container_image` | `"local-boombatower-docker-backup:latest"` | defaults/main.yml | バックアップ用コンテナイメージ。 |
| `docker_ce_backup_dockerfile_dir` | `"/usr/local/share/docker-backup"` | defaults/main.yml | Dockerfile 配置先。 |
| `users_list` | `[]` | defaults/main.yml | 追加で docker グループへ所属させるユーザ定義。`host_vars`や`vars/all-config.yml`で定義されることを想定し, 本ロールでは, 空リストで規定値を定義している。 |
| `build_docker_ce_backup_container_image` | `false` | defaults/main.yml | バックアップ用コンテナイメージを作成する場合は `true`。 |
| `docker_ce_enable_backup_script` | `false` | defaults/main.yml | バックアップスクリプト生成有効化フラグ。`docker_ce_enable_backup_script` が `true` の場合, restore-container.j2, Dockerfile.j2, backup.sh.j2 が配置されます。さらに `docker_ce_backup_nfs_server` と `docker_ce_backup_nfs_dir` が非空の場合にのみ, backup-containers.j2 が配置されます。不要な環境では `false` に設定するとテンプレート生成をスキップできます。 |

### その他

| 変数名 | 既定値 | 定義場所 | 説明 |
| --- | --- | --- | --- |
| `ansible_user` | inventory で指定 | inventory/hosts | Docker グループへ追加する接続ユーザ。 |

## デフォルト動作

- `build_docker_ce_backup_container_image: false` のため, バックアップ/復旧スクリプトとバックアップ用イメージは既定では作成されません。
- `docker` サービスは `enabled: true`, `state: restarted` で起動します。
- `/etc/docker/daemon.json` は iptables 管理の無効化と IPv6 有効化を含む設定で生成されます。
- `docker_ce_backup_output_dir` は `docker_ce_backup_mount_point` と `docker_ce_backup_dir_on_nfs` の結合値になります。既定では `/mnt/containers/docker-ce/daily-backup` です。
- sysctl は `/etc/modules-load.d/99-docker-bridge.conf` を通じて反映されます。設定内容には `net.bridge.bridge-nf-call-iptables`, `net.bridge.bridge-nf-call-ip6tables`, `net.ipv4.ip_forward`, `net.ipv6.conf.all.forwarding`, `net.ipv6.conf.default.forwarding`, `net.ipv6.bindv6only`, `net.ipv6.conf.<mgmt_nic>.accept_ra`, `net.ipv4.conf.*.rp_filter` が含まれます。

## テンプレート・ファイル

本ロールでは以下のテンプレート/ファイルを出力します:

| テンプレート/ファイル | 出力先パス | 条件 | 説明 |
| --- | --- | --- | --- |
| `docker-bridge.conf.j2` | `/etc/modules-load.d/99-docker-bridge.conf` | 常に実行 | Docker ブリッジ関連の sysctl 設定。 |
| `backup-containers.j2` | `/usr/local/bin/backup-containers` | `build_docker_ce_backup_container_image: true` かつ `docker_ce_enable_backup_script: true` かつ `docker_ce_backup_nfs_server` と `docker_ce_backup_nfs_dir` が非空 | コンテナバックアップスクリプト。 |
| `restore-container.j2` | `/usr/local/bin/restore-container` | `build_docker_ce_backup_container_image: true` かつ `docker_ce_enable_backup_script: true` | コンテナ復旧スクリプト。 |
| `Dockerfile.j2` | `/usr/local/share/docker-backup/Dockerfile` | `build_docker_ce_backup_container_image: true` かつ `docker_ce_enable_backup_script: true` | `opensuse/leap:15.6` をベースに boombatower/docker-backup 互換のイメージを作成。 |
| `backup.sh.j2` | `/usr/local/share/docker-backup/backup.sh` | `build_docker_ce_backup_container_image: true` かつ `docker_ce_enable_backup_script: true` | バックアップ用イメージのエントリスクリプト。 |
| `/etc/docker/daemon.json` | `/etc/docker/daemon.json` | 常に実行 | Docker の動作設定ファイル。 |

## OS 差異

| 項目 | Debian 系 | RHEL 系 | 備考 |
| --- | --- | --- | --- |
| 旧パッケージ削除対象 | `docker.io` など | `docker` など | `docker_ce_remove_packages` により異なる。 |
| 前提パッケージ | `apt-transport-https`, `gnupg` など | `gnupg2` など | `docker_ce_prereq_packages` により異なる。 |
| netcat コマンド | `nc` | `ncat` | NFS 疎通確認に使用。 |

## 設定例

### 基本設定

`group_vars/all/all.yml` または `host_vars/<hostname>/main.yml`:

```yaml
docker_ce_users:
  - user1
```

### Docker ログ設定

`group_vars/all/all.yml`:

```yaml
docker_ce_log_driver: "json-file"
docker_ce_log_opts:
  max-size: "50m"
  max-file: "5"
```

### バックアップ設定

`group_vars/all/all.yml` または `host_vars/<hostname>/main.yml`:

```yaml
docker_ce_backup_nfs_server: "nfs.example.org"
docker_ce_backup_nfs_dir: "/share"
docker_ce_backup_mount_point: "/mnt"
docker_ce_backup_dir_on_nfs: "/Linux/containers"
```

`host_vars/<hostname>/main.yml`:

```yaml
build_docker_ce_backup_container_image: true
```

## バックアップ/復旧フロー

### backup-containers の流れ

1. `nc_command` で `docker_ce_backup_nfs_server` への NFS ポート疎通を確認します。
2. `docker_ce_backup_nfs_dir` を `docker_ce_backup_mount_point` へマウントし, 年間通算日 (`date +%j`) を `docker_ce_backup_rotation` で割った余りを世代番号として算出します。
3. 稼働中コンテナを列挙し, `{{ docker_ce_backup_output_dir }}/<コンテナ名>/<コンテナ名>-<世代>.tar.xz` を生成します。
4. パーミッションを緩和 (`chmod -R o+rwX`) した後, NFS をアンマウントします。

バックアップは boombatower/docker-backup と互換のコンテナイメージを利用します。

### restore-container の流れ

1. 対象コンテナが停止していることを確認します。
2. アーカイブファイルを指定し, `docker run --rm --volumes-from ... restore <archive>` で復旧します。

## 検証ポイント

### 前提条件

- Docker CE リポジトリが設定済みであること
- `build_docker_ce_backup_container_image: true` の場合は NFS が到達可能であること

### 手順1: Docker バージョン確認

```bash
docker --version
```

**期待出力**:

```plaintext
Docker version 26.x.x, build ...
```

**確認ポイント**:

- Docker のバージョンが表示されること

### 手順2: Docker サービス状態

```bash
systemctl status docker
```

**期待出力**:

```plaintext
Active: active (running)
```

**確認ポイント**:

- `active (running)` であること

### 手順3: sysctl 設定確認

```bash
sysctl net.bridge.bridge-nf-call-iptables
sysctl net.bridge.bridge-nf-call-ip6tables
sysctl net.ipv4.ip_forward
sysctl net.ipv6.conf.all.forwarding
sysctl net.ipv6.conf.default.forwarding
sysctl net.ipv6.bindv6only
sysctl net.ipv6.conf.ens160.accept_ra
sysctl net.ipv4.conf.all.rp_filter
```

**期待出力**:

```plaintext
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
net.ipv6.conf.default.forwarding = 1
net.ipv6.bindv6only = 0
net.ipv6.conf.ens160.accept_ra = 2
net.ipv4.conf.all.rp_filter = 0
```

**確認ポイント**:

- 設定値がテンプレート通りであること
- 管理インターフェース(NIC) の `accept_ra` が`2`に設定されていること (上記の例の場合, 管理インターフェースである `ens160` の`accept_ra` ( `net.ipv6.conf.ens160.accept_ra` )が, `2`に設定されていることを確認)

### 手順4: daemon.json 設定確認

```bash
cat /etc/docker/daemon.json
```

**期待出力**:

```json
{
  "ipv6": true,
  "iptables": false,
  "ip6tables": false,
  "ip-forward": false,
  "ip-masq": false,
  "userland-proxy": true,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

**確認ポイント**:

- 既定ブリッジネットワークのIPv6を有効化する設定であること (ipv6が `true` であること)
- Dockerがiptablesルールを管理しない設定になっていること
  - iptablesが`false`となっており, IPv4のiptablesルールを追加させない設定であること
  - ip6tablesが`false`となっており, IPv6のiptables (ip6tables)ルールを追加させない設定であること
  - ip-forwardが`false`になっており, DockerによるシステムのIPフォワーディングの有効化処理を抑止する設定になっていること
  - ip-masqが`false`になっており, 既定ブリッジネットワークのアドレス変換を無効化する設定になっていること
- userland-proxyが, `true`になっており, ホストが公開しているポート(ポートフォワーディング)でループバックアドレス(`127.0.0.1`, `::1`)宛てに来た通信を, Dockerがユーザー空間のプロセス(`docker-proxy`)経由でコンテナに中継する設定になっていること
- ログ設定が反映されていること, 上記の例の場合以下を確認する
  - ログドライバ設定( `log-driver` ): `json-file`であること
  - 最大ファイルサイズ設定 (`max-size`): 10MiB (`10m`)であること
  - 作成ファイル数設定 (`max-file`): 3ファイル (`3`)であること

### 手順5: docker グループ確認

```bash
getent group docker
```

**期待出力**:

```plaintext
docker:x:999:user1,ansible
```

**確認ポイント**:

- `docker`グループが作成されていること
- `docker_ce_users`, `users_list`, `ansible_user` の各変数で定義されたユーザがグループに含まれていること

### 手順6: バックアップ用スクリプトとイメージ確認

```bash
ls -l /usr/local/bin/backup-containers /usr/local/bin/restore-container
ls -l /usr/local/share/docker-backup/Dockerfile /usr/local/share/docker-backup/backup.sh

docker images | grep local-boombatower-docker-backup
```

**期待出力**:

```plaintext
-rwxr-xr-x ... /usr/local/bin/backup-containers
-rwxr-xr-x ... /usr/local/bin/restore-container
```

**確認ポイント**:

- `build_docker_ce_backup_container_image: true` の場合のみ存在すること
- Docker イメージがビルドされていること

### 手順7: バックアップ実行確認

```bash
/usr/local/bin/backup-containers
```

**期待出力**:

```plaintext
generation: 3
NFS directory: nfs.example.org:/share
Mount ...
Unmount ...
```

**確認ポイント**:

- NFS がマウントされ, tar.xz が生成されること

## トラブルシューティング

### 1. Docker サービスが起動しない

**確認内容**:

- `/etc/docker/daemon.json` の JSON 構文
- `journalctl -u docker -n 50` のエラーログ

**対処**:

- daemon.json の構文を修正後に `systemctl restart docker`

### 2. sysctl が反映されない

**確認内容**:

- `/etc/modules-load.d/99-docker-bridge.conf` の内容
- `sysctl --system` の実行結果

**対処**:

- `sysctl --system` を再実行

### 3. バックアップが失敗する

**確認内容**:

- `nc_command` の実行結果
- NFS サーバー到達性
- `mount` の成否

**対処**:

- NFS サーバーとネットワーク経路を確認
- `nc` または `ncat` がインストールされているか確認

### 4. docker グループ権限が反映されない

**確認内容**:

- `getent group docker` にユーザが含まれているか

**対処**:

- ユーザの再ログイン, または `newgrp docker`

## 留意事項

- `backup-containers` は稼働中コンテナを対象にするため, 一貫性が必要なアプリケーションでは停止手順と組み合わせて運用してください。
- `templates/docker-bridge.conf.j2` は IPv4/IPv6 フォワーディングを有効化し, 管理インターフェースで RA を受け入れる設定と `rp_filter` 無効化を含みます。セキュリティポリシー上問題となる場合は値を見直してください。
- `/etc/docker/daemon.json` では Docker の iptables 管理を無効化しています。router-config ロールで独自に iptables を管理する前提のためです。