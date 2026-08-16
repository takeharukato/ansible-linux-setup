# elastic-agent-k8s-audit ロール

本ロールは, Kubernetes (K8s)のAPI監視情報をElastic Stackを用いて収集するための設定を行います。

- [elastic-agent-k8s-audit ロール](#elastic-agent-k8s-audit-ロール)
  - [用語](#用語)
  - [概要](#概要)
    - [導入するElastic Agentの導入仕様](#導入するelastic-agentの導入仕様)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
    - [Elastic Stack間共有設定値](#elastic-stack間共有設定値)
    - [各ロール固有の利用者入力値](#各ロール固有の利用者入力値)
      - [有効化変数](#有効化変数)
      - [任意入力値](#任意入力値)
    - [設定例](#設定例)
      - [`vars/all-config.yml`への設定例](#varsall-configymlへの設定例)
      - [Kubernetesコントロールプレーンノードの`host_vars`への設定例](#kubernetesコントロールプレーンノードのhost_varsへの設定例)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [検証ポイント](#検証ポイント)
    - [検証の前提条件](#検証の前提条件)
    - [検証環境の設定](#検証環境の設定)
    - [検証コマンドと期待結果](#検証コマンドと期待結果)
      - [1. Helm release状態](#1-helm-release状態)
      - [2. Audit用DaemonSetとPod状態](#2-audit用daemonsetとpod状態)
    - [3. Pod内からの監査ログ読み取り](#3-pod内からの監査ログ読み取り)
    - [4. Fleet Agent状態](#4-fleet-agent状態)
    - [5. Data Streamと監査イベント](#5-data-streamと監査イベント)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. Enrollment Tokenを取得できない場合](#1-enrollment-tokenを取得できない場合)
    - [2. DaemonSetが配置されない場合](#2-daemonsetが配置されない場合)
    - [3. `audit.log`をPodから読めない場合](#3-auditlogをpodから読めない場合)
    - [4. Data Streamが作成されない又は更新されない場合](#4-data-streamが作成されない又は更新されない場合)
  - [注意事項](#注意事項)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)
    - [関連ロール](#関連ロール)


## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| Playbook | - | 自動化処理の実行手順を記述したファイル。 |
| Helm Chart | - | Helmで導入するKubernetesリソース定義のまとまり。 |
| rollout | - | Deploymentなどの更新適用状況を確認する処理。 |
| kubeconfig | - | Kubernetes API接続先と認証情報を記述した設定ファイル。 |
| hostPath | - | Podがノード上のファイルパスを直接参照するためのボリューム定義。 |
| preset | - | Helm valuesで導入構成を選択する設定項目。 |
| clusterWide | - | Kubernetesクラスタ全体を対象として共通処理を実行するためのHelm valuesで指定する導入構成の選択値。 |
| perNode | - | Kubernetesを構成するノードで実施する処理を実行するためのHelm valuesで指定する導入構成の選択値。 |
| kube-state-metrics | - | Elastic StackでKubernetesリソース状態を収集するために利用するメトリクス公開コンポーネント。 |
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
| Enrollment Token共有ファイル | - | Fleet BootstrapがEnrollment Tokenを制御ホスト上へ保存し, Elastic Agent本体ロールがFleet Serverへの登録時に読み込む権限`0600`のYAMLファイル。 |
| Fleet Serverサービスアカウントトークンファイル | - | Fleet ServerがElasticsearchへ接続するためのサービスアカウントトークンを対象ホスト上へ保存し, Fleet Serverコンテナが起動時に読み込む権限`0600`のファイル。 |
| Classless Inter-Domain Routing | CIDR | Internet Protocolアドレスの範囲を先頭アドレスと接頭辞長で表す方式。 |
| Docker bridge network | Dockerブリッジネットワーク | 同一対象ホスト上のコンテナ間通信に使用する仮想的なネットワーク。 |
| Network Address Translation | NAT | 通信時にIPアドレスを変換する処理。 |
| systemd | - | Linux上でサービスの起動順序と実行状態を管理するソフトウェア。 |
| pipeline | - | 入力, 整形, 出力の処理順を定義する Logstash の設定単位。 |
| Elastic Agent入力 | - | Elastic Agentからデータストリーム情報を保持したイベントを受信するLogstashの入力機能。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| inventory group | - | Ansible Inventory内で同じ役割の対象ホストをまとめる識別単位。 |
| single-node | - | Elasticsearch を単一ノード構成で構成する方式。コンテナイメージを用いた導入時に典型的に用いられる。 |
| Hypertext Transfer Protocol | HTTP | World Wide Webで情報をやり取りする通信手順。 |
| Internet Protocol | IP | ネットワーク上で宛先を識別し, データを届けるための通信手順。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| Fully Qualified Domain Name | FQDN | 末尾まで省略せず書いた完全なドメイン名。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Linux | - | 多くの機器で使われる, 基本ソフトウェアの系統。 |
| Debian | - | コミュニティ主導で開発される Linux ディストリビューション。 |
| Red Hat | - | Red Hat Enterprise Linuxなどを提供する組織。 |
| Red Hat Enterprise Linux | RHEL | Red Hatが提供する企業向けLinuxディストリビューション。 |
| root | - | Unix 系システムの最上位権限を持つ管理者識別子。 |
| cron | - | 指定した時刻や周期でコマンドを自動実行する仕組み。 |
| Ansible Playbook | Playbook | Ansibleで実行する処理の順序と対象を記述したファイル。 |
| iptables | - | Linux の IPv4 パケットフィルタ設定ツール。 |
| ip6tables | - | Linux の IPv6 パケットフィルタ設定ツール。 |
| Python | - | スクリプティングやアプリケーション開発を手早く実施するために用いられる高水準プログラミング言語の一種。 |
| Canonical | - | Ubuntu を提供する組織名。 |
| Structured Query Language | SQL | データベースを操作するための記述言語。 |
| RPM Package Manager | RPM | RPM形式パッケージの導入, 更新, 削除, 情報参照を行う仕組み。 |
| Virtual Machine | VM | 物理計算機上で動作する仮想的な計算機。 |
| Central Processing Unit | CPU | 計算処理を実行する中核部品。 |
| Hypertext Transfer Protocol Secure | HTTPS | 通信内容を暗号化してWorld Wide Web通信を行う方式。 |
| localhost | - | 同一機器自身を指す名前。 |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウェア。 |
| Kubernetes API監査機能 ( Kubernetes API Audit )| - | Kubernetesクラスター内の一連の行動を記録するセキュリティに関連した時系列の記録を提供する機能。 |
| Pod | - | Kubernetes でコンテナをまとめて管理する最小単位。 |
| Ubuntu | - | Canonical が提供する Debian 系の Linux ディストリビューション。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Package Policy | - | Elastic Agent ポリシーへ追加する収集内容と統合パッケージの設定。 |
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| Elastic Stack | - | Elasticsearch, Kibana, Logstash, Fleet Server, Fleet Bootstrap, Elastic Agent などで構成される, 収集, 蓄積, 検索, 可視化を行うソフトウェア群。 |
| YAML | - | 設定を読みやすい形式で表す記述方法。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Key-Value | - | キーと値の組で情報を表す方式。 |
| Elasticsearchのサービスアカウントトークン ( Elasticsearch Service Account Token ) | - | Elasticsearchが提供するサービスアカウントに紐付く認証情報。 |
| Fleet Bootstrap | - | Fleet API を使用して Fleet の初期設定と Enrollment Token 共有を実施する初期化ロール。 |
| Deployment | - | Kubernetesで複数のPodの作成, 更新, 維持を管理するリソース。 |
| DaemonSet | - | Kubernetesで各ノードへPodを常駐配置するリソース。 |
| ConfigMap | - | 設定値をキーと値の組で保存するKubernetesリソース。 |
| Secret | - | 秘密情報を保存するKubernetesリソース。 |
| Service Account | - | Kubernetes上でPodがAPIを利用する主体を識別する情報。 |
| ロール | - | Ansible における処理のまとまり。 |
| System統合 | - | Elastic Agentが対象ホストのログとメトリクス情報を収集するための統合パッケージ。 |
| Custom Logs統合 | - | Elastic Agentが指定されたログファイルからテキストを収集するための統合パッケージ。 |
| インデックス | - | Elasticsearch に保存するデータの格納先識別単位。 |
| コンテナイメージ | - | コンテナ実行に必要な内容をまとめた保存形式。 |
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
| ホスト | - | 管理対象として識別される個別の計算機。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| サーバ | - | 他の機器や利用者へ機能やデータを提供する計算機, 又はその役割。 |
| ネットワーク | - | 機器同士を接続してデータをやり取りする仕組み。 |
| ディレクトリ | - | ファイルを階層的に整理するための入れ物。 |
| ログ | - | 処理の結果や状態を時系列で記録した情報。 |
| メトリクス | - | ホストやサービスの状態を数値で表した観測情報。 |
| データ | - | 処理や保存の対象となる情報。 |
| ポート | - | 通信の出入口を識別する番号または接点。 |
| URL スキーム | - | URL の先頭で通信方式を示す部分。例: `http`, `https`。 |
| ランタイムエンドポイント ( rumtime endpoint ) | - | 対象ホスト上で所定のサービスが動作していることを確認するための疎通確認に用いるエンドポイントです。ここでのエンドポイントは, <接続先ホスト名>と<接続先ポート番号>の組から構成されるURLになります。本ロールで規定した変数により明示的に指定されたエンドポイントがあればその値を採用し, 未指定の場合は, 対象ホスト名とポート番号からエンドポイントを組み立てます。 |
| 対象ホスト上での疎通確認 | - | 対象ホスト上で自ホスト(localhost)を指定して待ち受け先ポートへの疎通確認を実施すること。確認対象のサービスが対象ホスト上で起動していることを確認します。 |
| 外部ホストからの疎通確認 | - | 対象ホスト以外のホストから対象ホストを指定して待ち受け先ポートへの疎通確認を実施すること。確認対象のサービスがネットワーク接続を含めて適切に設定され, サービス受付可能な状態になっていることを確認します。 |
| ディストリビューション | - | 基本ソフトウェアと関連部品をまとめた配布形態。 |
| コミュニティ | - | 共通目的のもとで継続的に活動する利用者集団。 |
| ホストメトリクス ( host metrics ) | - | リソース使用状況など, ログ収集対象となるホスト群から収集する情報。 |
| ループ | - | 同じ処理を繰り返すこと。 |
| バックエンド | - | 利用者画面の背後で処理を実行する側。 |
| メタデータ | - | 対象データの属性や説明を示す付加情報。 |
| リソース | - | 処理に必要な計算機資源やデータ。 |
| コマンド | - | 実行者が計算機へ処理を指示するための命令。 |
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
| 名前空間 ( namespace ) | - | Kubernetes内部でリソースを論理的に分離する単位。 |
| サービスアカウント (Service Account) | - | 自動処理中でサービスを呼び出す側のプログラムを識別するための識別情報。 |
| Elastic Agentポリシー構成種別 | - | Fleet Bootstrap ロールの `fleet_bootstrap_agent_policy_profiles` で管理する `host`, `k8s_system`, `k8s_workload`, `k8s_cluster` の4種類を指す, Elastic Stack固有の分類単位。 |
| 統合パッケージ | - | Elastic Agentへデータの収集方法と収集項目を追加するためのパッケージ。 |
| Docker Compose | - | 複数のコンテナ定義をまとめて作成, 起動, 停止, 更新する仕組み。 |
| Docker Compose 定義ファイル | - | Docker Compose が参照するコンテナ構成の定義ファイル。 |
| compose project 名 | - | Docker Compose によって展開される個々のアプリケーションを識別する名前です。展開されたコンテナ, ネットワーク, ボリュームなどのリソースをグループ化し, 他のアプリケーション又は別途展開された同じアプリケーションと区別するために用います。 |
| Helm導入識別名 ( Helm release ) | - | Helm が管理する導入単位を識別する名前。 |
| values ファイル | - | Helm Chartへ渡す設定値を定義したYAMLファイル。 |
| ansible-playbookコマンド | ansible-playbook | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |
| makeコマンド | make | Makefile に定義された処理を実行するコマンド。 |
| curlコマンド | curl | URL を指定して通信結果を取得するコマンド。 |
| 環境変数 | - | 実行時の動作を調整するために外部から渡す設定値。 |
| dockerコマンド | - | Dockerブリッジネットワークを作成及び確認するコマンド。 |
| iptablesコマンド | - | IPパケットの通過条件とNAT規則を確認するコマンド。 |
| ip6tablesコマンド | - | IPv6パケットの通過条件とNAT規則を確認するコマンド。 |
| systemctlコマンド | - | systemdが管理するサービスの状態を確認するコマンド。 |
| jqコマンド | jq | JSON 形式のデータから必要な項目だけを抽出して表示するコマンド。 |
| yqコマンド | yq | YAML 形式のデータから必要な項目だけを抽出して表示するコマンド。 |
| statコマンド | stat | ファイルの権限, 大きさ及び名前を表示するコマンド。 |
| journalctlコマンド | journalctl | サービスが記録したログを確認するコマンド。 |
| elastic-agentコマンド | elastic-agent | Elastic Agentの版数確認や管理処理を実行するコマンド。 |
| Helm | - | Kubernetes向けパッケージを導入, 更新, 削除するコマンド。 |
| helmコマンド | helm | Kubernetes向けパッケージの導入, 更新, 状態確認を実施するコマンド。 |
| kubectlコマンド | kubectl | Kubernetes API と通信してリソースを操作, 参照するコマンド。 |
| grepコマンド | grep | テキストの中から条件に一致する行を抽出するコマンド。 |
| tailコマンド | tail | テキストの末尾側を表示するコマンド。 |

## 概要

本ロールは, Kubernetes API監査機能がコントロールプレーンノード上へ出力する監査ログを, Elastic Agent for Kubernetes の公式Helm Chartを使用して収集するためのElastic Agentを導入します。

本ロールが導入するElastic Agentは, 通常のKubernetesクラスタ状態情報を収集する`elastic-agent-k8s`ロールとは別のHelm導入識別名`elastic-agent-k8s-audit`で管理します。Fleet Bootstrapが作成する`k8s_audit`構成種別のElastic Agentポリシーへ登録し, Kubernetes統合の`audit-logs-filestream`入力から`kubernetes.audit_logs`データ集合を収集します。

監査ログの収集経路は次のとおりです。

```text
kube-apiserver
  -> /var/log/kubernetes/audit/audit.log
  -> hostPath
  -> elastic-agent-k8s-audit DaemonSet
  -> Fleet Serverから配布されるk8s_audit Elastic Agentポリシー
  -> Kubernetes統合 audit-logs-filestream
  -> Logstash Fleet Output
  -> Elasticsearch
  -> logs-kubernetes.audit_logs-k8s_system
  -> Kibana Discover
```

本ロールの主な処理は次のとおりです。

- `elastic_agent_k8s_audit_enabled`が`true`の場合だけ導入処理を実行します。
- `elastic-agent-k8s`ロールと同じHelmリポジトリ, Helm Chart版数, Kubernetes名前空間及びkubeconfig設定を継承します。
- Fleet Server接続先をElastic Stack共通設定から解決します。
- Fleet Bootstrapが制御ホスト上へ保存したEnrollment Token共有ファイルから`k8s_audit`構成種別のEnrollment Tokenを取得します。
- Helm valuesを生成し, `preset: perNode`, `mode: daemonset`としてElastic Agentを配置します。
- 既定では`node-role.kubernetes.io/control-plane`ラベルを持つLinuxノードだけへPodを配置します。
- `/var/log/kubernetes/audit`を`/hostfs/var/log/kubernetes/audit`へread-onlyのhostPathとしてマウントします。
- Kubernetes統合, System統合及びkube-state-metricsをHelm Chart側では無効化し, 実際の収集設定はFleet Bootstrapが作成するPackage Policyから配布します。
- `helm template`で, hostNetworkが有効化されていないこと, kube-state-metricsが生成されないこと, DaemonSetと監査ログ用volumeMountが生成されることを事前検証します。
- Helm releaseが`pending-*`又は`uninstalled`等の不整合状態にある場合は, 必要なクリーンアップ後に`helm upgrade --install`を再実行します。
- 導入後はHelm release, 監査ログ用DaemonSet, 対応Pod, control-plane配置及びPod内からの`audit.log`読み取り可否を検証します。

### 導入するElastic Agentの導入仕様

| 項目 | 既定値又は仕様 |
| --- | --- |
| Helm導入識別名 | `elastic-agent-k8s-audit` |
| Helm Chart | `elastic/elastic-agent` |
| Chart版数 | `elastic_agent_k8s_chart_version`を継承 |
| Kubernetes名前空間 | `elastic_agent_k8s_namespace`を継承。既定は`kube-system` |
| preset | `perNode` |
| mode | `daemonset` |
| hostNetwork | `false` |
| statePersistence | `HostPath` |
| Kubernetes統合(Helm values) | `false` |
| System統合(Helm values) | `false` |
| kube-state-metrics | `false` |
| 監査ログホスト側ディレクトリ | `/var/log/kubernetes/audit` |
| 監査ログコンテナ側ディレクトリ | `/hostfs/var/log/kubernetes/audit` |
| 収集ファイル | `/hostfs/var/log/kubernetes/audit/audit.log` |
| Fleet構成種別 | `k8s_audit` |
| Kubernetes統合入力 | `audit-logs-filestream` |
| データ集合 | `kubernetes.audit_logs` |
| データストリーム名前空間 | `k8s_system` |
| 生成されるData Stream | `logs-kubernetes.audit_logs-k8s_system` |
| 配置対象 | 既定ではLinuxのコントロールプレーンノード |
| Agent自身の監視 | `vars/all-config.yml`の共通設定で制御 |

## 前提条件

- Kubernetes API監査機能が有効であり, 各対象コントロールプレーンノードで`/var/log/kubernetes/audit/audit.log`が生成されていること。
- `audit.log`がJSON Lines形式のKubernetes Audit Eventとして出力されていること。
- 対象ホストがKubernetesのコントロールプレーンノードの場合, `host_vars`で`elastic_agent_k8s_audit_enabled: true`を設定していること。
- 監査ログ収集対象外ホストでは`elastic_agent_k8s_audit_enabled`を`false`にするか未定義とすること。
- 対象ホストで`helm`及び`kubectl`コマンドを実行できること。
- Helm実行ユーザがKubernetes API操作に使用するkubeconfigを読み取れること。
- Fleet Serverが起動済みであり, KubernetesクラスタからFleet Server接続先へ到達できること。
- Fleet Bootstrapが`k8s_audit`構成種別のElastic Agentポリシー, Kubernetes統合Package Policy及びEnrollment Tokenを作成済みであること。
- 現行Fleet Bootstrap実装ではKubernetes統合パッケージの明示導入条件が`include_k8s_cluster: true`であるため, 既定の`k8s_cluster`構成種別を維持した状態でFleet Bootstrapを実行すること。
- `fleet_bootstrap_enrollment_token_file`で指定するEnrollment Token共有ファイルが制御ホスト上に存在し, 通常ファイルかつ権限`0600`であること。

## 実行方法

制御ホストでlogging collector全体を構成する場合は次を実行します。

```bash
make run_logging_collector
```

又は次を実行します。

```bash
ansible-playbook -i inventory/hosts logging-collector.yml
```

本ロールだけを実行する場合は, 対象のコントロールプレーンノードに`elastic_agent_k8s_audit_enabled: true`を設定し, 以下を実行します:

```bash
make run_elastic_agent_k8s_audit
```

または, 次のようにタグを指定して, `ansible-playbook`コマンドを実行します:

```bash
ansible-playbook -i inventory/hosts logging-collector.yml --tags elastic-agent-k8s-audit
```

Fleet Bootstrap側の設定を変更した場合は, 先にlogging backend又はFleet Bootstrapを適用して`k8s_audit`用Enrollment Token共有ファイルを更新してから本ロールを実行します。

## 主要変数

### Elastic Stack間共有設定値

共有設定値の意味, 設定要否, 既定値及び設定例は, [Elasticsearchロールの共有設定値](../elasticsearch/Readme.md#varsall-configymlに設定するelastic-stack間共有設定値)を参照します。

本ロールに直接関係する共有設定値は次のとおりです。

| 変数名 | 意味 | 既定値 |
| --- | --- | --- |
| `logging_backend_elastic_agent_k8s_audit_package_policy_enabled` | `k8s_audit`構成種別向けKubernetes統合Package Policyを作成又は更新するかを指定します。 | `true` |
| `logging_backend_elastic_agent_k8s_audit_data_stream_namespace` | Kubernetes API監査ログのデータストリーム名前空間を指定します。 | `k8s_system` |
| `logging_backend_elastic_agent_k8s_audit_monitoring_enabled` | Kubernetes API監査ログ収集用Elastic Agent自身の監視を有効化します。 | 利用者設定 |
| `logging_backend_elastic_agent_k8s_audit_monitoring_logs_enabled` | Kubernetes API監査ログ収集用Elastic Agent自身の監視ログを収集します。 | 利用者設定 |
| `logging_backend_elastic_agent_k8s_audit_monitoring_metrics_enabled` | Kubernetes API監査ログ収集用Elastic Agent自身の監視メトリクスを収集します。 | 利用者設定 |
| `fleet_bootstrap_enrollment_token_file` | Fleet BootstrapがEnrollment Tokenを保存する制御ホスト上のファイルを指定します。 | `{{ playbook_dir }}/group_vars/logging_collector/enrollment-token.yml` |

監視関連3変数はFleet Bootstrapと本ロールの双方から参照するため, `host_vars`ではなく`vars/all-config.yml`へ設定します。

### 各ロール固有の利用者入力値

#### 有効化変数

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `elastic_agent_k8s_audit_enabled` | Kubernetes API監査ログ収集用Elastic Agentの導入を有効化します。 | `false` | `true` |

#### 任意入力値

| 変数名 | 意味 | 既定値 |
| --- | --- | --- |
| `elastic_agent_k8s_audit_helm_timeout_seconds` | Helm操作のタイムアウト秒数。 | `300` |
| `elastic_agent_k8s_audit_helm_retries` | Helm操作の再試行回数。 | `3` |
| `elastic_agent_k8s_audit_helm_retry_interval_seconds` | Helm操作の再試行間隔秒数。 | `5` |
| `elastic_agent_k8s_audit_helm_request_interval_seconds` | Kubernetes API及びHelm状態確認の実行間隔秒数。 | `5` |
| `elastic_agent_k8s_audit_host_log_dir` | Kubernetes監査ログのホスト側格納ディレクトリ。 | `/var/log/kubernetes/audit` |
| `elastic_agent_k8s_audit_container_log_dir` | Elastic Agentコンテナ内の監査ログ参照ディレクトリ。 | `/hostfs/var/log/kubernetes/audit` |
| `elastic_agent_k8s_audit_resources` | Audit用Elastic Agent Podのresources定義。 | 下記参照 |
| `elastic_agent_k8s_audit_node_selector` | Audit用Elastic Agentを配置するノード条件。 | Linuxかつcontrol-plane |
| `elastic_agent_k8s_audit_tolerations` | control-planeのNoSchedule Taintを許容する設定。 | control-plane Exists/NoSchedule |

`elastic_agent_k8s_audit_resources`の既定値は次のとおりです。

```yaml
elastic_agent_k8s_audit_resources:
  limits:
    memory: 1000Mi
  requests:
    cpu: 100m
    memory: 400Mi
```

CPU上限値及び`ephemeral-storage`の上限値は本ロールの既定値では設定しません。

配置条件の既定値は次のとおりです。

```yaml
elastic_agent_k8s_audit_node_selector:
  kubernetes.io/os: linux
  node-role.kubernetes.io/control-plane: ""

elastic_agent_k8s_audit_tolerations:
  - key: node-role.kubernetes.io/control-plane
    operator: Exists
    effect: NoSchedule
```

### 設定例

#### `vars/all-config.yml`への設定例

`vars/all-config.yml`にはFleet Bootstrapと共有する設定を記述します。

```yaml
1: logging_backend_elastic_agent_k8s_audit_monitoring_enabled: true
2: logging_backend_elastic_agent_k8s_audit_monitoring_logs_enabled: true
3: logging_backend_elastic_agent_k8s_audit_monitoring_metrics_enabled: true
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `logging_backend_elastic_agent_k8s_audit_monitoring_enabled: true` | Kubernetes API監査ログ収集用Elastic Agent自身の監視を有効化します。 | Kubernetes API監査ログ収集用Elastic Agent自身の動作を確認するためです。運用要件に応じて, `true`, または, `false` に設定してください。|
| 2 | `logging_backend_elastic_agent_k8s_audit_monitoring_logs_enabled: true` | Kubernetes API監査ログ収集用Elastic Agent自身の監視ログを収集します。 | Kubernetes API監査ログ収集用Elastic Agent自身の動作を確認するためです。運用要件に応じて, `true`, または, `false` に設定してください。|
| 3 | `logging_backend_elastic_agent_k8s_audit_monitoring_metrics_enabled: true` | Kubernetes API監査ログ収集用Elastic Agent自身の監視メトリクスを収集します。 | Kubernetes API監査ログ収集用Elastic Agent自身の動作を確認するためです。運用要件に応じて, `true`, または, `false` に設定してください。|

#### Kubernetesコントロールプレーンノードの`host_vars`への設定例

コントロールプレーンノードの`host_vars`には導入有効化フラグを設定します。

```yaml
1: elastic_agent_k8s_audit_enabled: true
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `elastic_agent_k8s_audit_enabled: true` | Kubernetes API監査ログ収集用Elastic Agentの導入を有効化します。 | Kubernetes API監査ログ収集用Elastic Agentを使用して, JSON形式のログを解析し, KibanaのGUIからキーによる検索可能な形式で保存するために設定します。 本設定をしない場合, Kibana GUIのDiscoverからキーによる検索作業が複雑になります。 |

## テンプレートと生成ファイル

| テンプレート | 生成ファイル | 用途 |
| --- | --- | --- |
| `templates/values.yaml.j2` | `{{ k8s_kubeadm_config_store }}/elastic-agent-k8s-audit/values.yaml` | Audit用Elastic AgentのHelm valuesを生成します。 |

Fleet Bootstrap側では, `k8s_audit`構成種別用Package Policyに次の収集設定を作成します。

```yaml
audit-logs-filestream:
  enabled: true
  streams:
    kubernetes.audit_logs:
      enabled: true
      vars:
        paths:
          - /hostfs/var/log/kubernetes/audit/audit.log
```

同じPackage Policy内のkube-state-metrics, Kubernetes event, kubelet, kube-apiserver, kube-proxy, kube-scheduler, kube-controller-manager, container logs及び各クラウドAudit入力は無効化し, Kubernetes API監査ログだけを収集します。

## 検証ポイント

### 検証の前提条件

検証を始める前に, 次の条件が満たされていることを確認します。

- Kubernetes API監査機能が有効であり, 各対象コントロールプレーンノードで`/var/log/kubernetes/audit/audit.log`が生成されていること。
- `audit.log`がJSON Lines形式のKubernetes Audit Eventとして出力されていること。
- 対象ホストがKubernetesのコントロールプレーンノードの場合, `host_vars`で`elastic_agent_k8s_audit_enabled: true`を設定していること。
- 監査ログ収集対象外ホストでは`elastic_agent_k8s_audit_enabled`を`false`にするか未定義とすること。
- 対象ホストで`helm`及び`kubectl`コマンドを実行できること。
- Fleet Serverが起動済みであり, KubernetesクラスタからFleet Server接続先へ到達できること。
- Fleet Bootstrapが`k8s_audit`構成種別のElastic Agentポリシー, Kubernetes統合Package Policy及びEnrollment Tokenを作成済みであること。

### 検証環境の設定

本節では, 検証用の設定内容について説明します。

**検証用の vars/all-config.yml**:

`vars/all-config.yml`にはFleet Bootstrapと共有する設定を記述します。

```yaml
1: logging_backend_elastic_agent_k8s_audit_monitoring_enabled: true
2: logging_backend_elastic_agent_k8s_audit_monitoring_logs_enabled: true
3: logging_backend_elastic_agent_k8s_audit_monitoring_metrics_enabled: true
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `logging_backend_elastic_agent_k8s_audit_monitoring_enabled: true` | Kubernetes API監査ログ収集用Elastic Agent自身の監視を有効化します。 | Kubernetes API監査ログ収集用Elastic Agent自身の動作を確認するためです。運用要件に応じて, `true`, または, `false` に設定してください。|
| 2 | `logging_backend_elastic_agent_k8s_audit_monitoring_logs_enabled: true` | Kubernetes API監査ログ収集用Elastic Agent自身の監視ログを収集します。 | Kubernetes API監査ログ収集用Elastic Agent自身の動作を確認するためです。運用要件に応じて, `true`, または, `false` に設定してください。|
| 3 | `logging_backend_elastic_agent_k8s_audit_monitoring_metrics_enabled: true` | Kubernetes API監査ログ収集用Elastic Agent自身の監視メトリクスを収集します。 | Kubernetes API監査ログ収集用Elastic Agent自身の動作を確認するためです。運用要件に応じて, `true`, または, `false` に設定してください。|

**検証用の各コントロールプレーンノードのhost_var**:

コントロールプレーンノードの`host_vars`には導入有効化フラグを設定します。

```yaml
1: elastic_agent_k8s_audit_enabled: true
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `elastic_agent_k8s_audit_enabled: true` | Kubernetes API監査ログ収集用Elastic Agentの導入を有効化します。 | Kubernetes API監査ログ収集用Elastic Agentを使用して, JSON形式のログを解析し, KibanaのGUIからキーによる検索可能な形式で保存するために設定します。 本設定をしない場合, Kibana GUIのDiscoverからキーによる検索作業が複雑になります。 |

### 検証コマンドと期待結果

#### 1. Helm release状態

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
helm status elastic-agent-k8s-audit --namespace kube-system -o json | jq -r '.info.status'
```

**期待される出力**:
```plaintext
deployed
```

**実行結果の例**:
```bash
$ helm status elastic-agent-k8s-audit --namespace kube-system -o json | jq -r '.info.status'
deployed
```
**確認ポイント**:

- 上記コマンドの出力結果が`deployed`であること ( `helm status elastic-agent-k8s-audit`コマンドの出力結果として得られるJSON形式の出力中の`info.status`項目が`deployed`となっていること )。

#### 2. Audit用DaemonSetとPod状態

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
kubectl --namespace kube-system get daemonset \
  -l app.kubernetes.io/instance=elastic-agent-k8s-audit -o wide
kubectl --namespace kube-system get pods -o wide
```

**期待される出力**:

`kubectl --namespace kube-system get daemonset -l app.kubernetes.io/instance=elastic-agent-k8s-audit -o wide`コマンド:
```plaintext
NAME                                    DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR                                                   AGE    CONTAINERS   IMAGES                                                  SELECTOR
agent-pernode-elastic-agent-k8s-audit   1         1         1       1            1           kubernetes.io/os=linux,node-role.kubernetes.io/control-plane=   155m   agent        docker.elastic.co/elastic-agent/elastic-agent:8.19.19   name=agent-pernode-elastic-agent-k8s-audit
```

`kubectl --namespace kube-system get pods -o wide`コマンド:
```plaintext
NAME                                                       READY   STATUS    RESTARTS       AGE    IP                         NODE             NOMINATED NODE   READINESS GATES
...
agent-pernode-elastic-agent-k8s-audit-57jlb                1/1     Running   0              157m   fdb6:6e92:3cfb:200::11bd   k8sctrlplane01   <none>           <none>
...
```

**実行結果の例**:
```bash
$ kubectl --namespace kube-system get daemonset \
  -l app.kubernetes.io/instance=elastic-agent-k8s-audit -o wide
NAME                                    DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR                                                   AGE    CONTAINERS   IMAGES                                                  SELECTOR
agent-pernode-elastic-agent-k8s-audit   1         1         1       1            1           kubernetes.io/os=linux,node-role.kubernetes.io/control-plane=   155m   agent        docker.elastic.co/elastic-agent/elastic-agent:8.19.19   name=agent-pernode-elastic-agent-k8s-audit
$ kubectl --namespace kube-system get pods -o wide
NAME                                                       READY   STATUS    RESTARTS       AGE    IP                         NODE             NOMINATED NODE   READINESS GATES
agent-clusterwide-elastic-agent-k8s-b68f4bd55-zd9ch        1/1     Running   0              28h    fdb6:6e92:3cfb:204::7470   k8sworker0102    <none>           <none>
agent-pernode-elastic-agent-k8s-audit-57jlb                1/1     Running   0              157m   fdb6:6e92:3cfb:200::11bd   k8sctrlplane01   <none>           <none>
cilium-envoy-2l575                                         1/1     Running   7 (29h ago)    30h    fdad:ba50:248b:1::42       k8sworker0101    <none>           <none>
cilium-envoy-hvmh9                                         1/1     Running   1 (30h ago)    30h    fdad:ba50:248b:1::41       k8sctrlplane01   <none>           <none>
cilium-envoy-lpzhx                                         1/1     Running   7 (29h ago)    30h    fdad:ba50:248b:1::43       k8sworker0102    <none>           <none>
cilium-gl9sr                                               1/1     Running   6              30h    fdad:ba50:248b:1::43       k8sworker0102    <none>           <none>
cilium-m8frl                                               1/1     Running   0              30h    fdad:ba50:248b:1::41       k8sctrlplane01   <none>           <none>
cilium-operator-7f9b9c849d-97hqs                           1/1     Running   1 (29h ago)    29h    fdad:ba50:248b:1::42       k8sworker0101    <none>           <none>
cilium-operator-7f9b9c849d-tr5fb                           1/1     Running   1 (30h ago)    30h    fdad:ba50:248b:1::41       k8sctrlplane01   <none>           <none>
cilium-xw4rw                                               1/1     Running   6              30h    fdad:ba50:248b:1::42       k8sworker0101    <none>           <none>
clustermesh-apiserver-599f5dcb5f-xhrxp                     3/3     Running   0              29h    fdb6:6e92:3cfb:204::5e7a   k8sworker0102    <none>           <none>
coredns-7c65d6cfc9-68j6d                                   1/1     Running   0              30h    fdb6:6e92:3cfb:200::7a92   k8sctrlplane01   <none>           <none>
coredns-7c65d6cfc9-ljkx2                                   1/1     Running   0              30h    fdb6:6e92:3cfb:200::947a   k8sctrlplane01   <none>           <none>
etcd-k8sctrlplane01                                        1/1     Running   18 (30h ago)   30h    fdad:ba50:248b:1::41       k8sctrlplane01   <none>           <none>
hubble-relay-6f576c4487-wdgwl                              1/1     Running   0              29h    fdb6:6e92:3cfb:204::26d3   k8sworker0102    <none>           <none>
hubble-ui-6b65d5f8f5-gdjg5                                 2/2     Running   0              29h    fdb6:6e92:3cfb:203::2459   k8sworker0101    <none>           <none>
kube-apiserver-k8sctrlplane01                              1/1     Running   2 (30h ago)    30h    fdad:ba50:248b:1::41       k8sctrlplane01   <none>           <none>
kube-controller-manager-k8sctrlplane01                     1/1     Running   18 (30h ago)   30h    fdad:ba50:248b:1::41       k8sctrlplane01   <none>           <none>
kube-multus-ds-5p5h7                                       1/1     Running   10 (29h ago)   30h    fdad:ba50:248b:1::43       k8sworker0102    <none>           <none>
kube-multus-ds-m6xl8                                       1/1     Running   11 (29h ago)   30h    fdad:ba50:248b:1::42       k8sworker0101    <none>           <none>
kube-multus-ds-vcdkm                                       1/1     Running   0              30h    fdad:ba50:248b:1::41       k8sctrlplane01   <none>           <none>
kube-scheduler-k8sctrlplane01                              1/1     Running   18 (30h ago)   30h    fdad:ba50:248b:1::41       k8sctrlplane01   <none>           <none>
kube-state-metrics-8556695f7c-24pkz                        1/1     Running   0              28h    fdb6:6e92:3cfb:203::c22b   k8sworker0101    <none>           <none>
whereabouts-whereabouts-chart-49dvm                        1/1     Running   24 (29h ago)   30h    fdad:ba50:248b:1::42       k8sworker0101    <none>           <none>
whereabouts-whereabouts-chart-controller-bd8d4fd75-8tnlq   1/1     Running   0              29h    fdb6:6e92:3cfb:204::9964   k8sworker0102    <none>           <none>
whereabouts-whereabouts-chart-g8rc2                        1/1     Running   23 (29h ago)   30h    fdad:ba50:248b:1::43       k8sworker0102    <none>           <none>
whereabouts-whereabouts-chart-pch2w                        1/1     Running   0              30h    fdad:ba50:248b:1::41       k8sctrlplane01   <none>           <none>
```

**確認ポイント**:

- Audit用DaemonSet(`agent-pernode-elastic-agent-k8s-audit`)の`DESIRED`が1以上で, `READY`と一致していること。
- 対応Pod(`agent-pernode-elastic-agent-k8s-audit`)が対象コントロールプレーンノードで`Running`になっていること。

### 3. Pod内からの監査ログ読み取り

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

1. 対象Pod名を以下のコマンドを実行して確認します:
```bash
kubectl --namespace kube-system get pods|grep 'agent-pernode-elastic-agent-k8s-audit'|awk -F' ' '{print $1;}'
```

2. 上記コマンドで得られた出力を以下の`<audit-agent-pod>`に指定して, 以下のコマンドを実行します:
```bash
kubectl --namespace kube-system exec <audit-agent-pod> -- \
  test -r /hostfs/var/log/kubernetes/audit/audit.log
```

3. 終了状態が0であることを`echo $?`コマンドを実行して確認します。

**期待される出力**:

上記手順3.の結果が`0`になること。

**実行結果の例**:
```bash
$ kubectl --namespace kube-system get pods|grep 'agent-pernode-elastic-agent-k8s-audit'|awk -F' ' '{print $1;}'
agent-pernode-elastic-agent-k8s-audit-57jlb
$ kubectl --namespace kube-system exec agent-pernode-elastic-agent-k8s-audit-57jlb -- test -r /hostfs/var/log/kubernetes/audit/audit.log
$ echo $?
0
```

**確認ポイント**:

- 対象Pod内に`/hostfs/var/log/kubernetes/audit/audit.log`ファイルが存在し, コンテナ内から読み取り可能であること。

### 4. Fleet Agent状態

Kibana GUIの`Management`内の`Fleet`画面で`Agents`タブを確認し,
  Agent PolicyがAudit用Agent Policy(`linux-host-policy-k8s-audit`)となっているAgentの状態(`Status`)が正常(`Healthy`)であることを確認します。

### 5. Data Streamと監査イベント

1. Kibana GUIの`Management`内の`Stack Management`画面で, `Data`内の`Index Management`項目を開き, `Data Streams`タブ内に`logs-kubernetes.audit_logs-k8s_system`が存在することを確認します。
2. Kibana GUIの`Discover`又はKibana GUIの`Management`内の`Dev Tools`で以下のコマンドを実行し, 最新イベントを確認します。

```json
GET logs-kubernetes.audit_logs-k8s_system/_search
{
  "size": 1,
  "sort": [
    {
      "@timestamp": {
        "order": "desc"
      }
    }
  ]
}
```

上記`Dev Tools`コマンドの実行結果の例は以下の通りです:

- `kubernetes.audit.responseStatus.code`がない場合の例:
    ```json
    {
      "took": 39,
      "timed_out": false,
      "_shards": {
        "total": 1,
        "successful": 1,
        "skipped": 0,
        "failed": 0
      },
      "hits": {
        "total": {
          "value": 10000,
          "relation": "gte"
        },
        "max_score": null,
        "hits": [
          {
            "_index": ".ds-logs-kubernetes.audit_logs-k8s_system-2026.08.15-000001",
            "_id": "tHG3BqABnXI6LQuok7OS",
            "_score": null,
            "_source": {
              "kubernetes": {
                "audit": {
                  "auditID": "e83cb841-b30e-460b-9afd-2a1998cc9f02",
                  "requestReceivedTimestamp": "2026-08-15T18:38:06.505176Z",
                  "objectRef": {
                    "apiGroup": "coordination.k8s.io",
                    "apiVersion": "v1",
                    "resource": "leases",
                    "namespace": "vc-manager",
                    "name": "vc-manager-leaderelection-lock"
                  },
                  "level": "RequestResponse",
                  "kind": "Event",
                  "verb": "update",
                  "userAgent": "app/v0.0.0 (linux/amd64) kubernetes/$Format/leader-election",
                  "requestURI": "/apis/coordination.k8s.io/v1/namespaces/vc-manager/leases/vc-manager-leaderelection-lock",
                  "stageTimestamp": "2026-08-15T18:38:06.505176Z",
                  "sourceIPs": [
                    "fdb6:6e92:3cfb:203::4558"
                  ],
                  "apiVersion": "audit.k8s.io/v1",
                  "stage": "RequestReceived",
                  "user": {
                    "uid": "5d1d0944-6488-4227-8156-71c3c8fe49d1",
                    "extra": {
                      "authentication.kubernetes.io/credential-id": [
                        "JTI=14e0c8c8-811e-4cf2-8351-c78e5f7b9f03"
                      ],
                      "authentication.kubernetes.io/node-name": [
                        "k8sworker0101"
                      ],
                      "authentication.kubernetes.io/pod-name": [
                        "vc-manager-5b5db8d89c-xbzbv"
                      ],
                      "authentication.kubernetes.io/node-uid": [
                        "60d2384b-16eb-436b-b172-aa3534195a1e"
                      ],
                      "authentication.kubernetes.io/pod-uid": [
                        "a799017e-b7ac-43c3-94da-38b1b611746d"
                      ]
                    },
                    "groups": [
                      "system:serviceaccounts",
                      "system:serviceaccounts:vc-manager",
                      "system:authenticated"
                    ],
                    "username": "system:serviceaccount:vc-manager:vc-manager"
                  }
                }
              },
              "agent": {
                "name": "agent-pernode-elastic-agent-k8s-audit-57jlb",
                "id": "37ec2337-34c1-4de6-86aa-bd659e7bec47",
                "ephemeral_id": "a13960ba-2189-473b-88ae-119e498ca5e5",
                "type": "filebeat",
                "version": "8.19.19"
              },
              "log": {
                "file": {
                  "inode": "1178339",
                  "path": "/hostfs/var/log/kubernetes/audit/audit.log",
                  "device_id": "51714"
                },
                "offset": 107279662
              },
              "elastic_agent": {
                "id": "37ec2337-34c1-4de6-86aa-bd659e7bec47",
                "version": "8.19.19",
                "snapshot": false
              },
              "source": {
                "ip": [
                  "fdb6:6e92:3cfb:203::4558"
                ]
              },
              "tags": [
                "forwarded",
                "kubernetes-audit_logs",
                "beats_input_raw_event"
              ],
              "input": {
                "type": "filestream"
              },
              "orchestrator": {
                "resource": {
                  "name": "vc-manager-leaderelection-lock",
                  "type": "leases"
                },
                "namespace": "vc-manager",
                "type": "kubernetes",
                "api_version": "audit.k8s.io/v1"
              },
              "@timestamp": "2026-08-15T18:38:07.171Z",
              "ecs": {
                "version": "8.0.0"
              },
              "related": {
                "ip": [
                  "fdb6:6e92:3cfb:203::4558"
                ],
                "user": [
                  "5d1d0944-6488-4227-8156-71c3c8fe49d1",
                  "system:serviceaccount:vc-manager:vc-manager"
                ]
              },
              "data_stream": {
                "namespace": "k8s_system",
                "type": "logs",
                "dataset": "kubernetes.audit_logs"
              },
              "@version": "1",
              "host": {
                "name": "agent-pernode-elastic-agent-k8s-audit-57jlb"
              },
              "client": {
                "ip": [
                  "fdb6:6e92:3cfb:203::4558"
                ]
              },
              "event": {
                "agent_id_status": "auth_metadata_missing",
                "ingested": "2026-08-15T18:38:09Z",
                "kind": "event",
                "action": "update",
                "dataset": "kubernetes.audit_logs"
              },
              "user": {
                "name": "system:serviceaccount:vc-manager:vc-manager",
                "id": "5d1d0944-6488-4227-8156-71c3c8fe49d1"
              },
              "user_agent": {
                "original": "app/v0.0.0 (linux/amd64) kubernetes/$Format/leader-election"
              }
            },
            "sort": [
              1786819087171
            ]
          }
        ]
      }
    }
    ```

- `kubernetes.audit.responseStatus.code`がある場合の例:
    ```json
    {
      "took": 2,
      "timed_out": false,
      "_shards": {
        "total": 1,
        "successful": 1,
        "skipped": 0,
        "failed": 0
      },
      "hits": {
        "total": {
          "value": 10000,
          "relation": "gte"
        },
        "max_score": null,
        "hits": [
          {
            "_index": ".ds-logs-kubernetes.audit_logs-k8s_system-2026.08.15-000001",
            "_id": "wnK_BqABnXI6LQuoTgqd",
            "_score": null,
            "_source": {
              "kubernetes": {
                "audit": {
                  "auditID": "64205e6b-3186-4202-8046-2262dfbf6d9c",
                  "requestReceivedTimestamp": "2026-08-15T18:46:33.342806Z",
                  "level": "RequestResponse",
                  "kind": "Event",
                  "verb": "get",
                  "annotations": {
                    "authorization_k8s_io/decision": "allow",
                    "authorization_k8s_io/reason": "RBAC: allowed by ClusterRoleBinding \"system:public-info-viewer\" of ClusterRole \"system:public-info-viewer\" to Group \"system:authenticated\""
                  },
                  "userAgent": "cilium-operator-generic/1.18.9 c4898256 2026-04-14T12:55:39+00:00 go version go1.25.9 linux/amd64 cilium-operator",
                  "requestURI": "/version",
                  "responseStatus": {
                    "code": 200
                  },
                  "stageTimestamp": "2026-08-15T18:46:33.343106Z",
                  "sourceIPs": [
                    "fdad:ba50:248b:1::51"
                  ],
                  "apiVersion": "audit.k8s.io/v1",
                  "stage": "ResponseComplete",
                  "user": {
                    "uid": "310793f4-00b5-4248-a40c-53053584a87e",
                    "extra": {
                      "authentication.kubernetes.io/credential-id": [
                        "JTI=da9c34b8-2c98-46b2-a362-c1f56e3c687a"
                      ],
                      "authentication.kubernetes.io/node-name": [
                        "k8sctrlplane02"
                      ],
                      "authentication.kubernetes.io/pod-name": [
                        "cilium-operator-7d87454f7f-sbk79"
                      ],
                      "authentication.kubernetes.io/node-uid": [
                        "b4df5acc-00db-4945-b306-f29e8f9e22d9"
                      ],
                      "authentication.kubernetes.io/pod-uid": [
                        "8815c84b-4c7a-4ef3-a577-0d1300f17ec7"
                      ]
                    },
                    "groups": [
                      "system:serviceaccounts",
                      "system:serviceaccounts:kube-system",
                      "system:authenticated"
                    ],
                    "username": "system:serviceaccount:kube-system:cilium-operator"
                  }
                }
              },
              "agent": {
                "name": "agent-pernode-elastic-agent-k8s-audit-2jv8h",
                "id": "36a2156b-6e48-424f-a195-77f665fe65e7",
                "ephemeral_id": "142a6beb-4f07-4610-89eb-92b8d26fe75b",
                "type": "filebeat",
                "version": "8.19.19"
              },
              "log": {
                "file": {
                  "inode": "83978328",
                  "path": "/hostfs/var/log/kubernetes/audit/audit.log",
                  "device_id": "51715"
                },
                "offset": 114418851
              },
              "elastic_agent": {
                "id": "36a2156b-6e48-424f-a195-77f665fe65e7",
                "version": "8.19.19",
                "snapshot": false
              },
              "source": {
                "ip": [
                  "fdad:ba50:248b:1::51"
                ]
              },
              "tags": [
                "forwarded",
                "kubernetes-audit_logs",
                "beats_input_raw_event"
              ],
              "input": {
                "type": "filestream"
              },
              "orchestrator": {
                "type": "kubernetes",
                "api_version": "audit.k8s.io/v1"
              },
              "@timestamp": "2026-08-15T18:46:33.818Z",
              "ecs": {
                "version": "8.0.0"
              },
              "related": {
                "ip": [
                  "fdad:ba50:248b:1::51"
                ],
                "user": [
                  "310793f4-00b5-4248-a40c-53053584a87e",
                  "system:serviceaccount:kube-system:cilium-operator"
                ]
              },
              "data_stream": {
                "namespace": "k8s_system",
                "type": "logs",
                "dataset": "kubernetes.audit_logs"
              },
              "@version": "1",
              "host": {
                "name": "agent-pernode-elastic-agent-k8s-audit-2jv8h"
              },
              "client": {
                "ip": [
                  "fdad:ba50:248b:1::51"
                ]
              },
              "event": {
                "agent_id_status": "auth_metadata_missing",
                "ingested": "2026-08-15T18:46:35Z",
                "kind": "event",
                "action": "get",
                "dataset": "kubernetes.audit_logs",
                "outcome": "success"
              },
              "user": {
                "name": "system:serviceaccount:kube-system:cilium-operator",
                "id": "310793f4-00b5-4248-a40c-53053584a87e"
              },
              "user_agent": {
                "original": "cilium-operator-generic/1.18.9 c4898256 2026-04-14T12:55:39+00:00 go version go1.25.9 linux/amd64 cilium-operator"
              }
            },
            "sort": [
              1786819593818
            ]
          }
        ]
      }
    }
    ```

**確認ポイント**:

取得されたイベントで,イベント内容およびAudit stageに応じて少なくとも次のフィールドを確認します。

- `data_stream.dataset = kubernetes.audit_logs`
- `data_stream.namespace = k8s_system`
- `kubernetes.audit.verb`
- `kubernetes.audit.user.username`
- `kubernetes.audit.objectRef`
- `kubernetes.audit.stage`
- `kubernetes.audit.responseStatus.code`（`ResponseComplete`などレスポンス情報を持つイベントの場合）

## トラブルシューティング

### 1. Enrollment Tokenを取得できない場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:
制御ホスト上の本playbookのトップディレクトリで, 以下のコマンドを実行し, `fleet_bootstrap_enrollment_token_file`が存在し, 通常ファイルかつ権限`0600`であることを確認します。以下の`<fleet_bootstrap_enrollment_token_file>`には, `fleet_bootstrap_enrollment_token_file`変数で指定したパスを指定します。規定値は, `group_vars/logging_collector/enroll
ment-token.yml`です:

```bash
LANG=C stat -c '%a %F' "<fleet_bootstrap_enrollment_token_file>"
```

**期待される出力**:
```plaintext
600 regular file
```

**実行結果の例**:
```bash
$ LANG=C stat -c '%a %F' group_vars/logging_collector/enroll
ment-token.yml
600 regular file
```

**対処**:

- ファイルのアクセス権が不正な場合や共有ファイル内に`k8s_audit`キーが存在しない場合は, 当該ファイルのアクセス権を適切に設定, または, 削除して, Fleet Bootstrapロールを再実行します。

### 2. DaemonSetが配置されない場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:
```bash
kubectl --namespace kube-system get daemonset \
  -l app.kubernetes.io/instance=elastic-agent-k8s-audit \
  -o json |
jq '.items[] | {
  name: .metadata.name,
  nodeSelector: .spec.template.spec.nodeSelector,
  tolerations: .spec.template.spec.tolerations
}'
kubectl get nodes -o json |
jq '.items[] | {
  name: .metadata.name,
  labels: .metadata.labels,
  taints: (.spec.taints // [])
}'
```

***実行結果の例**:
```bash
$ kubectl --namespace kube-system get daemonset \
  -l app.kubernetes.io/instance=elastic-agent-k8s-audit \
  -o json |
jq '.items[] | {
  name: .metadata.name,
  nodeSelector: .spec.template.spec.nodeSelector,
  tolerations: .spec.template.spec.tolerations
}'
{
  "name": "agent-pernode-elastic-agent-k8s-audit",
  "nodeSelector": {
    "kubernetes.io/os": "linux",
    "node-role.kubernetes.io/control-plane": ""
  },
  "tolerations": [
    {
      "effect": "NoSchedule",
      "key": "node-role.kubernetes.io/control-plane",
      "operator": "Exists"
    }
  ]
}
```

および,

```bash
$ kubectl get nodes -o json |
jq '.items[] | {
  name: .metadata.name,
  labels: .metadata.labels,
  taints: (.spec.taints // [])
}'
{
  "name": "k8sctrlplane01",
  "labels": {
    "beta.kubernetes.io/arch": "amd64",
    "beta.kubernetes.io/os": "linux",
    "kubernetes.io/arch": "amd64",
    "kubernetes.io/hostname": "k8sctrlplane01",
    "kubernetes.io/os": "linux",
    "node-role.kubernetes.io/control-plane": "",
    "node.kubernetes.io/exclude-from-external-load-balancers": ""
  },
  "taints": [
    {
      "effect": "NoSchedule",
      "key": "node-role.kubernetes.io/control-plane"
    }
  ]
}
```

**対処**:

以下を確認の上, 誤った値を変数に設定していないことを確認してください。

- `elastic_agent_k8s_audit_node_selector`変数の設定値が対象のコントロールプレインノードのノードラベルに含まれること
  - `elastic_agent_k8s_audit_node_selector`に`"node-role.kubernetes.io/control-plane"`が含まれること, かつ,
  - 対象のコントロールプレインノードのラベルに`"node-role.kubernetes.io/control-plane"`が含まれること
- コントロールプレーンノードの`tolerations`に`"effect": "NoSchedule"`が設定されていること(スケジューラからPod展開対象外ノードと指示されている場合でも, 本Podは展開する旨の指示)


### 3. `audit.log`をPodから読めない場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:
対象コントロールプレーンノードで以下のコマンドを実行します:
```bash
LANG=C sudo stat /var/log/kubernetes/audit/audit.log
sudo tail -n 1 /var/log/kubernetes/audit/audit.log
```
***実行結果の例**:
```bash
$ LANG=C sudo stat /var/log/kubernetes/audit/audit.log
  File: /var/log/kubernetes/audit/audit.log
  Size: 204168398       Blocks: 398776     IO Block: 4096   regular file
Device: 202,2   Inode: 1178339     Links: 1
Access: (0600/-rw-------)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-08-16 02:47:09.231849502 +0900
Modify: 2026-08-16 04:24:36.697525839 +0900
Change: 2026-08-16 04:24:36.697525839 +0900
 Birth: 2026-08-16 02:47:09.231849502 +0900
$ sudo tail -n 1 /var/log/kubernetes/audit/audit.log
{"kind":"Event","apiVersion":"audit.k8s.io/v1","level":"RequestResponse","auditID":"b76e7922-719c-45de-a6c9-15c0a76f2f13","stage":"ResponseComplete","requestURI":"/apis/coordination.k8s.io/v1/namespaces/vc-manager/leases/vc-manager-leaderelection-lock","verb":"update","user":{"username":"system:serviceaccount:vc-manager:vc-manager","uid":"5d1d0944-6488-4227-8156-71c3c8fe49d1","groups":["system:serviceaccounts","system:serviceaccounts:vc-manager","system:authenticated"],"extra":{"authentication.kubernetes.io/credential-id":["JTI=2fd84cfe-157f-4a61-85df-cc17dfc4d61f"],"authentication.kubernetes.io/node-name":["k8sworker0101"],"authentication.kubernetes.io/node-uid":["60d2384b-16eb-436b-b172-aa3534195a1e"],"authentication.kubernetes.io/pod-name":["vc-manager-5b5db8d89c-xbzbv"],"authentication.kubernetes.io/pod-uid":["a799017e-b7ac-43c3-94da-38b1b611746d"]}},"sourceIPs":["fdb6:6e92:3cfb:203::4558"],"userAgent":"app/v0.0.0 (linux/amd64) kubernetes/$Format/leader-election","objectRef":{"resource":"leases","namespace":"vc-manager","name":"vc-manager-leaderelection-lock","uid":"36ed60fe-4784-4ba0-b267-ec681a1878fd","apiGroup":"coordination.k8s.io","apiVersion":"v1","resourceVersion":"457081"},"responseStatus":{"metadata":{},"code":200},"requestObject":{"kind":"Lease","apiVersion":"coordination.k8s.io/v1","metadata":{"name":"vc-manager-leaderelection-lock","namespace":"vc-manager","uid":"36ed60fe-4784-4ba0-b267-ec681a1878fd","resourceVersion":"457081","creationTimestamp":"2026-08-14T13:02:33Z","managedFields":[{"manager":"app","operation":"Update","apiVersion":"coordination.k8s.io/v1","time":"2026-08-15T19:25:10Z","fieldsType":"FieldsV1","fieldsV1":{"f:spec":{"f:acquireTime":{},"f:holderIdentity":{},"f:leaseDurationSeconds":{},"f:leaseTransitions":{},"f:renewTime":{}}}}]},"spec":{"holderIdentity":"vc-manager-5b5db8d89c-xbzbv_772334f7-62fb-41e6-88a4-75ace8bb3e46","leaseDurationSeconds":15,"acquireTime":"2026-08-14T13:02:33.000000Z","renewTime":"2026-08-15T19:25:12.872883Z","leaseTransitions":0}},"responseObject":{"kind":"Lease","apiVersion":"coordination.k8s.io/v1","metadata":{"name":"vc-manager-leaderelection-lock","namespace":"vc-manager","uid":"36ed60fe-4784-4ba0-b267-ec681a1878fd","resourceVersion":"457090","creationTimestamp":"2026-08-14T13:02:33Z","managedFields":[{"manager":"app","operation":"Update","apiVersion":"coordination.k8s.io/v1","time":"2026-08-15T19:25:12Z","fieldsType":"FieldsV1","fieldsV1":{"f:spec":{"f:acquireTime":{},"f:holderIdentity":{},"f:leaseDurationSeconds":{},"f:leaseTransitions":{},"f:renewTime":{}}}}]},"spec":{"holderIdentity":"vc-manager-5b5db8d89c-xbzbv_772334f7-62fb-41e6-88a4-75ace8bb3e46","leaseDurationSeconds":15,"acquireTime":"2026-08-14T13:02:33.000000Z","renewTime":"2026-08-15T19:25:12.872883Z","leaseTransitions":0}},"requestReceivedTimestamp":"2026-08-15T19:25:12.922988Z","stageTimestamp":"2026-08-15T19:25:12.945442Z","annotations":{"authorization.k8s.io/decision":"allow","authorization.k8s.io/reason":"RBAC: allowed by ClusterRoleBinding \"vc-manager\" of ClusterRole \"vc-manager\" to ServiceAccount \"vc-manager/vc-manager\""}}
```

***対処**:

以下を確認し, `k8s-ctrlplane`ロールの設定値と本ロールの設定値が一致するように設定を見直してください:

- kube-apiserverの監査ログ出力設定通りに監査ログファイル(`audit.log`)が配置されていること
- 監査ログファイル(`audit.log`)のホスト側のファイルパスとHelm valuesファイル中のhostPath設定が一致していること
- 監査ログファイル(`audit.log`)にログが書き込まれていること

### 4. Data Streamが作成されない又は更新されない場合

**実施対象ホスト**:

Kibana Web UIへアクセス可能な管理端末

**実行するコマンド**:

Kibana GUIの`Dev Tools` -> `Console`を開き,以下を実行し, Fleet Agent一覧を取得します:
```plaintext
GET kbn:/api/fleet/agents?perPage=10000
```

**期待される出力**:
Fleet Agent一覧に,名前が以下の形式のAgentがコントロールプレーンノード数分存在することを確認します:

```text
agent-pernode-elastic-agent-k8s-audit-<suffix>
```

調査対象Fleet Agent名の例:
```text
agent-pernode-elastic-agent-k8s-audit-57jlb
```

**対処**:

各Agentについて,以下を確認し, 以下の条件に一致しなかった場合は, Elastic Stack関連コンポーネントのログ等を調査して原因を切り分け対処してください:

- policy_idがlinux-host-policy-k8s-auditのAgent Policy IDと一致すること。
- API上の`status`が異常状態(`offline`,`error`等)でないこと。
- Kibana GUIの`Management`内の`Fleet`画面で`Agents`タブを確認し,
  Agent PolicyがAudit用Agent Policy(`linux-host-policy-k8s-audit`)となっているAgentの状態(`Status`)が正常(`Healthy`)であること。

## 注意事項

- 本ロールはKubernetes API監査機能自体を有効化しません。kube-apiserver側のAudit Policy及び監査ログ出力設定はKubernetes構築ロール側で管理します。
- Audit Policyの内容は本ロールの管理対象外です。
- 本ロールは通常の`elastic-agent-k8s`とは別Helm releaseとして導入します。
- 監査ログ収集用Podは既定ではcontrol-planeノードだけへ配置します。
- `audit.log`の内容をAnsibleの検証出力へ表示せず, 読み取り可否だけを確認します。
- Fleet Bootstrapが設定する監査ログの収集パスと, 本ロールがマウントするコンテナ側パスを一致させてください。
- `logging_backend_elastic_agent_k8s_audit_monitoring_*`はAuditログそのものの収集可否ではなく, Audit用Elastic Agent自身の監視ログ及び監視メトリクスの収集可否を制御します。
- Chart版数変更時は, DaemonSet構造, volumeMount, Pod構成及びFleet入力定義の差分を再確認してください。

## 参考資料

### 公式ドキュメント

- [Kubernetes Auditing](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)
- [Kubernetes Audit Policy](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/#audit-policy)
- [Kubernetes DaemonSet](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)
- [Kubernetes volumes hostPath](https://kubernetes.io/docs/concepts/storage/volumes/#hostpath)
- [kubectlコマンド](https://kubernetes.io/docs/reference/kubectl/)
- [Helm](https://helm.sh/docs/)
- [Elastic Agent for Kubernetes](https://www.elastic.co/guide/en/fleet/current/running-on-kubernetes-managed-by-fleet.html)
- [Kubernetes integration](https://www.elastic.co/docs/reference/integrations/kubernetes/)
- [Kubernetes Audit Logs integration](https://www.elastic.co/docs/reference/integrations/kubernetes/audit-logs)
- [Fleet Server](https://www.elastic.co/docs/reference/fleet/fleet-server)
- [Fleet Agent policies](https://www.elastic.co/docs/reference/fleet/agent-policy)
- [Fleet enrollment tokens](https://www.elastic.co/docs/reference/fleet/fleet-enrollment-tokens)
- [Elasticsearch data streams](https://www.elastic.co/docs/manage-data/data-store/data-streams)
- [Kibana Discover](https://www.elastic.co/docs/explore-analyze/discover)

### 関連ロール

- [roles/k8s-ctrlplane/Readme.md](../k8s-ctrlplane/Readme.md)
- [roles/elasticsearch/Readme.md](../elasticsearch/Readme.md)
- [roles/logstash/Readme.md](../logstash/Readme.md)
- [roles/kibana/Readme.md](../kibana/Readme.md)
- [roles/fleet-server/Readme.md](../fleet-server/Readme.md)
- [roles/fleet-bootstrap/Readme.md](../fleet-bootstrap/Readme.md)
- [roles/elastic-agent/Readme.md](../elastic-agent/Readme.md)
- [roles/elastic-agent-k8s/Readme.md](../elastic-agent-k8s/Readme.md)
