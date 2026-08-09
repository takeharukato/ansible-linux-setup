# Logstash ロール

本ロールは, 本 playbook で導入する Logstash を, 本 playbook で導入する Elasticsearch, Kibana, Filebeat, Metricbeat と組み合わせて運用するためのロールです。

## 目次

- [Logstash ロール](#logstash-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
    - [前提条件](#前提条件)
    - [基本仕様](#基本仕様)
    - [本ロールで実施する主な処理](#本ロールで実施する主な処理)
  - [実行方法](#実行方法)
    - [Makefile ターゲットによる実行](#makefile-ターゲットによる実行)
    - [ansible-playbook による role 単位実行](#ansible-playbook-による-role-単位実行)
  - [主要変数](#主要変数)
    - [基本設定](#基本設定)
    - [コンテナイメージと接続設定](#コンテナイメージと接続設定)
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
      - [1. Logstash beats 待受確認](#1-logstash-beats-待受確認)
      - [2. Logstash HTTP 応答確認](#2-logstash-http-応答確認)
    - [異常時の確認項目](#異常時の確認項目)
      - [1. ポート競合の確認](#1-ポート競合の確認)
      - [2. ネットワーク作成状態の確認](#2-ネットワーク作成状態の確認)
      - [3. pipeline 定義生成状態の確認](#3-pipeline-定義生成状態の確認)
      - [4. Docker Compose 定義生成状態の確認](#4-docker-compose-定義生成状態の確認)
      - [5. コンテナログのエラー確認](#5-コンテナログのエラー確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. Logstash が起動しない場合](#1-logstash-が起動しない場合)
    - [2. beats 入力を受信できない場合](#2-beats-入力を受信できない場合)
    - [3. HTTP 監視ポートが応答しない場合](#3-http-監視ポートが応答しない場合)
    - [4. Elasticsearch へ転送できない場合](#4-elasticsearch-へ転送できない場合)
  - [注意事項](#注意事項)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)
    - [関連ロール](#関連ロール)

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Logstash | - | 受信したデータを整形し, 送信先へ転送するソフトウェア。 |
| Elasticsearch | - | 検索と集約を担当するサーバソフトウェア。 |
| Kibana | - | Elasticsearchに保存されたデータを可視化し, 参照するソフトウェア。 |
| Filebeat | - | ログファイルを収集し, 送信先へ転送するエージェント。 |
| Metricbeat | - | メトリクスを収集して送信するエージェント。 |
| pipeline | - | 入力, 整形, 出力の処理順を定義する Logstash の設定単位。 |
| beats | - | Filebeat や Metricbeat などの送信元エージェント群, 又はその通信方式。 |
| インデックス | - | Elasticsearch に保存するデータの格納先識別単位。 |
| コンテナイメージ | - | コンテナ実行に必要な内容をまとめた保存形式。 |
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Docker Compose | - | 複数のコンテナ定義をまとめて作成, 起動, 停止, 更新する仕組み。 |
| compose project 名 | - | Docker Compose によって展開される個々のアプリケーションを識別する名前です。展開されたコンテナ, ネットワーク, ボリュームなどのリソースをグループ化し, 他のアプリケーション又は別途展開された同じアプリケーションと区別するために用います。 |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| Playbook | - | 自動化処理の実行手順を記述したファイル。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| inventory group | - | Ansible Inventory内で同じ役割の対象ホストをまとめる識別単位。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| ホスト | - | 管理対象として識別される個別の計算機。 |
| サーバ | - | 他の機器や利用者へ機能やデータを提供する計算機, 又はその役割。 |
| ネットワーク | - | 機器同士を接続してデータをやり取りする仕組み。 |
| ディレクトリ | - | ファイルを階層的に整理するための入れ物。 |
| ログ | - | 処理の結果や状態を時系列で記録した情報。 |
| データ | - | 処理や保存の対象となる情報。 |
| ポート | - | 通信の出入口を識別する番号または接点。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| Hypertext Transfer Protocol | HTTP | World Wide Webで情報をやり取りする通信手順。 |
| Internet Protocol | IP | ネットワーク上で宛先を識別し, データを届けるための通信手順。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Linux | - | 多くの機器で使われる, 基本ソフトウェアの系統。 |
| ディストリビューション | - | 基本ソフトウェアと関連部品をまとめた配布形態。 |
| コミュニティ | - | 共通目的のもとで継続的に活動する利用者集団。 |
| Debian | - | コミュニティ主導で開発される Linux ディストリビューション。 |
| Red Hat | - | Red Hat Enterprise Linuxなどを提供する組織。 |
| Red Hat Enterprise Linux | RHEL | Red Hatが提供する企業向けLinuxディストリビューション。 |
| root | - | Unix 系システムの最上位権限を持つ管理者識別子。 |
| ansible-playbookコマンド | ansible-playbook | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |
| makeコマンド | make | Makefile に定義された処理を実行するコマンド。 |
| curlコマンド | curl | URL を指定して通信結果を取得するコマンド。 |
## 概要

### 前提条件

本 playbook を実行する前提条件は, 次のとおりです。

- 対象ホストが, `inventory/hosts` ファイル中の `logging_backend` グループに登録されていること。
- 対象ホストの OS は, Debian 系又は RHEL 系であること。
- 対象ホストで Docker と Docker Compose が利用可能であること。
- 対象ホストで `sudo` によるディレクトリ作成とコンテナ起動が可能であること。
- `logstash_beats_port` と `logstash_http_port` に設定するポート番号が, 既存サービスで使用するポート番号と競合しないこと。
- backend 用ネットワーク上で `elasticsearch` 名により本 playbook が導入する Elasticsearch へ到達できること。

### 基本仕様

本ロールで Logstash を導入する際の仕様は, 次のとおりです。

- コンテナイメージは `docker.elastic.co/logstash/logstash:8.17.3` を使用すること。
- beats 入力は TCPプロトコルのポート番号5044番 で待受すること。
- HTTP 監視ポートは TCPプロトコルのポート番号9600番 で待受すること。
- pipeline ID は `main` とすること。
- 出力先 Elasticsearch は `http://elasticsearch:9200` とすること。
- 出力先インデックス名は `shared-logs-%{+YYYY.MM.dd}` 形式とすること。
- 設定, pipeline 定義, データ, ログは, 本 playbook で導入する専用ディレクトリへ分離すること。

### 本ロールで実施する主な処理

本ロールでは, 次の処理を実施します。

1. `docker compose` が利用可能であることを確認します。
2. 本 playbook で導入するディレクトリを作成します。
3. Logstash の pipeline と Docker Compose 定義を生成します。
4. backend 用ネットワークへ接続して Logstash コンテナを起動します。
5. 起動後に HTTP 監視ポートの待機と HTTP 応答確認を行います。

## 実行方法

### Makefile ターゲットによる実行

制御ホストで次のコマンドを実行します。

```bash
make run_logging_backend
```

このターゲットは logging backend 用 Playbook の実行導線として用意されています。現状の Logstash 単独適用は, 次節の `ansible-playbook` による実行手順を使用します。

### ansible-playbook による role 単位実行

制御ホストで次のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts logging-backend.yml --tags logstash
```

このコマンドは, `logging_backend` グループに対して Logstash ロールのみを実行します。

## 主要変数

### 基本設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `logging_logstash_enabled` | Logstash ロールの有効化フラグ。 | `true` | `true` |
| `logstash_compose_dir` | Docker Compose 定義と関連ファイルを配置するディレクトリ。 | `/srv/logstash` | `/srv/logstash` |
| `logstash_compose_file` | Docker Compose 定義のファイルパス。 | `{{ logstash_compose_dir }}/docker-compose.yml` | `/srv/logstash/docker-compose.yml` |
| `logstash_config_dir` | Logstash 関連の設定用ディレクトリ。 | `{{ logstash_compose_dir }}/config` | `/srv/logstash/config` |
| `logstash_pipeline_dir` | Logstash の pipeline を配置するディレクトリ。 | `{{ logstash_config_dir }}/pipelines` | `/srv/logstash/config/pipelines` |
| `logstash_data_dir` | Logstash データを配置するディレクトリ。 | `{{ logstash_compose_dir }}/data` | `/srv/logstash/data` |
| `logstash_logs_dir` | Logstash ログを配置するディレクトリ。 | `{{ logstash_compose_dir }}/logs` | `/srv/logstash/logs` |
| `logstash_network_name` | Docker ネットワーク名。 | `elastic-backend` | `elastic-backend` |
| `logstash_container_name` | Logstash コンテナ名。 | `logstash` | `logstash` |

### コンテナイメージと接続設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `logstash_image` | Logstash のコンテナイメージ名。 | `docker.elastic.co/logstash/logstash:8.17.3` | `docker.elastic.co/logstash/logstash:8.17.3` |
| `logstash_beats_port` | beats 入力待受ポート。 | `5044` | `5044` |
| `logstash_http_port` | Logstash HTTP 監視ポート。 | `9600` | `9600` |
| `logstash_pipeline_id` | Logstash の pipeline ID。 | `main` | `main` |

### 起動検証関連設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `logstash_wait_host` | 起動確認で待機する接続先ホスト。 | `127.0.0.1` | `127.0.0.1` |
| `logstash_wait_delegate_to` | 起動確認を実行する接続元ホスト。 | `localhost` | `localhost` |
| `logstash_wait_timeout` | 起動確認のタイムアウト時間。 | `120` | `120` |
| `logstash_wait_delay` | 起動確認の開始遅延時間。 | `2` | `2` |
| `logstash_wait_sleep` | 起動確認の待機間隔。 | `2` | `2` |
| `logstash_wait_retries` | 起動確認の再試行回数。 | `5` | `5` |

### 変数設定例

#### host_vars の設定例

ホスト固有に変える値を `host_vars/logstash01.local.yml` に記載します。

```yaml
1: logging_logstash_enabled: true
2: logstash_beats_port: 5044
3: logstash_wait_delegate_to: "{{ inventory_hostname }}"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `logging_logstash_enabled: true` | Logstash ロールを有効化し, ディレクトリ作成, 設定生成, コンテナ起動, 起動確認を実行します。 | `false` の場合は Logstash ロールの処理が実行されず, 期待した導入結果を得られないためです。 |
| 2 | `logstash_beats_port: 5044` | beats 入力待受ポートを `5044` に設定します。 | ポートが未設定又は誤設定の場合, Filebeat や Metricbeat からの送信先が不一致となり, 受信できないためです。 |
| 3 | `logstash_wait_delegate_to: "{{ inventory_hostname }}"` | 起動確認タスクを対象ホスト自身から実行します。 | 到達不能な接続元を設定した場合, 起動済みでも待受確認に失敗し, ロール実行が異常終了するためです。 |

この例では, beats 入力待受ポートを明示し, 起動確認の接続元を対象ホスト自身にします。

#### vars/all-config.yml の設定例

全ホスト共通の値を `vars/all-config.yml` に記載します。

```yaml
1: logging_logstash_enabled: true
2: logstash_compose_dir: "/srv/logstash"
3: logstash_network_name: "elastic-backend"
4: logstash_image: "docker.elastic.co/logstash/logstash:8.17.3"
5: logstash_beats_port: 5044
6: logstash_http_port: 9600
7: logstash_pipeline_id: "main"
8: logstash_wait_host: "127.0.0.1"
9: logstash_wait_timeout: 120
10: logstash_wait_delay: 2
11: logstash_wait_sleep: 2
12: logstash_wait_retries: 5
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `logging_logstash_enabled: true` | Logstash ロールを有効化し, 共通設定にもとづく導入処理を実行します。 | `false` の場合は共通設定が存在しても導入処理が実行されず, 設定の反映漏れが発生するためです。 |
| 2 | `logstash_compose_dir: "/srv/logstash"` | Docker Compose 定義, 設定, データ, ログの保存先基準ディレクトリを `/srv/logstash` に統一します。 | 未設定又は誤設定の場合, 生成先の分散や競合が発生し, 保守作業で誤操作が起きやすくなるためです。 |
| 3 | `logstash_network_name: "elastic-backend"` | Logstash が参加する外部ネットワーク名を `elastic-backend` に設定します。 | 関連コンテナ群と異なるネットワーク名を設定した場合, 相互接続に失敗するためです。 |
| 4 | `logstash_image: "docker.elastic.co/logstash/logstash:8.17.3"` | 起動する Logstash のコンテナイメージ版数を指定します。 | 未設定又は誤設定の場合, 想定外の版数差異により互換性問題が発生するためです。 |
| 5-6 | `logstash_beats_port: 5044`, `logstash_http_port: 9600` | beats 入力待受と HTTP 監視用待受を設定し, 送信元接続と監視確認を可能にします。 | 未設定又は誤設定の場合, 送信元エージェントからの接続又は状態確認が失敗するためです。 |
| 7 | `logstash_pipeline_id: "main"` | Logstash の pipeline ID を `main` に設定し, 既定の実行対象を設定します。 | pipeline ID が不一致の場合, 想定した設定ファイルが読み込まれず, 受信と転送が機能しないためです。 |
| 8-12 | `logstash_wait_host: "127.0.0.1"`, `logstash_wait_timeout: 120`, `logstash_wait_delay: 2`, `logstash_wait_sleep: 2`, `logstash_wait_retries: 5` | 起動確認の接続先と再試行条件を定義し, 起動直後の待受未完了を吸収して到達性を検証します。 | これらが未設定又は不適切な場合, 起動直後の一時的な応答遅延を異常と誤判定し, ロール実行が失敗するためです。 |

この例では, 本 playbook で導入する側の共通値を一箇所へ集約します。

## テンプレートと生成ファイル

| テンプレート | 生成先 (括弧内は規定) | 用途 | 主な内容 |
| --- | --- | --- | --- |
| `templates/logstash.conf.j2` | `{{ logstash_pipeline_dir }}/main.conf` (規定: `/srv/logstash/config/pipelines/main.conf`) | Logstash の pipeline を生成します。 | beats 入力, Elasticsearch 出力, 日次インデックス名。 |
| `templates/docker-compose.yml.j2` | `{{ logstash_compose_file }}` (規定: `/srv/logstash/docker-compose.yml`) | Logstash の Docker Compose 定義を生成します。 | コンテナイメージ, コンテナ名, ボリューム, ポート公開, ネットワーク。 |

`logstash.conf.j2` は, Logstash コンテナ内で使用する pipeline 定義を展開します。`docker-compose.yml.j2` は, コンテナイメージ, コンテナ名, ボリューム, ポート公開, ネットワークの設定ファイルを展開します。

## 展開されるコンテナの仕様

### ポート公開

| ホスト側待受 | コンテナ側待受 | プロトコル | 用途 |
| --- | --- | --- | --- |
| `{{ logstash_beats_port }}` (既定: `5044`) | `{{ logstash_beats_port }}` (既定: `5044`) | TCP | Filebeat と Metricbeat からのイベント送信を受け付けます。 |
| `{{ logstash_http_port }}` (既定: `9600`) | `{{ logstash_http_port }}` (既定: `9600`) | TCP | Logstash の HTTP 監視エンドポイントを対象ホスト側から利用可能にします。 |

`templates/docker-compose.yml.j2` では, Logstash コンテナのポートを次の形式で公開します。

- `{{ logstash_beats_port }}:{{ logstash_beats_port }}` (既定: `5044:5044`)
- `{{ logstash_http_port }}:{{ logstash_http_port }}` (既定: `9600:9600`)

既定値は, beats 入力待受と HTTP 監視待受を同じポート番号でホスト側へ公開し, 送信元接続と状態確認の双方を可能にする設定であることを意味します。

### ファイルバインド

`templates/docker-compose.yml.j2` では, ホスト側のファイルやディレクトリを以下のようにコンテナ内から使用可能とするように設定します。

| ホスト側 | コンテナ側 | モード | 用途 |
| --- | --- | --- | --- |
| `{{ logstash_pipeline_dir }}/main.conf` (既定: `/srv/logstash/config/pipelines/main.conf`) | `/usr/share/logstash/pipeline/logstash.conf` | `ro` | ホスト側の pipeline 定義をコンテナ内から参照可能にします。コンテナ内から当該のファイルを破壊不可能なように読み取り専用でコンテナ側に公開します。 |
| `{{ logstash_data_dir }}` (既定: `/srv/logstash/data`) | `/usr/share/logstash/data` | `rw` | キューや内部状態を永続化し, コンテナの再作成時でも内部状態を継続的に利用可能にします。 |
| `{{ logstash_logs_dir }}` (既定: `/srv/logstash/logs`) | `/usr/share/logstash/logs` | `rw` | Logstash のログを永続化し, コンテナの動作が停止した場合でもホスト上からログ情報を参照可能にします。 |

既定値は, pipeline 定義をホスト上の `/srv/logstash/config/pipelines/main.conf` から読み込み, データをホスト上の `/srv/logstash/data`, ログをホスト上の `/srv/logstash/logs` に保存する設定です。

### ネットワーク定義

`templates/docker-compose.yml.j2` では, `elastic_backend` ネットワークを定義し, `external: true` で既存ネットワークを利用します。実体として参照するネットワーク名は `{{ logstash_network_name }}` (既定: `elastic-backend`) です。

既定値は, `elastic-backend` という外部ネットワーク(ホスト側ネットワーク)へ Logstash コンテナを参加させるためのネットワークを作成し, 同一のホスト側ネットワークを通して, 関連コンテナと通信する設定です。なお, `elastic-backend` が既に存在する場合は, 既設の `elastic-backend` ネットワークを使用します。

### ファイルバインドに関する補足事項

- 本ロールは, pipeline 定義, データ, ログの保存先をホスト側へ分離し, コンテナ再作成後もデータを保持することを保証します。
- 本ロールは, pipeline 定義を読み取り専用でコンテナへ渡し, コンテナ内の処理によって設定ファイルが書き換わらないことを保証します。
- 本ロールは, 規定値を使用する場合に `/srv/logstash` 配下へ設定, データ, ログを集約し, 配置先の一貫性を維持することを保証します。

### 公開ポートに関する補足事項

- 本ロールは, beats 入力ポートの公開により Filebeat と Metricbeat からイベントを受信可能にすることを保証します。
- 本ロールは, 起動後に HTTP 監視ポート経由で接続確認を実施し, `http://127.0.0.1:9600/` が応答することで Logstash が利用可能な状態になることを確認, 保証します。
- 規定値を使用する場合は beats 入力を `5044`, HTTP 監視待受を `9600` で公開します。外部公開範囲を調整したい場合は, ホスト側ファイアウォールや公開経路で制御することを検討してください。

## 実行フロー

1. [tasks/load-params.yml](tasks/load-params.yml) で OS 別パラメータと共通変数を読み込みます。
2. [tasks/validate.yml](tasks/validate.yml) で導入前提, パス, コンテナイメージ名, ポート, OS 条件を確認します。
3. [tasks/package.yml](tasks/package.yml) で Docker Compose が利用可能であることを確認します。
4. [tasks/directory.yml](tasks/directory.yml) で compose 用ディレクトリと設定, pipeline, データ, ログの配置先を作成します。
5. [tasks/user_group.yml](tasks/user_group.yml) で実行ユーザとグループを作成し, ディレクトリ所有権を調整します。
6. [tasks/config.yml](tasks/config.yml) で [templates/logstash.conf.j2](templates/logstash.conf.j2) と [templates/docker-compose.yml.j2](templates/docker-compose.yml.j2) を配置します。設定ファイルまたは Compose 定義の更新時は `logstash_restart_service` を通知し, [handlers/main.yml](handlers/main.yml) から読み込む [handlers/restart-service.yml](handlers/restart-service.yml) でコンテナを再作成します。
7. [tasks/service.yml](tasks/service.yml) で backend 専用ネットワークを確認または作成し, `docker compose up -d --remove-orphans` により Logstash コンテナを起動します。
8. [tasks/verify.yml](tasks/verify.yml) で `wait_for` による HTTP 監視ポート待機と, `uri` による `/` の応答確認を実施し, HTTP 応答が 200 であることを検証します。

## 検証ポイント

### 検証の前提条件

検証を始める前に, 次の条件が満たされていることを確認します。

- 対象ホストで Docker と Docker Compose が利用できること。
- `logstash_beats_port` と `logstash_http_port` に設定したポートが他のサービスで使われていないこと。
- `logstash_compose_dir` 配下を作成できること。
- `logging_backend` グループに対象ホストが登録されていること。
- backend 用ネットワーク上で `elasticsearch` 名が解決できること。

### 検証環境の設定

検証用の host_vars と vars/all-config.yml を次の値で整えます。

```yaml
1: logstash_compose_dir: "/srv/logstash"
2: logstash_network_name: "elastic-backend"
3: logstash_beats_port: 5044
4: logstash_http_port: 9600
5: logstash_pipeline_id: "main"
6: logstash_wait_host: "127.0.0.1"
7: logstash_wait_delegate_to: "{{ inventory_hostname }}"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `logstash_compose_dir: "/srv/logstash"` | 検証時に生成される設定, データ, ログの保存先を `/srv/logstash` 基準へ統一します。 | 保存先が分散すると検証対象ファイルの追跡が困難になり, 検証漏れが発生するためです。 |
| 2 | `logstash_network_name: "elastic-backend"` | 検証対象の Logstash を想定ネットワークへ参加させ, 関連コンテナとの通信経路を確立します。 | ネットワーク名不一致により接続検証が失敗し, 問題の原因切り分けが困難になるためです。 |
| 3-4 | `logstash_beats_port: 5044`, `logstash_http_port: 9600` | beats 入力待受と HTTP 監視待受を設定し, 送信元接続確認と状態確認を実行可能にします。 | ポートが不一致の場合, 送信元エージェントからの接続又は監視確認が失敗するためです。 |
| 5 | `logstash_pipeline_id: "main"` | 既定の pipeline ID を設定し, main.conf を実行対象として読み込ませます。 | pipeline ID が不適切な場合, 想定した入出力定義が反映されないためです。 |
| 6-7 | `logstash_wait_host: "127.0.0.1"`, `logstash_wait_delegate_to: "{{ inventory_hostname }}"` | 対象ホスト自身から `127.0.0.1` 宛に起動確認を実行します。 | 接続元又は接続先が不適切な場合, Logstash が起動済みでも待受確認が失敗し, 誤検知を招くためです。 |

この設定により, 本 playbook で導入する Logstash が対象ホスト上で待受し, 自己確認が可能になります。

### 検証コマンドと期待結果

#### 1. Logstash beats 待受確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
ss -ltn | grep ':5044 '
```

**期待される出力**:

```plaintext
LISTEN 0 4096 *:5044 *:*
```

**実行結果の例**:
```bash
$ ss -ltn | grep ':5044 '
LISTEN 0      4096         0.0.0.0:5044       0.0.0.0:*
LISTEN 0      4096            [::]:5044          [::]:*
```

**確認ポイント**:

- TCPプロトコルのポート番号5044番 が待受状態であること。
- beats 入力待受ポートとして公開されていること。

#### 2. Logstash HTTP 応答確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
curl -sS http://127.0.0.1:9600/
```

**期待される出力**:

```plaintext
{"host":"...","version":"8.17.3",...}
```

**実行結果の例**:
```bash
$ curl -sS http://127.0.0.1:9600/
{"host":"c0cfa45331f8","version":"8.17.3","http_address":"0.0.0.0:9600","id":"c5eb4ff1-e652-47a0-b3e0-f6449bf436e2","name":"c0cfa45331f8","ephemeral_id":"260fb682-44b1-4088-9e54-1377aa5b1498","snapshot":false,"status":"green","pipeline":{"workers":4,"batch_size":125,"batch_delay":50},"build_date":"2025-02-26T13:40:17+00:00","build_sha":"08b22ef499e2199e5976680090bae22ddd6174ba","build_snapshot":false}
```

**確認ポイント**:

- `http://127.0.0.1:9600/` へ接続できること。
- 応答本文に `host` や `version` が含まれること。

### 異常時の確認項目

#### 1. ポート競合の確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
ss -ltnp | grep -E ':5044 |:9600 '
```

**確認ポイント**:

- TCPプロトコルのポート番号5044番 と 9600番 が待受状態であること。
- Logstash コンテナの公開ポートとして待受していること。
- 想定外の別プロセスが同一ポートを占有していないこと。

#### 2. ネットワーク作成状態の確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
docker network ls --format '{{.Name}}' | grep -x 'elastic-backend'
```

**確認ポイント**:

- `logstash_network_name` の設定先ネットワークが存在すること。
- 規定値を使用する場合は, `elastic-backend` が存在すること。

#### 3. pipeline 定義生成状態の確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
ls -l /srv/logstash/config/pipelines/main.conf
```

**確認ポイント**:

- pipeline 定義ファイルが存在すること。
- 規定値を使用する場合の確認先は `/srv/logstash/config/pipelines/main.conf` であること。
- ファイルが 0 バイトではないこと。

#### 4. Docker Compose 定義生成状態の確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
ls -l /srv/logstash/docker-compose.yml
```

**確認ポイント**:

- `logstash_compose_file` に設定したファイルが存在すること。
- 規定値を使用する場合の確認先は `/srv/logstash/docker-compose.yml` であること。
- ファイルが 0 バイトではないこと。

#### 5. コンテナログのエラー確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
docker logs --tail 200 logstash
```

**確認ポイント**:

- pipeline 定義ファイルの読込失敗, 起動失敗, Elasticsearch 接続失敗に関するエラーメッセージが出ていないこと。
- `logstash_container_name` を変更している場合は, 変更後のコンテナ名を指定して確認すること。

## トラブルシューティング

### 1. Logstash が起動しない場合

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
docker ps -a --filter name=logstash
docker logs --tail 200 logstash
docker compose -f /srv/logstash/docker-compose.yml config
ls -ld /srv/logstash /srv/logstash/config /srv/logstash/config/pipelines /srv/logstash/data /srv/logstash/logs
```

**確認ポイント**:

- コンテナ状態が `Up` であること。
- ログに設定読込失敗, イメージ取得失敗, 起動失敗が出ていないこと。
- Compose 定義の構文確認が成功すること。
- 規定値を使用する場合, `/srv/logstash` 配下へ読み書き可能な権限があること。

### 2. beats 入力を受信できない場合

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
ss -ltnp | grep ':5044 '
docker logs --tail 200 logstash
```

**確認ポイント**:

- TCPプロトコルのポート番号5044番 で待受していること。
- ログに beats 入力初期化失敗が出ていないこと。
- Filebeat と Metricbeat 側の送信先設定と一致していること。

### 3. HTTP 監視ポートが応答しない場合

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
docker ps --filter name=logstash
ss -ltnp | grep ':9600 '
curl -v --max-time 5 http://127.0.0.1:9600/
```

**確認ポイント**:

- Logstash コンテナが起動中であること。
- TCPプロトコルのポート番号9600番 で待受していること。
- `curl` が接続エラーではなく HTTP 応答を返すこと。

### 4. Elasticsearch へ転送できない場合

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
docker exec logstash curl -sS http://elasticsearch:9200/
docker logs --tail 200 logstash
```

**確認ポイント**:

- Logstash コンテナ内から `http://elasticsearch:9200/` へ到達できること。
- backend 用ネットワーク上で Elasticsearch 名が解決できること。
- ログに出力先 URL の誤り又は名前解決失敗が出ていないこと。

## 注意事項

- 既存のサービスで使用されているポートやディレクトリと衝突しないような設定を実施すること。
- ネットワーク名と compose project 名を他の Docker Compose から展開されるコンテナと衝突しないようにすること。
- `logstash_data_dir` と `logstash_logs_dir` の所有者は, Logstashコンテナイメージで決まっている実行ユーザIDと実行グループID(既定値は 1000:1000)に合わせること。これらの値は運用で自由に決める値ではないため, コンテナイメージの仕様が変わったときだけ変更する。実行ユーザIDを変える場合は `logstash_user_id` 変数を修正し, 実行グループIDを変える場合は `logstash_group_id` 変数を修正する。
- 本ロールでは, pipeline の送信先として `http://elasticsearch:9200` を使用する。pipeline の送信先を変更する場合は, 次を満たすように設定すること:
  1. (`vars/all-config.yml` などで), `logstash_network_name` 変数の設定値と Elasticsearch ロール側のネットワーク名(`elastic_search_network_name` 変数の設定値)を同じ値に設定すること(既定値は `elastic-backend`)。
  2. `inventory/hosts` の `logging_backend` グループに Elasticsearch ロールを適用する対象ホストを登録すること。
  3. (`vars/all-config.yml` などで), `elastic_search_container_name` 変数に pipeline の送信先のホスト名部分(規定値の場合, `elasticsearch` に相当する部分)を設定すること。なお, 本変数で指定するホスト名は, コンテナ間通信で使用する名前であり, 対象ホストのホスト名ではないことに留意すること。
- 出力先インデックス名は日次で分割されるため, 保持期間や削除運用は Elasticsearch 側の運用方針と整合させること。

## 参考資料

### 公式ドキュメント

- [Logstash Reference](https://www.elastic.co/guide/en/logstash/8.17/index.html)
- [Logstash configuration files](https://www.elastic.co/guide/en/logstash/8.17/config-setting-files.html)
- [Docker Compose documentation](https://docs.docker.com/compose/)
- [Ansible documentation](https://docs.ansible.com/ansible/latest/)

### 関連ロール

- [roles/elasticsearch/Readme.md](../elasticsearch/Readme.md) Elasticsearch関連コンポーネント全体の仕様についての解説を記載しています。以下の内容について確認する場合に参照します。
	- 設計背景と非干渉条件
	- Elasticsearch 関連コンポーネント構成図
	- 各コンテナの役割分担
	- inventory group と展開されるコンテナとの対応関係
