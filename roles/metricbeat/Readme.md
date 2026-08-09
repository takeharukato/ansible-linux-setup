# Metricbeat ロール

本ロールは, logging_collector グループの対象ホストへ Metricbeat を導入し, 対象ホストのメトリクスを Logstash へ送信するためのロールです。

## 目次

- [Metricbeat ロール](#metricbeat-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
    - [前提条件](#前提条件)
    - [基本仕様](#基本仕様)
    - [本ロールで実施する主な処理](#本ロールで実施する主な処理)
  - [実行方法](#実行方法)
    - [Makefile ターゲットを使用する場合](#makefile-ターゲットを使用する場合)
    - [ansible-playbookコマンドを使用する場合](#ansible-playbookコマンドを使用する場合)
  - [主要変数](#主要変数)
    - [基本設定](#基本設定)
    - [収集設定](#収集設定)
      - [`logging_backend_host`, `filebeat_backend_host`, `metricbeat_backend_host`の設定値に関する留意事項](#logging_backend_host-filebeat_backend_host-metricbeat_backend_hostの設定値に関する留意事項)
    - [起動検証関連設定](#起動検証関連設定)
    - [変数設定例](#変数設定例)
      - [host\_vars の設定例](#host_vars-の設定例)
      - [vars/all-config.yml の設定例](#varsall-configyml-の設定例)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [展開されるサービスの仕様](#展開されるサービスの仕様)
    - [ポート公開](#ポート公開)
    - [ファイル/ディレクトリ構成](#ファイルディレクトリ構成)
    - [サービス起動処理に関する補足事項](#サービス起動処理に関する補足事項)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [検証の前提条件](#検証の前提条件)
    - [検証環境の設定](#検証環境の設定)
    - [検証コマンドと期待結果](#検証コマンドと期待結果)
      - [1. Metricbeat サービス状態確認](#1-metricbeat-サービス状態確認)
      - [2. Metricbeat HTTP 応答確認](#2-metricbeat-http-応答確認)
      - [3. Logstash 送信先到達確認](#3-logstash-送信先到達確認)
    - [異常時の確認項目](#異常時の確認項目)
      - [1. ポート競合の確認](#1-ポート競合の確認)
      - [2. 設定ファイル生成状態の確認](#2-設定ファイル生成状態の確認)
      - [3. systemd unit 定義生成状態の確認](#3-systemd-unit-定義生成状態の確認)
      - [4. 設定ファイルの配置状態確認](#4-設定ファイルの配置状態確認)
      - [5. サービスログのエラー確認](#5-サービスログのエラー確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. Metricbeat が起動しない場合](#1-metricbeat-が起動しない場合)
    - [2. HTTP 監視ポートが応答しない場合](#2-http-監視ポートが応答しない場合)
    - [3. メトリクス収集が進まない場合](#3-メトリクス収集が進まない場合)
    - [4. Logstash へ送信できない場合](#4-logstash-へ送信できない場合)
  - [注意事項](#注意事項)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)
    - [関連ロール](#関連ロール)

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Metricbeat | - | メトリクスを収集して送信するエージェント。 |
| Logstash | - | 受信したデータを整形し, 送信先へ転送するソフトウェア。 |
| Elasticsearch | - | 検索と集約を担当するサーバソフトウェア。 |
| Kibana | - | Elasticsearchに保存されたデータを可視化し, 参照するソフトウェア。 |
| メトリクス | - | ホストやサービスの状態を数値で表した観測情報。 |
| system module | - | Metricbeat が OS の基本情報を取得するためのモジュール。 |
| processor | - | 収集したイベントへ追加情報を付与する変換処理。 |
| collector | - | 収集起点を識別するためにイベントへ付与する固定値。 |
| systemd | - | Linux でサービスの起動, 停止, 自動起動を管理する仕組み。 |
| ローカルパッケージ | - | 本ロールでソースから生成し, 対象ホストへ導入する deb または rpm パッケージ。 |
| package build host | - | ローカルパッケージの構築処理を実行するホスト。 |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| Playbook | - | 自動化処理の実行手順を記述したファイル。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| inventory/hostsファイル | - | Ansible Inventory の実体ファイルとして, 実行対象ホストの一覧と接続情報を定義するファイル。 |
| ansible_host | - | Ansible が対象ホストへ接続するときに使用する接続先アドレス(IPアドレス又はFQDN)を指定する変数。 |
| inventory group | - | Ansible Inventory内で同じ役割の対象ホストをまとめる識別単位。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| ホスト | - | 管理対象として識別される個別の計算機。 |
| サーバ | - | 他の機器や利用者へ機能やデータを提供する計算機, 又はその役割。 |
| ネットワーク | - | 機器同士を接続してデータをやり取りする仕組み。 |
| ディレクトリ | - | ファイルを階層的に整理するための入れ物。 |
| データ | - | 処理や保存の対象となる情報。 |
| ログ | - | 処理の結果や状態を時系列で記録した情報。 |
| ポート | - | 通信の出入口を識別する番号または接点。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| Fully Qualified Domain Name | FQDN | 末尾まで省略せず書いた完全なドメイン名。 |
| Hypertext Transfer Protocol | HTTP | World Wide Webで情報をやり取りする通信手順。 |
| Internet Protocol | IP | ネットワーク上で宛先を識別し, データを届けるための通信手順。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Linux | - | 多くの機器で使われる, 基本ソフトウェアの系統。 |
| Debian | - | コミュニティ主導で開発される Linux ディストリビューション。 |
| Red Hat | - | Red Hat Enterprise Linuxなどを提供する組織。 |
| Red Hat Enterprise Linux | RHEL | Red Hatが提供する企業向けLinuxディストリビューション。 |
| localhost | - | 同一機器自身を指す名前。 |
| root | - | Unix 系システムの最上位権限を持つ管理者識別子。 |
| ansible-playbookコマンド | ansible-playbook | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |
| makeコマンド | make | Makefile に定義された処理を実行するコマンド。 |
| curlコマンド | curl | URL を指定して通信結果を取得するコマンド。 |

## 概要

Metricbeat は, 対象ホストの CPU, メモリ, ファイルシステム, プロセス, ネットワークなどのメトリクスを収集し, Logstash へ転送します。本ロールは, package build host でローカルパッケージを生成して対象ホストへ導入し, systemd サービスとして Metricbeat を起動します。

### 前提条件

本 playbook を実行する前提条件は, 次のとおりです。

- 対象ホストが, inventory/hosts の logging_collector グループに登録されていること。
- 対象ホストの OS は, Debian 系又は RHEL 系であること。
- 制御ホストでコンテナランタイム (既定値は Docker) が利用可能であること。
- 制御ホストで package build host への接続が可能であること。
- logging_backend_host が定義され, かつ空文字列でない場合は, その値が名前解決可能であること。
- logging_backend_host が未定義又は空文字列の場合は, logging_backend グループに 1 台以上のホストが登録され, 先頭ホスト(又は先頭ホストの ansible_host)が名前解決可能であること。
- metricbeat_http_port に設定するポート番号が, 他サービスと競合しないこと。

### 基本仕様

本ロールで Metricbeat を導入する際の仕様は, 次のとおりです。

- package build host 上で Metricbeat のソースをビルドし, ローカルパッケージを生成して導入すること。
- Metricbeat は systemd サービスとして起動し, 再起動時に自動起動すること。
- HTTP 監視ポートは 0.0.0.0:5067 で待受すること。
- system module で対象ホストのメトリクスを収集すること。
- 送信先 Logstash は metricbeat_backend_host:metricbeat_backend_port を使用すること。
- 設定, データ, ログは, 本 playbook で導入する専用ディレクトリへ分離すること。

### 本ロールで実施する主な処理

本ロールでは, 次の処理を実施します。

1. load-params.yml で共通変数と OS 差分変数を読み込みます。
2. validate.yml で必須変数, ポート範囲, inventory group を検証します。
3. package.yml で Metricbeat ソースからローカルパッケージを構築し, 対象ホストへ導入します。
4. directory.yml で config, data, logs ディレクトリを作成します。
5. config.yml で Metricbeat 設定と systemd unit 定義を生成します。
6. service.yml で systemd サービスを起動します。
7. verify.yml で待受ポートと HTTP 応答を確認します。

## 実行方法

### Makefile ターゲットを使用する場合

制御ホストで次のコマンドを実行します。

```bash
make run_logging_collector
```

このターゲットは filebeat と metricbeat をまとめて実行します。

### ansible-playbookコマンドを使用する場合

制御ホストで次のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts logging-collector.yml --tags metricbeat
```

## 主要変数

### 基本設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| logging_metricbeat_enabled | Metricbeat ロールの有効化フラグ。 | true | true |
| metricbeat_version | 構築対象の Metricbeat 版数。 | v8.17.3 | v8.17.3 |
| metricbeat_build_host | パッケージ構築を実行するホスト名。 | localhost | localhost |
| metricbeat_config_dir | Metricbeat 設定ファイルを配置するディレクトリ。 | /etc/metricbeat | /etc/metricbeat |
| metricbeat_config_file | Metricbeat 設定ファイルのパス。 | {{ metricbeat_config_dir }}/metricbeat.yml | /etc/metricbeat/metricbeat.yml |
| metricbeat_data_dir | Metricbeat データを配置するディレクトリ。 | /var/lib/metricbeat | /var/lib/metricbeat |
| metricbeat_logs_dir | Metricbeat ログを配置するディレクトリ。 | /var/log/metricbeat | /var/log/metricbeat |
| metricbeat_systemd_unit_file | Metricbeat の systemd unit ファイルパス。 | /etc/systemd/system/metricbeat.service | /etc/systemd/system/metricbeat.service |

### 収集設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| metricbeat_http_host | Metricbeat HTTP 待受アドレス。 | 0.0.0.0 | 0.0.0.0 |
| metricbeat_http_port | Metricbeat HTTP 待受ポート。 | 5067 | 5067 |
| metricbeat_system_period | system module の収集周期。 | 10s | 10s |
| metricbeat_backend_host | 送信先 Logstash ホスト。 | 自動解決(logging_backend_host が設定済みならその値, 未設定又は空文字列なら `inventory/hosts` の `logging_backend` グループ先頭ホストの接続先アドレス, 接続先アドレス未指定時は先頭ホスト名)。| 192.168.10.20 |
| metricbeat_backend_port | 送信先 Logstash ポート。 | 5044 | 5044 |

#### `logging_backend_host`, `filebeat_backend_host`, `metricbeat_backend_host`の設定値に関する留意事項

`logging_backend_host` が未定義又は空文字列の場合は, `inventory/hosts` の `logging_backend` グループに記載された先頭ホストを送信先候補として使用します。
このとき, 先頭ホストに接続先アドレス(IPアドレス又はFQDN)を `ansible_host` パラメタによって明示されている場合はその値を使用し, 明示されていない場合は先頭ホスト名を使用します。
例えば, `inventory/hosts` の先頭ホストの行が `elastic-backend01 ansible_host=192.168.30.109` と記載されている場合は, `192.168.30.109` を使用し, `elastic-backend01`のように, `ansible_host` パラメタが未指定の場合は, `inventory/hosts`に記載されたホスト名(ansibleのインベントリホスト名)である `elastic-backend01` を使用します。

`logging_backend_host`, `filebeat_backend_host`, `metricbeat_backend_host` には, IPアドレス又はFQDNを指定してください。`*.local` などの multicast DNS 名は, 環境によって名前解決が不安定になるため指定しないことを推奨します。

### 起動検証関連設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| metricbeat_wait_host | 待受確認で接続するホスト。 | 127.0.0.1 | 127.0.0.1 |
| metricbeat_wait_timeout | 待受確認のタイムアウト時間。 | 120 | 120 |
| metricbeat_wait_delay | 待受確認の開始遅延時間。 | 2 | 2 |
| metricbeat_wait_sleep | 待受確認の待機間隔。 | 2 | 2 |
| metricbeat_wait_delegate_to | 待受確認を実行する接続元ホスト。 | localhost | localhost |
| metricbeat_wait_retries | 待受確認と応答確認の再試行回数。 | 5 | 5 |

### 変数設定例

#### host_vars の設定例

host_vars/logcollector01.local.yml にホスト固有値を設定します。

```yaml
1: logging_metricbeat_enabled: true
2: metricbeat_http_port: 5067
3: metricbeat_wait_delegate_to: "{{ inventory_hostname }}"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | logging_metricbeat_enabled: true | Metricbeat ロールを有効化し, 導入処理を実行します。 | false の場合はロールが実行されず, 収集を開始できないためです。 |
| 2 | metricbeat_http_port: 5067 | HTTP 監視ポートを 5067 に設定します。 | 未設定又は誤設定の場合は待受確認の接続先が一致せず, 検証が失敗するためです。 |
| 3 | metricbeat_wait_delegate_to: "{{ inventory_hostname }}" | 対象ホスト自身を接続元として待受確認を実行します。 | 接続不能な接続元を指定した場合, 起動済みでも待受確認が失敗するためです。 |

#### vars/all-config.yml の設定例

vars/all-config.yml に共通値を設定します。

```yaml
1: logging_metricbeat_enabled: true
2: metricbeat_version: "v8.17.3"
3: metricbeat_build_host: "localhost"
4: metricbeat_http_host: "0.0.0.0"
5: metricbeat_http_port: 5067
6: metricbeat_system_period: "10s"
7: metricbeat_backend_port: 5044
8: metricbeat_wait_host: "127.0.0.1"
9: metricbeat_wait_timeout: 120
10: metricbeat_wait_delay: 2
11: metricbeat_wait_sleep: 2
12: metricbeat_wait_retries: 5
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | logging_metricbeat_enabled: true | 全対象ホストで Metricbeat 導入処理を実行します。 | false の場合は共通設定を記述しても導入されないためです。 |
| 2 | metricbeat_version: "v8.17.3" | ソース構築と導入先パッケージの版数を統一します。 | 未設定又は誤設定の場合は想定外版数が導入され, 検証結果と運用状態が不一致になるためです。 |
| 3 | metricbeat_build_host: "localhost" | 制御ホストをパッケージ構築先として指定します。 | 到達不能ホストを指定した場合はローカルパッケージ構築が失敗するためです。 |
| 4-5 | metricbeat_http_host: "0.0.0.0", metricbeat_http_port: 5067 | HTTP 監視エンドポイントの待受先を明示します。 | 未設定又は誤設定の場合は待受先不一致で監視確認に失敗するためです。 |
| 6 | metricbeat_system_period: "10s" | system module の収集周期を 10 秒に設定します。 | 過小値では対象ホスト負荷が増加し, 過大値では監視の遅延が大きくなるためです。 |
| 7 | metricbeat_backend_port: 5044 | Logstash 送信先ポートを指定します。 | 送信先ポートが不一致の場合はメトリクス送信が失敗するためです。 |
| 8-12 | metricbeat_wait_host: "127.0.0.1", metricbeat_wait_timeout: 120, metricbeat_wait_delay: 2, metricbeat_wait_sleep: 2, metricbeat_wait_retries: 5 | 起動確認の接続先と再試行条件を設定します。 | 起動直後の一時的な応答遅延を吸収できず, 正常起動を異常と誤判定することを防止するためです。 |

## テンプレートと生成ファイル

| テンプレート | 生成先 (括弧内は既定) | 用途 | 主な内容 |
| --- | --- | --- | --- |
| templates/metricbeat.yml.j2 | {{ metricbeat_config_file }} (既定: /etc/metricbeat/metricbeat.yml) | Metricbeat 設定ファイルを生成します。 | system module の収集対象, processor 定義, Logstash 出力, HTTP 監視設定。 |
| templates/metricbeat.service.j2 | {{ metricbeat_systemd_unit_file }} (既定: /etc/systemd/system/metricbeat.service) | Metricbeat の systemd unit 定義を生成します。 | 実行ユーザ, 実行コマンド, 再起動ポリシー。 |
| templates/build-metricbeat-deb.sh.j2 | package build host 上のビルド用スクリプト | Debian 系ローカルパッケージを構築します。 | ソース取得, ビルド, deb パッケージ作成。 |
| templates/build-metricbeat-rpm.sh.j2 | package build host 上のビルド用スクリプト | RHEL 系ローカルパッケージを構築します。 | ソース取得, ビルド, rpm パッケージ作成。 |

## 展開されるサービスの仕様

### ポート公開

| ホスト側待受 | サービス側待受 | プロトコル | 用途 |
| --- | --- | --- | --- |
| {{ metricbeat_http_host }}:{{ metricbeat_http_port }} (既定: 0.0.0.0:5067) | {{ metricbeat_http_port }} (既定: 5067) | TCP | Metricbeat の HTTP 監視エンドポイントを対象ホスト側から利用可能にします。 |

metricbeat.yml では, Metricbeat サービスの HTTP 監視ポートを次の形式で待受します。

- {{ metricbeat_http_host }}:{{ metricbeat_http_port }} (既定: 0.0.0.0:5067)

既定値は, 対象ホスト上のすべてのネットワークインターフェースで TCPプロトコルのポート番号5067番 を待受する設定であることを意味します。

### ファイル/ディレクトリ構成

本ロールは, 次のパスへ設定ファイルと運用データを配置します。

| パス | 用途 |
| --- | --- |
| {{ metricbeat_config_file }} (既定: /etc/metricbeat/metricbeat.yml) | Metricbeat の設定ファイルです。 |
| {{ metricbeat_systemd_unit_file }} (既定: /etc/systemd/system/metricbeat.service) | Metricbeat の起動定義です。 |
| {{ metricbeat_data_dir }} (既定: /var/lib/metricbeat) | Metricbeat の内部状態を保持します。 |
| {{ metricbeat_logs_dir }} (既定: /var/log/metricbeat) | Metricbeat のログを保存します。 |

既定値は, 設定ファイルを /etc/metricbeat/metricbeat.yml から読み込み, データを /var/lib/metricbeat, ログを /var/log/metricbeat に保存する設定です。

また, Metricbeat から Logstash への送信先を `metricbeat_backend_host`, `metricbeat_backend_port` で指定し, ホスト間通信として接続するよう設定します。

### サービス起動処理に関する補足事項

- 本ロールは, 起動後に HTTP 監視ポート経由で接続確認を実施し, http://127.0.0.1:5067/ が応答することで Metricbeat が利用可能な状態になることを確認, 保証します。
- 既定値を使用する場合は 0.0.0.0:5067 で待受します。外部公開範囲を調整したい場合は, ホスト側ファイアウォールや公開経路で制御することを検討してください。

## 実行フロー

1. [tasks/load-params.yml](tasks/load-params.yml) で OS 別パラメータと共通変数を読み込みます。
2. [tasks/validate.yml](tasks/validate.yml) で導入前提, パス, ポート, logging_backend グループ有無, OS 条件を確認します。
3. [tasks/package.yml](tasks/package.yml) で package build host 上にローカルパッケージを構築し, 対象ホストへ導入します。
4. [tasks/directory.yml](tasks/directory.yml) で設定, データ, ログの配置先を作成します。
5. [tasks/config.yml](tasks/config.yml) で [templates/metricbeat.yml.j2](templates/metricbeat.yml.j2) と [templates/metricbeat.service.j2](templates/metricbeat.service.j2) を配置します。設定更新時は metricbeat_restart_service を通知し, [handlers/main.yml](handlers/main.yml) から読み込む [handlers/restart-service.yml](handlers/restart-service.yml) で systemd サービスを再起動します。
6. [tasks/service.yml](tasks/service.yml) で Metricbeat systemd サービスを起動します。
7. [tasks/verify.yml](tasks/verify.yml) で wait_for による HTTP 監視ポート待機と, uri による / の応答確認を実施し, HTTP 応答が 200 であることを検証します。

## 検証ポイント

### 検証の前提条件

検証を始める前に, 次の条件が満たされていることを確認します。

- 対象ホストで Metricbeat systemd サービスが起動済みであること。
- metricbeat_http_port に設定したポートが他のサービスで使われていないこと。
- metricbeat_config_dir 配下を作成できること。
- logging_collector グループに対象ホストが登録されていること。
- logging_backend_host が定義され, かつ空文字列でない場合は, その値が名前解決できること。
- logging_backend_host が未定義又は空文字列の場合は, logging_backend グループに 1 台以上のホストが登録され, 先頭ホスト(又は先頭ホストの ansible_host)が名前解決できること。

### 検証環境の設定

検証用の host_vars と vars/all-config.yml を次の値で整えます。

```yaml
1: metricbeat_config_dir: "/etc/metricbeat"
2: metricbeat_http_host: "0.0.0.0"
3: metricbeat_http_port: 5067
4: metricbeat_backend_port: 5044
5: metricbeat_wait_host: "127.0.0.1"
6: metricbeat_wait_delegate_to: "{{ inventory_hostname }}"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | metricbeat_config_dir: "/etc/metricbeat" | 検証時に参照する設定ファイルの配置先を統一します。 | 配置先が不明確な場合は設定確認対象を誤り, 検証漏れが発生するためです。 |
| 2-3 | metricbeat_http_host: "0.0.0.0", metricbeat_http_port: 5067 | HTTP 待受を 0.0.0.0:5067 に設定し, 状態確認を実行可能にします。 | 待受先アドレス又はポートが不一致の場合, 検証コマンドが接続不能となり, 導入結果を判定できないためです。 |
| 4 | metricbeat_backend_port: 5044 | 送信先 Logstash の待受ポートを指定します。 | 送信先ポートが不一致の場合, メトリクス送信が失敗するためです。 |
| 5-6 | metricbeat_wait_host: "127.0.0.1", metricbeat_wait_delegate_to: "{{ inventory_hostname }}" | 対象ホスト自身から 127.0.0.1 宛に起動確認を実行します。 | 接続元又は接続先が不適切な場合, Metricbeat が起動済みでも待受確認が失敗し, 誤検知を招くためです。 |

この設定により, 本 playbook で導入する Metricbeat が対象ホスト上で待受し, 自己確認が可能になります。

### 検証コマンドと期待結果

#### 1. Metricbeat サービス状態確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
  ```bash
  sudo systemctl status metricbeat --no-pager
  ```

**期待される出力**:
  ```plaintext
  Active: active (running)
  ```

**実行結果の例**:
  ```bash
  $ sudo systemctl status metricbeat --no-pager
● metricbeat.service - Metricbeat Metrics Collector Service
     Loaded: loaded (/etc/systemd/system/metricbeat.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-08-03 15:33:52 JST; 1h 43min ago
   Main PID: 1690803 (metricbeat)
      Tasks: 10 (limit: 4547)
     Memory: 88.9M (peak: 113.5M)
        CPU: 4.924s
     CGroup: /system.slice/metricbeat.service
             └─1690803 /usr/local/bin/metricbeat -e -c /etc/metricbeat/metricbeat.yml --p…

 8月 03 17:15:22 k8sctrlplane01 metricbeat[1690803]: {"log.level":"info","@timestamp":"2…
 8月 03 17:15:48 k8sctrlplane01 metricbeat[1690803]: {"log.level":"error","@timestamp":"…
 8月 03 17:15:48 k8sctrlplane01 metricbeat[1690803]: {"log.level":"info","@timestamp":"2…
 8月 03 17:15:48 k8sctrlplane01 metricbeat[1690803]: {"log.level":"warn","@timestamp":"2…
 8月 03 17:15:52 k8sctrlplane01 metricbeat[1690803]: {"log.level":"info","@timestamp":"2…
 8月 03 17:16:22 k8sctrlplane01 metricbeat[1690803]: {"log.level":"info","@timestamp":"2…
 8月 03 17:16:42 k8sctrlplane01 metricbeat[1690803]: {"log.level":"error","@timestamp":"…
 8月 03 17:16:42 k8sctrlplane01 metricbeat[1690803]: {"log.level":"info","@timestamp":"2…
 8月 03 17:16:42 k8sctrlplane01 metricbeat[1690803]: {"log.level":"warn","@timestamp":"2…
 8月 03 17:16:52 k8sctrlplane01 metricbeat[1690803]: {"log.level":"info","@timestamp":"2…
Hint: Some lines were ellipsized, use -l to show in full.
  ```

**確認ポイント**:

- metricbeat サービスが active (running) であること。

#### 2. Metricbeat HTTP 応答確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
  ```bash
  curl -sS http://127.0.0.1:5067/
  ```

**期待される出力**:
  ```plaintext
  {"beat":"metricbeat","version":"8.17.3",...}
  ```

**実行結果の例**:
  ```bash
  $ curl -sS http://127.0.0.1:5067/
  {"beat":"metricbeat","binary_arch":"amd64","build_commit":"unknown","build_time":"","elastic_licensed":false,"ephemeral_id":"90cbeda5-49ed-4746-966d-a6b32c3047e9","gid":"0","hostname":"k8sctrlplane01","name":"k8sctrlplane01","uid":"0","username":"root","uuid":"fb380356-0e50-49d2-8f62-accf5b6c93c6","version":"8.17.3"}
  ```

**確認ポイント**:

- http://127.0.0.1:5067/ へ接続できること。
- 応答本文に beat や version が含まれること。

#### 3. Logstash 送信先到達確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
  ```bash
  getent hosts "{{ metricbeat_backend_host }}"
  ```

**期待される出力**:
  ```plaintext
  192.168.10.20 elastic-backend01.local
  ```

**実行結果の例**:
  ```bash
  $ getent hosts elastic-backend01.local
  192.168.30.109  elastic-backend01.local
  ```

**確認ポイント**:

- metricbeat_backend_host が名前解決できること。
- 解決した宛先が想定した Logstash ホストであること。

### 異常時の確認項目

#### 1. ポート競合の確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
  ```bash
  ss -ltnp | grep ':5067 '
  ```

**実行結果の例**:
  ```bash
  $ ss -ltnp | grep ':5067 '
  LISTEN 0      4096                        *:5067             *:*
  ```

**確認ポイント**:

- TCPプロトコルのポート番号5067番 が待受状態であること。
- Metricbeat 以外の不要なプロセスが 5067 番ポートを占有していないこと。

#### 2. 設定ファイル生成状態の確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
  ```bash
  ls -l /etc/metricbeat/metricbeat.yml
  ```

**実行結果の例**:
  ```bash
  $ ls -l /etc/metricbeat/metricbeat.yml
  -rw-r--r-- 1 root root 3033  8月  3 15:33 /etc/metricbeat/metricbeat.yml
  ```

**確認ポイント**:

- 設定ファイルが存在すること。
- 既定値を使用する場合の確認先は /etc/metricbeat/metricbeat.yml であること。
- ファイルが 0 バイトではないこと。

#### 3. systemd unit 定義生成状態の確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
  ```bash
  ls -l /etc/systemd/system/metricbeat.service
  ```

**実行結果の例**:
  ```bash
  $ ls -l /etc/systemd/system/metricbeat.service
  -rw-r--r-- 1 root root 745  8月  3 15:33 /etc/systemd/system/metricbeat.service
  ```

**確認ポイント**:

- systemd unit 定義ファイルが存在すること。
- 既定値を使用する場合の確認先は /etc/systemd/system/metricbeat.service であること。
- ファイルが 0 バイトではないこと。

#### 4. 設定ファイルの配置状態確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
  ```bash
  ls -l /etc/metricbeat/metricbeat.yml
  ```

**実行結果の例**:
  ```bash
  $ ls -l /etc/metricbeat/metricbeat.yml
  -rw-r--r-- 1 root root 3033  8月  3 15:33 /etc/metricbeat/metricbeat.yml
  ```

**確認ポイント**:

- 設定ファイルの所有者と権限が想定どおりであること。
- 設定ファイルの更新時刻が直近の導入結果と矛盾しないこと。

#### 5. サービスログのエラー確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:

1. 件数で確認する場合(以下の場合は直近200件の警告以上の問題を抽出する):
    ```bash
    journalctl -u metricbeat -p warning -n 200 --no-pager
    ```
2. 時間で確認する場合(以下の場合は直近10分間の警告以上の問題を抽出する):
    ```bash
    journalctl -u metricbeat -p warning --since "10 min ago" --no-pager
    ```

**実行結果の例**:
  ```bash
  $ journalctl -u metricbeat -p warning --since "10 min ago" --no-pager
  -- No entries --
  ```

**確認ポイント**:

- 起動失敗の継続エラーが反復出力されないこと。
- Logstash 接続失敗の継続エラーが反復出力されないこと。

## トラブルシューティング

### 1. Metricbeat が起動しない場合

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:

```bash
systemctl status metricbeat --no-pager
journalctl -u metricbeat -n 200 --no-pager | grep -Ei 'error|warn|fail|fatal'
ls -ld /etc/metricbeat /var/lib/metricbeat /var/log/metricbeat
```

**確認ポイント**:

- サービス状態が active (running) であること。
- ログに設定読込失敗, 起動失敗が出ていないこと。
- 既定値を使用する場合, /etc/metricbeat, /var/lib/metricbeat, /var/log/metricbeat 配下へ読み書き可能な権限があること。

### 2. HTTP 監視ポートが応答しない場合

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
```bash
systemctl status metricbeat --no-pager
ss -ltnp | grep ':5067 '
curl -v --max-time 5 http://127.0.0.1:5067/
```

**確認ポイント**:

- Metricbeat サービスが起動中であること。
- TCPプロトコルのポート番号5067番 で待受していること。
- curl が接続エラーではなく HTTP 応答を返すこと。

### 3. メトリクス収集が進まない場合

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
```bash
grep -n "metricsets:" -A 20 /etc/metricbeat/metricbeat.yml
journalctl -u metricbeat -n 200 --no-pager | grep -Ei 'error|warn|fail|fatal'
```

**確認ポイント**:

- system module の metricsets が想定どおりに展開されていること。
- ログに権限不足, 収集失敗のエラーが出ていないこと。

### 4. Logstash へ送信できない場合

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
```bash
getent hosts "{{ metricbeat_backend_host }}"
journalctl -u metricbeat -n 200 --no-pager | grep -Ei 'error|warn|fail|fatal'
```

**確認ポイント**:

- `metricbeat_backend_host` が名前解決できること。
- `logging_backend_host` が定義され, かつ空文字列でない場合は, `logging_backend_host` に IPアドレス又はFQDNを指定していること。
- `logging_backend_host` が未定義又は空文字列の場合は, `inventory/hosts` の `logging_backend` グループ先頭ホストに `ansible_host` パラメタを設定し, 適切な IPアドレス又はFQDNを指定していること。
- ログに出力先ホスト不達又は接続拒否が出ていないこと。
- `metricbeat_backend_port` が Logstash 側の待受ポートと一致していること。

## 注意事項

- `metricbeat_data_dir` の配下にあるデータは運用データを含むため, 削除前にバックアップ方針を確認してください。
- `metricbeat_system_period` を短く設定する場合は, 対象ホストの負荷増加に注意してください。
- `logging_backend_host` が定義され, かつ空文字列でない場合は `metricbeat_backend_host` はその値を使用するため, 当該の設定値が送信先 Logstash ホストを指すIPアドレスやFQDNとなっていること。
- `logging_backend_host` が未定義又は空文字列の場合は `metricbeat_backend_host` は `inventory/hosts` の `logging_backend` グループ先頭ホストから解決するため, `inventory/hosts` 内のホスト定義の順序と `inventory/hosts`や`host_vars` の `ansible_host` 定義が意図どおりであること。
- `logging_backend_host`, `filebeat_backend_host`, `metricbeat_backend_host` には, IPアドレス又はFQDNを指定してください。`*.local` などの multicast DNS 名は, 環境によって名前解決が不安定になるため指定しないことを推奨します。
- 本ロールでは, Metricbeat の設定ファイル(Metricbeatの動作設定ファイルである`metricbeat.yml`)に対する権限チェックを無効(`strict.perms`パラメタを`false`に設定)にして導入していますので, 設定ファイル保護はホスト側の権限管理で担保してください。

## 参考資料

### 公式ドキュメント

- [Metricbeat Reference](https://www.elastic.co/guide/en/beats/metricbeat/current/index.html)
- [Metricbeat System Module](https://www.elastic.co/guide/en/beats/metricbeat/current/metricbeat-module-system.html)
- [Metricbeat Configure Modules](https://www.elastic.co/guide/en/beats/metricbeat/current/configuration-metricbeat.html)
- [Metricbeat Logstash Output](https://www.elastic.co/guide/en/beats/metricbeat/current/logstash-output.html)
- [Ansible Playbooks](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html)
- [ansible-playbook command](https://docs.ansible.com/ansible/latest/cli/ansible-playbook.html)
- [sudo manual](https://www.sudo.ws/docs/man/sudo.man/)
- [GNU Make Manual](https://www.gnu.org/software/make/manual/make.html)
- [curl Documentation](https://curl.se/docs/)

### 関連ロール

- [roles/elasticsearch/Readme.md](../elasticsearch/Readme.md) Elasticsearch関連コンポーネント全体の仕様についての解説を記載しています。以下の内容について確認する場合に参照します。
	- 設計背景と非干渉条件
	- Elasticsearch 関連コンポーネント構成図
	- 各コンテナの役割分担
	- inventory group と展開されるコンテナとの対応関係
- [Filebeat ロール](../filebeat/Readme.md) ログ収集設定の対応関係について確認する場合に参照します。
