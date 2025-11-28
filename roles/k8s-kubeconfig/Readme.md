# k8s-kubeconfig ロール

このロールは Kubernetes ノードで利用する `kubeconfig` を生成, 統合, 配布し, オペレータ (`k8s_operator_user` 変数で定義, `kube` ユーザ) 用ホームディレクトリと `/etc/kubernetes` の両方を一貫した内容に保ちます。コントロールプレーン毎に証明書埋め込み版 `kubeconfig` を生成し, kubeconfigファイル結合ツール(`create-uniq-kubeconfig.py`) で複数クラスタコンテキストを統合した上で, 各ワーカーノードへも同じ内容を展開します。

以下では, `ansible-playbook` コマンド実行ノードを`制御ノード`と記載します。

## 実行フロー

1. `load-params.yml` でディストリビューション別パッケージ名, 共通設定, API エンドポイント定義などを読み込みます。
2. `prepare-vars.yml` が `kubeconfig` 関連パスを計算し, 埋め込みファイル名や `/etc/kubernetes` 配置先を決定します。
3. `directory.yml` で `/etc/kubernetes` と `{{ k8s_operator_user }}` の `~/.kube` を作成し, 必要な所有者, パーミッションを整えます。
4. `control-plane.yml` ( `k8s_ctrl_plane` グループのみ )では次を実施します。
   - `/etc/kubernetes/admin.conf` を `config-default` としてバックアップ。
   - `create-embedded-kubeconfig.py` を呼び出し, クラスタ毎の証明書埋め込み `kubeconfig` を生成。
   - 各コントロールプレーンから埋め込み `kubeconfig` を収集し, 一時ディレクトリに展開。
   - kubeconfigファイル結合ツール(`create-uniq-kubeconfig.py`) で `merged-kubeconfig.conf` を生成し, `/etc/kubernetes` と `~/.kube` に配布。
5. `distribute-workers.yml` ( `k8s_worker` グループのみ )はホスト変数 (`k8s_ctrlplane_host` 変数) で指定されたコントロールプレーンから `merged-kubeconfig.conf` を取得し, 制御ノード上の `~/.ansible/kubeconfig-cache/` に一旦保存してからワーカーノードへコピーします。
6. `symlink.yml` が `~/.kube/config` を `merged-kubeconfig.conf` への相対シンボリックリンクに置き換え, 従来ファイルは `config-default` に退避します。

## 主な生成物

| ファイル / ディレクトリ | 配置ホスト | 説明 |
| --- | --- | --- |
| `/etc/kubernetes/ca-embedded-admin.conf` | コントロールプレーン | 証明書を埋め込み済みの管理者 `kubeconfig`。`kubectl` をルート権限で利用するための控え。|
| `/etc/kubernetes/merged-kubeconfig.conf` | 全ノード | 全コントロールプレーンのコンテキストを統合した `kubeconfig`。コントロールプレイン/ワーカーノード共通で参照。|
| `~{{ k8s_operator_user }}/.kube/cluster*-embedded.kubeconfig` | コントロールプレーン | `create-embedded-kubeconfig.py` が生成するクラスタ固有の埋め込み版 kubeconfig。|
| `~{{ k8s_operator_user }}/.kube/ca-embedded-admin.conf` | コントロールプレーン | `/etc/kubernetes` に配置した埋め込み版のオペレータ控え。|
| `~{{ k8s_operator_user }}/.kube/merged-kubeconfig.conf` | 全ノード | `/etc/kubernetes/merged-kubeconfig.conf` のコピー。オペレータユーザが直接参照。|
| `~{{ k8s_operator_user }}/.kube/config -> merged-kubeconfig.conf` | 全ノード | 統合 `kubeconfig` への相対シンボリックリンク。既存ファイルは `config-default` にバックアップ。|

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_operator_user` | `kube` | `kubeconfig` を配置するオペレータユーザ。ホームディレクトリは `k8s_operator_home` 変数を参照します。|
| `k8s_embed_kubeconfig_script_path` | `/opt/k8snodes/sbin/create-embedded-kubeconfig.py` | 証明書埋め込み版 `kubeconfig` を生成するスクリプトパス。|
| `k8s_embed_kubeconfig_output_dir` | `{{ k8s_operator_home }}/.kube` | 埋め込み kubeconfig を出力するディレクトリ。|
| `k8s_embed_kubeconfig_file_postfix` | `-embedded.kubeconfig` | 埋め込み版 kubeconfig のファイル名サフィックス。|
| `k8s_create_unique_kubeconfig_script_path` | `/opt/k8snodes/sbin/create-uniq-kubeconfig.py` | 複数 `kubeconfig` を統合するスクリプトパス。|
| `k8s_kubeconfig_system_dir` | `/etc/kubernetes` | システム側 `kubeconfig` を配置するベースディレクトリ。|
| `k8s_embed_kubeconfig_shared_ca_path` | `""` | `control-plane.yml` で `create-embedded-kubeconfig.py` に渡す共通 CA のパス。未設定時は `/etc/kubernetes/admin.conf` に含まれるクラスタ CA をそのまま埋め込みます。|
| `k8s_kubeconfig_probe_timeout` | `15` | ワーカーノードが `k8s_ctrlplane_host` 変数へ接続確認する際のタイムアウト秒数。|
| `k8s_ctrlplane_host` | なし ( ホスト変数で必須 ) | ワーカーノードが `kubeconfig` を取得するコントロールプレーンホスト名。|

## 運用上の注意

- `create-embedded-kubeconfig.py` と kubeconfigファイル結合ツール(`create-uniq-kubeconfig.py`) は `k8s_node_setup_tools_dir` に事前配置しておく必要があります。
- `k8s_ctrl_plane` グループ以外でこのロールを実行すると埋め込み `kubeconfig` の生成はスキップされるため, ワーカーノードへ配布する前に必ずコントロールプレーンでロールを完了させてください。
- ワーカーノードごとの `k8s_ctrlplane_host` 変数を `host_vars/<worker>.yml` などで必ず定義してください。未定義の場合はタスクがエラーで停止します。
- `~/.ansible/kubeconfig-cache/` 配下にコントロールプレーンから取得した最新の `/etc/kubernetes/merged-kubeconfig.conf` をキャッシュし, ワーカーノードへ配布します。制御ノードでプレイブックを再実行しても同一ファイルを再利用できます。`~/.ansible/kubeconfig-cache/`は, `ansible-playbook` コマンド実行時のユーザ所有で 権限`0700` に設定されます。
- コントロールプレーンでロールが成功していない状態でワーカーノードのみ再配布すると, 過去にキャッシュしたファイルがそのまま配布されます。キャッシュ生成後にコントロールプレーン側の `/etc/kubernetes/merged-kubeconfig.conf` を更新し, ワーカーノードの処理だけを実行した場合は一貫性が崩れる可能性があるため, 本 playbook でコントロールプレーンの処理を完了させたうえでワーカーノードの処理を実行してください。
- `merged-kubeconfig.conf` は 0600 (システム/オペレータ共通) で配布されます。追加ユーザに読み取りを許可したい場合は別途 ACL やグループ管理を行ってください。
