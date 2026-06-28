# go-k8s-client-local ロール

本ロールは, Go 言語版 Kubernetes client (client-go) を対象ノード上で直接 `go get` せずに, 構築ホスト上のコンテナでローカルパッケージ (deb/rpm) を生成して配布, 導入するロールである。

## 概要

- 入力として `go_k8s_client_version` (例: `v0.31.0`) を受け取り, オフライン開発キット (`go.mod`, `go.sum`, `vendor/`) を含むローカルパッケージを作成する。
- ローカルパッケージの転送経路は, 構築ホスト -> 制御ノード -> 対象ホストである。
- 導入後に, `go.mod` 内の `k8s.io/client-go` 版数を検証する。

## 前提条件

- 対象 OS: Debian/Ubuntu系, RHEL系。
- 構築ホストでコンテナランタイム (`docker` など) が利用可能であること。
- 対象ホスト側では Go 言語パッケージ (`golang`/`golang-go`/`go-lang`) が導入済みであること。
- `go_k8s_client_version` は `vX.Y.Z` 形式で指定すること。

## 実行フロー

1. `load-params.yml` で OS別/共通変数を読み込む。
2. `package.yml` で版数形式を検証する。
3. Debian系では `build-client-go-source-deb.yml` でコンテナ内ビルドを行い, `install-client-go-local-deb.yml` で導入する。
4. RHEL系では `build-client-go-source-rpm.yml` でコンテナ内ビルドを行い, `install-client-go-local-rpm.yml` で導入する。
5. 導入後に `go.mod`, `go.sum`, `vendor/` の存在と, `k8s.io/client-go` 版数一致を確認する。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `go_k8s_client_version` | `""` | client-go の版数。`vX.Y.Z` 形式で指定する。 |
| `go_k8s_client_module_domain` | `dns_domain` または `"example.org"` | `go mod init` で使用するドメイン。 |
| `go_k8s_client_install_dir` | `"/opt/k8s-devel/go-client"` | オフラインキット導入先。 |
| `go_k8s_client_build_host` | `"localhost"` | 構築ホスト。 |
| `go_k8s_client_build_workspace` | `"/tmp/go-k8s-client-build"` | 構築ワークスペース。 |
| `go_k8s_client_build_output_dir` | `"{{ go_k8s_client_build_workspace }}/output"` | 成果物出力先。 |
| `go_k8s_client_deb_package_name` | `"go-k8s-client"` | Debian系ローカルパッケージ名。 |
| `go_k8s_client_rpm_package_name` | `"go-k8s-client"` | RHEL系ローカルパッケージ名。 |

## 検証例

```bash
ls -la /opt/k8s-devel/go-client
test -f /opt/k8s-devel/go-client/go.mod
test -f /opt/k8s-devel/go-client/go.sum
test -d /opt/k8s-devel/go-client/vendor
grep -E '^\s*k8s.io/client-go\s+v0\.31\.0$' /opt/k8s-devel/go-client/go.mod
```

## 注意事項

- 本ロールは client-go の導入ロジックのみを扱う。Go 本体の導入ロジックは `go-lang-local` ロールで扱う。
- `--check` 実行時は, パッケージ構築/導入処理をスキップする。