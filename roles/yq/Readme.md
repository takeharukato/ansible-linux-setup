# yq ロール

本ロールでは, Yet Another Markup Language (YAML), JavaScript Object Notation (JSON), Extensible Markup Language (XML)などを処理するためのコマンドラインツールである yq コマンドをソースコードから構築し, ローカルパッケージ(deb/rpm)として対象ホストへ導入する。

- [yq ロール](#yq-ロール)
  - [用語](#用語)
  - [動作仕様](#動作仕様)
  - [主要変数](#主要変数)
  - [実行例](#実行例)
  - [検証ポイント](#検証ポイント)
      - [Debian/Ubuntu環境での確認方法](#debianubuntu環境での確認方法)
      - [RHEL/AlmaLinux環境での確認方法](#rhelalmalinux環境での確認方法)
  - [参考リンク](#参考リンク)


## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| 制御ノード | - | Ansible 実行ホスト。 localhostを意味する。 |
| 構築ホスト | - | パッケージ構築を実行するホスト。 `yq_build_host` で指定する。 |
| Debian package | deb | Debian/Ubuntu 系で使用するパッケージ形式。 |
| Red Hat Package Manager | RPM | RHEL/AlmaLinux 系で使用するパッケージ形式。 |
| コンテナ ( Container ) | - | アプリケーションと依存関係を一つのパッケージ化したもの。軽量で, どの環境でも一貫して実行可能とするためのパッケージ形式。 |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウエア。 |
| Yet Another Markup Language | YAML | Kubernetesなどで用いられる設定ファイル形式。 |
| JavaScript Object Notation | JSON | 人間が読みやすいテキスト形式のデータ交換フォーマット。キーと値のペアで構成され, 設定ファイルやAPI レスポンスに広く使用される。 |
| Extensible Markup Language | XML | 構造を持ったデータを記述するための拡張可能なマークアップ言語のこと。 |

## 動作仕様

- `yq_enabled` が `false` の場合, 本ロールは導入処理をスキップする。
- `yq_enabled` が `true` の場合, `yq_version` の値を使って導入処理を実行する。
- `yq_version` が指定されている場合, `vX.Y.Z` または `X.Y.Z` を受け付ける。
- `yq_completion_enabled` が `true` の場合, パッケージに bash/zsh 補完ファイルを同梱して導入する。
- 版数指定時は, `pkgbld-common` を使って以下を実施する。
	- 構築ホスト上のコンテナ内で yq ソースビルド
	- deb/rpm パッケージ生成
	- 制御ノード経由で対象ホストへ配布して導入
	- `yq --version` の結果が指定版数と一致することを検証

## 主要変数

| 変数名 | 意味 | 規定値 |
| --- | --- | --- |
| `yq_enabled` | yq ロール実行フラグ。`true` の場合に導入処理を実行する。 | `false` |
| `yq_version` | 導入する yq 版数。 `vメジャー版数.マイナー版数.リビジョン` または `メジャー版数.マイナー版数.リビジョン` 形式。 | `"v4.47.1"` |
| `yq_completion_enabled` | bash/zsh 補完ファイル同梱有無。`true` の場合に補完を同梱する。 | `true` |
| `yq_build_host` | パッケージ構築ホスト。 | `"localhost"` |
| `yq_build_container_runtime` | コンテナランタイム。 | `"docker"` |
| `yq_build_container_network_mode` | コンテナネットワークモード。 | `"host"` |
| `yq_build_container_image_debian` | Debian向けビルド用コンテナイメージ。 | `"ubuntu:24.04"` |
| `yq_build_container_image_rhel` | RHEL向けビルド用コンテナイメージ。 | `"almalinux:9.6"` |
| `yq_pkg_build_timeout_seconds` | ビルド待機タイムアウト秒数。 | `3600` |
| `yq_pkg_build_loop_delay_seconds` | ビルド監視ポーリング間隔秒数。 | `5` |
| `yq_install_deb_lock_wait_seconds` | Debian系導入時のロック待機秒数。 | `600` |
| `yq_remove_existing_package` | 既存 yq パッケージ削除有無。 | `true` |
| `yq_bash_completion_path` | bash 補完配置先。Debian/RHEL 共通。 | `"/usr/share/bash-completion/completions/yq"` |
| `yq_zsh_completion_path` | zsh 補完配置先。Debian は vendor-completions, RHEL は site-functions。 | Debian: `"/usr/share/zsh/vendor-completions/_yq"`, RHEL: `"/usr/share/zsh/site-functions/_yq"` |

## 実行例

`vars/all-config.yml` などで `yq_enabled`, `yq_version` を指定して実行する。

```yaml
yq_enabled: true
yq_version: "v4.47.1"
```

yq ロールのみを実行する場合は, `Makefile` の `run_yq` ターゲットを利用する。

```bash
make run_yq
```

## 検証ポイント

以下の点を確認する:

- 導入されたyqの格納パスと版数
- 導入されたyqのパッケージ(yq-local)の導入状態
- シェル補完ファイルの格納先

#### Debian/Ubuntu環境での確認方法

Debian/Ubuntu環境の場合, 以下のコマンドを実行する:

```bash
which yq
yq --version
dpkg -l | grep yq-local
ls -l /usr/share/bash-completion/completions/yq
ls -l /usr/share/zsh/vendor-completions/_yq
```

Debian/Ubuntu環境での実行例:
```bash
$ which yq
/usr/local/bin/yq
$ yq --version
yq (https://github.com/mikefarah/yq/) version v4.47.1
$ dpkg -l | grep yq-local
ii  yq-local                              4.47.1-1                                amd64        yq command line YAML processor v4.47.1
$ ls -l /usr/share/bash-completion/completions/yq
-rw-r--r-- 1 root root 15913  7月 31 12:08 /usr/share/bash-completion/completions/yq
$ ls -l /usr/share/zsh/vendor-completions/_yq
-rw-r--r-- 1 root root 7604  7月 31 12:08 /usr/share/zsh/vendor-completions/_yq
```

#### RHEL/AlmaLinux環境での確認方法

RHEL/AlmaLinux環境の場合, 以下のコマンドを実行する:

```bash
which yq
yq --version
rpm -qa | grep yq-local
ls -l /usr/share/bash-completion/completions/yq
ls -l /usr/share/zsh/site-functions/_yq
```

RHEL/AlmaLinux環境での実行例:
```bash
$ which yq
/usr/local/bin/yq
$ yq --version
yq (https://github.com/mikefarah/yq/) version v4.47.1
$ rpm -qa | grep yq-local
yq-local-4.47.1-1.el9.x86_64
$ ls -l /usr/share/bash-completion/completions/yq
-rw-r--r--. 1 root root 15913 Jul 31 12:09 /usr/share/bash-completion/completions/yq
$ ls -l /usr/share/zsh/site-functions/_yq
-rw-r--r--. 1 root root 7604 Jul 31 14:23 /usr/share/zsh/site-functions/_yq
```

## 参考リンク

- [mikefarah/yq Githubサイト](https://github.com/mikefarah/yq)
