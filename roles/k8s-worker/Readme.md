# k8s-worker ロール

Kubernetes ワーカーノードをクラスタへ再参加させるためのロールです。`k8s-common` で整えた前提の上に, 低遅延化向けの OS チューニング, `kubeadm join` の再実行, NodePort を含む防火壁構成, Cilium BGP Control Plane の設定をまとめて適用します。再実行を想定し, 既存ノードの cordon / drain / delete まで一括で扱います。

## 実行フロー

1. [roles/k8s-worker/tasks/load-params.yml](roles/k8s-worker/tasks/load-params.yml#L8-L23) が OS ファミリ別のパッケージ定義と `vars/` 配下の共通変数 (`cross-distro.yml` / `all-config.yml` / `k8s-api-address.yml`) を読み込みます。
2. [roles/k8s-worker/tasks/main.yml](roles/k8s-worker/tasks/main.yml#L12-L15) で `package.yml` / `directory.yml` / `user_group.yml` / `service.yml` を include し, 将来の拡張に備えたタスク構造を維持します ( 現状は実処理なし )。
3. [roles/k8s-worker/tasks/config-k8sworker-firewall.yml](roles/k8s-worker/tasks/config-k8sworker-firewall.yml#L8-L195) は `enable_firewall` と `firewall_backend` に応じて UFW もしくは firewalld を整備し, 6443 側からの kubelet アクセスや NodePort 範囲の開放, 状態確認を行います。
4. [roles/k8s-worker/tasks/config-shielding.yml](roles/k8s-worker/tasks/config-shielding.yml#L8-L27) が `k8s_systemd_slices` 向けに cpuset ドロップイン (`systemd-cpuset.conf.j2`) を生成し, CPU シールドの前提を整えます。
5. [roles/k8s-worker/tasks/config-worker-node.yml](roles/k8s-worker/tasks/config-worker-node.yml#L11-L354) が `irq_balance_package` の削除, `k8s_reserved_system_cpus_default` を基にしたアプリケーション用 CPU レンジ算出, GRUB コマンドラインの最適化, pin スクリプトと systemd サービスの展開, 初回リブートと待機をまとめて実施します。
6. [roles/k8s-worker/tasks/config.yml](roles/k8s-worker/tasks/config.yml#L8-L186) が kube-apiserver の起動待ちとトークン／CA ハッシュ取得, `worker-kubeadm.config.j2` の生成, 既存ノードの cordon / drain / delete, `kubeadm reset` と再 join, サービス有効化, 二度目のリブートを実行します。
7. [roles/k8s-worker/tasks/config-cilium-bgp-cplane.yml](roles/k8s-worker/tasks/config-cilium-bgp-cplane.yml#L8-L105) は `k8s_bgp.enabled` が true の場合にのみ発動し, マニフェスト出力ディレクトリを整備して `roles/k8s-common/templates/cilium-bgp-resources.yml.j2` をレンダリングし, 関連 CRD の存在確認後に適用します。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_ctrlplane_endpoint` | 各 `host_vars` | コントロールプレーン API アドレス。API 待機, firewall 設定, `kubeadm join` に使用します。|
| `k8s_ctrlplane_host` | 各 `host_vars` | `delegate_to` で kubeadm/kubectl を実行するコントロールプレーンホスト。|
| `enable_firewall` | `false` (`vars/all-config.yml`) | true の場合に firewall タスクを有効化します。|
| `firewall_backend` | OS 判定で `['ufw']` または `['firewalld']` | firewall 実装の選択。複数指定時はループで順次処理します。|
| `k8s_worker_enable_nodeport` | `false` | NodePort の開放を行うかどうか。|
| `k8s_worker_nodeport_range` | `30000-32767` | NodePort 開放レンジ。UFW ではコロン区切りに変換されます。|
| `k8s_kubeadm_config_store` | `{{ ansible_home_dir }}/kubeadm` | `kubeadm.config.yml` や BGP マニフェストを保存するディレクトリ。|
| `k8s_kubeadm_ignore_preflight_errors_arg` | `--ignore-preflight-errors=all` | `kubeadm join` に渡す preflight 無視オプション。|
| `k8s_drain_timeout_minutes` / `k8s_worker_delete_wait_sec` | `5` / `5` | cordon/drain/delete のタイムアウトと削除待機時間。|
| `k8s_reserved_system_cpus_default` | 未定義 | システム系に割り当てる CPU レンジ。CPU シールドや GRUB 設定がこの値を参照します。|
| `k8s_systemd_slices` | `['init.scope.d', 'system.slice.d', 'user.slice.d', 'user-.slice.d']` | cpuset ドロップインを配置する systemd スライス一覧。|
| `k8s_node_setup_tools_dir` | `/opt/k8snodes/sbin` | pin スクリプトやユーティリティの配置先。|
| `k8s_bgp.enabled` | 未定義 | true 時に Cilium BGP Control Plane マニフェストを生成・適用します。|
| `k8s_bgp.neighbors` | 未定義 | BGP ピア定義。`k8s_bgp.enabled: true` の場合は空であってはなりません。|

## 主な処理

- **Firewall 構成**: `enable_firewall` が有効な環境で UFW/firewalld を初期化し, 10250/tcp などの制御プレーン向けポートと NodePort 範囲を恒久的に開放します。
- **CPU シールドの準備**: systemd スライス単位で AllowedCPUs を固定し, IRQ 片寄せスクリプトと連携する前提を整備します。
- **GRUB と低遅延調整**: `k8s_reserved_system_cpus_default` に基づき `nohz_full` や `isolcpus` などのカーネルパラメータを更新し, ワーカースレッドと IRQ をアプリケーション用 / システム用に分離します。
- **kubeadm 再 join**: 既存ワーカーの cordon / drain / delete, `kubeadm reset`, `kubeadm join --config` を自動化し, containerd / kubelet を有効化して再起動します。
- **Cilium BGP Control Plane**: ノード固有の識別子で CRD マニフェストを生成し, CiliumBGPAdvertisement / CiliumBGPPeerConfig / CiliumBGPClusterConfig を適用して Pod/Service CIDR をルータへ広告します。
- **再起動とユーティリティ登録**: pin-worker-queue / pin-irqs の systemd サービスを enabled 登録し, OS チューニング後と join 後にそれぞれリブートします。

## テンプレート／ファイル

| テンプレート | 生成ファイル | 説明 |
| --- | --- | --- |
| [roles/k8s-worker/templates/worker-kubeadm.config.j2](roles/k8s-worker/templates/worker-kubeadm.config.j2) | kubeadm.config.yml ( 対象ホストの k8s_kubeadm_config_store 配下 ) | kubeadm join に渡す設定をまとめ, トークンと CA ハッシュを組み込んだ構成ファイルを生成します。 |
| [roles/k8s-worker/templates/systemd-cpuset.conf.j2](roles/k8s-worker/templates/systemd-cpuset.conf.j2) | 40-cpuset.conf ( 対象ホストの各 systemd スライス配下 ) | CPU シールド用に AllowedCPUs を固定し, k8s_systemd_slices の各ドロップインで共有する設定を作成します。 |
| [roles/k8s-worker/templates/pin-worker-queue.sh.j2](roles/k8s-worker/templates/pin-worker-queue.sh.j2) | pin-worker-queue.sh ( 対象ホストの k8s_node_setup_tools_dir 配下 ) | workqueue のアンバウンドスレッドをアプリ用 CPU に寄せるセットアップスクリプトを配置します。 |
| [roles/k8s-worker/templates/pin-worker-queue.service.j2](roles/k8s-worker/templates/pin-worker-queue.service.j2) | pin-worker-queue.service ( 対象ホストの systemd ユニットディレクトリ ) | pin-worker-queue.sh をワンショット実行し, ブート後に CPU ピニングを適用する systemd ユニットを登録します。 |
| [roles/k8s-worker/templates/pin-irqs.py.j2](roles/k8s-worker/templates/pin-irqs.py.j2) | pin-irqs.py ( 対象ホストの k8s_node_setup_tools_dir 配下 ) | 割込みをシステム用 CPU へ片寄せる Python スクリプトを配備します。 |
| [roles/k8s-worker/templates/pin-irqs.service.j2](roles/k8s-worker/templates/pin-irqs.service.j2) | pin-irqs.service ( 対象ホストの systemd ユニットディレクトリ ) | pin-irqs.py を起動して IRQ アフィニティを適用する systemd ユニットを登録します。 |
| [roles/k8s-common/templates/cilium-bgp-resources.yml.j2](roles/k8s-common/templates/cilium-bgp-resources.yml.j2) | Cilium BGP マニフェスト ( 対象ホストの cilium_bgp_manifest_dir 配下 ) | ノード固有の識別子を含む CiliumBGP* リソースをまとめたマニフェストを生成し, apply_delegate で指定したホストに保存します。 |

## ハンドラ

| ハンドラ | トリガー | 説明 |
| --- | --- | --- |
| [roles/k8s-worker/handlers/kubelet.yml](roles/k8s-worker/handlers/kubelet.yml) | `notify: kubelet_restarted_and_enabled` | kubelet の daemon-reload と再起動, enable をまとめて実施し, join 後のサービス状態を整えます。 |
| [roles/k8s-worker/handlers/reload-firewall.yml](roles/k8s-worker/handlers/reload-firewall.yml) | `notify: reload firewalld` / `notify: reload ufw` | firewall_backend に応じて firewalld もしくは UFW を再読み込みし, NodePort などのポート開放設定を反映させます。 |
| [roles/k8s-worker/handlers/reboot-node.yml](roles/k8s-worker/handlers/reboot-node.yml) | `notify: reboot_node_handler` | リブートを実行し, GRUB 変更や kubeadm 再 join 後の状態を確定させます。 |

## 検証ポイント

- control-plane で `kubectl get nodes` を実行し, 対象ワーカーが `Ready` になっているか確認します。
- `journalctl -u kubelet` で kubelet の再起動後にエラーが出ていないことを確認します。
- `/etc/systemd/system/*/40-cpuset.conf` が生成され, 期待する CPU レンジが書き込まれていることを確認します。
- `systemctl status pin-worker-queue pin-irqs` が `loaded (enabled)` でワンショット実行後に正常終了していることを確認します。
- `k8s_bgp.enabled: true` の場合は `kubectl get ciliumbgpclusterconfigs.cilium.io -A` 等でマニフェストが適用されていることを確認します。
- firewall を有効化した場合は `ufw status verbose` または `firewall-cmd --list-ports --zone=public` で想定ポートが開放されているか確認します。

## 補足と注意事項

- 本ロールは `config-worker-node.yml` と `config.yml` の両方でリブートを実行します。
- `config.yml` には `kubeadm reset` が含まれるため, 稼働中クラスタへ適用する際は事前に Pod 退避や停止計画を準備してください。`kubectl drain --ignore-daemonsets --delete-emptydir-data` は DaemonSet を退避しないため, 必要に応じて, 対象ノードで稼働する各 DaemonSet Pod の停止／再スケジューリング手順を整備し, Local Persistent Volume に格納されたデータは退避やアンマウントを含めた保全策を講じてから実行してください。
- control-plane 側で `kubeadm token create` や `kubectl` を実行するため, `k8s_ctrlplane_host` ではパスワードレス sudo などの権限を整備しておいてください。設定を誤ると join 用トークン取得が失敗します。
- Cilium BGP Control Plane のマニフェストは `k8s_bgp.apply_delegate` で指定したホスト ( 既定は `k8s_ctrlplane_host` )上で生成・適用されます。
- NodePort を有効化する場合は必要なサービスのみが公開されるよう, 上位ネットワーク機器側のアクセス制御リストも合わせて確認してください。
- firewall タスクはデフォルトで無効化されています。現状は動作検証が十分でないため, `enable_firewall` は `false` を推奨します。
