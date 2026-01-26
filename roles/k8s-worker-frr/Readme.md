# k8s-worker-frr ロール

- [k8s-worker-frr ロール](#k8s-worker-frr-ロール)
  - [概要](#概要)
    - [前提](#前提)
    - [基本仕様](#基本仕様)
    - [実装方針](#実装方針)
  - [実行フロー](#実行フロー)
    - [BGP 設定の詳細](#bgp-設定の詳細)
  - [主要変数](#主要変数)
  - [変数設定例](#変数設定例)
    - [group\_vars/k8s\_worker/k8s\_worker\_frr.yml](#group_varsk8s_workerk8s_worker_frryml)
    - [host\_vars/k8sworker0101.local](#host_varsk8sworker0101local)
    - [host\_vars/k8sctrlplane01.local](#host_varsk8sctrlplane01local)
    - [DC 代表 FRR および外部ゲートウェイの設定](#dc-代表-frr-および外部ゲートウェイの設定)
      - [DC 代表 FRR 側の対応設定](#dc-代表-frr-側の対応設定)
  - [Cilium BGP Control Plane との排他関係](#cilium-bgp-control-plane-との排他関係)
  - [主な処理](#主な処理)
  - [テンプレート / ファイル](#テンプレート--ファイル)
  - [検証ポイント](#検証ポイント)
  - [実環境における host\_vars/ 設定例](#実環境における-host_vars-設定例)
    - [Cluster1 ワーカーノード設定例](#cluster1-ワーカーノード設定例)
      - [ワーカーノード設定 (host\_vars/k8sworker0101.local)](#ワーカーノード設定-host_varsk8sworker0101local)
      - [host\_vars/k8sworker0102.local](#host_varsk8sworker0102local)
    - [Cluster2 ワーカーノード設定例](#cluster2-ワーカーノード設定例)
      - [host\_vars/k8sworker0201.local](#host_varsk8sworker0201local)
      - [host\_vars/k8sworker0202.local](#host_varsk8sworker0202local)
    - [DC代表FRR設定例](#dc代表frr設定例)
      - [host\_vars/frr01.local (Cluster1 DC代表)](#host_varsfrr01local-cluster1-dc代表)
      - [host\_vars/frr02.local (Cluster2 DC代表)](#host_varsfrr02local-cluster2-dc代表)
    - [外部ゲートウェイ設定例](#外部ゲートウェイ設定例)
      - [host\_vars/extgw.local](#host_varsextgwlocal)
    - [ネットワーク構成まとめ](#ネットワーク構成まとめ)
  - [標準デュアルスタックでの検証方法](#標準デュアルスタックでの検証方法)
    - [標準デュアルスタック設定の特徴](#標準デュアルスタック設定の特徴)
    - [標準デュアルスタック設定例](#標準デュアルスタック設定例)
      - [標準デュアルスタック設定でのワーカーノード設定 (host\_vars/k8sworker0101.local)](#標準デュアルスタック設定でのワーカーノード設定-host_varsk8sworker0101local)
      - [DC代表FRR設定 (host\_vars/frr01.local)](#dc代表frr設定-host_varsfrr01local)
    - [前提条件](#前提条件)
    - [1. FRR サービス状態の確認](#1-frr-サービス状態の確認)
    - [2. FRR 設定の構文確認](#2-frr-設定の構文確認)
    - [3. iBGP セッション状態の確認](#3-ibgp-セッション状態の確認)
    - [4. 広告経路の確認 (IPv4)](#4-広告経路の確認-ipv4)
    - [5. 広告経路の確認 (IPv6)](#5-広告経路の確認-ipv6)
    - [6. カーネルルーティングテーブルの確認](#6-カーネルルーティングテーブルの確認)
      - [IPv4ルートの確認](#ipv4ルートの確認)
      - [IPv6ルートの確認](#ipv6ルートの確認)
    - [7. BGP ネイバー詳細情報の確認](#7-bgp-ネイバー詳細情報の確認)
      - [IPv4 ネイバーの詳細](#ipv4-ネイバーの詳細)
      - [IPv6 ネイバーの詳細](#ipv6-ネイバーの詳細)
    - [8. DC 代表 FRR での受信経路確認](#8-dc-代表-frr-での受信経路確認)
      - [8.1 IPv4 経路の確認](#81-ipv4-経路の確認)
      - [8.2 IPv6 経路の確認](#82-ipv6-経路の確認)
      - [8.3 External Gateway (extgw) での経路確認](#83-external-gateway-extgw-での経路確認)
    - [9. DC 間 Pod 疎通テスト (標準デュアルスタック)](#9-dc-間-pod-疎通テスト-標準デュアルスタック)
      - [9.1 既存テスト Pod の削除 ( 存在する場合 )](#91-既存テスト-pod-の削除--存在する場合-)
      - [9.2 テスト Pod のデプロイ](#92-テスト-pod-のデプロイ)
      - [9.3 Pod IP アドレスの確認](#93-pod-ip-アドレスの確認)
      - [9.4 Cilium 設定の確認](#94-cilium-設定の確認)
      - [9.5 Cluster1  =\>  Cluster2 疎通テスト (IPv4)](#95-cluster1----cluster2-疎通テスト-ipv4)
      - [9.6 Cluster2  =\>  Cluster1 疎通テスト (IPv4)](#96-cluster2----cluster1-疎通テスト-ipv4)
      - [9.7 Cluster1  =\>  Cluster2 疎通テスト (IPv6)](#97-cluster1----cluster2-疎通テスト-ipv6)
      - [9.8 Cluster2  =\>  Cluster1 疎通テスト (IPv6)](#98-cluster2----cluster1-疎通テスト-ipv6)
      - [9.9 テスト Pod のクリーンアップ](#99-テスト-pod-のクリーンアップ)
  - [補足](#補足)
  - [Multiprotocol BGP (IPv4トランスポートでIPv6のBGP広告も実施する設定) 利用時の検証方法](#multiprotocol-bgp-ipv4トランスポートでipv6のbgp広告も実施する設定-利用時の検証方法)
    - [Multiprotocol BGP 設定例](#multiprotocol-bgp-設定例)
      - [Multiprotocol BGPでのワーカーノード設定 (host\_vars/k8sworker0101.local)](#multiprotocol-bgpでのワーカーノード設定-host_varsk8sworker0101local)
      - [Multiprotocol BGP設定でのDC代表FRR設定 (host\_vars/frr01.local)](#multiprotocol-bgp設定でのdc代表frr設定-host_varsfrr01local)
      - [設定時の注意事項](#設定時の注意事項)
    - [Multiprotocol BGPでの前提条件](#multiprotocol-bgpでの前提条件)
    - [1. FRR サービス状態の確認 (Multiprotocol BGP)](#1-frr-サービス状態の確認-multiprotocol-bgp)
    - [2. FRR 設定の構文確認 (Multiprotocol BGP)](#2-frr-設定の構文確認-multiprotocol-bgp)
    - [3. iBGP セッション状態の確認 (Multiprotocol BGP)](#3-ibgp-セッション状態の確認-multiprotocol-bgp)
    - [4. Multiprotocol BGP設定での広告経路の確認 (IPv4)](#4-multiprotocol-bgp設定での広告経路の確認-ipv4)
    - [5. Multiprotocol BGP設定での広告経路の確認 (IPv6)](#5-multiprotocol-bgp設定での広告経路の確認-ipv6)
    - [6. prefix-list の確認](#6-prefix-list-の確認)
    - [7. route-map の確認](#7-route-map-の確認)
    - [8. カーネルルーティングテーブルの確認 (IPv4)](#8-カーネルルーティングテーブルの確認-ipv4)
    - [9. カーネルルーティングテーブルの確認 (IPv6)](#9-カーネルルーティングテーブルの確認-ipv6)
    - [10. IP フォワーディング設定の確認](#10-ip-フォワーディング設定の確認)
    - [11. DC 代表 FRR での受信経路確認](#11-dc-代表-frr-での受信経路確認)
      - [11.1 IPv4 経路の確認](#111-ipv4-経路の確認)
      - [11.2 IPv6 経路の確認](#112-ipv6-経路の確認)
      - [11.3 External Gateway (extgw) での経路確認](#113-external-gateway-extgw-での経路確認)
    - [12. DC 間 Pod 疎通テスト (IPv4/IPv6 デュアルスタック)](#12-dc-間-pod-疎通テスト-ipv4ipv6-デュアルスタック)
      - [12.1 既存テスト Pod の削除 ( 存在する場合 )](#121-既存テスト-pod-の削除--存在する場合-)
      - [12.2 テスト Pod のデプロイ](#122-テスト-pod-のデプロイ)
      - [12.3 Pod IP アドレスの確認](#123-pod-ip-アドレスの確認)
      - [12.4 Cilium 設定の確認 ( オプション )](#124-cilium-設定の確認--オプション-)
      - [12.5 Cluster1  =\>  Cluster2 疎通テスト (IPv4)](#125-cluster1----cluster2-疎通テスト-ipv4)
      - [12.6 Cluster2  =\>  Cluster1 疎通テスト (IPv4)](#126-cluster2----cluster1-疎通テスト-ipv4)
      - [12.7 Cluster1  =\>  Cluster2 疎通テスト (IPv6)](#127-cluster1----cluster2-疎通テスト-ipv6)
      - [12.8 Cluster2  =\>  Cluster1 疎通テスト (IPv6)](#128-cluster2----cluster1-疎通テスト-ipv6)
      - [12.9 テスト完了後のクリーンアップ](#129-テスト完了後のクリーンアップ)
  - [RFC 5549 (IPv6 トランスポート) 利用時の検証方法](#rfc-5549-ipv6-トランスポート-利用時の検証方法)
    - [RFC 5549 (IPv6 トランスポート) 利用時の前提条件](#rfc-5549-ipv6-トランスポート-利用時の前提条件)
    - [RFC 5549 環境での host\_vars 設定例](#rfc-5549-環境での-host_vars-設定例)
      - [ワーカーノードの設定例 (host\_vars/k8sworker0101.local)](#ワーカーノードの設定例-host_varsk8sworker0101local)
      - [DC 代表 FRR の設定例 (host\_vars/frr01.local)](#dc-代表-frr-の設定例-host_varsfrr01local)
      - [External Gateway の設定例 (host\_vars/extgw.local)](#external-gateway-の設定例-host_varsextgwlocal)
      - [Cluster2 のワーカーノード設定例 (host\_vars/k8sworker0201.local)](#cluster2-のワーカーノード設定例-host_varsk8sworker0201local)
    - [1. FRR サービス状態の確認 (RFC 5549 (IPv6 トランスポート) 利用時の例)](#1-frr-サービス状態の確認-rfc-5549-ipv6-トランスポート-利用時の例)
    - [2. BGP セッション状態の確認 (IPv6 トランスポート)](#2-bgp-セッション状態の確認-ipv6-トランスポート)
    - [3. 広告経路の確認 (IPv4 - RFC 5549)](#3-広告経路の確認-ipv4---rfc-5549)
    - [4. 広告経路の確認 (IPv6)](#4-広告経路の確認-ipv6)
    - [5. カーネルルーティングテーブルの確認 (IPv4 - RFC 5549)](#5-カーネルルーティングテーブルの確認-ipv4---rfc-5549)
    - [6. カーネルルーティングテーブルの確認 (IPv6)](#6-カーネルルーティングテーブルの確認-ipv6)
    - [7. DC 代表 FRR での経路確認 (RFC 5549)](#7-dc-代表-frr-での経路確認-rfc-5549)
      - [7.1 BGP ネイバー詳細確認 (Extended Nexthop Capability)](#71-bgp-ネイバー詳細確認-extended-nexthop-capability)
      - [7.2 IPv4 BGP テーブルの確認 (link-local nexthop)](#72-ipv4-bgp-テーブルの確認-link-local-nexthop)
    - [8. External Gateway での経路確認 (RFC 5549)](#8-external-gateway-での経路確認-rfc-5549)
      - [8.1 IPv4 BGP テーブルの確認](#81-ipv4-bgp-テーブルの確認)
      - [8.2 IPv6 BGP テーブルの確認](#82-ipv6-bgp-テーブルの確認)
    - [9. DC 間 Pod 疎通テスト (RFC 5549)](#9-dc-間-pod-疎通テスト-rfc-5549)
      - [9.1 テスト Pod のデプロイと IP アドレス確認](#91-テスト-pod-のデプロイと-ip-アドレス確認)
      - [9.2 IPv6 疎通テスト](#92-ipv6-疎通テスト)
      - [9.3 IPv4 疎通テスト](#93-ipv4-疎通テスト)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. BGP セッションが `Established` にならない場合](#1-bgp-セッションが-established-にならない場合)
      - [1.1 全構成共通の診断手順](#11-全構成共通の診断手順)
      - [1.2 標準デュアルスタック構成特有の問題](#12-標準デュアルスタック構成特有の問題)
      - [1.3 Multiprotocol BGP構成特有の問題](#13-multiprotocol-bgp構成特有の問題)
      - [1.4 RFC 5549構成特有の問題](#14-rfc-5549構成特有の問題)
    - [2. IPv6 BGP セッションが `NoNeg` 状態になる場合](#2-ipv6-bgp-セッションが-noneg-状態になる場合)
      - [2.1 Multiprotocol BGP 構成の場合](#21-multiprotocol-bgp-構成の場合)
      - [2.2 標準デュアルスタック構成の場合](#22-標準デュアルスタック構成の場合)
      - [2.3 RFC 5549 構成の場合](#23-rfc-5549-構成の場合)
    - [3. 経路が広告されない, またはホストルートのみ広告される場合](#3-経路が広告されない-またはホストルートのみ広告される場合)
      - [3.1 全構成共通の原因と解決方法](#31-全構成共通の原因と解決方法)
      - [3.2 標準デュアルスタック構成での確認ポイント](#32-標準デュアルスタック構成での確認ポイント)
      - [3.3 Multiprotocol BGP構成での確認ポイント](#33-multiprotocol-bgp構成での確認ポイント)
      - [3.4 RFC 5549構成での確認ポイント](#34-rfc-5549構成での確認ポイント)
    - [4. IPv6 Pod 通信が失敗する場合](#4-ipv6-pod-通信が失敗する場合)
    - [5. 経路受信は成功するが, Pod から外部への通信ができない場合](#5-経路受信は成功するが-pod-から外部への通信ができない場合)

## 概要

Kubernetes ワーカーノード上に FRR (Free Range Routing) を導入し, データセンタ(以下DCと略す) 代表 FRR への iBGP (Internal Border Gateway Protocol) 広告により Pod/Service ネットワークをデータセンター間で共有するロールです。Cilium native routing モードを前提とします。本ロールは, Cilium BGP Control Plane を使用しない場合の代替ルーティング機能です。

### 前提

- K8sクラスタのCNIは, Ciliumをnative routingモードで動作。
- K8sクラスタは, IPv4/IPv6デュアルスタック構成前提。
- Pod間通信はIPv6通信を主に使用しますが, IPv4での通信も行えることを想定。
- プライベートネットワークと仮想環境内の管理用プライベートネットワークは一つのデータセンター(DCと略す)内に敷設。
- データセンターには, データセンター間の経路を交換するためのDC代表FRRが存在。
- 各データセンターには複数のK8sクラスタが存在することを前提。
- K8sクラスタを構成するコントロールプレインとワーカーノードは, K8s用プライベートネットワークと管理用プライベートネットワークに接続される。
- K8s用プライベートネットワークはK8sクラスタごとに1つ用意
- 管理用プライベートネットワークはデータセンターごとに一つ用意
- K8sのBGP Control Plane機能を使わない場合を想定し, 各K8sのワーカーノード上のFRRからDC代表FRRにiBGP経路広告を行うことによりデータセンター間でのPod間通信を行うことを想定。
- 各K8sクラスタごとに固有なK8sのPodネットワーク, K8sのサービスネットワークが定義。
- 各K8sのワーカーノード上のFRRからDC代表FRRに, ワーカーノードとDC代表FRR間の静的ルート, K8sのPodネットワークへのルート, K8sのサービスネットワークへのルートをiBGP広告。
- 広告対象のネットワークプレフィクスの下限/上限を変数で変更可能とする。
- DC代表FRRはこのプレイブックでは, frr01.local/frr02.localのホストとして定義。
- DC代表FRRからextgw.localのホストで動作しているFRRに経路をeBGP (External Border Gateway Protocol)で広告。
- FRRのbgpdで交換されるK8sのPodネットワークへのルート, K8sのサービスネットワークへのルートをカーネルのルーティングテーブルに反映する。
- 本ロールに関連する変数は, パラメタ名から設定値への辞書のリストとして定義されるk8s_worker_frr変数に設定。

### 基本仕様

本ロールは以下の要件を満たすように設計されています:

- **IPv4/IPv6 デュアルスタック対応**: Pod 間通信は主に IPv6 を使用しますが, IPv4 での通信も可能です。
- **DC 代表 FRR への iBGP 広告**: 各ワーカーノードは DC 代表 FRR (frr01.local, frr02.local) に対して iBGP セッションを確立し, クラスタ全体の Pod ネットワークおよび Service ネットワーク CIDR を広告します。ワーカーノード自身への到達性確保用ホストルート (`/32` または `/128`) も併せて広告します。
- **プレフィックス長フィルタ**: BGP 送信時に prefix-list と route-map を使用して, 広告するネットワークプレフィックスの下限/上限を制御します。IPv4/IPv6, Pod/Service 別に範囲指定 ( 例: /24-/28 ) が可能です。
- **カーネルルーティングテーブルへの反映**: DC 代表 FRR から学習した BGP ルートをカーネルのルーティングテーブルに反映し, データセンター間の Pod 間通信を実現します。変数によるフィルタ設定が可能で, デフォルトでは全 BGP ルートを反映します。
- **複数クラスタ対応**: クラスタ名/ID による変数階層化により, 同一 DC 内の複数 K8s クラスタで異なる Pod/Service CIDR を広告できます。
- **Cilium BGP Control Plane との排他実行**: `k8s_bgp.enabled` が `false` かつ `k8s_worker_frr.enabled` が `true` の場合のみ動作します。
- **RFC 5549 サポート**: IPv6 トランスポートで IPv4 NLRI を運ぶ設定をオプションで有効化できます ( デフォルトは無効 ) 。
- **IPv4 トランスポートで IPv6 NLRI**: IPv4 ネイバーで IPv6 経路を交換する設定をオプションで有効化できます ( デフォルトは無効, RFC 5549 と排他的 ) 。
- **経路広告方法の選択**: 静的経路定義 + `redistribute static` (デフォルト, 他ノードとの互換性重視) または `network` コマンドによる直接広告 (Cilium がカーネルに経路を作成する前提) を選択できます。

### 実装方針

本ロールの実装における主要な設計判断と技術的詳細:

- **変数定義**: 本ロールに関連する変数は, パラメタ名から設定値への辞書として定義される `k8s_worker_frr` 変数に設定します。
- **データセンタ(DC) 代表 FRR の定義**: DC 代表 FRR (frr01.local/frr02.local) の情報は, ワーカーノードの `k8s_worker_frr` 辞書内の `dc_frr_addresses` キーに各 DC FRR ノードのリスニングアドレスをマッピングとして持ちます ( 例: `dc_frr_addresses: {frr01.local: "192.168.40.49"}` ) 。
- **Pod/Service CIDR 取得**: `k8s_worker_frr` 変数内の `clusters.<cluster_name>` 配下のキー `pod_cidrs_v4`, `service_cidrs_v4`, `pod_cidrs_v6`, `service_cidrs_v6` から取得します。これらのキーの値はネットワーク CIDR のリストです。
- **ホストルート広告**: ワーカーノードから DC FRR への nexthop 到達性確保のため, ワーカーノード自身への `/32` (IPv4) または `/128` (IPv6) ホストルートを広告します。これらは `k8s_worker_frr` 辞書の `advertise_host_route_ipv4`/`advertise_host_route_ipv6` キーで明示的に指定します。
- **プレフィックス長フィルタ実現方法**: FRR route-map + prefix-list 定義で実現します。IPv4/IPv6, Pod/Service 別に複数の prefix-list を address-family 別に分けて定義します ( 命名規則: `PL-V4-POD-OUT`, `PL-V4-SVC-OUT`, `PL-V4-HOST-OUT`, `PL-V6-POD-OUT`, `PL-V6-SVC-OUT`, `PL-V6-HOST-OUT` ) 。フィルタの粒度には範囲指定 ( 例: /24-/28 ) を使用します。
- **Route-map 適用タイミング**: prefix-list フィルタはネイバーへの送信時 ( `neighbor X route-map Y out` ) に適用します。
- **カーネルルート反映**: zebra のカーネルルート反映用 route-map (`RM-KERNEL-IMPORT`) を用意し, 変数 (`kernel_route_filter`) によってカーネルに反映するルートを指定できるようにしています。デフォルト ( 変数未定義時 ) は全 BGP ルートをカーネルに反映します。
- **経路広告方法**: 変数 `route_advertisement_method` で 2 つの方式を選択できます。`"static"` (デフォルト) は静的経路定義 + `redistribute static` で BGP に再配送します。この方式はカーネルに経路が存在しなくても広告でき, 他ノードとの互換性が高いです。`"network"` は `network` コマンドで直接広告します。この方式は Cilium がカーネルに経路を作成することを前提とします。

## 実行フロー

1. `load-params.yml` で OS 別パッケージ定義 (`vars/packages-*.yml`) とクラスタ共通変数 (`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込みます。
2. `package.yml` で FRR パッケージをインストールし, FRR サービスを有効化, 起動します。
3. `directory.yml` は現状プレースホルダとして読み込まれます (将来の拡張用)。
4. `user_group.yml` で vtysh アクセス許可グループを作成し, 指定されたユーザを追加します (`frr_vtysh_users` 変数で制御)。
5. `service.yml` は現状プレースホルダとして読み込まれます (将来の拡張用)。
6. `config.yml` で以下の設定ファイルを配置します:
   - `/etc/sysctl.d/90-frr-forwarding.conf`: IPv4/IPv6 フォワーディングを有効化し, `reload_sysctl` ハンドラを発火させます。
   - `/etc/frr/daemons`: zebra と bgpd を有効化し, `restart_frr` ハンドラを発火させます。
   - `/etc/frr/frr.conf`: BGP 設定, prefix-list, route-map, カーネルインポート設定を含むメイン設定ファイルを配置し, `restart_frr` ハンドラを発火させます。
   - **FRR 設定の構文検証**: `vtysh -f /etc/frr/frr.conf --dry-run` (FRR 8.1+) で構文を検証します。古いバージョンでは `vtysh -c 'configure terminal' < /etc/frr/frr.conf` を使用します。エラーがあればタスクを即座に停止します。

### BGP 設定の詳細

`frr.conf.j2` テンプレートは以下の設定を生成します:

- **BGP 基本設定**: `k8s_worker_frr.local_asn` (iBGP 構成のため DC 代表 FRR と同一 AS (Autonomous System)), および, `k8s_worker_frr.router_id` (ワーカーノードの Router ID) を使用します。
- **iBGP ネイバー**: `k8s_worker_frr.dc_frr_addresses` で定義された DC 代表 FRR ノードに対して iBGP セッションを確立します。
- **ネットワーク広告**:
  - ワーカーノード自身への到達性確保用 `/32` (IPv4) または `/128` (IPv6) ホストルート (`advertise_host_route_ipv4/ipv6`)
  - クラスタ全体の Pod ネットワーク CIDR (`clusters.<cluster_name>.pod_cidrs_v4/v6`)
  - クラスタ全体の Service ネットワーク CIDR (`clusters.<cluster_name>.service_cidrs_v4/v6`)
- **プレフィックス長フィルタ (送信)**: address-family 別に以下の prefix-list を定義します:
  - `PL-V4-POD-OUT`: IPv4 Pod ネットワーク用 (min/max 長は `prefix_filter.ipv4.pod_min_length/pod_max_length`)
  - `PL-V4-SVC-OUT`: IPv4 Service ネットワーク用 (min/max 長は `prefix_filter.ipv4.service_min_length/service_max_length`)
  - `PL-V4-HOST-OUT`: IPv4 ホストルート用 (`/32` のみ許可)
  - `PL-V6-POD-OUT`: IPv6 Pod ネットワーク用 (min/max 長は `prefix_filter.ipv6.pod_min_length/pod_max_length`)
  - `PL-V6-SVC-OUT`: IPv6 Service ネットワーク用 (min/max 長は `prefix_filter.ipv6.service_min_length/service_max_length`)
  - `PL-V6-HOST-OUT`: IPv6 ホストルート用 (`/128` のみ許可)
- **Route-map (送信)**: `RM-V4-OUT` および `RM-V6-OUT` で上記 prefix-list をマッチし, 各 DC 代表 FRR ネイバーに `neighbor X route-map Y out` で適用します。
- **カーネルインポート用 route-map**: `RM-KERNEL-IMPORT` を定義し, `ip protocol bgp route-map RM-KERNEL-IMPORT` および `ipv6 protocol bgp route-map RM-KERNEL-IMPORT` でカーネルへのルートインポートを制御します。`kernel_route_filter` が未定義の場合は全 BGP ルートを許可し, 定義されている場合は指定された prefix-list にマッチするルートのみをインポートします。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_worker_frr.enabled` | `false` | FRR 有効化フラグ。`true` かつ `k8s_bgp.enabled` が `false` の場合のみロールが実行されます。|
| `k8s_worker_frr.local_asn` | `0` | BGP AS 番号。iBGP 構成のため DC 代表 FRR と同一 AS を使用します。|
| `k8s_worker_frr.router_id` | `""` | BGP Router ID (IPv4 形式)。ワーカーノードの管理ネットワーク側 IPv4 アドレスを指定します。|
| `k8s_worker_frr.dc_frr_addresses` | `{}` | DC 代表 FRR ノードの IPv4 リスニングアドレス。キーは FRR ノードのホスト名 (例: `frr01.local`), 値は iBGP リスニングアドレス (IPv4, 例: `"192.168.40.49"`)。|
| `k8s_worker_frr.dc_frr_addresses_v6` | `{}` | DC 代表 FRR ノードの IPv6 リスニングアドレス。キーは FRR ノードのホスト名 (例: `frr01.local`), 値は iBGP リスニングアドレス (IPv6, 例: `"fd69:6684:61a:2::49"`)。|
| `k8s_worker_frr.cluster_name` | `""` | クラスタ名。`k8s_cilium_cm_cluster_name` と一致させ, `clusters` 辞書からクラスタ固有の Pod/Service CIDR を取得します。|
| `k8s_worker_frr.advertise_host_route_ipv4` | `""` | ワーカーノード自身への到達性確保用 IPv4 ホストルート (例: `"192.168.40.42/32"`)。|
| `k8s_worker_frr.advertise_host_route_ipv6` | `""` | ワーカーノード自身への到達性確保用 IPv6 ホストルート (例: `"fd69:6684:61a:2::42/128"`)。|
| `k8s_worker_frr.rfc5549_enabled` | `false` | RFC 5549 サポート (IPv6 トランスポートで IPv4 NLRI を運ぶ)。`true` の場合, `dc_frr_addresses_v6` で定義された IPv6 ネイバーも IPv4 address-family で activate し, `capability extended-nexthop` を有効化します。`false` (デフォルト) の場合, IPv4/IPv6 を別々のトランスポートで運びます。|
| `k8s_worker_frr.ipv4_transport_ipv6_nlri_enabled` | `false` | IPv4 トランスポートで IPv6 NLRI を運ぶ設定。`true` の場合, `dc_frr_addresses` で定義された IPv4 ネイバーも IPv6 address-family で activate し, `capability extended-nexthop` を有効化します。`false` (デフォルト) の場合, IPv4/IPv6 を別々のトランスポートで運びます。`rfc5549_enabled` との同時有効化は想定していません ( 排他的 ) 。|
| `k8s_worker_frr.route_advertisement_method` | `"static"` | 経路広告方法の選択。`"static"` (デフォルト): 静的経路定義 + `redistribute static` で BGP に再配送。カーネルに経路が存在しなくても広告可能, 他ノードとの互換性が高い。`"network"`: `network` コマンドで直接広告。Cilium がカーネルに経路を作成することを前提。|
| `k8s_worker_frr.static_route_interface` | `""` | 静的経路の出力インターフェース。`route_advertisement_method="static"` の場合のみ使用。未設定の場合は `mgmt_nic` 変数を使用 (VMware 環境: `ens160`, Xen環境: `enX0`, その他: `eth0`)。Pod/Service CIDR への静的経路がこのインターフェースを経由して定義されます。|
| `k8s_worker_frr.prefix_filter.ipv4.pod_min_length` | `24` | IPv4 Pod ネットワークの最小プレフィックス長。|
| `k8s_worker_frr.prefix_filter.ipv4.pod_max_length` | `28` | IPv4 Pod ネットワークの最大プレフィックス長。|
| `k8s_worker_frr.prefix_filter.ipv4.service_min_length` | `16` | IPv4 Service ネットワークの最小プレフィックス長。|
| `k8s_worker_frr.prefix_filter.ipv4.service_max_length` | `24` | IPv4 Service ネットワークの最大プレフィックス長。|
| `k8s_worker_frr.prefix_filter.ipv6.pod_min_length` | `56` | IPv6 Pod ネットワークの最小プレフィックス長。|
| `k8s_worker_frr.prefix_filter.ipv6.pod_max_length` | `64` | IPv6 Pod ネットワークの最大プレフィックス長。|
| `k8s_worker_frr.prefix_filter.ipv6.service_min_length` | `112` | IPv6 Service ネットワークの最小プレフィックス長。|
| `k8s_worker_frr.prefix_filter.ipv6.service_max_length` | `120` | IPv6 Service ネットワークの最大プレフィックス長。|
| `k8s_worker_frr.kernel_route_filter.ipv4` | 未定義 | カーネルへインポートする IPv4 prefix-list 名のリスト (例: `["PL-V4-KERNEL"]`)。未定義の場合は全 BGP ルートをインポートします。|
| `k8s_worker_frr.kernel_route_filter.ipv6` | 未定義 | カーネルへインポートする IPv6 prefix-list 名のリスト (例: `["PL-V6-KERNEL"]`)。未定義の場合は全 BGP ルートをインポートします。|
| `k8s_worker_frr.clusters.<cluster_name>.pod_cidrs_v4` | `[]` | クラスタ全体の Pod ネットワーク CIDR (IPv4) のリスト (例: `["10.244.0.0/16"]`)。|
| `k8s_worker_frr.clusters.<cluster_name>.service_cidrs_v4` | `[]` | クラスタ全体の Service ネットワーク CIDR (IPv4) のリスト (例: `["10.254.0.0/16"]`)。|
| `k8s_worker_frr.clusters.<cluster_name>.pod_cidrs_v6` | `[]` | クラスタ全体の Pod ネットワーク CIDR (IPv6) のリスト (例: `["fdb6:6e92:3cfb:0200::/56"]`)。|
| `k8s_worker_frr.clusters.<cluster_name>.service_cidrs_v6` | `[]` | クラスタ全体の Service ネットワーク CIDR (IPv6) のリスト (例: `["fdb6:6e92:3cfb:feed::/112"]`)。|
| `frr_vtysh_users` | `[]` | vtysh を sudo なしで実行可能とするユーザのリスト。|
| `frr_vtysh_group` | `frrvty` | vtysh アクセス許可グループ名 (`frr_vtysh_group_name` から取得, 既定値は `frrvty`)。|
| `frr_group` | `frr` | FRR グループ名 (`frr_group_name` から取得, 既定値は `frr`)。|
| `frr_packages` | (OS 別) | FRR パッケージ名 (`vars/cross-distro.yml` で定義)。|
| `frr_svc_name` | `frr` | FRR サービス名 (`vars/cross-distro.yml` で定義)。|
| `k8s_bgp.enabled` | `false` | Cilium BGP Control Plane の有効化フラグ。本ロールは `k8s_bgp.enabled` が `false` の場合のみ実行されます。|
| `k8s_cilium_cm_cluster_name` | 必須 | Cilium Cluster Mesh のクラスタ名。`k8s_worker_frr.cluster_name` のデフォルト値として使用されます。|

## 変数設定例

### group_vars/k8s_worker/k8s_worker_frr.yml

全 K8s ワーカーノードで共通の設定を定義します:

```yaml
k8s_worker_frr:
  enabled: false  # デフォルトは無効
  local_asn: 65011
  dc_frr_addresses:
    frr01.local: "192.168.40.49"
    frr02.local: "192.168.40.50"
  dc_frr_addresses_v6:
    frr01.local: "fd69:6684:61a:2::49"
    frr02.local: "fd69:6684:61a:3::48"
  # 経路広告方法 ("static" または "network")
  route_advertisement_method: "static"
  # 静的経路の出力インターフェース (route_advertisement_method="static" の場合)
  # static_route_interface: "ens160"  # 未設定の場合は mgmt_nic 変数を使用
  # RFC 5549 (IPv6 トランスポートで IPv4 NLRI) - ipv4_transport_ipv6_nlri_enabled と排他的
  rfc5549_enabled: false
  # IPv4 トランスポートで IPv6 NLRI - rfc5549_enabled と排他的
  ipv4_transport_ipv6_nlri_enabled: false
  prefix_filter:
    ipv4:
      pod_min_length: 24
      pod_max_length: 28
      service_min_length: 16
      service_max_length: 24
    ipv6:
      pod_min_length: 56
      pod_max_length: 64
      service_min_length: 112
      service_max_length: 120
  # カーネルへインポートする prefix-list (未定義の場合は全 BGP ルートをインポート)
  # kernel_route_filter:
  #   ipv4: ["PL-V4-KERNEL"]
  #   ipv6: ["PL-V6-KERNEL"]
  clusters:
    cluster1:
      pod_cidrs_v4: ["10.244.0.0/16"]
      service_cidrs_v4: ["10.254.0.0/16"]
      pod_cidrs_v6: ["fdb6:6e92:3cfb:0200::/56"]
      service_cidrs_v6: ["fdb6:6e92:3cfb:feed::/112"]
    cluster2:
      pod_cidrs_v4: ["10.243.0.0/16"]
      service_cidrs_v4: ["10.253.0.0/16"]
      pod_cidrs_v6: ["fdb6:6e92:3cfb:0100::/56"]
      service_cidrs_v6: ["fdb6:6e92:3cfb:feec::/112"]
```

### host_vars/k8sworker0101.local

各ワーカーノードで固有の設定を定義します:

```yaml
k8s_worker_frr:
  enabled: true
  local_asn: 65011
  router_id: "192.168.30.42"
  cluster_name: "cluster1"
  dc_frr_addresses:
    frr01.local: "192.168.40.49"
  dc_frr_addresses_v6:
    frr01.local: "fd69:6684:61a:2::49"
  advertise_host_route_ipv4: "192.168.40.42/32"
  advertise_host_route_ipv6: "fd69:6684:61a:2::42/128"
```

### host_vars/k8sctrlplane01.local

コントロールプレインノードでは本ロールを無効化します:

```yaml
k8s_worker_frr:
  enabled: false  # コントロールプレインではワーカー用FRRを無効化
```

**注**: コントロールプレインノードでは `enabled: false` を明示的に設定するか, 変数を未定義のままにします。

### DC 代表 FRR および外部ゲートウェイの設定

**frr01.local, frr02.local, extgw.local** などのDC代表FRRノードや外部ゲートウェイは, 本ロール (`k8s-worker-frr`) の対象外です。これらのノードは別のロール ( 例: `frr-basic` ) で管理され, 独自のBGP設定を持ちます。

本ロールはK8sワーカーノード上でのみ実行され, これらのFRRノードに対して `dc_frr_addresses` で定義されたアドレスに接続します。

#### DC 代表 FRR 側の対応設定

DC代表FRR (frr01.local等) では, K8sワーカーノードの**K8sネットワーク側アドレス**をiBGPピアとして設定します。例えば `frr01.local` の設定:

```yaml
# K8sノードとの iBGP ピア (IPv4セッション)
# K8sネットワーク側アドレスを使用 ( DC接続側 )
frr_k8s_neighbors:
  - { addr: "192.168.40.41", asn: 65011, desc: "C1 control-plane" }
  - { addr: "192.168.40.42", asn: 65011, desc: "C1 worker-1" }
  - { addr: "192.168.40.43", asn: 65011, desc: "C1 worker-2" }

# K8sノードとの iBGP ピア (IPv6セッション)
frr_k8s_neighbors_v6:
  - { addr: "fd69:6684:61a:2::41", asn: 65011, desc: "C1 control-plane" }
  - { addr: "fd69:6684:61a:2::42", asn: 65011, desc: "C1 worker-1" }
  - { addr: "fd69:6684:61a:2::43", asn: 65011, desc: "C1 worker-2" }

# 疑似外部ネットワーク側 eBGP ピア (IPv4セッション)
frr_ebgp_neighbors:
  - { addr: "192.168.255.81", asn: 65100, desc: "External GW" }

# 疑似外部ネットワーク側 eBGP ピア (IPv6セッション)
frr_ebgp_neighbors_v6:
  - { addr: "fd69:6684:61a:90::81", asn: 65100, desc: "External GW" }
```

**重要**:

- ワーカーノード側では `advertise_host_route_ipv4: "192.168.40.42/32"` でK8sネットワーク側アドレスをホストルートとして広告します。
- DC代表FRR側では `frr_k8s_neighbors` で同じK8sネットワーク側アドレスをiBGPピアとして設定します。

## Cilium BGP Control Plane との排他関係

本ロールは Cilium BGP Control Plane を使用しない場合の代替ルーティング機能です。以下の条件で排他実行されます:

- **本ロール実行条件**: `k8s_worker_frr.enabled` が `true` **かつ** `k8s_bgp.enabled` が `false`
- **Cilium BGP Control Plane 実行条件**: `k8s_bgp.enabled` が `true`

両方を同時に有効化することはできません。`k8s-worker.yml` で以下のように制御されています:

```yaml
    - role: k8s-worker
      tags: k8s-worker
    - role: k8s-worker-frr
      tags: k8s-worker-frr
      when:
        - k8s_worker_frr is defined
        - k8s_worker_frr.enabled | default(false)
        - not (k8s_bgp.enabled | default(false))
```

## 主な処理

- **FRR パッケージのインストール**: `frr_packages` で定義されたパッケージをインストールし, FRR サービスを有効化, 起動します。
- **IPv4/IPv6 フォワーディング有効化**: sysctl ドロップイン `/etc/sysctl.d/90-frr-forwarding.conf` を配置し, `net.ipv4.ip_forward` と `net.ipv6.conf.all.forwarding` を `1` に設定します。
- **FRR デーモン有効化**: `/etc/frr/daemons` で zebra と bgpd を有効化します。
- **BGP 設定の生成と配置**: `frr.conf.j2` テンプレートから `/etc/frr/frr.conf` を生成し, 以下を含みます:
  - iBGP ネイバー設定 (`dc_frr_addresses` から取得)
  - ネットワーク広告 (ホストルート, Pod CIDR, Service CIDR)
  - プレフィックス長フィルタ用 prefix-list (送信用とカーネルインポート用を分離)
  - Route-map (送信フィルタとカーネルインポートフィルタ)
- **FRR 設定の構文検証**: `vtysh -f /etc/frr/frr.conf --dry-run` (FRR 8.1+) で構文エラーをチェックします。古いバージョンでは代替検証方法を使用します。エラーがあればタスクを停止します。フォールバックや警告出力は行わず, 厳密な検証を優先します。
- **vtysh アクセス許可**: `frr_vtysh_users` で指定されたユーザを `frr_vtysh_group` に追加し, sudo なしで vtysh を実行可能にします。

## テンプレート / ファイル

- `templates/frr.conf.j2`: FRR メイン設定ファイルのテンプレート。BGP 設定, prefix-list, route-map, カーネルインポート設定を含みます。
- `templates/daemons.j2`: FRR デーモン有効化設定のテンプレート。zebra と bgpd を有効化します。
- `templates/90-frr-forwarding.conf.j2`: IPv4/IPv6 フォワーディング有効化用 sysctl 設定のテンプレート。

## 検証ポイント

- `systemctl status frr` で FRR サービスが `active (running)` である。
- `/etc/frr/frr.conf` が正しく配置され, 構文エラーがない (`vtysh -c "show running-config"` で確認可能)。
- `vtysh -c "show bgp summary"` で DC 代表 FRR への iBGP セッションが `Established` である。
- `vtysh -c "show ip bgp"` および `vtysh -c "show bgp ipv6"` で Pod/Service CIDR が広告されている。
- `ip route` および `ip -6 route` で DC 代表 FRR から学習した BGP ルートがカーネルのルーティングテーブルに反映されている (プロトコルが `bgp` として表示される)。
- `vtysh -c "show ip prefix-list"` および `vtysh -c "show ipv6 prefix-list"` で prefix-list が正しく定義されている。
- `vtysh -c "show route-map"` で route-map が正しく定義され, 意図したフィルタが適用されている。
- `/etc/sysctl.d/90-frr-forwarding.conf` が配置され, `sysctl net.ipv4.ip_forward` および `sysctl net.ipv6.conf.all.forwarding` が `1` を返す。
- 他 DC のワーカーノードから本ワーカーノードの Pod への疎通が可能である (ping テストなど)。

## 実環境における host_vars/ 設定例

以下は実際の環境で使用されているホスト固有の設定例です。

### Cluster1 ワーカーノード設定例

#### ワーカーノード設定 (host_vars/k8sworker0101.local)

```yaml
k8s_worker_frr:
  enabled: true
  local_asn: 65011
  rfc5549_enabled: false
  ipv4_transport_ipv6_nlri_enabled: false
  router_id: "192.168.30.42"
  cluster_name: "cluster1"
  dc_frr_addresses:
    frr01.local: "192.168.40.49"
  dc_frr_addresses_v6:
    frr01.local: "fd69:6684:61a:2::49"
  advertise_host_route_ipv4: "192.168.40.42/32"
  advertise_host_route_ipv6: "fd69:6684:61a:2::42/128"
```

**設定のポイント**:

- **管理側IPv4アドレス**: `192.168.30.42` (Router IDに使用)
- **K8sネットワーク側IPv4アドレス**: `192.168.40.42` (ホストルート広告)
- **K8sネットワーク側IPv6アドレス**: `fd69:6684:61a:2::42` (ホストルート広告)
- **DC代表FRR**: `frr01.local` (192.168.40.49 / fd69:6684:61a:2::49)
- **標準デュアルスタック構成**: IPv4とIPv6を別々のトランスポートで運用

#### host_vars/k8sworker0102.local

```yaml
k8s_worker_frr:
  enabled: true
  local_asn: 65011
  rfc5549_enabled: false
  ipv4_transport_ipv6_nlri_enabled: false
  router_id: "192.168.30.43"
  cluster_name: "cluster1"
  dc_frr_addresses:
    frr01.local: "192.168.40.49"
  dc_frr_addresses_v6:
    frr01.local: "fd69:6684:61a:2::49"
  advertise_host_route_ipv4: "192.168.40.43/32"
  advertise_host_route_ipv6: "fd69:6684:61a:2::43/128"
```

**k8sworker0101との差分**: Router IDとホストルートのアドレスが異なるのみ (`.42`  =>  `.43`)

### Cluster2 ワーカーノード設定例

#### host_vars/k8sworker0201.local

```yaml
k8s_worker_frr:
  enabled: true
  local_asn: 65012
  rfc5549_enabled: false
  ipv4_transport_ipv6_nlri_enabled: false
  router_id: "192.168.30.52"
  cluster_name: "cluster2"
  dc_frr_addresses:
    frr02.local: "192.168.50.48"
  dc_frr_addresses_v6:
    frr02.local: "fd69:6684:61a:3::48"
  advertise_host_route_ipv4: "192.168.50.52/32"
  advertise_host_route_ipv6: "fd69:6684:61a:3::52/128"
```

**Cluster1との差分**:

- **AS番号**: `65012` (Cluster1は65011)
- **クラスタ名**: `cluster2`
- **DC代表FRR**: `frr02.local` (192.168.50.48 / fd69:6684:61a:3::48)
- **アドレス体系**: K8sネットワークが `192.168.50.x` / `fd69:6684:61a:3::x`

#### host_vars/k8sworker0202.local

```yaml
k8s_worker_frr:
  enabled: true
  local_asn: 65012
  rfc5549_enabled: false
  ipv4_transport_ipv6_nlri_enabled: false
  router_id: "192.168.30.53"
  cluster_name: "cluster2"
  dc_frr_addresses:
    frr02.local: "192.168.50.48"
  dc_frr_addresses_v6:
    frr02.local: "fd69:6684:61a:3::48"
  advertise_host_route_ipv4: "192.168.50.53/32"
  advertise_host_route_ipv6: "fd69:6684:61a:3::53/128"
```

**k8sworker0201との差分**: Router IDとホストルートのアドレスが異なるのみ (`.52`  =>  `.53`)

### DC代表FRR設定例

#### host_vars/frr01.local (Cluster1 DC代表)

```yaml
# K8sノードとの iBGP ピア (IPv4セッション)
frr_k8s_neighbors:
  - { addr: "192.168.40.41", asn: 65011, desc: "C1 control-plane" }
  - { addr: "192.168.40.42", asn: 65011, desc: "C1 worker-1" }
  - { addr: "192.168.40.43", asn: 65011, desc: "C1 worker-2" }

# K8sノードとの iBGP ピア (IPv6セッション)
frr_k8s_neighbors_v6:
  - { addr: "fd69:6684:61a:2::41", asn: 65011, desc: "C1 control-plane" }
  - { addr: "fd69:6684:61a:2::42", asn: 65011, desc: "C1 worker-1" }
  - { addr: "fd69:6684:61a:2::43", asn: 65011, desc: "C1 worker-2" }

# 疑似外部ネットワーク側 eBGP ピア (IPv4セッション)
frr_ebgp_neighbors:
  - { addr: "192.168.255.81", asn: 65100, desc: "External GW" }

# 疑似外部ネットワーク側 eBGP ピア (IPv6セッション)
frr_ebgp_neighbors_v6:
  - { addr: "fd69:6684:61a:90::81", asn: 65100, desc: "External GW" }
```

**設定のポイント**:

- **frr-basicロールで管理**: k8s-worker-frrロールの対象外
- **iBGPピア**: Cluster1の全K8sノード (コントロールプレイン含む)
- **eBGPピア**: 外部ゲートウェイ (extgw.local, AS 65100)
- **標準デュアルスタック**: IPv4とIPv6で別々のピアリスト

#### host_vars/frr02.local (Cluster2 DC代表)

```yaml
# K8sノードとの iBGP ピア (IPv4セッション)
frr_k8s_neighbors:
  - { addr: "192.168.50.51", asn: 65012, desc: "C2 control-plane" }
  - { addr: "192.168.50.52", asn: 65012, desc: "C2 worker-1" }
  - { addr: "192.168.50.53", asn: 65012, desc: "C2 worker-2" }

# K8sノードとの iBGP ピア (IPv6セッション)
frr_k8s_neighbors_v6:
  - { addr: "fd69:6684:61a:3::51", asn: 65012, desc: "C2 control-plane" }
  - { addr: "fd69:6684:61a:3::52", asn: 65012, desc: "C2 worker-1" }
  - { addr: "fd69:6684:61a:3::53", asn: 65012, desc: "C2 worker-2" }

# 疑似外部ネットワーク側 eBGP ピア (IPv4セッション)
frr_ebgp_neighbors:
  - { addr: "192.168.255.81", asn: 65100, desc: "External GW" }

# 疑似外部ネットワーク側 eBGP ピア (IPv6セッション)
frr_ebgp_neighbors_v6:
  - { addr: "fd69:6684:61a:90::81", asn: 65100, desc: "External GW" }
```

**frr01との差分**:

- **AS番号**: `65012` (Cluster2)
- **アドレス体系**: `192.168.50.x` / `fd69:6684:61a:3::x`

### 外部ゲートウェイ設定例

#### host_vars/extgw.local

```yaml
# K8sノードとは直接話さない
frr_k8s_neighbors: []
frr_k8s_neighbors_v6: []

# frr01/frr02とeBGP接続 (IPv4セッション)
frr_ebgp_neighbors:
  - { addr: "192.168.255.49", asn: 65011, desc: "Cluster1 Gateway (frr01)" }
  - { addr: "192.168.255.48", asn: 65012, desc: "Cluster2 Gateway (frr02)" }

# frr01/frr02とeBGP接続 (IPv6セッション)
frr_ebgp_neighbors_v6:
  - { addr: "fd69:6684:61a:90::49", asn: 65011, desc: "Cluster1 Gateway (frr01)" }
  - { addr: "fd69:6684:61a:90::48", asn: 65012, desc: "Cluster2 Gateway (frr02)" }
```

**設定のポイント**:

- **iBGPピア**: なし (K8sノードとは直接接続しない)
- **eBGPピア**: frr01 (AS 65011) とfrr02 (AS 65012)
- **役割**: データセンター間のゲートウェイとして機能

### ネットワーク構成まとめ

| ノード | AS | 管理IPv4 | K8sネットワークIPv4 | K8sネットワークIPv6 | DC代表FRR |
|--------|-----|----------|-----------|-----------|-----------|
| k8sworker0101 | 65011 | 192.168.30.42 | 192.168.40.42 | fd69:6684:61a:2::42 | frr01 |
| k8sworker0102 | 65011 | 192.168.30.43 | 192.168.40.43 | fd69:6684:61a:2::43 | frr01 |
| k8sworker0201 | 65012 | 192.168.30.52 | 192.168.50.52 | fd69:6684:61a:3::52 | frr02 |
| k8sworker0202 | 65012 | 192.168.30.53 | 192.168.50.53 | fd69:6684:61a:3::53 | frr02 |
| frr01 | 65011 | 192.168.30.49 | 192.168.40.49 | fd69:6684:61a:2::49 | - |
| frr02 | 65012 | 192.168.30.48 | 192.168.50.48 | fd69:6684:61a:3::48 | - |
| extgw | 65100 | 192.168.30.81 | 192.168.255.81 | fd69:6684:61a:90::81 | - |

**BGP接続構成**:

- **Cluster1 (AS 65011)**: k8sworker01xx <=> (iBGP) <=> frr01 <=> (eBGP) <=> extgw
- **Cluster2 (AS 65012)**: k8sworker02xx <=> (iBGP) <=> frr02 <=> (eBGP) <=> extgw
- **クラスタ間通信**: extgw経由でルートを交換

## 標準デュアルスタックでの検証方法

以下は標準デュアルスタック構成 (IPv4とIPv6を別々のトランスポートで運ぶ) での具体的な検証手順です。

### 標準デュアルスタック設定の特徴

標準デュアルスタック構成では, IPv4とIPv6で独立したBGPセッションを確立します:

- **IPv4 BGPセッション**: IPv4トランスポートでIPv4ルートを交換
- **IPv6 BGPセッション**: IPv6トランスポートでIPv6ルートを交換
- **セッション数**: 2つ (IPv4用とIPv6用)
- **設定キー**: `dc_frr_addresses` (IPv4) と `dc_frr_addresses_v6` (IPv6) の両方が必要

### 標準デュアルスタック設定例

#### 標準デュアルスタック設定でのワーカーノード設定 (host_vars/k8sworker0101.local)

```yaml
k8s_worker_frr:
  enabled: true
  local_asn: 65011
  rfc5549_enabled: false
  ipv4_transport_ipv6_nlri_enabled: false  # 標準デュアルスタック
  router_id: "192.168.30.42"
  cluster_name: "cluster1"

  # IPv4 BGP セッション用
  dc_frr_addresses:
    frr01.local: "192.168.40.49"

  # IPv6 BGP セッション用
  dc_frr_addresses_v6:
    frr01.local: "fd69:6684:61a:2::49"

  # ホストルート (それぞれのセッションで広告)
  advertise_host_route_ipv4: "192.168.40.42/32"
  advertise_host_route_ipv6: "fd69:6684:61a:2::42/128"
```

**設定のポイント**:

- `ipv4_transport_ipv6_nlri_enabled: false` (デフォルト値, 明示的に記載)
- `dc_frr_addresses` と `dc_frr_addresses_v6` の両方を定義
- IPv4ルートはIPv4セッション, IPv6ルートはIPv6セッションで交換

#### DC代表FRR設定 (host_vars/frr01.local)

```yaml
# K8sノードとの iBGP ピア (IPv4セッション)
frr_k8s_neighbors:
  - { addr: "192.168.40.41", asn: 65011, desc: "C1 control-plane" }
  - { addr: "192.168.40.42", asn: 65011, desc: "C1 worker-1" }
  - { addr: "192.168.40.43", asn: 65011, desc: "C1 worker-2" }

# K8sノードとの iBGP ピア (IPv6セッション)
frr_k8s_neighbors_v6:
  - { addr: "fd69:6684:61a:2::41", asn: 65011, desc: "C1 control-plane" }
  - { addr: "fd69:6684:61a:2::42", asn: 65011, desc: "C1 worker-1" }
  - { addr: "fd69:6684:61a:2::43", asn: 65011, desc: "C1 worker-2" }

# 疑似外部ネットワーク側 eBGP ピア
frr_ebgp_neighbors:
  - { addr: "192.168.255.81", asn: 65100, desc: "External GW" }

frr_ebgp_neighbors_v6:
  - { addr: "fd69:6684:61a:90::81", asn: 65100, desc: "External GW" }
```

### 前提条件

本例で使用する設定値:

- **検証対象ワーカーノード**: `k8sworker0101.local`
- **AS 番号 (iBGP)**: `65011`
- **ワーカーノード管理側 IPv4 アドレス**: `192.168.30.42`
- **ワーカーノード DC 接続側 IPv4 アドレス**: `192.168.40.42`
- **ワーカーノード DC 接続側 IPv6 アドレス**: `fd69:6684:61a:2::42`
- **BGP Router ID**: `192.168.30.42`
- **iBGP ピア (DC 代表 FRR)**:
  - `frr01.local`: IPv4 `192.168.40.49`, IPv6 `fd69:6684:61a:2::49` (AS 65011)
- **クラスタ名**: `cluster1`
- **広告する経路**:
  - ホストルート IPv4: `192.168.40.42/32`
  - ホストルート IPv6: `fd69:6684:61a:2::42/128`
  - Pod CIDR IPv4: `10.244.0.0/16`
  - Pod CIDR IPv6: `fdb6:6e92:3cfb:0200::/56`
  - Service CIDR IPv4: `10.254.0.0/16`
  - Service CIDR IPv6: `fdb6:6e92:3cfb:feed::/112`

### 1. FRR サービス状態の確認

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
systemctl status frr
```

**期待される出力**:

```plaintext
● frr.service - FRRouting
     Loaded: loaded (/usr/lib/systemd/system/frr.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-01-26 18:00:12 JST; 1min 24s ago
       Docs: https://frrouting.readthedocs.io/en/latest/setup.html
    Process: 6957 ExecStart=/usr/lib/frr/frrinit.sh start (code=exited, status=0/SUCCESS)
   Main PID: 6967 (watchfrr)
     Status: "FRR Operational"
      Tasks: 13 (limit: 4594)
     Memory: 19.4M (peak: 28.9M)
        CPU: 183ms
     CGroup: /system.slice/frr.service
             ├─6967 /usr/lib/frr/watchfrr -d -F traditional zebra bgpd staticd
             ├─6980 /usr/lib/frr/zebra -d -F traditional -A 127.0.0.1
             ├─6985 /usr/lib/frr/bgpd -d -F traditional -A 127.0.0.1
             └─6992 /usr/lib/frr/staticd -d -F traditional

 1月 26 18:00:12 k8sworker0101 watchfrr[6967]: [QDG3Y-BY5TN] zebra state -> up : connect succeeded
 1月 26 18:00:12 k8sworker0101 watchfrr[6967]: [QDG3Y-BY5TN] bgpd state -> up : connect succeeded
 1月 26 18:00:12 k8sworker0101 watchfrr[6967]: [QDG3Y-BY5TN] staticd state -> up : connect succeeded
 1月 26 18:00:12 k8sworker0101 watchfrr[6967]: [KWE5Q-QNGFC] all daemons up, doing startup-complete notify
 1月 26 18:00:12 k8sworker0101 frrinit.sh[6957]:  * Started watchfrr
 1月 26 18:00:12 k8sworker0101 systemd[1]: Started frr.service - FRRouting.
 1月 26 18:00:16 k8sworker0101 bgpd[6985]: [ZM2F8-MV4BJ][EC 33554509] Interface: ens192 does not have a v6 LL address associated with it, waiting until one is created for it
 1月 26 18:00:16 k8sworker0101 bgpd[6985]: [ZM2F8-MV4BJ][EC 33554509] Interface: ens192 does not have a v6 LL address associated with it, waiting until one is created for it
 1月 26 18:00:18 k8sworker0101 bgpd[6985]: [M59KS-A3ZXZ] bgp_update_receive: rcvd End-of-RIB for IPv4 Unicast from 192.168.40.49 in vrf default
 1月 26 18:00:18 k8sworker0101 bgpd[6985]: [M59KS-A3ZXZ] bgp_update_receive: rcvd End-of-RIB for IPv6 Unicast from fd69:6684:61a:2::49 in vrf default
```

**確認ポイント**:

- `Active: active (running)` が表示される
- zebra, bgpd, staticd のプロセスが起動している
- `all daemons up, doing startup-complete notify` メッセージが表示される

### 2. FRR 設定の構文確認

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
sudo vtysh -c "show running-config" | head -20
```

**期待される出力**:

```plaintext
Building configuration...

Current configuration:
!
frr version 8.4.4
frr defaults traditional
hostname k8sworker0101
log syslog informational
service integrated-vtysh-config
!
ip route 10.244.0.0/16 ens160
ip route 10.254.0.0/16 ens160
ip route 192.168.40.42/32 ens160
ipv6 route fdb6:6e92:3cfb:200::/56 ens160
ipv6 route fdb6:6e92:3cfb:feed::/112 ens160
ipv6 route fd69:6684:61a:2::42/128 ens160
!
router bgp 65011
 bgp router-id 192.168.30.42
 no bgp ebgp-requires-policy
```

**確認ポイント**:

- 構文エラーが表示されない
- FRR バージョンが表示される (例: 8.4.4)
- 静的ルート定義が存在する (Pod CIDR, Service CIDR, ホストルート - IPv4/IPv6)
- AS 番号 (`65011`) と Router ID (`192.168.30.42`) が正しい

### 3. iBGP セッション状態の確認

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
sudo vtysh -c "show bgp summary"
```

**期待される出力**:

```plaintext
IPv4 Unicast Summary (VRF default):
BGP router identifier 192.168.30.42, local AS number 65011 vrf-id 0
BGP table version 9
RIB entries 16, using 3072 bytes of memory
Peers 1, using 724 KiB of memory

Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
192.168.40.49   4      65011         8         6        0    0    0 00:02:25            6        3 DC-FRR frr01.local

Total number of neighbors 1

IPv6 Unicast Summary (VRF default):
BGP router identifier 192.168.30.42, local AS number 65011 vrf-id 0
BGP table version 11
RIB entries 19, using 3648 bytes of memory
Peers 1, using 724 KiB of memory

Neighbor            V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
fd69:6684:61a:2::49 4      65011         8         6        0    0    0 00:02:25            8        3 DC-FRR frr01.local

Total number of neighbors 1
```

**確認ポイント**:

- **IPv4とIPv6で異なるネイバーアドレスが表示される**
  - IPv4: `192.168.40.49` (IPv4トランスポート)
  - IPv6: `fd69:6684:61a:2::49` (IPv6トランスポート)
- **2つの独立したBGPセッション**が確立している
- `State/PfxRcd` が数値 (IPv4: `6`, IPv6: `8`) であり, エラー状態でない
- `PfxSnt` が `3` である (Pod CIDR, Service CIDR, ホストルートの 3 つを送信)
- `Up/Down` に稼働時間が表示されている

**IPv4のみの詳細確認**:

```bash
sudo vtysh -c "show ip bgp summary"
```

**期待される出力**:

```plaintext
IPv4 Unicast Summary (VRF default):
BGP router identifier 192.168.30.42, local AS number 65011 vrf-id 0
BGP table version 9
RIB entries 16, using 3072 bytes of memory
Peers 1, using 724 KiB of memory

Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
192.168.40.49   4      65011         8         6        0    0    0 00:02:40            6        3 DC-FRR frr01.local

Total number of neighbors 1
```

**IPv6のみの詳細確認**:

```bash
sudo vtysh -c "show bgp ipv6 unicast summary"
```

**期待される出力**:

```plaintext
BGP router identifier 192.168.30.42, local AS number 65011 vrf-id 0
BGP table version 11
RIB entries 19, using 3648 bytes of memory
Peers 1, using 724 KiB of memory

Neighbor            V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
fd69:6684:61a:2::49 4      65011         8         6        0    0    0 00:02:54            8        3 DC-FRR frr01.local

Total number of neighbors 1
```

### 4. 広告経路の確認 (IPv4)

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
sudo vtysh -c "show ip bgp"
```

**期待される出力**:

```plaintext
BGP table version is 9, local router ID is 192.168.30.42, vrf id 0
Default local pref 100, local AS 65011
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

   Network          Next Hop            Metric LocPrf Weight Path
*>i10.243.0.0/16    192.168.255.48                100      0 65100 65012 ?
*> 10.244.0.0/16    0.0.0.0                  0         32768 ?
*>i10.253.0.0/16    192.168.255.48                100      0 65100 65012 ?
*> 10.254.0.0/16    0.0.0.0                  0         32768 ?
*>i192.168.30.0/24  192.168.40.49            0    100      0 i
*>i192.168.40.0/24  192.168.40.49            0    100      0 i
*> 192.168.40.42/32 0.0.0.0                  0         32768 ?
*>i192.168.50.0/24  192.168.255.48                100      0 65100 65012 i
*>i192.168.255.0/24 192.168.40.49            0    100      0 i

Displayed  9 routes and 9 total paths
```

**確認ポイント**:

- ワーカーノードから広告された 3 つの経路 (Pod CIDR, Service CIDR, ホストルート) が表示される
- `Next Hop` が `0.0.0.0` (自ノードで広告) である
- `Origin codes` が `?` (incomplete, `redistribute static` で広告された経路) である

### 5. 広告経路の確認 (IPv6)

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
sudo vtysh -c "show bgp ipv6"
```

**期待される出力**:

```plaintext
BGP table version is 11, local router ID is 192.168.30.42, vrf id 0
Default local pref 100, local AS 65011
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

   Network          Next Hop            Metric LocPrf Weight Path
*>ifd69:6684:61a:2::/64
                    fe80::250:56ff:fe00:4a1c
                                             0    100      0 i
*> fd69:6684:61a:2::42/128
                    ::                       0         32768 ?
*>ifd69:6684:61a:3::/64
                    fd69:6684:61a:90::48
                                                  100      0 65100 65012 i
*>ifd69:6684:61a:3::52/128
                    fd69:6684:61a:90::48
                                                  100      0 65100 65012 ?
*>ifd69:6684:61a:3::53/128
                    fd69:6684:61a:90::48
                                                  100      0 65100 65012 ?
*>ifd69:6684:61a:90::/64
                    fe80::250:56ff:fe00:4a1c
                                             0    100      0 i
*>ifdad:ba50:248b:1::/64
                    fe80::250:56ff:fe00:4a1c
                                             0    100      0 i
*>ifdb6:6e92:3cfb:100::/56
                    fd69:6684:61a:90::48
                                                  100      0 65100 65012 ?
*> fdb6:6e92:3cfb:200::/56
                    ::                       0         32768 ?
*>ifdb6:6e92:3cfb:feec::/112
                    fd69:6684:61a:90::48
                                                  100      0 65100 65012 ?
*> fdb6:6e92:3cfb:feed::/112
                    ::                       0         32768 ?

Displayed  11 routes and 11 total paths
```

**確認ポイント**:

- ワーカーノードから広告された 3 つの IPv6 経路 (ホストルート, Pod CIDR, Service CIDR) が表示される
- `Next Hop` が `::` (自ノード) である
- `Origin codes` が `?` (incomplete) である
- **IPv6セッション経由で受信**した経路も表示される

### 6. カーネルルーティングテーブルの確認

**実施ノード**: `k8sworker0101.local`

#### IPv4ルートの確認

**コマンド**:

```bash
ip route | grep proto
```

**期待される出力**:

```plaintext
default via 192.168.30.10 dev ens160 proto static metric 100
10.243.0.0/16 nhid 62 via 192.168.40.49 dev ens192 proto bgp metric 20
10.244.0.0/24 via 192.168.30.41 dev ens160 proto kernel
10.244.0.0/16 nhid 53 dev ens160 proto static metric 20
10.244.3.0/24 via 10.244.3.197 dev cilium_host proto kernel src 10.244.3.197
10.244.3.197 dev cilium_host proto kernel scope link
10.244.4.0/24 via 192.168.30.43 dev ens160 proto kernel
10.253.0.0/16 nhid 62 via 192.168.40.49 dev ens192 proto bgp metric 20
10.254.0.0/16 nhid 53 dev ens160 proto static metric 20
192.168.30.0/24 dev ens160 proto kernel scope link src 192.168.30.42 metric 100
192.168.40.0/24 dev ens192 proto kernel scope link src 192.168.40.42 metric 101
192.168.40.42 nhid 53 dev ens160 proto static metric 20
192.168.50.0/24 nhid 62 via 192.168.40.49 dev ens192 proto bgp metric 20
192.168.255.0/24 nhid 57 via 192.168.40.49 dev ens192 proto bgp metric 20
```

**確認ポイント**:

- `proto bgp` のルートが存在する (他クラスタからの学習経路, K8sネットワーク側のens192経由)
- `proto static` のルートが存在する (自ノードで広告する経路)
- BGPルートのnexthopは `192.168.40.49` (DC代表FRR, K8sネットワーク経由で到達)

#### IPv6ルートの確認

**コマンド**:

```bash
ip -6 route | grep proto
```

**期待される出力**:

```plaintext
fd69:6684:61a:2::42 nhid 52 dev ens160 proto static metric 20 pref medium
fd69:6684:61a:2::/64 dev ens192 proto kernel metric 101 pref medium
fd69:6684:61a:3::52 nhid 58 via fe80::250:56ff:fe00:4a1c dev ens192 proto bgp metric 20 pref medium
fd69:6684:61a:3::53 nhid 58 via fe80::250:56ff:fe00:4a1c dev ens192 proto bgp metric 20 pref medium
fd69:6684:61a:3::/64 nhid 58 via fe80::250:56ff:fe00:4a1c dev ens192 proto bgp metric 20 pref medium
fd69:6684:61a:90::/64 nhid 58 via fe80::250:56ff:fe00:4a1c dev ens192 proto bgp metric 20 pref medium
fdad:ba50:248b:1::10 dev ens160 proto static metric 100 pref medium
fdad:ba50:248b:1::/64 dev ens160 proto kernel metric 100 pref medium
fdb6:6e92:3cfb:100::/56 nhid 58 via fe80::250:56ff:fe00:4a1c dev ens192 proto bgp metric 20 pref medium
fdb6:6e92:3cfb:200::/64 via fdad:ba50:248b:1::41 dev ens160 proto kernel metric 1024 pref medium
fdb6:6e92:3cfb:203::f5bf dev cilium_host proto kernel metric 256 pref medium
fdb6:6e92:3cfb:203::/64 dev cilium_host proto kernel src fdb6:6e92:3cfb:203::f5bf metric 1024 pref medium
fdb6:6e92:3cfb:204::/64 via fdad:ba50:248b:1::43 dev ens160 proto kernel metric 1024 pref medium
fdb6:6e92:3cfb:200::/56 nhid 52 dev ens160 proto static metric 20 pref medium
fdb6:6e92:3cfb:feec::/112 nhid 58 via fe80::250:56ff:fe00:4a1c dev ens192 proto bgp metric 20 pref medium
fdb6:6e92:3cfb:feed::/112 dev ens160 proto static metric 1024 pref medium
fd69:6684:61a:2::42 dev ens160 proto static metric 1024 pref medium
```

**確認ポイント**:

- `proto bgp` のIPv6ルートが存在する (他クラスタからの学習経路)
- `proto static` のIPv6ルートが存在する (自ノードで広告する経路)

### 7. BGP ネイバー詳細情報の確認

**実施ノード**: `k8sworker0101.local`

#### IPv4 ネイバーの詳細

**コマンド**:

```bash
sudo vtysh -c "show ip bgp neighbors 192.168.40.49"
```

**期待される出力** (抜粋):

```plaintext
BGP neighbor is 192.168.40.49, remote AS 65011, local AS 65011, internal link
  Local Role: undefined
  Remote Role: undefined
 Description: DC-FRR frr01.local (IPv4)
Hostname: frr01
  BGP version 4, remote router ID 192.168.40.49, local router ID 192.168.30.42
  BGP state = Established, up for 00:04:22
  Last read 00:00:22, Last write 00:00:22
  Hold time is 180 seconds, keepalive interval is 60 seconds
  Configured hold time is 180 seconds, keepalive interval is 60 seconds
  Configured conditional advertisements interval is 60 seconds
  Neighbor capabilities:
    4 Byte AS: advertised and received
    Extended Message: advertised and received
    AddPath:
      IPv4 Unicast: RX advertised and received
    Long-lived Graceful Restart: advertised and received
      Address families by peer:
    Route refresh: advertised and received(old & new)
    Enhanced Route Refresh: advertised and received
    Address Family IPv4 Unicast: advertised and received
    Hostname Capability: advertised (name: k8sworker0101,domain name: n/a) received (name: frr01,domain name: n/a)
    Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Address families by peer:
        none
  Graceful restart information:
    End-of-RIB send: IPv4 Unicast
    End-of-RIB received: IPv4 Unicast
    Local GR Mode: Helper*
    Remote GR Mode: Helper
    R bit: False
    N bit: True
    Timers:
      Configured Restart Time(sec): 120
      Received Restart Time(sec): 120
    IPv4 Unicast:
      F bit: False
      End-of-RIB sent: Yes
      End-of-RIB sent after update: Yes
      End-of-RIB received: Yes
      Timers:
        Configured Stale Path Time(sec): 360
  Message statistics:
    Inq depth is 0
    Outq depth is 0
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:                2          4
    Keepalives:             5          5
    Route Refresh:          0          0
    Capability:             0          0
    Total:                  8         10
  Minimum time between advertisement runs is 0 seconds

 For address family: IPv4 Unicast
  Update group 2, subgroup 2
  Packet Queue length 0
  Community attribute sent to this neighbor(all)
  Outbound path policy configured
  Route map for outgoing advertisements is *RM-V4-OUT
  6 accepted prefixes

  Connections established 1; dropped 0
  Last reset 00:04:26,  Waiting for peer OPEN
  Internal BGP neighbor may be up to 255 hops away.
Local host: 192.168.40.42, Local port: 39006
Foreign host: 192.168.40.49, Foreign port: 179
Nexthop: 192.168.40.42
Nexthop global: fd69:6684:61a:2::42
Nexthop local: fe80::250:56ff:fe00:7b26
BGP connection: shared network
BGP Connect Retry Timer in Seconds: 120
Estimated round trip time: 8 ms
Read thread: on  Write thread: on  FD used: 24
```

**確認ポイント**:

- `BGP state = Established` である
- `For address family: IPv4 Unicast` が表示される
- `6 accepted prefixes` が表示される (他クラスタからの経路)
- `Route map for outgoing advertisements is *RM-V4-OUT` が適用されている
- `Local host: 192.168.40.42` (K8sネットワーク側アドレス)
- `Foreign host: 192.168.40.49` (DC代表FRR)

#### IPv6 ネイバーの詳細

**コマンド**:

```bash
sudo vtysh -c "show bgp ipv6 neighbors fd69:6684:61a:2::49"
```

**期待される出力** (抜粋):

```plaintext
BGP neighbor is fd69:6684:61a:2::49, remote AS 65011, local AS 65011, internal link
  Local Role: undefined
  Remote Role: undefined
 Description: DC-FRR frr01.local (IPv6)
Hostname: frr01
  BGP version 4, remote router ID 192.168.40.49, local router ID 192.168.30.42
  BGP state = Established, up for 00:04:35
  Last read 00:00:35, Last write 00:00:35
  Hold time is 180 seconds, keepalive interval is 60 seconds
  Configured hold time is 180 seconds, keepalive interval is 60 seconds
  Configured conditional advertisements interval is 60 seconds
  Neighbor capabilities:
    4 Byte AS: advertised and received
    Extended Message: advertised and received
    AddPath:
      IPv6 Unicast: RX advertised and received
    Long-lived Graceful Restart: advertised and received
      Address families by peer:
    Route refresh: advertised and received(old & new)
    Enhanced Route Refresh: advertised and received
    Address Family IPv4 Unicast: received
    Address Family IPv6 Unicast: advertised and received
    Hostname Capability: advertised (name: k8sworker0101,domain name: n/a) received (name: frr01,domain name: n/a)
    Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Address families by peer:
        none
  Graceful restart information:
    End-of-RIB send: IPv6 Unicast
    End-of-RIB received: IPv6 Unicast
    Local GR Mode: Helper*
    Remote GR Mode: Helper
    R bit: False
    N bit: True
    Timers:
      Configured Restart Time(sec): 120
      Received Restart Time(sec): 120
    IPv6 Unicast:
      F bit: False
      End-of-RIB sent: Yes
      End-of-RIB sent after update: Yes
      End-of-RIB received: Yes
      Timers:
        Configured Stale Path Time(sec): 360
  Message statistics:
    Inq depth is 0
    Outq depth is 0
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:                2          4
    Keepalives:             5          5
    Route Refresh:          0          0
    Capability:             0          0
    Total:                  8         10
  Minimum time between advertisement runs is 0 seconds

 For address family: IPv6 Unicast
  Update group 1, subgroup 1
  Packet Queue length 0
  Community attribute sent to this neighbor(all)
  Outbound path policy configured
  Route map for outgoing advertisements is *RM-V6-OUT
  8 accepted prefixes

  Connections established 1; dropped 0
  Last reset 00:04:39,  Waiting for peer OPEN
  Internal BGP neighbor may be up to 255 hops away.
Local host: fd69:6684:61a:2::42, Local port: 43722
Foreign host: fd69:6684:61a:2::49, Foreign port: 179
Nexthop: 192.168.40.42
Nexthop global: fd69:6684:61a:2::42
Nexthop local: fe80::250:56ff:fe00:7b26
BGP connection: shared network
BGP Connect Retry Timer in Seconds: 120
Estimated round trip time: 8 ms
Read thread: on  Write thread: on  FD used: 25
```

**確認ポイント**:

- `BGP state = Established` である
- `For address family: IPv6 Unicast` が表示される
- **IPv4とIPv6で異なるUpdate group**が使用されている (独立したセッション: IPv4はUpdate group 2, IPv6はUpdate group 1)
- `8 accepted prefixes` が表示される (他クラスタからの経路)
- `Route map for outgoing advertisements is *RM-V6-OUT` が適用されている
- `Local host: fd69:6684:61a:2::42` (K8sネットワーク側IPv6アドレス)
- `Foreign host: fd69:6684:61a:2::49` (DC代表FRR)

### 8. DC 代表 FRR での受信経路確認

**実施ノード**: `frr01.local` または `frr02.local`

#### 8.1 IPv4 経路の確認

**コマンド** (frr01.local で実行):

```bash
sudo vtysh -c "show ip bgp neighbors 192.168.40.42 routes"
```

**期待される出力**:

```plaintext
BGP table version is 88, local router ID is 192.168.40.49, vrf id 0
Default local pref 100, local AS 65011
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

   Network          Next Hop            Metric LocPrf Weight Path
*>i10.244.0.0/16    192.168.40.42            0    100      0 ?
*>i10.254.0.0/16    192.168.40.42            0    100      0 ?
  i192.168.40.42/32 192.168.40.42            0    100      0 ?

Displayed  3 routes and 17 total paths
```

**確認ポイント**:

- ワーカーノード (`192.168.40.42`) から広告された 3 つの経路 (Pod CIDR, Service CIDR, ホストルート) が表示される
- `Origin codes` が `?` (incomplete, `redistribute static` で広告された経路) である
- `LocPrf` が `100` (iBGP デフォルト Local Preference) である
- ホストルート (`192.168.40.42/32`) に `*>` が付いていない場合, 他のパスがベストパスとして選択されている可能性がある ( 複数のワーカーノードから同じホストルートが広告されている場合など )
- "Displayed 3 routes and 17 total paths" は, 3つの異なるネットワークプレフィクスに対して合計17のBGPパスが存在することを示す ( 複数のiBGPピアから同じ経路を受信している場合 )

#### 8.2 IPv6 経路の確認

**コマンド** (frr01.local で実行):

```bash
sudo vtysh -c "show bgp ipv6 unicast neighbors fd69:6684:61a:2::42 routes"
```

**期待される出力**:

```plaintext
BGP table version is 152, local router ID is 192.168.40.49, vrf id 0
Default local pref 100, local AS 65011
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

   Network          Next Hop            Metric LocPrf Weight Path
*>ifd69:6684:61a:2::42/128
                    fe80::250:56ff:fe00:7b26
                                             0    100      0 ?
*>ifdb6:6e92:3cfb:200::/56
                    fe80::250:56ff:fe00:7b26
                                             0    100      0 ?
*>ifdb6:6e92:3cfb:feed::/112
                    fe80::250:56ff:fe00:7b26
                                             0    100      0 ?

Displayed  3 routes and 15 total paths
```

**確認ポイント**:

- ワーカーノードから広告された 3 つの IPv6 経路 (ホストルート, Pod CIDR, Service CIDR) が表示される
- `Next Hop` が link-local アドレス (`fe80::250:56ff:fe00:7b26`) である (IPv6 BGP の一般的な動作)
- `Origin codes` が `?` (incomplete) である
- **IPv6セッションでIPv6ネイバー (`fd69:6684:61a:2::42`) から受信**している（標準デュアルスタック）
- "Displayed 3 routes and 15 total paths" は, 3つの異なるネットワークプレフィクスに対して合計15のBGPパスが存在することを示す ( 複数のiBGPピアから同じ経路を受信している場合 )

#### 8.3 External Gateway (extgw) での経路確認

**実施ノード**: `extgw.local`

**コマンド**:

```bash
sudo vtysh -c "show ip bgp"
```

**期待される出力**:

```plaintext
BGP table version is 64, local router ID is 192.168.255.81, vrf id 0
Default local pref 100, local AS 65100
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

    Network          Next Hop            Metric LocPrf Weight Path
 *  10.243.0.0/16    192.168.255.48                         0 65012 ?
 *>                  192.168.255.48                         0 65012 ?
 *  10.244.0.0/16    192.168.255.49                         0 65011 ?
 *>                  192.168.255.49                         0 65011 ?
 *  10.253.0.0/16    192.168.255.48                         0 65012 ?
 *>                  192.168.255.48                         0 65012 ?
 *  10.254.0.0/16    192.168.255.49                         0 65011 ?
 *>                  192.168.255.49                         0 65011 ?
 *  192.168.30.0/24  192.168.255.49           0             0 65011 i
 *>                  192.168.255.49           0             0 65011 i
 *                   192.168.255.48           0             0 65012 i
 *                   192.168.255.48           0             0 65012 i
 *  192.168.40.0/24  192.168.255.49           0             0 65011 i
 *>                  192.168.255.49           0             0 65011 i
 *  192.168.50.0/24  192.168.255.48           0             0 65012 i
 *>                  192.168.255.48           0             0 65012 i
 *  192.168.255.0/24 192.168.255.49           0             0 65011 i
 *                   192.168.255.49           0             0 65011 i
 *                   192.168.255.48           0             0 65012 i
 *                   192.168.255.48           0             0 65012 i
 *>                  0.0.0.0                  0         32768 i

Displayed  8 routes and 21 total paths
```

**確認ポイント**:

- 両クラスタ (AS 65011, AS 65012) の Pod/Service CIDR が表示される
- Cluster1: `10.244.0.0/16` (Pod), `10.254.0.0/16` (Service) - Next Hop `192.168.255.49` (frr01)
- Cluster2: `10.243.0.0/16` (Pod), `10.253.0.0/16` (Service) - Next Hop `192.168.255.48` (frr02)
- `Path` に AS 番号が表示される (eBGP 経由)
- 一部の経路で複数パスが存在する (`*` と `*>` の両方が表示)
- "Displayed 8 routes and 21 total paths" は, 8つの異なるネットワークプレフィクスに対して合計21のBGPパスが存在することを示す

**コマンド** (IPv6):

```bash
sudo vtysh -c "show bgp ipv6"
```

**期待される出力**:

```plaintext
BGP table version is 124, local router ID is 192.168.255.81, vrf id 0
Default local pref 100, local AS 65100
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

    Network          Next Hop            Metric LocPrf Weight Path
 *> fd69:6684:61a:2::/64
                    fe80::250:56ff:fe00:4a26
                                             0             0 65011 i
 *> fd69:6684:61a:2::42/128
                    fe80::250:56ff:fe00:4a26
                                                           0 65011 ?
 *> fd69:6684:61a:2::43/128
                    fe80::250:56ff:fe00:4a26
                                                           0 65011 ?
 *> fd69:6684:61a:3::/64
                    fe80::250:56ff:fe00:30c
                                             0             0 65012 i
 *> fd69:6684:61a:3::52/128
                    fe80::250:56ff:fe00:30c
                                                           0 65012 ?
 *> fd69:6684:61a:3::53/128
                    fe80::250:56ff:fe00:30c
                                                           0 65012 ?
 *  fd69:6684:61a:90::/64
                    fe80::250:56ff:fe00:4a26
                                             0             0 65011 i
 *                   fe80::250:56ff:fe00:30c
                                             0             0 65012 i
 *>                  ::                       0         32768 i
 *> fdad:ba50:248b:1::/64
                    fe80::250:56ff:fe00:4a26
                                             0             0 65011 i
 *                   fe80::250:56ff:fe00:30c
                                             0             0 65012 i
 *> fdb6:6e92:3cfb:100::/56
                    fe80::250:56ff:fe00:30c
                                                           0 65012 ?
 *> fdb6:6e92:3cfb:200::/56
                    fe80::250:56ff:fe00:4a26
                                                           0 65011 ?
 *> fdb6:6e92:3cfb:feec::/112
                    fe80::250:56ff:fe00:30c
                                                           0 65012 ?
 *> fdb6:6e92:3cfb:feed::/112
                    fe80::250:56ff:fe00:4a26
                                                           0 65011 ?

Displayed  12 routes and 15 total paths
```

**確認ポイント**:

- 両クラスタ (AS 65011, AS 65012) の IPv6 Pod/Service CIDR が表示される
- Cluster1: `fdb6:6e92:3cfb:200::/56` (Pod), `fdb6:6e92:3cfb:feed::/112` (Service) - Next Hop `fe80::250:56ff:fe00:4a26` (frr01のlink-local)
- Cluster2: `fdb6:6e92:3cfb:100::/56` (Pod), `fdb6:6e92:3cfb:feec::/112` (Service) - Next Hop `fe80::250:56ff:fe00:30c` (frr02のlink-local)
- ワーカーノードのホストルート (`fd69:6684:61a:2::42/128`, `fd69:6684:61a:2::43/128` 等) も表示される
- `Path` に AS 番号が表示される (eBGP 経由)
- Next Hop が link-local アドレス (`fe80::...`) である (IPv6 eBGP の一般的な動作)
- "Displayed 12 routes and 15 total paths" は, 12の異なるネットワークプレフィクスに対して合計15のBGPパスが存在することを示す
- External Gateway が両クラスタへの経路を学習している

### 9. DC 間 Pod 疎通テスト (標準デュアルスタック)

**前提**:

- Cluster1 (context: `kubernetes-admin@kubernetes`, Pod CIDR `10.244.0.0/16`, IPv6 Pod CIDR `fdb6:6e92:3cfb:0200::/56`)
- Cluster2 (context: `kubernetes-admin@kubernetes-2`, Pod CIDR `10.243.0.0/16`, IPv6 Pod CIDR `fdb6:6e92:3cfb:0100::/56`)
- テスト用 Pod として busybox イメージを使用

#### 9.1 既存テスト Pod の削除 ( 存在する場合 )

**コマンド**:

```bash
kubectl --context kubernetes-admin@kubernetes delete pod test-pod --ignore-not-found
kubectl --context kubernetes-admin@kubernetes-2 delete pod test-pod --ignore-not-found
```

#### 9.2 テスト Pod のデプロイ

**コマンド**:

```bash
kubectl --context kubernetes-admin@kubernetes run test-pod --image=busybox --command -- sleep 3600
kubectl --context kubernetes-admin@kubernetes-2 run test-pod --image=busybox --command -- sleep 3600
kubectl --context kubernetes-admin@kubernetes wait --for=condition=Ready pod/test-pod --timeout=60s
kubectl --context kubernetes-admin@kubernetes-2 wait --for=condition=Ready pod/test-pod --timeout=60s
```

**期待される出力**:

```plaintext
pod/test-pod created
pod/test-pod created
pod/test-pod condition met
pod/test-pod condition met
```

#### 9.3 Pod IP アドレスの確認

**コマンド**:

```bash
kubectl --context kubernetes-admin@kubernetes get pod test-pod -o wide
kubectl --context kubernetes-admin@kubernetes-2 get pod test-pod -o wide
kubectl --context kubernetes-admin@kubernetes exec test-pod -- ip addr
kubectl --context kubernetes-admin@kubernetes-2 exec test-pod -- ip addr
```

**期待される出力**:

```plaintext
NAME       READY   STATUS    RESTARTS   AGE   IP                         NODE            NOMINATED NODE   READINESS GATES
test-pod   1/1     Running   0          20s   fdb6:6e92:3cfb:203::d720   k8sworker0101   <none>           <none>
NAME       READY   STATUS    RESTARTS   AGE   IP                         NODE            NOMINATED NODE   READINESS GATES
test-pod   1/1     Running   0          20s   fdb6:6e92:3cfb:103::8806   k8sworker0202   <none>           <none>
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
8: eth0@if9: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue qlen 1000
    link/ether 92:43:6a:22:90:67 brd ff:ff:ff:ff:ff:ff
    inet 10.244.3.140/32 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 fdb6:6e92:3cfb:203::d720/128 scope global flags 02
       valid_lft forever preferred_lft forever
    inet6 fe80::9043:6aff:fe22:9067/64 scope link
       valid_lft forever preferred_lft forever
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
8: eth0@if9: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue qlen 1000
    link/ether 7e:e1:29:73:79:bd brd ff:ff:ff:ff:ff:ff
    inet 10.243.3.33/32 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 fdb6:6e92:3cfb:103::8806/128 scope global flags 02
       valid_lft forever preferred_lft forever
    inet6 fe80::7ce1:29ff:fe73:79bd/64 scope link
       valid_lft forever preferred_lft forever
```

**確認ポイント**:

- Cluster1 Pod: IPv4 `10.244.3.140/32`, IPv6 `fdb6:6e92:3cfb:203::d720/128`
- Cluster2 Pod: IPv4 `10.243.3.33/32`, IPv6 `fdb6:6e92:3cfb:103::8806/128`
- IPv6 アドレスがクラスタ固有の `/56` 範囲に属している (`0200::/56` vs `0100::/56`)

#### 9.4 Cilium 設定の確認

**コマンド**:

```bash
kubectl --context kubernetes-admin@kubernetes get cm -n kube-system cilium-config -o yaml | grep native-routing-cidr
kubectl --context kubernetes-admin@kubernetes-2 get cm -n kube-system cilium-config -o yaml | grep native-routing-cidr
```

**期待される出力**:

```plaintext
  ipv4-native-routing-cidr: 10.244.0.0/16
  ipv6-native-routing-cidr: fdb6:6e92:3cfb:0200::/56
  ipv4-native-routing-cidr: 10.243.0.0/16
  ipv6-native-routing-cidr: fdb6:6e92:3cfb:0100::/56
```

**確認ポイント**:

- 各クラスタで異なる `/16` (IPv4) と `/56` (IPv6) 範囲が設定されている
- FRR が広告している Pod CIDR と一致している

#### 9.5 Cluster1  =>  Cluster2 疎通テスト (IPv4)

**コマンド**:

```bash
kubectl --context kubernetes-admin@kubernetes exec test-pod -- ping -c 3 10.243.3.33
```

**期待される出力**:

```plaintext
PING 10.243.3.33 (10.243.3.33): 56 data bytes
64 bytes from 10.243.3.33: seq=0 ttl=59 time=1.668 ms
64 bytes from 10.243.3.33: seq=1 ttl=59 time=0.517 ms
64 bytes from 10.243.3.33: seq=2 ttl=59 time=0.532 ms

--- 10.243.3.33 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.517/0.905/1.668 ms
```

**確認ポイント**:

- TTL が `59` (複数ホップ経由)
- 0% パケットロス
- RTT が 0.5-1.7ms 程度 (LAN 環境)
- busybox の ping 出力形式 ( `seq=0` 形式 )

#### 9.6 Cluster2  =>  Cluster1 疎通テスト (IPv4)

**コマンド**:

```bash
kubectl --context kubernetes-admin@kubernetes-2 exec test-pod -- ping -c 3 10.244.3.140
```

**期待される出力**:

```plaintext
PING 10.244.3.140 (10.244.3.140): 56 data bytes
64 bytes from 10.244.3.140: seq=0 ttl=60 time=0.788 ms
64 bytes from 10.244.3.140: seq=1 ttl=60 time=0.471 ms
64 bytes from 10.244.3.140: seq=2 ttl=60 time=0.417 ms

--- 10.244.3.140 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.417/0.558/0.788 ms
```

**確認ポイント**:

- TTL が `60` (複数ホップ経由)
- 0% パケットロス
- 双方向での IPv4 通信が確立している

#### 9.7 Cluster1  =>  Cluster2 疎通テスト (IPv6)

**コマンド**:

```bash
kubectl --context kubernetes-admin@kubernetes exec test-pod -- ping -c 3 fdb6:6e92:3cfb:103::8806
```

**期待される出力**:

```plaintext
PING fdb6:6e92:3cfb:103::8806 (fdb6:6e92:3cfb:103::8806): 56 data bytes
64 bytes from fdb6:6e92:3cfb:103::8806: seq=0 ttl=59 time=1.022 ms
64 bytes from fdb6:6e92:3cfb:103::8806: seq=1 ttl=59 time=0.679 ms
64 bytes from fdb6:6e92:3cfb:103::8806: seq=2 ttl=59 time=0.685 ms

--- fdb6:6e92:3cfb:103::8806 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.679/0.795/1.022 ms
```

**確認ポイント**:

- TTL が `59` (複数ホップ経由)
- 0% パケットロス
- RTT が 0.6-1.0ms 程度
- IPv6 アドレスが Cluster2 の範囲 (`0100::/56`) に属している

#### 9.8 Cluster2  =>  Cluster1 疎通テスト (IPv6)

**コマンド**:

```bash
kubectl --context kubernetes-admin@kubernetes-2 exec test-pod -- ping -c 3 fdb6:6e92:3cfb:203::d720
```

**期待される出力**:

```plaintext
PING fdb6:6e92:3cfb:203::d720 (fdb6:6e92:3cfb:203::d720): 56 data bytes
64 bytes from fdb6:6e92:3cfb:203::d720: seq=0 ttl=59 time=1.068 ms
64 bytes from fdb6:6e92:3cfb:203::d720: seq=1 ttl=59 time=0.648 ms
64 bytes from fdb6:6e92:3cfb:203::d720: seq=2 ttl=59 time=0.753 ms

--- fdb6:6e92:3cfb:203::d720 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.648/0.823/1.068 ms
```

**確認ポイント**:

- TTL が `59` (複数ホップ経由)
- 0% パケットロス
- 双方向での IPv6 通信が確立している
- IPv6 アドレスが Cluster1 の範囲 (`0200::/56`) に属している

#### 9.9 テスト Pod のクリーンアップ

**コマンド**:

```bash
kubectl --context kubernetes-admin@kubernetes delete pod test-pod --ignore-not-found
kubectl --context kubernetes-admin@kubernetes-2 delete pod test-pod --ignore-not-found
```

**期待される出力**:

```plaintext
pod "test-pod" deleted
pod "test-pod" deleted
```

## 補足

- **Pod/Service CIDR 変更時の運用**: クラスタの Pod/Service CIDR が変更された場合, `group_vars/k8s_worker/k8s_worker_frr.yml` の `clusters.<cluster_name>` セクションを更新し, 本ロールを再実行してください。FRR 設定ファイルが再生成され, `restart_frr` ハンドラにより FRR サービスが再起動されます。再実行前に, 既存の BGP セッションが一時的に切断されることに注意してください。
- **複数クラスタ運用時のクラスタ ID 管理**: 同一 DC 内に複数の K8s クラスタがある場合, 各クラスタで異なる `cluster_name` を使用し, `group_vars/k8s_worker/k8s_worker_frr.yml` の `clusters` 辞書に各クラスタの Pod/Service CIDR を定義してください。各ワーカーノードの `host_vars` で `k8s_worker_frr.cluster_name` を適切に設定し, 所属するクラスタを明示してください。
- **経路広告方法の選択**: `route_advertisement_method` 変数で経路広告方法を選択できます。`"static"` (デフォルト) は静的経路定義 + `redistribute static` で BGP に再配送し, カーネルに経路が存在しなくても広告できます。この方式は他ノードとの互換性が高く推奨されます。`"network"` は `network` コマンドで直接広告し, Cilium がカーネルに経路を作成することを前提とします。既存環境や他ノードとの互換性を考慮して選択してください。
- **カーネルルートフィルタの使用**: `kernel_route_filter` が未定義の場合, DC 代表 FRR から学習した全 BGP ルートがカーネルに反映されます。特定のルートのみをインポートしたい場合は, `host_vars` で `kernel_route_filter.ipv4` または `kernel_route_filter.ipv6` に prefix-list 名のリストを定義し, 対応する prefix-list を `frr.conf.j2` テンプレート外で定義してください (現在のテンプレートはカーネルインポート用 prefix-list の定義をサポートしていないため, 手動で追加する必要があります)。
- **FRR 設定の手動確認**: FRR 設定ファイルの内容を確認したい場合は, `vtysh -c "show running-config"` を実行してください。また, `vtysh` を対話モードで起動し, `show bgp summary`, `show ip bgp`, `show route-map` などのコマンドで BGP セッション状態やルート情報を確認できます。
- **vtysh アクセス許可**: `frr_vtysh_users` にユーザを追加すると, そのユーザは sudo なしで `vtysh` コマンドを実行できるようになります。これにより, FRR の設定確認や操作が容易になります。
- **FRR 構文検証の厳密性**: 本ロールは `vtysh --dry-run` (FRR 8.1+) または代替方法で FRR 設定の構文を検証し, エラーがあればタスクを即座に停止します。フォールバックや警告出力は行わないため, 設定ミスがあると再実行が必要になります。設定変更時は慎重に行ってください。
- **RFC 5549 と IPv4 トランスポート IPv6 NLRI の排他制御**: `rfc5549_enabled` (IPv6 トランスポートで IPv4 NLRI を運ぶ) と `ipv4_transport_ipv6_nlri_enabled` (IPv4 トランスポートで IPv6 NLRI を運ぶ) は排他的な設定です。本ロールは実行開始時にパラメータ検証タスク (`config-check-params.yml`) で両変数の値をチェックし, 両方とも `true` に設定されている場合はアサーションエラーでタスクを停止します。エラーメッセージには現在の設定値と選択可能な3つのオプション (RFC 5549 のみ有効, IPv4 トランスポート IPv6 NLRI のみ有効, 両方とも無効) が表示されます。これにより, 矛盾した設定による FRR の誤動作を防ぎます。
- **Cilium BGP Control Plane との切り替え**: Cilium BGP Control Plane から本ロールへ切り替える場合, または逆方向の切り替えを行う場合は, 以下の手順を推奨します:
  1. 現在の BGP セッションを確認し, ルート情報をバックアップします。
  2. `host_vars` で `k8s_bgp.enabled` と `k8s_worker_frr.enabled` を適切に変更します (排他的に `true` にする)。
  3. ワーカーノードで `k8s-worker` ロールを再実行します。
  4. BGP セッションと ルート広告が正しく動作していることを確認します。

## Multiprotocol BGP (IPv4トランスポートでIPv6のBGP広告も実施する設定) 利用時の検証方法

### Multiprotocol BGP 設定例

Multiprotocol BGP構成では, IPv4 BGPセッション1つでIPv4とIPv6の両方のルートを交換します。

#### Multiprotocol BGPでのワーカーノード設定 (host_vars/k8sworker0101.local)

```yaml
k8s_worker_frr:
  enabled: true
  local_asn: 65011
  rfc5549_enabled: false
  ipv4_transport_ipv6_nlri_enabled: true  # Multiprotocol BGP を有効化
  router_id: "192.168.30.42"
  cluster_name: "cluster1"

  # IPv4 BGP セッションのみ定義 ( IPv6経路もこのセッションで交換 )
  dc_frr_addresses:
    frr01.local: "192.168.40.49"

  # dc_frr_addresses_v6 は不要 ( IPv4トランスポートで運ぶため )

  # ホストルートは両方定義 ( IPv4セッションで両方広告 )
  advertise_host_route_ipv4: "192.168.40.42/32"
  advertise_host_route_ipv6: "fd69:6684:61a:2::42/128"
```

**標準デュアルスタックからの変更点**:

- `ipv4_transport_ipv6_nlri_enabled: true` に変更
- `dc_frr_addresses_v6` を削除 ( 不要 )
- `advertise_host_route_ipv6` は維持 ( IPv4セッションで広告 )

**利点**:

- BGPセッション数が削減 ( IPv4のみ )
- IPv4接続のみでIPv6ルーティングも実現
- Extended Nexthop Capabilityが自動有効化

#### Multiprotocol BGP設定でのDC代表FRR設定 (host_vars/frr01.local)

DC代表FRR側も同様にMultiprotocol BGP対応が必要です。frr-basicロールのテンプレートが対応している場合, 以下のように設定します。

```yaml
# K8sノードとの iBGP ピア ( IPv4セッションでIPv4とIPv6の両方を交換 )
frr_k8s_neighbors:
  - { addr: "192.168.40.41", asn: 65011, desc: "C1 control-plane" }
  - { addr: "192.168.40.42", asn: 65011, desc: "C1 worker-1" }
  - { addr: "192.168.40.43", asn: 65011, desc: "C1 worker-2" }

# frr_k8s_neighbors_v6 は空または未定義
frr_k8s_neighbors_v6: []

# 疑似外部ネットワーク側 eBGP ピア
frr_ebgp_neighbors:
  - { addr: "192.168.255.81", asn: 65100, desc: "External GW" }

frr_ebgp_neighbors_v6: []
```

**注意**: frr-basicロールがMultiprotocol BGPに対応しているかテンプレートを確認してください。対応していない場合は, IPv4ネイバーでIPv6 address-familyをactivateする設定を手動で追加する必要があります。

#### 設定時の注意事項

1. **排他的な設定**: `rfc5549_enabled` と `ipv4_transport_ipv6_nlri_enabled` は同時に `true` にしないでください。
2. **対向側の設定**: DC代表FRR側もMultiprotocol BGPに対応した設定が必要です。
3. **Extended Nexthop Capability**: テンプレートが自動で有効化しますが, 対向側 ( DC代表FRR ) も対応している必要があります。
4. **セッション数の確認**: `show bgp summary` でIPv4セッション1つのみが表示され, IPv6 Unicast Summaryでも同じIPv4アドレスのネイバーが表示されることを確認してください。

### Multiprotocol BGPでの前提条件

本例で使用する設定値:

- **検証対象ワーカーノード**: `k8sworker0101.local`
- **AS 番号 (iBGP)**: `65011`
- **ワーカーノード管理側 IPv4 アドレス**: `192.168.30.42`
- **ワーカーノード DC 接続側 IPv4 アドレス**: `192.168.40.42`
- **ワーカーノード DC 接続側 IPv6 アドレス**: `fd69:6684:61a:2::42`
- **BGP Router ID**: `192.168.30.42`
- **iBGP ピア (DC 代表 FRR)**:
  - `frr01.local`: `192.168.40.49` (AS 65011)
  - `frr02.local`: `192.168.40.50` (AS 65011)
- **クラスタ名**: `cluster1`
- **広告する経路**:
  - ホストルート IPv4: `192.168.40.42/32`
  - ホストルート IPv6: `fd69:6684:61a:2::42/128`
  - Pod CIDR IPv4: `10.244.0.0/16`
  - Pod CIDR IPv6: `fdb6:6e92:3cfb:0200::/56`
  - Service CIDR IPv4: `10.254.0.0/16`
  - Service CIDR IPv6: `fdb6:6e92:3cfb:feed::/112`

### 1. FRR サービス状態の確認 (Multiprotocol BGP)

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
systemctl status frr
```

**期待される出力**:

```plaintext
● frr.service - FRRouting
     Loaded: loaded (/lib/systemd/system/frr.service; enabled; preset: enabled)
     Active: active (running) since Sun 2026-01-26 12:57:34 JST; 37min ago
       Docs: https://frrouting.readthedocs.io/en/latest/setup.html
    Process: 1234 ExecStart=/usr/lib/frr/frrinit.sh start (code=exited, status=0/SUCCESS)
   Main PID: 1250 (watchfrr)
      Tasks: 8
     Memory: 45.2M
     CGroup: /system.slice/frr.service
             ├─1250 /usr/lib/frr/watchfrr -d -F traditional zebra bgpd staticd
             ├─1252 /usr/lib/frr/zebra -d -F traditional -A 127.0.0.1
             ├─1254 /usr/lib/frr/bgpd -d -F traditional -A 127.0.0.1
             └─1256 /usr/lib/frr/staticd -d -F traditional

Jan 26 12:57:35 k8sworker0101 watchfrr[1250]: [QDG3Y-BY5TN] zebra state -> up : connect succeeded
Jan 26 12:57:35 k8sworker0101 watchfrr[1250]: [QDG3Y-BY5TN] bgpd state -> up : connect succeeded
Jan 26 12:57:35 k8sworker0101 watchfrr[1250]: [QDG3Y-BY5TN] staticd state -> up : connect succeeded
Jan 26 12:57:35 k8sworker0101 watchfrr[1250]: [KWE5Q-QNGFC] all daemons up, doing startup-complete notify
Jan 26 12:57:35 k8sworker0101 systemd[1]:  * Started watchfrr
Jan 26 12:57:35 k8sworker0101 systemd[1]: Started frr.service - FRRouting.
Jan 26 13:20:12 k8sworker0101 bgpd[1254]: [W59KS-A3ZXZ] bgp_update_receive: rcvd End-of-RIB for IPv4 Unicast from 192.168.40.49 in vrf 0
Jan 26 13:20:15 k8sworker0101 bgpd[1254]: [W59KS-A3ZXZ] bgp_update_receive: rcvd End-of-RIB for IPv6 Unicast from 192.168.40.49 in vrf 0
```

**確認ポイント**:

- `Active: active (running)` が表示される
- zebra, bgpd, staticd のプロセスが起動している
- `all daemons up, doing startup-complete notify` メッセージが表示される
- BGP End-of-RIB (IPv4/IPv6) メッセージが表示される ( BGPセッション確立後 )
- インターフェース関連の警告 ( 例: `Cannot find IF <interface> in VRF` ) は一時的なもので, 通常は無視可能

### 2. FRR 設定の構文確認 (Multiprotocol BGP)

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
sudo vtysh -c "show running-config" | head -20
```

**期待される出力**:

```plaintext
Building configuration...

Current configuration:
!
frr version 8.4.4
frr defaults traditional
hostname k8sworker0101
log syslog informational
service integrated-vtysh-config
!
ip route 10.244.0.0/16 ens160
ip route 10.254.0.0/16 ens160
ip route 192.168.40.42/32 ens160
ipv6 route fdb6:6e92:3cfb:200::/56 ens160
ipv6 route fdb6:6e92:3cfb:feed::/112 ens160
ipv6 route fd69:6684:61a:2::42/128 ens160
!
router bgp 65011
 bgp router-id 192.168.30.42
 no bgp ebgp-requires-policy
```

**確認ポイント**:

- 構文エラーが表示されない
- FRR バージョンが表示される (例: 8.4.4)
- 静的ルート定義が存在する (Pod CIDR, Service CIDR, ホストルート - IPv4/IPv6)
- インターフェース名 (`ens160`) は環境により異なる (例: `enX0`, `eth0` など)
- AS 番号 (`65011`) と Router ID (`192.168.30.42`) が正しい
- `no bgp ebgp-requires-policy` が設定されている

### 3. iBGP セッション状態の確認 (Multiprotocol BGP)

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
sudo vtysh -c "show bgp summary"
```

**期待される出力**:

```plaintext
IPv4 Unicast Summary (VRF default):
BGP router identifier 192.168.30.42, local AS number 65011 vrf-id 0
BGP table version 9
RIB entries 16, using 3072 bytes of memory
Peers 1, using 724 KiB of memory

Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
192.168.40.49   4      65011        51        47        0    0    0 00:41:54            6        3 DC-FRR frr01.local

Total number of neighbors 1

IPv6 Unicast Summary (VRF default):
BGP router identifier 192.168.30.42, local AS number 65011 vrf-id 0
BGP table version 11
RIB entries 19, using 3648 bytes of memory
Peers 1, using 724 KiB of memory

Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
192.168.40.49   4      65011        51        47        0    0    0 00:41:54            8        3 DC-FRR frr01.local

Total number of neighbors 1
```

**確認ポイント**:

- `show bgp summary` コマンド1回でIPv4とIPv6両方のBGPサマリーが表示される
- `State/PfxRcd` が数値 (IPv4: `6`, IPv6: `8`) であり, `Active`, `Connect`, `Idle`, `NoNeg` などのエラー状態でない
- `PfxSnt` が `3` である (Pod CIDR, Service CIDR, ホストルートの 3 つを送信)
- `Up/Down` に稼働時間が表示されている
- IPv4/IPv6 両方で同じネイバー ( 192.168.40.49 ) とのBGPセッションが確立している
- IPv4トランスポートでIPv6 NLRIも交換されている (`ipv4_transport_ipv6_nlri_enabled: true` の場合, IPv6のネイバーもIPv4アドレスで表示される)

**IPv6のみの詳細確認**:

```bash
sudo vtysh -c "show bgp ipv6 unicast summary"
```

**期待される出力**:

```plaintext
BGP router identifier 192.168.30.42, local AS number 65011 vrf-id 0
BGP table version 11
RIB entries 19, using 3648 bytes of memory
Peers 1, using 724 KiB of memory

Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
192.168.40.49   4      65011        52        48        0    0    0 00:42:51            8        3 DC-FRR frr01.local

Total number of neighbors 1
```

**複数の DC 代表 FRR と接続している場合の出力例**:

```plaintext
BGP router identifier 192.168.30.42, local AS number 65011 vrf-id 0
BGP table version 9
RIB entries 23, using 4416 bytes of memory
Peers 2, using 1447 KiB of memory

Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
192.168.40.49   4      65011       150       145        0    0    0 01:30:00            6        3 DC-FRR frr01.local
192.168.40.50   4      65011       148       143        0    0    0 01:29:55            6        3 DC-FRR frr02.local

Total number of neighbors 2
```

**確認ポイント**:

- `State/PfxRcd` 列に数値が表示されている (接続成功)
- `State/PfxRcd` 列が `Idle`, `Connect`, `Active` などの場合は接続失敗
- `Up/Down` 列にアップタイムが表示されている
- 両方の DC 代表 FRR (`192.168.40.49`, `192.168.40.50`) とのセッションが確立している

### 4. Multiprotocol BGP設定での広告経路の確認 (IPv4)

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
sudo vtysh -c "show ip bgp"
```

**期待される出力**:

```plaintext
BGP table version is 9, local router ID is 192.168.30.42, vrf id 0
Default local pref 100, local AS 65011
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

   Network          Next Hop            Metric LocPrf Weight Path
*>i10.243.0.0/16    192.168.255.48                100      0 65100 65012 ?
*> 10.244.0.0/16    0.0.0.0                  0         32768 ?
*>i10.253.0.0/16    192.168.255.48                100      0 65100 65012 ?
*> 10.254.0.0/16    0.0.0.0                  0         32768 ?
*>i192.168.30.0/24  192.168.40.49            0    100      0 i
*>i192.168.40.0/24  192.168.40.49            0    100      0 i
*> 192.168.40.42/32 0.0.0.0                  0         32768 ?
*>i192.168.50.0/24  192.168.255.48                100      0 65100 65012 i
*>i192.168.255.0/24 192.168.40.49            0    100      0 i

Displayed  9 routes and 9 total paths
```

**確認ポイント**:

- ホストルート `192.168.40.42/32` が広告されている (`Next Hop` が `0.0.0.0`, `Weight` が `32768`)
- Pod CIDR `10.244.0.0/16` が広告されている
- Service CIDR `10.254.0.0/16` が広告されている
- 対向クラスター (Cluster2) の経路 (`10.243.0.0/16`, `10.253.0.0/16`) がiBGP/eBGP経由で受信されている
- 自身の広告ルートの `Origin codes` が `?` (incomplete, `redistribute static` で再配送された経路) である

### 5. Multiprotocol BGP設定での広告経路の確認 (IPv6)

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
sudo vtysh -c "show bgp ipv6"
```

**期待される出力**:

```plaintext
BGP table version is 11, local router ID is 192.168.30.42, vrf id 0
Default local pref 100, local AS 65011
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

   Network          Next Hop            Metric LocPrf Weight Path
*>ifd69:6684:61a:2::/64
                    fe80::250:56ff:fe00:4a1c
                                             0    100      0 i
*> fd69:6684:61a:2::42/128
                    ::                       0         32768 ?
*>ifd69:6684:61a:3::/64
                    fd69:6684:61a:90::81
                                                  100      0 65100 65012 i
*>ifd69:6684:61a:3::52/128
                    fd69:6684:61a:90::81
                                                  100      0 65100 65012 ?
*>ifd69:6684:61a:3::53/128
                    fd69:6684:61a:90::81
                                                  100      0 65100 65012 ?
*>ifd69:6684:61a:90::/64
                    fe80::250:56ff:fe00:4a1c
                                             0    100      0 i
*>ifdad:ba50:248b:1::/64
                    fe80::250:56ff:fe00:4a1c
                                             0    100      0 i
*>ifdb6:6e92:3cfb:100::/56
                    fd69:6684:61a:90::81
                                                  100      0 65100 65012 ?
*> fdb6:6e92:3cfb:200::/56
                    ::                       0         32768 ?
*>ifdb6:6e92:3cfb:feec::/112
                    fd69:6684:61a:90::81
                                                  100      0 65100 65012 ?
*> fdb6:6e92:3cfb:feed::/112
                    ::                       0         32768 ?

Displayed  11 routes and 11 total paths
```

**確認ポイント**:

- ホストルート `fd69:6684:61a:2::42/128` が広告されている (`Next Hop` が `::`, `Weight` が `32768`)
- Pod CIDR `fdb6:6e92:3cfb:200::/56` (Cluster1専用範囲) が広告されている
- Service CIDR `fdb6:6e92:3cfb:feed::/112` が広告されている
- 対向クラスター (Cluster2) の Pod/Service CIDR (`fdb6:6e92:3cfb:100::/56`, `fdb6:6e92:3cfb:feec::/112`) がiBGP/eBGP経由で受信されている
- `Next Hop` にlink-local (`fe80::...`) またはglobal IPv6アドレス, ローカル生成経路では `::` が使用されている
- 自身の広告ルートの `Origin codes` が `?` (incomplete) である

**注**: `show bgp ipv6 unicast` コマンドも同じ結果を表示します。

**コマンド**:

```bash
sudo vtysh -c "show bgp ipv6 unicast"
```

**期待される出力**:

```plaintext
BGP table version is 11, local router ID is 192.168.30.42, vrf id 0
Default local pref 100, local AS 65011
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

   Network          Next Hop            Metric LocPrf Weight Path
*>ifd69:6684:61a:2::/64
                    fe80::250:56ff:fe00:4a1c
                                             0    100      0 i
*> fd69:6684:61a:2::42/128
                    ::                       0         32768 ?
*>ifd69:6684:61a:3::/64
                    fd69:6684:61a:90::81
                                                  100      0 65100 65012 i
*>ifd69:6684:61a:3::52/128
                    fd69:6684:61a:90::81
                                                  100      0 65100 65012 ?
*>ifd69:6684:61a:3::53/128
                    fd69:6684:61a:90::81
                                                  100      0 65100 65012 ?
*>ifd69:6684:61a:90::/64
                    fe80::250:56ff:fe00:4a1c
                                             0    100      0 i
*>ifdad:ba50:248b:1::/64
                    fe80::250:56ff:fe00:4a1c
                                             0    100      0 i
*>ifdb6:6e92:3cfb:100::/56
                    fd69:6684:61a:90::81
                                                  100      0 65100 65012 ?
*> fdb6:6e92:3cfb:200::/56
                    ::                       0         32768 ?
*>ifdb6:6e92:3cfb:feec::/112
                    fd69:6684:61a:90::81
                                                  100      0 65100 65012 ?
*> fdb6:6e92:3cfb:feed::/112
                    ::                       0         32768 ?

Displayed  11 routes and 11 total paths
```

### 6. prefix-list の確認

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
sudo vtysh -c "show ip prefix-list"
```

**期待される出力**:

```plaintext
ZEBRA: ip prefix-list PL-V4-HOST-OUT: 1 entries
   seq 5 permit 0.0.0.0/0 ge 32 le 32
ZEBRA: ip prefix-list PL-V4-POD-OUT: 1 entries
   seq 5 permit 0.0.0.0/0 ge 24 le 28
ZEBRA: ip prefix-list PL-V4-SVC-OUT: 1 entries
   seq 5 permit 0.0.0.0/0 ge 16 le 24
BGP: ip prefix-list PL-V4-HOST-OUT: 1 entries
   seq 5 permit 0.0.0.0/0 ge 32 le 32
BGP: ip prefix-list PL-V4-POD-OUT: 1 entries
   seq 5 permit 0.0.0.0/0 ge 24 le 28
BGP: ip prefix-list PL-V4-SVC-OUT: 1 entries
   seq 5 permit 0.0.0.0/0 ge 16 le 24
```

**コマンド**:

```bash
sudo vtysh -c "show ipv6 prefix-list"
```

**期待される出力**:

```plaintext
ZEBRA: ipv6 prefix-list PL-V6-HOST-OUT: 1 entries
   seq 5 permit ::/0 ge 128 le 128
ZEBRA: ipv6 prefix-list PL-V6-POD-OUT: 1 entries
   seq 5 permit ::/0 ge 56 le 64
ZEBRA: ipv6 prefix-list PL-V6-SVC-OUT: 1 entries
   seq 5 permit ::/0 ge 112 le 120
BGP: ipv6 prefix-list PL-V6-HOST-OUT: 1 entries
   seq 5 permit ::/0 ge 128 le 128
BGP: ipv6 prefix-list PL-V6-POD-OUT: 1 entries
   seq 5 permit ::/0 ge 56 le 64
BGP: ipv6 prefix-list PL-V6-SVC-OUT: 1 entries
   seq 5 permit ::/0 ge 112 le 120
```

**確認ポイント**:

- IPv4 Pod 用フィルタ (`PL-V4-POD-OUT`) が `/24` ～ `/28` の範囲を許可
- IPv4 Service 用フィルタ (`PL-V4-SVC-OUT`) が `/16` ～ `/24` の範囲を許可
- IPv4 Host 用フィルタ (`PL-V4-HOST-OUT`) が `/32` のみを許可
- IPv6 Pod 用フィルタ (`PL-V6-POD-OUT`) が `/56` ～ `/64` の範囲を許可
- IPv6 Service 用フィルタ (`PL-V6-SVC-OUT`) が `/112` ～ `/120` の範囲を許可
- IPv6 Host 用フィルタ (`PL-V6-HOST-OUT`) が `/128` のみを許可

### 7. route-map の確認

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
sudo vtysh -c "show route-map"
```

**期待される出力**:

```plaintext
ZEBRA:
route-map: RM-KERNEL-IMPORT Invoked: 13 Optimization: enabled Processed Change: false
 permit, sequence 10 Invoked 13
  Match clauses:
  Set clauses:
  Call clause:
  Action:
    Exit routemap
route-map: RM-V4-OUT Invoked: 0 Optimization: enabled Processed Change: false
 permit, sequence 10 Invoked 0
  Match clauses:
    ip address prefix-list PL-V4-POD-OUT
  Set clauses:
  Call clause:
  Action:
    Exit routemap
 permit, sequence 20 Invoked 0
  Match clauses:
    ip address prefix-list PL-V4-SVC-OUT
  Set clauses:
  Call clause:
  Action:
    Exit routemap
 permit, sequence 30 Invoked 0
  Match clauses:
    ip address prefix-list PL-V4-HOST-OUT
  Set clauses:
  Call clause:
  Action:
    Exit routemap
 deny, sequence 100 Invoked 0
  Match clauses:
  Set clauses:
  Call clause:
  Action:
    Exit routemap
route-map: RM-V6-OUT Invoked: 0 Optimization: enabled Processed Change: false
 permit, sequence 10 Invoked 0
  Match clauses:
    ipv6 address prefix-list PL-V6-POD-OUT
  Set clauses:
  Call clause:
  Action:
    Exit routemap
 permit, sequence 20 Invoked 0
  Match clauses:
    ipv6 address prefix-list PL-V6-SVC-OUT
  Set clauses:
  Call clause:
  Action:
    Exit routemap
 permit, sequence 30 Invoked 0
  Match clauses:
    ipv6 address prefix-list PL-V6-HOST-OUT
  Set clauses:
  Call clause:
  Action:
    Exit routemap
 deny, sequence 100 Invoked 0
  Match clauses:
  Set clauses:
  Call clause:
  Action:
    Exit routemap
BGP:
route-map: RM-KERNEL-IMPORT Invoked: 0 Optimization: enabled Processed Change: false
 permit, sequence 10 Invoked 0
  Match clauses:
  Set clauses:
  Call clause:
  Action:
    Exit routemap
route-map: RM-V4-OUT Invoked: 6 Optimization: enabled Processed Change: false
 permit, sequence 10 Invoked 0
  Match clauses:
    ip address prefix-list PL-V4-POD-OUT
  Set clauses:
  Call clause:
  Action:
    Exit routemap
 permit, sequence 20 Invoked 4
  Match clauses:
    ip address prefix-list PL-V4-SVC-OUT
  Set clauses:
  Call clause:
  Action:
    Exit routemap
 permit, sequence 30 Invoked 2
  Match clauses:
    ip address prefix-list PL-V4-HOST-OUT
  Set clauses:
  Call clause:
  Action:
    Exit routemap
 deny, sequence 100 Invoked 0
  Match clauses:
  Set clauses:
  Call clause:
  Action:
    Exit routemap
route-map: RM-V6-OUT Invoked: 6 Optimization: enabled Processed Change: false
 permit, sequence 10 Invoked 2
  Match clauses:
    ipv6 address prefix-list PL-V6-POD-OUT
  Set clauses:
  Call clause:
  Action:
    Exit routemap
 permit, sequence 20 Invoked 2
  Match clauses:
    ipv6 address prefix-list PL-V6-SVC-OUT
  Set clauses:
  Call clause:
  Action:
    Exit routemap
 permit, sequence 30 Invoked 2
  Match clauses:
    ipv6 address prefix-list PL-V6-HOST-OUT
  Set clauses:
  Call clause:
  Action:
    Exit routemap
 deny, sequence 100 Invoked 0
  Match clauses:
  Set clauses:
  Call clause:
  Action:
    Exit routemap
```

**確認ポイント**:

- `RM-V4-OUT` が Pod/Service/Host 用の prefix-list をマッチさせている
- `RM-V4-OUT` の最後に `deny, sequence 100` があり, デフォルト拒否が設定されている
- `RM-V6-OUT` も同様の構造である
- `RM-KERNEL-IMPORT` が定義されている (カーネルへのルートインポート用)

### 8. カーネルルーティングテーブルの確認 (IPv4)

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
ip route show proto bgp
```

**期待される出力**:

```plaintext
10.243.0.0/16 nhid 62 via 192.168.40.49 dev ens192 metric 20
10.253.0.0/16 nhid 62 via 192.168.40.49 dev ens192 metric 20
192.168.50.0/24 nhid 62 via 192.168.40.49 dev ens192 metric 20
192.168.255.0/24 nhid 57 via 192.168.40.49 dev ens192 metric 20
```

**確認ポイント**:

- `proto bgp` は `ip route show proto bgp` コマンドの出力には表示されるが, 各経路行には表示されない
- 他クラスタの Pod CIDR (`10.243.0.0/16`) やService CIDR (`10.253.0.0/16`) が表示される
- ネクストホップが DC 代表 FRR (`192.168.40.49`) である
- インターフェース名 (`ens192`) は環境により異なる (例: `enX1`, `eth1` など)
- `nhid` (nexthop ID) が表示される

### 9. カーネルルーティングテーブルの確認 (IPv6)

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
ip -6 route show proto bgp
```

**期待される出力**:

```plaintext
fd69:6684:61a:3::52 nhid 56 via fe80::250:56ff:fe00:4a1c dev ens192 metric 20 pref medium
fd69:6684:61a:3::53 nhid 56 via fe80::250:56ff:fe00:4a1c dev ens192 metric 20 pref medium
fd69:6684:61a:3::/64 nhid 56 via fe80::250:56ff:fe00:4a1c dev ens192 metric 20 pref medium
fd69:6684:61a:90::/64 nhid 56 via fe80::250:56ff:fe00:4a1c dev ens192 metric 20 pref medium
fdb6:6e92:3cfb:100::/56 nhid 56 via fe80::250:56ff:fe00:4a1c dev ens192 metric 20 pref medium
fdb6:6e92:3cfb:feec::/112 nhid 56 via fe80::250:56ff:fe00:4a1c dev ens192 metric 20 pref medium
```

**確認ポイント**:

- `proto bgp` は `ip -6 route show proto bgp` コマンドの出力には表示されるが, 各経路行には表示されない
- 他クラスタの Pod CIDR (`fdb6:6e92:3cfb:100::/56`) や Service CIDR (`fdb6:6e92:3cfb:feec::/112`) が表示される
- ネクストホップが link-local アドレス (`fe80::...`) である (IPv6 BGP の一般的な動作)
- インターフェース名 (`ens192`) は環境により異なる
- `nhid` (nexthop ID) が表示される

### 10. IP フォワーディング設定の確認

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
sysctl net.ipv4.ip_forward
sysctl net.ipv6.conf.all.forwarding
```

**期待される出力**:

```plaintext
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
```

**確認ポイント**:

- 両方の値が `1` である (フォワーディング有効)

### 11. DC 代表 FRR での受信経路確認

**実施ノード**: `frr01.local` または `frr02.local`

#### 11.1 IPv4 経路の確認

**コマンド** (frr01.local で実行):

```bash
sudo vtysh -c "show ip bgp neighbors 192.168.40.42 routes"
```

**期待される出力**:

```plaintext
BGP table version is 318, local router ID is 192.168.40.49, vrf id 0
Default local pref 100, local AS 65011
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

   Network          Next Hop            Metric LocPrf Weight Path
*>i10.244.0.0/16    192.168.40.42            0    100      0 ?
*>i10.254.0.0/16    192.168.40.42            0    100      0 ?
  i192.168.40.42/32 192.168.40.42            0    100      0 ?

Displayed  3 routes and 13 total paths
```

**確認ポイント**:

- ワーカーノード (`192.168.40.42`) から広告された 3 つの経路 (Pod CIDR, Service CIDR, ホストルート) が表示される
- `Origin codes` が `?` (incomplete, `redistribute static` で広告された経路) である
- `LocPrf` が `100` (iBGP デフォルト Local Preference) である
- ホストルート (`192.168.40.42/32`) に `*>` が付いていない場合, 他のパスがベストパスとして選択されている可能性がある ( 複数のワーカーノードから同じホストルートが広告されている場合など )
- "Displayed 3 routes and 13 total paths" は, 3つの異なるネットワークプレフィクスに対して合計13のBGPパスが存在することを示す ( 複数のiBGPピアから同じ経路を受信している場合 )

#### 11.2 IPv6 経路の確認

**コマンド** (frr01.local で実行):

```bash
sudo vtysh -c "show bgp ipv6 unicast neighbors 192.168.40.42 routes"
```

**期待される出力**:

```plaintext
BGP table version is 284, local router ID is 192.168.40.49, vrf id 0
Default local pref 100, local AS 65011
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

   Network          Next Hop            Metric LocPrf Weight Path
*>ifd69:6684:61a:2::42/128
                    fe80::250:56ff:fe00:7b26
                                             0    100      0 ?
*>ifdb6:6e92:3cfb:200::/56
                    fe80::250:56ff:fe00:7b26
                                             0    100      0 ?
*>ifdb6:6e92:3cfb:feed::/112
                    fe80::250:56ff:fe00:7b26
                                             0    100      0 ?

Displayed  3 routes and 15 total paths
```

**確認ポイント**:

- ワーカーノードから広告された 3 つの IPv6 経路 (ホストルート, Pod CIDR, Service CIDR) が表示される
- `Next Hop` が link-local アドレス (`fe80::...`) である (IPv6 BGP の一般的な動作)
- `Origin codes` が `?` (incomplete) である
- IPv4 トランスポート上で IPv6 NLRI が交換されている (`ipv4_transport_ipv6_nlri_enabled: true` の効果)
- "Displayed 3 routes and 15 total paths" は, 3つの異なるネットワークプレフィクスに対して合計15のBGPパスが存在することを示す ( 複数のiBGPピアから同じ経路を受信している場合 )

#### 11.3 External Gateway (extgw) での経路確認

**実施ノード**: `extgw.local`

**コマンド**:

```bash
sudo vtysh -c "show ip bgp"
```

**期待される出力**:

```plaintext
BGP table version is 293, local router ID is 192.168.255.81, vrf id 0
Default local pref 100, local AS 65100
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

    Network          Next Hop            Metric LocPrf Weight Path
 *> 10.243.0.0/16    192.168.255.48                         0 65012 ?
 *> 10.244.0.0/16    192.168.255.49                         0 65011 ?
 *> 10.253.0.0/16    192.168.255.48                         0 65012 ?
 *> 10.254.0.0/16    192.168.255.49                         0 65011 ?
 *> 192.168.30.0/24  192.168.255.49           0             0 65011 i
 *                   192.168.255.48           0             0 65012 i
 *> 192.168.40.0/24  192.168.255.49           0             0 65011 i
 *> 192.168.50.0/24  192.168.255.48           0             0 65012 i
 *  192.168.255.0/24 192.168.255.49           0             0 65011 i
 *                   192.168.255.48           0             0 65012 i
 *>                  0.0.0.0                  0         32768 i

Displayed  8 routes and 11 total paths
```

**コマンド** (IPv6):

```bash
sudo vtysh -c "show bgp ipv6"
```

**期待される出力 (抜粋)**:

```plaintext
   Network          Next Hop            Metric LocPrf Weight Path
*> fdb6:6e92:3cfb:100::/56
                    fd69:6684:61a:90::81
                                                            0 65012 ?
*> fdb6:6e92:3cfb:200::/56
                    fd69:6684:61a:90::80
                                                            0 65011 ?
*> fdb6:6e92:3cfb:feec::/112
                    fd69:6684:61a:90::81
                                                            0 65012 ?
*> fdb6:6e92:3cfb:feed::/112
                    fd69:6684:61a:90::80
                                                            0 65011 ?
```

**確認ポイント**:

- 両クラスタ (AS 65011, AS 65012) の Pod/Service CIDR が表示される
- `Path` に AS 番号が表示される (eBGP 経由)
- External Gateway が両クラスタへの経路を学習している

### 12. DC 間 Pod 疎通テスト (IPv4/IPv6 デュアルスタック)

**前提**:

- Cluster1 (context: `kubernetes-admin@kubernetes`, Pod CIDR `10.244.0.0/16`, IPv6 Pod CIDR `fdb6:6e92:3cfb:0200::/56`)
- Cluster2 (context: `kubernetes-admin@kubernetes-2`, Pod CIDR `10.243.0.0/16`, IPv6 Pod CIDR `fdb6:6e92:3cfb:0100::/56`)
- テスト用 Pod として busybox イメージを使用

#### 12.1 既存テスト Pod の削除 ( 存在する場合 )

**コマンド**:

```bash
kubectl --context kubernetes-admin@kubernetes delete pod test-pod --ignore-not-found
kubectl --context kubernetes-admin@kubernetes-2 delete pod test-pod --ignore-not-found
```

**期待される出力**:

```plaintext
kubectl --context kubernetes-admin@kubernetes delete pod test-pod --ignore-not-found
kubectl --context kubernetes-admin@kubernetes-2 delete pod test-pod --ignore-not-found
```

#### 12.2 テスト Pod のデプロイ

**コマンド**:

```bash
# Cluster1にデプロイ
kubectl --context kubernetes-admin@kubernetes run test-pod --image=busybox --command -- sleep 3600

# Cluster2にデプロイ
kubectl --context kubernetes-admin@kubernetes-2 run test-pod --image=busybox --command -- sleep 3600

# Pod起動完了を待つ
kubectl --context kubernetes-admin@kubernetes wait --for=condition=Ready pod/test-pod --timeout=60s
kubectl --context kubernetes-admin@kubernetes-2 wait --for=condition=Ready pod/test-pod --timeout=60s
```

**期待される出力**:

```plaintext
$ kubectl --context kubernetes-admin@kubernetes run test-pod --image=busybox --command -- sleep 3600
pod/test-pod created
$ kubectl --context kubernetes-admin@kubernetes-2 run test-pod --image=busybox --command -- sleep 3600
pod/test-pod created
$ kubectl --context kubernetes-admin@kubernetes wait --for=condition=Ready pod/test-pod --timeout=60s
pod/test-pod condition met
$ kubectl --context kubernetes-admin@kubernetes-2 wait --for=condition=Ready pod/test-pod --timeout=60s
pod/test-pod condition met
```

#### 12.3 Pod IP アドレスの確認

**コマンド**:

```bash
# 両クラスターのPod IPアドレスを確認
kubectl --context kubernetes-admin@kubernetes get pod test-pod -o wide
kubectl --context kubernetes-admin@kubernetes-2 get pod test-pod -o wide

# Pod内のIPアドレス詳細確認
kubectl --context kubernetes-admin@kubernetes exec test-pod -- ip addr
kubectl --context kubernetes-admin@kubernetes-2 exec test-pod -- ip addr
```

**期待される出力**:

```plaintext
$ kubectl --context kubernetes-admin@kubernetes get pod test-pod -o wide
NAME       READY   STATUS    RESTARTS   AGE     IP                         NODE            NOMINATED NODE   READINESS GATES
test-pod   1/1     Running   0          2m49s   fdb6:6e92:3cfb:203::806e   k8sworker0101   <none>           <none>
$ kubectl --context kubernetes-admin@kubernetes-2 get pod test-pod -o wide
NAME       READY   STATUS    RESTARTS   AGE     IP                         NODE            NOMINATED NODE   READINESS GATES
test-pod   1/1     Running   0          2m49s   fdb6:6e92:3cfb:105::3566   k8sworker0201   <none>           <none>
$ kubectl --context kubernetes-admin@kubernetes exec test-pod -- ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
8: eth0@if9: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue qlen 1000
    link/ether 9a:b9:1f:b2:c0:a8 brd ff:ff:ff:ff:ff:ff
    inet 10.244.3.226/32 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 fdb6:6e92:3cfb:203::806e/128 scope global flags 02
       valid_lft forever preferred_lft forever
    inet6 fe80::98b9:1fff:feb2:c0a8/64 scope link
       valid_lft forever preferred_lft forever
$ kubectl --context kubernetes-admin@kubernetes-2 exec test-pod -- ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
8: eth0@if9: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue qlen 1000
    link/ether ae:9a:91:9e:c5:84 brd ff:ff:ff:ff:ff:ff
    inet 10.243.5.191/32 scope global eth0
       valid_lft forever preferred_lft forever
    inet6 fdb6:6e92:3cfb:105::3566/128 scope global flags 02
       valid_lft forever preferred_lft forever
    inet6 fe80::ac9a:91ff:fe9e:c584/64 scope link
       valid_lft forever preferred_lft forever
```

**確認ポイント**:

- Cluster1 Pod: IPv4 `10.244.3.226/32`, IPv6 `fdb6:6e92:3cfb:203::806e/128`
- Cluster2 Pod: IPv4 `10.243.5.191/32`, IPv6 `fdb6:6e92:3cfb:105::3566/128`
- IPv6 アドレスがクラスタ固有の `/56` 範囲に属している (`0200::/56` vs `0100::/56`)

#### 12.4 Cilium 設定の確認 ( オプション )

**コマンド**:

```bash
kubectl --context kubernetes-admin@kubernetes get cm -n kube-system cilium-config -o yaml | grep ipv6-native-routing-cidr
kubectl --context kubernetes-admin@kubernetes-2 get cm -n kube-system cilium-config -o yaml | grep ipv6-native-routing-cidr
```

**期待される出力**:

```plaintext
$ kubectl --context kubernetes-admin@kubernetes get cm -n kube-system cilium-config -o yaml | grep ipv6-native-routing-cidr
  ipv6-native-routing-cidr: fdb6:6e92:3cfb:0200::/56
$ kubectl --context kubernetes-admin@kubernetes-2 get cm -n kube-system cilium-config -o yaml | grep ipv6-native-routing-cidr
  ipv6-native-routing-cidr: fdb6:6e92:3cfb:0100::/56
```

**確認ポイント**:

- 各クラスタで異なる `/56` 範囲が設定されている
- FRR が広告している Pod CIDR と一致している

#### 12.5 Cluster1  =>  Cluster2 疎通テスト (IPv4)

**コマンド**:

```bash
kubectl --context kubernetes-admin@kubernetes exec test-pod -- ping -c 3 10.243.5.191
```

**期待される出力**:

```plaintext
$ kubectl --context kubernetes-admin@kubernetes exec test-pod -- ping -c 3 10.243.5.191
PING 10.243.5.191 (10.243.5.191): 56 data bytes
64 bytes from 10.243.5.191: seq=0 ttl=60 time=1.162 ms
64 bytes from 10.243.5.191: seq=1 ttl=60 time=0.521 ms
64 bytes from 10.243.5.191: seq=2 ttl=60 time=0.531 ms

--- 10.243.5.191 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.521/0.738/1.162 ms
```

**確認ポイント**:

- TTL が `60` (複数ホップ経由)
- 0% パケットロス
- RTT が 0.5-1.2ms 程度 (LAN 環境)
- busybox の ping 出力形式 ( `seq=0` 形式 )

#### 12.6 Cluster2  =>  Cluster1 疎通テスト (IPv4)

**コマンド**:

```bash
kubectl --context kubernetes-admin@kubernetes-2 exec test-pod -- ping -c 3 10.244.3.226
```

**期待される出力**:

```plaintext
$ kubectl --context kubernetes-admin@kubernetes-2 exec test-pod -- ping -c 3 10.244.3.226
PING 10.244.3.226 (10.244.3.226): 56 data bytes
64 bytes from 10.244.3.226: seq=0 ttl=60 time=0.882 ms
64 bytes from 10.244.3.226: seq=1 ttl=60 time=0.443 ms
64 bytes from 10.244.3.226: seq=2 ttl=60 time=0.468 ms

--- 10.244.3.226 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.443/0.597/0.882 ms
```

**確認ポイント**:

- TTL が `60` (複数ホップ経由)
- 0% パケットロス
- 双方向での IPv4 通信が確立している

#### 12.7 Cluster1  =>  Cluster2 疎通テスト (IPv6)

**コマンド**:

```bash
kubectl --context kubernetes-admin@kubernetes exec test-pod -- ping -c 3 fdb6:6e92:3cfb:105::3566
```

**期待される出力**:

```plaintext
$ kubectl --context kubernetes-admin@kubernetes exec test-pod -- ping -c 3 fdb6:6e92:3cfb:105::3566
PING fdb6:6e92:3cfb:105::3566 (fdb6:6e92:3cfb:105::3566): 56 data bytes
64 bytes from fdb6:6e92:3cfb:105::3566: seq=0 ttl=59 time=1.795 ms
64 bytes from fdb6:6e92:3cfb:105::3566: seq=1 ttl=59 time=0.708 ms
64 bytes from fdb6:6e92:3cfb:105::3566: seq=2 ttl=59 time=0.655 ms

--- fdb6:6e92:3cfb:105::3566 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.655/1.052/1.795 ms
```

**確認ポイント**:

- TTL が `59` (複数ホップ経由, IPv6 は IPv4 より 1 少ない)
- 0% パケットロス
- RTT が 0.6-1.8ms 程度
- IPv6 アドレスが Cluster2 の範囲 (`0100::/56`) に属している

#### 12.8 Cluster2  =>  Cluster1 疎通テスト (IPv6)

**コマンド**:

```bash
kubectl --context kubernetes-admin@kubernetes-2 exec test-pod -- ping -c 3 fdb6:6e92:3cfb:203::806e
```

**期待される出力**:

```plaintext
$ kubectl --context kubernetes-admin@kubernetes-2 exec test-pod -- ping -c 3 fdb6:6e92:3cfb:203::806e
PING fdb6:6e92:3cfb:203::806e (fdb6:6e92:3cfb:203::806e): 56 data bytes
64 bytes from fdb6:6e92:3cfb:203::806e: seq=0 ttl=59 time=1.834 ms
64 bytes from fdb6:6e92:3cfb:203::806e: seq=1 ttl=59 time=0.887 ms
64 bytes from fdb6:6e92:3cfb:203::806e: seq=2 ttl=59 time=0.785 ms

--- fdb6:6e92:3cfb:203::806e ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.785/1.168/1.834 ms
```

**確認ポイント**:

- TTL が `59` (複数ホップ経由)
- 0% パケットロス
- 双方向での IPv6 通信が確立している
- IPv6 アドレスが Cluster1 の範囲 (`0200::/56`) に属している

#### 12.9 テスト完了後のクリーンアップ

**コマンド**:

```bash
kubectl --context kubernetes-admin@kubernetes delete pod test-pod
kubectl --context kubernetes-admin@kubernetes-2 delete pod test-pod
```

## RFC 5549 (IPv6 トランスポート) 利用時の検証方法

RFC 5549 を有効化した場合 (`rfc5549_enabled: true`), BGP セッションは IPv6 トランスポートで確立され, IPv4 および IPv6 の両方の NLRI が Extended Nexthop Capability を使用して運ばれます。この設定では, IPv4 ルートのネクストホップとして IPv6 アドレス (link-local または global) が使用されるため, 検証時の出力が通常の IPv4 トランスポートとは異なります。

以下は RFC 5549 を有効化した環境での具体的な検証手順です。

### RFC 5549 (IPv6 トランスポート) 利用時の前提条件

本例で使用する設定値:

- **検証対象ワーカーノード**: `k8sworker0101.local`
- **RFC 5549**: 有効 (`rfc5549_enabled: true`)
- **AS 番号 (iBGP)**: `65011`
- **BGP Router ID**: `192.168.30.42` (IPv4 形式)
- **iBGP ピア (DC 代表 FRR)**: `frr01.local`: IPv6 アドレス `fd69:6684:61a:2::49` (AS 65011)
- **クラスタ名**: `cluster1`
- **広告する経路**:
  - ホストルート IPv4: `192.168.40.42/32`
  - ホストルート IPv6: `fd69:6684:61a:2::42/128`
  - Pod CIDR IPv4: `10.244.0.0/16`
  - Service CIDR IPv4: `10.254.0.0/16`
  - Pod CIDR IPv6: `fdb6:6e92:3cfb:200::/56`
  - Service CIDR IPv6: `fdb6:6e92:3cfb:feed::/112`

### RFC 5549 環境での host_vars 設定例

RFC 5549 を使用する場合, すべての BGP ネイバーアドレスを IPv6 で指定します。以下に各ノードタイプの設定例を示します。

#### ワーカーノードの設定例 (host_vars/k8sworker0101.local)

```yaml
---
# K8s Worker FRR 設定 (RFC 5549 有効)
k8s_worker_frr:
  enabled: true
  rfc5549_enabled: true  # IPv6 トランスポートで IPv4/IPv6 NLRI を運ぶ
  local_asn: 65011
  router_id: "192.168.30.42"  # IPv4 形式の Router ID
  cluster_name: "cluster1"

  # DC 代表 FRR のアドレス (IPv6)
  dc_frr_addresses_v6:
    frr01.local: "fd69:6684:61a:2::49"

  # 広告するホストルート
  advertise_host_route_ipv4: "192.168.40.42/32"
  advertise_host_route_ipv6: "fd69:6684:61a:2::42/128"

  # 所属クラスタ定義
  clusters:
    cluster1:
      pod_cidrs_v4:
        - "10.244.0.0/16"
      service_cidrs_v4:
        - "10.254.0.0/16"
      pod_cidrs_v6:
        - "fdb6:6e92:3cfb:200::/56"
      service_cidrs_v6:
        - "fdb6:6e92:3cfb:feed::/112"
```

**標準デュアルスタックからの変更点**:

- `rfc5549_enabled: true` を設定
- `ipv4_transport_ipv6_nlri_enabled: false`を設定 ( 排他的 )
- `dc_frr_addresses_v6` に IPv6 アドレスを指定（`dc_frr_addresses` は使用しない）
- `router_id` は IPv4 形式のまま ( BGP Router ID は IPv4 形式が必須 )

#### DC 代表 FRR の設定例 (host_vars/frr01.local)

```yaml
---
# FRR 基本設定 (RFC 5549 有効)
frr_basic:
  enabled: true
  rfc5549_enabled: true  # IPv6 トランスポート有効
  local_asn: 65011
  router_id: "192.168.40.49"

  # K8s ワーカーノードとの iBGP 設定 (IPv6 アドレス)
  frr_k8s_neighbors:
    - { addr: "fd69:6684:61a:2::41", asn: 65011, desc: "C1 control-plane" }
    - { addr: "fd69:6684:61a:2::42", asn: 65011, desc: "C1 worker-1" }
    - { addr: "fd69:6684:61a:2::43", asn: 65011, desc: "C1 worker-2" }

  # 外部ゲートウェイとの eBGP 設定 (IPv6 アドレス)
  frr_ebgp_neighbors:
    - { addr: "fd69:6684:61a:90::81", asn: 65100, desc: "External GW" }

  # 広告する DC ネットワーク
  frr_advertise_networks_v4:
    - "192.168.30.0/24"
    - "192.168.40.0/24"
    - "192.168.255.0/24"

  frr_advertise_networks_v6:
    - "fd69:6684:61a:2::/64"
    - "fd69:6684:61a:90::/64"
    - "fdad:ba50:248b:1::/64"
```

**重要なポイント**:

- `frr_k8s_neighbors` の全アドレスを IPv6 で指定
- `frr_ebgp_neighbors` の全アドレスを IPv6 で指定
- コントロールプレーンノードを含める場合は, そのノードも FRR がインストールされている必要がある

#### External Gateway の設定例 (host_vars/extgw.local)

```yaml
---
# External Gateway FRR 設定 (RFC 5549 有効)
frr_basic:
  enabled: true
  rfc5549_enabled: true  # IPv6 トランスポート有効
  local_asn: 65100
  router_id: "192.168.255.81"

  # DC 代表 FRR との eBGP 設定 (IPv6 アドレス)
  frr_ebgp_neighbors:
    - { addr: "fd69:6684:61a:90::49", asn: 65011, desc: "Cluster1 Gateway (frr01)" }
    - { addr: "fd69:6684:61a:90::48", asn: 65012, desc: "Cluster2 Gateway (frr02)" }

  # 広告する外部ネットワーク
  frr_advertise_networks_v4:
    - "192.168.255.0/24"

  frr_advertise_networks_v6:
    - "fd69:6684:61a:90::/64"
```

**重要なポイント**:

- `frr_ebgp_neighbors` の全アドレスを IPv6 で指定 ( 各 DC の外部接続側アドレス )
- AS 番号は eBGP 用の独立した AS (65100) を使用

#### Cluster2 のワーカーノード設定例 (host_vars/k8sworker0201.local)

```yaml
---
# K8s Worker FRR 設定 (RFC 5549 有効 - Cluster2)
k8s_worker_frr:
  enabled: true
  rfc5549_enabled: true
  local_asn: 65012  # Cluster2 の AS 番号
  router_id: "192.168.30.52"
  cluster_name: "cluster2"

  # DC 代表 FRR のアドレス (IPv6)
  dc_frr_addresses_v6:
    frr02.local: "fd69:6684:61a:3::48"

  # 広告するホストルート
  advertise_host_route_ipv4: "192.168.50.52/32"
  advertise_host_route_ipv6: "fd69:6684:61a:3::52/128"

  # 所属クラスタ定義
  clusters:
    cluster2:
      pod_cidrs_v4:
        - "10.243.0.0/16"
      service_cidrs_v4:
        - "10.253.0.0/16"
      pod_cidrs_v6:
        - "fdb6:6e92:3cfb:100::/56"
      service_cidrs_v6:
        - "fdb6:6e92:3cfb:feec::/112"
```

**重要なポイント**:

- Cluster2 は独立した AS 番号 (65012) を使用
- IPv6 アドレスが Cluster2 の範囲 (`fd69:6684:61a:3::/64`) に属している
- Pod/Service CIDR も Cluster2 専用の範囲を使用

### 1. FRR サービス状態の確認 (RFC 5549 (IPv6 トランスポート) 利用時の例)

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
systemctl status frr
```

**期待される出力**:

```plaintext
● frr.service - FRRouting
     Loaded: loaded (/usr/lib/systemd/system/frr.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-01-26 15:40:49 JST; 1min 19s ago
       Docs: https://frrouting.readthedocs.io/en/latest/setup.html
    Process: 6976 ExecStart=/usr/lib/frr/frrinit.sh start (code=exited, status=0/SUCCESS)
   Main PID: 6986 (watchfrr)
     Status: "FRR Operational"
      Tasks: 13 (limit: 4594)
     Memory: 18.6M (peak: 29.2M)
        CPU: 208ms
     CGroup: /system.slice/frr.service
             ├─6986 /usr/lib/frr/watchfrr -d -F traditional zebra bgpd staticd
             ├─6999 /usr/lib/frr/zebra -d -F traditional -A 127.0.0.1
             ├─7004 /usr/lib/frr/bgpd -d -F traditional -A 127.0.0.1
             └─7011 /usr/lib/frr/staticd -d -F traditional

 1月 26 15:40:49 k8sworker0101 watchfrr[6986]: [QDG3Y-BY5TN] zebra state -> up : connect succeeded
 1月 26 15:40:49 k8sworker0101 watchfrr[6986]: [QDG3Y-BY5TN] bgpd state -> up : connect succeeded
 1月 26 15:40:49 k8sworker0101 watchfrr[6986]: [QDG3Y-BY5TN] staticd state -> up : connect succeeded
 1月 26 15:40:49 k8sworker0101 watchfrr[6986]: [KWE5Q-QNGFC] all daemons up, doing startup-complete notify
 1月 26 15:40:49 k8sworker0101 systemd[1]: Started frr.service - FRRouting.
 1月 26 15:40:54 k8sworker0101 bgpd[7004]: [M59KS-A3ZXZ] bgp_update_receive: rcvd End-of-RIB for IPv4 Unicast from fd69:6684:61a:2::49 in vrf default
 1月 26 15:40:54 k8sworker0101 bgpd[7004]: [M59KS-A3ZXZ] bgp_update_receive: rcvd End-of-RIB for IPv6 Unicast from fd69:6684:61a:2::49 in vrf default
```

**確認ポイント**:

- `Active: active (running)` が表示される
- zebra, bgpd, staticd のプロセスが起動している
- **BGP End-of-RIB メッセージでネイバーが IPv6 アドレス (`fd69:6684:61a:2::49`) として表示される** (RFC 5549 の証拠)
- IPv4/IPv6 両方の Unicast で End-of-RIB が受信されている

### 2. BGP セッション状態の確認 (IPv6 トランスポート)

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
sudo vtysh -c "show bgp summary"
```

**期待される出力**:

```plaintext
IPv4 Unicast Summary (VRF default):
BGP router identifier 192.168.30.42, local AS number 65011 vrf-id 0
BGP table version 11
RIB entries 19, using 3648 bytes of memory
Peers 1, using 724 KiB of memory

Neighbor            V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
fd69:6684:61a:2::49 4      65011        11         7        0    0    0 00:01:50            8        3 DC-FRR frr01.local

Total number of neighbors 1

IPv6 Unicast Summary (VRF default):
BGP router identifier 192.168.30.42, local AS number 65011 vrf-id 0
BGP table version 11
RIB entries 19, using 3648 bytes of memory
Peers 1, using 724 KiB of memory

Neighbor            V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt Desc
fd69:6684:61a:2::49 4      65011        11         7        0    0    0 00:01:50            8        3 DC-FRR frr01.local

Total number of neighbors 1
```

**確認ポイント**:

- **Neighbor 列に IPv6 アドレス (`fd69:6684:61a:2::49`) が表示される** (IPv6 トランスポート)
- `State/PfxRcd` が数値 (IPv4: `8`, IPv6: `8`) であり, エラー状態でない
- IPv4/IPv6 両方の Address Family で **同じ IPv6 ネイバー** とセッションが確立している
- `PfxSnt` が `3` である (Pod CIDR, Service CIDR, ホストルートを送信)

### 3. 広告経路の確認 (IPv4 - RFC 5549)

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
sudo vtysh -c "show ip bgp"
```

**期待される出力**:

```plaintext
BGP table version is 11, local router ID is 192.168.30.42, vrf id 0
Default local pref 100, local AS 65011
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

   Network          Next Hop            Metric LocPrf Weight Path
*>i10.243.0.0/16    fd69:6684:61a:90::81
                                                  100      0 65100 65012 ?
*> 10.244.0.0/16    0.0.0.0                  0         32768 ?
*>i10.253.0.0/16    fd69:6684:61a:90::81
                                                  100      0 65100 65012 ?
*> 10.254.0.0/16    0.0.0.0                  0         32768 ?
*>i192.168.30.0/24  fe80::250:56ff:fe00:4a1c
                                             0    100      0 i
*>i192.168.40.0/24  fe80::250:56ff:fe00:4a1c
                                             0    100      0 i
*> 192.168.40.42/32 0.0.0.0                  0         32768 ?
*>i192.168.50.0/24  fd69:6684:61a:90::81
                                                  100      0 65100 65012 i
*>i192.168.50.52/32 fd69:6684:61a:90::81
                                                  100      0 65100 65012 ?
*>i192.168.50.53/32 fd69:6684:61a:90::81
                                                  100      0 65100 65012 ?
*>i192.168.255.0/24 fe80::250:56ff:fe00:4a1c
                                             0    100      0 i

Displayed  11 routes and 11 total paths
```

**確認ポイント**:

- **IPv4 ルートのネクストホップに IPv6 アドレスが使用されている** (RFC 5549 の証拠):
  - iBGP ピアから学習したルート: link-local (`fe80::250:56ff:fe00:4a1c`) または global IPv6 (`fd69:6684:61a:90::81`)
  - ローカル広告ルート: `0.0.0.0`
- 対向クラスター (Cluster2) の IPv4 経路 (`10.243.0.0/16`, `10.253.0.0/16`, `192.168.50.0/24`) が受信されている
- ネクストホップが **IPv4 アドレスではなく IPv6 アドレス** である点に注意

### 4. 広告経路の確認 (IPv6)

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
sudo vtysh -c "show bgp ipv6"
```

**期待される出力**:

```plaintext
BGP table version is 11, local router ID is 192.168.30.42, vrf id 0
Default local pref 100, local AS 65011
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

   Network          Next Hop            Metric LocPrf Weight Path
*>ifd69:6684:61a:2::/64
                    fe80::250:56ff:fe00:4a1c
                                             0    100      0 i
*> fd69:6684:61a:2::42/128
                    ::                       0         32768 ?
*>ifd69:6684:61a:3::/64
                    fd69:6684:61a:90::48
                                                  100      0 65100 65012 i
*>ifd69:6684:61a:3::52/128
                    fd69:6684:61a:90::48
                                                  100      0 65100 65012 ?
*>ifd69:6684:61a:3::53/128
                    fd69:6684:61a:90::48
                                                  100      0 65100 65012 ?
*>ifd69:6684:61a:90::/64
                    fe80::250:56ff:fe00:4a1c
                                             0    100      0 i
*>ifdad:ba50:248b:1::/64
                    fe80::250:56ff:fe00:4a1c
                                             0    100      0 i
*>ifdb6:6e92:3cfb:100::/56
                    fd69:6684:61a:90::48
                                                  100      0 65100 65012 ?
*> fdb6:6e92:3cfb:200::/56
                    ::                       0         32768 ?
*>ifdb6:6e92:3cfb:feec::/112
                    fd69:6684:61a:90::48
                                                  100      0 65100 65012 ?
*> fdb6:6e92:3cfb:feed::/112
                    ::                       0         32768 ?

Displayed  11 routes and 11 total paths
```

**確認ポイント**:

- IPv6 ルートは通常通り link-local または global IPv6 アドレスをネクストホップとして使用
- 対向クラスター (Cluster2) の IPv6 経路が受信されている

### 5. カーネルルーティングテーブルの確認 (IPv4 - RFC 5549)

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
ip route show proto bgp
```

**期待される出力**:

```plaintext
10.243.0.0/16 nhid 42 via inet6 fe80::250:56ff:fe00:4a1c dev ens192 metric 20
10.253.0.0/16 nhid 42 via inet6 fe80::250:56ff:fe00:4a1c dev ens192 metric 20
192.168.50.0/24 nhid 42 via inet6 fe80::250:56ff:fe00:4a1c dev ens192 metric 20
192.168.50.52 nhid 42 via inet6 fe80::250:56ff:fe00:4a1c dev ens192 metric 20
192.168.50.53 nhid 42 via inet6 fe80::250:56ff:fe00:4a1c dev ens192 metric 20
192.168.255.0/24 nhid 42 via inet6 fe80::250:56ff:fe00:4a1c dev ens192 metric 20
```

**確認ポイント**:

- **IPv4 ルートが `via inet6 fe80::...` 形式で表示される** (RFC 5549 が正常に動作している証拠)
- カーネルが IPv4 パケットを IPv6 ネクストホップ経由でフォワーディングしている
- インターフェース名 (`ens192`) は環境により異なる

### 6. カーネルルーティングテーブルの確認 (IPv6)

**実施ノード**: `k8sworker0101.local`

**コマンド**:

```bash
ip -6 route show proto bgp
```

**期待される出力**:

```plaintext
fd69:6684:61a:3::52 nhid 42 via fe80::250:56ff:fe00:4a1c dev ens192 metric 20 pref medium
fd69:6684:61a:3::53 nhid 42 via fe80::250:56ff:fe00:4a1c dev ens192 metric 20 pref medium
fd69:6684:61a:3::/64 nhid 42 via fe80::250:56ff:fe00:4a1c dev ens192 metric 20 pref medium
fd69:6684:61a:90::/64 nhid 42 via fe80::250:56ff:fe00:4a1c dev ens192 metric 20 pref medium
fdb6:6e92:3cfb:100::/56 nhid 42 via fe80::250:56ff:fe00:4a1c dev ens192 metric 20 pref medium
fdb6:6e92:3cfb:feec::/112 nhid 42 via fe80::250:56ff:fe00:4a1c dev ens192 metric 20 pref medium
```

**確認ポイント**:

- IPv6 ルートは通常通り link-local ネクストホップを使用
- 対向クラスタの IPv6 Pod/Service CIDR が表示される

### 7. DC 代表 FRR での経路確認 (RFC 5549)

**実施ノード**: `frr01.local`

#### 7.1 BGP ネイバー詳細確認 (Extended Nexthop Capability)

**コマンド**:

```bash
sudo vtysh -c "show ip bgp neighbors fd69:6684:61a:2::42"
```

**期待される出力 (抜粋)**:

```plaintext
BGP neighbor is fd69:6684:61a:2::42, remote AS 65011, local AS 65011, internal link
 Description: C1 worker-1
Hostname: k8sworker0101
  BGP version 4, remote router ID 192.168.30.42, local router ID 192.168.40.49
  BGP state = Established, up for 00:06:45
  Neighbor capabilities:
    4 Byte AS: advertised and received
    Extended Message: advertised and received
    Extended nexthop: advertised and received
      Address families by peer:
                   IPv4 Unicast
    Address Family IPv4 Unicast: advertised and received
    Address Family IPv6 Unicast: advertised and received
  Message statistics:
    Inq depth is 0
    Outq depth is 0
                         Sent       Rcvd
    Opens:                 20          1
    Notifications:          0          0
    Updates:                8          4
    Keepalives:             7          7

 For address family: IPv4 Unicast
  Update group 3, subgroup 3
  Community attribute sent to this neighbor(all)
  3 accepted prefixes

 For address family: IPv6 Unicast
  Update group 4, subgroup 4
  Community attribute sent to this neighbor(all)
  3 accepted prefixes

Local host: fd69:6684:61a:2::49, Local port: 179
Foreign host: fd69:6684:61a:2::42, Foreign port: 44264
Nexthop: 192.168.40.49
Nexthop global: fd69:6684:61a:2::49
Nexthop local: fe80::250:56ff:fe00:4a1c
BGP connection: shared network
```

**確認ポイント**:

- **`Extended nexthop: advertised and received`** が表示される (RFC 5549 の証拠)
- **`Address families by peer: IPv4 Unicast`** が Extended nexthop の対象
- BGP セッションが IPv6 アドレス間で確立 (`fd69:6684:61a:2::49` <=> `fd69:6684:61a:2::42`)
- IPv4/IPv6 両方の Address Family が negotiated されている
- 3 prefixes (Pod CIDR, Service CIDR, ホストルート) が受信されている

#### 7.2 IPv4 BGP テーブルの確認 (link-local nexthop)

**コマンド**:

```bash
sudo vtysh -c "show ip bgp"
```

**期待される出力 (抜粋)**:

```plaintext
BGP table version is 14, local router ID is 192.168.40.49, vrf id 0
Default local pref 100, local AS 65011
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

   Network          Next Hop            Metric LocPrf Weight Path
*> 10.243.0.0/16    fe80::250:56ff:fe00:b8eb
                                                           0 65100 65012 ?
*=i10.244.0.0/16    fe80::250:56ff:fe00:bf27
                                             0    100      0 ?
*>i                 fe80::250:56ff:fe00:7b26
                                             0    100      0 ?
*> 10.253.0.0/16    fe80::250:56ff:fe00:b8eb
                                                           0 65100 65012 ?
*=i10.254.0.0/16    fe80::250:56ff:fe00:bf27
                                             0    100      0 ?
*>i                 fe80::250:56ff:fe00:7b26
                                             0    100      0 ?
*> 192.168.30.0/24  0.0.0.0                  0         32768 i
*> 192.168.40.0/24  0.0.0.0                  0         32768 i
*>i192.168.40.42/32 fe80::250:56ff:fe00:7b26
                                             0    100      0 ?
*>i192.168.40.43/32 fe80::250:56ff:fe00:bf27
                                             0    100      0 ?
*> 192.168.50.0/24  fe80::250:56ff:fe00:b8eb
                                                           0 65100 65012 i

Displayed  12 routes and 15 total paths
```

**確認ポイント**:

- **IPv4 ルートのネクストホップが link-local IPv6 アドレス (`fe80::...`) で表示される** (RFC 5549)
- ワーカーノードから学習したルート (`10.244.0.0/16`, `10.254.0.0/16`, ホストルート) が含まれる
- eBGP 経由で学習した対向クラスタのルートも link-local nexthop を使用

### 8. External Gateway での経路確認 (RFC 5549)

**実施ノード**: `extgw.local`

#### 8.1 IPv4 BGP テーブルの確認

**コマンド**:

```bash
sudo vtysh -c "show ip bgp"
```

**期待される出力**:

```plaintext
BGP table version is 12, local router ID is 192.168.255.81, vrf id 0
Default local pref 100, local AS 65100
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

    Network          Next Hop            Metric LocPrf Weight Path
 *> 10.243.0.0/16    fe80::250:56ff:fe00:30c
                                                           0 65012 ?
 *> 10.244.0.0/16    fe80::250:56ff:fe00:4a26
                                                           0 65011 ?
 *> 10.253.0.0/16    fe80::250:56ff:fe00:30c
                                                           0 65012 ?
 *> 10.254.0.0/16    fe80::250:56ff:fe00:4a26
                                                           0 65011 ?
 *> 192.168.30.0/24  fe80::250:56ff:fe00:4a26
                                             0             0 65011 i
 *                   fe80::250:56ff:fe00:30c
                                             0             0 65012 i
 *> 192.168.40.0/24  fe80::250:56ff:fe00:4a26
                                             0             0 65011 i
 *> 192.168.40.42/32 fe80::250:56ff:fe00:4a26
                                                           0 65011 ?
 *> 192.168.40.43/32 fe80::250:56ff:fe00:4a26
                                                           0 65011 ?
 *> 192.168.50.0/24  fe80::250:56ff:fe00:30c
                                             0             0 65012 i
 *> 192.168.50.52/32 fe80::250:56ff:fe00:30c
                                                           0 65012 ?
 *> 192.168.50.53/32 fe80::250:56ff:fe00:30c
                                                           0 65012 ?
 *  192.168.255.0/24 fe80::250:56ff:fe00:4a26
                                             0             0 65011 i
 *                   fe80::250:56ff:fe00:30c
                                             0             0 65012 i
 *>                  0.0.0.0                  0         32768 i

Displayed  12 routes and 15 total paths
```

**確認ポイント**:

- **eBGP で学習した IPv4 ルートのネクストホップが link-local IPv6 アドレス (`fe80::...`) である** (RFC 5549)
- 両クラスタ (AS 65011, AS 65012) からの Pod/Service CIDR が受信されている
- `Path` 列に AS 番号が表示される (eBGP 経由)
- ワーカーノードのホストルート (`192.168.40.42/32`, `192.168.40.43/32`, `192.168.50.52/32`, `192.168.50.53/32`) も link-local nexthop で学習されている

#### 8.2 IPv6 BGP テーブルの確認

**コマンド**:

```bash
sudo vtysh -c "show bgp ipv6"
```

**期待される出力**:

```plaintext
BGP table version is 12, local router ID is 192.168.255.81, vrf id 0
Default local pref 100, local AS 65100
Status codes:  s suppressed, d damped, h history, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

    Network          Next Hop            Metric LocPrf Weight Path
 *> fd69:6684:61a:2::/64
                    fe80::250:56ff:fe00:4a26
                                             0             0 65011 i
 *> fd69:6684:61a:2::42/128
                    fe80::250:56ff:fe00:4a26
                                                           0 65011 ?
 *> fd69:6684:61a:2::43/128
                    fe80::250:56ff:fe00:4a26
                                                           0 65011 ?
 *> fd69:6684:61a:3::/64
                    fe80::250:56ff:fe00:30c
                                             0             0 65012 i
 *> fd69:6684:61a:3::52/128
                    fe80::250:56ff:fe00:30c
                                                           0 65012 ?
 *> fd69:6684:61a:3::53/128
                    fe80::250:56ff:fe00:30c
                                                           0 65012 ?
 *  fd69:6684:61a:90::/64
                    fe80::250:56ff:fe00:4a26
                                             0             0 65011 i
 *                   fe80::250:56ff:fe00:30c
                                             0             0 65012 i
 *>                  ::                       0         32768 i
 *> fdad:ba50:248b:1::/64
                    fe80::250:56ff:fe00:4a26
                                             0             0 65011 i
 *                   fe80::250:56ff:fe00:30c
                                             0             0 65012 i
 *> fdb6:6e92:3cfb:100::/56
                    fe80::250:56ff:fe00:30c
                                                           0 65012 ?
 *> fdb6:6e92:3cfb:200::/56
                    fe80::250:56ff:fe00:4a26
                                                           0 65011 ?
 *> fdb6:6e92:3cfb:feec::/112
                    fe80::250:56ff:fe00:30c
                                                           0 65012 ?
 *> fdb6:6e92:3cfb:feed::/112
                    fe80::250:56ff:fe00:4a26
                                                           0 65011 ?

Displayed  12 routes and 15 total paths
```

**確認ポイント**:

- IPv6 ルートは通常通り link-local ネクストホップを使用
- 両クラスタの IPv6 Pod/Service CIDR および DC ネットワークの /64 プレフィクスが受信されている
- ワーカーノードのホストルート (`fd69:6684:61a:2::42/128`, etc.) も学習されている

### 9. DC 間 Pod 疎通テスト (RFC 5549)

RFC 5549 環境でも Pod 間通信テストの手順は通常の環境と同じです。詳細な手順は [12. DC 間 Pod 疎通テスト (IPv4/IPv6 デュアルスタック)](#12-dc-間-pod-疎通テスト-ipv4ipv6-デュアルスタック) を参照してください。

以下は RFC 5549 環境での実際の検証例です。

#### 9.1 テスト Pod のデプロイと IP アドレス確認

**コマンド**:

```bash
# 既存のPodを削除
kubectl --context kubernetes-admin@kubernetes delete pod test-pod --ignore-not-found
kubectl --context kubernetes-admin@kubernetes-2 delete pod test-pod --ignore-not-found

# 新しいPodをデプロイ
kubectl --context kubernetes-admin@kubernetes run test-pod --image=busybox --command -- sleep 3600
kubectl --context kubernetes-admin@kubernetes-2 run test-pod --image=busybox --command -- sleep 3600

# Pod起動を待機
kubectl --context kubernetes-admin@kubernetes wait --for=condition=Ready pod/test-pod --timeout=60s
kubectl --context kubernetes-admin@kubernetes-2 wait --for=condition=Ready pod/test-pod --timeout=60s

# IPアドレスを確認
kubectl --context kubernetes-admin@kubernetes get pod test-pod -o wide
kubectl --context kubernetes-admin@kubernetes-2 get pod test-pod -o wide
```

**期待される出力**:

```plaintext
pod/test-pod created
pod/test-pod created
pod/test-pod condition met
pod/test-pod condition met
NAME       READY   STATUS    RESTARTS   AGE   IP                         NODE            NOMINATED NODE   READINESS GATES
test-pod   1/1     Running   0          20s   fdb6:6e92:3cfb:204::f7c7   k8sworker0102   <none>           <none>
NAME       READY   STATUS    RESTARTS   AGE   IP                         NODE            NOMINATED NODE   READINESS GATES
test-pod   1/1     Running   0          20s   fdb6:6e92:3cfb:103::4a74   k8sworker0202   <none>           <none>
```

**詳細な IP アドレス情報の確認**:

```bash
kubectl --context kubernetes-admin@kubernetes exec test-pod -- ip addr
kubectl --context kubernetes-admin@kubernetes-2 exec test-pod -- ip addr
```

**期待される出力**:

```plaintext
# Cluster1 Pod
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
    inet6 ::1/128 scope host
8: eth0@if9: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue qlen 1000
    link/ether c6:17:07:2f:e5:0c brd ff:ff:ff:ff:ff:ff
    inet 10.244.4.183/32 scope global eth0
    inet6 fdb6:6e92:3cfb:204::f7c7/128 scope global flags 02
    inet6 fe80::c417:7ff:fe2f:e50c/64 scope link

# Cluster2 Pod
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
    inet6 ::1/128 scope host
8: eth0@if9: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue qlen 1000
    link/ether 2a:9e:a1:68:3f:9e brd ff:ff:ff:ff:ff:ff
    inet 10.243.3.45/32 scope global eth0
    inet6 fdb6:6e92:3cfb:103::4a74/128 scope global flags 02
    inet6 fe80::289e:a1ff:fe68:3f9e/64 scope link
```

**確認ポイント**:

- Cluster1 Pod: IPv4 `10.244.4.183/32`, IPv6 `fdb6:6e92:3cfb:204::f7c7/128` (k8sworker0102)
- Cluster2 Pod: IPv4 `10.243.3.45/32`, IPv6 `fdb6:6e92:3cfb:103::4a74/128` (k8sworker0202)
- IPv6 アドレスがクラスタ専用範囲に属している (`0200::/56` vs `0100::/56`)

#### 9.2 IPv6 疎通テスト

**コマンド (Cluster1  =>  Cluster2)**:

```bash
kubectl --context kubernetes-admin@kubernetes exec test-pod -- ping -c 3 fdb6:6e92:3cfb:103::4a74
```

**期待される出力**:

```plaintext
PING fdb6:6e92:3cfb:103::4a74 (fdb6:6e92:3cfb:103::4a74): 56 data bytes
64 bytes from fdb6:6e92:3cfb:103::4a74: seq=0 ttl=59 time=1.551 ms
64 bytes from fdb6:6e92:3cfb:103::4a74: seq=1 ttl=59 time=1.373 ms
64 bytes from fdb6:6e92:3cfb:103::4a74: seq=2 ttl=59 time=0.790 ms

--- fdb6:6e92:3cfb:103::4a74 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.790/1.238/1.551 ms
```

**コマンド (Cluster2  =>  Cluster1)**:

```bash
kubectl --context kubernetes-admin@kubernetes-2 exec test-pod -- ping -c 3 fdb6:6e92:3cfb:204::f7c7
```

**期待される出力**:

```plaintext
PING fdb6:6e92:3cfb:204::f7c7 (fdb6:6e92:3cfb:204::f7c7): 56 data bytes
64 bytes from fdb6:6e92:3cfb:204::f7c7: seq=0 ttl=59 time=1.293 ms
64 bytes from fdb6:6e92:3cfb:204::f7c7: seq=1 ttl=59 time=0.501 ms
64 bytes from fdb6:6e92:3cfb:204::f7c7: seq=2 ttl=59 time=0.615 ms

--- fdb6:6e92:3cfb:204::f7c7 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.501/0.803/1.293 ms
```

**確認ポイント**:

- TTL が `59` (複数ホップ経由)
- 0% パケットロス
- 双方向での IPv6 通信が成功
- **RFC 5549 環境でも Pod 間通信は正常に機能**

#### 9.3 IPv4 疎通テスト

RFC 5549 環境でも IPv4 通信は正常に機能します。以下は実際の検証例です。

**Pod IP アドレスの確認**:

```bash
kubectl --context kubernetes-admin@kubernetes get pod test-pod -o wide
kubectl --context kubernetes-admin@kubernetes-2 get pod test-pod -o wide
```

**期待される出力**:

```plaintext
NAME       READY   STATUS    RESTARTS   AGE   IP                         NODE            NOMINATED NODE   READINESS GATES
test-pod   1/1     Running   0          12s   fdb6:6e92:3cfb:204::76f5   k8sworker0102   <none>           <none>
NAME       READY   STATUS    RESTARTS   AGE   IP                         NODE            NOMINATED NODE   READINESS GATES
test-pod   1/1     Running   0          12s   fdb6:6e92:3cfb:103::597f   k8sworker0202   <none>           <none>
```

**詳細な IP アドレス情報**:

```bash
kubectl --context kubernetes-admin@kubernetes exec test-pod -- ip addr
kubectl --context kubernetes-admin@kubernetes-2 exec test-pod -- ip addr
```

**期待される出力**:

```plaintext
# Cluster1 Pod
10: eth0@if11: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue qlen 1000
    link/ether 0a:6c:92:fb:ec:58 brd ff:ff:ff:ff:ff:ff
    inet 10.244.4.219/32 scope global eth0
    inet6 fdb6:6e92:3cfb:204::76f5/128 scope global flags 02
    inet6 fe80::86c:92ff:fefb:ec58/64 scope link

# Cluster2 Pod
10: eth0@if11: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue qlen 1000
    link/ether 06:d9:65:6f:1a:c7 brd ff:ff:ff:ff:ff:ff
    inet 10.243.3.105/32 scope global eth0
    inet6 fdb6:6e92:3cfb:103::597f/128 scope global flags 02
    inet6 fe80::4d9:65ff:fe6f:1ac7/64 scope link
```

**コマンド (Cluster1  =>  Cluster2)**:

```bash
kubectl --context kubernetes-admin@kubernetes exec test-pod -- ping -c 3 10.243.3.105
```

**期待される出力**:

```plaintext
PING 10.243.3.105 (10.243.3.105): 56 data bytes
64 bytes from 10.243.3.105: seq=0 ttl=59 time=1.518 ms
64 bytes from 10.243.3.105: seq=1 ttl=59 time=0.706 ms
64 bytes from 10.243.3.105: seq=2 ttl=59 time=0.636 ms

--- 10.243.3.105 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.636/0.953/1.518 ms
```

**コマンド (Cluster2  =>  Cluster1)**:

```bash
kubectl --context kubernetes-admin@kubernetes-2 exec test-pod -- ping -c 3 10.244.4.219
```

**期待される出力**:

```plaintext
PING 10.244.4.219 (10.244.4.219): 56 data bytes
64 bytes from 10.244.4.219: seq=0 ttl=59 time=1.357 ms
64 bytes from 10.244.4.219: seq=1 ttl=59 time=0.613 ms
64 bytes from 10.244.4.219: seq=2 ttl=59 time=1.613 ms

--- 10.244.4.219 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.613/1.194/1.613 ms
```

**確認ポイント**:

- TTL が `59` (複数ホップ経由)
- 0% パケットロス
- 双方向での IPv4 通信が成功
- RFC 5549 環境でも IPv4 通信は正常に機能すること
- IPv4 ルートは内部的に IPv6 ネクストホップ経由でフォワーディングされているが, Pod からは透過的に動作

## トラブルシューティング

### 1. BGP セッションが `Established` にならない場合

**症状**: `show bgp summary` で `State/PfxRcd` が `Idle`, `Connect`, `Active` などのエラー状態

#### 1.1 全構成共通の診断手順

**1. ファイアウォール確認**:

```bash
sudo iptables -L -n | grep 179
sudo ip6tables -L -n | grep 179
```

BGP ポート (TCP 179) が許可されているか確認

**2. ネットワーク到達性確認**:

標準デュアルスタックとMultiprotocol BGP:

```bash
ping -c 3 192.168.40.49  # IPv4トランスポート
ping6 -c 3 fd69:6684:61a:2::49  # 標準デュアルスタックのみ
```

RFC 5549:

```bash
ping6 -c 3 fd69:6684:61a:2::49  # IPv6トランスポートのみ
```

DC 代表 FRR への到達性を確認

**3. FRR ログ確認**:

```bash
sudo journalctl -u frr -n 50
```

エラーメッセージを確認。特に以下のメッセージに注意:

- `Connection refused`: ファイアウォールまたはDC代表FRR側でポートが閉じている
- `No route to host`: ルーティング問題
- `AS mismatch`: AS番号の不一致

**4. DC 代表 FRR の設定確認**:

   DC 側の FRR (`frr01.local`, `frr02.local`) が正しい IP アドレス (K8s ネットワーク側: `192.168.40.x`, `192.168.50.x`) でワーカーノードをネイバーとして設定しているか確認。管理ネットワーク (`192.168.30.x`) を使用している場合は接続できません。

   ```bash
   # frr01.local で実行
   sudo vtysh -c "show bgp neighbors" | grep -A 5 "BGP neighbor is"
   ```

#### 1.2 標準デュアルスタック構成特有の問題

**症状**: IPv4セッションは確立するがIPv6セッションが `Idle` または `Active`

**原因**:

- IPv6ネイバー (`dc_frr_addresses_v6`) の定義不足
- IPv6アドレスの誤り
- DC代表FRR側でIPv6ネイバー設定が欠落

**解決方法**:

**1. host_vars でIPv6ネイバーを確認**:

```yaml
k8s_worker_frr:
  dc_frr_addresses:
    frr01.local: "192.168.40.49"
  dc_frr_addresses_v6:
    frr01.local: "fd69:6684:61a:2::49"  # この定義が必要
```

**2. IPv6アドレスの到達性確認**:

```bash
ping6 -c 3 fd69:6684:61a:2::49
ip -6 route get fd69:6684:61a:2::49
```

**3. DC代表FRR側でIPv6ネイバーを確認**:

```bash
# frr01.local で実行
sudo vtysh -c "show bgp ipv6 unicast summary"
```

#### 1.3 Multiprotocol BGP構成特有の問題

**症状**: IPv4セッションは確立するが, IPv6ルートが交換されない

**原因**:

- `ipv4_transport_ipv6_nlri_enabled` が設定されていない
- DC代表FRR側でMultiprotocol BGP対応が不足

**解決方法**: セクション「2.1 Multiprotocol BGP 構成の場合」を参照

#### 1.4 RFC 5549構成特有の問題

**症状**: IPv6セッションが確立しない, またはIPv4ルートが交換されない

**原因**:

- `rfc5549_enabled` が設定されていない
- IPv6ネイバー (`dc_frr_addresses_v6`) の定義不足
- DC代表FRR側でExtended Nexthop Capabilityが無効
- `dc_frr_addresses` (IPv4ネイバー) が誤って定義されている

**解決方法**:

**1. host_vars でRFC 5549設定を確認**:

```yaml
k8s_worker_frr:
  rfc5549_enabled: true
  ipv4_transport_ipv6_nlri_enabled: false  # falseまたは未定義
  dc_frr_addresses_v6:
    frr01.local: "fd69:6684:61a:2::49"
  # dc_frr_addresses は定義しない
```

**2. IPv6セッション確立確認**:

```bash
sudo vtysh -c "show bgp ipv6 unicast summary"
```

**3. Extended Nexthop Capability確認**:

```bash
sudo vtysh -c "show bgp ipv6 neighbors fd69:6684:61a:2::49" | grep "Extended nexthop"
```

`Extended nexthop: advertised and received` が表示されるか確認

**4. DC代表FRR側のRFC 5549対応確認**:

```bash
# frr01.local で実行
sudo vtysh -c "show bgp ipv6 neighbors fd69:6684:61a:2::42" | grep "Extended nexthop"
```

### 2. IPv6 BGP セッションが `NoNeg` 状態になる場合

**症状**: `show bgp ipv6 unicast summary` で `State/PfxRcd` が `NoNeg`

**原因と解決方法は構成により異なります**:

#### 2.1 Multiprotocol BGP 構成の場合

**原因**: IPv4 トランスポート上で IPv6 NLRI を交換する設定が有効になっていない

**解決方法**:

**1. host_vars で設定を追加**:

```yaml
k8s_worker_frr:
  enabled: true
  ipv4_transport_ipv6_nlri_enabled: true  # この行を追加
  local_asn: 65011
  # ...残りの設定...
```

**2. ロールを再実行**:

```bash
ansible-playbook -i inventory/hosts k8s-worker.yml --tags k8s-worker-frr
```

**3. BGP セッション再確認**:

```bash
sudo vtysh -c "show bgp ipv6 unicast summary"
```

`State/PfxRcd` が数値になれば成功

#### 2.2 標準デュアルスタック構成の場合

**原因**: IPv6 ネイバーが定義されていない, またはDC代表FRR側でIPv6ネイバー設定が不足している

**解決方法**:

**1. host_vars で IPv6 ネイバーを追加**:

```yaml
k8s_worker_frr:
  enabled: true
  local_asn: 65011
  # IPv4 ネイバー
  dc_frr_addresses:
    frr01.local: "192.168.40.49"
  # IPv6 ネイバー (この定義が必要)
  dc_frr_addresses_v6:
    frr01.local: "fd69:6684:61a:2::49"
  # ...残りの設定...
```

**2. DC代表FRR側の設定確認**:

DC代表FRR (`frr01.local`) でIPv6ネイバーが設定されているか確認:

```bash
# frr01.local で実行
sudo vtysh -c "show bgp ipv6 unicast summary"
```

ワーカーノードのIPv6アドレス (例: `fd69:6684:61a:2::42`) がネイバーとして表示されるか確認。表示されない場合は, DC代表FRR側の設定を見直してください。

**3. ロールを再実行**:

```bash
ansible-playbook -i inventory/hosts k8s-worker.yml --tags k8s-worker-frr
```

#### 2.3 RFC 5549 構成の場合

**原因**: RFC 5549ではIPv6トランスポートでIPv4/IPv6両方のNLRIを交換するため, IPv6 Unicast Summaryで`NoNeg`になることは通常ありません。代わりに, IPv4 Unicast Summaryで`NoNeg`が表示される場合があります。

**症状**: `show bgp ipv4 unicast summary` で `State/PfxRcd` が `NoNeg`

**原因**: RFC 5549が正しく設定されていない, またはExtended Nexthop Capabilityがネゴシエートされていない

**解決方法**:

**1. host_vars でRFC 5549設定を確認**:

```yaml
k8s_worker_frr:
  enabled: true
  rfc5549_enabled: true  # RFC 5549を有効化
  ipv4_transport_ipv6_nlri_enabled: false  # 排他的: false必須
  local_asn: 65011
  # IPv6 ネイバーのみ定義
  dc_frr_addresses_v6:
    frr01.local: "fd69:6684:61a:2::49"
  # dc_frr_addresses は不要
  # ...残りの設定...
```

**2. DC代表FRR側のRFC 5549対応確認**:

DC代表FRR側もRFC 5549 (Extended Nexthop Capability) に対応している必要があります。DC代表FRRで以下を確認:

```bash
# frr01.local で実行
sudo vtysh -c "show bgp ipv6 neighbors fd69:6684:61a:2::42" | grep "Extended nexthop"
```

`Extended nexthop: advertised and received` が表示されるか確認。表示されない場合, DC代表FRR側でRFC 5549を有効化してください。

**3. ロールを再実行**:

```bash
ansible-playbook -i inventory/hosts k8s-worker.yml --tags k8s-worker-frr
```

### 3. 経路が広告されない, またはホストルートのみ広告される場合

**症状**: `show ip bgp` や `show bgp ipv6` で Pod/Service CIDR が表示されない, ホストルート (例: `192.168.40.42/32`) のみ広告される

#### 3.1 全構成共通の原因と解決方法

**原因**: `host_vars` で `clusters.<cluster_name>` の定義が不足している

**解決方法**:

**1. host_vars で clusters 定義を追加**:

```yaml
k8s_worker_frr:
  enabled: true
  cluster_name: "cluster1"  # 所属クラスタを明示
  clusters:
    cluster1:
      pod_cidrs_v4: ["10.244.0.0/16"]
      pod_cidrs_v6: ["fdb6:6e92:3cfb:0200::/56"]
      svc_cidrs_v4: ["10.254.0.0/16"]
      svc_cidrs_v6: ["fdb6:6e92:3cfb:feed::/112"]
```

**2. 静的経路の確認** (`route_advertisement_method="static"` の場合):

```bash
ip route show 10.244.0.0/16
ip -6 route show fdb6:6e92:3cfb:200::/56
```

静的経路が定義されているか確認

**3. redistribute static の確認**:

```bash
sudo vtysh -c "show running-config" | grep "redistribute static"
```

`redistribute static` が address-family に設定されているか確認

**4. prefix-list のマッチ確認**:

```bash
sudo vtysh -c "show ip prefix-list PL-V4-POD-OUT"
sudo vtysh -c "show ipv6 prefix-list PL-V6-POD-OUT"
```

広告したい CIDR が prefix-list の範囲内か確認

#### 3.2 標準デュアルスタック構成での確認ポイント

**症状**: IPv4経路は広告されるがIPv6経路が広告されない

**原因**:

- `clusters.<cluster_name>.pod_cidrs_v6` または `svc_cidrs_v6` の定義不足
- IPv6静的経路の未作成
- IPv6 address-family で `redistribute static` が設定されていない

**解決方法**:

**1. IPv6経路の静的定義確認**:

```bash
ip -6 route show fdb6:6e92:3cfb:200::/56
ip -6 route show fdb6:6e92:3cfb:feed::/112
ip -6 route show fd69:6684:61a:2::42/128
```

**2. FRR設定でIPv6 address-family確認**:

```bash
sudo vtysh -c "show running-config" | grep -A 10 "address-family ipv6"
```

`redistribute static` がIPv6 address-familyに含まれているか確認

**3. IPv6経路の広告確認**:

```bash
sudo vtysh -c "show bgp ipv6 unicast"
```

自ノードで生成した経路 (Next Hop `::`) が表示されるか確認

#### 3.3 Multiprotocol BGP構成での確認ポイント

**症状**: IPv4経路は広告されるがIPv6経路が広告されない

**原因**:

- `ipv4_transport_ipv6_nlri_enabled` が設定されていない
- IPv4ネイバーでIPv6 address-familyがactivateされていない

**解決方法**:

**1. IPv4ネイバーでIPv6 address-family有効化確認**:

```bash
sudo vtysh -c "show running-config" | grep -A 15 "address-family ipv6"
```

`neighbor 192.168.40.49 activate` がIPv6 address-familyに含まれているか確認

**2. BGP IPv6サマリーでIPv4ネイバー確認**:

```bash
sudo vtysh -c "show bgp ipv6 unicast summary"
```

IPv4アドレス (`192.168.40.49`) のネイバーが表示され, `PfxSnt` が3以上であるか確認

#### 3.4 RFC 5549構成での確認ポイント

**症状**: IPv6経路は広告されるがIPv4経路が広告されない

**原因**:

- `rfc5549_enabled` が設定されていない
- Extended Nexthop Capabilityが有効化されていない
- IPv4 address-familyでIPv6ネイバーがactivateされていない

**解決方法**:

**1. IPv6ネイバーでIPv4 address-family有効化確認**:

```bash
sudo vtysh -c "show running-config" | grep -A 15 "address-family ipv4"
```

`neighbor fd69:6684:61a:2::49 activate` がIPv4 address-familyに含まれているか確認

**2. Extended Nexthop Capability確認**:

```bash
sudo vtysh -c "show bgp ipv6 neighbors fd69:6684:61a:2::49" | grep -A 5 "Address Family"
```

`IPv4 Unicast` が `extended-nexthop` とともに表示されるか確認

**3. IPv4経路がIPv6セッションで送信されているか確認**:

```bash
sudo vtysh -c "show bgp ipv4 unicast summary"
```

IPv6アドレス (`fd69:6684:61a:2::49`) のネイバーが表示され, `PfxSnt` が3以上であるか確認

### 4. IPv6 Pod 通信が失敗する場合

**症状**: IPv4 Pod 通信は成功するが, IPv6 Pod 通信が `Destination unreachable` で失敗

**診断手順**:

**1. BGP IPv6 セッション確認**:

```bash
sudo vtysh -c "show bgp ipv6 unicast summary"
```

IPv6 セッションが Established で, `PfxRcvd` が 0 より大きいか確認

**2. IPv6 経路の受信確認**:

```bash
sudo vtysh -c "show bgp ipv6 unicast"
```

対向クラスタの IPv6 Pod CIDR (例: `fdb6:6e92:3cfb:100::/56`) が表示されるか確認

**3. Cilium ipv6-native-routing-cidr の確認**:

```bash
kubectl -n kube-system get cm cilium-config -o yaml | grep ipv6-native-routing-cidr
```

**問題のある設定例** (両クラスタを含む広い範囲):

```yaml
ipv6-native-routing-cidr: fdb6:6e92:3cfb::/48  # 悪い例
```

**推奨される設定** (クラスタ専用範囲):

```yaml
# Cluster1
ipv6-native-routing-cidr: fdb6:6e92:3cfb:0200::/56

# Cluster2
ipv6-native-routing-cidr: fdb6:6e92:3cfb:0100::/56
```

Cilium が広すぎる範囲 (例: `/48`) を `ipv6-native-routing-cidr` に設定していると, 他クラスタの Pod CIDR もローカルとみなしてしまい, BGP ルートを使用しません。各クラスタで専用の `/56` 範囲を指定してください。

**4. Kubernetes Pod CIDR と FRR 広告 CIDR の整合性確認**:

   ```bash
   # Control Plane で確認
   kubectl cluster-info dump | grep -i cluster-cidr

   # または kubeadm の初期化設定を確認
   sudo cat /etc/kubernetes/manifests/kube-controller-manager.yaml | grep cluster-cidr
   ```

   Kubernetes の `--cluster-cidr` (Control Plane) と FRR が広告している IPv6 CIDR (`host_vars` の `clusters.<cluster_name>.pod_cidrs_v6`) が一致しているか確認。不一致の場合, 以下のいずれかで修正:

- **方法1**: `host_vars/k8sctrlplane*.local` の `k8s_pod_ipv6_network_cidr` をクラスタ専用範囲 (例: `fdb6:6e92:3cfb:0200::/56`) に変更し, クラスタを再構築
- **方法2**: ワーカーノードの `host_vars` で `clusters.<cluster_name>.pod_cidrs_v6` を Kubernetes の実際の Pod CIDR に合わせる

   **注意**: Kubernetes が `/48` を使用し, 各ノードに `/64` を割り当てている場合, FRR が `/56` を広告していると通信できません。CIDR は完全に一致させる必要があります。

**5. kernel の IPv6 経路確認**:

   ```bash
   ip -6 route show proto bgp
   ```

   対向クラスタの Pod CIDR が表示されない場合, BGP ルートがカーネルに反映されていません。FRR の `table` 設定や `kernel_route_filter` を確認してください。

### 5. 経路受信は成功するが, Pod から外部への通信ができない場合

**診断手順**:

**1. IP フォワーディング確認**:

```bash
sysctl net.ipv4.ip_forward
sysctl net.ipv6.conf.all.forwarding
```

両方が `1` であることを確認

**2. Cilium のルーティングモード確認**:

```bash
kubectl -n kube-system get cm cilium-config -o yaml | grep routing-mode
```

`native` または `routed` になっているか確認。`overlay` モードでは BGP ルーティングは機能しません。

**3. Pod から外部への traceroute**:

```bash
kubectl exec -it test-pod-c1 -- traceroute -n 192.168.255.48
```

パケットがどこで止まるか確認
