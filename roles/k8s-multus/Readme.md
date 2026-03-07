# k8s-multus ロール

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
| 名前空間 ( namespace )  | - | Kubernetes内部でリソースを論理的に分離する単位。 |
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

## 概要

### ロールの目的

本ロールは Kubernetes コントロールプレーンノード上に Multus CNI を導入します。Multus は複数の CNI プラグインを同時に使用可能にするメタ CNI プラグインで, Pod に複数のネットワークインターフェースをアタッチできるようにします。

`k8s-common` および `k8s-ctrlplane` で構築された Kubernetes クラスタに対して, Multus を追加導入することで, Cilium (プライマリ CNI) に加えて追加のネットワークインターフェース (ipvlan, macvlan, bridge 等) を Pod にアタッチ可能になります。

### 前提ロール

本ロールは以下のロールが実行済みであることを前提とします:

- `k8s-common`: Kubernetes クラスタの基本設定
- `k8s-ctrlplane`: コントロールプレーンノードの構築 (Cilium CNI 導入済み)

### 基本仕様

- **デフォルト導入方式**: Helm Chart (推奨)
- **代替導入方式**: kubectl apply (後方互換性のため提供)
- **Multus タイプ**: thin インストール (軽量版, 既定)
- **配置対象**: すべての Kubernetes ノード (DaemonSet)
- **再実行対応**: 可 (冪等性を保証)

### 実装方針

本ロールでは Multus の導入に2つの方式を提供しています:

1. **Helm 方式 (推奨, 既定)**: ローカル Helm Chart (`files/multus-chart/`) を使用し, values をカスタマイズして導入します。バージョン管理と設定の一元管理が容易です。
2. **kubectl apply 方式**: 公式マニフェストを直接適用します。既存環境との互換性維持や, 簡易的な導入に使用できます。

Helm 方式から kubectl apply 方式への切り替え, またはその逆の切り替え時には, `k8s_multus_cleanup_resources: true` を設定することで既存リソースをクリーンアップしてから再導入できます。

## 前提条件

本ロールを実行する前に, 以下の条件が満たされている必要があります:

- **対象ノード**: Kubernetes コントロールプレーンノード (`k8s-ctrlplane` ロール実行済み)
- **Kubernetes バージョン**: 1.24 以降 (kubeadm で構築されたクラスタ)
- **プライマリ CNI**: Cilium が導入済みであること
- **必要なツール**:
  - kubectl: Kubernetes クラスタ操作用 (/usr/local/bin/kubectl)
  - helm: Helm Chart 導入用 (Helm 方式使用時, 既定で有効)
- **kube-apiserver**: 稼働中で応答可能であること
- **管理者権限**: kubectl 実行に /etc/kubernetes/admin.conf を使用するため root 権限が必要 (sudoコマンドによるコマンド実行が可能であることが必要)
- **ネットワーク接続**: コンテナイメージ取得のためのインターネット接続 (または内部レジストリへの接続)

## 実行フロー

本ロールは以下の手順で Multus CNI を導入します:

1. **パラメータ読み込み** (`load-params.yml`): `vars/config.yml` から設定を読み込みます (現在は placeholder のみ)。
2. **パッケージインストール** (`package.yml`): 必要なパッケージをインストールします (現在は処理なし, 将来の拡張用)。
3. **ディレクトリ作成** (`directory.yml`): Multus 用の設定ディレクトリを作成します。
4. **ユーザ/グループ作成** (`user_group.yml`): オペレータユーザ (k8s_multus_operator) の設定を行います (既定では作成しない)。
5. **サービス設定** (`service.yml`): Multus 関連サービスの設定を行います (現在は処理なし, 将来の拡張用)。
6. **既存リソースのクリーンアップ** (`config-cleanup-multus.yml`): `k8s_multus_cleanup_resources: true` の場合, 既存の Multus リソース (DaemonSet, ClusterRole, ClusterRoleBinding, ServiceAccount, ConfigMap, CRD) を削除します。導入方式の切り替え時に使用します。
7. **Multus 導入 (Helm 方式)** (`config-multus.yml`): `k8s_multus_use_helm: true` (既定) の場合, 以下の手順で Helm Chart を使用して Multus を導入します:
   - **kube-apiserver 応答待機**: `wait_for` モジュールで kube-apiserver (https://{{ k8s_multus_k8s_api_endpoint_address }}:{{ k8s_multus_k8s_api_endpoint_port }}) が応答可能になるまで最大 {{ k8s_multus_k8s_api_wait_time }} 秒待機します。
   - **Helm Chart コピー**: `files/multus-chart/` をターゲットホストへコピーします。
   - **Helm values 生成**: `templates/multus-values.yml.j2` から values ファイルを生成します。
   - **Helm インストール/アップグレード**: `helm upgrade --install` コマンドで Multus をデプロイします。
8. **Multus 導入 (kubectl apply 方式)** (`config-kubectl-applied-multus.yml`): `k8s_multus_use_helm: false` の場合, 公式マニフェスト ({{ k8s_multus_manifest_thin_install_url }}) を `kubectl apply` で適用します。
9. **テストポッド用マニフェスト配置** (`test-pod-manifest.yml`): Multus 動作確認用のテストポッド定義 (`templates/app-pod.yml.j2`) を `/tmp/multus-test-app-pod.yml` に配置します。

## 導入方式

本ロールでは Multus の導入に2つの方式を提供しています。既定では **Helm 方式** を使用します。

### Helm 方式 (推奨, 既定)

**メリット**:

- バージョン管理が容易 (Helm Release として管理される)
- values ファイルでの設定変更が簡単
- アップグレード, ロールバックが容易

**使用方法**:

```yaml
k8s_multus_use_helm: true  # 既定値
```

**確認方法**:

```bash
sudo kubectl get daemonset -n kube-system
helm list -n kube-system
```

### kubectl apply 方式

**メリット**:

- 既存環境との互換性維持
- Helm 不要 (kubectl のみで導入可能)
- シンプルな導入手順

**使用方法**:

```yaml
k8s_multus_use_helm: false
```

**確認方法**:

```bash
sudo kubectl get daemonset -n kube-system
```

### 導入方式の切り替え

Helm 方式から kubectl apply 方式, またはその逆に切り替える場合は, 既存リソースをクリーンアップしてから再導入します:

```yaml
k8s_multus_cleanup_resources: true  # 既存リソースを削除
k8s_multus_use_helm: true  # または false
```

## 主要変数

### 基本設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_multus_enabled` | `true` | Multus 導入を有効化するかどうか。`false` にするとロール全体をスキップします。 |
| `k8s_multus_cleanup_resources` | `false` | 既存の Multus リソースを削除するかどうか。導入方式の切り替え時に使用します。 |
| `k8s_multus_install_test_pod_manifest` | `true` | テストポッド用マニフェストを配置するかどうか。 |

### Helm 設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_multus_use_helm` | `true` | Helm Chart を使用して Multus を導入するかどうか。`false` にすると kubectl apply 方式に切り替わります。 |
| `k8s_multus_helm_release_name` | `"multus"` | Helm Release の名前。 |
| `k8s_multus_helm_namespace` | `"kube-system"` | Helm Release をデプロイする名前空間。 |
| `k8s_multus_helm_chart_path` | `"/tmp/multus-chart"` | ターゲットホストにコピーする Helm Chart のパス。 |
| `k8s_multus_helm_values_path` | `"/tmp/multus-values.yml"` | 生成した Helm values ファイルのパス。 |

### コンテナイメージ設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_multus_image_repository` | `"ghcr.io/k8snetworkplumbingwg/multus-cni"` | Multus コンテナイメージのリポジトリ。 |
| `k8s_multus_image_tag` | `"v4.2.3"` | Multus コンテナイメージのタグ。 |

### CNI 設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_multus_cni_bin_dir` | `"/opt/cni/bin"` | CNI プラグインバイナリの配置ディレクトリ。 |
| `k8s_multus_cni_conf_dir` | `"/etc/cni/net.d"` | CNI 設定ファイルの配置ディレクトリ。 |

### kubectl apply 設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_multus_manifest_thin_install_url` | `"https://raw.githubusercontent.com/k8snetworkplumbingwg/multus-cni/v4.2.3/deployments/multus-daemonset-thin.yml"` | kubectl apply 方式で使用する公式マニフェストの URL (thin インストール版)。 |

### API 待機設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_multus_k8s_api_wait_time` | `300` | kube-apiserver の応答を待機する最大秒数。 |

### オペレータユーザ設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_multus_operator` | `""` | Multus 操作用のユーザ名。空文字列の場合は作成しません (既定)。 |
| `k8s_multus_operator_group` | `""` | Multus 操作用のグループ名。空文字列の場合は作成しません (既定)。 |

### 共通変数参照

以下の変数は `k8s-common` ロールや `group_vars/all/all.yml` で定義されている共通変数を参照します:

- `k8s_multus_k8s_api_endpoint_address`: kube-apiserver のエンドポイントアドレス (既定: `{{ k8s_api_endpoint_address }}`)
- `k8s_multus_k8s_api_endpoint_port`: kube-apiserver のエンドポイントポート (既定: `{{ k8s_api_endpoint_port }}`)

## テンプレート, ファイル

本ロールで使用する主要なテンプレートとファイルは以下の通りです:

| ファイル名 | 種別 | 説明 |
| --- | --- | --- |
| `templates/multus-values.yml.j2` | Jinja2 テンプレート | Helm Chart 用の values ファイルを生成するテンプレート。 |
| `templates/app-pod.yml.j2` | Jinja2 テンプレート | Multus 動作確認用のテストポッド定義。secondary ネットワークインターフェースとして ipvlan を使用する例を含みます。 |
| `files/multus-chart/` | Helm Chart | ローカル Helm Chart ディレクトリ。公式 Multus Chart を元にカスタマイズしたものです。 |

### Helm Chart 構成

`files/multus-chart/` には以下のファイルが含まれています:

| ファイル名 | 説明 |
| --- | --- |
| `Chart.yaml` | Helm Chart のメタデータ (name: multus-cni, version: 4.2.3, appVersion: v4.2.3)。 |
| `values.yaml` | Helm Chart の既定値。namespace, image, serviceAccount, CNI パス, リソース制限等を定義します。 |
| `templates/daemonset.yaml` | Multus DaemonSet の定義。各ノードで Multus コンテナを起動します。 |
| `templates/serviceaccount.yaml` | Multus 用 ServiceAccount の定義。 |
| `templates/clusterrole.yaml` | Multus 用 ClusterRole の定義 (CRD, Pod, NetworkAttachmentDefinition 等へのアクセス権)。 |
| `templates/clusterrolebinding.yaml` | ClusterRole を ServiceAccount に紐付ける ClusterRoleBinding の定義。 |
| `templates/configmap.yaml` | Multus 用 ConfigMap の定義 (CNI 設定等)。 |
| `templates/crd.yaml` | NetworkAttachmentDefinition CRD の定義。 |
| `templates/_helpers.tpl` | Helm テンプレートヘルパー関数。 |

**使用方法**:

1. ロール実行時に `files/multus-chart/` がターゲットホストの `/tmp/multus-chart/` にコピーされます。
2. `templates/multus-values.yml.j2` から `/tmp/multus-values.yml` が生成されます。
3. `helm upgrade --install multus /tmp/multus-chart/ --namespace kube-system --values /tmp/multus-values.yml` でデプロイされます。

**カスタマイズポイント**:

- `templates/multus-values.yml.j2`: コンテナイメージ, CNI パス, ServiceAccount 名等を変更できます。
- `files/multus-chart/values.yaml`: Helm Chart 側の既定値を変更したい場合はこちらを編集します。
- `files/multus-chart/templates/`: リソース定義自体をカスタマイズしたい場合はこちらを編集します。

## 検証ポイント

Multus CNI が正常に導入されたことを確認するため, 以下の手順で段階的に検証します。

### 1. kube-apiserver の応答確認

```bash
sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf cluster-info
```

**期待される結果**:

```
Kubernetes control plane is running at https://[fdad:ba50:248b:1::41]:6443
CoreDNS is running at https://[fdad:ba50:248b:1::41]:6443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

**確認ポイント**:

- `Kubernetes control plane is running` が表示され, kube-apiserver が正常に応答していること
- API エンドポイントのアドレスとポート番号が正しく表示されること (IPv4 または IPv6)

### 2. Multus DaemonSet の起動確認

```bash
sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf get daemonset -n kube-system
```

**期待される結果**:

```
NAME             DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR   AGE
kube-multus-ds   3         3         3       3            3           <none>          21h
```

多数のDaemonSetが表示される場合は、その中に `kube-multus-ds` が含まれていることを確認します。

全ノードで Multus Pod が `READY` 状態であることを確認します:

```bash
sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf get pods -n kube-system -l app=multus
```

**期待される結果**:

```
NAME                   READY   STATUS    RESTARTS      AGE
kube-multus-ds-5jn8r   1/1     Running   2 (21h ago)   21h
kube-multus-ds-c2wbk   1/1     Running   0             20h
kube-multus-ds-cdd95   1/1     Running   3 (20h ago)   20h
```

**確認ポイント**:

- DaemonSet 出力で `DESIRED`, `CURRENT`, `READY`, `UP-TO-DATE`, `AVAILABLE` の値がすべて一致していること (クラスタ内の全ノード数と同じ)
- Pod 一覧で各 Pod の `READY` 列が `1/1` となっていること (コンテナが正常に起動している)
- `STATUS` 列が `Running` となっていること (Pod が稼働中)
- `RESTARTS` は再起動回数を示します (0 が理想的ですが, ノード再起動等で増加することがあります)

### 3. Helm Release の確認 (Helm 方式使用時)

```bash
helm list -n kube-system
```

**期待される結果**:

```
NAME        NAMESPACE    REVISION  UPDATED                                 STATUS    CHART             APP VERSION
multus-cni  kube-system  1         2026-03-06 02:17:20.715233566 +0900 JST deployed  multus-cni-4.2.3  v4.2.3
```

**確認ポイント**:

- `NAME` 列に `multus-cni` (または設定した Helm Release 名) が表示されること
- `STATUS` 列が `deployed` となっていること (正常にデプロイ済み)
- `CHART` 列が `multus-cni-4.2.3` (使用した Chart バージョン) と一致すること
- `APP VERSION` 列が `v4.2.3` (Multus のバージョン) と一致すること

### 4. NetworkAttachmentDefinition CRD の確認

```bash
sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf get crd network-attachment-definitions.k8s.cni.cncf.io
```

**期待される結果**:

```
NAME                                             CREATED AT
network-attachment-definitions.k8s.cni.cncf.io   2026-03-05T17:17:20Z
```

**確認ポイント**:

- `network-attachment-definitions.k8s.cni.cncf.io` という名前の CRD が存在すること
- この CRD により, NetworkAttachmentDefinition リソースを作成してセカンダリネットワークを定義できるようになります

### 5. RBAC リソースの確認

```bash
sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf get clusterrole multus
sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf get clusterrolebinding multus
sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf get serviceaccount -n kube-system multus
```

**期待される結果**:

ClusterRole:
```
NAME     CREATED AT
multus   2026-03-05T17:17:20Z
```

ClusterRoleBinding:
```
NAME     ROLE                AGE
multus   ClusterRole/multus  21h
```

ServiceAccount:
```
NAME     SECRETS   AGE
multus   0         21h
```

**確認ポイント**:

- `multus` という名前の ClusterRole が存在すること (Multus が必要なリソースへのアクセス権限を定義)
- `multus` という名前の ClusterRoleBinding が存在し, ClusterRole を ServiceAccount に紐付けていること
- `multus` という名前の ServiceAccount が kube-system 名前空間に存在すること (Multus Pod が使用)

### 6. CNI 設定ファイルの確認

各ノードで CNI 設定ディレクトリを確認します:

```bash
sudo ls -l /etc/cni/net.d/
```

**期待される結果**:

Multus の設定ファイル (`00-multus.conf` または `multus.d/multus.kubeconfig`) が配置されていることを確認します。

**確認ポイント**:

- `/etc/cni/net.d/` ディレクトリ内に Multus 関連の設定ファイルが存在すること
- `00-` で始まるファイル名の場合, CNI プラグインの実行順序で最初に呼び出されます (Multus がメタ CNI として機能するため)
- `multus.d/` ディレクトリが存在する場合, その中に `multus.kubeconfig` が配置されていること

### 7. Multus 動作確認 (テストポッド起動)

テストポッド用マニフェスト (`/tmp/multus-test-app-pod.yml`) を使用して, Multus が正常に secondary ネットワークインターフェースをアタッチできることを確認します:

```bash
sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf apply -f /tmp/multus-test-app-pod.yml
sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf wait --for=condition=ready pod/demo-net1 --timeout=60s
```

**Pod 内のネットワークインターフェース確認**:

```bash
sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf exec demo-net1 -- ip addr show
```

**期待される結果**:

`eth0` (プライマリインターフェース, Cilium) に加えて, `net1` (セカンダリインターフェース, ipvlan) が表示されることを確認します:

```
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
2: net1@net1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue
    link/ether 00:50:56:00:bf:1d brd ff:ff:ff:ff:ff:ff
    inet 192.168.20.50/24 brd 192.168.20.255 scope global net1
       valid_lft forever preferred_lft forever
18: eth0@if19: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue qlen 1000
    link/ether 62:eb:6d:4d:1c:ab brd ff:ff:ff:ff:ff:ff
    inet 10.244.2.43/32 scope global eth0
       valid_lft forever preferred_lft forever
```

**確認ポイント**:

- `lo`: ループバックインターフェース (常に存在)
  - `inet 127.0.0.1/8` が表示されていること
- `net1`: セカンダリネットワークインターフェース (Multus が NetworkAttachmentDefinition に基づいてアタッチ)
  - インターフェース名は NetworkAttachmentDefinition の設定により変わります (net1, net2, ... など)
  - `<BROADCAST,MULTICAST,UP,LOWER_UP>` のフラグが表示されていること
  - IP アドレスが割り当てられていること (上記例では `192.168.20.50/24`)
  - ブロードキャストアドレスが表示されていること (上記例では `192.168.20.255`)
- `eth0`: プライマリネットワークインターフェース (Cilium が管理, Pod 間通信や Service 通信に使用)
  - `<BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN>` のフラグが表示されていること
  - IP アドレスが割り当てられていること (通常は /32, 上記例では `10.244.2.43/32`)
  - インターフェース番号は環境により変わります (上記例では 18)

**ルーティング確認**:

```bash
sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf exec demo-net1 -- ip route show
```

**期待される結果**:

プライマリインターフェース (`eth0`) がデフォルトゲートウェイとして設定され, セカンダリインターフェース (`net1`) 用のルートが追加されていることを確認します:

```
default via 10.244.2.168 dev eth0
10.244.2.168 dev eth0 scope link
192.168.20.0/24 dev net1 scope link  src 192.168.20.50
```

**確認ポイント**:

- `default via ...` のルートが `eth0` 経由で設定されていること (デフォルトゲートウェイ, Cilium 管理のプライマリネットワーク, 上記例では `10.244.2.168`)
- Cilium ゲートウェイへの直接ルート (`10.244.2.168 dev eth0 scope link`) が存在すること
- セカンダリネットワーク用のルートが `net1` 経由で設定されていること (上記例では `192.168.20.0/24 dev net1 scope link src 192.168.20.50`)
- セカンダリネットワークのルートに送信元IP (`src`) が指定されていること (これにより通信経路の安定化が図られる)

**テストポッド削除**:

確認後はテストポッドを削除します:

```bash
sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf delete -f /tmp/multus-test-app-pod.yml
```

### 8. Multus ログの確認

問題が発生した場合は, Multus Pod のログを確認します:

```bash
sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf logs -n kube-system -l app=multus --tail=50
```

## トラブルシューティング

### 1. Multus DaemonSet が起動しない

**症状**:

- `kubectl get daemonset -n kube-system` で `kube-multus-ds` の `DESIRED` と `READY` が一致しない
- `kubectl get pods -n kube-system -l app=multus` で Pod が `CrashLoopBackOff` や `ImagePullBackOff` 状態

**原因**:

- コンテナイメージが取得できない (ネットワーク接続, レジストリアクセス権限)
- CNI バイナリディレクトリ (`/opt/cni/bin`) または CNI 設定ディレクトリ (`/etc/cni/net.d`) が存在しない
- RBAC 権限不足

**対処方法**:

1. コンテナイメージのプルエラーを確認: `sudo kubectl describe pod -n kube-system <POD_NAME>`
2. ノード上で CNI ディレクトリの存在を確認: `sudo ls -ld /opt/cni/bin /etc/cni/net.d`
3. ServiceAccount, ClusterRole, ClusterRoleBinding の存在を確認: `sudo kubectl get sa,clusterrole,clusterrolebinding | grep multus`

### 2. NetworkAttachmentDefinition (NAD) が認識されない

**症状**:

- `kubectl get network-attachment-definitions` でエラーが発生する
- Pod に Annotation でセカンダリネットワークを指定してもアタッチされない

**原因**:

- NetworkAttachmentDefinition CRD が登録されていない
- NAD リソース自体が作成されていない

**対処方法**:

1. CRD の存在を確認: `sudo kubectl get crd | grep network-attachment-definitions`
2. CRD が存在しない場合は, Helm 導入または kubectl apply 導入が正常に完了していない可能性があります。ロールを再実行するか, `k8s_multus_cleanup_resources: true` で既存リソースをクリーンアップしてから再導入します。
3. NAD リソースの作成は **別ロール** (例: `k8s-whereabouts`) で行います。本ロールでは NAD 自体の作成は行いません。

### 3. Pod にセカンダリネットワークインターフェースがアタッチされない

**症状**:

- Pod 内で `ip addr show` を実行しても `net1` 等のセカンダリインターフェースが表示されない
- Pod に NAD を指定する Annotation (`k8s.v1.cni.cncf.io/networks`) を付与しているが反映されない

**原因**:

- Annotation の記述ミス (名前空間の省略, NAD 名の誤り)
- NAD リソースが存在しない, または不正な CNI 設定が含まれている
- Multus が thin モードで動作しているが, 参照先の CNI プラグインバイナリが存在しない

**対処方法**:

1. Annotation の記述を確認: `sudo kubectl get pod <POD_NAME> -o jsonpath='{.metadata.annotations}'`
   - 正しい形式: `k8s.v1.cni.cncf.io/networks: <NAMESPACE>/<NAD_NAME>` または `k8s.v1.cni.cncf.io/networks: <NAD_NAME>` (同一名前空間の場合)
2. NAD の存在と内容を確認: `sudo kubectl get network-attachment-definitions -n <NAMESPACE> <NAD_NAME> -o yaml`
3. CNI プラグインバイナリの存在を確認 (thin モードの場合): `sudo ls -l /opt/cni/bin/` で必要なプラグイン (ipvlan, macvlan, bridge 等) が存在するか確認
4. Multus Pod のログを確認: `sudo kubectl logs -n kube-system -l app=multus`

### 4. Helm Release が失敗する

**症状**:

- `helm upgrade --install` コマンドがエラーを返す
- `helm list -n kube-system` で Multus Release が `failed` 状態

**原因**:

- Helm Chart の構文エラー
- values ファイルの記述ミス
- kube-apiserver への接続失敗

**対処方法**:

1. Helm Release の状態を確認: `helm list -n kube-system | grep multus`
2. Release の詳細を確認: `helm get all multus -n kube-system`
3. values ファイルの内容を確認: `cat /tmp/multus-values.yml`
4. kube-apiserver の応答を確認: `sudo kubectl cluster-info`
5. Helm を使用せず kubectl apply 方式に切り替える: `k8s_multus_use_helm: false`

### 5. kube-apiserver に接続できない

**症状**:

- `wait_for` タスクでタイムアウトが発生する
- `kubectl` コマンドが `connection refused` または `timed out` エラーを返す

**原因**:

- kube-apiserver が起動していない
- ファイアウォールやネットワーク設定で API エンドポイントへの接続がブロックされている
- `/etc/kubernetes/admin.conf` のエンドポイント設定が誤っている

**対処方法**:

1. kube-apiserver プロセスの起動を確認: `systemctl status kubelet` (コントロールプレーンノード)
2. エンドポイントへの接続を確認: `curl -k https://<API_ENDPOINT>:6443/healthz`
3. ファイアウォール設定を確認: `sudo iptables -L -n | grep 6443` または `sudo firewall-cmd --list-all`
4. `k8s_multus_k8s_api_wait_time` を増やして再実行

## 補足

### thin インストールと thick インストール

Multus には2つのインストールモードがあります:

- **thin インストール** (既定): Multus 自身は最小限の機能のみを持ち, 実際の CNI プラグイン (ipvlan, macvlan, bridge 等) は別途ノード上に配置されている必要があります。本ロールでは thin インストールを使用します。
- **thick インストール**: Multus コンテナ内に主要な CNI プラグインバイナリをバンドルし, ノード上に CNI プラグインが存在しなくても動作可能にします。

thin インストールを使用する場合は, 各ノードの `/opt/cni/bin/` に必要な CNI プラグインバイナリが配置されていることを確認してください (通常は containerd や kubelet のインストール時に配置されます)。

### Cilium との共存

本ロールでは Cilium をプライマリ CNI として使用し, Multus をメタ CNI として併用します。この構成では:

- **eth0** (プライマリインターフェース): Cilium が管理し, Pod 間通信, Service 通信, NetworkPolicy 等に使用されます。
- **net1, net2, ...** (セカンダリインターフェース): Multus が NetworkAttachmentDefinition (NAD) で定義された CNI プラグイン (ipvlan, macvlan, bridge 等) を呼び出してアタッチします。

セカンダリネットワークインターフェースは通常, レガシーアプリケーションの L2 通信要件, マルチテナント環境でのネットワーク分離, 専用ネットワークへの直接接続等に使用されます。

### NetworkAttachmentDefinition (NAD) の使用

NAD の作成と使用方法については, 以下のロールを参照してください:

- `k8s-whereabouts`: Multus 用の IPAM (IP Address Management) プラグインである Whereabouts と NAD の導入例が記載されています。

NAD を定義することで, Pod に対して以下のような Annotation を付与してセカンダリネットワークインターフェースをアタッチできます:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: example-pod
  annotations:
    k8s.v1.cni.cncf.io/networks: <NAMESPACE>/<NAD_NAME>
spec:
  containers:
  - name: example-container
    image: busybox
```

### セカンダリネットワークのルーティング

`templates/app-pod.yml.j2` のコメントに記載されている通り, セカンダリネットワークインターフェース経由で通信を行う場合は, 送信元 IP アドレス (`src`) を明示的に指定することで通信経路を安定化できます:

```bash
ip route add <DESTINATION_NETWORK> via <GATEWAY> dev net1 src <NET1_IP>
```

この設定により, カーネルが送信元 IP アドレスを自動選択する際に `net1` の IP アドレスを使用するようになり, セカンダリネットワーク経由の通信が確実に行われます。

## 参考資料

### 公式ドキュメント

- [Multus CNI GitHub リポジトリ](https://github.com/k8snetworkplumbingwg/multus-cni)
- [Multus Quickstart Guide](https://github.com/k8snetworkplumbingwg/multus-cni/blob/master/docs/quickstart.md)
- [NetworkAttachmentDefinition 仕様](https://github.com/k8snetworkplumbingwg/network-attachment-definition-client)
- [CNI 仕様](https://github.com/containernetworking/cni/blob/master/SPEC.md)
- [Multus Helm Chart](https://github.com/k8snetworkplumbingwg/multus-cni/tree/master/deployments/helm)

### 関連ロール

- `k8s-common`: Kubernetes クラスタ共通設定
- `k8s-ctrlplane`: コントロールプレーンノード構築 (Cilium 導入)
- `k8s-whereabouts`: Multus セカンダリネットワーク用 IPAM プラグインと NAD 導入例
