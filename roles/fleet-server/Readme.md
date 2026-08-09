# fleet-server ロール

本ロールは, Elastic Agent コンテナを Fleet Server モードで起動するロールです。

## 目次

- [fleet-server ロール](#fleet-server-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
    - [各ロール固有の利用者入力値](#各ロール固有の利用者入力値)
      - [条件付き必須入力値](#条件付き必須入力値)
      - [任意入力値](#任意入力値)
    - [Elastic Stack間共有設定値](#elastic-stack間共有設定値)
    - [変数設定例](#変数設定例)
      - [vars/all-config.ymlによる認証情報の上書き例](#varsall-configymlによる認証情報の上書き例)
      - [vars/all-config.yml の設定例](#varsall-configyml-の設定例)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [検証の前提条件](#検証の前提条件)
    - [検証環境の設定](#検証環境の設定)
    - [検証コマンドと期待結果](#検証コマンドと期待結果)
      - [1. Fleet Server コンテナ稼働状態確認](#1-fleet-server-コンテナ稼働状態確認)
      - [2. Fleet Server 公開ポート待受確認](#2-fleet-server-公開ポート待受確認)
      - [3. Fleet Serverサービスアカウントトークンファイル存在確認](#3-fleet-serverサービスアカウントトークンファイル存在確認)
    - [異常時の確認項目](#異常時の確認項目)
      - [1. コンテナ起動失敗時の確認](#1-コンテナ起動失敗時の確認)
      - [2. ポート待受状態の確認](#2-ポート待受状態の確認)
      - [3. Fleet Serverサービスアカウントトークンファイル生成状態の確認](#3-fleet-serverサービスアカウントトークンファイル生成状態の確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. 必須変数不足または不正値で検証に失敗する場合](#1-必須変数不足または不正値で検証に失敗する場合)
    - [2. サービスアカウントトークン発行で 400 エラーが発生する場合](#2-サービスアカウントトークン発行で-400-エラーが発生する場合)
    - [3. Elasticsearch の起動状態を確認中に接続に失敗する場合](#3-elasticsearch-の起動状態を確認中に接続に失敗する場合)
    - [4. サービスアカウントトークン自動発行が失敗する場合](#4-サービスアカウントトークン自動発行が失敗する場合)
  - [注意事項](#注意事項)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)
    - [関連ロール](#関連ロール)


## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| Ansible Playbook | playbook | 自動化処理の実行手順を順序付きで記述したファイル。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| makeコマンド | make | Makefile に定義された処理を実行するコマンド。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Docker Compose | - | 複数のコンテナ定義をまとめて作成, 起動, 停止, 更新する仕組み。 |
| Docker Compose 定義ファイル | - | Docker Compose が参照するコンテナ構成の定義ファイル。 |
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
| コンテナイメージ | - | コンテナ実行に必要な内容をまとめた保存形式。 |
| Fleet Server | - | Elastic Agent の管理通信を受け付けるサーバ機能。 |
| Elastic Agent | - | ログやメトリクスを収集して送信する実行要素。 |
| Elasticsearch | - | ログやメトリクス情報を集約, 検索するためのサーバソフトウェア。 |
| Elasticsearchのセキュリティ機能 | - | Elasticsearchへの接続者を認証し, 利用者に付与した権限に基づいて実行可能な操作を制御する機能。 |
| Kibana | - | Elasticsearchに保存されたデータを可視化し, 参照するソフトウェア。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| URL スキーム | - | URL の先頭で通信方式を示す部分。例: `http`, `https`。 |
| サービスアカウント (Service Account) | - | 自動処理中でサービスを呼び出す側のプログラムを識別するための識別情報。 |
| サービスアカウントトークン (Service Account Token) | - | サービスアカウントに紐付く認証情報。 |
| Fleet Serverサービスアカウントトークンファイル | - | Fleet ServerがElasticsearchへ接続するためのサービスアカウントトークンを対象ホスト上へ保存し, Fleet Serverコンテナが起動時に読み込む権限`0600`のファイル。 |
| Enrollment Token | - | Elastic AgentがFleet Serverへの登録を許可されていることを確認し, 登録先のElastic Agent ポリシーを特定するための登録用認証情報。 |
| Enrollment Token共有ファイル | - | Fleet BootstrapがEnrollment Tokenを制御ホスト上へ保存し, Elastic Agent本体ロールがFleet Serverへの登録時に読み込む権限`0600`のYAMLファイル。 |
| Hypertext Transfer Protocol | HTTP | World Wide Webで情報をやり取りする通信手順。 |
| Hypertext Transfer Protocol Secure | HTTPS | 通信内容を暗号化してWorld Wide Web通信を行う方式。 |
| localhost | - | 同一機器自身を指す名前。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| 対象ホスト上での疎通確認 | - | 対象ホスト上で自ホスト(localhost)を指定して待ち受け先ポートへの疎通確認を実施すること。確認対象のサービスが対象ホスト上で起動していることを確認します。 |
| 外部ホストからの疎通確認 | - | 対象ホスト以外のホストから対象ホストを指定して待ち受け先ポートへの疎通確認を実施すること。確認対象のサービスがネットワーク接続を含めて適切に設定され, サービス受付可能な状態になっていることを確認します。 |
| サービス | - | 機能を利用者や他システムへ提供する仕組み。 |
| ポート | - | 通信の出入口を識別する番号または接点。 |
| jqコマンド | jq | JSON 形式のデータから必要な項目だけを抽出して表示するコマンド。 |

## 概要

本ロールは, 対象ホスト上に Fleet Server 用 Docker Compose 定義ファイルを生成し, サービスアカウントトークンを参照してコンテナを起動します。Fleet Serverは, このコンテナ設定に指定されたElasticsearch接続先を使用し, 通常のElastic Agent向け既定Logstashを経由せずにElasticsearchへ直接接続します。Fleet Serverサービスアカウントトークンファイルが未配置の場合は, 変数設定により Elasticsearch API でサービスアカウントトークンを自動発行できます。Elasticsearchのセキュリティ機能が有効な場合は, Fleet Bootstrap が後続で利用する Kibana API キーも生成して同一 playbook 実行内で共有します。`fleet-server` と `fleet-bootstrap` を同一 `ansible-playbook` 実行で連続適用することを前提とし, 本ロールが設定するAPI キー ( `fleet_bootstrap_kibana_api_key`変数で設定) を Fleet Bootstrap ロール側で引き継ぎます。引き継いだ API キーを使用して, Fleet Bootstrap 側の `roles/fleet-bootstrap/tasks/verify.yml` で Fleet Output 登録先ホストの対象ホスト上での疎通確認と外部ホストからの疎通確認を実行します。起動後は待受ポートとコンテナ稼働状態を検証します。

## 前提条件

- 対象ホストで Docker と Docker Compose が利用可能であること。
- 対象ホストで `docker` コマンドを管理者権限で実行可能であること。
- Elasticsearch と Kibana の接続先が, 対象ホストから到達可能であること。
- `host_vars` または共通変数で, Fleet Server 用変数が定義済みであること。

## 実行方法

制御ホストで次のいずれかを実行します。

```bash
make run_fleet_server
```

```bash
ansible-playbook -i inventory/hosts logging-backend.yml --tags "fleet-server"
```

Fleet Bootstrap まで続けて再実行する場合は, 次を使用してください。

```bash
make run_fleet_bootstrap
```

```bash
ansible-playbook -i inventory/hosts logging-backend.yml --tags "fleet-server,fleet-bootstrap"
```

`fleet-server` と `fleet-bootstrap` を別々の `ansible-playbook` 実行へ分割すると, Fleet Server が生成した API キー共有値を Fleet Bootstrap へ引き継げません。

## 主要変数

### 各ロール固有の利用者入力値

#### 条件付き必須入力値

利用者が必ず設定するFleet Server固有変数はありません。認証情報を明示しない場合は, Elasticsearchの認証情報を共通派生値として使用します。

#### 任意入力値

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `logging_fleet_server_enabled` | ロール実行可否を指定するフラグ変数 | `true` | `true` |
| `fleet_server_endpoint_url_explicit` | Fleet Server のランタイムエンドポイント明示指定値。未指定時は `logging_backend_resolved_host` と `fleet_server_port` から組み立てる。 | 空文字列 | `https://fleet.example.org:8220` |
| `fleet_server_tls_mode` | ランタイムエンドポイントのURLスキームが`https`の場合に参照するTLS検証モード。指定可能な値は, [Elasticsearchロールの共有設定値](../elasticsearch/Readme.md#共有設定値に関する補足説明)を参照する。 | `logging_backend_default_tls_mode`の指定値。 | `none` |
| `fleet_server_token_issue_timeout_seconds` | サービスアカウントトークン発行APIの接続タイムアウト秒数 | `30` | `30` |
| `fleet_server_token_issue_retries` | サービスアカウントトークン発行APIの再試行回数 | `3` | `3` |
| `fleet_server_token_issue_retry_delay_seconds` | サービスアカウントトークン発行APIの再試行待機秒数 | `5` | `5` |
| `fleet_server_kibana_api_key_expiration` | Fleet Bootstrap 共有用 Kibana API キーの有効期限指定値。未設定時は expiration を送らない。 | 空文字列 | `24h` |
| `fleet_server_token_issue_username` | サービスアカウントトークン発行APIへ接続する利用者名。 | `elastic_search_security_username`の指定値。 | `elastic` |
| `fleet_server_token_issue_password` | サービスアカウントトークン発行APIへ接続するパスワード。 | `elastic_search_bootstrap_password`の指定値。 | `DUMMY_ELASTIC_PASSWORD` |
| `fleet_server_kibana_auth_username` | Fleet Bootstrap共有用Kibana APIキーの生成時にElasticsearch APIへ接続する利用者名。 | `elastic_search_security_username`の指定値。 | `elastic` |
| `fleet_server_kibana_auth_password` | Fleet Bootstrap共有用Kibana APIキーの生成時にElasticsearch APIへ接続するパスワード。 | `elastic_search_bootstrap_password`の指定値。 | `DUMMY_ELASTIC_PASSWORD` |

### Elastic Stack間共有設定値

共有設定値の意味, 設定要否, 既定値及び設定例は, [Elasticsearchロールの共有設定値](../elasticsearch/Readme.md#varsall-configymlに設定するelastic-stack間共有設定値)を参照します。Fleet Serverでは, 共通の版数, Dockerブリッジネットワーク, Elasticsearch接続先, URLスキーム及びTLS検証モードが影響します。


### 変数設定例

#### vars/all-config.ymlによる認証情報の上書き例

Elasticsearchの認証情報と異なる値を使用する場合に限り, `vars/all-config.yml`へ次の値を記載します。

```yaml
1: fleet_server_token_issue_username: "elastic"
2: fleet_server_token_issue_password: "DUMMY_ELASTIC_PASSWORD"
3: fleet_server_kibana_auth_username: "elastic"
4: fleet_server_kibana_auth_password: "DUMMY_ELASTIC_PASSWORD"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1-2 | `fleet_server_token_issue_username: "elastic"`, `fleet_server_token_issue_password: "DUMMY_ELASTIC_PASSWORD"` | サービスアカウントトークン自動発行 API の認証情報を指定します。 | Elasticsearchのセキュリティ機能が有効な場合に認証情報が不足又は不一致であると, トークン自動発行が失敗するためです。 |
| 3-4 | `fleet_server_kibana_auth_username: "elastic"`, `fleet_server_kibana_auth_password: "DUMMY_ELASTIC_PASSWORD"` | Kibana API キー生成時に Elasticsearch API へ接続する認証情報を指定します。 | 認証情報が未設定又は誤設定の場合, Fleet Bootstrap 連携用 API キーの生成又は再利用が失敗するためです。 |

この例を省略した場合は, `elastic_search_security_username`と`elastic_search_bootstrap_password`の指定値を使用します。

#### vars/all-config.yml の設定例

全ホスト共通の値を `vars/all-config.yml` に記載します。
`logging_backend_*` は `host_vars` に重複定義せず, この節の例のように `vars/all-config.yml` のみに記載します。

```yaml
1: logging_fleet_server_enabled: true
2: fleet_server_endpoint_url_explicit: "https://fleet.example.org:8220"
3: fleet_server_tls_mode: "full"
4: fleet_server_kibana_api_key_expiration: "24h"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `logging_fleet_server_enabled: true` | Fleet Server ロールを有効化し, 共通設定にもとづく導入処理を実行します。 | `false` の場合は Fleet Server ロールの処理が実行されず, 期待した導入結果を得られないためです。 |
| 2-3 | `fleet_server_endpoint_url_explicit: "https://fleet.example.org:8220"`, `fleet_server_tls_mode: "full"` | Fleet Serverの公開接続先を指定し, HTTPS証明書を検証します。 | 接続先又はTLS検証モードが誤っている場合は, Elastic Agentの登録及び疎通確認が失敗するためです。 |
| 4 | `fleet_server_kibana_api_key_expiration: "24h"` | Fleet Bootstrap 連携用 Kibana API キーの有効期限を `24h` に設定します。 | 未設定時は既定の有効期限運用に依存し, 誤設定時は API キーの再利用計画と整合しないためです。 |

この例では, 本 playbook で導入する側の共通値を一箇所へ集約します。

## テンプレートと生成ファイル

| 種別 | 入力 | 出力 | 目的 |
| --- | --- | --- | --- |
| テンプレート | `templates/docker-compose.yml.j2` | `{{ fleet_server_runtime_compose_file }}` (既定: `{{ fleet_server_compose_dir }}/docker-compose.yml`) | Fleet Server の Docker Compose 定義ファイルを生成する。 |
| タスク生成 | `tasks/token.yml` | `{{ fleet_server_runtime_service_token_path }}` (既定: `{{ fleet_server_compose_dir }}/secrets/fleet-server-service-token`) | Fleet Serverサービスアカウントトークンファイルをコンテナ実行ユーザの所有物として権限`0400`で保存する。 |
| タスク生成 | `tasks/directory.yml` | `{{ fleet_server_compose_dir }}` (既定: `/opt/fleet-server`), `{{ fleet_server_runtime_state_dir }}` (既定: `{{ fleet_server_compose_dir }}/state`) | 実行に必要なディレクトリを作成する。 |

## 実行フロー

1. [tasks/load-params.yml](tasks/load-params.yml) で OS 別パラメータと共通変数を読み込みます。
2. [tasks/validate.yml](tasks/validate.yml) で必須変数, パス, ポート範囲を確認します。
3. [tasks/package.yml](tasks/package.yml) で Docker と Docker Compose コマンドの利用可否を確認します。
4. [tasks/directory.yml](tasks/directory.yml) で Compose 配置先, state, Fleet Serverサービスアカウントトークンファイル格納先のディレクトリを作成します。
5. [tasks/token.yml](tasks/token.yml) で既存のFleet Serverサービスアカウントトークンファイルを確認し, 必要時は Elasticsearch API でサービスアカウントトークンを発行して同ファイルへ保存します。
6. [tasks/api-key.yml](tasks/api-key.yml) で Fleet Bootstrap 共有用の Kibana API キーを再利用または生成します。expiration は明示設定時のみ Elasticsearch API へ送信します。
7. [tasks/config.yml](tasks/config.yml) で [templates/docker-compose.yml.j2](templates/docker-compose.yml.j2) を配置し, `FLEET_ENROLL=1`による自己登録を指定します。Docker Compose 定義ファイルの更新時は fleet_server_restart_service を通知し, [handlers/main.yml](handlers/main.yml) から読み込む [handlers/restart-service.yml](handlers/restart-service.yml) でコンテナ再起動処理を実行します。
8. [tasks/service.yml](tasks/service.yml) でdocker-network-elastic-stackロールが作成したbackend用ネットワークの存在確認, 既存コンテナ整理, `docker compose up -d`によるFleet Serverコンテナ起動を実行します。
9. [tasks/verify.yml](tasks/verify.yml) で サービス提供ポートの待機と, `docker container inspect` によるコンテナ稼働状態確認を実施し, Fleet Server が起動済みであることを検証します。Fleet Bootstrapが有効な場合は`missing config fleet.agent.id`だけを後続処理で回復する一時状態として許容し, それ以外の異常状態では処理を停止します。
10. 同一 `ansible-playbook` 実行で `fleet-bootstrap` を続けて適用することで, `tasks/api-key.yml` で設定した `fleet_bootstrap_kibana_api_key` が Fleet Bootstrap の Fleet API 呼び出しと Elasticsearch hosts health 確認(対象ホスト上での疎通確認/外部ホストからの疎通確認)に引き継がれます。

## 検証ポイント

### 検証の前提条件

検証を始める前に, 次の条件が満たされていることを確認します:

- 対象ホストで Fleet Server コンテナが起動済みであること。
- 対象ホストで `docker` コマンドを実行可能であること。
- 対象ホストで `sudo` コマンドにより管理者権限でコマンドを実行可能であること。
- `fleet_server_port` に設定したポートが他のサービスで使用されていないこと。
- `fleet_server_compose_dir` 配下に Compose 定義ファイルと状態ディレクトリを作成できること。
- `fleet_server_compose_dir` 配下の `secrets/fleet-server-service-token` へFleet Serverサービスアカウントトークンファイルを配置できること。
- Elasticsearch との接続先が名前解決可能であること。

### 検証環境の設定

検証用の host_vars, または, vars/all-config.yml を以下のように設定します。

```yaml
1: fleet_server_endpoint_url_explicit: "https://fleet.example.org:8220"
2: fleet_server_tls_mode: "full"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題) |
| --- | --- | --- | --- |
| 1-2 | `fleet_server_endpoint_url_explicit: "https://fleet.example.org:8220"`, `fleet_server_tls_mode: "full"` | Fleet Serverの公開接続先を指定し, HTTPS証明書を検証します。 | 接続先又はTLS検証モードが誤っている場合は, Elastic Agentの登録及び疎通確認が失敗します。 |

この設定により, 本 playbook で導入する Fleet Server が対象ホスト上で待受し, 自己確認が可能になります。

### 検証コマンドと期待結果

#### 1. Fleet Server コンテナ稼働状態確認

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
docker container inspect fleet-server --format '{{.State.Running}}'
```

**期待される出力**:

```plaintext
true
```

**実行結果の例**:

```bash
$ docker container inspect fleet-server --format '{{.State.Running}}'
true
```

**確認ポイント**:

- コンテナが起動済みであること。
- `true` が返されること。

#### 2. Fleet Server 公開ポート待受確認

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
ss -lntp | grep ':8220 '
```

**期待される出力**:

```plaintext
LISTEN 0      4096         0.0.0.0:8220       0.0.0.0:*
```

**実行結果の例**:

```bash
$ ss -lntp | grep ':8220 '
LISTEN 0      4096         0.0.0.0:8220       0.0.0.0:*
```

**確認ポイント**:

- 指定したポートで待受していること。
- `:8220` を含む待受行が表示されること。

#### 3. Fleet Serverサービスアカウントトークンファイル存在確認

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
sudo test -f /opt/fleet-server/secrets/fleet-server-service-token && echo OK
```

**期待される出力**:

```plaintext
OK
```

**実行結果の例**:

```bash
$ sudo test -f /opt/fleet-server/secrets/fleet-server-service-token
&& echo OK
OK
```

**確認ポイント**:

- Fleet Serverサービスアカウントトークンファイルが配置済みであること。
- `OK` が表示されること。

### 異常時の確認項目

#### 1. コンテナ起動失敗時の確認

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
docker compose -f /opt/fleet-server/docker-compose.yml ps --no-trunc
```

**期待される出力**:

```plaintext
fleet-server  Up
```

**実行結果の例**:

```bash
$ docker compose -f /opt/fleet-server/docker-compose.yml ps --no-trunc
NAME           IMAGE                                                  COMMAND                                               SERVICE        CREATED          STATUS          PORTS
fleet-server   docker.elastic.co/elastic-agent/elastic-agent:8.17.3   "/usr/bin/tini -- /usr/local/bin/docker-entrypoint"   fleet-server   14 minutes ago   Up 14 minutes   0.0.0.0:8220->8220/tcp
```

**確認ポイント**:

- コンテナが `Up` 状態であること。
- 表示されたサービス名が `fleet-server` であること。

#### 2. ポート待受状態の確認

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
ss -lntp | grep ':8220 '
```

**期待される出力**:

```plaintext
LISTEN 0      4096         0.0.0.0:8220       0.0.0.0:*
```

**実行結果の例**:

```bash
$ ss -lntp | grep ':8220 '
LISTEN 0      4096         0.0.0.0:8220       0.0.0.0:*
```

**確認ポイント**:

- 出力が空でないこと。
- `ss` コマンドの出力に表示される `LISTEN` 行のポート番号 `:8220` を確認し, Fleet Server の待受ポートが確立されていること。

#### 3. Fleet Serverサービスアカウントトークンファイル生成状態の確認

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
sudo ls -ln /opt/fleet-server/secrets/fleet-server-service-token
```

**期待される出力**:

```plaintext
-r--------. 1 1000 1000 101 Aug  4 22:32 /opt/fleet-server/secrets/fleet-server-service-token
```

**実行結果の例**:

```bash
$ sudo ls -ln /opt/fleet-server/secrets/fleet-server-service-token
-r--------. 1 1000 1000 100 Aug  6 00:39 /opt/fleet-server/secrets/fleet-server-service-token
```

**確認ポイント**:

- Fleet Serverサービスアカウントトークンファイルが存在すること。
- `ls` コマンドの出力にFleet Serverサービスアカウントトークンファイルのパスが表示されること。
- `ls` コマンドの出力中のファイルサイズが 0 バイトではないこと。


## トラブルシューティング

### 1. 必須変数不足または不正値で検証に失敗する場合

- 現象: `Required fleet-server variables are missing or invalid.` が表示される。
- 対処: `fleet_server_image`, `fleet_server_container_name`, `fleet_server_compose_dir`, `fleet_server_service_token_container_path`, `logging_backend_container_user`, `fleet_server_policy_id`, `fleet_server_port` の設定値を確認し, 未定義, 空文字列, 範囲外ポート番号がないことを確認する。加えて, runtime 算出元である `logging_backend_host` と `elastic_search_http_port` が正しく設定されていることを確認する。

### 2. サービスアカウントトークン発行で 400 エラーが発生する場合

- 現象: `invalid service token name` が表示される。
- 対処:
  1. Fleet Server または Kibana へ接続できる環境で, まず接続先とエンドポイントが適切であることを確認する。
     - 実施コマンド例:
       以下の`DUMMY_ELASTIC_PASSWORD`を`elastic_search_bootstrap_password`の設定値に変更して実行してください:
       ```bash
       curl -u elastic:DUMMY_ELASTIC_PASSWORD http://<kibana-host>:5601/api/fleet/agent_policies
       ```
     - 確認事項:
       - `{"error":"no handler found for uri [/api/fleet/agent_policies] and method [GET]"}` のような応答が返る場合は, 接続先が Elasticsearch の 9200 ポートまたは誤った URL になっている可能性がある。
      - その場合は, 接続先を Kibana または Fleet Server サービスの URL に変更する。
      - `{"items":[],"total":0,"page":1,"perPage":20}` のように空の結果が返る場合は, その時点では Fleet Server 側に Elastic Agent ポリシーが登録されていない可能性がある。
  2. 取得結果に `fleet_server_policy_id` で設定した Elastic Agent ポリシー識別子が含まれることを確認する。
     - 実施コマンド例:
       以下の`DUMMY_ELASTIC_PASSWORD`を`elastic_search_bootstrap_password`の設定値に変更して実行してください:
       ```bash
       curl -u elastic:DUMMY_ELASTIC_PASSWORD http://<kibana-host>:5601/api/fleet/agent_policies | jq '.items[]?.id'
       ```
     - 確認事項:
       - 取得結果に `fleet_server_policy_id` で設定した値が表示されること。
      - 表示されない場合は, `fleet_server_policy_id` の設定値を正しい Elastic Agent ポリシー識別子に変更する。

### 3. Elasticsearch の起動状態を確認中に接続に失敗する場合

- 現象: `Connection reset by peer` や `Connection refused` が断続的に表示される。
- 対処: Elasticsearch 起動直後の初期化待ちで再試行中の可能性があるため, `fleet_server_wait_timeout` と `fleet_server_wait_retries` を確認する。

### 4. サービスアカウントトークン自動発行が失敗する場合

- 現象: 本ロール実行時に, `Failed to create service account token. Please check credentials and Elasticsearch connectivity.`メッセージが表示されplaybookの実行が停止する
- 対処: 共通派生値が参照する`elastic_search_security_username`, `elastic_search_bootstrap_password`を確認する。Fleet Server固有の認証情報が必要な場合は, `fleet_server_token_issue_username`, `fleet_server_token_issue_password`を`vars/all-config.yml`で上書きする。また, Elasticsearchとの接続状態を確認する。確認コマンドは以下のとおりである。
  - 実施コマンド例:
    以下の`DUMMY_ELASTIC_PASSWORD`を`elastic_search_bootstrap_password`の設定値に変更して実行してください:
    ```bash
    curl -u elastic:DUMMY_ELASTIC_PASSWORD http://<elasticsearch-host>:9200/_cluster/health
    ```
  - 実行結果例:
    ```json
    {"cluster_name":"shared-logs","status":"yellow","timed_out":false,"number_of_nodes":1,"number_of_data_nodes":1,"active_primary_shards":33,"active_shards":33,"relocating_shards":0,"initializing_shards":0,"unassigned_shards":2,"unassigned_primary_shards":0,"delayed_unassigned_shards":0,"number_of_pending_tasks":0,"number_of_in_flight_fetch":0,"task_max_waiting_in_queue_millis":0,"active_shards_percent_as_number":94.28571428571428}
    ```
  - 確認事項:
    - `cluster_name` と `status` が表示され, Elasticsearch へ接続できていること。
    - `status` 項目が, Elasticsearch のクラスタ状態が 検索や保存の基本機能は利用できるが一部の予備コピーが未配置である状態 ( `yellow` 状態 ), または, 予備コピーを含む全データ配置が完了している状態 ( `green` 状態 ) になること。
    - 接続できない場合は, `fleet_server_elasticsearch_host` や `fleet_server_elasticsearch_port` の設定値を確認し正しいホスト名やIPアドレス, ポート番号を設定する。

## 注意事項

- `fleet_server_service_token_auto_create: true` を使用する場合, `fleet_server_token_issue_password` は平文で保持されるため, 運用管理者はファイル権限と保管場所を適切に管理する必要があります。
- サービスアカウントトークン処理タスクは機密値保護のため `no_log: true` を適用し, 機密値をansibleの実行ログ中に残さないようにしています。なお, 障害追跡性を優先するため, Elasticsearch の起動状態を確認するタスクには, `no_log:true` を設定していません。
- 本ロールの初期化責務はFleet Bootstrap用Kibana APIキーの供給までです。本ロールが対象ホスト上で管理するFleet Serverサービスアカウントトークンファイルと異なり, Enrollment Tokenの作成, 再利用及び制御ホスト上のEnrollment Token共有ファイルへの保存は後続のFleet Bootstrapが担当します。
- Docker Compose 定義ファイルでは`FLEET_ENROLL=1`を指定し, Fleet Serverコンテナの起動時に自己登録を実行します。後続のFleet Bootstrapが有効な場合に限り, Fleet Server統合の設定前に発生する`missing config fleet.agent.id`状態を一時的に許容します。Fleet BootstrapはFleet Server統合を設定した後, 識別子が未生成の登録状態だけを除去してコンテナを再起動し, 状態APIが`HEALTHY`を返すまで検証します。


## 参考資料

### 公式ドキュメント

- [Ansible Documentation](https://docs.ansible.com/ansible/latest/index.html)
- [Ansible Playbooks](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html)
- [ansible-playbook command](https://docs.ansible.com/ansible/latest/cli/ansible-playbook.html)
- [GNU Make Manual](https://www.gnu.org/software/make/manual/make.html)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose file reference](https://docs.docker.com/reference/compose-file/)
- [Fleet and Elastic Agent Guide](https://www.elastic.co/guide/en/fleet/current/index.html)
- [Elastic Agent container deployment](https://www.elastic.co/guide/en/fleet/current/elastic-agent-container.html)
- [Fleet Server reference](https://www.elastic.co/guide/en/fleet/current/fleet-server.html)
- [Elasticsearch Reference](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Secure the Elastic Stack](https://www.elastic.co/guide/en/elasticsearch/reference/8.17/secure-cluster.html)
- [Kibana Guide](https://www.elastic.co/guide/en/kibana/current/index.html)
- [Service accounts and tokens](https://www.elastic.co/guide/en/elasticsearch/reference/current/service-accounts.html)
- [Enrollment Token](https://www.elastic.co/docs/reference/fleet/fleet-enrollment-tokens)
- [HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [URI Generic Syntax](https://www.rfc-editor.org/rfc/rfc3986)
- [jq Manual](https://jqlang.github.io/jq/manual/)

### 関連ロール

- [roles/elasticsearch/Readme.md](../elasticsearch/Readme.md) Elasticsearch関連コンポーネント全体の仕様についての解説を記載しています。以下の内容について確認する場合に参照します。
  - 設計背景と非干渉条件
  - Elasticsearch 関連コンポーネント構成図
  - 各コンテナの役割分担
  - inventory group と展開されるコンテナとの対応関係
