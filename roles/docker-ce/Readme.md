# docker-ce ロール

本ロールは, Docker Community Edition (Docker CE) を導入し, サービス初期化, sysctl の調整, 利用ユーザのグループ設定, およびコンテナボリュームのバックアップ環境を一括で整備するロールです。

## 目次

- [docker-ce ロール](#docker-ce-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
    - [主な処理](#主な処理)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
    - [make ターゲット](#make-ターゲット)
    - [ansible-playbook](#ansible-playbook)
  - [主要変数](#主要変数)
    - [ロール固有変数 (defaults/main.yml)](#ロール固有変数-defaultsmainyml)
    - [設定例](#設定例)
      - [docker-ceコマンド利用ユーザの設定](#docker-ceコマンド利用ユーザの設定)
      - [Docker ログ設定](#docker-ログ設定)
      - [バックアップ設定](#バックアップ設定)
      - [ローカルレジストリ設定](#ローカルレジストリ設定)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
    - [デフォルト動作](#デフォルト動作)
    - [OS 差異](#os-差異)
    - [バックアップ/復旧フロー](#バックアップ復旧フロー)
      - [backup-containers の流れ](#backup-containers-の流れ)
      - [restore-container の流れ](#restore-container-の流れ)
  - [検証ポイント](#検証ポイント)
    - [前提条件](#前提条件-1)
    - [手順1: Docker バージョン確認](#手順1-docker-バージョン確認)
    - [手順2: Docker サービス状態](#手順2-docker-サービス状態)
    - [手順3: sysctl 設定確認](#手順3-sysctl-設定確認)
    - [手順4: daemon.json 設定確認](#手順4-daemonjson-設定確認)
    - [手順5: docker グループ確認](#手順5-docker-グループ確認)
    - [手順6: バックアップ用スクリプトとイメージ確認](#手順6-バックアップ用スクリプトとイメージ確認)
    - [手順7: バックアップ実行確認](#手順7-バックアップ実行確認)
    - [手順8: ローカルレジストリ確認](#手順8-ローカルレジストリ確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. Docker サービスが起動しない](#1-docker-サービスが起動しない)
    - [2. sysctl が反映されない](#2-sysctl-が反映されない)
    - [3. バックアップが失敗する](#3-バックアップが失敗する)
    - [4. docker グループ権限が反映されない](#4-docker-グループ権限が反映されない)
  - [注意事項](#注意事項)
    - [ローカルコンテナレジストリ設定時のansible 制御ノード側の設定について](#ローカルコンテナレジストリ設定時のansible-制御ノード側の設定について)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| ユーザ | - | 機能を利用する人, 又は識別された利用主体。 |
| ツール | - | 特定作業を実行するための機能や道具。 |
| リソース | - | 処理に必要な計算機資源やデータ。 |
| クラスタ | - | 複数の機器を連携させて一体運用する構成。 |
| ディストリビューション | - | 基本ソフトウェアと関連部品をまとめた配布形態。 |
| コンテナイメージ | - | コンテナ実行に必要な内容をまとめた保存形式。 |
| プログラム | - | 計算機に処理をさせるための命令列。 |
| コミュニティ | - | 共通目的のもとで継続的に活動する利用者集団。 |
| プラグイン | - | 既存機能へ追加機能を組み込むための拡張部品。 |
| サービスアカウント (Service Account) | - | 自動処理中でサービスを呼び出す側のプログラムを識別するための識別情報。 |
| コンテナランタイム | - | コンテナを起動, 停止, 管理する実行基盤。 |
| リクエスト | - | 処理実行や情報取得を要求する操作。 |
| コントローラ | - | 対象状態を監視し, 期待状態へ調整する制御機能。 |
| メタデータ | - | 対象データの属性や説明を示す付加情報。 |
| バックエンド | - | 利用者画面の背後で処理を実行する側。 |
| ストレージ | - | データを保存する仕組み。 |
| インストール | - | ソフトウェアを導入して利用可能にする作業。 |
| マシン | - | 処理を実行する計算機。 |
| プロビジョニング | - | 利用開始に必要な設定や資源を準備する作業。 |
| ルーティング | - | 宛先までの経路を選択して転送する処理。 |
| オブジェクト | - | ひとかたまりとして扱うデータ単位。 |
| エージェント | - | 指示に従って処理を代行する構成要素。 |
| ストア | - | データや成果物を保存する場所。 |
| ジャーナル | - | 時系列の記録を保持する仕組み。 |
| アカウント | - | 利用者や処理主体を識別する登録情報。 |
| エンドポイント | - | 通信の接続先を表す識別点。 |
| パターン | - | 繰り返し現れる構造や記述形式。 |
| パケット | - | ネットワークで転送するデータ単位。 |
| カーネル | - | 基本ソフトウェアの中核機能。 |
| シェル | - | コマンド入力で計算機を操作する仕組み。 |
| Playbook | - | 自動化処理の実行手順を記述したファイル。 |
| Canonical | - | Ubuntu を提供する組織名。 |
| Key-Value | - | キーと値の組で情報を表す方式。 |
| Internet Protocol | IP | ネットワーク上で宛先を識別し, データを届けるための通信手順。 |
| Structured Query Language | SQL | データベースを操作するための記述言語。 |
| Hypertext Transfer Protocol | HTTP | World Wide Webで情報をやり取りする通信手順。 |
| Hypertext Transfer Protocol Secure | HTTPS | 通信内容を暗号化してWorld Wide Web通信を行う方式。 |
| RPM Package Manager | RPM | RPM形式パッケージの導入, 更新, 削除, 情報参照を行う仕組み。 |
| Virtual Machine | VM | 物理計算機上で動作する仮想的な計算機。 |
| localhost | - | 同一機器自身を指す名前。 |
| root | - | Unix 系システムの最上位権限を持つ管理者識別子。 |
| ソフトウェア | - | 情報処理システムで使用するプログラム, 手順, 規則及び関連文書の全体又は一部分。 |
| アプリケーション | - | 利用者の目的を実現するために動作するソフトウェア。 |
| パッケージ | - | ソフトウェア導入に必要なファイルをまとめた配布単位。 |
| リポジトリ | - | ソフトウェアや設定情報を保管し, 取得できるようにした管理場所。 |
| コマンド | - | 実行者が計算機へ処理を指示するための命令。 |
| ホスト | - | 管理対象として識別される個別の計算機。 |
| サーバ | - | 他の機器や利用者へ機能やデータを提供する計算機, 又はその役割。 |
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
| ネットワーク | - | 機器同士を接続してデータをやり取りする仕組み。 |
| プロトコル | - | 通信やデータ交換の手順を定めた取り決め。 |
| ディレクトリ | - | ファイルを階層的に整理するための入れ物。 |
| ログ | - | 処理の結果や状態を時系列で記録した情報。 |
| コード | - | 処理内容を記述した文字列。 |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウェア。 |
| Pod | - | Kubernetes でコンテナをまとめて管理する最小単位。 |
| Linux | - | 多くの機器で使われる, 基本ソフトウェアの系統。 |
| Debian | - | コミュニティ主導で開発される Linux ディストリビューション。 |
| Ubuntu | - | Canonical が提供する Debian 系の Linux ディストリビューション。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| Docker Community Edition | Docker CE | Docker のコミュニティ版。Docker Engine と関連ツールで構成される。 |
| Docker Engine | - | コンテナの実行基盤。 `dockerd` とその API を含む。 |
| containerd | - | Dockerから分離された軽量なコンテナランタイム。 |
| Network File System | NFS | ネットワーク越しにファイル共有を行う仕組み。 |
| Hypertext Transfer Protocol Secure | HTTPS | 通信内容を暗号化してWorld Wide Web通信を行う方式。 |
| Router Advertisement | RA | IPv6 で経路情報を通知する仕組み。 |
| Reverse Path Filtering | rp_filter | 逆引きパスフィルタリングの設定。 |
| sysctl | - | カーネル動作パラメタを参照, 変更するコマンド。 |
| netcat | nc | ネットワーク到達性を確認するコマンド。RHEL 系では `ncat` を使用。 |
| Hypertext Transfer Protocol | HTTP | World Wide Webで情報をやり取りする通信手順。 |
| JavaScript Object Notation | JSON | 人間が読みやすいテキスト形式のデータ交換フォーマット。キーと値のペアで構成され, 設定ファイルやAPI レスポンスに広く使用される。 |
| Network Interface Card | NIC | 計算機をネットワークへ接続するための装置または機能。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Red Hat Enterprise Linux | RHEL | Red Hatが提供する企業向けLinuxディストリビューション。 |
| Red Hat Enterprise Linux 9 | RHEL9 | Red Hat Enterprise Linux の第9系統版。 |
| Secure Shell | SSH | 遠隔の計算機へ安全に接続して操作する方式。 |
| Ansible Playbook | playbook | 自動化処理の実行手順を順序付きで記述したファイル。 |
| Community Edition | CE | 商用版と区別する無償版の製品区分。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `cat` | - | ファイル内容を標準出力へ表示するコマンド。 |
| `chmod` | - | ファイルやディレクトリのアクセス権を変更するコマンド。 |
| `curl` | - | URL を指定してデータ送受信を行うコマンド。 |
| `date` | - | 現在日時を表示するコマンド。 |
| `docker` | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| `getent` | - | システムの名前解決データベースを参照するコマンド。 |
| `journalctl` | - | systemd ジャーナルのログを参照するコマンド。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| makeコマンド | make | Makefile に定義された処理を実行するコマンド。 |
| `systemctl` | - | systemd 管理下のサービスを起動, 停止, 状態確認するコマンド。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
| サービス | - | 機能を利用者や他システムへ提供する仕組み。 |
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| ポート | - | 通信の出入口を識別する番号または接点。 |
| ログイン | - | 利用者認証を行って利用を開始する操作。 |
| リモートホスト | - | ネットワーク越しに接続して操作する別ホスト。 |
| ローカルコンテナレジストリ | - | 実行中ホストまたは同一環境内で運用するコンテナイメージ保管先。 |
| ローカルコンテナレジストリホスト | - | ローカルコンテナレジストリを提供するホスト。 |
| ローカルレジストリ | - | 実行中ホストまたは同一環境内で運用する成果物保管先。 |
| ローカルレジストリコンテナ | - | ローカルレジストリ機能を提供するコンテナ。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |
## 概要
Docker Community Edition (Docker CE) を導入し, サービス初期化, sysctl の調整, 利用ユーザのグループ設定, およびコンテナボリュームのバックアップ環境を一括で整備するロールです。Debian 系と RHEL 系の差異は `ansible_facts.os_family` を基準に変数を切り替えることで吸収しています。

### 主な処理

本ロールは, Docker Engine の導入と運用補助設定を実行する。

1. OS ごとのリポジトリ設定を行い, docker-ce 関連パッケージを導入する。
2. daemon 設定と sysctl 設定を反映し, サービスを有効化して起動する。
3. 必要に応じてバックアップ補助スクリプトと補助設定を配置する。

## 前提条件

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
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
| `docker_ce_registry_enabled` | `false` | defaults/main.yml | ローカルコンテナレジストリ機能を有効化するフラグ。 |
| `docker_ce_registry_container_name` | `"local-registry"` | defaults/main.yml | ローカルレジストリのコンテナ名。 |
| `docker_ce_registry_image` | `"registry:2"` | defaults/main.yml | ローカルレジストリで使用するコンテナイメージ。 |
| `docker_ce_registry_bind_address` | `"0.0.0.0"` | defaults/main.yml | ローカルレジストリの待ち受けアドレス。 |
| `docker_ce_registry_port` | `5000` | defaults/main.yml | ローカルレジストリの待ち受けポート。 |
| `docker_ce_registry_data_dir` | `"/var/lib/local-registry"` | defaults/main.yml | ローカルレジストリのデータ保存先ディレクトリ。 |
| `docker_ce_insecure_registries` | `{{ container_registry_endpoints \| default([], true) }}` | defaults/main.yml | dockerクライアントからpush/pull/search可能にする対象のコンテナレジストリ設定。各要素は辞書 (`endpoint`, 任意で `scheme`, `skip_verify`) で指定します。`scheme != https` または `skip_verify: true` のエントリを `/etc/docker/daemon.json` の `insecure-registries` に設定します。既定では共有変数 `container_registry_endpoints` を参照します。 |
| `build_docker_ce_backup_container_image` | `false` | defaults/main.yml | バックアップ用コンテナイメージを作成する場合は `true`。 |
| `docker_ce_enable_backup_script` | `false` | defaults/main.yml | バックアップスクリプト生成有効化フラグ。`docker_ce_enable_backup_script` が `true` の場合, restore-container.j2, Dockerfile.j2, backup.sh.j2 が配置されます。さらに `docker_ce_backup_nfs_server` と `docker_ce_backup_nfs_dir` が非空の場合にのみ, backup-containers.j2 が配置されます。不要な環境では `false` に設定するとテンプレート生成をスキップできます。 |

### 設定例

本節では, docker-ceロールの設定方法について説明します。

#### docker-ceコマンド利用ユーザの設定

本節では, docker-ceコマンドを利用するユーザを`docker_ce_users`変数にリストとして記載します。
`vars/all-config.yml` または `host_vars/<hostname>/main.yml`に以下の形式で利用するユーザのリストを記載します:

```yaml
docker_ce_users:
  - user1
```

#### Docker ログ設定

本節では, Dockerデーモンのログファイルの設定方法について説明します。
`vars/all-config.yml` または `host_vars/<hostname>`に以下の設定を記載します:

```yaml
docker_ce_log_driver: "json-file"
docker_ce_log_opts:
  max-size: "50m"
  max-file: "5"
```

#### バックアップ設定

登録されているコンテナイメージをNFSの共有ディレクトリにバックアップする場合は,
`vars/all-config.yml` および `host_vars/<hostname>`に以下の内容を記載します:

`vars/all-config.yml`:
```yaml
docker_ce_backup_nfs_server: "nfs.example.org"
docker_ce_backup_nfs_dir: "/share"
docker_ce_backup_mount_point: "/mnt"
docker_ce_backup_dir_on_nfs: "/Linux/containers"
```

`host_vars/<hostname>`:

```yaml
build_docker_ce_backup_container_image: true
```

#### ローカルレジストリ設定

docker-ceを用いてローカルコンテナレジストリ機能を提供する場合は, `vars/all-config.yml` または `host_vars/<hostname>`に以下の設定を記載します:

`vars/all-config.yml`:
```yaml
container_registry_endpoints:
  - endpoint: "local-registry.local:5000"
    scheme: "http"
    skip_verify: true
  - endpoint: "devserver.example.org:5050"
    scheme: "https"
    skip_verify: true
```

`host_vars/<hostname>`
```yaml
docker_ce_registry_enabled: true
docker_ce_registry_port: 5000
docker_ce_insecure_registries: "{{ container_registry_endpoints }}"
```

## テンプレートと生成ファイル

本ロールでは以下のテンプレート/ファイルを出力します:

| テンプレート/ファイル | 出力先パス | 条件 | 説明 |
| --- | --- | --- | --- |
| `docker-bridge.conf.j2` | `/etc/modules-load.d/95-docker-bridge.conf` | 常に実行 | Docker ブリッジ関連の sysctl 設定。 |
| `backup-containers.j2` | `/usr/local/bin/backup-containers` | `build_docker_ce_backup_container_image: true` かつ `docker_ce_enable_backup_script: true` かつ `docker_ce_backup_nfs_server` と `docker_ce_backup_nfs_dir` が非空 | コンテナバックアップスクリプト。 |
| `restore-container.j2` | `/usr/local/bin/restore-container` | `build_docker_ce_backup_container_image: true` かつ `docker_ce_enable_backup_script: true` | コンテナ復旧スクリプト。 |
| `Dockerfile.j2` | `/usr/local/share/docker-backup/Dockerfile` | `build_docker_ce_backup_container_image: true` かつ `docker_ce_enable_backup_script: true` | `opensuse/leap:15.6` をベースに boombatower/docker-backup 互換のイメージを作成。 |
| `backup.sh.j2` | `/usr/local/share/docker-backup/backup.sh` | `build_docker_ce_backup_container_image: true` かつ `docker_ce_enable_backup_script: true` | バックアップ用イメージのエントリスクリプト。 |
| `daemon.json.j2` | `/etc/docker/daemon.json` | 常に実行 | Docker の動作設定ファイルテンプレート。`docker_ce_insecure_registries` が非空の場合は `insecure-registries` を追加します。 |
| `/etc/docker/daemon.json` | `/etc/docker/daemon.json` | 常に実行 | Docker の動作設定ファイル。 |

## 実行フロー

本ロールは以下の順序で処理を実行します:

1. **パラメータ読み込み** (`load-params.yml`): OS 別パッケージ定義と共通変数を読み込みます。
2. **パッケージ操作** (`package.yml`): 旧パッケージ削除, 前提パッケージ導入, Docker CE パッケージ導入を行います。
3. **サービス設定** (`service.yml`): sysctl 設定ファイルを配置し, `sysctl --system` を実行後に docker サービスを再起動します。
4. **ディレクトリ作成** (`directory.yml`): `/usr/local/bin` と `/usr/local/share` を作成します。`docker_ce_registry_enabled: true` の場合はレジストリデータ用ディレクトリ (`docker_ce_registry_data_dir`) も作成します。
5. **ローカルレジストリ設定** (`registry.yml`): `docker_ce_registry_enabled` が `true` の場合, レジストリコンテナを起動または再作成します。
6. **バックアップ用ファイル配置とイメージ作成** (`docker-backup-image.yml`): `build_docker_ce_backup_container_image` が `true` の場合のみ, バックアップ・復旧スクリプトと Dockerfile を配置します。`docker_ce_enable_backup_script` が有効な場合, restore-container.j2, Dockerfile.j2, backup.sh.j2 を配置し, さらに `docker_ce_backup_nfs_server` と `docker_ce_backup_nfs_dir` が非空の場合にのみ backup-containers.j2 を配置します。その後, バックアップ用イメージをビルドします。
7. **ユーザとグループ設定** (`user_group.yml`): docker グループを作成し, `ansible_user`, `docker_ce_users`, `users_list` のユーザを追加します。
8. **Docker 設定** (`config.yml`): `/etc/docker/daemon.json` を作成し, iptables 管理の無効化などを設定します。`docker_ce_insecure_registries` が非空の場合のみ `insecure-registries` を設定します。既定では共有変数 `container_registry_endpoints` を参照します。

### デフォルト動作

- `build_docker_ce_backup_container_image: false` のため, バックアップ/復旧スクリプトとバックアップ用イメージは既定では作成されません。
- `docker_ce_registry_enabled: false` のため, ローカルレジストリコンテナは既定では作成されません。
- `docker` サービスは `enabled: true`, `state: restarted` で起動します。
- `/etc/docker/daemon.json` は iptables 管理の無効化と IPv6 有効化を含む設定で生成されます。
- `docker_ce_insecure_registries` が空または未定義の場合, `/etc/docker/daemon.json` に `insecure-registries` は出力されません。
- `docker_ce_backup_output_dir` は `docker_ce_backup_mount_point` と `docker_ce_backup_dir_on_nfs` の結合値になります。既定では `/mnt/containers/docker-ce/daily-backup` です。
- sysctl は `/etc/modules-load.d/95-docker-bridge.conf` を通じて反映されます。設定内容には `net.bridge.bridge-nf-call-iptables`, `net.bridge.bridge-nf-call-ip6tables`, `net.ipv4.ip_forward`, `net.ipv6.conf.all.forwarding`, `net.ipv6.conf.default.forwarding`, `net.ipv6.bindv6only`, `net.ipv6.conf.<mgmt_nic>.accept_ra`, `net.ipv4.conf.*.rp_filter` が含まれます。

### OS 差異

| 項目 | Debian 系 | RHEL 系 | 備考 |
| --- | --- | --- | --- |
| 旧パッケージ削除対象 | `docker.io` など | `docker` など | `docker_ce_remove_packages` により異なる。 |
| 前提パッケージ | `apt-transport-https`, `gnupg` など | `gnupg2` など | `docker_ce_prereq_packages` により異なる。 |
| netcat コマンド | `nc` | `ncat` | NFS 疎通確認に使用。 |

### バックアップ/復旧フロー

#### backup-containers の流れ

1. `nc_command` で `docker_ce_backup_nfs_server` への NFS ポート疎通を確認します。
2. `docker_ce_backup_nfs_dir` を `docker_ce_backup_mount_point` へマウントし, 年間通算日 (`date +%j`) を `docker_ce_backup_rotation` で割った余りを世代番号として算出します。
3. 稼働中コンテナを列挙し, `{{ docker_ce_backup_output_dir }}/<コンテナ名>/<コンテナ名>-<世代>.tar.xz` を生成します。
4. パーミッションを緩和 (`chmod -R o+rwX`) した後, NFS をアンマウントします。

バックアップは boombatower/docker-backup と互換のコンテナイメージを利用します。

#### restore-container の流れ

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

### 手順8: ローカルレジストリ確認

ローカルコンテナレジストリホスト上で以下を実行する:

```bash
docker ps --filter name=local-registry
ss -lntp | grep :5000
curl http://127.0.0.1:5000/v2/
```

他のホスト上で以下を実行する(`<endpoint>`には, `<ローカルコンテナレジストリのホスト名, または, IPアドレス>:<ポート番号>`を指定する):

```bash
curl http://<endpoint>/v2/
```

**期待出力**:

ローカルコンテナレジストリホスト上の実行例:
```bash
$ docker ps --filter name=local-registry
CONTAINER ID   IMAGE        COMMAND                   CREATED             STATUS          PORTS                    NAMES
6f2ad5277dbb   registry:2   "/entrypoint.sh /etc…"   About an hour ago   Up 17 minutes   0.0.0.0:5000->5000/tcp   local-registry
$ ss -lntp | grep :5000

LISTEN 0      4096         0.0.0.0:5000      0.0.0.0:*
$ curl http://127.0.0.1:5000/v2/

{}
```

他のホスト上の実行例:
```bash
$ curl http://registry1.local:5000/v2/
{}
```

**確認ポイント**:

- `docker_ce_registry_enabled: true` の場合に local-registry コンテナが稼働していること。
- レジストリポートが待ち受けていること。
- `/v2/` エンドポイントへ HTTP でアクセスできること。

## トラブルシューティング

### 1. Docker サービスが起動しない

**確認内容**:

- `/etc/docker/daemon.json` の JSON 構文
- `journalctl -u docker -n 50` のエラーログ

**対処**:

- daemon.json の構文を修正後に `systemctl restart docker`

### 2. sysctl が反映されない

**確認内容**:

- `/etc/modules-load.d/95-docker-bridge.conf` の内容
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
- `nc` または `ncat` がインストールされていることを確認

### 4. docker グループ権限が反映されない

**確認内容**:

- `getent group docker` にユーザが含まれていること

**対処**:

- ユーザの再ログイン, または `newgrp docker`

## 注意事項

- `backup-containers` は稼働中コンテナを対象にするため, 一貫性が必要なアプリケーションでは停止手順と組み合わせて運用してください。
- `templates/docker-bridge.conf.j2` は IPv4/IPv6 フォワーディングを有効化し, 管理インターフェースで RA を受け入れる設定と `rp_filter` 無効化を含みます。セキュリティポリシー上問題となる場合は値を見直してください。
- `/etc/docker/daemon.json` では Docker の iptables 管理を無効化しています。router-config ロールで独自に iptables を管理する前提のためです。

### ローカルコンテナレジストリ設定時のansible 制御ノード側の設定について

本playbookでは, コンテナイメージをローカルコンテナレジストリに登録する際に制御ノード上のDockerクライアントを使用します。

ローカルコンテナレジストリの接続スキームが`http`の場合, 制御ノード上の`/etc/docker/daemon.json`ファイルに以下の項目を追加し, 登録対象レジストリ(`container_registry_endpoints`変数の`endpoint`の項目に記載されたレジストリ)に対するアクセスを許可するよう設定してください。

```json
{
  "insecure-registries": ["<レジストリのエンドポイント>"]
}
```

例えば, `container_registry_endpoints`変数を以下に用に設定している場合:

```yaml
container_registry_endpoints:
  - endpoint: "registry1.local:5000"
    scheme: "http"
    skip_verify: true
  - endpoint: "registry2.local:5000"
    scheme: "http"
    skip_verify: true
```

`/etc/docker/daemon.json`ファイルには, 以下の項目を記載します。

```json
{
  "insecure-registries": ["registry1.local:5000", "registry2.local:5000"]
}
```

本playbookのdocker-ce ロールが適用されたホストの場合は, 上記の設定を自動的に実施します。ただし, `container_registry_endpoints`が空の場合や, `scheme`が, `https`, かつ,`skip_verify=false`と定義されたエントリのみの場合は, `/etc/docker/daemon.json`に`insecure-registries`項目を出力しません。

また, Ansible制御ノード自体に docker-ce ロールを適用していない場合, 制御ノードの daemon.json は変更されません。

## 参考資料

### 公式ドキュメント

- Docker Engine: https://docs.docker.com/engine/
- Docker Compose: https://docs.docker.com/compose/
