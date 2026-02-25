 # k8s-vc-instances ロール

[VirtualCluster - Enabling Kubernetes Hard Multi-tenancy](https://github.com/kubernetes-retired/cluster-api-provider-nested/tree/main/virtualcluster) (
Kubernetes Virtual Cluster ) のテナント環境を構築するロールです。k8s-virtual-cluster ロールが展開した基盤 (vc-manager, syncer, vn-agent, CRD) 上に, ClusterVersion および VirtualCluster CRD で定義されたカスタムリソース(CR)インスタンスを生成します。各テナントの論理的な Kubernetes クラスタ設定を一元管理し, スーパークラスタから自動検出されたコンポーネントバージョンを活用します。本ロールはイメージ情報を独立に取得するため, k8s-virtual-cluster ロールと同一 play 内での実行は必須ではありません。ただし, CRD が事前に登録されている必要があります。

本文中の~(チルダ記号)は, ansibleアカウントでログイン時のホームディレクトリ(規定: `/home/ansible`)を意味します。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウエア。 |
| CustomResourceDefinition | CRD | Kubernetes に独自のリソース型を追加するための型定義。 |
| Custom Resource | CR | CRD で定義された独自のリソース型に基づいて作成される実際のリソースオブジェクト。CRD はリソース型の定義であり, CR はその型に基づいて作成されたリソースの個別インスタンス。 |
| コントロールプレーン ( Control Plane ) | コントロールプレーン | Kubernetes クラスタの管理機能を提供するコンポーネント群。API サーバー, スケジューラー, コントローラーマネージャー, etcd などを含み, クラスタ全体の制御と調整を行う。 |
| ワーカーノード ( Worker Node ) | ワーカーノード | Kubernetes クラスタで実際にアプリケーション(ポッド ( Pod ))が実行されるノード。kubelet と呼ばれるエージェントが動作し, コントロールプレーンからの指示に基づいてコンテナを実行管理する。 |
| 仮想クラスタ ( Virtual Cluster ) | Virtual Cluster | Kubernetes API を仮想化して提供する論理的な Kubernetes クラスタ。各テナントに独立した専用クラスタとして見える環境を提供する。 |
| スーパークラスタ ( Super Cluster ) | Super Cluster | 仮想クラスタ ( Virtual Cluster ) を動作させるホスト側の物理 Kubernetes クラスタ。実際のノードリソースを提供する。 |
| Tenant | テナント | 互いに独立した Kubernetes コントロールプレーンを持つ論理的な利用者またはチーム。各テナントについて, 専用の仮想クラスタ ( Virtual Cluster ) が割り当てられ, テナントに割り当てられた仮想クラスタ ( Virtual Cluster ) 内のリソース (名前空間, CRD) を他のテナントに影響を与えずに作成できる。物理リソース (ノード) をスーパークラスタ (Super Cluster) を通じて他のテナントと共有し, かつ, 仮想リソース (Kubernetes のリソース) は, Kubernetes のコントロールプレーンレベルで分離される。 |
| VirtualClusterCRD | VirtualCluster | テナント用仮想クラスタ ( Virtual Cluster ) の設定を定義するリソース型(CRD)。 |
| ClusterVersionCRD | ClusterVersion | 仮想クラスタ ( Virtual Cluster ) 内で使用するコンポーネント(etcd, kube-apiserver, kube-controller-manager)のコンテナイメージ情報を定義するリソース型(CRD)。 |
| ClusterVersionインスタンス | - | ClusterVersionCRD リソース型に基づいて作成された実際のリソースオブジェクト(例: `cv-k8s-1-31`)。 |
| VirtualClusterインスタンス | - | VirtualClusterCRD リソース型に基づいて作成された実際のリソースオブジェクト(例: `tenant-alpha`, `tenant-beta`)。 |
| vc-manager | - | 仮想クラスタ ( Virtual Cluster ) の制御コンポーネント。 |
| etcd | etcd | Kubernetes の設定情報と状態を保存する分散キーバリューストア。 |
| kube-apiserver | kube-apiserver | Kubernetes API サーバー, API リクエストを受け付けて処理するコンポーネント。 |
| kube-controller-manager | kube-controller-manager | Kubernetes コントローラーマネージャー, リソースの状態を監視して制御するコンポーネント。 |
| 名前空間 | namespace | Kubernetes クラスタ内で複数のユーザーやチーム間でリソースを分離管理する論理的な区分。 |

## 前提条件

- Kubernetes クラスタが稼働していること(v1.22 以上推奨)。
- `kubectl` コマンドが利用可能であること。
- **k8s-virtual-cluster ロールが実行済みであること**(以下のリソースが存在する必要があります):
  - `vc-manager` 名前空間
  - ClusterVersionCRD(`clusterversions.tenancy.x-k8s.io`)
  - VirtualClusterCRD(`virtualclusters.tenancy.x-k8s.io`)
  - vc-manager, syncer, vn-agent コンポーネントが稼働中
- `virtualcluster_supercluster_kubeconfig_path` の参照先にアクセス可能であること(既定: `/etc/kubernetes/admin.conf`)。

## 実行フロー

本ロールは以下の順序で処理を実行します。`k8s_vcinstances_enabled: true` でない場合, すべてのタスクをスキップします。

1. **パラメータ読み込み**(`load-params.yml`): クラスタ共通変数を読み込みます(このファイルは変更禁止)。
2. **追加パラメータ検証**(`load-additional-params.yml`): CRD 関連の変数が存在することを確認します。
3. **前提条件検証**(`validate.yml`): `vc-manager` 名前空間, ClusterVersionCRD, VirtualClusterCRD が存在することを確認します。存在しない場合はエラーで停止します。
4. **設定ディレクトリ作成**(`directory.yml`): マニフェスト出力先ディレクトリ(`vcinstances_config_dir`, 既定: `~/kubeadm/vc-instances`)を作成します。
5. **スーパークラスタイメージ検出**(`detect-supercluster-images.yml`): kube-system 名前空間から etcd, kube-apiserver, kube-controller-manager のイメージを自動検出します(`vcinstances_auto_detect_supercluster_images: true` の場合のみ)。
6. **ClusterVersionインスタンス生成**(`clusterversion-instances.yml`): `vcinstances_clusterversions` をループ処理し, 各 ClusterVersionインスタンスのマニフェストを生成, 適用します。`name` がない定義は警告を出してスキップします。
7. **VirtualClusterインスタンス生成**(`virtualcluster-instances.yml`): `vcinstances_virtualclusters` をループ処理し, 各 VirtualClusterインスタンスのマニフェストを生成, 適用します。`name` または `clusterVersionName` がない定義は警告を出してスキップします。
8. **検証**(`verify.yml`): 作成された ClusterVersionインスタンス, VirtualClusterインスタンスを `kubectl get` で一覧表示し, ログに出力します。VirtualClusterインスタンスの一覧は `--all-namespaces` で取得します。

## 主要変数

| 変数名 | 既定値 | k8s-virtual-cluster ロール由来 | 説明 |
| --- | --- | --- | --- |
| `k8s_vcinstances_enabled` | `false` | - | ロール実行の有効化を示します。 |
| `vcinstances_config_dir` | `"{{ k8s_kubeadm_config_store | default(ansible_user + '/kubeadm', true) }}/vc-instances"` | - | マニフェスト出力先ディレクトリです(既定値: `~/kubeadm/vc-instances`)。 |
| `vcinstances_auto_detect_supercluster_images` | `true` | - | スーパークラスタからのイメージ情報自動検出の有効化を示します。 |
| `vcinstances_clusterversions` | `[]` | - | ClusterVersionインスタンス定義のリストです(詳細は「設定例」節を参照)。 |
| `vcinstances_virtualclusters` | `[]` | - | VirtualClusterインスタンス定義のリストです(詳細は「設定例」節を参照)。 |
| `virtualcluster_api_group` | `"tenancy.x-k8s.io"` | yes | CRD の API グループです。 |
| `virtualcluster_api_version` | `"v1alpha1"` | yes | CRD の API バージョンです。 |
| `virtualcluster_namespace` | `"vc-manager"` | yes | 仮想クラスタ ( Virtual Cluster ) 管理コンポーネントの名前空間です。 |
| `virtualcluster_supercluster_kubeconfig_path` | `"/etc/kubernetes/admin.conf"` | yes | スーパークラスタ操作用 kubeconfig パスです。 |

k8s-virtual-cluster ロール由来の列に`yes`と記載されている変数は, k8s-virtual-cluster ロール内の同名の変数の定義値と同じ値にする必要があります。

本ロールでは, ロールを単独で実行可能とするために, k8s-virtual-cluster ロール内の同名の変数を本ロール内で再定義しています。

### 検出されたイメージ情報(ロール内変数)

本ロール内で以下のロール内変数(fact)が設定されます。

| 変数名 | 説明 |
| --- | --- |
| `vcinstances_detected_etcd_image` | 検出されたまたはフォールバック etcd イメージ。 |
| `vcinstances_detected_apiserver_image` | 検出されたまたはフォールバック kube-apiserver イメージ。 |
| `vcinstances_detected_controller_manager_image` | 検出されたまたはフォールバック kube-controller-manager イメージ。 |

### 自動検出のフォールバック値

イメージ検出に失敗した場合, 以下の値をフォールバックとして使用します。

- etcd: `registry.k8s.io/etcd:{{ k8s_etcd_major_minor | default('3.5', true) }}.0`
- kube-apiserver: `registry.k8s.io/kube-apiserver:v{{ k8s_major_minor | default('1.31', true) }}.0`
- kube-controller-manager: `registry.k8s.io/kube-controller-manager:v{{ k8s_major_minor | default('1.31', true) }}.0`

`vcinstances_auto_detect_supercluster_images: false` の場合, 検出処理は行われないため, ClusterVersionインスタンスの各イメージを明示指定してください。

## 主な処理

- `k8s_vcinstances_enabled` の有効化を確認します。
- CRD 関連の変数と `vc-manager` 名前空間の存在を検証します。
- マニフェスト出力先ディレクトリを作成します。
- kube-system からコントロールプレーン ( Control Plane ) イメージを検出します(自動検出有効時)。
- ClusterVersionインスタンスと VirtualClusterインスタンスのマニフェストを生成, 適用し, 作成完了を待機します。
- ClusterVersionインスタンス, VirtualClusterインスタンスの一覧を出力し, 作成結果を可視化します。

## テンプレートと生成ファイル

| テンプレート | 出力先 | 説明 |
| --- | --- | --- |
| `templates/clusterversion-instance.yaml.j2` | `{{ vcinstances_config_dir }}/clusterversion-<name>.yaml` | ClusterVersionインスタンスマニフェストです。 |
| `templates/virtualcluster-instance.yaml.j2` | `{{ vcinstances_config_dir }}/virtualcluster-<name>.yaml` | VirtualClusterインスタンスマニフェストです。 |

## 生成されるリソース

| リソース種別 | リソース名(例) | 説明 |
| --- | --- | --- |
| ClusterVersionインスタンス | `cv-k8s-1-31` | ClusterVersionCRD リソース型に基づいて生成されるインスタンス。仮想クラスタ ( Virtual Cluster ) 内で使用するコントロールプレーン ( Control Plane ) コンポーネント(etcd, kube-apiserver, kube-controller-manager)のコンテナイメージ情報を定義します。 |
| VirtualClusterインスタンス | `tenant-alpha`, `tenant-beta` | VirtualClusterCRD リソース型に基づいて生成されるインスタンス。テナントに割り当てられた仮想クラスタ ( Virtual Cluster ) の設定を定義します。 |

## 設定例

### ClusterVersionインスタンス定義

`vcinstances_clusterversions` はリスト形式で定義します。各要素は以下のキーを持ちます。

```yaml
vcinstances_clusterversions:
  - name: "cv-k8s-1-31"  # ClusterVersionインスタンス リソース名(必須)
    # 以下はオプション(省略時は検出値を使用)
    etcd:
      image: "registry.k8s.io/etcd"
      imageTag: "3.5.15-0"
    apiServer:
      image: "registry.k8s.io/kube-apiserver"
      imageTag: "v1.31.0"
    controllerManager:
      image: "registry.k8s.io/kube-controller-manager"
      imageTag: "v1.31.0"
```

**設定のポイント**:
- `name` は必須です。未指定の場合, 該当定義は警告を出してスキップされます。
- `etcd`, `apiServer`, `controllerManager` は省略可能です。省略時はスーパークラスタから自動検出されたイメージを使用します。
- `vcinstances_auto_detect_supercluster_images: false` の場合, イメージは明示指定してください。

### VirtualClusterインスタンス定義

`vcinstances_virtualclusters` はリスト形式で定義します。各要素は以下のキーを持ちます。

```yaml
vcinstances_virtualclusters:
  - name: "tenant-alpha"               # VirtualClusterインスタンス リソース名(必須)
    namespace: "vc-manager"            # デプロイ先 Kubernetes の名前空間(省略時: vc-manager)
    clusterVersionName: "cv-k8s-1-31"  # 使用する ClusterVersionインスタンス リソース名(必須)
    clusterDomain: "tenant-alpha.vc.local"         # テナント DNS ドメイン(オプション)
    kubeConfigSecretName: "tenant-alpha-kubeconfig"  # kubeconfig Secret 名(オプション)

  - name: "tenant-beta"
    namespace: "vc-manager"
    clusterVersionName: "cv-k8s-1-31"
    clusterDomain: "tenant-beta.vc.local"
```

**設定のポイント**:
- `name` と `clusterVersionName` は必須です。未指定の場合, 該当定義は警告を出してスキップされます。
- `namespace` は省略時に `virtualcluster_namespace`(既定: `vc-manager`)が使用されます。
- `clusterDomain`, `kubeConfigSecretName` はオプションです。

### host_vars での完全な設定例

```yaml
# host_vars/k8sctrlplane01.local

# k8s-virtual-cluster を有効化
virtualcluster_enabled: true

# k8s-vc-instances を有効化
k8s_vcinstances_enabled: true

# ClusterVersionインスタンス定義
vcinstances_clusterversions:
  - name: "cv-k8s-1-31"
    # イメージ指定を省略(スーパークラスタ検出値を使用)

# VirtualClusterインスタンス定義
vcinstances_virtualclusters:
  - name: "tenant-alpha"
    namespace: "vc-manager"
    clusterVersionName: "cv-k8s-1-31"
    clusterDomain: "tenant-alpha.vc.local"
    kubeConfigSecretName: "tenant-alpha-kubeconfig"

  - name: "tenant-beta"
    namespace: "vc-manager"
    clusterVersionName: "cv-k8s-1-31"
    clusterDomain: "tenant-beta.vc.local"
    kubeConfigSecretName: "tenant-beta-kubeconfig"
```

## 実行方法

```bash
# k8s-management.yml を実行
ansible-playbook -i inventory/hosts k8s-management.yml

# 特定ホストのみ対象
ansible-playbook -i inventory/hosts k8s-management.yml -l k8sctrlplane01.local

# k8s-vc-instances タスクのみ実行
ansible-playbook -i inventory/hosts k8s-management.yml -t k8s-vc-instances
```

または Makefile から:

```bash
make run_k8s_vc_instances
```

## 検証ポイント

以下の順序で確認してください。検証コマンドは実装の verify.yml と同じ範囲になるように記載しています。

### 1. 前提リソースの確認

```bash
kubectl get namespace vc-manager
kubectl get crd clusterversions.tenancy.x-k8s.io
kubectl get crd virtualclusters.tenancy.x-k8s.io
```

**期待される出力例**:
```
NAME         STATUS   AGE
vc-manager   Active   15h
NAME                               CREATED AT
clusterversions.tenancy.x-k8s.io   2026-02-24T21:08:15Z
NAME                               CREATED AT
virtualclusters.tenancy.x-k8s.io   2026-02-24T21:08:15Z
```

**確認ポイント**:
- `vc-manager` 名前空間が存在すること。
- ClusterVersionCRD, VirtualClusterCRD が登録されていること。

### 2. ClusterVersionインスタンス一覧の確認

```bash
kubectl get clusterversions -o wide
```

**期待される出力例**:
```
NAME           AGE
cv-k8s-1-31    15h
```

### 3. VirtualClusterインスタンス一覧の確認

```bash
kubectl get virtualclusters --all-namespaces -o wide
```

**期待される出力例**:
```
NAMESPACE    NAME           STATUS    AGE   CLUSTERVERSION
vc-manager   tenant-alpha   Running   15h   cv-k8s-1-31
vc-manager   tenant-beta    Running   15h   cv-k8s-1-31
```

**補足**:
`vc-manager` に限定する場合は以下を使用します。

```bash
kubectl get virtualclusters -n vc-manager -o wide
```

**確認ポイント**:
- 対象の VirtualClusterインスタンスが表示されること。
- `STATUS` が `Pending` から `Running` に遷移すること。

### 4. VirtualClusterインスタンス詳細の確認

```bash
kubectl get virtualcluster tenant-alpha -n vc-manager -o yaml
```

**期待される出力例** (一部抜粋):
```yaml
apiVersion: tenancy.x-k8s.io/v1alpha1
kind: VirtualCluster
metadata:
  name: tenant-alpha
  namespace: vc-manager
spec:
  clusterDomain: tenant-alpha.vc.local
  clusterVersionName: cv-k8s-1-31
status:
  clusterNamespace: vc-manager-64b627-tenant-alpha
  message: tenant control plane is running
  phase: Running
  reason: TenantControlPlaneRunning
```

**確認ポイント**:
- `spec.clusterVersionName` が意図した ClusterVersionインスタンスを参照していること。
- `spec.clusterDomain` が意図したドメインに設定されていること(指定した場合)。
- `status.phase` が `Running` へ遷移していること。

### 5. vc-manager ログの確認

```bash
kubectl -n vc-manager logs deployment/vc-manager --tail=50
```

**確認ポイント**:
- VirtualClusterインスタンス作成処理の開始ログが出力されていること。
- `fail to create virtualcluster` 等のエラーが出ていないこと。

### 6. テナント名前空間の確認

```bash
kubectl get namespaces | grep tenant
```

**期待される出力例**:
```
vc-manager-64b627-tenant-alpha                   Active   15h
vc-manager-64b627-tenant-alpha-default           Active   15h
vc-manager-64b627-tenant-alpha-kube-node-lease   Active   15h
vc-manager-64b627-tenant-alpha-kube-public       Active   15h
vc-manager-64b627-tenant-alpha-kube-system       Active   15h
vc-manager-e94731-tenant-beta                    Active   15h
```

**確認ポイント**:
- `vc-manager-<suffix>-<tenant>` 形式の名前空間が作成されていること。

### 7. テナント用 Pod の確認

```bash
kubectl get pods --all-namespaces | grep tenant
```

**期待される出力例**:
```
vc-manager-64b627-tenant-alpha   apiserver-0            1/1   Running   0   15h
vc-manager-64b627-tenant-alpha   controller-manager-0   1/1   Running   0   15h
vc-manager-64b627-tenant-alpha   etcd-0                 1/1   Running   0   15h
vc-manager-e94731-tenant-beta    apiserver-0            1/1   Running   0   15h
vc-manager-e94731-tenant-beta    controller-manager-0   1/1   Running   0   15h
vc-manager-e94731-tenant-beta    etcd-0                 1/1   Running   0   15h
```

**確認ポイント**:
- 各テナント名前空間に `etcd-0`, `apiserver-0`, `controller-manager-0` が存在すること。

### 8. イベントの確認

```bash
kubectl -n vc-manager get events --sort-by='.lastTimestamp' | tail -20
```

**期待される出力例**:
```
LAST SEEN   TYPE      REASON             OBJECT               MESSAGE
69s         Warning   DNSConfigForming   pod/vn-agent-tlqgb   Nameserver limits were exceeded, some nameservers have been omitted, the applied nameserver line is: 192.168.20.11 192.168.20.1 fd69:6684:61a:1::11
45s         Warning   DNSConfigForming   pod/vn-agent-xjsq4   Nameserver limits were exceeded, some nameservers have been omitted, the applied nameserver line is: 192.168.20.11 192.168.20.1 fd69:6684:61a:1::11
```

**確認ポイント**:
- VirtualClusterインスタンス作成イベントが記録されていること。
- 直近の Warning/ERROR が意図しない内容でないこと。

## トラブルシューティング

### ClusterVersionインスタンスが作成されない場合

#### 原因 1: k8s-virtual-cluster ロールが未実行

**症状**:
```
Error from server (NotFound): customresourcedefinitions.apiextensions.k8s.io "clusterversions.tenancy.x-k8s.io" not found
```

**解決方法**:
1. k8s-virtual-cluster ロールを先に実行してください:
   ```bash
   ansible-playbook -i inventory/hosts k8s-management.yml -t k8s-virtual-cluster
   ```

2. CRD が登録されていることを確認:
   ```bash
   kubectl get crd clusterversions.tenancy.x-k8s.io
   ```

#### 原因 2: イメージ検出に失敗した場合

**症状**:
テンプレート生成時に不正な形式のイメージ情報が使用される。

**確認コマンド**:
```bash
# Ansible 実行ログで検出されたイメージを確認
grep "Detected Super Cluster images" /tmp/ansible.log
```

**解決方法**:
`vcinstances_auto_detect_supercluster_images` を `false` に設定し, ClusterVersionインスタンス定義で明示的にイメージを指定してください:

```yaml
vcinstances_auto_detect_supercluster_images: false
vcinstances_clusterversions:
  - name: "cv-k8s-1-31"
    etcd:
      image: "registry.k8s.io/etcd"
      imageTag: "3.5.15-0"
    apiServer:
      image: "registry.k8s.io/kube-apiserver"
      imageTag: "v1.31.0"
    controllerManager:
      image: "registry.k8s.io/kube-controller-manager"
      imageTag: "v1.31.0"
```

### VirtualClusterインスタンスが `Pending` から遷移しない場合

#### 原因 1: vc-manager が起動していない

**確認コマンド**:
```bash
kubectl -n vc-manager get pods -l app=vc-manager
```

**解決方法**:
vc-manager Pod が Running でない場合, k8s-virtual-cluster ロールを再実行してください。

#### 原因 2: ClusterVersionインスタンスが存在しない

**確認コマンド**:
```bash
kubectl get clusterversion cv-k8s-1-31
```

**解決方法**:
VirtualClusterインスタンスの `spec.clusterVersionName` で指定した ClusterVersionインスタンスが存在することを確認してください。

#### 原因 3: vc-manager のログにエラーがある

**確認コマンド**:
```bash
kubectl -n vc-manager logs deployment/vc-manager --tail=100 | grep -i error
```

**解決方法**:
エラーメッセージに応じて対処してください。一般的な問題:
- リソース不足: ノードのリソース (CPU, メモリ) を確認
- イメージ取得失敗: イメージレジストリへの疎通を確認

### マニフェストファイルが生成されない場合

#### 原因: k8s_vcinstances_enabled が false

**確認コマンド**:
```bash
grep k8s_vcinstances_enabled host_vars/k8sctrlplane01.local
```

**解決方法**:
host_vars で `k8s_vcinstances_enabled: true` を設定してください。

### kubectl apply で権限エラーが発生する場合

**症状**:
```
Error from server (Forbidden): error when creating ...
```

**解決方法**:
使用している kubeconfig に ClusterVersionインスタンス, VirtualClusterインスタンスの作成権限があることを確認してください。本ロールは既定で `/etc/kubernetes/admin.conf` を使用します。

## 参考リンク

- [VirtualCluster - Enabling Kubernetes Hard Multi-tenancy](https://github.com/kubernetes-retired/cluster-api-provider-nested/tree/main/virtualcluster)
