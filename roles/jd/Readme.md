# jd ロール

本ロールでは, JavaScript Object Notation (JSON) および Yet Another Markup Language (YAML) の差分比較とパッチ適用を行うコマンドラインツールである jd コマンドをソースコードから構築し, ローカルパッケージ(deb/rpm)として対象ホストへ導入する。

- [jd ロール](#jd-ロール)
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
| 制御ノード | - | Ansible 実行ホスト。localhostを意味する。 |
| 構築ホスト | - | パッケージ構築を実行するホスト。 `jd_build_host` で指定する。 |
| Debian package | deb | Debian/Ubuntu 系で使用するパッケージ形式。 |
| Red Hat Package Manager | RPM | RHEL/AlmaLinux 系で使用するパッケージ形式。 |
| JavaScript Object Notation | JSON | 人間が読みやすいテキスト形式のデータ交換フォーマット。 |
| Yet Another Markup Language | YAML | 構造化データを表現するためのテキスト形式。 |

## 動作仕様

- `jd_enabled` が `false` の場合, 本ロールは導入処理をスキップする。
- `jd_enabled` が `true` の場合, `jd_version` の値を使って導入処理を実行する。
- `jd_version` が指定されている場合, `vX.Y.Z` または `X.Y.Z` を受け付ける。
- `jd_completion_enabled` が `true` の場合, パッケージに bash/zsh 補完ファイルを同梱して導入する。
- 版数指定時は, `pkgbld-common` を使って以下を実施する。
  - 構築ホスト上のコンテナ内で jd ソースビルド
  - deb/rpm パッケージ生成
  - 制御ノード経由で対象ホストへ配布して導入
  - `jd --version` の結果が指定版数と一致することを検証

## 主要変数

| 変数名 | 意味 | 規定値 |
| --- | --- | --- |
| `jd_enabled` | jd ロール実行フラグ。`true` の場合に導入処理を実行する。 | `false` |
| `jd_version` | 導入する jd 版数。`vメジャー版数.マイナー版数.リビジョン` または `メジャー版数.マイナー版数.リビジョン` 形式。 | `"v2.5.0"` |
| `jd_completion_enabled` | bash/zsh 補完ファイル同梱有無。`true` の場合に補完を同梱する。 | `true` |
| `jd_build_host` | パッケージ構築ホスト。 | `"localhost"` |
| `jd_build_container_runtime` | コンテナランタイム。 | `"docker"` |
| `jd_build_container_network_mode` | コンテナネットワークモード。 | `"host"` |
| `jd_build_container_image_debian` | Debian向けビルド用コンテナイメージ。 | `"ubuntu:24.04"` |
| `jd_build_container_image_rhel` | RHEL向けビルド用コンテナイメージ。 | `"almalinux:9.6"` |
| `jd_pkg_build_timeout_seconds` | ビルド待機タイムアウト秒数。 | `3600` |
| `jd_pkg_build_loop_delay_seconds` | ビルド監視ポーリング間隔秒数。 | `5` |
| `jd_install_deb_lock_wait_seconds` | Debian系導入時のロック待機秒数。 | `600` |
| `jd_remove_existing_package` | 既存 jd パッケージ削除有無。 | `true` |

## 実行例

`vars/all-config.yml` などで `jd_enabled`, `jd_version` を指定して実行する。

```yaml
jd_enabled: true
jd_version: "v2.5.0"
```

jd ロールのみを実行する場合は, `Makefile` の `run_jd` ターゲットを利用する。

```bash
make run_jd
```

## 検証ポイント

以下を対象ホスト上で確認する。

- 導入されたjdの格納パスと版数
- 導入されたjdのパッケージ(jd-local)の導入状態
- シェル補完ファイルの格納先


### Debian/Ubuntu環境での確認方法

Debian/Ubuntu環境の場合, 以下のコマンドを実行する:

```bash
which jd
jd --version
dpkg -l | grep jd-local
ls -l /usr/share/bash-completion/completions/jd
ls -l /usr/share/zsh/vendor-completions/_jd
```

実行結果の例:
```bash
$ which jd
/usr/local/bin/jd
$ jd --version
jd version 2.5.0
$ dpkg -l | grep jd-local
ii  jd-local                              2.5.0-1                                 amd64        jd command line JSON/YAML diff and patch tool v2.5.0
$ ls -l /usr/share/bash-completion/completions/jd
-rw-r--r-- 1 root root 875  7月 31 19:43 /usr/share/bash-completion/completions/jd
$ ls -l /usr/share/zsh/vendor-completions/_jd
-rw-r--r-- 1 root root 831  7月 31 19:43 /usr/share/zsh/vendor-completions/_jd
```

### RHEL/AlmaLinux環境での確認方法

RHEL/AlmaLinux環境の場合, 以下のコマンドを実行する:

```bash
which jd
jd --version
rpm -qa | grep jd-local
ls -l /usr/share/bash-completion/completions/jd
ls -l /usr/share/zsh/site-functions/_jd
```

実行結果の例:
```bash
$ which jd
/usr/local/bin/jd
$ jd --version
jd version 2.5.0
$ rpm -qa | grep jd-local
jd-local-2.5.0-1.el9.x86_64
$ ls -l /usr/share/bash-completion/completions/jd
-rw-r--r--. 1 root root 875 Jul 31 19:44 /usr/share/bash-completion/completions/jd
$ ls -l /usr/share/zsh/site-functions/_jd
-rw-r--r--. 1 root root 831 Jul 31 19:44 /usr/share/zsh/site-functions/_jd
```

## 参考リンク

- [josephburnett/jd Githubサイト](https://github.com/josephburnett/jd)
