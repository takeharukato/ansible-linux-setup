# additional-routes ロール

## 概要

このロールは, 外部ネットワーク(`VM Network`(VMware)や`Pool-wide network associated with ethX`(xcp-ng))につながっているサーバから仮想環境内部管理ネットワークへの追加ルートを自動設定するためのものです。netplan を利用する Debian/Ubuntu 系と, NetworkManager を利用する RHEL 系の双方に対応しています。

## 主な処理内容

- 追加ルートは `additional_network_routes` が定義され, 要素数が 1 以上のときのみ設定される
- IPv4/IPv6 デュアルスタックに対応し, メトリック指定にも対応
- 管理用インターフェース名は `mgmt_nic` を使用 ( デフォルトのインターフェース名は, [group_vars/all/all.yml](../../../group_vars/all/all.yml) で自動判定 )

### Debian/Ubuntu (netplan)

- `/etc/netplan/30-additional-routes.yaml` をテンプレートから生成
- `netplan generate` で文法検証し, テンプレートに変更がある場合のみ `netplan apply` を実行
- ゲートウェイへのオンリンクルートと宛先ネットワークへのルートを追加

### RHEL 系 (NetworkManager)

- `nmcli connection modify <mgmt_nic> ipv4.routes/ipv6.routes` でルートを上書き設定
- ルートを空にしたい場合は空リストにしてクリア
- `nmcli connection up <mgmt_nic>` で設定を反映

## 変数

- `additional_network_routes`: 追加ルートのリスト ( 必須, 空なら処理スキップ )
  - `address_family`: `ipv4` または `ipv6`
  - `destination`: 宛先ネットワーク (CIDR)
  - `gateway`: ゲートウェイアドレス
  - `metric`: メトリック ( 省略可 )
- `mgmt_nic`: ルートを設定する接続/インターフェース名。`group_vars/all/all.yml` で環境に応じて自動設定。

### 設定例

```yaml
additional_network_routes:
  - address_family: 'ipv4'
    destination: "192.168.30.0/24"
    gateway: "192.168.30.10"
  - address_family: 'ipv6'
    destination: "fdad:ba50:248b:1::/64"
    gateway: "fdad:ba50:248b:1::10"
    metric: 100
```

## ファイル構成と実装

- テンプレート: `templates/30-additional-routes.yaml.j2` ( netplan v2 形式 )
- Ubuntu 用タスク: `tasks/config-ubuntu-add-routes.yml` ( 生成→検証→適用 )
- RHEL 用タスク: `tasks/config-rhel-add-routes.yml` ( nmcli で routes を設定し connection up )
- 追加ルート定義が空の場合はどのタスクも実行されない

## 動作確認

設定適用後の確認例:

```bash
ip route           # IPv4 ルート
ip -6 route        # IPv6 ルート
nmcli -f connection.id,ipv4.routes,ipv6.routes connection show "${mgmt_nic}"  # RHEL 系の確認
```
