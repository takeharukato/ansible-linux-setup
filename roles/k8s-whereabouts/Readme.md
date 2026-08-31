# k8s-whereabouts ロール

本ロールは, Kubernetes コントロールプレーンノードから Whereabouts を導入し, 検証用の Network Attachment Definition (NAD) を適用するロールです。

## 目次

- [k8s-whereabouts ロール](#k8s-whereabouts-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
    - [主な役割](#主な役割)
  - [前提条件](#前提条件)
    - [Whereabouts 本体の導入, および, 検証用 NAD 有効化条件](#whereabouts-本体の導入-および-検証用-nad-有効化条件)
    - [実行順序](#実行順序)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
    - [各ロール固有の利用者入力値](#各ロール固有の利用者入力値)
    - [設定例](#設定例)
      - [NAD の名前空間を変更する手順](#nad-の名前空間を変更する手順)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [検証の前提条件](#検証の前提条件)
    - [検証環境の設定](#検証環境の設定)
    - [検証コマンドと期待結果](#検証コマンドと期待結果)
      - [1. NAD 設定内容の確認](#1-nad-設定内容の確認)
      - [2. 検証用 Pod の生成と配置確認](#2-検証用-pod-の生成と配置確認)
      - [3. IPv4/IPv6 アドレス割り当て確認](#3-ipv4ipv6-アドレス割り当て確認)
      - [4. IPv4 双方向通信確認](#4-ipv4-双方向通信確認)
      - [5. IPv6 双方向通信確認](#5-ipv6-双方向通信確認)
      - [6. IP アドレス割り当て状態確認](#6-ip-アドレス割り当て状態確認)
      - [7. Pod 削除後の IP アドレス解放確認](#7-pod-削除後の-ip-アドレス解放確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. Whereabouts が導入されない場合](#1-whereabouts-が導入されない場合)
    - [2. Whereabouts は導入されるが検証用 NAD が生成されない場合](#2-whereabouts-は導入されるが検証用-nad-が生成されない場合)
    - [3. `net1` に IPv4 または IPv6 アドレスが設定されない場合](#3-net1-に-ipv4-または-ipv6-アドレスが設定されない場合)
    - [4. Pod 間通信に失敗する場合](#4-pod-間通信に失敗する場合)
  - [注意事項](#注意事項)
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
| kubectlコマンド | kubectl | Kubernetes API と通信してリソースを操作, 参照するコマンド。 |
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
| Red Hat Enterprise Linux | RHEL | Red Hatが提供する企業向けLinuxディストリビューション。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
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
| jqコマンド | jq | JSON 形式のデータから必要な項目だけを抽出して表示するコマンド。 |
| ipコマンド | - | ネットワーク設定や経路情報の確認, 変更を行うコマンド。 |
| helmコマンド | helm | Kubernetes向けパッケージの導入, 更新, 状態確認を実施するコマンド。 |
| IPPool | - | Whereabouts がネットワークごとの IP アドレス割り当て状態を記録する Kubernetes リソース。 |
| BusyBox | - | 基本的なコマンドを小さな実行環境へまとめて提供するソフトウェア。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
| サービス | - | 機能を利用者や他システムへ提供する仕組み。 |
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |

## 概要

本ロールは, Multus が導入された Kubernetes クラスタへ Whereabouts を導入します。Whereabouts の Helm による導入, 更新, 状態確認に必要な共通処理は `k8s-helm-common` ロールへ委譲し, 本ロールでは Whereabouts 固有の設定解決, 導入後検証, および検証用 Network Attachment Definition (NAD) `ipvlan-wb` の生成と適用を担当します。

検証用 NAD は, `k8s_nic` に対応するネットワークインタフェースの設定と Whereabouts の IP アドレス割り当て範囲が利用可能な場合だけ生成します。検証用 NAD の生成条件を満たさない場合でも, Whereabouts 本体の導入は継続します。

### 主な役割

- Whereabouts の導入に必要な設定値を解決します。
- Helm による Whereabouts の導入, 更新, 状態確認を `k8s-helm-common` ロールへ委譲します。
- Whereabouts の DaemonSet と Pod が利用可能な状態であることを確認します。
- 条件を満たす場合に, IPvLAN を使用する検証用 NAD `ipvlan-wb` を生成して `kube-system` 名前空間へ適用します。
- 検証用 NAD では, Whereabouts の `ipRanges` に IPv4 と IPv6 の割り当て範囲を設定できます。


## 前提条件

本ロールを実行する前に, 次の条件が満たされていることを確認します。

- Multus を導入する設定となっていること (`vars/all-config.yml`で, `k8s_multus_enabled`変数が`true`となっていること)。
- 対象 Kubernetes クラスタが構築済みであること。本ロールは, 次のロールが事前に完了していることを前提とします。
  - `k8s-common`: Kubernetes 共通設定を構成します。
  - `k8s-ctrlplane`: Kubernetes コントロールプレーンを構成します。
  - `k8s-multus`: Multus を導入します。
- Helm 操作用のユーザから対象 Kubernetes クラスタへアクセスできること。
- 検証用 NAD を生成する場合は, Kubernetesコントロールプレーンノードの `host_vars` 内に, `k8s_nic` に対応する `netif_list` のネットワーク設定が存在すること。
- 検証用 NAD で IPv4 を使用する場合は, IPv4 の開始アドレスと終了アドレスが設定されていること。
- 検証用 NAD で IPv6 を使用する場合は, IPv6 の開始アドレスと終了アドレスが設定されていること。

### Whereabouts 本体の導入, および, 検証用 NAD 有効化条件

Whereabouts 本体は, 次の両方を設定した場合に導入します。

- `k8s_multus_enabled: true`
- `k8s_whereabouts_enabled: true`

検証用 NAD `ipvlan-wb` は, Whereabouts 本体の有効化条件に加えて, `k8s_nic` に対応する `netif_list` の設定が存在し, IPv4 または IPv6 のネットワーク情報と対応する IP アドレス割り当て範囲が利用可能な場合に生成します。

検証用 NAD の生成条件を満たさない場合, 実行ログへ警告を出力して NAD の生成と検証だけを省略し, Whereabouts 本体の導入と検証は継続します。

### 実行順序

本ロールは, 次の順序で関連ロールが実行されていることを前提とします。

1. `k8s-common`
2. `k8s-ctrlplane`
3. `k8s-multus`
4. `k8s-whereabouts`

## 実行方法

制御ホストで次のコマンドを実行します。

```bash
make run_k8s_whereabouts
```

または,

```bash
ansible-playbook -i inventory/hosts site.yml --tags "k8s-whereabouts"
```

## 主要変数

### 各ロール固有の利用者入力値

本節では, 利用者が Whereabouts の有効化, 版数, および検証用 NAD の IP アドレス割り当て範囲を設定するために使用する主要変数を示します。Helm 共通処理へ渡す内部変数と実行時に算出する変数は記載しません。

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `k8s_whereabouts_enabled` | Whereabouts の導入を有効にします。 | `false` | `true` |
| `k8s_whereabouts_version` | 導入する Whereabouts の版数を指定します。Helm Chart の版数は本値から内部的に決定します。 | `"0.9.2"` | `"0.9.2"` |
| `k8s_whereabouts_ipv4_range_start` | 検証用 NAD で払い出す IPv4 アドレス範囲の開始アドレスを指定します。 | `""` | `"192.168.40.100"` |
| `k8s_whereabouts_ipv4_range_end` | 検証用 NAD で払い出す IPv4 アドレス範囲の終了アドレスを指定します。 | `""` | `"192.168.40.254"` |
| `k8s_whereabouts_ipv6_range_start` | 検証用 NAD で払い出す IPv6 アドレス範囲の開始アドレスを指定します。 | `""` | `"fd69:6684:61a:2::100"` |
| `k8s_whereabouts_ipv6_range_end` | 検証用 NAD で払い出す IPv6 アドレス範囲の終了アドレスを指定します。 | `""` | `"fd69:6684:61a:2::ffff"` |

検証用 NAD の接続先ネットワークは, 共通ネットワーク設定の `k8s_nic` と, `k8s_nic` に対応する `netif_list` の静的 IP アドレスおよびプレフィックス長から決定します。

### 設定例

IPv4 と IPv6 の両方を使用する場合の設定例を示します。

```yaml
1: k8s_whereabouts_enabled: true
2: k8s_whereabouts_version: "0.9.2"
3: k8s_whereabouts_ipv4_range_start: "192.168.40.100"
4: k8s_whereabouts_ipv4_range_end: "192.168.40.254"
5: k8s_whereabouts_ipv6_range_start: "fd69:6684:61a:2::100"
6: k8s_whereabouts_ipv6_range_end: "fd69:6684:61a:2::ffff"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `k8s_whereabouts_enabled: true` | Whereabouts の導入を有効にします。 | `false` の場合は本ロールの Whereabouts 導入処理を実行しないためです。 |
| 2 | `k8s_whereabouts_version: "0.9.2"` | 指定した版数の Whereabouts を導入します。 | 対象環境で使用する Whereabouts の版数を明示し, 意図しない版数の導入を防ぐためです。 |
| 3-4 | IPv4 の開始アドレスと終了アドレス | 検証用 NAD から IPv4 アドレスを払い出せるようにします。 | 範囲が未設定の場合は IPv4 を検証用 NAD の払い出し対象にできず, 既存機器のアドレス範囲と重複する値を設定した場合はアドレス競合が発生するためです。 |
| 5-6 | IPv6 の開始アドレスと終了アドレス | 検証用 NAD から IPv6 アドレスを払い出せるようにします。 | 範囲が未設定の場合は IPv6 を検証用 NAD の払い出し対象にできず, 既存機器のアドレス範囲と重複する値を設定した場合はアドレス競合が発生するためです。 |

#### NAD の名前空間を変更する手順

検証用 NAD `ipvlan-wb` は `kube-system` 名前空間へ生成します。名前空間を変更する場合は, `templates/ipvlan-wb-nad.yml.j2` の `metadata.namespace` だけでなく, NAD 名と名前空間を参照するロール内の処理および利用側 Pod の `k8s.v1.cni.cncf.io/networks` Annotation も同時に変更する必要があります。

別の名前空間にある NAD を Pod から参照する場合は, `名前空間/NAD名` の形式で指定します。例えば, `kube-system` 名前空間の `ipvlan-wb` を `default` 名前空間の Pod から参照する場合は, 次のように指定します。

```yaml
1: metadata:
2:   annotations:
3:     k8s.v1.cni.cncf.io/networks: kube-system/ipvlan-wb
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1-3 | `k8s.v1.cni.cncf.io/networks: kube-system/ipvlan-wb` | `default` 名前空間の Pod から `kube-system` 名前空間の NAD `ipvlan-wb` を参照します。 | 別名前空間の NAD を参照する場合に名前空間を省略すると, Pod と同じ名前空間の NAD を参照するためです。 |

## テンプレートと生成ファイル

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `templates/ipvlan-wb-nad.yml.j2` | `{{ k8s_whereabouts_config_dir }}/ipvlan-wb-nad.yml` (既定: `/home/ansible/kubeadm/whereabouts/ipvlan-wb-nad.yml`) | IPvLAN と Whereabouts を使用する検証用 NAD を生成します。`ipRanges` に IPv4 と IPv6 の割り当て範囲を設定できます。 |

## 実行フロー

本ロールは次の順序で処理を実行します。

1. `load-params.yml` で共通設定を読み込みます。
2. `resolve-runtime-vars.yml` で検証用 NAD の接続先ネットワークと Whereabouts の導入情報を解決します。
3. `package.yml`, `directory.yml`, `user_group.yml`, `service.yml` を実行します。
4. `config-whereabouts.yml` で Kubernetes API が利用可能になるまで待機します。
5. `helm.yml` から `k8s-helm-common` ロールを呼び出し, Whereabouts の Helm Chart を事前描画した後, 導入または更新し, Helm release が `deployed` 状態になるまで確認します。
6. 検証用 NAD の生成条件を満たす場合は, `ipvlan-wb-nad.yml.j2` から NAD 設定ファイルを生成し, `kube-system` 名前空間へ適用します。
7. `verify.yml` で Whereabouts の Helm release, DaemonSet, Pod, および生成条件を満たす場合は NAD を検証します。

検証用 NAD の生成条件を満たさない場合は, NAD の生成と検証だけを省略し, Whereabouts 本体の導入と検証は継続します。

## 検証ポイント

### 検証の前提条件

検証を始める前に, 次の条件が満たされていることを確認します。

- `k8s-whereabouts` ロールの実行が正常終了していること。
- `kube-system` 名前空間に NAD `ipvlan-wb` が存在すること。
- `k8sworker0101` と `k8sworker0102` に `k8s_nic` に対応するネットワークインタフェース(本節の例では, `ens192`を例として使用)が存在し, 同一の IPv4/IPv6 ネットワークへ接続されていること。
- 対象ホストとなるKubernetesのコントロールプレーンノードから `kubectl` コマンドで対象 Kubernetes クラスタを操作できること。
- 対象ホストとなるKubernetesのコントロールプレーンノードで `jq` コマンドを使用できること。

### 検証環境の設定

本節では, 検証用の設定内容について説明します。

検証用 Pod は `default` 名前空間へ作成し, `kube-system` 名前空間の NAD `ipvlan-wb` を使用します。2 個の Pod を異なるワーカノードへ配置することで, IPvLAN の追加ネットワークを使用したノード間通信を確認します。

`/tmp/whereabouts-test.yaml` を次の内容で作成します。

```yaml
1: apiVersion: v1
2: kind: Pod
3: metadata:
4:   name: whereabouts-test-1
5:   namespace: default
6:   annotations:
7:     k8s.v1.cni.cncf.io/networks: kube-system/ipvlan-wb
8: spec:
9:   nodeName: k8sworker0101
10:   containers:
11:     - name: test
12:       image: busybox:1.36
13:       command:
14:         - /bin/sh
15:         - -c
16:         - sleep infinity
17: ---
18: apiVersion: v1
19: kind: Pod
20: metadata:
21:   name: whereabouts-test-2
22:   namespace: default
23:   annotations:
24:     k8s.v1.cni.cncf.io/networks: kube-system/ipvlan-wb
25: spec:
26:   nodeName: k8sworker0102
27:   containers:
28:     - name: test
29:       image: busybox:1.36
30:       command:
31:         - /bin/sh
32:         - -c
33:         - sleep infinity
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 4-7 | `whereabouts-test-1`, `default`, `kube-system/ipvlan-wb` | 1 個目の検証用 Pod を `default` 名前空間へ作成し, `kube-system` 名前空間の NAD を使用します。 | Pod と NAD の名前空間が異なるため, NAD の名前空間を含めて指定する必要があります。 |
| 9 | `nodeName: k8sworker0101` | 1 個目の Pod を `k8sworker0101` へ配置します。 | 2 個の Pod を異なるノードへ配置し, ノード間通信を確認するためです。 |
| 11-16 | `busybox:1.36` と `sleep infinity` | 通信確認に使用できる Pod を継続して実行します。 | 検証中に Pod が終了すると通信確認を実施できないためです。 |
| 21-24 | `whereabouts-test-2`, `default`, `kube-system/ipvlan-wb` | 2 個目の検証用 Pod を `default` 名前空間へ作成し, `kube-system` 名前空間の NAD を使用します。 | 1 個目と同じ追加ネットワークへ接続して相互通信を確認するためです。 |
| 26 | `nodeName: k8sworker0102` | 2 個目の Pod を `k8sworker0102` へ配置します。 | 1 個目と異なるノードへ配置し, ノード間通信を確認するためです。 |
| 28-33 | `busybox:1.36` と `sleep infinity` | 2 個目の通信確認用 Pod を継続して実行します。 | 検証中に Pod が終了すると通信確認を実施できないためです。 |

実際にファイルを作成する場合は, 次のコマンドを使用できます。

```bash
cat <<'EOF' > /tmp/whereabouts-test.yaml
apiVersion: v1
kind: Pod
metadata:
  name: whereabouts-test-1
  namespace: default
  annotations:
    k8s.v1.cni.cncf.io/networks: kube-system/ipvlan-wb
spec:
  nodeName: k8sworker0101
  containers:
    - name: test
      image: busybox:1.36
      command:
        - /bin/sh
        - -c
        - sleep infinity
---
apiVersion: v1
kind: Pod
metadata:
  name: whereabouts-test-2
  namespace: default
  annotations:
    k8s.v1.cni.cncf.io/networks: kube-system/ipvlan-wb
spec:
  nodeName: k8sworker0102
  containers:
    - name: test
      image: busybox:1.36
      command:
        - /bin/sh
        - -c
        - sleep infinity
EOF
```

### 検証コマンドと期待結果

#### 1. NAD 設定内容の確認

**実施対象ホスト**: 対象ホストとなるKubernetesのコントロールプレーンノード

**実行するコマンド**:

```bash
kubectl -n kube-system \
  get network-attachment-definition ipvlan-wb \
  -o jsonpath='{.spec.config}' \
  | jq .
```

**期待される出力**:

```json
{
  "cniVersion": "0.3.1",
  "type": "ipvlan",
  "master": "ens192",
  "mode": "l2",
  "ipam": {
    "type": "whereabouts",
    "ipRanges": [
      {
        "range": "192.168.40.41/24",
        "range_start": "192.168.40.100",
        "range_end": "192.168.40.254"
      },
      {
        "range": "fd69:6684:61a:2::41/64",
        "range_start": "fd69:6684:61a:2::100",
        "range_end": "fd69:6684:61a:2::ffff"
      }
    ]
  }
}
```

**実行結果の例**:

```bash
$ kubectl -n kube-system \
    get network-attachment-definition ipvlan-wb \
    -o jsonpath='{.spec.config}' \
    | jq .
{
  "cniVersion": "0.3.1",
  "type": "ipvlan",
  "master": "ens192",
  "mode": "l2",
  "ipam": {
    "type": "whereabouts",
    "ipRanges": [
      {
        "range": "192.168.40.41/24",
        "range_start": "192.168.40.100",
        "range_end": "192.168.40.254"
      },
      {
        "range": "fd69:6684:61a:2::41/64",
        "range_start": "fd69:6684:61a:2::100",
        "range_end": "fd69:6684:61a:2::ffff"
      }
    ],
    "log_file": "/var/log/whereabouts.log",
    "log_level": "info"
  }
}
```

**確認ポイント**:

- `mode` が `l2` であることを確認することで, 検証用 NAD が IPvLAN の L2 動作を使用する設定であることを確認します。
- `ipam.type` が `whereabouts` であることを確認することで, Whereabouts が IP アドレス割り当てに使用されることを確認します。
- `ipRanges` に IPv4 と IPv6 の 2 個の範囲が存在することを確認することで, IPv4/IPv6 の両方を払い出す設定であることを確認します。

#### 2. 検証用 Pod の生成と配置確認

**実施対象ホスト**: 対象ホストとなるKubernetesのコントロールプレーンノード

**実行するコマンド**:

```bash
kubectl apply -f /tmp/whereabouts-test.yaml
kubectl -n default \
  get pod \
  whereabouts-test-1 whereabouts-test-2 \
  -o wide
```

**期待される出力**:

```text
pod/whereabouts-test-1 created
pod/whereabouts-test-2 created
NAME                 READY   STATUS    RESTARTS   AGE   IP                         NODE
whereabouts-test-1   1/1     Running   0          ...   ...                        k8sworker0101
whereabouts-test-2   1/1     Running   0          ...   ...                        k8sworker0102
```

**実行結果の例**:

```bash
$ kubectl apply -f /tmp/whereabouts-test.yaml
pod/whereabouts-test-1 created
pod/whereabouts-test-2 created
$ kubectl -n default \
    get pod \
    whereabouts-test-1 whereabouts-test-2 \
    -o wide
NAME                 READY   STATUS    RESTARTS   AGE   IP                         NODE            NOMINATED NODE   READINESS GATES
whereabouts-test-1   1/1     Running   0          26s   fdb6:6e92:3cfb:201::923    k8sworker0101   <none>           <none>
whereabouts-test-2   1/1     Running   0          26s   fdb6:6e92:3cfb:202::43b8   k8sworker0102   <none>           <none>
```

**確認ポイント**:

- `STATUS` が両 Pod とも `Running` であることを確認することで, 検証用 Pod が正常に起動したことを確認します。
- `NODE` が `whereabouts-test-1` では `k8sworker0101`, `whereabouts-test-2` では `k8sworker0102` であることを確認することで, 異なるワーカノードへ配置されたことを確認します。

#### 3. IPv4/IPv6 アドレス割り当て確認

**実施対象ホスト**: 対象ホストとなるKubernetesのコントロールプレーンノード

**実行するコマンド**:

```bash
kubectl -n default \
  get pod whereabouts-test-1 \
  -o jsonpath='{.metadata.annotations.k8s\.v1\.cni\.cncf\.io/network-status}' \
  | jq .
kubectl -n default \
  get pod whereabouts-test-2 \
  -o jsonpath='{.metadata.annotations.k8s\.v1\.cni\.cncf\.io/network-status}' \
  | jq .
kubectl -n default \
  exec whereabouts-test-1 -- \
  ip addr show dev net1
kubectl -n default \
  exec whereabouts-test-2 -- \
  ip addr show dev net1
```

**期待される出力**:

`network-status` の `kube-system/ipvlan-wb` に対応する `ips` に IPv4 と IPv6 の両方が表示され, `ip addr show dev net1` に同じ IPv4/IPv6 アドレスが表示されます。

**実行結果の例**:

```bash
$ kubectl -n default \
    get pod whereabouts-test-1 \
    -o jsonpath='{.metadata.annotations.k8s\.v1\.cni\.cncf\.io/network-status}' \
    | jq .
[
  {
    "name": "cilium",
    "interface": "eth0",
    "ips": [
      "fdb6:6e92:3cfb:201::923",
      "10.244.1.182"
    ],
    "mac": "e6:11:8a:fd:4d:05",
    "default": true,
    "dns": {},
    "gateway": [
      "fdb6:6e92:3cfb:201::1d83",
      "10.244.1.13"
    ]
  },
  {
    "name": "kube-system/ipvlan-wb",
    "interface": "net1",
    "ips": [
      "192.168.40.101",
      "fd69:6684:61a:2::101"
    ],
    "mac": "00:50:56:00:7b:7b",
    "dns": {}
  }
]
$ kubectl -n default \
    get pod whereabouts-test-2 \
    -o jsonpath='{.metadata.annotations.k8s\.v1\.cni\.cncf\.io/network-status}' \
    | jq .
[
  {
    "name": "cilium",
    "interface": "eth0",
    "ips": [
      "fdb6:6e92:3cfb:202::43b8",
      "10.244.2.98"
    ],
    "mac": "4e:de:0d:82:69:70",
    "default": true,
    "dns": {},
    "gateway": [
      "fdb6:6e92:3cfb:202::54ac",
      "10.244.2.194"
    ]
  },
  {
    "name": "kube-system/ipvlan-wb",
    "interface": "net1",
    "ips": [
      "192.168.40.100",
      "fd69:6684:61a:2::100"
    ],
    "mac": "00:50:56:00:bf:7b",
    "dns": {}
  }
]
$ kubectl -n default \
    exec whereabouts-test-1 -- \
    ip addr show dev net1
2: net1@if3: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue
    link/ether 00:50:56:00:7b:7b brd ff:ff:ff:ff:ff:ff
    inet 192.168.40.101/24 brd 192.168.40.255 scope global net1
       valid_lft forever preferred_lft forever
    inet6 fd69:6684:61a:2::101/64 scope global
       valid_lft forever preferred_lft forever
    inet6 fe80::50:5600:100:7b7b/64 scope link
       valid_lft forever preferred_lft forever
$ kubectl -n default \
    exec whereabouts-test-2 -- \
    ip addr show dev net1
2: net1@if3: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue
    link/ether 00:50:56:00:bf:7b brd ff:ff:ff:ff:ff:ff
    inet 192.168.40.100/24 brd 192.168.40.255 scope global net1
       valid_lft forever preferred_lft forever
    inet6 fd69:6684:61a:2::100/64 scope global
       valid_lft forever preferred_lft forever
    inet6 fe80::50:5600:100:bf7b/64 scope link
       valid_lft forever preferred_lft forever
```
**確認ポイント**:

- `kube-system/ipvlan-wb` の `interface` が `net1` であることを確認することで, 検証用 NAD による追加ネットワークが生成されたことを確認します。
- `whereabouts-test-1` の `net1` に IPv4アドレス (`192.168.40.101`) と IPv6アドレス (`fd69:6684:61a:2::101`) が設定されていることを確認します。
- `whereabouts-test-2` の `net1` に IPv4アドレス (`192.168.40.100`) と IPv6アドレス ( `fd69:6684:61a:2::100`) が設定されていることを確認します。

#### 4. IPv4 双方向通信確認

**実施対象ホスト**: 対象ホストとなるKubernetesのコントロールプレーンノード

**実行するコマンド**:

```bash
kubectl -n default \
  exec whereabouts-test-1 -- \
  ping -c 3 192.168.40.100
kubectl -n default \
  exec whereabouts-test-2 -- \
  ping -c 3 192.168.40.101
```

**期待される出力**:

両方向の `ping` コマンドで `3 packets transmitted, 3 packets received, 0% packet loss` と表示されます。

**実行結果の例**:

```bash
$ kubectl -n default exec whereabouts-test-1 -- ping -c 3 192.168.40.100
PING 192.168.40.100 (192.168.40.100): 56 data bytes
64 bytes from 192.168.40.100: seq=0 ttl=64 time=0.692 ms
64 bytes from 192.168.40.100: seq=1 ttl=64 time=0.210 ms
64 bytes from 192.168.40.100: seq=2 ttl=64 time=0.517 ms

--- 192.168.40.100 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.210/0.473/0.692 ms
$ kubectl -n default exec whereabouts-test-2 -- ping -c 3 192.168.40.101
PING 192.168.40.101 (192.168.40.101): 56 data bytes
64 bytes from 192.168.40.101: seq=0 ttl=64 time=0.327 ms
64 bytes from 192.168.40.101: seq=1 ttl=64 time=0.176 ms
64 bytes from 192.168.40.101: seq=2 ttl=64 time=0.201 ms

--- 192.168.40.101 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.176/0.234/0.327 ms
```

**確認ポイント**:

- 両方向で `0% packet loss` と表示されることを確認することで, 異なるワーカノード上の Pod 間で IPv4 通信が成立していることを確認します。

#### 5. IPv6 双方向通信確認

**実施対象ホスト**: 対象ホストとなるKubernetesのコントロールプレーンノード

**実行するコマンド**:

```bash
kubectl -n default \
  exec whereabouts-test-1 -- \
  ping -6 -c 3 fd69:6684:61a:2::100
kubectl -n default \
  exec whereabouts-test-2 -- \
  ping -6 -c 3 fd69:6684:61a:2::101
```

**期待される出力**:

両方向の `ping` コマンドで `3 packets transmitted, 3 packets received, 0% packet loss` と表示されます。

**実行結果の例**:

```bash
$ kubectl -n default exec whereabouts-test-1 -- ping -6 -c 3 fd69:6684:61a:2::100
PING fd69:6684:61a:2::100 (fd69:6684:61a:2::100): 56 data bytes
64 bytes from fd69:6684:61a:2::100: seq=0 ttl=64 time=0.603 ms
64 bytes from fd69:6684:61a:2::100: seq=1 ttl=64 time=0.210 ms
64 bytes from fd69:6684:61a:2::100: seq=2 ttl=64 time=0.146 ms

--- fd69:6684:61a:2::100 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.146/0.319/0.603 ms
$ kubectl -n default exec whereabouts-test-2 -- ping -6 -c 3 fd69:6684:61a:2::101
PING fd69:6684:61a:2::101 (fd69:6684:61a:2::101): 56 data bytes
64 bytes from fd69:6684:61a:2::101: seq=0 ttl=64 time=0.263 ms
64 bytes from fd69:6684:61a:2::101: seq=1 ttl=64 time=0.203 ms
64 bytes from fd69:6684:61a:2::101: seq=2 ttl=64 time=0.170 ms

--- fd69:6684:61a:2::101 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.170/0.212/0.263 ms
```

**確認ポイント**:

- 両方向で `0% packet loss` と表示されることを確認することで, 異なるワーカノード上の Pod 間で IPv6 通信が成立していることを確認します。

#### 6. IP アドレス割り当て状態確認

**実施対象ホスト**: 対象ホストとなるKubernetesのコントロールプレーンノード

**実行するコマンド**:

```bash
kubectl get ippools.whereabouts.cni.cncf.io \
  -A \
  -o yaml
```

**期待される出力**:

IPv4 と IPv6 の IPPool の `spec.allocations` に `default/whereabouts-test-1` と `default/whereabouts-test-2` が表示されます。

**実行結果の例**:

```yaml
$ kubectl get ippools.whereabouts.cni.cncf.io \
    -A \
    -o yaml
apiVersion: v1
items:
- apiVersion: whereabouts.cni.cncf.io/v1alpha1
  kind: IPPool
  metadata:
    creationTimestamp: "2026-08-26T10:49:10Z"
    generation: 11
    name: 192.168.40.0-24
    namespace: kube-system
    resourceVersion: "2325073"
    uid: 07d54d36-5328-4407-a664-51bf8b2a2315
  spec:
    allocations:
      "100":
        id: c451f9c9febef58007dd3ff8945350da924f7b2340d176acb2eb3fb32555f35e
        ifname: net1
        podref: default/whereabouts-test-2
      "101":
        id: edd5acc52e3065665d37a1e9df857fc728fa76db4e1351a5a371b5e65738deef
        ifname: net1
        podref: default/whereabouts-test-1
    range: 192.168.40.0/24
- apiVersion: whereabouts.cni.cncf.io/v1alpha1
  kind: IPPool
  metadata:
    creationTimestamp: "2026-08-26T11:16:01Z"
    generation: 7
    name: fd69-6684-61a-2---64
    namespace: kube-system
    resourceVersion: "2325075"
    uid: 1238ffe4-5539-46d4-b640-c2f5f9e33564
  spec:
    allocations:
      "256":
        id: c451f9c9febef58007dd3ff8945350da924f7b2340d176acb2eb3fb32555f35e
        ifname: net1
        podref: default/whereabouts-test-2
      "257":
        id: edd5acc52e3065665d37a1e9df857fc728fa76db4e1351a5a371b5e65738deef
        ifname: net1
        podref: default/whereabouts-test-1
    range: fd69:6684:61a:2::/64
kind: List
metadata:
  resourceVersion: ""
```

**確認ポイント**:

- IPv4 の IPPool に `default/whereabouts-test-1` と `default/whereabouts-test-2` が存在することを確認することで, IPv4 アドレスの割り当て状態が記録されていることを確認します。
- IPv6 の IPPool に同じ 2 Pod が存在することを確認することで, IPv6 アドレスの割り当て状態が記録されていることを確認します。

#### 7. Pod 削除後の IP アドレス解放確認

**実施対象ホスト**: 対象ホストとなるKubernetesのコントロールプレーンノード

**実行するコマンド**:

```bash
kubectl -n default \
  delete pod whereabouts-test-1 whereabouts-test-2
kubectl -n default \
  get pod whereabouts-test-1 whereabouts-test-2
kubectl get ippools.whereabouts.cni.cncf.io \
  -n kube-system \
  192.168.40.0-24 \
  -o yaml
kubectl get ippools.whereabouts.cni.cncf.io \
  -n kube-system \
  fd69-6684-61a-2---64 \
  -o yaml
```

**期待される出力**:

Pod 削除後は 2 Pod が `NotFound` となり, IPv4 と IPv6 の両方の IPPool で `spec.allocations: {}` と表示されます。

**実行結果の例**:

```bash
$ kubectl -n default \
    delete pod whereabouts-test-1 whereabouts-test-2
pod "whereabouts-test-1" deleted
pod "whereabouts-test-2" deleted
$ kubectl -n default \
    get pod whereabouts-test-1 whereabouts-test-2
Error from server (NotFound): pods "whereabouts-test-1" not found
Error from server (NotFound): pods "whereabouts-test-2" not found
$ kubectl get ippools.whereabouts.cni.cncf.io \
    -n kube-system \
    192.168.40.0-24 \
    -o yaml
apiVersion: whereabouts.cni.cncf.io/v1alpha1
kind: IPPool
metadata:
  creationTimestamp: "2026-08-26T10:49:10Z"
  generation: 13
  name: 192.168.40.0-24
  namespace: kube-system
  resourceVersion: "2327277"
  uid: 07d54d36-5328-4407-a664-51bf8b2a2315
spec:
  allocations: {}
  range: 192.168.40.0/24
$ kubectl get ippools.whereabouts.cni.cncf.io \
    -n kube-system \
    fd69-6684-61a-2---64 \
    -o yaml
apiVersion: whereabouts.cni.cncf.io/v1alpha1
kind: IPPool
metadata:
  creationTimestamp: "2026-08-26T11:16:01Z"
  generation: 9
  name: fd69-6684-61a-2---64
  namespace: kube-system
  resourceVersion: "2327280"
  uid: 1238ffe4-5539-46d4-b640-c2f5f9e33564
spec:
  allocations: {}
  range: fd69:6684:61a:2::/64
```

**確認ポイント**:

- `kubectl get pod` の実行結果で 2 Pod が `NotFound` となることを確認することで, 検証用 Pod が削除されたことを確認します。
- IPv4 と IPv6 の両方の IPPool で `allocations: {}` と表示されることを確認することで, Pod に割り当てられていた IP アドレスが解放されたことを確認します。

## トラブルシューティング

### 1. Whereabouts が導入されない場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:


1. 必須変数の定義を確認
    ```bash
    grep -E 'k8s_(multus|whereabouts)_enabled' host_vars/*.yml vars/all-config.yml
    ```
2. 本ロールの再実行
    ```bash
    make run_k8s_whereabouts
    ```

    または,

    ```bash
    ansible-playbook -i inventory/hosts site.yml --tags "k8s-whereabouts"
    ```

**確認ポイント**:

- `k8s_multus_enabled` と `k8s_whereabouts_enabled` がともに `true` であることを確認することで, Whereabouts 本体の実行条件が満たされていることを確認します。
- Playbook の実行結果に Whereabouts の Helm 導入失敗がないことを確認します。

### 2. Whereabouts は導入されるが検証用 NAD が生成されない場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
ansible-playbook -i inventory/hosts site.yml --tags "k8s-whereabouts"
```

**実施対象ホスト**: 対象ホストとなるKubernetesのコントロールプレーンノード

**実行するコマンド**:

```bash
kubectl -n kube-system get network-attachment-definition ipvlan-wb
```

**確認ポイント**:

- Playbook の実行結果に `k8s_nic is not configured` または `No netif_list entry matches k8s_nic` の警告が表示されていないことを確認することで, NAD の接続先ネットワークが解決されていることを確認します。
- IPv4 または IPv6 のネットワーク情報と対応する開始アドレス, 終了アドレスが設定されていることを確認します。

### 3. `net1` に IPv4 または IPv6 アドレスが設定されない場合

**実施対象ホスト**: 対象ホストとなるKubernetesのコントロールプレーンノード

**実行するコマンド**:

```bash
kubectl -n kube-system \
  get network-attachment-definition ipvlan-wb \
  -o jsonpath='{.spec.config}' \
  | jq .
kubectl -n default \
  get pod whereabouts-test-1 \
  -o jsonpath='{.metadata.annotations.k8s\.v1\.cni\.cncf\.io/network-status}' \
  | jq .
```

**確認ポイント**:

- NAD の `ipRanges` に使用するアドレス種別の `range`, `range_start`, `range_end` が存在することを確認することで, Whereabouts へ払い出し範囲が渡されていることを確認します。
- `network-status` の `kube-system/ipvlan-wb` に対応する `ips` に必要な IPv4/IPv6 アドレスが存在することを確認します。

### 4. Pod 間通信に失敗する場合

**実施対象ホスト**: 対象ホストとなるKubernetesのコントロールプレーンノード

**実行するコマンド**:

```bash
kubectl -n default exec whereabouts-test-1 -- ip addr show dev net1
kubectl -n default exec whereabouts-test-2 -- ip addr show dev net1
kubectl -n default exec whereabouts-test-1 -- ping -c 3 192.168.40.100
kubectl -n default exec whereabouts-test-1 -- ping -6 -c 3 fd69:6684:61a:2::100
```

**確認ポイント**:

- 両 Pod の `net1` に同じ IPv4/IPv6 ネットワークの異なるアドレスが設定されていることを確認します。
- `ping` コマンドで応答がない場合は, `k8s_nic` に対応するネットワークインタフェースが両ワーカノードで同じネットワークへ接続されていることを確認します。

## 注意事項

- `k8s_multus_enabled: true` と `k8s_whereabouts_enabled: true` の両方を設定した場合に Whereabouts 本体を導入します。
- 検証用 NAD `ipvlan-wb` は, Whereabouts 本体の導入条件とは別に, `k8s_nic` に対応するネットワーク設定と IPv4 または IPv6 の割り当て範囲が利用可能な場合だけ生成します。
- 検証用 NAD の生成条件を満たさない場合でも, Whereabouts 本体の導入と検証は継続します。
- IPv4/IPv6 の割り当て範囲は, 対象ネットワークで他の機器が使用するアドレスと重複しない値を指定してください。
- `ipvlan-wb` は本ロールの動作確認に使用する NAD です。利用環境のアプリケーション用 NAD は, 利用目的に合わせて別途定義してください。

## 参考資料

### 公式ドキュメント

- [Whereabouts](https://github.com/k8snetworkplumbingwg/whereabouts)
- [Multus](https://github.com/k8snetworkplumbingwg/multus-cni)
- [Multus NetworkAttachmentDefinition configuration](https://github.com/k8snetworkplumbingwg/multus-cni/blob/master/docs/configuration.md)
- [kubectlコマンド](https://kubernetes.io/docs/concepts/overview/kubectl/)
- [Helm Commands](https://helm.sh/docs/v3/helm/)
- [helm list](https://helm.sh/docs/v3/helm/helm_list/)
- [jq Manual](https://jqlang.org/manual/)
- [BusyBox](https://busybox.net/BusyBox.html)
- [ipコマンド](https://man7.org/linux/man-pages/man8/ip.8.html)

### 関連ロール

- [roles/k8s-multus/Readme.md](../k8s-multus/Readme.md) Multus の導入仕様と追加ネットワーク設定を記載しています。
