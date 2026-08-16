# Elasticsearch ロール

本ロールは, 本 playbook で導入する Elasticsearch を, 本 playbook で導入する Elastic Stack関連ロールである Kibana, Logstash, Fleet Server, Elastic Agent と組み合わせて運用するためのロールです。

Elastic Stack関連ロールを適用することで, 以下のURLからElastic StackのKibanaのWEB ユーザインターフェースにアクセス可能になります:
```plaintext
http://導入先ホスト:5601
```

## 目次

- [Elasticsearch ロール](#elasticsearch-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
    - [基本仕様](#基本仕様)
    - [設計背景と非干渉条件](#設計背景と非干渉条件)
    - [Elasticsearch関連コンポーネント構成図](#elasticsearch関連コンポーネント構成図)
    - [Elasticsearch関連コンポーネントの役割](#elasticsearch関連コンポーネントの役割)
    - [inventory group と Elasticsearch 関連コンポーネントの関係](#inventory-group-と-elasticsearch-関連コンポーネントの関係)
    - [Elasticsearch 関連コンポーネントの導入方式](#elasticsearch-関連コンポーネントの導入方式)
    - [Elasticsearch 関連ロールの構成](#elasticsearch-関連ロールの構成)
    - [展開されるコンテナの仕様](#展開されるコンテナの仕様)
      - [公開ポート](#公開ポート)
        - [公開ポートに関する補足事項](#公開ポートに関する補足事項)
      - [ファイルバインド](#ファイルバインド)
        - [ファイルバインドに関する補足事項](#ファイルバインドに関する補足事項)
      - [ネットワーク定義](#ネットワーク定義)
    - [本ロールで実施する主な処理](#本ロールで実施する主な処理)
  - [実行方法](#実行方法)
    - [Makefile ターゲットを使用する場合](#makefile-ターゲットを使用する場合)
    - [ansible-playbookコマンドを使用する場合](#ansible-playbookコマンドを使用する場合)
  - [主要変数](#主要変数)
    - [各ロール固有の利用者入力値](#各ロール固有の利用者入力値)
      - [必須入力値](#必須入力値)
      - [任意入力値](#任意入力値)
        - [基本設定](#基本設定)
        - [接続設定](#接続設定)
        - [Elasticsearchのセキュリティ機能関連設定](#elasticsearchのセキュリティ機能関連設定)
        - [HTTPS 証明書関連設定](#https-証明書関連設定)
    - [`vars/all-config.yml`に設定するElastic Stack間共有設定値](#varsall-configymlに設定するelastic-stack間共有設定値)
      - [共有設定値に関する補足説明](#共有設定値に関する補足説明)
      - [`logging_backend_host` の設定値に関する留意事項](#logging_backend_host-の設定値に関する留意事項)
    - [コンテナ起動確認関連設定](#コンテナ起動確認関連設定)
    - [バックアップ/リストア関連設定](#バックアップリストア関連設定)
    - [変数設定例](#変数設定例)
      - [host\_vars の設定例](#host_vars-の設定例)
      - [vars/all-config.yml の設定例](#varsall-configyml-の設定例)
    - [ログ対象を追加する手順](#ログ対象を追加する手順)
  - [バックアップ/リストア運用](#バックアップリストア運用)
    - [導入されるスクリプト仕様](#導入されるスクリプト仕様)
    - [バックアップ実行スクリプトのコマンドラインオプション](#バックアップ実行スクリプトのコマンドラインオプション)
    - [リストア実行スクリプトのコマンドラインオプション](#リストア実行スクリプトのコマンドラインオプション)
    - [バックアップ実行手順](#バックアップ実行手順)
    - [リストア実行手順](#リストア実行手順)
    - [定期バックアップ実行手順](#定期バックアップ実行手順)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [検証の前提条件](#検証の前提条件)
    - [検証環境の設定](#検証環境の設定)
    - [検証コマンドと期待結果](#検証コマンドと期待結果)
      - [1. Elasticsearch 待受確認](#1-elasticsearch-待受確認)
      - [2. Elasticsearch のクラスタ状態確認](#2-elasticsearch-のクラスタ状態確認)
    - [異常時の確認項目](#異常時の確認項目)
      - [1. ポート競合の確認](#1-ポート競合の確認)
      - [2. ネットワーク作成状態の確認](#2-ネットワーク作成状態の確認)
      - [3. 設定ファイル生成状態の確認](#3-設定ファイル生成状態の確認)
      - [4. Docker Compose 定義ファイル生成状態の確認](#4-docker-compose-定義ファイル生成状態の確認)
      - [5. コンテナログのエラー確認](#5-コンテナログのエラー確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. Elasticsearch が起動しない場合](#1-elasticsearch-が起動しない場合)
    - [2. `curl` で応答しない場合](#2-curl-で応答しない場合)
    - [3. Elasticsearch のクラスタ状態が `yellow` 又は `green` にならない場合](#3-elasticsearch-のクラスタ状態が-yellow-又は-green-にならない場合)
    - [4. 他者導入の Fluent Bit へ影響があるように見える場合](#4-他者導入の-fluent-bit-へ影響があるように見える場合)
    - [5. Kibana 起動直後に `.kibana_task_manager` の 503 警告が出る場合](#5-kibana-起動直後に-kibana_task_manager-の-503-警告が出る場合)
  - [注意事項](#注意事項)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)

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

## 前提条件

本 playbook を実行する前提条件は, 次のとおりです。

- 対象ホストが, `inventory/hosts` ファイル中の `logging_backend` グループに登録されていること。
- 対象ホストの OS は, Debian 系又は RHEL 系であること。
- 対象ホストで Docker と Docker Compose が利用可能であること。
- 対象ホストで `sudo`によるディレクトリ作成とコンテナ起動が可能であること。
- `elastic_search_http_port` に設定するポート番号が, 既存サービスで使用するポート番号と競合しないこと。

### 基本仕様

本ロールで Elasticsearch を導入する際の仕様は, 次のとおりです。

- コンテナイメージは `docker.elastic.co/elasticsearch/elasticsearch:8.19.19` を使用すること。
- Elasticsearch のクラスタ名は `shared-logs` とすること。
- ノード名は, 対象ホスト名を用いること。
- Elasticsearch は `0.0.0.0:9200` で待受し, TCPプロトコルのポート番号9200番 を使用すること。
- ノード探索方式は `single-node` とすること。
- 認証機能は有効とすること。
- HTTP層の暗号化は, Elasticsearch API エンドポイント URL スキームが `https` の場合に有効とすること。
- HTTP層の暗号化を有効化する場合は, HTTP層 TLS 用のサーバ証明書と秘密鍵を対象ホストへ事前配置し, 共通変数又は Elasticsearch 個別変数でそのパスを指定すること。
- HTTP層 TLS 用のサーバ証明書と秘密鍵は, Elasticsearch 個別変数が定義されている場合は個別変数を優先し, 未定義の場合は logging backend 共通変数を使用すること。
- ノード間通信の暗号化は無効とすること。
- 設定, データ, ログは, 本 playbook で導入する専用ディレクトリへ分離すること。
- 送信経路は, 本 playbook で導入する Logstash を経由すること。

### 設計背景と非干渉条件

本ロールでは, 他者導入の Fluent Bit などと干渉しないように独立したメトリクス収集機能を構成します:

- 他者導入の Fluent Bit 設定を変更しないこと。
- 他者導入の Elastic, Kibana, Logstash を変更しないこと。
- 既存ポートを再利用しないこと。
- 既存永続化ディレクトリを再利用しないこと。
- 既存サービスの定義や所有関係を変更しないこと。
- 共有ログ情報を削除しないこと。
- 共有メトリクス情報を削除しないこと。
- 本 playbook で導入する compose project 名, ネットワーク名, inventory group は, 他者導入の設定と分離すること。

### Elasticsearch関連コンポーネント構成図

本ロールでは, VM ゲスト OS のサービスログと Pod ログ, および対象ホストの資源使用状況を共有情報とし, 他者導入側と本 playbook 側の双方が参照可能となるよう Elasticsearch を構成します。

構成図を以下に示します。以下の図では, 実行時に動作するElasticsearch関連コンポーネントを四角形で記載し, コンポーネントが入出力に使用する情報とファイルを円柱形で記載します:

```mermaid
flowchart LR
  LOG_SRC[(共有ログ情報: VM ゲスト OS のサービスログと Pod ログ)]
  METRIC_SRC[(共有メトリクス情報: 対象ホストの資源使用状況)]

  subgraph other[他者導入]
    FBIT[Fluent Bit]
    EOLD[既存 Elastic / Kibana]
  end

  subgraph this[本 playbook で導入]
    ES[Elasticsearch]
    KB[Kibana]
    LS[Logstash]
    FS[Fleet Server]
    COL[Elastic Agent]
  end

  subgraph files[本 playbook で生成するファイル]
    TOKEN_FILE[(Enrollment Token共有ファイル)]
  end

  LOG_SRC -. 収集対象として参照可能 .-> COL
  LOG_SRC -. 収集対象として参照可能 .-> FBIT
  METRIC_SRC -. 収集対象として参照可能 .-> FBIT
  METRIC_SRC -. 収集対象として参照可能 .-> COL
  TOKEN_FILE -. Elastic Agent導入時にEnrollment Tokenを読込 .-> COL
  FS -->|Fleet管理設定を配布| COL
  COL --> LS
  LS --> ES
  ES --> KB
  FBIT --> EOLD
```

図中の矢印の意味は以下の通りです:

- 破線矢印: ログやメトリクス情報の参照関係, 又はファイルからElastic Agentへの入力関係を示します。Enrollment Token共有ファイルはElastic Agentロールが導入時に読み込みます。

- 実線矢印: 実行時の通信, 収集データ又は管理情報の流れを示します(例: Fleet Server -> Elastic Agent, Elastic Agent -> Logstash, Logstash -> Elasticsearch)。

### Elasticsearch関連コンポーネントの役割

各Elasticsearch関連コンポーネントの役割は以下の表の通りです:

| コンポーネント | 収集対象 | 送信先 | 主な責務 |
| --- | --- | --- | --- |
| Fleet Server | Elastic Agent 管理通信 | Elastic Agent | Elastic Agent の登録と Elastic Agent ポリシー配布を担います。 |
| Elastic Agent | Enrollment Token共有ファイル, 共有ログ情報, 共有メトリクス情報 | Fleet Server, Logstash | Enrollment Token共有ファイルからのEnrollment Token読込, Fleet Serverへの登録, ログとメトリクス情報の収集, 整形, 送信を担います。 |
| Logstash | Elastic Agent の送信内容 | Elasticsearch | 受信, 整形, 振り分けを担います。 |
| Elasticsearch | Logstash が整形して送信したデータ | Kibana | データの保存と検索を担います。 |
| Kibana | Elasticsearch に保存されたデータ | 利用者画面 | 可視化と閲覧操作を担います。 |

### inventory group と Elasticsearch 関連コンポーネントの関係

本節では, inventory group とその上で動作するコンポーネントの対応関係を図と表で示します。

Elasticsearch 関連コンポーネントに関するinventory groupは以下の2種類に分類されます:

1. `logging_backend` : Fleet Server, Elasticsearch, Logstash, Kibana が動作し, 収集データの管理, 集約, 保存, 可視化を提供するホストです。
2. `logging_collector` : Elastic Agent 関連ロールが適用され, VM ゲスト OS のサービスログ, Pod ログ, cgroup 由来の資源使用状況, ホストメトリクス ( host metrics ) を収集するホストです。

inventory group, ノード, ノード上で動作するコンポーネントの包含関係を箱で示し, コンポーネント間のデータフローを矢印で表した関係図を以下に示します:

```mermaid
flowchart LR
  subgraph LC[logging_collector]
    direction TB
    subgraph COL_NODE[ログ収集ノード]
      direction TB
      EA_COMP[Elastic Agent]
    end
  end

  subgraph LB[logging_backend]
    direction TB
    subgraph AGG_NODE[ログ集約ノード]
      direction TB
      FS_COMP[Fleet Server]
      LS_COMP[Logstash]
      ES_COMP[Elasticsearch]
      KB_COMP[Kibana]
    end
  end

  subgraph CTRL[制御ホスト]
    TOKEN_FILE_COMP[(Enrollment Token共有ファイル)]
  end

  TOKEN_FILE_COMP -. Elastic Agent導入時にEnrollment Tokenを読込 .-> EA_COMP
  FS_COMP -->|Fleet管理設定を配布| EA_COMP
  EA_COMP --> LS_COMP
  LS_COMP --> ES_COMP
  ES_COMP --> KB_COMP
```

上記の図は, 単純化のため, `logging_collector`, `logging_backend`のそれぞれ単一ノード構成で記載していますが, `logging_collector`, `logging_backend` のそれぞれのinventory groupに複数のノードを含めることが可能です。

Enrollment Token共有ファイルは`logging_backend`に属するファイルではなく, Fleet Bootstrapロールが制御ホスト上へ生成し, Elastic Agentロールが導入時に読み込むファイルです。実行時の管理設定はFleet ServerからElastic Agentへ配布されます。

### Elasticsearch 関連コンポーネントの導入方式

本playbookでは, `logging_backend` に導入する Elasticsearch 関連コンポーネントは Elastic の公式コンテナイメージを展開する方式で導入します。`logging_collector` にはElastic Agentをサービスとして導入し, Fleet ServerからElastic Agent ポリシーとPackage Policyを配布します。

inventory group, ノード種別, 当該ノード種別のホスト上で動作するElasticsearch 関連コンポーネント, Elasticsearch 関連コンポーネントの導入方式の関係は以下の表の通りです:

| inventory group | ノード種別 | 動作するコンポーネント |パッケージ導入方式|
| --- | --- | --- | --- |
| `logging_backend` | ログ集約ノード | Fleet Server, Logstash, Elasticsearch, Kibana | コンテナイメージを展開 |
| `logging_collector` | ログ収集ノード | Elastic Agent | Elastic Agent公式配布物を使用してサービスとして導入 |

将来的なOS版数変更の影響を軽減するため, Kubernetes クラスタ外の運用管理ノードとしてログ集約ノードを用意することを想定し, ログ集約ノードに導入するコンポーネントは, コンテナイメージを用いてコンポーネントを導入する方針としています。

本playbookでは, Kubernetes クラスタ上のPodのログなどを収集することを想定しています。Kubernetes クラスタの動作に必要となるcontainerdなどのContainer Runtime Interface (CRI)とElasticsearch 関連コンポーネントを動作させるために用いるDockerなどのCRIとを混在させることにより発生するトラブルを防止する観点から, ログ収集ノードにはElastic Agentだけを導入し, 収集設定はFleet BootstrapがFleet Serverから配布可能なPackage Policyとして管理します。

### Elasticsearch 関連ロールの構成

Elasticsearchの導入に関連するロールは以下の通りです:

|ロール名|ロール定義ディレクトリ|処理内容|
| ---| --- | --- |
| Elasticsearch | roles/elasticsearch | Elasticsearch コンテナの設定生成, 起動, 起動確認を行うロールです。 |
| Kibana | roles/kibana | Kibana コンテナの設定生成, 起動, 起動確認を行うロールです。 |
| Logstash | roles/logstash | Logstash コンテナの pipeline 設定生成, 起動, 起動確認を行うロールです。 |
| Fleet Server | roles/fleet-server | Elastic Agent コンテナを Fleet Server モードで起動し, 管理通信の受け口を提供するロールです。 |
| Fleet Bootstrap | roles/fleet-bootstrap | Fleet Serverの初期化設定を行うロールです。Fleet Output, Elastic Agent ポリシー, Package Policy, Enrollment Token の生成又は再利用, Enrollment Token共有ファイルへの保存と, 接続先疎通確認を担います。 |
| Elastic Agent | roles/elastic-agent | Fleet BootstrapがEnrollment Token共有ファイルへ保存したEnrollment Tokenを読み込み, Elastic Agent本体の導入とFleet Serverへの登録を行うロールです。 |

### 展開されるコンテナの仕様

#### 公開ポート

| ホスト側待受 | コンテナ側待受 | プロトコル | 用途 |
| --- | --- | --- | --- |
| `{{ elastic_search_http_host }}:{{ elastic_search_http_port }}` (既定: `0.0.0.0:9200`) | `{{ elastic_search_http_port }}` (既定: `9200`) | TCP | Elasticsearch の HTTP エンドポイントを対象ホスト側から利用可能にします。 |

`templates/docker-compose.yml.j2` では, Elasticsearch コンテナの HTTP ポートを次の形式で公開します:

- `{{ elastic_search_http_host }}:{{ elastic_search_http_port }}:{{ elastic_search_http_port }}` (既定: `0.0.0.0:9200:9200`)

既定値は, 対象ホスト上のすべてのネットワークインターフェースで TCPプロトコルのポート番号9200番 を待受し, 同じポート番号で Elasticsearch コンテナへ転送する設定であることを意味します。

##### 公開ポートに関する補足事項

- 本ロールは, 公開ポート設定にもとづいて Elasticsearch の HTTP エンドポイントに対して対象ホスト側からアクセス可能になることを待ち合わせることで, 正常にポート公開がなされていることを確認, 保証します。
- 本ロールは, 起動後に公開ポート経由で接続確認を実施し, Elasticsearch のクラスタ状態が 検索や保存の基本機能は利用できるが一部の予備コピーが未配置である状態 ( Elasticsearchの用語でいう `yellow` 状態 ), または, 予備コピーを含む全データ配置が完了している状態 ( Elasticsearchの用語でいう `green` 状態 ) になるまで待機することで, Elasticsearchが利用可能な状態になることを保証します。
- 規定値を使用する場合は `0.0.0.0:9200` で待受します。外部からの接続元を限定したい場合は, `elastic_search_http_host` に `127.0.0.1` などの値を設定することで, 待受先アドレスを制限することも可能です。

#### ファイルバインド

`templates/docker-compose.yml.j2` では, ホスト側のファイルやディレクトリを以下のようにコンテナ内から使用可能とするように設定します:

| ホスト側 | コンテナ側 | モード | 用途 |
| --- | --- | --- | --- |
| `{{ elastic_search_config_file }}` (既定: `/srv/elastic-search/config/elasticsearch.yml`) | `/usr/share/elasticsearch/config/elasticsearch.yml` | `ro` | ホスト側のElasticsearch の設定ファイルをコンテナ内から参照可能します。コンテナ内から当該のファイルを破壊不可能なように読み取り専用でコンテナ側に公開します。 |
| `{{ elastic_search_data_dir }}` (既定: `/srv/elastic-search/data`) | `/usr/share/elasticsearch/data` | `rw` | インデックスを永続化し, コンテナの再作成時でも当該のインデックスデータを継続的に利用可能にします。 |
| `{{ elastic_search_logs_dir }}` (既定: `/srv/elastic-search/logs`) | `/usr/share/elasticsearch/logs` | `rw` | Elasticsearch のログを永続化し, コンテナの動作が停止した場合でもホスト上からログ情報を参照可能にします。 |
| `{{ elastic_search_snapshot_repo_path_host }}` (既定: `/srv/elastic-search/backup/snapshot-repo`) | `{{ elastic_search_snapshot_repo_path_container }}` (既定: `/usr/share/elasticsearch/snapshot-repo`) | `rw` | Snapshot Repository の保存先をホスト側へ永続化し, バックアップ/リストア処理で参照可能にします。 |

既定値は, 設定ファイルをホスト上の `/srv/elastic-search/config/elasticsearch.yml` から読み込み, インデックスをホスト上の `/srv/elastic-search/data`, ログをホスト上の `/srv/elastic-search/logs` に保存する設定です。

##### ファイルバインドに関する補足事項

- 本ロールは, 設定ファイル, データ, ログの保存先をホスト側へ分離し, コンテナ再作成後もデータを保持することを保証します。
- 本ロールは, 設定ファイルを読み取り専用でコンテナへ渡し, コンテナ内の処理によって設定ファイルが書き換わらないことを保証します。
- 本ロールは, 規定値を使用する場合に `/srv/elastic-search` 配下へ設定, データ, ログを集約し, 配置先の一貫性を維持することを保証します。

#### ネットワーク定義

`templates/docker-compose.yml.j2` では, `elastic_backend` ネットワークを定義し, `external: true` で既存ネットワークを利用します。実体として参照するネットワーク名は `{{ elastic_search_network_name }}` (既定: `elastic-backend`) です。

既定値は, docker-network-elastic-stackロールが作成する`elastic-backend`外部ネットワークへElasticsearchコンテナを参加させ, 同一のホスト側ネットワークを通して関連コンテナと通信する設定です。本ロールは`elastic-backend`の存在を確認し, 存在しない場合は処理を停止します。

### 本ロールで実施する主な処理

本ロールでは, 次の処理を実施します。

1. `docker compose` が利用可能であることを確認します。
2. 本 playbook で導入するディレクトリを作成します。
3. Elasticsearch の設定ファイルと Docker Compose 定義ファイルを生成します。
4. Elasticsearch コンテナを起動します。
5. 起動後にポート待機と応答確認を行います。

## 実行方法

### Makefile ターゲットを使用する場合

制御ホストで次のコマンドを実行します。

```bash
make run_logging_backend
```

このコマンドは, `logging_backend` グループに対して本 playbook で導入する Elasticsearch, Kibana, Logstash を実行します。

### ansible-playbookコマンドを使用する場合

制御ホストで次のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts logging-backend.yml
```

このコマンドは, `logging_backend` グループに対して本 playbook で導入する Elasticsearch, Kibana, Logstash を実行します。

## 主要変数

### 各ロール固有の利用者入力値

#### 必須入力値

本ロール固有の必須入力値はありません。Elasticsearchのセキュリティ機能を有効にする場合は, 運用環境用の`elastic_search_bootstrap_password`を明示設定します。

#### 任意入力値

##### 基本設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `elastic_search_enabled` | Elasticsearch ロールの有効化フラグ。 | `true` | `true` |
| `elastic_search_vm_max_map_count` | Elasticsearch の起動前提として設定する `vm.max_map_count` の値。 | `262144` | `262144` |

`elastic_search_vm_max_map_count`の値は, Elasticsearch Guideの[Maximum map count check](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/bootstrap-checks-max-map-count.html)の指定値を元に設定しています。

##### 接続設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `elastic_search_cluster_name` | Elasticsearch のクラスタ名。 | `shared-logs` | `shared-logs` |
| `elastic_search_node_name` | Elasticsearch ノード名。IPアドレス, または, ホスト名 (FQDN形式) で記載する。 | `{{ inventory_hostname }}` | `elasticsearch01.local` |
| `elastic_search_discovery_type` | 単一ノード起動時の探索方式。 | `single-node` | `single-node` |
| `elastic_search_http_host` | Elasticsearch の HTTP 待受アドレス。 | `0.0.0.0` | `0.0.0.0` |
| `elastic_search_http_port` | Elasticsearch の HTTP 待受ポート。 | `9200` | `9200` |
| `elastic_search_api_endpoint_url_explicit` | ランタイムエンドポイントの明示指定値。未指定時は `logging_backend_resolved_host` と `elastic_search_http_port` から組み立てる。 | 空文字列 | `https://elastic-backend01.example.org:9200` |
| `elastic_search_tls_mode` | ランタイムエンドポイントの URL スキームが `https` の場合に参照する TLS 検証モードです。ランタイムエンドポイントの URL スキームが `http` の場合は, ロールの実行時に `off` として扱います。指定可能な値については, [共有設定値に関する補足説明](#共有設定値に関する補足説明) の `logging_backend_default_tls_mode` 変数の説明を参照ください。 | `logging_backend_default_tls_mode` の指定値。`logging_backend_default_tls_mode` が未設定の場合は `none` を使用します。 | `none` |
| `elastic_search_java_opts` | Elasticsearch の Java オプション。 | `-Xms512m -Xmx512m` | `-Xms512m -Xmx512m` |

##### Elasticsearchのセキュリティ機能関連設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `elastic_search_security_enabled` | Elasticsearchのセキュリティ機能を有効化するフラグ。 | `true` | `false` |
| `elastic_search_transport_ssl_enabled` | Elasticsearch の transport 層で TLS を有効化するフラグ。 | `false` | `false` |
| `elastic_search_security_username` | Elasticsearchのセキュリティ機能が有効な場合に使用する認証ユーザ名。 | `elastic` | `elastic` |
| `elastic_search_bootstrap_password` | Elasticsearchのセキュリティ機能が有効な場合に使用する初期パスワード。 | `elastic` | `DUMMY_ELASTIC_PASSWORD` |

##### HTTPS 証明書関連設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `elastic_search_http_ssl_certificate_host_path` | Elasticsearch の HTTP層 TLS サーバ証明書ファイルのホスト側パス。未指定時は共通変数を使用する。 | `""` | `/srv/elastic-certs/elasticsearch/tls.crt` |
| `elastic_search_http_ssl_key_host_path` | Elasticsearch の HTTP層 TLS サーバ秘密鍵ファイルのホスト側パス。未指定時は共通変数を使用する。 | `""` | `/srv/elastic-certs/elasticsearch/tls.key` |

ランタイムエンドポイントの URL スキームが `https` の場合は, `elastic_search_http_ssl_certificate_host_path` と `elastic_search_http_ssl_key_host_path` を優先し, どちらかが未指定であれば `vars/all-config.yml` 側の共通変数を使用します。

### `vars/all-config.yml`に設定するElastic Stack間共有設定値

本節は, Elastic Stack関連ロールで共有する利用者入力値の正本です。共通既定値を使用する変数は`vars/all-config.yml`への記載を省略し, 既定値を変更する場合だけ`vars/all-config.yml`へ設定します。`host_vars`への重複定義は行いません。

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `logging_backend_elastic_stack_version` | Elasticsearch, Kibana, Logstash, Fleet Server及びElastic Agentで共通利用する版数。 | `8.19.19` | `8.19.19` |
| `logging_backend_network_name` | Elastic Stack関連コンテナが共有するDockerブリッジネットワーク名。 | `elastic-backend` | `elastic-backend` |
| `logging_backend_network_ipv4_subnet` | 共有Dockerブリッジネットワークへ割り当てるIPv4 CIDR。 | `172.18.0.0/16` | `172.18.0.0/16` |
| `logging_backend_network_ipv6_subnet` | 共有Dockerブリッジネットワークへ割り当てるIPv6 CIDR。 | `fd00:172:18::/64` | `fd00:172:18::/64` |
| `logging_backend_host` | Elasticsearch, Kibana, Logstash, Fleet Server, Fleet Bootstrap, Elastic Agent 関連ロールが参照する共通の接続先ホスト名。 | 未定義 | `elastic-backend01.example.org` |
| `logging_backend_default_scheme` | ランタイムエンドポイントの明示指定がない場合に使用する既定の URL スキーム。 | `https` | `https` |
| `logging_backend_default_tls_mode` | `https` 利用時に各ロールの TLS 検証モード既定値として使用する値。 | `none` | `full` |
| `logging_backend_disallow_mixed_scheme` | Fleet Bootstrap で複数エンドポイントを扱う際に URL スキーム混在を禁止するフラグ。 | `true` | `true` |
| `logging_backend_tls_certificate_host_path` | logging backend 関連ロールで共通利用する HTTPS サーバ証明書ファイルのホスト側パス。 | `""` | `/srv/elastic-certs/backend/tls.crt` |
| `logging_backend_tls_key_host_path` | logging backend 関連ロールで共通利用する HTTPS サーバ秘密鍵ファイルのホスト側パス。 | `""` | `/srv/elastic-certs/backend/tls.key` |
| `logging_verify_external_enabled` | 外部ホストからの疎通確認を共通で有効化するフラグ。 | `false` | `true` |
| `logging_verify_external_delegate_to` | 外部ホストからの疎通確認を実行する接続元ホスト名。 | `localhost` | `bastion01` |

#### 共有設定値に関する補足説明

`logging_backend_default_scheme` は, `elastic_search_api_endpoint_url_explicit` のような個別のランタイムエンドポイント明示指定がない場合に使用する既定の URL スキームです。

`logging_backend_default_tls_mode` は, `https` を使用する場合に各ロールの TLS 検証モード既定値として使用します。指定可能な値と意味は次のとおりです。

- `off`: URL スキームが `http` の場合に使用します。TLS を使用しません。
- `none`: URL スキームが `https` の場合に使用します。証明書検証を実施しません。
- `full`: URL スキームが `https` の場合に使用します。証明書検証を実施します。

Elasticsearch ロールでは, `elastic_search_tls_mode` が未設定の場合にこの値を継承します。

`logging_backend_tls_certificate_host_path` と `logging_backend_tls_key_host_path` は, logging backend 関連ロール全体で共通利用する証明書と秘密鍵のパスです。Elasticsearch ロールでは, `elastic_search_http_ssl_certificate_host_path` 又は `elastic_search_http_ssl_key_host_path` が定義されている場合はそちらを優先し, 未定義の場合に共通変数を使用します。

`logging_verify_external_enabled` と `logging_verify_external_delegate_to` は, 対象ホスト上での疎通確認に加えて, 外部ホストからの疎通確認の実施有無と, その接続元ホストを制御する共通変数です。

`vars/all-config.yml` の設定例を以下に示します。

```yaml
1: logging_backend_host: "elastic-backend01.example.org"
2: logging_backend_default_scheme: "https"
3: logging_backend_default_tls_mode: "none"
4: logging_backend_tls_certificate_host_path: "/srv/elastic-certs/backend/tls.crt"
5: logging_backend_tls_key_host_path: "/srv/elastic-certs/backend/tls.key"
6: logging_verify_external_enabled: true
7: logging_verify_external_delegate_to: "bastion01"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `logging_backend_host: "elastic-backend01.example.org"` | Elasticsearch, Logstash, Kibana, Fleet Server, Fleet Bootstrap, Elastic Agent 関連ロールが参照する共通の接続先ホストを `elastic-backend01.example.org` に設定します。 | 未設定又は空文字列の場合は `inventory/hosts` の `logging_backend` グループ先頭ホストへフォールバックするため, inventory の並び順変更で接続先が変わる問題を防止するためです。 |
| 2-3 | `logging_backend_default_scheme: "https"`, `logging_backend_default_tls_mode: "none"` | 明示 URL 未指定時の既定接続方式を HTTPS とし, 証明書検証をスキップする既定値を各ロールへ適用します。 | スキームと TLS 検証モードの既定値が不明確な場合, ロールごとに異なる既定動作となり, 接続不整合が発生するためです。 |
| 4-5 | `logging_backend_tls_certificate_host_path: "/srv/elastic-certs/backend/tls.crt"`, `logging_backend_tls_key_host_path: "/srv/elastic-certs/backend/tls.key"` | logging backend 関連ロール全体で共通利用する HTTPS サーバ証明書と秘密鍵を指定します。 | 共通証明書を設定しないまま HTTPS を有効化すると, 各ロールで証明書パス未設定エラーや起動失敗が発生するためです。 |
| 6-7 | `logging_verify_external_enabled: true`, `logging_verify_external_delegate_to: "bastion01"` | 外部ホスト `bastion01` からの疎通確認を有効化します。 | 対象ホスト上での疎通確認だけでは外部経路の誤設定を検出できないためです。 |

#### `logging_backend_host` の設定値に関する留意事項

`logging_backend_host` が未定義又は空文字列の場合は, `inventory/hosts` の `logging_backend` グループに記載された先頭ホストを送信先候補として使用します。
このとき, 先頭ホストに接続先アドレス(IPアドレス又はFQDN)を `ansible_host` パラメタによって明示されている場合はその値を使用し, 明示されていない場合は先頭ホスト名を使用します。

Elasticsearch, Logstash, Kibana, Fleet Server を導入するホストでは, `inventory/hosts` の先頭順依存を避けるため, `vars/all-config.yml` で `logging_backend_host` を明示設定することを推奨します。

`logging_backend_host` には, IPアドレス又はFQDNを指定します。`*.local` などの multicast DNS 名は, 環境により名前解決が不安定になるため指定しないことを推奨します。

### コンテナ起動確認関連設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `elastic_search_wait_host` | 起動確認で待機する接続先ホスト。 | `127.0.0.1` | `127.0.0.1` |
| `elastic_search_wait_delegate_to` | 起動確認を実行する接続元ホスト。 | `{{ inventory_hostname }}` | `{{ inventory_hostname }}` |
| `elastic_search_wait_timeout` | 起動確認のタイムアウト時間。 | `120` | `120` |
| `elastic_search_wait_delay` | 起動確認の開始遅延時間。 | `5` | `5` |
| `elastic_search_wait_sleep` | 起動確認の待機間隔。 | `2` | `2` |
| `elastic_search_wait_retries` | 起動確認の再試行回数。 | `60` | `60` |

### バックアップ/リストア関連設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `elastic_search_enable_backup_script` | バックアップ/リストア関連スクリプトの生成有無を制御するフラグ。 | `false` | `true` |
| `elastic_search_snapshot_repository` | Elasticsearch の snapshot repository 名。 | `elastic-backup-repo` | `elastic-backup-repo` |
| `elastic_search_backup_name_prefix` | 生成する snapshot 名の接頭辞。 | `elastic-snapshot` | `elastic-snapshot` |
| `elastic_search_backup_retention` | 保持する snapshot 世代数。 | `7` | `14` |
| `elastic_search_daily_backup_extra_args` | 日次バックアップラッパーからバックアップ実行へ引き渡す追加引数。 | `""` | `--retention 14` |

### 変数設定例

#### host_vars の設定例

ホスト固有に変える値を `host_vars/elastic-search01.local.yml` に記載します。
`logging_backend_host` は共通変数であるため, この例には含めず `vars/all-config.yml` に記載します。

```yaml
1: elastic_search_enabled: true
2: elastic_search_node_name: "elastic-search01.local"
3: elastic_search_wait_delegate_to: "{{ inventory_hostname }}"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `elastic_search_enabled: true` | Elasticsearch ロールを有効化し, ディレクトリ作成, 設定生成, コンテナ起動, 起動確認を実行します。 | `false` の場合は Elasticsearch ロールの処理が実行されず, 期待した導入結果を得られないためです。 |
| 2 | `elastic_search_node_name: "elastic-search01.local"` | Elasticsearch ノード名を `elastic-search01.local` として設定し, Elasticsearch のクラスタ状態確認で識別可能にします。 | ノード名が未設定又は誤設定の場合, 運用時の識別性が低下し, 障害切り分けが難しくなるためです。 |
| 3 | `elastic_search_wait_delegate_to: "{{ inventory_hostname }}"` | 起動確認タスクを対象ホスト自身から実行します。 | 到達不能な接続元を設定した場合, 起動済みでも待受確認に失敗し, ロール実行が異常終了するためです。 |

この例では, ノード名を対象ホスト名に合わせ, 起動確認の接続元を対象ホスト自身にします。

#### vars/all-config.yml の設定例

全ホスト共通の値を `vars/all-config.yml` に記載します。
`logging_backend_*` は `host_vars` に重複定義せず, この節の例のように `vars/all-config.yml` のみに記載します。

```yaml
1: elastic_search_enabled: true
2: elastic_search_cluster_name: "shared-logs"
3: elastic_search_http_host: "0.0.0.0"
4: elastic_search_http_port: 9200
5: elastic_search_java_opts: "-Xms512m -Xmx512m"
6: elastic_search_wait_host: "127.0.0.1"
7: elastic_search_wait_timeout: 120
8: elastic_search_wait_delay: 5
9: elastic_search_wait_sleep: 2
10: elastic_search_wait_retries: 60
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `elastic_search_enabled: true` | Elasticsearch ロールを有効化し, 共通設定にもとづく導入処理を実行します。 | `false` の場合は共通設定が存在しても導入処理が実行されず, 設定の反映漏れが発生するためです。 |
| 2 | `elastic_search_cluster_name: "shared-logs"` | Elasticsearch のクラスタ名を `shared-logs` に設定し, 関連コンポーネントとの前提を一致させます。 | Elasticsearch のクラスタ名不一致により, 監視や運用手順で対象を識別できなくなるためです。 |
| 3-4 | `elastic_search_http_host: "0.0.0.0"`, `elastic_search_http_port: 9200` | Elasticsearch の HTTP 待受を `0.0.0.0:9200` に設定し, 対象ホストから利用可能にします。 | 未設定又は誤設定の場合, 待受先アドレスやポートが期待値と一致せず, 接続確認が失敗するためです。 |
| 5 | `elastic_search_java_opts: "-Xms512m -Xmx512m"` | JVM の初期ヒープ, 最大ヒープをともに `512m` に設定します。 | 過小設定では性能低下, 過大設定ではメモリ圧迫を招き, 安定運用を阻害するためです。 |
| 6-10 | `elastic_search_wait_host: "127.0.0.1"`, `elastic_search_wait_timeout: 120`, `elastic_search_wait_delay: 5`, `elastic_search_wait_sleep: 2`, `elastic_search_wait_retries: 60` | 起動確認の接続先と再試行条件を定義し, 起動直後の待受未完了を吸収して到達性を検証します。 | これらが未設定又は不適切な場合, 起動直後の一時的な応答遅延を異常と誤判定し, ロール実行が失敗するためです。 |

この例では, 本 playbook で導入する側の共通値を一箇所へ集約します。

### ログ対象を追加する手順

ログ対象を追加する際に次の順で更新します。

1. Elastic Agent ポリシーの入力対象を追加します。
2. 必要なら Elastic Agent ポリシーのメタデータ設定を追加します。
3. Logstash の受け口と振り分け条件を更新します。
4. 必要なら Elastic Agent ポリシーの収集周期や対象を調整します。
5. `ansible-lint` と起動確認を通す。

## バックアップ/リストア運用

本節では, 運用者視点で本ロールが生成するバックアップ/リストア用スクリプトの使い方を示します。

### 導入されるスクリプト仕様

本ロールで `elastic_search_enable_backup_script: true` を設定した場合は, 次のスクリプトを導入します。

導入する Python スクリプトは標準ライブラリのみを使用するため, 追加の pip パッケージ導入は不要です。

| スクリプト | 配置先(既定) | 仕様 |
| --- | --- | --- |
| backup-elasticsearch-data.py | /srv/elastic-search/scripts/backup-elasticsearch-data.py | Snapshot Repository の登録確認, snapshot 作成, 世代整理を実装する Python 本体。 |
| restore-elasticsearch-data.py | /srv/elastic-search/scripts/restore-elasticsearch-data.py | 指定した snapshot からの復元を実装する Python 本体。必要に応じて既存 index を削除する。 |
| backup-elasticsearch-data.sh | /srv/elastic-search/scripts/backup-elasticsearch-data.sh | バックアップ Python 本体を呼び出す実行ラッパー。 |
| restore-elasticsearch-data.sh | /srv/elastic-search/scripts/restore-elasticsearch-data.sh | リストア Python 本体を呼び出す実行ラッパー。 |
| daily-backup-elasticsearch.sh | /srv/elastic-search/scripts/daily-backup-elasticsearch.sh | 日次実行向けラッパー。cron から呼び出す用途を想定する。 |

### バックアップ実行スクリプトのコマンドラインオプション

バックアップ実行スクリプト(backup-elasticsearch-data.sh)のコマンドラインオプションは, 以下の通りです。

| オプション | 規定値 | 意味 | 指定例 |
| --- | --- | --- | --- |
| --endpoint | `http://127.0.0.1:9200` | 接続先 Elasticsearch URL を指定します。 | --endpoint http://127.0.0.1:9200 |
| --repository | `elastic-backup-repo` | Snapshot Repository 名を指定します。 | --repository elastic-backup-repo |
| --repository-path | `/usr/share/elasticsearch/snapshot-repo` | Snapshot Repository のコンテナ側パスを指定します。 | --repository-path /usr/share/elasticsearch/snapshot-repo |
| --snapshot-prefix | `elastic-snapshot` | 生成する snapshot 名の接頭辞を指定します。 | --snapshot-prefix elastic-snapshot |
| --retention | `7` | 保持世代数を指定します。 | --retention 14 |
| --timeout-seconds | `120` | HTTP タイムアウト秒数を指定します。 | --timeout-seconds 180 |
| --verbose | `false` | 詳細ログを有効化します。指定時に `true` 扱いとなります。 | --verbose |

### リストア実行スクリプトのコマンドラインオプション

リストア実行スクリプト(restore-elasticsearch-data.sh)のコマンドラインオプションは, 以下の通りです。

| オプション | 規定値 | 意味 | 指定例 |
| --- | --- | --- | --- |
| --endpoint | `http://127.0.0.1:9200` | 接続先 Elasticsearch URL を指定します。 | --endpoint http://127.0.0.1:9200 |
| --repository | `elastic-backup-repo` | 復元元の Snapshot Repository 名を指定します。 | --repository elastic-backup-repo |
| --snapshot-name | なし(必須) | 復元対象の snapshot 名を指定します。 | --snapshot-name elastic-snapshot-20260803-030000 |
| --timeout-seconds | `120` | HTTP タイムアウト秒数を指定します。 | --timeout-seconds 180 |
| --delete-existing | `false` | 復元前に既存 index を削除します。指定時に `true` 扱いとなります。 | --delete-existing |
| --verbose | `false` | 詳細ログを有効化します。指定時に `true` 扱いとなります。 | --verbose |

### バックアップ実行手順

運用者は次のコマンドを対象ホストで実行します。

```bash
/srv/elastic-search/scripts/backup-elasticsearch-data.sh
```

このコマンドは, Snapshot Repository の登録確認, snapshot 作成, 保持世代を超えた snapshot の削除を順に実行します。

### リストア実行手順

運用者は復元対象の snapshot 名を指定して, 次のコマンドを対象ホストで実行します。

```bash
/srv/elastic-search/scripts/restore-elasticsearch-data.sh --snapshot-name elastic-snapshot-20260803-030000
```

既存 index を削除してから復元する場合は, `--delete-existing` を追加します。

```bash
/srv/elastic-search/scripts/restore-elasticsearch-data.sh --snapshot-name elastic-snapshot-20260803-030000 --delete-existing
```

### 定期バックアップ実行手順

日次実行用ラッパースクリプトは次のコマンドです。

```bash
/srv/elastic-search/scripts/daily-backup-elasticsearch.sh
```

本ロールは crontab エントリを自動作成せず, 運用者責任で登録する方針です。定期実行する場合は, 対象ホスト上で crontab へ手動登録します。`crontab -e` コマンドを実行し, 次のようなエントリを登録します。本例では, 午前3時にバックアップ処理を実施します:

```text
0 3 * * * /srv/elastic-search/scripts/daily-backup-elasticsearch.sh
```

登録後は, 次のコマンドで反映状態を確認します。

```bash
crontab -l
```

実行例:
```bash
$ crontab -l
# Edit this file to introduce tasks to be run by cron.
#
# Each task to run has to be defined through a single line
# indicating with different fields when the task will be run
# and what command to run for the task
#
# To define the time you can provide concrete values for
# minute (m), hour (h), day of month (dom), month (mon),
# and day of week (dow) or use '*' in these fields (for 'any').
#
# Notice that tasks will be started based on the cron's system
# daemon's notion of time and timezones.
#
# Output of the crontab jobs (including errors) is sent through
# email to the user the crontab file belongs to (unless redirected).
#
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
#
# For more information see the manual pages of crontab(5) and cron(8)
#
# m h  dom mon dow   command
0 3 * * * /srv/elastic-search/scripts/daily-backup-elasticsearch.sh
```

## テンプレートと生成ファイル

| テンプレート | 生成先 (括弧内は規定) | 用途 | 主な内容 |
| --- | --- | --- | --- |
| `templates/elasticsearch.yml.j2` | `{{ elastic_search_config_file }}` (規定: `/srv/elastic-search/config/elasticsearch.yml`) | Elasticsearch の設定ファイルを生成します。 | Elasticsearch のクラスタ名, ノード名, 待受アドレス, 待受ポート, 探索方式, セキュリティ設定。 |
| `templates/docker-compose.yml.j2` | `{{ elastic_search_compose_file }}` (規定: `/srv/elastic-search/docker-compose.yml`) | Elasticsearch の Docker Compose 定義ファイルを生成します。 | コンテナイメージ, コンテナ名, ボリューム, ポート公開, 起動確認, ネットワーク。 |
| `templates/90-elasticsearch.conf.j2` | `{{ elastic_search_sysctl_dropin_file }}` (規定: `/etc/sysctl.d/90-elasticsearch.conf`) | `vm.max_map_count` を設定する sysctl ドロップインファイルを生成します。 | `vm.max_map_count={{ elastic_search_vm_max_map_count }}` の設定行。 |
| `templates/backup-elasticsearch-data.py.j2` | `{{ elastic_search_backup_python_script_path }}` (規定: `/srv/elastic-search/scripts/backup-elasticsearch-data.py`) | Snapshot API を使ってバックアップと世代整理を行う Python スクリプトを生成します。 | repository 登録, snapshot 作成, 保持世代を超えた snapshot 削除。 |
| `templates/restore-elasticsearch-data.py.j2` | `{{ elastic_search_restore_python_script_path }}` (規定: `/srv/elastic-search/scripts/restore-elasticsearch-data.py`) | Snapshot API を使ってリストアを行う Python スクリプトを生成します。 | snapshot 指定リストア, 既存 index 削除オプション。 |
| `templates/backup-elasticsearch-data.sh.j2` | `{{ elastic_search_backup_script_path }}` (規定: `/srv/elastic-search/scripts/backup-elasticsearch-data.sh`) | バックアップ Python 実装を呼び出すラッパースクリプトを生成します。 | Python 実装への引数透過。 |
| `templates/restore-elasticsearch-data.sh.j2` | `{{ elastic_search_restore_script_path }}` (規定: `/srv/elastic-search/scripts/restore-elasticsearch-data.sh`) | リストア Python 実装を呼び出すラッパースクリプトを生成します。 | Python 実装への引数透過。 |
| `templates/daily-backup-elasticsearch.sh.j2` | `{{ elastic_search_daily_backup_script_path }}` (規定: `/srv/elastic-search/scripts/daily-backup-elasticsearch.sh`) | 日次バックアップ実行用ラッパースクリプトを生成します。 | cron からバックアップ実行ラッパーを呼び出す。 |

`elasticsearch.yml.j2` は, Elasticsearch コンテナ内の設定用ファイルを展開します。`docker-compose.yml.j2` は, コンテナイメージ, コンテナ名, ボリューム, ポート公開, ネットワークの設定ファイルを展開します。`backup-elasticsearch-data.py.j2` と `restore-elasticsearch-data.py.j2` は Snapshot API を呼び出す実装本体であり, `.sh.j2` は運用者が扱う呼び出しインターフェースです。

## 実行フロー

1. [tasks/load-params.yml](tasks/load-params.yml) で OS 別パラメータと共通変数を読み込みます。
2. [tasks/resolve-runtime-flags.yml](tasks/resolve-runtime-flags.yml) で 指定されたエンドポイント URL と TLS モードから, ランタイムエンドポイントの URL スキーム, TLS 検証モード, HTTP層 TLS 有効化フラグを確定します。
3. [tasks/resolve-runtime-vars.yml](tasks/resolve-runtime-vars.yml) で ランタイムエンドポイント, 疎通確認に使用する URL, 共通証明書変数と Elasticsearch 個別証明書変数を加味した証明書パスを確定します。
4. [tasks/validate.yml](tasks/validate.yml) で導入前提, パス, コンテナイメージ名, ポート, OS 条件に加え, `https` 利用時の証明書パスと実ファイル存在を確認します。
5. [tasks/package.yml](tasks/package.yml) で Docker Compose が利用可能であることを確認します。
6. [tasks/directory.yml](tasks/directory.yml) で compose 用ディレクトリと設定, データ, ログの配置先を作成します。
7. [tasks/user_group.yml](tasks/user_group.yml) で実行ユーザとグループを作成し, ディレクトリ所有権を調整します。
8. [tasks/config.yml](tasks/config.yml) で [templates/elasticsearch.yml.j2](templates/elasticsearch.yml.j2) と [templates/docker-compose.yml.j2](templates/docker-compose.yml.j2) を配置します。`elastic_search_enable_backup_script` が `true` の場合は, [templates/backup-elasticsearch-data.py.j2](templates/backup-elasticsearch-data.py.j2), [templates/restore-elasticsearch-data.py.j2](templates/restore-elasticsearch-data.py.j2), [templates/backup-elasticsearch-data.sh.j2](templates/backup-elasticsearch-data.sh.j2), [templates/restore-elasticsearch-data.sh.j2](templates/restore-elasticsearch-data.sh.j2), [templates/daily-backup-elasticsearch.sh.j2](templates/daily-backup-elasticsearch.sh.j2) も配置します。設定ファイルまたは Docker Compose 定義ファイルの更新時は `elasticsearch_restart_service` を通知し, [handlers/main.yml](handlers/main.yml) から読み込む [handlers/restart-service.yml](handlers/restart-service.yml) でコンテナを再作成します。
9. [tasks/service.yml](tasks/service.yml) でdocker-network-elastic-stackロールが作成したbackend専用ネットワークの存在を確認し, `docker compose up -d --remove-orphans`によりElasticsearchコンテナを起動します。
10. [tasks/verify.yml](tasks/verify.yml) で対象ホスト上での疎通確認として `wait_for` によるポート待機と `uri` による `/_cluster/health` 応答確認を実施し, Elasticsearch のクラスタ状態が `yellow` または `green` であることを検証します。`logging_verify_external_enabled: true` の場合は, 同じランタイムエンドポイントに対して外部ホストからの疎通確認も実施します。

## 検証ポイント

### 検証の前提条件

検証を始める前に, 次の条件が満たされていることを確認します。

- 対象ホストで Docker と Docker Compose が利用できること。
- `elastic_search_http_port` に設定したポートが他のサービスで使われていないこと。
- `elastic_search_compose_dir` 配下を作成できること。
- `logging_backend` グループに対象ホストが登録されていること。

### 検証環境の設定

本節では, 検証用の設定内容について説明します。

**検証用の host_vars**:

```yaml
1: elastic_search_http_host: "0.0.0.0"
2: elastic_search_http_port: 9200
3: elastic_search_wait_host: "127.0.0.1"
4: elastic_search_wait_delegate_to: "{{ inventory_hostname }}"
5: elastic_search_security_username: "elastic"
6: elastic_search_bootstrap_password: "DUMMY_ELASTIC_PASSWORD"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1-2 | `elastic_search_http_host: "0.0.0.0"`, `elastic_search_http_port: 9200` | `0.0.0.0:9200` で待受し, HTTP 接続確認を実行可能にします。 | 待受先アドレス又はポートが不一致の場合, 検証コマンドが接続不能となり, 導入結果を判定できないためです。 |
| 3-4 | `elastic_search_wait_host: "127.0.0.1"`, `elastic_search_wait_delegate_to: "{{ inventory_hostname }}"` | 対象ホスト自身から `127.0.0.1` 宛に起動確認を実行します。 | 接続元又は接続先が不適切な場合, Elasticsearch が起動済みでも待受確認が失敗し, 誤検知を招くためです。 |
| 5-6 | `elastic_search_security_username: "elastic"`, `elastic_search_bootstrap_password: "DUMMY_ELASTIC_PASSWORD"` | Elasticsearchのセキュリティ機能が有効な場合に, 検証コマンドとロール内の疎通確認で使用するBasic認証情報を設定します。 | 認証情報が未指定又は不一致の場合, Elasticsearchが稼働中でもHTTP応答が`401 Unauthorized`となり, クラスタ状態を確認できないためです。 |

この設定により, 本 playbook で導入する Elasticsearch が対象ホスト上で待受し, 自己確認が可能になります。

このロールでは, ランタイムエンドポイントを起点に, 対象ホスト上での疎通確認と外部ホストからの疎通確認を段階的に実施します。

### 検証コマンドと期待結果

#### 1. Elasticsearch 待受確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

以下の`DUMMY_ELASTIC_PASSWORD`を`elastic_search_bootstrap_password`の設定値に変更して実行してください。

```bash
curl -sS -u 'elastic:DUMMY_ELASTIC_PASSWORD' http://127.0.0.1:9200/
```

**期待される出力**:

```plaintext
{"name":"elasticsearch","cluster_name":"shared-logs",...}
```

**実行結果の例**:
```bash
$ curl -sS -u 'elastic:elastic' \
  'http://127.0.0.1:9200/_cluster/health?wait_for_status=yellow&timeout=60s'
{"cluster_name":"shared-logs","status":"yellow","timed_out":false,"number_of_nodes":1,"number_of_data_nodes":1,"active_primary_shards":56,"active_shards":56,"relocating_shards":0,"initializing_shards":0,"unassigned_shards":18,"unassigned_primary_shards":0,"delayed_unassigned_shards":0,"number_of_pending_tasks":0,"number_of_in_flight_fetch":0,"task_max_waiting_in_queue_millis":0,"active_shards_percent_as_number":75.67567567567568}
```

**確認ポイント**:

- Basic認証を使用して`http://127.0.0.1:9200/`へ接続できること。
- 応答本文に Elasticsearch の情報 (`name`, `cluster_name`) が含まれること。

#### 2. Elasticsearch のクラスタ状態確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

以下の`DUMMY_ELASTIC_PASSWORD`を`elastic_search_bootstrap_password`の設定値に変更して実行してください。

```bash
curl -sS -u 'elastic:DUMMY_ELASTIC_PASSWORD' "http://127.0.0.1:9200/_cluster/health?wait_for_status=yellow&timeout=60s"
```

**期待される出力**:

```plaintext
{"cluster_name":"shared-logs","status":"yellow",...}
```

**実行結果の例**:
```bash
$ curl -sS -u 'elastic:elastic' "http://127.0.0.1:9200/_cluster/health?wait_for_status=yellow&timeout=60s"
{"cluster_name":"shared-logs","status":"yellow","timed_out":false,"number_of_nodes":1,"number_of_data_nodes":1,"active_primary_shards":56,"active_shards":56,"relocating_shards":0,"initializing_shards":0,"unassigned_shards":18,"unassigned_primary_shards":0,"delayed_unassigned_shards":0,"number_of_pending_tasks":0,"number_of_in_flight_fetch":0,"task_max_waiting_in_queue_millis":0,"active_shards_percent_as_number":75.67567567567568}
```

**確認ポイント**:

- `status` が `yellow` 又は `green` であること。
- タイムアウト (`timeout=60s`) 以内に応答すること。

### 異常時の確認項目

#### 1. ポート競合の確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

```bash
ss -ltnp | grep ':9200 '
```

**実行結果の例**:
```bash
$ ss -ltnp | grep ':9200 '
LISTEN 0      4096         0.0.0.0:9200       0.0.0.0:*
```

**確認ポイント**:

- TCPプロトコルのポート番号9200番 が待受状態であること。
- Elasticsearch コンテナの公開ポートとして待受していること。
- 想定外の別プロセスが同一ポートを占有していないこと。

#### 2. ネットワーク作成状態の確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

```bash
docker network ls --format '{{.Name}}' | grep -x 'elastic-backend'
```

**実行結果の例**:
```bash
$ docker network ls --format '{{.Name}}' | grep -x 'elastic-backend'
elastic-backend
```

**確認ポイント**:

- `elastic_search_network_name` の設定先ネットワークが存在すること。
- 規定値を使用する場合は, `elastic-backend` が存在すること。

#### 3. 設定ファイル生成状態の確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

```bash
ls -l /srv/elastic-search/config/elasticsearch.yml
```

**実行結果の例**:
```bash
$ ls -l /srv/elastic-search/config/elasticsearch.yml
-rw-r--r--. 1 root root 2115 Aug  9 12:37 /srv/elastic-search/config/elasticsearch.yml
```

**確認ポイント**:

- `elastic_search_config_file` に設定したファイルが存在すること。
- 規定値を使用する場合の確認先は `/srv/elastic-search/config/elasticsearch.yml` であること。
- ファイルが 0 バイトではないこと。

#### 4. Docker Compose 定義ファイル生成状態の確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

```bash
ls -l /srv/elastic-search/docker-compose.yml
```

**実行結果の例**:
```bash
$ ls -l /srv/elastic-search/docker-compose.yml
-rw-r--r--. 1 root root 3154 Aug  9 12:37 /srv/elastic-search/docker-compose.yml
```

**確認ポイント**:

- `elastic_search_compose_file` に設定したファイルが存在すること。
- 規定値を使用する場合の確認先は `/srv/elastic-search/docker-compose.yml` であること。
- ファイルが 0 バイトではないこと。

#### 5. コンテナログのエラー確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

```bash
docker logs --tail 200 elasticsearch 2>&1 | grep -E '"log.level"[[:space:]]*:[[:space:]]*"(WARN|ERROR|FATAL)"'
```

**実行結果の例**:
```bash
$ docker logs --tail 200 elasticsearch 2>&1 | grep -E '"log.level"[[:space:]]*:[[:space:]]*"(WARN|ERROR|FATAL)"'
```


**確認ポイント**:

- 設定読込失敗, 起動失敗, ポート競合に関するエラーメッセージが出ていないこと。
- `elastic_search_container_name` を変更している場合は, 変更後のコンテナ名を指定して確認すること。

## トラブルシューティング

### 1. Elasticsearch が起動しない場合

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

```bash
docker ps -a --filter name=elasticsearch
docker logs --tail 200 elasticsearch 2>&1 | grep -E '"log.level"[[:space:]]*:[[:space:]]*"(WARN|ERROR|FATAL)"'
docker compose -f /srv/elastic-search/docker-compose.yml config
ls -ld /srv/elastic-search /srv/elastic-search/config /srv/elastic-search/data /srv/elastic-search/logs
```

**実行結果の例**:
```bash
$ docker ps -a --filter name=elasticsearch
CONTAINER ID   IMAGE                                                  COMMAND                  CREATED             STATUS                       PORTS                              NAMES
3810ef71ee6d   docker.elastic.co/elasticsearch/elasticsearch:8.19.19   "/bin/tini -- /usr/l…"   About an hour ago   Up About an hour (healthy)   0.0.0.0:9200->9200/tcp, 9300/tcp   elasticsearch
$ docker logs --tail 200 elasticsearch 2>&1 | grep -E '"log.level"[[:space:]]*:[[:space:]]*"(WARN|ERROR|FATAL)"'
$ docker compose -f /srv/elastic-search/docker-compose.yml config

name: elastic-search
services:
  elasticsearch:
    container_name: elasticsearch
    environment:
      ELASTIC_PASSWORD: elastic
      ES_JAVA_OPTS: -Xms512m -Xmx512m
      bootstrap.memory_lock: "true"
      cluster.name: shared-logs
      discovery.type: single-node
      node.name: observer01.example.org
    healthcheck:
      test:
        - CMD-SHELL
        - bash -c 'exec 3<>/dev/tcp/127.0.0.1/9200'
      timeout: 5s
      interval: 10s
      retries: 12
    image: docker.elastic.co/elasticsearch/elasticsearch:8.19.19
    networks:
      elastic_backend: null
    ports:
      - mode: ingress
        host_ip: 0.0.0.0
        target: 9200
        published: "9200"
        protocol: tcp
    restart: unless-stopped
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - type: bind
        source: /srv/elastic-search/config/elasticsearch.yml
        target: /usr/share/elasticsearch/config/elasticsearch.yml
        read_only: true
        bind: {}
      - type: bind
        source: /srv/elastic-search/data
        target: /usr/share/elasticsearch/data
        bind: {}
      - type: bind
        source: /srv/elastic-search/logs
        target: /usr/share/elasticsearch/logs
        bind: {}
      - type: bind
        source: /srv/elastic-search/backup/snapshot-repo
        target: /usr/share/elasticsearch/snapshot-repo
        bind: {}
networks:
  elastic_backend:
    name: elastic-backend
    external: true
$ ls -ld /srv/elastic-search /srv/elastic-search/config /srv/elastic-search/data /srv/elastic-search/logs
drwxr-xr-x. 6 root    root      84 Aug  9 12:37 /srv/elastic-search
drwxr-xr-x. 2 root    root      31 Aug  9 12:37 /srv/elastic-search/config
drwxr-xr-x. 5 ansible ansible   87 Aug  9 13:50 /srv/elastic-search/data
drwxr-xr-x. 2 ansible ansible 4096 Aug  9 12:42 /srv/elastic-search/logs
```

**確認ポイント**:

- コンテナ状態が `Up` であること。
- ログに設定読込失敗, イメージ取得失敗, 起動失敗が出ていないこと。
- Compose 定義の構文確認が成功すること。
- 規定値を使用する場合, `/srv/elastic-search` 配下へ読み書き可能な権限があること。

### 2. `curl` で応答しない場合

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

以下の`DUMMY_ELASTIC_PASSWORD`を`elastic_search_bootstrap_password`の設定値に変更して実行してください。

```bash
docker ps --filter name=elasticsearch
ss -ltnp | grep ':9200 '
curl -v --max-time 5 -u 'elastic:DUMMY_ELASTIC_PASSWORD' http://127.0.0.1:9200/
```

**実行結果の例**:
```bash
$ docker ps --filter name=elasticsearch
CONTAINER ID   IMAGE                                                  COMMAND                  CREATED             STATUS                       PORTS                              NAMES
3810ef71ee6d   docker.elastic.co/elasticsearch/elasticsearch:8.19.19   "/bin/tini -- /usr/l…"   About an hour ago   Up About an hour (healthy)   0.0.0.0:9200->9200/tcp, 9300/tcp   elasticsearch
$ ss -ltnp | grep ':9200 '
LISTEN 0      4096         0.0.0.0:9200       0.0.0.0:*
$ curl -v --max-time 5 -u 'elastic:elastic' http://127.0.0.1:9200/
*   Trying 127.0.0.1:9200...
* Connected to 127.0.0.1 (127.0.0.1) port 9200 (#0)
* Server auth using Basic with user 'elastic'
> GET / HTTP/1.1
> Host: 127.0.0.1:9200
> Authorization: Basic ZWxhc3RpYzplbGFzdGlj
> User-Agent: curl/7.76.1
> Accept: */*
>
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< X-elastic-product: Elasticsearch
< content-type: application/json
< content-length: 540
<
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
* Connection #0 to host 127.0.0.1 left intact
```

**確認ポイント**:

- Elasticsearch コンテナが起動中であること。
- TCPプロトコルのポート番号9200番 で待受していること。
- `curl` が接続エラーではなく HTTP 応答を返すこと。

### 3. Elasticsearch のクラスタ状態が `yellow` 又は `green` にならない場合

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

以下の`DUMMY_ELASTIC_PASSWORD`を`elastic_search_bootstrap_password`の設定値に変更して実行してください。

```bash
curl -sS -u 'elastic:DUMMY_ELASTIC_PASSWORD' 'http://127.0.0.1:9200/_cluster/health?pretty'
curl -sS -u 'elastic:DUMMY_ELASTIC_PASSWORD' 'http://127.0.0.1:9200/_cat/nodes?v'
docker logs --tail 200 elasticsearch 2>&1 | grep -E '"log.level"[[:space:]]*:[[:space:]]*"(WARN|ERROR|FATAL)"'
```

**実行結果の例**:
```bash
$ curl -sS -u 'elastic:elastic' 'http://127.0.0.1:9200/_cluster/health?pretty'
{
  "cluster_name" : "shared-logs",
  "status" : "yellow",
  "timed_out" : false,
  "number_of_nodes" : 1,
  "number_of_data_nodes" : 1,
  "active_primary_shards" : 56,
  "active_shards" : 56,
  "relocating_shards" : 0,
  "initializing_shards" : 0,
  "unassigned_shards" : 18,
  "unassigned_primary_shards" : 0,
  "delayed_unassigned_shards" : 0,
  "number_of_pending_tasks" : 0,
  "number_of_in_flight_fetch" : 0,
  "task_max_waiting_in_queue_millis" : 0,
  "active_shards_percent_as_number" : 75.67567567567568
}
$ curl -sS -u 'elastic:elastic' 'http://127.0.0.1:9200/_cat/nodes?v'
ip         heap.percent ram.percent cpu load_1m load_5m load_15m node.role   master name
172.18.0.2           66          97   2    0.05    0.04     0.04 cdfhilmrstw *      observer01.example.org
$ docker logs --tail 200 elasticsearch 2>&1 | grep -E '"log.level"[[:space:]]*:[[:space:]]*"(WARN|ERROR|FATAL)"'
$
```

**確認ポイント**:

- `_cluster/health` の `cluster_name` が `shared-logs` であること。
- ノード一覧で想定したノード名が表示されること。
- ログにデータパス異常, ディスク不足, 起動時エラーが出ていないこと。

### 4. 他者導入の Fluent Bit へ影響があるように見える場合

**実施対象ホスト**: `logging_backend` グループと既存導入側の対象ホスト

**実行するコマンド**:

```bash
docker network ls
docker ps --format 'table {{.Names}}\t{{.Ports}}\t{{.Networks}}'
ls -ld /srv/elastic-search
```

**実行結果の例**:
```bash
$ docker network ls
NETWORK ID     NAME              DRIVER    SCOPE
32bf2d901566   bridge            bridge    local
216cb7cac2d8   elastic-backend   bridge    local
e5653ff38886   host              host      local
d1c807d24c35   none              null      local
$ docker ps --format 'table {{.Names}}\t{{.Ports}}\t{{.Networks}}'
NAMES           PORTS                                                                                      NETWORKS
kibana          0.0.0.0:5601->5601/tcp                                                                     elastic-backend
logstash        0.0.0.0:5044->5044/tcp, [::]:5044->5044/tcp, 0.0.0.0:9600->9600/tcp, [::]:9600->9600/tcp   elastic-backend
elasticsearch   0.0.0.0:9200->9200/tcp, 9300/tcp                                                           elastic-backend
fleet-server    0.0.0.0:8220->8220/tcp                                                                     elastic-backend
$ ls -ld /srv/elastic-search
drwxr-xr-x. 6 root root 84 Aug  9 12:37 /srv/elastic-search
```

**確認ポイント**:

- 本 playbook 側のネットワーク名が `elastic-backend` として分離されていること。
- 公開ポート `0.0.0.0:9200` が他者導入側のポートと競合していないこと。
- 規定値を使用する場合, 本 playbook 側のデータ配置先が `/srv/elastic-search` 配下で分離されていること。

### 5. Kibana 起動直後に `.kibana_task_manager` の 503 警告が出る場合

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**実行するコマンド**:

以下の`DUMMY_ELASTIC_PASSWORD`を`elastic_search_bootstrap_password`の設定値に変更して実行してください。

```bash
curl -sS -u 'elastic:DUMMY_ELASTIC_PASSWORD' 'http://127.0.0.1:9200/_cluster/health?pretty'
curl -sS -u 'elastic:DUMMY_ELASTIC_PASSWORD' 'http://127.0.0.1:9200/_cat/indices/.kibana*?v'
curl -sS 'http://127.0.0.1:5601/api/status'
```

**実行結果の例**:
```bash
$ curl -sS -u 'elastic:elastic' 'http://127.0.0.1:9200/_cluster/health?pretty'
{
  "cluster_name" : "shared-logs",
  "status" : "yellow",
  "timed_out" : false,
  "number_of_nodes" : 1,
  "number_of_data_nodes" : 1,
  "active_primary_shards" : 56,
  "active_shards" : 56,
  "relocating_shards" : 0,
  "initializing_shards" : 0,
  "unassigned_shards" : 18,
  "unassigned_primary_shards" : 0,
  "delayed_unassigned_shards" : 0,
  "number_of_pending_tasks" : 0,
  "number_of_in_flight_fetch" : 0,
  "task_max_waiting_in_queue_millis" : 0,
  "active_shards_percent_as_number" : 75.67567567567568
}
$ curl -sS -u 'elastic:elastic' 'http://127.0.0.1:9200/_cat/indices/.kibana*?v'
health status index                                      uuid                   pri rep docs.count docs.deleted store.size pri.store.size dataset.size
green  open   .kibana_usage_counters_8.19.19_001          mC4hG0NWRaqj-vfEt16vFQ   1   0        112           16     61.1kb         61.1kb       61.1kb
green  open   .ds-.kibana-event-log-ds-2026.08.05-000001 eG6TnJGrR0e1IdJ6K4UfvQ   1   0         72            0       82kb           82kb         82kb
green  open   .kibana_security_solution_8.19.19_001       gfo2-JeUSMu0qQNIgMFHzg   1   0          2            0     20.4kb         20.4kb       20.4kb
green  open   .kibana_8.19.19_001                         UOILuHY5SP6o4rnElPYs6g   1   0         96           24     96.8kb         96.8kb       96.8kb
green  open   .kibana_task_manager_8.19.19_001            eWAy13ezRQ-52FVcAplLgA   1   0         36           12    218.9kb        218.9kb      218.9kb
green  open   .kibana_security_session_1                 rigWS9lfQXCzc7AENWSxmw   1   0          2            0     13.2kb         13.2kb       13.2kb
green  open   .kibana_alerting_cases_8.19.19_001          Q4zHa0sVRG2CxiK_XRAzkQ   1   0          1            0      6.9kb          6.9kb        6.9kb
green  open   .kibana_ingest_8.19.19_001                  V5vNxzNYSySdt9KwZL_Kaw   1   0        759           97      3.3mb          3.3mb        3.3mb
green  open   .kibana_analytics_8.19.19_001               rPc8R2mLQpOyjC_AUXDRug   1   0       1378            0      2.9mb          2.9mb        2.9mb
$ curl -sS 'http://127.0.0.1:5601/api/status'
{"status":{"overall":{"level":"available"}}}
```

**確認ポイント**:

- 以下を満たす場合は, Kibana 起動直後の初期化処理に伴う一時的な 503 警告です:
  - `_cluster/health` の `status` が `green` または `yellow` であること。
  - `/_cat/indices/.kibana*?v` の `.kibana_task_manager_*` を含む index の `health` が `green` または `yellow` であること。
  - `/api/status` の応答本文に `"level":"available"` が含まれること。
- 数分経過後も同じ警告が継続する場合は, Elasticsearch と Kibana のログを再確認すること。

## 注意事項

- 既存のサービスで使用されているポートやディレクトリと衝突しないような設定を実施すること。
- ネットワーク名と compose project 名を他のDocker composeから展開されるコンテナと衝突しないようにすること。
- `elastic_search_data_dir`, `elastic_search_logs_dir`, `elastic_search_snapshot_repo_path_host` の所有者は, Elasticsearchコンテナイメージ仕様で指定される実行ユーザIDと実行グループID(既定では 1000:1000)に合わせること。これらの値は playbook の設計値ではなくコンテナイメージ仕様により決定されるため, コンテナイメージの仕様変更時だけ `vars/logging-backend-common.yml` の `logging_backend_container_user_id` と `logging_backend_container_group_id` を変更する。
- Elasticsearch のデータ保全のため, cron による定期バックアップを実施する運用方針を採用することを推奨します。
- 定期バックアップで作成したバックアップデータについて, 世代管理, 保存先分離, 復旧手順の定期検証を実施することが望ましいです。

## 参考資料

### 公式ドキュメント

- [Elasticsearch Reference](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/index.html)
- [Secure the Elastic Stack](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/secure-cluster.html)
- [Maximum map count check](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/bootstrap-checks-max-map-count.html)
- [Kibana Guide](https://www.elastic.co/guide/en/kibana/8.17/index.html)
- [Logstash Reference](https://www.elastic.co/guide/en/logstash/8.17/index.html)
- [Enrollment Token](https://www.elastic.co/docs/reference/fleet/fleet-enrollment-tokens)
- [Service accounts and tokens](https://www.elastic.co/guide/en/elasticsearch/reference/current/service-accounts.html)
- [Docker Compose documentation](https://docs.docker.com/compose/)
- [Ansible documentation](https://docs.ansible.com/ansible/latest/)
- [The java Command](https://docs.oracle.com/en/java/javase/24/docs/specs/man/java.html)
