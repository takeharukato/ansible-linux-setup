# k8s-shared-ca ロール

## 概要

本ロールは, Kubernetes クラスタ間の通信を保護するための共通認証局(Certificate Authority, 以下「共通CA」)の証明書と秘密鍵を `ansible-playbook` コマンド実行ノード(以下, 「制御ノード」)上で準備し, 各コントロールプレーンノードへ配置します。共通CAは, Cilium Cluster Mesh による複数クラスタ間の mTLS(相互認証 TLS)を同一発行元で統一するほか, kubeconfig に埋め込むクラスタ認証局として, また Kubernetes のデフォルトルート CA を置き換える際に使用されます。

### 共通CA の主な用途

1. **Kubernetes コアコンポーネント証明書の再発行**: `k8s_shared_ca_replace_kube_ca: true` を指定した場合, kube-apiserver, kube-controller-manager, kube-scheduler 等のコアコンポーネント証明書を共通CAで発証します。これにより, 複数クラスタ間で統一された認証局を使用できます。

2. **kubeconfig へのクラスタ認証局埋め込み**: `roles/k8s-ctrlplane/tasks/config-cluster-mesh-tools.yml` が呼び出す `create-embedded-kubeconfig.py --shared-ca` スクリプト内で, kubeconfig ファイルに埋め込むクラスタ認証局として使用されます。これにより, クラスタ外のツールが Kubernetes の CA 証明書なしに kubeconfig のみで Cilium Cluster Mesh に接続可能になります。

3. **Cilium Cluster Mesh 用の統一された mTLS 発行元**: `k8s-cilium-shared-ca` ロール(`k8s_cilium_shared_ca_enabled: true` かつ `k8s_cilium_shared_ca_reuse_k8s_ca: true` を指定した場合)が, Cilium Cluster Mesh 用の `cilium-ca` Secret を発行する際に, この共通CA で証明書を生成します。複数の Kubernetes クラスタ間の Cilium Cluster Mesh 接続において, 全クラスタで同一の発行元を使用し, mTLS の相互信頼を確立します。

### 共通CA の供給元と優先順位

本ロールは, 共通CA を以下の順序で探して利用します。`enable_create_k8s_ca` と `k8s_common_ca` 変数の組み合わせにより動作を制御します:

| `enable_create_k8s_ca` | `k8s_common_ca` | ロールの挙動 |
| --- | --- | --- |
| `false` | 必須(値あり) | 指定ディレクトリ内の `cluster-mesh-ca.crt` と `cluster-mesh-ca.key` を利用します。ファイルが読めない場合は即エラーで playbook の動作を終了します。 |
| `true` | 有効(値あり) | 指定ディレクトリ内の共通CA を最優先で再利用します。アクセス不可の場合は警告を出した上でロール内の共通CA またはOpenSSL での新規生成にフォールバックします。 |
| `true` | 読めない | 指定ディレクトリにアクセスできない場合は警告を出した上で, ロール内に含まれる共通CA(`roles/k8s-shared-ca/files/shared-ca/`)またはOpenSSL での新規生成にフォールバックします。 |
| `true` | 未指定 | `roles/k8s-shared-ca/files/shared-ca/` に既存の共通CA があれば再利用します。なければ OpenSSL で新規生成し, `files/shared-ca/` に保存して以後も利用します。 |

本ロールは再実行可能な設計になっており, 既存ファイルがある場合は作成済みの証明書, 鍵ファイルを再利用します。生成した共通CA はセキュリティ要件に応じて, 適切に運用, 管理してください。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Application Programming Interface | API | アプリケーション同士がやり取りする方法を定めた仕様。 |
| Custom Resource Definition | CRD | Kubernetes APIを拡張してユーザ独自のリソース種別を定義する仕組み。 |
| Role-Based Access Control | RBAC | ユーザやサービスアカウントが実行可能な操作を役割(Role)で制限する仕組み。 |
| Certificate Authority | CA | デジタル証明書を発行し, 署名する信頼された機関。Kubernetesでは各種コンポーネント間の通信を保護するために使用される。 |
| Transport Layer Security | TLS | ネットワーク通信を暗号化し, 通信相手を認証するセキュリティプロトコル。 |
| mutual TLS | mTLS | クライアントとサーバー双方が証明書で互いを認証する相互認証方式。 |
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
| LoadBalancer | - | サービス ( Service )の一種で, クラウドプロバイダーやオンプレミス環境の外部ロードバランサーを利用してクラスタ外部からのアクセスを提供する仕組み。 |
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
| Cilium Cluster Mesh | - | Cilium固有の機能で, 複数のKubernetesクラスタ間で以下の処理を行い接続する仕組み。(1)各クラスタのPod IPアドレス範囲に加え, Serviceの仮想IP(ClusterIP), そのServiceを提供するPodやノードの到達先情報を相互に交換, (2)到達先に応じた転送設定を行う(CiliumをNative Routingモードで使用する場合は, Pod間通信が相互に到達できるように経路を準備する必要がある。経路の実現方法は環境依存であり, 外部ルータでの静的経路設定, 同一L2セグメントでの直接到達, BGPによる経路広告などを用いる), (3)通信相手の証明書を検証して相互認証する, (4)Global Serviceを有効にした場合は, 複数クラスタ間で同じService名に対応するServiceエンドポイント情報を相互に共有し, クラスタをまたいだ負荷分散を行う。これにより, 異なるクラスタのPod同士が直接通信したり, サービスを共有したりできる。 |
| Global Service | - | Cilium Cluster Mesh環境で複数クラスタ間でサービスを共有し, 負荷分散する機能。 |
| Serviceエンドポイント ( Service Endpoint ) | - | Serviceのバックエンドとして通信を受けるPod, または, 当該の通信を受けるPodに加え, 当該の通信を受けるPodへ通信を届けるためのネットワーク上の転送先情報全体を指す。 |
| Serviceエンドポイント情報 ( Service Endpoint Information ) | - | Serviceエンドポイントを特定して転送先を決めるための情報。主にバックエンドPodのIPアドレス, ポート番号, プロトコル, 所属クラスタ名(またはクラスタ識別子)で構成される。 |
| Multus | - | 複数のCNIプラグインを同時に使用できるようにするメタCNIプラグイン。 |
| Container Runtime Interface | CRI | Kubernetesがコンテナランタイムと通信するための標準インターフェース。 |
| containerd | - | Dockerから分離された軽量なコンテナランタイム。 |
| kubeadm | - | Kubernetesクラスタの初期構築と管理を支援する公式ツール。 |
| kubectl | - | Kubernetesクラスタを操作するためのコマンドラインツール。 |
| kubeconfig | - | kubectlや他のツールがKubernetesクラスタにアクセスするための設定ファイル。接続先クラスタ情報, 認証情報, コンテキストを含む。 |
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
| OpenSSL | - | SSL/TLSプロトコルの実装およびデジタル証明書, 秘密鍵を生成, 管理するためのオープンソースツール。 |
| Ansible Vault | - | Ansibleで機密情報(パスワード, 秘密鍵など)を暗号化して安全に保管, 管理する機能。 |

## 前提条件

本ロールを実行する前に, 以下の条件が満たされている必要があります:

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- Ansible: 2.15 以降
- 制御ノードから各ホストへの接続: SSH 接続が確立されていること
- 管理者権限: 各ホスト上で sudo による root 権限実行が可能なこと
- 制御ノード上で OpenSSL が利用可能: 共通CA新規生成時に必須

## 実行フロー

本ロールは以下の手順で共通CA を準備し, 各コントロールプレーンノードへ配置します:

### 1. 制御ノード上での共通CA 準備

ロール実行時に, 以下の順序で共通CA の供給元を探査します:

1. **ユーザー提供の共通CA**: `k8s_common_ca` が指定され, 対象ディレクトリ内の `cluster-mesh-ca.crt` と `cluster-mesh-ca.key` が読み取り可能な場合は最優先で使用
2. **ロール内同梱の共通CA**: `roles/k8s-shared-ca/files/shared-ca/` に既存ファイルがある場合は次に優先
3. **新規生成**: `enable_create_k8s_ca: true` の場合に限り, OpenSSL で新規生成

いずれも利用不可の場合, `enable_create_k8s_ca: false` 時はエラーで終了, `enable_create_k8s_ca: true` 時は警告を出しながら生成処理へ進みます。

### 2. 各コントロールプレーンノードへの配置

準備した共通CA の証明書と秘密鍵を, 各ターゲットホスト上の `{{ k8s_shared_ca_output_dir }}` (既定値: `/etc/kubernetes/pki/shared-ca/`)に配置します。ファイルの所有者は `root:root`, パーミッションは `0600` で固定されます。

### 3. オプション: Kubernetes デフォルトルート CA の置き換え

`k8s_shared_ca_replace_kube_ca: true` を指定した場合:

1. Kubernetes デフォルトルート CA(`/etc/kubernetes/pki/ca.crt`, `/etc/kubernetes/pki/ca.key`)を共通CA に置き換え
2. kube-apiserver, kube-controller-manager, kube-scheduler 等のコアコンポーネント証明書の再発行
3. ワーカーノードの再 join により新しいルート CA を信頼させることが必要

## 主要変数

### 基本設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `enable_create_k8s_ca` | `false` | 共通CAをロール内で新規生成するか, 既存ファイルを必須とするかを切り替えます。`false`時は `k8s_common_ca` が必須です。 |
| `k8s_common_ca` | `""` | 既存の共通CAが格納されたディレクトリパス。未指定時はロール同梱資材(`roles/k8s-shared-ca/files/shared-ca/`)または新規生成にフォールバックします。 |
| `k8s_shared_ca_output_dir` | `/etc/kubernetes/pki/shared-ca` | コントロールプレーンノードに配置する共通CA 一式の配置先ディレクトリ。 |
| `k8s_shared_ca_replace_kube_ca` | `false` | Kubernetes デフォルトルート CA を共通CA に置き換えるかを制御します。`true` の場合, コアコンポーネント証明書の再発行とワーカーノードの再 join が必須です。 |

### CA 生成パラメータ

これらのパラメータは `enable_create_k8s_ca: true` かつ新規生成時にのみ効果があります。

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_shared_ca_cert_filename` | `cluster-mesh-ca.crt` | 共通CA 証明書ファイル名。 |
| `k8s_shared_ca_key_filename` | `cluster-mesh-ca.key` | 共通CA 秘密鍵ファイル名。 |
| `k8s_shared_ca_subject` | `/CN=cilium-cluster-mesh-ca` | 新規生成時に指定する証明書サブジェクト。 |
| `k8s_shared_ca_valid_days` | `3650` | 新規生成する共通CA の有効日数(10年相当)。 |
| `k8s_shared_ca_key_size` | `4096` | 新規生成時に使用するRSA 鍵長(ビット数)。 |
| `k8s_shared_ca_digest` | `sha256` | 証明書署名に利用するダイジェストアルゴリズム。 |

## 検証ポイント

ロール実行後, 以下のコマンドで正常配置を確認してください:

### 制御ノード上での確認

```bash
# 制御ノードの役割同梱ディレクトリに CA ファイルが存在することを確認
ls -la roles/k8s-shared-ca/files/shared-ca/
```

期待される出力:

```
total 16
drwxr-xr-x 2 user user 4096 Mar  7 10:00 .
drwxr-xr-x 3 user user 4096 Mar  7 10:00 ..
-rw-r--r-- 1 user user 1870 Mar  7 10:00 cluster-mesh-ca.crt
-rw------- 1 user user 3243 Mar  7 10:00 cluster-mesh-ca.key
```

確認ポイント:

- `cluster-mesh-ca.crt` (証明書ファイル)が存在する
- `cluster-mesh-ca.key` (秘密鍵ファイル)が存在する
- 秘密鍵のパーミッションが `600` または `rw-------` である

### 各コントロールプレーンノード上での確認

対象ホスト( `k8sctrlplane01.local` など)で以下を実行:

```bash
# 配置先ディレクトリの確認
ls -ld /etc/kubernetes/pki/shared-ca/
```

期待される出力:

```
drwx------ 2 root root 4096 Mar  7 10:05 /etc/kubernetes/pki/shared-ca/
```

確認ポイント:

- ディレクトリの所有者が `root:root` である
- ディレクトリのパーミッションが `700` または `drwx------` である

```bash
# CA ファイルの詳細確認
ls -la /etc/kubernetes/pki/shared-ca/
```

期待される出力:

```
total 16
drwx------ 2 root root 4096 Mar  7 10:05 .
drwxr-xr-x 5 root root 4096 Mar  7 10:05 ..
-rw------- 1 root root 1870 Mar  7 10:05 cluster-mesh-ca.crt
-rw------- 1 root root 3243 Mar  7 10:05 cluster-mesh-ca.key
```

確認ポイント:

- `cluster-mesh-ca.crt` と `cluster-mesh-ca.key` が存在する
- 両ファイルの所有者が `root:root` である
- 両ファイルのパーミッションが `600` または `rw-------` である

```bash
# 証明書の内容確認
sudo openssl x509 -noout -text -in /etc/kubernetes/pki/shared-ca/cluster-mesh-ca.crt
```

期待される出力の一部:

```
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number: ...
        Signature Algorithm: sha256WithRSAEncryption
        Issuer: CN=cilium-cluster-mesh-ca
        Validity
            Not Before: Mar  7 01:05:00 2026 GMT
            Not After : Mar  5 01:05:00 2036 GMT
        Subject: CN=cilium-cluster-mesh-ca
        Subject Public Key Info:
            Public Key Algorithm: rsaEncryption
                Public-Key: (4096 bit)
```

確認ポイント:

- Issuer と Subject が `CN=cilium-cluster-mesh-ca` (または `k8s_shared_ca_subject` で指定した値)である
- Validity の期間が期待通り(既定値では10年)である
- Public-Key が `4096 bit` (または `k8s_shared_ca_key_size` で指定した値)である

### オプション: ルート CA 置き換えが有効な場合

`k8s_shared_ca_replace_kube_ca: true` を指定した場合のみ実施:

```bash
# Kubernetes デフォルトルート CA が共通CA に置き換わっているか確認
sudo openssl x509 -noout -text -in /etc/kubernetes/pki/ca.crt | grep -A2 "Subject:"
```

期待される出力:

```
        Subject: CN=cilium-cluster-mesh-ca
        Subject Public Key Info:
            Public Key Algorithm: rsaEncryption
```

確認ポイント:

- Subject が `CN=cilium-cluster-mesh-ca` である
- `/etc/kubernetes/pki/ca.crt` が共通CA に置き換わっている

```bash
# kube-apiserver 証明書の発行者が共通CA になっているか確認
sudo openssl x509 -noout -text -in /etc/kubernetes/pki/apiserver.crt | grep -A1 "Issuer:"
```

期待される出力:

```
        Issuer: CN=cilium-cluster-mesh-ca
        Validity
```

確認ポイント:

- Issuer が `CN=cilium-cluster-mesh-ca` である
- kube-apiserver 証明書が共通CA で再発行されている

### オプション: kubeconfig 埋め込みの確認

`create-embedded-kubeconfig.py --shared-ca` で kubeconfig を生成した場合のみ実施:

```bash
# kubeconfig 内の certificate-authority-data をデコードして Subject を確認
kubectl config view --raw --kubeconfig=/path/to/generated-kubeconfig | \
  grep certificate-authority-data | head -1 | \
  awk '{print $2}' | base64 -d | openssl x509 -noout -text | grep -A1 "Subject:"
```

期待される出力:

```
        Subject: CN=cilium-cluster-mesh-ca
        Subject Public Key Info:
```

確認ポイント:

- kubeconfig に埋め込まれた CA の Subject が `CN=cilium-cluster-mesh-ca` である
- クラスタ外から kubeconfig のみで接続可能になっている

### Cilium Cluster Mesh 接続時の確認

Cilium Cluster Mesh を有効化している場合のみ実施:

```bash
# Cilium Cluster Mesh の接続状態と TLS エラーの有無を確認
cilium clustermesh status
```

期待される出力の一部:

```
⚠️  Service "clustermesh-apiserver" of type "LoadBalancer" found
✅ Cluster Connections:
- cluster2: 5/5 configured, 5/5 connected

🔌 Global services: [ min:0 / avg:0.0 / max:0 ]
```

確認ポイント:

- `Cluster Connections` セクションで対向クラスタが `connected` 状態である
- TLS エラー(例: `TLS: failed to verify peer certificate`)が表示されない
- Global Service を使用している場合: `Global services` が正常に同期されている

## トラブルシューティング

### `enable_create_k8s_ca: false` かつ CA ファイルが見つからない

**症状**: playbook がエラーで終了

```
FAILED - The following required files are missing: cluster-mesh-ca.crt, cluster-mesh-ca.key
```

**対処方法**:

1. `k8s_common_ca` が存在し, 読み取り可能か確認:
   ```bash
   ls -la "$k8s_common_ca"/{cluster-mesh-ca.crt,cluster-mesh-ca.key}
   ```

2. アクセス不可の場合, パス指定を確認し, `enable_create_k8s_ca: true` に変更するか, `k8s_common_ca` を正しい値に修正してからプレイブックを再実行します。

### ファイルパーミッション エラー

**症状**: 秘密鍵が読み取り可能な権限で配置されている

```
ERROR: cluster-mesh-ca.key has insecure permissions (644, expected 600)
```

**対処方法**:

各ノード上で以下で権限を修正:

```bash
sudo chmod 600 /etc/kubernetes/pki/shared-ca/cluster-mesh-ca.key
```

### OpenSSL 不在またはCA 生成失敗

**症状**: `enable_create_k8s_ca: true` 時に CA 生成が失敗

```
ERROR: openssl not found or certificate generation failed
```

**対処方法**:

1. 制御ノード上で OpenSSL がインストール済みか確認:
   ```bash
   which openssl && openssl version
   ```

2. インストール済みでない場合:
   ```bash
   sudo apt-get install openssl         # Ubuntu
   # または
   sudo dnf install openssl            # RHEL
   ```

3. 既に存在するCA をロール同梱ディレクトリに手動配置:
   ```bash
   mkdir -p roles/k8s-shared-ca/files/shared-ca/
   cp /path/to/cluster-mesh-ca.{crt,key} roles/k8s-shared-ca/files/shared-ca/
   ```

### `k8s_shared_ca_replace_kube_ca: true` 後, クライアント接続が TLS エラー

**症状**: kubectl コマンドで TLS エラー

```
error: x509: certificate signed by unknown authority
```

**対処方法**:

1. ワーカーノードが新しいルート CA を信頼していない可能性があります。ワーカーノードの再 join が必須です:
   ```bash
   # 各ワーカーノードで:
   sudo kubeadm reset -f
   <新しい join トークン情報で再 join>
   ```

2. クライアント側の kubeconfig が古い CA を参照している場合は, `create-embedded-kubeconfig.py --shared-ca` で新しい kubeconfig を生成してください。

### Cilium Cluster Mesh が TLS エラーで接続できない

**症状**: `cilium clustermesh status` で TLS エラーが表示される

```
TLS: failed to verify peer certificate
```

**対処方法**:

1. 対向クラスタの `k8s-shared-ca` ロールが同じ共通CA を使用しているか確認:
   ```bash
   # 現在のクラスタ
   openssl x509 -noout -subject -in /etc/kubernetes/pki/shared-ca/cluster-mesh-ca.crt

   # 対向クラスタ (対向クラスタのコントロールプレーンノードで実行)
   ssh <対向クラスタのコントロールプレーン> \
     openssl x509 -noout -subject -in /etc/kubernetes/pki/shared-ca/cluster-mesh-ca.crt
   ```

2. 同じ CA を使用していない場合, `k8s_cilium_shared_ca_enabled: true` かつ `k8s_cilium_shared_ca_reuse_k8s_ca: true` を指定して, 両クラスタで `k8s-cilium-shared-ca` ロールを再実行してください。

## 補足

### 保管ポリシー

- 生成された CA 秘密鍵 (`cluster-mesh-ca.key`) は **必ず** 所有者:`root:root`, アクセス権`600`で保持します。

セキュリティ要件に応じて, 制御ノード上では `ansible-vault encrypt roles/k8s-shared-ca/files/shared-ca/cluster-mesh-ca.key` などを用いて暗号化保管することを推奨します。Vault パスワードは別媒体で管理してください。セキュリティ要件に応じて別途対策を検討, 実施してください。

また, 耐災害性を確保する必要がある用途では, オフラインバックアップとして, 暗号化されたメディア ( ハードウェアトークンやフルディスク暗号化済みUSBストレージ等 )に CA 鍵と証明書, Vault パスワード情報を保管するなどの対策を別途実施してください。

### ローテーション手順の指針

1. 新しい CA を生成する場合は, 既存Kubernetesクラスタの再構築前に `roles/k8s-shared-ca/files/shared-ca/` をバックアップし, 必要なら Vault へも保存します。
2. `enable_create_k8s_ca: true` のまま `roles/k8s-shared-ca/files/shared-ca/` を空にしてプレイブックを再実行すると, 新しい共通CAが生成されます。
3. 既存Kubernetesクラスタへの段階的移行が必要な場合は, サービス停止計画を立てた上で以下を順に実行します。
   - 新CA配布 (`k8s-shared-ca` ロール再実行)
   - Cilium Cluster Mesh 証明書の再発行
   - `cilium clustermesh status` による疎通確認
4. ローテーション後は旧CAを失効または安全に廃棄し, Vaultおよびオフラインバックアップを更新します。
