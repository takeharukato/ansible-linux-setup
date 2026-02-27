 # k8s-vc-instances ロール

[VirtualCluster - Enabling Kubernetes Hard Multi-tenancy](https://github.com/kubernetes-retired/cluster-api-provider-nested/tree/main/virtualcluster) (
Kubernetes Virtual Cluster ) のテナント ( Tenant ) 環境を構築するロールです。k8s-virtual-cluster ロールが展開した基盤 (vc-manager, syncer, vn-agent, CRD) 上に, ClusterVersion および VirtualCluster CRD で定義されたカスタムリソース(CR)インスタンスを生成します。各テナント ( Tenant ) の論理的な Kubernetes クラスタ設定を一元管理し, スーパークラスタから自動検出されたコンポーネントバージョンを活用します。本ロールはイメージ情報を独立に取得するため, k8s-virtual-cluster ロールと同一 play 内での実行は必須ではありません。ただし, CRD が事前に登録されている必要があります。

本文中の~(チルダ記号)は, ansibleアカウントでログイン時のホームディレクトリ(規定: `/home/ansible`)を意味します。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウエア。 |
| Application Programming Interface | API | 他の仕組みから機能を呼び出すための窓口。 |
| CustomResourceDefinition | CRD | Kubernetes に独自のリソース型を追加する仕組み。 |
| Custom Resource | CR | CRD で定義された独自のリソース型に基づいて作成される実際のリソースオブジェクト。CRD はリソース型の定義であり, CR はその型に基づいて作成されたリソースの個別インスタンス。 |
| Role Based Access Control | RBAC | 権限を役割単位で制御する仕組み。 |
| Transport Layer Security | TLS | 通信を暗号化する仕組み。 |
| Domain Name System | DNS | 名前と IP アドレスを対応付ける仕組み。 |
| etcd | etcd | Kubernetes の設定情報と状態を保存する分散キーバリューストア。 |
| kube-apiserver | kube-apiserver | Kubernetes API サーバー, API リクエストを受け付けて処理するコンポーネント。 |
| kube-controller-manager | kube-controller-manager | Kubernetes コントローラーマネージャー, リソースの状態を監視して制御するコンポーネント。 |
| kubectl | kubectl | Kubernetes クラスタを操作するコマンドラインツール。API サーバーへのリクエストを送信し, リソースの作成・更新・削除・確認を行う。 |
| コントロールプレーン ( Control Plane ) | コントロールプレーン | Kubernetes クラスタの管理機能を提供するコンポーネント群。API サーバー, スケジューラー, コントローラーマネージャー, etcd などを含み, クラスタ全体の制御と調整を行う。 |
| コントロールプレーンノード ( Control Plane Node ) | コントロールプレーンノード | Kubernetes コントロールプレーンコンポーネント(API サーバー, スケジューラー, コントローラーマネージャー, etcd など)が動作するノード(物理マシンまたは仮想マシン)。 |
| ワーカーノード ( Worker Node ) | ワーカーノード | Kubernetes クラスタで実際にアプリケーション(ポッド ( Pod ))が実行されるノード。kubelet と呼ばれるエージェントが動作し, コントロールプレーンからの指示に基づいてコンテナを実行管理する。 |
| コンテナ ( Container ) | コンテナ | アプリケーションと依存関係を一つのパッケージ化したもの。軽量で, どの環境でも一貫して実行可能。 |
| ポッド ( Pod ) | Pod | Kubernetes の最小デプロイメント単位。1 個以上のコンテナ ( Container ) で構成される実行環境。ポッド ( Pod ) 内のすべてのコンテナ ( Container ) は共有ネットワーク(共用 IP・ポート), 共有ストレージによって密接に結合され, 同一ノード上で常に共存・同期スケジュール される。 |
| デプロイメント ( Deployment ) | Deployment | Kubernetes リソース。ステートレスなアプリケーション向け。複数のレプリカ(ポッド ( Pod ) の複製)を管理し, 水平スケーリング に対応。 |
| ステートレス ( Stateless ) | ステートレス | アプリケーションの性質を表す用語で，アプリケーションから使用される各種データの状態を永続記憶(ストレージ)に保持しなくとも，動作可能なアプリケーションであることを示す。 |
| ステートフル ( Stateful ) | ステートフル | アプリケーションの性質を表す用語で，アプリケーションから使用される各種データの状態を永続記憶(ストレージ)に保持することを前提として動作するアプリケーションであることを示す。 |
| PersistentVolume | PV | Kubernetes リソース。クラスタ内の永続ストレージを表すリソース。ボリュームのサイズ, アクセスモード, 回収ポリシー, バックエンド(ローカルストレージ, NFS, ブロック型ストレージなど)を定義。 |
| PersistentVolumeClaim | PVC | Kubernetes リソース。ポッド ( Pod ) がストレージを利用する際の要求リソース。必要なストレージ容量, アクセスモードを指定し, Kubernetes のコントローラーが対応する PersistentVolume にバインドする。 |
| StorageClass | - | Kubernetes リソース。永続ストレージのプロビジョニング方法を定義するリソース。プロビジョナー(ローカルストレージプロビジョナー, AWS EBS, NFS など)とパラメータを指定し, PersistentVolumeClaim の要求に基づいて動的に PersistentVolume を作成する。 |
| バインド ( Bind ) | - | Kubernetes ストレージレイヤーにおける処理。PersistentVolumeClaim の要求条件(容量, アクセスモード)が PersistentVolume の仕様と合致した場合, Kubernetes のコントローラーが両者を紐付ける。バインド後, ポッドは PVC 経由で PV のストレージを利用できるようになる。 |
| プロビジョニング ( Provisioning ) | - | Kubernetes ストレージレイヤーにおける処理。StorageClass で定義されたプロビジョナーが, PersistentVolumeClaim の要求に応じて新しい PersistentVolume を自動的に作成するプロセス。動的プロビジョニングにより, ユーザーが個別に PV を作成する手間を削減できる。静的プロビジョニング(管理者が事前に PV を作成)に対応する概念。 |
| プロビジョナー ( Provisioner ) | - | Kubernetes ストレージスタックのコンポーネント。StorageClass で指定し, PersistentVolumeClaim の要求に基づいて PersistentVolume を自動作成する。実装にはローカルストレージプロビジョナー, AWS EBS CSI ドライバー, NFS などが存在。 |
| emptyDir | - | Kubernetes ボリュームタイプ。ポッドがノードに割り当てられた時に作成される一時的なボリューム。ポッドが存在する限りデータが保持され, ポッド削除時にデータが失われる。開発環境での一時データ保存や Pod 内のコンテナ間でのファイル共有に使用。 |
| コンフィグマップ ( ConfigMap ) | ConfigMap | Kubernetes リソース。設定データをキー・バリューペアで保存し, 非機密情報を管理。 |
| シークレット ( Secret ) | Secret | Kubernetes リソース。パスワード, API キー, 証明書などの機密データを暗号化して安全に保存・管理。 |
| 仮想クラスタ ( Virtual Cluster ) | Virtual Cluster | Kubernetes API を仮想化して提供する論理的な Kubernetes クラスタ。各テナントに独立した専用クラスタとして見える環境を提供する。 |
| スーパークラスタ ( Super Cluster ) | Super Cluster | 仮想クラスタ ( Virtual Cluster ) を動作させるホスト側の物理 Kubernetes クラスタ。実際のノードリソースを提供する。 |
| Kubernetesのデプロイメント | - | Kubernetes を用いて, アプリケーションプロセスやリソースを配置, 展開, 管理するための操作を意味する。Kubernetes の配置・管理における最小実行単位は, ポッド ( Pod ) となる。 |
| テナント ( Tenant ) | テナント | 互いに独立した Kubernetes コントロールプレーンを持つ論理的な利用者またはチーム。各テナントについて, 専用の仮想クラスタ ( Virtual Cluster ) が割り当てられ, テナントに割り当てられた仮想クラスタ ( Virtual Cluster ) 内のリソース (名前空間, CRD) を他のテナントに影響を与えずに作成できる。物理リソース (ノード) をスーパークラスタ (Super Cluster) を通じて他のテナントと共有し, かつ, 仮想リソース (Kubernetes のリソース) は, Kubernetes のコントロールプレーンレベルで分離される。 |
| VirtualClusterCRD | VirtualCluster | テナント用仮想クラスタ ( Virtual Cluster ) の設定を定義するリソース型(CRD)。 |
| ClusterVersionCRD | ClusterVersion | 仮想クラスタ ( Virtual Cluster ) 内で使用するコンポーネント(etcd, kube-apiserver, kube-controller-manager)のコンテナイメージ情報を定義するリソース型(CRD)。 |
| ClusterVersionインスタンス | - | ClusterVersionCRD リソース型に基づいて作成された実際のリソースオブジェクト(例: `cv-k8s-1-31`)。 |
| VirtualClusterインスタンス | - | VirtualClusterCRD リソース型に基づいて作成された実際のリソースオブジェクト(例: `tenant-alpha`, `tenant-beta`)。 |
| vc-manager | - | 仮想クラスタ ( Virtual Cluster ) の制御コンポーネント。 |
| vc-syncer ( Virtual Cluster Syncer ) | vc-syncer | 仮想クラスタ ( Virtual Cluster ) とスーパークラスタ ( Super Cluster ) の状態を同期するコンポーネント。 |
| vn-agent ( Virtual Node Agent ) | vn-agent | ワーカーノード上で仮想クラスタ ( Virtual Cluster ) の通信を中継するエージェント。 |
| 名前空間 | namespace | Kubernetes におけるリソースのグループ化と分離の仕組み。 |

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
6. **StorageClass の準備**(`prepare-storage.yml`): `vcinstances_etcd_storage_enabled: true` の場合, スーパークラスタ側に StorageClass が存在しない場合は自動作成します。存在する場合はスキップします。
7. **Failed PV のクリーンアップ**(`cleanup-pvs.yml`): `vcinstances_cleanup_failed_pvs: true` の場合, テナント名に一致する Failed 状態の PV を自動削除します。VirtualCluster 再作成時に名前空間が変わることで PV が Failed 状態になる問題を自動的に解決します。
8. **PersistentVolume の準備**(`prepare-pvs.yml`): `vcinstances_etcd_storage_enabled: true` かつ `vcinstances_auto_create_pv: true` の場合, テナント数分の etcd 用 PV を自動作成します。ワーカーノード上にディレクトリを作成し, local-storage タイプの PV を生成します。
9. **ClusterVersionインスタンス生成**(`clusterversion-instances.yml`): `vcinstances_clusterversions` をループ処理し, 各 ClusterVersionインスタンスのマニフェストを生成, 適用します。`name` がない定義は警告を出してスキップします。
10. **VirtualClusterインスタンス生成**(`virtualcluster-instances.yml`): `vcinstances_virtualclusters` をループ処理し, 各 VirtualClusterインスタンスのマニフェストを生成, 適用します。`name` または `clusterVersionName` がない定義は警告を出してスキップします。
11. **検証**(`verify.yml`): 作成された ClusterVersionインスタンス, VirtualClusterインスタンスを `kubectl get` で一覧表示し, ログに出力します。VirtualClusterインスタンスの一覧は `--all-namespaces` で取得します。

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
| `vcinstances_etcd_storage_enabled` | `false` | - | etcd 永続ストレージの有効化を示します。 |
| `vcinstances_etcd_storage_size` | `"10Gi"` | - | etcd PVC のサイズです。 |
| `vcinstances_etcd_storage_class` | `""` | - | etcd PVC が使用する StorageClass 名です。空の場合はデフォルト StorageClass を使用します。 |
| `vcinstances_default_storage_class_name` | `"local-storage"` | - | 自動作成する StorageClass の名前です。 |
| `vcinstances_auto_create_storage_class` | `true` | - | StorageClass が存在しない場合に自動作成するかどうかを示します。 |
| `vcinstances_auto_create_pv` | `true` | - | etcd用PVを自動作成するかどうかを示します。 |
| `vcinstances_pv_base_path` | `"/mnt/etcd-data"` | - | ワーカーノード上のPVベースパスです。 |
| `vcinstances_etcd_replicas` | `1` | - | etcd レプリカ数です(通常変更不要)。 |
| `vcinstances_cleanup_failed_pvs` | `true` | - | Failed状態のPVを自動クリーンアップするかどうかを示します。VirtualCluster再作成時に名前空間が変わることで生じるFailed PVを自動的に削除します。 |
| `k8s_supercluster_kubeconfig_path` | `"/etc/kubernetes/admin.conf"` | - | スーパークラスタの kubeconfig パスです。 |
| `k8s_supercluster_context` | `""` | - | スーパークラスタの kubeconfig コンテキストです。空の場合は現在のコンテキストを使用します。 |

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

| コンポーネント | フォールバック値 | 参照変数 | 既定値 |
| --- | --- | --- | --- |
| etcd | `registry.k8s.io/etcd:<バージョン>.0` | `k8s_etcd_major_minor` | `3.5` |
| kube-apiserver | `registry.k8s.io/kube-apiserver:v<バージョン>.0` | `k8s_major_minor` | `1.31` |
| kube-controller-manager | `registry.k8s.io/kube-controller-manager:v<バージョン>.0` | `k8s_major_minor` | `1.31` |

`k8s_major_minor` と `k8s_etcd_major_minor` は、各リポジトリロール（`repo-deb`, `repo-rpm`）の `defaults/main.yml` でデフォルト値を定義しています。

`vcinstances_auto_detect_supercluster_images: false` の場合, 検出処理は行われないため, ClusterVersionインスタンスの各イメージを明示指定してください。

## 主な処理

- `k8s_vcinstances_enabled` の有効化を確認します。
- CRD 関連の変数と `vc-manager` 名前空間の存在を検証します。
- マニフェスト出力先ディレクトリを作成します。
- kube-system からコントロールプレーン管理コンポーネント（etcd, kube-apiserver, kube-controller-manager）のイメージを検出します(自動検出有効時)。
- **StorageClass の準備** (`prepare-storage.yml`): `vcinstances_etcd_storage_enabled: true` の場合, スーパークラスタ側に StorageClass が存在しない場合は自動作成します。存在する場合はスキップします。
- **Failed PV のクリーンアップ** (`cleanup-pvs.yml`): `vcinstances_cleanup_failed_pvs: true` の場合, テナント名に一致する Failed 状態の PV を自動削除します。VirtualCluster 再作成時に古い Claim を保持した PV が Failed 状態になる問題を自動的に解決します。
- **PersistentVolume の準備** (`prepare-pvs.yml`): `vcinstances_etcd_storage_enabled: true` かつ `vcinstances_auto_create_pv: true` の場合, テナント数分の etcd 用 PV を自動作成します。ワーカーノード上にディレクトリを作成し, local-storage タイプの PV を生成します。
- ClusterVersionインスタンスと VirtualClusterインスタンスのマニフェストを生成, 適用し, 作成完了を待機します。
- ClusterVersionインスタンス, VirtualClusterインスタンスの一覧を出力し, 作成結果を可視化します。

## etcd 永続ストレージ設定

### 概要

本ロールでは, `vcinstances_etcd_storage_enabled: true` に設定することで, 各テナント ( Tenant ) の仮想クラスタ ( Virtual Cluster ) etcd データを スーパークラスタ ( Super Cluster ) の PersistentVolume (PV) に永続化できます。

### StorageClass の自動作成

#### 動作

`vcinstances_etcd_storage_enabled: true` の場合, 本ロールは以下の処理を実行します:

1. **スーパークラスタの StorageClass をチェック**: `kubectl get storageclass` で既存の StorageClass を確認
2. **StorageClass が存在しない場合**: `{{ vcinstances_default_storage_class_name }}` (デフォルト: `local-storage`) という名前の StorageClass を自動作成
3. **StorageClass が存在する場合**: 作成処理をスキップして既存の StorageClass を使用

自動作成される StorageClass の設定:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-storage  # vcinstances_default_storage_class_name で変更可能
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
```

#### 設定変数

| 変数名 | デフォルト値 | 説明 |
| --- | --- | --- |
| `vcinstances_etcd_storage_enabled` | `false` | etcd 永続ストレージを有効化するかどうか。`true` の場合, StorageClass が自動検査/作成され, etcd が PVC を使用するようになります。 |
| `vcinstances_etcd_storage_size` | `"10Gi"` | etcd の PVC サイズ。ClusterVersionインスタンスのテンプレートで使用されます。 |
| `vcinstances_etcd_storage_class` | `""` | etcd の PVC が使用する StorageClass 名。空文字列の場合, スーパークラスタのデフォルト StorageClass が使用されます。 |
| `vcinstances_default_storage_class_name` | `"local-storage"` | 自動作成される StorageClass の名前。既存 StorageClass がない場合のみこの名前で作成されます。 |
| `vcinstances_auto_create_storage_class` | `true` | StorageClass が存在しない場合に自動作成するかどうか (現在は常に `true` で動作します)。 |
| `k8s_supercluster_kubeconfig_path` | `"/etc/kubernetes/admin.conf"` | スーパークラスタの kubeconfig ファイルパス。StorageClass チェック/作成に使用されます。 |
| `k8s_supercluster_context` | `""` | スーパークラスタの kubeconfig コンテキスト。空の場合は現在のコンテキストを使用します。 |

### 設定例

#### 例1: etcd 永続ストレージ有効化 (デフォルト StorageClass 自動作成)

```yaml
# host_vars/k8sctrlplane01.local

k8s_vcinstances_enabled: true

vcinstances_etcd_storage_enabled: true  # 永続ストレージ有効化
# vcinstances_etcd_storage_size と vcinstances_etcd_storage_class は省略可能

vcinstances_clusterversions:
  - name: "cv-k8s-1-31"

vcinstances_virtualclusters:
  - name: "tenant-alpha"
    clusterVersionName: "cv-k8s-1-31"
```

実行すると, 以下の処理が自動実行されます:

1. スーパークラスタの StorageClass をチェック
2. StorageClass が存在しない場合, `local-storage` という名前の StorageClass を作成
3. ClusterVersionインスタンスで `volumeClaimTemplates` が有効化され, etcd が PVC を使用するように設定される

検証方法:

```bash
# スーパークラスタで StorageClass を確認
kubectl get storageclass
# 出力: local-storage が表示されるはず

# クラスタバージョンの etcd が PVC を使用しているか確認
kubectl get clusterversion cv-k8s-1-31 -o yaml | grep -A10 volumeClaimTemplates
```

#### 例2: 整備済み StorageClass を使用

スーパークラスタに既に StorageClass が存在する場合は, 自動作成処理はスキップされ, 既存の StorageClass が使用されます。

```bash
# 事前に StorageClass を確認
kubectl get storageclass
# 出力: fast-ssd が表示される場合

# 上記の例1の設定を実行すると, fast-ssd が使用される (existing storage class が優先)
```

#### 例3: 永続ストレージを無効化 (emptyDir を使用)

```yaml
# host_vars/k8sctrlplane01.local

k8s_vcinstances_enabled: true
vcinstances_etcd_storage_enabled: false  # デフォルト値: 永続ストレージ無効化
```

この場合, etcd は `emptyDir` でマウントされ, Pod の再起動でデータが失われます。開発環境や一時的な検証用途向けです。

### トラブルシューティング

**症状: StorageClass 作成に失敗する**

```bash
# エラーを確認
ansible-playbook k8s-management.yml -t k8s-vc-instances -vv 2>&1 | grep -i storage

# kubeconfig パスを確認
ls -la {{ k8s_supercluster_kubeconfig_path }}  # デフォルト: /etc/kubernetes/admin.conf

# kubeconfig が正しいか検証
kubectl --kubeconfig=/etc/kubernetes/admin.conf get storageclass
```

**症状: 既存 StorageClass が無視されている**

本ロールは既存 StorageClass を優先します。新しい StorageClass を作成させたい場合は, 既存の StorageClass を削除してからロールを実行してください:

```bash
# 既存 StorageClass 削除（データ損失のリスク注意）
kubectl delete storageclass <name>

# ロールを再実行
ansible-playbook k8s-management.yml -t k8s-vc-instances
```

## テンプレートと生成ファイル

| テンプレート | 出力先 | 説明 |
| --- | --- | --- |
| `templates/clusterversion-instance.yaml.j2` | `{{ vcinstances_config_dir }}/clusterversion-<name>.yaml` | ClusterVersionインスタンスマニフェストです。 |
| `templates/virtualcluster-instance.yaml.j2` | `{{ vcinstances_config_dir }}/virtualcluster-<name>.yaml` | VirtualClusterインスタンスマニフェストです。 |

## 生成されるリソース

| リソース種別 | リソース名(例) | 説明 |
| --- | --- | --- |
| ClusterVersionインスタンス | `cv-k8s-1-31` | ClusterVersionCRD リソース型に基づいて生成されるインスタンス。仮想クラスタ ( Virtual Cluster ) 内で使用するコントロールプレーン ( Control Plane ) コンポーネント(etcd, kube-apiserver, kube-controller-manager)のコンテナイメージ情報を定義します。 |
| VirtualClusterインスタンス | `tenant-alpha`, `tenant-beta` | VirtualClusterCRD リソース型に基づいて生成されるインスタンス。テナント ( Tenant ) に割り当てられた仮想クラスタ ( Virtual Cluster ) の設定を定義します。 |

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

### 8. 永続ストレージ有効時の確認 (vcinstances_etcd_storage_enabled: true)

#### 1. StorageClass の確認

```bash
kubectl get storageclass
```

**期待される出力例**:
```
NAME            PROVISIONER                    RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
default-sc      kubernetes.io/no-provisioner   Delete          WaitForFirstConsumer   false                  133m
local-storage   kubernetes.io/no-provisioner   Delete          WaitForFirstConsumer   false                  154m
```

#### 2. etcd PVC の確認 (Bound になっていること)

```bash
kubectl get pvc -A | grep etcd
```

**期待される出力例**:
```
vc-manager-c55f6e-tenant-alpha   data-etcd-0   Bound    pv-etcd-tenant-alpha-0   10Gi       RWO            default-sc     <unset>                 85m
vc-manager-cb204f-tenant-beta    data-etcd-0   Bound    pv-etcd-tenant-beta-1    10Gi       RWO            default-sc     <unset>                 85m
```

#### 3. テナント Pod の確認 (etcd-0, apiserver-0, controller-manager-0 が Running)

```bash
kubectl get pods -A | grep tenant
```

**期待される出力例**:
```
vc-manager-c55f6e-tenant-alpha   apiserver-0                                                1/1     Running            0                85m
vc-manager-c55f6e-tenant-alpha   controller-manager-0                                       1/1     Running            0                85m
vc-manager-c55f6e-tenant-alpha   etcd-0                                                     1/1     Running            0                85m
vc-manager-cb204f-tenant-beta    apiserver-0                                                1/1     Running            0                85m
vc-manager-cb204f-tenant-beta    controller-manager-0                                       1/1     Running            0                85m
vc-manager-cb204f-tenant-beta    etcd-0                                                     1/1     Running            0                85m
```

#### 4. PV の確認 (PVC と Bound していること)

```bash
kubectl get pv
```

**期待される出力例**:
```
NAME                     CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                                        STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
pv-etcd-tenant-alpha-0   10Gi       RWO            Delete           Bound    vc-manager-c55f6e-tenant-alpha/data-etcd-0   default-sc     <unset>                          85m
pv-etcd-tenant-beta-1    10Gi       RWO            Delete           Bound    vc-manager-cb204f-tenant-beta/data-etcd-0    default-sc     <unset>                          85m
```

**確認ポイント**:
- `vcinstances_etcd_storage_class` で指定した StorageClass 名で PVC が作成されていること。
- 各テナントの `data-etcd-0` が `Bound` であること。
- 各テナントの `etcd-0` が `Running` であること。
- `pv-etcd-<tenant>-<index>` 形式の PV が作成され, 対応PVCに `Bound` していること。

### 9. イベントの確認

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

#### 原因 4: local-storage 用 PV が不足している

**症状**:
- `kubectl get pvc -A | grep etcd` で `Pending` のままになる。
- `kubectl describe pod etcd-0 -n <tenant-namespace>` に `didn't find available persistent volumes to bind` が出る。

**確認コマンド**:
```bash
kubectl get pv
kubectl get pvc -A | grep etcd
kubectl describe pod etcd-0 -n <tenant-namespace>
```

**解決方法**:
- `vcinstances_auto_create_pv: true` を有効にして本ロールを再実行してください。
- `vcinstances_etcd_storage_class` と PV の `storageClassName` が一致していることを確認してください。

#### 原因 5: PV が Failed 状態で古い Claim を保持している

**症状**:
- PVC が `Pending` 状態のまま。
- `kubectl get pv` で PV が `Failed` 状態になっている。
- PV の CLAIM が現在の名前空間と一致しない（例: PV が `vc-manager-c55f6e-tenant-alpha/data-etcd-0` を参照しているが, 実際の PVC は `vc-manager-476dc1-tenant-alpha` 名前空間にある）。

**原因**:
VirtualCluster が再作成されると名前空間のサフィックス（ハッシュ値）が変わりますが, 既存の PV は古い Claim 情報を保持し続けるため, バインドできなくなります。

**確認コマンド**:
```bash
# PV の状態と Claim を確認
kubectl get pv -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,CLAIM:.spec.claimRef.name,NAMESPACE:.spec.claimRef.namespace

# 現在の PVC の名前空間を確認
kubectl get pvc -A | grep etcd
```

**自動解決**:
このロールでは, `vcinstances_cleanup_failed_pvs: true`（デフォルト）の場合, PV作成前に自動的にFailed状態のPVをクリーンアップします。通常は手動対応は不要です。

**手動解決方法**（自動クリーンアップが無効の場合）:
1. Failed 状態の古い PV を削除:
   ```bash
   kubectl delete pv pv-etcd-tenant-alpha-0 pv-etcd-tenant-beta-1
   ```

2. 本ロールを再実行して新しい PV を作成:
   ```bash
   ansible-playbook -i inventory/hosts k8s-management.yml -t k8s-vc-instances
   ```

3. PVC が Bound になることを確認:
   ```bash
   kubectl get pvc -A | grep etcd
   ```

**クリーンアップの無効化**（通常は非推奨）:
```yaml
# host_vars/k8sctrlplane01.local
vcinstances_cleanup_failed_pvs: false  # 自動クリーンアップを無効化
```

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

## クリーンアップ/再構築

### VirtualCluster の完全な再構築

VirtualCluster を完全に削除して再構築する場合, 以下の手順で実行してください。

#### 1. VirtualCluster インスタンスの削除

```bash
# 全 VirtualCluster インスタンスを削除
kubectl delete virtualclusters --all -n vc-manager

# 特定の VirtualCluster インスタンスのみ削除
kubectl delete virtualcluster tenant-alpha -n vc-manager
kubectl delete virtualcluster tenant-beta -n vc-manager
```

VirtualCluster インスタンスを削除すると, 対応するテナント名前空間（`vc-manager-<hash>-<tenant>`）と PVC も自動的に削除されます。

#### 2. PV の削除（永続ストレージ有効時）

`vcinstances_etcd_storage_enabled: true` の場合, PV は自動削除されないため手動で削除する必要があります。

```bash
# 全 etcd 用 PV を削除
kubectl delete pv -l app=virtualcluster-etcd

# または個別に削除
kubectl delete pv pv-etcd-tenant-alpha-0 pv-etcd-tenant-beta-1
```

**注意**: PV を削除すると, etcd データも完全に失われます。必要に応じて事前にバックアップを取得してください。

#### 3. ClusterVersion インスタンスの削除（必要に応じて）

```bash
# 全 ClusterVersion インスタンスを削除
kubectl delete clusterversions --all

# 特定の ClusterVersion インスタンスのみ削除
kubectl delete clusterversion cv-k8s-1-31
```

#### 4. ワーカーノード上の PV データディレクトリ削除（必要に応じて）

ローカルストレージを使用している場合, ワーカーノード上のデータディレクトリも削除してください。

```bash
# 各ワーカーノードで実行
sudo rm -rf /mnt/etcd-data/tenant-*
```

#### 5. ロールを再実行

```bash
ansible-playbook -i inventory/hosts k8s-management.yml -t k8s-vc-instances
```

### 部分的なクリーンアップ

特定のテナントのみを再作成する場合:

```bash
# 1. 対象の VirtualCluster インスタンスを削除
kubectl delete virtualcluster tenant-alpha -n vc-manager

# 2. 対象の PV を削除（永続ストレージ有効時）
kubectl delete pv pv-etcd-tenant-alpha-0

# 3. ロールを再実行（全体を実行すると他のテナントも再作成されるため注意）
ansible-playbook -i inventory/hosts k8s-management.yml -t k8s-vc-instances
```

### クリーンアップの自動化

以下のコマンドで一括削除できます:

```bash
# VirtualCluster と ClusterVersion を全削除
kubectl delete virtualclusters --all -n vc-manager
kubectl delete clusterversions --all

# etcd 用 PV を全削除
kubectl get pv | grep etcd | awk '{print $1}' | xargs kubectl delete pv

# または label がある場合
kubectl delete pv -l app=virtualcluster-etcd
```

## 参考リンク

- [VirtualCluster - Enabling Kubernetes Hard Multi-tenancy](https://github.com/kubernetes-retired/cluster-api-provider-nested/tree/main/virtualcluster)
