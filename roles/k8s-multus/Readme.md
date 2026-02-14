# k8s-multus ロール

Kubernetes コントロールプレーンノード上に Multus CNI を導入するロールです。`k8s-common`, `k8s-ctrlplane` で整えた共通前提の上で, Multus を Helm もしくは `kubectl apply` で導入します。再実行にも対応するよう設計されています。

## 実行フロー

1. `load-params.yml` で OS 別パッケージ定義 (`vars/packages-*.yml`) とクラスタ共通変数 (`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込みます。
2. `package.yml` を読み込みます (現状はタスクなしのプレースホルダです)。
3. `directory.yml` が Multus 用の設定ディレクトリ (既定では `{{ k8s_kubeadm_config_store }}/multus`) を作成します。
4. `user_group.yml` と `service.yml` は将来の拡張用に読み込まれます (現状はタスクなし)。
5. `config-cleanup-multus.yml` は `k8s_multus_enabled` 有効かつ `k8s_multus_cleanup_resources` が `true` の場合に発動し, 以前のインストール方式 ( `kubectl apply` ) で作成された DaemonSet / ClusterRole / ServiceAccount など Multus 関連リソースを削除してクリーンな環境を確保します。Helm への移行時に有効化してください。
6. `config-multus.yml` は `k8s_multus_enabled` 有効かつ `k8s_multus_kubectl_apply_enabled` が `false` の場合に発動し, Helm Chart をリモートホストにコピーし, Multus values (`templates/multus-values.yml.j2`) を生成してから, リモートホスト上の Chart から `helm upgrade --install` を実行して Multus CNI を導入します。
7. `config-kubectl-applied-multus.yml` は `k8s_multus_enabled` 有効かつ `k8s_multus_kubectl_apply_enabled` が `true` の場合に発動し, 公式マニフェストを `kubectl apply` により導入します (後方互換性のためのオプション経路)。
8. `directory-multus-test-pod.yml` は `k8s_multus_enabled` 有効時に Multus テスト用 Pod マニフェストを配置します。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_ctrlplane_endpoint` | 各ホストの `host_vars` で指定 | Control Plane API の広告アドレス (IPv4/IPv6)。本ロール内の待機処理で使用。|
| `k8s_kubeadm_config_store` | `{{ ansible_home_dir }}/kubeadm` | Multus 設定ファイル生成のルートディレクトリ。|
| `k8s_operator_user` | `kube` | オペレータユーザ名 (将来の拡張用に保持)。|
| `k8s_operator_home` | `/home/kube` | オペレータユーザのホームディレクトリ。|
| `k8s_operator_shell` | `/bin/bash` | オペレータユーザのデフォルトシェル。|
| `k8s_operator_groups_list` | `{{ adm_groups }}` | オペレータユーザの所属グループ。|
| `k8s_multus_enabled` | `false` | Multus 関連タスクを実行するかどうか。|
| `k8s_multus_config_dir` | `{{ k8s_kubeadm_config_store }}/multus` | Multus 設定ファイル ( values など ) の生成先ディレクトリ。|
| `k8s_multus_version` | `v4.2.3` | Multus のバージョン ( `kubectl apply` 方式でも Helm 方式でも参照 ) 。|
| `k8s_multus_helm_chart_version` | `{{ k8s_multus_version }}` | Multus Helm チャートのバージョン。|
| `k8s_multus_helm_chart_source` | `{{ role_path }}/files/multus-chart` | ローカルの Multus Helm チャートソースディレクトリ ( Helm 方式で使用 ) 。|
| `k8s_multus_helm_chart_path` | `{{ k8s_multus_config_dir }}/chart` | リモートホストに複製される Multus Helm チャートのパス ( Helm 方式で使用 ) 。|
| `k8s_multus_image_repository` | `ghcr.io/k8snetworkplumbingwg/multus-cni` | Multus コンテナイメージのリポジトリ。|
| `k8s_multus_image_version` | `{{ k8s_multus_version }}` | Multus コンテナイメージのタグ。|
| `k8s_multus_cni_bin_dir` | `/opt/cni/bin` | Multus CNI バイナリディレクトリ。|
| `k8s_multus_cni_conf_dir` | `/etc/cni/net.d` | Multus CNI 設定ディレクトリ。|
| `k8s_multus_install_type` | `thin` | Multus インストールタイプ。`thin` (軽量版) または `thick` (フル機能版) を指定します。|
| `k8s_multus_cleanup_resources` | `true` | 既存の Multus DaemonSet / ClusterRole / ServiceAccount などを削除してから再インストールするか (Helm への移行時)。`false` に設定するとクリーンアップをスキップします。|
| `k8s_multus_daemonset_manifest_url` | `https://raw.githubusercontent.com/k8snetworkplumbingwg/multus-cni/refs/tags/{{ k8s_multus_version }}/deployments/multus-daemonset.yml` | Multus DaemonSet の公式マニフェスト URL (`k8s_multus_kubectl_apply_enabled` が `true` の場合に使用)。|
| `k8s_multus_kubectl_apply_enabled` | `false` | Multus CNI を公式マニフェストで `kubectl apply` により導入する場合は `true` に設定します。本変数が `false` の場合, Helm Chart を用いて Multus を導入します。|

その他, `vars/cross-distro.yml` と `vars/all-config.yml` に含まれる共通変数は, 本ロール内のテンプレートや待機処理で参照されます。

## 主な処理

- **Multus 導入 (Helm)**: ローカル Helm Chart (`files/multus-chart/`) をリモートホストにコピーし, values を生成して `helm upgrade --install` を実行します。
- **Multus 導入 (kubectl apply)**: `k8s_multus_kubectl_apply_enabled: true` の場合に公式マニフェストを適用します (後方互換性のための経路)。
- **既存リソースのクリーンアップ**: `k8s_multus_cleanup_resources: true` の場合に旧方式のリソースを削除してから再導入します。
- **テスト用 Pod マニフェスト配置**: `templates/app-pod.yml.j2` から動作確認用 Pod マニフェストを生成し配置します。

## テンプレート／ファイル

| テンプレート/ファイル | 用途 | インストール先パス |
| --- | --- | --- |
| `templates/multus-values.yml.j2` | Multus CNI Helm values。 | `{{ k8s_multus_config_dir }}/multus-values.yml` (既定: `/home/ansible/kubeadm/multus/multus-values.yml`) |
| `templates/app-pod.yml.j2` | Multus 接続テスト用 Pod マニフェスト。 | `{{ k8s_multus_config_dir }}/app-pod.yml` (既定: `/home/ansible/kubeadm/multus/app-pod.yml`) |
| `files/multus-chart/` | Multus CNI のローカル Helm Chart。 | `{{ k8s_multus_helm_chart_path }}` (既定: `/home/ansible/kubeadm/multus/chart`) |

## 検証ポイント

- `kubectl --kubeconfig /etc/kubernetes/admin.conf get nodes` が正常に返り, API サーバが応答している。
- Multus が有効な場合, `kubectl -n kube-system get ds kube-multus-ds` で DaemonSet が稼働している。
- `helm list -n kube-system` に `multus-cni` が想定通りのバージョンで存在する (Helm 方式の場合)。
- `{{ k8s_multus_config_dir }}/app-pod.yml` が生成されている。

### Multus 動作確認

生成された Pod マニフェストを適用してインタフェースと経路を確認します:

```bash
kubectl apply -f {{ k8s_multus_config_dir }}/app-pod.yml
kubectl exec demo-net1 -it -- ip addr
kubectl exec demo-net1 -it -- ip route
```

## 補足

- `config.yml` は現状タスク未定義のため, 追加実装が必要な場合はここに処理を追加してください。
- Multus が不要な場合は `k8s_multus_enabled: false` を維持するか, `--skip-tags` で該当タスクをスキップしてください。
