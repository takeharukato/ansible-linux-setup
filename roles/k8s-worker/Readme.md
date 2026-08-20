# k8s-worker ロール

本ロールは, Kubernetes ワーカーノードを Kubernetes クラスタへ参加させるためのロールです。

## 目次

- [k8s-worker ロール](#k8s-worker-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
    - [API 待機設定](#api-待機設定)
    - [containerd 待機設定](#containerd-待機設定)
    - [Kubernetes オペレータユーザ設定](#kubernetes-オペレータユーザ設定)
    - [セットアップツール配置先](#セットアップツール配置先)
    - [ワーカーノード固有設定](#ワーカーノード固有設定)
    - [ファイアウォール / NodePort 設定](#ファイアウォール--nodeport-設定)
    - [CPU / systemd スライス設定](#cpu--systemd-スライス設定)
    - [Cilium BGP Control Plane 設定](#cilium-bgp-control-plane-設定)
  - [設定例](#設定例)
    - [基本設定](#基本設定)
    - [低遅延構成](#低遅延構成)
    - [Cilium BGP Control Plane 有効構成](#cilium-bgp-control-plane-有効構成)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
    - [ハンドラ処理](#ハンドラ処理)
    - [OS 差異](#os-差異)
      - [ファイアウォール設定の差異](#ファイアウォール設定の差異)
      - [GRUB 更新方法の差異](#grub-更新方法の差異)
  - [検証ポイント](#検証ポイント)
    - [前提条件](#前提条件-1)
    - [1. Kubernetes ノード登録状態の確認](#1-kubernetes-ノード登録状態の確認)
    - [2. kubelet サービス状態の確認](#2-kubelet-サービス状態の確認)
    - [3. kubelet ログの確認](#3-kubelet-ログの確認)
    - [4. CPU 予約設定の確認 (低遅延構成時)](#4-cpu-予約設定の確認-低遅延構成時)
    - [5. CPU 割り当て固定サービスの確認 (低遅延構成時)](#5-cpu-割り当て固定サービスの確認-低遅延構成時)
    - [6. Cilium BGP Control Plane リソースの確認 (Cilium BGP Control Plane 有効構成時)](#6-cilium-bgp-control-plane-リソースの確認-cilium-bgp-control-plane-有効構成時)
    - [7. ファイアウォール設定の確認 (`enable_firewall: true` の場合)](#7-ファイアウォール設定の確認-enable_firewall-true-の場合)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. k8s-worker の実処理がスキップされる場合](#1-k8s-worker-の実処理がスキップされる場合)
    - [2. kubeadm join が失敗する場合](#2-kubeadm-join-が失敗する場合)
    - [3. Cilium BGP Control Plane のマニフェスト生成で失敗する場合](#3-cilium-bgp-control-plane-のマニフェスト生成で失敗する場合)
    - [4. Cilium BGP Control Plane の適用で resource type エラーが出る場合](#4-cilium-bgp-control-plane-の適用で-resource-type-エラーが出る場合)
    - [5. ファイアウォール関連タスクが失敗する場合](#5-ファイアウォール関連タスクが失敗する場合)
    - [6. 低遅延化タスクが実行されない場合](#6-低遅延化タスクが実行されない場合)
    - [7. リブート後にノードが Ready へ戻らない場合](#7-リブート後にノードが-ready-へ戻らない場合)
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
| ワーカーノード ( Worker Node ) | - | Kubernetes クラスタで実際にアプリケーション(ポッド ( Pod ))が実行されるノード。kubelet と呼ばれるエージェントが動作し, コントロールプレーンノードからの指示に基づいてコンテナを実行管理します。 |
| kube-apiserver | - | KubernetesのAPIリクエストを受け付け, etcdへの読み書きを仲介するコンポーネント。 |
| kube-controller-manager | - | Deployment, ReplicaSetなど各種コントローラを実行し, Kubernetesクラスタの状態を監視, 調整するコンポーネント。 |
| kube-scheduler | - | 新規作成されたPodを適切なNodeへ配置するコンポーネント。 |
| kubelet | - | 各Node上で動作し, Podの起動, 停止, 監視を行うエージェント。 |
| kube-proxy | - | 各Node上でServiceのネットワークルールを管理するコンポーネント。 |
| etcd | - | KubernetesのKubernetesクラスタ状態を保存する分散Key-Valueストア。 |
| Container Network Interface | CNI | コンテナ間のネットワーク接続を標準化するプラグイン仕様。 |
| Cilium | - | eBPFを活用した高性能なCNIプラグイン。ネットワークポリシーやサービスメッシュ機能を提供します。 |
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
| Uncomplicated Firewall | UFW | 簡易な操作で設定できるパケット制御機能。 |
| Border Gateway Protocol | BGP | 自律システム間で経路情報を交換する経路制御方式。 |
| Cilium BGP Control Plane | - | Cilium が提供する BGP 連携機能。Kubernetes ノード情報や Service 情報に基づく経路広告を外部ルータへ配布するために利用します。 |
| CiliumBGPAdvertisement | - | Cilium BGP Control Plane で広告対象のプレフィックスや属性を定義するカスタムリソース。 |
| CiliumBGPPeerConfig | - | Cilium BGP Control Plane で BGP ピアとのセッション設定を定義するカスタムリソース。 |
| CiliumBGPClusterConfig | - | Cilium BGP Control Plane で Kubernetes ノード単位の BGP 構成を定義するカスタムリソース。 |
| NodePort | - | Service の公開方式の一つで, 各 Kubernetes ノードの特定ポートを開放して Kubernetes クラスタ外部からのアクセスを受け付ける仕組み。 |
| Classless Inter-Domain Routing | CIDR | IP アドレスとネットワークプレフィックス長を組み合わせた表記法。 |
| ReplicaSet | - | 指定した数の Pod レプリカを維持する Kubernetes リソース。通常は Deployment が内部的に管理します。 |
| kubeconfig | - | Kubernetes 接続設定ファイルを指す名称。kubectl などが参照する。 |
| Extended Berkeley Packet Filter | eBPF | Linux カーネル内で安全にプログラムを実行する仕組み。高性能なパケット処理や観測機能の実装に利用される。 |
| Hypertext Transfer Protocol | HTTP | World Wide Webで情報をやり取りする通信手順。 |
| Hypertext Transfer Protocol Secure | HTTPS | 通信内容を暗号化してWorld Wide Web通信を行う方式。 |
| Internet Protocol | IP | ネットワーク上で宛先を識別し, データを届けるための通信手順。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| systemd スライス ( systemd slice ) | - | Linux の systemd でプロセスを階層的にまとめて管理するための単位。CPU やメモリなどの資源制御に利用します。 |
| Red Hat Enterprise Linux | RHEL | Red Hatが提供する企業向けLinuxディストリビューション。 |
| Secure Shell | SSH | 遠隔の計算機へ安全に接続して操作する方式。 |
| Certificate Authority | CA | 電子証明書を発行して正当性を保証する組織または仕組み。 |
| Basic Input/Output System | BIOS | 起動時にハードウェア初期化とブート処理を実行するファームウェア方式。 |
| Unified Extensible Firmware Interface | UEFI | BIOS を拡張, 置換するファームウェア方式。 |
| Central Processing Unit | CPU | 計算処理を実行する中核部品。 |
| Interrupt Request | IRQ | ハードウェアの一部からプロセッサーに直ちに送信されるシグナル。IRQ は Interrupt ReQuest の略。 |
| GNU GRand Unified Bootloader | GRUB | Linux 系 OS で広く利用されるブートローダ。カーネル起動引数の設定を管理します。 |
| Red Hat Enterprise Linux 9 | RHEL9 | Red Hat Enterprise Linux の第9系統版。 |
| systemd | - | Linux システムの初期化とサービス管理を行う仕組み。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `cat` | - | ファイル内容を標準出力へ表示するコマンド。 |
| `journalctl` | - | systemd ジャーナルのログを参照するコマンド。 |
| makeコマンド | make | Makefile に定義された処理を実行するコマンド。 |
| `systemctl` | - | systemd 管理下のサービスを起動, 停止, 状態確認するコマンド。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
| サービス | - | 機能を利用者や他システムへ提供する仕組み。 |
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| スケジューリング | - | 実行順序や時刻を計画して割り当てる処理。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| ポート | - | 通信の出入口を識別する番号または接点。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |

## 概要

Kubernetes ワーカーノードを Kubernetes クラスタへ参加させるためのロールです。`k8s-common` で整えた前提の上に, 低遅延化向けの OS チューニング, ワーカーノードを Kubernetes クラスタへ参加させる設定, ワーカーノードで必要な通信を許可するファイアウォール設定 (NodePort を使う場合の設定を含む), Cilium BGP Control Plane の設定をまとめて適用します。既存ワーカーノードのスケジュール停止 (`kubectl cordon`), Pod退避 (`kubectl drain`), Kubernetes クラスタからの削除 (`kubectl delete node`) まで一括で扱います。

本ロールは, ワーカーノードの参加処理, 低遅延向け設定, ファイアウォール設定, Cilium BGP Control Plane 設定をまとめて適用します。

- **ファイアウォール構成**: `enable_firewall` が有効な環境で UFW/firewalld を初期化し, 10250/tcp などの制御プレーン向けポートと NodePort 範囲を恒久的に開放します。
- **CPU シールドの準備**: systemd スライス単位で使用可能CPU範囲 (`AllowedCPUs`) を固定します。これにより, IRQを受け付けるCPUを固定するスクリプトを実行できる状態にします。
- **GRUB と低遅延調整**: `k8s_reserved_system_cpus_default` に基づき `nohz_full` や `isolcpus` などのカーネルパラメータを更新し, ワーカースレッドと IRQ をアプリケーション向け / システム処理向けに分離します。
- **Kubernetes クラスタ参加処理**: 既存ワーカーノードのスケジュール停止 (`kubectl cordon`), Pod退避 (`kubectl drain`), Kubernetes クラスタからの削除 (`kubectl delete node`), ワーカーノード構成リセット (`kubeadm reset`), Kubernetes クラスタへ参加 (`kubeadm join --config`) を自動化し, `containerd` は起動 (`state: started`) と自動起動有効化 (`enabled: true`), `kubelet` は自動起動有効化 (`enabled: true`) と再起動を実施します。
- **Cilium BGP Control Plane**: Kubernetes ノード固有の識別子で CRD マニフェストを生成し, CiliumBGPAdvertisement / CiliumBGPPeerConfig / CiliumBGPClusterConfig を適用して Pod/Service CIDR をルータへ広告します。
- **再起動とユーティリティ登録**: CPU割り当てサービス (`pin-worker-queue`, `pin-irqs`) を `enabled` 登録し, OS チューニング後と Kubernetes クラスタ参加後にそれぞれリブートします。

## 前提条件

- 対象 OS: Debian/Ubuntu 系 (Ubuntu 24.04 を想定), RHEL9 系 (AlmaLinux 9.6 等を想定)
- `roles/k8s-common` の実行が完了していること (`kubeadm`, `kubelet`, `containerd` が導入済みであること)
- コントロールプレーンノードで `kubectl`, `kubeadm`, `openssl` が実行可能であること
- 対象ホストで管理者権限 (sudo) が利用可能であること
- `k8s_ctrlplane_endpoint`, `k8s_ctrlplane_port`, `k8s_ctrlplane_host` が適切に設定済みであること

## 実行方法

実行者は制御ホストで以下のいずれかを実行します。

```bash
make run_k8s_worker
```

または,

```bash
ansible-playbook -i inventory/hosts k8s-worker.yml --tags "k8s-worker"
```

または,

```
ansible-playbook -i inventory/hosts site.yml --tags "k8s-worker"
```

## 主要変数

### API 待機設定

Kubernetes API Server の待機条件は [k8s-common ロール](../k8s-common/Readme.md) の共通内部設定を使用します。

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_ctrlplane_endpoint` | `""` (未設定) | コントロールプレーン API の到達先アドレス。本ロールでは, kubelet 側で優先される Pod CIDR のIPアドレスファミリと Kubernetes API エンドポイント広告アドレスのアドレスファミリ整合を確実にするため, IPアドレスを指定します。 |

補足 (未定義時の動作):
- `k8s_ctrlplane_endpoint` または `k8s_ctrlplane_host` が未定義, もしくは空文字列の場合, `roles/k8s-worker/tasks/main.yml` のガード条件により `k8s-worker` の実処理タスクはスキップされます。
- `k8s_ctrlplane_port` は通常 `k8s_ctrlplane_endpoint` から自動算出されるため, 個別に定義しなくても動作します。
- `k8s_ctrlplane_endpoint` にポート番号を含めない場合は, `k8s_ctrlplane_port` として `6443` が自動的に使われます。

### containerd 待機設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_containerd_wait_timeout` | `60` | containerd ソケット待機タイムアウト (秒)。 |
| `k8s_containerd_wait_retries` | `5` | containerd ソケット待機処理の再試行回数。 |
| `k8s_containerd_wait_sleep` | `2` | containerd ソケット待機処理の再試行間隔 (秒)。 |
| `k8s_containerd_wait_delegate_to` | `localhost` | containerd 待機処理を実行する接続元ホスト。 |

### Kubernetes オペレータユーザ設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_operator_user` | `kube` | Kubernetes 操作用ユーザ名。 |

### セットアップツール配置先

セットアップツールの共通配置規約は [k8s-common ロール](../k8s-common/Readme.md) を参照してください。kubeconfig の生成・統合・配布仕様は [k8s-kubeconfig ロール](../k8s-kubeconfig/Readme.md) を参照してください。

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |

### ワーカーノード固有設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_ctrlplane_host` | `""` (未設定) | `delegate_to` で `kubeadm`, `kubectl` を実行するコントロールプレーンノード。 |
| `k8s_kubeadm_config_store` | `/home/ansible/kubeadm` | `kubeadm.config.yml` や Cilium BGP Control Plane マニフェスト保存先。 |
| `k8s_drain_timeout_minutes` | `5` | Pod退避 (`kubectl drain`) のタイムアウト (分)。 |
| `k8s_worker_delete_wait_sec` | `5` | ワーカーノード削除 (`kubectl delete node`) 後の待機時間 (秒)。 |
| `reboot_timeout_sec` | `600` | 再起動後の復帰待ちタイムアウト (秒)。 |

### ファイアウォール / NodePort 設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `enable_firewall` | `false` | `true` の場合にファイアウォール設定を有効化。 |
| `firewall_backend` | Debian/Ubuntu: `['ufw']`, RHEL: `['firewalld']` | 使用するファイアウォール実装。 |
| `k8s_worker_enable_nodeport` | `false` | NodePort 範囲の開放有無。 |
| `k8s_worker_nodeport_range` | `30000-32767` | NodePort 開放範囲。 |
| `k8s_worker_node_ports_from_ctrlplane` | `['10250/tcp']` | コントロールプレーンから許可するポート。 |

### CPU / systemd スライス設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_reserved_system_cpus_default` | 未定義 | システム処理向け CPU 範囲。 |
| `k8s_systemd_slices` | `['init.scope.d', 'system.slice.d', 'user.slice.d', 'user-.slice.d']` | CPU割り当て設定ファイルの対象スライス一覧。 |

### Cilium BGP Control Plane 設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_bgp.enabled` | 未定義 | `true` 時に Cilium BGP Control Plane マニフェストを生成, 適用。 |
| `k8s_bgp.neighbors` | 未定義 | BGP ピア定義。`k8s_bgp.enabled: true` の場合は必須。 |
| `k8s_bgp.node_name` | 対象ホスト名 | BGP リソース名生成に利用するワーカーノード名。 |
| `k8s_bgp.apply_delegate` | `""` (未設定時は対象ホスト名) | BGP マニフェストを適用するホスト。 |

補足 (未定義時の動作):
- `k8s_bgp.node_name` が未定義, もしくは空文字列の場合は `ansible_hostname` が自動的に使われます。
- `k8s_bgp.neighbors` 配下の `peer_address` または `peer_asn` が未定義, もしくは空文字列のエントリは, マニフェスト生成時に当該ピア設定を出力しません。
- `k8s_bgp.neighbors` の全エントリが上記条件に該当する場合は, BGP ピア設定が空になります。意図した経路広告を行うため, 有効な `peer_address` と `peer_asn` を少なくとも 1 組設定してください。

## 設定例

本節では, `host_vars`ディレクトリ配下に配置するワーカーノードの設定内容を例を用いて説明します。

### 基本設定

Kubernetesクラスタのワーカーノードの基本設定項目の設定例を以下に示します。これらの設定項目は, 低遅延構成, Cilium BGP Control Plane機能の使用有無に依らず共通です:

```yaml
# host_vars/k8sworker0101.local
k8s_ctrlplane_endpoint: "192.168.40.11"
k8s_ctrlplane_port: 6443
k8s_ctrlplane_host: "k8sctrlplane01.local"
```

ポイント:
- `k8s_ctrlplane_endpoint`: ワーカーノードが接続する Kubernetes API の宛先アドレスを指定します。kubelet 側で優先される Pod CIDR のIPアドレスファミリと Kubernetes API エンドポイント広告アドレスのアドレスファミリを一致させる必要があるため, IPアドレスで宛先を設定してください。
- `k8s_ctrlplane_port`: Kubernetes API の待受ポート番号を指定します。標準構成では `6443` を設定します。
- `k8s_ctrlplane_host`: Ansible の `delegate_to` で `kubeadm` や `kubectl` を実行するコントロールプレーンノードのインベントリ名を指定します。`inventory/hosts` と `host_vars` に定義したホスト名を設定してください。

### 低遅延構成

低遅延処理を行うKubernetesクラスタのワーカーノード設定例を以下に示します:

```yaml
# 低遅延構成用の設定
k8s_reserved_system_cpus_default: "0-3"
k8s_systemd_slices:
  - init.scope.d
  - system.slice.d
  - user.slice.d
  - "user-.slice.d"
```

ポイント:
- 例えば, 論理CPU番号0番から3番までのCPUをシステム処理向けCPUとして設定する場合, `k8s_reserved_system_cpus_default`を, `k8s_reserved_system_cpus_default: "0-3"` のように指定します。
  - `0-3` は論理CPU番号 `0,1,2,3` を意味します。Linux の論理CPU番号は通常 `0` から始まります。
  - 論理CPU番号は `lscpu -e=CPU,CORE,SOCKET,NODE` や `cat /sys/devices/system/cpu/online` で確認してから, 実機のトポロジに合わせて範囲を決めてください。
- `k8s_systemd_slices:` に `init.scope.d`, `system.slice.d`, `user.slice.d`, `user-.slice.d` を列挙して, CPU 割り当て対象の systemd スライスを指定します。
- 低遅延化の確認では CPU割り当てサービス (`pin-worker-queue`, `pin-irqs`) の状態確認を必ず行ってください。

### Cilium BGP Control Plane 有効構成

Cilium BGP Control Planeを有効にしたコントロールプレーンノード配下の Kubernetes クラスタを構成するワーカーノードの設定例を以下に示します:

```yaml
# Cilium BGP Control Plane機能有効時の設定
k8s_bgp:
  enabled: true
  node_name: "k8sworker0102"
  neighbors:
    - peer_address: "192.168.40.49"
      peer_asn: 65011
```

ポイント:
- `k8s_bgp.enabled: true` を指定して Cilium BGP Control Plane 機能を有効化するよう指示します。
- `k8s_bgp.node_name: "k8sworker0102"` のようにノード識別子を指定します。
- `k8s_bgp.neighbors:` 配下には次の項目を必ず指定します。
  - `peer_address`: ワーカーノードからBGPセッションを張る相手 (外部ルータやL3スイッチ) のIPアドレスを指定します。
  - `peer_asn`: `peer_address` で指定した相手装置側のAS番号 (Autonomous System Number) を指定します。

なお, Cilium BGP Control Plane マニフェストの生成, 適用は `k8s_bgp.apply_delegate` で指定したホスト (既定値: 空文字列, 未指定時は対象ホスト名) で実施されます。

## テンプレートと生成ファイル

本ロールでは以下のテンプレート / ファイルを出力します:
展開先ホストは, `cilium_bgp_delegate_host`で指定されたホスト(既定は, 対象ホスト) です。

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `roles/k8s-common/templates/cilium-bgp-resources.yml.j2` | `/home/ansible/kubeadm/cilium/bgp/cilium-bgp-resources-<node-suffix>.yml` | Cilium BGP Control Plane の ClusterConfig, PeerConfig, Advertisement 定義を生成するマニフェストです。 |
| `systemd-cpuset.conf.j2` | `/etc/systemd/system/init.scope.d/40-cpuset.conf`, `/etc/systemd/system/system.slice.d/40-cpuset.conf`, `/etc/systemd/system/user.slice.d/40-cpuset.conf`, `/etc/systemd/system/user-.slice.d/40-cpuset.conf` | kubelet やランタイムの CPU 割り当てを固定し, ワーカーノードの遅延揺らぎを抑える systemd 設定です。 |
| `pin-worker-queue.sh.j2` | `/opt/k8snodes/sbin/pin-worker-queue.sh` | ワーカーノードの NIC キュー割り当てを最適化し, 割り込み偏りを抑えるための設定スクリプトです。 |
| `pin-worker-queue.service.j2` | `/etc/systemd/system/pin-worker-queue.service` (既定: `/etc/systemd/system/pin-worker-queue.service`) | 起動時に NIC キュー固定処理を適用する systemd サービス定義です。 |
| `pin-irqs.py.j2` | `/opt/k8snodes/sbin/pin-irqs.py` | IRQ を CPU コアへ分散配置し, レイテンシ安定化を図るための調整スクリプトです。 |
| `pin-irqs.service.j2` | `/etc/systemd/system/pin-irqs.service` (既定: `/etc/systemd/system/pin-irqs.service`) | 起動時に IRQ 固定処理を自動適用する systemd サービス定義です。 |
| `worker-kubeadm.config.j2` | `/home/ansible/kubeadm/kubeadm.config.yml` | ワーカーノード参加時の kubeadm 実行パラメタを定義する設定ファイルです。 |

## 実行フロー

1. [roles/k8s-worker/tasks/load-params.yml](roles/k8s-worker/tasks/load-params.yml) で OS ファミリ別パッケージ情報と共通変数 (`cross-distro.yml`, `all-config.yml`, `k8s-api-address.yml`) を読み込みます。
2. [roles/k8s-worker/tasks/main.yml](roles/k8s-worker/tasks/main.yml) で `package.yml`, `directory.yml`, `user_group.yml`, `service.yml` を include します (現状はプレースホルダ)。
3. [roles/k8s-worker/tasks/config-k8sworker-firewall.yml](roles/k8s-worker/tasks/config-k8sworker-firewall.yml) で `enable_firewall` と `firewall_backend` に応じたファイアウォール設定を行います。
4. [roles/k8s-worker/tasks/config-irq-balance.yml](roles/k8s-worker/tasks/config-irq-balance.yml) で低遅延構成時に `irq balance`パッケージ(`irq_balance_package`変数で定義) を削除します。
5. [roles/k8s-worker/tasks/config-shielding.yml](roles/k8s-worker/tasks/config-shielding.yml) で `k8s_systemd_slices` 配下に CPU割り当て設定ファイルを生成します。
6. [roles/k8s-worker/tasks/config-worker-node.yml](roles/k8s-worker/tasks/config-worker-node.yml) で CPU レンジ算出, GRUBのOSカーネル起動パラメタを設定, CPU割り当てスクリプト配置, 初回リブートを実施します。
7. [roles/k8s-worker/tasks/config.yml](roles/k8s-worker/tasks/config.yml) で kube-apiserver 待機, Kubernetes クラスタ参加設定生成, 既存ワーカーノード整理, ワーカーノード構成リセット (`kubeadm reset`), Kubernetes クラスタへ参加 (`kubeadm join`), `containerd` と `kubelet` の自動起動有効化 (`enabled: true`), 二度目のリブートを実施します。
8. [roles/k8s-worker/tasks/config-cilium-bgp-cplane.yml](roles/k8s-worker/tasks/config-cilium-bgp-cplane.yml) で `k8s_bgp.enabled: true` の場合に Cilium BGP Control Plane マニフェストを生成, CRD 確認後に適用します。

### ハンドラ処理

| ハンドラ | トリガー | 説明 |
| --- | --- | --- |
| [roles/k8s-worker/handlers/kubelet.yml](roles/k8s-worker/handlers/kubelet.yml) | `notify: kubelet_restarted_and_enabled` | kubelet の daemon-reload と再起動, enable をまとめて実施し, Kubernetes クラスタ参加後のサービス状態を整えます。 |
| [roles/k8s-worker/handlers/reload-firewall.yml](roles/k8s-worker/handlers/reload-firewall.yml) | `notify: reload firewalld` / `notify: reload ufw` | firewall_backend に応じて firewalld もしくは UFW を再読み込みし, NodePort などのポート開放設定を反映させます。 |
| [roles/k8s-worker/handlers/reboot-node.yml](roles/k8s-worker/handlers/reboot-node.yml) | `notify: reboot_node_handler` | リブートを実行し, GRUBのOSカーネル起動パラメタ設定や Kubernetes クラスタ参加 (`kubeadm join`) 後の状態を確定させます。 |

### OS 差異

#### ファイアウォール設定の差異

| 項目 | RHEL 系 | Debian/Ubuntu 系 |
| --- | --- | --- |
| バックエンド | firewalld | UFW |
| ルール適用方法 | 条件を細かく指定するルール (rich rule)とポート開放 | allow ルール |
| 反映方法 | `firewall-cmd --reload` | `ufw reload` |
| NodePort 範囲表記 | `30000-32767/tcp` | `30000:32767/tcp` |

#### GRUB 更新方法の差異

| 項目 | RHEL 系 | Debian/Ubuntu 系 |
| --- | --- | --- |
| 更新コマンド | `grub2-mkconfig` | `update-grub` |
| 出力先 | BIOS/UEFI を判別して `/boot/grub2/grub.cfg` または `/boot/efi/EFI/*/grub.cfg` | 既定の GRUB 設定先 |

## 検証ポイント

本節では, 本ロール適用後の検証方法について説明します。

### 前提条件

- ロール実行が成功していることを確認してください。
- コントロールプレーンノードから `kubectl` が実行可能であることを確認してください。
- 対象ワーカーノードへ SSH 接続できることを確認してください。

### 1. Kubernetes ノード登録状態の確認

**実施Kubernetes ノード種別**: コントロールプレーンノード

**コマンド**:

```bash
kubectl get nodes -o wide
```

**実行例**:

```plaintext
NAME             STATUS   ROLES           AGE   VERSION    INTERNAL-IP                EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION      CONTAINER-RUNTIME
k8sctrlplane01   Ready    control-plane   26h   v1.31.14   fdad:ba50:248b:1::41       <none>        Ubuntu 24.04.3 LTS   6.8.0-101-generic   containerd://1.7.28
k8sworker0101    Ready    <none>          25h   v1.31.14   fdad:ba50:248b:1::42       <none>        Ubuntu 24.04.3 LTS   6.8.0-101-generic   containerd://1.7.28
k8sworker0102    Ready    <none>          25h   v1.31.14   fdad:ba50:248b:1::43       <none>        Ubuntu 24.04.3 LTS   6.8.0-101-generic   containerd://1.7.28
```

**確認ポイント**:
- 対象ワーカーノードの `STATUS`列が`Ready`となっていることを確認してください。

### 2. kubelet サービス状態の確認

**実施Kubernetes ノード種別**: ワーカーノード

**コマンド**:

```bash
systemctl status kubelet
```

**実行例**:

```plaintext
● kubelet.service - kubelet: The Kubernetes Node Agent
     Loaded: loaded (/usr/lib/systemd/system/kubelet.service; enabled; preset: enabled)
     Active: active (running) since Fri 2026-03-06 02:50:03 JST; 1 day 1h ago
   Main PID: 1027 (kubelet)
```

**確認ポイント**:
- `active (running)` であることを確認してください。
- `enabled;` が付いていることを確認してください。

### 3. kubelet ログの確認

**実施Kubernetes ノード種別**: ワーカーノード

**コマンド**:

```bash
journalctl -u kubelet -n 50 --no-pager
```

**実行例**:

```plaintext
3月 07 04:30:44 k8sworker0101 kubelet[1027]: E0307 ... "Unable to read config path" ... path="/etc/kubernetes/manifests"
```

**確認ポイント**:
- `failed`, `error` が連続して出力されていないことを確認してください。
- Kubernetes ノード登録に関する正常ログが含まれることを確認してください。

### 4. CPU 予約設定の確認 (低遅延構成時)

**実施Kubernetes ノード種別**: 低遅延構成を適用したワーカーノード

**コマンド**:

```bash
cat /etc/systemd/system/*/40-cpuset.conf
cat /proc/cmdline
```

**実行例**:

```plaintext
# /etc/systemd/system/init.scope.d/40-cpuset.conf
[Slice]
AllowedCPUs="0-1"

# /proc/cmdline
BOOT_IMAGE=/boot/vmlinuz-6.8.0-101-generic ... nohz_full=2-3 isolcpus=managed,2-3 rcu_nocbs=2-3 irqaffinity=0-1 workqueue.unbound_cpus=0-1 ...
```

**確認ポイント**:
- 使用可能CPU範囲 (`AllowedCPUs`) が期待値になっていることを確認してください。
- カーネルパラメータに CPU 分離のためのオプションが含まれることを確認してください。

### 5. CPU 割り当て固定サービスの確認 (低遅延構成時)

**実施Kubernetes ノード種別**: 低遅延構成を適用したワーカーノード

**コマンド**:

```bash
systemctl status pin-worker-queue pin-irqs
```

**実行例 (先頭抜粋)**:

```plaintext
○ pin-worker-queue.service - Pin all unbounded worker queues to system CPUs
  Loaded: loaded (/etc/systemd/system/pin-worker-queue.service; enabled; preset: enabled)
  Active: inactive (dead) since Fri 2026-03-06 02:50:09 JST; 1 day 1h ago

○ pin-irqs.service - Pin all IRQs to housekeeping CPUs
  Loaded: loaded (/etc/systemd/system/pin-irqs.service; enabled; preset: enabled)
  Active: inactive (dead) since Fri 2026-03-06 02:50:09 JST; 1 day 1h ago
```

**確認ポイント**:
- 1回だけ起動するサービス (systemdのone-shotサービス)として実行された後に, `inactive (dead)` で終了していることを確認してください。
- `enabled;` が付いていることを確認してください。
- 直近の実行が失敗していないことを確認してください。

### 6. Cilium BGP Control Plane リソースの確認 (Cilium BGP Control Plane 有効構成時)

**実施Kubernetes ノード種別**: コントロールプレーンノード

**コマンド**:

```bash
kubectl get ciliumbgpclusterconfigs.cilium.io -A
kubectl get ciliumbgppeerconfigs.cilium.io -A
kubectl get ciliumbgpadvertisements.cilium.io -A
```

**実行例 (Cilium BGP Control Plane 有効時)**:

```plaintext
$ kubectl get ciliumbgpclusterconfigs.cilium.io -A
NAMESPACE   NAME                 AGE
default     k8sworker0102-bgp    2m

$ kubectl get ciliumbgppeerconfigs.cilium.io -A
NAMESPACE   NAME                           AGE
default     k8sworker0102-peer-65011       2m

$ kubectl get ciliumbgpadvertisements.cilium.io -A
NAMESPACE   NAME                               AGE
default     k8sworker0102-podcidr-service      2m
```

**実行例 (Cilium BGP Control Plane 無効時, CRD 導入済み)**:

```plaintext
$ kubectl get ciliumbgpclusterconfigs.cilium.io -A
No resources found

$ kubectl get ciliumbgppeerconfigs.cilium.io -A
No resources found

$ kubectl get ciliumbgpadvertisements.cilium.io -A
No resources found
```

**実行例 (CRD 未導入時)**:

```plaintext
error: the server doesn't have a resource type "ciliumbgpclusterconfigs"
```

**確認ポイント**:
- Cilium BGP Control Plane を有効化した環境では, BGP 関連リソースが表示されることを確認してください。
- Cilium BGP Control Plane を無効化し, CRD が導入済みの環境では `No resources found` が表示されることを確認してください。
- `resource type` が存在しない場合は, Cilium BGP Control Plane の Custom Resource Definition (CRD) が未導入であることを示します。

### 7. ファイアウォール設定の確認 (`enable_firewall: true` の場合)

**実施Kubernetes ノード種別**: ワーカーノード

**コマンド (Ubuntu)**:

```bash
sudo ufw status verbose
```

**コマンド (RHEL)**:

```bash
sudo firewall-cmd --list-ports --zone=public
sudo firewall-cmd --list-rich-rules --zone=public
```

**実行例**:

```plaintext
sudo: ufw: コマンドが見つかりません
```

**確認ポイント**:
- `10250/tcp` が開放されていることを確認してください。
- NodePort を有効化している場合, 範囲ルールが反映されていることを確認してください。
- `ufw` コマンドが見つからない場合は, UFW 未導入または firewalld 利用環境です。OS と `firewall_backend` の設定に合わせて確認コマンドを使い分けてください。

## トラブルシューティング

### 1. k8s-worker の実処理がスキップされる場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
grep -nE '^(k8s_ctrlplane_endpoint|k8s_ctrlplane_host):' vars/all-config.yml host_vars/*.yml
ansible-playbook -i inventory/hosts k8s-worker.yml --tags "k8s-worker" --list-tasks
```

**確認ポイント**:

- k8s_ctrlplane_endpoint と k8s_ctrlplane_host が定義済みであること。
- 2つの変数が空文字列ではないこと。
- list-tasks 出力で k8s-worker の実処理タスクが含まれること。

### 2. kubeadm join が失敗する場合

**実施対象ホスト**: ワーカーノード, コントロールプレーンノード

**実行するコマンド**:

```bash
nc -zv <k8s_ctrlplane_endpoint> <k8s_ctrlplane_port>
kubeadm token create
timedatectl status
```

**確認ポイント**:

- コントロールプレーン API へ到達可能であること。
- kubeadm token create が成功すること。
- 時刻同期状態に異常がないこと。

### 3. Cilium BGP Control Plane のマニフェスト生成で失敗する場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
grep -nE 'k8s_bgp|peer_address|peer_asn' vars/all-config.yml host_vars/*.yml
```

**確認ポイント**:

- k8s_bgp.enabled が true の場合, k8s_bgp.neighbors が空ではないこと。
- 各 neighbor に peer_address と peer_asn が設定されていること。

### 4. Cilium BGP Control Plane の適用で resource type エラーが出る場合

**実施対象ホスト**: コントロールプレーンノード

**実行するコマンド**:

```bash
kubectl get crd ciliumbgpadvertisements.cilium.io
kubectl get crd ciliumbgppeerconfigs.cilium.io
kubectl get crd ciliumbgpclusterconfigs.cilium.io
```

**確認ポイント**:

- Cilium BGP 関連 CRD がすべて存在すること。
- CRD が不足している場合は Cilium 側の導入状態を整えてから再適用すること。

### 5. ファイアウォール関連タスクが失敗する場合

**実施対象ホスト**: ワーカーノード

**実行するコマンド**:

```bash
cat /etc/os-release
which ufw || true
which firewall-cmd || true
```

**確認ポイント**:

- Debian/Ubuntu 系では ufw, RHEL 系では firewalld を利用する設定であること。
- firewall_backend と OS の組み合わせが一致していること。
- 切り分け時は enable_firewall を false にして段階的に再有効化すること。

### 6. 低遅延化タスクが実行されない場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
grep -n '^k8s_reserved_system_cpus_default:' vars/all-config.yml host_vars/*.yml
```

**確認ポイント**:

- k8s_reserved_system_cpus_default が定義済みであること。
- CPU 範囲 (例: 0-3) が空でないこと。

### 7. リブート後にノードが Ready へ戻らない場合

**実施対象ホスト**: ワーカーノード, コントロールプレーンノード

**実行するコマンド**:

```bash
systemctl status containerd kubelet --no-pager
journalctl -u kubelet -n 100 --no-pager
kubectl get nodes -o wide
```

**確認ポイント**:

- containerd と kubelet が active (running) であること。
- kubelet ログに再参加失敗のエラーが継続出力されていないこと。
- kubectl get nodes で対象ワーカーノードが Ready へ復帰していること。

## 注意事項

- 本ロールは `config-worker-node.yml` と `config.yml` の両方でリブートを実行します。
- `config.yml` には ワーカーノード構成リセット (`kubeadm reset`) が含まれるため, 稼働中 Kubernetes クラスタへ適用する際は事前に Pod 退避や停止計画を準備してください。Pod退避 (`kubectl drain --ignore-daemonsets --delete-emptydir-data`) は DaemonSet を退避しないため, 必要に応じて対象ワーカーノードで稼働する各 DaemonSet Pod の停止, 再スケジューリング手順を整備し, Local Persistent Volume のデータは退避やアンマウントを含む保全策を講じてから実行してください。
- コントロールプレーン側でトークン生成 (`kubeadm token create`) や `kubectl` を実行するため, `k8s_ctrlplane_host` では Ansible の権限昇格 (`become: true`) が成功するように設定してください。権限昇格に失敗すると Kubernetes クラスタ参加用トークン取得が失敗します。
- Cilium BGP Control Plane のマニフェストは `k8s_bgp.apply_delegate` で指定したホスト (既定値: 空文字列, 未指定時は対象ホスト名) 上で生成・適用されます。
- NodePort を有効化する場合は必要なサービスのみが公開されるよう, 上位ネットワーク機器側のアクセス制御リストも合わせて確認してください。
- ファイアウォールタスクはデフォルトで無効化されています。現状は動作検証が十分でないため, `enable_firewall` は `false` を推奨します。

## 参考資料

### 公式ドキュメント

- [Kubernetes](https://kubernetes.io/docs/home/)
- [kubeadm join](https://kubernetes.io/docs/reference/setup-tools/kubeadm/kubeadm-join/)
