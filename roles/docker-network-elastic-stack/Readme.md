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
| Ansible | - | 対象ホストへ所定の設定を適用する処理を自動化するソフトウェア。 |
| Ansible Playbook | Playbook | Ansibleで実行する処理の順序と対象を記述したファイル。 |
| Classless Inter-Domain Routing | CIDR | Internet Protocolアドレスの範囲を先頭アドレスと接頭辞長で表す方式。 |
| Docker | - | コンテナイメージとコンテナ及びコンテナ用ネットワークを管理するソフトウェア。 |
| Docker bridge network | Dockerブリッジネットワーク | 同一対象ホスト上のコンテナ間通信に使用する仮想的なネットワーク。 |
| Internet Protocol | IP | ネットワーク上の通信元と通信先を識別する通信手順。 |
| iptables | - | Linux の IPv4 パケットフィルタ設定ツール。 |
| ip6tables | - | Linux の IPv6 パケットフィルタ設定ツール。 |
| Network Address Translation | NAT | 通信時にIPアドレスを変換する処理。 |
| systemd | - | Linux上でサービスの起動順序と実行状態を管理するソフトウェア。 |
| Python | - | スクリプティングやアプリケーション開発を手早く実施するために用いられる高水準プログラミング言語の一種。 |
| 制御ホスト | - | Playbookを実行し, 対象ホストへ処理を指示するホスト。 |
| 対象ホスト | - | Dockerブリッジネットワークとiptables規則を設定するホスト。 |
| ansible-playbookコマンド | - | Playbookを実行して対象ホストへ設定を適用するコマンド。 |
| dockerコマンド | - | Dockerブリッジネットワークを作成及び確認するコマンド。 |
| iptablesコマンド | - | IPパケットの通過条件とNAT規則を確認するコマンド。 |
| ip6tablesコマンド | - | IPv6パケットの通過条件とNAT規則を確認するコマンド。 |
| systemctlコマンド | - | systemdが管理するサービスの状態を確認するコマンド。 |
| jqコマンド | jq | JSON 形式のデータから必要な項目だけを抽出して表示するコマンド。 |

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
| `docker_network_elastic_stack_retry_delay_seconds` | Dockerネットワーク検証を再実行するまでの待機秒数。 | `2` | `2` |
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
3: docker_network_elastic_stack_retry_delay_seconds: 3
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `docker_network_elastic_stack_command_timeout_seconds: 60` | Docker, iptables及びip6tablesの各コマンドを最大60秒待ちます。 | 実行環境の応答時間より短い値では正常な処理を異常終了と判定するため, 実行環境に合う値を指定します。 |
| 2-3 | `docker_network_elastic_stack_retries: 5`, `docker_network_elastic_stack_retry_delay_seconds: 3` | Dockerネットワーク検証を3秒間隔で最大5回実行します。 | 一時的なDocker応答失敗を直ちに恒久障害と判定しないため, 再試行条件を指定します。 |

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
