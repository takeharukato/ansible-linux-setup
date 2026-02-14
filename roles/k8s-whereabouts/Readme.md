# k8s-whereabouts ロール

Kubernetes コントロールプレーンノード上に Whereabouts を導入し, NetworkAttachmentDefinition (NAD) を適用するロールです。`k8s-common`, `k8s-ctrlplane`, `k8s-multus` で整えた共通前提の上に, Whereabouts の Helm チャート導入と NAD の適用を行います。再実行にも対応するよう設計されています。

## 実行フロー

1. `load-params.yml` で OS 別パッケージ定義 (`vars/packages-*.yml`) とクラスタ共通変数 (`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込みます。
2. `package.yml` を読み込みます (現状はタスクなしのプレースホルダです)。
3. `directory.yml` が Whereabouts 用の設定ディレクトリ (既定では `{{ k8s_kubeadm_config_store }}/whereabouts`) を作成します。
4. `user_group.yml` と `service.yml` は将来の拡張用に読み込まれます (現状はタスクなし)。
5. `config-whereabouts.yml` は `k8s_multus_enabled` と `k8s_whereabouts_enabled` が有効で, かつ IPv4 または IPv6 のアドレス範囲が揃っている場合に発動します。API サーバの起動を待機後, Whereabouts Helm チャートを導入し, `ipvlan-wb-nad.yml.j2` から生成した NAD を `kubectl apply` します。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_ctrlplane_endpoint` | 各ホストの `host_vars` で指定 | Control Plane API の広告アドレス (IPv4/IPv6)。待機処理で使用。|
| `k8s_kubeadm_config_store` | `{{ ansible_home_dir }}/kubeadm` | Whereabouts 設定ファイルのルートディレクトリ。|
| `k8s_whereabouts_config_dir` | `{{ k8s_kubeadm_config_store }}/whereabouts` | NAD 設定ファイルの生成先ディレクトリ。|
| `k8s_multus_enabled` | `false` | Multus が有効な場合のみ Whereabouts を導入します。|
| `k8s_whereabouts_enabled` | `false` | Whereabouts 関連タスクを実行するかどうか。|
| `k8s_whereabouts_version` | `0.9.2` | Whereabouts のベースバージョン。|
| `k8s_whereabouts_helm_chart_version` | `{{ k8s_whereabouts_version }}` | Whereabouts チャートバージョン。|
| `k8s_whereabouts_image_version` | `{{ k8s_whereabouts_version }}` | Whereabouts コンテナイメージのタグ (テンプレート内で参照)。|
| `k8s_whereabouts_chart_url` | `oci://ghcr.io/k8snetworkplumbingwg/whereabouts-chart` | Whereabouts Helm チャートの OCI URL。|
| `k8s_whereabouts_ipv4_range_start` / `k8s_whereabouts_ipv4_range_end` | `""` | NAD で使用する IPv4 プール範囲。適用前に要設定。|
| `k8s_whereabouts_ipv6_range_start` / `k8s_whereabouts_ipv6_range_end` | `""` | NAD で使用する IPv6 プール範囲。|
| `network_ipv4_cidr` | `vars/all-config.yml` 由来 | NAD で使用する IPv4 CIDR。|
| `network_ipv6_cidr` | `vars/all-config.yml` 由来 | NAD で使用する IPv6 CIDR。|
| `mgmt_nic` | `group_vars/all/all.yml` 由来 | NAD の `master` インタフェース名。|

その他, `vars/cross-distro.yml` と `vars/all-config.yml` に含まれる共通変数は, NAD テンプレート生成に利用されます。

## 主な処理

- **Whereabouts 導入**: OCI Helm チャートを `helm upgrade --install` で導入します。
- **NAD 適用**: `templates/ipvlan-wb-nad.yml.j2` から生成した NAD を `kubectl apply` します。

## テンプレート／ファイル

| テンプレート/ファイル | 用途 | インストール先パス |
| --- | --- | --- |
| `templates/ipvlan-wb-nad.yml.j2` | Whereabouts + IPvLAN 用 NetworkAttachmentDefinition。 | `{{ k8s_whereabouts_config_dir }}/ipvlan-wb-nad.yml` (既定: `/home/ansible/kubeadm/whereabouts/ipvlan-wb-nad.yml`) |

## 検証ポイント

- `helm list -n kube-system` に `whereabouts` が想定通りのバージョンで存在する。
- `kubectl get networkattachmentdefinition` で `ipvlan-wb` が登録されている。
- `{{ k8s_whereabouts_config_dir }}/ipvlan-wb-nad.yml` が生成されている。

### NAD 動作確認

`ipvlan-wb` の NAD が生成されていることを確認します:

```bash
kubectl get networkattachmentdefinition ipvlan-wb -o yaml
```

## 補足

- `k8s_multus_enabled: true` と `k8s_whereabouts_enabled: true` の両方が必要です。
- `k8s_whereabouts_ipv4_range_start` / `k8s_whereabouts_ipv4_range_end` を事前に設定してください (IPv4 を使う場合)。
- `k8s_whereabouts_ipv6_range_start` / `k8s_whereabouts_ipv6_range_end` を事前に設定してください (IPv6 を使う場合)。
- IPv4/IPv6 のいずれかが揃っていない場合, `config-whereabouts.yml` は実行されません。

### IPv6 範囲を有効化する手順

1. 変数を設定します。

```yaml
k8s_whereabouts_ipv6_range_start: "<IPv6の開始アドレス>"
k8s_whereabouts_ipv6_range_end: "<IPv6の終了アドレス>"
```

2. ロールを再実行して NAD を再生成・再適用します。

3. IPv6 アドレスが付与されていることを確認します。

```bash
kubectl get networkattachmentdefinition ipvlan-wb -o yaml
kubectl exec demo-net1 -it -- ip -6 addr
```

### NAD の namespace を変更する手順

`templates/ipvlan-wb-nad.yml.j2` の `metadata.namespace` を変更します。

1. 例: `default` から `kube-system` に変更する場合

```yaml
metadata:
	name: ipvlan-wb
	namespace: kube-system
```

2. 既存の NAD を削除し, 再適用します。

```bash
kubectl delete networkattachmentdefinition ipvlan-wb -n default
kubectl apply -f "{{ k8s_whereabouts_config_dir }}/ipvlan-wb-nad.yml"
```

3. 参照側 (Pod/CRD) の `k8s.v1.cni.cncf.io/networks` が namespace 指定を含む場合は合わせて更新します。
