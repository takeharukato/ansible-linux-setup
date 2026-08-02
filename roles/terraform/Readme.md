# terraform ロール

本ロールは HashiCorp 提供の公式リポジトリを登録し, `terraform` パッケージをインストールします。

## 目次

- [terraform ロール](#terraform-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [1. ロール実行結果の確認](#1-ロール実行結果の確認)
    - [2. terraform コマンドの動作確認](#2-terraform-コマンドの動作確認)
    - [3. GPG keyring の確認 (Debian/Ubuntu 系のみ)](#3-gpg-keyring-の確認-debianubuntu-系のみ)
    - [4. リポジトリ設定の確認 (Debian/Ubuntu 系)](#4-リポジトリ設定の確認-debianubuntu-系)
    - [5. リポジトリ設定の確認 (RHEL 系)](#5-リポジトリ設定の確認-rhel-系)
    - [6. パッケージ情報の確認](#6-パッケージ情報の確認)
  - [トラブルシューティング](#トラブルシューティング)
  - [注意事項](#注意事項)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)


## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| ユーザ | - | 機能を利用する人, 又は識別された利用主体。 |
| ツール | - | 特定作業を実行するための機能や道具。 |
| リソース | - | 処理に必要な計算機資源やデータ。 |
| クラスタ | - | 複数の機器を連携させて一体運用する構成。 |
| ディストリビューション | - | 基本ソフトウェアと関連部品をまとめた配布形態。 |
| コンテナイメージ | - | コンテナ実行に必要な内容をまとめた保存形式。 |
| プログラム | - | 計算機に処理をさせるための命令列。 |
| コミュニティ | - | 共通目的のもとで継続的に活動する利用者集団。 |
| プラグイン | - | 既存機能へ追加機能を組み込むための拡張部品。 |
| サービスアカウント | - | 自動処理向けに用意する利用主体の識別情報。 |
| コンテナランタイム | - | コンテナを起動, 停止, 管理する実行基盤。 |
| リクエスト | - | 処理実行や情報取得を要求する操作。 |
| コントローラ | - | 対象状態を監視し, 期待状態へ調整する制御機能。 |
| メタデータ | - | 対象データの属性や説明を示す付加情報。 |
| バックエンド | - | 利用者画面の背後で処理を実行する側。 |
| ストレージ | - | データを保存する仕組み。 |
| インストール | - | ソフトウェアを導入して利用可能にする作業。 |
| マシン | - | 処理を実行する計算機。 |
| プロビジョニング | - | 利用開始に必要な設定や資源を準備する作業。 |
| ルーティング | - | 宛先までの経路を選択して転送する処理。 |
| オブジェクト | - | ひとかたまりとして扱うデータ単位。 |
| エージェント | - | 指示に従って処理を代行する構成要素。 |
| ストア | - | データや成果物を保存する場所。 |
| ジャーナル | - | 時系列の記録を保持する仕組み。 |
| アカウント | - | 利用者や処理主体を識別する登録情報。 |
| エンドポイント | - | 通信の接続先を表す識別点。 |
| パターン | - | 繰り返し現れる構造や記述形式。 |
| パケット | - | ネットワークで転送するデータ単位。 |
| カーネル | - | 基本ソフトウェアの中核機能。 |
| シェル | - | コマンド入力で計算機を操作する仕組み。 |
| Playbook | - | 自動化処理の実行手順を記述したファイル。 |
| Canonical | - | Ubuntu を提供する組織名。 |
| Key-Value | - | キーと値の組で情報を表す方式。 |
| IP | - | インターネットプロトコルの略称。 |
| SQL | - | データベースを操作するための記述言語。 |
| HTTP | - | WWW で情報をやり取りする通信手順。 |
| HTTPS | - | 通信内容を暗号化して WWW 通信を行う方式。 |
| RPM | - | RHEL 系で使用するパッケージ形式。 |
| VM | - | 物理機器上で動作する仮想的な計算機。 |
| localhost | - | 同一機器自身を指す名前。 |
| root | - | Unix 系システムの最上位権限を持つ管理者識別子。 |
| ソフトウェア | - | 情報処理システムで使用するプログラム, 手順, 規則及び関連文書の全体又は一部分。 |
| システム | - | 複数の要素が連携して目的を実現する仕組み全体。 |
| アプリケーション | - | 利用者の目的を実現するために動作するソフトウェア。 |
| パッケージ | - | ソフトウェア導入に必要なファイルをまとめた配布単位。 |
| リポジトリ | - | ソフトウェアや設定情報を保管し, 取得できるようにした管理場所。 |
| コマンド | - | 実行者が計算機へ処理を指示するための命令。 |
| ホスト | - | 管理対象として識別される個別の計算機。 |
| サーバ | - | 他の機器や利用者へ機能やデータを提供する計算機, 又はその役割。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
| ネットワーク | - | 機器同士を接続してデータをやり取りする仕組み。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
| プロトコル | - | 通信やデータ交換の手順を定めた取り決め。 |
| ディレクトリ | - | ファイルを階層的に整理するための入れ物。 |
| ログ | - | 処理の結果や状態を時系列で記録した情報。 |
| コード | - | 処理内容を記述した文字列。 |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウェア。 |
| Pod | - | Kubernetes でコンテナをまとめて管理する最小単位。 |
| Linux | - | 多くの機器で使われる, 基本ソフトウェアの系統。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| API | - | アプリケーション同士がやり取りする方法を定めた仕様。 |
| URL | - | WWW 上の資源の場所を示す文字列。 |
| Advanced Package Tool | APT | Debian 系のパッケージ管理ツール |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| curl | - | URL を指定してデータ送受信を行うコマンド。 |
| Dandified YUM | DNF | YUM の後継として利用するパッケージ管理ツール。 |
| Deb822 | - | Debian系のパッケージ管理情報を構造化された形式で記述するための記述形式。 |
| Debian | - | コミュニティ主導で開発される Linux ディストリビューション。 |
| `dpkg` | - | Debian パッケージの情報参照や導入確認を行うコマンド。 |
| GNU Privacy Guard | GPG | 公開鍵暗号方式でデータを保護するためのソフトウェア。 |
| gnupg | - | GNU Privacy Guardのパッケージ実装, 公開鍵暗号によるデータの署名と暗号化を提供 |
| HashiCorp | - | Terraform, Vault, Consulなどのインフラ管理ツールを提供する企業 |
| Infrastructure as Code | IaC | インフラ構成をコードで定義・管理する手法, 再現性と保守性を向上 |
| keyring | - | GPG公開鍵の保管形式。複数の公開鍵をまとめて管理し, パッケージ署名の検証に使用 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Red Hat Enterprise Linux | RHEL | Red Hat 社が提供する商用 Linux ディストリビューション。 |
| RPM Package Manager | RPM | RHEL/AlmaLinux 系で使用するパッケージ形式。 |
| Secure Shell | SSH | 遠隔の計算機へ安全に接続して操作する方式。 |
| software-properties-common | - | APTリポジトリ管理用のユーティリティパッケージ。add-apt-repositoryコマンドなどを提供し, サードパーティリポジトリの追加を支援 |
| Superuser Do | - | 別のユーザ (通常は root) の権限で指定されたコマンドを実行することを可能にする Unix 系システムのプログラム。管理者以外のユーザが管理作業を行うときに使用される |
| Terraform | - | HashiCorp提供のインフラストラクチャをコードで管理するIaCツール |
| Ubuntu | - | Canonical が提供する Debian 系の Linux ディストリビューション。 |
| Yellowdog Updater Modified | YUM | RPM パッケージの導入, 更新, 削除を行う管理ツール。 |
| Red Hat Enterprise Linux 9 | RHEL9 | Red Hat Enterprise Linux の第9系統版。 |
| Uniform Resource Locator | URL | URL の正式名称。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `dnf` | - | RHEL 系でパッケージを導入, 更新, 削除するコマンド。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| `make` | - | Makefile に定義された処理を実行するコマンド。 |
| rpmコマンド | - | RPM パッケージの情報参照や導入確認を行うコマンド。 |
| サービス | - | 機能を利用者や他システムへ提供する仕組み。 |
| リモートホスト | - | ネットワーク越しに接続して操作する別ホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |

## 概要

このロールは HashiCorp 提供の公式リポジトリを登録し, `terraform` パッケージをインストールします。Debian/Ubuntu 系では APT リポジトリを, RHEL 系では YUM/DNF リポジトリを設定し, GPG 公開鍵による署名検証を有効化します。Ansible 2.15 以降では Deb822 の設定に対応します。

## 前提条件

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- Ansible 2.15 以降 (推奨。2.15 未満でも動作しますが, Debian 系で Deb822 の代わりに apt_repository 形式を使用します)
- リモートホストへの SSH 接続が確立されていること
- 管理者権限 (sudo) が利用可能であること
- インターネット接続 (HashiCorp公式リポジトリへのアクセスが必要)
- Debian/Ubuntu 系の場合: curl, gnupg が利用可能であること (ロール内で自動インストール)

## 実行方法

terraform ロールのみ実行する場合:
```bash
make run_terraform
```

または,

```bash
ansible-playbook -i inventory/hosts site.yml -t terraform
```

特定ホストのみ対象として実行する場合:
```bash
ansible-playbook -i inventory/hosts site.yml -l ubuntu-server.local -t terraform
```

## 主要変数

以下の変数は `vars/cross-distro.yml` で定義されており, 必要に応じて `vars/all-config.yml`や`host_vars` で上書きできます。

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `terraform_repository_url_debian` | `https://apt.releases.hashicorp.com` | Debian/Ubuntu 系で利用する HashiCorp APT リポジトリ URL。 |
| `terraform_repository_url_rhel` | `https://rpm.releases.hashicorp.com` | RHEL 系で利用する HashiCorp RPM リポジトリ URL。 |
| `terraform_apt_keyring_debian` | `/etc/apt/trusted.gpg.d/hashicorp.gpg` | Debian/Ubuntu 系で GPG 公開鍵を `gpg --dearmor` した keyring の配置先。 |

## 実行フロー

本ロールは以下の順序で処理を実行します:

1. **パラメータ読み込み** (`load-params.yml`): OS 別パッケージ定義 (`vars/packages-ubuntu.yml`, `vars/packages-rhel.yml`) とクラスタ共通変数 (`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`) を読み込みます。

2. **パッケージ管理** (Ansible バージョンに基づいて分岐):
     - **Ansible >= 2.15** の場合 (`package.yml`):
         - **Debian/Ubuntu 系**:
             1. `gnupg`, `software-properties-common` パッケージをインストール
             2. apt cache を更新
             3. `curl` で HashiCorp GPG 公開鍵を取得し, `gpg --dearmor` で keyring 形式に変換して `{{ terraform_apt_keyring_debian }}` (既定: `/etc/apt/trusted.gpg.d/hashicorp.gpg`) に配置
             4. `ansible.builtin.deb822_repository` モジュールで HashiCorp APT リポジトリを Deb822 で登録 (`signed-by: {{ terraform_apt_keyring_debian }}` を指定)
             5. apt cache を更新
         - **RHEL 系**:
             1. `ansible.builtin.yum_repository` モジュールで HashiCorp YUM リポジトリを登録 (`{{ terraform_repository_url_rhel }}/RHEL/$releasever/$basearch/stable`)
         - **共通**:
             - `terraform` パッケージをインストール
     - **Ansible < 2.15** の場合 (`package-on-rhel9.yml`):
         - Debian/Ubuntu 系では `ansible.builtin.apt_repository` モジュールを使用 (Deb822 の代わりに従来の sources.list 形式)
         - その他の処理は `package.yml` と同様

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
```

期待する出力例:

```text
Hashicorp       HashiCorp Stable - x86_64
```

検証ポイント:

- HashiCorp リポジトリが有効になっていることを確認します。

### 6. パッケージ情報の確認

確認コマンド:

Debian/Ubuntu 系の場合:
```bash
dpkg -l terraform
```

RHEL 系の場合:
```bash
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

## トラブルシューティング

代表的なトラブルと対処を以下に示します。

| 想定トラブル | 主な原因 | 対処方法 |
| --- | --- | --- |
| ロール実行後も `terraform` が導入されない | `terraform_enabled` が `false` のままで, `package.yml` または `package-on-rhel9.yml` がスキップされている | 実行者は `vars/all-config.yml` または `host_vars` で `terraform_enabled: true` を設定し, Ansible 出力で package 系タスクが `skipping` になっていないことを確認して再実行します。 |
| Debian/Ubuntu 系で `Add HashiCorp GPG key` が失敗する | `curl` での鍵取得失敗, `gpg --dearmor` 実行失敗, リポジトリ URL 到達不可 | 実行者は対象ホストで `curl -fsSL https://apt.releases.hashicorp.com/gpg` を単体実行し, ネットワーク到達性とプロキシ設定を確認します。社内ミラーを利用する場合は `terraform_repository_url_debian` を到達可能な URL に上書きして再実行します。 |
| Debian/Ubuntu 系で `apt-cache policy terraform` に HashiCorp リポジトリが出ない | Ansible 版数に応じたリポジトリ形式差異, suite 不一致, Deb822/APT repository 登録失敗 | 実行者は `ansible --version` を確認し, 2.15 以上では Deb822, 2.15 未満では `apt_repository` 形式になることを前提に `/etc/apt/sources.list.d/` 配下の HashiCorp 定義を確認します。`ansible_distribution_release` に対応する suite が正しいことも確認します。 |
| RHEL 系で `terraform` パッケージが見つからない | HashiCorp YUM リポジトリ未登録, `https://rpm.releases.hashicorp.com` への到達不可, `$releasever` / `$basearch` 差異 | 実行者は `dnf repolist | grep -i hashicorp` と `dnf info terraform` を確認します。社内ミラー使用時は `terraform_repository_url_rhel` を上書きし, RHEL9 系であることを確認して再実行します。 |
| keyring ファイルが存在するのに `apt update` で署名検証に失敗する | `/etc/apt/trusted.gpg.d/hashicorp.gpg` が壊れている, 古い鍵が残っている, 鍵取得途中で失敗した | 実行者は `/etc/apt/trusted.gpg.d/hashicorp.gpg` を退避または削除し, ロールを再実行して鍵を再生成します。その後 `apt update` と `apt-cache policy terraform` を再確認します。 |
| `terraform version` は通るが期待版数にならない | HashiCorp リポジトリから最新安定版を導入する実装であり, 版数固定機能がない | 実行者は本ロールが特定版数固定に未対応であることを確認します。特定版数が必要な場合は, リポジトリ側の提供版数を制御するか, 別途パッケージ固定手順を追加してください。 |

## 注意事項

- **Ansible バージョンによる動作の違い**: Ansible 2.15 未満の環境では `package-on-rhel9.yml` が使用され, Debian/Ubuntu 系で `ansible.builtin.apt_repository` モジュール (従来の sources.list 形式) によりリポジトリが登録されます。Ansible 2.15 以降では `ansible.builtin.deb822_repository` モジュール (Deb822 形式) が使用されます。
- **空実装タスク**: `directory.yml`, `user_group.yml`, `service.yml`, `config.yml` は現在空実装で, 将来の機能拡張に備えて用意されています。これらのタスクファイルでは Terraform 自体のサービス化やユーザ作成は行いません。
- **パッケージバージョン**: HashiCorp リポジトリから最新の安定版がインストールされます。特定バージョンに固定する機能は現在未実装です。
- **変数の上書き**: `vars/cross-distro.yml` で定義されている変数は, `group_vars/all/all.yml` や `host_vars` で上書きできます。例えば, 社内ミラーリポジトリを使用する場合は `terraform_repository_url_debian` / `terraform_repository_url_rhel` を上書きしてください。

## 参考資料

### 公式ドキュメント

- [Terraform](https://developer.hashicorp.com/terraform/docs)
