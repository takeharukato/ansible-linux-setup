# k8s-register-image ロール

本ロールは, 呼び出し元ロールが事前に用意したコンテナイメージ tar を Kubernetes ノードへ配布し, control plane ノードと worker ノード上の Container Runtime Interface (CRI, containerd など) に登録するための共通ロールである。

- [k8s-register-image ロール](#k8s-register-image-ロール)
  - [用語](#用語)
  - [本ロールの動作仕様](#本ロールの動作仕様)
  - [呼び出し元ロールからの使用方法](#呼び出し元ロールからの使用方法)
    - [呼び出し元ロール作成者が実施する作業](#呼び出し元ロール作成者が実施する作業)
    - [呼び出し元ロールでのパラメタの設定手順](#呼び出し元ロールでのパラメタの設定手順)
    - [呼び出し元ロールから本ロールを呼び出すansibleタスクの記載方法](#呼び出し元ロールから本ロールを呼び出すansibleタスクの記載方法)
      - [コンテナイメージをcontrol plane ノード群に配布する場合の例](#コンテナイメージをcontrol-plane-ノード群に配布する場合の例)
      - [コンテナイメージをworker ノード群に配布する場合の例](#コンテナイメージをworker-ノード群に配布する場合の例)
    - [各パラメタ変数に設定する値](#各パラメタ変数に設定する値)
  - [注意事項](#注意事項)
  - [検証ポイント](#検証ポイント)

## 用語

この節では, 本文で使用する用語を定義する。

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| ロール | - | Ansible における処理のまとまり。 |
| 変数 | - | 実行時に値を切り替えるための設定項目。 |
| 制御ホスト | - | Ansible を実行するホスト。呼び出し元ロールが準備した tar を保持し, 対象ノードへ配布する。 |
| 対象ノード | - | コンテナイメージ tar を配布し, containerd への登録を実行するノード。 |
| Kubernetes | K8s | コンテナをまとめて管理, 配置, 再起動, 監視するためのオーケストレーション基盤。 |
| control plane ノード | - | Kubernetes の制御機能を担うノード。 |
| worker ノード | - | Kubernetes 上で動作するアプリケーションを実行するノード。 |
| Container Runtime Interface | CRI | Kubernetes が containerd や cri-o などのランタイムとやり取りするための共通インターフェース。 |
| containerd | containerd | Linux 上でコンテナの取得, 展開, 実行を担うランタイム。 |
| ctr | ctr | containerd に付属する低レベル操作コマンド。image import によるコンテナイメージ登録やコンテナイメージへのタグ (tag) 付けに使用する。 |
| コンテナイメージ tar ファイル| - | コンテナイメージをアーカイブ化したファイル。呼び出し元ロールが事前準備する成果物。 |
| 未修飾名イメージ | - | レジストリ名が付かないイメージ名。例: `library/busybox:latest`。 |
| 既定レジストリ | - | 未修飾名イメージへ補完するレジストリ名。`k8s_register_image_unqualified_image_registry` で指定する。 |
| kubeconfig | kubeconfig | Kubernetes API 接続に必要な設定ファイル。worker ノードの自動検出時(K8sクラスタ内に含まれるワーカーノード群を列挙する際)に `kubectl` が参照する。 |

## 本ロールの動作仕様

本ロールの役割, 動作仕様は以下の通り。

- 呼び出し元ロールが制御ホスト上に準備したコンテナイメージ tar を, 対象ノード(control plane ノード, worker ノード)へ転送する。
- 対象ノード上で containerd の `ctr` コマンドを用いて image import を行う。
- 未修飾名のイメージについては, CRI の既定レジストリ解決差異を吸収するための別名タグを付与する。
- 本ロールは, コンテナイメージ tar を新しく作成したり, 外部から取得したりしない。利用者は, 配布対象の tar ファイルを制御ホスト上の所定ディレクトリに事前配置しておく。

## 呼び出し元ロールからの使用方法

本節では, 呼び出し元ロール作成者が本ロールを利用する際の使用法を述べる。

### 呼び出し元ロール作成者が実施する作業

呼び出し元ロール作成者が本ロールを利用する際に設定する変数と設定値の概要は以下の通り。

1. 登録対象コンポーネントの定義として以下の変数を設定する。
    1. `k8s_register_image_components`: 登録対象コンポーネント名と tar ファイル絶対パスの対応表
    2. `k8s_register_image_expected_images`: コンポーネント名とコンテナイメージ名の対応表
2. 対象ノードの指定方式として以下のいずれかを設定する。
    1. 明示指定:
         - `k8s_register_image_control_plane_hosts`: 登録対象の control plane ノード名配列を設定する (例: `['k8sctrlplane01.local', 'k8sctrlplane02.local']`)。
         - `k8s_register_image_worker_hosts`: 登録対象の worker ノード名配列を設定する (例: `['k8sworker0101.local', 'k8sworker0102.local']`)。
    2. 自動検出:
         - `k8s_register_image_auto_discover_worker_hosts`: worker ノードを自動検出する場合に `true` を設定する。
         - `k8s_kubeconfig_to_discover_workers_path`: worker ノード自動検出で `kubectl` が参照する kubeconfig ファイルパスを設定する(例: `/etc/kubernetes/admin.conf`)。
3. 実行時制御として以下の変数を設定する。
   1. `k8s_register_image_remote_cache_dir`: 対象ノードで tar を一時配置するディレクトリ
   2. `k8s_register_image_unqualified_image_registry`: 未修飾名イメージへ補完する既定レジストリ名
  3. `k8s_register_image_cleanup_remote_tar`: 登録後に対象ノード上の tar を削除する場合は `true`, 保持する場合は `false`
  4. `k8s_register_image_skip_discovery`: 対象ノード再探索を抑止する場合は `true`, 再探索を実行する場合は `false`

### 呼び出し元ロールでのパラメタの設定手順

1. 呼び出し元ロールで, 制御ホスト上に登録対象コンテナイメージ tar を配置する。
2. 呼び出し元ロールで, 本ロールに渡す入力パラメタを目的別に設定する。
   - コンポーネント定義: コンポーネント名と tar ファイルパス, 期待タグ
  - 対象ノード指定: control plane は明示指定, worker は明示指定または自動検出
   - 実行制御: 一時配置先, 未修飾名補完レジストリ, 後始末方針
3. `include_role` で `k8s-register-image` を呼び出し, 設定した入力パラメタを渡す。
4. 実行結果で, 対象ノード上の `ctr -n k8s.io images ls` を実行し, 期待したタグが登録されたことを確認する。

### 呼び出し元ロールから本ロールを呼び出すansibleタスクの記載方法

本節では, 呼び出し元ロールから本ロールを呼び出す際の ansible タスクの記載方法を例示する。

本稿では, 登録対象コンポーネント名, コンテナイメージ tar ファイル, コンテナイメージ名について, 以下を用いる:

|登録対象コンポーネント名|コンテナイメージ tar ファイル|コンテナイメージ名|
|---|---|---|
|manager|/opt/virtual-cluster/binary/manager-amd64.tar|virtualcluster/manager-amd64:latest|
|syncer|/opt/virtual-cluster/binary/syncer-amd64.tar|virtualcluster/syncer-amd64:latest|
|vn-agent|/opt/virtual-cluster/binary/vn-agent-amd64.tar|virtualcluster/vn-agent-amd64:latest|

#### コンテナイメージをcontrol plane ノード群に配布する場合の例

本節で示す処理内容の仕様は以下の通り。

- 登録対象コンポーネントとコンテナイメージ tar ファイル, コンテナイメージ名の対応表を定義する:
  - `k8s_register_image_components`: `コンポーネント名` から `コンテナイメージ tar ファイルへのパス` への辞書
  - `k8s_register_image_expected_images`: `コンポーネント名` から `コンテナイメージ名`への辞書
- control plane ノード群へ配布するために, 以下の設定を行う:
  - `k8s_register_image_control_plane_hosts` に control plane ノード一覧を設定する
- 配布時の一時配置先を `k8s_register_image_remote_cache_dir` へ設定
- 未修飾名イメージの補完先レジストリを `k8s_register_image_unqualified_image_registry` へ設定
- 登録後も対象ノード上のコンテナイメージ tar ファイルを削除せず保持するために `k8s_register_image_cleanup_remote_tar` に `false` を設定する。典型的な場合は, control plane ノードへの配布後に続けて worker ノードへの配布処理を行うためである。そのため, control plane ノードへの配布後に対象ノード上のコンテナイメージ tar ファイルを削除しないようにする。

本ロールを使用して上記のコンテナイメージを K8s の control plane ノード群に配布するタスクの記載例を以下に示す:

```yaml
1: - name: Register images via k8s-register-image
2:   ansible.builtin.include_role:
3:     name: k8s-register-image
4:     tasks_from: register-control-plane.yml
5:   vars:
6:     k8s_register_image_components:
7:       manager: "/opt/virtual-cluster/binary/manager-amd64.tar"
8:       syncer: "/opt/virtual-cluster/binary/syncer-amd64.tar"
9:       vn-agent: "/opt/virtual-cluster/binary/vn-agent-amd64.tar"
10:     k8s_register_image_expected_images:
11:       manager: "virtualcluster/manager-amd64:latest"
12:       syncer: "virtualcluster/syncer-amd64:latest"
13:       vn-agent: "virtualcluster/vn-agent-amd64:latest"
14:     k8s_register_image_control_plane_hosts:
15:       - "k8sctrlplane01.local"
16:       - "k8sctrlplane02.local"
17:     k8s_register_image_remote_cache_dir: "/tmp/vc-images"
18:     k8s_register_image_unqualified_image_registry: "docker.io"
19:     k8s_register_image_cleanup_remote_tar: false
```

上記例の各行での記載内容は以下の通り。

- 1-4 行目: `k8s-register-image` ロール呼び出し処理を実施するための記載である。
  - 1行目: タスクの名前を設定
  - 2行目: `include_role` モジュールを使用することを指定
  - 3行目: 呼び出すロール名(`k8s-register-image`)を指定
  - 4行目: 実行するタスクファイルにcontrol plane ノードへの配布処理(`register-control-plane.yml`)を指定
- 6-13 行目: 登録対象コンポーネント名, コンテナイメージ tar ファイル, コンテナイメージ名を指定するための設定である。
  - 6-9行目: 登録対象コンポーネント名をキーにコンテナイメージ tar ファイルを取得する辞書を設定
  - 10-13行目: 登録対象コンポーネント名をキーにコンテナイメージ名を取得する辞書を設定
- 14-16 行目: control plane ノード一覧を明示指定するための設定である。
- 17-19 行目: 一時配置先, 未修飾名補完レジストリ, 登録後の tar 保持方針を指定するための設定である。
  - 17行目: 対象ノード上で tar を一時配置するディレクトリ(`k8s_register_image_remote_cache_dir`)を指定
  - 18行目: 未修飾名イメージへ補完する既定レジストリ(`k8s_register_image_unqualified_image_registry`)を指定
  - 19行目: CRIへの登録後に対象ノード上の tar を削除せず保持する設定(`k8s_register_image_cleanup_remote_tar: false`)

#### コンテナイメージをworker ノード群に配布する場合の例

本節で示す処理内容の仕様は以下の通り。

- 登録対象コンポーネントとコンテナイメージ tar ファイル, コンテナイメージ名の対応表を定義する:
  - `k8s_register_image_components`: `コンポーネント名` から `コンテナイメージ tar ファイルへのパス` への辞書
  - `k8s_register_image_expected_images`: `コンポーネント名` から `コンテナイメージ名`への辞書
- worker ノード群へ配布するために, 以下の設定を行う:
  - `k8s_register_image_auto_discover_worker_hosts` を `true` に設定
  - worker ノード一覧の算出に使用する kubeconfig のパスを `k8s_kubeconfig_to_discover_workers_path` 変数に設定
- worker ノードへの配布処理の重複実行を抑止するために, 以下の設定を行う:
  - `k8s_register_image_control_plane_hosts` に control plane ノード一覧を明示指定する
- 配布時の一時配置先を `k8s_register_image_remote_cache_dir` へ設定
- 未修飾名イメージの補完先レジストリを `k8s_register_image_unqualified_image_registry` へ設定
- 登録後に対象ノード上のコンテナイメージ tar ファイルを削除するために `k8s_register_image_cleanup_remote_tar` に `true` を設定する。典型的な場合は, worker ノードへの配布処理が本節の処理の終端となるためである。そのため, 対象ノード上にコンテナイメージ tar ファイルを残さないようにする。

本ロールを使用して上記のコンテナイメージを K8s の worker ノード群に配布するタスクの記載例を以下に示す:

```yaml
1: - name: Register images via k8s-register-image
2:   ansible.builtin.include_role:
3:     name: k8s-register-image
4:     tasks_from: register-workers.yml
5:   vars:
6:     k8s_register_image_components:
7:       manager: "/opt/virtual-cluster/binary/manager-amd64.tar"
8:       syncer: "/opt/virtual-cluster/binary/syncer-amd64.tar"
9:       vn-agent: "/opt/virtual-cluster/binary/vn-agent-amd64.tar"
10:     k8s_register_image_expected_images:
11:       manager: "virtualcluster/manager-amd64:latest"
12:       syncer: "virtualcluster/syncer-amd64:latest"
13:       vn-agent: "virtualcluster/vn-agent-amd64:latest"
14:     k8s_register_image_control_plane_hosts:
15:       - "k8sctrlplane01.local"
16:       - "k8sctrlplane02.local"
17:     k8s_register_image_auto_discover_worker_hosts: true
18:     k8s_kubeconfig_to_discover_workers_path: "/etc/kubernetes/admin.conf"
19:     k8s_register_image_remote_cache_dir: "/tmp/vc-images"
20:     k8s_register_image_unqualified_image_registry: "docker.io"
21:     k8s_register_image_cleanup_remote_tar: true
```

上記例の各行での記載内容は以下の通り。

- 1-4 行目: `k8s-register-image` ロール呼び出し処理を実施するための記載である。
  - 1行目: タスクの名前を設定
  - 2行目: `include_role` モジュールを使用することを指定
  - 3行目: 呼び出すロール名(`k8s-register-image`)を指定
  - 4行目: 実行するタスクファイルに worker ノードへの配布処理(`register-workers.yml`)を指定
- 6-13 行目: 登録対象コンポーネント名, コンテナイメージ tar ファイル, コンテナイメージ名を指定するための設定である。
  - 6-9行目: 登録対象コンポーネント名をキーにコンテナイメージ tar ファイルを取得する辞書を設定
  - 10-13行目: 登録対象コンポーネント名をキーにコンテナイメージ名を取得する辞書を設定
- 14-16 行目: worker 配布時の実行主体判定に使う control plane ノード一覧を明示指定する設定である。
- 17-18 行目: worker ノードを自動検出するための設定である。
  - 17行目: worker ノードを自動検出する設定(`k8s_register_image_auto_discover_worker_hosts: true`)を指定
  - 18行目: worker ノード自動検出時に `kubectl` が参照する kubeconfig (`k8s_kubeconfig_to_discover_workers_path`)を指定
- 19-21 行目: 一時配置先, 未修飾名補完レジストリ, 登録後のコンテナイメージ tar ファイル削除方針を指定するための設定である。
  - 19行目: 対象ノード上でコンテナイメージ tar ファイルを一時配置するディレクトリ(`k8s_register_image_remote_cache_dir`)を指定
  - 20行目: 未修飾名イメージへ補完する既定レジストリ(`k8s_register_image_unqualified_image_registry`)を指定
  - 21行目: CRIへの登録後に対象ノード上のコンテナイメージ tar ファイルを削除する設定(`k8s_register_image_cleanup_remote_tar: true`)を指定


### 各パラメタ変数に設定する値

| 分類 | 変数 | 規定値 | 設定する値 |
| --- | --- | --- | --- |
| コンポーネント定義 | `k8s_register_image_components` | `{}` | コンポーネント名をキー, コンテナイメージ tar ファイルの絶対パスを値とする対応表を指定する。 |
| コンポーネント定義 | `k8s_register_image_expected_images` | `{}` | コンポーネント名をキー, コンテナイメージ名を値とする対応表を指定する。 |
| 対象ノード指定(明示指定時) | `k8s_register_image_control_plane_hosts` | `[]` | 登録対象の control plane ノード名配列を指定する。 |
| 対象ノード指定(明示指定時) | `k8s_register_image_worker_hosts` | `[]` | 登録対象の worker ノード名配列を指定する。 |
| 対象ノード指定(自動検出時) | `k8s_register_image_auto_discover_worker_hosts` | `false` | worker ノードを自動検出する場合に `true` を指定する。 |
| 対象ノード指定(明示指定補助) | `k8s_register_image_control_plane_group_name` | `"k8s_ctrl_plane"` | 呼び出し元で `groups[...]` を参照して control plane ノード一覧を組み立てる際のグループ名を指定する。 |
| 対象ノード指定(自動検出時) | `k8s_kubeconfig_to_discover_workers_path` | `""` | worker ノード自動検出時に `kubectl` が参照する kubeconfig パスを指定する。 |
| 実行制御 | `k8s_register_image_skip_discovery` | `false` | 対象ノード再探索を抑止する場合に `true` を指定する。 |
| 実行制御 | `k8s_register_image_remote_cache_dir` | `"/tmp/k8s-register-image"` | 対象ノード上でコンテナイメージ tar ファイルを一時配置するディレクトリを指定する。 |
| 実行制御 | `k8s_register_image_unqualified_image_registry` | `"docker.io"` | 未修飾名イメージへ補完する既定レジストリ名を指定する。 |
| 実行制御 | `k8s_register_image_cleanup_remote_tar` | `true` | 登録後に対象ノード上のコンテナイメージ tar ファイルを削除する場合は `true`, 保持する場合は `false` を指定する。 |


## 注意事項

- 対象ノードで `ctr` コマンドが利用可能であることを前提とする。
- 利用者は, 対象ノードで管理者権限のコマンド実行ができるように, 実行ユーザーの権限設定(sudo設定など)を事前に済ませておく。あわせて, 権限昇格時に対話入力が必要にならない設定であることを確認する。
- control plane ノードと worker ノードの一覧は, 呼び出し側で明示的に渡すか, 自動検出用変数を設定してロール側で検出する。
- 登録対象の tar ファイルは, Ansible 制御ノード上の指定ディレクトリに存在している必要がある。

- `k8s_register_image_cleanup_remote_tar` の設定は呼び出し元責務である。後続処理で同じ tar を再利用する場合は `false` を指定する。

## 検証ポイント

- control plane ノードと worker ノードの双方で, `ctr -n k8s.io images ls` にコンテナイメージ名とコンテナイメージ名に指定したタグ名が現れること。
- 未修飾名のイメージについて, コンテナイメージ名に指定したタグ名と別名タグ名の双方が登録されること。
