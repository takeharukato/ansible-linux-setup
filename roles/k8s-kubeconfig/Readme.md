# k8s-kubeconfig ロール

本ロールは, Kubernetes クラスタの各ノード(コントロールプレーン・ワーカー)で利用する `kubeconfig` を生成, 統合, 配布するロールです。

## 目次

- [k8s-kubeconfig ロール](#k8s-kubeconfig-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
    - [基本設定](#基本設定)
    - [スクリプトパス](#スクリプトパス)
    - [出力ディレクトリ](#出力ディレクトリ)
    - [ホスト間連携](#ホスト間連携)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [キャッシング機構](#キャッシング機構)
  - [実行フロー](#実行フロー)
    - [全ノード共通フロー](#全ノード共通フロー)
    - [コントロールプレーンノード向けフロー](#コントロールプレーンノード向けフロー)
    - [ワーカーノード向けフロー](#ワーカーノード向けフロー)
  - [検証ポイント](#検証ポイント)
    - [kubeconfig ファイルの生成確認(コントロールプレーンノード)](#kubeconfig-ファイルの生成確認コントロールプレーンノード)
    - [統合 kubeconfig 内容確認(全ノード)](#統合-kubeconfig-内容確認全ノード)
    - [kubectl コマンド実行確認(全ノード)](#kubectl-コマンド実行確認全ノード)
    - [ワーカーノード kubeconfig 同期確認](#ワーカーノード-kubeconfig-同期確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. kubectl コマンドが実行できない場合](#1-kubectl-コマンドが実行できない場合)
    - [2. 統合 kubeconfig に期待したコンテキストが含まれない場合](#2-統合-kubeconfig-に期待したコンテキストが含まれない場合)
    - [3. ワーカーノードへ配布した kubeconfig が同期しない場合](#3-ワーカーノードへ配布した-kubeconfig-が同期しない場合)
    - [4. ワーカーノード配布で旧内容が残る場合](#4-ワーカーノード配布で旧内容が残る場合)
  - [注意事項](#注意事項)
    - [スクリプト配置の確認](#スクリプト配置の確認)
    - [ロール実行順序の制約](#ロール実行順序の制約)
    - [ワーカーノードの必須変数](#ワーカーノードの必須変数)
    - [キャッシング機構と単発実行](#キャッシング機構と単発実行)
    - [ファイルパーミッション](#ファイルパーミッション)
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
| Secure Shell | SSH | 遠隔の計算機へ安全に接続して操作する方式。 |
| Superuser Do | sudo | 別のユーザ (通常は root) の権限で指定されたコマンドを実行することを可能にする Unix 系システムのプログラム。管理者以外のユーザが管理作業を行うときに使用される |
| Certificate Authority | CA | 電子証明書を発行して正当性を保証する組織または仕組み。 |
| Access Control List | ACL | 通信やアクセスを許可または禁止するための規則一覧。 |
| Message Digest Algorithm 5 | MD5 | 任意の長さのデータをから一定の長さのハッシュ値に変換するアルゴリズム。ファイル検証や整合性確認に用いる。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| Python | - | スクリプティングやアプリケーション開発を手早く実施するために用いられる高水準プログラミング言語の一種。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| `md5sum` | - | ファイルの MD5 ハッシュ値を計算して一致確認に用いるコマンド。 |
| `setfacl` | - | ファイルやディレクトリの詳細アクセス制御情報を設定するコマンド。 |
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| リモートホスト | - | ネットワーク越しに接続して操作する別ホスト。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |

## 概要

Kubernetes クラスタの各ノード(コントロールプレーン・ワーカー)で利用する `kubeconfig` を生成, 統合, 配布するロールです。証明書埋め込みやコンテキスト統合により, 複数クラスタ環境での運用を効率化します。

本ロールは Kubernetes の kubeconfig ライフサイクル全体を管理します。主な特徴は以下の通りです:

- **証明書埋め込みサポート**: `create-embedded-kubeconfig.py` で CA 証明書を kubeconfig ファイルに埋め込み, クラスタ環境にかかわらず実行可能にします。
- **複数クラスタコンテキスト統合**: `create-uniq-kubeconfig.py` で複数コントロールプレーンノードのコンテキストを1つの kubeconfig に統合します。
- **双方向ファイル配置**: `/etc/kubernetes` とオペレータユーザの `~/.kube` の両方に統合 kubeconfig を配置し, 権限分離と一貫性を両立。
- **キャッシング機構**: 制御ノード上の `~/.ansible/kubeconfig-cache/` に merged-kubeconfig を保管し, ワーカーノード配布の効率化と再実行時の一貫性確保。
- **シンボリックリンク管理**: `~/.kube/config` を相対シンボリックリンク化し, 既存ファイルは `config-default` として退避。
- **権限分離**: `k8s_operator_user` によるアクセス制御で, システムと一般ユーザの権限を分離。

## 前提条件

本ロール実行前に以下の条件が満たされていることを確認してください:

- Kubernetes クラスタが既に構築済みであること(k8s-ctrlplane ロール実行済み)
- コントロールプレーンノード・ワーカーノードが Ansible インベントリで定義されていること
- 制御ノードから全 Kubernetes ノードへの SSH 接続が確立されていること(ホスト鍵確認完了)
- 各ノードで管理者権限(sudo)が利用可能であること
- Python 3.8 以上がリモートホストにインストールされていること
- `create-embedded-kubeconfig.py`, `create-uniq-kubeconfig.py` スクリプトが `k8s_node_setup_tools_dir` に事前配置されていること

## 実行方法

制御ホストで以下のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts site.yml --tags "k8s-kubeconfig"
```

## 主要変数

### 基本設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_operator_user` | `kube` | `kubeconfig` を配置するオペレータユーザ。このユーザのホームディレクトリに `~/.kube` 以下が作成されます。 |
| `k8s_kubeconfig_system_dir` | `/etc/kubernetes` | システム側で `kubeconfig` を配置するベースディレクトリ。管理者権限で操作します。 |
| `k8s_embed_kubeconfig_shared_ca_path` | `""` | `create-embedded-kubeconfig.py` に渡す共通 CA 証明書のパス。未設定時は各クラスタの `/etc/kubernetes/admin.conf` に含まれる CA をそのまま埋め込みます。 |

### スクリプトパス

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_embed_kubeconfig_script_path` | `/opt/k8snodes/sbin/create-embedded-kubeconfig.py` | 証明書埋め込み版 `kubeconfig` を生成するスクリプト。コントロールプレーンノードで実行されます。 |
| `k8s_create_unique_kubeconfig_script_path` | `/opt/k8snodes/sbin/create-uniq-kubeconfig.py` | 複数の `kubeconfig` コンテキストを1つのファイルに統合するスクリプト。 |

### 出力ディレクトリ

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_embed_kubeconfig_output_dir` | `{{ k8s_operator_home }}/.kube` | 埋め込み kubeconfig を出力するディレクトリ。コントロールプレーンノードで使用。 |
| `k8s_embed_kubeconfig_file_postfix` | `-embedded.kubeconfig` | 埋め込み版 kubeconfig のファイル名サフィックス。クラスタ名と組み合わせて「`cluster01-embedded.kubeconfig`」のような形式になります。 |

### ホスト間連携

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_ctrlplane_host` | なし(ホスト変数で必須) | ワーカーノードが統合 kubeconfig を取得するコントロールプレーンノードのホスト名。`host_vars/<worker-node>/` で必ず定義してください。 |
| `k8s_kubeconfig_probe_timeout` | `15` | ワーカーノードがコントロールプレーンノードへの接続確認するときのタイムアウト秒数。 |

## テンプレートと生成ファイル

本ロールはコントロールプレーンノード配下に生成ファイル群を作成し, 最終的に全Kubernetesノードに統合 kubeconfig を配布します。

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `テンプレート未使用 (ランタイム生成)` | `/etc/kubernetes/ca-embedded-admin.conf` (既定: `/etc/kubernetes/ca-embedded-admin.conf`) | 証明書を埋め込み済みの管理者 `kubeconfig`。`kubectl` をルート権限で利用するための控え。 配置ホスト: コントロールプレーンノード, 権限: `0600`。 |
| `テンプレート未使用 (ランタイム生成)` | `/etc/kubernetes/config-default` (既定: `/etc/kubernetes/config-default`) | 既存の `/etc/kubernetes/admin.conf` のバックアップ。ロール実行前の kubeconfig を保持。 配置ホスト: コントロールプレーンノード, 権限: `0600`。 |
| `テンプレート未使用 (ランタイム生成)` | `/etc/kubernetes/merged-kubeconfig.conf` (既定: `/etc/kubernetes/merged-kubeconfig.conf`) | 全コントロールプレーンノードのコンテキストを統合した `kubeconfig`。管理者用。 配置ホスト: 全Kubernetes ノード, 権限: `0600`。 |
| `テンプレート未使用 (ランタイム生成)` | `~{{ k8s_operator_user }}/.kube/cluster*-embedded.kubeconfig` (既定: `~{{ k8s_operator_user }}/.kube/cluster*-embedded.kubeconfig`) | `create-embedded-kubeconfig.py` が生成するクラスタ固有の埋め込み版 kubeconfig。中間成果物。 配置ホスト: コントロールプレーンノード, 権限: `0600`。 |
| `テンプレート未使用 (ランタイム生成)` | `~{{ k8s_operator_user }}/.kube/ca-embedded-admin.conf` (既定: `~{{ k8s_operator_user }}/.kube/ca-embedded-admin.conf`) | `/etc/kubernetes` に配置した埋め込み版のオペレータ控え。 配置ホスト: コントロールプレーンノード, 権限: `0600`。 |
| `テンプレート未使用 (ランタイム生成)` | `~{{ k8s_operator_user }}/.kube/merged-kubeconfig.conf` (既定: `~{{ k8s_operator_user }}/.kube/merged-kubeconfig.conf`) | `/etc/kubernetes/merged-kubeconfig.conf` と同一内容。オペレータユーザが直接参照。 配置ホスト: 全Kubernetes ノード, 権限: `0600`。 |
| `テンプレート未使用 (ランタイム生成)` | `~{{ k8s_operator_user }}/.kube/config` (既定: `~{{ k8s_operator_user }}/.kube/config`) | 統合 `kubeconfig` (`merged-kubeconfig.conf`) への相対シンボリックリンク。既存ファイルは `config-default` に退避。 配置ホスト: 全Kubernetes ノード, 権限: リンク。 |
| `テンプレート未使用 (ランタイム生成)` | `~{{ k8s_operator_user }}/.kube/config-default` (既定: `~{{ k8s_operator_user }}/.kube/config-default`) | `symlink.yml` 実行前の既存 `~/.kube/config` のバックアップ(存在した場合のみ)。 配置ホスト: 全Kubernetes ノード, 権限: `0600`。 |

## キャッシング機構

制御ノード上の `~/.ansible/kubeconfig-cache/` にはコントロールプレーンノードから取得した最新の `/etc/kubernetes/merged-kubeconfig.conf` がキャッシュされます。ワーカーノード配布時にこのキャッシュを参照するため, プレイブック再実行時の効率化と一貫性が確保されます。 キャッシュディレクトリのパーミッションは `0700`(ユーザのみアクセス可能)に設定されます。

## 実行フロー

### 全ノード共通フロー

1. `load-params.yml` でディストリビューション別パッケージ名, 共通設定, API エンドポイント定義などを読み込みます。
2. `prepare-vars.yml` が `kubeconfig` 関連パスを計算し, 埋め込みファイル名や `/etc/kubernetes` 配置先を決定します。
3. `directory.yml` で `/etc/kubernetes` と `{{ k8s_operator_user }}` の `~/.kube` を作成し, 必要な所有者, パーミッションを整えます。

### コントロールプレーンノード向けフロー

4. `control-plane.yml` ( `k8s_ctrl_plane` グループのみ )では次を実施します:
   - `/etc/kubernetes/admin.conf` を `config-default` としてバックアップ。
   - `create-embedded-kubeconfig.py` を呼び出し, Kubernetesクラスタ毎の証明書埋め込み `kubeconfig` を生成。
   - 各コントロールプレーンノードから埋め込み `kubeconfig` を収集し, 一時ディレクトリに展開。
   - kubeconfigファイル結合ツール(`create-uniq-kubeconfig.py`) で複数コンテキストを統合し `merged-kubeconfig.conf` を生成。
   - 生成された `merged-kubeconfig.conf` を `/etc/kubernetes` とオペレータユーザホームの `~/.kube` に配布。

### ワーカーノード向けフロー

5. `distribute-workers.yml` ( `k8s_worker` グループのみ )はホスト変数 (`k8s_ctrlplane_host` 変数) で指定されたコントロールプレーンノード上の `merged-kubeconfig.conf` を取得し, 制御ノード上の `~/.ansible/kubeconfig-cache/` に一旦キャッシュしてからワーカーノードへコピーします。
6. `symlink.yml` が `~/.kube/config` を `merged-kubeconfig.conf` への相対シンボリックリンクに置き換え, 既存ファイル(あれば)は `config-default` にリネームして退避します。

## 検証ポイント

本ロール実行後の kubeconfig 統合状況は以下のコマンドで確認できます。

### kubeconfig ファイルの生成確認(コントロールプレーンノード)

**実施ホスト**: コントロールプレーンノード

**コマンド**:
```bash
ls -lh /etc/kubernetes/{admin.conf,config-default,merged-kubeconfig.conf}
ls -lh ~/.kube/{cluster*-embedded.kubeconfig,merged-kubeconfig.conf,config}
```

**期待される出力**:
```
-rw------- 1 root root 5.2K Jul 15 10:30 /etc/kubernetes/admin.conf
-rw------- 1 root root 5.2K Jul 15 10:25 /etc/kubernetes/config-default
-rw------- 1 root root 8.5K Jul 15 10:30 /etc/kubernetes/merged-kubeconfig.conf
-rw------- 1 kube kube 5.0K Jul 15 10:28 /home/kube/.kube/cluster01-embedded.kubeconfig
-rw------- 1 kube kube 8.5K Jul 15 10:30 /home/kube/.kube/merged-kubeconfig.conf
lrwxrwxrwx 1 kube kube 24 Jul 15 10:30 /home/kube/.kube/config -> merged-kubeconfig.conf
```

**確認ポイント**:
- `/etc/kubernetes/merged-kubeconfig.conf` が作成されていること
- `~/.kube/config` が `merged-kubeconfig.conf` へのシンボリックリンクになっていること
- パーミッションが `0600` になっていること

### 統合 kubeconfig 内容確認(全ノード)

**実施ホスト**: コントロールプレーン / ワーカーノード

**コマンド**:
```bash
kubectl config get-contexts
kubectl config get-clusters
```

**期待される出力**:
```
CURRENT   NAME                          CLUSTER                       AUTHINFO                      NAMESPACE
*         kubernetes-admin@cluster01    kubernetes-admin@cluster01    kubernetes-admin@cluster01
          kubernetes-admin@cluster02    kubernetes-admin@cluster02    kubernetes-admin@cluster02
          kubernetes-admin@cluster03    kubernetes-admin@cluster03    kubernetes-admin@cluster03

NAME
cluster01
cluster02
cluster03
```

**確認ポイント**:
- 全コントロールプレーンノードのコンテキストが統合されていること
- クラスタ名, ユーザ情報が正しく表示されていること

### kubectl コマンド実行確認(全ノード)

**実施ホスト**: コントロールプレーン / ワーカーノード

**コマンド**:
```bash
kubectl get nodes
kubectl auth can-i get pods --as=system:serviceaccount:default:default
```

**期待される出力**:
```
NAME                    STATUS   ROLES           AGE   VERSION
k8sctrlplane01.local    Ready    control-plane   20d   v1.29.0
k8sctrlplane02.local    Ready    control-plane   20d   v1.29.0
k8sworker0101.local     Ready    <none>          20d   v1.29.0
k8sworker0102.local     Ready    <none>          20d   v1.29.0

yes
```

**確認ポイント**:
- `kubectl` がクラスタに接続できていること (エラーなく実行結果が返されること)
- 全ノードが `Ready` 状態こと

### ワーカーノード kubeconfig 同期確認

**実施ホスト**: ワーカーノード

**コマンド**:
```bash
ls -l ~/.kube/config ~/.kube/merged-kubeconfig.conf
md5sum ~/.kube/merged-kubeconfig.conf
```

**期待される出力**:
```
lrwxrwxrwx 1 kube kube 24 Jul 15 10:35 /home/kube/.kube/config -> merged-kubeconfig.conf
-rw------- 1 kube kube 8.5K Jul 15 10:35 /home/kube/.kube/merged-kubeconfig.conf
9f5c3e4d2b1a6f8e7c0d5a9b2c3e4f5a  /home/kube/.kube/merged-kubeconfig.conf
```

**確認ポイント**:
- ワーカーノードのファイル内容がコントロールプレーンノードと同期していること(ワーカーノードも MD5 で確認)
- 権限が正しく設定されていること

## トラブルシューティング

### 1. kubectl コマンドが実行できない場合

**実施対象ホスト**: コントロールプレーンノード, ワーカーノード

**実行するコマンド**:

```bash
ls -lh /etc/kubernetes/merged-kubeconfig.conf
ls -lh ~/.kube/{config,merged-kubeconfig.conf}
kubectl config get-contexts
kubectl get nodes
```

**確認ポイント**:

- `/etc/kubernetes/merged-kubeconfig.conf` が作成されていること。
- `~/.kube/config` が `merged-kubeconfig.conf` を参照するシンボリックリンクであること。
- `kubectl config get-contexts` と `kubectl get nodes` が接続エラーなしで実行できること。

### 2. 統合 kubeconfig に期待したコンテキストが含まれない場合

**実施対象ホスト**: コントロールプレーンノード

**実行するコマンド**:

```bash
kubectl config get-contexts
kubectl config get-clusters
ls -lh ~/.kube/cluster*-embedded.kubeconfig
```

**確認ポイント**:

- `kubectl config get-contexts` に全コントロールプレーンノード分のコンテキストが含まれていること。
- `kubectl config get-clusters` に運用対象クラスタ名がすべて表示されること。
- `~/.kube/cluster*-embedded.kubeconfig` が生成されており, 統合元ファイルが欠落していないこと。

### 3. ワーカーノードへ配布した kubeconfig が同期しない場合

**実施対象ホスト**: コントロールプレーンノード, ワーカーノード

**実行するコマンド**:

```bash
md5sum ~/.kube/merged-kubeconfig.conf
ls -l ~/.kube/config ~/.kube/merged-kubeconfig.conf
```

**確認ポイント**:

- コントロールプレーンノードとワーカーノードで `~/.kube/merged-kubeconfig.conf` のハッシュ値が一致していること。
- `~/.kube/config` が `merged-kubeconfig.conf` を参照するシンボリックリンクであること。
- `~/.kube/merged-kubeconfig.conf` の権限が `0600` であること。

### 4. ワーカーノード配布で旧内容が残る場合

**実施対象ホスト**: 制御ノード, コントロールプレーンノード, ワーカーノード

**実行するコマンド**:

```bash
ls -ld ~/.ansible/kubeconfig-cache
ls -l ~/.ansible/kubeconfig-cache
ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml --tags k8s-kubeconfig
ansible-playbook -i inventory/hosts k8s-worker.yml --tags k8s-kubeconfig
```

**確認ポイント**:

- 制御ノードの `~/.ansible/kubeconfig-cache` が存在し, 実行ユーザのみアクセス可能な権限で管理されていること。
- コントロールプレーンノード側のロール実行後にワーカーノード配布を実施していること。
- 再配布後にワーカーノードの `~/.kube/merged-kubeconfig.conf` が最新内容へ更新されていること。

## 注意事項

### スクリプト配置の確認

`create-embedded-kubeconfig.py` と `create-uniq-kubeconfig.py` は必ず `k8s_node_setup_tools_dir` に事前配置してください。未配置の場合はロール実行時にエラーになります。

### ロール実行順序の制約

`k8s_ctrl_plane` グループ以外でこのロールを実行すると, 埋め込み `kubeconfig` の生成はスキップされます。ワーカーノードへ配布する前に**必ずコントロールプレーンノードでロールを完了させてください**。

### ワーカーノードの必須変数

ワーカーノードごとの `k8s_ctrlplane_host` 変数は `host_vars/<worker>/` などで**必ず定義してください**。未定義の場合はタスクがエラーで停止します。

```yaml
# host_vars/k8sworker0101.local/main.yml
k8s_ctrlplane_host: k8sctrlplane01.local
```

### キャッシング機構と単発実行

`~/.ansible/kubeconfig-cache/` は制御ノードのユーザが所有し, パーミッション `0700` で管理される kubeconfig キャッシュです。以下の点に注意してください:

- 制御ノードでプレイブックを再実行すると, キャッシュから同一ファイルを再利用して効率化します。
- コントロールプレーンノードでロール実行をスキップした状態でワーカー配布のみを実行すると, 旧キャッシュが配布されます。**一貫性確保のため, コントロールプレーン処理 => ワーカー配布の順序を通常通り実行してください**。

### ファイルパーミッション

`merged-kubeconfig.conf` は `0600`(ユーザのみ読み取り可能)で配布されます。追加ユーザに読み取りを許可したい場合は, 別途 ACL やグループ管理を行ってください:

```bash
# ACL で別ユーザに読み取り許可
setfacl -m u:otheruser:r ~/.kube/merged-kubeconfig.conf
```

## 参考資料

### 公式ドキュメント

- [Kubernetes kubeconfig](https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/)
- [kubectl](https://kubernetes.io/docs/reference/kubectl/)
