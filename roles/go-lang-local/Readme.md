# go-lang-local ロール

本ロールは, 特定の版数のGo言語ソースを公式サイトからダウンロードし, Go 言語パッケージを構築, 導入するロールである。

- [go-lang-local ロール](#go-lang-local-ロール)
  - [用語](#用語)
  - [本ロールの動作仕様](#本ロールの動作仕様)
  - [主要変数](#主要変数)
  - [本ロールでの処理内容](#本ロールでの処理内容)
    - [パッケージ構築関連ファイル一覧](#パッケージ構築関連ファイル一覧)
    - [パッケージ構築～導入までの流れ](#パッケージ構築導入までの流れ)
    - [導入版数確認方針](#導入版数確認方針)
  - [注意事項](#注意事項)
  - [検証ポイント](#検証ポイント)
    - [OSディストリビューション標準のパッケージから導入した場合の確認方法](#osディストリビューション標準のパッケージから導入した場合の確認方法)
      - [Ubuntu24.04環境での実行例](#ubuntu2404環境での実行例)
      - [AlmaLinux9.6環境での実行例](#almalinux96環境での実行例)
    - [公式のソースからDebian/Ubuntu用パッケージ(debパッケージ)を構築して導入した場合の確認方法](#公式のソースからdebianubuntu用パッケージdebパッケージを構築して導入した場合の確認方法)
    - [公式のソースからRHEL/Alma Linux用パッケージ(RPMパッケージ)を構築して導入した場合の確認方法](#公式のソースからrhelalma-linux用パッケージrpmパッケージを構築して導入した場合の確認方法)

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
|制御ノード| - | Ansible 実行ホストや仮想マシン(VM)を指す。 localhostを意味する。|
|構築ホスト| - | 公式のソースを元にパッケージ構築処理を実施する際に使用するホスト。 本ロールの制御変数`go_build_host`で定義したホストを意味する。 |
| Go Programming Language | Go | Google が開発したプログラミング言語。 |
| End Of Life | EOL | サポート終了。公式APIから旧系列版数が返らない場合がある。 |
| Debian package | deb | Debian/Ubuntu 系で使用するパッケージ形式。 |
| Red Hat Package Manager | RPM | RHEL/AlmaLinux 系で使用するパッケージ形式。 |

## 本ロールの動作仕様

本ロールの役割, 動作仕様は以下の通り:

- `go_lang_version` が空文字または未定義: Go の追加導入は行わず, `go_command` を `go_command_package` に設定する。
- `go_lang_version` が指定されている場合: Go 公式 API から導入版数を解決し, `go_build_host` で指定した構築ホスト上のコンテナ内で指定版数の Go をソースビルドしてローカル成果物(deb/rpm)を対象ホストへ配布して導入する。
- 指定版数とビルド結果, さらに導入後の版数が一致しない場合は `fail` で停止する。
- `go_lang_version` が不正形式, または API から解決不能でフォールバックもない場合は, 警告を出してソース導入処理をスキップする。

## 主要変数

本ロールの動作パラメタとなる変数を以下に示す。

| 変数名 | 意味 | 規定値 |
| --- | --- | --- |
| `go_lang_version` | 導入する Go 版数。空/未定義時は Go の追加導入を行わず, 既存環境の `go` コマンドを利用する。指定時は `x.y` または `x.y.z` 形式を想定。 | `""` |
| `go_package_name` | OS 標準 Go パッケージ名。現行の本ロール実装では未使用で, 呼び出し元ロール側の導入処理で利用する。 | `"golang"` |
| `go_lang_remove_existing_package` | 公式のソースから作成したパッケージを導入する前に既存 Go パッケージを削除する指示。 `true`に設定した場合は, パッケージ導入前に既存 Go パッケージを削除する。| `true` |
| `go_build_host` | 公式のソースを元にパッケージ構築処理を実施する際に使用するホスト(構築ホスト)。 | `"localhost"` |
| `go_build_workspace` | 公式のソースから作成したパッケージを導入する際に使用する作業ディレクトリ。 | `"/tmp/go-build"` |
| `go_build_output_dir` | 成果物となるパッケージファイルの出力先ディレクトリ。 | `"{{ go_build_workspace }}/output"` |
| `go_pkg_build_timeout_seconds` | コンテナイメージ作成/パッケージ構築処理の最大待機時間(単位:秒)。 | `3600` |
| `go_pkg_build_loop_delay_seconds` | 非同期ジョブ監視時のポーリング間隔(単位:秒)。 | `5` |
| `go_install_deb_lock_wait_seconds` | Debian系で dpkg ロック解放を待機する時間(単位:秒)。 | `600` |
| `go_build_container_runtime` | 公式のソースを元にパッケージ構築処理を実施する際に使用するコンテナランタイム。 | `"docker"` |
| `go_build_container_network_mode` | コンテナ実行時のネットワークモード。 | `"host"` |
| `go_build_container_image_debian` | Debian/Ubuntu 向けパッケージ構築作業用コンテナイメージ名。 | `"go-build-ubuntu:24.04"` |
| `go_build_container_image_rhel` | RHEL/AlmaLinux 向けパッケージ構築作業用コンテナイメージ名。 | `"go-build-almalinux:9.6"` |

以下は `vars/cross-distro.yml` から読み込まれる主な関連変数である:

| 変数名 | 意味 | 規定値 |
| --- | --- | --- |
| `go_versions_api` | Go 公式版数 API エンドポイント。 | `"https://go.dev/dl/?mode=json&include=all"` |
| `go_base_url` | Go 公式ダウンロードベース URL。 | `"https://go.dev/dl"` |
| `go_install_dir` | 公式のソースを元にパッケージ構築処理を実施した場合のGo言語導入先ディレクトリのパス。 | `"/usr/local/go"` |
| `go_profile_script` | PATH 付与用の profile.d スクリプト導入先ファイルパス。 | `"/etc/profile.d/golang.sh"` |
| `go_deb_package_name` | ソース導入時の deb パッケージ名。 | `"go-lang"` |
| `go_rpm_package_name` | ソース導入時の rpm パッケージ名。 | `"go-lang"` |
| `go_command_package` | OS 標準パッケージ導入時の go コマンドパス。 | `"/usr/bin/go"` |
| `go_command_from_tarball_path` | 公式のソースを元にパッケージ構築処理を実施した場合の go コマンドパス。`/usr/local/bin/go` (シンボリックリンク)の実体となるコマンド。 | `"/usr/local/go/bin/go"` |
| `go_series_fallback_versions` | End of Life (EOL) 系列向けフォールバック版数マップ。 | `{ "1.25": "1.25.11" }` |

## 本ロールでの処理内容

本ロールでは, `go_lang_version` 指定の有無により以下の処理を行う:

- `go_lang_version` 未指定時: Go の追加導入は行わず, `go_command` を `go_command_package` に設定する。
- `go_lang_version` 指定時: Go 版数を API で解決し, コンテナ内でパッケージを構築後, 制御ノード経由で対象ホストに転送して導入する。

### パッケージ構築関連ファイル一覧

パッケージ構築処理, パッケージ導入処理に関連するファイルは以下の通り:

| ロール内での相対パス | 処理内容 |
| --- | --- |
| `tasks/main.yml` | エントリポイント。`load-params.yml`, `package.yml` を読み込む。|
| `tasks/load-params.yml` | OS別/共通変数(`vars/packages-*.yml`, `vars/cross-distro.yml`, `vars/all-config.yml`)を読み込む。 |
| `tasks/package.yml` | Go 導入メイン処理。`go_lang_version` 指定時はソースから構築したパッケージを導入し, 未指定時は `go_command` のみ設定する。 |
| `tasks/resolve-go-version.yml` | Go API 版数解決。`x.y` 系列解決, EOL フォールバック, 不正形式スキップ判定。 |
| `tasks/build-go-source-deb.yml` | Debian/Ubuntu 向け deb パッケージ構築処理。 |
| `tasks/build-go-source-rpm.yml` | RHEL/AlmaLinux 向け rpm パッケージ構築処理。 |
| `tasks/install-go-local-deb.yml` | 構築済み deb の回収, 転送, 導入, 導入版数確認。 |
| `tasks/install-go-local-rpm.yml` | 構築済み rpm の回収, 転送, 導入, 導入版数確認。 |
| `files/resolve_go_latest_patch.py` | API payload から `x.y` 系列の最新 `x.y.z` を抽出する Python スクリプト。 |
| `templates/build-go-deb.sh.j2` | コンテナ内で実行される deb 構築スクリプト。 |
| `templates/build-go-rpm.sh.j2` | コンテナ内で実行される rpm 構築スクリプト。 |
| `templates/Dockerfile.ubuntu.j2` | Debian/Ubuntu 向けパッケージ構築作業用コンテナ定義テンプレート。 |
| `templates/Dockerfile.almalinux.j2` | RHEL/AlmaLinux 向けパッケージ構築作業用コンテナ定義テンプレート。 |

### パッケージ構築～導入までの流れ

`go_lang_version` 指定時の流れは以下の通り:

1. Go 公式 API から版数情報を取得し, 指定形式に応じて導入版数を解決する。
2. 必要に応じて既存の Go パッケージを削除する。
3. ビルド用コンテナイメージを Dockerfile から作成する。
4. コンテナ内で Go パッケージ(deb/rpm)を構築する。
5. 成果物の存在確認と版数確認を行う。
6. 構築済みパッケージを構築ホストから制御ノードに回収する。
7. 制御ノードから対象ホストへコピーして導入する。
8. 導入後の `go version` で版数一致を確認する。

`go_lang_version` 未指定時は, 上記のソース導入処理を行わず, `go_command` を `go_command_package` に設定する。

### 導入版数確認方針

`go_lang_version` を指定した場合, 本ロールは以下を確認し, どれか 1 つでも不一致なら失敗で停止する:

1. 解決された版数が指定形式(`x.y` または `x.y.z`)の期待と一致すること。
2. 生成パッケージ(deb/rpm)の版数が解決版数と一致すること。
3. 導入後の `go version` から取得した版数が解決版数と一致すること。

## 注意事項

- ソースビルドは `go_build_host` で指定した構築ホスト上でコンテナランタイム(Docker)が利用可能であることを前提とする。
- 本ロールから構築したパッケージに対する署名付与は行わない。
- `go_lang_version` を指定する場合, 制御ノードから `go_versions_api` で指定したへGo 公式サイト (`https://go.dev/dl/`) へのネットワークアクセスが必須となる。
- `--check` 実行時は版数解決のみ行い, ビルド/導入はスキップする。

## 検証ポイント

- `go version` の出力版数が期待版数と一致すること。
- `go`コマンドの導入先が期待したパス名と一致すること。
  - `go_lang_version` 未指定時は, `/usr/bin/go` が利用可能であることを確認する。
  - 公式のソースからパッケージを構築して導入している場合は, `/usr/local/go/bin/go`に導入されていることを確認する。
- `dpkg -l` または `rpm -q` 中にGo言語パッケージが含まれ, かつ, 導入されている版数が期待版数と一致すること。
  - OSディストリビューション標準のパッケージから導入した場合は, パッケージ名に`golang`を指定して確認する。
  - 公式のソースからパッケージを構築して導入している場合は, パッケージ名に`go-lang`を指定して確認する。

### OSディストリビューション標準のパッケージから導入した場合の確認方法

`go_lang_version` を未指定で利用する場合は, 呼び出し元ロールで OSディストリビューション標準のパッケージから導入済みである前提となるため,
以下のコマンドを実行し, `go`コマンドの導入先, `go`コマンドの版数, 導入されている`golang` パッケージの版数を確認する。

```shell
which go
go version
dpkg -l | egrep golang  # Ubuntu
# または
rpm -qa | egrep golang   # RHEL
```

#### Ubuntu24.04環境での実行例

Ubuntu24.04環境での実行例を以下に示す:

```shell
$ which go
/usr/bin/go
$ go version
go version go1.22.2 linux/amd64
$ dpkg -l|egrep golang
ii  golang:amd64                                     2:1.22~2build1                                   amd64        Go programming language compiler - metapackage
ii  golang-1.22                                      1.22.2-2ubuntu0.4                                all          Go programming language compiler - metapackage
ii  golang-1.22-doc                                  1.22.2-2ubuntu0.4                                all          Go programming language - documentation
ii  golang-1.22-go                                   1.22.2-2ubuntu0.4                                amd64        Go programming language compiler, linker, compiled stdlib
ii  golang-1.22-src                                  1.22.2-2ubuntu0.4                                all          Go programming language - source files
ii  golang-doc                                       2:1.22~2build1                                   all          Go programming language - documentation
ii  golang-go:amd64                                  2:1.22~2build1                                   amd64        Go programming language compiler, linker, compiled stdlib
ii  golang-src                                       2:1.22~2build1                                   all          Go programming language - source files
```

#### AlmaLinux9.6環境での実行例

AlmaLinux9.6環境での実行例を以下に示す:

```shell
$ which go
/usr/bin/go
$ go version
go version go1.26.3 (Red Hat 1.26.3-1.el9_8) linux/amd64
$ rpm -qa|egrep golang
golang-src-1.26.3-1.el9_8.noarch
golang-bin-1.26.3-1.el9_8.x86_64
golang-race-1.26.3-1.el9_8.x86_64
golang-1.26.3-1.el9_8.x86_64
```

### 公式のソースからDebian/Ubuntu用パッケージ(debパッケージ)を構築して導入した場合の確認方法

公式のソースからdebパッケージを構築して導入している場合は,
以下のコマンドを実行し, `go`コマンドの導入先, `go`コマンドの版数, 導入されている`go-lang` パッケージの版数を確認する。

```shell
which go
/usr/local/go/bin/go version
dpkg -l|egrep go-lang
```

実行例を以下に示す:

```shell
$ which go
/usr/local/go/bin/go
$ /usr/local/go/bin/go version
go version go1.25.11 linux/amd64
$ dpkg -l|egrep go-lang
ii  go-lang                                          1.25.11-1                                  amd64        Go language toolchain 1.25.11
```

### 公式のソースからRHEL/Alma Linux用パッケージ(RPMパッケージ)を構築して導入した場合の確認方法

公式のソースからRPMパッケージを構築して導入している場合は,
以下のコマンドを実行し, `go`コマンドの導入先, `go`コマンドの版数, 導入されている`go-lang` パッケージの版数を確認する。

```shell
which go
/usr/local/go/bin/go version
rpm -qa|egrep go-lang
```

実行例を以下に示す:

```shell
$ which go
/usr/local/go/bin/go
$ /usr/local/go/bin/go version
go version go1.25.11 linux/amd64
$ rpm -qa|egrep go-lang
go-lang-1.25.11-1.el9.x86_64
```
