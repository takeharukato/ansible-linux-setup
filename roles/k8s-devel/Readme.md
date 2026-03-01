# k8s-devel ロール

Kubernetes 開発向けの言語別 Client ライブラリ導入を行うロールです。対象言語は Python, Go, C ( 将来対応 ) です。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウエアです。 |
| Python Package Installer | pip | Python パッケージを導入するためのツールです。 |
| Go toolchain | - | Go のビルド, 依存解決, テストに必要な基本ツール群です。 |
| client-go | - | Go から Kubernetes API を操作するための公式ライブラリです。 |
| etcd | - | Kubernetes の設定情報と状態を保存する分散キーバリューストアです。 |
| kube-apiserver | - | Kubernetes API サーバーで, API リクエストを受け付けて処理するコンポーネントです。 |
| kube-scheduler | - | Kubernetes スケジューラーで, ポッド ( Pod ) を適切なノードに配置するコンポーネントです。 |
| kube-controller-manager | - | Kubernetes コントローラーマネージャーで, リソースの状態を監視して制御するコンポーネントです。 |
| コントロールプレーンノード ( Control Plane Node ) | - | Kubernetes クラスタを制御するためのコンポーネント(API サーバー, スケジューラー, コントローラーマネージャー, etcd など)が動作し, クラスタ全体の制御と調整を行うノードです。 |
| ワーカーノード ( Worker Node ) | - | Kubernetes クラスタで実際にアプリケーション(ポッド ( Pod ))が実行されるノード。kubelet と呼ばれるエージェントが動作し, コントロールプレーンノードからの指示に基づいてコンテナを実行管理します。 |
| コンテナ ( Container ) | - | アプリケーションと依存関係を一つのパッケージ化したものです。軽量で, どの環境でも一貫して実行可能です。 |
| ポッド ( Pod ) | - | Kubernetes の最小デプロイメント単位です。1 個以上のコンテナ ( Container ) で構成される実行環境で, ポッド ( Pod ) 内のすべてのコンテナ ( Container ) は共有ネットワーク(共用 IP, ポート), 共有ストレージによって密接に結合され, 同一ノード上で常に共存, 同期スケジュール されます。 |

## 前提条件

- 対象 OS は Ubuntu 24.04, RHEL 9.6 系を想定します。
- `repo-deb` または `repo-rpm` が先に適用され, `k8s_major_minor` が定義されていることを前提とします。
- `go_lang_version` を指定する場合, Ansible 実行ホスト (localhost) から Go 公式サイト (`https://go.dev/dl/`) へのネットワークアクセスが必須です。
- Ubuntu 24.04 以降では PEP 668 (外部管理環境) により, システム Python への直接インストールが制限されています。本ロールでは自動的に `--break-system-packages` オプションを付与してインストールします。

## 実行フロー

1. `load-params.yml` で OS 別パッケージ定義と共通変数を読み込みます。
2. `post-load-params.yml` で `k8s_major_minor` から版数既定値を導出します。
3. `package.yml` で前提パッケージ, Python client, Go client, C client(将来サポート予定) を順に処理します。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_devel_python_client_enabled` | `false` | Python Kubernetes client を導入する場合は, `true`に設定します。 |
| `k8s_devel_go_client_enabled` | `false` | Go Kubernetes client を導入する場合は, `true`に設定します。 |
| `k8s_devel_c_client_enabled` | `false` | C Kubernetes client を導入する場合は, `true`に設定します。将来サポート予定。 |
| `k8s_devel_go_packages_enabled` | `false` | Go 最小ツールチェーンを導入する場合は, `true`に設定します。 |
| `go_lang_version` | `""` | Go 言語版数。空文字列の場合は OS 提供パッケージを `latest` で導入します。`x.y` 形式 (例: `1.18`) を指定すると該当系列の最新版 (例: `1.18.10`) を Go 公式から自動取得します。`x.y.z` 形式 (例: `1.18.5`) を指定するとその正確なバージョンを取得します。指定バージョンが Go 公式に存在しない場合は警告メッセージを表示してスキップします。 |
| `go_lang_remove_existing_package` | `true` | `go_lang_version` 指定時に既存の Go パッケージを削除するか制御します。`true` の場合は既存パッケージを削除してから tarball をインストールし, `false` の場合は既存パッケージを残したまま tarball をインストールします (PATH の優先順位に注意が必要です)。 |
| `k8s_devel_python_client_version` | `""` | Python client 版数。空文字列時は `k8s_major_minor` (例: `1.31`) から `~=<minor>.0` (例: `~=31.0`) を導出します。`~=` は互換バージョン指定 (PEP 440) で, 該当系列 (例: `31.0.0`, `31.1.0`, `31.2.3` など, ただし `32.0.0` 未満) の最新版を pip が自動選択します。 |
| `k8s_devel_go_client_version` | `""` | Go client 版数。空文字列時は `k8s_major_minor` (例: `1.31`) から `v0.<minor>.0` (例: `v0.31.0`) を導出します。client-go は常にメジャー版数が `0` で, Kubernetes のマイナー版数がそのままマイナー版数になります。 |
| `k8s_devel_go_work_dir` | `"/opt/k8s-devel/go-client"` | Go client 導入用作業ディレクトリ。`go mod init` と `go get` を実行し, `go.mod`, `go.sum` を配置するディレクトリです。実際の client-go ライブラリは Go のモジュールキャッシュにダウンロードされます。 |

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

## 主な処理

- Python client は `ansible.builtin.pip` で `kubernetes<python_client_version>` を導入します。
  (`<python_client_version>` は `k8s_devel_python_client_version` の値, または, その既定値 (例: `~=31.0`) を使用します)
  - Ubuntu 24.04 以降では PEP 668 対応のため, 自動的に `--break-system-packages` オプションを付与します。
- Go client は `go mod init` と `go get k8s.io/client-go@<go_client_version>` で導入します。
  (`<go_client_version>` は `k8s_devel_go_client_version` の値, または, その既定値を使用します)
- Go 基盤導入は Go client 導入と分離しています。`k8s_devel_go_packages_enabled=true` の場合, client 導入有無に関わらず Go を導入します。
- Go 基盤パッケージの導入フロー:
  (以下, `<go_lang_version>` は `go_lang_version` 変数に指定された値を示します)
  - `go_lang_version` 未指定時: OS 提供パッケージの最新版 ( `latest` ) をパッケージマネージャ経由で導入します。 Go コマンドパスは `/usr/bin/go`になります。
  - `go_lang_version` 指定時 (x.y または x.y.z 形式):
    - `go_lang_remove_existing_package=true` (既定値) の場合, 既存の Go パッケージを削除してから tarball をインストールします。
    - Go 公式API (`https://go.dev/dl/?mode=json&include=all`) からバージョン情報を取得, 解析し, 以下の手順でインストールします:
      - x.y 形式の場合は該当系列の最新パッチ版を自動検出 (例: `1.18` => `1.18.10`)。
      - x.y.z 形式の場合は指定されたバージョンを使用。
      - インストールする Go の tarball を Go 公式サイト ( `https://go.dev/dl/go<version>.linux-<arch>.tar.gz` )からダウンロード, 展開 (`<version>` はインストールする Go 言語のバージョン, `<arch>` は導入先ホストのアーキテクチャを示します)します。
      - 既存インストールディレクトリ (`/usr/local/go`) は削除してから新規導入します。Go コマンドは `/usr/local/go/bin/go` にインストールされます。
      - 指定されたバージョンがGo 公式API中に見つからない場合は警告ログを出力し, インストール処理をスキップします。
      - 注意: `include=all` パラメータを使用して, 過去のリリース系列 (例: 1.18.x) も含めて検索します。
- Go コマンドパス (`{{ go_command }}`) は インストール方法に応じて自動設定されます (パッケージ: `/usr/bin/go`, tarball: `/usr/local/go/bin/go`)。
- C client は将来対応予定です。

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

## 検証ポイント

- `k8s_major_minor` から Python client, Go client の既定版数が期待通り導出されます。
- `k8s_devel_go_packages_enabled=true` で Go 基盤が導入されます。
- `go_lang_version=""` (未指定) の場合, パッケージマネージャから Go が導入されます。
- `go_lang_version="1.18"` など x.y 形式の場合, Go 公式サイトから該当系列の最新版を自動検出, 導入できます。
- `go_lang_version="1.18.10"` など x.y.z 形式の場合, 指定バージョンが Go 公式から導入されます。
- `go_lang_version` 指定時, Go tarball が `/usr/local/go` に正常に展開されます。
- `go_lang_version` 指定時, PATH 設定スクリプト `/etc/profile.d/golang.sh` が配置されます。
- `k8s_devel_go_client_enabled=true` で `{{ k8s_devel_go_work_dir }}` 配下に `go.mod` が作成されます。
- `k8s_devel_go_packages_enabled=true` で `go version` コマンドが正常に実行されます。
- `k8s_devel_python_client_enabled=true` で pip から `kubernetes` パッケージが導入されます。
- `k8s_devel_c_client_enabled=true` でも処理失敗せず, 将来サポート予定として完了します。

## 検証手順例

### 前提条件

- 事前に `repo-deb` または `repo-rpm` が適用され, `k8s_major_minor` が有効であること。
- 対象ノードが inventory 上で `k8s_ctrl_plane`, `k8s_worker`, `devel`, `internal_devel` のいずれかのグループに所属していること。

### 1. Go 基盤をパッケージマネージャ経由でインストールしている場合の確認事項

パッケージマネージャからGo 基盤をインストールしている場合の確認手順は以下の通りです:

1. `k8s_devel_go_packages_enabled=true`, `go_lang_version=""` (未指定), `k8s_devel_go_client_enabled=false` を設定します。
2. プレイブックを実行し, `golang` パッケージが導入されることを確認します。
3. `go version` で Go のバージョンが表示されることを確認します。

確認する内容:

Go コマンドパス ( `/usr/bin/go` )にGo言語がインストールされていることを確認してください。

### 2. Go tarball からGo 基盤をインストールしている場合の確認事項

Go 公式サイトからtarballをインストールしている場合の確認手順は以下の通りです:

1. `k8s_devel_go_packages_enabled=true`, `go_lang_version="1.18"` (x.y 形式) (または, `go_lang_version="1.22.5"` (x.y.z 形式) ) を設定し, プレイブックを実行します。
2. `go version` で Go のバージョンが表示されることを確認します。

確認する内容:

- Go 基盤 が `/usr/local/go` に展開されていることを確認します
- Go コマンドパス ( `/usr/local/go/bin/go` ) に Go言語がインストールされていることを確認します。
- PATH 設定スクリプト `/etc/profile.d/golang.sh` が配置されていることを確認します。
- 指定されたバージョンのGo 言語がインストールされていることを確認します。

### 3. Go client 導入の確認

1. `k8s_devel_go_client_enabled=true` を設定します。
2. プレイブックを実行します。

確認する内容:

- `{{ k8s_devel_go_work_dir }}` (規定: `"/opt/k8s-devel/go-client"` ) 配下に `go.mod`, `go.sum` が作成されることを確認します。

### 4. Python client 導入の確認

1. `k8s_devel_python_client_enabled=true` を設定します。
2. プレイブックを実行します。

確認する内容:

- pip で `kubernetes` パッケージが導入されることを確認します。
- 以下のコマンドで, 導入済み版数と実ファイルパスを確認します。

```bash
python3 -m pip show kubernetes
python3 -c 'import kubernetes; print(kubernetes.__version__)'
python3 -c 'import kubernetes; print(kubernetes.__file__)'
```

- パス確認の目安は以下です。
  - Ubuntu 24.04: `/usr/local/lib/python3.12/dist-packages/kubernetes/__init__.py`
  - RHEL 9.6: `/usr/local/lib/python3.9/site-packages/kubernetes/__init__.py`
- 版数未指定時は `k8s_major_minor` の マイナーバージョンに合わせた版数のPython clientが導入されます。

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
