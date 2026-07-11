# k8s-register-image ロール

このロールは, 生成済みのコンテナイメージ tar を各 Kubernetes ノードへ配布し, control plane と worker 上の containerd に同一の手順で登録するための共通ロールである。

- [k8s-register-image ロール](#k8s-register-image-ロール)
  - [用語](#用語)
  - [本ロールの動作仕様](#本ロールの動作仕様)
  - [主要変数](#主要変数)
  - [本ロールでの処理内容](#本ロールでの処理内容)
    - [処理の流れ](#処理の流れ)
    - [利用例](#利用例)
      - [control planeノード上のcontainerdへのイメージ登録処理の例](#control-planeノード上のcontainerdへのイメージ登録処理の例)
      - [workerノード上のcontainerdへのイメージ登録処理の例](#workerノード上のcontainerdへのイメージ登録処理の例)
  - [注意事項](#注意事項)
  - [検証ポイント](#検証ポイント)

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Kubernetes | K8s | コンテナをまとめて管理, 配置, 再起動, 監視するためのオーケストレーション基盤。 |
| Container Runtime Interface | CRI | Kubernetes が containerd や cri-o などのランタイムとやり取りするための共通インターフェース。 |
| containerd | containerd | Linux 上でコンテナの取得, 展開, 実行を担うランタイム。 |
| `ctr` | ctr | containerd に付属する低レベル操作コマンド。image import や tag 操作に使う。 |

## 本ロールの動作仕様

本ロールの役割, 動作仕様は以下の通り。

- Ansible 制御ノード上にある コンテナイメージ tar ファイル を, Kubernetes のcontrol plane ホストと worker ホストの各ホストへ転送する。
- 対象ホスト上で containerd の `ctr` を用いて image import を行う。
- 未修飾名のイメージについては, CRI の既定レジストリ解決差異を吸収するための別名タグを付与する。
- コンテナイメージ tar ファイル の生成やローカルキャッシュの準備は行わない。成果物の準備は呼び出し側ロールの責務とする。

## 主要変数

本ロールの動作パラメタとなる変数を以下に示す。

| 変数名 | 意味 | 規定値 |
| --- | --- | --- |
| `k8s_register_image_components` | 登録対象コンポーネント名と tar パスの対応表。 | `{}` |
| `k8s_register_image_expected_images` | コンポーネント名から期待タグへの対応表。 | `{}` |
| `k8s_register_image_control_plane_hosts` | 登録対象の control plane ホスト一覧。 | `[]` |
| `k8s_register_image_worker_hosts` | 登録対象の worker ホスト一覧。 | `[]` |
| `k8s_register_image_auto_discover_control_plane_hosts` | control plane ホスト一覧を自動解決する場合は, `true`に設定する。 | `false` |
| `k8s_register_image_auto_discover_worker_hosts` | worker ホスト一覧を自動解決する場合は, `true`に設定する。 | `false` |
| `k8s_register_image_control_plane_group_name` | control plane 自動解決時に参照するインベントリグループ名。 | `"k8s_ctrlplane"` |
| `k8s_register_image_cluster_key` | 呼び出し元が渡すクラスタ識別キー。ノードが所属するK8sクラスタを判定するために使用する。典型的な場合には, 各ノードの所属するK8sクラスタのコントロールプレインのAPIエンドポイントを引き渡す。 | `""` |
| `k8s_kubeconfig_to_discover_workers_path` | worker 自動解決時に `kubectl` が参照する kubeconfig のパス。 | `""` |
| `k8s_register_image_skip_discovery` | 転送先ホスト(対象ホスト)の再探索を抑止する。 | `false` |
| `k8s_register_image_remote_cache_dir` | 対象ノード上の一時 tar 配置先ディレクトリ。 | `"/tmp/k8s-register-image"` |
| `k8s_register_image_unqualified_image_registry` | 未修飾名に付与する既定レジストリ名。 コンテナイメージ取得先レジストリ名が記載されていなかった場合のデフォルトのレジストリ名を補足するために使用する。| `"docker.io"` |
| `k8s_register_image_cleanup_remote_tar` | 登録後に対象ノード上の一時 tar を削除するかどうか。 | `true` |

## 本ロールでの処理内容

本ロールは, 既に用意されたコンテナイメージ tar を control plane と worker へ配布し, それぞれのホスト上で containerd に登録する。

### 処理の流れ

1. 入力変数の妥当性を検証する。
2. 必要に応じて対象ホストを自動解決し, 同一クラスタ内の代表ノードを判定する。
3. control plane ホストへ tar を配布し, `ctr images import` を実行する。
4. worker ホストへ tar を配布し, 同じ import ロジックを再利用して登録する。
5. 必要に応じて対象ノード上の一時 tar を削除する。

### 利用例

以下の利用例は, 呼び出し元ロールが目的別に変数を設定し, k8s-register-image ロールへ処理を委譲する方法を示す。
1つ目は control plane ノードへの登録処理を実行するための設定であり, 2つ目は worker ノードの自動検出と登録処理を実行するための設定である。

#### control planeノード上のcontainerdへのイメージ登録処理の例

Ansible 制御ノード(localhost)上のtar形式のコンテナイメージを control plane へ転送する。

典型的な場合, コントロールプレインノードとワーカーノードの双方にコンテナイメージを登録するため, , 以下では, 登録後も後続処理で再利用できるように対象ノード(転送先ノード)上のコンテナイメージを削除せず保持させるように設定する例である。

各変数には以下の値を設定している。control plane 自動解決は有効化し, `k8s_ctrlplane_endpoint` をクラスタ識別キーとして渡すことで, 同じクラスタに属する control plane ノードだけを対象にする。登録後も後続処理で tar を使い回せるように, 対象ノード上の一時 tar は削除しない。

- k8s_register_image_components: 登録対象コンポーネント名と tar パスの対応表である。`manager`, `syncer`, `vn-agent` の 3 つをキーとして, それぞれの tar ファイルの絶対パスを値として渡している。コンポーネント名は containerd 登録時の期待タグを引くためのキーとしても使用する。
- k8s_register_image_expected_images: コンポーネント名ごとの期待イメージタグの対応表である。ここでは, 各コンポーネントを VirtualCluster の既定イメージタグに対応付けている。
- k8s_register_image_auto_discover_control_plane_hosts: control plane ホスト一覧をロール側で自動解決する指定である。`true` にすることで, 事前にホスト一覧を明示しなくても対象ホストを決められる。
- k8s_register_image_cluster_key: 呼び出し元が渡すクラスタ識別キーである。自動解決時に, どのクラスタの control plane かを判定するために使う。
- k8s_register_image_remote_cache_dir: 対象 control plane ノード上で一時的に tar を配置するディレクトリである。ここでは `/tmp/vc-images` を使い, control plane 上の一時配置先を固定している。
- k8s_register_image_unqualified_image_registry: 未修飾名イメージへ補完する既定レジストリ名である。`docker.io` を指定して, CRI の既定レジストリ解決差異を吸収している。
- k8s_register_image_cleanup_remote_tar: 登録後も, 後続処理向けに対象ノード上の一時 tar を削除しないように `false` を指定している。


```yaml
- name: Register VirtualCluster images on control-plane
  ansible.builtin.include_role:
    name: k8s-register-image
    tasks_from: register-control-plane.yml
  vars:
    k8s_register_image_components:
      manager: "/opt/virtual-cluster/binary/manager-amd64.tar"
      syncer: "/opt/virtual-cluster/binary/syncer-amd64.tar"
      vn-agent: "/opt/virtual-cluster/binary/vn-agent-amd64.tar"
    k8s_register_image_expected_images:
      manager: "virtualcluster/manager-amd64:latest"
      syncer: "virtualcluster/syncer-amd64:latest"
      vn-agent: "virtualcluster/vn-agent-amd64:latest"
    k8s_register_image_auto_discover_control_plane_hosts: true
    k8s_register_image_cluster_key: "192.168.30.41:6443"
    k8s_register_image_remote_cache_dir: "/tmp/vc-images"
    k8s_register_image_unqualified_image_registry: "docker.io"
    k8s_register_image_cleanup_remote_tar: false
```

#### workerノード上のcontainerdへのイメージ登録処理の例

Ansible 制御ノード(localhost)上のtar形式のコンテナイメージを worker へ転送し, worker 上の containerd に登録する。

典型的な場合, control plane から得たクラスタ情報を使って worker を自動検出するため, 以下では, worker 検出に使う kubeconfig を指定し, localhost のローカルキャッシュにある tar を各 worker へ登録する例である。

各変数には以下の値を設定している。ここでは, control plane から取得した worker 一覧を使って対象ノードを決めるため, control plane 自動解決と worker 自動解決の両方を有効化している。worker 検出には `/etc/kubernetes/admin.conf` を `k8s_kubeconfig_to_discover_workers_path` に渡し, localhost 上の固定配置先 `/opt/virtual-cluster/binary/` に置かれた tar をそのまま各 worker へ登録している。`remote_cache_dir` は worker 上の一時配置先として `/tmp` を使い, 未修飾名イメージの補完先レジストリは `docker.io` を指定している。

- k8s_register_image_components: 登録対象コンポーネント名と tar パスの対応表である。`manager`, `syncer`, `vn-agent` の 3 つをキーとして, それぞれの tar ファイルの絶対パスを値として渡している。コンポーネント名は containerd 登録時の期待タグを引くためのキーとしても使用する。
- k8s_register_image_expected_images: コンポーネント名ごとの期待イメージタグの対応表である。ここでは, 各コンポーネントを VirtualCluster の既定イメージタグに対応付けている。
- k8s_register_image_auto_discover_control_plane_hosts: control plane ホストを自動解決し, 代表ノード判定に使う指定である。`true` にすることで, control plane の代表ノードをロール側で決められる。
- k8s_register_image_auto_discover_worker_hosts: `kubectl` により worker ノードを自動検出する指定である。`true` にすることで, 実在する worker ノード一覧をスーパークラスタから取得する。
- k8s_register_image_cluster_key: 呼び出し元が渡すクラスタ識別キーである。worker 検出時にも同じクラスタに属する control plane であることを確認するために使う。
- k8s_kubeconfig_to_discover_workers_path: worker 自動検出時に `kubectl` が参照する kubeconfig のパスである。ここではスーパークラスタの管理者用 kubeconfig を指定している。
- k8s_register_image_remote_cache_dir: 各 worker ノード上で tar を一時配置するディレクトリである。ここでは `/tmp` を指定して, 一時領域に登録する。
- k8s_register_image_unqualified_image_registry: 未修飾名イメージへ補完する既定レジストリ名である。`docker.io` を指定して, CRI の既定レジストリ解決差異を吸収している。
- k8s_register_image_cleanup_remote_tar: 登録後に各 worker ノードへ転送したコンテナイメージ tar を削除するかどうかの指定である。`true` を指定して, worker 登録後に後始末する。

```yaml
- name: Discover worker nodes and register images on workers
  ansible.builtin.include_role:
    name: k8s-register-image
    tasks_from: register-workers.yml
  vars:
    k8s_register_image_components:
      manager: "/opt/virtual-cluster/binary/manager-amd64.tar"
      syncer: "/opt/virtual-cluster/binary/syncer-amd64.tar"
      vn-agent: "/opt/virtual-cluster/binary/vn-agent-amd64.tar"
    k8s_register_image_expected_images:
      manager: "virtualcluster/manager-amd64:latest"
      syncer: "virtualcluster/syncer-amd64:latest"
      vn-agent: "virtualcluster/vn-agent-amd64:latest"
    k8s_register_image_auto_discover_control_plane_hosts: true
    k8s_register_image_auto_discover_worker_hosts: true
    k8s_register_image_cluster_key: "192.168.30.41:6443"
    k8s_kubeconfig_to_discover_workers_path: "/etc/kubernetes/admin.conf"
    k8s_register_image_remote_cache_dir: "/tmp/vc-images"
    k8s_register_image_unqualified_image_registry: "docker.io"
    k8s_register_image_cleanup_remote_tar: true
```

## 注意事項

- 対象ホストで `ctr` コマンドが利用可能であることを前提とする。
- 対象ホストで `become: true` による権限昇格が可能であることを前提とする。
- control plane と worker の対象ホスト一覧は, 呼び出し側で明示的に渡すか, 自動解決用変数を設定してロール側で解決する。
- 登録対象の tar ファイルは, Ansible 制御ノード上の指定ディレクトリに存在している必要がある。
- このロールは, build/fetch そのものを実行しない。成果物の準備は呼び出し側で完了させる。
- `k8s_register_image_cleanup_remote_tar` の設定は呼び出し元責務である。後続処理で同じ tar を再利用する場合は `false` を指定する。

## 検証ポイント

- control plane と worker の双方で, `ctr -n k8s.io images ls` に期待タグが現れること。
- 未修飾名のイメージについて, 期待タグと別名タグの双方が登録されること。
