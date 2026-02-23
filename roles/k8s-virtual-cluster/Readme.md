# k8s-virtual-cluster ロール

Kubernetes Virtual Cluster の基盤コンポーネントをデプロイするロールです。このロールは, Kubernetes API を仮想化し, 複数の論理的な Kubernetes クラスタを単一の物理 Kubernetes クラスタ上で動作させるための基盤を構築します。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウエア。 |
| Application Programming Interface | API | 他の仕組みから機能を呼び出すための窓口。 |
| CustomResourceDefinition | CRD | Kubernetes に独自のリソース型を追加する仕組み。 |
| Role Based Access Control | RBAC | 権限を役割単位で制御する仕組み。 |
| Transport Layer Security | TLS | 通信を暗号化する仕組み。 |
| Domain Name System | DNS | 名前と IP アドレスを対応付ける仕組み。 |
| etcd | etcd | Kubernetes の設定情報と状態を保存する分散キーバリューストア。 |
| kube-apiserver | kube-apiserver | Kubernetes API サーバー, API リクエストを受け付けて処理するコンポーネント。 |
| kube-controller-manager | kube-controller-manager | Kubernetes コントローラーマネージャー, リソースの状態を監視して制御するコンポーネント。 |
| Virtual Cluster | - | Kubernetes APIを仮想化して提供する論理的なKubernetesクラスタ。 |
| Super Cluster | - | Virtual Clusterを動作させるホスト側の物理Kubernetesクラスタ。 |
| vc-manager (Virtual Cluster Manager) | vc-manager | Virtual Clusterの制御コンポーネント。Super Cluster上でVirtual Clusterの管理を行う。 |
| Syncer | syncer | Virtual ClusterとSuper Clusterの状態を同期するコンポーネント。 |
| Virtual Node Agent | vn-agent | ワーカーノード上でVirtual Clusterの通信を中継するエージェント。 |
| Debian Bookworm Slim | debian:bookworm-slim | Dockerイメージ作成時に使用するDebian 12 (Bookworm)の軽量ベースイメージ。 |

## 前提条件

- Kubernetes クラスタが稼働していること。目安は v1.22 以上です。
- `kubectl` コマンドが利用可能であること。
- `k8s-common` と `k8s-ctrlplane` ロールが事前に実行済みであること。
- Virtual Cluster のコンポーネントは実験環境向けの実装です。
- ビルドノード(デフォルトはAnsibleの制御ノード(localhost), `virtualcluster_build_host`で変更可能)に以下がインストールされていること:
  - Go (バージョン 1.16以上推奨)
  - Make
  - Docker
- コントロールプレーンからワーカーノードへSSH接続可能であること。
- ワーカーノードが containerd を使用していること。
- `virtualcluster_auto_detect_supercluster_images: true` (既定値)の場合, Ansible制御ノードから `kubectl` でスーパークラスタに疎通可能であること。

## 概要

Virtual Cluster により, ホスト Kubernetes クラスタ(以下, Super Cluster)上で複数のテナント向けコントロールプレインを独立して運用できます。各テナントコントロールプレインは Super Cluster のワーカーノードを共有しながら, API レベルの分離を実現します。

## 実行フロー

1. `validate.yml` で前提条件と API 疎通を検証します。
2. `detect-supercluster-images.yml` でスーパークラスタから稼働中のetcd, kube-apiserver, kube-controller-managerのイメージを自動検出します（デフォルト, `virtualcluster_auto_detect_supercluster_images: true` の場合）。
3. `namespace.yml` で `vc-manager` の namespace を作成します。
4. `crd.yml` で ClusterVersion と VirtualCluster の CRD を登録します。
5. `virtualcluster_build_from_source: true` の場合:
   - `download-source.yml` でソースリポジトリをクローン/更新します。
   - `build-binaries.yml` で `make build-images` を実行してバイナリをビルドします。
   - `build-docker-images.yml` でDockerイメージをビルドしてtarファイルに保存します。
   - `fetch-images.yml` でビルドノードからAnsibleの制御ノード(localhost)へtarファイルを取得します。
6. `upload-to-ctrlplane.yml` でコントロールプレーンへイメージをアップロードします。
7. `distribute-to-workers.yml` でコントロールプレーンからワーカーノードへイメージを配布します:
   - `kubectl get nodes` で実際のワーカーノードリストを取得します。
   - SSH経由で各ワーカーノードにイメージを転送します。
   - 各ワーカーで `ctr -n k8s.io images import` を実行します。
7. `deploy-manager.yml` で vc-manager, syncer, vn-agent をデプロイします。
8. `verify.yml` で CRD と Pod 起動を確認します。

## コンテナイメージ作成と配布の流れ

以下の`<component>`には`virtualcluster_build_components`の各要素を指し, 既定では`manager`, `syncer`, `vn-agent`が入ります。

- `virtualcluster_source_repo`を`virtualcluster_build_host`上の`virtualcluster_source_dir`へクローンまたは更新します。
- `make build-images`でバイナリを生成します。
- 生成したバイナリから, `debian:bookworm-slim`をベースにDockerイメージを作成し, `virtualcluster/<component>-amd64:latest`でタグ付けします。
- ビルドノード上で`docker save`により`/tmp/vc_<component>-amd64.tar`を作成します。
- `fetch-images.yml`でビルドノードからAnsibleの制御ノード(localhost)へtarファイルを転送します。
- `upload-to-ctrlplane.yml`でAnsibleの制御ノード(localhost)からコントロールプレーンへtarファイルを転送します。
- `distribute-to-workers.yml`でコントロールプレーン上の配布スクリプトを実行し, `virtualcluster_supercluster_kubeconfig_path`でK8sクラスタ(スーパークラスタ)のノード一覧を取得します。
- コントロールプレーンから各ワーカーノードへ`scp`でtarファイルを転送し, 各ワーカーで`ctr -n k8s.io images import`によりイメージを取り込みます。

### ソース取得からコンテナイメージ作成配布処理中での排他制御について

複数の`k8s_management`ホストが存在する場合でも, 以下は`run_once: true`で1回のみ実行されます。

- ソース取得: `download-source.yml`。
- バイナリ作成: `build-binaries.yml`。
- Dockerイメージ作成とtar出力: `build-docker-images.yml`。
- Ansibleの制御ノード(localhost)への取得とクリーンアップ: `fetch-images.yml`。
- コントロールプレーンへの転送: `upload-to-ctrlplane.yml`。
- ワーカーノードへの配布とクリーンアップ: `distribute-to-workers.yml`。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `virtualcluster_enabled` | `false` | ロールを実行するかどうかを指定します。 |
| `virtualcluster_build_from_source` | `true` | ソースからビルドするか(true), 既存バイナリ/イメージを使用するか(false)を指定します。 |
| `virtualcluster_auto_detect_supercluster_images` | `true` | スーパークラスタから稼働中のetcd, kube-apiserver, kube-controller-managerイメージを動的に検出するかどうか。既定: true。falseの場合は`registry.k8s.io/etcd:<すーぱクラスタのETCDメジャーバージョン.マイナーバージョン>.0`等のフォールバック値を使用します。運用環境では自動検出により, バージョンズレを防止できます。 |
| `virtualcluster_build_host` | `"localhost"` | ビルドを実行するホストを指定します (既定: Ansibleの制御ノード)。Docker/Go/Makeがインストール済みである必要があります。 |
| `virtualcluster_source_repo` | `"https://github.com/kubernetes-retired/cluster-api-provider-nested"` | Virtual Cluster のソースリポジトリURLです。 |
| `virtualcluster_source_version` | `"main"` | クローンするバージョン/ブランチ/タグです。 |
| `virtualcluster_source_dir` | `"/tmp/cluster-api-provider-nested"` | ソースのダウンロード先ディレクトリです (既定: `/tmp/cluster-api-provider-nested`)。 |
| `virtualcluster_build_components` | `['manager', 'syncer', 'vn-agent']` | ビルド対象コンポーネントのリストです。 |
| `virtualcluster_build_timeout` | `1800` | ビルドタイムアウト(秒)です。 |
| `virtualcluster_local_cache_dir` | `"{{ lookup('env', 'HOME') }}/.ansible/vc-images-cache"` | Ansibleの制御ノード(localhost)上のイメージキャッシュディレクトリです (既定: `~/.ansible/vc-images-cache`)。 |
| `virtualcluster_ctrlplane_cache_dir` | `"/tmp/vc-images"` | コントロールプレーン上のイメージキャッシュディレクトリです (既定: `/tmp/vc-images`)。 |
| `virtualcluster_ssh_keyscan_enabled` | `true` | SSH接続時にknown_hostsへ事前登録するか(true), StrictHostKeyChecking=noで回避するか(false)を指定します。 |
| `virtualcluster_ssh_user` | `"{{ ansible_user }}"` | コントロールプレーンからワーカーへのSSH接続ユーザーです。 (規定: `"ansible"`)|
| `virtualcluster_namespace` | `"vc-manager"` | Virtual Cluster 管理コンポーネントを展開する namespace です。 |
| `virtualcluster_config_dir` | `"{{ k8s_kubeadm_config_store }}/virtual-cluster"` | マニフェストの出力先です (既定: `~/kubeadm/virtual-cluster`)。 |
| `virtualcluster_supercluster_kubeconfig_path` | `"/etc/kubernetes/admin.conf"` | K8sクラスタ(スーパークラスタ)操作に使用するkubeconfigのパスです。 |
| `virtualcluster_manager_image` | `"virtualcluster/manager-amd64:latest"` | vc-manager のイメージです。 |
| `virtualcluster_syncer_image` | `"virtualcluster/syncer-amd64:latest"` | syncer のイメージです。 |
| `virtualcluster_vn_agent_image` | `"virtualcluster/vn-agent-amd64:latest"` | vn-agent のイメージです。 |
| `virtualcluster_pod_resource_requests.cpu` | `"500m"` | vc-manager の CPU リクエストです。 |
| `virtualcluster_pod_resource_requests.memory` | `"512Mi"` | vc-manager のメモリリクエストです。 |
| `virtualcluster_pod_resource_limits.cpu` | `"1000m"` | vc-manager の CPU リミットです。 |
| `virtualcluster_pod_resource_limits.memory` | `"1Gi"` | vc-manager のメモリリミットです。 |
| `k8s_api_wait_host` | `"{{ k8s_ctrlplane_endpoint }}"` | API サーバの待ち受け先です。 |
| `k8s_api_wait_port` | `"{{ k8s_ctrlplane_port }}"` | API サーバの待ち受けポートです。  (規定: `6443`)|

## 設定例

```yaml
# host_vars/k8sctrlplane01.local
virtualcluster_enabled: true

# ソースからビルドする場合
virtualcluster_build_from_source: true
virtualcluster_build_host: "localhost"  # Ansibleの制御ノード(localhost)またはリモートビルドサーバー

# 既存イメージを使用する場合
# virtualcluster_build_from_source: false

virtualcluster_pod_resource_requests:
  cpu: "1000m"
  memory: "1Gi"
virtualcluster_pod_resource_limits:
  cpu: "2000m"
  memory: "2Gi"
```

## 実行方法

```bash
make run_k8s_virtual_cluster
```

または,

```bash
# k8s-management.yml を実行
ansible-playbook k8s-management.yml

# 特定ホストのみ対象
ansible-playbook k8s-management.yml -l k8sctrlplane01.local

# Virtual Cluster タスクのみ実行
ansible-playbook k8s-management.yml -t k8s-virtual-cluster
```

## 主な処理

- ソースリポジトリからのクローンとビルド(オプション, `virtualcluster_build_from_source: true` の場合)。
- ビルドノードでDockerイメージをビルドしてtarファイルに保存。
- ビルドノード  =>  Ansibleの制御ノード(localhost)  =>  コントロールプレーンへの転送。
- コントロールプレーンで `kubectl get nodes` から実際のワーカーノードリストを取得。
- SSH経由で各ワーカーノードへイメージを配布し, `ctr -n k8s.io` で取り込み。
- CRD の生成と登録を行います。
- vc-manager, syncer, vn-agent のマニフェストを生成して apply します。
- vc-manager の webhook 用証明書をコンテナ内で生成できるように, `/tmp/k8s-webhook-server` を書き込み可能な `emptyDir` で提供します。
- vc-manager の RBAC に `admissionregistration.k8s.io` と `coordination.k8s.io` の権限を付与します。
- vn-agent はコントロールプレインノードを除外します。

## テンプレートと生成ファイル

以下の表中の~(チルダ記号)は, ansibleアカウントでログイン時のホームディレクトリ(規定: `/home/ansible`)を意味します。

| テンプレート | 出力先 | 説明 |
| --- | --- | --- |
| `templates/namespace.yaml.j2` | `{{ virtualcluster_config_dir }}/namespace.yaml` (既定: `~/kubeadm/virtual-cluster/namespace.yaml`) | namespace 定義です。 |
| `templates/clusterversion-crd.yaml.j2` | `{{ virtualcluster_config_dir }}/clusterversion-crd.yaml` (既定: `~/kubeadm/virtual-cluster/clusterversion-crd.yaml`) | ClusterVersion CRD です。 |
| `templates/virtualcluster-crd.yaml.j2` | `{{ virtualcluster_config_dir }}/virtualcluster-crd.yaml` (既定: `~/kubeadm/virtual-cluster/virtualcluster-crd.yaml`) | VirtualCluster CRD です。 |
| `templates/all-in-one.yaml.j2` | `{{ virtualcluster_config_dir }}/all-in-one.yaml` (既定: `~/kubeadm/virtual-cluster/all-in-one.yaml`) | vc-manager, syncer, vn-agent のマニフェストです。 |
| `templates/distribute-images.sh.j2` | `{{ virtualcluster_ctrlplane_cache_dir }}/distribute-images.sh` (既定: `/tmp/vc-images/distribute-images.sh`) | ワーカーノードへのイメージ配布スクリプトです(一時ファイル)。 |

## 生成されるリソース

| リソース | 説明 |
| --- | --- |
| `Namespace: vc-manager` | 管理コンポーネント用 namespace です。 |
| `CustomResourceDefinition` | `virtualclusters.tenancy.x-k8s.io` を登録します。 |
| `CustomResourceDefinition` | `clusterversions.tenancy.x-k8s.io` を登録します。 |
| `Deployment: vc-manager` | Virtual Cluster の管理コンポーネントです。 |
| `DaemonSet: vn-agent` | ワーカーノードの kubelet API プロキシです。 |

## 検証ポイント

以下の順で確認してください。

1. namespace の確認
   - 目的: `vc-manager` が作成されていることを確認します。
   - コマンド:
     ```bash
     kubectl get namespace vc-manager
     ```

2. CRD の確認
   - 目的: VirtualCluster と ClusterVersion の CRD が登録済みであることを確認します。
   - コマンド:
     ```bash
     kubectl get crd | grep virtualcluster
     kubectl get crd | grep clusterversion
     ```

3. Pod の確認
   - 目的: vc-manager と vn-agent の Pod が Running であることを確認します。
   - コマンド:
     ```bash
     kubectl -n vc-manager get pods -o wide
     ```

4. DaemonSet の配置確認
   - 目的: vn-agent がワーカーノードのみに配置されていることを確認します。
   - コマンド:
     ```bash
     kubectl -n vc-manager get pods -l app=vn-agent -o wide
     ```

5. イベントの確認
   - 目的: 直近のエラーが残っていないことを確認します。
   - コマンド:
     ```bash
     kubectl -n vc-manager get events --sort-by='.lastTimestamp' | tail -20
     ```

## トラブルシューティング

### ビルドが失敗する場合

```bash
# ビルドノードでGo/Docker/Makeが利用可能か確認
ssh {{ virtualcluster_build_host }} "go version && docker version && make --version"

# ビルドログを確認
# Ansibleのタスク実行ログから build-binaries.yml のstdoutを確認
```

### vc-manager が起動しない場合

```bash
kubectl -n vc-manager logs deployment/vc-manager
kubectl -n vc-manager describe pod -l app=vc-manager
```

### CRD 登録が失敗する場合

```bash
kubectl get crd virtualclusters.tenancy.x-k8s.io -o yaml
kubectl logs -n kube-system -l component=kube-apiserver --tail=50
```

### イメージ配布に失敗する場合

#### SSH接続の確認

本ロールでは, コントロールプレインからワーカーノードへsshによるパスワードレスログインが可能であることを前提としています。
以下のように, ansibleユーザで, コントロールプレインからワーカーノードへパスワードレスログインが可能であることを確認してください:

```bash
# コントロールプレーンからワーカーへのSSH接続を確認
ssh -o ConnectTimeout=5 <ansibleユーザ名>@<worker-node-name> hostname
```

#### コンテナイメージの確認

本ロールでは, virtual clusterを構成するために必要なコンテナイメージをワーカーノード上に配布し, containerdにコンテナイメージを登録します。

各ワーカーノード上で, コンテナイメージが登録されていることを以下のコマンドにより確認してください。

```bash
# ワーカーノードでイメージを確認
sudo ctr -n k8s.io images ls | grep virtualcluster
```

実行例を以下に示します:

```bash
$ sudo ctr -n k8s.io images ls | grep virtualcluster
docker.io/virtualcluster/manager-amd64:latest                                                                    application/vnd.oci.image.index.v1+json                   sha256:2e8dc650dc067fcc7f2d6444511b4473c58357d1f4e6c57630839a89274b0d51 37.1 MiB  linux/amd64                                                                  io.cri-containerd.image=managed
docker.io/virtualcluster/manager-amd64@sha256:3dd6190a87b41592d897862f47b3c0318c338e15978f25bd4f2af065334a9168   application/vnd.docker.distribution.manifest.v2+json      sha256:3dd6190a87b41592d897862f47b3c0318c338e15978f25bd4f2af065334a9168 26.3 MiB  linux/amd64                                                                  io.cri-containerd.image=managed
docker.io/virtualcluster/syncer-amd64:latest                                                                     application/vnd.oci.image.index.v1+json                   sha256:79ffe0c8a1adce6abcff9f44eea474b2a28bc14d477ee835f46ab831ae87e840 39.4 MiB  linux/amd64                                                                  io.cri-containerd.image=managed
docker.io/virtualcluster/vn-agent-amd64:latest                                                                   application/vnd.oci.image.index.v1+json                   sha256:dd6af8306a682f2052cbea4403290c79614b7f45b00eed2bdc0ec0edc9e8b75c 37.3 MiB  linux/amd64                                                                  io.cri-containerd.image=managed
docker.io/virtualcluster/vn-agent-amd64@sha256:6e0415c7690e034a1cd9a45243508ff180fa3053364442579e166708cf641511  application/vnd.docker.distribution.manifest.v2+json      sha256:6e0415c7690e034a1cd9a45243508ff180fa3053364442579e166708cf641511 27.0 MiB  linux/amd64                                                                  io.cri-containerd.image=managed
$
```

#### 配布スクリプトのログ確認

本ロールでは, virtual clusterを構成するために必要なコンテナイメージをワーカーノード上に配布する処理を本ロールで作成されるコンテナイメージ配布スクリプトによって実施します。

`roles/k8s-virtual-cluster/tasks/distribute-to-workers.yml`の動作状況を, ansibleの実行ログから確認し, 適切にコンテナイメージの配布が行えていることを確認してください。

正常に成功した場合のログの例を以下に示します:

```plaintext
ok: [k8sctrlplane01.local] => {
    "changed": false,
    "cmd": [
        "/tmp/vc-images/distribute-images.sh"
    ],
    "delta": "0:00:11.490155",
    "end": "2026-02-24 01:23:22.475830",
    "invocation": {
        "module_args": {
            "_raw_params": "/tmp/vc-images/distribute-images.sh",
            "_uses_shell": false,
            "argv": null,
            "chdir": null,
            "creates": null,
            "executable": null,
            "expand_argument_vars": true,
            "removes": null,
            "stdin": null,
            "stdin_add_newline": true,
            "strip_empty_ends": true
        }
    },
    "msg": "",
    "rc": 0,
    "start": "2026-02-24 01:23:10.985675",
    "stderr": "",
    "stderr_lines": [],
    "stdout": "=== Virtual Cluster Image Distribution Script ===\nStarted at: 2026年  2月 24日 火曜日 01:23:10 JST\nUser: ansible\nImage directory: /tmp/vc-images\nComponents: manager syncer vn-agent\n=== Fetching worker node list from Kubernetes cluster ===\nWorker nodes found: k8sworker0101 k8sworker0102\n=== Registering SSH host keys ===\nRegistering k8sworker0101...\nRegistering k8sworker0102...\n=== Distributing images to worker nodes ===\n--- Processing worker: k8sworker0101 ---\n  Transferring manager-amd64.tar to k8sworker0101...\n  Importing manager-amd64.tar on k8sworker0101...\ndocker.io/virtualcluster/manager-amd64:latest\nunpacking docker.io/virtualcluster/manager-amd64:latest (sha256:2e8dc650dc067fcc7f2d6444511b4473c58357d1f4e6c57630839a89274b0d51)...done\n  Completed: manager on k8sworker0101\n  Transferring syncer-amd64.tar to k8sworker0101...\n  Importing syncer-amd64.tar on k8sworker0101...\ndocker.io/virtualcluster/syncer-amd64:latest\nunpacking docker.io/virtualcluster/syncer-amd64:latest (sha256:79ffe0c8a1adce6abcff9f44eea474b2a28bc14d477ee835f46ab831ae87e840)...done\n  Completed: syncer on k8sworker0101\n  Transferring vn-agent-amd64.tar to k8sworker0101...\n  Importing vn-agent-amd64.tar on k8sworker0101...\ndocker.io/virtualcluster/vn-agent-amd64:latest\nunpacking docker.io/virtualcluster/vn-agent-amd64:latest (sha256:dd6af8306a682f2052cbea4403290c79614b7f45b00eed2bdc0ec0edc9e8b75c)...done\n  Completed: vn-agent on k8sworker0101\n--- Worker k8sworker0101 completed ---\n--- Processing worker: k8sworker0102 ---\n  Transferring manager-amd64.tar to k8sworker0102...\n  Importing manager-amd64.tar on k8sworker0102...\ndocker.io/virtualcluster/manager-amd64:latest\nunpacking docker.io/virtualcluster/manager-amd64:latest (sha256:2e8dc650dc067fcc7f2d6444511b4473c58357d1f4e6c57630839a89274b0d51)...done\n  Completed: manager on k8sworker0102\n  Transferring syncer-amd64.tar to k8sworker0102...\n  Importing syncer-amd64.tar on k8sworker0102...\ndocker.io/virtualcluster/syncer-amd64:latest\nunpacking docker.io/virtualcluster/syncer-amd64:latest (sha256:79ffe0c8a1adce6abcff9f44eea474b2a28bc14d477ee835f46ab831ae87e840)...done\n  Completed: syncer on k8sworker0102\n  Transferring vn-agent-amd64.tar to k8sworker0102...\n  Importing vn-agent-amd64.tar on k8sworker0102...\ndocker.io/virtualcluster/vn-agent-amd64:latest\nunpacking docker.io/virtualcluster/vn-agent-amd64:latest (sha256:dd6af8306a682f2052cbea4403290c79614b7f45b00eed2bdc0ec0edc9e8b75c)...done\n  Completed: vn-agent on k8sworker0102\n--- Worker k8sworker0102 completed ---\n=== All images distributed successfully ===\nCompleted at: 2026年  2月 24日 火曜日 01:23:22 JST",
    "stdout_lines": [
        "=== Virtual Cluster Image Distribution Script ===",
        "Started at: 2026年  2月 24日 火曜日 01:23:10 JST",
        "User: ansible",
        "Image directory: /tmp/vc-images",
        "Components: manager syncer vn-agent",
        "=== Fetching worker node list from Kubernetes cluster ===",
        "Worker nodes found: k8sworker0101 k8sworker0102",
        "=== Registering SSH host keys ===",
        "Registering k8sworker0101...",
        "Registering k8sworker0102...",
        "=== Distributing images to worker nodes ===",
        "--- Processing worker: k8sworker0101 ---",
        "  Transferring manager-amd64.tar to k8sworker0101...",
        "  Importing manager-amd64.tar on k8sworker0101...",
        "docker.io/virtualcluster/manager-amd64:latest",
        "unpacking docker.io/virtualcluster/manager-amd64:latest (sha256:2e8dc650dc067fcc7f2d6444511b4473c58357d1f4e6c57630839a89274b0d51)...done",
        "  Completed: manager on k8sworker0101",
        "  Transferring syncer-amd64.tar to k8sworker0101...",
        "  Importing syncer-amd64.tar on k8sworker0101...",
        "docker.io/virtualcluster/syncer-amd64:latest",
        "unpacking docker.io/virtualcluster/syncer-amd64:latest (sha256:79ffe0c8a1adce6abcff9f44eea474b2a28bc14d477ee835f46ab831ae87e840)...done",
        "  Completed: syncer on k8sworker0101",
        "  Transferring vn-agent-amd64.tar to k8sworker0101...",
        "  Importing vn-agent-amd64.tar on k8sworker0101...",
        "docker.io/virtualcluster/vn-agent-amd64:latest",
        "unpacking docker.io/virtualcluster/vn-agent-amd64:latest (sha256:dd6af8306a682f2052cbea4403290c79614b7f45b00eed2bdc0ec0edc9e8b75c)...done",
        "  Completed: vn-agent on k8sworker0101",
        "--- Worker k8sworker0101 completed ---",
        "--- Processing worker: k8sworker0102 ---",
        "  Transferring manager-amd64.tar to k8sworker0102...",
        "  Importing manager-amd64.tar on k8sworker0102...",
        "docker.io/virtualcluster/manager-amd64:latest",
        "unpacking docker.io/virtualcluster/manager-amd64:latest (sha256:2e8dc650dc067fcc7f2d6444511b4473c58357d1f4e6c57630839a89274b0d51)...done",
        "  Completed: manager on k8sworker0102",
        "  Transferring syncer-amd64.tar to k8sworker0102...",
        "  Importing syncer-amd64.tar on k8sworker0102...",
        "docker.io/virtualcluster/syncer-amd64:latest",
        "unpacking docker.io/virtualcluster/syncer-amd64:latest (sha256:79ffe0c8a1adce6abcff9f44eea474b2a28bc14d477ee835f46ab831ae87e840)...done",
        "  Completed: syncer on k8sworker0102",
        "  Transferring vn-agent-amd64.tar to k8sworker0102...",
        "  Importing vn-agent-amd64.tar on k8sworker0102...",
        "docker.io/virtualcluster/vn-agent-amd64:latest",
        "unpacking docker.io/virtualcluster/vn-agent-amd64:latest (sha256:dd6af8306a682f2052cbea4403290c79614b7f45b00eed2bdc0ec0edc9e8b75c)...done",
        "  Completed: vn-agent on k8sworker0102",
        "--- Worker k8sworker0102 completed ---",
        "=== All images distributed successfully ===",
        "Completed at: 2026年  2月 24日 火曜日 01:23:22 JST"
    ]
}
```

## 留意事項

- `virtualcluster_enabled` が `true` の場合のみロールが実行されます。
- `virtualcluster_build_from_source: false` を設定すると, ビルド処理をスキップして既存のイメージからの配布のみを実行できます。
- ワーカーノードリストは `kubectl get nodes` から動的に取得されるため, inventory/hosts の設定は不要です。
- ビルドノードとしてリモートサーバーを指定する場合, `virtualcluster_build_host` を適切に設定してください。
- 本ロールは実験環境向けに作成されており, 実運用環境での設計の妥当性については考慮していません。