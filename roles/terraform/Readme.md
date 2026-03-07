# terraform ロール

## 概要

このロールは HashiCorp 提供の公式リポジトリを登録し, `terraform` パッケージをインストールします。Debian/Ubuntu 系では APT リポジトリを, RHEL 系では YUM/DNF リポジトリを設定し, GPG 公開鍵による署名検証を有効化します。Ansible 2.15 以降では deb822 形式のリポジトリ設定に対応します。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Advanced Package Tool | APT | Debian 系のパッケージ管理ツール |
| Ansible | - | インフラストラクチャの構成管理と自動化を行うオープンソースツール。YAML 形式のプレイブックでシステム構成を記述し, SSH を使用して複数のリモートホストに対して冪等な変更を実行できる |
| curl | - | コマンドラインHTTPクライアント, URLでデータ転送をサポート |
| Dandified YUM | DNF | YUMの後継として開発されたパッケージ管理ツール, RHEL 8以降で標準 |
| deb822 | - | Debian系リポジトリ設定の新形式。構造化されたフィールド形式でリポジトリ情報を記述し, 従来の sources.list 形式よりも管理性が向上 |
| Debian | - | コミュニティ主導で開発されるLinuxディストリビューション |
| Debian Package Manager | dpkg | Debianパッケージの低レベル管理ツール, パッケージのインストール・削除・情報表示を行う |
| GNU Privacy Guard | GPG | 電子署名と暗号化を行うオープンソース暗号化ソフトウェア |
| gnupg | - | GNU Privacy Guardのパッケージ実装, 公開鍵暗号によるデータの署名と暗号化を提供 |
| HashiCorp | - | Terraform, Vault, Consulなどのインフラ管理ツールを提供する企業 |
| Infrastructure as Code | IaC | インフラ構成をコードで定義・管理する手法, 再現性と保守性を向上 |
| keyring | - | GPG公開鍵の保管形式。複数の公開鍵をまとめて管理し, パッケージ署名の検証に使用 |
| Operating System | OS | 基本ソフトウエア |
| Red Hat Enterprise Linux | RHEL | Red Hat 社が提供する Linux ディストリビューション。RHEL9 はそのメジャーバージョン 9 を指す |
| Red Hat Package Manager | RPM | RHEL系Linuxのパッケージ管理システム, パッケージのインストール・削除・検証を行う |
| Secure Shell | SSH | リモートコンピュータへの安全なログインと通信を可能にするプロトコル。ネットワーク接続を暗号化することで, ユーザ認証と通信内容の機密性を確保する |
| software-properties-common | - | APTリポジトリ管理用のユーティリティパッケージ。add-apt-repositoryコマンドなどを提供し, サードパーティリポジトリの追加を支援 |
| sudo | - | 別のユーザ (通常は root) の権限で指定されたコマンドを実行することを可能にする Unix 系システムのプログラム。管理者以外のユーザが管理作業を行うときに使用される |
| Terraform | - | HashiCorp提供のインフラストラクチャをコードで管理するIaCツール |
| Ubuntu | - | Canonicalが提供するDebianベースのLinuxディストリビューション |
| Yellowdog Updater Modified | YUM | RPMベースのパッケージ管理ツール, RHEL 7まで標準 |

## 前提条件

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- Ansible 2.15 以降 (推奨。2.15 未満でも動作しますが, Debian 系でdeb822形式の代わりにapt_repository形式を使用します)
- リモートホストへの SSH 接続が確立されていること
- 管理者権限 (sudo) が利用可能であること
- インターネット接続 (HashiCorp公式リポジトリへのアクセスが必要)
- Debian/Ubuntu 系の場合: curl, gnupg が利用可能であること (ロール内で自動インストール)

## 実行フロー

本ロールは以下の順序で処理を実行します:

1. **パラメータ読み込み** (`load-params.yml`): OS 別パッケージ定義 (`vars/packages-ubuntu.yml`, `vars/packages-rhel.yml`) とクラスタ共通変数 (`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込みます。

2. **パッケージ管理** (Ansible バージョンに基づいて分岐):
     - **Ansible >= 2.15** の場合 (`package.yml`):
         - **Debian/Ubuntu 系**:
             1. `gnupg`, `software-properties-common` パッケージをインストール
             2. apt cache を更新
             3. `curl` で HashiCorp GPG 公開鍵を取得し, `gpg --dearmor` で keyring 形式に変換して `{{ terraform_apt_keyring_debian }}` (既定: `/etc/apt/trusted.gpg.d/hashicorp.gpg`) に配置
             4. `ansible.builtin.deb822_repository` モジュールで HashiCorp APT リポジトリを deb822 形式で登録 (`signed-by: {{ terraform_apt_keyring_debian }}` を指定)
             5. apt cache を更新
         - **RHEL 系**:
             1. `ansible.builtin.yum_repository` モジュールで HashiCorp YUM リポジトリを登録 (`{{ terraform_repository_url_rhel }}/RHEL/$releasever/$basearch/stable`)
         - **共通**:
             - `terraform` パッケージをインストール
     - **Ansible < 2.15** の場合 (`package-on-rhel9.yml`):
         - Debian/Ubuntu 系では `ansible.builtin.apt_repository` モジュールを使用 (deb822 形式の代わりに従来の sources.list 形式)
         - その他の処理は `package.yml` と同様

3. **ディレクトリ操作** (`directory.yml`): 現在は空実装 (将来の拡張に予約)。

4. **ユーザ・グループ管理** (`user_group.yml`): 現在は空実装 (将来の拡張に予約)。

5. **サービス管理** (`service.yml`): 現在は空実装 (将来の拡張に予約)。

6. **設定管理** (`config.yml`): 現在は空実装 (将来の拡張に予約)。

## 主要変数

以下の変数は `vars/cross-distro.yml` で定義されており, 必要に応じて `group_vars` / `host_vars` で上書きできます。

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `terraform_repository_url_debian` | `https://apt.releases.hashicorp.com` | Debian/Ubuntu 系で利用する HashiCorp APT リポジトリ URL。 |
| `terraform_repository_url_rhel` | `https://rpm.releases.hashicorp.com` | RHEL 系で利用する HashiCorp RPM リポジトリ URL。 |
| `terraform_apt_keyring_debian` | `/etc/apt/trusted.gpg.d/hashicorp.gpg` | Debian/Ubuntu 系で GPG 公開鍵を `gpg --dearmor` した keyring の配置先。 |

## 実行方法

```bash
make run_terraform
```

または,

```bash
# terraform ロールのみ実行
ansible-playbook -i inventory/hosts site.yml -t terraform

# 特定ホストのみ対象
ansible-playbook -i inventory/hosts site.yml -l ubuntu-server.local -t terraform
```

## 検証ポイント

### 1. ロール実行結果の確認

確認コマンド:

```bash
ansible-playbook -i inventory/hosts site.yml --tags terraform
```

期待する出力例:

```text
PLAY RECAP *********************************************************************
ubuntu-server.local        : ok=10   changed=5    unreachable=0    failed=0    skipped=2   rescued=0    ignored=0
```

検証ポイント:

- `PLAY RECAP` で `failed=0` かつ `unreachable=0` であることを確認します。

### 2. terraform コマンドの動作確認

確認コマンド:

```bash
terraform version
```

期待する出力例:

```text
Terraform v1.9.8
on linux_amd64
```

検証ポイント:

- `terraform` コマンドが正常に実行でき, バージョン情報が表示されることを確認します。

### 3. GPG keyring の確認 (Debian/Ubuntu 系のみ)

確認コマンド:

```bash
ls -l /etc/apt/trusted.gpg.d/hashicorp.gpg
stat -c "%a %U:%G" /etc/apt/trusted.gpg.d/hashicorp.gpg
```

期待する出力例:

```text
-rw-r--r-- 1 root root 3980 Mar  7 10:30 /etc/apt/trusted.gpg.d/hashicorp.gpg
644 root:root
```

検証ポイント:

- keyring ファイルが存在し, パーミッションが `644`, 所有者が `root:root` であることを確認します。

### 4. リポジトリ設定の確認 (Debian/Ubuntu 系)

確認コマンド:

```bash
apt-cache policy terraform
```

期待する出力例:

```text
terraform:
    Installed: 1.9.8-1
    Candidate: 1.9.8-1
    Version table:
 *** 1.9.8-1 500
                500 https://apt.releases.hashicorp.com noble/main amd64 Packages
                100 /var/lib/dpkg/status
```

検証ポイント:

- HashiCorp リポジトリ (`https://apt.releases.hashicorp.com`) がソースとして表示されることを確認します。

### 5. リポジトリ設定の確認 (RHEL 系)

確認コマンド:

```bash
dnf repolist | grep -i hashicorp
# または
yum repolist | grep -i hashicorp
```

期待する出力例:

```text
Hashicorp       HashiCorp Stable - x86_64
```

検証ポイント:

- HashiCorp リポジトリが有効になっていることを確認します。

### 6. パッケージ情報の確認

確認コマンド:

```bash
# Debian/Ubuntu 系
dpkg -l terraform

# RHEL 系
rpm -q terraform
```

期待する出力例 (Debian/Ubuntu 系):

```text
ii  terraform  1.9.8-1  amd64  Terraform
```

期待する出力例 (RHEL 系):

```text
terraform-1.9.8-1.x86_64
```

検証ポイント:

- `terraform` パッケージがインストールされていることを確認します。

## 補足

- **Ansible バージョンによる動作の違い**: Ansible 2.15 未満の環境では `package-on-rhel9.yml` が使用され, Debian/Ubuntu 系で `ansible.builtin.apt_repository` モジュール (従来の sources.list 形式) によりリポジトリが登録されます。Ansible 2.15 以降では `ansible.builtin.deb822_repository` モジュール (deb822 形式) が使用されます。
- **空実装タスク**: `directory.yml`, `user_group.yml`, `service.yml`, `config.yml` は現在空実装で, 将来の機能拡張に備えて用意されています。これらのタスクファイルでは Terraform 自体のサービス化やユーザ作成は行いません。
- **パッケージバージョン**: HashiCorp リポジトリから最新の安定版がインストールされます。特定バージョンに固定する機能は現在未実装です。
- **変数の上書き**: `vars/cross-distro.yml` で定義されている変数は, `group_vars/all/all.yml` や `host_vars` で上書きできます。例えば, 社内ミラーリポジトリを使用する場合は `terraform_repository_url_debian` / `terraform_repository_url_rhel` を上書きしてください。
