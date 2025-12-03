# k8s-ctrlplane ロール

Kubernetes コントロールプレーンノードを構築するロールです。`k8s-common` で整えた共通前提の上に, kubeadm 設定の生成と実行, Cilium を中心としたネットワーク周りのインストール, クラスタメッシュ用 kubeconfig の準備, Helm/Cilium CLI 環境整備などをまとめて行います。IPv4/IPv6 デュアルスタックと複数 CNI ( Cilium + Multus + Whereabouts )を前提とした構成になっており, 再実行にも対応するよう設計されています。

## 実行フロー

1. `load-params.yml` で OS 別パッケージ定義 (`vars/packages-*.yml`) とクラスタ共通変数 (`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込みます。
2. `package.yml` (プレースホルダ) の後に `directory.yml` が Cilium / Multus / Whereabouts 用の設定ディレクトリ (既定では `{{ k8s_kubeadm_config_store }}/cilium` など) を作成します。
3. `user_group.yml` と `service.yml` は将来の拡張用に読み込まれます (現状はタスクなし)。
4. `config-k8sctrlplane-firewall.yml` が `enable_firewall` と `firewall_backend` に応じて UFW もしくは firewalld を有効化し, 6443/tcp, 10250/tcp, 10257/tcp, 10259/tcp, 2379-2380/tcp を恒久的に開放します。
5. `config-helm.yml` で Helm (指定バージョンまたは最新) と Cilium CLI を導入し, `yq` / `xargs` を使って既存の Helm リポジトリを一度全削除したうえで cilium リポジトリを root / `k8s_operator_user` 双方に登録します。
6. `config-k8s-cilium-shell-completion.yml` が `k8s_cilium_cli_completion_enabled` 有効時に bash/zsh 用補完スクリプトを生成・配置します。
7. `config.yml` が kubeadm 設定ファイル `ctrlplane-kubeadm.config.yml` を生成し, Pod/Service CIDR の順序を API ファミリと揃えた上で `kubeadm reset` → `kubeadm init` を実行します。必要に応じて共通 CA を `/etc/kubernetes/pki` へ復元し, containerd / kubelet を有効化してから kubeconfig を root / ansible / `k8s_operator_user` に配布し, ホストを再起動します。
8. `config-cilium.yml` が API サーバの起動を待機し, `kubernetes-admin` に cluster-admin 権限を付与してから kube-proxy (DaemonSet / ConfigMap / iptables ルール) を除去し, (必要時) `k8s-cilium-shared-ca` ロールで Cluster Mesh 用 Secret を更新し, 生成した values で `helm install cilium` を実行します (既存リリースが残っていると失敗するため, 再適用時は手動で削除が必要)。処理後に再起動します。
9. `config-multus.yml` は `k8s_multus_enabled` 有効時に Multus values を生成し, `k8s_multus_helm_repo_git_url` の HEAD を `force: true` で再取得してローカルから `helm upgrade --install` を実行し, 動作確認用 Pod マニフェストを配置します。
10. `config-whereabouts.yml` は `k8s_whereabouts_enabled` 有効時に Whereabouts チャートを OCI から導入し, `ipvlan-wb-nad.yml.j2` から生成した NAD を `kubectl apply` します (セカンダリネットワークの範囲は `k8s_whereabouts_ipv4_range_*` 等で指定)。
11. `config-cluster-mesh-tools.yml` が Cluster Mesh 向けツールディレクトリを作成し, 証明書埋め込み kubeconfig 生成スクリプトと手順書を配布します。クラスタ名/ID が指定されている場合は共有 CA の存在を検証し, 見つからなければ明示的に失敗させます。条件を満たせば埋め込み kubeconfig を生成し, ファイル所有者を `k8s_operator_user` に設定します。
12. `package-netgauge.yml` が `k8s_netgauge_packages` 定義時にノイズ測定系パッケージを導入します。

各ステップの間で必要に応じて待機や再起動を行い, 最終的に kubeconfig 配布と追加ツール整備まで完了させます。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_ctrlplane_endpoint` | 各ホストの `host_vars` で指定 | Control Plane API の広告アドレス (IPv4/IPv6)。kubeadm 設定, 本ロール内の待機処理, Cilium 設定で使用。|
| `k8s_kubeadm_config_store` | `{{ ansible_home_dir }}/kubeadm` | `ctrlplane-kubeadm.config.yml` や CNI 用 values ファイルのルートディレクトリ。|
| `k8s_kubeadm_ignore_preflight_errors_arg` | `--ignore-preflight-errors=all` | `kubeadm init` 実行時に無視する preflight エラーを制御。|
| `k8s_pod_ipv4_network_cidr` / `k8s_pod_ipv6_network_cidr` | 必須 | Pod ネットワーク CIDR。kubeadm, Cilium, Whereabouts で参照。|
| `k8s_pod_ipv4_service_subnet` / `k8s_pod_ipv6_service_subnet` | 必須 | Service CIDR。 k8s_pod_ipv6_service_subnet	必須API ファミリと順序を揃えて kubeadm テンプレートで使用。|
| `k8s_helm_completion_enabled` | `true` | `true` の場合, Helm の bash / zsh 補完ファイルを生成・配置します。|
| `k8s_cilium_version` | 必須 | Cilium のベースバージョン。Helm チャートやイメージタグの既定値に参照されます。|
| `k8s_cilium_helm_chart_version` | `{{ k8s_cilium_version }}` | 導入する Cilium チャートのバージョン。|
| `k8s_cilium_image_version` | `v{{ k8s_cilium_version }}` | Cilium / Cilium Operator コンテナイメージのタグ。|
| `k8s_cilium_helm_repo_url` | `https://helm.cilium.io/` | Helm リポジトリ URL (`config-helm.yml` で登録)。|
| `k8s_cilium_cli_archive_name` | `cilium-linux-amd64.tar.gz` | Cilium CLI のアーカイブ名。|
| `k8s_cilium_cli_download_url` | `https://github.com/cilium/cilium-cli/releases/latest/download/{{ k8s_cilium_cli_archive_name }}` | Cilium CLI のダウンロード先。|
| `k8s_cilium_cli_checksum_url` | `{{ k8s_cilium_cli_download_url }}.sha256sum` | Cilium CLI の SHA256 チェックサム取得先。|
| `k8s_cilium_cli_completion_enabled` | `true` | `true` の場合, Cilium CLI の bash / zsh 補完ファイルを生成・配置します。|
| `k8s_cilium_cm_cluster_name` / `k8s_cilium_cm_cluster_id` | 必要時に設定 | Cluster Mesh を構成する場合に指定。Helm values と埋め込み kubeconfig 生成で使用。|
| `k8s_cilium_shared_ca_enabled` | `false` | Cluster Mesh 用の共通 CA Secret を `k8s-cilium-shared-ca` ロールで整備するか。|
| `k8s_multus_enabled` | `false` | Multus 関連タスクを実行するかどうか。|
| `k8s_multus_version` | `v4.2.3` | Multus のバージョン。|
| `k8s_multus_daemonset_manifest_url`| `https://raw.githubusercontent.com/k8snetworkplumbingwg/multus-cni/refs/tags/{{ k8s_multus_version }}/deployments/multus-daemonset.yml` | multusのDaemon Setを適用するマニュフェスト (公式)|
| `k8s_whereabouts_enabled` | `false` | Whereabouts 関連タスクを実行するかどうか。|
| `k8s_whereabouts_version` | `0.9.2` | Whereabouts のベースバージョン。|
| `k8s_whereabouts_helm_chart_version` | `{{ k8s_whereabouts_version }}` | Whereabouts チャートバージョン。|
| `k8s_whereabouts_image_version` | `{{ k8s_whereabouts_version }}` | Whereabouts コンテナイメージのタグ。|
| `k8s_whereabouts_ipv4_range_start` / `k8s_whereabouts_ipv4_range_end` | `""` | NAD で使用する IPv4 プール範囲。適用前に要設定。|
| `k8s_netgauge_packages` | `['python3-pip','gnuplot','python3-matplotlib','python3-numpy']` | ノイズ測定ツールを導入する際に利用。|
| `k8s_shared_ca_replace_kube_ca` | `false` | kubeadm reset 後に `/etc/kubernetes/pki/{ca.crt,ca.key}` を共通 CA で置換するか。|
| `k8s_operator_user` | `kube` | オペレータユーザ名。kubeconfig 配布や Helm リポジトリ登録で利用。|

その他, `k8s_helm_version`, `k8s_embed_kubeconfig_*`, `k8s_embed_kubeconfig_shared_ca_path`, `cilium_bash_completion_path` / `cilium_zsh_completion_path` などは `vars/cross-distro.yml` から読み込まれ, 各環境に合わせて調整できます。

## 主な処理

- **kubeadm 設定と再初期化**: `ctrlplane-kubeadm.config.j2` をもとに API アドレスや Pod/Service CIDR を API ファミリ順に並べ替えた上で `kubeadm init` を実行します。共通 CA を再配置するロジックも含みます。
- **Cilium 導入**: kube-proxy を削除し, Helm から Cilium をネイティブルーティング (IPv4/IPv6) で導入します。必要に応じて `k8s-cilium-shared-ca` ロールで Cluster Mesh 向け Secret を整備し, `helm install cilium` 後にホストを再起動します (再適用時は既存リリースの削除が前提)。
- **Cilium CLI 補完**: `k8s_cilium_cli_completion_enabled` が `true` の場合に bash / zsh 用補完スクリプトを生成し, root 配下に配置します。
- **Multus / Whereabouts**: `k8s_multus_enabled` / `k8s_whereabouts_enabled` が有効な場合にのみ実行され, Multus は git リポジトリを `force: true` で再取得してローカルチャートを適用し, Whereabouts は OCI Helm チャートから導入します。生成した NAD を適用して Multi-CNI 向けネットワークを準備します。
- **Cluster Mesh ツール**: `create-embedded-kubeconfig.py` と手順書を配布し, Cluster Mesh 用に共通 CA を埋め込んだ kubeconfig を生成します。必須の CA ファイルが欠けている場合は明示的に失敗させ, 生成した kubeconfig の所有者を `k8s_operator_user` に調整します。
- **Helm 環境構築**: Helm 本体と Cilium CLI を導入し, `yq` / `xargs` を使って既存リポジトリを削除したうえで cilium リポジトリを root とオペレータユーザ双方に登録します。
- **Firewall 開放**: コントロールプレーンの必須ポートを UFW/firewalld で恒久的に許可し, 状態確認コマンドを実行します。
- **ノイズ測定ツール導入**: `k8s_netgauge_packages` が定義されていれば gnuplot / matplotlib 等をインストールし, ネットワーク遅延測定などの解析に備えます。

## テンプレート／ファイル

- `templates/ctrlplane-kubeadm.config.j2`: kubeadm 初期化設定のテンプレート。
- `templates/cilium-install.yml.j2`: Cilium Helm リリース用 values。
- `templates/multus-install.yml.j2`: (レガシー) Multus CNI Helm values。
- `templates/ipvlan-wb-nad.yml.j2`: Whereabouts + IPvLAN 用 NetworkAttachmentDefinition。
- `templates/create-embedded-kubeconfig.py.j2`: 証明書埋め込み kubeconfig 生成スクリプト。
- `templates/app-pod.yml.j2`: Multus 接続テスト用 Pod マニフェスト。
- `files/Readme-create-embedded-kubeconfig-JP.md`: Cluster Mesh 用 kubeconfig 生成手順書。

## 検証ポイント

- `kubeadm init` 実行後に `kubectl --kubeconfig /etc/kubernetes/admin.conf get nodes` が正常に返り, API サーバが `Ready` である。
- `/etc/kubernetes/pki` に共通 CA が配置されている (必要に応じて `openssl x509 -in /etc/kubernetes/pki/ca.crt -noout -subject`)。
- `kubectl -n kube-system get ds cilium` で Cilium DaemonSet が稼働し, `cilium status` が `OK` を示す。
- `helm list -n kube-system` に `cilium`, `multus`, `whereabouts` が想定通りのバージョンで存在する。
- `kubectl get networkattachmentdefinition` で `ipvlan-wb` (など) が登録されている。
- `ls /opt/k8snodes/sbin` に `create-embedded-kubeconfig.py` が存在し, `/home/{{ k8s_operator_user }}/.kube/<cluster>-embedded.kubeconfig` が生成されている。
- ファイアウォールの設定が反映され, `ufw status` または `firewall-cmd --list-ports` にコントロールプレーンポートが開放済みである。
- Cluster Mesh 接続時に `cilium clustermesh connect` が TLS エラーなく成功する。

## 補足

- `k8s_shared_ca_replace_kube_ca: true` を組み合わせると, `k8s-shared-ca` で生成した共通 CA で kube-apiserver / etcd 証明書を再発行できます。ローテーション時は `k8s-cilium-shared-ca` と合わせて再実行してください。
- `config.yml` は `kubeadm reset` を含むため, 既存クラスタに適用する際は事前に制御プレーンを退避させるなど停止計画を立ててください。
- Multus や Whereabouts が不要な場合は `k8s_multus_enabled: false` / `k8s_whereabouts_enabled: false` を維持するか, 適宜 `--skip-tags` で該当タスクをスキップしてください。
- Cluster Mesh 用 kubeconfig を追加で配布したい場合は生成された `<cluster>-embedded.kubeconfig` を `cilium clustermesh connect` や `cilium clustermesh status` コマンドに引き渡してください。
- `k8s_cilium_cli_completion_enabled: false` とすると Cilium CLI の補完ファイル生成をスキップできます (生成先パスは `vars/cross-distro.yml` で OS 別に定義)。
- `enable_firewall` を有効にした場合は, `firewall_backend` に応じて UFW または firewalld の導入とポート開放が実施されます (`reload ufw` / `reload firewalld` ハンドラが呼ばれます)。
