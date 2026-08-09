# Filebeat ロール

本ロールは, 本 playbook で導入する Filebeat を, 本 playbook で導入する Logstash, Elasticsearch, Kibana, Metricbeat と組み合わせて運用するためのロールです。

## 目次

- [Filebeat ロール](#filebeat-ロール)
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
      - [1. Filebeat サービス状態確認](#1-filebeat-サービス状態確認)
      - [2. Filebeat HTTP 応答確認](#2-filebeat-http-応答確認)
      - [3. Logstash 送信先到達確認](#3-logstash-送信先到達確認)
    - [異常時の確認項目](#異常時の確認項目)
      - [1. ポート競合の確認](#1-ポート競合の確認)
      - [2. 設定ファイル生成状態の確認](#2-設定ファイル生成状態の確認)
      - [3. systemd unit 定義生成状態の確認](#3-systemd-unit-定義生成状態の確認)
      - [4. 収集対象ログパスの確認](#4-収集対象ログパスの確認)
      - [5. サービスログのエラー確認](#5-サービスログのエラー確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. Filebeat が起動しない場合](#1-filebeat-が起動しない場合)
    - [2. HTTP 監視ポートが応答しない場合](#2-http-監視ポートが応答しない場合)
    - [3. ログ収集が進まない場合](#3-ログ収集が進まない場合)
    - [4. Logstash へ送信できない場合](#4-logstash-へ送信できない場合)
  - [注意事項](#注意事項)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)
    - [関連ロール](#関連ロール)

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Filebeat | - | ログファイルを収集し, 送信先へ転送するエージェント。 |
| Logstash | - | 受信したデータを整形し, 送信先へ転送するソフトウェア。 |
| Elasticsearch | - | 検索と集約を担当するサーバソフトウェア。 |
| Kibana | - | Elasticsearchに保存されたデータを可視化し, 参照するソフトウェア。 |
| Metricbeat | - | メトリクスを収集して送信するエージェント。 |
| filestream | - | 追記されるファイルを継続監視してログを取り込む Filebeat の入力方式。 |
| processor | - | 収集したイベントへ追加情報を付与する変換処理。 |
| collector | - | 収集起点を識別するためにイベントへ付与する固定値。 |
| ローカルパッケージ | - | 本ロールでソースから生成し, 対象ホストへ導入する deb または rpm パッケージ。 |
| コンテナイメージ | - | コンテナ実行に必要な内容をまとめた保存形式。 |
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Docker Compose | - | 複数のコンテナ定義をまとめて作成, 起動, 停止, 更新する仕組み。 |
| compose project 名 | - | Docker Compose によって展開される個々のアプリケーションを識別する名前です。展開されたコンテナ, ネットワーク, ボリュームなどのリソースをグループ化し, 他のアプリケーション又は別途展開された同じアプリケーションと区別するために用います。 |
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
| ログ | - | 処理の結果や状態を時系列で記録した情報。 |
| データ | - | 処理や保存の対象となる情報。 |
| ポート | - | 通信の出入口を識別する番号または接点。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| Fully Qualified Domain Name | FQDN | 末尾まで省略せず書いた完全なドメイン名。 |
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

- 対象ホストが, inventory/hosts ファイル中の logging_collector グループに登録されていること。
- 対象ホストの OS は, Debian 系又は RHEL 系であること。
- 制御ホストでコンテナランタイム (既定値は Docker) が利用可能であること。
- 制御ホストで package build host への接続が可能であること。
- filebeat_http_port に設定するポート番号が, 既存サービスで使用するポート番号と競合しないこと。
- logging_backend_host が定義され, かつ空文字列でない場合は, その値が名前解決可能であること。
- logging_backend_host が未定義又は空文字列の場合は, logging_backend グループに 1 台以上のホストが登録され, 先頭ホスト(又は先頭ホストの ansible_host)が名前解決可能であること。

### 基本仕様

本ロールで Filebeat を導入する際の仕様は, 次のとおりです。

- package build host 上で Filebeat のソースをビルドし, ローカルパッケージを生成して導入すること。
- Filebeat は systemd サービスとして起動し, 再起動時に自動起動すること。
- HTTP 監視ポートは 0.0.0.0:5066 で待受すること。
- 収集入力方式は filestream を使用すること。
- 送信先 Logstash は filebeat_backend_host:filebeat_backend_port を使用すること。
- 設定, データ, ログは, 本 playbook で導入する専用ディレクトリへ分離すること。

### 本ロールで実施する主な処理

本ロールでは, 次の処理を実施します。

1. Filebeat ソースからローカルパッケージを構築し, 対象ホストへ導入します。
2. 本 playbook で導入するディレクトリを作成します。
3. Filebeat の設定ファイルと systemd unit を生成します。
4. Filebeat サービスを起動します。
5. 起動後に HTTP 監視ポートの待機と HTTP 応答確認を行います。

## 実行方法

### Makefile ターゲットを使用する場合

制御ホストで次のコマンドを実行します。

```bash
make run_logging_collector
```

このターゲットは logging collector 用 Playbook の実行導線として用意されています。現状の Filebeat 単独適用は, 次節の ansible-playbook による実行手順を使用します。

### ansible-playbookコマンドを使用する場合

制御ホストで次のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts logging-collector.yml --tags filebeat
```

このコマンドは, logging_collector グループに対して Filebeat ロールのみを実行します。

## 主要変数

### 基本設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| logging_filebeat_enabled | Filebeat ロールの有効化フラグ。 | true | true |
| filebeat_version | 構築対象の Filebeat 版数。 | v8.17.3 | v8.17.3 |
| filebeat_build_host | パッケージ構築を実行するホスト名。 | localhost | localhost |
| filebeat_config_dir | Filebeat 設定ファイルを配置するディレクトリ。 | /etc/filebeat | /etc/filebeat |
| filebeat_config_file | Filebeat 設定ファイルのパス。 | {{ filebeat_config_dir }}/filebeat.yml | /etc/filebeat/filebeat.yml |
| filebeat_data_dir | Filebeat データを配置するディレクトリ。 | /var/lib/filebeat | /var/lib/filebeat |
| filebeat_logs_dir | Filebeat ログを配置するディレクトリ。 | /var/log/filebeat | /var/log/filebeat |
| filebeat_systemd_unit_file | Filebeat の systemd unit ファイルパス。 | /etc/systemd/system/filebeat.service | /etc/systemd/system/filebeat.service |

### 収集設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| filebeat_http_host | Filebeat の HTTP 待受アドレス。 | 0.0.0.0 | 0.0.0.0 |
| filebeat_http_port | Filebeat の HTTP 待受ポート。 | 5066 | 5066 |
| filebeat_log_paths | 収集対象ログファイルパスの一覧。 | /var/log/*.log, /var/log/syslog, /var/log/messages, /var/log/containers/*.log, /var/log/pods/*/*.log | /var/log/*.log |
| filebeat_backend_host | 送信先 Logstash ホスト。| 自動解決(logging_backend_host が設定済みならその値, 未設定又は空文字列なら `inventory/hosts` の `logging_backend` グループ先頭ホストの接続先アドレス, 接続先アドレス未指定時は先頭ホスト名)。 | 192.168.10.20 |
| filebeat_backend_port | 送信先 Logstash ポート。 | 5044 | 5044 |
#### `logging_backend_host`, `filebeat_backend_host`, `metricbeat_backend_host`の設定値に関する留意事項

`logging_backend_host` が未定義又は空文字列の場合は, `inventory/hosts` の `logging_backend` グループに記載された先頭ホストを送信先候補として使用します。
このとき, 先頭ホストに接続先アドレス(IPアドレス又はFQDN)を `ansible_host` パラメタによって明示されている場合はその値を使用し, 明示されていない場合は先頭ホスト名を使用します。
例えば, `inventory/hosts` の先頭ホストの行が `elastic-backend01 ansible_host=192.168.30.109` と記載されている場合は, `192.168.30.109` を使用し, `elastic-backend01`のように, `ansible_host` パラメタが未指定の場合は, `inventory/hosts`に記載されたホスト名(ansibleのインベントリホスト名)である `elastic-backend01` を使用します。

`logging_backend_host`, `filebeat_backend_host`, `metricbeat_backend_host` には, IPアドレス又はFQDNを指定してください。`*.local` などの multicast DNS 名は, 環境によって名前解決が不安定になるため指定しないことを推奨します。

### 起動検証関連設定

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| filebeat_wait_host | 起動確認で待機する接続先ホスト。 | 127.0.0.1 | 127.0.0.1 |
| filebeat_wait_delegate_to | 起動確認を実行する接続元ホスト。 | localhost | localhost |
| filebeat_wait_timeout | 起動確認のタイムアウト時間。 | 120 | 120 |
| filebeat_wait_delay | 起動確認の開始遅延時間。 | 2 | 2 |
| filebeat_wait_sleep | 起動確認の待機間隔。 | 2 | 2 |
| filebeat_wait_retries | 起動確認の再試行回数。 | 5 | 5 |

### 変数設定例

#### host_vars の設定例

ホスト固有に変える値を host_vars/logcollector01.local.yml に記載します。

```yaml
1: logging_filebeat_enabled: true
2: filebeat_http_port: 5066
3: filebeat_wait_delegate_to: "{{ inventory_hostname }}"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | logging_filebeat_enabled: true | Filebeat ロールを有効化し, ディレクトリ作成, 設定生成, サービス起動, 起動確認を実行します。 | false の場合は Filebeat ロールの処理が実行されず, 期待した導入結果を得られないためです。 |
| 2 | filebeat_http_port: 5066 | Filebeat の HTTP 待受ポートを 5066 に設定します。 | ポートが未設定又は誤設定の場合, 監視確認の接続先が不一致となり, 到達確認に失敗するためです。 |
| 3 | filebeat_wait_delegate_to: "{{ inventory_hostname }}" | 起動確認タスクを対象ホスト自身から実行します。 | 到達不能な接続元を設定した場合, 起動済みでも待受確認に失敗し, ロール実行が異常終了するためです。 |

この例では, HTTP 監視待受ポートを明示し, 起動確認の接続元を対象ホスト自身にします。

#### vars/all-config.yml の設定例

全ホスト共通の値を vars/all-config.yml に記載します。

```yaml
1: logging_filebeat_enabled: true
2: filebeat_version: "v8.17.3"
3: filebeat_build_host: "localhost"
4: filebeat_http_host: "0.0.0.0"
5: filebeat_http_port: 5066
6: filebeat_backend_port: 5044
7: filebeat_wait_host: "127.0.0.1"
8: filebeat_wait_timeout: 120
9: filebeat_wait_delay: 2
10: filebeat_wait_sleep: 2
11: filebeat_wait_retries: 5
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | logging_filebeat_enabled: true | Filebeat ロールを有効化し, 共通設定にもとづく導入処理を実行します。 | false の場合は共通設定が存在しても導入処理が実行されず, 設定の反映漏れが発生するためです。 |
| 2 | filebeat_version: "v8.17.3" | ソース構築と導入先パッケージの版数を統一します。 | 未設定又は誤設定の場合, 想定外版数が導入され, 検証結果と運用状態が不一致になるためです。 |
| 3 | filebeat_build_host: "localhost" | 制御ホストをパッケージ構築先として指定します。 | 到達不能ホストを指定した場合はローカルパッケージ構築が失敗するためです。 |
| 4-5 | filebeat_http_host: "0.0.0.0", filebeat_http_port: 5066 | Filebeat の HTTP 待受を 0.0.0.0:5066 に設定し, 対象ホストから利用可能にします。 | 未設定又は誤設定の場合, 待受先アドレスやポートが期待値と一致せず, 接続確認が失敗するためです。 |
| 6 | filebeat_backend_port: 5044 | 送信先 Logstash の待受ポートを指定します。 | 送信先ポートが不一致の場合, イベント送信が失敗するためです。 |
| 7-11 | filebeat_wait_host: "127.0.0.1", filebeat_wait_timeout: 120, filebeat_wait_delay: 2, filebeat_wait_sleep: 2, filebeat_wait_retries: 5 | 起動確認の接続先と再試行条件を定義し, 起動直後の待受未完了を吸収して到達性を検証します。 | これらが未設定又は不適切な場合, 起動直後の一時的な応答遅延を異常と誤判定し, ロール実行が失敗するためです。 |

この例では, 本 playbook で導入する側の共通値を一箇所へ集約します。

## テンプレートと生成ファイル

| テンプレート | 生成先 (括弧内は既定) | 用途 | 主な内容 |
| --- | --- | --- | --- |
| templates/filebeat.yml.j2 | {{ filebeat_config_file }} (既定: /etc/filebeat/filebeat.yml) | Filebeat の設定ファイルを生成します。 | filestream 入力, processor 定義, Logstash 出力, HTTP 監視設定。 |
| templates/filebeat.service.j2 | {{ filebeat_systemd_unit_file }} (既定: /etc/systemd/system/filebeat.service) | Filebeat の systemd unit 定義を生成します。 | 実行ユーザ, 実行コマンド, 再起動ポリシー。 |
| templates/build-filebeat-deb.sh.j2 | package build host 上のビルド用スクリプト | Debian 系ローカルパッケージを構築します。 | ソース取得, ビルド, deb パッケージ作成。 |
| templates/build-filebeat-rpm.sh.j2 | package build host 上のビルド用スクリプト | RHEL 系ローカルパッケージを構築します。 | ソース取得, ビルド, rpm パッケージ作成。 |

filebeat.yml.j2 は, Filebeat 設定用ファイルを展開します。filebeat.service.j2 は, systemd サービス定義を展開します。

## 展開されるサービスの仕様

### ポート公開

| ホスト側待受 | サービス側待受 | プロトコル | 用途 |
| --- | --- | --- | --- |
| {{ filebeat_http_host }}:{{ filebeat_http_port }} (既定: 0.0.0.0:5066) | {{ filebeat_http_port }} (既定: 5066) | TCP | Filebeat の HTTP 監視エンドポイントを対象ホスト側から利用可能にします。 |

filebeat.yml では, Filebeat サービスの HTTP 監視ポートを次の形式で待受します。

- {{ filebeat_http_host }}:{{ filebeat_http_port }} (既定: 0.0.0.0:5066)

既定値は, 対象ホスト上のすべてのネットワークインターフェースで TCPプロトコルのポート番号5066番 を待受する設定であることを意味します。

### ファイル/ディレクトリ構成

本ロールは, 次のパスへ設定ファイルと運用データを配置します。

| パス | 用途 |
| --- | --- |
| {{ filebeat_config_file }} (既定: /etc/filebeat/filebeat.yml) | Filebeat の設定ファイルです。 |
| {{ filebeat_systemd_unit_file }} (既定: /etc/systemd/system/filebeat.service) | Filebeat の起動定義です。 |
| {{ filebeat_data_dir }} (既定: /var/lib/filebeat) | Filebeat の内部状態を保持します。 |
| {{ filebeat_logs_dir }} (既定: /var/log/filebeat) | Filebeat のログを保存します。 |

既定値は, 設定ファイルを /etc/filebeat/filebeat.yml から読み込み, データを /var/lib/filebeat, ログを /var/log/filebeat に保存する設定です。

また, Filebeat から Logstash への送信先を `filebeat_backend_host`, `filebeat_backend_port` で指定し, ホスト間通信として接続するよう設定します。

### サービス起動処理に関する補足事項

- 本ロールは, 起動後に HTTP 監視ポート経由で接続確認を実施し, http://127.0.0.1:5066/ が応答することで Filebeat が利用可能な状態になることを確認, 保証します。
- 既定値を使用する場合は 0.0.0.0:5066 で待受します。外部公開範囲を調整したい場合は, ホスト側ファイアウォールや公開経路で制御することを検討してください。

## 実行フロー

1. [tasks/load-params.yml](tasks/load-params.yml) で OS 別パラメータと共通変数を読み込みます。
2. [tasks/validate.yml](tasks/validate.yml) で導入前提, パス, ポート, logging_backend グループ有無, OS 条件を確認します。
3. [tasks/package.yml](tasks/package.yml) で package build host 上にローカルパッケージを構築し, 対象ホストへ導入します。
4. [tasks/directory.yml](tasks/directory.yml) で設定, データ, ログの配置先を作成します。
5. [tasks/user_group.yml](tasks/user_group.yml) で実行ユーザとグループを作成し, ディレクトリ所有権を調整します。
6. [tasks/config.yml](tasks/config.yml) で [templates/filebeat.yml.j2](templates/filebeat.yml.j2) と [templates/filebeat.service.j2](templates/filebeat.service.j2) を配置します。設定更新時は filebeat_restart_service を通知し, [handlers/main.yml](handlers/main.yml) から読み込む [handlers/restart-service.yml](handlers/restart-service.yml) で systemd サービスを再起動します。
7. [tasks/service.yml](tasks/service.yml) で Filebeat systemd サービスを起動します。
8. [tasks/verify.yml](tasks/verify.yml) で wait_for による HTTP 監視ポート待機と, uri による / の応答確認を実施し, HTTP 応答が 200 であることを検証します。

## 検証ポイント

### 検証の前提条件

検証を始める前に, 次の条件が満たされていることを確認します。

- 対象ホストで Filebeat systemd サービスが起動済みであること。
- filebeat_http_port に設定したポートが他のサービスで使われていないこと。
- filebeat_config_dir 配下を作成できること。
- logging_collector グループに対象ホストが登録されていること。
- logging_backend_host が定義され, かつ空文字列でない場合は, その値が名前解決できること。
- logging_backend_host が未定義又は空文字列の場合は, logging_backend グループに 1 台以上のホストが登録され, 先頭ホスト(又は先頭ホストの ansible_host)が名前解決できること。

### 検証環境の設定

検証用の host_vars, または, vars/all-config.yml を以下のように設定します:

```yaml
1: filebeat_config_dir: "/etc/filebeat"
2: filebeat_http_host: "0.0.0.0"
3: filebeat_http_port: 5066
4: filebeat_backend_port: 5044
5: filebeat_wait_host: "127.0.0.1"
6: filebeat_wait_delegate_to: "{{ inventory_hostname }}"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | filebeat_config_dir: "/etc/filebeat" | 検証時に参照する設定ファイルの配置先を統一します。 | 配置先が不明確な場合は設定確認対象を誤り, 検証漏れが発生するためです。 |
| 2-3 | filebeat_http_host: "0.0.0.0", filebeat_http_port: 5066 | Filebeat の HTTP 待受を 0.0.0.0:5066 に設定し, 状態確認を実行可能にします。 | 待受先アドレス又はポートが不一致の場合, 検証コマンドが接続不能となり, 導入結果を判定できないためです。 |
| 4 | filebeat_backend_port: 5044 | 送信先 Logstash の待受ポートを指定します。 | 送信先ポートが不一致の場合, ログイベント送信が失敗するためです。 |
| 5-6 | filebeat_wait_host: "127.0.0.1", filebeat_wait_delegate_to: "{{ inventory_hostname }}" | 対象ホスト自身から 127.0.0.1 宛に起動確認を実行します。 | 接続元又は接続先が不適切な場合, Filebeat が起動済みでも待受確認が失敗し, 誤検知を招くためです。 |

この設定により, 本 playbook で導入する Filebeat が対象ホスト上で待受し, 自己確認が可能になります。

### 検証コマンドと期待結果

#### 1. Filebeat サービス状態確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
  ```bash
  sudo systemctl status filebeat --no-pager
  ```

**期待される出力**:
  ```plaintext
  Active: active (running)
  ```

**実行結果の例**:
  ```bash
  $ sudo systemctl status filebeat --no-pager
  ● filebeat.service - Filebeat Log Collector Service
      Loaded: loaded (/etc/systemd/system/filebeat.service; enabled; preset: enabled)
      Active: active (running) since Mon 2026-08-03 15:33:47 JST; 2h 1min ago
    Main PID: 1690676 (filebeat)
        Tasks: 13 (limit: 4547)
      Memory: 30.5M (peak: 31.5M)
          CPU: 1.922s
      CGroup: /system.slice/filebeat.service
              └─1690676 /usr/local/bin/filebeat -e -c /etc/filebeat/filebeat.yml --path.ho…

  8月 03 17:33:48 k8sctrlplane01 filebeat[1690676]: {"log.level":"info","@timestamp":"202…
  8月 03 17:34:11 k8sctrlplane01 filebeat[1690676]: {"log.level":"error","@timestamp":"20…
  8月 03 17:34:11 k8sctrlplane01 filebeat[1690676]: {"log.level":"info","@timestamp":"202…
  8月 03 17:34:11 k8sctrlplane01 filebeat[1690676]: {"log.level":"warn","@timestamp":"202…
  8月 03 17:34:18 k8sctrlplane01 filebeat[1690676]: {"log.level":"info","@timestamp":"202…
  8月 03 17:34:44 k8sctrlplane01 filebeat[1690676]: {"log.level":"error","@timestamp":"20…
  8月 03 17:34:44 k8sctrlplane01 filebeat[1690676]: {"log.level":"info","@timestamp":"202…
  8月 03 17:34:44 k8sctrlplane01 filebeat[1690676]: {"log.level":"warn","@timestamp":"202…
  8月 03 17:34:48 k8sctrlplane01 filebeat[1690676]: {"log.level":"info","@timestamp":"202…
  8月 03 17:35:18 k8sctrlplane01 filebeat[1690676]: {"log.level":"info","@timestamp":"202…
  Hint: Some lines were ellipsized, use -l to show in full.
  ```

**確認ポイント**:

- filebeat サービスが active (running) であること。

#### 2. Filebeat HTTP 応答確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
  ```bash
  curl -sS http://127.0.0.1:5066/
  ```

**期待される出力**:
  ```plaintext
  {"beat":"filebeat","version":"8.17.3",...}
  ```

**実行結果の例**:
  ```bash
  $ curl -sS http://127.0.0.1:5066/
  {"beat":"filebeat","binary_arch":"amd64","build_commit":"unknown","build_time":"","elastic_licensed":false,"ephemeral_id":"843e63b4-2106-4c58-bec2-7b6ce1e45baf","gid":"0","hostname":"k8sctrlplane01","name":"k8sctrlplane01","uid":"0","username":"root","uuid":"81dbf7db-c1c4-4c18-938e-bb3ea92684ab","version":"8.17.3"}
  ```

**確認ポイント**:

- http://127.0.0.1:5066/ へ接続できること。
- 応答本文に beat や version が含まれること。

#### 3. Logstash 送信先到達確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
  ```bash
  getent hosts "{{ filebeat_backend_host }}"
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

- filebeat_backend_host が名前解決できること。
- 解決した宛先が想定した Logstash ホストであること。

### 異常時の確認項目

#### 1. ポート競合の確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
  ```bash
  ss -ltnp | grep ':5066 '
  ```

**実行結果の例**:
  ```bash
  $ ss -ltnp | grep ':5066 '
  LISTEN 0      4096                        *:5066             *:*
  ```

**確認ポイント**:

- TCPプロトコルのポート番号5066番 が待受状態であること。
- Filebeat サービスが待受していること。
- 想定外の別プロセスが同一ポートを占有していないこと。

#### 2. 設定ファイル生成状態の確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
  ```bash
  ls -l /etc/filebeat/filebeat.yml
  ```

**実行結果の例**:
  ```bash
  $ ls -l /etc/filebeat/filebeat.yml
  -rw-r--r-- 1 root root 3002  8月  3 15:25 /etc/filebeat/filebeat.yml
  ```

**確認ポイント**:

- Filebeat の設定ファイルが存在すること。
- 既定値を使用する場合の確認先は /etc/filebeat/filebeat.yml であること。
- ファイルが 0 バイトではないこと。

#### 3. systemd unit 定義生成状態の確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
  ```bash
  ls -l /etc/systemd/system/filebeat.service
  ```

**実行結果の例**:
  ```bash
  $ ls -l /etc/systemd/system/filebeat.service
  -rw-r--r-- 1 root root 725  8月  3 15:25 /etc/systemd/system/filebeat.service
  ```

**確認ポイント**:

- filebeat_systemd_unit_file に設定したファイルが存在すること。
- 既定値を使用する場合の確認先は /etc/systemd/system/filebeat.service であること。
- ファイルが 0 バイトではないこと。

#### 4. 収集対象ログパスの確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
  ```bash
  grep -n "paths:" -A 10 /etc/filebeat/filebeat.yml
  ```

**実行結果の例**:
  ```bash
  $ grep -n "paths:" -A 10 /etc/filebeat/filebeat.yml
  20:    paths:
  21-    # 収集対象パス一覧を順に展開して filestream の paths へ並べる。
  22-    # 展開処理の対応関係: 反復対象(filebeat_log_paths) を for で取り出し, 各要素(path) を paths 配列要素へ出力する ( ... "/var/log/*.log" ...  ... "/var/log/syslog" ...  ... "/var/log/messages" ...  ... "/var/log/containers/*.log" ...  ... "/var/log/pods/*/*.log" ... )。
  23-      - "/var/log/*.log"
  24-      - "/var/log/syslog"
  25-      - "/var/log/messages"
  26-      - "/var/log/containers/*.log"
  27-      - "/var/log/pods/*/*.log"
  28-
  29-# イベント加工処理を設定し, 収集イベントへホスト情報と識別情報を付加する。
  30-processors:
  ```

**確認ポイント**:

- filebeat_log_paths で指定したパスが paths 配下に展開されていること。
- 収集したいログパスが漏れていないこと。

#### 5. サービスログのエラー確認

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:

1. 件数で確認する場合(以下の場合は直近200件の警告以上の問題を抽出する):
    ```bash
    journalctl -u filebeat  -p warning -n 200 --no-pager
    ```
2. 時間で確認する場合(以下の場合は直近10分間の警告以上の問題を抽出する):
    ```bash
    journalctl -u filebeat -p warning --since "10 min ago" --no-pager
    ```

**実行結果の例**:
  ```bash
  $ journalctl -u filebeat -p warning --since "10 min ago" --no-pager
  -- No entries --
  ```

**確認ポイント**:

- 設定読込失敗, 起動失敗, Logstash 接続失敗に関するエラーメッセージが出ていないこと。

## トラブルシューティング

### 1. Filebeat が起動しない場合

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
```bash
systemctl status filebeat --no-pager
journalctl -u filebeat -n 200 --no-pager | grep -Ei 'error|warn|fail|fatal'
ls -ld /etc/filebeat /var/lib/filebeat /var/log/filebeat
```

**確認ポイント**:

- サービス状態が active (running) であること。
- ログに設定読込失敗, 起動失敗が出ていないこと。
- 既定値を使用する場合, /etc/filebeat, /var/lib/filebeat, /var/log/filebeat 配下へ読み書き可能な権限があること。

### 2. HTTP 監視ポートが応答しない場合

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
```bash
systemctl status filebeat --no-pager
ss -ltnp | grep ':5066 '
curl -v --max-time 5 http://127.0.0.1:5066/
```

**確認ポイント**:

- Filebeat サービスが起動中であること。
- TCPプロトコルのポート番号5066番 で待受していること。
- curl が接続エラーではなく HTTP 応答を返すこと。

### 3. ログ収集が進まない場合

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
```bash
grep -n "paths:" -A 20 /etc/filebeat/filebeat.yml
journalctl -u filebeat -n 200 --no-pager | grep -Ei 'error|warn|fail|fatal'
```

**確認ポイント**:

- filebeat_log_paths で指定したパスが正しく展開されていること。
- ログに権限不足又はパス不存在のエラーが出ていないこと。
- 収集対象ログファイルが実際に存在していること。

### 4. Logstash へ送信できない場合

**実施対象ホスト**: logging_collector グループに属する対象ホスト

**実行するコマンド**:
```bash
getent hosts "{{ filebeat_backend_host }}"
journalctl -u filebeat -n 200 --no-pager | grep -Ei 'error|warn|fail|fatal'
```

**確認ポイント**:

- filebeat_backend_host が名前解決できること。
- logging_backend_host が定義され, かつ空文字列でない場合は, logging_backend_host に IPアドレス又はFQDNを指定していること。
- logging_backend_host が未定義又は空文字列の場合は, inventory/hosts の logging_backend グループ先頭ホストに ansible_host パラメタを設定し, 適切な IPアドレス又はFQDNを指定していること。
- ログに出力先ホスト不達又は接続拒否が出ていないこと。
- filebeat_backend_port が Logstash 側の待受ポートと一致していること。

## 注意事項

- 既存のサービスで使用されているポートやディレクトリと衝突しないような設定を実施すること。
- `filebeat_log_paths` で指定するログパスは対象ホスト上に存在し, Filebeat サービス実行ユーザから読み取り可能であること。
- `logging_backend_host` が定義され, かつ空文字列でない場合は `filebeat_backend_host` はその値を使用するため, 当該の設定値が送信先 Logstash ホストを指すIPアドレスやFQDNとなっていること。
- `logging_backend_host` が未定義又は空文字列の場合は `filebeat_backend_host` は `inventory/hosts` の `logging_backend` グループ先頭ホストから解決するため, `inventory/hosts` 内のホスト定義の順序と `inventory/hosts`や`host_vars` の `ansible_host` 定義が意図どおりであること。
- `logging_backend_host`, `filebeat_backend_host`, `metricbeat_backend_host` には, IPアドレス又はFQDNを指定してください。`*.local` などの multicast DNS 名は, 環境によって名前解決が不安定になるため指定しないことを推奨します。
- 本ロールでは, Filebeat の設定ファイル(Filebeatの動作設定ファイルである`filebeat.yml`)に対する権限チェックを無効(`strict.perms`パラメタを`false`に設定)にして導入していますので, 設定ファイル保護はホスト側の権限管理で担保してください。

## 参考資料

### 公式ドキュメント

- [Filebeat Reference](https://www.elastic.co/guide/en/beats/filebeat/8.17/index.html)
- [Filebeat input configuration](https://www.elastic.co/guide/en/beats/filebeat/8.17/configuration-filebeat-options.html)
- [Filebeat Logstash Output](https://www.elastic.co/guide/en/beats/filebeat/8.17/logstash-output.html)
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
- [Metricbeat ロール](../metricbeat/Readme.md) メトリクス収集設定の対応関係について確認する場合に参照します。
