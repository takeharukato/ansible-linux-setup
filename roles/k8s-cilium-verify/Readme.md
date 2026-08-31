# k8s-cilium-verify ロール

本ロールは, Cilium DaemonSet, Cilium Operator Deployment, Hubble Relay DeploymentおよびHubble Relay APIの実行時状態を検証するロールです。

## 目次

- [k8s-cilium-verify ロール](#k8s-cilium-verify-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
    - [設定例](#設定例)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [検証の前提条件](#検証の前提条件)
    - [検証環境の設定](#検証環境の設定)
    - [検証コマンドと期待結果](#検証コマンドと期待結果)
      - [1. 通常構築時のCilium関連検証ログ確認](#1-通常構築時のcilium関連検証ログ確認)
      - [2. 構築済みクラスタに対する再検証ログ確認](#2-構築済みクラスタに対する再検証ログ確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. Cilium DaemonSetのReady数が配置対象数に到達しない場合](#1-cilium-daemonsetのready数が配置対象数に到達しない場合)
    - [2. Hubble Relay DeploymentがReadyにならない場合](#2-hubble-relay-deploymentがreadyにならない場合)
    - [3. Hubble Relay API接続確認が失敗する場合](#3-hubble-relay-api接続確認が失敗する場合)
  - [注意事項](#注意事項)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| ユーザ | - | 機能を利用する人, 又は識別された利用主体。 |
| ツール | - | 特定作業を実行するための機能や道具。 |
| リソース | - | 処理に必要な計算機資源やデータ。 |
| クラスタ | - | 複数の機器を連携させて一体運用する構成。 |
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
| Kubernetes | K8s | コンテナを管理する基盤ソフトウェア。 |
| Pod | - | Kubernetes でコンテナをまとめて管理する最小単位。 |
| Linux | - | 多くの機器で使われる, 基本ソフトウェアの系統。 |
| Debian | - | コミュニティ主導で開発される Linux ディストリビューション。 |
| Ubuntu | - | Canonical が提供する Debian 系の Linux ディストリビューション。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| control plane ノード | - | Kubernetes の制御機能を担うノード。 |
| worker ノード | - | Kubernetes 上で動作するアプリケーションを実行するノード。 |
| Multus | - | 複数のCNIプラグインを同時に使用できるようにするメタCNIプラグイン。 |
| Whereabouts | - | Kubernetes 上で複数のネットワークインタフェースに対応する IPAM (IP Address Management) プラグイン。 |
| レプリカ ( Replica ) | - | ポッド ( Pod ) の複製。デプロイメント ( Deployment ) などのリソースが高可用性や負荷分散のために複数のレプリカを作成, 管理します。指定されたレプリカ数に基づいて同一の仕様を持つポッドが複数実行される。 |
| kubeconfig | - | Kubernetes API接続先と認証情報を記述した設定ファイル。 |
| kubectlコマンド | kubectl | Kubernetes API と通信してリソースを操作, 参照するコマンド。 |
| makeコマンド | make | Makefile に定義された処理を実行するコマンド。 |
| grepコマンド | grep | テキストの中から条件に一致する行を抽出するコマンド。 |
| DaemonSet | - | Kubernetesで各ノードへPodを常駐配置するリソース。 |
| Deployment | - | Kubernetesで複数のPodの作成, 更新, 維持を管理するリソース。 |
| Cilium | - | Kubernetesクラスタ内のPod通信とネットワーク制御を提供するソフトウェア。 |
| Cilium Operator | - | Ciliumのクラスタ全体に関係する制御処理を実行する構成要素。 |
| Hubble | - | Ciliumが処理するネットワーク通信の状態を観測する機能。 |
| Hubble Relay | - | 各ノードのHubble情報を集約し, Hubble CLIなどから参照できるようにする構成要素。 |
| Hubble CLI | hubble | Hubble Relayへ接続し, Hubbleの状態や通信情報を参照するコマンド。 |
| timeoutコマンド | timeout | 指定した時間を超えて実行中のコマンドを終了させるコマンド。 |
| Ready | - | Kubernetesリソースが処理を受け付けられる状態であることを示す状態。 |
| Available | - | Kubernetes Deploymentで利用可能なPod数が必要数を満たす状態。 |

## 概要

本ロールは, MultusとWhereaboutsの再構築後にCilium関連リソースとHubble Relayの実行時状態を検証するロールです。

本ロールは次の処理を実行します。

- Cilium DaemonSetで配置対象数, 最新状態への更新数, Ready数, Available数が一致するまで再試行します。
- Cilium Operator Deploymentで指定レプリカ数, 更新済みレプリカ数, Readyレプリカ数, Availableレプリカ数が一致するまで再試行します。
- Hubble Relay Deploymentで指定レプリカ数, 更新済みレプリカ数, Readyレプリカ数, Availableレプリカ数が一致するまで再試行します。
- Hubble CLIの`hubble status --port-forward`を実行し, Hubble RelayのHealthcheckが`Ok`であることを確認します。
- `Connected Nodes: N/N`の接続済みノード数と総ノード数が1件以上かつ一致することを確認します。
- Kubernetes API要求とHubble Relay機能確認に通信待機時間と再試行条件を設定し, 利用者が値を変更できるようにします。

通常のKubernetesクラスタ構築では, `k8s-management.yml`により`k8s-multus`, `k8s-whereabouts`の後に本ロールを実行します。`make run_k8s_cilium_verify`は, MultusとWhereaboutsが構築済みのクラスタに対する再検証専用です。

## 前提条件

- Kubernetesクラスタのcontrol plane ノードが構築済みで, Kubernetes APIへ接続できること。
- worker ノードが対象Kubernetesクラスタへ参加済みであること。
- MultusとWhereaboutsが現在のKubernetesクラスタ向けに構築済みであること。
- Cilium DaemonSet, Cilium Operator Deployment, Hubble Relay Deploymentが`kube-system`名前空間へ導入済みであること。
- 対象ホストでkubectlコマンドを実行可能であること。
- `k8s_cilium_verify_kubeconfig_path`に指定したkubeconfigが通常ファイルとして存在すること。
- `k8s_cilium_verify_hubble_binary_path`に指定したHubble CLIが実行可能な通常ファイルとして存在すること。

## 実行方法

通常のKubernetesクラスタ構築では, 制御ホストで次のmakeコマンドを実行します。

```bash
make
```

このmakeコマンドは`site.yml`を実行し, `k8s-management.yml`の一連処理としてMultusとWhereaboutsの構築後に本ロールを実行します。実行結果は`build.log`へ保存されるため, 通常構築時の検証ではこのログを確認します。

MultusとWhereaboutsが現在のKubernetesクラスタ向けに構築済みであり, Cilium関連機能だけを再検証する場合は, 制御ホストで次のmakeコマンドを実行します。

```bash
make run_k8s_cilium_verify
```

このmakeコマンドは`k8s-cilium-verify`タグだけを実行し, 実行結果を`build-k8s-cilium-verify.log`へ保存します。MultusとWhereaboutsは再構築しないため, このmakeコマンドは構築済みクラスタに対する再検証専用です。

## 主要変数

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `k8s_cilium_verify_kubeconfig_path` | Kubernetes API検証に使用するkubeconfig。 | `"/etc/kubernetes/admin.conf"` | `"/etc/kubernetes/admin.conf"` |
| `k8s_cilium_verify_hubble_binary_path` | Hubble Relay機能確認に使用するHubble CLIのパス。 | `"/usr/local/bin/hubble"` | `"/usr/local/bin/hubble"` |
| `k8s_cilium_verify_request_timeout_seconds` | kubectlコマンドによるKubernetes API要求1回のtimeout秒数。 | `10` | `10` |
| `k8s_cilium_verify_retry_interval_seconds` | KubernetesリソースとHubble Relay機能確認を再試行する間隔秒数。 | `5` | `5` |
| `k8s_cilium_verify_retries` | KubernetesリソースとHubble Relay機能確認の最大再試行回数。 | `60` | `60` |
| `k8s_cilium_verify_hubble_timeout_seconds` | Hubble CLIを1回実行する際のtimeout秒数。 | `30` | `30` |

### 設定例

基本的には設定値を修正する必要はありませんが, 設定する場合は,
`vars/all-config.yml`へ次の値を設定します。

```yaml
1: k8s_cilium_verify_kubeconfig_path: "/etc/kubernetes/admin.conf"
2: k8s_cilium_verify_hubble_binary_path: "/usr/local/bin/hubble"
3: k8s_cilium_verify_request_timeout_seconds: 10
4: k8s_cilium_verify_retry_interval_seconds: 5
5: k8s_cilium_verify_retries: 60
6: k8s_cilium_verify_hubble_timeout_seconds: 30
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | `/etc/kubernetes/admin.conf` | Kubernetes API検証で管理者用kubeconfigを使用します。 | 存在しないファイルを指定するとKubernetes API検証を開始できないため, 対象クラスタのkubeconfigを指定します。 |
| 2 | `/usr/local/bin/hubble` | Hubble Relay機能確認で指定したHubble CLIを使用します。 | 実行できないファイルを指定するとHubble Relay機能確認を開始できないため, 導入済みHubble CLIを指定します。 |
| 3 | `10` | Kubernetes API要求1回を最大10秒待ちます。 | 実行環境より短い値では一時的な応答遅延を異常終了と判定するため, 環境に合う値を指定します。 |
| 4-5 | `5`, `60` | 5秒間隔で最大60回, KubernetesリソースとHubble Relayを再確認します。 | Pod起動途中の過渡状態を恒久障害と判定しないため, 最大待機時間を制御可能にします。 |
| 6 | `30` | Hubble CLIを1回につき最大30秒実行します。 | Hubble Relayへの接続が完了しない場合に処理が無期限に停止することを防止します。 |

設定後の確認方法は[検証コマンドと期待結果](#検証コマンドと期待結果)を参照してください。

## テンプレートと生成ファイル

本ロールはテンプレートからファイルを生成しません。

## 実行フロー

1. チェックモードの場合は実行時検証をスキップします。
2. kubeconfig, Hubble CLIのパス, 通信待機時間と再試行条件の入力値を検証します。
3. kubeconfigが通常ファイルとして存在することを確認します。
4. Cilium DaemonSetが最新の世代番号で全配置対象PodがReadyかつAvailableになるまで再試行します。
5. Cilium Operator DeploymentとHubble Relay Deploymentを共通Deployment検証処理で確認します。
6. Hubble CLIが実行可能な通常ファイルであることを確認します。
7. timeoutコマンドを使用して`hubble status --port-forward`を実行し, Hubble RelayのHealthcheckと接続ノード数を確認します。
8. `Connected Nodes`の接続済みノード数と総ノード数を抽出し, 総ノード数が1件以上かつ両者が一致することを確認します。

## 検証ポイント

### 検証の前提条件

検証を始める前に, 次の条件が満たされていることを確認します。

- Kubernetesクラスタへworker ノードが参加済みであること。
- MultusとWhereaboutsが現在のKubernetesクラスタ向けに構築済みであること。
- Cilium DaemonSet, Cilium Operator Deployment, Hubble Relay Deploymentが`kube-system`名前空間に存在すること。
- 通常構築を`make`で実行した場合は`build.log`が生成されていること。
- 再検証を`make run_k8s_cilium_verify`で実行した場合は`build-k8s-cilium-verify.log`が生成されていること。

### 検証環境の設定

本節では, 検証用の設定内容について説明します。

**検証用の host_vars**:

```yaml
1: k8s_cilium_verify_kubeconfig_path: "/etc/kubernetes/admin.conf"
2: k8s_cilium_verify_hubble_binary_path: "/usr/local/bin/hubble"
3: k8s_cilium_verify_request_timeout_seconds: 10
4: k8s_cilium_verify_retry_interval_seconds: 5
5: k8s_cilium_verify_retries: 60
6: k8s_cilium_verify_hubble_timeout_seconds: 30
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1-2 | kubeconfigとHubble CLIのパス | 対象クラスタに対するKubernetes API検証とHubble Relay機能確認を実行します。 | 別クラスタ又は存在しないファイルを参照すると検証対象を誤るためです。 |
| 3-6 | 通信待機時間と再試行条件 | 外部通信を待機上限付きで再試行します。 | 一時的な応答遅延による誤検知と無期限待機を防止するためです。 |

### 検証コマンドと期待結果

#### 1. 通常構築時のCilium関連検証ログ確認

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
grep -F \
  -e 'TASK [k8s-cilium-verify : Wait for Cilium DaemonSet readiness]' \
  -e 'TASK [k8s-cilium-verify : Wait for cilium-operator Deployment readiness]' \
  -e 'TASK [k8s-cilium-verify : Wait for hubble-relay Deployment readiness]' \
  -e 'TASK [k8s-cilium-verify : Verify Hubble Relay API access]' \
  -e 'TASK [k8s-cilium-verify : Assert Hubble Relay API status is healthy]' \
  -e 'Healthcheck (via ' \
  -e 'Connected Nodes:' \
  -e 'PLAY RECAP' \
  -e 'failed=0' \
  build.log
```

**期待される出力**:

```plaintext
TASK [k8s-cilium-verify : Wait for Cilium DaemonSet readiness] *****************
TASK [k8s-cilium-verify : Wait for cilium-operator Deployment readiness] ******
TASK [k8s-cilium-verify : Wait for hubble-relay Deployment readiness] *********
TASK [k8s-cilium-verify : Verify Hubble Relay API access] **********************
Healthcheck (via 127.0.0.1:4245): Ok
Connected Nodes: 3/3
TASK [k8s-cilium-verify : Assert Hubble Relay API status is healthy] ***********
PLAY RECAP *********************************************************************
k8sctrlplane01.local : ... unreachable=0 failed=0 ...
k8sctrlplane02.local : ... unreachable=0 failed=0 ...
```

**実行結果の例**:

```bash
$ grep -F \
  -e 'TASK [k8s-cilium-verify : Wait for Cilium DaemonSet readiness]' \
  -e 'TASK [k8s-cilium-verify : Wait for cilium-operator Deployment readiness]' \
  -e 'TASK [k8s-cilium-verify : Wait for hubble-relay Deployment readiness]' \
  -e 'TASK [k8s-cilium-verify : Verify Hubble Relay API access]' \
  -e 'TASK [k8s-cilium-verify : Assert Hubble Relay API status is healthy]' \
  -e 'Healthcheck (via ' \
  -e 'Connected Nodes:' \
  -e 'PLAY RECAP' \
  -e 'failed=0' \
  build.log
TASK [k8s-cilium-verify : Wait for Cilium DaemonSet readiness] *****************
TASK [k8s-cilium-verify : Wait for cilium-operator Deployment readiness] *******
TASK [k8s-cilium-verify : Wait for hubble-relay Deployment readiness] **********
TASK [k8s-cilium-verify : Verify Hubble Relay API access] **********************
<k8sctrlplane01.local> (0, b'\r\n{"changed": true, "stdout": "Healthcheck (via 127.0.0.1:4245): Ok\\nCurrent/Max Flows: 8,378/12,285 (68.20%)\\nFlows/s: 51.15\\nConnected Nodes: 3/3", "stderr": "", "rc": 0, "cmd": ["env", "KUBECONFIG=/etc/kubernetes/admin.conf", "timeout", "30s", "/usr/local/bin/hubble", "status", "--port-forward"], "start": "2026-08-31 03:42:05.083288", "end": "2026-08-31 03:42:05.174729", "delta": "0:00:00.091441", "msg": "", "invocation": {"module_args": {"argv": ["env", "KUBECONFIG=/etc/kubernetes/admin.conf", "timeout", "30s", "/usr/local/bin/hubble", "status", "--port-forward"], "_uses_shell": false, "expand_argument_vars": true, "stdin_add_newline": true, "strip_empty_ends": true, "_raw_params": null, "chdir": null, "executable": null, "creates": null, "removes": null, "stdin": null}}}\r\n', b'Shared connection to k8sctrlplane01.local closed.\r\n')
    "stdout": "Healthcheck (via 127.0.0.1:4245): Ok\nCurrent/Max Flows: 8,378/12,285 (68.20%)\nFlows/s: 51.15\nConnected Nodes: 3/3",
        "Healthcheck (via 127.0.0.1:4245): Ok",
        "Connected Nodes: 3/3"
<k8sctrlplane02.local> (0, b'\r\n{"changed": true, "stdout": "Healthcheck (via 127.0.0.1:4245): Ok\\nCurrent/Max Flows: 12,285/12,285 (100.00%)\\nFlows/s: 88.70\\nConnected Nodes: 3/3", "stderr": "", "rc": 0, "cmd": ["env", "KUBECONFIG=/etc/kubernetes/admin.conf", "timeout", "30s", "/usr/local/bin/hubble", "status", "--port-forward"], "start": "2026-08-31 03:42:05.202123", "end": "2026-08-31 03:42:05.263133", "delta": "0:00:00.061010", "msg": "", "invocation": {"module_args": {"argv": ["env", "KUBECONFIG=/etc/kubernetes/admin.conf", "timeout", "30s", "/usr/local/bin/hubble", "status", "--port-forward"], "_uses_shell": false, "expand_argument_vars": true, "stdin_add_newline": true, "strip_empty_ends": true, "_raw_params": null, "chdir": null, "executable": null, "creates": null, "removes": null, "stdin": null}}}\r\n', b'Shared connection to k8sctrlplane02.local closed.\r\n')
    "stdout": "Healthcheck (via 127.0.0.1:4245): Ok\nCurrent/Max Flows: 12,285/12,285 (100.00%)\nFlows/s: 88.70\nConnected Nodes: 3/3",
        "Healthcheck (via 127.0.0.1:4245): Ok",
        "Connected Nodes: 3/3"
TASK [k8s-cilium-verify : Assert Hubble Relay API status is healthy] ***********
PLAY RECAP *********************************************************************
k8sctrlplane01.local       : ok=782  changed=83   unreachable=0    failed=0    skipped=332  rescued=0    ignored=0
k8sctrlplane02.local       : ok=678  changed=36   unreachable=0    failed=0    skipped=335  rescued=0    ignored=0
```

**確認ポイント**:

- `Wait for Cilium DaemonSet readiness`が出力され, その後も後続の検証タスクが実行されていることを確認することで, Cilium DaemonSetのreadiness検証が成功したことを確認します。
- `Wait for cilium-operator Deployment readiness`と`Wait for hubble-relay Deployment readiness`が出力され, その後も後続の検証タスクが実行されていることを確認することで, Cilium Operator DeploymentとHubble Relay Deploymentのreadiness検証が成功したことを確認します。
- `Healthcheck (via 127.0.0.1:4245): Ok`が出力されることを確認することで, Hubble Relay APIへの接続確認が成功したことを確認します。
- `Connected Nodes: N/N`の左辺と右辺が1件以上かつ同一値であることを確認することで, Hubble Relayが全Ciliumノードへ接続済みであることを確認します。
- `Assert Hubble Relay API status is healthy`の後に`PLAY RECAP`まで処理が継続し, 対象ホストの`unreachable=0`と`failed=0`が出力されることを確認することで, 本ロールの全検証処理が成功したことを確認します。

#### 2. 構築済みクラスタに対する再検証ログ確認

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
grep -F \
  -e 'TASK [k8s-cilium-verify : Assert Hubble Relay API status is healthy]' \
  -e 'Healthcheck (via ' \
  -e 'Connected Nodes:' \
  -e 'PLAY RECAP' \
  -e 'failed=0' \
  build-k8s-cilium-verify.log
```

**期待される出力**:

```plaintext
Healthcheck (via 127.0.0.1:4245): Ok
Connected Nodes: 3/3
TASK [k8s-cilium-verify : Assert Hubble Relay API status is healthy] ***********
PLAY RECAP *********************************************************************
k8sctrlplane01.local : ... unreachable=0 failed=0 ...
k8sctrlplane02.local : ... unreachable=0 failed=0 ...
```

**実行結果の例**:

```bash
$ grep -F \
    -e 'TASK [k8s-cilium-verify : Assert Hubble Relay API status is healthy]' \
    -e 'Healthcheck (via ' \
    -e 'Connected Nodes:' \
    -e 'PLAY RECAP' \
    -e 'failed=0' \
    build-k8s-cilium-verify.log
Healthcheck (via 127.0.0.1:4245): Ok
Connected Nodes: 3/3
TASK [k8s-cilium-verify : Assert Hubble Relay API status is healthy] ***********
PLAY RECAP *********************************************************************
k8sctrlplane01.local : ok=21 changed=0 unreachable=0 failed=0 skipped=2 rescued=0 ignored=0
k8sctrlplane02.local : ok=21 changed=0 unreachable=0 failed=0 skipped=2 rescued=0 ignored=0
```

**確認ポイント**:

- `Healthcheck`が`Ok`であり, `Connected Nodes`の接続済みノード数と総ノード数が一致することを確認することで, Hubble Relayの機能確認が成功したことを確認します。
- `PLAY RECAP`で対象ホストの`unreachable=0`と`failed=0`が出力されることを確認することで, 再検証処理が正常終了したことを確認します。

## トラブルシューティング

### 1. Cilium DaemonSetのReady数が配置対象数に到達しない場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
kubectl --kubeconfig /etc/kubernetes/admin.conf --namespace kube-system get daemonset cilium
kubectl --kubeconfig /etc/kubernetes/admin.conf --namespace kube-system get pods -l k8s-app=cilium -o wide
```

**確認ポイント**:

- kubectlコマンドの出力結果中の`DESIRED`, `READY`, `AVAILABLE`が一致しないノードを確認することで, Cilium Podが利用可能になっていない範囲を確認します。

### 2. Hubble Relay DeploymentがReadyにならない場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
kubectl --kubeconfig /etc/kubernetes/admin.conf --namespace kube-system get deployment hubble-relay
kubectl --kubeconfig /etc/kubernetes/admin.conf --namespace kube-system get pods -l k8s-app=hubble-relay -o wide
kubectl --kubeconfig /etc/kubernetes/admin.conf --namespace kube-system logs deployment/hubble-relay
```

**確認ポイント**:

- kubectlコマンドの出力結果中のHubble Relay Deploymentの`READY`と`AVAILABLE`が指定レプリカ数に到達していることを確認します。
- Hubble Relayのログに接続失敗又は名前解決失敗が表示されている場合は, 表示された接続先を根拠にKubernetesクラスタ側の状態を調査します。原因を確定する前に設定変更を行いません。

### 3. Hubble Relay API接続確認が失敗する場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
env KUBECONFIG=/etc/kubernetes/admin.conf timeout 30s /usr/local/bin/hubble status --port-forward
```

**確認ポイント**:

- Hubble CLIの出力結果中の`Healthcheck`が`Ok`であることを確認します。
- Hubble CLIの出力結果中の`Connected Nodes`を確認し, 接続済みノード数が総ノード数より少ない場合は, 未接続ノードを特定してから原因を調査します。

## 注意事項

- 通常のKubernetesクラスタ構築では, MultusとWhereaboutsを現在のKubernetesクラスタ向けに再構築した後に本ロールを実行します。
- `make run_k8s_cilium_verify`は再検証専用です。このmakeコマンドはMultusとWhereaboutsを構築しません。
- チェックモードではKubernetes APIとHubble Relayへの実通信を行わないため, 実行時検証をスキップします。
- `k8s_cilium_verify_retries`と`k8s_cilium_verify_retry_interval_seconds`は, worker ノード参加後のPod起動時間と実行環境の応答時間に合わせて設定します。
- Hubble Relay API接続確認ではHubble CLIの`--port-forward`を使用し, Hubble Relay Serviceへの一時的な転送を自動的に設定します。

## 参考資料

### 公式ドキュメント

- [Kubernetes - DaemonSet](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)
- [Kubernetes - Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes - kubectl](https://kubernetes.io/docs/reference/kubectl/)
- [Cilium - Setting up Hubble Observability](https://docs.cilium.io/en/stable/observability/hubble/setup/)
