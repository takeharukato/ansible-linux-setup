# frr-basic ロール

本ロールは FRRouting (FRR) をインストールし, ルーティング機能を提供するホストで最低限必要となるシステム設定と FRR 本体の初期構成を適用します。

## 目次

- [frr-basic ロール](#frr-basic-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
    - [データセンタ間でのBGPルーティングに関する前提](#データセンタ間でのbgpルーティングに関する前提)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
    - [host\_varsファイルでの設定例](#host_varsファイルでの設定例)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
  - [主な処理](#主な処理)
  - [検証ポイント](#検証ポイント)
    - [IPv6 でピアが張れていることの検証手順](#ipv6-でピアが張れていることの検証手順)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. FRR サービスが起動しない場合](#1-frr-サービスが起動しない場合)
    - [2. frr-basic ロールを実行しても処理が進まない場合](#2-frr-basic-ロールを実行しても処理が進まない場合)
    - [3. BGP ピアが Established にならない場合](#3-bgp-ピアが-established-にならない場合)
    - [4. IPv6 ピア向けの接続確認に失敗する場合](#4-ipv6-ピア向けの接続確認に失敗する場合)
    - [5. frr-common 呼び出し時のパッケージ導入で失敗する場合](#5-frr-common-呼び出し時のパッケージ導入で失敗する場合)
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
| Pod | - | Kubernetes でコンテナをまとめて管理する最小単位。 |
| Linux | - | 多くの機器で使われる, 基本ソフトウェアの系統。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| Free Range Routing | FRR | 複数の経路制御方式を実装したオープンソースの経路制御ソフトウェア。 |
| Border Gateway Protocol | BGP | 自律システム間で経路情報を交換する経路制御方式。 |
| Internet Protocol | IP | ネットワーク上で宛先を識別し, データを届けるための通信手順。 |
| Autonomous System | AS | 単一の管理主体で運用されるネットワークのまとまり。 |
| Autonomous System Number | ASN | インターネット上で各組織や管理ドメインを識別するために割り当てられる一意の番号。BGP でルーティング情報を交換する際の識別子として使用される。 |
| Internal BGP | iBGP | 同一自律システム内の BGP ルータ間で経路情報を交換するための BGP の動作モード。AS 番号が同じルータ間で使用される。 |
| External BGP | eBGP | 異なる自律システム間で経路情報を交換するための BGP の動作モード。AS 番号が異なるルータ間で使用される。 |
| Classless Inter-Domain Routing | CIDR | IP アドレスとネットワークプレフィックス長を組み合わせた表記法。 |
| Internet Protocol version 4 | IPv4 | 32 ビットアドレス空間を持つインターネットプロトコル。現在最も広く使用されているバージョン。 |
| Internet Protocol version 6 | IPv6 | 128 ビットアドレス空間を持つ次世代インターネットプロトコル。IPv4 アドレス枯渇問題を解決します。 |
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Debian | - | コミュニティ主導で開発される Linux ディストリビューション。 |
| Ubuntu | - | Canonical が提供する Debian 系の Linux ディストリビューション。 |
| Open Shortest Path First | OSPF | ルータ同士が内部ネットワークの到達経路を交換するための経路制御方式。 |
| Routing Information Protocol | RIP | ホップ数を基準に経路を選択する, 比較的単純な経路制御方式。 |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウェア。 |
| Data Center | DC | サーバやネットワーク機器を集約して運用する拠点。 |
| Gateway | GW | 他のネットワークへ通信を中継する装置。 |
| Pod Classless Inter-Domain Routing | Pod CIDR | Kubernetes の Pod に割り当てる IP アドレス範囲。 |
| Router Identifier | Router-ID | BGP ルータを識別するための 32 ビット識別値。通常は IPv4 形式で設定する値。 |
| Transmission Control Protocol | TCP | 通信相手との接続を確立してからデータを送受信する通信方式。 |
| Layer 3 | L3 | IP アドレスを使って宛先までの経路を判断する通信層。 |
| Network Layer Reachability Information | NLRI | BGP で交換する到達可能な経路情報。 |
| Request for Comments | RFC | インターネット技術の仕様を公開する文書体系。 |
| Established | ESTABLISHED | BGP の状態表示で, 接続相手との経路交換が可能な状態を示す文字列。 |
| Ansible Playbook | playbook | 自動化処理の実行手順を順序付きで記述したファイル。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| Ansible Handler | handler | 設定変更時など特定条件でのみ実行する後続処理。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Red Hat Enterprise Linux | RHEL | Red Hatが提供する企業向けLinuxディストリビューション。 |
| systemd | - | Linux システムの初期化とサービス管理を行う仕組み。 |
| Cluster 1 | C1 | 文書内で第1クラスタを示す識別名。 |
| Identifier | ID | 対象を一意に識別するための値。 |
| Python | - | スクリプティングやアプリケーション開発を手早く実施するために用いられる高水準プログラミング言語の一種。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
| サービス | - | 機能を利用者や他システムへ提供する仕組み。 |
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| ipコマンド | - | ネットワーク設定や経路情報の確認, 変更を行うコマンド。 |
| makeコマンド | make | Makefile に定義された処理を実行するコマンド。 |
| `nc` | - | 任意ポートへの接続可否を確認するコマンド。 |
| `ping6` | - | IPv6 宛先への到達性と往復遅延を確認するコマンド。 |
| `sysctl` | - | カーネル動作パラメタを参照, 変更するコマンド。 |
| `systemctl` | - | systemd 管理下のサービスを起動, 停止, 状態確認するコマンド。 |
| `vtysh` | - | FRR の統合操作シェルで設定や状態確認を行うコマンド。 |

## 概要

このロールは FRRouting (FRR) をインストールし, ルーティング機能を提供するホストで最低限必要となるシステム設定と FRR 本体の初期構成を適用します。Debian/Ubuntu 系および Red Hat 系ディストリビューションを対象としており, `ansible-playbook` を実行する制御ノードから対象ホストへ以下の作業を行います。
- FRR 関連パッケージ (`frr`, `frr-pythontools` など) の導入
- FRR サービスの有効化と起動 (`systemd`)
- `/etc/sysctl.d/90-frr-forwarding.conf` を配布し, IPv4/IPv6 のカーネルフォワーディングを有効化
- `/etc/frr/daemons` を配布し, `zebra` / `bgpd` を有効化
- `frr.conf.j2` テンプレートを展開して `/etc/frr/frr.conf` を生成し, BGP 設定などを適用
- 設定更新時に `sysctl --system` や `systemctl restart frr` をハンドラ経由で実行
再実行可能な構成になっており, テンプレート内容に変更が無ければ変更は `changed: false` となります。

## 前提条件

本ロールを適用する前に, 対象ホストが inventory に登録済みであることを確認します。
本ロールを適用する前に, 関連する共通変数が vars/all-config.yml または host_vars に定義済みであることを確認します。

### データセンタ間でのBGPルーティングに関する前提

本ロールでは, データセンタ間のBGPによる経路制御を以下の方針で実現することを前提として, FRR<=>K8sコントロールプレイン間のBGPルーティングの設定を行います。

1. 各K8sクラスタの Pod CIDR は, データセンタ(DC) 全体でユニークです (重複しません)。
2. 各K8sクラスタの BGP 広告ノード (本リポジトリでは K8s コントロールプレインノードを想定します。構成によりワーカーノードを代表としてもよいですが, その場合は FRR の iBGP ピアとしてそのワーカーノードを設定します) が, 自K8sクラスタの PodCIDR を BGP で広告し, DC ルータ(FRR)がそれを学習して "宛先 PodCIDR => 次ホップ(宛先PodCIDR を広告したBGP広告ノード)" の経路を持ちます。
3. DC 間は iBGP で宛先PodCIDR へのルートを伝播し, 相互に到達可能とします。
4. K8sノードが宛先 PodCIDR を知らない場合でも, 未知宛先の PodCIDR 向けトラフィックが DC ルータ(FRR) へ到達できるように, デフォルトルートまたは DC 全体の PodCIDR を包含する集約プレフィックスへのルートの次ホップを DC ルータ(FRR) に向けて設定しておきます。

上記4.については,

- 0.0.0.0/0 のデフォルトルート, または
- "遠隔PodCIDR全部を包含する"ような集約ルート

が存在し, K8sノードから DC ルータ(FRR) へ転送できることが必要です。

例えば, (複数のK8sクラスタ含む)DC全体の PodCIDR がたとえば 10.128.0.0/9 の範囲に収まる設計なら, 各K8sノードは細かい /16 や /24 を知らなくても 10.128.0.0/9 の次ホップを DC ルータ(FRR) にする静的経路を設定しておくことで, 未知のPod宛てパケットをDCルータに渡し, BGP経路を通して, 他のDC内のPodと通信できます。

この前提が成立する場合は, 各K8sノードが他DC上にある PodCIDR への経路を BGP で学習して各K8sノード内のカーネルのルーティングテーブルへ反映しなくても, FRR 側で DC 間の経路確立を集約して提供できます。

## 実行方法

制御ホストで以下のコマンドを実行します。

```bash
make run_frr_basic
```

または,

```bash
ansible-playbook -i inventory/hosts site.yml --tags "frr-basic"
```

## 主要変数

`host_vars` で以下の変数を指定します。具体値は環境に合わせて定義してください。

| 変数名 | 意味 | 例 | 必須 | 備考 |
| ------ | ---- | -- | ---- | ---- |
| `frr_basic_enabled` | `frr-basic` ロールを実行するかを制御 | `true` | 任意 | `false` の場合は 本ロールのタスクをスキップします。 |
| `frr_bgp_asn` | BGP 自律システム (Autonomous System - ASと略す)番号 | `65011` | 必須 | `frr.conf`を生成する`frr.conf.j2` テンプレートで使用。 |
| `frr_bgp_router_id` | BGP Router-ID | `192.168.30.49` | 必須 | BGPセッションで使用するIPv4アドレスを指定します。IPv4 形式で指定。`frr.conf`を生成する`frr.conf.j2` テンプレートで使用。 |
| `frr_ibgp_neighbors` | iBGP ピア情報のリスト | `[{ addr: '192.168.30.41', asn: 65011, desc: 'C1 control-plane' }, ...]` | 任意 | `addr` は IPv4/IPv6 どちらでも指定可能。`frr.conf`を生成する`frr.conf.j2` テンプレートで使用。 |
| `frr_ebgp_neighbors` | eBGP ピア情報のリスト | `[{ addr: '192.168.90.1', asn: 65100, desc: 'External GW' }]` | 任意 | `addr` は IPv4/IPv6 どちらでも指定可能。`frr.conf`を生成する`frr.conf.j2` テンプレートで使用。 |
| `frr_networks_v4` | 広告する IPv4 プレフィックス | `['192.168.30.0/24', '192.168.90.0/24']` | 任意 | BGP address-family ipv4 の設定に使用。`frr.conf`を生成する`frr.conf.j2` テンプレートで使用。 |
| `frr_networks_v6` | 広告する IPv6 プレフィックス | `['fd69:6684:61a:2::/64', 'fd69:6684:61a:90::/64']` | 任意 | BGP address-family ipv6 の設定に使用。 `frr.conf`を生成する`frr.conf.j2` テンプレートで使用。 |
| `frr_vtysh_users` | sudo なしで `vtysh` を実行できるユーザ名のリスト | `[]` | 任意 | `frr_vtysh_group` に追加します。 |
| `frr_vtysh_group` | `vtysh` 実行権限を付与するグループ名 | `'frrvty'` | 任意 | Ubuntu/Debian/RHEL などのFRR のパッケージ で設定されている `vtysh` の接続権限を付与するグループを必要に応じて上書きしてください。 |

### host_varsファイルでの設定例

以下は `host_vars/frr01.local` を想定した設定例です。

```text
1  frr_basic_enabled: true
2  frr_bgp_asn: 65011
3  frr_bgp_router_id: "192.168.30.49"
4  frr_ibgp_neighbors:
5    - addr: "192.168.30.41"
6      asn: 65011
7      desc: "C1 control-plane"
8  frr_ebgp_neighbors:
9    - addr: "192.168.90.1"
10     asn: 65100
11     desc: "External GW"
12 frr_networks_v4:
13   - "192.168.30.0/24"
14   - "192.168.90.0/24"
15 frr_networks_v6:
16   - "fd69:6684:61a:2::/64"
17   - "fd69:6684:61a:90::/64"
18 frr_vtysh_users:
19   - "opsuser"
20 frr_vtysh_group: "frrvty"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景 |
| --- | --- | --- | --- |
| 1 | frr_basic_enabled: true | true の場合は FRR サービスを起動し, 192.168.30.41 と 192.168.90.1 に対して TCP/179 の接続試行を開始します。false の場合は FRR 関連タスクを実行せず, 設定ファイルの更新とサービス再起動を行いません。 | false のままでは FRR 関連処理をすべてスキップするためです。 |
| 2-3 | frr_bgp_asn: 65011, frr_bgp_router_id: "192.168.30.49" | 本ノードを AS65011 の BGP ルータとして動作させ, 識別用 IPv4 アドレス 192.168.30.49 を使って接続管理を行います。 | BGP セッション確立に必須の基本情報であるためです。 |
| 4-11 | frr_ibgp_neighbors: [{ addr: "192.168.30.41", asn: 65011, desc: "C1 control-plane" }], frr_ebgp_neighbors: [{ addr: "192.168.90.1", asn: 65100, desc: "External GW" }] | 192.168.30.41 向けは相手AS番号を 65011 として接続条件を設定し, 192.168.90.1 向けは相手AS番号を 65100 として接続条件を設定します。各相手装置から届く接続開始通知に含まれる相手AS番号が, それぞれ設定した値と一致した場合にだけ接続確立状態へ遷移します。接続確立状態へ遷移した後に, 経路の受信学習と送信広告を開始します。 | 対向ピア情報がないと経路交換を開始できないためです。 |
| 12-17 | frr_networks_v4: ["192.168.30.0/24", "192.168.90.0/24"], frr_networks_v6: ["fd69:6684:61a:2::/64", "fd69:6684:61a:90::/64"] | 192.168.30.0/24 と 192.168.90.0/24 は IPv4 の広告対象として扱い, fd69:6684:61a:2::/64 と fd69:6684:61a:90::/64 は IPv6 の広告対象として扱います。各経路が本ノード内で有効な場合, 接続確立状態にある相手装置へ経路情報を送信します。 | 広告対象が未設定の場合, 期待する経路が外部へ広報されないためです。 |
| 18-20 | frr_vtysh_users: ["opsuser"], frr_vtysh_group: "frrvty" | opsuser を frrvty グループへ追加し, 管理者権限への昇格なしで FRR 状態確認コマンドを実行できる状態にします。これにより BGP 接続状態と経路学習結果を即時確認できます。 | 運用ユーザが管理者権限への昇格なしで確認操作を実行できるようにするためです。 |

## テンプレートと生成ファイル

本ロールでは以下のテンプレート / ファイルを出力します:
主な展開先ホストは, 対象ホスト(既定) です。

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `90-frr-forwarding.conf.j2` | `/etc/sysctl.d/90-frr-forwarding.conf` (既定: `/etc/sysctl.d/90-frr-forwarding.conf`) | IPv4/IPv6 転送と関連カーネルパラメタを有効化する sysctl 設定ファイルです。 |
| `frr.conf.j2` | `/etc/frr/frr.conf` (既定: `/etc/frr/frr.conf`) | FRR の経路制御動作(ルーティングプロトコルやポリシー)を定義する設定ファイルです。 |
| `daemons.j2` | `/etc/frr/daemons` (既定: `/etc/frr/daemons`) | FRR で起動する各デーモンの有効/無効を定義する設定ファイルです。 |

## 実行フロー

本ロールは以下の順序で処理を実行します。

1. load-params.yml を実行し, OS種別ごとのパッケージ変数, 共通変数, Kubernetes API 広告アドレス変数を読み込みます。
2. frr_basic_enabled が false の場合, 本ロールの処理をスキップしたことをデバッグメッセージで記録して終了します。
3. frr_basic_enabled が true の場合, package-frr.yml を実行します。frr-common ロールの package.yml を読み込み, `/etc/sysctl.d/90-frr-forwarding.conf`, `/etc/frr/frr.conf`, `/etc/frr/daemons` を配置し, FRR サービスを有効化して起動します。起動失敗時は systemctl と journalctl の情報を採取してplaybookを終了します。
4. frr_basic_enabled が true の場合, user_group.yml を実行します。`frr_vtysh_users` が1件以上ある場合に `frr_vtysh_group` を作成し, 指定ユーザをグループへ追加します。

## 主な処理

本ロールは, FRR の基本導入と BGP ピア設定の反映を行う。

1. OS 別の変数を読み込み, 実行可否と入力値を確認する。
2. FRR パッケージと設定ファイルを適用し, サービスを起動する。
3. 必要に応じて運用ユーザの vtysh 実行権限を整備する。

## 検証ポイント

以下を確認してください。

- 対象ホストで `systemctl status frr` が `active (running)` となっていること。
- `/etc/sysctl.d/90-frr-forwarding.conf` が所定内容で配置され, `sysctl net.ipv4.ip_forward` / `sysctl net.ipv6.conf.all.forwarding` が `1` を返すこと。
- `/etc/frr/frr.conf` がテンプレートの意図した内容 (BGP ピア, 広告プレフィックス等) になっていること。
- BGP ピアとのセッション状態が `vtysh -c "show ip bgp summary"` / `vtysh -c "show bgp ipv6 unicast summary"` で ESTABLISHED になっていること。

### IPv6 でピアが張れていることの検証手順

IPv6 アドレスで BGP ピア (`frr_ibgp_neighbors` / `frr_ebgp_neighbors` の `addr`) を指定している場合は, 以下の順で切り分けると確実です。

1. L3 到達性 (IPv6) を確認

   - `ping6 -c 3 <peer_ipv6>` が疎通する
   - ルーティングが必要なら `ip -6 route` で経路が存在する
2. TCP/179 の疎通を確認

   - `nc -6 -vz <peer_ipv6> 179` (成功すること)
3. FRR が動作していることを確認

   - `systemctl status frr`
4. FRR にピア設定が入っていることを確認

   - `vtysh -c "show running-config | section router bgp"` で `neighbor <peer_ipv6>` が存在する
5. セッション確立を確認 (意図したアドレスファミリで確認する)

   - IPv4 NLRI (IPv4 プレフィックス) を交換したい場合:
     - `vtysh -c "show bgp ipv4 unicast summary"` で対象ピアが `Established` になっている
   - IPv6 NLRI (IPv6 プレフィックス) を交換したい場合:
     - `vtysh -c "show bgp ipv6 unicast summary"` で対象ピアが `Established` になっている

補足:

- 本ロールのテンプレートでは `address-family ipv4 unicast` と `address-family ipv6 unicast` の両方に対して `neighbor ... activate` を出力します。
  運用上 IPv4 だけ/IPv6 だけ交換する場合, もう一方の address-family では必ずしも `Established` になりません (相手側の capabilities 設定次第)。
- IPv6 トランスポートで IPv4 NLRI を運ぶ (RFC 5549) 想定の場合は, `vtysh -c "show running-config | section router bgp"` で `capability extended-nexthop` が出力されていることも確認してください。

## トラブルシューティング

### 1. FRR サービスが起動しない場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
systemctl status frr --no-pager
journalctl -u frr -n 200 --no-pager | grep -Ei 'error|warn|fail|fatal'
ls -l /etc/frr/frr.conf /etc/frr/daemons
```

**確認ポイント**:

- `systemctl status frr` が `active (running)` であること。
- ログに設定読込失敗や起動失敗が継続出力されていないこと。
- `/etc/frr/frr.conf` と `/etc/frr/daemons` が配置済みであること。

### 2. frr-basic ロールを実行しても処理が進まない場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
grep -n "frr_basic_enabled" vars/all-config.yml host_vars/*/main.yml
ansible-playbook -i inventory/hosts site.yml --tags "frr-basic" -vv | grep -Ei "frr-basic|skipping|ok|changed"
```

**確認ポイント**:

- `frr_basic_enabled` が `true` であること。
- `frr_basic_enabled` が `false` の場合に本ロールの処理がスキップされる仕様を理解していること。
- 再実行時に対象 task が `skipping` ではなく `ok` または `changed` で進んでいること。

### 3. BGP ピアが Established にならない場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
vtysh -c "show ip bgp summary"
vtysh -c "show bgp ipv6 unicast summary"
vtysh -c "show running-config | section router bgp"
```

**確認ポイント**:

- `frr_ibgp_neighbors` / `frr_ebgp_neighbors` で指定したピアが設定へ反映されていること。
- 交換対象のアドレスファミリ(IPv4/IPv6)でピア状態が `Established` であること。
- `frr_bgp_asn` と対向 AS 情報の組み合わせに不整合がないこと。

### 4. IPv6 ピア向けの接続確認に失敗する場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
ping6 -c 3 <peer_ipv6>
ip -6 route
nc -6 -vz <peer_ipv6> 179
```

**確認ポイント**:

- `ping6` で到達可能であること。
- `ip -6 route` で対象ピアへの経路が存在すること。
- TCP/179 への接続確認(`nc -6 -vz`)が成功すること。

### 5. frr-common 呼び出し時のパッケージ導入で失敗する場合

**実施対象ホスト**: 制御ホスト, 構築ホスト, 対象ホスト

**実行するコマンド**:

```bash
ls -1 build-*.log
grep -n "FAILED\|fatal" build-*.log
ansible-playbook -i inventory/hosts site.yml --tags "frr-basic" -vv
```

**確認ポイント**:

- `build-*.log` で失敗した task 名を特定できること。
- 失敗 task が参照する変数の未定義や不整合を解消していること。
- `frr-common` の導入タスク完了後に再実行でエラーが再発しないこと。

## 注意事項

- 本ロールは `frr-common` ロールの導入処理に依存するため, 既存の実行順依存を崩さないことを確認した上で実行してください。
- `frr_basic_enabled` が `false` の場合は FRR 関連タスクをスキップするため, 導入対象ホストでは `true` を設定していることを確認してください。
- `frr_bgp_asn`, `frr_bgp_router_id`, `frr_ibgp_neighbors`, `frr_ebgp_neighbors` の不整合は BGP セッション確立失敗の主因となるため, 対向装置側設定と対にして変更してください。
- `frr.conf` の変更は `systemctl restart frr` を伴うため, 経路切替の瞬断が許容できる時間帯に適用してください。
- `/etc/sysctl.d/90-frr-forwarding.conf` の適用によりホストの IPv4/IPv6 転送設定が変わるため, 同一ホスト上で稼働する他サービスへの影響を事前確認してください。
- テンプレートは IPv4/IPv6 の両 address-family に対して隣接ピア活性化設定を出力するため, 片系のみを運用する場合は想定どおりのセッション状態であることを `vtysh` で確認してください。

## 参考資料

### 公式ドキュメント

- [FRRouting](https://docs.frrouting.org/en/latest/)
- [systemd](https://www.freedesktop.org/wiki/Software/systemd/)
