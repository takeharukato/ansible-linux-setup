# k8s-devel ロール

Kubernetes 開発向けの言語別 Client ライブラリ導入を行うロールです。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Application Programming Interface | API | アプリケーション同士がやり取りする方法を定めた仕様。 |
| Custom Resource Definition | CRD | Kubernetes APIを拡張してユーザ独自のリソース種別を定義する仕組み。 |
| Role-Based Access Control | RBAC | ユーザやサービスアカウントが実行可能な操作を役割(Role)で制限する仕組み。 |
| Service Account | - | Kubernetes内部でPodが他のリソースにアクセスする際に用いる仮想的なアカウント。 |
| ClusterRole | - | Kubernetesクラスタ全体に適用される権限の集合。 |
| ClusterRoleBinding | - | ClusterRoleをユーザやサービスアカウントに紐付ける仕組み。 |
| Role | - | 特定の名前空間内で有効な権限の集合。 |
| RoleBinding | - | Roleをユーザやサービスアカウントに紐付ける仕組み。 |
| 名前空間 (namespace) | - | Kubernetes内部でリソースを論理的に分離する単位。 |
| ポッド ( Pod ) | - | Kubernetes上で動作するコンテナの最小単位。 |
| デーモンセット ( DaemonSet ) | - | Kubernetesクラスタ内の全ノード(または指定した一部のノード)で必ずPodを1つずつ起動させるリソース。 |
| デプロイメント ( Deployment ) | - | 指定した数のPodを維持し, ローリングアップデート等を管理するリソース。 |
| StatefulSet | - | 状態を持つアプリケーションのPodを順序付けて管理するリソース。 |
| サービス ( Service ) | - | Podへのアクセスを抽象化し, 負荷分散やサービスディスカバリを提供するリソース。 |
| Ingress | - | Kubernetesクラスタ外部からHTTP/HTTPS通信を受け付け, 内部のServiceへルーティングする仕組み。 |
| コンフィグマップ ( ConfigMap ) | - | 設定情報を保持し, Podへ環境変数やファイルとして注入するリソース。 |
| シークレット ( Secret ) | - | 機密情報を保持し, Podへ安全に注入するリソース。 |
| PersistentVolume | PV | Kubernetesクラスタ内で利用可能なストレージリソースを表すオブジェクト。 |
| PersistentVolumeClaim | PVC | ユーザがPVを要求する際に利用するリソース。 |
| StorageClass | - | 動的にPVをプロビジョニングする際のストレージ種別を定義するリソース。 |
| Kubernetes ノード ( Kubernetes Node ) | - | Kubernetesクラスタを構成する物理マシンまたは仮想マシン。 |
| コントロールプレーンノード ( Control Plane Node ) | - | Kubernetesクラスタ全体を管理, 制御する中枢ノード群。kube-apiserver, kube-controller-manager, kube-schedulerなどが動作する。 |
| ワーカノード ( Worker Node ) | - | 実際にアプリケーションのPodを実行するノード。 |
| kube-apiserver | - | KubernetesのAPIリクエストを受け付け, etcdへの読み書きを仲介するコンポーネント。 |
| kube-controller-manager | - | Deployment, ReplicaSetなど各種コントローラを実行し, Kubernetesクラスタの状態を監視, 調整するコンポーネント。 |
| kube-scheduler | - | 新規作成されたPodを適切なNodeへ配置するコンポーネント。 |
| kubelet | - | 各Node上で動作し, Podの起動, 停止, 監視を行うエージェント。 |
| kube-proxy | - | 各Node上でServiceのネットワークルールを管理するコンポーネント。 |
| etcd | - | KubernetesのKubernetesクラスタ状態を保存する分散Key-Valueストア。 |
| Container Network Interface | CNI | コンテナ間のネットワーク接続を標準化するプラグイン仕様。 |
| Cilium | - | eBPFを活用した高性能なCNIプラグイン。ネットワークポリシーやサービスメッシュ機能を提供する。 |
| Serviceエンドポイント ( Service Endpoint ) | - | Serviceのバックエンドとして通信を受けるPod, または, 当該の通信を受けるPodに加え, 当該の通信を受けるPodへ通信を届けるためのネットワーク上の転送先情報全体を指す。 |
| Serviceエンドポイント情報 ( Service Endpoint Information ) | - | Serviceエンドポイントを特定して転送先を決めるための情報。主にバックエンドPodのIPアドレス, ポート番号, プロトコル, 所属クラスタ名(またはクラスタ識別子)で構成される。 |
| Multus | - | 複数のCNIプラグインを同時に使用できるようにするメタCNIプラグイン。 |
| Container Runtime Interface | CRI | Kubernetesがコンテナランタイムと通信するための標準インターフェース。 |
| containerd | - | Dockerから分離された軽量なコンテナランタイム。 |
| kubeadm | - | Kubernetesクラスタの初期構築と管理を支援する公式ツール。 |
| kubectl | - | Kubernetesクラスタを操作するためのコマンドラインツール。 |
| Helm | - | Kubernetesアプリケーションのパッケージ管理ツール。Chart形式でアプリケーションを配布, インストールする。 |
| Chart | - | Helmで管理されるアプリケーションパッケージの単位。Kubernetes Manifestのテンプレート集。 |
| Operator | - | アプリケーション固有の運用知識をコードで自動化するKubernetesの拡張パターン。 |
| Custom Resource | CR | CRDで定義されたユーザ独自のリソースの実体。 |
| Admission Controller | - | APIリクエストがetcdに保存される前に検証, 変更を行うプラグイン。 |
| Network Policy | - | Pod間の通信を制御するファイアウォールルールを定義するリソース。 |
| Label | - | リソースに付与するKey-Value形式のメタデータ。リソースの分類, 検索に利用される。 |
| Selector | - | Labelを利用してリソースを選択する条件式。 |
| Annotation | - | リソースに付与するKey-Value形式の補足情報。ツールやコントローラが参照するメタデータ。 |
| Taint | - | Kubernetes ノードに設定する特殊なマークで, 特定の条件を満たさないPodの配置を拒否する。 |
| Toleration | - | PodがTaintを持つNodeへ配置されることを許可する設定。 |
| Python Enhancement Proposal | PEP | Python の機能改善や標準化を提案・議論するための公式文書体系。ソフトウェア開発における仕様策定の枠組み。 |
| End-of-Life | EOL | ソフトウェアやシステムのサポート終了状態。セキュリティ更新や機能追加が停止される。 |

## 概要

本ロールは Kubernetes 開発環境向けに, Python, Go, C (将来対応) の各言語で Kubernetes API を操作するための Client ライブラリを導入します。

本ロールは Go 導入処理を直接実施せず, 導入済みの Go 実行環境を利用して Go 言語版 Kubernetes client を導入します。版数指定時の Go 導入処理は `go-lang-local` ロールを playbook 側で実行します。

主な機能:

- **Python 言語版 Kubernetes client の導入方式切替**: 既定では `python-k8s-client-local` ロールに委譲して, ローカルパッケージ方式で導入します。`k8s_devel_python_client_install_via_pip=true` を明示した場合のみ, 互換運用として pip 導入を行います。
- **Kubernetes 版数からの client 既定版数導出**: `k8s_major_minor` (例: `1.31`) から, Python 言語版 Kubernetes client は `~=31.0`, Go 言語版 Kubernetes client は `v0.31.0` を導出します。
- **PEP 668 対応 (pip導入モード時)**: Ubuntu 24.04 以降では PEP 668 (外部管理環境) によりシステム Python への直接導入が制限されるため, pip導入モードでは自動的に `--break-system-packages` を付与します。
- **Go client 導入前の事前検証**: `k8s_devel_go_client_enabled=true` の場合, `golang` / `golang-go` / `go-lang` の導入有無を確認し, 未導入なら `fail` で停止します。

## 前提条件

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- `repo-deb` または `repo-rpm` が先に適用され, `k8s_major_minor` が定義されていることを前提とします。
- Ubuntu 24.04 以降で pip導入モードを利用する場合は, PEP 668 (外部管理環境) により `--break-system-packages` が必要です。本ロールは pip導入モード時に自動付与します。

## 実行フロー

本ロールは以下の順序で処理を実行します:

1. **パラメータ読み込み** (`load-params.yml`): OS 別パッケージ定義 (`vars/packages-ubuntu.yml`, `vars/packages-rhel.yml`) と共通変数 (`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込みます。
2. **版数導出** (`post-load-params.yml`): `k8s_major_minor` (例: `1.31`) から Python 言語版 Kubernetes client と Go 言語版 Kubernetes client の既定版数を導出します。
   - Python 言語版 Kubernetes client: `~=<minor>.0` (例: `~=31.0`) 形式で互換バージョン指定 (PEP 440) を生成します。pip が該当系列の最新版を自動選択します。
   - Go 言語版 Kubernetes client: `v0.<minor>.0` (例: `v0.31.0`) 形式で版数を生成します。client-go は常にメジャー版数が `0` で, Kubernetes のマイナー版数がそのままマイナー版数になります。
   - `k8s_major_minor` の形式検証 (`^[0-9]+\.[0-9]+$`) を実施します。形式不正時は `k8s_devel_skip_version_derivation=true` を設定し, 後段の `package.yml` 実行をスキップします。
3. **Python 実効変数確定** (`post-load-params-python-client.yml`): Python 言語版 Kubernetes client 導入用の実効変数 (`k8s_devel_python_prereq_packages_effective`, `k8s_devel_python_pip_executable_effective`) を確定します。
4. **前提パッケージ導入** (`install-prereqs.yml` - Python 部分): `k8s_devel_python_client_enabled=true` かつ `k8s_devel_python_client_install_via_pip=true` の場合のみ, Python 用 pip パッケージを導入します。
   - Debian: `python3-pip`
   - RHEL: `k8s_python_packages_version` 指定時は `python3.12-pip`, 未指定時は `python3-pip`
5. **Go実行パス既定値設定** (`install-go.yml`): `k8s_devel_go_packages_enabled=true` または `k8s_devel_go_client_enabled=true` の場合, `go_command` の既定値を `go_command_package` に設定します。
6. **Python 言語版 Kubernetes client 導入** (`install-python-client.yml`): `k8s_devel_python_client_enabled=true` の場合, Python 言語版 Kubernetes client を導入します。
   - **既定方式 (推奨)**: `python-k8s-client-local` ロールに委譲してローカルパッケージを導入します。導入先は `python_k8s_client_install_dir` (既定: `/opt/k8s-devel/python-client`) 配下の仮想環境です。
   - **互換方式 (legacy)**: `k8s_devel_python_client_install_via_pip=true` の場合のみ pip 導入を実施します。Ubuntu 24.04 以降では自動的に `--break-system-packages` を付与します。
7. **Go 言語版 Kubernetes client 導入** (`install-go-client.yml`): `k8s_devel_go_client_enabled=true` の場合, `go-k8s-client-local` ロールに委譲して Go 言語版 Kubernetes client を導入します。
   - 事前検証として `golang`/`golang-go`/`go-lang` パッケージの導入有無を確認し, 未導入の場合は設定誤りとして `fail` で停止します。
   - `go-k8s-client-local` ロールは, 構築ホスト上のコンテナでオフライン開発キット (`go.mod`, `go.sum`, `vendor/`) を含むローカルパッケージ (deb/rpm) を構築します。
   - 構築済みパッケージを「構築ホスト -> 制御ノード -> 対象ホスト」で転送し, `{{ k8s_devel_go_client_work_dir }}` (既定: `/opt/k8s-devel/go-client`) に導入します。
   - 導入後に `go.mod` の `k8s.io/client-go` 版数が `{{ k8s_devel_go_client_version }}` (実効値) と一致することを検証します。
8. **C client 導入** (`install-c-client.yml`): `k8s_devel_c_client_enabled=true` の場合でも処理失敗せず, 将来サポート予定として完了します。現在は「C Kubernetes client installation is deferred」メッセージを表示するのみです。

## 主要変数

### クライアント有効化設定

各言語の Kubernetes Client ライブラリの導入を制御する変数です。

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_devel_python_client_enabled` | `false` | Python 言語版 Kubernetes client を導入する場合は, `true`に設定します。 |
| `k8s_devel_go_client_enabled` | `false` | Go 言語版 Kubernetes client を導入する場合は, `true`に設定します。 |
| `k8s_devel_c_client_enabled` | `false` | C Kubernetes client を導入する場合は, `true`に設定します。将来サポート予定。 |
| `k8s_devel_go_packages_enabled` | `false` | Go 関連タスクを有効化する補助フラグです。Go自体の導入は本ロールでは実施しません。 |
| `k8s_devel_python_client_install_via_pip` | `false` | Python 言語版 Kubernetes client の導入方式切替フラグ。既定値 `false` では `python-k8s-client-local` ロールによるローカルパッケージ導入, `true` では legacy の pip 導入を行います。 |

### 版数指定

Python 言語版 Kubernetes client と Go 言語版 Kubernetes client の版数を指定する変数です。未指定時は `k8s_major_minor` から自動導出されます。

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_devel_python_client_version` | `""` | Python 言語版 Kubernetes client 版数。空文字列時は `k8s_major_minor` (例: `1.31`) から `~=<minor>.0` (例: `~=31.0`) を導出します。`~=` は互換バージョン指定 (PEP 440) で, 該当系列 (例: `31.0.0`, `31.1.0`, `31.2.3` など, ただし `32.0.0` 未満) の最新版を pip が自動選択します。 |
| `k8s_devel_go_client_version` | `""` | Go 言語版 Kubernetes client 版数。空文字列時は `k8s_major_minor` (例: `1.31`) から `v0.<minor>.0` (例: `v0.31.0`) を導出します。client-go は常にメジャー版数が `0` で, Kubernetes のマイナー版数がそのままマイナー版数になります。 |

**注記**: `k8s_major_minor` は `repo-deb` または `repo-rpm` ロールで定義される Kubernetes のメジャー.マイナー版数 (例: `1.31`) です。

### Go 言語版 Kubernetes client設定

Go 言語版 Kubernetes clientの版数とインストール方法を制御する変数です。

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_devel_go_client_work_dir` | `"/opt/k8s-devel/go-client"` | Go 言語版 Kubernetes client のオフライン開発キット導入先ディレクトリ。`go-k8s-client-local` ロールがローカルパッケージ経由で `go.mod`, `go.sum`, `vendor/` を配置します。 |
| `k8s_devel_go_module_domain` | `dns_domain` または `"example.org"` | Go モジュールドメイン。`go-k8s-client-local` ロールの構築処理内で `go mod init` に使用します。`dns_domain` が定義されている場合はその値を使用し, 未定義の場合は `"example.org"` を使用します。 |

`go_lang_version`, `go_lang_remove_existing_package` など Go 導入方式に関する変数は `go-lang-local` ロールで管理します。設定方法と既定値は `roles/go-lang-local/Readme.md` を参照ください。

### vars/cross-distro.yml 参照変数

本ロールは `load-params.yml` で `vars/cross-distro.yml` を読み込み, 以下の変数を参照します。

| 変数名 | 用途 | 主な参照タスク |
| --- | --- | --- |
| `k8s_devel_python_prereq_packages_cross_distro` | Python 前提パッケージ名 (OS差分吸収) | `post-load-params-python-client.yml` |
| `k8s_devel_python_pip_executable_cross_distro` | 開発用 Python 向け pip 実行ファイル (OS差分吸収) | `post-load-params-python-client.yml` |

### Python 環境設定 (OS 別参照変数)

Python 言語版 Kubernetes client 導入時に参照される OS 別の変数です。`vars/packages-ubuntu.yml`, `vars/packages-rhel.yml` で定義されます。

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_python_packages_version` | `"3.12"` | 開発用 Python バージョン。Ubuntu では標準 Python が該当バージョンのため参照のみ, RHEL では `python3.12`, `python3.12-pip` 等の版数指定パッケージ名に使用されます。 |

## テンプレート / ファイル

本ロールで生成, 配置, または更新される主なファイルは以下です。

| ファイル | 用途 |
| --- | --- |
| `{{ k8s_devel_go_client_work_dir }}/go.mod` | `go-k8s-client-local` ロールがローカルパッケージ導入で配置する Go モジュール定義ファイルです。 |
| `{{ k8s_devel_go_client_work_dir }}/go.sum` | `go-k8s-client-local` ロールがローカルパッケージ導入で配置する依存関係チェックサムファイルです。 |
| `{{ k8s_devel_go_client_work_dir }}/vendor/` | `go-k8s-client-local` ロールが配置する Go 言語版 Kubernetes client のオフライン依存キットです。 |
| `/opt/k8s-devel/python-client/venv/` | 既定方式 (`k8s_devel_python_client_install_via_pip=false`) で導入される Python 言語版 Kubernetes client 用仮想環境です。`python-k8s-client-local` ロールがローカルパッケージ導入で配置します。 |
| `kubernetes` Python パッケージ | pip導入モード (`k8s_devel_python_client_install_via_pip=true`) で導入される Python 言語版 Kubernetes client です。 |

## 実行方法

```bash
# make コマンドで実行 (全ホスト対象)
make run_k8s_devel

# コントロールプレーンノードに適用
ansible-playbook k8s-ctrl-plane.yml

# ワーカーノードに適用
ansible-playbook k8s-worker.yml

# 開発環境に適用
ansible-playbook devel.yml

# 特定ホストのみ対象
ansible-playbook k8s-ctrl-plane.yml -l k8sctrlplane01.local

# k8s-devel タスクのみ実行
ansible-playbook k8s-ctrl-plane.yml -t k8s-devel
```

## 設定例

```yaml
# Kubernetes Go 言語版 clientを導入する
k8s_devel_go_client_enabled: true
# Kubernetes Python 言語版 clientを導入する
k8s_devel_python_client_enabled: true
# Go 言語版 Kubernetes clientの版数としてv0.31.0を指定する
k8s_devel_go_client_version: "v0.31.0"
# Python 言語版 Kubernetes clientの版数指定(PEP 440)。例: ~=31.0, ==31.0.0
k8s_devel_python_client_version: "~=31.0"
```

## 設定内容の検証

本節では, `k8s-devel` ロール実行後にシステムが正しく設定されているかを確認する手順を示します。

### 前提条件

- `k8s-devel` ロールが正常に完了していること。
- リモートホストへ SSH で接続可能であること。
- sudo 権限が利用可能であること (一部コマンド用)。

### 1. Go 言語版 Kubernetes client 導入の確認

**実施ホスト**: `devserver.local`

**コマンド**:

```bash
ls -la /opt/k8s-devel/go-client
rpm -qa | egrep '^go-k8s-client' || dpkg -l | egrep '^ii\s+go-k8s-client'
cat /opt/k8s-devel/go-client/go.mod
cat /opt/k8s-devel/go-client/go.sum | head -10
```

**期待される出力**:

```plaintext
total 20
drwxr-xr-x 3 root root 4096  3月  5 10:20 .
drwxr-xr-x 3 root root 4096  3月  5 10:20 ..
-rw-r--r-- 1 root root  156  3月  5 10:20 go.mod
-rw-r--r-- 1 root root 6842  3月  5 10:20 go.sum
drwxr-xr-x 8 root root 4096  3月  5 10:20 vendor

go-k8s-client-0.31.0-1.el9.noarch

module example.org/k8s-devel-client-go

go 1.22

require k8s.io/client-go v0.31.0

github.com/davecgh/go-spew v1.1.1 h1:vj9j/u1bqnvCEfJOwUhtlOARqs3+rkHYY13jYWTU97c=
github.com/davecgh/go-spew v1.1.1/go.mod h1:J7Y8YcW2NihsgmVo/mv3lAwl/skON4iLHjSsI+c5H38=
github.com/emicklei/go-restful/v3 v3.11.0 h1:rAQnmNREppS9F9Q2gfUYfXBHhVZP4jY9w7V/fPz9S6Q=
github.com/emicklei/go-restful/v3 v3.11.0/go.mod h1:6n3XBCmQQb25CM2LCACGz8ukIrRry+4bhvbpWn3mrbc=
github.com/evanphx/json-patch v5.6.0+incompatible h1:jBYDEEiFBPxA0v50tFdvOzQQTCvpL6mnFh5mB2/l16U=
github.com/evanphx/json-patch v5.6.0+incompatible/go.mod h1:50XU6AFN0ol/bzJsmQLiYLvXMP4fmwYFNcr97nuDLSk=
github.com/fxamacker/cbor/v2 v2.7.0 h1:+0XTmHEIiKtcFgqTHW1eqmnKw6FrBfz0f0u+TmCAQBk=
github.com/fxamacker/cbor/v2 v2.7.0/go.mod h1:lhLxFQWdGBEe+qhyPFzKOMWCWFqfRAKMxV5YVqKU0Rg=
github.com/go-logr/logr v1.4.2 h1:6pFjapn5bLjiuzPgRSQ7hjBCqq9sFzaJK6e0/z8Pqfs=
github.com/go-logr/logr v1.4.2/go.mod h1:9T104GzyrTigFIr8wt5mBrctHMim0Nb2HLGrmQ40KvY=
```

**確認ポイント**:

- `/opt/k8s-devel/go-client` ディレクトリに `go.mod` と `go.sum` が存在
- `go-k8s-client` パッケージが導入済みである
- `/opt/k8s-devel/go-client/vendor` ディレクトリが存在する
- `go.mod` に `require k8s.io/client-go v0.31.0` (または指定版数) が記載されている
- `go.sum` に client-go の依存関係チェックサムが記録されている

### 2. Python 言語版 Kubernetes client 導入の確認 (既定: ローカルパッケージ方式)

**実施ホスト**: `devserver.local` (Ubuntu 24.04)

**コマンド**:

```bash
/opt/k8s-devel/python-client/venv/bin/python -c 'import kubernetes; print(kubernetes.__version__)'
/opt/k8s-devel/python-client/venv/bin/python -c 'import kubernetes; print(kubernetes.__file__)'
```

**期待される出力**:

```plaintext
31.0.0
/opt/k8s-devel/python-client/venv/lib/python*/site-packages/kubernetes/__init__.py
```

**確認ポイント**:

- `/opt/k8s-devel/python-client/venv` 配下の Python で kubernetes が import できる
- 版数が k8s_major_minor (例: 1.31) のマイナー版数 (31) と一致
- インストールパスが `/opt/k8s-devel/python-client/venv/` 配下

### 3. Python 言語版 Kubernetes client 導入の確認 (RHEL 9.6, 既定: ローカルパッケージ方式)

**実施ホスト**: `rhel-server.local` (RHEL 9.6)

**コマンド**:

```bash
/opt/k8s-devel/python-client/venv/bin/python -c 'import kubernetes; print(kubernetes.__version__)'
/opt/k8s-devel/python-client/venv/bin/python -c 'import kubernetes; print(kubernetes.__file__)'
```

**期待される出力**:

```plaintext
31.0.0
/opt/k8s-devel/python-client/venv/lib/python*/site-packages/kubernetes/__init__.py
```

**確認ポイント**:

- `/opt/k8s-devel/python-client/venv` 配下の Python で kubernetes が import できる
- 版数が期待値と一致
- インストールパスが `/opt/k8s-devel/python-client/venv/` 配下

### 4. Python 言語版 Kubernetes client 導入の確認 (互換: pip導入モード)

`k8s_devel_python_client_install_via_pip=true` を明示した場合は, 以下のように pip 実行ファイルを使って確認します。

**実施ホスト**: `devserver.local` (Ubuntu 24.04), `rhel-server.local` (RHEL 9.6)

**コマンド**:

```bash
pip3 list | grep kubernetes
python3 -c 'import kubernetes; print(kubernetes.__version__)'
python3 -c 'import kubernetes; print(kubernetes.__file__)'
```

RHEL で `k8s_python_packages_version` を指定している場合は, 必要に応じて `pip3.12` / `python3.12` でも確認します。

## トラブルシューティング

- `k8s_major_minor` 形式エラー時は, 本ロールは `package.yml` 実行をスキップします。`major.minor` 形式(例: `1.31`)に修正後, 再実行してください。
- Go ローカルパッケージ導入失敗時: ビルドホストから `https://go.dev/dl/` へのネットワーク接続と, `/tmp/go-build` 配下の成果物生成状況を確認してください。
- Go 言語版 Kubernetes client 導入で失敗する場合は, `golang`/`golang-go`/`go-lang` の導入有無に加え, 構築ホストでのコンテナ実行可否とローカルパッケージ生成状況を確認してください。
- Python 言語版 Kubernetes client 導入で失敗する場合は, 既定方式では `python-k8s-client-local` ロールのビルドホストでのローカルパッケージ生成状況を, pip導入モードでは pip 実行環境と外部リポジトリアクセス可否を確認してください。
- Ubuntu 24.04 で "externally-managed-environment" エラーが出る場合: pip導入モードでは本ロールが `--break-system-packages` を付与します。手動で導入する場合は `pip install --break-system-packages <package>` を使用してください。

## 参考リンク

- [Python 言語版 Kubernetes client](https://github.com/kubernetes-client/python)
- [client-go](https://github.com/kubernetes/client-go)
- [PEP 668 – Marking Python base environments as "externally managed"](https://peps.python.org/pep-0668/)
