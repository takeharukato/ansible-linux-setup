# terraform ロール

このロールは HashiCorp 提供の公式リポジトリを登録し、`terraform` パッケージをインストールします。
Debian/Ubuntu 系では APT (deb822) を、RHEL 系では YUM/DNF リポジトリを設定し、GPG 公開鍵による検証を有効化します。

## 変数一覧

変数名|既定値|説明
---|---|---
`terraform_repository_url_debian`|`https://apt.releases.hashicorp.com`|Debian/Ubuntu 系で利用する HashiCorp APT リポジトリ URL。
`terraform_repository_url_rhel`|`https://rpm.releases.hashicorp.com`|RHEL 系で利用する HashiCorp RPM リポジトリ URL。
`terraform_apt_keyring_debian`|`/etc/apt/trusted.gpg.d/hashicorp.gpg`|Debian/Ubuntu 系で GPG 公開鍵を `gpg --dearmor` した keyring の配置先。

## ロール内の動作

`tasks/main.yml` から以下の順でタスクを実行します。

1. `tasks/load-params.yml` でディストリビューション差異吸収用の変数や、共通設定を読み込みます。
    - `../vars/cross-distro.yml` / `../vars/all-config.yml` / `../vars/k8s-api-address.yml` など
2. `tasks/package.yml` で HashiCorp リポジトリの登録と `terraform` のインストールを行います。
    - Debian/Ubuntu 系:
        - `gnupg` 等の前提パッケージをインストール
        - `{{ terraform_repository_url_debian }}/gpg` から公開鍵を取得し、`{{ terraform_apt_keyring_debian }}` に keyring を生成
        - `ansible.builtin.deb822_repository` で `signed_by: {{ terraform_apt_keyring_debian }}` を指定してリポジトリを登録
        - APT のキャッシュを更新
    - RHEL 系:
        - `ansible.builtin.yum_repository` で `{{ terraform_repository_url_rhel }}/RHEL/$releasever/$basearch/stable` を登録
    - その後、`terraform` パッケージをインストール

補足:

- `tasks/directory.yml` / `tasks/user_group.yml` / `tasks/service.yml` は現状空のため、Terraform それ自体のサービス化やユーザ作成は行いません。
- 変数は主に `../vars/cross-distro.yml` で定義されており、必要に応じて `group_vars` / `host_vars` で上書きできます。

## 検証ポイント

- `terraform version` が実行でき、期待したバージョンが表示される。
- Debian/Ubuntu 系では `/etc/apt/trusted.gpg.d/hashicorp.gpg` が存在し、権限が `0644` になっている。
- Debian/Ubuntu 系では `apt-cache policy terraform` で HashiCorp リポジトリ由来の候補が表示される。
- RHEL 系では `dnf repolist | grep -i hashicorp`（または `yum repolist`）でリポジトリが見える。
