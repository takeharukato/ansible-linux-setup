# fleet-bootstrap ロール

本ロールは, Kibana の Fleet API へ接続して Logstashを送信先とするFleet Output, 3種類のElastic Agent ポリシー, Package Policy及びEnrollment Tokenを作成又は更新するための初期化ロールです。3種類のElastic Agent ポリシーは, ホスト監視, Kubernetesシステム監視及びKubernetesワークロード監視に対応します。加えて, Logstashの下流にあるElasticsearchに対して `_cluster/health` を対象ホスト上での疎通確認と外部ホストからの疎通確認に分けて確認し, 接続先の到達性も同時に検証します。`fleet-server` と `fleet-bootstrap` を同一 `ansible-playbook` 実行で連続適用することを前提とし, Fleet Server ロール側で設定された Fleet API 呼び出し用のキーを用いて, Fleet APIに接続し, Fleet Serverの設定を行います。
本ロールでは, コンテナ起動やサービス管理は行わず, 既存の Fleet Serverの設定作業のみを実施します。

## 目次

- [fleet-bootstrap ロール](#fleet-bootstrap-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
    - [fleet-bootstrapロールの実行方法](#fleet-bootstrapロールの実行方法)
  - [主要変数](#主要変数)
    - [各ロール固有の利用者入力値](#各ロール固有の利用者入力値)
      - [必須入力値](#必須入力値)
      - [任意入力値](#任意入力値)
    - [Elastic Stack間共有設定値](#elastic-stack間共有設定値)
    - [設定例](#設定例)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [検証の前提条件](#検証の前提条件)
    - [検証環境の設定](#検証環境の設定)
    - [検証コマンドと期待結果](#検証コマンドと期待結果)
      - [1. Kibana の Fleet API から生成結果を確認](#1-kibana-の-fleet-api-から生成結果を確認)
      - [2. Fleet Output 用 Elasticsearch hosts の対象ホスト上での疎通確認を確認](#2-fleet-output-用-elasticsearch-hosts-の対象ホスト上での疎通確認を確認)
      - [3. Fleet Output 用 Elasticsearch hosts の外部ホストからの疎通確認を確認](#3-fleet-output-用-elasticsearch-hosts-の外部ホストからの疎通確認を確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. API キー未設定または不正値で実行に失敗する場合](#1-api-キー未設定または不正値で実行に失敗する場合)
    - [2. Kibana への接続に失敗する場合](#2-kibana-への接続に失敗する場合)
    - [3. Fleet POST API が timeout する場合](#3-fleet-post-api-が-timeout-する場合)
    - [4. Output, Policy, 認証情報の作成後に一覧に反映されない場合](#4-output-policy-認証情報の作成後に一覧に反映されない場合)
    - [5. Elasticsearch hosts の health check に失敗する場合](#5-elasticsearch-hosts-の-health-check-に失敗する場合)
    - [6. Enrollment Token共有ファイルの保存に失敗する場合](#6-enrollment-token共有ファイルの保存に失敗する場合)
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
| Elasticsearch のクラスタ | - | 複数の Elasticsearch ノードを連携させて一体運用する構成。 |
| ディストリビューション | - | 基本ソフトウェアと関連部品をまとめた配布形態。 |
| コンテナイメージ | - | コンテナ実行に必要な内容をまとめた保存形式。 |
| プログラム | - | 計算機に処理をさせるための命令列。 |
| コミュニティ | - | 共通目的のもとで継続的に活動する利用者集団。 |
| プラグイン | - | 既存機能へ追加機能を組み込むための拡張部品。 |
| サービスアカウント (Service Account) | - | 自動処理中でサービスを呼び出す側のプログラムを識別するための識別情報。 |
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
| Central Processing Unit | CPU | 計算処理を実行する中核部品。 |
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
| ノード | - | ネットワークに接続された機器または処理単位。 |
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
| ネットワーク | - | 機器同士を接続してデータをやり取りする仕組み。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
| プロトコル | - | 通信やデータ交換の手順を定めた取り決め。 |
| ディレクトリ | - | ファイルを階層的に整理するための入れ物。 |
| ログ | - | 処理の結果や状態を時系列で記録した情報。 |
| コード | - | 処理内容を記述した文字列。 |
| ファイルシステム | - | 記憶装置上のファイルとディレクトリを管理する仕組み。 |
| プロセス | - | 実行中のプログラムを管理する単位。 |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウェア。 |
| Pod | - | Kubernetes でコンテナをまとめて管理する最小単位。 |
| 名前空間 ( namespace ) | - | Kubernetes内部でリソースを論理的に分離する単位。 |
| Linux | - | 多くの機器で使われる, 基本ソフトウェアの系統。 |
| Debian | - | コミュニティ主導で開発される Linux ディストリビューション。 |
| Ubuntu | - | Canonical が提供する Debian 系の Linux ディストリビューション。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| statコマンド | stat | ファイルの権限, 大きさ及び名前を表示するコマンド。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Elasticsearch | - | ログやメトリクス情報を集約, 検索するためのサーバソフトウェア。 |
| Elasticsearchのセキュリティ機能 | - | Elasticsearchへの接続者を認証し, 利用者に付与した権限に基づいて実行可能な操作を制御する機能。 |
| Kibana | - | Elasticsearchに保存されたデータを可視化し, 参照するソフトウェア。 |
| Fleet Server | - | Elastic Agent の管理通信を受け付けるサーバ機能。 |
| Elastic Agent | - | ログやメトリクスを収集して送信する実行要素。 |
| Fleet Output | - | Elastic Agent が送信先として利用する出力設定。 |
| Elastic Agent ポリシー | - | Fleetが管理し, Elastic Agentのデータ収集方法と動作を定める設定情報。 |
| 統合パッケージ | - | Elastic Agentへデータの収集方法と収集項目を追加するためのパッケージ。 |
| Package Policy | - | Elastic Agent ポリシーへ追加する収集内容と統合パッケージの設定。 |
| System統合 | - | Elastic Agentが対象ホストのログとメトリクス情報を収集するための統合パッケージ。 |
| Custom Logs統合 | - | Elastic Agentが指定されたログファイルからテキストを収集するための統合パッケージ。 |
| Enrollment Token | - | Elastic AgentがFleet Serverへの登録を許可されていることを確認し, 登録先のElastic Agent ポリシーを特定するための登録用認証情報。 |
| Enrollment Token共有ファイル | - | Fleet BootstrapがEnrollment Tokenを制御ホスト上へ保存し, Elastic Agent本体ロールがFleet Serverへの登録時に読み込む権限`0600`のYAMLファイル。 |
| Fleet Serverサービスアカウントトークンファイル | - | Fleet ServerがElasticsearchへ接続するためのサービスアカウントトークンを対象ホスト上へ保存し, Fleet Serverコンテナが起動時に読み込む権限`0600`のファイル。 |
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| 対象ホスト上での疎通確認 | - | 対象ホスト上で自ホスト(localhost)を指定して待ち受け先ポートへの疎通確認を実施すること。確認対象のサービスが対象ホスト上で起動していることを確認します。 |
| 外部ホストからの疎通確認 | - | 対象ホスト以外のホストから対象ホストを指定して待ち受け先ポートへの疎通確認を実施すること。確認対象のサービスがネットワーク接続を含めて適切に設定され, サービス受付可能な状態になっていることを確認します。 |
| ロール | - | Ansible における処理のまとまり。 |

## 概要

本ロールは, KibanaのFleet APIを使用してFleetの初期設定を行います。本ロールの担当作業は次のとおりです:

- KibanaのFleet APIを使用して, Fleet APIを使用できる状態にします。
- Fleet APIを使用し, Fleetを利用できる状態へ初期化します。
  - Fleet Server接続先とデータ送信先を設定します。
    - Fleetに既定のFleet Server host設定が存在しない場合は, `fleet_bootstrap_fleet_server_host_name`変数で指定した名称と`fleet_bootstrap_fleet_server_host_urls_explicit`変数で指定した接続先一覧を使用して作成します。
      - `fleet_bootstrap_fleet_server_host_urls_explicit`変数で接続先一覧を指定していない場合は, Fleet Serverロールが設定した接続先を使用します。
    - Elastic Agentが収集したデータとElastic Agent自身の監視データをLogstashへ送信するFleet Outputを作成又は更新し, 両方の既定出力に設定します。
      - Fleet Server専用Elasticsearch Outputを作成又は更新し, Fleet Server用Elastic Agent ポリシーへ設定します。
  - Elastic Agentのデータ収集設定を準備します。
    - Fleet Server統合, System統合及びCustom Logs統合を導入します。
    - Elastic Stack間で共有するFleet Server用Elastic Agent ポリシーIDを使用してポリシーを作成又は再利用し, Fleet Server統合を関連付けます。
    - ホスト監視, Kubernetesシステム監視及びKubernetesワークロード監視に使用する3種類のElastic Agent ポリシーを作成又は再利用します。
      - ホスト監視では, 対象ホストのCPU使用状況, データを一時保持する領域の使用状況及び指定したホスト上のログを収集します。
      - Kubernetesシステム監視では, ホスト監視の収集対象に加えて, Kubernetesノードのファイルシステムとプロセスの情報及びKubernetesの`kube-system`名前空間に属するコンテナのログを収集します。
      - Kubernetesワークロード監視では, Kubernetesシステム監視の収集対象に加えて, Kubernetesの`kube-system`名前空間に属さないコンテナのログを収集します。
    - 各Elastic Agent ポリシーへSystem統合とCustom Logs統合のPackage Policyを作成又は更新します。
  - Elastic Agentの登録情報を準備します。
    - 各Elastic Agent ポリシーのEnrollment Tokenを作成又は再利用し, 既存Enrollment Tokenを再利用する場合はFleet APIから秘密値を取得します。
  - Fleetの初期設定結果を検証します。
    - Fleet Output, Fleet Server用を含むElastic Agent ポリシー, Package Policy及びEnrollment Tokenが期待した状態であることをFleet APIで検証します。
- 3種類のElastic Agent ポリシーに対応するEnrollment TokenをEnrollment Token共有ファイルへ保存します。
- Logstashの下流にあるElasticsearchへの対象ホスト上での疎通確認を実施し, 指定時は外部ホストからの疎通確認も実施します。

3種類のElastic Agent ポリシーは個別の出力IDを持たず, 既定のLogstash Outputを継承します。Fleet Server統合の追加時だけFleet Server専用Elasticsearch Outputを一時的な既定出力に設定し, 統合追加後にLogstash Outputを既定出力へ戻します。この切替により, Basicライセンスで通常AgentはLogstashへ送信し, Fleet Serverは専用Elasticsearch Outputを使用してElasticsearchへ直接接続します。

本ロールの実行結果及び成果物を使用して, Fleet ServerロールとElastic Agentロールは次の作業を実施します。

- Fleet Serverロールは, Fleet Bootstrapロールが管理するPackage Policyを含むElastic Agent ポリシーをElastic Agentへ配布します。
- Elastic Agentロールは, 対象ホストで収集するログやメトリクス情報の集合に応じてEnrollment TokenをEnrollment Token共有ファイル内の辞書から選択し, Fleet Serverへ登録します。
- 登録されたElastic Agentは, Fleet ServerからElastic Agent ポリシーを取得します。

`fleet_bootstrap_enrollment_token_file`は`vars/logging-backend-common.yml`で定義し, Fleet BootstrapロールとElastic Agentロールの間でEnrollment Token共有ファイルの保存先を共有する契約変数です。保存先ディレクトリは, Fleet API処理より前に制御ホスト上へ権限`0700`で作成します。Fleet Serverサービスアカウントトークンファイルは対象ホスト上でFleet Serverロールが管理する別のファイルであり, 本ロールは作成, 更新又は読込を行いません。

## 前提条件

- Kibana の Fleet API へ接続できること。
- 本フェーズの運用では, 単一の `ansible-playbook` 実行で `fleet-server,fleet-bootstrap` を連続適用すること。
- 同一実行内で Fleet Server 側が設定した `fleet_bootstrap_kibana_api_key` を本ロールが利用できること。単独検証時は, Kibana で作成した Fleet 用の API キーを `host_vars` または `vars/all-config.yml` に直接設定すること。
- Elasticsearchのセキュリティ機能が有効な場合は, `elastic_search_security_username` と `elastic_search_bootstrap_password` が利用可能であること。
- [roles/fleet-bootstrap/defaults/main.yml](roles/fleet-bootstrap/defaults/main.yml) に定義した変数を適切に上書きできること。
- Fleet Server の準備後に本ロールを実行すること。
- `fleet_bootstrap_enrollment_token_file`の共通既定値が制御ホスト上の絶対パスとして解決されること。
- `fleet_bootstrap_kibana_url_explicit` と `fleet_bootstrap_elasticsearch_endpoints_explicit` を未設定で運用する場合は, 対象ホスト自身の `127.0.0.1:5601` と `127.0.0.1:9200` に到達可能であること。

## 実行方法

### fleet-bootstrapロールの実行方法

制御ホストで次のいずれかを実行します。

logging backend全体を構成し, Fleet BootstrapによるEnrollment Token共有ファイルの保存まで完了する場合は, 次のコマンドを実行します。

```bash
make run_logging_backend
```

Fleet ServerとFleet Bootstrapだけを連続適用する場合は, 次のコマンドを実行します。

```bash
make run_fleet_bootstrap
```

`make run_fleet_bootstrap` は, 単一の `ansible-playbook` 実行で `fleet-server,fleet-bootstrap` を順に適用します。

```bash
ansible-playbook -i inventory/hosts logging-backend.yml --tags "fleet-server,fleet-bootstrap"
```

`fleet_bootstrap_enrollment_token_file`で指定したEnrollment Token共有ファイルがすでに存在する場合は, 既存のEnrollment Token共有ファイルを維持します。

## 主要変数

### 各ロール固有の利用者入力値

#### 必須入力値

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `fleet_bootstrap_output_name` | Elastic Agentの収集データをLogstashへ送信するFleet Outputの名称。 | 空文字列 | `main-logstash-output` |
| `fleet_bootstrap_policy_name` | ホスト監視用Elastic Agent ポリシーの名称。 | 空文字列 | `linux-host-policy` |
| `fleet_bootstrap_enrollment_token_name` | ホスト監視用Enrollment Tokenの名称。 | 空文字列 | `linux-host-token` |

`fleet_bootstrap_kibana_api_key`は, `fleet-server`と本ロールを同一の`ansible-playbook`実行で連続適用する場合はFleet Serverが生成します。本ロールだけを実行する場合は, 有効なAPIキーを明示設定します。

#### 任意入力値

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `fleet_bootstrap_enabled` | Fleet Server導入時の初期化処理実施指示フラグ。Fleet Server導入時の初期化処理を実施する場合は, `true`に設定する。 | `true` | `true` |
| `fleet_bootstrap_kibana_url_explicit` | Kibana の Fleet API 接続先明示指定値。未設定時は対象ホスト上の `http://127.0.0.1:5601` を使用する。 | 空文字列 | `https://kibana.example.org:5601` |
| `fleet_bootstrap_kibana_tls_mode` | Kibana APIのエンドポイントURLスキームが`https`の場合に参照するTLS検証モード。指定可能な値は, [Elasticsearchロールの共有設定値](../elasticsearch/Readme.md#共有設定値に関する補足説明)を参照する。 | `logging_backend_default_tls_mode`の指定値。 | `none` |
| `fleet_bootstrap_kibana_api_key` | Kibanaに設定するFleet用APIキー。`vars/all-config.yml`または, `host_vars`に設定を記載する。 | 空文字列 | `"your-api-key"` |
| `fleet_bootstrap_kibana_timeout_seconds` | Kibana の Fleet API 接続タイムアウト秒数。package registry 待ちを考慮して長めに設定する。 | `180` | `240` |
| `fleet_bootstrap_kibana_retries` | 外部 API 呼び出しの再試行回数 | `3` | `5` |
| `fleet_bootstrap_kibana_retry_delay_seconds` | 外部 API 呼び出しの再試行間隔秒数 | `5` | `10` |
| `fleet_bootstrap_system_package_version` | System統合パッケージの版数。 | `2.4.0` | `2.4.0` |
| `fleet_bootstrap_filestream_package_version` | Custom Logs統合パッケージの版数。 | `1.2.0` | `1.2.0` |
| `fleet_bootstrap_fleet_server_package_version` | Fleet Server統合パッケージの版数。 | `1.6.1` | `1.6.1` |
| `fleet_bootstrap_fleet_server_output_name` | Fleet Server用Elastic Agent ポリシーが使用するElasticsearch Outputの名称。 | `fleet-server-elasticsearch-output` | `fleet-server-elasticsearch-output` |
| `fleet_bootstrap_fleet_server_elasticsearch_hosts_explicit` | Fleet Server専用Elasticsearch Outputの送信先一覧明示指定値。未設定時はFleet Serverロールが解決したElasticsearch接続先を使用する。 | 空リスト | [`https://elasticsearch.example.org:9200`] |
| `fleet_bootstrap_enrollment_token_list_page_size` | 既存Enrollment Tokenの検索と検証で一覧APIから取得する最大件数。`1`から`10000`までを指定する。 | `10000` | `10000` |
| `fleet_bootstrap_logstash_hosts_explicit` | Fleet Outputに設定するLogstash接続先一覧明示指定値。未設定時は共通接続先ホストのポート番号5044番を使用する。 | 空リスト | [`logstash.example.org:5044`] |
| `fleet_bootstrap_elasticsearch_endpoints_explicit` | Logstashの下流にあるElasticsearchの疎通確認先一覧明示指定値。未設定時は対象ホスト上の `http://127.0.0.1:9200` を使用する。 | 空リスト | [`https://elasticsearch:9200`] |
| `fleet_bootstrap_fleet_server_host_name` | Fleet Server host 設定へ登録する名称。 | `default-fleet-server-host` | `default-fleet-server-host` |
| `fleet_bootstrap_fleet_server_host_urls_explicit` | Fleet Server host 設定へ登録する接続先一覧明示指定値。未設定時は Fleet Server のランタイムエンドポイント URL を使用する。 | 空リスト | [`https://fleet.example.org:8220`] |
| `fleet_bootstrap_enrollment_token_file` | Enrollment Token共有ファイルの制御ホスト上の絶対パス。 | `{{ playbook_dir }}/group_vars/logging_collector/enrollment-token.yml` | `{{ playbook_dir }}/group_vars/logging_collector/enrollment-token.yml` |
| `fleet_bootstrap_debug_auth_diagnostics` | 認証切り分け用の補助 debug 出力有無。通常運用では `false` のままとする。 | `false` | `true` |
| `fleet_bootstrap_no_log` | Fleet API 呼び出し結果の秘匿有無。通常運用では `true` のままとし, API 応答本文まで確認する調査時だけ `false` に切り替える。 | `true` | `false` |

### Elastic Stack間共有設定値

共有設定値の意味, 設定要否, 既定値及び設定例は, [Elasticsearchロールの共有設定値](../elasticsearch/Readme.md#varsall-configymlに設定するelastic-stack間共有設定値)を参照します。Fleet Bootstrapでは, 共通の接続先ホスト, URLスキーム, TLS検証モード, 複数接続先の方式混在禁止及び外部ホストからの疎通確認設定が影響します。

### 設定例

```yaml
1: fleet_bootstrap_enabled: true
2: fleet_bootstrap_kibana_url_explicit: "https://kibana.example.org:5601"
3: fleet_bootstrap_kibana_api_key: "your-api-key"
4: fleet_bootstrap_output_name: "main-logstash-output"
5: fleet_bootstrap_policy_name: "linux-host-policy"
6: fleet_bootstrap_enrollment_token_name: "linux-host-token"
7: fleet_bootstrap_elasticsearch_endpoints_explicit:
8:   - "https://elasticsearch:9200"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | fleet_bootstrap_enabled: true | 本ロールを実行する。 | 既定値のままでは実行対象となるため, 明示的に有効化するための設定です。 |
| 2 | fleet_bootstrap_kibana_url_explicit: "https://kibana.example.org:5601" | Kibana の Fleet API 接続先を指定する。 | 未設定時は対象ホスト上の `127.0.0.1:5601` を使用するため, 別ホスト上の Kibana を使用する構成では明示設定が必要です。 |
| 3 | fleet_bootstrap_kibana_api_key: "your-api-key" | Fleet API 認証に使用する API キーを指定する。 | 秘密情報を defaults へ置かず, host_vars や vars/all-config.yml へ直接記載するための設定です。 |
| 4-6 | fleet_bootstrap_output_name, fleet_bootstrap_policy_name, fleet_bootstrap_enrollment_token_name | 生成または再利用する対象名を指定する。 | 既定名と異なる場合でも本ロールで扱えるようにするための設定です。 |
| 7-8 | fleet_bootstrap_elasticsearch_endpoints_explicit | Logstashの下流にあるElasticsearchの疎通確認先一覧を指定する。 | 未設定時は対象ホスト上の `127.0.0.1:9200` を使用するため, 別ホスト上の Elasticsearch を使用する構成では明示設定が必要です。 |

## テンプレートと生成ファイル

| 種別 | 入力 | 出力 | 目的 |
| --- | --- | --- | --- |
| タスク生成 | [roles/fleet-bootstrap/tasks/config.yml](roles/fleet-bootstrap/tasks/config.yml) | 既存または新規の Fleet Output, Elastic Agent ポリシー, Package Policy及びEnrollment Token | Kibana の Fleet API を呼び出して初期化対象を設定する。 |
| タスク生成 | [roles/fleet-bootstrap/tasks/configure-fleet-server-policy.yml](roles/fleet-bootstrap/tasks/configure-fleet-server-policy.yml) | Fleet Server用Elastic Agent ポリシー及びFleet Server統合 | Fleet Server用Elastic Agent ポリシーを指定IDで作成し, Fleet Server統合を設定する。 |
| Enrollment Token共有ファイル | 3種類のEnrollment Token | `group_vars/logging_collector/enrollment-token.yml` | Elastic Agentへ渡す`elastic_agent_enrollment_tokens`辞書を制御ホスト上へ権限`0600`で保存する。 |
| 変数定義 | [roles/fleet-bootstrap/defaults/main.yml](roles/fleet-bootstrap/defaults/main.yml) | 制御用変数 | 接続先, 既定名, タイムアウト, TLS 設定を提供する。 |

## 実行フロー

1. [roles/fleet-bootstrap/tasks/main.yml](roles/fleet-bootstrap/tasks/main.yml) で各タスクファイルを読み込みます。
2. [roles/fleet-bootstrap/tasks/config.yml](roles/fleet-bootstrap/tasks/config.yml) で Fleet Bootstrap の実行可否と API キー設定を確認します。
3. [roles/fleet-bootstrap/tasks/config.yml](roles/fleet-bootstrap/tasks/config.yml) で Fleet の初期化 API を呼び出して, GUI がなくても利用できる前提を整えます。
4. [roles/fleet-bootstrap/tasks/config.yml](roles/fleet-bootstrap/tasks/config.yml) で Fleet Server host 設定を一覧取得し, 既定 host が存在しない場合にのみ作成します。
5. [roles/fleet-bootstrap/tasks/config.yml](roles/fleet-bootstrap/tasks/config.yml) で Fleet Output を一覧取得し, 指定名の既定Logstash Outputが存在しない場合は作成し, 既存設定がLogstash出力の期待値と異なる場合は更新します。
6. [roles/fleet-bootstrap/tasks/config.yml](roles/fleet-bootstrap/tasks/config.yml) でFleet Server統合, System統合及びCustom Logs統合を導入します。
7. [roles/fleet-bootstrap/tasks/configure-fleet-server-policy.yml](roles/fleet-bootstrap/tasks/configure-fleet-server-policy.yml) でFleet Server専用Elasticsearch Outputを一時的な既定出力に設定し, Fleet Server用Elastic Agent ポリシーを指定IDで作成又は再利用してFleet Server統合を設定した後, Logstash Outputを既定出力へ戻します。Fleet Server自身のAgent IDが空の場合は, 統合追加前に生成された不完全な登録情報を除去してコンテナを再起動します。
8. 3種類の通常Agent用Elastic Agent ポリシーを作成又は再利用し, System統合とCustom Logs統合のPackage Policyを作成又は更新します。
9. `fleet_bootstrap_enrollment_token_list_page_size`件までEnrollment Tokenを一覧取得し, 各Elastic Agent ポリシーにKibanaが`指定名 (UUID)`形式で保存したEnrollment Tokenが存在しない場合にのみ作成します。
10. 既存Enrollment Tokenを再利用する場合は, 一覧APIからIDを取得し, 個別取得APIからEnrollment Tokenの秘密値を取得します。
11. 3種類のEnrollment Tokenを辞書として制御ホスト上のEnrollment Token共有ファイルへ権限`0600`で保存し, 保存後にEnrollment Token共有ファイルの種別と権限を検証します。
12. [roles/fleet-bootstrap/tasks/verify.yml](roles/fleet-bootstrap/tasks/verify.yml) で Fleet Output, Fleet Server用を含むElastic Agent ポリシー, Package Policy及びEnrollment Tokenの存在を Fleet API で確認します。
13. [roles/fleet-bootstrap/tasks/verify.yml](roles/fleet-bootstrap/tasks/verify.yml) で Logstashの下流にあるElasticsearchの対象ホスト上での疎通確認と, `logging_verify_external_enabled: true` 時の外部ホストからの疎通確認を `_cluster/health` で確認します。
14. 生成または既存利用された ID と認証情報を, 以後の処理で参照できるようにします。

## 検証ポイント

### 検証の前提条件

検証を始める前に, 次の条件が満たされていることを確認します。

- Kibana の Fleet API へ接続できること。
- 本ロールで利用する API キーが host_vars または vars/all-config.yml に直接設定済みであること。
- [roles/fleet-bootstrap/tasks/config.yml](roles/fleet-bootstrap/tasks/config.yml) で作成する対象名が, 既存の Fleet 構成と衝突しないこと。
- 制御ホストで Ansible と ansible-lint が利用できること。
- 制御ホスト上の`fleet_bootstrap_enrollment_token_file`で指定した親ディレクトリへEnrollment Token共有ファイルを作成できること。

### 検証環境の設定

検証用の host_vars, または, vars/all-config.yml を以下のように設定します。

```yaml
1: fleet_bootstrap_enabled: true
2: fleet_bootstrap_kibana_url_explicit: "https://kibana.example.org:5601"
3: fleet_bootstrap_kibana_api_key: "your-api-key"
4: fleet_bootstrap_kibana_timeout_seconds: 180
5: fleet_bootstrap_output_name: "main-logstash-output"
6: fleet_bootstrap_policy_name: "linux-host-policy"
7: fleet_bootstrap_enrollment_token_name: "linux-host-token"
8: fleet_bootstrap_elasticsearch_endpoints_explicit:
9:   - "https://elasticsearch:9200"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景 |
| --- | --- | --- | --- |
| 1 | fleet_bootstrap_enabled: true | 本ロールを実行する。 | 既定値のままでは実行対象となるため, 明示的に有効化するための設定です。 |
| 2 | fleet_bootstrap_kibana_url_explicit: "https://kibana.example.org:5601" | Kibana の Fleet API 接続先を指定する。 | 未設定時は対象ホスト上の `127.0.0.1:5601` を使用するため, 別ホスト上の Kibana を使用する構成では明示設定が必要です。 |
| 3 | fleet_bootstrap_kibana_api_key: "your-api-key" | Fleet API 認証に使用する API キーを指定する。 | Kibana で作成した Fleet 用の API キーを, 秘密情報として host_vars や vars/all-config.yml へ直接記載するための設定です。 |
| 4 | fleet_bootstrap_kibana_timeout_seconds: 180 | Fleet POST API 呼び出しの待機時間を延長する。 | package registry 応答待ちで `api/fleet/setup` や `api/fleet/agent_policies` が 30 秒を超える場合があるため, 余裕を持たせるための設定です。 |
| 5-7 | fleet_bootstrap_output_name, fleet_bootstrap_policy_name, fleet_bootstrap_enrollment_token_name | 生成または再利用する対象名を指定する。 | 既定名と異なる場合でも本ロールで扱えるようにするための設定です。 |
| 8-9 | fleet_bootstrap_elasticsearch_endpoints_explicit | Logstashの下流にあるElasticsearchの疎通確認先一覧を指定する。 | 未設定時は対象ホスト上の `127.0.0.1:9200` を使用するため, 別ホスト上の Elasticsearch を使用する構成では明示設定が必要です。 |

この設定により, 本ロールで使用する Fleet の対象名と接続情報が明確になり, 検証手順を実行しやすくなります。

### 検証コマンドと期待結果

#### 1. Kibana の Fleet API から生成結果を確認

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
curl -k -H "Authorization: ApiKey ${KIBANA_FLEET_API_KEY}" -H "kbn-xsrf: 1" "https://127.0.0.1:5601/api/fleet/outputs"
```

**期待される出力**:

```plaintext
{"items":[{"name":"main-logstash-output",...}],"total":1,...}
```

**実行結果の例**:

```bash
$ curl -k -H "Authorization: ApiKey ${KIBANA_FLEET_API_KEY}" -H "kbn-xsrf: 1" "https://127.0.0.1:5601/api/fleet/outputs"
{"items":[{"id":"output-id-1","name":"main-logstash-output"}],"total":1,"page":1,"perPage":20}
```

**確認ポイント**:

- 指定した Output 名が一覧に表示されること。
- 生成済みの Policy や認証情報も同様に確認できること。

#### 2. Fleet Output 用 Elasticsearch hosts の対象ホスト上での疎通確認を確認

**実施対象ホスト**: 対称ホスト

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
$ curl -sS -u 'elastic:elastic' 'http://127.0.0.1:9200/_cluster/health?wait_for_status=yellow&timeout=60s'
{"cluster_name":"shared-logs","status":"yellow","timed_out":false,"number_of_nodes":1,"number_of_data_nodes":1,"active_primary_shards":56,"active_shards":56,"relocating_shards":0,"initializing_shards":0,"unassigned_shards":18,"unassigned_primary_shards":0,"delayed_unassigned_shards":0,"number_of_pending_tasks":0,"number_of_in_flight_fetch":0,"task_max_waiting_in_queue_millis":0,"active_shards_percent_as_number":75.67567567567568}
```

**確認ポイント**:

- `fleet_bootstrap_elasticsearch_hosts` に設定した各 URL へ `/_cluster/health` 要求を送信した応答が得られること。
- 応答 JSON の `status` が, Elasticsearch のクラスタ状態が 検索や保存の基本機能は利用できるが一部の予備コピーが未配置である状態 ( `yellow` 状態), または, 予備コピーを含む全データ配置が完了している状態 ( `green` 状態) であること。

#### 3. Fleet Output 用 Elasticsearch hosts の外部ホストからの疎通確認を確認

**実施対象ホスト**: `logging_backend` グループ以外のホスト

**実行するコマンド**:

以下の`DUMMY_ELASTIC_PASSWORD`を`elastic_search_bootstrap_password`の設定値に変更し, `<Elasticsearch導入先ホスト>`の部分をElasticsearch導入先ホストにそれぞれ変更して実行してください。

```bash
curl -sS -u 'elastic:DUMMY_ELASTIC_PASSWORD' 'http://<Elasticsearch導入先ホスト>:9200/_cluster/health?wait_for_status=yellow&timeout=60s'
```

**期待される出力**:

```plaintext
{"cluster_name":"shared-logs","status":"yellow",...}
```

**実行結果の例**:
```bash
curl -sS -u 'elastic:elastic' 'http://observer01.example.org:9200/_cluster/health?wait_for_status=yellow&timeout=60s'
{"cluster_name":"shared-logs","status":"yellow","timed_out":false,"number_of_nodes":1,"number_of_data_nodes":1,"active_primary_shards":56,"active_shards":56,"relocating_shards":0,"initializing_shards":0,"unassigned_shards":18,"unassigned_primary_shards":0,"delayed_unassigned_shards":0,"number_of_pending_tasks":0,"number_of_in_flight_fetch":0,"task_max_waiting_in_queue_millis":0,"active_shards_percent_as_number":75.67567567567568}
```

**確認ポイント**:

- 外部ホストから `fleet_bootstrap_elasticsearch_hosts` に設定した各 URL へ `/_cluster/health` 要求を送信した応答が得られること。
- 応答 JSON の `status` が, Elasticsearch のクラスタ状態が 検索や保存の基本機能は利用できるが一部の予備コピーが未配置である状態 ( `yellow` 状態), または, 予備コピーを含む全データ配置が完了している状態 ( `green` 状態) であること。

## トラブルシューティング

### 1. API キー未設定または不正値で実行に失敗する場合

- 現象: API キーが未設定の状態で本ロールを実行すると, [roles/fleet-bootstrap/tasks/config.yml](roles/fleet-bootstrap/tasks/config.yml) で停止します。
- 対処: Kibana で作成した Fleet 用の API キーを host_vars または vars/all-config.yml に直接設定する方法, 又は `fleet-server,fleet-bootstrap` を同一 `ansible-playbook` 実行で適用して Fleet Server 側の共有値を引き継ぐ方法を使用してください。

### 2. Kibana への接続に失敗する場合

- 現象: Kibana の Fleet API へ接続できず, リクエストが失敗します。
- 対処: `fleet_bootstrap_kibana_url_explicit` を未設定で運用している場合は, 対象ホスト上の `127.0.0.1:5601` に Kibana が待受していることを確認してください。別ホスト上の Kibana を使用する構成では, `fleet_bootstrap_kibana_url_explicit` を明示設定してください。

### 3. Fleet POST API が timeout する場合

- 現象: `api/fleet/setup` や `api/fleet/agent_policies` が timeout して停止します。
- 対処: package registry 応答待ちで Fleet 初期化が長時間化することがあるため, `fleet_bootstrap_kibana_timeout_seconds` を 180 秒以上へ調整してください。

### 4. Output, Policy, 認証情報の作成後に一覧に反映されない場合

- 現象: 作成処理は成功しているように見えても, Fleet API の一覧に反映されません。
- 対処: Kibana の Fleet API が利用可能であることを確認し, 作成対象の名前や接続先が正しいこと, および default Fleet Server host 設定が作成済みであることを確認してください。

### 5. Elasticsearch hosts の health check に失敗する場合

- 現象: `fleet_bootstrap_elasticsearch_hosts` の `/_cluster/health` が 200 で応答しません。
- 対処: `fleet_bootstrap_elasticsearch_endpoints_explicit` が正しい URL であること, Elasticsearchのセキュリティ機能が有効な場合は `elastic_search_security_username` と `elastic_search_bootstrap_password` が利用可能であること, そして対象ホストで Elasticsearch が稼働していることを確認してください。

### 6. Enrollment Token共有ファイルの保存に失敗する場合

- 現象: `fleet_bootstrap_enrollment_token_file`が未定義, 空文字列又は相対パスの場合, 又は保存後のEnrollment Token共有ファイルが通常ファイルかつ権限`0600`でない場合に停止します。
- 対処: `vars/logging-backend-common.yml`の共通既定値が制御ホスト上の絶対パスとして解決されることを確認してください。保存先を変更する場合は, `vars/all-config.yml`へ制御ホスト上の絶対パスを指定してください。本ロールは一覧APIで既存Enrollment TokenのIDを特定した後, 個別取得APIから秘密値を取得します。個別取得APIが既存Enrollment Tokenを返さない場合は, Fleet上の同名Enrollment Tokenの状態とFleet APIの応答を確認してください。

## 注意事項

- 本ロールは Fleet の初期化を行うための処理であり, コンテナ起動やサービス管理は実施しません。
- Enrollment Token共有ファイルの保存先は [vars/logging-backend-common.yml](../../vars/logging-backend-common.yml) の共通既定値を使用し, 保存先を変更する場合だけ [vars/all-config.yml](../../vars/all-config.yml) の`fleet_bootstrap_enrollment_token_file`で上書きしてください。
- 既存の Fleet 構成が存在する場合は, 同名の Output, Elastic Agent ポリシー, 認証情報を再利用するように動作します。
- Enrollment Token共有ファイルはFleet上の3種類のEnrollment Tokenと一致する内容へ更新します。
- 認証切り分け用の debug 出力が必要な場合は, `fleet_bootstrap_debug_auth_diagnostics: true` を一時的に指定してください。通常運用では `fleet_bootstrap_no_log: true` と `fleet_bootstrap_debug_auth_diagnostics: false` を維持してください。

## 参考資料

### 公式ドキュメント

- [Fleet API docs](https://www.elastic.co/docs/reference/fleet/fleet-api-docs)
- [Fleet enrollment tokens](https://www.elastic.co/docs/reference/fleet/fleet-enrollment-tokens)
- [Service accounts and tokens](https://www.elastic.co/guide/en/elasticsearch/reference/current/service-accounts.html)
- [Fleet agent policies](https://www.elastic.co/docs/reference/fleet/agent-policy)
- [統合パッケージ (Elastic integrations)](https://www.elastic.co/docs/reference/integrations/)
- [Fleet integration policies](https://www.elastic.co/docs/reference/fleet/integration-level-outputs)
- [System integration](https://www.elastic.co/docs/reference/integrations/system)
- [Custom Logs integration](https://www.elastic.co/docs/reference/integrations/filestream)
- [Fleet outputs](https://www.elastic.co/docs/reference/fleet/fleet-settings#output-settings)
- [Fleet and Elastic Agent Guide](https://www.elastic.co/guide/en/fleet/current/index.html)
- [Kibana Guide](https://www.elastic.co/guide/en/kibana/current/index.html)
- [Elasticsearch Reference](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Secure the Elastic Stack](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/secure-cluster.html)
- [Ansible documentation](https://docs.ansible.com/ansible/latest/)
- [statコマンド](https://www.gnu.org/software/coreutils/manual/html_node/stat-invocation.html)
- [ansible-playbook command](https://docs.ansible.com/ansible/latest/cli/ansible-playbook.html)
- [curl Manual](https://curl.se/docs/manpage.html)
- [ssh command](https://man.openbsd.org/ssh)

### 関連ロール

- [roles/elasticsearch/Readme.md](../elasticsearch/Readme.md) Elasticsearch関連コンポーネント全体の仕様についての解説を記載しています。以下の内容について確認する場合に参照します。
  - 設計背景と非干渉条件
  - Elasticsearch 関連コンポーネント構成図
  - 各コンテナの役割分担
  - inventory group と展開されるコンテナとの対応関係
