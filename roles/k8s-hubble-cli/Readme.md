# k8s-hubble-cli ロール

Cilium Hubble の観測, デバッグ用 CLI ツールを Kubernetes ノードへ導入するロールです。

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
| 名前空間 ( namespace ) | - | Kubernetes内部でリソースを論理的に分離する単位。 |
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

本ロールは Cilium Hubble の観測, デバッグ用 CLI ツール (`hubble`) を GitHub 公式リリースから取得し, 各 Kubernetes ノードへ配置します。

主な機能:

- **GitHub releases からの直接取得**: 指定バージョンのバイナリ (`hubble-linux-amd64.tar.gz`) を GitHub から直接ダウンロードし, `/usr/local/bin/hubble` に配置します。
- **シェル補完の自動生成**: bash, zsh 向けに補完スクリプトを動的生成し, OS 別の標準パスへ配置します。Ubuntu と RHEL で補完スクリプトの配置先が異なりますが, 本ロールが自動的に差異を吸収します。
- **冪等性の確保**: 同一バージョンでの再実行時はダウンロード, インストールをスキップします。バージョン変更時は自動的に新バージョンを取得, 再配置します。
- **Python 3.12+ 対応**: Ansible 2.15 未満と Python 3.12 以上の組み合わせで発生する SSL/TLS 問題に対し, curl fallback により回避します。

## 前提条件

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- Ansible 2.15 以降推奨 (2.15 未満の場合 Python 3.12+ 環境で curl fallback を使用)
- リモートホストへの SSH 接続が確立されていること
- 管理者権限 (sudo) が利用可能であること
- **`hubble_cli_version` が定義されていること (必須)**: `vars/all-config.yml`, `group_vars`, `host_vars` のいずれかで明示的に設定してください
- Ansible 実行ホストから GitHub (`https://github.com`) へのネットワークアクセスが可能であること

## 実行フロー

本ロールは以下の順序で処理を実行します:

1. **パラメータ読み込み** (`load-params.yml`): OS 別パッケージ定義 (`vars/packages-ubuntu.yml`, `vars/packages-rhel.yml`) とクロスディストロ変数 (`vars/cross-distro.yml`), 共通変数 (`vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込みます。`hubble_cli_version` を正規化 (trim) し, 未定義の場合は assert で失敗します。
2. **前提パッケージインストール** (`package.yml`): `curl`, `tar`, `gzip` をインストールします (OS 別 vars で定義)。
3. **ディレクトリ作成** (`directory.yml`):
   - 一時作業ディレクトリ (`/tmp/hubble-cli-v{version}`, mode: `0755`)
   - インストールディレクトリ (`/usr/local/bin`, mode: `0755`)
   - bash 補完ディレクトリ (`/etc/bash_completion.d`, mode: `0755`)
   - zsh 補完ディレクトリ (Ubuntu: `/usr/share/zsh/vendor-completions`, RHEL: `/usr/share/zsh/site-functions`, mode: `0755`)
4. **ユーザ, グループ作成** (`user_group.yml`): 現状プレースホルダ (実処理なし)。
5. **サービス設定** (`service.yml`): 現状プレースホルダ (実処理なし)。
6. **バイナリ, 補完スクリプト配置** (`config.yml`):
   - GitHub releases からアーカイブダウンロード (Ansible 2.15+ では `get_url`, 2.15 未満 & Python 3.12+ では curl workaround)
   - アーカイブ展開 (`unarchive`, `creates` 句で冪等性確保)
   - バイナリインストール (`/usr/local/bin/hubble`, owner: `root`, group: `root`, mode: `0755`)
   - bash 補完生成, 配置 (`hubble completion bash` → `/etc/bash_completion.d/hubble`, mode: `0644`)
   - zsh 補完生成, 配置 (`hubble completion zsh` → OS 別パス, mode: `0644`)

## 主要変数

本ロールで扱う主な変数と用途を示します。変数は `group_vars`, `host_vars`, または `vars/all-config.yml` で上書きできます。

### バージョン, リポジトリ設定

| 変数名 | 既定値 | 説明 |
| ------ | ------ | ---- |
| `hubble_cli_version` | `"1.18.3"` | **必須**。配布する Hubble CLI のバージョン。未定義の場合はロール冒頭で assert が失敗します。 |
| `hubble_cli_github_repo` | `"cilium/hubble"` | リリースを参照する GitHub リポジトリ。独自フォークを使用する場合に変更します。 |
| `hubble_cli_release_tag_prefix` | `"v"` | GitHub リリースタグの接頭辞。通常は `v{version}` 形式です。 |
| `hubble_cli_download_url` | (自動構築) | ダウンロード URL。既定値は上記パラメータから自動構築されます。社内ミラーを利用する場合に上書きします。 |

### インストール設定

| 変数名 | 既定値 | 説明 |
| ------ | ------ | ---- |
| `hubble_cli_install_dir` | `"/usr/local/bin"` | バイナリ配置先ディレクトリ。 |
| `hubble_cli_binary_name` | `"hubble"` | 配置するバイナリ名。 |
| `hubble_cli_temp_parent` | `"/tmp"` | 一時作業ディレクトリの親ディレクトリ。特殊なディスクレイアウトの場合に変更します。 |
| `hubble_cli_temp_dir` | `"/tmp/hubble-cli-v{version}"` | アーカイブ展開用一時ディレクトリ。 |
| `hubble_cli_packages` | (OS 別) | 依存パッケージリスト。`vars/packages-ubuntu.yml` / `vars/packages-rhel.yml` で OS ごとに定義 (`curl`, `tar`, `gzip`)。 |

### 補完設定

| 変数名 | 既定値 | 説明 |
| ------ | ------ | ---- |
| `hubble_cli_completion_enabled` | `true` | `true` で bash/zsh 補完スクリプトを生成, 配置。`false` で補完処理をスキップ。 |
| `hubble_cli_bash_completion_path` | `/etc/bash_completion.d/hubble` | bash 補完スクリプトの配置先 (`vars/cross-distro.yml` で定義, Ubuntu/RHEL 共通)。 |
| `hubble_cli_zsh_completion_path` | (OS 別) | zsh 補完スクリプトの配置先 (`vars/cross-distro.yml` で定義)。Ubuntu: `/usr/share/zsh/vendor-completions/_hubble`, RHEL: `/usr/share/zsh/site-functions/_hubble`。 |

## テンプレートとファイル

本ロールは, テンプレートファイル自体は利用せず, すべての設定ファイルをランタイムで生成します。生成されるファイルを以下に示します。

| パス | 権限 | 役割 |
| ---- | ---- | ---- |
| `{{ hubble_cli_install_dir }}/hubble` | `0755` (root:root) | Hubble CLI バイナリ本体。GitHub リリースから直接ダウンロード。 |
| `{{ hubble_cli_bash_completion_path }}` (既定: `/etc/bash_completion.d/hubble`) | `0644` (root:root) | bash 補完スクリプト。`hubble completion bash` の出力をリダイレクトして生成。 |
| `{{ hubble_cli_zsh_completion_path }}` (Ubuntu: `/usr/share/zsh/vendor-completions/_hubble`) | `0644` (root:root) | zsh 補完スクリプト (Ubuntu)。`hubble completion zsh` の出力をリダイレクトして生成。 |
| `{{ hubble_cli_zsh_completion_path }}` (RHEL: `/usr/share/zsh/site-functions/_hubble`) | `0644` (root:root) | zsh 補完スクリプト (RHEL/Alma Linux)。`hubble completion zsh` の出力をリダイレクトして生成。 |
| `{{ hubble_cli_temp_dir }}` (既定: `/tmp/hubble-cli-v{{ hubble_cli_version }}`) | 一時 | アーカイブ展開用ワークスペース。処理完了後に削除されます。 |

テンプレートを利用しない理由は, Hubble CLI 自体が補完スクリプトを生成できるため, 常に実行中のバージョンと整合性のある補完候補が提供される点にあります。

## 実行方法

### 単独実行

```bash
ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml --tags k8s-hubble-cli
```

### 他のロールと組み合わせて実行

```bash
ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml --tags k8s-common,k8s-hubble-cli
```

### 特定ホストに限定

```bash
ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml --limit k8sctrlplane01.local --tags k8s-hubble-cli
```

## 設定例

### 基本設定 (必須変数のみ)

`vars/all-config.yml` に Hubble CLI バージョンを指定します。

```yaml
# Hubble CLI バージョン
hubble_cli_version: "1.18.3"
```

このように `hubble_cli_version` を指定すれば, 他の変数は既定値で動作します。

### 社内ミラー利用

独自ミラーアーカイブへパスを差し替える例です。

```yaml
hubble_cli_version: "1.18.3"
hubble_cli_download_url: "https://mirror.example.org/hubble/v{{ hubble_cli_version }}/hubble-linux-amd64.tar.gz"
```

### 補完スクリプトを無効化

開発環境や CI/CD サーバーなど, 補完スクリプトが不要な場合に `hubble_cli_completion_enabled` を `false` に設定します。

```yaml
hubble_cli_version: "1.18.3"
hubble_cli_completion_enabled: false
```

### カスタムインストールパス

`/opt/bin` など独自パスへ配置する場合の例です。

```yaml
hubble_cli_version: "1.18.3"
hubble_cli_install_dir: "/opt/bin"
```

## 設定内容の検証

Ansible 実行後, 以下の項目を確認することで, Hubble CLI が正しく導入されているか検証できます。

### 1. Hubble CLI バイナリの配置確認

**実施ホスト:** 対象 Kubernetes ノード (コントロールプレーン / ワーカーノード)

**コマンド:**

```bash
ls -l /usr/local/bin/hubble
hubble version
```

**期待される出力:**

```plaintext
-rwxr-xr-x 1 root root 12345678 Jan  1 12:34 /usr/local/bin/hubble

hubble v1.18.3 compiled with go1.23.4 on linux/amd64
```

**確認ポイント:**
- `/usr/local/bin/hubble` が `root:root`, `0755` で配置されていること
- `hubble version` が `vars/all-config.yml` で指定した `hubble_cli_version` と一致すること
- バイナリサイズが極端に小さくない (通常10MB以上) こと

### 2. bash 補完スクリプトの配置確認

**実施ホスト:** 対象 Kubernetes ノード (コントロールプレーン / ワーカーノード)

**コマンド:**

```bash
ls -l /etc/bash_completion.d/hubble
cat /etc/bash_completion.d/hubble | head -n 5
source /etc/bash_completion.d/hubble
hubble <Tab><Tab>
```

**期待される出力:**

```plaintext
-rw-r--r-- 1 root root 45678 Jan  1 12:34 /etc/bash_completion.d/hubble

# bash completion for hubble                               -*- shell-script -*-
# This file was generated by the application.
# You should not modify this file directly.

<Tab><Tab> 実行時に補完候補が表示される (completion, config, observe, status, version など)
```

**確認ポイント:**
- `/etc/bash_completion.d/hubble` が `root:root`, `0644` で配置されていること
- ファイル先頭に `# bash completion for hubble` 等のコメントが含まれていること
- `source` 後に `hubble <Tab><Tab>` でサブコマンド候補 (`completion`, `observe`, `status`, `version` 等) が表示されること

### 3. zsh 補完スクリプトの配置確認 (Ubuntu)

**実施ホスト:** 対象 Kubernetes ノード (Ubuntu)

**コマンド:**

```bash
ls -l /usr/share/zsh/vendor-completions/_hubble
cat /usr/share/zsh/vendor-completions/_hubble | head -n 5
autoload -Uz compinit && compinit
hubble <Tab>
```

**期待される出力:**

```plaintext
-rw-r--r-- 1 root root 23456 Jan  1 12:34 /usr/share/zsh/vendor-completions/_hubble

#compdef hubble
# This file was generated by the application.
# You should not modify this file directly.

<Tab> 実行時に補完候補が表示される (completion, config, observe, status, version など)
```

**確認ポイント:**
- `/usr/share/zsh/vendor-completions/_hubble` が `root:root`, `0644` で配置されていること
- ファイル先頭に `#compdef hubble` コメントが含まれていること
- `compinit` 後に `hubble <Tab>` でサブコマンド候補が表示されること

### 4. zsh 補完スクリプトの配置確認 (RHEL/Alma Linux)

**実施ホスト:** 対象 Kubernetes ノード (RHEL/Alma Linux)

**コマンド:**

```bash
ls -l /usr/share/zsh/site-functions/_hubble
cat /usr/share/zsh/site-functions/_hubble | head -n 5
autoload -Uz compinit && compinit
hubble <Tab>
```

**期待される出力:**

```plaintext
-rw-r--r-- 1 root root 23456 Jan  1 12:34 /usr/share/zsh/site-functions/_hubble

#compdef hubble
# This file was generated by the application.
# You should not modify this file directly.

<Tab> 実行時に補完候補が表示される (completion, config, observe, status, version など)
```

**確認ポイント:**
- `/usr/share/zsh/site-functions/_hubble` が `root:root`, `0644` で配置されていること (Ubuntu と異なり `site-functions` 配下)
- ファイル先頭に `#compdef hubble` コメントが含まれていること
- `compinit` 後に `hubble <Tab>` でサブコマンド候補が表示されること
- Ubuntu との相違点: パスが `/usr/share/zsh/vendor-completions/_hubble` ではなく `/usr/share/zsh/site-functions/_hubble` であること

## バージョン更新の指針

1. 新しいバージョンへ更新する際は, `hubble_cli_version` を変更し, 必要なら `hubble_cli_download_url` を同じタグへ揃えます。
2. 再度ロールを適用すると, 新しいアーカイブをダウンロードして既存バイナリを上書きします。
3. ロール適用後, `hubble version` と補完機能が新バージョンで動作することを確認してください。

## トラブルシューティング

### 1. ダウンロードに失敗する

**原因:** GitHub へのネットワーク接続に失敗しているか, 指定したバージョンが存在しないか, Python 3.12+ 環境で Ansible < 2.15 を使用している可能性があります。

**対処:**
- `curl -L https://github.com/cilium/hubble/releases/download/v{{ hubble_cli_version }}/hubble-linux-amd64.tar.gz` で対象ホストから直接ダウンロードできるか確認します。
- 接続できる場合は, バージョン番号 (`hubble_cli_version`) とタグ形式 (`hubble_cli_release_tag_prefix`) が正しいか確認します。
- Python 3.12+ 環境で Ansible < 2.15 を使用している場合, urllib3 の SSL/TLS 問題により失敗する可能性があります。この場合, Ansible を 2.15+ へ更新するか, 本ロールが自動で利用する curl フォールバック機構 (タスク `tasks/config/download-hubble-cli-binary.yml` で実装) が動作していることを確認します。
- 社内プロキシを利用する場合, `hubble_cli_download_url` を内部ミラーへ変更します。

### 2. Python 3.12+ 環境でダウンロードに失敗する

**原因:** Ansible の `ansible.builtin.unarchive` モジュールがリモート URL を指定した際, Python 3.12+ の urllib3 SSL/TLS 変更により動作しないことがあります (Ansible < 2.15)。

**対処:**
- Ansible 2.15+ へ更新することが推奨されます。
- 本ロールは自動的に curl フォールバック処理 (タスク `tasks/config/download-hubble-cli-binary.yml` で実装) を使用してダウンロードするため, 通常は影響を受けません。curl が正しくインストールされているか確認してください。

### 3. 補完が動作しない

**原因:** bash/zsh の補完スクリプトが読み込まれていない, または `hubble_cli_completion_enabled: false` で無効化されています。

**対処:**
- bash の場合, `source /etc/bash_completion.d/hubble` を実行してから `hubble <Tab>` を試します。
- zsh の場合, `autoload -Uz compinit && compinit` を実行してから `hubble <Tab>` を試します。
- `hubble_cli_completion_enabled` が `true` になっているか確認します。

### 4. 一時ディレクトリが残る

**原因:** Ansible 実行が途中で失敗し, クリーンアップタスクが実行されませんでした。

**対処:**
- 手動で一時ディレクトリを削除します。
  ```bash
  rm -rf /tmp/hubble-cli-v{{ hubble_cli_version }}
  ```
- 次回実行時, ロールは同じ一時ディレクトリを再利用するため, 通常は問題になりません。

## 参考リンク

- [Hubble CLI GitHub リポジトリ](https://github.com/cilium/hubble): リリース情報と使用方法
- [Hubble 公式ドキュメント](https://docs.cilium.io/en/stable/observability/hubble/): Hubble の機能と設定ガイド
- [Cilium 公式サイト](https://cilium.io/): Cilium エコシステム全体の情報

## 備考

- プロキシ環境やオフライン環境で利用する場合は, あらかじめダウンロードしたアーカイブを内部リポジトリに配置し, `hubble_cli_download_url` を差し替えてください。
- `hubble_cli_completion_enabled` を `false` にすると補完スクリプト生成をスキップできます。端末ごとに利用したい場合, ホスト変数で切り替えてください。
- 依存パッケージは OS ファミリーごとに `vars/packages-*.yml` で管理しているため, 新たなユーティリティが必要になった場合は該当ファイルへ追記します。
