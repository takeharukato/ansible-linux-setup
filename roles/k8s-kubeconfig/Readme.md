# k8s-kubeconfig ロール

Kubernetes クラスタの各ノード(コントロールプレーン・ワーカー)で利用する `kubeconfig` を生成, 統合, 配布するロールです。証明書埋め込みやコンテキスト統合により, 複数クラスタ環境での運用を効率化します。

## 概要

本ロールは Kubernetes の kubeconfig ライフサイクル全体を管理します。主な特徴は以下の通りです:

- **証明書埋め込みサポート**: `create-embedded-kubeconfig.py` で CA 証明書を kubeconfig ファイルに埋め込み, クラスタ環境にかかわらず実行可能にします。
- **複数クラスタコンテキスト統合**: `create-uniq-kubeconfig.py` で複数コントロールプレーンノードのコンテキストを1つの kubeconfig に統合します。
- **双方向ファイル配置**: `/etc/kubernetes` とオペレータユーザの `~/.kube` の両方に統合 kubeconfig を配置し, 権限分離と一貫性を両立。
- **キャッシング機構**: 制御ノード上の `~/.ansible/kubeconfig-cache/` に merged-kubeconfig を保管し, ワーカーノード配布の効率化と再実行時の一貫性確保。
- **シンボリックリンク管理**: `~/.kube/config` を相対シンボリックリンク化し, 既存ファイルは `config-default` として退避。
- **権限分離**: `k8s_operator_user` によるアクセス制御で, システムと一般ユーザの権限を分離。

## 前提条件

本ロール実行前に以下の条件が満たされていることを確認してください:

- Kubernetes クラスタが既に構築済みであること(k8s-ctrlplane ロール実行済み)
- コントロールプレーンノード・ワーカーノードが Ansible インベントリで定義されていること
- 制御ノードから全 Kubernetes ノードへの SSH 接続が確立されていること(ホスト鍵確認完了)
- 各ノードで管理者権限(sudo)が利用可能であること
- Python 3.8 以上がリモートホストにインストールされていること
- `create-embedded-kubeconfig.py`, `create-uniq-kubeconfig.py` スクリプトが `k8s_node_setup_tools_dir` に事前配置されていること

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
| Secure Shell | SSH | ネットワークを通じてリモートマシンに安全に接続し, コマンド実行やファイル転送を行うプロトコル。 |
| Superuser Do | sudo | Unix/Linux システムで管理者権限(root)でコマンドを実行するためのユーティリティ。 |
| Certificate Authority | CA | 公開鍵基盤(PKI)に基づいてデジタル証明書を発行・管理する信頼された機関。Kubernetes では認証局証明書を使って API サーバやクライアント認証を行う。 |
| Access Control List | ACL | ファイルやディレクトリの細かいアクセス権限を設定するメカニズム。`setfacl` 等のツールで管理する。 |
| Message Digest Algorithm 5 | MD5 | 任意の長さのデータをから一定の長さのハッシュ値に変換するアルゴリズム。ファイル検証や整合性確認に用いる。 |

## 実行フロー

### 全ノード共通フロー

1. `load-params.yml` でディストリビューション別パッケージ名, 共通設定, API エンドポイント定義などを読み込みます。
2. `prepare-vars.yml` が `kubeconfig` 関連パスを計算し, 埋め込みファイル名や `/etc/kubernetes` 配置先を決定します。
3. `directory.yml` で `/etc/kubernetes` と `{{ k8s_operator_user }}` の `~/.kube` を作成し, 必要な所有者, パーミッションを整えます。

### コントロールプレーンノード向けフロー

4. `control-plane.yml` ( `k8s_ctrl_plane` グループのみ )では次を実施します:
   - `/etc/kubernetes/admin.conf` を `config-default` としてバックアップ。
   - `create-embedded-kubeconfig.py` を呼び出し, Kubernetesクラスタ毎の証明書埋め込み `kubeconfig` を生成。
   - 各コントロールプレーンノードから埋め込み `kubeconfig` を収集し, 一時ディレクトリに展開。
   - kubeconfigファイル結合ツール(`create-uniq-kubeconfig.py`) で複数コンテキストを統合し `merged-kubeconfig.conf` を生成。
   - 生成された `merged-kubeconfig.conf` を `/etc/kubernetes` とオペレータユーザホームの `~/.kube` に配布。

### ワーカーノード向けフロー

5. `distribute-workers.yml` ( `k8s_worker` グループのみ )はホスト変数 (`k8s_ctrlplane_host` 変数) で指定されたコントロールプレーンノード上の `merged-kubeconfig.conf` を取得し, 制御ノード上の `~/.ansible/kubeconfig-cache/` に一旦キャッシュしてからワーカーノードへコピーします。
6. `symlink.yml` が `~/.kube/config` を `merged-kubeconfig.conf` への相対シンボリックリンクに置き換え, 既存ファイル(あれば)は `config-default` にリネームして退避します。

## テンプレートとファイル

本ロールはコントロールプレーンノード配下に生成ファイル群を作成し, 最終的に全Kubernetesノードに統合 kubeconfig を配布します。主な生成物は以下の通りです:

### 生成されるファイル一覧

| ファイル / ディレクトリ | 配置ホスト | パーミッション | 説明 |
| --- | --- | --- | --- |
| `/etc/kubernetes/ca-embedded-admin.conf` | コントロールプレーンノード | `0600` | 証明書を埋め込み済みの管理者 `kubeconfig`。`kubectl` をルート権限で利用するための控え。 |
| `/etc/kubernetes/config-default` | コントロールプレーンノード | `0600` | 既存の `/etc/kubernetes/admin.conf` のバックアップ。ロール実行前の kubeconfig を保持。 |
| `/etc/kubernetes/merged-kubeconfig.conf` | 全Kubernetes ノード | `0600` | 全コントロールプレーンノードのコンテキストを統合した `kubeconfig`。管理者用。 |
| `~{{ k8s_operator_user }}/.kube/cluster*-embedded.kubeconfig` | コントロールプレーンノード | `0600` | `create-embedded-kubeconfig.py` が生成するクラスタ固有の埋め込み版 kubeconfig。中間成果物。 |
| `~{{ k8s_operator_user }}/.kube/ca-embedded-admin.conf` | コントロールプレーンノード | `0600` | `/etc/kubernetes` に配置した埋め込み版のオペレータ控え。 |
| `~{{ k8s_operator_user }}/.kube/merged-kubeconfig.conf` | 全Kubernetes ノード | `0600` | `/etc/kubernetes/merged-kubeconfig.conf` と同一内容。オペレータユーザが直接参照。 |
| `~{{ k8s_operator_user }}/.kube/config` | 全Kubernetes ノード | リンク | 統合 `kubeconfig` (`merged-kubeconfig.conf`) への相対シンボリックリンク。既存ファイルは `config-default` に退避。 |
| `~{{ k8s_operator_user }}/.kube/config-default` | 全Kubernetes ノード | `0600` | `symlink.yml` 実行前の既存 `~/.kube/config` のバックアップ(存在した場合のみ)。 |

### キャッシング機構

制御ノード上の `~/.ansible/kubeconfig-cache/` にはコントロールプレーンノードから取得した最新の `/etc/kubernetes/merged-kubeconfig.conf` がキャッシュされます。ワーカーノード配布時にこのキャッシュを参照するため, プレイブック再実行時の効率化と一貫性が確保されます。 キャッシュディレクトリのパーミッションは `0700`(ユーザのみアクセス可能)に設定されます。

## 主要変数

### 基本設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_operator_user` | `kube` | `kubeconfig` を配置するオペレータユーザ。このユーザのホームディレクトリ(`k8s_operator_home` 変数で参照)に `~/.kube` 以下が作成されます。 |
| `k8s_kubeconfig_system_dir` | `/etc/kubernetes` | システム側で `kubeconfig` を配置するベースディレクトリ。管理者権限で操作します。 |
| `k8s_embed_kubeconfig_shared_ca_path` | `""` | `create-embedded-kubeconfig.py` に渡す共通 CA 証明書のパス。未設定時は各クラスタの `/etc/kubernetes/admin.conf` に含まれる CA をそのまま埋め込みます。 |

### スクリプトパス

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_embed_kubeconfig_script_path` | `/opt/k8snodes/sbin/create-embedded-kubeconfig.py` | 証明書埋め込み版 `kubeconfig` を生成するスクリプト。コントロールプレーンノードで実行されます。 |
| `k8s_create_unique_kubeconfig_script_path` | `/opt/k8snodes/sbin/create-uniq-kubeconfig.py` | 複数の `kubeconfig` コンテキストを1つのファイルに統合するスクリプト。 |

### 出力ディレクトリ

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_embed_kubeconfig_output_dir` | `{{ k8s_operator_home }}/.kube` | 埋め込み kubeconfig を出力するディレクトリ。コントロールプレーンノードで使用。 |
| `k8s_embed_kubeconfig_file_postfix` | `-embedded.kubeconfig` | 埋め込み版 kubeconfig のファイル名サフィックス。クラスタ名と組み合わせて「`cluster01-embedded.kubeconfig`」のような形式になります。 |

### ホスト間連携

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_ctrlplane_host` | なし(ホスト変数で必須) | ワーカーノードが統合 kubeconfig を取得するコントロールプレーンノードのホスト名。`host_vars/<worker-node>/` で必ず定義してください。 |
| `k8s_kubeconfig_probe_timeout` | `15` | ワーカーノードがコントロールプレーンノードへの接続確認するときのタイムアウト秒数。 |

## 検証ポイント

本ロール実行後の kubeconfig 統合状況は以下のコマンドで確認できます。

### kubeconfig ファイルの生成確認(コントロールプレーンノード)

**実施ホスト**: コントロールプレーンノード

**コマンド**:
```bash
ls -lh /etc/kubernetes/{admin.conf,config-default,merged-kubeconfig.conf}
ls -lh ~/.kube/{cluster*-embedded.kubeconfig,merged-kubeconfig.conf,config}
```

**期待される出力**:
```
-rw------- 1 root root 5.2K Jul 15 10:30 /etc/kubernetes/admin.conf
-rw------- 1 root root 5.2K Jul 15 10:25 /etc/kubernetes/config-default
-rw------- 1 root root 8.5K Jul 15 10:30 /etc/kubernetes/merged-kubeconfig.conf
-rw------- 1 kube kube 5.0K Jul 15 10:28 /home/kube/.kube/cluster01-embedded.kubeconfig
-rw------- 1 kube kube 8.5K Jul 15 10:30 /home/kube/.kube/merged-kubeconfig.conf
lrwxrwxrwx 1 kube kube 24 Jul 15 10:30 /home/kube/.kube/config -> merged-kubeconfig.conf
```

**確認ポイント**:
- `/etc/kubernetes/merged-kubeconfig.conf` が作成されているか
- `~/.kube/config` が `merged-kubeconfig.conf` への シンボリックリンク化されているか
- パーミッションが `0600` になっているか

### 統合 kubeconfig 内容確認(全ノード)

**実施ホスト**: コントロールプレーン / ワーカーノード

**コマンド**:
```bash
kubectl config get-contexts
kubectl config get-clusters
```

**期待される出力**:
```
CURRENT   NAME                          CLUSTER                       AUTHINFO                      NAMESPACE
*         kubernetes-admin@cluster01    kubernetes-admin@cluster01    kubernetes-admin@cluster01
          kubernetes-admin@cluster02    kubernetes-admin@cluster02    kubernetes-admin@cluster02
          kubernetes-admin@cluster03    kubernetes-admin@cluster03    kubernetes-admin@cluster03

NAME
cluster01
cluster02
cluster03
```

**確認ポイント**:
- 全コントロールプレーンノードのコンテキストが統合されていること
- クラスタ名, ユーザ情報が正しく表示されていること

### kubectl コマンド実行確認(全ノード)

**実施ホスト**: コントロールプレーン / ワーカーノード

**コマンド**:
```bash
kubectl get nodes
kubectl auth can-i get pods --as=system:serviceaccount:default:default
```

**期待される出力**:
```
NAME                    STATUS   ROLES           AGE   VERSION
k8sctrlplane01.local    Ready    control-plane   20d   v1.29.0
k8sctrlplane02.local    Ready    control-plane   20d   v1.29.0
k8sworker0101.local     Ready    <none>          20d   v1.29.0
k8sworker0102.local     Ready    <none>          20d   v1.29.0

yes
```

**確認ポイント**:
- `kubectl` がクラスタに接続できていること (エラーなく実行結果が返されること)
- 全ノードが `Ready` 状態こと

### ワーカーノード kubeconfig 同期確認

**実施ホスト**: ワーカーノード

**コマンド**:
```bash
ls -l ~/.kube/config ~/.kube/merged-kubeconfig.conf
md5sum ~/.kube/merged-kubeconfig.conf
```

**期待される出力**:
```
lrwxrwxrwx 1 kube kube 24 Jul 15 10:35 /home/kube/.kube/config -> merged-kubeconfig.conf
-rw------- 1 kube kube 8.5K Jul 15 10:35 /home/kube/.kube/merged-kubeconfig.conf
9f5c3e4d2b1a6f8e7c0d5a9b2c3e4f5a  /home/kube/.kube/merged-kubeconfig.conf
```

**確認ポイント**:
- ワーカーノードのファイル内容がコントロールプレーンノードと同期していること(ワーカーノードも MD5 で確認)
- 権限が正しく設定されていること

## 運用上の注意

### スクリプト配置の確認

`create-embedded-kubeconfig.py` と `create-uniq-kubeconfig.py` は必ず `k8s_node_setup_tools_dir` に事前配置してください。未配置の場合はロール実行時にエラーになります。

### ロール実行順序の制約

`k8s_ctrl_plane` グループ以外でこのロールを実行すると, 埋め込み `kubeconfig` の生成はスキップされます。ワーカーノードへ配布する前に**必ずコントロールプレーンノードでロールを完了させてください**。

### ワーカーノードの必須変数

ワーカーノードごとの `k8s_ctrlplane_host` 変数は `host_vars/<worker>/` などで**必ず定義してください**。未定義の場合はタスクがエラーで停止します。

```yaml
# host_vars/k8sworker0101.local/main.yml
k8s_ctrlplane_host: k8sctrlplane01.local
```

### キャッシング機構と単発実行

`~/.ansible/kubeconfig-cache/` は制御ノードのユーザが所有し, パーミッション `0700` で管理される kubeconfig キャッシュです。以下の点に注意してください:

- 制御ノードでプレイブックを再実行すると, キャッシュから同一ファイルを再利用して効率化します。
- コントロールプレーンノードでロール実行をスキップした状態でワーカー配布のみを実行すると, 旧キャッシュが配布されます。**一貫性確保のため, コントロールプレーン処理 => ワーカー配布の順序を通常通り実行してください**。

### ファイルパーミッション

`merged-kubeconfig.conf` は `0600`(ユーザのみ読み取り可能)で配布されます。追加ユーザに読み取りを許可したい場合は, 別途 ACL やグループ管理を行ってください:

```bash
# ACL で別ユーザに読み取り許可
setfacl -m u:otheruser:r ~/.kube/merged-kubeconfig.conf
```

### トラブルシューティング

**症状**: `kubectl` コマンドが実行できない

- **原因**: kubeconfig ファイルが正しく配置されていない可能性があります。
- **確認**: 検証セクションの「kubeconfig ファイルの生成確認」を実行し, `/etc/kubernetes/merged-kubeconfig.conf` と `~/.kube/config` の存在を確認。
- **対処**: ロールを再実行するか, 手動で検証セクションのコマンドを試行してください。

**症状**: ワーカーノードとコントロールプレーンで kubeconfig 内容が異なる

- **原因**: キャッシュ更新が行われていない可能性があります。
- **確認**: `md5sum ~/.kube/merged-kubeconfig.conf` で両ノードを比較。
- **対処**: `~/.ansible/kubeconfig-cache/` を削除してプレイブックを再実行し, キャッシュを再生成してください。
