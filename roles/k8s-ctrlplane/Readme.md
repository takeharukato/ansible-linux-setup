# k8s-ctrlplane ロール

Kubernetes コントロールプレーンノードを構築するロールです。`k8s-common` で整えた共通前提の上に, kubeadm 設定の生成と実行, Cilium の導入, Cluster Mesh 用 kubeconfig 生成ツールの配布, Helm/Cilium CLI 環境整備を行います。IPv4/IPv6 デュアルスタックを前提にしており, 再実行にも対応するよう設計されています。

## 実行フロー

1. `load-params.yml` で OS 別パッケージ定義 (`vars/packages-*.yml`) とクラスタ共通変数 (`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込みます。
2. `package.yml` を読み込みます (現状はタスクなしのプレースホルダです)。
3. `directory.yml` が Cilium / Multus / Whereabouts 用の設定ディレクトリ (既定では `{{ k8s_kubeadm_config_store }}/cilium` など) を作成します。Multus / Whereabouts の導入は本ロールでは行いません。
4. `user_group.yml` と `service.yml` は将来の拡張用に読み込まれます (現状はタスクなし)。
5. `config-k8sctrlplane-firewall.yml` が `enable_firewall` と `firewall_backend` に応じて UFW もしくは firewalld を有効化し, 6443/tcp, 10250/tcp, 10257/tcp, 10259/tcp, 2379-2380/tcp を恒久的に開放します。
6. `config-helm.yml` で Helm (指定バージョンまたは最新) と Cilium CLI を導入し, 既存の Helm リポジトリを全削除したうえで cilium リポジトリを root / `k8s_operator_user` 双方に登録します。
7. `config-k8s-helm-shell-completion.yml` が `k8s_helm_cli_completion_enabled` 有効時に bash/zsh 用補完スクリプトを生成・配置します。
8. `config-k8s-cilium-shell-completion.yml` が `k8s_cilium_cli_completion_enabled` 有効時に bash/zsh 用補完スクリプトを生成・配置します。
9. `config.yml` が kubeadm 設定ファイル `ctrlplane-kubeadm.config.yml` を生成し, Pod/Service CIDR の順序を API ファミリと揃えた上で `kubeadm reset` → `kubeadm init` を実行します。必要に応じて共通 CA を `/etc/kubernetes/pki` へ復元し, containerd / kubelet を有効化してから kubeconfig を root / ansible / `k8s_operator_user` に配布し, ホストを再起動します。
10. `config-cilium.yml` が API サーバの起動を待機し, `kubernetes-admin` に cluster-admin 権限を付与してから kube-proxy (DaemonSet / ConfigMap / iptables ルール) を除去し, (必要時) `k8s-cilium-shared-ca` ロールで Cluster Mesh 用 Secret を更新し, 生成した values で `helm install cilium` を実行します (既存リリースが残っていると失敗するため, 再適用時は手動で削除が必要)。処理後に再起動します。
11. `config-cilium-bgp-cplane.yml` は `k8s_bgp.enabled` が `true` のホストで発動し, ノード名などの識別子を算出して Cilium BGP Control Plane 用 manifest を生成します。その後, 関連 CRD (CiliumBGPAdvertisement / CiliumBGPPeerConfig / CiliumBGPClusterConfig) の存在を確認しながら manifest を適用します。
12. `config-cluster-mesh-tools.yml` が Cluster Mesh 向けツールディレクトリを作成し, 証明書埋め込み kubeconfig 生成スクリプトと手順書を配布します。クラスタ名/ID が指定されている場合は共有 CA の存在を検証し, 見つからなければ明示的に失敗させます。条件を満たせば埋め込み kubeconfig を生成し, ファイル所有者を `k8s_operator_user` に設定します。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_ctrlplane_endpoint` | 各ホストの `host_vars` で指定 | Control Plane API の広告アドレス (IPv4/IPv6)。kubeadm 設定, 本ロール内の待機処理, Cilium 設定で使用。|
| `k8s_kubeadm_config_store` | `{{ ansible_home_dir }}/kubeadm` | `ctrlplane-kubeadm.config.yml` や Cilium values の生成先ルート。|
| `k8s_cilium_config_dir` | `{{ k8s_kubeadm_config_store }}/cilium` | Cilium 設定ファイルの生成先ディレクトリ。|
| `k8s_multus_config_dir` | 未定義 | Multus 設定ディレクトリ (本ロールでは作成のみ)。|
| `k8s_whereabouts_config_dir` | 未定義 | Whereabouts 設定ディレクトリ (本ロールでは作成のみ)。|
| `k8s_kubeadm_ignore_preflight_errors_arg` | `--ignore-preflight-errors=all` | `kubeadm init` 実行時に無視する preflight エラーを制御。|
| `k8s_pod_ipv4_network_cidr` / `k8s_pod_ipv6_network_cidr` | 必須 | Pod ネットワーク CIDR。kubeadm と Cilium で参照。|
| `k8s_pod_ipv4_service_subnet` / `k8s_pod_ipv6_service_subnet` | 必須 | Service CIDR。API ファミリ順に並べ替えて kubeadm で使用。|
| `enable_firewall` | `false` | `true` の場合, UFW/firewalld によりコントロールプレーンポートを開放します。|
| `firewall_backend` | OS 既定 | `ufw` または `firewalld` を指定 (複数可)。|
| `k8s_control_plane_ports` | 6443/10250/10257/10259/2379-2380 | 開放するコントロールプレーンポートの一覧。|
| `k8s_helm_version` | 未定義 | `latest` または明示バージョン。未定義時は最新版を導入します。|
| `k8s_helm_cli_completion_enabled` | `true` | Helm の bash/zsh 補完ファイルを生成・配置します。|
| `k8s_cilium_version` | 必須 | Cilium のベースバージョン。Helm チャートやイメージタグの既定値に参照されます。|
| `k8s_cilium_helm_chart_version` | `{{ k8s_cilium_version }}` | 導入する Cilium チャートのバージョン。|
| `k8s_cilium_image_version` | `v{{ k8s_cilium_version }}` | Cilium / Cilium Operator コンテナイメージのタグ。|
| `k8s_cilium_helm_repo_url` | `https://helm.cilium.io/` | Helm リポジトリ URL (`config-helm.yml` で登録)。|
| `k8s_cilium_cli_completion_enabled` | `true` | Cilium CLI の bash / zsh 補完ファイルを生成・配置します。|
| `k8s_cilium_shared_ca_enabled` | `false` | Cluster Mesh 用の共通 CA Secret を `k8s-cilium-shared-ca` ロールで整備するか。|
| `k8s_cilium_bgp_control_plane_enabled` | 未定義 | Cilium Helm values 内の BGP Control Plane 有効化フラグ。未定義時は `k8s_bgp.enabled` に連動します。|
| `k8s_cilium_cm_cluster_name` / `k8s_cilium_cm_cluster_id` | 必要時に設定 | Cluster Mesh を構成する場合に指定。埋め込み kubeconfig 生成で使用。|
| `k8s_embed_kubeconfig_*` | defaults 参照 | 埋め込み kubeconfig の出力先やコンテキスト名を制御します。|
| `k8s_shared_ca_replace_kube_ca` | `false` | kubeadm reset 後に `/etc/kubernetes/pki/{ca.crt,ca.key}` を共通 CA で置換するか。|
| `k8s_shared_ca_source_cert` / `k8s_shared_ca_source_key` | 未定義 | 共通 CA のソースファイル (指定時のみ復元を実行)。|
| `k8s_shared_ca_cert_path` / `k8s_shared_ca_key_path` | 未定義 | 共通 CA の配置先パス。|
| `k8s_shared_ca_output_dir` | 未定義 | 共通 CA 出力ディレクトリ。|
| `k8s_bgp` | 未定義 | `enabled` / `neighbors` などの BGP 設定を含むマップ (`enabled: true` の場合は `neighbors` 必須)。|
| `k8s_operator_user` | `kube` | オペレータユーザ名。kubeconfig 配布や Helm リポジトリ登録で利用。|

その他, `helm_bash_completion_path` / `helm_zsh_completion_path` / `cilium_bash_completion_path` / `cilium_zsh_completion_path` は `vars/cross-distro.yml` から読み込まれ, OS ごとに補完ファイルの配置先が決まります。

## 主な処理

- **kubeadm 設定と再初期化**: `ctrlplane-kubeadm.config.j2` をもとに API アドレスや Pod/Service CIDR を API ファミリ順に並べ替えた上で `kubeadm init` を実行します。共通 CA を再配置するロジックも含みます。
- **Cilium 導入**: kube-proxy を削除し, Helm から Cilium をネイティブルーティング (IPv4/IPv6) で導入します。必要に応じて `k8s-cilium-shared-ca` ロールで Cluster Mesh 向け Secret を整備し, `helm install cilium` 後にホストを再起動します (再適用時は既存リリースの削除が前提)。
- **Cilium CLI 補完**: `k8s_cilium_cli_completion_enabled` が `true` の場合に bash / zsh 用補完スクリプトを生成し, root 配下に配置します。
- **Helm 環境構築**: Helm 本体と Cilium CLI を導入し, 既存リポジトリを削除したうえで cilium リポジトリを root と `k8s_operator_user` 双方に登録します。
- **Firewall 開放**: コントロールプレーンの必須ポートを UFW/firewalld で恒久的に許可し, 状態確認コマンドを実行します。
- **Cluster Mesh ツール**: `create-embedded-kubeconfig.py` と手順書を配布し, Cluster Mesh 用に共通 CA を埋め込んだ kubeconfig を生成します。必須の CA ファイルが欠けている場合は明示的に失敗させ, 生成した kubeconfig の所有者を `k8s_operator_user` に調整します。

## テンプレート／ファイル

| テンプレート/ファイル | 用途 | インストール先パス |
| --- | --- | --- |
| `templates/ctrlplane-kubeadm.config.j2` | kubeadm 初期化設定のテンプレート。 | `{{ k8s_kubeadm_config_store }}/ctrlplane-kubeadm.config.yml` (既定: `/home/ansible/kubeadm/ctrlplane-kubeadm.config.yml`) |
| `templates/cilium-install.yml.j2` | Cilium Helm リリース用 values。 | `{{ k8s_cilium_config_dir }}/cilium-install.yml` (既定: `/home/ansible/kubeadm/cilium/cilium-install.yml`) |
| `templates/create-embedded-kubeconfig.py.j2` | 証明書埋め込み kubeconfig 生成スクリプト。 | `{{ k8s_embed_kubeconfig_script_path }}` (既定: `/opt/k8snodes/sbin/create-embedded-kubeconfig.py`) |
| `files/Readme-create-embedded-kubeconfig-JP.md` | Cluster Mesh 用 kubeconfig 生成手順書。 | `{{ k8s_node_setup_tools_docs_dir }}/Readme-create-embedded-kubeconfig-JP.md` (既定: `/opt/k8snodes/docs/Readme-create-embedded-kubeconfig-JP.md`) |

## 検証ポイント

- `kubeadm init` 実行後に `kubectl --kubeconfig /etc/kubernetes/admin.conf get nodes` が正常に返り, API サーバが `Ready` である。
- `/etc/kubernetes/pki` に共通 CA が配置されている (必要に応じて `openssl x509 -in /etc/kubernetes/pki/ca.crt -noout -subject`)。
- `kubectl -n kube-system get ds cilium` で Cilium DaemonSet が稼働し, `cilium status` が `OK` を示す。
- `helm list -n kube-system` に `cilium` が想定通りのバージョンで存在する。
- `ls /opt/k8snodes/sbin` に `create-embedded-kubeconfig.py` が存在し, `/home/{{ k8s_operator_user }}/.kube/<cluster>-embedded.kubeconfig` が生成されている。
- ファイアウォールの設定が反映され, `ufw status` または `firewall-cmd --list-ports` にコントロールプレーンポートが開放済みである。
- Cluster Mesh 接続時に `cilium clustermesh connect` が TLS エラーなく成功する。

### デュアルスタック構成の確認

コントロールプレーン構築後, クラスタが IPv4/IPv6 デュアルスタックで正常に動作しているかを確認するため, 以下の手順を実行します。これらは特にワーカーノード追加前の段階での検証に有用です。

#### Node podCIDRs の確認

各ノードに割り当てられた Pod CIDR が IPv4 と IPv6 の両方を含むことを確認します:

```bash
kubectl get nodes -o custom-columns=NAME:.metadata.name,POD-CIDRS:.spec.podCIDRs
```

期待される出力例 (IPv6 優先の場合):

```plaintext
NAME             POD-CIDRS
k8sctrlplane01   [fdb6:6e92:3cfb:200::/64 10.244.0.0/24]
```

期待される出力例 (IPv4 優先の場合):

```plaintext
NAME             POD-CIDRS
k8sctrlplane01   [10.244.0.0/24 fdb6:6e92:3cfb:200::/64]
```

#### CoreDNS Service の ipFamilyPolicy 確認

kube-system 名前空間の kube-dns (CoreDNS) Service がデュアルスタック設定になっているか確認します:

```bash
kubectl get svc -n kube-system kube-dns -o yaml
```

デュアルスタックの場合の出力例 (重要な部分のみ抜粋):

```yaml
spec:
  clusterIP: fdb6:6e92:3cfb:feed::a
  clusterIPs:
  - fdb6:6e92:3cfb:feed::a
  - 10.254.0.10
  ipFamilies:
  - IPv6
  - IPv4
  ipFamilyPolicy: PreferDualStack
```

シングルスタックの場合(IPv6の場合):

```yaml
spec:
  clusterIP: fdb6:6e92:3cfb:feed::a
  clusterIPs:
  - fdb6:6e92:3cfb:feed::a
  ipFamilies:
  - IPv6
  ipFamilyPolicy: SingleStack
```

シングルスタックの場合(IPv4の場合):

```yaml
spec:
  clusterIP: 10.254.0.10
  clusterIPs:
  - 10.254.0.10
  internalTrafficPolicy: Cluster
  ipFamilies:
  - IPv4
  ipFamilyPolicy: SingleStack
```

#### kube-apiserver の service-cluster-ip-range 確認

API サーバが起動時に指定された Service CIDR 範囲を確認します:

```bash
kubectl cluster-info dump | grep service-cluster-ip-range
```

期待される出力例 (IPv6 優先の場合):

```plaintext
      "--service-cluster-ip-range=fdb6:6e92:3cfb:feed::/112,10.254.0.0/16",
```

期待される出力例 (IPv4 優先の場合):

```plaintext
      "--service-cluster-ip-range=10.254.0.0/16,fdb6:6e92:3cfb:feed::/112",
```

#### 確認のタイミング

- コントロールプレーン構築直後 (ワーカーノード追加前) に実行することで, クラスタ基盤のデュアルスタック設定を早期検証できます。
- シングルスタックで構築された場合, kubeadm による再初期化が必要です。デュアルスタックへのアップグレードはKubernetesの仕様によりサポートされていません。

## 補足

- `k8s_shared_ca_replace_kube_ca: true` を組み合わせると, `k8s-shared-ca` で生成した共通 CA で kube-apiserver / etcd 証明書を再発行できます。ローテーション時は `k8s-cilium-shared-ca` と合わせて再実行してください。
- `config.yml` は `kubeadm reset` を含むため, 既存クラスタに適用する際は事前に制御プレーンを退避させるなど必要に応じた停止計画を立ててください。
- Helm リポジトリは全削除されるため, 既存のリポジトリ運用がある場合は事前に退避してください。
- Cilium BGP Control Plane のマニフェストは `k8s-common` ロールの `templates/cilium-bgp-resources.yml.j2` を使って生成し, 既定では `{{ k8s_cilium_config_dir }}/bgp` 配下に出力します。
- Cluster Mesh 用 kubeconfig を追加で配布したい場合は生成された `<cluster>-embedded.kubeconfig` を `cilium clustermesh connect` や `cilium clustermesh status` コマンドに引き渡してください。
- `k8s_cilium_cli_completion_enabled: false` とすると Cilium CLI の補完ファイル生成をスキップできます (生成先パスは `vars/cross-distro.yml` で OS 別に定義)。
- `enable_firewall` を有効にした場合は, `firewall_backend` に応じて UFW または firewalld の導入とポート開放が実施されます (`reload ufw` / `reload firewalld` ハンドラが呼ばれます)。
