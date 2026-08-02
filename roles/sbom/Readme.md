# sbom ロール

本ロールは `sbom-tool` を用いて、対象ホスト上で SPDX JSON 形式 ( 既定: SPDX 2.2 ) の SBOM を生成します。

## 目次

- [sbom ロール](#sbom-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
    - [対象ホスト上の生成物](#対象ホスト上の生成物)
    - [制御ノード上の収集物](#制御ノード上の収集物)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
  - [トラブルシューティング](#トラブルシューティング)
  - [注意事項](#注意事項)
    - [RHEL系の `copyrightText`について](#rhel系の-copyrighttextについて)
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
| Internet Protocol | IP | インターネットプロトコルの略称。 |
| Structured Query Language | SQL | データベースを操作するための記述言語。 |
| Hypertext Transfer Protocol | HTTP | WWW で情報をやり取りする通信手順。 |
| Hypertext Transfer Protocol Secure | HTTPS | 通信内容を暗号化して WWW 通信を行う方式。 |
| RPM Package Manager | RPM | RHEL 系で使用するパッケージ形式。 |
| Virtual Machine | VM | 物理機器上で動作する仮想的な計算機。 |
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
| コンテナ | - | アプリケーションを動かす隔離された実行単位。 |
| ネットワーク | - | 機器同士を接続してデータをやり取りする仕組み。 |
| アドレス | - | 宛先や所在を識別するための情報。 |
| プロトコル | - | 通信やデータ交換の手順を定めた取り決め。 |
| ディレクトリ | - | ファイルを階層的に整理するための入れ物。 |
| ログ | - | 処理の結果や状態を時系列で記録した情報。 |
| コード | - | 処理内容を記述した文字列。 |
| Linux | - | 多くの機器で使われる, 基本ソフトウェアの系統。 |
| Debian | - | コミュニティ主導で開発される Linux ディストリビューション。 |
| Ubuntu | - | Canonical が提供する Debian 系の Linux ディストリビューション。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Application Programming Interface | API | アプリケーション同士がやり取りする方法を定めた仕様。 |
| Uniform Resource Locator | URL | WWW 上の資源の場所を示す文字列。 |
| Software Bill of Materials | SBOM | ソフトウェア構成部品の明細書, 使用しているライブラリや依存関係を記録 |
| Software Package Data Exchange | SPDX | ソフトウェアパッケージのメタデータとライセンス情報を記述する標準形式 |
| JavaScript Object Notation | JSON | 人間が読みやすいテキスト形式のデータ交換フォーマット。キーと値のペアで構成され, 設定ファイルやAPI レスポンスに広く使用される。 |
| Kubernetes | - | コンテナを管理する基盤ソフトウェア。 |
| Helm | - | Kubernetesアプリケーションのパッケージ管理ツール。Chart形式でアプリケーションを配布, インストールします。 |
| Pod | - | Kubernetes でコンテナをまとめて管理する最小単位。 |
| Yet Another Markup Language | YAML | 設定ファイル形式です。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| Off | OFF | 無効状態を示す値。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `helm` | - | Kubernetesアプリケーションのパッケージ管理ツール。Chart形式でアプリケーションを配布, インストールします。 |
| `kubectl` | - | Kubernetesクラスタを操作するためのコマンドラインツール。 |
| rpmコマンド | - | RPM パッケージの情報参照や導入確認を行うコマンド。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |

## 概要
このロールは `sbom-tool` を用いて、対象ホスト上で SPDX JSON 形式 ( 既定: SPDX 2.2 ) の SBOM を生成します。
併せて, 対象ホストの状態 ( OSパッケージ、K8sコンポーネント、Helm、Podのimage、docker-composeのimage ) を収集し、追加の SPDX JSON を生成し, 生成された `*.spdx.json` を `ansible-playbook` 実行ノード ( 以下、制御ノード ) へ収集します。

### 対象ホスト上の生成物

`{{ sbom_drop_path }}/_manifest/{{ sbom_manifest_dir }}/manifest.spdx.json` ( sbom-tool による SBOM )と以下のファイルを対象ホスト上に生成します:

- `{{ sbom_extra_output_dir }}/os-packages.spdx.json` ( OSパッケージ一覧 )
- `{{ sbom_extra_output_dir }}/k8s-components.spdx.json` ( K8s関連コンポーネント )
- `{{ sbom_extra_output_dir }}/helm-releases.spdx.json` ( `helm list -A -o json` の結果 )
- `{{ sbom_extra_output_dir }}/k8s-images.spdx.json` ( `kubectl get pods -A -o json` から抽出した image 一覧 )
- `{{ sbom_extra_output_dir }}/compose-images.spdx.json` ( docker-compose YAML から抽出した image 一覧 )

### 制御ノード上の収集物

対象ホスト上の `{{ sbom_drop_path }}/_manifest` 配下から `*.spdx.json` を検索し、制御ノードの`{{ sbom_artifact_dir }}/<inventory_hostname>/*.spdx.json`に集約します。

## 前提条件

本ロールの実行者は, 対象ホストが inventory に登録済みであることを確認します。
本ロールの実行者は, 関連する共通変数が vars/all-config.yml または host_vars に定義済みであることを確認します。

## 実行方法

制御ホストで以下のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts site.yml --tags "sbom"
```
または,
```bash
make run_sbom
```

## 主要変数

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
| `sbom_collect_artifacts_enabled` | `true` | `*.spdx.json` を制御ノードへ収集する設定の可否 |
| `sbom_artifact_dir` | `sbom-artifact` | 制御ノード上の収集先 |

## テンプレートと生成ファイル

本ロールでは以下のテンプレート / ファイルを出力します:
主な展開先ホストは, 対象ホスト(既定) です。

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `spdx-minimal.json.j2` | `{{ sbom_extra_output_dir }}/os-packages.spdx.json` (既定: `{{ sbom_extra_output_dir }}/os-packages.spdx.json`) | OS パッケージ一覧を SPDX 形式で出力するための最小 SBOM テンプレートです。 |

## 実行フロー

1. 対象ホスト上で `sbom-tool generate` を実行し、`manifest.spdx.json` を生成します。
2. 追加SBOMが有効な場合、対象ホスト上の情報を収集して `{{ sbom_extra_output_dir }}` へ追加SBOMを出力します。

- `k8s-components.spdx.json` は、OSパッケージ名に加えて `kubelet` / `kubectl` / `containerd` のバイナリ版数 ( 取得できた場合 ) も含めます。
- `helm` / `kubectl` が無い、または接続できない場合、該当SBOMは空の一覧になり得ます。

収集が有効な場合、対象ホストの `{{ sbom_drop_path }}/_manifest` 配下から `*.spdx.json` を検索して制御ノードへ収集します。

## 検証ポイント

- 対象ホスト上で `{{ sbom_drop_path }}/_manifest/{{ sbom_manifest_dir }}/manifest.spdx.json` が生成されている。
- 追加SBOMが有効な場合、`{{ sbom_extra_output_dir }}` 配下に `*.spdx.json` が生成されている。
- 収集が有効な場合、制御ノード上の `{{ sbom_artifact_dir }}/<inventory_hostname>/` 配下に `*.spdx.json` が収集されている。

## トラブルシューティング

エラー発生時に build-*.log を確認し, 失敗した task 名と不足変数を特定します。

## 注意事項

### RHEL系の `copyrightText`について

RHEL系では、インストール済み実体に含まれるライセンス/著作権文書 ( 例: `/usr/share/licenses/<pkg>` や `rpm -q --licensefiles/--docfiles` ) から `copyrightText`
を抽出します。パッケージによっては文書が同梱されない場合があり、その場合は `NOASSERTION` になります。

## 参考資料

### 公式ドキュメント

- [SPDX](https://spdx.dev/specifications/)
