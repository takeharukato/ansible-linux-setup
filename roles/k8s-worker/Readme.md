# k8s-worker ロール

Kubernetes ワーカーノードをクラスタへ再参加させる際に必要な OS チューニングと kubeadm join 手続きを自動化するロールです。`k8s-common` で行う基本セットアップを前提に、CPU シールドや IRQ 片寄せなどの低遅延設定、NodePort を含む防火壁調整、control-plane からの kubeadm トークン取得と再初期化、kubeconfig 関連スクリプトの展開までを一括で扱います。再実行可能な構成を意識しており、既存ノードの cordon / drain / delete を含むクリーンな再 join オペレーションを提供します。

## 主な処理と順序

1. **変数読込 (`tasks/load-params.yml`)**: OS 系差分 (`vars/cross-distro.yml`)、共通設定 (`vars/all-config.yml`)、API エンドポイント (`vars/k8s-api-address.yml`) を取り込み、Debian / RHEL それぞれのパッケージ名や GRUB パス、`k8s_ctrlplane_endpoint` 等を利用可能にします。
1. **プレースホルダタスク (`package.yml`, `directory.yml`, `user_group.yml`, `service.yml`)**: 将来の拡張用に include されています。現時点では処理は実装されていませんが、タスク構造を保つために呼び出されます。
1. **防火壁設定 (`config-k8sworker-firewall.yml`)**: `enable_firewall: true` かつバックエンドに応じて UFW または firewalld を初期化し、10250/tcp を control-plane からのみ許可します。`k8s_worker_enable_nodeport: true` を指定すると `k8s_worker_nodeport_range` に従って NodePort 範囲を追加で開放します。IPv4/IPv6 は `k8s_ctrlplane_endpoint` の種別に応じて処理されます。
1. **CPU シールド (`config-shielding.yml`)**: `k8s_systemd_slices`（既定で init/system/user スライス）に対して `systemd-cpuset.conf.j2` を展開し、`k8s_reserved_system_cpus_default` で指定した CPU へシステムスレッドを寄せます。
1. **ワーカーノード OS 調整 (`config-worker-node.yml`)**

    - `irqbalance` を削除し、`k8s_reserved_system_cpus_default` をもとにアプリケーション用／システム用 CPU 範囲を算出します。
    - GRUB のカーネルパラメータへ `nohz_full`, `isolcpus`, `rcu_nocbs`, `irqaffinity`, `workqueue.*`, `systemd.cpu_affinity` を設定し、`config-grub-debian.yml` / `config-grub-rhel.yml` が OS 別に `update-grub` / `grub2-mkconfig` を実行します。
    - `pin-worker-queue.sh`, `pin-irqs.py` を `/opt/k8snodes/sbin` に配置し、対応する systemd サービスを有効化して再起動時にワーカースレッドと IRQ をハウスキーピング CPU へ固定します。
    - ここまでの設定変更を反映するため１回目の再起動を行い、SSH 復帰を待機します。

1. **kubeadm 再 join (`config.yml`)**

    - control-plane ノードへ `delegate_to` し、既存トークンを取得（なければ生成）して `k8s_join_token_from_ctrlplane` に格納します。同時に CA ハッシュ (`k8s_join_discovery_hash_from_ctrlplane`) を収集し、API サーバ疎通を確認します。
    - 対象ノード名を取得し、control-plane 側で `kubectl cordon/drain/delete` を実行、既存ワーカー登録を整理します。`k8s_worker_delete_wait_sec` だけ待機することで API 反映を待ちます。
    - 対象ノード上で `kubeadm reset -f` 後に kubelet/containerd を停止し、`/etc/kubernetes/manifests` や `/etc/cni/net.d` を削除、`k8s_kubeadm_config_store` に生成した `worker-kubeadm.config.yml` を `kubeadm join --config` で適用します。`k8s_kubeadm_ignore_preflight_errors_arg`（既定で `--ignore-preflight-errors=all`）を併用します。
    - kubelet/containerd の自動起動を有効化し、`kubelet_restarted_and_enabled` ハンドラを呼び出した後、２回目の再起動と接続待ちを実施します。

上記フロー全体で `k8s_ctrlplane_endpoint`・`k8s_ctrlplane_host` が必須となり、control-plane 上で kubeadm/kubectl が正しく動作していることが前提です。

## 変数と制御フラグ

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `k8s_ctrlplane_endpoint` | 各 `host_vars` | API サーバの (IPv4/IPv6) アドレス。firewall 設定と kubeadm join で使用。|
| `k8s_ctrlplane_host` | 各 `host_vars` | control-plane ノードへ `delegate_to` するホスト名。|
| `enable_firewall` | `vars/all-config.yml` | UFW/firewalld を構成するかどうか。`true` 時に `config-k8sworker-firewall.yml` が実行されます。現時点では, Firewallを有効にした場合の動作に未対応です。`enable_firewall`変数を`false`に設定してください。|
| `firewall_backend` | `vars/cross-distro.yml` | 利用する Firewall バックエンド。Debian 系は `['ufw']`, RHEL 系は `['firewalld']` が既定。|
| `k8s_worker_enable_nodeport` | `false` | NodePort を公開する場合に `true`。指定範囲を Firewall へ開放します。|
| `k8s_worker_nodeport_range` | `"30000-32767"` | NodePort の開放レンジ。UFW では `30000:32767` へ変換されます。|
| `k8s_reserved_system_cpus_default` | 未定義 | システム系に割り当てる CPU リスト（例: `"0-1"`）。定義時に CPU シールドと IRQ 片寄せが有効化されます。未定義なら関連処理はスキップされます。|
| `k8s_systemd_slices` | `defaults/main.yml` | cpuset 設定を適用する systemd スライス一覧。|
| `k8s_kubeadm_config_store` | `{{ ansible_home_dir }}/kubeadm` | `worker-kubeadm.config.yml` を配置するディレクトリ。|
| `k8s_kubeadm_ignore_preflight_errors_arg` | `--ignore-preflight-errors=all` | kubeadm join 時の preflight 無視パラメータ。|
| `k8s_drain_timeout_minutes` / `k8s_worker_delete_wait_sec` | `5` / `5` | cordon/drain/delete の待機時間を制御。|
| `k8s_node_setup_tools_dir` | `/opt/k8snodes/sbin` | pin スクリプトを配置するディレクトリ。|
| `k8s_operator_user` | `kube` |オペレータユーザ名。kubeconfig 配布や Helm リポジトリ登録で利用。 |

その他、`vars/cross-distro.yml` で `grub_default_cfg_path`, `irq_balance_package`, `kubelet_resolv_conf_path` などの OS 差分を吸収しています。追加で調整したい場合は `vars/all-config.yml` / `host_vars/` で上書きしてください。

## テンプレートとスクリプト

- `templates/worker-kubeadm.config.j2`: control-plane のトークン・CA ハッシュを埋め込み、IPv6 時は `[addr]:port` 形式に変換した JoinConfiguration を生成します。
- `templates/systemd-cpuset.conf.j2`: systemd各スライスの `AllowedCPUs` を `k8s_reserved_system_cpus_default` に固定します。
- `templates/pin-worker-queue.sh.j2` / `pin-worker-queue.service.j2`: workqueue (unbound) をシステム CPU に固定するユーティリティと unit ファイル。
- `templates/pin-irqs.py.j2` / `pin-irqs.service.j2`: IRQ affinity を制御する Python スクリプトと systemd unit。`--set-default` と `--set-existing` を併用し、全 IRQ を指定 CPU へ片寄せます。

## ハンドラ

- `handlers/kubelet.yml`: `kubelet_restarted_and_enabled` 通知で kubelet を再起動し、daemon-reload を行います。
- `handlers/reload-firewall.yml`: `reload ufw` / `reload firewalld` 通知に応じて各 Firewall を再読み込みします。
- `handlers/reboot-node.yml`: `reboot_node_handler` を受け取った場合に追加の再起動を実行します（`config.yml` で通知）。

## 検証ポイント

- control-plane で `kubectl get nodes` を実行し、対象ワーカーが `Ready` かつ `STATUS` に `SchedulingDisabled` が含まれていないことを確認します。
- `sudo journalctl -u kubelet` で kubelet がエラーなく起動していることを確認します。
- `sudo systemctl status pin-worker-queue pin-irqs` が `loaded (enabled)` かつ `Active: inactive (dead)` / `oneshot` 正常終了になっていること。
- `cat /proc/cmdline` に `nohz_full`, `isolcpus`, `rcu_nocbs`, `irqaffinity` などが追加されていること。必要に応じて `grubby --info` でも確認します。
- firewall 設定が反映されていること (`ufw status verbose` または `firewall-cmd --list-ports` / `--direct --get-all-rules`)。
- `{{ k8s_node_setup_tools_dir }}` 配下に pin スクリプトが存在し、`/etc/systemd/system/` に対応する unit ファイルが配置されていること。

## 補足と注意事項

- `config.yml` には `kubeadm reset` を含むため、稼働中クラスタへ適用する際は計画停止・Pod 退避を事前に済ませてください。`kubectl drain --ignore-daemonsets --delete-emptydir-data` を自動実行しますが、DaemonSet / LocalPV の扱いに注意が必要です。
- `k8s_reserved_system_cpus_default` 未定義の場合、CPU シールド／IRQ 片寄せ関連タスクはスキップされます（その場合でも GRUB 変更は行われません）。
- control-plane 側で実行する `kubeadm token create` / `kubectl` の実行にはパスワードレス sudo 等が必要です。`k8s_ctrlplane_host` の設定を誤ると join 用トークンの取得が失敗するためご注意ください。
- NodePort を有効化する場合は、必要なサービスのみが公開されるよう上位ネットワーク機器側の ACL も合わせて確認してください。
- 追加の `--skip-tags` を使えば CPU シールドや Firewall 処理を個別に無効化できます（例: `--skip-tags config-k8sworker-firewall`）。
- 現時点では, Firewallを有効にした場合の動作に未対応です。`enable_firewall`変数を`false`に設定してください。
