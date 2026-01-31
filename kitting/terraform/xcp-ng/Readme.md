# TerraformによるXCP-ng仮想環境構築用ファイル群について

- [TerraformによるXCP-ng仮想環境構築用ファイル群について](#terraformによるxcp-ng仮想環境構築用ファイル群について)
  - [プロジェクト構造](#プロジェクト構造)
  - [本Terraformファイルから作成されるVMの構成](#本terraformファイルから作成されるvmの構成)
    - [Infrastructure VM ( 5台 )](#infrastructure-vm--5台-)
    - [pool-wide network接続開発用VM(vmlinux) ( 5台 )](#pool-wide-network接続開発用vmvmlinux--5台-)
    - [内部プライベートネットワーク接続開発用VM(devlinux) (5台)](#内部プライベートネットワーク接続開発用vmdevlinux-5台)
    - [Kubernetes クラスタを構成するVM ( 9台 )](#kubernetes-クラスタを構成するvm--9台-)
  - [本Terraformファイルから生成されるネットワーク構成](#本terraformファイルから生成されるネットワーク構成)
  - [各VMの設定パラメタの修正方法](#各vmの設定パラメタの修正方法)
  - [各ネットワークの設定パラメタの修正方法](#各ネットワークの設定パラメタの修正方法)
  - [セットアップ手順](#セットアップ手順)
    - [新規環境の構築](#新規環境の構築)
      - [1. 環境変数の設定](#1-環境変数の設定)
      - [2. terraform.tfvarsの作成](#2-terraformtfvarsの作成)
      - [3. Terraformの初期化](#3-terraformの初期化)
      - [4. 設定の検証とデプロイ](#4-設定の検証とデプロイ)
    - [既存環境のアップグレード](#既存環境のアップグレード)
      - [State移行手順](#state移行手順)
        - [ステップ1: ドライラン確認](#ステップ1-ドライラン確認)
        - [ステップ2: 実際の移行](#ステップ2-実際の移行)
        - [ステップ3: 最終検証](#ステップ3-最終検証)
  - [Makefileターゲット](#makefileターゲット)
    - [初期化と検証](#初期化と検証)
    - [ネットワークターゲット](#ネットワークターゲット)
    - [ビルドターゲット](#ビルドターゲット)
    - [個別VMターゲット](#個別vmターゲット)
    - [削除ターゲット](#削除ターゲット)
    - [State移行ターゲット](#state移行ターゲット)
    - [クリーンアップターゲット](#クリーンアップターゲット)
  - [VM削除時の動作確認](#vm削除時の動作確認)
  - [注意事項](#注意事項)
  - [トラブルシューティング](#トラブルシューティング)
    - [State移行でエラーが出る場合](#state移行でエラーが出る場合)
    - [ネットワークが重複作成される場合](#ネットワークが重複作成される場合)
    - [Validationエラーが出る場合](#validationエラーが出る場合)
  - [新規VM追加方法](#新規vm追加方法)
    - [1. terraform.tfvarsにVM定義を追加する](#1-terraformtfvarsにvm定義を追加する)
    - [2. Makefileにターゲット追加 ( 任意 )](#2-makefileにターゲット追加--任意-)
    - [3. 適用確認](#3-適用確認)
  - [参考情報](#参考情報)

このドキュメントはTerraform構成と付属の`Makefile`に定義されたターゲットの役割をまとめたものです。
本TerraformはXCP-ngをXen Orchestra (XO) 経由で操作する構成を想定しています。

## プロジェクト構造

```text
xcp-ng-base-servers/
├── main.tf                    # プロバイダー設定
├── versions.tf                # Terraform/Provider バージョン制約
├── variables.tf               # 入力変数定義
├── data.tf                    # データソース定義
├── locals.tf                  # VMのプロファイル定義 (ローカル変数)
├── outputs.tf                 # 出力値定義
├── networks.tf                # ネットワークリソース
├── vms-infrastructure.tf      # インフラVM定義
├── vms-vmlinux.tf             # Vmlinux開発VM定義
├── vms-devlinux.tf            # Devlinux開発VM定義
├── vms-k8s.tf                 # Kubernetes クラスタを構成するVMの定義
├── terraform.tfvars           # 変数値 ( gitignore対象 )
├── terraform.tfvars.example   # 変数値テンプレート
├── Makefile                   # ビルド自動化
├── modules/
│   ├── vm/                    # VMモジュール
│   └── network/               # ネットワークモジュール
├── templates/
│   └── base.yaml.tpl          # Cloud-initテンプレート
└── scripts/
    ├── migrate-all.sh                      # 統合State移行スクリプト
    ├── migrate-state-infrastructure.sh     # Infrastructure VM移行
    ├── migrate-state-vmlinux.sh            # Vmlinux VM移行
    ├── migrate-state-devlinux.sh           # Devlinux VM移行
    └── migrate-state-k8s.sh                # K8s VM移行
```

## 本Terraformファイルから作成されるVMの構成

本Terraformファイルから生成される仮想マシン(VM)と用途は, 以下の通りです:

|仮想マシン種別|仮想マシンのラベル名|仮想マシンのキー名|用途|
|---|---|---|---|
|Infrastructure VM|router|`router`|pool-wide networkと内部プライベートネットワーク間のルータ, radvd, DHCPv4サーバ|
|Infrastructure VM|mgmt-server|`mgmt-server`|管理サーバー ( DNS, LDAP, コンテナレジストリなど ) |
|Infrastructure VM|rhel-server|`rhel-server`|RHELベースの管理サーバー検証用VM|
|Infrastructure VM|ubuntu-server|`ubuntu-server`|Ubuntuベースの管理サーバー検証用VM|
|Infrastructure VM|devserver|`devserver`|管理サーバー動作確認用予備VM ( 通常作成不要 ) |
|pool-wide network接続開発用VM|vmlinux1|`vmlinux1`|外部ネットワーク接続開発VM ( Ubuntu ) |
|pool-wide network接続開発用VM|vmlinux2|`vmlinux2`|外部ネットワーク接続開発VM ( Ubuntu ) |
|pool-wide network接続開発用VM|vmlinux3|`vmlinux3`|外部ネットワーク接続開発VM ( Ubuntu ) |
|pool-wide network接続開発用VM|vmlinux4|`vmlinux4`|外部ネットワーク接続開発VM ( RHEL ) |
|pool-wide network接続開発用VM|vmlinux5|`vmlinux5`|外部ネットワーク接続開発VM ( RHEL ) |
|内部プライベートネットワーク接続開発用VM|devlinux1|`devlinux1`|内部ネットワーク接続開発VM ( Ubuntu ) |
|内部プライベートネットワーク接続開発用VM|devlinux2|`devlinux2`|内部ネットワーク接続開発VM ( Ubuntu ) |
|内部プライベートネットワーク接続開発用VM|devlinux3|`devlinux3`|内部ネットワーク接続開発VM ( Ubuntu ) |
|内部プライベートネットワーク接続開発用VM|devlinux4|`devlinux4`|内部ネットワーク接続開発VM ( RHEL ) |
|内部プライベートネットワーク接続開発用VM|devlinux5|`devlinux5`|内部ネットワーク接続開発VM ( RHEL ) |
|Kubernetes クラスタVM|k8sctrlplane01|`k8sctrlplane01`|K8s Cluster01 コントロールプレイン|
|Kubernetes クラスタVM|k8sworker0101|`k8sworker0101`|K8s Cluster01 ワーカーノード1|
|Kubernetes クラスタVM|k8sworker0102|`k8sworker0102`|K8s Cluster01 ワーカーノード2|
|Kubernetes クラスタVM|frr01|`frr01`|K8s Cluster01 FRRルーター|
|Kubernetes クラスタVM|k8sctrlplane02|`k8sctrlplane02`|K8s Cluster02 コントロールプレイン|
|Kubernetes クラスタVM|k8sworker0201|`k8sworker0201`|K8s Cluster02 ワーカーノード1|
|Kubernetes クラスタVM|k8sworker0202|`k8sworker0202`|K8s Cluster02 ワーカーノード2|
|Kubernetes クラスタVM|frr02|`frr02`|K8s Cluster02 FRRルーター|
|Kubernetes クラスタVM|extgw|`extgw`|疑似外部ネットワークゲートウェイ ( eBGP集約 ) |

**留意事項**: VMのキー名は, terraform.tfvarsの各VMグループ ( `infrastructure_vms`, `vmlinux_vms`, `devlinux_vms`, `k8s_vms` ) 内でVM定義のキーとして使用します。

### Infrastructure VM ( 5台 )

仮想環境内部のVM間で共通的に使用されるサービスを提供するVM群を`Infrastructure VM`と呼ぶ。

- router pool-wide networkと内部プライベートネットワーク間のルータ動作, 内部プライベートネットワークに対するルータ広告デーモン(rtadvd)やDHCPv4サーバを動作させることを想定している。
- mgmt-server 管理サーバー。仮想環境内部向けのDNSサーバ, LDAPサーバ, コンテナレジストリ(Gitlab)などを動作させることを想定している。
- rhel-server RHELベースの管理サーバー(管理サーバ構築テスト用)
- ubuntu-server Ubuntuベースの管理サーバー(管理サーバ構築テスト用)

上記の他に, `devserver`というVMが定義されている。`devserver`は, 管理サーバーの動作確認用の予備として定義しているが通常作成する必要はない。

### pool-wide network接続開発用VM(vmlinux) ( 5台 )

pool-wide networkに接続された開発用VMを生成する。
これらのVMには, ソフトウエア開発用のゲストOS環境を構築することを想定したストレージ容量が設定され, pool-wide networkに接続される。
これらのVMは仮想環境外部と直接通信することが可能であるため, 他のVMのゲスト環境を構築する用途で用いることを想定している。

vmlinux1からvmlinux3は, UbuntuベースのVMテンプレートから生成され, vmlinux4からvmlinux4は, RHELベースのVMテンプレートから生成されることを想定している。

これらのVMのMACアドレスは, 仮想環境による自動MACアドレス割り当て機能によって割り当てられるように設定されている。

### 内部プライベートネットワーク接続開発用VM(devlinux) (5台)

内部プライベートネットワークのみに接続された開発用VMを生成する。
これらのVMには, ソフトウエア開発用のゲストOS環境を構築することを想定したストレージ容量が設定され, 内部プライベートネットワークに接続される。
これらのVMは, Infrastructure VMのrouterノードを通して, 仮想環境外部のネットワークに接続されることを想定している。Infrastructure VMのrouterノードのVMを生成し, ゲストOS環境の設定が完了してからこれらのVMを起動することを推奨する。

devlinux1からdevlinux3は, UbuntuベースのVMテンプレートから生成され, devlinux4からdevlinux4は, RHELベースのVMテンプレートから生成されることを想定している。

これらのVMのMACアドレスは, 仮想環境による自動MACアドレス割り当て機能によって割り当てられるように設定されている。

### Kubernetes クラスタを構成するVM ( 9台 )

本Terraformファイルでは, Cluster01とCluster02の2つのKubernetes クラスタを構成することを想定している。
Cluster01とCluster02それぞれに, `K8sNetwork01`, `K8sNetwork02`という各クラスタ内部に閉じたプライベートネットワークが生成される。
`K8sNetwork01`, `K8sNetwork02`は, 異なる自律システム(Autonomous System(AS))を構成し, eBGPにより, ルート情報を他のASに対して広告する。
これらのASから広告されたeBGP広告を異なるAS間で交換するためのネットワークとして, `coreNetwork`が作成される。`coreNetwork`には, 各ASから受け取ったBGPを他のASに広告するためのホストとして, `extgw`VMが接続される。
各K8sクラスタのプライベートネットワーク(`K8sNetwork01`, `K8sNetwork02`)内には, 当該のプライベートネットワーク内のK8sノードからiBGP広告を受け取り, `extgw`にeBGP広告するためのホスト`frr*`が作成される(*にはクラスタ番号(01,02など)が入る)。`frr*`と`extgw`間は, `coreNetwork`を通して接続されており, eBGP広告は, `coreNetwork`を通して行われる。`frr*`とプライベートネットワーク内のK8sノードは, 各K8sクラスタのプライベートネットワーク(`K8sNetwork01`, `K8sNetwork02`)を通して, iBGP広告を行う。

- k8sctrlplane01: K8s Cluster01のコントロールプレイン
- k8sworker0101-0102: K8s Cluster01のワーカーノード (2台)
- frr01: Cluster01内のFRRノード
- k8sctrlplane02: K8s Cluster02のコントロールプレイン
- k8sworker0201-0202: K8s Cluster02のワーカーノード (2台)
- frr02: Cluster02内のFRRノード
- extgw: Cluster01, Cluster02内のFRRノードから広告されたeBGP広告を他のASに広告するためのFRRノード

Kubernetes クラスタを構成するVM群は, 内部プライベートネットワークに接続され, ゲストOS環境構築時などは, 内部プライベートネットワークを通して外部のネットワークに接続されることを想定している。

## 本Terraformファイルから生成されるネットワーク構成

本Terraformファイルから生成される仮想ネットワークと用途は, 以下の通りです:

|ネットワークのラベル名|ネットワークのキー名 (`network_key`)|用途|
|---|---|---|
|GlobalPrivateManagementNetwork|`gpn_mgmt`|仮想化基盤内に閉じた内部プライベートネットワーク。本ネットワークに接続された開発VM(devlinux)やK8sクラスタを構成するVM群の構築作業などの管理・運用作業に使用する。|
|K8sNetwork01|`k8s_net01`|Kubernetes Cluster01用のプライベートネットワーク|
|K8sNetwork02|`k8s_net02`|Kubernetes Cluster02用のプライベートネットワーク|
|coreNetwork|`core_net`|Kubernetes クラスタ間でのeBGP広告による経路交換を行うためのネットワーク|
|pool-wide network (※)|`mgmt`|XCP-ngのプール間をまたがって接続される管理ネットワーク。仮想環境外部に直接出ることが可能。Terraform管理外の既存ネットワーク。|

留意事項: `network_key`は, terraform.tfvarsのVMネットワーク設定時に使用するキー名です。VMのnetworks配列内で`network_key`パラメータとして指定します。

## 各VMの設定パラメタの修正方法

本Terraformファイルでは, 各VMについて, 以下のパラメタを個別に設定可能です。未指定時は, 各VM種別ごとのプロファイルに基づいてデフォルト値を設定します。

|パラメタ名|意味|設定値の例|
|---|---|---|
|template_type|VM作成時に使用するテンプレート種別|"ubuntu" または "rhel"|
|firmware|VM起動時のファームウェア種別|"uefi" または "bios"|
|resource_profile|リソース割り当てプロファイル名|"infrastructure", "vmlinux", "devlinux", "k8s_ctrlplane", "k8s_worker", "frr", "extgw"|
|networks|接続するネットワークのキー名とMACアドレスのリスト|`[{ network_key = "mgmt", mac_address = "00:50:56:00:46:51" }]`|
|disk_gb|(オプション) ディスク容量 (単位:GiB)|50|
|vcpus|(オプション) 仮想CPU数(単位:個)|8|
|memory_mb|(オプション) メモリ容量 (単位:MiB)|8192|
|power_state|(オプション) 初期電源状態|"Running" または "Halted"|

VMにパラメタを設定する場合は, 以下の形式で設定対象VMのキー名を指定して設定パラメタを記載したobject変数を設定します。

```hcl
<設定対象VMのキー名>=<設定パラメタを記載したobject変数>
```

terraform.tfvarsファイル内に記載する具体的な設定例を以下に示します。

```hcl
vmlinux_vms = {
  vmlinux1 = {
    template_type    = "ubuntu"
    firmware         = "uefi"
    resource_profile = "infrastructure"
    # リソースプロファイルの値をオーバーライドする例
    disk_gb          = 128      # デフォルトから変更
    vcpus            = 8        # デフォルトから変更
    memory_mb        = 16384    # デフォルトから変更
    networks = [
      { network_key = "mgmt", mac_address = "00:50:56:00:aa:bb" },
      { network_key = "gpn_mgmt", mac_address = null }  # MACアドレス自動割り当て
    ]
  }
}
```

## 各ネットワークの設定パラメタの修正方法

本Terraformファイルでは, 各ネットワーク種別ごとに以下のパラメタを設定可能です。

|パラメタ名|意味|設定値の例|
|---|---|---|
|automatic|ネットワークをVMに自動的にアタッチするか|true または false|
|default_is_locked|ネットワークをデフォルトでロックするか|true または false|
|mtu|ネットワークのMTU値|1500, 9000など|
|name_description|ネットワークの説明文|"K8s Cluster 01 Network"|
|nbd|NBD (Network Block Device)を有効にするか|true または false|
|vlan|VLAN ID (0はタグなし, 1-4094)|100, 200など|
|source_pif_device|VLAN作成元の物理インターフェース名 (vlanとセット)|"eth0", "eth1"など|

**留意事項**: `vlan`と`source_pif_device`はXenOrchestra Providerの制約により, セットで指定する必要があります。どちらか一方だけを指定するとエラーになります。

ネットワークにパラメタを設定する場合は, 以下の形式で設定対象ネットワークのキー名を指定して設定パラメタを記載したobject変数を設定します。

```hcl
<設定対象ネットワークのキー名>=<設定パラメタを記載したobject変数>
```

terraform.tfvarsファイル内に記載する具体的な設定例を以下に示します。

```hcl
network_options = {
  # 例1: 単一ホスト内のプライベートネットワーク
  gpn_mgmt = {
    automatic         = false
    default_is_locked = false
    mtu               = 1500
    name_description  = "Global Private Management Network"
    nbd               = false
    # vlan と source_pif_device を指定しない = 単一ホスト内のみ
  }
  # 例2: 複数ホスト間で拡張可能なVLANネットワーク
  k8s_net01 = {
    name_description  = "K8s Cluster 01 Network"
    vlan              = 100         # VLAN ID
    source_pif_device = "eth0"      # 物理インターフェース ( vlanとセット )
    mtu               = 1500
  }
  # 例3: ジャンボフレーム対応ネットワーク
  storage_net = {
    name_description  = "Storage Network"
    mtu               = 9000        # ジャンボフレーム
    vlan              = 200
    source_pif_device = "eth1"
  }
}
```

## セットアップ手順

### 新規環境の構築

新規にインフラを構築する場合の手順:

#### 1. 環境変数の設定

XO接続パスワードは環境変数で設定します:

```bash
export TF_VAR_xoa_password="your_password_here"
```

#### 2. terraform.tfvarsの作成

```bash
cp terraform.tfvars.example terraform.tfvars
# terraform.tfvarsを編集して環境に合わせて設定
# - xoa_url: Xen OrchestraのURL
# - xoa_username: ユーザー名
# - network_names: ネットワーク名 ( 環境に応じて変更 )
# - 各VMの設定 ( template_type, firmware, resource_profile, networksなど )
```

#### 3. Terraformの初期化

```bash
terraform init
```

または

```bash
make prepare
```

#### 4. 設定の検証とデプロイ

```bash
# 構文検証
terraform validate

# 実行計画の確認
terraform plan

# 全リソースのデプロイ
terraform apply
```

または段階的なデプロイ:

```bash
# 基本インフラのみ構築
make build

# K8sクラスターも含めて構築
make build-k8s
```

個別VM構築:

```bash
make router           # routerのみ
make devlinux         # devlinuxグループ全体
make cluster01        # K8s cluster01全体
```

### 既存環境のアップグレード

既存のterraform.tfstateがある環境で, 旧構成から新しいモジュール構造にアップグレードする場合はState移行が必要です。

#### State移行手順

旧構成 ( xen_vmlinux.tf, xen_vms.tf, xen_k8s.tf ) から新しいモジュール構造へState移行する手順:

##### ステップ1: ドライラン確認

```bash
./scripts/migrate-all.sh --dry-run
```

または個別グループ:

```bash
./scripts/migrate-state-infrastructure.sh --dry-run
./scripts/migrate-state-vmlinux.sh --dry-run
./scripts/migrate-state-devlinux.sh --dry-run
./scripts/migrate-state-k8s.sh --dry-run
```

##### ステップ2: 実際の移行

```bash
./scripts/migrate-all.sh
```

または段階的に:

```bash
make migrate-infrastructure
terraform plan -target='module.infrastructure_vms'  # 差分ゼロ確認

make migrate-vmlinux
terraform plan -target='module.vmlinux_vms'         # 差分ゼロ確認

make migrate-devlinux
terraform plan -target='module.devlinux_vms'        # 差分ゼロ確認

make migrate-k8s
terraform plan -target='module.k8s_vms'             # 差分ゼロ確認
```

##### ステップ3: 最終検証

```bash
terraform plan  # 全体で差分がないことを確認
```

移行ログは`scripts/migration-*.log`に保存されます。

## Makefileターゲット

### 初期化と検証

```bash
make init           # Terraform初期化 ( terraform init )
make validate       # 設定検証 ( terraform validate )
make plan           # 実行計画確認 ( terraform plan )
make fmt            # コードフォーマット ( terraform fmt )
```

### ネットワークターゲット

```bash
make networks       # ネットワーク作成
make destroy-networks  # ネットワーク削除
```

### ビルドターゲット

```bash
make build          # 基本インフラ構築 ( router, mgmt-server, vmlinux, devlinux )
make build-k8s      # K8sクラスター構築 ( cluster01, cluster02, extgw )
```

### 個別VMターゲット

```bash
# Infrastructure
make router
make devserver
make rhel-server
make ubuntu-server
make mgmt-server

# Devlinux
make devlinux1      # 個別
make devlinux       # 全体

# Vmlinux
make vmlinux1       # 個別
make vmlinux        # 全体

# Kubernetes
make k8sctrlplane01
make k8sworker0101
make frr01
make cluster01      # Cluster01全体
make cluster02      # Cluster02全体
make extgw
make frr            # FRRルーター全体 ( frr01, frr02 )
make gateways       # ゲートウェイ全体 ( extgw, frr01, frr02 )
```

### 削除ターゲット

```bash
# 個別VM削除
make destroy-router
make destroy-devlinux1
make destroy-k8sctrlplane01

# グループ削除
make destroy-devlinux
make destroy-vmlinux
make destroy-cluster01
make destroy-cluster02

# 全削除
make destroy
```

### State移行ターゲット

```bash
make migrate                    # 全グループ一括移行
make migrate-infrastructure     # Infrastructure VMのみ
make migrate-vmlinux            # Vmlinux VMのみ
make migrate-devlinux           # Devlinux VMのみ
make migrate-k8s                # K8s VMのみ
```

### クリーンアップターゲット

```bash
make clean          # ログファイル削除
make clean-state    # Terraform state削除 ( 注意! )
make distclean      # 完全初期化 ( .terraform含む )
```

## VM削除時の動作確認

VM削除時にcloud-configリソースも正しく削除されることを確認:

```bash
make destroy-router
# cloud-configとVMの両方が削除されることを確認
terraform state list  # module.infrastructure_vms["router"]が消えていることを確認
```

## 注意事項

1. パスワード管理: `xoa_password`は環境変数で管理し, terraform.tfvarsには記載しない
2. State管理: terraform.tfstateはgitignore対象としている。本ファイルのバックアップ等を別途実施することを想定している。

## トラブルシューティング

### State移行でエラーが出る場合

```bash
# 現在のstate確認
terraform state list

# 個別リソース移行
terraform state mv 'xenorchestra_vm.router' 'module.infrastructure_vms["router"].xenorchestra_vm.this'
```

### ネットワークが重複作成される場合

ネットワークモジュールはTerraformのステート管理により, 一度作成したネットワークは再利用されます。同名ネットワークが既にXCP-ngに存在する場合は, `terraform import`で取り込むことができます。

```bash
# 既存ネットワークをインポート
terraform import 'module.network["core_net"].xenorchestra_network.network' <network-id>
```

### Validationエラーが出る場合

```bash
terraform validate
# エラー内容を確認してterraform.tfvarsを修正
```

## 新規VM追加方法

作成するVMを追加するには以下の手順を実施する。

1. terraform.tfvarsにVM定義を追加する
2. Makefileにターゲット追加 ( オプション )
3. 適用確認

### 1. terraform.tfvarsにVM定義を追加する

VM種別に応じて, terraform.tfvars内の以下のオブジェクトにVM定義を追加する。

|オブジェクト名|VM種別|
|---|---|
|infrastructure_vms|Infrastructure VM(router, mgmt-server, rhel-server, ubuntu-server, devserver)|
|devlinux_vms|内部プライベートネットワークのみに接続された開発用VM|
|vmlinux_vms|pool-wide networkに接続のみに接続された開発用VM|
|k8s_vms|Kubernetes クラスタを構成するVM(extgw, frr*, k8sctrlplane*, k8sworker*)|

新規に作成するVMのパラメタを定義するobjectを以下の形式で記述する。

```hcl
変数名={
    template_type    = "<テンプレート種別>"
    firmware         = "<ファームウエア種別>"
    resource_profile = "<リソースプロファイル名>"
    networks = [
      { network_key = "<ネットワークのラベル名>", mac_address = "<MACアドレス>" },
    ]
  }
}
```

各項目には以下を記載する。

|項目名|記載内容|記載例|
|---|---|---|
|<テンプレート種別>|VM作成時に使用するテンプレート名。Xen Orchestraに登録されているテンプレート名を指定する。本Terraformファイルでは, Ubuntu VMの場合は, "ubuntu-vm", RHEL VMの場合は, "rhel-vm"を指定することを想定している。|"ubuntu-vm"または"rhel-vm"|
|<ファームウエア種別>|VM起動時に使用するファームウエアを指定する。UEFIの場合は, "uefi", BIOSを使用する場合は, "bios"を指定する。各OSのXen Orchestraの既存テンプレートでの指定に合わせて, "uefi", "bios"のいずれかを指定する。|"uefi", または, "bios"|
|<リソースプロファイル名>|locals.tf内の`vm_resource_defaults`変数内で, 定義されている各VM種別ごとのデフォルトプロファイル名(変数名)を指定する。|"infrastructure"など|

<リソースプロファイル名>には, 以下のいずれかを指定する。

|<リソースプロファイル名>|用途|
|---|---|
|"infrastructure"|Infrastructure VMのデフォルト値を指定する|
|devlinux|内部プライベートネットワークのみに接続された開発用VMのデフォルト値を指定する|
|vmlinux|pool-wide networkに接続のみに接続された開発用VMのデフォルト値を指定する|
|k8s_ctrlplane|K8sのコントロールプレイン用VMのデフォルト値を指定する|
|k8s_worker|K8sのワーカーノード用VMのデフォルト値を指定する|
|frr|K8sクラスタ単位に用意するFRR動作ホストのデフォルト値を指定する|
|extgw|K8sクラスタの疑似外部ネットワーク向けゲートウエイホストのデフォルト値を指定する|

実際に設定される値は, locals.tf内の`vm_resource_defaults`変数を参照。

### 2. Makefileにターゲット追加 ( 任意 )

```makefile
new_server: prepare
    ${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.infrastructure_vms["new_server"]' 2>&1 | tee $@.log

destroy-new_server: prepare
    ${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.infrastructure_vms["new_server"]' 2>&1 | tee $@.log
```

### 3. 適用確認

```bash
terraform plan
terraform apply
# または
make new_server
```

## 参考情報

- [Terraform XenOrchestra Provider](https://registry.terraform.io/providers/vatesfr/xenorchestra/latest/docs)
- [XCP-ng Documentation](https://xcp-ng.org/docs/)
- [Xen Orchestra Documentation](https://xen-orchestra.com/docs/)
