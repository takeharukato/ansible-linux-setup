# additional-routes ロール

## 概要

このロールは, 外部ネットワーク(例: VM Network(VMware), Pool-wide network associated with ethX(xcp-ng))につながるサーバから, 仮想環境内部管理ネットワークへの追加ルートを自動設定します。Debian/Ubuntu 系は netplan, RHEL 系は NetworkManager を利用します。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Network Interface Card | NIC | ネットワーク接続のためのインターフェース。 |
| NetworkManager | - | RHEL 系でネットワークを管理するサービス。 |
| netplan | - | Debian/Ubuntu 系でネットワーク設定を生成する仕組み。 |
| route | - | 宛先ネットワークに到達するための経路。 |
| metric | - | ルート優先度を示す数値。 |

## 前提条件

- 対象 OS: Debian/Ubuntu 系 (Ubuntu24.04を想定), RHEL9 系 (AlmaLinux9.6を想定)
- Ansible 2.15 以降, ansibleメタパッケージをディストリビューションから導入していることを想定
- `mgmt_nic` が正しく設定されていること

## 実行フロー

1. 変数を読み込み, `additional_network_routes` の定義を確認する。
2. Debian/Ubuntu 系は netplan 用設定を生成し, 文法検証を行う。
3. RHEL 系は NetworkManager にルートを設定し, 接続を再起動する。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `additional_network_routes` | `[]` | 追加ルート定義リスト。リストが空の場合は, 追加ルート設定処理を行わない。 |
| `mgmt_nic` | なし | ルートを適用する接続/インターフェース名。`group_vars/all/all.yml` で自動設定。 |

## 追加ルート定義の詳細

`additional_network_routes` 変数は, 以下のキーを持つ辞書を要素とするリストです:

| キー | 必須 | 説明 |
| --- | --- | --- |
| `address_family` | 必須 | `ipv4` または `ipv6` を指定。 |
| `destination` | 必須 | 宛先ネットワーク(CIDR)。 |
| `gateway` | 必須 | ゲートウェイアドレス。 |
| `metric` | 任意 | メトリック値。 |

## デフォルト動作

- `additional_network_routes` が未定義または空配列の場合, 追加ルート設定は行われません。

## OS 差異

### Debian/Ubuntu(netplan)

- `/etc/netplan/30-additional-routes.yaml` をテンプレートから生成。
- `netplan generate` で文法検証を行い, テンプレートに変更がある場合のみ `netplan apply` を実行。
- ゲートウェイへのオンリンクルートと宛先ネットワークへのルートを追加。

### RHEL(NetworkManager)

- `nmcli connection modify <mgmt_nic> ipv4.routes/ipv6.routes` でルートを上書き設定。
- `additional_network_routes` から `address_family: ipv4` の要素が 0 件の場合, ルート一覧は空として扱われ, `ipv4.routes` に空文字が設定されて既存の IPv4 ルートがクリアされます。同様に, `address_family: ipv6` の要素が 0 件の場合は `ipv6.routes` に空文字が設定され, 既存の IPv6 ルートがクリアされます。
- `nmcli connection up <mgmt_nic>` で設定を反映。

## テンプレート/ファイル

本ロールでは以下のファイルを出力します。

| テンプレートファイル | 出力先 | 既定の配置先 | 説明 |
| --- | --- | --- | --- |
| `templates/30-additional-routes.yaml.j2` | `/etc/netplan/30-additional-routes.yaml` | `/etc/netplan/30-additional-routes.yaml` | netplan v2 形式の追加ルート設定。 |

## 設定例

追加ルートを IPv4 と IPv6 の両方で設定する例です。記載先は, 変数ファイルです。

**記載先**:
- host_vars/ホスト名.yml または group_vars/all/all.yml

**記載例**:

```yaml
additional_network_routes:
  - address_family: "ipv4"
    destination: "192.168.30.0/24"
    gateway: "192.168.30.10"
  - address_family: "ipv6"
    destination: "fdad:ba50:248b:1::/64"
    gateway: "fdad:ba50:248b:1::10"
    metric: 100
```

**各項目の意味**:

| 項目 | 説明 | 記載例での値 | 動作 |
| --- | --- | --- | --- |
| `additional_network_routes` | 追加ルート定義のリストです。 | `[{...}, {...}]` | 指定したルートが追加されます。空配列の場合は追加ルート設定を行いません。 |
| `address_family` | `ipv4` または `ipv6` を指定します。 | `ipv4`, `ipv6` | `ipv4` は IPv4 ルート, `ipv6` は IPv6 ルートとして扱われます。 |
| `destination` | 宛先ネットワーク(CIDR)です。 | `192.168.30.0/24`, `fdad:ba50:248b:1::/64` | 指定した宛先ネットワークに対するルートが作成されます。 |
| `gateway` | ゲートウェイアドレスです。 | `192.168.30.10`, `fdad:ba50:248b:1::10` | 指定したゲートウェイ経由のルートになります。 |
| `metric` | ルートの優先度を表すメトリックです。 | `100` | 数値が小さいほど優先度が高くなります。指定しない場合は OS の既定値に従います。 |

## 検証ポイント

本節では, `additional-routes` ロール実行後に追加ルートが反映されているかを確認します。

### 前提条件

- `additional-routes` ロールが正常に完了していること (`changed` または `ok` の状態)。
- リモートホストへ SSH で接続可能であること。
- sudo 権限が利用可能であること。

### 1. 追加ルートの確認 (共通)

IPv4/IPv6 の追加ルートが反映されているかを確認します。

```bash
ip route
ip -6 route
```

**期待される出力例**:

```
192.168.30.0/24 via 192.168.30.10 dev ens160 metric 100
fdad:ba50:248b:1::/64 via fdad:ba50:248b:1::10 dev ens160 metric 100
```

**確認ポイント**:
- `additional_network_routes` で指定した宛先ネットワークとゲートウェイが表示されること。

### 2. Debian/Ubuntu(netplan) の設定ファイル確認

netplan 設定ファイルが配置されているかを確認します。

```bash
ls -l /etc/netplan/30-additional-routes.yaml
```

**確認ポイント**:
- `/etc/netplan/30-additional-routes.yaml` が存在すること。

### 3. RHEL(NetworkManager) の設定確認

NetworkManager に登録されたルートを確認します。

```bash
nmcli -f connection.id,ipv4.routes,ipv6.routes connection show "${mgmt_nic}"
```

**確認ポイント**:
- `ipv4.routes`/`ipv6.routes` に追加ルートが表示されること。

## トラブルシューティング

- Debian/Ubuntu 系で適用に失敗する場合は, `netplan generate` のエラー内容を確認してください。
- RHEL 系で反映されない場合は, `nmcli connection show "${mgmt_nic}"` で接続名とルート設定を確認してください。
