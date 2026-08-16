# docker-network-elastic-stack ロール

本ロールは, Elastic Stack関連コンテナが共有するDockerブリッジネットワークを明示したIPv4 CIDRとIPv6 CIDRで作成します。また, 当該CIDRから外部ネットワークへのIPv4通信とIPv6通信に必要な転送規則とNAT規則を設定します。

## 目次

- [docker-network-elastic-stack ロール](#docker-network-elastic-stack-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
    - [Elastic Stack間共有設定値](#elastic-stack間共有設定値)
    - [各ロール固有の利用者入力値](#各ロール固有の利用者入力値)
      - [必須入力値](#必須入力値)
      - [任意入力値](#任意入力値)
    - [設定例](#設定例)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [検証の前提条件](#検証の前提条件)
    - [検証環境の設定](#検証環境の設定)
    - [検証コマンドと期待結果](#検証コマンドと期待結果)
      - [1. DockerブリッジネットワークCIDR確認](#1-dockerブリッジネットワークcidr確認)
      - [2. iptables規則確認](#2-iptables規則確認)
      - [3. systemdサービス状態確認](#3-systemdサービス状態確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. DockerネットワークCIDR不一致で停止する場合](#1-dockerネットワークcidr不一致で停止する場合)
    - [2. systemdサービスが起動しない場合](#2-systemdサービスが起動しない場合)
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
| Enrollment Token共有ファイル | - | Fleet BootstrapがEnrollment Tokenを制御ホスト上へ保存し, Elastic Agent本体ロールがFleet Serverへの登録時に読み込む権限`0600`のYAMLファイル。 |
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

本ロールは`elastic-backend`ネットワークの作成を所有します。Elasticsearch, Logstash, Kibana及びFleet Serverの各ロールは, 本ロールが作成したネットワークの存在だけを確認します。

既存の同名ネットワークが指定したIPv4 CIDR及びIPv6 CIDRと一致しない場合, 又は別のDockerブリッジネットワークが同じアドレス種別の指定CIDRと重複する場合, 本ロールは既存コンテナの通信を破壊しないため処理を停止します。既存ネットワークの削除及び再作成は実行しません。

## 前提条件

- 対象ホストでDockerが起動済みであること。
- 対象ホストでiptables, ip6tables, Python及びsystemdが利用できること。
- 制御ホストから対象ホストへ管理者権限で設定を適用できること。
- 指定したIPv4 CIDR及びIPv6 CIDRが対象ホスト上の他のDockerブリッジネットワークと重複しないこと。

## 実行方法

Elastic Stack関連ロールとともに実行する場合は, 制御ホストで次のコマンドを実行します。

```bash
make run_logging_backend
```

本ロールだけを実行する場合は, 制御ホストで次のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts logging-backend.yml --tags docker-network-elastic-stack
```

`logging-backend.yml`は本ロールをElasticsearchより前に実行します。

## 主要変数

### Elastic Stack間共有設定値

共有設定値の意味, 設定要否, 既定値及び設定例は, [Elasticsearchロールの共有設定値](../elasticsearch/Readme.md#varsall-configymlに設定するelastic-stack間共有設定値)を参照します。本ロールでは, 共有するDockerブリッジネットワーク名, IPv4 CIDR及びIPv6 CIDRが影響します。

### 各ロール固有の利用者入力値

#### 必須入力値

本ロール固有の必須入力値はありません。共有ネットワークの3値は, 前節の正本に従って設定します。

#### 任意入力値

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `docker_network_elastic_stack_command_timeout_seconds` | Docker, iptables及びip6tablesの各コマンド完了を待つ最大秒数。 | `30` | `30` |
| `docker_network_elastic_stack_retries` | Dockerネットワーク検証の最大実行回数。 | `3` | `3` |
| `docker_network_elastic_stack_retry_interval_seconds` | Dockerネットワーク検証を再実行するまでの待機秒数。 | `2` | `2` |
| `docker_network_elastic_stack_validate_script` | CIDR検証プログラムの配置先。 | `/usr/local/libexec/docker-network-elastic-stack-validate.py` | `/usr/local/libexec/docker-network-elastic-stack-validate.py` |
| `docker_network_elastic_stack_apply_script` | iptables規則適用プログラムの配置先。 | `/usr/local/libexec/docker-network-elastic-stack-apply` | `/usr/local/libexec/docker-network-elastic-stack-apply` |
| `docker_network_elastic_stack_service_name` | 規則を再適用するsystemdサービス名。 | `docker-network-elastic-stack.service` | `docker-network-elastic-stack.service` |
| `docker_network_elastic_stack_filter_chain` | 転送規則を格納する専用iptablesチェーン名。 | `ELASTIC-STACK-FWD` | `ELASTIC-STACK-FWD` |
| `docker_network_elastic_stack_nat_chain` | NAT規則を格納する専用iptablesチェーン名。 | `ELASTIC-STACK-NAT` | `ELASTIC-STACK-NAT` |

### 設定例

共有ネットワーク設定は`vars/all-config.yml`へ記載します。設定例は[Elasticsearchロールの共有設定値](../elasticsearch/Readme.md#varsall-configymlに設定するelastic-stack間共有設定値)を参照します。本ロール固有の待機時間と再試行条件を変更する例を次に示します。

```yaml
1: docker_network_elastic_stack_command_timeout_seconds: 60
2: docker_network_elastic_stack_retries: 5
3: docker_network_elastic_stack_retry_interval_seconds: 3
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `docker_network_elastic_stack_command_timeout_seconds: 60` | Docker, iptables及びip6tablesの各コマンドを最大60秒待ちます。 | 実行環境の応答時間より短い値では正常な処理を異常終了と判定するため, 実行環境に合う値を指定します。 |
| 2-3 | `docker_network_elastic_stack_retries: 5`, `docker_network_elastic_stack_retry_interval_seconds: 3` | Dockerネットワーク検証を3秒間隔で最大5回実行します。 | 一時的なDocker応答失敗を直ちに恒久障害と判定しないため, 再試行条件を指定します。 |

設定例の適用結果は, 「検証コマンドと期待結果」のDockerブリッジネットワークCIDR確認とiptables規則確認で検証します。

## テンプレートと生成ファイル

| テンプレート | 生成ファイル | 用途 |
| --- | --- | --- |
| `templates/validate-network.py.j2` | `/usr/local/libexec/docker-network-elastic-stack-validate.py` | 同名ネットワークのIPv4 CIDR及びIPv6 CIDRの一致と他ネットワークとの非重複を検証します。 |
| `templates/apply-rules.sh.j2` | `/usr/local/libexec/docker-network-elastic-stack-apply` | 専用iptablesチェーン及びip6tablesチェーンへ転送規則とNAT規則を冪等に設定します。 |
| `templates/docker-network-elastic-stack.service.j2` | `/etc/systemd/system/docker-network-elastic-stack.service` | Docker起動後にiptables規則及びip6tables規則を再適用します。 |

## 実行フロー

1. Docker, iptables, ip6tables及びPythonの各コマンドが利用できることを確認します。
2. ネットワーク名, IPv4 CIDR, IPv6 CIDR, 最大待機秒数及び再実行値を検証します。
3. Dockerネットワーク一覧を取得し, 同名ネットワークのIPv4 CIDR及びIPv6 CIDRと他ネットワークの同じアドレス種別のCIDRを検証します。
4. 同名ネットワークが存在しない場合だけ, 指定したIPv4 CIDR及びIPv6 CIDRでDockerブリッジネットワークを作成します。
5. 専用iptablesチェーン及びip6tablesチェーンへ指定CIDRだけを対象とする転送規則とNAT規則を設定します。
6. systemdサービスを有効化し, 対象ホスト又はDockerの再起動後に規則を再適用します。
7. 専用iptablesチェーン及びip6tablesチェーンが存在することを確認します。

本ロールはiptables及びip6tablesの`FORWARD`チェーンと`POSTROUTING`チェーン全体を消去しません。`ELASTIC-STACK-FWD`及び`ELASTIC-STACK-NAT`だけを再生成するため, 他のDockerブリッジネットワーク向け規則を変更しません。

## 検証ポイント

### 検証の前提条件

検証を始める前に, 次の条件が満たされていることを確認します。

- 対象ホストで本ロールの実行が正常終了していること。
- 対象ホストでDockerが実行中であること。
- `logging_backend_network_ipv4_subnet`及び`logging_backend_network_ipv6_subnet`に設定したCIDRが他のDockerブリッジネットワークと重複していないこと。

### 検証環境の設定

本節では, 検証用の設定内容について説明します。

検証には「主要変数」の設定例に示した`elastic-backend`, `172.18.0.0/16`及び`fd00:172:18::/64`を使用します。外部疎通確認はホスト内でIPv4とIPv6を併用する構成を前提としてIPv4通信で代表して実施しますが, Dockerネットワーク及び規則の構成確認はIPv4とIPv6の両方で実施します。

### 検証コマンドと期待結果

#### 1. DockerブリッジネットワークCIDR確認

**実施対象ホスト**: logging_backendグループに属する対象ホスト

**実行するコマンド**:

```bash
docker network inspect elastic-backend --format '{{range .IPAM.Config}}{{println .Subnet}}{{end}}'
```

**期待される出力**:

```plaintext
172.18.0.0/16
fd00:172:18::/64
```

**実行結果の例**:

```bash
$ docker network inspect elastic-backend --format '{{range .IPAM.Config}}{{println .Subnet}}{{end}}'
172.18.0.0/16
fd00:172:18::/64
```

**確認ポイント**:

- dockerコマンドの出力結果が`172.18.0.0/16`及び`fd00:172:18::/64`であることを確認することで, 指定したIPv4 CIDR及びIPv6 CIDRのDockerブリッジネットワークが存在することを確認します。

#### 2. iptables規則確認

**実施対象ホスト**: logging_backendグループに属する対象ホスト

**実行するコマンド**:

```bash
sudo iptables -t filter -S ELASTIC-STACK-FWD
sudo iptables -t nat -S ELASTIC-STACK-NAT
sudo ip6tables -t filter -S ELASTIC-STACK-FWD
sudo ip6tables -t nat -S ELASTIC-STACK-NAT
```

**期待される出力**:

```plaintext
-A ELASTIC-STACK-FWD -s 172.18.0.0/16 ! -o br-... -j ACCEPT
-A ELASTIC-STACK-NAT ! -o br-... -j MASQUERADE
-A ELASTIC-STACK-FWD -s fd00:172:18::/64 ! -o br-... -j ACCEPT
-A ELASTIC-STACK-NAT ! -o br-... -j MASQUERADE
```

**実行結果の例**:

```bash
$ sudo iptables -t filter -S ELASTIC-STACK-FWD
-N ELASTIC-STACK-FWD
-A ELASTIC-STACK-FWD -s 172.18.0.0/16 ! -o br-123456789abc -j ACCEPT
$ sudo iptables -t nat -S ELASTIC-STACK-NAT
-N ELASTIC-STACK-NAT
-A ELASTIC-STACK-NAT ! -o br-123456789abc -j MASQUERADE
$ sudo ip6tables -t filter -S ELASTIC-STACK-FWD
-N ELASTIC-STACK-FWD
-A ELASTIC-STACK-FWD -s fd00:172:18::/64 ! -o br-123456789abc -j ACCEPT
$ sudo ip6tables -t nat -S ELASTIC-STACK-NAT
-N ELASTIC-STACK-NAT
-A ELASTIC-STACK-NAT ! -o br-123456789abc -j MASQUERADE
```

**確認ポイント**:

- iptablesコマンドのfilter表出力結果に送信元`172.18.0.0/16`の許可規則があることを確認することで, 外向きIPv4転送が許可されていることを確認します。
- iptablesコマンドのnat表出力結果に`MASQUERADE`規則があることを確認することで, 外向き通信の送信元IPアドレスが変換されることを確認します。
- ip6tablesコマンドのfilter表出力結果に送信元`fd00:172:18::/64`の許可規則があることを確認することで, 外向きIPv6転送が許可されていることを確認します。
- ip6tablesコマンドのnat表出力結果に`MASQUERADE`規則があることを確認することで, 外向きIPv6通信の送信元IPアドレスが変換されることを確認します。

#### 3. systemdサービス状態確認

**実施対象ホスト**: logging_backendグループに属する対象ホスト

**実行するコマンド**:

```bash
systemctl is-enabled docker-network-elastic-stack.service
systemctl is-active docker-network-elastic-stack.service
```

**期待される出力**:

```plaintext
enabled
active
```

**実行結果の例**:

```bash
$ systemctl is-enabled docker-network-elastic-stack.service
enabled
$ systemctl is-active docker-network-elastic-stack.service
active
```

**確認ポイント**:

- systemctlコマンドの出力結果が`enabled`及び`active`であることを確認することで, 再起動後の規則再適用が有効であることを確認します。

## トラブルシューティング

### 1. DockerネットワークCIDR不一致で停止する場合

**実施対象ホスト**: logging_backendグループに属する対象ホスト

**実行するコマンド**:

```bash
docker network inspect elastic-backend | jq -r '.[].IPAM.Config[].Subnet'
docker network ls
```

**実行結果の例**:
```bash
$ docker network inspect elastic-backend | jq -r '.[].IPAM.Config[].
Subnet'
172.18.0.0/16
fd00:172:18::/64
$ docker network ls
NETWORK ID     NAME              DRIVER    SCOPE
32bf2d901566   bridge            bridge    local
216cb7cac2d8   elastic-backend   bridge    local
e5653ff38886   host              host      local
d1c807d24c35   none              null      local
```

**確認ポイント**:

- dockerコマンドの出力結果中の`IPAM.Config.Subnet`を確認することで, 既存ネットワークのCIDRが`logging_backend_network_ipv4_subnet`及び`logging_backend_network_ipv6_subnet`と一致していることを確認します。
- dockerコマンドの出力結果中の各ネットワーク名を確認することで, 対象CIDRと重複する別ネットワークを特定します。

### 2. systemdサービスが起動しない場合

**実施対象ホスト**: logging_backendグループに属する対象ホスト

**実行するコマンド**:

```bash
systemctl status docker-network-elastic-stack.service --no-pager
journalctl -u docker-network-elastic-stack.service -n 100 --no-pager
```

**実行結果の例**:
```bash
$ systemctl status docker-network-elastic-stack.service --no-pager
● docker-network-elastic-stack.service - Elastic Stack Docker network IPv4 and IPv6 egress rules
     Loaded: loaded (/etc/systemd/system/docker-network-elastic-stack.service; enabled; preset: disabled)
     Active: active (exited) since Sun 2026-08-09 12:37:34 JST; 3h 31min ago
    Process: 3123118 ExecStart=/usr/local/libexec/docker-network-elastic-stack-apply (code=exited, status=0/SUCCESS)
   Main PID: 3123118 (code=exited, status=0/SUCCESS)
        CPU: 54ms

Aug 09 12:37:34 observer01 systemd[1]: Starting Elastic Stack Docker network IPv4 and …es...
Aug 09 12:37:34 observer01 systemd[1]: Finished Elastic Stack Docker network IPv4 and …ules.
Hint: Some lines were ellipsized, use -l to show in full.
$ journalctl -u docker-network-elastic-stack.service -n 100 --no-pager
Aug 09 12:37:34 observer01 systemd[1]: Starting Elastic Stack Docker network IPv4 and IPv6 egress rules...
Aug 09 12:37:34 observer01 systemd[1]: Finished Elastic Stack Docker network IPv4 and IPv6 egress rules.
```

**確認ポイント**:

- systemctlコマンドの出力結果中の`Active:`と`ExecStart`を確認することで, 規則適用プログラムの終了状態を確認します。
- journalctlコマンドの出力結果中のエラーメッセージを確認することで, Dockerネットワーク又はiptables規則の適用失敗原因を確認します。

## 注意事項

- `logging_backend_network_ipv4_subnet`又は`logging_backend_network_ipv6_subnet`を変更する場合は, 既存コンテナを停止して既存ネットワークを管理者が削除した後に本ロールを実行します。
- IPv4単独で作成済みの同名ネットワークをIPv4とIPv6を併用する構成へ移行する場合は, 既存コンテナを停止して既存ネットワークを管理者が削除した後に本ロールを実行します。
- 本ロールはDocker全体のiptables自動管理を有効化しません。
- 本ロールはDocker全体のip6tables自動管理を有効化しません。
- 本ロールはElastic Stack専用CIDR以外のDockerブリッジネットワークへ規則を追加しません。

## 参考資料

### 公式ドキュメント

- [Ansible Playbook](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html)
- [CIDRとIPネットワーク](https://docs.python.org/3/library/ipaddress.html)
- [Docker bridge network](https://docs.docker.com/engine/network/drivers/bridge/)
- [docker network create](https://docs.docker.com/reference/cli/docker/network/create/)
- [iptables](https://man7.org/linux/man-pages/man8/iptables.8.html)
- [ip6tables](https://man7.org/linux/man-pages/man8/ip6tables.8.html)
- [NAT HOWTO](https://www.netfilter.org/documentation/HOWTO/NAT-HOWTO.html)
- [systemd service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html)
- [systemctl](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)
- [Python](https://docs.python.org/3/)
- [jq Manual](https://jqlang.github.io/jq/manual/)

### 関連ロール

- [roles/elasticsearch/Readme.md](../elasticsearch/Readme.md) Elasticsearch関連コンポーネント全体の仕様についての解説を記載しています。以下の内容について確認する場合に参照します。
  - 設計背景と非干渉条件
  - Elasticsearch 関連コンポーネント構成図
  - 各コンテナの役割分担
  - inventory group と展開されるコンテナとの対応関係
