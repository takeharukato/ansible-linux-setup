# k8s-whereabouts ロール

本ロールは, Kubernetes コントロールプレーンノード上に Whereabouts を導入し, Network Attachment Definition (NAD) を適用するロールです。

## 目次

- [k8s-whereabouts ロール](#k8s-whereabouts-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
    - [主な役割](#主な役割)
    - [依存ロール](#依存ロール)
    - [有効化条件](#有効化条件)
  - [主な処理](#主な処理)
  - [前提条件](#前提条件)
    - [実行順序](#実行順序)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
    - [Kubernetes API 接続設定](#kubernetes-api-接続設定)
    - [有効化フラグ](#有効化フラグ)
    - [ディレクトリパス設定](#ディレクトリパス設定)
    - [Whereabouts Helm チャート設定](#whereabouts-helm-チャート設定)
    - [ネットワーク範囲設定 (NAD 生成用)](#ネットワーク範囲設定-nad-生成用)
    - [ネットワークおよびインタフェース設定](#ネットワークおよびインタフェース設定)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
    - [パラメータおよび設定情報の読み込み](#パラメータおよび設定情報の読み込み)
    - [パッケージの確認](#パッケージの確認)
    - [ディレクトリ構造の作成](#ディレクトリ構造の作成)
    - [ユーザ・グループおよびサービス設定](#ユーザグループおよびサービス設定)
    - [Whereabouts 導入と NAD 適用](#whereabouts-導入と-nad-適用)
      - [NAD テンプレート生成](#nad-テンプレート生成)
  - [検証ポイント](#検証ポイント)
    - [必須確認事項](#必須確認事項)
      - [1. Whereabouts Helm チャートのインストール確認](#1-whereabouts-helm-チャートのインストール確認)
      - [2. Whereabouts デプロイメントの動作確認](#2-whereabouts-デプロイメントの動作確認)
      - [3. NAD 登録確認](#3-nad-登録確認)
      - [4. NAD 設定ファイルの存在確認](#4-nad-設定ファイルの存在確認)
    - [オプション確認事項](#オプション確認事項)
      - [5. Whereabouts Pod の詳細確認](#5-whereabouts-pod-の詳細確認)
      - [6. NAD の詳細内容確認](#6-nad-の詳細内容確認)
      - [7. ログの確認](#7-ログの確認)
      - [8. Pod 間通信の確認 (実通信)](#8-pod-間通信の確認-実通信)
  - [トラブルシューティング](#トラブルシューティング)
    - [問題 1: Helm チャート導入失敗 - OCI URL にアクセスできない](#問題-1-helm-チャート導入失敗---oci-url-にアクセスできない)
    - [問題 2: `config-whereabouts.yml` が実行されない](#問題-2-config-whereaboutsyml-が実行されない)
    - [問題 3: NAD の IP プール範囲が不正](#問題-3-nad-の-ip-プール範囲が不正)
    - [問題 4: kube-apiserver 待機がタイムアウト](#問題-4-kube-apiserver-待機がタイムアウト)
    - [問題 5: NAD 名前空間が不正](#問題-5-nad-名前空間が不正)
  - [注意事項](#注意事項)
    - [必須設定項目](#必須設定項目)
    - [IPv6 範囲を有効化する手順](#ipv6-範囲を有効化する手順)
    - [NAD の 名前空間 ( namespace ) を変更する手順](#nad-の-名前空間--namespace--を変更する手順)
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
| IP | - | インターネットプロトコルの略称。 |
| SQL | - | データベースを操作するための記述言語。 |
| HTTP | - | WWW で情報をやり取りする通信手順。 |
| HTTPS | - | 通信内容を暗号化して WWW 通信を行う方式。 |
| RPM | - | RHEL 系で使用するパッケージ形式。 |
| VM | - | 物理機器上で動作する仮想的な計算機。 |
| localhost | - | 同一機器自身を指す名前。 |
| root | - | Unix 系システムの最上位権限を持つ管理者識別子。 |
| ソフトウェア | - | 情報処理システムで使用するプログラム, 手順, 規則及び関連文書の全体又は一部分。 |
| アプリケーション | - | 利用者の目的を実現するために動作するソフトウェア。 |
| パッケージ | - | ソフトウェア導入に必要なファイルをまとめた配布単位。 |
| リポジトリ | - | ソフトウェアや設定情報を保管し, 取得できるようにした管理場所。 |
| コマンド | - | 実行者が計算機へ処理を指示するための命令。 |
| ホスト | - | 管理対象として識別される個別の計算機。 |
| サーバ | - | 他の機器や利用者へ機能やデータを提供する計算機, 又はその役割。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
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
| API | - | アプリケーション同士がやり取りする方法を定めた仕様。 |
| URL | - | WWW 上の資源の場所を示す文字列。 |
| Application Programming Interface | API | API の正式名称。 |
| Custom Resource Definition | CRD | Kubernetes APIを拡張してユーザ独自のリソース種別を定義する仕組み。 |
| Role-Based Access Control | RBAC | ユーザやサービスアカウントが実行可能な操作を役割(Role)で制限する仕組み。 |
| Service Account | - | Kubernetes内部でPodが他のリソースにアクセスする際に用いる仮想的なアカウント。 |
| ClusterRole | - | Kubernetesクラスタ全体に適用される権限の集合。 |
| ClusterRoleBinding | - | ClusterRoleをユーザやサービスアカウントに紐付ける仕組み。 |
| Role | - | 特定の名前空間内で有効な権限の集合。 |
| RoleBinding | - | Roleをユーザやサービスアカウントに紐付ける仕組み。 |
| 名前空間 ( namespace )  | - | Kubernetes内部でリソースを論理的に分離する単位。 |
| ポッド ( Pod ) | - | Kubernetes上で動作するコンテナの最小単位。 |
| デーモンセット ( DaemonSet ) | - | Kubernetesクラスタ内の全ノード(または指定した一部のノード)で必ずPodを1つずつ起動させるリソース。 |
| デプロイメント ( Deployment ) | - | 指定した数のPodを維持し, ローリングアップデート等を管理するリソース。 |
| StatefulSet | - | 状態を持つアプリケーションのPodを順序付けて管理するリソース。 |
| サービス ( Service ) | - | Podへのアクセスを抽象化し, 負荷分散やサービスディスカバリを提供するリソース。 |
| Ingress | - | Kubernetesクラスタ外部からHTTP/HTTPS通信を受け付け, 内部のServiceへルーティングする仕組み。 |
| コンフィグマップ ( ConfigMap ) | - | 設定情報を保持し, Podへ環境変数やファイルとして注入するリソース。 |
| シークレット ( Secret ) | - | 機密情報を保持し, Podへ安全に注入するリソース。 |
| PersistentVolume | PV | Kubernetesクラスタ内で利用可能なストレージリソースを表すオブジェクト。 |
| PersistentVolumeClaim | PVC | ユーザがPVを要求する際に利用するリソース。 |
| StorageClass | - | 動的にPVをプロビジョニングする際のストレージ種別を定義するリソース。 |
| Kubernetes ノード ( Kubernetes Node ) | - | Kubernetesクラスタを構成する物理マシンまたは仮想マシン。 |
| コントロールプレーンノード ( Control Plane Node ) | - | Kubernetesクラスタ全体を管理, 制御する中枢ノード群。kube-apiserver, kube-controller-manager, kube-schedulerなどが動作します。 |
| ワーカノード ( Worker Node ) | - | 実際にアプリケーションのPodを実行するノード。 |
| kube-apiserver | - | KubernetesのAPIリクエストを受け付け, etcdへの読み書きを仲介するコンポーネント。 |
| kube-controller-manager | - | Deployment, ReplicaSetなど各種コントローラを実行し, Kubernetesクラスタの状態を監視, 調整するコンポーネント。 |
| kube-scheduler | - | 新規作成されたPodを適切なNodeへ配置するコンポーネント。 |
| kubelet | - | 各Node上で動作し, Podの起動, 停止, 監視を行うエージェント。 |
| kube-proxy | - | 各Node上でServiceのネットワークルールを管理するコンポーネント。 |
| etcd | - | KubernetesのKubernetesクラスタ状態を保存する分散Key-Valueストア。 |
| Container Network Interface | CNI | コンテナ間のネットワーク接続を標準化するプラグイン仕様。 |
| Cilium | - | eBPFを活用した高性能なCNIプラグイン。ネットワークポリシーやサービスメッシュ機能を提供します。 |
| Extended Berkeley Packet Filter | eBPF | Linux カーネル内で安全にプログラムを実行する仕組み。高性能なパケット処理や観測機能の実装に利用される。 |
| Serviceエンドポイント ( Service Endpoint ) | - | Serviceのバックエンドとして通信を受けるPod, または, 当該の通信を受けるPodに加え, 当該の通信を受けるPodへ通信を届けるためのネットワーク上の転送先情報全体を指す。 |
| Serviceエンドポイント情報 ( Service Endpoint Information ) | - | Serviceエンドポイントを特定して転送先を決めるための情報。主にバックエンドPodのIPアドレス, ポート番号, プロトコル, 所属クラスタ名(またはクラスタ識別子)で構成される。 |
| Multus | - | 複数のCNIプラグインを同時に使用できるようにするメタCNIプラグイン。 |
| Container Runtime Interface | CRI | Kubernetesがコンテナランタイムと通信するための標準インターフェース。 |
| containerd | - | Dockerから分離された軽量なコンテナランタイム。 |
| kubeadm | - | Kubernetesクラスタの初期構築と管理を支援する公式ツール。 |
| kubectl | - | Kubernetesクラスタを操作するためのコマンドラインツール。 |
| Helm | - | Kubernetesアプリケーションのパッケージ管理ツール。Chart形式でアプリケーションを配布, インストールします。 |
| Chart | - | Helmで管理されるアプリケーションパッケージの単位。Kubernetes Manifestのテンプレート集。 |
| Operator | - | アプリケーション固有の運用知識をコードで自動化するKubernetesの拡張パターン。 |
| Custom Resource | CR | CRDで定義されたユーザ独自のリソースの実体。 |
| Admission Controller | - | APIリクエストがetcdに保存される前に検証, 変更を行うプラグイン。 |
| Network Policy | - | Pod間の通信を制御するファイアウォールルールを定義するリソース。 |
| Label | - | リソースに付与するKey-Value形式のメタデータ。リソースの分類, 検索に利用される。 |
| Selector | - | Labelを利用してリソースを選択する条件式。 |
| Annotation | - | リソースに付与するKey-Value形式の補足情報。ツールやコントローラが参照するメタデータ。 |
| Taint | - | Kubernetes ノードに設定する特殊なマークで, 特定の条件を満たさないPodの配置を拒否します。 |
| Toleration | - | PodがTaintを持つNodeへ配置されることを許可する設定。 |
| Whereabouts | - | Kubernetes 上で複数のネットワークインタフェースに対応する IPAM (IP Address Management) プラグイン。 |
| Network Attachment Definition | NAD | 追加ネットワーク接続設定を定義する Kubernetes の リソース。 |
| IPvLAN | - | ネットワークインタフェースを仮想化し, 複数の仮想インタフェースを異なるIPアドレスで提供するLinuxカーネル機機能。 |
| IPAM (IP Address Management) | - | Kubernetes クラスタ内の Pod に IP アドレスを割り当てる仕組み。 |
| Classless Inter-Domain Routing | CIDR | IP アドレスとネットワークプレフィックス長を組み合わせた表記法。 |
| Internet Protocol | IP | ネットワーク上で宛先を識別し, データを届けるための通信手順。 |
| IP Address Management | IPAM | IP アドレス割当を管理する仕組み。 |
| Open Container Initiative | OCI | コンテナ形式と実行方式の標準仕様。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Red Hat Enterprise Linux | RHEL | Red Hat 社が提供する商用 Linux ディストリビューション。 |
| Uniform Resource Locator | URL | URL の正式名称。 |
| Yet Another Markup Language | YAML | 設定ファイル形式です。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| Layer 3 | L3 | IP アドレスを使って宛先までの経路を判断する通信層。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `cat` | - | ファイル内容を標準出力へ表示するコマンド。 |
| `curl` | - | URL を指定してデータ送受信を行うコマンド。 |
| `grep` | - | テキストから条件に一致する行を抽出するコマンド。 |
| `helm` | - | Kubernetesアプリケーションのパッケージ管理ツール。Chart形式でアプリケーションを配布, インストールします。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| `ping` | - | 対象への到達性と往復遅延を確認するコマンド。 |
| `systemctl` | - | systemd 管理下のサービスを起動, 停止, 状態確認するコマンド。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
| サービス | - | 機能を利用者や他システムへ提供する仕組み。 |
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| リモートノード | - | ネットワーク越しに管理対象となる別ホストのノード。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |

## 概要
Kubernetes コントロールプレーンノード上に Whereabouts を導入し, Network Attachment Definition (NAD) を適用するロールです。`k8s-common`, `k8s-ctrlplane`, `k8s-multus` で整えた共通前提の上に, Whereabouts の Helm チャート導入と NAD の適用を行います。再実行にも対応するよう設計されています。

本ロールは, Kubernetes クラスタに対して複数ネットワークインタフェースを提供するために必要な IPAM (IP Address Management) プラグインである **Whereabouts** をコントロールプレーンノード上に Helm チャートで導入し, 関連設定を適用します。

なお, 本文中の`~` は ansible ログインユーザ (`ansible_user` 変数, 既定: `"ansible"`) のホームディレクトリ(規定: `"/home/ansible"`)を表します。

### 主な役割

- **Whereabouts Helm チャートの導入**: `oci://ghcr.io/k8snetworkplumbingwg/whereabouts-chart` から OCI 形式で Helm チャートを取得し, `kubectl` で鎖ラスタに導入します。
- **Network Attachment Definition (NAD) の生成・適用**: Jinja2 テンプレートから IPv4/IPv6 デュアルスタック対応の NAD `ipvlan-wb` を生成し, `kubectl apply` で適用します。
- **再実行対応**: ロールの再実行時に既存ファイルを再利用し, 冪等性を確保しています。

### 依存ロール

このロールは以下のロールが事前に完了していることを前提とします。

- **k8s-common**: 基本的なシステム設定
- **k8s-ctrlplane**: Kubernetes コントロールプレーン構築
- **k8s-multus**: Multus CNI メタプラグイン導入

Whereabouts は Multus を通じて複数ネットワーク機能を提供するため, `k8s_multus_enabled: true` と `k8s_whereabouts_enabled: true` の両方が必要です。

### 有効化条件

本ロールのコア処理 (`config-whereabouts.yml`) は以下の条件をすべて満たす場合にのみ実行されます。

1. `k8s_multus_enabled: true` (Multus が有効)
2. `k8s_whereabouts_enabled: true` (Whereabouts が有効)
3. IPv4 範囲 (`k8s_whereabouts_ipv4_range_start` および `k8s_whereabouts_ipv4_range_end`) が定義されている, または
4. IPv6 範囲 (`k8s_whereabouts_ipv6_range_start` および `k8s_whereabouts_ipv6_range_end`) が定義されている

すべての条件が満たされない場合, 本ロールは初期化のみを実行し, Whereabouts の導入は実施されません。

## 主な処理

本ロールは tasks/main.yml から task 群を呼び出し, 設定適用と検証を実施します。

## 前提条件

本ロールは以下の条件下で動作します。

- **対象 OS**: Ubuntu 24.04, RHEL 9 系 (AlmaLinux 9.6 を想定)
- **Ansible**: 2.15 以降
- **Kubernetes**: 1.27 以降 (k8s-ctrlplane で構築されたクラスタ)
- **Helm**: 3.10 以降 (ターゲットノードに導入済みまたはコントロール側から実行可能)
- **kubectl**: 対象クラスタへのアクセス権限
- **Multus**: `k8s_multus_enabled: true` で事前導入済み
- **IPv4/IPv6 範囲**: NAD に適用する IP アドレス範囲が事前に `host_vars` または `group_vars` で定義されていること

### 実行順序

本ロールは以下のロールが事前に実行されていることを前提とします。

1. `k8s-common`: 基本的なシステム設定 (パッケージインストール, ネットワーク設定など)
2. `k8s-ctrlplane`: Kubernetes コントロールプレーン構築 (kubeadm による初期化)
3. `k8s-multus`: Multus CNI メタプラグイン導入

これらが完了した後, 本ロール (`k8s-whereabouts`) を実行してください。

## 実行方法

実行者は制御ホストで以下のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts site.yml --tags "k8s-whereabouts"
```

## 主要変数

本ロールで利用される主要な変数を以下のカテゴリに分類します。

### Kubernetes API 接続設定

これらの変数は kube-apiserver の起動待機処理で使用されます。

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_ctrlplane_endpoint` | 各ホストの `host_vars` で指定 | Control Plane API の広告アドレス (IPv4/IPv6)。待機処理で使用。|
| `k8s_api_wait_host` | `"{{ k8s_ctrlplane_endpoint }}"` | kube-apiserver の待ち合わせ先ホスト名/IP アドレス。 |
| `k8s_api_wait_port` | `"{{ k8s_ctrlplane_port }}"` | kube-apiserver の待ち合わせ先ポート番号。既定: `6443` |
| `k8s_api_wait_timeout` | `600` | kube-apiserver 待ち合わせ時間 (単位: 秒)。 |
| `k8s_api_wait_delay` | `2` | kube-apiserver 待ち合わせ開始の遅延時間 (単位: 秒)。 |
| `k8s_api_wait_sleep` | `1` | kube-apiserver 待機間隔 (単位: 秒)。 |
| `k8s_api_wait_delegate_to` | `"localhost"` | kube-apiserver 待ち合わせ実行ホスト (制御側)。 |

### 有効化フラグ

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_multus_enabled` | `false` | Multus が有効な場合のみ Whereabouts を導入します。 |
| `k8s_whereabouts_enabled` | `false` | Whereabouts のすべてのタスク実行を制御します。 |

### ディレクトリパス設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_kubeadm_config_store` | `{{ ansible_home_dir }}/kubeadm` | Whereabouts 設定ファイルのルートディレクトリ。`{{ ansible_home_dir }}` は ansible ログインユーザ (`ansible_user` 変数, 既定: `"ansible"`) の home ディレクトリを展開したパス。 |
| `k8s_whereabouts_config_dir` | `{{ k8s_kubeadm_config_store }}/whereabouts` | NAD 設定ファイルの生成先ディレクトリ。 |

### Whereabouts Helm チャート設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_whereabouts_version` | `0.9.2` | Whereabouts のベースバージョン。 |
| `k8s_whereabouts_helm_chart_version` | `{{ k8s_whereabouts_version }}` | Whereabouts Helm チャートバージョン。 |
| `k8s_whereabouts_image_version` | `{{ k8s_whereabouts_version }}` | Whereabouts コンテナイメージのタグ。テンプレート内で参照。 |
| `k8s_whereabouts_chart_url` | `oci://ghcr.io/k8snetworkplumbingwg/whereabouts-chart` | Whereabouts Helm チャートの OCI URL。 |

### ネットワーク範囲設定 (NAD 生成用)

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_whereabouts_ipv4_range_start` | `""` | NAD で使用する IPv4 プール範囲の開始アドレス。設定必須 (IPv4 使用時)。 |
| `k8s_whereabouts_ipv4_range_end` | `""` | NAD で使用する IPv4 プール範囲の終了アドレス。設定必須 (IPv4 使用時)。 |
| `k8s_whereabouts_ipv6_range_start` | `""` | NAD で使用する IPv6 プール範囲の開始アドレス。設定必須 (IPv6 使用時)。 |
| `k8s_whereabouts_ipv6_range_end` | `""` | NAD で使用する IPv6 プール範囲の終了アドレス。設定必須 (IPv6 使用時)。 |

### ネットワークおよびインタフェース設定

以下の変数は `vars/all-config.yml` と `group_vars/all/all.yml` から読み込まれ, NAD テンプレート生成に利用されます。

| 変数名 | 由来 | 説明 |
| --- | --- | --- |
| `network_ipv4_cidr` | `vars/all-config.yml` | NAD で使用する IPv4 CIDR (例: `10.0.0.0/16`)。 |
| `network_ipv6_cidr` | `vars/all-config.yml` | NAD で使用する IPv6 CIDR (例: `fd00::/64`)。 |
| `mgmt_nic` | `group_vars/all/all.yml` | NAD の `master` インタフェース名。既定: `ens160` |

## テンプレートと生成ファイル

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `templates/ipvlan-wb-nad.yml.j2` | `{{ k8s_whereabouts_config_dir }}/ipvlan-wb-nad.yml` (既定: `~/kubeadm/whereabouts/ipvlan-wb-nad.yml`) | Whereabouts + IPvLAN 用 Network Attachment Definition。 |

## 実行フロー

本ロールは以下の順序で処理を実行します:

1. **パラメータおよび設定情報の読み込み** (`load-params.yml`): OS 別パッケージ定義, Kubernetes クラスタ共通変数, ホスト固有変数を読み込みます。
2. **パッケージの確認** (`package.yml`): 将来の拡張用プレースホルダです。
3. **ディレクトリ構造の作成** (`directory.yml`): Whereabouts 用の設定ディレクトリを作成します。
4. **ユーザ・グループおよびサービス設定** (`user_group.yml`, `service.yml`): 将来の拡張用プレースホルダです。
5. **Whereabouts 導入と NAD 適用** (`config-whereabouts.yml`): kube-apiserver 待機後, Helm チャート導入と NAD を適用します。

### パラメータおよび設定情報の読み込み

`load-params.yml` を実行し, 以下の情報を読み込みます。

- **OS 別パッケージ定義**: `vars/packages-ubuntu.yml`, `vars/packages-rhel.yml`
- **Kubernetes クラスタ共通変数**: `vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`
- **ホスト固有変数**: `host_vars/` からの読み込み

これらの変数は以降の処理で NAD テンプレート生成やネットワーク設定に利用されます。

### パッケージの確認

`package.yml` を読み込みます。現状ではプレースホルダであり, 必要なパッケージは `k8s-common` で既にインストール済みです。

### ディレクトリ構造の作成

`directory.yml` が以下のディレクトリを作成します。

- **メインディレクトリ**: `{{ k8s_kubeadm_config_store }}/whereabouts` (既定: `~/kubeadm/whereabouts` )
- **NAD 設定ファイルの保存先**: `{{ k8s_whereabouts_config_dir }}/` (既定: `~/kubeadm/whereabouts/`)

### ユーザ・グループおよびサービス設定

`user_group.yml` および `service.yml` を読み込みます。現状ではプレースホルダですが, 今後の拡張で Whereabouts 専用ユーザやサービス単位の管理に対応する予定です。

### Whereabouts 導入と NAD 適用

本処理は以下の条件をすべて満たす場合に実行されます。

**実行条件:**
- `k8s_multus_enabled: true` (Multus が有効)
- `k8s_whereabouts_enabled: true` (Whereabouts が有効)
- IPアドレス範囲が定義されている場合:
  - IPv4 範囲 (`k8s_whereabouts_ipv4_range_start` および `k8s_whereabouts_ipv4_range_end`) が定義されている, または,
  - IPv6 範囲 (`k8s_whereabouts_ipv6_range_start` および `k8s_whereabouts_ipv6_range_end`) が定義されている

**処理手順:**

1. **kube-apiserver 待機**: 変数 `k8s_ctrlplane_endpoint`, `k8s_api_wait_port` などを使って, Kubernetes API サーバの起動を確認します。
2. **Helm チャート導入**: `helm upgrade --install` コマンドで OCI URL `oci://ghcr.io/k8snetworkplumbingwg/whereabouts-chart` から Whereabouts Helm チャート (版: `{{ k8s_whereabouts_helm_chart_version }}`) をクラスタに導入します。
3. **NAD テンプレート生成**: Jinja2 テンプレート `templates/ipvlan-wb-nad.yml.j2` を変数で展開し, ファイル `{{ k8s_whereabouts_config_dir }}/ipvlan-wb-nad.yml` (規定値: `~/kubeadm/whereabouts/ipvlan-wb-nad.yml`) を生成します。
4. **NAD 適用**: 生成した YAML ファイルを `kubectl apply -f` で Kubernetes クラスタに適用します。

すべての条件が満たされない場合, 本処理はスキップされ, 1～4 の初期化のみが実行されます。

#### NAD テンプレート生成

テンプレート `templates/ipvlan-wb-nad.yml.j2` は以下の情報から NAD を生成します。

- **IPAM プラグイン**: `whereabouts`
- **マスタインタフェース**: `{{ mgmt_nic }}` (既定: `ens160`)
- **ネットワーク**: `{{ network_ipv4_cidr }}`, `{{ network_ipv6_cidr }}` (from `vars/all-config.yml`)
- **IPv4 プール**: `{{ k8s_whereabouts_ipv4_range_start }}`～`{{ k8s_whereabouts_ipv4_range_end }}`
- **IPv6 プール**: `{{ k8s_whereabouts_ipv6_range_start }}`～`{{ k8s_whereabouts_ipv6_range_end }}` (IPv6 有効時)
- **デバイス種別**: IPvLAN (L3 モード)

## 検証ポイント

本ロール実行後に Whereabouts が正しく導入されたことを確認するための検証ポイントを以下に示します。

### 必須確認事項

#### 1. Whereabouts Helm チャートのインストール確認

```bash
helm list -n kube-system
```

**期待される出力例:**

```
NAME          NAMESPACE    REVISION    UPDATED                                 STATUS      CHART
whereabouts   kube-system  1           2025-03-07 10:00:00 +0900 JST          deployed    whereabouts-0.9.2
```

- `NAME` 列に `whereabouts` が存在することを確認します。
- `NAMESPACE` 列が `kube-system` であることを確認します。
- `STATUS` 列が `deployed` であることを確認します。
- `CHART` 列のバージョンが設定値 (`k8s_whereabouts_helm_chart_version`) と一致することを確認します。

#### 2. Whereabouts デプロイメントの動作確認

```bash
kubectl get deployment -n kube-system whereabouts
```

**期待される出力例:**

```
NAME          READY   UP-TO-DATE   AVAILABLE   AGE
whereabouts   1/1     1            1           2d
```

- `READY` 列が `1/1` であること (Pod が起動していること) を確認します。
- `UP-TO-DATE` 列と `AVAILABLE` 列が `1` であることを確認します。

#### 3. NAD 登録確認

```bash
kubectl get networkattachmentdefinition -A
```

**期待される出力例:**

```
NAMESPACE      NAME           AGE
kube-system    ipvlan-wb      2d
```

または詳細確認:

```bash
kubectl get networkattachmentdefinition ipvlan-wb -o yaml
```

NAD の詳細設定 (IPAM, マスタインタフェース, IP プール範囲など) を確認します。

#### 4. NAD 設定ファイルの存在確認

コントロールプレーンノード上で以下を確認します。

```bash
ls -la "{{ k8s_whereabouts_config_dir }}/ipvlan-wb-nad.yml"
# 例: ~/kubeadm/whereabouts/ipvlan-wb-nad.yml
```

**期待される出力例:**

```text
-rw-r--r-- 1 ansible ansible 1240 Mar  7 10:05 /home/ansible/kubeadm/whereabouts/ipvlan-wb-nad.yml
```

確認項目:
- 先頭が `-` であり, 通常ファイルとして作成されていること。
- ファイルパスが `.../kubeadm/whereabouts/ipvlan-wb-nad.yml` であること。
- 所有者/グループが `ansible:ansible` (または運用で想定した実行ユーザ) であること。

続けて, 内容を確認します。

```bash
grep -E '"type":\s*"whereabouts"|"range_start"|"range_end"|"master"' "{{ k8s_whereabouts_config_dir }}/ipvlan-wb-nad.yml"
```

**期待される出力例 (抜粋):**

```text
"master": "ens160",
"type": "whereabouts",
"range_start": "10.100.1.0",
"range_end": "10.100.254.255"
```

確認項目:
- `"type": "whereabouts"` が含まれること。
- `"master"` が想定インタフェース (例: `ens160`) と一致すること。
- `"range_start"`/`"range_end"` が設定値と一致すること。

### オプション確認事項

#### 5. Whereabouts Pod の詳細確認

```bash
kubectl describe pod -n kube-system -l app=whereabouts
```

`kubectl describe pod` の出力に含まれる `Limits`/`Requests`, `Environment`, `Mounts`, `Events` を確認します。

**期待される出力例 (抜粋):**

```text
Name:           whereabouts-7d9c7f8b9c-abcde
Namespace:      kube-system
Containers:
  whereabouts:
    Limits:
      cpu:     100m
      memory:  128Mi
    Requests:
      cpu:      50m
      memory:   64Mi
    Environment:
      KUBERNETES_SERVICE_HOST: 10.96.0.1
    Mounts:
      /etc/cni/net.d from cni-net-dir (rw)
Events:
  Type    Reason     Age   From               Message
  Normal  Pulled     2m    kubelet            Container image already present on machine
```

確認項目:
- `Namespace` が `kube-system` であること。
- `Environment` セクションに環境変数が表示されること。
- `Mounts` セクションにマウント先パス (例: `/etc/cni/net.d`) が表示されること。
- `Events` に継続的な `Warning` が出ていないこと。

必要に応じて, 以下のコマンドでコンテナ定義の環境変数とボリュームマウントを直接確認します。

```bash
kubectl get pod -n kube-system -l app=whereabouts -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{.spec.containers[*].env[*].name}{"\n"}{.spec.containers[*].volumeMounts[*].mountPath}{"\n\n"}{end}'
```

**期待される出力例:**

```text
whereabouts-7d9c7f8b9c-abcde
KUBERNETES_SERVICE_HOST KUBERNETES_SERVICE_PORT
/etc/cni/net.d /var/run/secrets/kubernetes.io/serviceaccount
```

確認項目:
- 1行目に Pod 名が表示されること。
- 2行目に環境変数名が表示されること。
- 3行目にマウントパスが表示されること。

#### 6. NAD の詳細内容確認

```bash
kubectl get networkattachmentdefinition ipvlan-wb -n kube-system -o jsonpath='{.spec}'
```

確認項目:
- `type` が `ipvlan` であること。
- `ipam.type` が `whereabouts` であること。
- `master` が期待のインタフェース (例: `ens160`) であること。

#### 7. ログの確認

```bash
kubectl logs -n kube-system -l app=whereabouts --tail=20
```

エラーログがないことを確認します。

#### 8. Pod 間通信の確認 (実通信)

NAD (`ipvlan-wb`) を付与した 2 つの Pod を起動し, 追加ネットワーク経由で疎通確認を行います。

```bash
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: wb-test-a
  annotations:
    k8s.v1.cni.cncf.io/networks: kube-system/ipvlan-wb
spec:
  containers:
    - name: toolbox
      image: alpine:latest
      command: ["/bin/sh", "-c", "apk add --no-cache iproute2 && sleep infinity"]
---
apiVersion: v1
kind: Pod
metadata:
  name: wb-test-b
  annotations:
    k8s.v1.cni.cncf.io/networks: kube-system/ipvlan-wb
spec:
  containers:
    - name: toolbox
      image: alpine:latest
      command: ["/bin/sh", "-c", "apk add --no-cache iproute2 && sleep infinity"]
EOF
```

```bash
kubectl wait --for=condition=Ready pod/wb-test-a pod/wb-test-b --timeout=180s
```

**期待される出力例:**

```text
pod/wb-test-a condition met
pod/wb-test-b condition met
```

確認項目:
- 両 Pod について `condition met` と表示されること。

次に, `wb-test-b` の `net1` アドレスを取得し, `wb-test-a` から ping します。

**IPv4 疎通確認:**

```bash
WB_TEST_B_IP=$(kubectl exec wb-test-b -- sh -c "ip -o -4 addr show dev net1 | awk '{print \$4}' | cut -d/ -f1")
echo "wb-test-b IPv4 address: $WB_TEST_B_IP"
kubectl exec wb-test-a -- ping -c 3 "$WB_TEST_B_IP"
```

**期待される出力例:**

```text
wb-test-b IPv4 address: 192.168.20.51
PING 192.168.20.51 (192.168.20.51): 56 data bytes
64 bytes from 192.168.20.51: seq=0 ttl=64 time=0.856 ms
64 bytes from 192.168.20.51: seq=1 ttl=64 time=0.170 ms
64 bytes from 192.168.20.51: seq=2 ttl=64 time=0.178 ms

--- 192.168.20.51 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.170/0.401/0.856 ms
```

確認項目:
- 1行目に `wb-test-b IPv4 address:` の後にIPv4アドレス（例: `192.168.20.51`）が表示されること。
- `ping statistics` で `0% packet loss` と表示されること。
- `64 bytes from` の後に `wb-test-b` の `net1` IPv4アドレスが表示されること。

**IPv6 疎通確認:**

```bash
WB_TEST_B_IPV6=$(kubectl exec wb-test-b -- sh -c "ip -o -6 addr show dev net1 scope global | awk '{print \$4}' | cut -d/ -f1")
echo "wb-test-b IPv6 address: $WB_TEST_B_IPV6"
kubectl exec wb-test-a -- ping -c 3 "$WB_TEST_B_IPV6"
```

**期待される出力例:**

```text
wb-test-b IPv6 address: fdad:ba50:248b:1:50:5600:100:7b1c
PING fdad:ba50:248b:1:50:5600:100:7b1c (fdad:ba50:248b:1:50:5600:100:7b1c): 56 data bytes
64 bytes from fdad:ba50:248b:1:50:5600:100:7b1c: seq=0 ttl=64 time=0.667 ms
64 bytes from fdad:ba50:248b:1:50:5600:100:7b1c: seq=1 ttl=64 time=0.182 ms
64 bytes from fdad:ba50:248b:1:50:5600:100:7b1c: seq=2 ttl=64 time=0.166 ms

--- fdad:ba50:248b:1:50:5600:100:7b1c ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.166/0.338/0.667 ms
```

確認項目:
- 1行目に `wb-test-b IPv6 address:` の後にIPv6アドレス（例: `fdad:ba50:248b:1:50:5600:100:7b1c`）が表示されること。
- `ping statistics` で `0% packet loss` と表示されること。
- `64 bytes from` の後に `wb-test-b` の `net1` IPv6アドレスが表示されること。

検証後はテスト Pod を削除します。

```bash
kubectl delete pod wb-test-a wb-test-b --ignore-not-found
```

## トラブルシューティング

本ロール実行時に問題が発生した場合の対応を示します。

### 問題 1: Helm チャート導入失敗 - OCI URL にアクセスできない

**症状:**
```
Error: failed to fetch "oci://ghcr.io/k8snetworkplumbingwg/whereabouts-chart"
```

**原因:**
- インターネット接続がない, または ghcr.io (GitHub Container Registry) にアクセスできない。
- プロキシ設定が不正。

**対応:**
1. インターネット接続を確認します。
2. 次のコマンドでレジストリへのアクセスを確認します。

```bash
curl -I https://ghcr.io
```

3. プロキシが必要な場合は, `helm upgrade --install` コマンドに認証設定を指定します。

### 問題 2: `config-whereabouts.yml` が実行されない

**症状:**
- Whereabouts が導入されない。
- ロール実行時の出力に `config-whereabouts.yml` に関するタスクが表示されない。

**原因:**
- `k8s_multus_enabled: false` または `k8s_whereabouts_enabled: false`
- IPv4/IPv6 範囲が定義されていない。

**対応:**
1. 変数設定を確認します。

```bash
grep -E "k8s_(multus|whereabouts)_enabled" host_vars/*.yml group_vars/all/all.yml
```

2. 有効化フラグを `true` に設定し, IPv4/IPv6 範囲を定義します。

```yaml
# host_vars/k8sctrlplane01.local (例)
k8s_multus_enabled: true
k8s_whereabouts_enabled: true
k8s_whereabouts_ipv4_range_start: "10.100.0.0"
k8s_whereabouts_ipv4_range_end: "10.100.255.255"
```

3. ロールを再実行します。

### 問題 3: NAD の IP プール範囲が不正

**症状:**
```
kubectl get networkattachmentdefinition ipvlan-wb -o yaml
# ipam.range が空, または形式が不正
```

**原因:**
- `k8s_whereabouts_ipv4_range_start` または `k8s_whereabouts_ipv4_range_end` が IP アドレス形式でない。
- `network_ipv4_cidr` が定義されていない。

**対応:**
1. テンプレート生成前に変数を確認します。

```bash
ansible-playbook -i inventory/hosts roles/k8s-whereabouts/main.yml -e "ansible_connection=local" --check
```

2. 変数を修正します。

```yaml
# group_vars/all/all.yml
network_ipv4_cidr: "10.100.0.0/16"

# host_vars/k8sctrlplane01.local
k8s_whereabouts_ipv4_range_start: "10.100.1.0"
k8s_whereabouts_ipv4_range_end: "10.100.254.255"
```

### 問題 4: kube-apiserver 待機がタイムアウト

**症状:**
```
FAILED - RETRYING [config-whereabouts : Wait for kube-apiserver]
```

**原因:**
- kube-apiserver が起動していない。
- `k8s_ctrlplane_endpoint` が不正。
- ファイアウォール設定により通信が遮断されている。

**対応:**
1. kube-apiserver の状態を確認します。

```bash
kubectl get nodes
# または
systemctl status kubelet  # リモートノード上で
```

2. API エンドポイントへの疎通を確認します。

```bash
curl -k https://k8s_ctrlplane_endpoint:6443/api/v1
```

3. 待機タイムアウト値を増加させます。

```yaml
k8s_api_wait_timeout: 1200  # デフォルト 600 から増加
```

### 問題 5: NAD 名前空間が不正

**症状:**
- NAD が異なる名前空間に登録される (例: `default` など)。

**原因:**
- テンプレート `templates/ipvlan-wb-nad.yml.j2` の `metadata.namespace` が不正。

**対応:**

テンプレートを確認し, 名前空間を修正します。

```bash
cat roles/k8s-whereabouts/templates/ipvlan-wb-nad.yml.j2 | grep -A2 "metadata:"
```

編集内容は[NAD の 名前空間 ( namespace ) を変更する手順](#nad-の-名前空間--namespace--を変更する手順)を参照してください。

## 注意事項

### 必須設定項目

- `k8s_multus_enabled: true` と `k8s_whereabouts_enabled: true` の両方が必要です。
- `k8s_whereabouts_ipv4_range_start` / `k8s_whereabouts_ipv4_range_end` を事前に設定してください (IPv4 を使う場合)。
- `k8s_whereabouts_ipv6_range_start` / `k8s_whereabouts_ipv6_range_end` を事前に設定してください (IPv6 を使う場合)。
- IPv4/IPv6 のいずれかが揃っていない場合, `config-whereabouts.yml` は実行されません。

### IPv6 範囲を有効化する手順

IPv6 対応のネットワークを構築する場合, 以下の手順に従います。

1. **変数設定**: 以下の変数を設定ファイル (`host_vars`, `group_vars`) に追加します。

```yaml
k8s_whereabouts_ipv6_range_start: "<IPv6の開始アドレス>"
k8s_whereabouts_ipv6_range_end: "<IPv6の終了アドレス>"
```

例:
```yaml
k8s_whereabouts_ipv6_range_start: "fd00:100::1"
k8s_whereabouts_ipv6_range_end: "fd00:100::ff"
```

2. **ロール再実行**: ロールを再実行して NAD を再生成・再適用します。

```bash
ansible-playbook -i inventory/hosts site.yml --tags=k8s-whereabouts
```

3. **検証**: IPv6 アドレスが付与されていることを確認します。

```bash
kubectl get networkattachmentdefinition ipvlan-wb -o yaml
kubectl run test-pod --image=busybox -- sleep 3600
kubectl exec test-pod -- ip -6 addr
```

### NAD の 名前空間 ( namespace ) を変更する手順

デフォルトでは NAD は `kube-system` 名前空間に新規作成されます。これを別の名前空間に変更する場合, 以下の手順に従います。

1. **テンプレート確認**: テンプレートの現在の namespace を確認します。

```bash
grep "namespace:" roles/k8s-whereabouts/templates/ipvlan-wb-nad.yml.j2
```

2. **編集**: テンプレート内の `metadata.namespace` を変更します。

例: `default` に変更する場合

```yaml
metadata:
  name: ipvlan-wb
  namespace: default
```

3. **既存 NAD 削除**: 旧 namespace の NAD を削除します (必要に応じて)。

```bash
kubectl delete networkattachmentdefinition ipvlan-wb -n kube-system
```

4. **ロール再実行**: NAD を再生成・再適用します。

```bash
ansible-playbook -i inventory/hosts site.yml --tags=k8s-whereabouts
```

5. **参照側更新**: Pod や Deployment の `k8s.v1.cni.cncf.io/networks` アノテーションが namespace 指定を含む場合は,合わせて更新します。

```yaml
metadata:
  annotations:
    k8s.v1.cni.cncf.io/networks: "default/ipvlan-wb"  # namespace/nad-name
```

## 参考資料

### 公式ドキュメント

- Whereabouts CNI: https://github.com/k8snetworkplumbingwg/whereabouts
- Multus CNI: https://github.com/k8snetworkplumbingwg/multus-cni
