# Kibana ロール

本ロールは, 本 playbook で導入する Kibana を, 本 playbook で導入する Elasticsearch, Logstash, Filebeat, Metricbeat と組み合わせて運用するためのロールです。

## 目次

- [Kibana ロール](#kibana-ロール)
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
      - [1. Kibana 待受確認](#1-kibana-待受確認)
      - [2. Kibana 状態確認](#2-kibana-状態確認)
    - [異常時の確認項目](#異常時の確認項目)
      - [1. ポート競合の確認](#1-ポート競合の確認)
      - [2. ネットワーク作成状態の確認](#2-ネットワーク作成状態の確認)
      - [3. 設定ファイル生成状態の確認](#3-設定ファイル生成状態の確認)
      - [4. Docker Compose 定義生成状態の確認](#4-docker-compose-定義生成状態の確認)
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
| Kibana | - | Elasticsearchに保存されたデータを可視化し, 参照するソフトウェア。 |
| Elasticsearch | - | 検索と集約を担当するサーバソフトウェア。 |
| Logstash | - | 受信したデータを整形し, 送信先へ転送するソフトウェア。 |
| Filebeat | - | ログファイルを収集し, 送信先へ転送するエージェント。 |
| Metricbeat | - | メトリクスを収集して送信するエージェント。 |
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
| Fully Qualified Domain Name | FQDN | 末尾まで省略せず書いた完全なドメイン名。 |
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
| jqコマンド | jq | JSON 形式のデータから必要な項目だけを抽出して表示するコマンド。 |
## 概要

### 前提条件

本 playbook を実行する前提条件は, 次のとおりです。

- 対象ホストが, `inventory/hosts` ファイル中の `logging_backend` グループに登録されていること。
- 対象ホストの OS は, Debian 系又は RHEL 系であること。
- 対象ホストで Docker と Docker Compose が利用可能であること。
- 対象ホストで `sudo` によるディレクトリ作成とコンテナ起動が可能であること。
- `kibana_server_port` に設定するポート番号が, 既存サービスで使用するポート番号と競合しないこと。

### 基本仕様

本ロールの Kibana 導入処理の仕様は, 次のとおりです:

- コンテナイメージは `docker.elastic.co/kibana/kibana:8.17.3` を使用すること。
- Kibana は `0.0.0.0:5601` で待受し, TCPプロトコルのポート番号5601番 を使用すること。
- 設定, データ, ログは, 本 playbook で導入する専用ディレクトリへ分離すること。
- Kibana は, 本 playbook で導入する backend 用ネットワークへ参加すること。
- Kibana から接続する Elasticsearch の接続先は, `elastic_search_container_name` と `elastic_search_http_port` から内部的に生成し, ロールの利用者の設定変更誤りが生じにくい動作とすること。

### 本ロールで実施する主な処理

本ロールでは, 次の処理を実施します。

1. `docker compose` が利用可能であることを確認します。
2. 本 playbook で導入するディレクトリを作成します。
3. Kibana の設定ファイルと Docker Compose 定義を生成します。
4. backend 用ネットワークへ接続して Kibana コンテナを起動します。
5. 起動後にポート待機と HTTP 応答確認を行います。

## 実行方法

### Makefile ターゲットによる実行

制御ホストで次のコマンドを実行します。

```bash
make run_logging_backend
```

このターゲットは logging backend 用 Playbook の実行導線として用意されています。現状の Kibana 単独適用は, 次節の `ansible-playbook` による実行手順を使用します。

### ansible-playbook による role 単位実行

制御ホストで次のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts logging-backend.yml --tags kibana
```

このコマンドは, `logging_backend` グループに対して Kibana ロールのみを実行します。

## 主要変数

### 基本設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `logging_kibana_enabled` | Kibana ロールの有効化フラグ。 | `true` | `true` |
| `kibana_compose_dir` | Docker Compose 定義と関連ファイルを配置するディレクトリ。 | `/srv/kibana` | `/srv/kibana` |
| `kibana_compose_file` | Docker Compose 定義のファイルパス。 | `{{ kibana_compose_dir }}/docker-compose.yml` | `/srv/kibana/docker-compose.yml` |
| `kibana_config_dir` | Kibana 関連の設定用ディレクトリ。 | `{{ kibana_compose_dir }}/config` | `/srv/kibana/config` |
| `kibana_data_dir` | Kibana データを配置するディレクトリ。 | `{{ kibana_compose_dir }}/data` | `/srv/kibana/data` |
| `kibana_logs_dir` | Kibana ログを配置するディレクトリ。 | `{{ kibana_compose_dir }}/logs` | `/srv/kibana/logs` |
| `kibana_network_name` | Docker ネットワーク名。 | `elastic-backend` | `elastic-backend` |
| `kibana_container_name` | Kibana コンテナ名。 | `kibana` | `kibana` |

### コンテナイメージと接続設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `kibana_image` | Kibana のコンテナイメージ名。 | `docker.elastic.co/kibana/kibana:8.17.3` | `docker.elastic.co/kibana/kibana:8.17.3` |
| `kibana_server_host` | Kibana の HTTP 待受アドレス。 | `0.0.0.0` | `0.0.0.0` |
| `kibana_server_port` | Kibana の HTTP 待受ポート。 | `5601` | `5601` |

### 起動検証関連設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `kibana_wait_host` | 起動確認で待機する接続先ホスト。 | `127.0.0.1` | `127.0.0.1` |
| `kibana_wait_delegate_to` | 起動確認を実行する接続元ホスト。 | `localhost` | `localhost` |
| `kibana_wait_timeout` | 起動確認のタイムアウト時間。 | `120` | `120` |
| `kibana_wait_delay` | 起動確認の開始遅延時間。 | `2` | `2` |
| `kibana_wait_sleep` | 起動確認の待機間隔。 | `2` | `2` |
| `kibana_wait_retries` | 起動確認の再試行回数。 | `5` | `5` |

### 変数設定例

#### host_vars の設定例

ホスト固有に変える値を `host_vars/kibana01.local.yml` に記載します。

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

```yaml
1: logging_kibana_enabled: true
2: kibana_compose_dir: "/srv/kibana"
3: kibana_network_name: "elastic-backend"
4: kibana_image: "docker.elastic.co/kibana/kibana:8.17.3"
5: kibana_server_host: "0.0.0.0"
6: kibana_server_port: 5601
7: kibana_wait_host: "127.0.0.1"
8: kibana_wait_timeout: 120
9: kibana_wait_delay: 2
10: kibana_wait_sleep: 2
11: kibana_wait_retries: 5
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `logging_kibana_enabled: true` | Kibana ロールを有効化し, 共通設定にもとづく導入処理を実行します。 | `false` の場合は共通設定が存在しても導入処理が実行されず, 設定の反映漏れが発生するためです。 |
| 2 | `kibana_compose_dir: "/srv/kibana"` | Docker Compose 定義, 設定, データ, ログの保存先基準ディレクトリを `/srv/kibana` に統一します。 | 未設定又は誤設定の場合, 生成先の分散や競合が発生し, 保守作業で誤操作が起きやすくなるためです。 |
| 3 | `kibana_network_name: "elastic-backend"` | Kibana が参加する外部ネットワーク名を `elastic-backend` に設定します。 | 関連コンテナ群と異なるネットワーク名を設定した場合, 相互接続に失敗するためです。 |
| 4 | `kibana_image: "docker.elastic.co/kibana/kibana:8.17.3"` | 起動する Kibana のコンテナイメージ版数を指定します。 | 未設定又は誤設定の場合, 想定外の版数差異により互換性問題が発生するためです。 |
| 5-6 | `kibana_server_host: "0.0.0.0"`, `kibana_server_port: 5601` | Kibana の HTTP 待受を `0.0.0.0:5601` に設定し, 対象ホストから利用可能にします。 | 未設定又は誤設定の場合, 待受先アドレスやポートが期待値と一致せず, 接続確認が失敗するためです。 |
| 7-11 | `kibana_wait_host: "127.0.0.1"`, `kibana_wait_timeout: 120`, `kibana_wait_delay: 2`, `kibana_wait_sleep: 2`, `kibana_wait_retries: 5` | 起動確認の接続先と再試行条件を定義し, 起動直後の待受未完了を吸収して到達性を検証します。 | これらが未設定又は不適切な場合, 起動直後の一時的な応答遅延を異常と誤判定し, ロール実行が失敗するためです。 |

この例では, 本 playbook で導入する側の共通値を一箇所へ集約します。

## テンプレートと生成ファイル

| テンプレート | 生成先 (括弧内は規定) | 用途 | 主な内容 |
| --- | --- | --- | --- |
| `templates/kibana.yml.j2` | `{{ kibana_compose_dir }}/kibana.yml` (規定: `/srv/kibana/kibana.yml`) | Kibana の設定ファイルを生成します。 | 待受アドレス, 待受ポート, Elasticsearch 接続先。 |
| `templates/docker-compose.yml.j2` | `{{ kibana_compose_file }}` (規定: `/srv/kibana/docker-compose.yml`) | Kibana の Docker Compose 定義を生成します。 | コンテナイメージ, コンテナ名, ボリューム, ポート公開, ネットワーク。 |

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

既定値は, `elastic-backend` という外部ネットワーク(ホスト側ネットワーク)へ Kibana コンテナを参加させるためのネットワークを作成し, 同一のホスト側ネットワークを通して, 関連コンテナと通信する設定です。なお, `elastic-backend` が既に存在する場合は, 既設の `elastic-backend` ネットワークを使用します。

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
3. [tasks/package.yml](tasks/package.yml) で Docker Compose が利用可能であることを確認します。
4. [tasks/directory.yml](tasks/directory.yml) で compose 用ディレクトリと設定, データ, ログの配置先を作成します。
5. [tasks/user_group.yml](tasks/user_group.yml) で実行ユーザとグループを作成し, ディレクトリ所有権を調整します。
6. [tasks/config.yml](tasks/config.yml) で [templates/kibana.yml.j2](templates/kibana.yml.j2) と [templates/docker-compose.yml.j2](templates/docker-compose.yml.j2) を配置します。設定ファイルまたは Compose 定義の更新時は `kibana_restart_service` を通知し, [handlers/main.yml](handlers/main.yml) から読み込む [handlers/restart-service.yml](handlers/restart-service.yml) でコンテナを再作成します。
7. [tasks/service.yml](tasks/service.yml) で backend 専用ネットワークを確認または作成し, `docker compose up -d --remove-orphans` により Kibana コンテナを起動します。
8. [tasks/verify.yml](tasks/verify.yml) で `wait_for` によるポート待機と, `uri` による `/api/status` の応答確認を実施し, `status.overall.state` または `status.overall.level` が `yellow`, `green`, `available` のいずれかであることを検証します。

## 検証ポイント

### 検証の前提条件

検証を始める前に, 次の条件が満たされていることを確認します。

- 対象ホストで Docker と Docker Compose が利用できること。
- `kibana_server_port` に設定したポートが他のサービスで使われていないこと。
- `kibana_compose_dir` 配下を作成できること。
- `logging_backend` グループに対象ホストが登録されていること。

### 検証環境の設定

検証用の host_vars と vars/all-config.yml を次の値で整えます。

```yaml
1: kibana_compose_dir: "/srv/kibana"
2: kibana_network_name: "elastic-backend"
3: kibana_server_host: "0.0.0.0"
4: kibana_server_port: 5601
5: kibana_wait_host: "127.0.0.1"
6: kibana_wait_delegate_to: "{{ inventory_hostname }}"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `kibana_compose_dir: "/srv/kibana"` | 検証時に生成される設定, データ, ログの保存先を `/srv/kibana` 基準へ統一します。 | 保存先が分散すると検証対象ファイルの追跡が困難になり, 検証漏れが発生するためです。 |
| 2 | `kibana_network_name: "elastic-backend"` | 検証対象の Kibana を想定ネットワークへ参加させ, 関連コンテナとの通信経路を確立します。 | ネットワーク名不一致により接続検証が失敗し, 問題の原因切り分けが困難になるためです。 |
| 3-4 | `kibana_server_host: "0.0.0.0"`, `kibana_server_port: 5601` | `0.0.0.0:5601` で待受し, HTTP 接続確認を実行可能にします。 | 待受先アドレス又はポートが不一致の場合, 検証コマンドが接続不能となり, 導入結果を判定できないためです。 |
| 5-6 | `kibana_wait_host: "127.0.0.1"`, `kibana_wait_delegate_to: "{{ inventory_hostname }}"` | 対象ホスト自身から `127.0.0.1` 宛に起動確認を実行します。 | 接続元又は接続先が不適切な場合, Kibana が起動済みでも待受確認が失敗し, 誤検知を招くためです。 |

この設定により, 本 playbook で導入する Kibana が対象ホスト上で待受し, 自己確認が可能になります。

### 検証コマンドと期待結果

#### 1. Kibana 待受確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

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

**コマンド**:

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

### 異常時の確認項目

#### 1. ポート競合の確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
ss -ltnp | grep ':5601 '
```

**確認ポイント**:

- TCPプロトコルのポート番号5601番 が待受状態であること。
- Kibana コンテナの公開ポートとして待受していること。
- 想定外の別プロセスが同一ポートを占有していないこと。

#### 2. ネットワーク作成状態の確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
docker network ls --format '{{.Name}}' | grep -x 'elastic-backend'
```

**確認ポイント**:

- `kibana_network_name` の設定先ネットワークが存在すること。
- 規定値を使用する場合は, `elastic-backend` が存在すること。

#### 3. 設定ファイル生成状態の確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
ls -l /srv/kibana/kibana.yml
```

**確認ポイント**:

- Kibana の設定ファイルが存在すること。
- 規定値を使用する場合の確認先は `/srv/kibana/kibana.yml` であること。
- ファイルが 0 バイトではないこと。

#### 4. Docker Compose 定義生成状態の確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
ls -l /srv/kibana/docker-compose.yml
```

**確認ポイント**:

- `kibana_compose_file` に設定したファイルが存在すること。
- 規定値を使用する場合の確認先は `/srv/kibana/docker-compose.yml` であること。
- ファイルが 0 バイトではないこと。

#### 5. コンテナログのエラー確認

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
docker logs --tail 200 kibana
```

**確認ポイント**:

- 設定読込失敗, 起動失敗, Elasticsearch 接続失敗に関するエラーメッセージが出ていないこと。
- `kibana_container_name` を変更している場合は, 変更後のコンテナ名を指定して確認すること。

## トラブルシューティング

### 1. Kibana が起動しない場合

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
docker ps -a --filter name=kibana
docker logs --tail 200 kibana
docker compose -f /srv/kibana/docker-compose.yml config
ls -ld /srv/kibana /srv/kibana/data /srv/kibana/logs
```

**確認ポイント**:

- コンテナ状態が `Up` であること。
- ログに設定読込失敗, イメージ取得失敗, 起動失敗が出ていないこと。
- Compose 定義の構文確認が成功すること。
- 規定値を使用する場合, `/srv/kibana` 配下へ読み書き可能な権限があること。

### 2. `curl` で応答しない場合

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
docker ps --filter name=kibana
ss -ltnp | grep ':5601 '
curl -v --max-time 5 http://127.0.0.1:5601/
```

**確認ポイント**:

- Kibana コンテナが起動中であること。
- TCPプロトコルのポート番号5601番 で待受していること。
- `curl` が接続エラーではなく HTTP 応答を返すこと。

### 3. Kibana 状態が `green`, `yellow`, `available` にならない場合

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
curl -sS http://127.0.0.1:5601/api/status | jq '.status.overall'
docker logs --tail 200 kibana
```

**確認ポイント**:

- `status.overall.state` または `status.overall.level` が `red` ではないこと。
- ログに起動時エラー又は Elasticsearch 接続失敗が出ていないこと。

### 4. Elasticsearch へ接続できない場合

**実施対象ホスト**: `logging_backend` グループに属する対象ホスト

**コマンド**:

```bash
docker exec kibana curl -sS http://elasticsearch:9200/
docker logs --tail 200 kibana
```

**確認ポイント**:

- Kibana コンテナ内から `http://{{ elastic_search_container_name }}:{{ elastic_search_http_port }}` で示される接続先へ到達できること。
- backend 用ネットワーク上で Elasticsearch 名が解決できること。
- ログに接続先 URL の誤り又は名前解決失敗が出ていないこと。

## 注意事項

- 既存のサービスで使用されているポートやディレクトリと衝突しないような設定を実施すること。
- ネットワーク名と compose project 名を他の Docker Compose から展開されるコンテナと衝突しないようにすること。
- `kibana_data_dir` と `kibana_logs_dir` の所有者は, Kibanaコンテナイメージ仕様で固定される実行ユーザIDと実行グループID(既定では 1000:1000)に合わせること。これらの値はコンテナイメージ仕様により決定されるため, コンテナイメージの仕様変更に伴って変更が必要となる。実行ユーザIDは, `kibana_user_id` 変数, 実行グループIDは, `kibana_group_id` 変数を修正することで変更する。
- Kibana の Elasticsearch 接続先は内部変数として導出する設計であるため, 接続先を変更する場合は `elastic_search_container_name` 又は `elastic_search_http_port` を変更すること。
- 設定ファイル生成先は `/srv/kibana/config` ではなく `/srv/kibana/kibana.yml` であるため, 運用確認時の参照先を取り違えないこと。

## 参考資料

### 公式ドキュメント

- [Kibana Guide](https://www.elastic.co/guide/en/kibana/8.17/index.html)
- [Kibana settings](https://www.elastic.co/guide/en/kibana/8.17/settings.html)
- [jq Manual](https://jqlang.github.io/jq/manual/)
- [Docker Compose documentation](https://docs.docker.com/compose/)
- [Ansible documentation](https://docs.ansible.com/ansible/latest/)

### 関連ロール

- [roles/elasticsearch/Readme.md](../elasticsearch/Readme.md) Elasticsearch関連コンポーネント全体の仕様についての解説を記載しています。以下の内容について確認する場合に参照します。
  - 設計背景と非干渉条件
  - Elasticsearch 関連コンポーネント構成図
  - 各コンテナの役割分担
  - inventory group と展開されるコンテナとの対応関係
