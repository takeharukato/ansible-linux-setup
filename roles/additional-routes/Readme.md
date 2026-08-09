# additional-routes ロール

本ロールは, 外部ネットワーク(例: VM Network(VMware), Pool-wide network associated with ethX(xcp-ng))につながるサーバから, 仮想環境内部管理ネットワークへの追加ルートを自動設定します。

## 目次

- [additional-routes ロール](#additional-routes-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [追加ルート定義の詳細](#追加ルート定義の詳細)
    - [デフォルト動作](#デフォルト動作)
    - [設定例](#設定例)
  - [実行フロー](#実行フロー)
  - [主な処理](#主な処理)
    - [OS 毎の差異](#os-毎の差異)
      - [Debian/Ubuntu (netplan)](#debianubuntu-netplan)
      - [RHEL (NetworkManager)](#rhel-networkmanager)
  - [検証ポイント](#検証ポイント)
    - [前提条件](#前提条件-1)
    - [1. 追加ルートの確認 (共通)](#1-追加ルートの確認-共通)
    - [2. Debian/Ubuntu(netplan) の設定ファイル確認](#2-debianubuntunetplan-の設定ファイル確認)
    - [3. RHEL(NetworkManager) の設定確認](#3-rhelnetworkmanager-の設定確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. Debian/Ubuntu 系で netplan 適用が失敗する場合](#1-debianubuntu-系で-netplan-適用が失敗する場合)
    - [2. RHEL 系でルートが反映されない場合](#2-rhel-系でルートが反映されない場合)
    - [3. 管理ネットワークインターフェース名が不一致の場合](#3-管理ネットワークインターフェース名が不一致の場合)
  - [注意事項](#注意事項)
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
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| アプリケーション | - | 利用者の目的を実現するために動作するソフトウェア。 |
| パッケージ | - | ソフトウェア導入に必要なファイルをまとめた配布単位。 |
| リポジトリ | - | ソフトウェアや設定情報を保管し, 取得できるようにした管理場所。 |
| コマンド | - | 実行者が計算機へ処理を指示するための命令。 |
| ホスト | - | 管理対象として識別される個別の計算機。 |
| サーバ | - | 他の機器や利用者へ機能やデータを提供する計算機, 又はその役割。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
| ネットワーク | - | 機器同士を接続してデータをやり取りする仕組み。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
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
| Network Interface Card | NIC | 計算機をネットワークへ接続するための装置または機能。 |
| NetworkManager | - | RHEL 系でネットワークを管理するサービス。 |
| netplan | - | Debian/Ubuntu 系でネットワーク設定を生成する仕組み。 |
| route | - | 宛先ネットワークに到達するための経路。 |
| metric | - | ルート優先度を示す数値。 |
| Classless Inter-Domain Routing | CIDR | IP アドレスとネットワークプレフィックス長を組み合わせた表記法。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Red Hat Enterprise Linux | RHEL | Red Hatが提供する企業向けLinuxディストリビューション。 |
| Red Hat Enterprise Linux 9 | RHEL9 | Red Hat Enterprise Linux の第9系統版。 |
| Secure Shell | SSH | 遠隔の計算機へ安全に接続して操作する方式。 |
| Virtual Machine | VM | 物理計算機上で動作する仮想的な計算機。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| ipコマンド | - | ネットワーク設定や経路情報の確認, 変更を行うコマンド。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| リモートホスト | - | ネットワーク越しに接続して操作する別ホスト。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |
## 概要

このロールは, 外部ネットワーク(例: VM Network(VMware), Pool-wide network associated with ethX(xcp-ng))につながるサーバから, 仮想環境内部管理ネットワークへの追加ルートを自動設定します。Debian/Ubuntu 系は netplan, RHEL 系は NetworkManager を利用します。

## 前提条件

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- Ansible 2.15 以降, ansibleメタパッケージをディストリビューションから導入していることを想定
- `mgmt_nic` が正しく設定されていること

## 実行方法

単体で実行する場合は, 制御ホストで以下のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts site.yml --tags "additional-routes"
```

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `additional_network_routes` | `[]` | 追加ルート定義リスト。リストが空の場合は, 追加ルート設定処理を行わない。 |
| `mgmt_nic` | なし | ルートを適用する接続/インターフェース名。`group_vars/all/all.yml` で自動設定。 |

## テンプレートと生成ファイル

本ロールでは以下のファイルを出力します。

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `templates/30-additional-routes.yaml.j2` | `/etc/netplan/30-additional-routes.yaml` (既定: `/etc/netplan/30-additional-routes.yaml`) | netplan v2 形式の追加ルート設定。 |

## 追加ルート定義の詳細

`additional_network_routes` 変数は, 以下のキーを持つ辞書を要素とするリストです:

| キー | 必須 | 説明 |
| --- | --- | --- |
| `address_family` | 必須 | `ipv4` または `ipv6` を指定。 |
| `destination` | 必須 | 宛先ネットワーク(CIDR)。 |
| `gateway` | 必須 | ゲートウェイアドレス。 |
| `metric` | 任意 | メトリック値。 |

### デフォルト動作

- `additional_network_routes` が未定義または空配列の場合, 追加ルート設定は実行しない。

### 設定例

追加ルートを IPv4 と IPv6 の両方で設定する例です。記載先は, 変数ファイルです。

**記載先**:
- host_vars/ホスト名.yml または group_vars/all/all.yml

**記載例**:

```yaml
additional_network_routes:
  - address_family: "ipv4"
    destination: "192.168.30.0/24"
    gateway: "192.168.30.10"
  - address_family: "ipv6"
    destination: "fdad:ba50:248b:1::/64"
    gateway: "fdad:ba50:248b:1::10"
    metric: 100
```

**各項目の意味**:

| 項目 | 説明 | 記載例での値 | 動作 |
| --- | --- | --- | --- |
| `additional_network_routes` | 追加ルート定義のリストです。 | `[{...}, {...}]` | 指定したルートが追加されます。空配列の場合は追加ルート設定を行いません。 |
| `address_family` | `ipv4` または `ipv6` を指定します。 | `ipv4`, `ipv6` | `ipv4` は IPv4 ルート, `ipv6` は IPv6 ルートとして扱われます。 |
| `destination` | 宛先ネットワーク(CIDR)です。 | `192.168.30.0/24`, `fdad:ba50:248b:1::/64` | 指定した宛先ネットワークに対するルートが作成されます。 |
| `gateway` | ゲートウェイアドレスです。 | `192.168.30.10`, `fdad:ba50:248b:1::10` | 指定したゲートウェイ経由のルートになります。 |
| `metric` | ルートの優先度を表すメトリックです。 | `100` | 数値が小さいほど優先度が高くなります。指定しない場合は OS の既定値に従います。 |

## 実行フロー

## 主な処理

本ロールは tasks/main.yml から次の task を順に呼び出す。

1. `load-params.yml` で OS 別変数と共通変数を読み込む。
2. `config.yml` で `additional_network_routes` の有無を確認し, OS 別の設定タスクへ分岐します。
3. Debian/Ubuntu 系は `config-ubuntu-add-routes.yml` で netplan 設定を生成し, `netplan generate` で文法を検証し, 変更時に `netplan apply` を実行します。
4. RHEL 系は `config-rhel-add-routes.yml` で `nmcli` の route 設定を更新し, `nmcli connection up` で反映します。

### OS 毎の差異

#### Debian/Ubuntu (netplan)

- `templates/30-additional-routes.yaml.j2` から `/etc/netplan/30-additional-routes.yaml` を生成します。
- `netplan generate` で文法検証を行い, テンプレートに変更がある場合のみ `netplan apply` を実行します。
- 各 route について, gateway への on-link ルートと destination へのルートを追加します。

#### RHEL (NetworkManager)

- `nmcli connection modify <mgmt_nic> ipv4.routes/ipv6.routes` で route 一覧を上書き設定します。
- `additional_network_routes` から `address_family: ipv4` の要素が 0 件の場合, `ipv4.routes` に空文字を設定して既存の IPv4 ルートを消去します。同様に, `address_family: ipv6` の要素が 0 件の場合は `ipv6.routes` に空文字を設定して既存の IPv6 ルートを消去します。
- `nmcli connection up <mgmt_nic>` で設定を反映します。

## 検証ポイント

本節では, `additional-routes` ロール実行後に追加ルートが反映されていることを確認します。

### 前提条件

- `additional-routes` ロールが正常に完了していること (`changed` または `ok` の状態)。
- リモートホストへ SSH で接続可能であること。
- sudo 権限が利用可能であること。

### 1. 追加ルートの確認 (共通)

IPv4/IPv6 の追加ルートが反映されていることを確認します。

```bash
ip route
ip -6 route
```

**期待される出力例**:

```
192.168.30.0/24 via 192.168.30.10 dev ens160 metric 100
fdad:ba50:248b:1::/64 via fdad:ba50:248b:1::10 dev ens160 metric 100
```

**確認ポイント**:
- `additional_network_routes` で指定した宛先ネットワークとゲートウェイが表示されること。

### 2. Debian/Ubuntu(netplan) の設定ファイル確認

netplan 設定ファイルが配置されていることを確認します。

```bash
ls -l /etc/netplan/30-additional-routes.yaml
```

**確認ポイント**:
- `/etc/netplan/30-additional-routes.yaml` が存在すること。

### 3. RHEL(NetworkManager) の設定確認

NetworkManager に登録されたルートを確認します。

```bash
nmcli -f connection.id,ipv4.routes,ipv6.routes connection show "${mgmt_nic}"
```

**確認ポイント**:
- `ipv4.routes`/`ipv6.routes` に追加ルートが表示されること。

## トラブルシューティング

### 1. Debian/Ubuntu 系で netplan 適用が失敗する場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
sudo netplan generate
sudo netplan apply
sudo ls -l /etc/netplan/30-additional-routes.yaml
```

**確認ポイント**:

- `netplan generate` がエラーなく完了すること。
- `/etc/netplan/30-additional-routes.yaml` が存在すること。
- `additional_network_routes` の `destination` と `gateway` が CIDR 形式およびアドレス形式として有効であること。

### 2. RHEL 系でルートが反映されない場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
nmcli -f connection.id,ipv4.routes,ipv6.routes connection show "${mgmt_nic}"
sudo nmcli connection up "${mgmt_nic}"
ip route
ip -6 route
```

**確認ポイント**:

- `nmcli` の表示に `additional_network_routes` で指定した経路が反映されること。
- `ip route` と `ip -6 route` に想定経路が表示されること。
- `address_family` の片系のみを定義した場合は, 未定義側の既存経路がクリアされる挙動を考慮していること。

### 3. 管理ネットワークインターフェース名が不一致の場合

**実施対象ホスト**: 制御ホスト, 対象ホスト

**実行するコマンド**:

```bash
ansible -i inventory/hosts all -m debug -a "var=mgmt_nic"
ip link
nmcli connection show
```

**確認ポイント**:

- `mgmt_nic` の値が対象ホスト上に実在する接続名又はインターフェース名であること。
- RHEL 系では `nmcli connection show` の接続名と一致していること。
- Debian/Ubuntu 系では実在するインターフェース名に対して netplan が生成されていること。

## 注意事項

- 本ロールは既存のルート設定を書き換えるため, 実行前に対象ホストの現行ルートを `ip route` と `ip -6 route` で確認し, 復旧手順を事前に準備してください。
- RHEL 系では `additional_network_routes` で指定していないアドレス系の既存ルートがクリアされるため, 運用で必要な経路を漏れなく定義し, 変更後に `nmcli connection show` で反映結果を確認してください。
- Debian/Ubuntu 系では netplan 設定生成後の `netplan apply` により通信経路が即時反映されるため, 作業時間帯は業務影響が許容できる時間であることを確認してください。
- `mgmt_nic` の誤設定は管理ネットワーク到達性の喪失につながるため, 実行前に対象ホストで `ip -o link show` 又は `nmcli connection show` を実行し, 接続名又はインターフェース名が一致していることを確認してください。
- `additional_network_routes` の `destination` と `gateway` は環境変更時に陳腐化しやすいため, ネットワーク変更作業の都度, 変数定義の見直しと再検証を実施してください。

## 参考資料

### 公式ドキュメント

- [ip-route(8)](https://man7.org/linux/man-pages/man8/ip-route.8.html)
- [ip(8)](https://man7.org/linux/man-pages/man8/ip.8.html)
- [route(8)](https://man7.org/linux/man-pages/man8/route.8.html)
- [nmcli(1)](https://networkmanager.dev/docs/api/latest/nmcli.html)
- [netplan reference](https://netplan.readthedocs.io/en/stable/reference/)
