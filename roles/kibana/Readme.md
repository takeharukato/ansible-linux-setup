# Kibana ロール

本ロールは, 本 playbook で導入する Kibana を, 本 playbook で導入する Elasticsearch, Logstash, Elastic Agent と組み合わせて運用するためのロールです。

## 目次

- [Kibana ロール](#kibana-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
    - [基本仕様](#基本仕様)
    - [本ロールで実施する主な処理](#本ロールで実施する主な処理)
    - [Kubernetes API監査ログの参照](#kubernetes-api監査ログの参照)
  - [実行方法](#実行方法)
    - [Makefile ターゲットを使用する場合](#makefile-ターゲットを使用する場合)
    - [ansible-playbookコマンドを使用する場合](#ansible-playbookコマンドを使用する場合)
  - [主要変数](#主要変数)
    - [各ロール固有の利用者入力値](#各ロール固有の利用者入力値)
      - [必須入力値](#必須入力値)
      - [任意入力値](#任意入力値)
        - [基本設定](#基本設定)
        - [接続設定](#接続設定)
        - [service account token 関連設定](#service-account-token-関連設定)
    - [Elastic Stack間共有設定値](#elastic-stack間共有設定値)
        - [起動検証関連設定](#起動検証関連設定)
    - [変数設定例](#変数設定例)
      - [host\_vars の設定例](#host_vars-の設定例)
      - [vars/all-config.yml の設定例](#varsall-configyml-の設定例)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [展開されるコンテナの仕様](#展開されるコンテナの仕様)
    - [ポート公開](#ポート公開)
    - [ファイルバインド](#ファイルバインド)
    - [ネットワーク定義](#ネットワーク定義)
    - [ファイルバインドに関する補足事項](#ファイルバインドに関する補足事項)
    - [公開ポートに関する補足事項](#公開ポートに関する補足事項)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [検証の前提条件](#検証の前提条件)
    - [検証環境の設定](#検証環境の設定)
    - [検証コマンドと期待結果](#検証コマンドと期待結果)
      - [1. Kibana 待受確認](#1-kibana-待受確認)
      - [2. Kibana 状態確認](#2-kibana-状態確認)
      - [3. Kubernetes API監査ログのDiscover表示確認](#3-kubernetes-api監査ログのdiscover表示確認)
    - [異常時の確認項目](#異常時の確認項目)
      - [1. ポート競合の確認](#1-ポート競合の確認)
      - [2. ネットワーク作成状態の確認](#2-ネットワーク作成状態の確認)
      - [3. 設定ファイル生成状態の確認](#3-設定ファイル生成状態の確認)
      - [4. Docker Compose 定義ファイル生成状態の確認](#4-docker-compose-定義ファイル生成状態の確認)
      - [5. コンテナログのエラー確認](#5-コンテナログのエラー確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. Kibana が起動しない場合](#1-kibana-が起動しない場合)
    - [2. `curl` で応答しない場合](#2-curl-で応答しない場合)
    - [3. Kibana 状態が `green`, `yellow`, `available` にならない場合](#3-kibana-状態が-green-yellow-available-にならない場合)
    - [4. Elasticsearch へ接続できない場合](#4-elasticsearch-へ接続できない場合)
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

## 前提条件

本 playbook を実行する前提条件は, 次のとおりです。

- 対象ホストが, `inventory/hosts` ファイル中の `logging_backend` グループに登録されていること。
- 対象ホストの OS は, Debian 系又は RHEL 系であること。
- 対象ホストで Docker と Docker Compose が利用可能であること。
- 対象ホストで `sudo` によるディレクトリ作成とコンテナ起動が可能であること。
- `kibana_server_port` に設定するポート番号が, 既存サービスで使用するポート番号と競合しないこと。

### 基本仕様

本ロールの Kibana 導入処理の仕様は, 次のとおりです:

- コンテナイメージは `docker.elastic.co/kibana/kibana:8.19.19` を使用すること。
- Kibana は `0.0.0.0:5601` で待受し, TCPプロトコルのポート番号5601番 を使用すること。
- 設定, データ, ログは, 本 playbook で導入する専用ディレクトリへ分離すること。
- Kibana は, 本 playbook で導入する backend 用ネットワークへ参加すること。
- Kibana から接続する Elasticsearch の接続先は, `elastic_search_container_name` と `elastic_search_http_port` から内部的に生成し, ロールの利用者の設定変更誤りが生じにくい動作とすること。

### 本ロールで実施する主な処理

本ロールでは, 次の処理を実施します。

1. `docker compose` が利用可能であることを確認します。
2. 本 playbook で導入するディレクトリを作成します。
3. Kibana の設定ファイルと Docker Compose 定義ファイルを生成します。
4. backend 用ネットワークへ接続して Kibana コンテナを起動します。
5. 起動後にポート待機と HTTP 応答確認を行います。

### Kubernetes API監査ログの参照

`elastic-agent-k8s-audit`で収集したKubernetes API監査ログは, 既定では`logs-kubernetes.audit_logs-k8s_system` Data Streamへ保存されます。Kibana GUI上のDiscoverでは, このData Streamを含むData Viewを選択して監査イベントを検索します。

代表的な検索対象フィールドは`data_stream.dataset`, `data_stream.namespace`, `kubernetes.audit.verb`, `kubernetes.audit.user.username`, `kubernetes.audit.objectRef.*`, `kubernetes.audit.responseStatus.*`です。

## 実行方法

### Makefile ターゲットを使用する場合

制御ホストで次のコマンドを実行します。

```bash
make run_logging_backend
```

このターゲットは Elasticsearch, Logstash, Kibana, Fleet Server, Fleet Bootstrapを順に適用し, 制御ホスト上のEnrollment Token共有ファイルへの保存まで完了します。Kibana単独適用は, 次節の`ansible-playbook`による実行手順を使用します。

### ansible-playbookコマンドを使用する場合

制御ホストで次のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts logging-backend.yml --tags kibana
```

このコマンドは, `logging_backend` グループに対して Kibana ロールのみを実行します。

## 主要変数

### 各ロール固有の利用者入力値

#### 必須入力値

本ロール固有の必須入力値はありません。Elasticsearchのセキュリティ機能が有効な場合のservice account tokenは, 既存ファイル又は自動発行処理から取得します。

#### 任意入力値

##### 基本設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `logging_kibana_enabled` | Kibana ロールの有効化フラグ。 | `false` | `true` |
| `kibana_encrypted_saved_objects_key_generation_timeout_seconds` | 暗号化キー生成処理のタイムアウト秒数。 | `30` | `30` |

##### 接続設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `kibana_server_host` | Kibana の HTTP 待受アドレス。 | `0.0.0.0` | `0.0.0.0` |
| `kibana_server_port` | Kibana の HTTP 待受ポート。 | `5601` | `5601` |
| `kibana_endpoint_url_explicit` | ランタイムエンドポイントの明示指定値。未指定時は `logging_backend_resolved_host` と `kibana_server_port` から組み立てる。 | 空文字列 | `https://kibana01.example.org:5601` |
| `kibana_tls_mode` | ランタイムエンドポイントのURLスキームが`https`の場合に参照するTLS検証モード。指定可能な値は, [Elasticsearchロールの共有設定値](../elasticsearch/Readme.md#共有設定値に関する補足説明)を参照する。 | `logging_backend_default_tls_mode`の指定値。 | `none` |

##### service account token 関連設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `kibana_service_token_auto_create` | Kibana 用 service account token が未配置時に自動発行するフラグ。 | `true` | `false` |
| `kibana_service_token_name` | Kibana 用 service account token 名。 | `kibana-service-token` | `kibana-service-token` |
| `kibana_service_token_namespace` | Kibana 用 service account token の namespace。 | `elastic` | `elastic` |
| `kibana_service_token_service_name` | Kibana 用 service account token の service 名。 | `kibana` | `kibana` |
| `kibana_service_token_issue_username` | Kibana 用 service account token 発行時に利用する Elasticsearch ユーザ名。 | `{{ elastic_search_security_username | default('elastic') }}` | `elastic` |
| `kibana_service_token_issue_password` | Kibana 用 service account token 発行時に利用する Elasticsearch パスワード。 | `{{ elastic_search_bootstrap_password | default('') }}` | `DUMMY_ELASTIC_PASSWORD` |
| `kibana_service_token_issue_timeout_seconds` | Kibana 用 service account token 発行APIの接続タイムアウト秒数。 | `30` | `30` |
| `kibana_service_token_issue_retries` | Kibana 用 service account token 発行APIの再試行回数。 | `3` | `3` |
| `kibana_service_token_issue_retry_interval_seconds` | Kibana 用 service account token 発行APIの再試行待機秒数。 | `5` | `5` |

### Elastic Stack間共有設定値

共有設定値の意味, 設定要否, 既定値及び設定例は, [Elasticsearchロールの共有設定値](../elasticsearch/Readme.md#varsall-configymlに設定するelastic-stack間共有設定値)を参照します。Kibanaでは, 共通の版数, Dockerブリッジネットワーク, 接続先ホスト, URLスキーム, TLS検証モード, 証明書及び外部ホストからの疎通確認設定が影響します。

##### 起動検証関連設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `kibana_wait_host` | 起動確認で待機する接続先ホスト。 | `127.0.0.1` | `127.0.0.1` |
| `kibana_wait_delegate_to` | 起動確認を実行する接続元ホスト。 | `{{ inventory_hostname }}` | `{{ inventory_hostname }}` |
| `kibana_wait_timeout` | 起動確認のタイムアウト時間。 | `120` | `120` |
| `kibana_wait_delay` | 起動確認の開始遅延時間。 | `2` | `2` |
| `kibana_wait_sleep` | 起動確認の待機間隔。 | `2` | `2` |
| `kibana_wait_retries` | 起動確認の再試行回数。 | `5` | `5` |

### 変数設定例

#### host_vars の設定例

ホスト固有に変える値を `host_vars/kibana01.local.yml` に記載します。
`logging_backend_host` は共通変数であるため, この例には含めず `vars/all-config.yml` に記載します。

```yaml
1: logging_kibana_enabled: true
2: kibana_server_port: 5601
3: kibana_wait_delegate_to: "{{ inventory_hostname }}"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `logging_kibana_enabled: true` | Kibana ロールを有効化し, ディレクトリ作成, 設定生成, コンテナ起動, 起動確認を実行します。 | `false` の場合は Kibana ロールの処理が実行されず, 期待した導入結果を得られないためです。 |
| 2 | `kibana_server_port: 5601` | Kibana の HTTP 待受ポートを `5601` に設定します。 | ポートが未設定又は誤設定の場合, 利用者画面への接続先が不一致となり, 到達確認に失敗するためです。 |
| 3 | `kibana_wait_delegate_to: "{{ inventory_hostname }}"` | 起動確認タスクを対象ホスト自身から実行します。 | 到達不能な接続元を設定した場合, 起動済みでも待受確認に失敗し, ロール実行が異常終了するためです。 |

この例では, Kibana の待受ポートを明示し, 起動確認の接続元を対象ホスト自身にします。

#### vars/all-config.yml の設定例

全ホスト共通の値を `vars/all-config.yml` に記載します。
`logging_backend_*` は `host_vars` に重複定義せず, この節の例のように `vars/all-config.yml` のみに記載します。

```yaml
1: logging_kibana_enabled: true
2: kibana_server_host: "0.0.0.0"
3: kibana_server_port: 5601
4: kibana_wait_host: "127.0.0.1"
5: kibana_wait_timeout: 120
6: kibana_wait_delay: 2
7: kibana_wait_sleep: 2
8: kibana_wait_retries: 5
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `logging_kibana_enabled: true` | Kibana ロールを有効化し, 共通設定にもとづく導入処理を実行します。 | `false` の場合は共通設定が存在しても導入処理が実行されず, 設定の反映漏れが発生するためです。 |
| 2-3 | `kibana_server_host: "0.0.0.0"`, `kibana_server_port: 5601` | Kibana の HTTP 待受を `0.0.0.0:5601` に設定し, 対象ホストから利用可能にします。 | 未設定又は誤設定の場合, 待受先アドレスやポートが期待値と一致せず, 接続確認が失敗するためです。 |
| 4-8 | `kibana_wait_host: "127.0.0.1"`, `kibana_wait_timeout: 120`, `kibana_wait_delay: 2`, `kibana_wait_sleep: 2`, `kibana_wait_retries: 5` | 起動確認の接続先と再試行条件を定義し, 起動直後の待受未完了を吸収して到達性を検証します。 | これらが未設定又は不適切な場合, 起動直後の一時的な応答遅延を異常と誤判定し, ロール実行が失敗するためです。 |

この例では, 本 playbook で導入する側の共通値を一箇所へ集約します。

## テンプレートと生成ファイル

| テンプレート | 生成先 (括弧内は規定) | 用途 | 主な内容 |
| --- | --- | --- | --- |
| `templates/kibana.yml.j2` | `{{ kibana_compose_dir }}/kibana.yml` (規定: `/srv/kibana/kibana.yml`) | Kibana の設定ファイルを生成します。 | 待受アドレス, 待受ポート, Elasticsearch 接続先, 暗号化済み保存オブジェクト用キー。 |
| `templates/docker-compose.yml.j2` | `{{ kibana_compose_file }}` (規定: `/srv/kibana/docker-compose.yml`) | Kibana の Docker Compose 定義ファイルを生成します。 | コンテナイメージ, コンテナ名, ボリューム, ポート公開, ネットワーク。 |

`kibana.yml.j2` は, Kibana コンテナ内の設定用ファイルを展開します。`docker-compose.yml.j2` は, コンテナイメージ, コンテナ名, ボリューム, ポート公開, ネットワークの設定ファイルを展開します。

## 展開されるコンテナの仕様

### ポート公開

| ホスト側待受 | コンテナ側待受 | プロトコル | 用途 |
| --- | --- | --- | --- |
| `{{ kibana_server_host }}:{{ kibana_server_port }}` (既定: `0.0.0.0:5601`) | `{{ kibana_server_port }}` (既定: `5601`) | TCP | Kibana の HTTP エンドポイントを対象ホスト側から利用可能にします。 |

`templates/docker-compose.yml.j2` では, Kibana コンテナの HTTP ポートを次の形式で公開します。

- `{{ kibana_server_host }}:{{ kibana_server_port }}:{{ kibana_server_port }}` (既定: `0.0.0.0:5601:5601`)

既定値は, 対象ホスト上のすべてのネットワークインターフェースで TCPプロトコルのポート番号5601番 を待受し, 同じポート番号で Kibana コンテナへ転送する設定であることを意味します。

### ファイルバインド

`templates/docker-compose.yml.j2` では, ホスト側のファイルやディレクトリを以下のようにコンテナ内から使用可能とするように設定します。

| ホスト側 | コンテナ側 | モード | 用途 |
| --- | --- | --- | --- |
| `{{ kibana_compose_dir }}/kibana.yml` (既定: `/srv/kibana/kibana.yml`) | `/usr/share/kibana/config/kibana.yml` | `ro` | ホスト側の Kibana 設定ファイルをコンテナ内から参照可能にします。コンテナ内から当該のファイルを破壊不可能なように読み取り専用でコンテナ側に公開します。 |
| `{{ kibana_data_dir }}` (既定: `/srv/kibana/data`) | `/usr/share/kibana/data` | `rw` | Kibana の内部データを永続化し, コンテナの再作成時でも内部状態を継続的に利用可能にします。 |
| `{{ kibana_logs_dir }}` (既定: `/srv/kibana/logs`) | `/usr/share/kibana/logs` | `rw` | Kibana のログを永続化し, コンテナの動作が停止した場合でもホスト上からログ情報を参照可能にします。 |

既定値は, 設定ファイルをホスト上の `/srv/kibana/kibana.yml` から読み込み, データをホスト上の `/srv/kibana/data`, ログをホスト上の `/srv/kibana/logs` に保存する設定です。

### ネットワーク定義

`templates/docker-compose.yml.j2` では, `elastic_backend` ネットワークを定義し, `external: true` で既存ネットワークを利用します。実体として参照するネットワーク名は `{{ kibana_network_name }}` (既定: `elastic-backend`) です。

既定値は, docker-network-elastic-stackロールが作成する`elastic-backend`外部ネットワークへKibanaコンテナを参加させ, 同一のホスト側ネットワークを通して関連コンテナと通信する設定です。本ロールは`elastic-backend`の存在を確認し, 存在しない場合は処理を停止します。

### ファイルバインドに関する補足事項

- 本ロールは, 設定ファイル, データ, ログの保存先をホスト側へ分離し, コンテナ再作成後もデータを保持することを保証します。
- 本ロールは, 設定ファイルを読み取り専用でコンテナへ渡し, コンテナ内の処理によって設定ファイルが書き換わらないことを保証します。
- 本ロールは, 規定値を使用する場合に `/srv/kibana` 配下へ設定, データ, ログを集約し, 配置先の一貫性を維持することを保証します。

### 公開ポートに関する補足事項

- 本ロールは, 公開ポート設定にもとづいて Kibana の HTTP エンドポイントに対して対象ホスト側からアクセス可能になることを待ち合わせることで, 正常にポート公開がなされていることを確認, 保証します。
- 本ロールは, 起動後に公開ポート経由で接続確認を実施し, 状態確認用 URL である `/api/status` の `status.overall.state` または `status.overall.level` が, 全機能が利用可能である状態 (`green`), 基本機能は利用可能だが一部機能の準備が継続中の状態 (`yellow`), 及び Kibana の状態 API で全サービスと全プラグインが利用可能であることを示す状態 (`available`) のいずれかになるまで待機することで, Kibana が利用可能な状態になることを保証します。
- 規定値を使用する場合は `0.0.0.0:5601` で待受します。外部からの接続元を限定したい場合は, `kibana_server_host` に `127.0.0.1` などの値を設定することで, 待受先アドレスを制限することも可能です。

## 実行フロー

1. [tasks/load-params.yml](tasks/load-params.yml) で OS 別パラメータと共通変数を読み込みます。
2. [tasks/validate.yml](tasks/validate.yml) で導入前提, パス, コンテナイメージ名, ポート, Elasticsearch 接続先を導出する変数, OS 条件を確認します。
3. [tasks/package.yml](tasks/package.yml) で Docker Compose と暗号化キー生成処理が利用可能であることを確認します。
4. [tasks/directory.yml](tasks/directory.yml) で compose 用ディレクトリと設定, データ, ログ, 暗号化キーの配置先を作成します。
5. [tasks/user_group.yml](tasks/user_group.yml) で実行ユーザとグループを作成し, ディレクトリ所有権を調整します。
6. [tasks/config.yml](tasks/config.yml) で暗号化キーが未作成の場合に64桁の16進キーを生成し, 権限`0600`で保存します。続いて [templates/kibana.yml.j2](templates/kibana.yml.j2) と [templates/docker-compose.yml.j2](templates/docker-compose.yml.j2) を配置します。設定ファイルまたは Docker Compose 定義ファイルの更新時は `kibana_restart_service` を通知し, [handlers/main.yml](handlers/main.yml) から読み込む [handlers/restart-service.yml](handlers/restart-service.yml) でコンテナを再作成します。
7. [tasks/service.yml](tasks/service.yml) でdocker-network-elastic-stackロールが作成したbackend専用ネットワークの存在を確認し, `docker compose up -d --remove-orphans`によりKibanaコンテナを起動します。
8. [tasks/verify.yml](tasks/verify.yml) で対象ホスト上での疎通確認として `wait_for` によるポート待機と `uri` による `/api/status` の応答確認を実施し, `status.overall.state` または `status.overall.level` が `yellow`, `green`, `available` のいずれかであることを検証します。`logging_verify_external_enabled: true` の場合は, 同じランタイムエンドポイントに対して外部ホストからの疎通確認も実施します。

## 検証ポイント

### 検証の前提条件

検証を始める前に, 次の条件が満たされていることを確認します。

- 対象ホストで Docker と Docker Compose が利用できること。
- `kibana_server_port` に設定したポートが他のサービスで使われていないこと。
- `kibana_compose_dir` 配下を作成できること。
- `logging_backend` グループに対象ホストが登録されていること。

### 検証環境の設定

本節では, 検証用の設定内容について説明します。

**検証用の host_vars**:

```yaml
1: kibana_server_host: "0.0.0.0"
2: kibana_server_port: 5601
3: kibana_wait_host: "127.0.0.1"
4: kibana_wait_delegate_to: "{{ inventory_hostname }}"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1-2 | `kibana_server_host: "0.0.0.0"`, `kibana_server_port: 5601` | `0.0.0.0:5601` で待受し, HTTP 接続確認を実行可能にします。 | 待受先アドレス又はポートが不一致の場合, 検証コマンドが接続不能となり, 導入結果を判定できないためです。 |
| 3-4 | `kibana_wait_host: "127.0.0.1"`, `kibana_wait_delegate_to: "{{ inventory_hostname }}"` | 対象ホスト自身から `127.0.0.1` 宛に起動確認を実行します。 | 接続元又は接続先が不適切な場合, Kibana が起動済みでも待受確認に失敗し, 誤検知を招くためです。 |

この設定により, 本 playbook で導入する Kibana が対象ホスト上で待受し, 自己確認が可能になります。

このロールでは, ランタイムエンドポイントを起点に, 対象ホスト上での疎通確認と外部ホストからの疎通確認を段階的に実施します。

### 検証コマンドと期待結果

#### 1. Kibana 待受確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

```bash
curl -sS -i http://127.0.0.1:5601/
```

**期待される出力**:

```plaintext
HTTP/1.1 302 Found
location: /spaces/enter
```

**実行結果の例**:
```bash
$ curl -sS -i http://127.0.0.1:5601/
HTTP/1.1 302 Found
location: /spaces/enter
x-content-type-options: nosniff
referrer-policy: strict-origin-when-cross-origin
permissions-policy: camera=(), display-capture=(), fullscreen=(self), geolocation=(), microphone=(), web-share=()
cross-origin-opener-policy: same-origin
content-security-policy: script-src 'report-sample' 'self'; worker-src 'report-sample' 'self' blob:; style-src 'report-sample' 'self' 'unsafe-inline'
content-security-policy-report-only: form-action 'report-sample' 'self'
kbn-name: 307d5ff3664b
kbn-license-sig: ad4bbec651b4d857d896b55bfae1dc500b08d7b7a5688555b8081a642d9455dc
cache-control: private, no-cache, no-store, must-revalidate
content-length: 0
Date: Mon, 03 Aug 2026 03:00:59 GMT
Connection: keep-alive
Keep-Alive: timeout=120
```

**確認ポイント**:

- `http://127.0.0.1:5601/` へ接続できること。
- HTTPステータスコードが `302` であること。
- `location` ヘッダに `/spaces/enter` が含まれること。

#### 2. Kibana 状態確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

```bash
curl -sS http://127.0.0.1:5601/api/status | jq '.status.overall'
```

**期待される出力**:

```plaintext
{
  "level": "available",
  "summary": "All services and plugins are available"
}
```

**実行結果の例**:

```bash
$ curl -sS http://127.0.0.1:5601/api/status | jq '.status.overall'
{
  "level": "available",
  "summary": "All services and plugins are available"
}
```

**確認ポイント**:

- `status.overall.state` または `status.overall.level` が `yellow`, `green`, `available` のいずれかであること。
- `yellow` は基本機能が利用可能で一部機能の準備が継続中であること, `green` は全機能が利用可能であること, `available` は Kibana の状態 API で全サービスと全プラグインが利用可能であることを示すこと。
- Elasticsearch 接続先の異常により `red` になっていないこと。

#### 3. Kubernetes API監査ログのDiscover表示確認

Kibana GUI上のDiscoverで`logs-kubernetes.audit_logs-k8s_system`を含むData Viewを選択し, `data_stream.dataset : "kubernetes.audit_logs"`でイベントを検索します。検索結果が0件の場合は, Data Viewの対象パターンと`@timestamp`の時間範囲を確認します。Data Stream自体の有無と保存済みdocumentはDev Toolsから直接確認できます。

### 異常時の確認項目

#### 1. ポート競合の確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

```bash
ss -ltnp | grep ':5601 '
```

**確認ポイント**:

- TCPプロトコルのポート番号5601番 が待受状態であること。
- Kibana コンテナの公開ポートとして待受していること。
- 想定外の別プロセスが同一ポートを占有していないこと。

#### 2. ネットワーク作成状態の確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

```bash
docker network ls --format '{{.Name}}' | grep -x 'elastic-backend'
```

**確認ポイント**:

- `kibana_network_name` の設定先ネットワークが存在すること。
- 規定値を使用する場合は, `elastic-backend` が存在すること。

#### 3. 設定ファイル生成状態の確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

```bash
ls -l /srv/kibana/kibana.yml
```

**確認ポイント**:

- Kibana の設定ファイルが存在すること。
- 規定値を使用する場合の確認先は `/srv/kibana/kibana.yml` であること。
- ファイルが 0 バイトではないこと。

#### 4. Docker Compose 定義ファイル生成状態の確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

```bash
ls -l /srv/kibana/docker-compose.yml
```

**確認ポイント**:

- `kibana_compose_file` に設定したファイルが存在すること。
- 規定値を使用する場合の確認先は `/srv/kibana/docker-compose.yml` であること。
- ファイルが 0 バイトではないこと。

#### 5. コンテナログのエラー確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

```bash
docker logs --tail 200 kibana
```

**確認ポイント**:

- 設定読込失敗, 起動失敗, Elasticsearch 接続失敗に関するエラーメッセージが出ていないこと。
- `kibana_container_name` を変更している場合は, 変更後のコンテナ名を指定して確認すること。

## トラブルシューティング

### 1. Kibana が起動しない場合

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

```bash
docker ps -a --filter name=kibana
docker logs --tail 200 kibana 2>&1 | grep -E '"log.level"[[:space:]]*:[[:space:]]*"(WARN|ERROR|FATAL)"'
docker compose -f /srv/kibana/docker-compose.yml config
sudo stat -c '%a %U %G' /srv/kibana/secrets/encrypted-saved-objects-encryption-key
ls -lnd /srv/kibana /srv/kibana/data /srv/kibana/logs
```

**実行結果の例**:

```bash
$ docker ps -a --filter name=kibana
CONTAINER ID   IMAGE                                    COMMAND                  CREATED       STATUS       PORTS                    NAMES
e896a5150359   docker.elastic.co/kibana/kibana:8.19.19   "/bin/tini -- /usr/l…"   2 hours ago   Up 2 hours   0.0.0.0:5601->5601/tcp   kibana
$ docker logs --tail 200 kibana 2>&1 | grep -E '"log.level"[[:space:]]*:[[:space:]]*"(WARN|ERROR|FATAL)"'
$ docker compose -f /srv/kibana/docker-compose.yml config
name: kibana
services:
  kibana:
    container_name: kibana
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
      ELASTICSEARCH_SERVICEACCOUNTTOKEN: AAEAAWVsYXN0aWMva2liYW5hL2tpYmFuYS1zZXJ2aWNlLXRva2VuOm80b2RFU0tXUWtlTGVmdjA3Znpzenc
      SERVER_HOST: 0.0.0.0
      SERVER_PORT: "5601"
    image: docker.elastic.co/kibana/kibana:8.19.19
    networks:
      elastic_backend: null
    ports:
      - mode: ingress
        host_ip: 0.0.0.0
        target: 5601
        published: "5601"
        protocol: tcp
    restart: unless-stopped
    volumes:
      - type: bind
        source: /srv/kibana/kibana.yml
        target: /usr/share/kibana/config/kibana.yml
        read_only: true
        bind: {}
      - type: bind
        source: /srv/kibana/data
        target: /usr/share/kibana/data
        bind: {}
      - type: bind
        source: /srv/kibana/logs
        target: /usr/share/kibana/logs
        bind: {}
networks:
  elastic_backend:
    name: elastic-backend
    external: true
$ sudo stat -c '%a %U %G' /srv/kibana/secrets/encrypted-saved-object
s-encryption-key
600 root root
$ ls -lnd /srv/kibana /srv/kibana/data /srv/kibana/logs
drwxr-xr-x.  6    0    0  103 Aug  9 12:39 /srv/kibana
drwxr-xr-x. 71 1000 1000 4096 Aug  9 12:42 /srv/kibana/data
drwxr-xr-x.  2 1000 1000    6 Aug  5 19:55 /srv/kibana/logs
```

**確認ポイント**:

- コンテナ状態が `Up` であること。
- ログに設定読込失敗, イメージ取得失敗, 起動失敗が出ていないこと。
- Compose 定義の構文確認が成功すること。
- 規定値を使用する場合, `/srv/kibana` 配下へ読み書き可能な権限があること。
- `stat`コマンドの出力が`600 root root`であり, 暗号化キーが他の利用者から読み取れないこと。

### 2. `curl` で応答しない場合

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

以下の`DUMMY_ELASTIC_PASSWORD`を`elastic_search_bootstrap_password`の設定値に変更して実行してください。

```bash
docker ps --filter name=kibana
ss -ltnp | grep ':5601 '
curl -v -u 'elastic:DUMMY_ELASTIC_PASSWORD' --max-time 5 http://127.0.0.1:5601/
```

**実行結果の例**:

```bash
$ docker ps --filter name=kibana
CONTAINER ID   IMAGE                                    COMMAND                  CREATED       STATUS       PORTS                    NAMES
e896a5150359   docker.elastic.co/kibana/kibana:8.19.19   "/bin/tini -- /usr/l…"   2 hours ago   Up 2 hours   0.0.0.0:5601->5601/tcp   kibana
$ ss -ltnp | grep ':5601 '
LISTEN 0      4096         0.0.0.0:5601       0.0.0.0:*
$ curl -v -u 'elastic:elastic' --max-time 5 http://127.0.0.1:5601/
*   Trying 127.0.0.1:5601...
* Connected to 127.0.0.1 (127.0.0.1) port 5601 (#0)
* Server auth using Basic with user 'elastic'
> GET / HTTP/1.1
> Host: 127.0.0.1:5601
> Authorization: Basic ZWxhc3RpYzplbGFzdGlj
> User-Agent: curl/7.76.1
> Accept: */*
>
* Mark bundle as not supporting multiuse
< HTTP/1.1 302 Found
< location: /spaces/enter
< x-content-type-options: nosniff
< referrer-policy: strict-origin-when-cross-origin
< permissions-policy: camera=(), display-capture=(), fullscreen=(self), geolocation=(), microphone=(), web-share=()
< cross-origin-opener-policy: same-origin
< content-security-policy: script-src 'report-sample' 'self'; worker-src 'report-sample' 'self' blob:; style-src 'report-sample' 'self' 'unsafe-inline'
< content-security-policy-report-only: form-action 'report-sample' 'self'
< kbn-name: e896a5150359
< kbn-license-sig: 1d4ed730859ad08b72ff054fb9da59fa18ef829ba57bc487616c073daf9f808e
< cache-control: private, no-cache, no-store, must-revalidate
< content-length: 0
< Date: Sun, 09 Aug 2026 05:48:20 GMT
< Connection: keep-alive
< Keep-Alive: timeout=120
<
* Connection #0 to host 127.0.0.1 left intact
```

**確認ポイント**:

- Kibana コンテナが起動中である(`STATUS`の列が`Up`である)こと。
- TCPプロトコルのポート番号5601番 で待受していること。
- `curl` が接続エラーではなく HTTP 応答を返すこと。

### 3. Kibana 状態が `green`, `yellow`, `available` にならない場合

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

以下の`DUMMY_ELASTIC_PASSWORD`を`elastic_search_bootstrap_password`の設定値に変更して実行してください。

```bash
curl -sS -u 'elastic:DUMMY_ELASTIC_PASSWORD' http://127.0.0.1:5601/api/status | jq '.status.overall'
docker logs --tail 200 kibana 2>&1 | grep -E '"log.level"[[:space:]]*:[[:space:]]*"(WARN|ERROR|FATAL)"'
```

**実行結果の例**:

```bash
$ curl -sS -u 'elastic:elastic' http://127.0.0.1:5601/api/status | j
q '.status.overall'
{
  "level": "available",
  "summary": "All services and plugins are available"
}
$ docker logs --tail 200 kibana 2>&1 | grep -E '"log.level"[[:space:]]*:[[:space:]]*"(WARN|ERROR|FATAL)"'
$
```

**確認ポイント**:

- `status.overall.state` または `status.overall.level` が `red` ではないこと。
- ログに起動時エラー又は Elasticsearch 接続失敗が出ていないこと。

### 4. Elasticsearch へ接続できない場合

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

以下の`DUMMY_ELASTIC_PASSWORD`を`elastic_search_bootstrap_password`の設定値に変更して実行してください。

```bash
docker exec kibana curl -sS -u 'elastic:DUMMY_ELASTIC_PASSWORD' http://elasticsearch:9200/
docker logs --tail 200 kibana 2>&1 | grep -E '"log.level"[[:space:]]*:[[:space:]]*"(WARN|ERROR|FATAL)"'
```

**実行結果の例**:

```bash
$ docker exec kibana curl -sS -u 'elastic:elastic' http://elasticsea
rch:9200/
{
  "name" : "observer01.example.org",
  "cluster_name" : "shared-logs",
  "cluster_uuid" : "mWEU68ySRbqcHfnuBsJ2Uw",
  "version" : {
    "number" : "8.19.19",
    "build_flavor" : "default",
    "build_type" : "docker",
    "build_hash" : "a091390de485bd4b127884f7e565c0cad59b10d2",
    "build_date" : "2025-02-28T10:07:26.089129809Z",
    "build_snapshot" : false,
    "lucene_version" : "9.12.0",
    "minimum_wire_compatibility_version" : "7.17.0",
    "minimum_index_compatibility_version" : "7.0.0"
  },
  "tagline" : "You Know, for Search"
}
$ docker logs --tail 200 kibana 2>&1 | grep -E '"log.level"[[:space:]]*:[[:space:]]*"(WARN|ERROR|FATAL)"'
$
```

**確認ポイント**:

- Kibana コンテナ内から `http://{{ elastic_search_container_name }}:{{ elastic_search_http_port }}` で示される接続先へ到達できること。
- backend 用ネットワーク上で Elasticsearch 名が解決できること。
- ログに接続先 URL の誤り又は名前解決失敗が出ていないこと。

## 注意事項

- 既存のサービスで使用されているポートやディレクトリと衝突しないような設定を実施すること。
- ネットワーク名と compose project 名を他の Docker Compose から展開されるコンテナと衝突しないようにすること。
- `kibana_data_dir` と `kibana_logs_dir` の所有者は, Kibanaコンテナイメージ仕様で指定される実行ユーザIDと実行グループID(既定では 1000:1000)に合わせること。これらの値は playbook の設計値ではなくコンテナイメージ仕様により決定されるため, コンテナイメージの仕様変更時だけ `vars/logging-backend-common.yml` の `logging_backend_container_user_id` と `logging_backend_container_group_id` を変更する。
- Kibana の Elasticsearch 接続先は内部変数として導出する設計であるため, 接続先を変更する場合は `elastic_search_container_name` 又は `elastic_search_http_port` を変更すること。
- 設定ファイル生成先は `/srv/kibana/config` ではなく `/srv/kibana/kibana.yml` であるため, 運用確認時の参照先を取り違えないこと。
- `kibana_encrypted_saved_objects_key_file`の内容を変更又は削除すると, 変更前のキーで暗号化したFleetの秘密情報を復号できなくなるため, 対象ホストの再構築時はキーファイルを安全に引き継ぐこと。

## 参考資料

### 公式ドキュメント

- [Kibana Guide](https://www.elastic.co/guide/en/kibana/8.17/index.html)
- [Kibana settings](https://www.elastic.co/guide/en/kibana/8.17/settings.html)
- [Secure the Elastic Stack](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/secure-cluster.html)
- [Enrollment Token](https://www.elastic.co/docs/reference/fleet/fleet-enrollment-tokens)
- [Service accounts and tokens](https://www.elastic.co/guide/en/elasticsearch/reference/current/service-accounts.html)
- [jq Manual](https://jqlang.github.io/jq/manual/)
- [Docker Compose documentation](https://docs.docker.com/compose/)
- [Ansible documentation](https://docs.ansible.com/ansible/latest/)

### 関連ロール

- [roles/elasticsearch/Readme.md](../elasticsearch/Readme.md) Elasticsearch関連コンポーネント全体の仕様についての解説を記載しています。以下の内容について確認する場合に参照します。
  - 設計背景と非干渉条件
  - Elasticsearch 関連コンポーネント構成図
  - 各コンテナの役割分担
  - inventory group と展開されるコンテナとの対応関係
