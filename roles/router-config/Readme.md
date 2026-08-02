# router-config ロール

本ロールは, ルータホストで IPv4/IPv6 パケット転送と Network Address Translation (NAT) を制御する設定を行います。

## 目次

- [router-config ロール](#router-config-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [主な処理](#主な処理)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
    - [前提](#前提)
    - [Make ターゲットで実行](#make-ターゲットで実行)
    - [ansible-playbook で直接実行](#ansible-playbook-で直接実行)
    - [推奨実行順序 (モード切替時)](#推奨実行順序-モード切替時)
  - [主要変数](#主要変数)
    - [動作制御](#動作制御)
    - [パッケージ, サービス, ノード再起動](#パッケージ-サービス-ノード再起動)
    - [ネットワーク関連 (必須)](#ネットワーク関連-必須)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
    - [ハンドラ](#ハンドラ)
      - [bastion\_config\_reload\_sysctl (`handlers/reload-sysctl.yml`)](#bastion_config_reload_sysctl-handlersreload-sysctlyml)
    - [OS差異](#os差異)
  - [検証ポイント](#検証ポイント)
    - [1. ネットワーク構成とルータホストの役割](#1-ネットワーク構成とルータホストの役割)
      - [ネットワークの分類](#ネットワークの分類)
      - [IP アドレスの例](#ip-アドレスの例)
      - [トラフィックの流れ](#トラフィックの流れ)
    - [2. 共通検証](#2-共通検証)
      - [2.1 sysctl 設定確認](#21-sysctl-設定確認)
      - [2.2 永続化状態確認](#22-永続化状態確認)
    - [3. 純粋ルーティング構成の検証 (config-forward.yml)](#3-純粋ルーティング構成の検証-config-forwardyml)
      - [3.1 FORWARD ルール確認](#31-forward-ルール確認)
      - [3.2 NAT 不在確認](#32-nat-不在確認)
      - [3.3 疎通確認 (送信元保持)](#33-疎通確認-送信元保持)
    - [4. NAT 構成の検証 (config-nat.yml)](#4-nat-構成の検証-config-natyml)
      - [4.1 FORWARD, POSTROUTING ルール確認](#41-forward-postrouting-ルール確認)
      - [4.2 疎通確認 (NAT 変換)](#42-疎通確認-nat-変換)
      - [4.3 tcpdump による SNAT 確認](#43-tcpdump-による-snat-確認)
    - [5. 意図的にパケット転送を無効化している場合](#5-意図的にパケット転送を無効化している場合)
      - [5.1 ルール未設定確認](#51-ルール未設定確認)
      - [5.2 ルール残骸がある場合の対処](#52-ルール残骸がある場合の対処)
  - [トラブルシューティング](#トラブルシューティング)
  - [注意事項](#注意事項)
  - [テンプレート / 出力ファイル](#テンプレート--出力ファイル)
  - [補足](#補足)
    - [動作モード](#動作モード)
    - [設定値による動作の違い](#設定値による動作の違い)
    - [makeターゲット `run_router_clear_rules`の処理内容](#makeターゲット-run_router_clear_rulesの処理内容)
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
| サービスアカウント | - | 自動処理向けに用意する利用主体の識別情報。 |
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
| Internet Protocol | IP | インターネットプロトコルの略称。 |
| Structured Query Language | SQL | データベースを操作するための記述言語。 |
| Hypertext Transfer Protocol | HTTP | WWW で情報をやり取りする通信手順。 |
| Hypertext Transfer Protocol Secure | HTTPS | 通信内容を暗号化して WWW 通信を行う方式。 |
| RPM Package Manager | RPM | RHEL 系で使用するパッケージ形式。 |
| Virtual Machine | VM | 物理機器上で動作する仮想的な計算機。 |
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
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Application Programming Interface | API | アプリケーション同士がやり取りする方法を定めた仕様。 |
| Uniform Resource Locator | URL | WWW 上の資源の場所を示す文字列。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| systemd | - | Linux システムの初期化とサービス管理を行う仕組み。 |
| Network Address Translation | NAT | IP アドレスを変換する仕組み。 |
| Source Network Address Translation | SNAT | 送信元アドレスを変換する NAT 方式。 |
| Masquerading | MASQUERADE | iptables の SNAT ターゲット。送信元を送信インターフェースのアドレスへ変換します。 |
| Reverse Path Filtering | RPF | 逆引きパスフィルタリングの設定。 |
| Internet Protocol version 4 | IPv4 | 32 ビットアドレス空間を持つインターネットプロトコル。現在最も広く使用されているバージョン。 |
| Internet Protocol version 6 | IPv6 | 128 ビットアドレス空間を持つ次世代インターネットプロトコル。IPv4 アドレス枯渇問題を解決します。 |
| Classless Inter-Domain Routing | CIDR | IP アドレスとネットワークプレフィックス長を組み合わせた表記法。 |
| Network Interface Card | NIC | 計算機をネットワークへ接続するための装置または機能。 |
| iptables | - | Linux の IPv4 パケットフィルタ設定ツール。 |
| ip6tables | - | Linux の IPv6 パケットフィルタ設定ツール。 |
| FORWARD chain | FORWARD | 転送パケットを評価するフィルタチェーン。 |
| POSTROUTING chain | POSTROUTING | 送信直前パケットを評価する NAT チェーン。 |
| Connection Tracking | conntrack | 接続状態を追跡する機能。 |
| Connection State | ESTABLISHED, RELATED | 既存接続, または既存接続に関連する通信状態。 |
| conntrack state match | ctstate | `-m conntrack --ctstate ...` で接続状態を条件指定する機能。 |
| netfilter-persistent | - | Debian 系で iptables/ip6tables ルールを保存, 復元する仕組み。 |
| iptables-services | - | Red Hat 系で iptables/ip6tables を管理するパッケージ。 |
| systemctl | - | systemd 管理下のサービスを起動, 停止, 状態確認するコマンド。 |
| sysctl | - | カーネル動作パラメタを参照, 変更するコマンド。 |
| Handler | - | 通知時に実行する再処理です。 |
| Role | - | 特定の名前空間内で有効な権限の集合。 |
| Ansible Playbook | playbook | 自動化処理の実行手順を順序付きで記述したファイル。 |
| Yet Another Markup Language | YAML | 設定ファイル形式です。 |
| Tag | - | Ansibleで実行対象を絞るラベルです。 |
| Ansible Inventory | - | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Docker Community Edition | Docker CE | Docker のコミュニティ版。Docker Engine と関連ツールで構成される。 |
| become | - | Ansible の権限昇格指定。管理者権限でタスクを実行します。 |
| tcpdump | - | パケットをキャプチャして通信を確認するコマンド。 |
| Graceful reboot | - | 稼働中サービスへの影響を抑えて実行するノード再起動方式。 |
| Internet Control Message Protocol | ICMP | 疎通確認や障害通知に使う通信方式。 |
| Internet Protocol | IP | ネットワーク上で宛先を識別し, データを届けるための通信手順。 |
| Red Hat Enterprise Linux 9 | RHEL9 | Red Hat Enterprise Linux の第9系統版。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| Accept | ACCEPT | 通信を許可する判定結果。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `cat` | - | ファイル内容を標準出力へ表示するコマンド。 |
| `make` | - | Makefile に定義された処理を実行するコマンド。 |
| `ping` | - | 対象への到達性と往復遅延を確認するコマンド。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
| サービス | - | 機能を利用者や他システムへ提供する仕組み。 |
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |

## 概要
本ロールは, ルータホストで IPv4/IPv6 パケット転送と Network Address Translation (NAT) を制御する設定を行います。実装では, sysctl 設定ファイルの生成, iptables/ip6tables ルール投入, OS 別の永続化, サービス有効化, およびノード再起動を実施します。

## 主な処理

- `95-ipfoward.conf` を配置し, IPv4/IPv6 転送と RPF ルーズモードを有効化します。
- ルール投入前に既存 FORWARD/POSTROUTING ルールを削除し, モード切替時のルール残骸を防ぎます。
- 純粋ルーティングモードでは, 外部向けネットワーク <=> 内部プライベートネットワークの双方向 FORWARD ルールを投入します。
- NAT モードでは, FORWARD ルールに加えて POSTROUTING MASQUERADE を投入します。
- ルールは `iptables`, `ip6tables` コマンド実行時に即座にカーネルへ適用され, 直ちに有効化されます。
- 再起動後も設定を維持するため, OS 別方式でルールをファイルへ永続化します。
  - Debian 系: `netfilter-persistent save` で `/etc/iptables/rules.v4` (IPv4), `/etc/iptables/rules.v6` (IPv6) へ保存
  - Red Hat 系: `iptables-save`, `ip6tables-save` で `{{ etc_default_dir }}/iptables` (`/etc/sysconfig/iptables`), `{{ etc_default_dir }}/ip6tables` (`/etc/sysconfig/ip6tables`) へ保存後, `iptables`, `ip6tables` サービスを再起動してファイルから再読み込み

## 前提条件

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- Ansible 2.15 以降, ansibleメタパッケージをディストリビューションから導入していることを想定
- Ansible から対象ホストへ接続可能であること。
- 対象ホストで管理者権限へ昇格して実行できること (`become: true`)。
- 以下の変数が定義済みであること。
  - `gpm_mgmt_nic`
  - `mgmt_nic`
  - `gpm_mgmt_ipv4_network_cidr`
  - `gpm_mgmt_ipv6_network_cidr`
- `gpm_mgmt_nic` と `mgmt_nic` が, 対象ホストのインターフェース一覧に存在すること。

これらの NIC 条件を満たさない場合, `Load Params` 以外のタスクは実行されません。

## 実行方法

### 前提

- インベントリに対象ルータホストが含まれていること。
- `router.yml` では `docker-ce` の後に `router-config` が実行されます。
- モード切替時は, 必要に応じて先にクリアルールを実行します。

### Make ターゲットで実行

```bash
# router-config ロール実行
make run_router_config

# 既存ルールクリア
make run_router_clear_rules
```

`run_router_clear_rules` は `router-clear-rules.yml` を `hosts: all` で実行します。必要に応じて, ansible-playbook で直接実行し, `-l router.local` で対象ホストを限定してください。

### ansible-playbook で直接実行

```bash
# router プレイブック全体
ansible-playbook -i inventory/hosts router.yml

# site.yml から router-config タグのみ
ansible-playbook -i inventory/hosts site.yml --tags "router-config"

# ホスト限定で実行
ansible-playbook -i inventory/hosts site.yml --tags "router-config" -l router.local

# クリア専用プレイブック
ansible-playbook -i inventory/hosts router-clear-rules.yml
```

### 推奨実行順序 (モード切替時)

1. `make run_router_clear_rules` で既存ルールを削除します。
2. 変数 (`router_forwarding_enabled`, `router_nat_enabled`, `additional_network_routes`) を調整します。
3. `make run_router_config` で新モードを適用します。

## 主要変数

### 動作制御

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `router_forwarding_enabled` | `true` | NAT 無しの双方向 FORWARD ルールを有効化します。`true` の場合は NAT より優先されます。 |
| `router_nat_enabled` | `false` | NAT 構成を有効化します。`router_forwarding_enabled: true` または `additional_network_routes` 定義時は実行されません。 |
| `additional_network_routes` | 未定義 | `additional-routes` ロールと連携する追加ルート定義です。定義時は FORWARD 構成が優先されます。 |

### パッケージ, サービス, ノード再起動

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `iptables_persistent_package` | OS 依存 | Debian 系は `iptables-persistent`, Red Hat 系は `iptables-services`。 |
| `iptables_persistent_service` | OS 依存 | Debian 系は `iptables-persistent`, Red Hat 系は `iptables`。 |
| `iptables_persistent_ipv6_service` | OS 依存 | Debian 系は `iptables-persistent`, Red Hat 系は `ip6tables`。 |
| `etc_default_dir` | OS 依存 | Debian 系は `/etc/default`, Red Hat 系は `/etc/sysconfig`。 |
| `reboot_timeout_sec` | `600` | ノード再起動後の応答待ちタイムアウト (秒)。 |

### ネットワーク関連 (必須)

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `mgmt_nic` | 必須 | 外部向けネットワーク側 NIC。 |
| `gpm_mgmt_nic` | 必須 | 内部プライベートネットワーク側 NIC。 |
| `network_ipv4_network_address` | 必須 | 外部向け IPv4 ネットワークアドレス。 |
| `network_ipv4_prefix_len` | 必須 | 外部向け IPv4 プレフィックス長。 |
| `network_ipv6_network_address` | 必須 | 外部向け IPv6 ネットワークアドレス。 |
| `network_ipv6_prefix_len` | 必須 | 外部向け IPv6 プレフィックス長。 |
| `gpm_mgmt_ipv4_network_cidr` | 必須 | 内部プライベート側 IPv4 CIDR。 |
| `gpm_mgmt_ipv6_network_cidr` | 必須 | 内部プライベート側 IPv6 CIDR。 |

## テンプレートと生成ファイル

本ロールでは以下のテンプレート / ファイルを出力します:
主な展開先ホストは, 対象ホスト(既定) です。

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `95-ipfoward.j2` | `/etc/sysctl.d/95-ipfoward.conf` (既定) | ルータノードで必要な IPv4/IPv6 転送と逆経路フィルタ設定を定義する sysctl 設定です。 |

## 実行フロー

`roles/router-config/tasks/main.yml` は次の順序で処理します。

1. **Load Params** (`tasks/load-params.yml`)
- OS 別パッケージ変数, `cross-distro.yml`, `all-config.yml`, `k8s-api-address.yml` を読み込みます。

2. **Package** (`tasks/package.yml`)
- `iptables_persistent_package` をインストールします。

3. **Directory** (`tasks/directory.yml`)
- 現在の実装は空タスクです。

4. **User Group** (`tasks/user_group.yml`)
- 現在の実装は空タスクです。

5. **Service** (`tasks/service.yml`)
- Red Hat 系で `iptables_persistent_service`, `iptables_persistent_ipv6_service` を `enabled: true` にします。

6. **Config Sysctl** (`tasks/config-sysctl.yml`)
- `templates/95-ipfoward.j2` を `/etc/sysctl.d/95-ipfoward.conf` に配置します。
- 変更時はハンドラ `bastion_config_reload_sysctl` を通知します。

7. **Config Clear Rules** (`tasks/config-clear-rules.yml`)
- `router_forwarding_enabled`, `router_nat_enabled`, `additional_network_routes` のいずれかが有効な場合に既存ルールを削除します。

8. **Config Forward** (`tasks/config-forward.yml`)
- 実行条件: `(router_forwarding_enabled == true or additional_network_routes が定義済み) and router_nat_enabled == false`。
- IPv4/IPv6 双方向 FORWARD ルールを設定します。

9. **Config Nat** (`tasks/config-nat.yml`)
- 実行条件: `router_nat_enabled == true and router_forwarding_enabled == false and (additional_network_routes 未定義または空)`。
- IPv4/IPv6 の FORWARD ルールと POSTROUTING MASQUERADE ルールを設定します。

10. **Config** (`tasks/config.yml`)
- 現在の実装は空タスクです。

11. **Reboot** (`tasks/reboot.yml`)
- `reboot_timeout_sec` を使ってノードの graceful reboot を実行します。

### ハンドラ

#### bastion_config_reload_sysctl (`handlers/reload-sysctl.yml`)

- `listen`: `bastion_config_reload_sysctl`
- 実行コマンド: `sysctl --system`
- 起動条件: `config-sysctl.yml` でテンプレート更新が発生した場合

### OS差異

| 項目 | Debian/Ubuntu | Red Hat系 |
| --- | --- | --- |
| 永続化パッケージ | `iptables-persistent` | `iptables-services` |
| IPv4 サービス変数 | `iptables-persistent` | `iptables` |
| IPv6 サービス変数 | `iptables-persistent` | `ip6tables` |
| 永続化コマンド | `netfilter-persistent save` | `iptables-save`, `ip6tables-save` |
| ルール保存先ディレクトリ | `/etc/iptables` | `/etc/sysconfig` |
| service.yml の有効化処理 | 実質なし | `iptables`, `ip6tables` を有効化 |

## 検証ポイント

### 1. ネットワーク構成とルータホストの役割

本セクションの検証手順で使用するネットワーク構成とIPアドレスについて説明します。

#### ネットワークの分類

| ネットワーク | 本稿で例示するネットワーク CIDR | 用途 | インターフェース | 説明 |
| --- | --- | --- | --- | --- |
| 外部向けネットワーク | `192.168.20.0/24` | 物理サーバ/管理用 | `mgmt_nic` (ens160) | 外部接続側 NIC。 |
| 内部プライベート | `192.168.30.0/24` | 内部管理 | `gpm_mgmt_nic` (ens192) | 内部接続側 NIC。 |

#### IP アドレスの例

- 外部向け `192.168.20.0/24`
  - `192.168.20.1`: 外部ゲートウェイ
  - `192.168.20.10`: ルータホスト `mgmt_nic`
  - `192.168.20.100`: 外部ホスト (外部ゲートウェイと同一L2ネットワーク上に設置されているホスト)

- 内部プライベート `192.168.30.0/24`
  - `192.168.30.10`: ルータホスト `gpm_mgmt_nic`
  - `192.168.30.41`: 内部ホスト ( 内部プライベートネットワークのみに接続されているホスト )

#### トラフィックの流れ

```mermaid
graph TD
    I([外部ゲートウェイ<br/>192.168.20.1])
    J([外部ホスト<br/>192.168.20.100])
    subgraph ExtNet["外部ネットワーク (192.168.20.0/24)"]
    end

    subgraph Router["ルータホスト"]
        B["mgmt_nic: ens160<br/>192.168.20.10"]
        C["FORWARD<br/>パケット転送<br/>iptables/ip6tables"]
        C2["MASQUERADE<br/>送信元アドレス変換 (SNAT)<br/>iptables/ip6tables"]
        D["gpm_mgmt_nic: ens192<br/>192.168.30.10"]
        B --> C
        C --> D
        D -.->|内部->外部| C2
        C2 -.-> B
    end

    subgraph IntNet["内部プライベートネットワーク (192.168.30.0/24)"]
    end

    F([内部ホスト<br/>192.168.30.41])

    I --- ExtNet
    J --- ExtNet
    ExtNet <-->|パケット転送| B
    D <-->|パケット転送| IntNet

    IntNet --- F

    classDef hostStyle fill:#e1f5ff,stroke:#333,stroke-width:2px
    classDef nicStyle fill:#d4edda,stroke:#333,stroke-width:2px
    classDef controlStyle fill:#fff3cd,stroke:#333,stroke-width:2px
    classDef networkStyle fill:#f0f0f0,stroke:#666,stroke-width:2px

    class F,I,J hostStyle
    class B,D nicStyle
    class C,C2 controlStyle
    class ExtNet,IntNet networkStyle
```

### 2. 共通検証

#### 2.1 sysctl 設定確認

**実施ノード**: ルータホスト

**コマンド**:
```bash
cat /etc/sysctl.d/95-ipfoward.conf
sysctl net.ipv4.ip_forward net.ipv4.conf.all.rp_filter net.ipv6.conf.all.forwarding
```

**期待される出力例**:
```bash
$ cat /etc/sysctl.d/95-ipfoward.conf
#
#  -*- coding:utf-8 mode:bash -*-
# This file is generated by ansible.
# last update: 2026-03-01 15:19:44 JST

#
# IPv4 Forwarding設定
#
# ipv4フォワーディングを有効化
net.ipv4.ip_forward=1
# ソースルーティングパケットの処理設定を変更
# Reverse Path Filtering（RPF）をルーズモードに設定し,
# 受信パケットのソースアドレスが, どのネットワークインターフェースからでも
# 到達可能であればパケットを受け入れる。
net.ipv4.conf.all.rp_filter=2
# デフォルトインターフェースのソースルーティングパケットの処理設定を
# Reverse Path Filtering（RPF）をルーズモードに設定することで,
# 作成されるネットワークインターフェースのデフォルトのRP_Filter値を
# ルーズモードにする。
net.ipv4.conf.default.rp_filter=2

#
# IPv6 Forwarding設定
#
# ipv6フォワーディングを有効化
net.ipv6.conf.all.forwarding=1
# デフォルトインターフェースのipv6フォワーディングを有効化
# 作成されるネットワークインターフェースのデフォルトの
# ipv6フォワーディング値を有効化する。
net.ipv6.conf.default.forwarding=1
# 管理インターフェースでルーター広告(RA)を受け入れる
# フォワーディングが有効でもRAを受け入れるようにする
net.ipv6.conf.ens160.accept_ra=2

$ sysctl net.ipv4.ip_forward net.ipv4.conf.all.rp_filter net.ipv6.conf.all.forwarding
net.ipv4.ip_forward = 1
net.ipv4.conf.all.rp_filter = 2
net.ipv6.conf.all.forwarding = 1
```

**確認ポイント**:
- `/etc/sysctl.d/95-ipfoward.conf` が存在し, ファイル内で以下が設定されていること。
  - `net.ipv4.ip_forward=1` (IPv4 転送有効)
  - `net.ipv4.conf.all.rp_filter=2` (RPF ルーズモード)
  - `net.ipv6.conf.all.forwarding=1` (IPv6 転送有効)
- `sysctl` コマンドで実行中カーネルの値が以下と一致すること。
  - `net.ipv4.ip_forward = 1`
  - `net.ipv4.conf.all.rp_filter = 2`
  - `net.ipv6.conf.all.forwarding = 1`

#### 2.2 永続化状態確認

**実施ノード**: ルータホスト

**コマンド** (Debian/Ubuntu の場合):
```bash
systemctl status netfilter-persistent
systemctl is-enabled netfilter-persistent
```

**期待される出力例** (Debian/Ubuntu):
```bash
$ systemctl status netfilter-persistent
● netfilter-persistent.service - netfilter persistent configuration
     Loaded: loaded (/usr/lib/systemd/system/netfilter-persistent.service; enabled; preset: enabled)
    Drop-In: /usr/lib/systemd/system/netfilter-persistent.service.d
             └─iptables.conf
     Active: active (exited) since Sun 2026-03-01 15:28:31 JST; 5 days ago
       Docs: man:netfilter-persistent(8)
   Main PID: 571 (code=exited, status=0/SUCCESS)
        CPU: 13ms

 3月 01 15:28:31 router systemd[1]: Starting netfilter-persistent.service - netfilter persistent configuration...
 3月 01 15:28:31 router netfilter-persistent[592]: run-parts: executing /usr/share/netfilter-persistent/plugins.d/15-ip4tables start
 3月 01 15:28:31 router netfilter-persistent[592]: run-parts: executing /usr/share/netfilter-persistent/plugins.d/25-ip6tables start
 3月 01 15:28:31 router systemd[1]: Finished netfilter-persistent.service - netfilter persistent configuration.

$ systemctl is-enabled netfilter-persistent
enabled
```

**確認ポイント** (Debian/Ubuntu):
- サービスが `Active: active (exited)` 状態であること (正常終了を示す)。
- `Loaded:` 行に `enabled` が含まれ, システム起動時の自動起動が有効であること。
- `systemctl is-enabled` コマンドで `enabled` が返ること。

**コマンド** (Red Hat系 の場合):
```bash
sudo systemctl status iptables
sudo systemctl status ip6tables
sudo systemctl is-enabled iptables
sudo systemctl is-enabled ip6tables
```

**確認ポイント** (Red Hat系):
- `iptables`, `ip6tables` サービスが `Active: active (running)` であること。
- 両サービスが `enabled` で自動起動が有効であること。

### 3. 純粋ルーティング構成の検証 (config-forward.yml)

#### 3.1 FORWARD ルール確認

**実施ノード**: ルータホスト

**コマンド**:
```bash
sudo iptables -L FORWARD -nv --line-numbers
sudo ip6tables -L FORWARD -nv --line-numbers
```

**期待される出力例** (純粋ルーティングモードの場合):
```bash
$ sudo iptables -L FORWARD -nv --line-numbers
Chain FORWARD (policy DROP 0 packets, 0 bytes)
num   pkts bytes target     prot opt in     out     source               destination
1      22M   60G DOCKER-USER  0    --  *      *       0.0.0.0/0            0.0.0.0/0
2      22M   60G DOCKER-FORWARD  0    --  *      *       0.0.0.0/0            0.0.0.0/0
3    8457K  492M ACCEPT     0    --  ens192   ens160    192.168.30.0/24      0.0.0.0/0
4      14M   60G ACCEPT     0    --  ens160   ens192    0.0.0.0/0            192.168.30.0/24      ctstate RELATED,ESTABLISHED
5        0     0 ACCEPT     0    --  ens160   ens192    0.0.0.0/0            192.168.30.0/24

$ sudo ip6tables -L FORWARD -nv --line-numbers
Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
num   pkts bytes target     prot opt in     out     source               destination
1     8938 1001K DOCKER-USER  0    --  *      *       ::/0                 ::/0
2     8938 1001K DOCKER-FORWARD  0    --  *      *       ::/0                 ::/0
3     4486  390K ACCEPT     0    --  ens192   ens160    fdad:ba50:248b:1::/64  ::/0
4     4449  611K ACCEPT     0    --  ens160   ens192    ::/0                 fdad:ba50:248b:1::/64  ctstate RELATED,ESTABLISHED
5        0     0 ACCEPT     0    --  ens160   ens192    ::/0                 fdad:ba50:248b:1::/64
```

**確認ポイント**:
- IPv4 FORWARD チェーンで以下のルールが存在すること。
  - 行 3: 内部 (`ens192`) から外部 (`ens160`) への, 内部プライベート IPv4 ネットワーク (`192.168.30.0/24`) からのパケットを `ACCEPT`
  - 行 4-5: 外部 (`ens160`) から内部 (`ens192`) への, 内部プライベート IPv4 ネットワーク宛 (`192.168.30.0/24`) のパケットを `ACCEPT` (行4の`ESTABLISHED,RELATED` は既存接続とその戻り通信(`ESTABLISHED`), または関連通信(`RELATED`)を許可し, 行 5 で新規接続を許可)
- IPv6 FORWARD チェーンで以下のルールが存在すること。
  - 行 3: 内部 (`ens192`) から外部 (`ens160`) への, 内部プライベート IPv6 ネットワーク (`fdad:ba50:248b:1::/64`) からのパケットを `ACCEPT`
  - 行 4-5: 外部 (`ens160`) から内部 (`ens192`) への, 内部プライベート IPv6 ネットワーク宛 (`fdad:ba50:248b:1::/64`) のパケットを `ACCEPT` (行4の`ESTABLISHED,RELATED` は既存接続とその戻り通信(`ESTABLISHED`), または関連通信(`RELATED`)を許可し, 行 5 で新規接続を許可)
- 疎通試験の実行前後で同じコマンドを少なくとも 2 回実行し, `pkts` (パケット数) と `bytes` (バイト数) のカウンタが増加していることを確認することで, 実際にトラフィックが転送されていることを確認。

#### 3.2 NAT 不在確認

**実施ノード**: ルータホスト

**コマンド**:
```bash
sudo iptables -t nat -L POSTROUTING -nv --line-numbers
sudo ip6tables -t nat -L POSTROUTING -nv --line-numbers
```

**期待される出力例** (純粋ルーティングモードの場合):
```bash
$ sudo iptables -t nat -L POSTROUTING -nv --line-numbers
Chain POSTROUTING (policy ACCEPT 808 packets, 65136 bytes)
num   pkts bytes target     prot opt in     out     source               destination
1        0     0 MASQUERADE  0    --  *      !docker0  172.17.0.0/16        0.0.0.0/0

$ sudo ip6tables -t nat -L POSTROUTING -nv --line-numbers
Chain POSTROUTING (policy ACCEPT 21 packets, 2822 bytes)
num   pkts bytes target     prot opt in     out     source               destination
```

**確認ポイント**:
- 純粋ルーティングモードでは, 管理対象の内部プライベートネットワーク IPv4 (`192.168.30.0/24`) と IPv6 (`fdad:ba50:248b:1::/64`) に対する MASQUERADE ルールが存在しないこと。
- Docker 関連の MASQUERADE ルール (例: `172.17.0.0/16`) は存在しても問題なし (Docker が独自に管理)。

#### 3.3 疎通確認 (送信元保持)

**実施ノード**: 外部ホスト (外部ゲートウェイと同一L2ネットワーク上に設置されているホスト, `192.168.20.100`)

**コマンド**:
```bash
ping -c3 192.168.30.41
```

**期待される出力例**:
```bash
$ ping -c3 192.168.30.41
PING 192.168.30.41 (192.168.30.41) 56(84) bytes of data.
64 bytes from 192.168.30.41: icmp_seq=1 ttl=63 time=0.64 ms
64 bytes from 192.168.30.41: icmp_seq=2 ttl=63 time=0.58 ms
64 bytes from 192.168.30.41: icmp_seq=3 ttl=63 time=0.61 ms

--- 192.168.30.41 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 0.580/0.610/0.640/0.025 ms
```

**確認ポイント**:
- 外部向けネットワークのホストから内部ホスト (`192.168.30.41`) への通信が成功すること。
- `3 packets transmitted, 3 received, 0% packet loss` で全パケットが到達していること。
- 応答が返ってくること (`64 bytes from 192.168.30.41`) で, ルーティングが正常に機能していることを確認。
- 送信元 IP が NAT 変換されず保持されること (tcpdump で確認)。

### 4. NAT 構成の検証 (config-nat.yml)

#### 4.1 FORWARD, POSTROUTING ルール確認

**実施ノード**: ルータホスト

**コマンド**:
```bash
sudo iptables -L FORWARD -nv --line-numbers | grep -E "ens|Chain"
sudo iptables -t nat -L POSTROUTING -nv --line-numbers | grep -E "MASQUERADE|Chain"
sudo ip6tables -L FORWARD -nv --line-numbers | grep -E "ens|Chain"
sudo ip6tables -t nat -L POSTROUTING -nv --line-numbers | grep -E "MASQUERADE|Chain"
```

**期待される出力例** (NAT モードの場合):
```bash
$ sudo iptables -L FORWARD -nv --line-numbers | grep -E "ens|Chain"
Chain FORWARD (policy DROP 197 packets, 19012 bytes)
3    8457K  492M ACCEPT     0    --  ens192   ens160    192.168.30.0/24      0.0.0.0/0
4      14M   60G ACCEPT     0    --  ens160   ens192    0.0.0.0/0            192.168.30.0/24      ctstate RELATED,ESTABLISHED
5        0     0 ACCEPT     0    --  ens160   ens192    0.0.0.0/0            192.168.30.0/24

$ sudo iptables -t nat -L POSTROUTING -nv --line-numbers | grep -E "MASQUERADE|Chain"
Chain POSTROUTING (policy ACCEPT 808 packets, 65136 bytes)
1        0     0 MASQUERADE  0    --  *      !docker0  172.17.0.0/16        0.0.0.0/0
2     174K   13M MASQUERADE  0    --  *      ens160    192.168.30.0/24      0.0.0.0/0

$ sudo ip6tables -L FORWARD -nv --line-numbers | grep -E "ens|Chain"
Chain FORWARD (policy ACCEPT 3 packets, 264 bytes)
3     4486  390K ACCEPT     0    --  ens192   ens160    fdad:ba50:248b:1::/64  ::/0
4     4449  611K ACCEPT     0    --  ens160   ens192    ::/0                 fdad:ba50:248b:1::/64  ctstate RELATED,ESTABLISHED
5        0     0 ACCEPT     0    --  ens160   ens192    ::/0                 fdad:ba50:248b:1::/64

$ sudo ip6tables -t nat -L POSTROUTING -nv --line-numbers | grep -E "MASQUERADE|Chain"
Chain POSTROUTING (policy ACCEPT 21 packets, 2822 bytes)
1     2469  214K MASQUERADE  0    --  *      ens160    fdad:ba50:248b:1::/64  ::/0
```

**確認ポイント**:
- **IPv4 FORWARD ルール**: 内部プライベート IPv4 ネットワーク (`192.168.30.0/24`) から外部 (`ens160`) への転送, および戻りトラフィックの ACCEPT ルールが存在すること。
- **IPv4 POSTROUTING MASQUERADE**: 行 2 で内部プライベート IPv4 ネットワーク (`192.168.30.0/24`) から `ens160` への送信パケットに MASQUERADE が適用されていること。疎通試験中に同じコマンドを2回実行し, `pkts` カウンタ (例: `174K`) が増加していることを確認することで NAT 変換が実行されていることを確認します。
- **IPv6 FORWARD ルール**: 内部プライベート IPv6 ネットワーク (`fdad:ba50:248b:1::/64`) から外部への転送ルールが存在すること。
- **IPv6 POSTROUTING MASQUERADE**: 行 1 で内部プライベート IPv6 ネットワーク (`fdad:ba50:248b:1::/64`) から `ens160` への送信パケットに MASQUERADE が適用されていること。

#### 4.2 疎通確認 (NAT 変換)

**実施ノード**: 内部プライベートネットワークのホスト

**コマンド**:
```bash
ping -c3 8.8.8.8
```

**期待される出力例**:
```bash
$ ping -c3 8.8.8.8
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=5.14 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=117 time=5.84 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=117 time=4.70 ms

--- 8.8.8.8 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2001ms
rtt min/avg/max/mdev = 4.697/5.226/5.841/0.470 ms
```

**確認ポイント**:
- 内部ホスト (`192.168.30.41`) から外部インターネット (`8.8.8.8`) への通信が成功すること。
- `3 packets transmitted, 3 received, 0% packet loss` で全パケットが到達していること。
- 応答が返ってくること (`64 bytes from 8.8.8.8`) で, NAT 変換とルーティングが正常に機能していることを確認。

#### 4.3 tcpdump による SNAT 確認

**実施ノード**: ルータホスト

**前提**: 内部プライベートネットワークのホスト (192.168.30.41) から外部 (例: 8.8.8.8) への ping を実行中。

**コマンド**:
```bash
sudo tcpdump -i ens160 -n icmp and host 8.8.8.8 -c10
```

**期待される出力例**:
```bash
$ sudo tcpdump -i ens160 -n icmp and host 8.8.8.8 -c10
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on ens160, link-type EN10MB (Ethernet), snapshot length 262144 bytes
10:15:23.456789 IP 192.168.20.10 > 8.8.8.8: ICMP echo request, id 12345, seq 1, length 64
10:15:23.461234 IP 8.8.8.8 > 192.168.20.10: ICMP echo reply, id 12345, seq 1, length 64
10:15:24.457890 IP 192.168.20.10 > 8.8.8.8: ICMP echo request, id 12345, seq 2, length 64
10:15:24.462123 IP 8.8.8.8 > 192.168.20.10: ICMP echo reply, id 12345, seq 2, length 64
10:15:25.458901 IP 192.168.20.10 > 8.8.8.8: ICMP echo request, id 12345, seq 3, length 64
10:15:25.463234 IP 8.8.8.8 > 192.168.20.10: ICMP echo reply, id 12345, seq 3, length 64
6 packets captured
```

**確認ポイント**:
- **送信元アドレスの変換**: 外部インターフェース (`ens160`) で観測されるパケットの送信元 IP が, 内部ホスト (`192.168.30.41`) ではなく, ルータの外部 NIC IP (`192.168.20.10`) に変換されていること。
- **MASQUERADE 動作**: ICMP echo request の送信元がルータの外部 NIC IP (`192.168.20.10`) になっていることで, SNAT (MASQUERADE) が正常に機能していることを確認。
- **戻りトラフィック**: ICMP echo reply の宛先がルータの外部 NIC IP (`192.168.20.10`) で, ルータが NAT 変換テーブルを使って内部ホストへ正しく転送していることを確認。

### 5. 意図的にパケット転送を無効化している場合

#### 5.1 ルール未設定確認

**実施ノード**: ルータホスト

**コマンド**:
```bash
sudo iptables -L FORWARD -nv --line-numbers | grep -E "192.168.30|Chain"
sudo iptables -t nat -L POSTROUTING -nv --line-numbers | grep -E "192.168.30|Chain"
```

**期待される出力例** (転送無効化の場合):
```bash
$ sudo iptables -L FORWARD -nv --line-numbers | grep -E "192.168.30|Chain"
Chain FORWARD (policy DROP 0 packets, 0 bytes)
(192.168.30 に関連するルールが表示されない)

$ sudo iptables -t nat -L POSTROUTING -nv --line-numbers | grep -E "192.168.30|Chain"
Chain POSTROUTING (policy ACCEPT 808 packets, 65136 bytes)
(192.168.30 に関連するルールが表示されない)
```

**確認ポイント**:
- FORWARD チェーンに, 内部プライベート IPv4 ネットワーク (`192.168.30.0/24`) に関連する ACCEPT ルールが存在しないこと。
- POSTROUTING チェーンに, 内部プライベート IPv4 ネットワーク (`192.168.30.0/24`) に対する MASQUERADE ルールが存在しないこと。
- Docker 関連のルールは存在しても問題なし (別途管理されている)。

#### 5.2 ルール残骸がある場合の対処

**実施条件**: 設定変更後にルールが残っている場合。

**実施ノード**: ansible-playbookコマンドを実行するホスト (Ansible 制御ホスト)

**コマンド**:
```bash
# 既存ルールをクリア
make run_router_clear_rules

# 新しい設定を適用
make run_router_config
```

**期待される動作**:
```bash
$ make run_router_clear_rules
ansible-playbook -i inventory/hosts router-clear-rules.yml \
    $(OPT_COMMON) |tee build-router-clear-rules.log
...
TASK [router-config : Clear IPv4 FORWARD rules] ********************************
changed: [router.local]

TASK [router-config : Clear IPv6 FORWARD rules] ********************************
changed: [router.local]

TASK [router-config : Clear IPv4 NAT POSTROUTING rules] ************************
changed: [router.local]

TASK [router-config : Clear IPv6 NAT POSTROUTING rules] ************************
changed: [router.local]
...

$ make run_router_config
ansible-playbook -i inventory/hosts site.yml --tags "router-config" \
    $(OPT_COMMON) |tee build-router-config.log
...
PLAY RECAP **********************************************************************
router.local               : ok=15   changed=3    unreachable=0    failed=0
```

**確認ポイント**:
- `run_router_clear_rules` でルール削除タスクが `changed` 状態で実行されること。
- `run_router_config` 実行後, 意図した設定 (転送無効化, 純粋ルーティング, NAT のいずれか) が適用されること。
- 再度 `sudo iptables -L FORWARD -nv` および `sudo iptables -t nat -L POSTROUTING -nv` で確認し, 期待通りのルール構成になっていること。

## トラブルシューティング

実行者はエラー発生時に build-*.log を確認し, 失敗した task 名と不足変数を特定します。

## 注意事項

実行者は既存の実行順依存を崩さないことを確認した上で本ロールを実行します。

## テンプレート / 出力ファイル

| テンプレートまたは生成物 | 出力先 | 説明 |
| --- | --- | --- |
| `templates/95-ipfoward.j2` | `/etc/sysctl.d/95-ipfoward.conf` | IPv4/IPv6 転送, RPF, `accept_ra` を設定します。 |
| 永続化処理 (Debian 系, IPv4) | `/etc/iptables/rules.v4` | `netfilter-persistent save` で IPv4 ルールを保存します。 |
| 永続化処理 (Debian 系, IPv6) | `/etc/iptables/rules.v6` | `netfilter-persistent save` で IPv6 ルールを保存します。 |
| 永続化処理 (Red Hat 系, IPv4) | `{{ etc_default_dir }}/iptables` (`/etc/sysconfig/iptables`) | `iptables-save` の出力先。 |
| 永続化処理 (Red Hat 系, IPv6) | `{{ etc_default_dir }}/ip6tables` (`/etc/sysconfig/ip6tables`) | `ip6tables-save` の出力先。 |

## 補足

### 動作モード

本ロールでルータノードに設定可能な動作モードは以下の通り:

- 純粋なルーティング (デフォルト): NAT 無しの双方向パケット転送 (`config-forward.yml`)。
- NAT 動作: MASQUERADE による送信元アドレス変換 (`config-nat.yml`)。

### 設定値による動作の違い

`enable_firewall` が `false` である前提で, 設定値とルータノードの挙動の対応関係は以下のようになります:

| `router_forwarding_enabled` | `router_nat_enabled` | `additional_network_routes` | 動作 |
| --- | --- | --- | --- |
| `false` | `false` | 未定義, または空リスト | FORWARD/NAT 設定なし |
| `false` | `false` | 長さ 1 以上 | FORWARD 設定を実施 (純粋ルーティング) |
| `false` | `true` | 未定義, または空リスト | SNAT (MASQUERADE) と FORWARD 設定を実施 |
| `false` | `true` | 長さ 1 以上 | 設定値矛盾のため, FORWARD/NAT 設定なし |
| `true` | `false` | 未定義, または空リスト | FORWARD 設定を実施 (純粋ルーティング) |
| `true` | `false` | 長さ 1 以上 | FORWARD 設定を実施 (純粋ルーティング) |
| `true` | `true` | 未定義, または空リスト | 設定値矛盾のため, FORWARD/NAT 設定なし |
| `true` | `true` | 長さ 1 以上 | 設定値矛盾のため, FORWARD/NAT 設定なし |

### makeターゲット `run_router_clear_rules`の処理内容

ルータノードで設定している各種ルールを削除するためのmakeターゲットとして, `run_router_clear_rules`ターゲットを用意しています。
本makeターゲット実行時の処理内容は以下の通りです:

- NAT から純粋ルーティングへ切替える前に NAT ルールを削除します。
- 純粋ルーティングから NAT へ切替える前に FORWARD ルールを削除します。
- ルーティング機能を停止する前に, ルール残骸を削除します。
- クリア処理は削除対象ルールが存在しない場合でも `|| true` により継続されます。
- `make run_router_clear_rules` 実行時のログは `build-router-clear-rules.log` に保存されます。
## 参考資料

### 公式ドキュメント

- iptables: https://man7.org/linux/man-pages/man8/iptables.8.html
- ip6tables: https://man7.org/linux/man-pages/man8/ip6tables.8.html
- sysctl: https://man7.org/linux/man-pages/man8/sysctl.8.html
