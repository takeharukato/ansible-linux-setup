# k8s-hubble-cli ロール

このロールは Hubble CLI (`hubble`) を GitHub 公式リリースから取得して各ノードへ配置し、Bash/Zsh の補完スクリプトを生成・展開します。既存のパッケージマネージャに依存せず任意バージョンを配布できるため、Kubernetes クラスタの Cilium/Hubble 運用に必要な CLI 環境を一貫して整備できます。

主な処理内容は以下の通りです。

- 事前に指定した `hubble_cli_version` を元に GitHub Releases からアーカイブをダウンロード
- 展開済みバイナリを `hubble_cli_install_dir` にオーナー `root:root`, パーミッション `0755` で配置
- Bash と Zsh の補完スクリプトを生成し、クロスディストロ変数で指定したディレクトリへコピー
- `curl`, `tar`, `gzip` などの補助パッケージを OS ファミリーごとの vars から導入

再実行に対応しており、同一バージョンでの再適用時はバイナリ・補完スクリプトをそのまま維持します。バージョンを変更すると自動的に再取得・再配置されます。

## 変数一覧

本ロールで扱う主な変数と用途は次の通りです。変数は `group_vars`, `host_vars`, あるいは `vars/all-config.yml` などで上書きできます。

| 変数名 | 役割 / 備考 |
| ------ | ----------- |
| `hubble_cli_version` | **必須**。配布する Hubble CLI のバージョン。未指定の場合はロール冒頭で `assert` が失敗します。 |
| `hubble_cli_github_repo` | リリースを参照する GitHub リポジトリ。既定は `cilium/hubble`。 |
| `hubble_cli_release_tag_prefix` | GitHub タグに付与する接頭辞。既定は `v`。 |
| `hubble_cli_download_url` | ダウンロード URL。既定値は上記パラメータを組み合わせた文字列で、独自ミラーを利用する場合に上書きします。 |
| `hubble_cli_install_dir` | バイナリ配置先。既定は `/usr/local/bin`。 |
| `hubble_cli_binary_name` | 配置するバイナリ名。既定は `hubble`。 |
| `hubble_cli_completion_enabled` | `true` で Bash/Zsh 補完を生成。`false` で補完処理をスキップ。 |
| `hubble_cli_bash_completion_path` | Bash 補完の出力先。`vars/cross-distro.yml` で Debian/RHEL の差異を吸収します。 |
| `hubble_cli_zsh_completion_path` | Zsh 補完の出力先。同上。 |
| `hubble_cli_packages` | 依存パッケージ一覧。`vars/packages-ubuntu.yml` / `vars/packages-rhel.yml` で OS ごとに定義しています。 |

そのほか一時展開ディレクトリ (`hubble_cli_temp_dir` など) も `defaults/main.yml` に配置しており、特殊なディスクレイアウトであれば適宜上書きしてください。

## 事前準備と実行手順

1. `vars/all-config.yml` などで `hubble_cli_version` を指定します。GitHub API を呼び出さない設計のため、必ず明示的に設定してください。
2. 必要であれば `hubble_cli_download_url` や `hubble_cli_install_dir` を上書きし、社内ミラーや独自パスへ切り替えます。
3. `ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml --tags k8s-hubble-cli` などでロールを適用します。ワーカーノードにも展開する場合は対応するプレイブックにタグを追加してください。
4. 適用後、対象ノードで `hubble version` を実行し、指定したバージョンが導入されたことを確認します。

## 検証ポイント

- `{{ hubble_cli_install_dir }}/hubble` が `root:root`、`0755` で配置され、`hubble version` が期待するバージョンを返すこと。
- Bash の場合 `source /etc/bash_completion` 後に `hubble <Tab>` で補完候補が表示されること。
- Zsh の場合 `autoload -Uz compinit && compinit` 後に `hubble <Tab>` で補完候補が表示されること。RHEL 系では `/usr/share/zsh/site-functions/_hubble`、Debian 系では `/usr/share/zsh/vendor-completions/_hubble` が生成されます。
- `/tmp` 配下の一時ディレクトリ (既定は `{{ hubble_cli_temp_parent }}/hubble-cli-<version>` ) が残らないこと。必要に応じて `hubble_cli_temp_parent` を変更してください。

## バージョン更新の指針

1. 新しいバージョンへ更新する際は、`hubble_cli_version` を変更し、必要なら `hubble_cli_download_url` を同じタグへ揃えます。
2. 再度ロールを適用すると、新しいアーカイブをダウンロードして既存バイナリを上書きします。
3. ロール適用後、`hubble version` と補完機能が新バージョンで動作することを確認してください。

## 備考

- プロキシ環境やオフライン環境で利用する場合は、あらかじめダウンロードしたアーカイブを内部リポジトリに配置し、`hubble_cli_download_url` を差し替えてください。
- `hubble_cli_completion_enabled` を `false` にすると補完スクリプト生成をスキップできます。端末ごとに利用したい場合、ホスト変数で切り替えてください。
- 依存パッケージは OS ファミリーごとに `vars/packages-*.yml` で管理しているため、新たなユーティリティが必要になった場合は該当ファイルへ追記します。
