# frr-basic ロール

このロールは FRRouting (FRR) をインストールし, ルーティング機能を提供するホストで最低限必要となるシステム設定と FRR 本体の初期構成を適用します。Debian/Ubuntu 系ディストリビューションを対象としており, `ansible-playbook` を実行する制御ノードから対象ホストへ以下の作業を行います。

- FRR 関連パッケージ (`frr`, `frr-pythontools` など) の導入
- FRR サービスの有効化と起動 (`systemd`)
- `/etc/sysctl.d/90-frr-forwarding.conf` を配布し, IPv4/IPv6 のカーネルフォワーディングを有効化
- `frr.conf.j2` テンプレートを展開して `/etc/frr/frr.conf` を生成し, BGP 設定などを適用
- 設定更新時に `sysctl --system` や `systemctl restart frr` をハンドラ経由で実行

再実行可能な構成になっており, テンプレート内容に変更が無ければ変更は `changed: false` となります。

## 変数一覧

`host_vars` で次の変数を指定します。具体値は環境に合わせて定義してください。

| 変数名 | 役割 | 例 | 必須 | 備考 |
| ------ | ---- | -- | ---- | ---- |
| `frr_bgp_asn` | BGP 自律システム (Autonomous System - ASと略す)番号 | `65011` | 必須 | `frr.conf`を生成する`frr.conf.j2` テンプレートで使用。|
| `frr_bgp_router_id` | BGP Router-ID | `192.168.30.49` | 必須 | BGPセッションで使用するIPv4アドレスを指定する。IPv4 形式で指定。`frr.conf`を生成する`frr.conf.j2` テンプレートで使用。 |
| `frr_k8s_neighbors` | iBGP ピア情報のリスト | `[{ addr: '192.168.30.41', asn: 65011, desc: 'C1 control-plane' }, ...]` | 任意 | BGPセッションで使用するIPv4アドレスを指定する。IPv4 形式で指定。`frr.conf`を生成する`frr.conf.j2` テンプレートで使用。 |
| `frr_ebgp_neighbors` | eBGP ピア情報のリスト | `[{ addr: '192.168.90.1', asn: 65100, desc: 'External GW' }]` | 任意 | BGPセッションで使用するIPv4アドレスを指定する。IPv4 形式で指定。`frr.conf`を生成する`frr.conf.j2` テンプレートで使用。 |
| `frr_networks_v4` | 広告する IPv4 プレフィックス | `['192.168.30.0/24', '192.168.90.0/24']` | 任意 | BGP address-family ipv4 の設定に使用。`frr.conf`を生成する`frr.conf.j2` テンプレートで使用。 |
| `frr_networks_v6` | 広告する IPv6 プレフィックス | `['fd69:6684:61a:2::/64', 'fd69:6684:61a:90::/64']` | 任意 | BGP address-family ipv6 の設定に使用。 `frr.conf`を生成する`frr.conf.j2` テンプレートで使用。 |

テンプレート内で `ansible_hostname` を参照しており, 対象ホストに設定済みのホスト名が `hostname` ステートメントへ展開されます。

## 実行手順の例

1. `vars/all-config.yml` や `host_vars/<hostname>` で上記変数を定義します。
2. `ansible-playbook -i inventory/hosts frr.yml --tags frr-basic` などでロールを含むプレイブックを実行します。
3. 既存環境からの更新や検証時は `--check` オプションを併用し, 期待する差分のみ生成されるか確認します。

## 検証ポイント

以下を確認してください。

- 対象ホストで `systemctl status frr` が `active (running)` となっていること。
- `/etc/sysctl.d/90-frr-forwarding.conf` が所定内容で配置され, `sysctl net.ipv4.ip_forward` / `sysctl net.ipv6.conf.all.forwarding` が `1` を返すこと。
- `/etc/frr/frr.conf` がテンプレートの意図した内容 (BGP ピア, 広告プレフィックス等) になっていること。
- BGP ピアとのセッション状態が `show ip bgp summary` / `show bgp ipv6 unicast summary` で ESTABLISHED になっていること。

## 補足

- IPv6でBGPセッションを張ると, アンダーレイネットワーク(L3)のネットワークのIPv6ネットワークによるルーティング, BGP Network Layer Reachability Information (NLRI)でIPv4, IPv6プレフィクス交換を行う必要があり, 複雑化しやすい。このため, 本playbookでは, BGPセッションはIPv4で張り, 単純化しました。K8s のPod/Serviceネットワークの外側の接続を行う機能単位なのでまずは単純化する方針で設計しています。
- IPv4/IPv6 フォワーディング設定は drop-in ファイルで管理しており, 他ロールで `sysctl.d` を触る場合はファイル名重複に注意してください。
