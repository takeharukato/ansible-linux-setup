# elastic-agent-k8s ロール

本ロールは, Kubernetesクラスタ監視用の Elastic Agent を Helm で導入し, Fleet Server へ登録するロールです。 本ロールは, Kubernetes (K8s)のコントロールプレーンノードに適用するロールです (ワーカーノードへの適用は不要)。

## 目次

- [elastic-agent-k8s ロール](#elastic-agent-k8s-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
    - [Elastic Stack間共有設定値](#elastic-stack間共有設定値)
    - [各ロール固有の利用者入力値](#各ロール固有の利用者入力値)
      - [条件付き必須入力値](#条件付き必須入力値)
      - [任意入力値](#任意入力値)
      - [辞書形式変数の既定値と設定例](#辞書形式変数の既定値と設定例)
        - [elastic\_agent\_k8s\_clusterwide\_resources](#elastic_agent_k8s_clusterwide_resources)
        - [elastic\_agent\_k8s\_kube\_state\_metrics\_resources](#elastic_agent_k8s_kube_state_metrics_resources)
    - [設定例](#設定例)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [検証の前提条件](#検証の前提条件)
    - [検証環境の設定](#検証環境の設定)
    - [検証コマンドと期待結果](#検証コマンドと期待結果)
      - [1. Helm導入識別名 状態確認](#1-helm導入識別名-状態確認)
      - [2. Deployment 稼働状態確認](#2-deployment-稼働状態確認)
      - [3. kube-state-metrics 設定確認](#3-kube-state-metrics-設定確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. Helm template 検証で停止する場合](#1-helm-template-検証で停止する場合)
    - [2. Deployment の rollout 待機で停止する場合](#2-deployment-の-rollout-待機で停止する場合)
  - [注意事項](#注意事項)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)
    - [関連ロール](#関連ロール)

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Elasticsearch | - | ログやメトリクス情報を集約, 検索するためのサーバソフトウェア。 |
| Elasticsearchのセキュリティ機能 | - | Elasticsearchへの接続者を認証し, 利用者に付与した権限に基づいて実行可能な操作を制御する機能。 |
| Snapshot Repository | - | Elasticsearch がバックアップデータを保存する場所として参照する保存先の定義。 |
| snapshot | - | ある時点の Elasticsearch データを復旧可能な形で保存したバックアップ単位。 |
| Snapshot API | - | Elasticsearch の snapshot 作成, 一覧取得, 削除, 復元を行う操作手順。 |
| Kibana | - | Elasticsearchに保存されたデータを可視化し, 参照するソフトウェア。 |
| Logstash | - | 受信したデータを整形し, 送信先へ転送するソフトウェア。 |
| Fleet Server | - | Elastic Agent の管理通信を受け付けるサーバ機能。 |
| Elastic Agent | - | ログやメトリクスを収集して送信する実行要素。 |
| Fleet Output | - | Elastic Agent が送信先として利用する出力設定。 |
| Elastic Agent ポリシー | - | Fleetが管理し, Elastic Agentのデータ収集方法と動作を定める設定情報。 |
| Enrollment Token | - | Elastic AgentがFleet Serverへの登録を許可されていることを確認し, 登録先のElastic Agent ポリシーを特定するための登録用認証情報。 |
| Fleet Serverサービスアカウントトークンファイル | - | Fleet ServerがElasticsearchへ接続するためのサービスアカウントトークンを対象ホスト上へ保存し, Fleet Serverコンテナが起動時に読み込む権限`0600`のファイル。 |
| コンテナイメージ | - | コンテナ実行に必要な内容をまとめた保存形式。 |
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Docker Compose | - | 複数のコンテナ定義をまとめて作成, 起動, 停止, 更新する仕組み。 |
| Docker Compose 定義ファイル | - | Docker Compose が参照するコンテナ構成の定義ファイル。 |
| compose project 名 | - | Docker Compose によって展開される個々のアプリケーションを識別する名前です。展開されたコンテナ, ネットワーク, ボリュームなどのリソースをグループ化し, 他のアプリケーション又は別途展開された同じアプリケーションと区別するために用います。 |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| Playbook | - | 自動化処理の実行手順を記述したファイル。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| inventory group | - | Ansible Inventory内で同じ役割の対象ホストをまとめる識別単位。 |
| single-node | - | Elasticsearch を単一ノード構成で構成する方式。コンテナイメージを用いた導入時に典型的に用いられる。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| ホスト | - | 管理対象として識別される個別の計算機。 |
| サーバ | - | 他の機器や利用者へ機能やデータを提供する計算機, 又はその役割。 |
| ネットワーク | - | 機器同士を接続してデータをやり取りする仕組み。 |
| ディレクトリ | - | ファイルを階層的に整理するための入れ物。 |
| ログ | - | 処理の結果や状態を時系列で記録した情報。 |
| メトリクス | - | ホストやサービスの状態を数値で表した観測情報。 |
| データ | - | 処理や保存の対象となる情報。 |
| ポート | - | 通信の出入口を識別する番号または接点。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| URL スキーム | - | URL の先頭で通信方式を示す部分。例: `http`, `https`。 |
| ランタイムエンドポイント ( rumtime endpoint ) | - | 対象ホスト上で所定のサービスが動作していることを確認するための疎通確認に用いるエンドポイントです。ここでのエンドポイントは, <接続先ホスト名>と<接続先ポート番号>の組から構成されるURLになります。本ロールで規定した変数により明示的に指定されたエンドポイントがあればその値を採用し, 未指定の場合は, 対象ホスト名とポート番号からエンドポイントを組み立てます。 |
| 対象ホスト上での疎通確認 | - | 対象ホスト上で自ホスト(localhost)を指定して待ち受け先ポートへの疎通確認を実施すること。確認対象のサービスが対象ホスト上で起動していることを確認します。 |
| 外部ホストからの疎通確認 | - | 対象ホスト以外のホストから対象ホストを指定して待ち受け先ポートへの疎通確認を実施すること。確認対象のサービスがネットワーク接続を含めて適切に設定され, サービス受付可能な状態になっていることを確認します。 |
| Hypertext Transfer Protocol | HTTP | World Wide Webで情報をやり取りする通信手順。 |
| Internet Protocol | IP | ネットワーク上で宛先を識別し, データを届けるための通信手順。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Fully Qualified Domain Name | FQDN | 末尾まで省略せず書いた完全なドメイン名。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Linux | - | 多くの機器で使われる, 基本ソフトウェアの系統。 |
| ディストリビューション | - | 基本ソフトウェアと関連部品をまとめた配布形態。 |
| コミュニティ | - | 共通目的のもとで継続的に活動する利用者集団。 |
| Debian | - | コミュニティ主導で開発される Linux ディストリビューション。 |
| Red Hat | - | Red Hat Enterprise Linuxなどを提供する組織。 |
| Red Hat Enterprise Linux | RHEL | Red Hatが提供する企業向けLinuxディストリビューション。 |
| ホストメトリクス ( host metrics ) | - | リソース使用状況など, ログ収集対象となるホスト群から収集する情報。 |
| root | - | Unix 系システムの最上位権限を持つ管理者識別子。 |
| ループ | - | 同じ処理を繰り返すこと。 |
| バックエンド | - | 利用者画面の背後で処理を実行する側。 |
| メタデータ | - | 対象データの属性や説明を示す付加情報。 |
| リソース | - | 処理に必要な計算機資源やデータ。 |
| コマンド | - | 実行者が計算機へ処理を指示するための命令。 |
| ansible-playbookコマンド | ansible-playbook | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| Python | - | スクリプティングやアプリケーション開発を手早く実施するために用いられる高水準プログラミング言語の一種。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |
| makeコマンド | make | Makefile に定義された処理を実行するコマンド。 |
| curlコマンド | curl | URL を指定して通信結果を取得するコマンド。 |
| 環境変数 | - | 実行時の動作を調整するために外部から渡す設定値。 |
| cron | - | 指定した時刻や周期でコマンドを自動実行する仕組み。 |
| Ansible Playbook | Playbook | Ansibleで実行する処理の順序と対象を記述したファイル。 |
| Classless Inter-Domain Routing | CIDR | Internet Protocolアドレスの範囲を先頭アドレスと接頭辞長で表す方式。 |
| Docker bridge network | Dockerブリッジネットワーク | 同一対象ホスト上のコンテナ間通信に使用する仮想的なネットワーク。 |
| iptables | - | Linux の IPv4 パケットフィルタ設定ツール。 |
| ip6tables | - | Linux の IPv6 パケットフィルタ設定ツール。 |
| Network Address Translation | NAT | 通信時にIPアドレスを変換する処理。 |
| systemd | - | Linux上でサービスの起動順序と実行状態を管理するソフトウェア。 |
| dockerコマンド | - | Dockerブリッジネットワークを作成及び確認するコマンド。 |
| iptablesコマンド | - | IPパケットの通過条件とNAT規則を確認するコマンド。 |
| ip6tablesコマンド | - | IPv6パケットの通過条件とNAT規則を確認するコマンド。 |
| systemctlコマンド | - | systemdが管理するサービスの状態を確認するコマンド。 |
| jqコマンド | jq | JSON 形式のデータから必要な項目だけを抽出して表示するコマンド。 |
| yqコマンド | yq | YAML 形式のデータから必要な項目だけを抽出して表示するコマンド。 |
| pipeline | - | 入力, 整形, 出力の処理順を定義する Logstash の設定単位。 |
| Elastic Agent入力 | - | Elastic Agentからデータストリーム情報を保持したイベントを受信するLogstashの入力機能。 |
| インデックス | - | Elasticsearch に保存するデータの格納先識別単位。 |
| Makefile | - | 実行手順を定義したファイル。 |
| サービスアカウント (Service Account) | - | 自動処理中でサービスを呼び出す側のプログラムを識別するための識別情報。 |
| Elasticsearchのサービスアカウントトークン ( Elasticsearch Service Account Token ) | - | Elasticsearchが提供するサービスアカウントに紐付く認証情報。 |
| Hypertext Transfer Protocol Secure | HTTPS | 通信内容を暗号化してWorld Wide Web通信を行う方式。 |
| localhost | - | 同一機器自身を指す名前。 |
| サービス | - | 機能を利用者や他システムへ提供する仕組み。 |
| ユーザ | - | 機能を利用する人, 又は識別された利用主体。 |
| ツール | - | 特定作業を実行するための機能や道具。 |
| Elasticsearch のクラスタ | - | 複数の Elasticsearch ノードを連携させて一体運用する構成。 |
| プログラム | - | 計算機に処理をさせるための命令列。 |
| プラグイン | - | 既存機能へ追加機能を組み込むための拡張部品。 |
| コンテナランタイム | - | コンテナを起動, 停止, 管理する実行基盤。 |
| リクエスト | - | 処理実行や情報取得を要求する操作。 |
| コントローラ | - | 対象状態を監視し, 期待状態へ調整する制御機能。 |
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
| Canonical | - | Ubuntu を提供する組織名。 |
| Key-Value | - | キーと値の組で情報を表す方式。 |
| Structured Query Language | SQL | データベースを操作するための記述言語。 |
| RPM Package Manager | RPM | RPM形式パッケージの導入, 更新, 削除, 情報参照を行う仕組み。 |
| Virtual Machine | VM | 物理計算機上で動作する仮想的な計算機。 |
| Central Processing Unit | CPU | 計算処理を実行する中核部品。 |
| ソフトウェア | - | 情報処理システムで使用するプログラム, 手順, 規則及び関連文書の全体又は一部分。 |
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| アプリケーション | - | 利用者の目的を実現するために動作するソフトウェア。 |
| パッケージ | - | ソフトウェア導入に必要なファイルをまとめた配布単位。 |
| リポジトリ | - | ソフトウェアや設定情報を保管し, 取得できるようにした管理場所。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
| プロトコル | - | 通信やデータ交換の手順を定めた取り決め。 |
| コード | - | 処理内容を記述した文字列。 |
| ファイルシステム | - | 記憶装置上のファイルとディレクトリを管理する仕組み。 |
| プロセス | - | 実行中のプログラムを管理する単位。 |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウェア。 |
| Pod | - | Kubernetes でコンテナをまとめて管理する最小単位。 |
| 名前空間 ( namespace ) | - | Kubernetes内部でリソースを論理的に分離する単位。 |
| Ubuntu | - | Canonical が提供する Debian 系の Linux ディストリビューション。 |
| statコマンド | stat | ファイルの権限, 大きさ及び名前を表示するコマンド。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Elastic Agentポリシー構成種別 | - | Fleet Bootstrap ロールの `fleet_bootstrap_agent_policy_profiles` で管理する `host`, `k8s_system`, `k8s_workload`, `k8s_cluster` の4種類を指す, Elastic Stack固有の分類単位。 |
| 統合パッケージ | - | Elastic Agentへデータの収集方法と収集項目を追加するためのパッケージ。 |
| Package Policy | - | Elastic Agent ポリシーへ追加する収集内容と統合パッケージの設定。 |
| System統合 | - | Elastic Agentが対象ホストのログとメトリクス情報を収集するための統合パッケージ。 |
| Custom Logs統合 | - | Elastic Agentが指定されたログファイルからテキストを収集するための統合パッケージ。 |
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ロール | - | Ansible における処理のまとまり。 |
| Elastic Stack | - | Elasticsearch, Kibana, Logstash, Fleet Server, Fleet Bootstrap, Elastic Agent などで構成される, 収集, 蓄積, 検索, 可視化を行うソフトウェア群。 |
| YAML | - | 設定を読みやすい形式で表す記述方法。 |
| journalctlコマンド | journalctl | サービスが記録したログを確認するコマンド。 |
| elastic-agentコマンド | elastic-agent | Elastic Agentの版数確認や管理処理を実行するコマンド。 |
| Fleet Bootstrap | - | Fleet API を使用して Fleet の初期設定と Enrollment Token 共有を実施する初期化ロール。 |
| Deployment | - | Kubernetesで複数のPodの作成, 更新, 維持を管理するリソース。 |
| DaemonSet | - | Kubernetesで各ノードへPodを常駐配置するリソース。 |
| ConfigMap | - | 設定値をキーと値の組で保存するKubernetesリソース。 |
| Secret | - | 秘密情報を保存するKubernetesリソース。 |
| Service Account | - | Kubernetes上でPodがAPIを利用する主体を識別する情報。 |
| Helm | - | Kubernetes向けパッケージを導入, 更新, 削除するコマンド。 |
| Helm Chart | - | Helmで導入するKubernetesリソース定義のまとまり。 |
| Helm導入識別名 ( Helm release ) | - | Helm が管理する導入単位を識別する名前。 |
| rollout | - | Deploymentなどの更新適用状況を確認する処理。 |
| kubeconfig | - | Kubernetes API接続先と認証情報を記述した設定ファイル。 |
| hostPath | - | Podがノード上のファイルパスを直接参照するためのボリューム定義。 |
| preset | - | Helm valuesで導入構成を選択する設定項目。 |
| clusterWide | - | Kubernetesクラスタ全体を対象として共通処理を実行するためのHelm valuesで指定する導入構成の選択値。 |
| perNode | - | Kubernetesを構成するノードで実施する処理を実行するためのHelm valuesで指定する導入構成の選択値。 |
| values ファイル | - | Helm Chartへ渡す設定値を定義したYAMLファイル。 |
| kube-state-metrics | - | Elastic StackでKubernetesリソース状態を収集するために利用するメトリクス公開コンポーネント。 |
| helmコマンド | helm | Kubernetes向けパッケージの導入, 更新, 状態確認を実施するコマンド。 |
| kubectlコマンド | kubectl | Kubernetes API と通信してリソースを操作, 参照するコマンド。 |
| grepコマンド | grep | テキストの中から条件に一致する行を抽出するコマンド。 |
| tailコマンド | tail | テキストの末尾側を表示するコマンド。 |

## 概要

本ロールは, Elastic Agent for Kubernetes の Helm Chart を使用し, Kubernetesクラスタ監視向け設定で Elastic Agent を導入します。

本ロールの主な処理は次のとおりです。

- `elastic_agent_k8s_enabled` が `true` の場合のみ, 導入処理を実行します。
- `elastic_agent_k8s_fleet_server_url_explicit` が未設定の場合は, 共通設定値から Fleet Server 接続先 URL を組み立てます。
- `elastic_agent_k8s_enrollment_token` が未設定の場合は, Fleet Bootstrap が共有した Enrollment Token を利用します。
- Helm values ファイルをテンプレートから生成し, `preset: clusterWide` と `kube-state-metrics.enabled: true` を明示して適用します。
- Elastic Agent の clusterWide 構成, perNode 構成及び kube-state-metrics 構成の resources を辞書型変数で指定できるようにします。
- DiskPressure 発生時の資源判定を安定化するため, Elastic Agent の resources で ephemeral-storage の要求値と上限値を明示します。
- `helm template` で導入前検証を実施し, `hostPath` 定義の混入がないことを確認します。
- `helm upgrade --install` を待機付きで実行し, 再試行条件を満たすまで適用を試みます。
- 導入後は, Helm導入識別名状態, 名前空間上の関連リソース, 対象のKubernetesクラスタに属するノード全体に対する Deployment 稼働状態を検証します。

## 前提条件

- 対象ホストが, K8sのコントロールプレーンノードの場合, `host_vars`で, `elastic_agent_k8s_enabled` 変数が `true` に設定されていること。
- 対象ホストが, K8sのコントロールプレーンノード以外の場合, `host_vars`で, `elastic_agent_k8s_enabled` 変数が `false` に設定されているか, または, `elastic_agent_k8s_enabled` 変数が定義されていない状態となっていること。
- 対象ホストで `helm` コマンドと `kubectl` コマンドを実行可能であること。
- 対象ホストで Kubernetes API 操作に使用する kubeconfig ファイルを読み取り可能であること。
- Fleet Server が起動済みであり, 対象ホストから Fleet Server 接続先 URL へ到達可能であること。
- Fleet Bootstrap による Enrollment Token 共有処理が完了していること。

## 実行方法

制御ホストで次のいずれかを実行します。

```bash
make run_logging_collector
```

```bash
ansible-playbook -i inventory/hosts logging-collector.yml
```

本ロール単独で確認する場合は, 対象ホストに `elastic_agent_k8s_enabled: true` を設定した上で, 本ロールを呼び出すPlaybookだけを実行する構成としてください。

## 主要変数

### Elastic Stack間共有設定値

共有設定値の意味, 設定要否, 既定値及び設定例は, [Elasticsearchロールの共有設定値](../elasticsearch/Readme.md#varsall-configymlに設定するelastic-stack間共有設定値)を参照します。

### 各ロール固有の利用者入力値

#### 条件付き必須入力値

| 変数名 | 必須となる条件 | 意味 | 設定例 |
| --- | --- | --- | --- |
| `elastic_agent_k8s_enrollment_token` | Fleet Bootstrap 連携を使用せずに明示的に登録トークンを指定する場合。 | Fleet Serverへの登録に使用する秘密情報。 | 対象のElastic Agent ポリシー用Enrollment Token |

#### 任意入力値

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `elastic_agent_k8s_enabled` | ロール実行可否を指定するフラグ変数。 | `false` | `true` |
| `elastic_agent_k8s_helm_timeout_seconds` | Helm 実行タイムアウト秒数。 | `300` | `300` |
| `elastic_agent_k8s_helm_retries` | Helm 実行再試行回数。 | `3` | `3` |
| `elastic_agent_k8s_helm_retry_interval_seconds` | Helm 実行再試行周期。 | `5` | `5` |
| `elastic_agent_k8s_helm_request_interval_seconds` | Kubernetes API 及び Helm 状態確認のリクエスト発行間隔。 | `5` | `5` |
| `elastic_agent_k8s_fleet_server_url_explicit` | Fleet Server 接続先 URL 明示指定値。 | 空文字列 | `https://fleet.example.org:8220` |
| `elastic_agent_k8s_insecure` | Fleet Server 接続時の証明書検証省略フラグ。 | `false` | `false` |
| `elastic_agent_k8s_clusterwide_resources` | clusterWide 構成の Elastic Agent Pod に適用する resources 辞書。 | [elastic_agent_k8s_clusterwide_resources](#elastic_agent_k8s_clusterwide_resources) を参照してください。 | [elastic_agent_k8s_clusterwide_resources](#elastic_agent_k8s_clusterwide_resources) を参照してください。 |
| `elastic_agent_k8s_kube_state_metrics_resources` | kube-state-metrics Pod に適用する resources 辞書。 | [elastic_agent_k8s_kube_state_metrics_resources](#elastic_agent_k8s_kube_state_metrics_resources) を参照してください。 | [elastic_agent_k8s_kube_state_metrics_resources](#elastic_agent_k8s_kube_state_metrics_resources) を参照してください。 |

#### 辞書形式変数の既定値と設定例

##### elastic_agent_k8s_clusterwide_resources

| 辞書のキー | 設定する内容 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `limits.ephemeral-storage` | Pod が使用できる一時領域の上限値を指定します。 | `2Gi` | `3Gi` |
| `limits.memory` | Pod が使用できるメモリの上限値を指定します。 | `800Mi` | `1200Mi` |
| `requests.cpu` | Pod が要求する CPU の下限値を指定します。 | `100m` | `200m` |
| `requests.ephemeral-storage` | Pod が要求する一時領域の下限値を指定します。 | `512Mi` | `1Gi` |
| `requests.memory` | Pod が要求するメモリの下限値を指定します。 | `400Mi` | `600Mi` |

##### elastic_agent_k8s_kube_state_metrics_resources

| 辞書のキー | 設定する内容 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `limits.memory` | Pod が使用できるメモリの上限値を指定します。 | 未設定 | `512Mi` |
| `requests.cpu` | Pod が要求する CPU の下限値を指定します。 | 未設定 | `100m` |
| `requests.memory` | Pod が要求するメモリの下限値を指定します。 | 未設定 | `256Mi` |

### 設定例

`vars/all-config.yml` に共通設定を記載する例を次に示します。

```yaml
1: elastic_agent_k8s_enabled: true
2: elastic_agent_k8s_helm_timeout_seconds: 300
3: elastic_agent_k8s_helm_retries: 3
4: elastic_agent_k8s_helm_retry_interval_seconds: 5
5: elastic_agent_k8s_helm_request_interval_seconds: 5
6: elastic_agent_k8s_fleet_server_url_explicit: "http://fleet.example.org:8220"
7: elastic_agent_k8s_insecure: true
8: elastic_agent_k8s_clusterwide_resources:
9:   limits:
10:     ephemeral-storage: "2Gi"
11:     memory: "1200Mi"
12:   requests:
13:     cpu: "200m"
14:     ephemeral-storage: "512Mi"
15:     memory: "600Mi"
16: elastic_agent_k8s_kube_state_metrics_resources:
17:   limits:
18:     memory: "512Mi"
19:   requests:
20:     cpu: "100m"
21:     memory: "256Mi"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `elastic_agent_k8s_enabled: true` | 本ロールの導入処理を実行します。 | `false` のままでは導入処理が実行されないためです。 |
| 2-5 | タイムアウト値, 再試行回数, 再試行周期, リクエスト発行間隔 | 一時的な接続失敗時に, 指定した周期と間隔で所定回数の再試行を実施します。 | 値が不適切な場合は早期失敗又は過剰待機が発生するためです。 |
| 6-7 | Fleet Server接続先URL, 証明書検証省略フラグ | Fleet Server 登録先と接続方式を指定します。 | URL不整合又は検証設定不整合で登録処理が失敗するためです。 |
| 8-15 | `elastic_agent_k8s_clusterwide_resources` | clusterWide 構成の Elastic Agent Pod が使用する CPU, メモリ, 一時領域の要求値及び上限値を指定します。 | 値が未指定又は不適切な場合は, Pod の資源割当が不足し, 稼働が不安定になるためです。 |
| 16-21 | `elastic_agent_k8s_kube_state_metrics_resources` | kube-state-metrics Pod が使用する CPU とメモリの要求値及び上限値を指定します。 | 値が未指定又は不適切な場合は, クラスタ状態情報収集処理が遅延又は停止するためです。 |

## テンプレートと生成ファイル

| 入力 | 出力 ( 既定 ) | 目的 |
| --- | --- | --- |
| `templates/values.yaml.j2` | `/home/kube/kubeadm/elastic-agent-k8s/values.yaml` など | Helm values ファイルを生成し, `preset: clusterWide`, `agent.presets.clusterWide.resources`, `agent.presets.perNode.resources`, `kube-state-metrics.enabled` 及び任意指定の `kube-state-metrics.resources` を適用する。 |

values.yamlファイルは, Helm 実行ユーザに合わせて実行時に決定されます。
接続ユーザのホーム配下を指すパスが指定された場合は, 接続ユーザと Helm 実行ユーザの実ホームディレクトリを参照して, Helm 実行ユーザ側のホーム配下へ自動変換します。

## 実行フロー

1. [tasks/load-params.yml](tasks/load-params.yml) で共通変数を読み込みます。
2. [tasks/resolve-runtime-vars.yml](tasks/resolve-runtime-vars.yml) で導入に必要な実行時変数を解決します。
3. [tasks/load-enrollment-token.yml](tasks/load-enrollment-token.yml) で Enrollment Token を明示値優先で解決し, 未設定時は Fleet Bootstrap 連携の共有情報を利用します。
4. [tasks/validate.yml](tasks/validate.yml) で Chart版数形式, 名前空間, kubeconfig パス, Enrollment Token, 再試行値を検証します。
5. [tasks/package.yml](tasks/package.yml) で helmコマンドとkubectlコマンドの利用可否を確認します。
6. [tasks/config.yml](tasks/config.yml) で values ファイルをテンプレートから生成します。
7. [tasks/config.yml](tasks/config.yml) で `helm template` を実行し, `hostPath` 定義の非生成を検証します。
8. [tasks/config.yml](tasks/config.yml) で `helm upgrade --install` を実行し, 待機付き導入が失敗した場合は release 状態を再確認して `pending-*` 又は `uninstalling` を解消した後に再試行します。
9. [tasks/verify.yml](tasks/verify.yml) で `helm status` により release 状態を確認します。
10. [tasks/verify.yml](tasks/verify.yml) で名前空間上の関連リソース存在を確認します。
11. [tasks/verify.yml](tasks/verify.yml) で対象のKubernetesクラスタに属するノード全体に対する Deployment の rollout 状態を確認します。

## 検証ポイント

### 検証の前提条件

検証を始める前に, 次の条件が満たされていることを確認します。

- 対象ホストで `helm` コマンドと `kubectl` コマンドを実行可能であること。
- `elastic_agent_k8s_enabled` が `true` に設定されていること。
- Kubernetes API 操作で使用する kubeconfig ファイルを対象ホストで読み取り可能であること。
- Fleet Server が起動済みであること。
- Fleet Bootstrap による Enrollment Token 共有処理が完了していること。

### 検証環境の設定

本節では, 検証用の設定内容について説明します。

**検証用の vars/all-config.yml**:

```yaml
1: elastic_agent_k8s_enabled: true
2: elastic_agent_k8s_fleet_server_url_explicit: "https://fleet.example.org:8220"
3: elastic_agent_k8s_insecure: true
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `elastic_agent_k8s_enabled: true` | 導入処理と検証処理を実行します。 | `false` の場合は検証対象の導入が行われないためです。 |
| 2-3 | Fleet Server接続先URL, 証明書検証省略フラグ | Fleet Server登録先と通信方式を指定します。 | 接続先又は検証設定が不整合な場合は登録失敗が発生するためです。 |

### 検証コマンドと期待結果

#### 1. Helm導入識別名 状態確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト (K8sのコントロールプレーンノード)

**実行するコマンド**:

```bash
helm status elastic-agent-k8s --namespace kube-system --output json | jq -r '.info.status'
```

**期待される出力**:

```plaintext
deployed
```

**実行結果の例**:

```bash
$ helm status elastic-agent-k8s --namespace kube-system --output json | jq -r '.info.status'
deployed
```

**確認ポイント**:

- 出力が `deployed` であることを確認することで, Helm導入識別名が適用済みであることを確認します。

#### 2. Deployment 稼働状態確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト (K8sのコントロールプレーンノード)

**実行するコマンド**:

Kubernetes 共通設定で解決された Helm 実行ユーザを使用し, 共通設定が未指定の場合は `k8s_operator_user`変数で指定されたユーザ(既定:`kube`)を使用します。`${HOME}` は実行ユーザのホームディレクトリを指します。

```bash
kubectl --kubeconfig "${HOME}/.kube/ca-embedded-admin.conf" -n kube-system get deployment -l app.kubernetes.io/instance=elastic-agent-k8s
kubectl --kubeconfig "${HOME}/.kube/ca-embedded-admin.conf" -n kube-system rollout status deployment/kube-state-metrics --timeout=300s
```

**期待される出力**:

```plaintext
NAME                                        READY   UP-TO-DATE   AVAILABLE
kube-state-metrics                          1/1     1            1
deployment "kube-state-metrics" successfully rolled out
```

**実行結果の例**:

```bash
$ kubectl --kubeconfig "${HOME}/.kube/ca-embedded-admin.conf" -n kube-system get deployment -l app.kubernetes.io/instance=elastic-agent-k8s
NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE
agent-clusterwide-elastic-agent-k8s   1/1     1            1           44m
kube-state-metrics                    1/1     1            1           44m
$ kubectl --kubeconfig "${HOME}/.kube/ca-embedded-admin.conf" -n kube-system rollout status deployment/kube-state-metrics --timeout=300s
deployment "kube-state-metrics" successfully rolled out
```

**確認ポイント**:

- `AVAILABLE` 列が `1` 以上であることを確認することで, 対象のKubernetesクラスタに属するノード全体に対するDeploymentが稼働していることを確認します。
- `successfully rolled out` が表示されることを確認することで, rollout が完了していることを確認します。

#### 3. kube-state-metrics 設定確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト (K8sのコントロールプレーンノード)

**実行するコマンド**:

```bash
helm get values elastic-agent-k8s --namespace kube-system -o yaml | yq '.["kube-state-metrics"].enabled == true'
```

**期待される出力**:

```plaintext
true
```

**実行結果の例**:

```bash
$ helm get values elastic-agent-k8s --namespace kube-system -o yaml | yq '.["kube-state-metrics"].enabled == true'
true
```

**確認ポイント**:

- `kube-state-metrics` の `enabled` が `true` であることを確認することで, クラスタ状態情報収集設定が有効であることを確認します。

## トラブルシューティング

### 1. Helm template 検証で停止する場合

**実施対象ホスト**: logging_collector グループに属する対象ホスト (K8sのコントロールプレーンノード)

**実行するコマンド**:

```bash
helm template elastic-agent-k8s elastic/elastic-agent --namespace kube-system --version 8.19.19 --kubeconfig "${HOME}/.kube/ca-embedded-admin.conf" -f "${HOME}/kubeadm/elastic-agent-k8s/values.yaml" | grep -nE '^[[:space:]]*hostPath[[:space:]]*:'
```

**実行結果の例**:

```bash
$ helm template elastic-agent-k8s elastic/elastic-agent --namespace kube-system --version 8.19.19 --kubeconfig "${HOME}/.kube/ca-embedded-admin.conf" -f "${HOME}/kubeadm/elastic-agent-k8s/values.yaml" | grep -nE '^[[:space:]]*hostPath[[:space:]]*:'
$
```

**確認ポイント**:

- 出力に一致行がある場合は, values ファイル又は Chart 版数の組み合わせにより不要なボリューム定義が混入していることを確認します。
- 出力に一致行がない場合は, テンプレート検証失敗の原因が `hostPath` 混入でないことを確認します。

### 2. Deployment の rollout 待機で停止する場合

**実施対象ホスト**: logging_collector グループに属する対象ホスト (K8sのコントロールプレーンノード)

**実行するコマンド**:

Kubernetes 共通設定で解決された Helm 実行ユーザを使用し, 共通設定が未指定の場合は `k8s_operator_user`変数で指定されたユーザ(既定:`kube`)を使用します。`${HOME}` は実行ユーザのホームディレクトリを指します。

```bash
kubectl --kubeconfig "${HOME}/.kube/ca-embedded-admin.conf" -n kube-system get deployment -l app.kubernetes.io/instance=elastic-agent-k8s -o wide
kubectl --kubeconfig "${HOME}/.kube/ca-embedded-admin.conf" -n kube-system describe deployment kube-state-metrics
kubectl --kubeconfig "${HOME}/.kube/ca-embedded-admin.conf" -n kube-system get events --sort-by=.metadata.creationTimestamp | tail -n 50
```

**実行結果の例**:

```bash
$ kubectl --kubeconfig "${HOME}/.kube/ca-embedded-admin.conf" -n kube-system get deployment -l app.kubernetes.io/instance=elastic-agent-k8s -o wide
NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS           IMAGES                                                          SELECTOR
agent-clusterwide-elastic-agent-k8s   1/1     1            1           10h   agent                docker.elastic.co/elastic-agent/elastic-agent:8.19.19           name=agent-clusterwide-elastic-agent-k8s
kube-state-metrics                    1/1     1            1           10h   kube-state-metrics   registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.16.0   app.kubernetes.io/instance=elastic-agent-k8s,app.kubernetes.io/name=kube-state-metrics
$ kubectl --kubeconfig "${HOME}/.kube/ca-embedded-admin.conf" -n kube-system describe deployment kube-state-metrics
Name:                   kube-state-metrics
Namespace:              kube-system
CreationTimestamp:      Tue, 11 Aug 2026 15:00:11 +0900
Labels:                 app.kubernetes.io/component=metrics
                        app.kubernetes.io/instance=elastic-agent-k8s
                        app.kubernetes.io/managed-by=Helm
                        app.kubernetes.io/name=kube-state-metrics
                        app.kubernetes.io/part-of=kube-state-metrics
                        app.kubernetes.io/version=2.16.0
                        helm.sh/chart=kube-state-metrics-6.1.0
Annotations:            deployment.kubernetes.io/revision: 1
                        meta.helm.sh/release-name: elastic-agent-k8s
                        meta.helm.sh/release-namespace: kube-system
Selector:               app.kubernetes.io/instance=elastic-agent-k8s,app.kubernetes.io/name=kube-state-metrics
Replicas:               1 desired | 1 updated | 1 total | 1 available | 0 unavailable
StrategyType:           RollingUpdate
MinReadySeconds:        0
RollingUpdateStrategy:  25% max unavailable, 25% max surge
Pod Template:
  Labels:           app.kubernetes.io/component=metrics
                    app.kubernetes.io/instance=elastic-agent-k8s
                    app.kubernetes.io/managed-by=Helm
                    app.kubernetes.io/name=kube-state-metrics
                    app.kubernetes.io/part-of=kube-state-metrics
                    app.kubernetes.io/version=2.16.0
                    helm.sh/chart=kube-state-metrics-6.1.0
  Service Account:  kube-state-metrics
  Containers:
   kube-state-metrics:
    Image:      registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.16.0
    Port:       8080/TCP
    Host Port:  0/TCP
    Args:
      --port=8080
      --resources=certificatesigningrequests,configmaps,cronjobs,daemonsets,deployments,endpoints,horizontalpodautoscalers,ingresses,jobs,leases,limitranges,mutatingwebhookconfigurations,namespaces,networkpolicies,nodes,persistentvolumeclaims,persistentvolumes,poddisruptionbudgets,pods,replicasets,replicationcontrollers,resourcequotas,secrets,services,statefulsets,storageclasses,validatingwebhookconfigurations,volumeattachments
    Liveness:      http-get http://:8080/livez delay=5s timeout=5s period=10s #success=1 #failure=3
    Readiness:     http-get http://:8081/readyz delay=5s timeout=5s period=10s #success=1 #failure=3
    Environment:   <none>
    Mounts:        <none>
  Volumes:         <none>
  Node-Selectors:  <none>
  Tolerations:     <none>
Conditions:
  Type           Status  Reason
  ----           ------  ------
  Progressing    True    NewReplicaSetAvailable
  Available      True    MinimumReplicasAvailable
OldReplicaSets:  <none>
NewReplicaSet:   kube-state-metrics-8556695f7c (1/1 replicas created)
Events:          <none>
$ kubectl --kubeconfig "${HOME}/.kube/ca-embedded-admin.conf" -n kube-system get events --sort-by=.metadata.creationTimestamp | tail -n 50
23s         Normal    Scheduled             pod/agent-clusterwide-elastic-agent-k8s-7d55dbc8f4-p78vs    Successfully assigned kube-system/agent-clusterwide-elastic-agent-k8s-7d55dbc8f4-p78vs to k8sworker0201
22s         Normal    AddedInterface        pod/agent-clusterwide-elastic-agent-k8s-7d55dbc8f4-p78vs    Add eth0 [fdb6:6e92:3cfb:102::48eb/128 10.243.2.133/32] from cilium
20s         Normal    Pulled                pod/agent-clusterwide-elastic-agent-k8s-7d55dbc8f4-p78vs    Container image "docker.elastic.co/elastic-agent/elastic-agent:8.19.19" already present on machine
18s         Normal    Started               pod/agent-clusterwide-elastic-agent-k8s-7d55dbc8f4-p78vs    Started container agent
18s         Normal    Created               pod/agent-clusterwide-elastic-agent-k8s-7d55dbc8f4-p78vs    Created container: agent
```

**確認ポイント**:

- `get deployment` の出力結果中の `READY` と `AVAILABLE` を確認することで, 起動完了状態を確認します。
- `describe deployment` の出力結果中の `Events` を確認することで, イメージ取得失敗又は権限不足などの原因を確認します。
- `get events` の出力結果中の `Warning` を確認することで, 直近の異常事象を確認します。

## 注意事項

- 本ロールは `elastic_agent_k8s_enabled` が `true` の場合だけ導入処理を実行します。
- Enrollment Token を `vars/all-config.yml` や版管理対象ファイルへ保存しないでください。
- `elastic_agent_k8s_insecure: true` は検証環境を前提とした設定です。本番運用では HTTPS と証明書検証を使用してください。
- 本ロールは `helm template` と `helm upgrade --install` を同一 values で実行します。適用前後で入力値を変更しない運用としてください。

## 参考資料

### 公式ドキュメント

- [ansible-playbookコマンド](https://docs.ansible.com/ansible/latest/cli/ansible-playbook.html)
- [makeコマンドとMakefile](https://www.gnu.org/software/make/manual/make.html)
- [Helm コマンド](https://helm.sh/docs/helm/helm/)
- [helm template](https://helm.sh/docs/helm/helm_template/)
- [helm upgrade](https://helm.sh/docs/helm/helm_upgrade/)
- [helm status](https://helm.sh/docs/helm/helm_status/)
- [jq Manual](https://jqlang.github.io/jq/manual/)
- [yq Documentation](https://mikefarah.gitbook.io/yq/)
- [kubectlコマンド](https://kubernetes.io/docs/reference/kubectl/)
- [kubectl rollout status](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/kubectl_rollout_status/)
- [Elastic Agent for Kubernetes](https://www.elastic.co/guide/en/fleet/current/running-on-kubernetes-managed-by-fleet.html)
- [Fleet Server](https://www.elastic.co/docs/reference/fleet/fleet-server)
- [Enrollment Token](https://www.elastic.co/docs/reference/fleet/fleet-enrollment-tokens)
- [kube-state-metrics](https://github.com/kubernetes/kube-state-metrics)
- [Kubernetes Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes DaemonSet](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)

### 関連ロール

- [roles/elasticsearch/Readme.md](../elasticsearch/Readme.md)
- [roles/logstash/Readme.md](../logstash/Readme.md)
- [roles/kibana/Readme.md](../kibana/Readme.md)
- [roles/fleet-server/Readme.md](../fleet-server/Readme.md)
- [roles/fleet-bootstrap/Readme.md](../fleet-bootstrap/Readme.md)
- [roles/elastic-agent/Readme.md](../elastic-agent/Readme.md)
