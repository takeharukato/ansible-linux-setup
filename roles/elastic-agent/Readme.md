# elastic-agent ロール

本ロールは, 対象ホストへElastic Agentを導入し, Fleet Bootstrapが保存したEnrollment Tokenを使用してFleet Serverへ登録するロールです。

## 目次

- [elastic-agent ロール](#elastic-agent-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
    - [Elastic Stack間共有設定値](#elastic-stack間共有設定値)
    - [各ロール固有の利用者入力値](#各ロール固有の利用者入力値)
      - [条件付き必須入力値](#条件付き必須入力値)
      - [任意入力値](#任意入力値)
    - [設定例](#設定例)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [検証の前提条件](#検証の前提条件)
    - [検証環境の設定](#検証環境の設定)
    - [検証コマンドと期待結果](#検証コマンドと期待結果)
      - [1. Elastic Agentサービス状態確認](#1-elastic-agentサービス状態確認)
      - [2. Elastic Agent版数確認](#2-elastic-agent版数確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. Enrollment Token共有ファイルの入力検証で停止する場合](#1-enrollment-token共有ファイルの入力検証で停止する場合)
    - [2. Elastic Agentサービスが起動しない場合](#2-elastic-agentサービスが起動しない場合)
  - [注意事項](#注意事項)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)
    - [関連ロール](#関連ロール)


## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Elasticsearch | - | ログやメトリクス情報を集約, 検索するためのサーバソフトウェア。 |
| Kibana | - | Elasticsearchに保存されたデータを可視化し, 参照するソフトウェア。 |
| Logstash | - | 受信したデータを整形し, 送信先へ転送するソフトウェア。 |
| Elastic Agent | - | ログやメトリクスを収集して送信する実行要素。 |
| Elastic Stack | - | Elasticsearch, Kibana, Logstash, Fleet Server, Fleet Bootstrap, Elastic Agent などで構成される, 収集, 蓄積, 検索, 可視化を行うソフトウェア群。 |
| Enrollment Token | - | Elastic AgentがFleet Serverへの登録を許可されていることを確認し, 登録先のElastic Agent ポリシーを特定するための登録用認証情報。 |
| Enrollment Token共有ファイル | - | Fleet BootstrapがEnrollment Tokenを制御ホスト上へ保存し, Elastic Agent本体ロールがFleet Serverへの登録時に読み込む権限`0600`のYAMLファイル。 |
| Fleet Serverサービスアカウントトークンファイル | - | Fleet ServerがElasticsearchへ接続するためのサービスアカウントトークンを対象ホスト上へ保存し, Fleet Serverコンテナが起動時に読み込む権限`0600`のファイル。 |
| コンテナイメージ | - | コンテナ実行に必要な内容をまとめた保存形式。 |
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Docker Compose | - | 複数のコンテナ定義をまとめて作成, 起動, 停止, 更新する仕組み。 |
| Docker Compose 定義ファイル | - | Docker Compose が参照するコンテナ構成の定義ファイル。 |
| compose project 名 | - | Docker Compose によって展開される個々のアプリケーションを識別する名前です。展開されたコンテナ, ネットワーク, ボリュームなどのリソースをグループ化し, 他のアプリケーション又は別途展開された同じアプリケーションと区別するために用います。 |
| YAML | - | 設定を読みやすい形式で表す記述方法。 |
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
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |
| makeコマンド | make | Makefile に定義された処理を実行するコマンド。 |
| curlコマンド | curl | URL を指定して通信結果を取得するコマンド。 |
| systemctlコマンド | systemctl | サービスの起動状態と自動起動設定を確認又は変更するコマンド。 |
| journalctlコマンド | journalctl | サービスが記録したログを確認するコマンド。 |
| elastic-agentコマンド | elastic-agent | Elastic Agentの版数確認や管理処理を実行するコマンド。 |

## 概要

本ロールは, Elastic Agent公式配布物を取得し, 対象ホストへサービスとして導入します。導入時は`elastic_agent_enrollment_token`で明示されたEnrollment Tokenを使用してFleet Serverへ登録します。Enrollment Tokenが未設定の場合は, Fleet Bootstrapが制御ホスト上へ保存したEnrollment Token共有ファイルを`fleet_bootstrap_enrollment_token_file`から特定し, `k8s_workload`, `k8s_system`, `host`の優先順で対象ホストの有効化変数に対応するEnrollment Tokenを選択します。Enrollment Tokenを使用する読込処理, 検証処理及び導入処理には`no_log: true`を設定し, Ansibleの実行ログへ秘密値を出力しません。本ロールは対象ホスト上のFleet Serverサービスアカウントトークンファイルを使用しません。

対象ホストに`elastic-agent.service`が登録済みの場合は, 公式配布物の取得, 展開, 導入及び再登録を実行しません。既存Agentに対する`--force`を使用しないため, Fleet上の重複登録を防止します。導入済みの場合もサービスの起動状態と導入版数を検証します。

HTTPでFleet Serverへ接続する場合は, Elastic Agent公式仕様に従って`--insecure`を指定します。HTTPではEnrollment Tokenが暗号化されずに送信されるため, 検証環境以外ではHTTPSを使用してください。

## 前提条件

- 対象ホストがLinuxであり, サービス管理にsystemdを使用していること。
- 対象ホストからElastic Agent公式配布物のURLへ接続可能であること。
- 対象ホストからFleet ServerのURLへ接続可能であること。
- Fleet BootstrapによりElastic Agent ポリシー, Enrollment Token及び`fleet_bootstrap_enrollment_token_file`で指定したEnrollment Token共有ファイルが作成済みであること。
- 対象ホストのCPU種別が`x86_64`又は`aarch64`であること。

## 実行方法

本ロールを実行する前に, Fleet Bootstrapの実行方法に従ってFleet初期化とEnrollment Token共有ファイルへの保存を完了してください。Enrollment Tokenの作成, 再利用及びEnrollment Token共有ファイルへの保存手順は[../fleet-bootstrap/Readme.md](../fleet-bootstrap/Readme.md)を参照してください。本ロールはEnrollment Tokenを作成又は更新しません。

対象ホストごとに異なるEnrollment Tokenを使用する場合は, 各`host_vars`で`elastic_agent_enrollment_token`を上書きします。Enrollment Tokenが設定済みの場合は, Enrollment Token共有ファイルの読込を省略します。

Elastic Agent本体だけを導入する場合は, 制御ホストで次のコマンドを実行します。

```bash
make run_elastic_agent
```

Elastic Agent本体を対象ホストの有効化変数に対応するElastic Agent ポリシーへ登録する場合は, 次のコマンドを実行します。

```bash
make run_logging_collector
```

## 主要変数

### Elastic Stack間共有設定値

共有設定値の意味, 設定要否, 既定値及び設定例は, [Elasticsearchロールの共有設定値](../elasticsearch/Readme.md#varsall-configymlに設定するelastic-stack間共有設定値)を参照します。本ロールでは, 共通の版数, Fleet Server接続先のURLスキーム及びTLS検証モードが影響します。

### 各ロール固有の利用者入力値

#### 条件付き必須入力値

| 変数名 | 必須となる条件 | 意味 | 設定例 |
| --- | --- | --- | --- |
| `fleet_bootstrap_enrollment_token_file` | `elastic_agent_enrollment_token`を対象ホストへ直接設定しない場合。 | Fleet Bootstrapが生成したEnrollment Token共有ファイルの制御ホスト上の絶対パス。 | `{{ playbook_dir }}/group_vars/logging_collector/enrollment-token.yml` |
| `elastic_agent_enrollment_token` | Enrollment Token共有ファイルを使用しない場合。 | Fleet Serverへの登録に使用する秘密情報。 | 対象のElastic Agent ポリシー用Enrollment Token |

#### 任意入力値

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `elastic_agent_fleet_server_url_explicit` | Fleet Serverの接続先URL明示指定値 | 空文字列 | `https://fleet.example.org:8220` |
| `elastic_agent_tls_mode` | Fleet Server接続時のTLS検証モード | `fleet_server_tls_mode` | `full` |
| `elastic_agent_certificate_authorities` | HTTPS証明書を検証する認証局証明書パス | 空文字列 | `/etc/elastic-agent/certs/ca.crt` |
| `elastic_agent_download_timeout_seconds` | 公式配布物取得時の接続タイムアウト秒数 | `120` | `120` |
| `elastic_agent_download_retries` | 公式配布物取得の再試行回数 | `3` | `3` |
| `elastic_agent_download_retry_delay_seconds` | 公式配布物取得の再試行間隔秒数 | `5` | `5` |
| `elastic_agent_install_timeout_seconds` | 導入処理のタイムアウト秒数 | `300` | `300` |
| `elastic_agent_install_retries` | 導入処理の再試行回数 | `3` | `3` |
| `elastic_agent_install_retry_delay_seconds` | 導入処理の再試行間隔秒数 | `10` | `10` |
| `elastic_agent_service_retries` | サービス起動確認の再試行回数 | `12` | `12` |
| `elastic_agent_service_retry_delay_seconds` | サービス起動確認の再試行間隔秒数 | `5` | `5` |

### 設定例

`vars/all-config.yml`へ非秘密設定を記載する例を次に示します。

```yaml
1: elastic_agent_fleet_server_url_explicit: "https://fleet.example.org:8220"
2: elastic_agent_tls_mode: "full"
3: elastic_agent_certificate_authorities: "/etc/elastic-agent/certs/ca.crt"
4: elastic_agent_download_timeout_seconds: 120
5: elastic_agent_download_retries: 3
6: elastic_agent_download_retry_delay_seconds: 5
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `elastic_agent_fleet_server_url_explicit` | 指定したFleet Serverへ登録します。 | 接続先が誤っている場合は登録に失敗するためです。 |
| 2-3 | TLS検証モードと認証局証明書パス | HTTPS接続時にFleet Server証明書を検証します。 | 証明書検証を省略した場合は通信相手を確認できないためです。 |
| 4-6 | 取得処理のタイムアウト値と再試行値 | 一時的な通信失敗から所定回数復旧を試みます。 | 値が不適切な場合は処理停止又は過剰な再試行が発生するためです。 |

Enrollment Tokenは, Fleet Bootstrapにより次の変数名で`fleet_bootstrap_enrollment_token_file`が示す制御ホスト上のEnrollment Token共有ファイルへ権限`0600`で保存されます。検証コマンドと期待結果は「検証ポイント」を参照してください。

```yaml
1: elastic_agent_enrollment_tokens:
2:   host: "<ホスト監視用Elastic Agent ポリシーのEnrollment Token>"
3:   k8s_system: "<Kubernetesシステム監視用Elastic Agent ポリシーのEnrollment Token>"
4:   k8s_workload: "<Kubernetesワークロード監視用Elastic Agent ポリシーのEnrollment Token>"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1-4 | `elastic_agent_enrollment_tokens` | 対象ホストの有効化変数に対応するElastic Agent ポリシーへ登録します。 | 必要なキーが未設定の場合は入力検証で停止し, 誤設定時はFleet Serverによる登録が拒否されるためです。 |

## テンプレートと生成ファイル

本ロールはテンプレートから設定ファイルを生成しません。Fleet Bootstrapが生成したEnrollment Token共有ファイルを`fleet_bootstrap_enrollment_token_file`から特定して入力として使用します。公式配布物を`elastic_agent_work_dir`へ取得して展開し, Elastic Agentコマンドの`install`処理によりElastic Agentサービスを導入します。導入後の標準配置先はElastic Agent公式仕様に従います。

## 実行フロー

1. 共通変数と対象ホスト変数を読み込みます。
2. `elastic_agent_enrollment_token`が未設定の場合は, Fleet Bootstrapが制御ホスト上へ保存したEnrollment Token共有ファイルの存在と権限`0600`を確認して明示的に読み込みます。
3. Kubernetesワークロード監視用, Kubernetesシステム監視用, ホスト監視用の順で有効化変数を評価し, 対応するElastic Agent ポリシーのEnrollment Tokenを選択します。
4. CPU種別, Fleet Server接続先URL及び公式配布物URLを算出します。
5. Enrollment Token, 通信方式, TLS検証モード及び再試行値を検証します。
6. 展開処理とタイムアウト処理に必要なパッケージを導入します。
7. 対象ホストのサービス登録状態を取得します。
8. Elastic Agentが未導入の場合だけ, 公式配布物をSHA-512検証付きで取得して展開します。
9. Elastic Agentが未導入の場合だけ, Enrollment Token共有ファイルから渡されたEnrollment Tokenを使用してサービス導入とFleet登録を実行します。
10. Elastic Agentサービスを起動し, 自動起動を有効化します。
11. サービスの起動状態と導入版数を検証します。

## 検証ポイント

### 検証の前提条件

検証を始める前に, 次の条件が満たされていることを確認します。

- 対象ホストが`logging_collector`グループへ登録されていること。
- Fleet Serverが起動していること。
- `fleet_bootstrap_enrollment_token_file`で指定したEnrollment Token共有ファイルに有効なEnrollment Tokenが設定され, 権限が`0600`であること。
- 対象ホストからFleet Serverへ接続可能であること。

### 検証環境の設定

本節では, 検証用の設定内容について説明します。

検証環境では「主要変数」の設定例とEnrollment Token共有ファイルを使用します。秘密値を画面や実行ログへ出力する検証は実施しません。

### 検証コマンドと期待結果

#### 1. Elastic Agentサービス状態確認

**実施対象ホスト**: logging_collectorグループに属する対象ホスト

**実行するコマンド**:

```bash
systemctl status elastic-agent --no-pager
```

**期待される出力**:

```plaintext
Active: active (running)
```

**実行結果の例**:

```bash
$ systemctl status elastic-agent --no-pager
systemctl status elastic-agent --no-pager
● elastic-agent.service - Elastic Agent is a unified agent to observe, monitor and protect your system.
     Loaded: loaded (/etc/systemd/system/elastic-agent.service; enabled; preset: disabled)
     Active: active (running) since Sun 2026-08-09 02:08:53 JST; 14h ago
   Main PID: 2760972 (elastic-agent)
      Tasks: 67 (limit: 48838)
     Memory: 778.3M (peak: 978.1M)
        CPU: 2min 24.180s
     CGroup: /system.slice/elastic-agent.service
             ├─2760972 elastic-agent
             ├─2947801 /opt/Elastic/Agent/data/elastic-agent-8.17.3-0efe49/components/age…
             ├─2947807 /opt/Elastic/Agent/data/elastic-agent-8.17.3-0efe49/components/age…
             ├─2947813 /opt/Elastic/Agent/data/elastic-agent-8.17.3-0efe49/components/age…
             ├─2947820 /opt/Elastic/Agent/data/elastic-agent-8.17.3-0efe49/components/age…
             └─2947829 /opt/Elastic/Agent/data/elastic-agent-8.17.3-0efe49/components/age…

Aug 09 02:08:59 observer01 elastic-agent[2760972]: {"log.level":"info","@timestamp":"2026-0…
Hint: Some lines were ellipsized, use -l to show in full.
```

**確認ポイント**:

- `Active:`の行が`active (running)`であることを確認することで, Elastic Agentサービスが実行中であることを確認します。

#### 2. Elastic Agent版数確認

**実施対象ホスト**: logging_collectorグループに属する対象ホスト

**実行するコマンド**:

```bash
sudo elastic-agent version
```

**期待される出力**:

```plaintext
Binary: 8.17.3
Daemon: 8.17.3
```

**実行結果の例**:

```bash
$ sudo elastic-agent version
Binary: 8.17.3 (build: 0efe4920ea5cea17aad2d353244c3d3f04f6162a at 2025-02-27 22:53:35 +0000 UTC)
Daemon: 8.17.3 (build: 0efe4920ea5cea17aad2d353244c3d3f04f6162a at 2025-02-27 22:53:35 +0000 UTC)
```

**確認ポイント**:

- 出力中の版数が`logging_backend_elastic_stack_version`の設定値と一致することで, 共有版数が導入済みであることを確認します。

## トラブルシューティング

### 1. Enrollment Token共有ファイルの入力検証で停止する場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
LANG=C stat -c '%a %F %n' group_vars/logging_collector/enrollment-token.yml
```

**実行結果の例**:

```bash
$ LANG=C stat -c '%a %F %n' group_vars/logging_collector/enr
ollment-token.yml
600 regular file group_vars/logging_collector/enrollment-token.yml
```

**確認ポイント**:

- `stat`コマンドの出力結果が`600 regular file`を含むことを確認することで, Enrollment Token共有ファイルが通常ファイルであり, 所有者だけが読み書き可能であることを確認します。
- Enrollment Tokenの値は画面共有又は実行ログへ出力しないでください。

### 2. Elastic Agentサービスが起動しない場合

**実施対象ホスト**: logging_collectorグループに属する対象ホスト

**実行するコマンド**:

```bash
systemctl status elastic-agent --no-pager
docker logs --tail 200 elastic-agent 2>&1 | grep -E '"log.level"[[:spa
ce:]]*:[[:space:]]*"(warning|error)"'
```

**実行結果の例**:

```bash
$ systemctl status elastic-agent --no-pager
systemctl status elastic-agent --no-pager
● elastic-agent.service - Elastic Agent is a unified agent to observe, monitor and protect your system.
     Loaded: loaded (/etc/systemd/system/elastic-agent.service; enabled; preset: disabled)
     Active: active (running) since Sun 2026-08-09 02:08:53 JST; 14h ago
   Main PID: 2760972 (elastic-agent)
      Tasks: 67 (limit: 48838)
     Memory: 778.3M (peak: 978.1M)
        CPU: 2min 24.180s
     CGroup: /system.slice/elastic-agent.service
             ├─2760972 elastic-agent
             ├─2947801 /opt/Elastic/Agent/data/elastic-agent-8.17.3-0efe49/components/age…
             ├─2947807 /opt/Elastic/Agent/data/elastic-agent-8.17.3-0efe49/components/age…
             ├─2947813 /opt/Elastic/Agent/data/elastic-agent-8.17.3-0efe49/components/age…
             ├─2947820 /opt/Elastic/Agent/data/elastic-agent-8.17.3-0efe49/components/age…
             └─2947829 /opt/Elastic/Agent/data/elastic-agent-8.17.3-0efe49/components/age…

Aug 09 02:08:59 observer01 elastic-agent[2760972]: {"log.level":"info","@timestamp":"2026-0…
Hint: Some lines were ellipsized, use -l to show in full.
$ docker logs --tail 200 elastic-agent 2>&1 | grep -E '"log.level"[[:spa
ce:]]*:[[:space:]]*"(warning|error)"'
$
```

**確認ポイント**:

- `systemctl status elastic-agent --no-pager`の出力結果中の`Active:`を確認することで, サービスの停止状態を確認します。
- `journalctl -u elastic-agent -n 200 --no-pager`の出力結果中の接続失敗又は登録失敗メッセージを確認することで, Fleet Server接続先とEnrollment Tokenの問題を特定します。

## 注意事項

- 1台の対象ホストへ導入できるElastic Agentは1つです。
- 導入済みAgentの再登録は自動実行しません。Enrollment Token又はElastic Agent ポリシーを変更した場合は, Fleet側の運用手順に従って登録状態を変更してください。
- `--force`はFleet上へ重複Agentを作成する可能性があるため使用しません。
- HTTP接続ではEnrollment Tokenが暗号化されません。検証環境以外ではHTTPSと証明書検証を使用してください。
- Enrollment Tokenの値を`vars/all-config.yml`, Git管理対象のファイル又は実行ログへ保存しないでください。
- Fleet管理型Elastic Agentの更新はFleetから実行してください。

## 参考資料

### 公式ドキュメント

- [ansible-playbookコマンド](https://docs.ansible.com/ansible/latest/cli/ansible-playbook.html)
- [makeコマンドとMakefile](https://www.gnu.org/software/make/manual/make.html)
- [systemctlコマンド](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)
- [journalctlコマンド](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)
- [Elastic Agent](https://www.elastic.co/docs/reference/fleet/install-elastic-agents)
- [elastic-agentコマンド](https://www.elastic.co/docs/reference/fleet/agent-command-reference)
- [Fleet Server](https://www.elastic.co/docs/reference/fleet/fleet-server)
- [Enrollment Token](https://www.elastic.co/docs/reference/fleet/fleet-enrollment-tokens)
- [Service accounts and tokens](https://www.elastic.co/guide/en/elasticsearch/reference/current/service-accounts.html)
- [Elastic Agentポリシー](https://www.elastic.co/docs/reference/fleet/agent-policy)
- [HTTP](https://www.rfc-editor.org/rfc/rfc9110)
- [HTTPS](https://www.rfc-editor.org/rfc/rfc2818)
- [TLS](https://www.rfc-editor.org/rfc/rfc8446)
- [URL](https://www.rfc-editor.org/rfc/rfc3986)
- [Ansible Inventory](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html)

### 関連ロール

- [roles/elasticsearch/Readme.md](../elasticsearch/Readme.md) Elasticsearch関連コンポーネント全体の仕様についての解説を記載しています。以下の内容について確認する場合に参照します。
  - 設計背景と非干渉条件
  - Elasticsearch 関連コンポーネント構成図
  - 各コンテナの役割分担
  - inventory group と展開されるコンテナとの対応関係
