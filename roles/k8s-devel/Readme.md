# k8s-devel ロール

本ロールは, Kubernetes 開発向けの言語別 Client ライブラリ導入を行うロールです。

## 目次

- [k8s-devel ロール](#k8s-devel-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
    - [クライアント有効化設定](#クライアント有効化設定)
    - [版数指定](#版数指定)
    - [Go 言語版 Kubernetes client設定](#go-言語版-kubernetes-client設定)
    - [vars/cross-distro.yml 参照変数](#varscross-distroyml-参照変数)
    - [Python 環境設定 (OS 別参照変数)](#python-環境設定-os-別参照変数)
  - [設定例](#設定例)
  - [設定内容の検証](#設定内容の検証)
    - [前提条件](#前提条件-1)
    - [1. Go 言語版 Kubernetes client 導入の確認](#1-go-言語版-kubernetes-client-導入の確認)
    - [2. Python 言語版 Kubernetes client 導入の確認 (既定: ローカルパッケージ方式)](#2-python-言語版-kubernetes-client-導入の確認-既定-ローカルパッケージ方式)
    - [3. Python 言語版 Kubernetes client 導入の確認 (RHEL 9.6, 既定: ローカルパッケージ方式)](#3-python-言語版-kubernetes-client-導入の確認-rhel-96-既定-ローカルパッケージ方式)
    - [4. Python 言語版 Kubernetes client 導入の確認 (互換: pip導入モード)](#4-python-言語版-kubernetes-client-導入の確認-互換-pip導入モード)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. k8s\_major\_minor の形式エラーで package.yml が実行されない場合](#1-k8s_major_minor-の形式エラーで-packageyml-が実行されない場合)
    - [2. Go ローカルパッケージ導入で失敗する場合](#2-go-ローカルパッケージ導入で失敗する場合)
    - [3. Go 言語版 Kubernetes client 導入で失敗する場合](#3-go-言語版-kubernetes-client-導入で失敗する場合)
    - [4. Python 言語版 Kubernetes client 導入で失敗する場合](#4-python-言語版-kubernetes-client-導入で失敗する場合)
    - [5. Ubuntu 24.04 で externally-managed-environment エラーが出る場合](#5-ubuntu-2404-で-externally-managed-environment-エラーが出る場合)
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
| アプリケーション | - | 利用者の目的を実現するために動作するソフトウェア。 |
| パッケージ | - | ソフトウェア導入に必要なファイルをまとめた配布単位。 |
| リポジトリ | - | ソフトウェアや設定情報を保管し, 取得できるようにした管理場所。 |
| コマンド | - | 実行者が計算機へ処理を指示するための命令。 |
| ホスト | - | 管理対象として識別される個別の計算機。 |
| サーバ | - | 他の機器や利用者へ機能やデータを提供する計算機, 又はその役割。 |
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
| Python | - | スクリプティングやアプリケーション開発を手早く実施するために用いられる高水準プログラミング言語の一種。 |
| Python Enhancement Proposal | PEP | Python の機能改善や標準化を提案・議論するための公式文書体系。ソフトウェア開発における仕様策定の枠組み。 |
| End-of-Life | EOL | ソフトウェアやシステムのサポート終了状態。セキュリティ更新や機能追加が停止される。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Red Hat Enterprise Linux | RHEL | Red Hatが提供する企業向けLinuxディストリビューション。 |
| Red Hat Enterprise Linux 9 | RHEL9 | Red Hat Enterprise Linux の第9系統版。 |
| Secure Shell | SSH | 遠隔の計算機へ安全に接続して操作する方式。 |
| Ansible Playbook | playbook | 自動化処理の実行手順を順序付きで記述したファイル。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `cat` | - | ファイル内容を標準出力へ表示するコマンド。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| makeコマンド | make | Makefile に定義された処理を実行するコマンド。 |
| `python3` | - | Python 3 系インタプリタを実行するコマンド。 |
| rpmコマンド | - | RPM パッケージの情報参照や導入確認を行うコマンド。 |
| オフライン | - | ネットワーク未接続で動作する状態。 |
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| オフライン開発キット | - | 外部ネットワーク接続なしで開発や検証を行うために必要な資材一式。 |
| リモートホスト | - | ネットワーク越しに接続して操作する別ホスト。 |
| ローカルパッケージ | - | 外部配布元ではなく, 手元環境で作成または保管した導入用パッケージ。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| 構築ホスト | - | パッケージや実行資材を生成するビルド処理を担当するホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |
## 概要
Kubernetes 開発向けの言語別 Client ライブラリ導入を行うロールです。

本ロールは Kubernetes 開発環境向けに, Python, Go, C (将来対応) の各言語で Kubernetes API を操作するための Client ライブラリを導入します。

本ロールは Go 導入処理を直接実施せず, 導入済みの Go 実行環境を利用して Go 言語版 Kubernetes client を導入します。版数指定時の Go 導入処理は `go-lang-local` ロールを playbook 側で実行します。

主な機能:

- **Python 言語版 Kubernetes client の導入方式切替**: 既定では `python-k8s-client-local` ロールに委譲して, ローカルパッケージ方式で導入します。`k8s_devel_python_client_install_via_pip=true` を明示した場合のみ, 互換運用として pip 導入を行います。
- **Kubernetes 版数からの client 既定版数導出**: `k8s_major_minor` (例: `1.31`) から, Python 言語版 Kubernetes client は `~=31.0`, Go 言語版 Kubernetes client は `v0.31.0` を導出します。
- **PEP 668 対応 (pip導入モード時)**: Ubuntu 24.04 以降では PEP 668 (外部管理環境) によりシステム Python への直接導入が制限されるため, pip導入モードでは自動的に `--break-system-packages` を付与します。
- **Go client 導入前の事前検証**: `k8s_devel_go_client_enabled=true` の場合, `golang` / `golang-go` / `go-lang` の導入有無を確認し, 未導入なら `fail` で停止します。

## 前提条件

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- `repo-deb` または `repo-rpm` が先に適用され, `k8s_major_minor` が定義されていることを前提とします。
- Ubuntu 24.04 以降で pip導入モードを利用する場合は, PEP 668 (外部管理環境) により `--break-system-packages` が必要です。本ロールは pip導入モード時に自動付与します。

## 実行方法

以下のいずれかのコマンドを制御ホスト上で実行します:

**make コマンドで実行 (全ホスト対象)**:
```bash
make run_k8s_devel
```

**コントロールプレーンノードに適用**:
```bash
ansible-playbook k8s-ctrl-plane.yml
```

**ワーカーノードに適用**:
```bash
ansible-playbook k8s-worker.yml
```

**開発環境に適用**:
```bash
ansible-playbook devel.yml
```

**特定ホストのみに適用**:
```bash
ansible-playbook k8s-ctrl-plane.yml -l k8sctrlplane01.local
```

**k8s-devel タスクのみ実行**:
```bash
ansible-playbook k8s-ctrl-plane.yml -t k8s-devel
```

## 主要変数

### クライアント有効化設定

各言語の Kubernetes Client ライブラリの導入を制御する変数です。

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_devel_python_client_enabled` | `false` | Python 言語版 Kubernetes client を導入する場合は, `true`に設定します。 |
| `k8s_devel_go_client_enabled` | `false` | Go 言語版 Kubernetes client を導入する場合は, `true`に設定します。 |
| `k8s_devel_c_client_enabled` | `false` | C Kubernetes client を導入する場合は, `true`に設定します。将来サポート予定。 |
| `k8s_devel_go_packages_enabled` | `false` | Go 関連タスクを有効化する補助フラグです。Go自体の導入は本ロールでは実施しません。 |
| `k8s_devel_python_client_install_via_pip` | `false` | Python 言語版 Kubernetes client の導入方式切替フラグ。既定値 `false` では `python-k8s-client-local` ロールによるローカルパッケージ導入, `true` では legacy の pip 導入を行います。 |

### 版数指定

Python 言語版 Kubernetes client と Go 言語版 Kubernetes client の版数を指定する変数です。未指定時は `k8s_major_minor` から自動導出されます。

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_devel_python_client_version` | `""` | Python 言語版 Kubernetes client 版数。空文字列時は `k8s_major_minor` (例: `1.31`) から `~=<minor>.0` (例: `~=31.0`) を導出します。`~=` は互換バージョン指定 (PEP 440) で, 該当系列 (例: `31.0.0`, `31.1.0`, `31.2.3` など, ただし `32.0.0` 未満) の最新版を pip が自動選択します。 |
| `k8s_devel_go_client_version` | `""` | Go 言語版 Kubernetes client 版数。空文字列時は `k8s_major_minor` (例: `1.31`) から `v0.<minor>.0` (例: `v0.31.0`) を導出します。client-go は常にメジャー版数が `0` で, Kubernetes のマイナー版数がそのままマイナー版数になります。 |

**注記**: `k8s_major_minor` は `repo-deb` または `repo-rpm` ロールで定義される Kubernetes のメジャー.マイナー版数 (例: `1.31`) です。

### Go 言語版 Kubernetes client設定

Go 言語版 Kubernetes clientの版数とインストール方法を制御する変数です。

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_devel_go_client_work_dir` | `"/opt/k8s-devel/go-client"` | Go 言語版 Kubernetes client のオフライン開発キット導入先ディレクトリ。`go-k8s-client-local` ロールがローカルパッケージ経由で `go.mod`, `go.sum`, `vendor/` を配置します。 |
| `k8s_devel_go_module_domain` | `"elliptic-curve.net"` (未定義時は `"example.org"`) | Go モジュールドメイン。`go-k8s-client-local` ロールの構築処理内で `go mod init` に使用します。既定では `vars/all-config.yml` の `dns_domain` から末尾の `.` を除去した値を使用し, `dns_domain` が未定義の場合のみ `"example.org"` を使用します。 |

`go_lang_version`, `go_lang_remove_existing_package` など Go 導入方式に関する変数は `go-lang-local` ロールで管理します。設定方法と既定値は `roles/go-lang-local/Readme.md` を参照ください。

### vars/cross-distro.yml 参照変数

本ロールは `load-params.yml` で `vars/cross-distro.yml` を読み込み, 以下の変数を参照します。

| 変数名 | 用途 | 主な参照タスク |
| --- | --- | --- |
| `k8s_devel_python_prereq_packages_cross_distro` | Python 前提パッケージ名 (OS差分吸収) | `post-load-params-python-client.yml` |
| `k8s_devel_python_pip_executable_cross_distro` | 開発用 Python 向け pip 実行ファイル (OS差分吸収) | `post-load-params-python-client.yml` |

### Python 環境設定 (OS 別参照変数)

Python 言語版 Kubernetes client 導入時に参照される OS 別の変数です。`vars/packages-ubuntu.yml`, `vars/packages-rhel.yml` で定義されます。

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_python_packages_version` | `"3.12"` | 開発用 Python バージョン。Ubuntu では標準 Python が該当バージョンのため参照のみ, RHEL では `python3.12`, `python3.12-pip` 等の版数指定パッケージ名に使用されます。 |

## 設定例

```yaml
# Kubernetes Go 言語版 clientを導入する
k8s_devel_go_client_enabled: true
# Kubernetes Python 言語版 clientを導入する
k8s_devel_python_client_enabled: true
# Go 言語版 Kubernetes clientの版数としてv0.31.0を指定する
k8s_devel_go_client_version: "v0.31.0"
# Python 言語版 Kubernetes clientの版数指定(PEP 440)。例: ~=31.0, ==31.0.0
k8s_devel_python_client_version: "~=31.0"
```

## 設定内容の検証

本節では, `k8s-devel` ロール実行後にシステムが正しく設定されていることを確認する手順を示します。

### 前提条件

- `k8s-devel` ロールが正常に完了していること。
- リモートホストへ SSH で接続可能であること。
- sudo 権限が利用可能であること (一部コマンド用)。

### 1. Go 言語版 Kubernetes client 導入の確認

**実施ホスト**: `devserver.local`

**コマンド**:

```bash
ls -la /opt/k8s-devel/go-client
rpm -qa | egrep '^go-k8s-client' || dpkg -l | egrep '^ii\s+go-k8s-client'
cat /opt/k8s-devel/go-client/go.mod
cat /opt/k8s-devel/go-client/go.sum | head -10
```

**期待される出力**:

```plaintext
total 20
drwxr-xr-x 3 root root 4096  3月  5 10:20 .
drwxr-xr-x 3 root root 4096  3月  5 10:20 ..
-rw-r--r-- 1 root root  156  3月  5 10:20 go.mod
-rw-r--r-- 1 root root 6842  3月  5 10:20 go.sum
drwxr-xr-x 8 root root 4096  3月  5 10:20 vendor

go-k8s-client-0.31.0-1.el9.noarch

module example.org/k8s-devel-client-go

go 1.22

require k8s.io/client-go v0.31.0

github.com/davecgh/go-spew v1.1.1 h1:vj9j/u1bqnvCEfJOwUhtlOARqs3+rkHYY13jYWTU97c=
github.com/davecgh/go-spew v1.1.1/go.mod h1:J7Y8YcW2NihsgmVo/mv3lAwl/skON4iLHjSsI+c5H38=
github.com/emicklei/go-restful/v3 v3.11.0 h1:rAQnmNREppS9F9Q2gfUYfXBHhVZP4jY9w7V/fPz9S6Q=
github.com/emicklei/go-restful/v3 v3.11.0/go.mod h1:6n3XBCmQQb25CM2LCACGz8ukIrRry+4bhvbpWn3mrbc=
github.com/evanphx/json-patch v5.6.0+incompatible h1:jBYDEEiFBPxA0v50tFdvOzQQTCvpL6mnFh5mB2/l16U=
github.com/evanphx/json-patch v5.6.0+incompatible/go.mod h1:50XU6AFN0ol/bzJsmQLiYLvXMP4fmwYFNcr97nuDLSk=
github.com/fxamacker/cbor/v2 v2.7.0 h1:+0XTmHEIiKtcFgqTHW1eqmnKw6FrBfz0f0u+TmCAQBk=
github.com/fxamacker/cbor/v2 v2.7.0/go.mod h1:lhLxFQWdGBEe+qhyPFzKOMWCWFqfRAKMxV5YVqKU0Rg=
github.com/go-logr/logr v1.4.2 h1:6pFjapn5bLjiuzPgRSQ7hjBCqq9sFzaJK6e0/z8Pqfs=
github.com/go-logr/logr v1.4.2/go.mod h1:9T104GzyrTigFIr8wt5mBrctHMim0Nb2HLGrmQ40KvY=
```

**確認ポイント**:

- `/opt/k8s-devel/go-client` ディレクトリに `go.mod` と `go.sum` が存在
- `go-k8s-client` パッケージが導入済みである
- `/opt/k8s-devel/go-client/vendor` ディレクトリが存在する
- `go.mod` に `require k8s.io/client-go v0.31.0` (または指定版数) が記載されている
- `go.sum` に client-go の依存関係チェックサムが記録されている

### 2. Python 言語版 Kubernetes client 導入の確認 (既定: ローカルパッケージ方式)

**実施ホスト**: `devserver.local` (Ubuntu 24.04)

**コマンド**:

```bash
/opt/k8s-devel/python-client/venv/bin/python -c 'import kubernetes; print(kubernetes.__version__)'
/opt/k8s-devel/python-client/venv/bin/python -c 'import kubernetes; print(kubernetes.__file__)'
```

**期待される出力**:

```plaintext
31.0.0
/opt/k8s-devel/python-client/venv/lib/python*/site-packages/kubernetes/__init__.py
```

**確認ポイント**:

- `/opt/k8s-devel/python-client/venv` 配下の Python で kubernetes が import できる
- 版数が k8s_major_minor (例: 1.31) のマイナー版数 (31) と一致
- インストールパスが `/opt/k8s-devel/python-client/venv/` 配下

### 3. Python 言語版 Kubernetes client 導入の確認 (RHEL 9.6, 既定: ローカルパッケージ方式)

**実施ホスト**: `rhel-server.local` (RHEL 9.6)

**コマンド**:

```bash
/opt/k8s-devel/python-client/venv/bin/python -c 'import kubernetes; print(kubernetes.__version__)'
/opt/k8s-devel/python-client/venv/bin/python -c 'import kubernetes; print(kubernetes.__file__)'
```

**期待される出力**:

```plaintext
31.0.0
/opt/k8s-devel/python-client/venv/lib/python*/site-packages/kubernetes/__init__.py
```

**確認ポイント**:

- `/opt/k8s-devel/python-client/venv` 配下の Python で kubernetes が import できる
- 版数が期待値と一致
- インストールパスが `/opt/k8s-devel/python-client/venv/` 配下

### 4. Python 言語版 Kubernetes client 導入の確認 (互換: pip導入モード)

`k8s_devel_python_client_install_via_pip=true` を明示した場合は, 以下のように pip 実行ファイルを使って確認します。

**実施ホスト**: `devserver.local` (Ubuntu 24.04), `rhel-server.local` (RHEL 9.6)

**コマンド**:

```bash
pip3 list | grep kubernetes
python3 -c 'import kubernetes; print(kubernetes.__version__)'
python3 -c 'import kubernetes; print(kubernetes.__file__)'
```

RHEL で `k8s_python_packages_version` を指定している場合は, 必要に応じて `pip3.12` / `python3.12` でも確認します。

## テンプレートと生成ファイル

本ロールで生成, 配置, または更新されるファイルは以下です。

| ファイル | 用途 |
| --- | --- |
| `/opt/k8s-devel/go-client/go.mod` | `go-k8s-client-local` ロールがローカルパッケージ導入で配置する Go モジュール定義ファイルです。 |
| `/opt/k8s-devel/go-client/go.sum` | `go-k8s-client-local` ロールがローカルパッケージ導入で配置する依存関係チェックサムファイルです。 |
| `/opt/k8s-devel/go-client/vendor/` | `go-k8s-client-local` ロールが配置する Go 言語版 Kubernetes client のオフライン依存キットです。 |
| `/opt/k8s-devel/python-client/venv/` | 既定方式 (`k8s_devel_python_client_install_via_pip=false`) で導入される Python 言語版 Kubernetes client 用仮想環境です。`python-k8s-client-local` ロールがローカルパッケージ導入で配置します。 |
| `kubernetes` Python パッケージ | pip導入モード (`k8s_devel_python_client_install_via_pip=true`) で導入される Python 言語版 Kubernetes client です。 |

## 実行フロー

本ロールは以下の順序で処理を実行します:

1. **パラメータ読み込み** (`load-params.yml`): OS 別パッケージ定義 (`vars/packages-ubuntu.yml`, `vars/packages-rhel.yml`) と共通変数 (`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込みます。
2. **版数導出** (`post-load-params.yml`): `k8s_major_minor` (例: `1.31`) から Python 言語版 Kubernetes client と Go 言語版 Kubernetes client の既定版数を導出します。
   - Python 言語版 Kubernetes client: `~=<minor>.0` (例: `~=31.0`) 形式で互換バージョン指定 (PEP 440) を生成します。pip が該当系列の最新版を自動選択します。
   - Go 言語版 Kubernetes client: `v0.<minor>.0` (例: `v0.31.0`) 形式で版数を生成します。client-go は常にメジャー版数が `0` で, Kubernetes のマイナー版数がそのままマイナー版数になります。
   - `k8s_major_minor` の形式検証 (`^[0-9]+\.[0-9]+$`) を実施します。形式不正時は `k8s_devel_skip_version_derivation=true` を設定し, 後段の `package.yml` 実行をスキップします。
3. **Python 実効変数確定** (`post-load-params-python-client.yml`): Python 言語版 Kubernetes client 導入用の実効変数 (`k8s_devel_python_prereq_packages_effective`, `k8s_devel_python_pip_executable_effective`) を確定します。
4. **前提パッケージ導入** (`install-prereqs.yml` - Python 部分): `k8s_devel_python_client_enabled=true` かつ `k8s_devel_python_client_install_via_pip=true` の場合のみ, Python 用 pip パッケージを導入します。
   - Debian: `python3-pip`
   - RHEL: `k8s_python_packages_version` 指定時は `python3.12-pip`, 未指定時は `python3-pip`
5. **Go実行パス既定値設定** (`install-go.yml`): `k8s_devel_go_packages_enabled=true` または `k8s_devel_go_client_enabled=true` の場合, `go_command` の既定値を `/usr/bin/go` に設定します。
6. **Python 言語版 Kubernetes client 導入** (`install-python-client.yml`): `k8s_devel_python_client_enabled=true` の場合, Python 言語版 Kubernetes client を導入します。
   - **既定方式 (推奨)**: `python-k8s-client-local` ロールに委譲してローカルパッケージを導入します。導入先は `/opt/k8s-devel/python-client` 配下の仮想環境です。
   - **互換方式 (legacy)**: `k8s_devel_python_client_install_via_pip=true` の場合のみ pip 導入を実施します。Ubuntu 24.04 以降では自動的に `--break-system-packages` を付与します。
7. **Go 言語版 Kubernetes client 導入** (`install-go-client.yml`): `k8s_devel_go_client_enabled=true` の場合, `go-k8s-client-local` ロールに委譲して Go 言語版 Kubernetes client を導入します。
   - 事前検証として `golang`/`golang-go`/`go-lang` パッケージの導入有無を確認し, 未導入の場合は設定誤りとして `fail` で停止します。
   - `go-k8s-client-local` ロールは, 構築ホスト上のコンテナでオフライン開発キット (`go.mod`, `go.sum`, `vendor/`) を含むローカルパッケージ (deb/rpm) を構築します。
   - 構築済みパッケージを「構築ホスト -> 制御ノード -> 対象ホスト」で転送し, `/opt/k8s-devel/go-client` (既定) に導入します。
   - 導入後に `go.mod` の `k8s.io/client-go` 版数が実効版数 (既定導出時は `v0.31.0`) と一致することを検証します。
8. **C client 導入** (`install-c-client.yml`): `k8s_devel_c_client_enabled=true` の場合でも処理失敗せず, 将来サポート予定として完了します。現在は「C Kubernetes client installation is deferred」メッセージを表示するのみです。

## 検証ポイント

[設定内容の検証](#設定内容の検証)の説明を参考に検証作業を実施してください。

## トラブルシューティング

### 1. k8s_major_minor の形式エラーで package.yml が実行されない場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
grep -n "k8s_major_minor" host_vars/*/main.yml group_vars/all/all.yml
ansible-playbook -i inventory/hosts devel.yml --tags k8s-devel -vv | grep -Ei "k8s_major_minor|skip|package.yml"
```

**確認ポイント**:

- `k8s_major_minor` が `major.minor` 形式 (例: `1.31`) で指定されていること。
- 形式が不正な場合は `package.yml` がスキップされるため, 変数修正後に再実行していること。

### 2. Go ローカルパッケージ導入で失敗する場合

**実施対象ホスト**: 構築ホスト, 制御ホスト

**実行するコマンド**:

```bash
curl -I https://go.dev/dl/
ls -la /tmp/go-build
```

**確認ポイント**:

- 構築ホストから `https://go.dev/dl/` へ到達できること。
- `/tmp/go-build` 配下にローカルパッケージ成果物が生成されていること。
- 生成物がない場合は, ビルド手順またはネットワーク到達性を見直していること。

### 3. Go 言語版 Kubernetes client 導入で失敗する場合

**実施対象ホスト**: 対象ホスト, 構築ホスト

**実行するコマンド**:

```bash
command -v golang || command -v golang-go || command -v go-lang
go version
ansible-playbook -i inventory/hosts devel.yml --tags k8s-devel -vv | grep -Ei "go-k8s-client-local|fail|error"
```

**確認ポイント**:

- 対象ホストで `golang`/`golang-go`/`go-lang` のいずれかが導入済みであること。
- 構築ホストでコンテナ実行が可能で, `go-k8s-client-local` のローカルパッケージ生成が完了していること。
- 導入後検証で `go.mod` の `k8s.io/client-go` 版数が実効版数と一致していること。

### 4. Python 言語版 Kubernetes client 導入で失敗する場合

**実施対象ホスト**: 構築ホスト, 対象ホスト

**実行するコマンド**:

```bash
ansible-playbook -i inventory/hosts devel.yml --tags k8s-devel -vv | grep -Ei "python-k8s-client-local|pip|error|fail"
python3 -m pip --version
```

**確認ポイント**:

- 既定方式では `python-k8s-client-local` ロールによるローカルパッケージ生成が完了していること。
- `k8s_devel_python_client_install_via_pip=true` の場合は, pip 実行環境と外部リポジトリアクセスが確保されていること。
- 仮想環境導入先 (`/opt/k8s-devel/python-client`) が作成され, 依存パッケージが解決されていること。

### 5. Ubuntu 24.04 で externally-managed-environment エラーが出る場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
python3 --version
python3 -m pip install --break-system-packages <package>
```

**確認ポイント**:

- pip 導入モードでは本ロールが `--break-system-packages` を付与すること。
- 手動導入時は `pip install --break-system-packages <package>` を使用していること。
- 手動導入で回避できる場合は, pip 実行時オプション不足が主因であること。

## 注意事項

- `k8s_devel_python_client_enabled`, `k8s_devel_go_client_enabled`, `k8s_devel_c_client_enabled` は既定で `false` のため, 必要な言語だけを明示的に有効化していること。
- `k8s_major_minor` の値は Python 言語版 Kubernetes client と Go 言語版 Kubernetes client の既定版数導出に使用するため, `major.minor` 形式 (例: `1.31`) で指定していること。
- Go 言語版 Kubernetes client 導入では Go 本体を本ロールで導入しないため, 対象ホストに `golang`/`golang-go`/`go-lang` のいずれかが事前導入済みであること。
- 既定方式の Python 言語版 Kubernetes client 導入は `python-k8s-client-local` ロールへ委譲するため, 構築ホストでローカルパッケージ生成が可能な実行環境 (コンテナ実行可否, 必要なネットワーク到達性) を満たしていること。
- `k8s_devel_python_client_install_via_pip=true` の互換方式を使用する場合は, pip 実行環境と外部リポジトリアクセスを確保していること。Ubuntu 24.04 では externally-managed-environment 対応のため, `--break-system-packages` が必要になること。
- `/opt/k8s-devel/go-client` および `/opt/k8s-devel/python-client` 配下の内容は開発用の運用資産を含むため, 削除や再配置の前にバックアップ方針を確認していること。

## 参考資料

### 公式ドキュメント

- [Kubernetes](https://kubernetes.io/docs/home/)
- [Python 言語版 Kubernetes client](https://github.com/kubernetes-client/python)
- [Go 言語版 Kubernetes client(client-go)](https://github.com/kubernetes/client-go)
- [PEP 668 – Marking Python base environments as "externally managed"](https://peps.python.org/pep-0668/)
