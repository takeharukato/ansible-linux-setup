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

主な機能:

- **Python client の二段階導入**: 標準 Python (例: python3) と開発用 Python (例: python3.12, RHEL のみ) の両方に Kubernetes client を導入します。これにより, OS 標準の Python 環境と開発用の新しい Python 環境の両方で Kubernetes API を利用できます。
- **Go 版数の柔軟な指定**: Go 言語の版数を `x.y` 形式 (例: `1.22`) で指定すると該当系列の最新パッチ版を自動検出し, `x.y.z` 形式 (例: `1.22.10`) で指定すると正確な版数を取得します。Go 公式 API (`https://go.dev/dl/?mode=json&include=all`) から版数情報を取得し, End-of-Life (EOL) 系列にも対応します。
- **PEP 668 対応**: Ubuntu 24.04 以降では PEP 668 (外部管理環境) により, システム Python への直接インストールが制限されています。本ロールでは自動的に `--break-system-packages` オプションを付与してインストールします。
- **OS 別の差異を吸収**: Ubuntu と RHEL の Python 環境の違い (Python 版数, pip コマンド名, インストールパス) を自動的に吸収し, 統一的なインターフェースで導入できます。

## 前提条件

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- `repo-deb` または `repo-rpm` が先に適用され, `k8s_major_minor` が定義されていることを前提とします。
- `go_lang_version` を指定する場合, Ansible 実行ホスト (localhost) から Go 公式サイト (`https://go.dev/dl/`) へのネットワークアクセスが必須です。
- Ubuntu 24.04 以降では PEP 668 (外部管理環境) により, システム Python への直接インストールが制限されています。本ロールでは自動的に `--break-system-packages` オプションを付与してインストールします。

## 実行フロー

本ロールは以下の順序で処理を実行します:

1. **パラメータ読み込み** (`load-params.yml`): OS 別パッケージ定義 (`vars/packages-ubuntu.yml`, `vars/packages-rhel.yml`) と共通変数 (`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込みます。
2. **版数導出** (`post-load-params.yml`): `k8s_major_minor` (例: `1.31`) から Python client と Go client の既定版数を導出します。
   - Python client: `~=<minor>.0` (例: `~=31.0`) 形式で互換バージョン指定 (PEP 440) を生成します。pip が該当系列の最新版を自動選択します。
   - Go client: `v0.<minor>.0` (例: `v0.31.0`) 形式で版数を生成します。client-go は常にメジャー版数が `0` で, Kubernetes のマイナー版数がそのままマイナー版数になります。
   - `k8s_major_minor` の形式検証 (`^[0-9]+\.[0-9]+$`) を実施します。
3. **Python 実効変数確定** (`post-load-params-python-client.yml`): Python client 導入用の実効変数 (`k8s_devel_python_prereq_packages_effective`, `k8s_devel_python_pip_executable_effective`) を確定します。
4. **前提パッケージ導入** (`install-prereqs.yml` - Python 部分): `k8s_devel_python_client_enabled=true` の場合, Python 用 pip パッケージを導入します。
   - Debian: `python3-pip`
   - RHEL: `k8s_python_packages_version` 指定時は `python3.12-pip`, 未指定時は `python3-pip`
5. **Go 基盤導入** (`install-prereqs.yml` - Go 部分): `k8s_devel_go_packages_enabled=true` の場合, Go 言語をインストールします。
   - **`go_lang_version` 未指定時**: OS 提供パッケージの最新版 (`latest`) をパッケージマネージャ (apt/dnf) 経由で導入します。Go コマンドパスは `/usr/bin/go` になります。
   - **`go_lang_version` 指定時**: Go 公式 API (`https://go.dev/dl/?mode=json&include=all`) からバージョン情報を取得し, 以下の手順でインストールします:
     - **`x.y` 形式の場合** (例: `1.22`): 該当系列 (1.22.x) の最新パッチ版を自動検出します (例: `1.22.10`)。EOL 系列の場合は `go_series_fallback_versions` で定義されたフォールバック版数を使用します。
     - **`x.y.z` 形式の場合** (例: `1.22.10`): 指定されたバージョンを正確に取得します。
     - Go の tarball を Go 公式サイト (`https://go.dev/dl/go<version>.linux-<arch>.tar.gz`) からダウンロードし, `/usr/local/go` に展開します。
     - `/etc/profile.d/golang.sh` で PATH を設定します (`export PATH=/usr/local/go/bin:$PATH`)。
     - Go コマンドパスは `/usr/local/go/bin/go` になります。
     - `go_lang_remove_existing_package=true` (既定値) の場合, 既存の Go パッケージを削除してから tarball をインストールします。
6. **Python client 導入** (`install-python-client.yml`): `k8s_devel_python_client_enabled=true` の場合, Python Kubernetes client を導入します。
   - **標準 Python への導入**: `pip3` を使用して `kubernetes<python_client_version>` を導入します (`<python_client_version>` は `k8s_devel_python_client_version` の値, または既定値を使用)。
     - Ubuntu 24.04 以降: PEP 668 対応のため, 自動的に `--break-system-packages` オプションを付与します。
     - RHEL 9.6: 標準 Python 3.9 に導入します。
   - **開発用 Python への導入**: `k8s_python_packages_version` が定義されている場合, 該当バージョンの `pip` を使用して追加導入します。
     - Ubuntu: 標準 Python が該当バージョンのため実質的に冪等性により重複インストールとなります。
     - RHEL: 開発用 Python (例: python3.12) にも導入します。
7. **Go client 導入** (`install-go-client.yml`): `k8s_devel_go_client_enabled=true` の場合, Go Kubernetes client を導入します。
   - `{{ k8s_devel_go_work_dir }}` (既定: `/opt/k8s-devel/go-client`) ディレクトリを作成します。
   - `go mod init {{ k8s_devel_go_module_domain }}/k8s-devel-client-go` を実行します。
   - `go get k8s.io/client-go@{{ k8s_devel_go_client_version }}` で client-go を導入します (`{{ k8s_devel_go_client_version }}` は変数の値, または既定値を使用)。
   - `go.mod`, `go.sum` が生成されます。実際のライブラリは Go モジュールキャッシュに配置されます。
8. **C client 導入** (`install-c-client.yml`): `k8s_devel_c_client_enabled=true` の場合でも処理失敗せず, 将来サポート予定として完了します。現在は「C Kubernetes client installation is deferred」メッセージを表示するのみです。

## 主要変数

### クライアント有効化設定

各言語の Kubernetes Client ライブラリの導入を制御する変数です。

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_devel_python_client_enabled` | `false` | Python Kubernetes client を導入する場合は, `true`に設定します。 |
| `k8s_devel_go_client_enabled` | `false` | Go Kubernetes client を導入する場合は, `true`に設定します。 |
| `k8s_devel_c_client_enabled` | `false` | C Kubernetes client を導入する場合は, `true`に設定します。将来サポート予定。 |
| `k8s_devel_go_packages_enabled` | `false` | Go 最小ツールチェーンを導入する場合は, `true`に設定します。 |

### 版数指定

Python client と Go client の版数を指定する変数です。未指定時は `k8s_major_minor` から自動導出されます。

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_devel_python_client_version` | `""` | Python client 版数。空文字列時は `k8s_major_minor` (例: `1.31`) から `~=<minor>.0` (例: `~=31.0`) を導出します。`~=` は互換バージョン指定 (PEP 440) で, 該当系列 (例: `31.0.0`, `31.1.0`, `31.2.3` など, ただし `32.0.0` 未満) の最新版を pip が自動選択します。 |
| `k8s_devel_go_client_version` | `""` | Go client 版数。空文字列時は `k8s_major_minor` (例: `1.31`) から `v0.<minor>.0` (例: `v0.31.0`) を導出します。client-go は常にメジャー版数が `0` で, Kubernetes のマイナー版数がそのままマイナー版数になります。 |

**注記**: `k8s_major_minor` は `repo-deb` または `repo-rpm` ロールで定義される Kubernetes のメジャー.マイナー版数 (例: `1.31`) です。

### Go 言語環境設定

Go 言語の版数とインストール方法を制御する変数です。

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `go_lang_version` | `""` | Go 言語版数。空文字列の場合は OS 提供パッケージを `latest` で導入します。`x.y` 形式 (例: `1.18`) を指定すると該当系列の最新版 (例: `1.18.10`) を Go 公式から自動取得します。`x.y.z` 形式 (例: `1.18.5`) を指定するとその正確なバージョンを取得します。指定バージョンが Go 公式に存在しない場合は警告メッセージを表示してスキップします。 |
| `go_lang_remove_existing_package` | `true` | `go_lang_version` 指定時に既存の Go パッケージを削除するか制御します。`true` の場合は既存パッケージを削除してから tarball をインストールし, `false` の場合は既存パッケージを残したまま tarball をインストールします (PATH の優先順位に注意が必要です)。 |
| `k8s_devel_go_work_dir` | `"/opt/k8s-devel/go-client"` | Go client 導入用作業ディレクトリ。`go mod init` と `go get` を実行し, `go.mod`, `go.sum` を配置するディレクトリです。実際の client-go ライブラリは Go のモジュールキャッシュにダウンロードされます。 |
| `k8s_devel_go_module_domain` | `dns_domain` または `"example.org"` | Go モジュールドメイン (`go mod init` 用)。`dns_domain` が定義されている場合はその値を使用し, 未定義の場合は `"example.org"` を使用します。 |

### Python 環境設定 (OS 別参照変数)

Python client 導入時に参照される OS 別の変数です。`vars/packages-ubuntu.yml`, `vars/packages-rhel.yml` で定義されます。

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_python_packages_version` | `"3.12"` | 開発用 Python バージョン。Ubuntu では標準 Python が該当バージョンのため参照のみ, RHEL では `python3.12`, `python3.12-pip` 等の版数指定パッケージ名に使用されます。 |

## テンプレート / ファイル

本ロールで生成, 配置, または更新される主なファイルは以下です。

| ファイル | 用途 |
| --- | --- |
| `/usr/bin/go` | `go_lang_version` 未指定で Go をパッケージマネージャ導入した場合の Go コマンドです。 |
| `/usr/local/go/bin/go` | `go_lang_version` 指定時に Go tarball から導入される Go コマンドです。 |
| `/etc/profile.d/golang.sh` | `go_lang_version` 指定時に作成される PATH 設定スクリプトです。 |
| `{{ k8s_devel_go_work_dir }}/go.mod` | `go mod init` 実行時に生成される Go モジュール定義ファイルです。 |
| `{{ k8s_devel_go_work_dir }}/go.sum` | `go get` 実行時に生成または更新される依存関係チェックサムファイルです。 |
| `/tmp/go<version>.linux-<arch>.tar.gz` | `go_lang_version` 指定時に localhost へ一時保存される tarball です。展開後に削除されます。 |
| `kubernetes` Python パッケージ | Python client 導入時に pip で導入されます。導入先は Ubuntu 24.04 では通常 `/usr/local/lib/python3.12/dist-packages/kubernetes/`, RHEL 9.6 では通常 `/usr/local/lib/python3.9/site-packages/kubernetes/` です。 |

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
# Go 言語を導入する
k8s_devel_go_packages_enabled: true
# Go言語の版数を 1.18.10 に指定する
go_lang_version: "1.18.10"
# Kubernetes Go Clientを導入する
k8s_devel_go_client_enabled: true
# Kubernetes Python Clientを導入する
k8s_devel_python_client_enabled: true
# Go Clientの版数としてv0.31.0を指定する
k8s_devel_go_client_version: "v0.31.0"
# Python Clientの版数として31.0.0を指定する
k8s_devel_python_client_version: "31.0.0"
```

## 設定内容の検証

本節では, `k8s-devel` ロール実行後にシステムが正しく設定されているかを確認する手順を示します。

### 前提条件

- `k8s-devel` ロールが正常に完了していること。
- リモートホストへ SSH で接続可能であること。
- sudo 権限が利用可能であること (一部コマンド用)。

### 1. Go 基盤 (パッケージマネージャ導入) の確認

**実施ホスト**: `devserver.local`

**コマンド**:

```bash
which go
go version
dpkg -l | grep golang  # Ubuntu
# または
rpm -qa | grep golang   # RHEL
```

**期待される出力** (Ubuntu例):

```plaintext
/usr/bin/go
go version go1.21.12 linux/amd64
ii  golang-1.21                  1.21.12-1ubuntu1         amd64        Go programming language compiler
ii  golang-1.21-go               1.21.12-1ubuntu1         amd64        Go programming language compiler
ii  golang-1.21-src              1.21.12-1ubuntu1         all          Go programming language - source files
```

**確認ポイント**:

- `which go` が `/usr/bin/go` を返す
- `go version` で版数が表示される
- パッケージマネージャで golang パッケージが導入されている

### 2. Go 基盤 (tarball 導入) の確認

**実施ホスト**: `devserver.local`

**コマンド**:

```bash
which go
go version
ls -la /usr/local/go
cat /etc/profile.d/golang.sh
```

**期待される出力**:

```plaintext
/usr/local/go/bin/go
go version go1.22.10 linux/amd64
total 236
drwxr-xr-x  10 root root  4096  3月  5 10:15 .
drwxr-xr-x  13 root root  4096  3月  5 10:15 ..
drwxr-xr-x   2 root root 49152  3月  5 10:15 bin
-rw-r--r--   1 root root 52600  1月  8 05:46 CONTRIBUTING.md
drwxr-xr-x   8 root root  4096  3月  5 10:15 lib
-rw-r--r--   1 root root  1339  1月  8 05:46 LICENSE
drwxr-xr-x  15 root root  4096  3月  5 10:15 pkg
-rw-r--r--   1 root root  1455  1月  8 05:46 README.md
-rw-r--r--   1 root root   425  1月  8 05:46 SECURITY.md
drwxr-xr-x  47 root root  4096  3月  5 10:15 src
-rw-r--r--   1 root root     8  1月  8 05:46 VERSION

export PATH=/usr/local/go/bin:$PATH
```

**確認ポイント**:

- `which go` が `/usr/local/go/bin/go` を返す
- `go version` で指定した版数が表示される
- `/usr/local/go` ディレクトリに bin, pkg, src が存在
- `/etc/profile.d/golang.sh` で PATH が設定されている

### 3. Go client 導入の確認

**実施ホスト**: `devserver.local`

**コマンド**:

```bash
ls -la /opt/k8s-devel/go-client
cat /opt/k8s-devel/go-client/go.mod
cat /opt/k8s-devel/go-client/go.sum | head -10
```

**期待される出力**:

```plaintext
total 20
drwxr-xr-x 2 root root 4096  3月  5 10:20 .
drwxr-xr-x 3 root root 4096  3月  5 10:20 ..
-rw-r--r-- 1 root root  156  3月  5 10:20 go.mod
-rw-r--r-- 1 root root 6842  3月  5 10:20 go.sum

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
- `go.mod` に `require k8s.io/client-go v0.31.0` (または指定版数) が記載されている
- `go.sum` に client-go の依存関係チェックサムが記録されている

### 4. Python client 導入の確認 (Ubuntu 24.04)

**実施ホスト**: `devserver.local` (Ubuntu 24.04)

**コマンド**:

```bash
pip3 list | grep kubernetes
python3 -c 'import kubernetes; print(kubernetes.__version__)'
python3 -c 'import kubernetes; print(kubernetes.__file__)'
```

**期待される出力**:

```plaintext
kubernetes                31.0.0
31.0.0
/usr/local/lib/python3.12/dist-packages/kubernetes/__init__.py
```

**確認ポイント**:

- `pip3 list` で kubernetes パッケージが表示される
- 版数が k8s_major_minor (例: 1.31) のマイナー版数 (31) と一致
- インストールパスが `/usr/local/lib/python3.12/dist-packages/` 配下

### 5. Python client 導入の確認 (RHEL 9.6 - 標準 Python)

**実施ホスト**: `rhel-server.local` (RHEL 9.6)

**コマンド**:

```bash
pip3 list | grep kubernetes
python3 -c 'import kubernetes; print(kubernetes.__version__)'
python3 -c 'import kubernetes; print(kubernetes.__file__)'
```

**期待される出力**:

```plaintext
kubernetes                31.0.0
31.0.0
/usr/local/lib/python3.9/site-packages/kubernetes/__init__.py
```

**確認ポイント**:

- 標準 Python (python3.9) で kubernetes パッケージが導入されている
- 版数が期待値と一致
- インストールパスが `/usr/local/lib/python3.9/site-packages/` 配下

### 6. Python client 導入の確認 (RHEL 9.6 - 開発用 Python)

**実施ホスト**: `rhel-server.local` (RHEL 9.6)

**コマンド**:

```bash
pip3.12 list | grep kubernetes
python3.12 -c 'import kubernetes; print(kubernetes.__version__)'
python3.12 -c 'import kubernetes; print(kubernetes.__file__)'
```

**期待される出力**:

```plaintext
kubernetes                31.0.0
31.0.0
/usr/local/lib/python3.12/site-packages/kubernetes/__init__.py
```

**確認ポイント**:

- 開発用 Python (python3.12) で kubernetes パッケージが導入されている
- 標準 Python と開発用 Python の両方に同一版数が導入されている
- インストールパスが `/usr/local/lib/python3.12/site-packages/` 配下

## トラブルシューティング

- `k8s_major_minor` 形式エラー時は `major.minor` 形式(例: `1.31`)に修正してください。
- Go tarball インストール失敗時: Ansible 実行ホストから `https://go.dev/dl/` へのネットワーク接続を確認してください。
- "version not found" エラーが出た場合: `go_lang_version` を `x.y.z` 形式から `x.y` 形式に変更し, 最新版の自動検出を試してください。
- Go client 導入で失敗する場合は, `golang` の導入有無とネットワーク疎通を確認してください。
- Python client 導入で失敗する場合は, pip 実行環境と外部リポジトリアクセス可否を確認してください。
- Ubuntu 24.04 で "externally-managed-environment" エラーが出る場合: 本ロールでは自動的に `--break-system-packages` を付与しますが, 手動でインストールする場合は `pip install --break-system-packages <package>` を使用してください。

## 参考リンク

- [Kubernetes Python client](https://github.com/kubernetes-client/python)
- [client-go](https://github.com/kubernetes/client-go)
- [PEP 668 – Marking Python base environments as "externally managed"](https://peps.python.org/pep-0668/)
