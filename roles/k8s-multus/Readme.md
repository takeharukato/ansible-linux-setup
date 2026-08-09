# k8s-multus ロール

本ロールは, Kubernetes 上で動作する Pod から複数の CNI プラグインを同時に使用できるようにするメタ CNI プラグインである [Multus](https://github.com/k8snetworkplumbingwg/multus-cni) を導入します。

## 目次

- [k8s-multus ロール](#k8s-multus-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
    - [ロールの目的](#ロールの目的)
    - [前提ロール](#前提ロール)
    - [基本仕様](#基本仕様)
  - [導入方式](#導入方式)
    - [Helm 方式 (推奨, 既定)](#helm-方式-推奨-既定)
    - [kubectl apply 方式](#kubectl-apply-方式)
    - [導入方式の切り替え](#導入方式の切り替え)
    - [Multusのインストール形式](#multusのインストール形式)
    - [Cilium との共存](#cilium-との共存)
    - [NetworkAttachmentDefinition (NAD) の使用](#networkattachmentdefinition-nad-の使用)
    - [セカンダリネットワークのルーティング](#セカンダリネットワークのルーティング)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
    - [基本設定](#基本設定)
    - [Helm 設定](#helm-設定)
    - [コンテナイメージ設定](#コンテナイメージ設定)
    - [CNI 設定](#cni-設定)
    - [kubectl apply 設定](#kubectl-apply-設定)
    - [API 待機設定](#api-待機設定)
    - [オペレータユーザ設定](#オペレータユーザ設定)
    - [Pod アドレス収集ツール設定](#pod-アドレス収集ツール設定)
    - [共通変数参照](#共通変数参照)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
    - [Helm Chart 構成](#helm-chart-構成)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [1. kube-apiserver の応答確認](#1-kube-apiserver-の応答確認)
    - [2. Multus DaemonSet の起動確認](#2-multus-daemonset-の起動確認)
    - [3. Helm Release の確認 (Helm 方式使用時)](#3-helm-release-の確認-helm-方式使用時)
    - [4. NetworkAttachmentDefinition CRD の確認](#4-networkattachmentdefinition-crd-の確認)
    - [5. RBAC リソースの確認](#5-rbac-リソースの確認)
    - [6. CNI 設定ファイルの確認](#6-cni-設定ファイルの確認)
    - [7. Multus 動作確認 (テストポッド起動)](#7-multus-動作確認-テストポッド起動)
      - [7.1. 事前準備 (NetworkAttachmentDefinitionの作成)](#71-事前準備-networkattachmentdefinitionの作成)
      - [7.2. テストポッドの起動](#72-テストポッドの起動)
      - [7.3. Pod 内のネットワークインターフェース確認](#73-pod-内のネットワークインターフェース確認)
      - [7.4 テストポッドの削除](#74-テストポッドの削除)
    - [8. Multus ログの確認](#8-multus-ログの確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. Multus DaemonSet が起動しない](#1-multus-daemonset-が起動しない)
    - [2. NetworkAttachmentDefinition (NAD) が認識されない](#2-networkattachmentdefinition-nad-が認識されない)
    - [3. Pod にセカンダリネットワークインターフェースがアタッチされない](#3-pod-にセカンダリネットワークインターフェースがアタッチされない)
    - [4. Helm Release が失敗する](#4-helm-release-が失敗する)
    - [5. kube-apiserver に接続できない](#5-kube-apiserver-に接続できない)
  - [注意事項](#注意事項)
  - [付録](#付録)
    - [Pod アドレス収集補助スクリプト](#pod-アドレス収集補助スクリプト)
    - [スクリプト配置](#スクリプト配置)
    - [コマンドライン仕様](#コマンドライン仕様)
    - [共通オプション](#共通オプション)
    - [実行時の情報表示](#実行時の情報表示)
    - [実行例](#実行例)
      - [例1: 全 Pod のアドレス情報を表示](#例1-全-pod-のアドレス情報を表示)
      - [例2: 特定名前空間だけを対象にする](#例2-特定名前空間だけを対象にする)
      - [例3: ラベルセレクタで Multus Pod を絞り込む](#例3-ラベルセレクタで-multus-pod-を絞り込む)
      - [例4: 警告を検知したら失敗させる](#例4-警告を検知したら失敗させる)
    - [シェル補完機能](#シェル補完機能)
      - [補完機能の有効化設定](#補完機能の有効化設定)
      - [補完ファイル配置先](#補完ファイル配置先)
      - [補完機能の使用方法](#補完機能の使用方法)
      - [補完の動作](#補完の動作)
      - [補完機能のトラブルシューティング](#補完機能のトラブルシューティング)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)
    - [関連ロール](#関連ロール)

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
| サービスアカウント (Service Account) | - | 自動処理中でサービスを呼び出す側のプログラムを識別するための識別情報。 Kubernetesでは, 人間以外の実体をKubernetesクラスタ内で一意に識別するために用いられるアカウントのことを指す。 アプリケーションPod, システムコンポーネント, および, Kubernetesクラスター内外の実体に紐づけられたServiceAccountの認証情報を通して, これらの実体を互いに識別する。 |
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
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
| ネットワーク | - | 機器同士を接続してデータをやり取りする仕組み。 |
| プロトコル | - | 通信やデータ交換の手順を定めた取り決め。 |
| ディレクトリ | - | ファイルを階層的に整理するための入れ物。 |
| ログ | - | 処理の結果や状態を時系列で記録した情報。 |
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
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Custom Resource Definition | CRD | Kubernetes APIを拡張してユーザ独自のリソース種別を定義する仕組み。 |
| Role-Based Access Control | RBAC | ユーザやサービスアカウントが実行可能な操作を役割(Role)で制限する仕組み。 |
| Service Account | - | Kubernetes内部でPodが他のリソースにアクセスする際に用いる仮想的なアカウント。 |
| ClusterRole | - | Kubernetesクラスタ全体に適用される権限の集合。 |
| ClusterRoleBinding | - | ClusterRoleをユーザやサービスアカウントに紐付ける仕組み。 |
| Role | - | 特定の名前空間内で有効な権限の集合。 |
| RoleBinding | - | Roleをユーザやサービスアカウントに紐付ける仕組み。 |
| 名前空間 ( namespace ) | - | Kubernetes内部でリソースを論理的に分離する単位。 |
| ポッド ( Pod ) | - | Kubernetes上で動作するコンテナの最小単位。 |
| デーモンセット ( DaemonSet ) | - | Kubernetesクラスタ内の全ノード(または指定した一部のノード)で必ずPodを1つずつ起動させるリソース。 |
| デプロイ ( Deploy ) | - | 機能や設定を実行環境へ展開し, 利用可能な状態にする作業。 |
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
| Internet Protocol | IP | ネットワーク上で宛先を識別し, データを届けるための通信手順。 |
| IP Address Management | IPAM | IP アドレス割当を管理する仕組み。 |
| Red Hat Enterprise Linux | RHEL | Red Hatが提供する企業向けLinuxディストリビューション。 |
| User Identifier | UID | 利用者を識別する番号。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| Yet Another Markup Language | YAML | 設定ファイル形式です。 |
| Network Attachment Definition | NAD | 追加ネットワーク接続設定を定義する Kubernetes の リソース。 |
| Layer 2 | L2 | 同一ネットワーク内で装置間転送を扱う通信層。 |
| Python | - | スクリプティングやアプリケーション開発を手早く実施するために用いられる高水準プログラミング言語の一種。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `cat` | - | ファイル内容を標準出力へ表示するコマンド。 |
| `curl` | - | URL を指定してデータ送受信を行うコマンド。 |
| `helm` | - | Kubernetesアプリケーションのパッケージ管理ツール。Chart形式でアプリケーションを配布, インストールします。 |
| ipコマンド | - | ネットワーク設定や経路情報の確認, 変更を行うコマンド。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| makeコマンド | make | Makefile に定義された処理を実行するコマンド。 |
| `source` | - | シェル設定ファイルやスクリプトを現在シェルへ読み込むコマンド。 |
| `systemctl` | - | systemd 管理下のサービスを起動, 停止, 状態確認するコマンド。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
| コード | - | 処理内容を記述した文字列。 |
| サービス | - | 機能を利用者や他システムへ提供する仕組み。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| ブロック | - | ひとかたまりとして扱う処理単位や領域。 |
| ポート | - | 通信の出入口を識別する番号または接点。 |
| ローカル | - | 実行中の装置や同一環境の内部。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |

## 概要

本ロールは, Kubernetes 上で動作する Pod から複数の CNI プラグインを同時に使用できるようにするメタ CNI プラグインである [Multus](https://github.com/k8snetworkplumbingwg/multus-cni) を導入します。

### ロールの目的

本ロールは Kubernetes コントロールプレーンノード上に Multus CNI を導入します。Multus は複数の CNI プラグインを同時に使用可能にするメタ CNI プラグインで, Pod に複数のネットワークインターフェースをアタッチできるようにします。

`k8s-common` および `k8s-ctrlplane` で構築された Kubernetes クラスタに対して, Multus を追加導入することで, Cilium (プライマリ CNI) に加えて追加のネットワークインターフェース (ipvlan, macvlan, bridge 等) を Pod にアタッチ可能になります。

### 前提ロール

本ロールは以下のロールが実行済みであることを前提とします:

- `k8s-common`: Kubernetes クラスタの基本設定
- `k8s-ctrlplane`: コントロールプレーンノードの構築 (Cilium CNI 導入済み)

### 基本仕様

- **デフォルト導入方式**: Helm Chart (推奨)
- **代替導入方式**: kubectl apply (後方互換性のため提供)
- **Multus タイプ**: thin インストール (軽量版, 既定)
- **配置対象**: すべての Kubernetes ノード (DaemonSet)
- **再実行対応**: 可 (冪等性を保証)

## 導入方式

本ロールでは Multus の導入に2つの方式を提供しています。既定では **Helm 方式** を使用します。

### Helm 方式 (推奨, 既定)

**メリット**:

- バージョン管理が容易 (Helm Release として管理される)
- values ファイルでの設定変更が簡単
- アップグレード, ロールバックが容易

**使用方法**:

```yaml
k8s_multus_kubectl_apply_enabled: false  # 既定値
```

**確認方法**:

```bash
kubectl get daemonset -n kube-system
helm list -n kube-system
```

### kubectl apply 方式

**メリット**:

- 既存環境との互換性維持
- Helm 不要 (kubectl のみで導入可能)
- シンプルな導入手順

**使用方法**:

```yaml
k8s_multus_kubectl_apply_enabled: true
```

**確認方法**:

```bash
kubectl get daemonset -n kube-system
```

### 導入方式の切り替え

Helm 方式から kubectl apply 方式, またはその逆に切り替える場合は, 既存リソースをクリーンアップしてから再導入します:

```yaml
k8s_multus_cleanup_resources: true  # 既存リソースを削除
k8s_multus_kubectl_apply_enabled: false  # または true
```

### Multusのインストール形式

Multus には2つのインストールモードがあります:

- **thin インストール** (既定): Multus 自身は最小限の機能のみを持ち, 実際の CNI プラグイン (ipvlan, macvlan, bridge 等) は別途ノード上に配置されている必要があります。本ロールでは thin インストールを使用します。
- **thick インストール**: Multus コンテナ内に主要な CNI プラグインバイナリをバンドルし, ノード上に CNI プラグインが存在しなくても動作可能にします。

thin インストールを使用する場合は, 各ノードの `/opt/cni/bin/` に必要な CNI プラグインバイナリが配置されていることを確認してください (通常は containerd や kubelet のインストール時に配置されます)。

### Cilium との共存

本ロールでは Cilium をプライマリ CNI として使用し, Multus をメタ CNI として併用します。この構成では:

- **eth0** (プライマリインターフェース): Cilium が管理し, Pod 間通信, Service 通信, NetworkPolicy 等に使用されます。
- **net1, net2, ...** (セカンダリインターフェース): Multus が NetworkAttachmentDefinition (NAD) で定義された CNI プラグイン (ipvlan, macvlan, bridge 等) を呼び出してアタッチします。

セカンダリネットワークインターフェースは通常, レガシーアプリケーションの L2 通信要件, マルチテナント環境でのネットワーク分離, 専用ネットワークへの直接接続等に使用されます。

### NetworkAttachmentDefinition (NAD) の使用

NAD の作成と使用方法については, 以下のロールを参照してください:

- `k8s-whereabouts`: Multus 用の IPAM (IP Address Management) プラグインである Whereabouts と NAD の導入例が記載されています。

NAD を定義することで, Pod に対して以下のような Annotation を付与してセカンダリネットワークインターフェースをアタッチできます:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: example-pod
  annotations:
    k8s.v1.cni.cncf.io/networks: <NAMESPACE>/<NAD_NAME>
spec:
  containers:
  - name: example-container
    image: busybox
```

### セカンダリネットワークのルーティング

`templates/app-pod.yml.j2` のコメントに記載されている通り, セカンダリネットワークインターフェース経由で通信を行う場合は, 送信元 IP アドレス (`src`) を明示的に指定することで通信経路を安定化できます:

```bash
ip route add <DESTINATION_NETWORK> via <GATEWAY> dev net1 src <NET1_IP>
```

この設定により, カーネルが送信元 IP アドレスを自動選択する際に `net1` の IP アドレスを使用するようになり, セカンダリネットワーク経由の通信が確実に行われます。

## 前提条件

本ロールを実行する前に, 以下の条件が満たされている必要があります:

- **対象ノード**: Kubernetes コントロールプレーンノード (`k8s-ctrlplane` ロール実行済み)
- **Kubernetes バージョン**: 1.24 以降 (kubeadm で構築されたクラスタ)
- **プライマリ CNI**: Cilium が導入済みであること
- **必要なツール**:
  - kubectl: Kubernetes クラスタ操作用 (/usr/local/bin/kubectl)
  - helm: Helm Chart 導入用 (Helm 方式使用時, 既定で有効)
- **kube-apiserver**: 稼働中で応答可能であること
- **管理者権限**: kubectl 実行に /etc/kubernetes/admin.conf を使用する場合は, root 権限が必要 (sudoコマンドによるコマンド実行が可能であることが必要)
- **ネットワーク接続**: コンテナイメージ取得のためのインターネット接続 (または内部レジストリへの接続)

## 実行方法

実行者は制御ホストで以下のいずれかを実行します。

```bash
make run_k8s_multus

ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml --tags "k8s-multus"
ansible-playbook -i inventory/hosts site.yml --tags "k8s-multus"
```

## 主要変数

### 基本設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_multus_enabled` | `true` | Multus 導入を有効化する可否。`false` にするとロール全体をスキップします。 |
| `k8s_multus_cleanup_resources` | `false` | 既存の Multus リソースを削除する可否。導入方式の切り替え時に使用します。 |
| `k8s_node_setup_tools_prefix` | `"/opt/k8snodes"` | ノード向け補助スクリプト格納先ディレクトリのプレフィックス。 |
| `k8s_node_setup_tools_dir` | `"{{ k8s_node_setup_tools_prefix }}/sbin"` | ノード向け補助スクリプト格納先ディレクトリ。 |

### Helm 設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_multus_kubectl_apply_enabled` | `false` | kubectl apply 方式を有効化する可否。`false` の場合は Helm Chart 方式を使用します。 |
| `k8s_multus_helm_chart_path` | `"/tmp/multus-chart"` | ターゲットホストにコピーする Helm Chart のパス。 |

### コンテナイメージ設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_multus_image_repository` | `"ghcr.io/k8snetworkplumbingwg/multus-cni"` | Multus コンテナイメージのリポジトリ。 |
| `k8s_multus_image_version` | `"v4.2.3"` | Multus コンテナイメージのタグ。 |

### CNI 設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_multus_cni_bin_dir` | `"/opt/cni/bin"` | CNI プラグインバイナリの配置ディレクトリ。 |
| `k8s_multus_cni_conf_dir` | `"/etc/cni/net.d"` | CNI 設定ファイルの配置ディレクトリ。 |

### kubectl apply 設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_multus_daemonset_manifest_url` | `"https://raw.githubusercontent.com/k8snetworkplumbingwg/multus-cni/refs/tags/{{ k8s_multus_version }}/deployments/multus-daemonset.yml"` | kubectl apply 方式で使用する公式マニフェストの URL。 |

### API 待機設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_api_wait_timeout` | `600` | kube-apiserver の応答を待機する最大秒数。 |

### オペレータユーザ設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_operator_user` | `"kube"` | Multus 操作を実行するユーザ名。 |
| `k8s_operator_groups_list` | `"{{ adm_groups }}"` | `k8s_operator_user` に付与するグループ一覧。 |

### Pod アドレス収集ツール設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_collect_pod_ips_completion_enabled` | `true` | `collect-pod-ips.py` 用の bash/zsh 補完ファイルを配置する可否。 |
| `k8s_collect_pod_ips_script_path` | `"{{ k8s_node_setup_tools_dir }}/collect-pod-ips.py"` | Pod アドレス収集ツール本体の配置先。 |
| `k8s_collect_pod_ips_bash_completion_path` | `"/etc/bash_completion.d/collect-pod-ips"` | bash 補完ファイルの配置先。 |
| `k8s_collect_pod_ips_zsh_completion_path_debian` | `"/usr/share/zsh/vendor-completions/_collect-pod-ips"` | Debian/Ubuntu 系での zsh 補完ファイル配置先。 |
| `k8s_collect_pod_ips_zsh_completion_path_rhel` | `"/usr/share/zsh/site-functions/_collect-pod-ips"` | RHEL 系での zsh 補完ファイル配置先。 |
| `k8s_collect_pod_ips_zsh_completion_path` | `"{{ (ansible_facts.os_family == 'Debian') | ternary(k8s_collect_pod_ips_zsh_completion_path_debian, k8s_collect_pod_ips_zsh_completion_path_rhel) }}"` | 実行ホストのディストリビューション差異を吸収した zsh 補完ファイル配置先。 |

### 共通変数参照

以下の変数は `k8s-common` ロールや `group_vars/all/all.yml` で定義されている共通変数を参照します:

- `k8s_multus_k8s_api_endpoint_address`: kube-apiserver のエンドポイントアドレス (既定: `k8s_ctrlplane_endpoint` で指定したアドレス)
- `k8s_multus_k8s_api_endpoint_port`: kube-apiserver のエンドポイントポート (既定: `6443`)

## テンプレートと生成ファイル

本ロールでは以下のテンプレート / ファイルを出力します:
主な展開先ホストは, 対象ホスト(既定) です。

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `multus-values.yml.j2` | `{{ k8s_multus_config_dir }}/multus-values.yml` (既定: `/home/ansible/kubeadm/multus/multus-values.yml`) | Multus CNI の導入オプションを定義し, 追加ネットワーク利用を有効化する Helm values 設定です。 |
| `app-pod.yml.j2` | `{{ k8s_multus_config_dir }}/app-pod.yml` (既定: `/home/ansible/kubeadm/multus/app-pod.yml`) | Multus の複数ネットワーク割当を検証するためのテスト Pod マニフェストです。 |
| `collect-pod-ips.py` | `{{ k8s_collect_pod_ips_script_path }}` (既定: `/opt/k8snodes/sbin/collect-pod-ips.py`) | Pod の割当 IP を収集し, CNI 設定検証や運用確認に利用する補助スクリプトです。 |
| `collect-pod-ips.bash-completion.j2` | `{{ k8s_collect_pod_ips_bash_completion_path }}` (既定: `/etc/bash_completion.d/collect-pod-ips`) | collect-pod-ips コマンドの入力補完を提供し, 運用コマンド入力を効率化する設定です。 |
| `_collect-pod-ips.zsh-completion.j2` | `{{ k8s_collect_pod_ips_zsh_completion_path }}` (既定: Debian/Ubuntu系 `/usr/share/zsh/vendor-completions/_collect-pod-ips`, RHEL系 `/usr/share/zsh/site-functions/_collect-pod-ips`) | collect-pod-ips コマンドの入力補完を提供し, 運用コマンド入力を効率化する設定です。 |

### Helm Chart 構成

`files/multus-chart/` には以下のファイルが含まれています:

| ファイル名 | 説明 |
| --- | --- |
| `Chart.yaml` | Helm Chart のメタデータ (name: multus-cni, version: 4.2.3, appVersion: v4.2.3)。 |
| `values.yaml` | Helm Chart の既定値。namespace, image, serviceAccount, CNI パス, リソース制限等を定義します。 |
| `templates/daemonset.yaml` | Multus DaemonSet の定義。各ノードで Multus コンテナを起動します。 |
| `templates/serviceaccount.yaml` | Multus 用 ServiceAccount の定義。 |
| `templates/clusterrole.yaml` | Multus 用 ClusterRole の定義 (CRD, Pod, NetworkAttachmentDefinition 等へのアクセス権)。 |
| `templates/clusterrolebinding.yaml` | ClusterRole を ServiceAccount に紐付ける ClusterRoleBinding の定義。 |
| `templates/configmap.yaml` | Multus 用 ConfigMap の定義 (CNI 設定等)。 |
| `templates/crd.yaml` | NetworkAttachmentDefinition CRD の定義。 |
| `templates/_helpers.tpl` | Helm テンプレートヘルパー関数。 |

**使用方法**:

1. ロール実行時に `files/multus-chart/` がターゲットホストの `/tmp/multus-chart/` にコピーされます。
2. `templates/multus-values.yml.j2` から `/tmp/multus-values.yml` が生成されます。
3. `helm upgrade --install multus /tmp/multus-chart/ --namespace kube-system --values /tmp/multus-values.yml` でデプロイされます。

**カスタマイズポイント**:

- `templates/multus-values.yml.j2`: コンテナイメージ, CNI パス, ServiceAccount 名等を変更できます。
- `files/multus-chart/values.yaml`: Helm Chart 側の既定値を変更したい場合はこちらを編集します。
- `files/multus-chart/templates/`: リソース定義自体をカスタマイズしたい場合はこちらを編集します。

## 実行フロー

本ロールは以下の手順で Multus CNI を導入します:

1. **パラメータ読み込み** (`load-params.yml`): `vars/config.yml` から設定を読み込みます (現在は placeholder のみ)。
2. **パッケージインストール** (`package.yml`): Pod アドレス収集ツール `collect-pod-ips.py` を `{{ k8s_node_setup_tools_dir }}` 配下へ配置します。`k8s_collect_pod_ips_completion_enabled: true` の場合は, bash/zsh 補完ファイルもあわせて導入します。
3. **ディレクトリ作成** (`directory.yml`): Multus 用の設定ディレクトリを作成します。
4. **ユーザ/グループ作成** (`user_group.yml`): オペレータユーザ (`k8s_operator_user`) の設定を行います (既定では作成しない)。
5. **サービス設定** (`service.yml`): Multus 関連サービスの設定を行います (現在は処理なし, 将来の拡張用)。
6. **既存リソースのクリーンアップ** (`config-cleanup-multus.yml`): `k8s_multus_cleanup_resources: true` の場合, 既存の Multus リソース (DaemonSet, ClusterRole, ClusterRoleBinding, ServiceAccount, ConfigMap, CRD) を削除します。導入方式の切り替え時に使用します。
7. **Multus 導入 (Helm 方式)** (`config-multus.yml`): `k8s_multus_kubectl_apply_enabled: false` (既定) の場合, 以下の手順で Helm Chart を使用して Multus を導入します:
   - **kube-apiserver 応答待機**: `wait_for` モジュールで kube-apiserver (https://{{ k8s_api_wait_host }}:{{ k8s_api_wait_port }}) が応答可能になるまで最大 {{ k8s_api_wait_timeout }} 秒待機します。
   - **Helm Chart コピー**: `files/multus-chart/` をターゲットホストへコピーします。
   - **Helm values 生成**: `templates/multus-values.yml.j2` から values ファイルを生成します。
   - **Helm インストール/アップグレード**: `helm upgrade --install` コマンドで Multus をデプロイします。
8. **Multus 導入 (kubectl apply 方式)** (`config-kubectl-applied-multus.yml`): `k8s_multus_kubectl_apply_enabled: true` の場合, 公式マニフェスト ({{ k8s_multus_daemonset_manifest_url }}) を `kubectl apply` で適用します。
9. **テストポッド用マニフェスト配置** (`directory-multus-test-pod.yml`): Multus 動作確認用のテストポッド定義 (`templates/app-pod.yml.j2`) を `{{ k8s_multus_config_dir }}/app-pod.yml` に配置します。

## 検証ポイント

Multus CNI が正常に導入されたことを確認するため, 以下の手順で段階的に検証します。

### 1. kube-apiserver の応答確認

```bash
kubectl cluster-info
```

**期待される結果**:

```
Kubernetes control plane is running at https://[fdad:ba50:248b:1::41]:6443
CoreDNS is running at https://[fdad:ba50:248b:1::41]:6443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

**確認ポイント**:

- `Kubernetes control plane is running` が表示され, kube-apiserver が正常に応答していること
- API エンドポイントのアドレスとポート番号が正しく表示されること (IPv4 または IPv6)

### 2. Multus DaemonSet の起動確認

```bash
kubectl get daemonset -n kube-system
```

**期待される結果**:

```
NAME             DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR   AGE
kube-multus-ds   3         3         3       3            3           <none>          21h
```

多数のDaemonSetが表示される場合は、その中に `kube-multus-ds` が含まれていることを確認します。

全ノードで Multus Pod が `READY` 状態であることを確認します:

```bash
kubectl get pods -n kube-system -l app=multus
```

**期待される結果**:

```
NAME                   READY   STATUS    RESTARTS      AGE
kube-multus-ds-5jn8r   1/1     Running   2 (21h ago)   21h
kube-multus-ds-c2wbk   1/1     Running   0             20h
kube-multus-ds-cdd95   1/1     Running   3 (20h ago)   20h
```

**確認ポイント**:

- DaemonSet 出力で `DESIRED`, `CURRENT`, `READY`, `UP-TO-DATE`, `AVAILABLE` の値がすべて一致していること (クラスタ内の全ノード数と同じ)
- Pod 一覧で各 Pod の `READY` 列が `1/1` となっていること (コンテナが正常に起動している)
- `STATUS` 列が `Running` となっていること (Pod が稼働中)
- `RESTARTS` は再起動回数を示します (0 が理想的ですが, ノード再起動等で増加することがあります)

### 3. Helm Release の確認 (Helm 方式使用時)

```bash
helm list -n kube-system
```

**期待される結果**:

```
NAME        NAMESPACE    REVISION  UPDATED                                 STATUS    CHART             APP VERSION
multus-cni  kube-system  1         2026-03-06 02:17:20.715233566 +0900 JST deployed  multus-cni-4.2.3  v4.2.3
```

**確認ポイント**:

- `NAME` 列に `multus-cni` (または設定した Helm Release 名) が表示されること
- `STATUS` 列が `deployed` となっていること (正常にデプロイ済み)
- `CHART` 列が `multus-cni-4.2.3` (使用した Chart バージョン) と一致すること
- `APP VERSION` 列が `v4.2.3` (Multus のバージョン) と一致すること

### 4. NetworkAttachmentDefinition CRD の確認

```bash
kubectl get crd network-attachment-definitions.k8s.cni.cncf.io
```

**期待される結果**:

```
NAME                                             CREATED AT
network-attachment-definitions.k8s.cni.cncf.io   2026-03-05T17:17:20Z
```

**確認ポイント**:

- `network-attachment-definitions.k8s.cni.cncf.io` という名前の CRD が存在すること
- この CRD により, NetworkAttachmentDefinition リソースを作成してセカンダリネットワークを定義できるようになります

### 5. RBAC リソースの確認

```bash
kubectl get clusterrole multus
kubectl get clusterrolebinding multus
kubectl get serviceaccount -n kube-system multus
```

**期待される結果**:

ClusterRole:
```
NAME     CREATED AT
multus   2026-03-05T17:17:20Z
```

ClusterRoleBinding:
```
NAME     ROLE                AGE
multus   ClusterRole/multus  21h
```

ServiceAccount:
```
NAME     SECRETS   AGE
multus   0         21h
```

**確認ポイント**:

- `multus` という名前の ClusterRole が存在すること (Multus が必要なリソースへのアクセス権限を定義)
- `multus` という名前の ClusterRoleBinding が存在し, ClusterRole を ServiceAccount に紐付けていること
- `multus` という名前の ServiceAccount が kube-system 名前空間に存在すること (Multus Pod が使用)

### 6. CNI 設定ファイルの確認

各ノードで CNI 設定ディレクトリを確認します:

```bash
sudo ls -l /etc/cni/net.d/
```

**期待される結果**:

Multus の設定ファイル (`00-multus.conf` または `multus.d/multus.kubeconfig`) が配置されていることを確認します。

**確認ポイント**:

- `/etc/cni/net.d/` ディレクトリ内に Multus 関連の設定ファイルが存在すること
- `00-` で始まるファイル名の場合, CNI プラグインの実行順序で最初に呼び出されます (Multus がメタ CNI として機能するため)
- `multus.d/` ディレクトリが存在する場合, その中に `multus.kubeconfig` が配置されていること

### 7. Multus 動作確認 (テストポッド起動)

本節では, テストポッド投入によるMultusの動作確認手順を説明します。

#### 7.1. 事前準備 (NetworkAttachmentDefinitionの作成)

Podを展開する前に, Pod が参照する NetworkAttachmentDefinition `ipvlan-wb` が `default` 名前空間に存在することを確認します:

```bash
kubectl get network-attachment-definition -n default ipvlan-wb
```

`NotFound` になる場合は, 以下の手順でNetworkAttachmentDefinitionを作成します。
例えば, 上記は, WhereaboutsによるIPアドレスの割当てとipvlan を利用する場合は以下のように, NetworkAttachmentDefinitionを作成するためのマニュフェストを生成します。

`ipvlan` の `master` には, **Pod内の `eth0` ではなく, Podが配置されるノード上の実インターフェース名** を指定します。
Pod投入先K8sクラスタのワーカノード上で以下のコマンドを実行し, 実インターフェース名を取得します:

```bash
ip -o route show default | awk '{print $5; exit}'
```

実行結果の例:
```bash
$ ip -o route show default | awk '{print $5; exit}'
ens160
```

上記コマンドの出力結果を以下の`<NODE_PRIMARY_IFNAME>`の部分に指定して, 以下のコマンドを実行し, NetworkAttachmentDefinitionを作成するためのマニュフェストを生成します:
```bash
cat <<'EOF' >/tmp/ipvlan-wb-nad.yml
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: ipvlan-wb
  namespace: default
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "type": "ipvlan",
      "master": "<NODE_PRIMARY_IFNAME>",
      "mode": "l2",
      "ipam": {
        "type": "whereabouts",
        "range": "192.168.20.0/24"
      }
    }
EOF
```

実行例:
```bash
$ cat <<'EOF' >/tmp/ipvlan-wb-nad.yml
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: ipvlan-wb
  namespace: default
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "type": "ipvlan",
      "master": "ens160",
      "mode": "l2",
      "ipam": {
        "type": "whereabouts",
        "range": "192.168.20.0/24"
      }
    }
EOF
```

以下のコマンドにより, 上記で作成したNetworkAttachmentDefinition作成用マニュフェストを適用します:
```bash
kubectl apply -f /tmp/ipvlan-wb-nad.yml
```

実行例:
```bash
$ kubectl apply -f /tmp/ipvlan-wb-nad.yml
networkattachmentdefinition.k8s.cni.cncf.io/ipvlan-wb created
```

#### 7.2. テストポッドの起動

本ロールでは, Multusの動作確認用マニフェスト (`{{ k8s_multus_config_dir }}/app-pod.yml`, 既定は, `/home/ansible/kubeadm/multus/app-pod.yml`) をコントロールプレインノード上に導入します。

Multusの動作確認用マニフェストの内容は以下の通りです:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: demo-net1
  namespace: default
  annotations:
    k8s.v1.cni.cncf.io/networks: |
      [
        { "name": "ipvlan-wb" }
      ]
spec:
  containers:
  - name: app
    image: busybox:1.36
    command: ["/bin/sh","-c","ip addr; echo '---'; ip route; sleep 3600"]
```

以下のコマンドを実行し, 本マニュフェストを適用します:
```bash
kubectl apply -f /home/ansible/kubeadm/multus/app-pod.yml
kubectl wait --for=condition=ready pod/demo-net1 --timeout=60s
```

実行結果の例:
```bash
$ kubectl apply -f app-pod.yml
pod/demo-net1 created
$ kubectl wait --for=condition=ready pod/demo-net1 --timeout=60s
pod/demo-net1 condition met
```

`kubectl wait` がタイムアウトし, `kubectl describe pod demo-net1` に
`failed to lookup master "eth0": Link not found` が表示される場合は,
NAD の `master` がノード実IF名と不一致です。`master` を実IF名へ修正して再適用してください。

#### 7.3. Pod 内のネットワークインターフェース確認

以下のコマンドを実行し, Pod内のネットワークインターフェース情報を確認します:

```bash
kubectl exec demo-net1 -- ip addr show
```

**期待される結果**:

`eth0` (プライマリインターフェース, Cilium) に加えて, `net1` (セカンダリインターフェース, ipvlan) が表示されることを確認します:

```
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
2: net1@net1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue
    link/ether 00:50:56:00:bf:1d brd ff:ff:ff:ff:ff:ff
    inet 192.168.20.50/24 brd 192.168.20.255 scope global net1
       valid_lft forever preferred_lft forever
18: eth0@if19: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue qlen 1000
    link/ether 62:eb:6d:4d:1c:ab brd ff:ff:ff:ff:ff:ff
    inet 10.244.2.43/32 scope global eth0
       valid_lft forever preferred_lft forever
```

**確認ポイント**:

- `lo`: ループバックインターフェース (常に存在)
  - `inet 127.0.0.1/8` が表示されていること
- `net1`: セカンダリネットワークインターフェース (Multus が NetworkAttachmentDefinition に基づいてアタッチ)
  - インターフェース名は NetworkAttachmentDefinition の設定により変わります (net1, net2, ... など)
  - `<BROADCAST,MULTICAST,UP,LOWER_UP>` のフラグが表示されていること
  - IP アドレスが割り当てられていること (上記例では `192.168.20.50/24`)
  - ブロードキャストアドレスが表示されていること (上記例では `192.168.20.255`)
- `eth0`: プライマリネットワークインターフェース (Cilium が管理, Pod 間通信や Service 通信に使用)
  - `<BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN>` のフラグが表示されていること
  - IP アドレスが割り当てられていること (通常は /32, 上記例では `10.244.2.43/32`)
  - インターフェース番号は環境により変わります (上記例では 18)

**ルーティング確認**:

```bash
kubectl exec demo-net1 -- ip route show
```

**期待される結果**:

プライマリインターフェース (`eth0`) がデフォルトゲートウェイとして設定され, セカンダリインターフェース (`net1`) 用のルートが追加されていることを確認します:

```
default via 10.244.2.168 dev eth0
10.244.2.168 dev eth0 scope link
192.168.20.0/24 dev net1 scope link  src 192.168.20.50
```

**確認ポイント**:

- `default via ...` のルートが `eth0` 経由で設定されていること (デフォルトゲートウェイ, Cilium 管理のプライマリネットワーク, 上記例では `10.244.2.168`)
- Cilium ゲートウェイへの直接ルート (`10.244.2.168 dev eth0 scope link`) が存在すること
- セカンダリネットワーク用のルートが `net1` 経由で設定されていること (上記例では `192.168.20.0/24 dev net1 scope link src 192.168.20.50`)
- セカンダリネットワークのルートに送信元IP (`src`) が指定されていること (これにより通信経路の安定化が図られる)

#### 7.4 テストポッドの削除

確認後は, 以下のコマンドを実行し, テストポッドを削除します:

```bash
kubectl delete -f /home/ansible/kubeadm/multus/app-pod.yml
kubectl delete -f /tmp/ipvlan-wb-nad.yml --ignore-not-found
```

### 8. Multus ログの確認

問題が発生した場合は, Multus Pod のログを確認します:

```bash
kubectl logs -n kube-system -l app=multus --tail=50
```

## トラブルシューティング

### 1. Multus DaemonSet が起動しない

**症状**:

- `kubectl get daemonset -n kube-system` で `kube-multus-ds` の `DESIRED` と `READY` が一致しない
- `kubectl get pods -n kube-system -l app=multus` で Pod が `CrashLoopBackOff` や `ImagePullBackOff` 状態

**原因**:

- コンテナイメージが取得できない (ネットワーク接続, レジストリアクセス権限)
- CNI バイナリディレクトリ (`/opt/cni/bin`) または CNI 設定ディレクトリ (`/etc/cni/net.d`) が存在しない
- RBAC 権限不足

**対処方法**:

1. コンテナイメージのプルエラーを確認: `kubectl describe pod -n kube-system <POD_NAME>`
2. ノード上で CNI ディレクトリの存在を確認: `sudo ls -ld /opt/cni/bin /etc/cni/net.d`
3. ServiceAccount, ClusterRole, ClusterRoleBinding の存在を確認: `kubectl get sa,clusterrole,clusterrolebinding | grep multus`

### 2. NetworkAttachmentDefinition (NAD) が認識されない

**症状**:

- `kubectl get network-attachment-definitions` でエラーが発生する
- Pod に Annotation でセカンダリネットワークを指定してもアタッチされない

**原因**:

- NetworkAttachmentDefinition CRD が登録されていない
- NAD リソース自体が作成されていない

**対処方法**:

1. CRD の存在を確認: `kubectl get crd | grep network-attachment-definitions`
2. CRD が存在しない場合は, Helm 導入または kubectl apply 導入が正常に完了していない可能性があります。ロールを再実行, または `k8s_multus_cleanup_resources: true` で既存リソースをクリーンアップしてから再導入します。
3. NAD リソースの作成は 別ロール で行います(例: `k8s-whereabouts`)。**本ロールでは, NAD 自体の作成は行いません**。

### 3. Pod にセカンダリネットワークインターフェースがアタッチされない

**症状**:

- Pod 内で `ip addr show` を実行しても `net1` 等のセカンダリインターフェースが表示されない
- Pod に NAD を指定する Annotation (`k8s.v1.cni.cncf.io/networks`) を付与しているが反映されない

**原因**:

- Annotation の記述ミス (名前空間の省略, NAD 名の誤り)
- NAD リソースが存在しない, または不正な CNI 設定が含まれている
- Multus が thin モードで動作しているが, 参照先の CNI プラグインバイナリが存在しない

**対処方法**:

1. Annotation の記述を確認: `kubectl get pod <POD_NAME> -o jsonpath='{.metadata.annotations}'`
   - 正しい形式: `k8s.v1.cni.cncf.io/networks: <NAMESPACE>/<NAD_NAME>` または `k8s.v1.cni.cncf.io/networks: <NAD_NAME>` (同一名前空間の場合)
2. NAD の存在と内容を確認: `kubectl get network-attachment-definitions -n <NAMESPACE> <NAD_NAME> -o yaml`
3. CNI プラグインバイナリの存在を確認 (thin モードの場合): `sudo ls -l /opt/cni/bin/` で必要なプラグイン (ipvlan, macvlan, bridge 等) が存在することを確認
4. Multus Pod のログを確認: `kubectl logs -n kube-system -l app=multus`

### 4. Helm Release が失敗する

**症状**:

- `helm upgrade --install` コマンドがエラーを返す
- `helm list -n kube-system` で Multus Release が `failed` 状態

**原因**:

- Helm Chart の構文エラー
- values ファイルの記述ミス
- kube-apiserver への接続失敗

**対処方法**:

1. Helm Release の状態を確認: `helm list -n kube-system | grep multus`
2. Release の詳細を確認: `helm get all multus -n kube-system`
3. values ファイルの内容を確認: `cat /tmp/multus-values.yml`
4. kube-apiserver の応答を確認: `kubectl cluster-info`
5. Helm を使用せず kubectl apply 方式に切り替える: `k8s_multus_kubectl_apply_enabled: true`

### 5. kube-apiserver に接続できない

**症状**:

- `wait_for` タスクでタイムアウトが発生する
- `kubectl` コマンドが `connection refused` または `timed out` エラーを返す

**原因**:

- kube-apiserver が起動していない
- ファイアウォールやネットワーク設定で API エンドポイントへの接続がブロックされている
- `/etc/kubernetes/admin.conf` のエンドポイント設定が誤っている

**対処方法**:

1. kube-apiserver プロセスの起動を確認: `systemctl status kubelet` (コントロールプレーンノード)
2. エンドポイントへの接続を確認: `curl -k https://<API_ENDPOINT>:6443/healthz`
3. ファイアウォール設定を確認: `sudo iptables -L -n | grep 6443` または `sudo firewall-cmd --list-all`
4. `k8s_api_wait_timeout` を増やして再実行

## 注意事項

- `k8s_multus_install_via_helm` の値を切り替える場合は, 既存の導入方式で作成したリソース(Helm release, DaemonSet, 設定ファイル)を事前に整理し, 新旧方式の定義が同時に残存しない状態で再実行すること。
- `k8s_multus_cni_conf_filename` は, 既存 CNI 設定との読込順序競合を避ける値であること。特に `00-` 接頭辞を変更する場合は, 対象ノードの `/etc/cni/net.d` 配下で先頭適用される設定ファイルが意図どおりであること。
- `k8s_multus_k8s_api_endpoint_address` と `k8s_multus_k8s_api_endpoint_port` は, `/etc/kubernetes/admin.conf` で実際に使用する API エンドポイントと一致していること。
- `k8s_multus_network_definitions` に定義する CIDR, gateway, interface 名は, 既存ネットワーク設計と重複しないこと。重複がある場合は, Pod 間通信の断続的失敗や経路競合が発生するため, 導入前にネットワーク設計書で確認すること。
- `k8s_multus_test_pod_enabled: true` で検証 Pod を起動する場合は, `k8s_multus_test_pod_image` を全対象ノードが取得可能であること。オフライン環境では, 事前にローカルレジストリへ配置したイメージを指定すること。
- `k8s_collect_pod_ips_completion_enabled: true` を使用する場合は, 対象ホストに bash または zsh 補完機能が導入済みであること。加えて, `collect-pod-ips.py` 実行に必要な Python ライブラリ(Python版Kubernetes Client Library, PyYAML)が対象ホストで導入済みであること。

## 付録

### Pod アドレス収集補助スクリプト

本ロールでは, `collect-pod-ips.py` をノード上の補助ツールとして配置できます。このスクリプトは, Kubernetes API から Pod 一覧を取得し, `status.podIPs` と Multus の `k8s.v1.cni.cncf.io/network-status` 注釈をもとに, Pod ごとの IP アドレス情報を YAML 形式で一覧化します。

本ツールの動作には, 以下のpythonライブラリが導入されている必要があります:

- [Python版Kubernetes Client Library](https://github.com/kubernetes-client/python)
- [PyYAML](https://pyyaml.org/wiki/PyYAML)

### スクリプト配置

Ansible ロール実行時に以下のスクリプトと補完ファイルが自動配置されます。

| 変数名 | デフォルト値 | 説明 |
| --- | --- | --- |
| `k8s_collect_pod_ips_script_path` | `/opt/k8snodes/sbin/collect-pod-ips.py` | Pod アドレス収集スクリプト本体の配置先 |
| `k8s_collect_pod_ips_completion_enabled` | `true` | bash/zsh 補完配置の有効/無効切り替え |
| `k8s_collect_pod_ips_bash_completion_path` | `/etc/bash_completion.d/collect-pod-ips` | bash 補完ファイル配置先 |
| `k8s_collect_pod_ips_zsh_completion_path` | ディストリビューション依存 | zsh 補完ファイル配置先 |

### コマンドライン仕様

`collect-pod-ips.py` は以下の基本形式で使用します。

```bash
collect-pod-ips.py [オプション...]
```

### 共通オプション

| オプション | 説明 |
| --- | --- |
| `--namespace NAMESPACE` | 対象の名前空間 ( namespace ) を指定します。省略時は全名前空間が対象です。 |
| `--label-selector SELECTOR` | Kubernetes のラベルセレクタを指定します。 |
| `--field-selector SELECTOR` | Kubernetes のフィールドセレクタを指定します。 |
| `--in-cluster` | Pod 内から実行する前提で, ServiceAccount 認証情報を使用します。 |
| `--kubeconfig KUBECONFIG` | Kubernetes APIサーバ接続時に使用するkubeconfigファイルを指定します。`--in-cluster`指定時は無視されます。未指定時は, Kubernetes Client Libraryの既定動作に従います。|
| `--include-empty` | IP アドレスを抽出できなかった Pod も出力対象に含めます。 |
| `--strict` | 警告または IP 未報告インターフェースがある場合, 終了コード 1 で終了します。 |
| `--debug` | 詳細ログを有効化します。 |
| `-h, --help` | ヘルプメッセージを表示して終了します。 |

### 実行時の情報表示

本スクリプトは, 取得結果を以下の YAML 形式で標準出力へ出力します。

- `apiVersion`: 固定値 `pod-network-report.example/v1`
- `kind`: 固定値 `PodNetworkAddressList`
- `items`: Pod ごとのアドレス情報一覧

各 Pod エントリには以下の情報が含まれます。

- `namespace`: Pod が属する名前空間
- `name`: Pod 名
- `uid`: Pod UID
- `node_name`: 配置ノード名
- `phase`: Pod phase
- `addresses`: 収集したアドレス一覧
- `interfaces_without_reported_ip`: IP 未報告インターフェース一覧
- `warnings`: 警告一覧

### 実行例

#### 例1: 全 Pod のアドレス情報を表示

```bash
/opt/k8snodes/sbin/collect-pod-ips.py
```

実行例:

```yaml
$ /opt/k8snodes/sbin/collect-pod-ips.py
apiVersion: pod-network-report.example/v1
kind: PodNetworkAddressList
items:
- namespace: default
  name: demo-net1
  uid: 0cc98742-b28d-4a9a-bd36-1b130982000a
  node_name: k8sworker0102
  phase: Running
  addresses:
  - address: 10.244.2.92
    family: IPv4
    network: cilium
    interface: eth0
    mac: 06:da:6e:1e:6a:ab
    default_network: true
    source: k8s.v1.cni.cncf.io/network-status
  - address: fdb6:6e92:3cfb:202::6907
    family: IPv6
    network: cilium
    interface: eth0
    mac: 06:da:6e:1e:6a:ab
    default_network: true
    source: k8s.v1.cni.cncf.io/network-status
  - address: 192.168.20.1
    family: IPv4
    network: default/ipvlan-wb
    interface: net1
    mac: 00:50:56:00:bf:71
    default_network: false
    source: k8s.v1.cni.cncf.io/network-status
  interfaces_without_reported_ip: []
  warnings: []
略
```

#### 例2: 特定名前空間だけを対象にする

```bash
/opt/k8snodes/sbin/collect-pod-ips.py --namespace kube-system
```

実行例:
```bash
$ /opt/k8snodes/sbin/collect-pod-ips.py --namespace kube-system
apiVersion: pod-network-report.example/v1
kind: PodNetworkAddressList
items:
- namespace: kube-system
  name: cilium-98mm4
  uid: 78fabbb1-d795-4591-85b8-e17871eee248
  node_name: k8sworker0102
  phase: Running
  addresses:
  - address: 192.168.30.43
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::43
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: cilium-envoy-87z7v
  uid: a08f7a8d-ff1a-487b-8daf-35193bedf0ef
  node_name: k8sworker0101
  phase: Running
  addresses:
  - address: 192.168.30.42
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::42
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: cilium-envoy-r9kpf
  uid: 990fed7f-ca3f-423f-bb04-f6fc9a4f6e54
  node_name: k8sctrlplane01
  phase: Running
  addresses:
  - address: 192.168.30.41
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::41
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: cilium-envoy-xz588
  uid: 886a5165-855b-42b8-97f7-3a44b0746355
  node_name: k8sworker0102
  phase: Running
  addresses:
  - address: 192.168.30.43
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::43
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: cilium-operator-7f9b9c849d-5bx9w
  uid: 19bb7f06-9fc5-43e0-86b8-c96d80277e01
  node_name: k8sworker0101
  phase: Running
  addresses:
  - address: 192.168.30.42
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::42
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: cilium-operator-7f9b9c849d-9mvj2
  uid: 4403aff2-7b76-490a-be0f-79ae261de714
  node_name: k8sctrlplane01
  phase: Running
  addresses:
  - address: 192.168.30.41
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::41
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: cilium-p7jc2
  uid: e7672dd8-12fc-4fd0-9f0b-1d5464094d49
  node_name: k8sctrlplane01
  phase: Running
  addresses:
  - address: 192.168.30.41
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::41
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: cilium-vfpz2
  uid: cdb583a3-d2a7-44e6-9ab7-25ae9858a086
  node_name: k8sworker0101
  phase: Running
  addresses:
  - address: 192.168.30.42
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::42
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: clustermesh-apiserver-599f5dcb5f-lfgkz
  uid: a760231e-a466-4b9f-8a59-58ebdbc7844e
  node_name: k8sworker0101
  phase: Running
  addresses:
  - address: 10.244.1.46
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdb6:6e92:3cfb:201::10fc
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: coredns-7c65d6cfc9-rt5z7
  uid: 96f29068-15bc-45a0-ae5e-bd03c5ebdfc0
  node_name: k8sctrlplane01
  phase: Running
  addresses:
  - address: 10.244.0.140
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdb6:6e92:3cfb:200::ad32
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: coredns-7c65d6cfc9-t5bh9
  uid: ab97ad24-e8d9-4616-8a17-49095523dc80
  node_name: k8sctrlplane01
  phase: Running
  addresses:
  - address: 10.244.0.202
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdb6:6e92:3cfb:200::3cdc
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: etcd-k8sctrlplane01
  uid: 6f826f54-8699-4259-b7a9-fcc860447a6f
  node_name: k8sctrlplane01
  phase: Running
  addresses:
  - address: 192.168.30.41
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::41
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: hubble-relay-6f576c4487-2z55v
  uid: 32ad1aa1-41d5-4f28-b6a3-12cde597cf70
  node_name: k8sworker0101
  phase: Running
  addresses:
  - address: 10.244.1.96
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdb6:6e92:3cfb:201::a68
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: hubble-ui-6b65d5f8f5-lxvxn
  uid: a3f1247f-a893-428c-8f86-8a13037b1e54
  node_name: k8sworker0101
  phase: Running
  addresses:
  - address: 10.244.1.101
    family: IPv4
    network: cilium
    interface: eth0
    mac: 76:ce:b2:49:e6:93
    default_network: true
    source: k8s.v1.cni.cncf.io/network-status
  - address: fdb6:6e92:3cfb:201::13d8
    family: IPv6
    network: cilium
    interface: eth0
    mac: 76:ce:b2:49:e6:93
    default_network: true
    source: k8s.v1.cni.cncf.io/network-status
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: kube-apiserver-k8sctrlplane01
  uid: 78939a41-a73d-4542-90c9-cc113371198f
  node_name: k8sctrlplane01
  phase: Running
  addresses:
  - address: 192.168.30.41
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::41
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: kube-controller-manager-k8sctrlplane01
  uid: 8d6b7dea-7659-49f3-95cf-c59bc841cd80
  node_name: k8sctrlplane01
  phase: Running
  addresses:
  - address: 192.168.30.41
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::41
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: kube-multus-ds-6cn2s
  uid: b68d280b-9268-4d47-b261-f38cb205c484
  node_name: k8sctrlplane01
  phase: Running
  addresses:
  - address: 192.168.30.41
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::41
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: kube-multus-ds-9k87r
  uid: c9051ad8-e25d-4f03-8d95-fa8b4c3d0234
  node_name: k8sworker0101
  phase: Running
  addresses:
  - address: 192.168.30.42
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::42
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: kube-multus-ds-wfcpq
  uid: 47812fdf-30d4-4fb3-8531-dfab80b22b8b
  node_name: k8sworker0102
  phase: Running
  addresses:
  - address: 192.168.30.43
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::43
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: kube-scheduler-k8sctrlplane01
  uid: 8f25b2ef-bf03-495e-8f1b-0e0f0b10cc22
  node_name: k8sctrlplane01
  phase: Running
  addresses:
  - address: 192.168.30.41
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::41
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: whereabouts-whereabouts-chart-controller-bd8d4fd75-gzwsz
  uid: f87fe8b2-8c87-4f2f-8d10-0cb4dbec7c4c
  node_name: k8sworker0101
  phase: Running
  addresses:
  - address: 10.244.1.193
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdb6:6e92:3cfb:201::a67a
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: whereabouts-whereabouts-chart-crfzj
  uid: 5bea06b6-e9b2-4b99-8a08-7efaaaced864
  node_name: k8sworker0101
  phase: Running
  addresses:
  - address: 192.168.30.42
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::42
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: whereabouts-whereabouts-chart-jq4zq
  uid: df76db06-515e-4231-9905-9872bf49196e
  node_name: k8sctrlplane01
  phase: Running
  addresses:
  - address: 192.168.30.41
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::41
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: whereabouts-whereabouts-chart-tm7cw
  uid: 6596b4bb-a63d-4b99-912d-6332676a492a
  node_name: k8sworker0102
  phase: Running
  addresses:
  - address: 192.168.30.43
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::43
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
```

#### 例3: ラベルセレクタで Multus Pod を絞り込む

```bash
/opt/k8snodes/sbin/collect-pod-ips.py --namespace kube-system --label-selector app=multus
```

実行例:
```bash
$ /opt/k8snodes/sbin/collect-pod-ips.py --namespace kube-system --label-selector app=multus
apiVersion: pod-network-report.example/v1
kind: PodNetworkAddressList
items:
- namespace: kube-system
  name: kube-multus-ds-6cn2s
  uid: b68d280b-9268-4d47-b261-f38cb205c484
  node_name: k8sctrlplane01
  phase: Running
  addresses:
  - address: 192.168.30.41
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::41
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: kube-multus-ds-9k87r
  uid: c9051ad8-e25d-4f03-8d95-fa8b4c3d0234
  node_name: k8sworker0101
  phase: Running
  addresses:
  - address: 192.168.30.42
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::42
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
- namespace: kube-system
  name: kube-multus-ds-wfcpq
  uid: 47812fdf-30d4-4fb3-8531-dfab80b22b8b
  node_name: k8sworker0102
  phase: Running
  addresses:
  - address: 192.168.30.43
    family: IPv4
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  - address: fdad:ba50:248b:1::43
    family: IPv6
    network: null
    interface: null
    mac: null
    default_network: true
    source: status.podIPs
  interfaces_without_reported_ip: []
  warnings: []
```

#### 例4: 警告を検知したら失敗させる

以下のように本コマンドを実行することで, 追加ネットワーク要求があるのに `network-status` 注釈から IP アドレスを抽出できない場合や, IP 未報告インターフェースが存在する場合に終了コード 1 で終了させることができます。本機能は, 設定異常を検出することを想定した機能です。

```bash
/opt/k8snodes/sbin/collect-pod-ips.py --strict --include-empty
```

### シェル補完機能

`collect-pod-ips.py` には, bash および zsh 用のシェル補完機能が提供されています。補完機能を使用することで, オプション名をタブキーで補完できます。

#### 補完機能の有効化設定

| 変数名 | デフォルト値 | 説明 |
| --- | --- | --- |
| `k8s_collect_pod_ips_completion_enabled` | `true` | bash/zsh 補完の有効/無効切り替え |

#### 補完ファイル配置先

| シェル | ディストリビューション | 配置先パス |
| --- | --- | --- |
| bash | Debian/Ubuntu | `/etc/bash_completion.d/collect-pod-ips` |
| bash | RHEL/CentOS | `/etc/bash_completion.d/collect-pod-ips` |
| zsh | Debian/Ubuntu | `/usr/share/zsh/vendor-completions/_collect-pod-ips` |
| zsh | RHEL/CentOS | `/usr/share/zsh/site-functions/_collect-pod-ips` |

#### 補完機能の使用方法

新しいシェルセッションを開始すると自動的に補完機能が有効化されます。既存のセッションで有効化する場合は以下を実行します。

**bash の場合:**

```bash
source /etc/bash_completion.d/collect-pod-ips
```

**zsh の場合:**

zsh の場合は, 新しいターミナルセッションを開始しなおしてください。

#### 補完の動作

シェル補完では以下のオプション名を補完できます。

- `--namespace`
- `--label-selector`
- `--field-selector`
- `--in-cluster`
- `--include-empty`
- `--strict`
- `--debug`
- `--help`

#### 補完機能のトラブルシューティング

**補完が動作しない場合:**

1. 補完ファイルが配置されていることを確認

    a. bashを使用している場合
      ```bash
      ls -l /etc/bash_completion.d/collect-pod-ips
      ```

    b. zshを使用している場合(Ubuntu/Debian環境)
      ```
      ls -l /usr/share/zsh/vendor-completions/_collect-pod-ips
      ```

    c. zshを使用している場合(RHEL/Alma Linux環境)
      ```
      ls -l /usr/share/zsh/site-functions/_collect-pod-ips
      ```

2. 新しいシェルセッションを開始
  bash/zsh ともに新しいターミナルセッションで自動的に有効化されます。

## 参考資料

### 公式ドキュメント

- [Multus CNI GitHub リポジトリ](https://github.com/k8snetworkplumbingwg/multus-cni)
- [Multus Quickstart Guide](https://github.com/k8snetworkplumbingwg/multus-cni/blob/master/docs/quickstart.md)
- [NetworkAttachmentDefinition 仕様](https://github.com/k8snetworkplumbingwg/network-attachment-definition-client)
- [CNI 仕様](https://github.com/containernetworking/cni/blob/master/SPEC.md)
- [Multus Helm Chart](https://github.com/k8snetworkplumbingwg/multus-cni/tree/master/deployments/helm)
- [Python版Kubernetes Client Library](https://github.com/kubernetes-client/python)
- [PyYAML](https://pyyaml.org/wiki/PyYAML)

### 関連ロール

- `k8s-common`: Kubernetes クラスタ共通設定
- `k8s-ctrlplane`: コントロールプレーンノード構築 (Cilium 導入)
- `k8s-whereabouts`: Multus セカンダリネットワーク用 IPAM プラグインと NAD 導入例
- `python-k8s-client-local`: Python版 Kubernetes Clientライブラリ導入ロール
