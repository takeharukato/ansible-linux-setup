# k8s-ctrlplane ロール

Kubernetes コントロールプレーンノードを構築するロールです。`k8s-common` で整えた共通前提の上に、kubeadm 設定の生成と実行、Cilium を中心としたネットワーク周りのインストール、クラスタメッシュ用 kubeconfig の準備、Helm/Cilium CLI 環境整備などをまとめて行います。IPv4/IPv6 デュアルスタックと複数 CNI（Cilium + Multus + Whereabouts）を前提とした構成になっており、再実行にも対応するよう設計されています。

## 実行フロー

1. `load-params.yml` で OS 別パッケージ名やクラスタ共通設定 (`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml` など) を読み込みます。
2. `package.yml` (現状はプレースホルダ) の後、`directory.yml` が `k8s_kubeadm_config_store` 配下に Cilium/Multus/Whereabouts 用ディレクトリを作成します。
3. `user_group.yml` / `service.yml` で追加の処理があれば実施できるよう順序を確保しています（現状は空）。
4. `config-k8sctrlplane-firewall.yml` が `enable_firewall` / `firewall_backend` に応じてコントロールプレーン用ポート (6443/tcp, 10250/tcp, 10257/tcp, 10259/tcp, 2379-2380/tcp) を UFW または firewalld で開放します。
5. `config-helm.yml` で Helm と Cilium CLI を導入し、`k8s_operator_user` アカウントにも Helm リポジトリ (cilium / bitnami) を登録します。
6. `config.yml` が kubeadm 用設定ファイル `ctrlplane-kubeadm.config.yml` を生成し、既存クラスタを `kubeadm reset` で初期化後、`kubeadm init` を実行してコントロールプレーンを再構成します。必要に応じて `k8s-shared-ca` で配布した共通 CA を `/etc/kubernetes/pki` に復元します。
7. `config-cilium.yml` で kube-proxy を削除し、`k8s-cilium-shared-ca` ロールを呼び出して Cilium Cluster Mesh 用 Secret を更新した後、Cilium Helm チャートを `k8s_cilium_config_dir` の values ファイルを用いて導入します。
8. `config-multus.yml` が Multus CNI を Helm で導入し、テスト Pod マニフェストを出力します。
9. `config-whereabouts.yml` が Whereabouts (IPAM) をインストールし、NetworkAttachmentDefinition (NAD) を `ipvlan-wb-nad.yml` から適用します。
10. `config-cluster-mesh-tools.yml` が Cluster Mesh 接続用の証明書埋め込み kubeconfig を生成し、ドキュメント (`Readme-create-embedded-kubeconfig-JP.md`) を配布します。
11. `package-netgauge.yml` でノイズ測定ツール (netgauge, gnuplot, python3-matplotlib 等) をインストールします。

各ステップの間で必要に応じて再起動・待機を行い、最終的に kubeconfig を root/ansible/`k8s_operator_user`ユーザへ配布した状態で完了します。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_ctrlplane_endpoint` | 各ホストの `host_vars` で指定 | Control Plane API の広告アドレス (IPv4/IPv6)。kubeadm 設定、本ロール内の待機処理、Cilium 設定で使用。|
| `k8s_kubeadm_config_store` | `{{ ansible_home_dir }}/kubeadm` | `ctrlplane-kubeadm.config.yml` や CNI 用 values ファイルのルートディレクトリ。|
| `k8s_pod_ipv4_network_cidr` / `k8s_pod_ipv6_network_cidr` | 必須 | Pod ネットワーク CIDR。kubeadm, Cilium, Whereabouts で参照。|
| `k8s_pod_ipv4_service_subnet` / `k8s_pod_ipv6_service_subnet` | 必須 | Service CIDR。API ファミリと順序を揃えて kubeadm テンプレートで使用。|
| `k8s_cilium_helm_chart_version` | `vars/all-config.yml` 等で指定 | 導入する Cilium チャートのバージョン。|
| `k8s_multus_helm_chart_version` / `k8s_whereabouts_helm_chart_version` | 同上 | Multus / Whereabouts のチャートバージョン。|
| `cilium_shared_ca_enabled` | `false` | Cilium Cluster Mesh 用 Secret を生成するか。`true` の場合に `k8s-cilium-shared-ca` ロールを実行。|
| `k8s_shared_ca_replace_kube_ca` | `false` | kubeadm reset 後に共通 CA で `/etc/kubernetes/pki/{ca.crt,ca.key}` を置換するか。|
| `k8s_operator_user` | `kube` | オペレータユーザ名。kubeconfig 配布や Helm リポジトリ登録で利用。|
| `k8s_netgauge_packages` | python3-pip など | ネットワーク測定ツール構築・実行用に導入するパッケージ。|

その他、`k8s_helm_version`、`k8s_cilium_cm_cluster_name` / `k8s_cilium_cm_cluster_id`、`k8s_embed_kubeconfig_*` 変数が Cluster Mesh 用 kubeconfig 生成を制御します。

## 主な処理

- **kubeadm 設定と再初期化**: `ctrlplane-kubeadm.config.j2` をもとに API アドレスや Pod/Service CIDR を API ファミリ順に並べ替えた上で `kubeadm init` を実行します。共通 CA を再配置するロジックも含みます。
- **Cilium 導入**: kube-proxy を削除し、Helm から Cilium をネイティブルーティング (IPv4/IPv6) で導入します。Cilium CLI のインストールと Helm values の生成も本ロールで実施します。
- **Multus / Whereabouts**: Helm チャート経由で追加 CNI (Multus) と IPAM (Whereabouts) を導入し、NetworkAttachmentDefinition (NAD) を適用します。Multi-CNI 環境でクラスタメッシュやセカンダリネットワークを扱えるようにします。
- **Cluster Mesh ツール**: `create-embedded-kubeconfig.py` を配布し、`--shared-ca` オプションで共通 CA 証明書を埋め込んだ kubeconfig を生成します。これにより `cilium clustermesh connect` 時に同一発行元 CA での相互認証が可能になります。
- **Helm 環境構築**: Helm 本体と Cilium/Bitnami リポジトリを root とオペレータユーザの両方に設定し、`helm repo list` 初期化や `helm repo update` を済ませます。
- **Firewall 開放**: コントロールプレーンの必須ポートを UFW/firewalld で恒久的に許可し、状態確認コマンドを実行します。
- **ノイズ測定ツール導入**: `k8s_netgauge_packages` で定義した gnuplot / matplotlib 等をインストールし、ネットワーク遅延測定などの解析に備えます。

## テンプレート／ファイル

- `templates/ctrlplane-kubeadm.config.j2`: kubeadm 初期化設定のテンプレート。
- `templates/cilium-install.yml.j2`: Cilium Helm リリース用 values。
- `templates/multus-install.yml.j2`: Multus CNI Helm values。
- `templates/ipvlan-wb-nad.yml.j2`: Whereabouts + IPvLAN 用 NetworkAttachmentDefinition。
- `templates/create-embedded-kubeconfig.py.j2`: 証明書埋め込み kubeconfig 生成スクリプト。
- `templates/app-pod.yml.j2`: Multus 接続テスト用 Pod マニフェスト。
- `files/Readme-create-embedded-kubeconfig-JP.md`: Cluster Mesh 用 kubeconfig 生成手順書。

## 検証ポイント

- `kubeadm init` 実行後に `kubectl --kubeconfig /etc/kubernetes/admin.conf get nodes` が正常に返り、API サーバが `Ready` である。
- `/etc/kubernetes/pki` に共通 CA が配置されている (必要に応じて `openssl x509 -in /etc/kubernetes/pki/ca.crt -noout -subject`)。
- `kubectl -n kube-system get ds cilium` で Cilium DaemonSet が稼働し、`cilium status` が `OK` を示す。
- `helm list -n kube-system` に `cilium`, `multus-cni`、`whereabouts` が表示され、バージョンが想定通りである。
- `kubectl get networkattachmentdefinition` で `ipvlan-wb` (など) が登録されている。
- `ls /opt/k8snodes/sbin` に `create-embedded-kubeconfig.py` が存在し、`/home/{{ k8s_operator_user }}/.kube/<cluster>-embedded.kubeconfig` が生成されている。
- ファイアウォールの設定が反映され、`ufw status` または `firewall-cmd --list-ports` にコントロールプレーンポートが開放済みである。
- Cluster Mesh 接続時に `cilium clustermesh connect` が TLS エラーなく成功する。

## 補足

- `k8s_shared_ca_replace_kube_ca: true` を組み合わせると、`k8s-shared-ca` で生成した共通 CA で kube-apiserver / etcd 証明書を再発行できます。ローテーション時は `k8s-cilium-shared-ca` と合わせて再実行してください。
- `config.yml` は `kubeadm reset` を含むため、既存クラスタに適用する際は事前に制御プレーンを退避させるなど停止計画を立ててください。
- Multus/Whereabouts を不要とする場合はそれぞれのタスクを `--skip-tags` で除外するか、`k8s_multus_helm_chart_version` / `k8s_whereabouts_helm_chart_version` を未設定にする運用も可能です。
- Cluster Mesh 用 kubeconfig を追加で配布したい場合は生成された `<cluster>-embedded.kubeconfig` を `cilium clustermesh connect` や `cilium clustermesh status` コマンドに引き渡してください。
- 現時点では, Firewallを有効にした場合の動作に未対応です。`enable_firewall`変数を`false`に設定してください。
