# sbom ロール

このロールは `sbom-tool` を用いて、対象ホスト上で SPDX JSON 形式 ( 既定: SPDX 2.2 ) の SBOM を生成します。

併せて、対象ホストの状態 ( OSパッケージ、K8sコンポーネント、Helm、Podのimage、docker-composeのimage ) を収集し、追加の SPDX JSON を生成できます。

また、生成された `*.spdx.json` を `ansible-playbook` 実行ノード ( 以下、制御ノード ) へ収集できます。

## 生成物

### 対象ホスト上の生成物

- `{{ sbom_drop_path }}/_manifest/{{ sbom_manifest_dir }}/manifest.spdx.json` ( sbom-tool による SBOM )

追加SBOM ( Ansible側で収集 => テンプレート出力 )

- `{{ sbom_extra_output_dir }}/os-packages.spdx.json` ( OSパッケージ一覧 )
- `{{ sbom_extra_output_dir }}/k8s-components.spdx.json` ( K8s関連コンポーネント )
- `{{ sbom_extra_output_dir }}/helm-releases.spdx.json` ( `helm list -A -o json` の結果 )
- `{{ sbom_extra_output_dir }}/k8s-images.spdx.json` ( `kubectl get pods -A -o json` から抽出した image 一覧 )
- `{{ sbom_extra_output_dir }}/compose-images.spdx.json` ( docker-compose YAML から抽出した image 一覧 )

### 制御ノード上の収集物

対象ホスト上の `{{ sbom_drop_path }}/_manifest` 配下から `*.spdx.json` を検索し、制御ノードへ収集します。

- `{{ sbom_artifact_dir }}/<inventory_hostname>/*.spdx.json`

## 変数一覧

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `sbom_enabled` | `false` | ロール全体のON/OFF |
| `sbom_tool_bin_path` | `/usr/local/bin/sbom-tool` | sbom-tool の配置先 |
| `sbom_tool_download_url` | `""` | sbom-tool のダウンロードURL ( 未指定時は既定URLを利用 ) |
| `sbom_drop_path` | `/opt/sbom/drop` | sbom-tool の `-b` ( 成果物ディレクトリ ) |
| `sbom_build_components_path` | `{{ sbom_drop_path }}` | sbom-tool の `-bc` ( ビルドコンポーネントパス ) |
| `sbom_package_name` | `example-package` | sbom-tool の `-pn` |
| `sbom_package_version` | `0.0.0` | sbom-tool の `-pv` |
| `sbom_package_supplier` | `example-supplier` | sbom-tool の `-ps` / 追加SBOMの supplier |
| `sbom_namespace_uri_base` | `https://example.invalid/sbom` | SBOMの namespace 基底 |
| `sbom_manifest_info` | `SPDX:2.2` | sbom-tool の `-mi` |
| `sbom_manifest_dir` | `spdx_2.2` | sbom-tool の manifest ディレクトリ名 |
| `sbom_force_regenerate` | `true` | 既存manifestがあっても再生成 |
| `sbom_extra_sboms_enabled` | `true` | 追加SBOM全体のON/OFF |
| `sbom_extra_output_dir` | `{{ sbom_drop_path }}/_manifest` | 追加SBOMの出力先 |
| `sbom_extra_doc_prefix` | `{{ inventory_hostname }}` | 追加SBOMの Document 名プレフィックス |
| `sbom_os_packages_sbom_enabled` | `true` | OSパッケージSBOMのON/OFF |
| `sbom_k8s_components_sbom_enabled` | `true` | K8sコンポーネントSBOMのON/OFF |
| `sbom_k8s_component_name_patterns` | ( roles/sbom/defaults/main.yml 参照 ) | OSパッケージ名からK8s関連を抽出する正規表現リスト |
| `sbom_helm_sbom_enabled` | `true` | Helm releases SBOMのON/OFF |
| `sbom_k8s_images_sbom_enabled` | `true` | 稼働Pod image SBOMのON/OFF |
| `sbom_compose_sbom_enabled` | `false` | docker-compose image SBOMのON/OFF |
| `sbom_compose_files` | ( roles/sbom/defaults/main.yml 参照 ) | 対象 docker-compose YAML のパス |
| `sbom_collect_artifacts_enabled` | `true` | `*.spdx.json` を制御ノードへ収集するか |
| `sbom_artifact_dir` | `sbom-artifact` | 制御ノード上の収集先 |

## ロール内の動作

1. 対象ホスト上で `sbom-tool generate` を実行し、`manifest.spdx.json` を生成します。
2. 追加SBOMが有効な場合、対象ホスト上の情報を収集して `{{ sbom_extra_output_dir }}` へ追加SBOMを出力します。

- `k8s-components.spdx.json` は、OSパッケージ名に加えて `kubelet` / `kubectl` / `containerd` のバイナリ版数 ( 取得できた場合 ) も含めます。
- `helm` / `kubectl` が無い、または接続できない場合、該当SBOMは空の一覧になり得ます。

1. 収集が有効な場合、対象ホストの `{{ sbom_drop_path }}/_manifest` 配下から `*.spdx.json` を検索して制御ノードへ収集します。

## 検証ポイント

- 対象ホスト上で `{{ sbom_drop_path }}/_manifest/{{ sbom_manifest_dir }}/manifest.spdx.json` が生成されている。
- 追加SBOMが有効な場合、`{{ sbom_extra_output_dir }}` 配下に `*.spdx.json` が生成されている。
- 収集が有効な場合、制御ノード上の `{{ sbom_artifact_dir }}/<inventory_hostname>/` 配下に `*.spdx.json` が収集されている。

## 補足 ( RHEL系の `copyrightText` )

RHEL系では、インストール済み実体に含まれるライセンス/著作権文書 ( 例: `/usr/share/licenses/<pkg>` や `rpm -q --licensefiles/--docfiles` ) から `copyrightText`
を抽出します。パッケージによっては文書が同梱されない場合があり、その場合は `NOASSERTION` になります。
