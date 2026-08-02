# OpenGrok

本ロールは, OpenGrok 導入ロール。

## 目次

- [OpenGrok](#opengrok)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
  - [トラブルシューティング](#トラブルシューティング)
  - [注意事項](#注意事項)
  - [参考資料](#参考資料)

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
| Kubernetes | K8s | コンテナを管理する基盤ソフトウェア。 |
| Pod | - | Kubernetes でコンテナをまとめて管理する最小単位。 |
| Linux | - | 多くの機器で使われる, 基本ソフトウェアの系統。 |
| Debian | - | コミュニティ主導で開発される Linux ディストリビューション。 |
| Ubuntu | - | Canonical が提供する Debian 系の Linux ディストリビューション。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Application Programming Interface | API | アプリケーション同士がやり取りする方法を定めた仕様。 |
| Uniform Resource Locator | URL | WWW 上の資源の場所を示す文字列。 |
| OpenGrok | - | ソースコード検索およびクロスリファレンス生成ツール。 |
| Docker Compose | - | 複数のコンテナからなるマルチコンテナアプリケーション(docker-compose.yml)を一括管理, 起動するツール |
| ソース同期 | - | Git リポジトリの clone/pull により, 解析対象のソースを更新する処理。 |
| インデクス更新処理 | - | 取り込んだファイル一覧を作り直し, 検索結果を最新化する処理。 |
| Application Programming Interface | API | API の正式名称。 |
| Hypertext Transfer Protocol | HTTP | HTTP の正式名称。 |
| Java Virtual Machine | JVM | Java プログラムを実行するための実行環境。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Representational State Transfer | REST | Web API を設計するための基本方針。 |
| Secure Shell | SSH | 遠隔の計算機へ安全に接続して操作する方式。 |
| Transmission Control Protocol | TCP | 通信相手との接続を確立してからデータを送受信する通信方式。 |
| User Interface | UI | 利用者がソフトウェアを操作するための見た目と操作方法。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `crontab` | - | 定期実行設定を登録, 表示, 削除するコマンド。 |
| `curl` | - | URL を指定してデータ送受信を行うコマンド。 |
| `docker` | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| `make` | - | Makefile に定義された処理を実行するコマンド。 |
| コード | - | 処理内容を記述した文字列。 |
| サービス | - | 機能を利用者や他システムへ提供する仕組み。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| ポート | - | 通信の出入口を識別する番号または接点。 |
| ローカルグループ | - | 実行中ホスト内で定義されるユーザグループ。 |
| ローカルユーザ | - | 実行中ホスト内に存在する利用者アカウント。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |

## 概要
OpenGrok 導入ロール。
本ロールを適用すると,
```text
http://ホスト名:28080/
```
で OpenGrok サーバにアクセス可能となる。
以下, {{と}}で囲んだ文字列はansible playbookの変数名を表す。
実行例中, `$`は一般ユーザのシェルプロンプト, `#`は`root`ユーザのシェルプロンプトを意味します。

本ロールは, opengrok-server に関する設定処理を実施します。

## 主な処理

本ロールは tasks/main.yml から task 群を呼び出し, 設定適用と検証を実施します。

## 前提条件

本ロールの実行者は, 対象ホストが inventory に登録済みであることを確認します。
本ロールの実行者は, 関連する共通変数が vars/all-config.yml または host_vars に定義済みであることを確認します。

## 実行方法

本ロールの実行方法は以下の通り:

```bash
make run_opengrok_server
```

または,

```bash
# OpenGrok タスクのみ実行
ansible-playbook --tags "opengrok-server" -i inventory/hosts site.yml
```

## 主要変数

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| `opengrok_enabled` | OpenGrok の導入可否を制御します。 | `false` | `true` |
| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `opengrok_enabled` | `false` | OpenGrokの導入制御変数。導入する場合は, `true`に設定します。|
| `opengrok_root_dir` | `/opt/opengrok` | OpenGrok 関連ファイルのベースディレクトリ。 |
| `opengrok_docker_dir` | `{{ opengrok_root_dir }}/docker` | docker-compose.yml 配置先。 |
| `opengrok_etc_dir` | `{{ opengrok_root_dir }}/etc` | source-urls.yml 配置先。 |
| `opengrok_scripts_dir` | `{{ opengrok_root_dir }}/scripts` | 同期スクリプト配置先。 |
| `opengrok_source_dir` | `{{ opengrok_root_dir }}/src` | OpenGrok が参照するソース配置先。 |
| `opengrok_sync_group_name` | `opengrok` | ソース同期ディレクトリへ書き込むためのローカルグループ名。 |
| `opengrok_sync_user_name` | `opengrok` | コンテナ実行IDに合わせて作成するローカルユーザ名。 |
| `opengrok_sync_user_list` | `[]` | ソース同期を実行するユーザの一覧。ここに指定したユーザをソースコード格納先ディレクトリのグループ(OpenGrokの公式コンテナイメージ内で設定されているアプリケーション実行グループ(appgroup)のGIDに対応するグループ)へ追加することでソースコードの更新許可を与える。 |
| `opengrok_image_version` | `1.14` | OpenGrok コンテナイメージのバージョン。 |
| `opengrok_service` | `opengrok` | OpenGrok サービス名 (docker compose)。 |
| `opengrok_service_port` | `28080` | OpenGrok 公開ポート (ホスト側)。 |
| `opengrok_reindex_service_port` | `25000` | 手動再インデクスREST公開ポート (ホスト側)。 |
| `opengrok_data_volume` | `opengrok_data` | OpenGrok データ用 Docker ボリューム名。 |
| `opengrok_java_opts` | `-Xms512m -Xmx2g` | Java オプション。 |
| `opengrok_java_module_opts` | `--add-exports ... --add-opens ...` | Java 21 で OpenGrok suggester の ChronicleMap が必要とする module export/open 設定。 |
| `opengrok_sync_period_minutes` | `10` | OpenGrok のインデックス更新周期(分)。 |
| `opengrok_wait_timeout` | `300` | サービス待ち合わせ時間(秒)。 |
| `opengrok_wait_delay` | `5` | サービス待ち合わせ開始遅延(秒)。 |
| `opengrok_wait_sleep` | `2` | サービス待ち合わせ間隔(秒)。 |
| `opengrok_wait_delegate_to_waitnode` | `localhost` | サービス待ち合わせ実行元ホスト(対象ホスト外, 制御ノード側)。 |
| `opengrok_source_urls_file` | `{{ opengrok_etc_dir }}/source-urls.yml` | 同期対象リポジトリ定義ファイル。 |
| `opengrok_gitconfig_file` | `{{ opengrok_etc_dir }}/gitconfig` | OpenGrok コンテナへ mount する Git system config。reindex 時の `opengrok-mirror` が bind mount 済みリポジトリを扱えるようにします。 |
| `opengrok_sync_script_path` | `{{ opengrok_scripts_dir }}/opengrok-source-sync.py` | Python 同期スクリプト配置先。 |
| `opengrok_sync_wrapper_path` | `{{ opengrok_scripts_dir }}/opengrok-source-sync.sh` | 同期処理用シェルスクリプト(Python 同期スクリプトを呼び出すラッパシェルスクリプト)配置先。 |
| `opengrok_daily_sync_script_path` | `{{ opengrok_scripts_dir }}/daily-sync-opengrok-sources.sh` | 日次同期処理用シェルスクリプト配置先。 |
| `opengrok_reindex_script_path` | `{{ opengrok_scripts_dir }}/opengrok-reindex.sh` | 手動再インデクス実行用シェルスクリプト配置先。 |
| `opengrok_sync_command_path` | `/usr/local/bin/opengrok-source-sync` | 同期処理用シェルスクリプト(Python 同期スクリプトを呼び出すラッパシェルスクリプト)への実行コマンドシンボリックリンク先。 |
| `opengrok_reindex_command_path` | `/usr/local/bin/opengrok-reindex` | 手動再インデクス実行用シェルスクリプトへの実行コマンドシンボリックリンク先。 |
| `opengrok_sync_log_file` | `/var/log/opengrok-source-sync.log` | 同期ログ出力先。 |
| `opengrok_logrotate_enabled` | `true` | 同期ログ向け logrotate 設定の導入有効化フラグ。 |
| `opengrok_logrotate_config_path` | `/etc/logrotate.d/opengrok-source-sync` | logrotate 設定ファイル配置先。 |
| `opengrok_logrotate_frequency` | `daily` | ログローテーション周期。 |
| `opengrok_logrotate_maxsize` | `50M` | このサイズを超えた場合に周期を待たずローテーションする閾値。 |
| `opengrok_logrotate_rotate` | `2` | 保持世代数。 |
| `opengrok_logrotate_dateext` | `true` | ローテーション後ファイル名への日付付与設定。 |
| `opengrok_logrotate_compress` | `true` | ローテーション済みログ圧縮設定。 |
| `opengrok_logrotate_delaycompress` | `true` | 最新世代の圧縮を1回遅延させる設定。 |
| `opengrok_logrotate_missingok` | `true` | ログファイル未作成時にエラー扱いしない設定。 |
| `opengrok_logrotate_notifempty` | `true` | 空ログをローテーションしない設定。 |
| `opengrok_logrotate_create_mode` | `0640` | ローテーション後に作成するログファイルのパーミッション。 |
| `opengrok_logrotate_create_owner` | `root` | ローテーション後に作成するログファイルのオーナ。 |
| `opengrok_logrotate_create_group` | `root` | ローテーション後に作成するログファイルのグループ。 |
| `opengrok_logrotate_su_user` | `root` | logrotate 実行時に使用するユーザ。 |
| `opengrok_logrotate_su_group` | `root` | logrotate 実行時に使用するグループ。 |
| `opengrok_python_command` | `/usr/bin/python3` | Python 実行コマンド。環境変数PATHに依存しないよう, 絶対パスで指定します。 |
| `opengrok_daily_sync_extra_args` | `""` | 日次同期スクリプトへ渡す追加引数。 |
| `opengrok_completion_enabled` | `true` | bash/zsh 補完導入有効化フラグ。 |

## テンプレートと生成ファイル

本ロールを適用すると, `/opt/opengrok` 配下に以下のファイルが作られる。

- docker ディレクトリ
  - docker-compose.yml OpenGrok サーバを起動するための docker compose ファイル。
- etc ディレクトリ
  - source-urls.yml 同期対象リポジトリ定義ファイル。
  - gitconfig OpenGrok コンテナに mount する Git system config。
- scripts ディレクトリ
  - opengrok-source-sync.py リポジトリ同期を実行する Python スクリプト。
  - opengrok-source-sync.sh Python スクリプト呼び出し用ラッパシェルスクリプト。
  - daily-sync-opengrok-sources.sh 日次同期実行用シェルスクリプト。crontab からの呼び出しを想定。
  - opengrok-reindex.sh 手動再インデクス実行用シェルスクリプト。
- src ディレクトリ
  - source-urls.yml 記述に従って clone/pull されるソースを展開する先となるディレクトリ。

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `docker-compose.yml.j2` | `/opt/opengrok/docker/docker-compose.yml` (既定: `/opt/opengrok/docker/docker-compose.yml`) | OpenGrok の Docker Compose 定義ファイル。コンテナ実行ユーザはOpenGrok公式コンテナイメージの既定値(ユーザID/グループID共に1111)を使用します。`NOMIRROR=1` を設定し, 自動的にリポジトリを同期する処理(コンテナ内で Git リポジトリに対して `git pull --ff-only` を実行して更新を取り込む処理)を常に無効化します。 |
| `source-urls.yml.j2` | `/opt/opengrok/etc/source-urls.yml` (既定: `/opt/opengrok/etc/source-urls.yml`) | 同期対象リポジトリ定義ファイル。 |
| `gitconfig.j2` | `{{ opengrok_gitconfig_file }}` (既定: `{{ opengrok_gitconfig_file }}`) | OpenGrok コンテナへ mount する Git system config。reindex 時に `opengrok-mirror` が bind mount 済みリポジトリで `dubious ownership` エラーにならないよう `safe.directory` を設定します。 |
| `opengrok-source-sync.py.j2` | `/opt/opengrok/scripts/opengrok-source-sync.py` (既定: `/opt/opengrok/scripts/opengrok-source-sync.py`) | source-urls.yml を読み取り clone/pull を行うスクリプト。 |
| `opengrok-source-sync.sh.j2` | `/opt/opengrok/scripts/opengrok-source-sync.sh` (既定: `/opt/opengrok/scripts/opengrok-source-sync.sh`) | Python 同期スクリプトを呼び出すラッパシェルスクリプト。 |
| `daily-sync-opengrok-sources.sh.j2` | `/opt/opengrok/scripts/daily-sync-opengrok-sources.sh` (既定: `/opt/opengrok/scripts/daily-sync-opengrok-sources.sh`) | 日次同期実行用ラッパシェルスクリプト。 |
| `opengrok-reindex.sh.j2` | `/opt/opengrok/scripts/opengrok-reindex.sh` (既定: `/opt/opengrok/scripts/opengrok-reindex.sh`) | 手動再インデクス実行用 処理用スクリプト。 |
| `opengrok-source-sync.logrotate.j2` | `/etc/logrotate.d/opengrok-source-sync` (既定: `/etc/logrotate.d/opengrok-source-sync`) | 同期ログ(`/var/log/opengrok-source-sync.log`)のローテーション設定。 |
| `opengrok-source-sync.bash-completion.j2` | `/etc/bash_completion.d/opengrok-source-sync` (既定: `/etc/bash_completion.d/opengrok-source-sync`) | bash 補完定義。 |
| `_opengrok-source-sync.zsh-completion.j2` | `{{ opengrok_sync_zsh_completion_path }}` (既定: `{{ opengrok_sync_zsh_completion_path }}`) | zsh 補完定義。 |

## 実行フロー

1. [tasks/load-params.yml](tasks/load-params.yml) で OS 別パッケージ名や共通変数を読み込む。
2. [tasks/package.yml](tasks/package.yml) で Python 依存を含む前提パッケージを導入します。
3. [tasks/directory.yml](tasks/directory.yml) で Docker ボリューム作成, 主要ディレクトリ作成, [templates/docker-compose.yml.j2](templates/docker-compose.yml.j2) を配置します。あわせて [templates/source-urls.yml.j2](templates/source-urls.yml.j2), [templates/gitconfig.j2](templates/gitconfig.j2), [templates/opengrok-source-sync.py.j2](templates/opengrok-source-sync.py.j2), [templates/opengrok-source-sync.sh.j2](templates/opengrok-source-sync.sh.j2), [templates/daily-sync-opengrok-sources.sh.j2](templates/daily-sync-opengrok-sources.sh.j2), [templates/opengrok-reindex.sh.j2](templates/opengrok-reindex.sh.j2) を配置します。
4. [tasks/user_group.yml](tasks/user_group.yml) で 以下の処理を実施する:
   1. OpenGrok公式コンテナイメージ内で設定されているグループIDを基準に, 対象ホスト側で使用するグループを決定する(競合時は既存アカウントを優先利用)。
   2. `{{ opengrok_source_dir }}` の所有者は `root` のまま, グループを OpenGrok公式コンテナイメージ内で設定されているグループIDに対応するグループID(`1111`)に設定します。
   3. 以下のようにアクセス権を設定(8進数で, `2775`に設定):
      1. グループIDを継承するよう指定(`setgid`ビットを設定)
      2. 所有者/所有グループに対して, 読み書き実行可能
      3. その他に対して読み取りと実行可能
   4. `opengrok_sync_user_list` に列挙されたユーザを当該グループに追加します。
5. [tasks/service.yml](tasks/service.yml) で `docker compose down` / `docker compose up -d` を実行し, `{{ opengrok_service_port }}` の起動待ち合わせを2段階で実施します。第1段階で対象ホスト内 (localhost) の待受を確認し, 第2段階で制御ノードから inventory ホスト名への到達性を確認します。コンテナ内で自動的にリポジトリを同期する処理(コンテナ内で Git リポジトリに対して `git pull --ff-only` を実行して更新を取り込む処理)は, [templates/docker-compose.yml.j2](templates/docker-compose.yml.j2) で `NOMIRROR=1` を設定することで常に無効化します。
6. [tasks/logrotate.yml](tasks/logrotate.yml) で 同期ログ向け logrotate 設定を配備します。
7. [tasks/config.yml](tasks/config.yml) で bash/zsh 補完を導入します。

## 検証ポイント

- `/opt/opengrok` 以下に docker, etc, scripts, src ディレクトリが作成されていること。
- `docker compose -f /opt/opengrok/docker/docker-compose.yml ps` で OpenGrok コンテナが稼働していること。
- OpenGrok サービスが `http://ホスト名:28080/` でアクセス可能なこと。
- `/usr/local/bin/opengrok-source-sync --dry-run` が正常終了すること。
- `crontab -l` に手動登録したエントリが反映されていること。
- `logrotate -d /etc/logrotate.conf` で `/etc/logrotate.d/opengrok-source-sync` の設定が解釈されること。

### `/opt/opengrok` 以下に docker, etc, scripts, src ディレクトリが作成されていることの確認

本作業は, 本ロールを適用したホスト上で実施します。実行するコマンドは以下の通り:
```bash
ls -l /opt/opengrok
```

実行例:
```bash
$ ls -l /opt/opengrok
合計 16K
drwxr-xr-x 2 root     root     4096  7月 19 16:33 docker
drwxr-xr-x 2 root     root     4096  7月 19 16:09 etc
drwxr-xr-x 2 root     root     4096  7月 19 16:47 scripts
drwxrwsr-x 3 opengrok opengrok 4096  7月 19 16:48 src
```

docker, etc, scripts, src ディレクトリが作成されていること, `src` ディレクトリの所有者が `root` であること, グループがコンテナ内規定の実行グループGID(`1111`)に対応するグループであること, パーミッションが `2775` であることを確認します。

### `docker compose -f /opt/opengrok/docker/docker-compose.yml ps` で OpenGrok コンテナが稼働していることの確認

本作業は, 本ロールを適用したホスト上で実施します。実行するコマンドは以下の通り:
```bash
docker compose -f /opt/opengrok/docker/docker-compose.yml ps
```

実行例:
```bash
$ docker compose -f /opt/opengrok/docker/docker-compose.yml ps

NAME                  IMAGE                        COMMAND                   SERVICE       CREATED         STATUS         PORTS
opengrok              opengrok/docker:1.14         "/scripts/entrypoint…"   opengrok      6 minutes ago   Up 6 minutes   0.0.0.0:25000->5000/tcp, [::]:25000->5000/tcp, 0.0.0.0:28080->8080/tcp, [::]:28080->8080/tcp
```

以下の項目を確認する:
- `NAME`の列にopengrokという名前のコンテナが含まれること
- `IMAGE`の列のコンテナイメージのタグ名部分が`opengrok_image_version`変数での指定値と一致すること
- PORTSの項目に以下の項目が含まれること
  - `0.0.0.0:25000->5000/tcp`
  - `[::]:25000->5000/tcp`
  - `0.0.0.0:28080->8080/tcp`
  - `[::]:28080->8080/tcp`

### OpenGrok サービスが `http://ホスト名:28080/` でアクセス可能なことの確認

本作業は, 本ロールを適用したホストに接続可能なホスト上で実施します。実行するコマンドは以下の通り:
```bash
curl -I http://ホスト名:28080/
```

実行例:
```bash
$ curl -I http://mgmt-server.local:28080/
HTTP/1.1 200
Set-Cookie: JSESSIONID=1CD3D328266E6160A6535AC0694A0296; Path=/; HttpOnly; Secure; SameSite=Strict
Set-Cookie: OpenGrokProject=VirtualCluster; Secure; SameSite=Strict
Content-Type: text/html;charset=UTF-8
Date: Sun, 19 Jul 2026 08:01:08 GMT

```

以下の項目を確認する:
- 応答コードが, 正常系の応答(`200`など)となっていること

### `/usr/local/bin/opengrok-source-sync --dry-run` が正常終了すること

本作業は, 本ロールを適用したホスト上で実施します。実行するコマンドは以下の通り:
```bash
/usr/local/bin/opengrok-source-sync --dry-run
```

実行例:
```bash
$ /usr/local/bin/opengrok-source-sync --dry-run
2026-07-19 17:04:40 INFO [VirtualCluster] synchronized default branch=main
2026-07-19 17:04:40 INFO Synchronization completed successfully
```

以下の項目を確認する:
- 端末上の出力結果に`Synchronization completed successfully`という文字列が含まれること

### `crontab -l` に手動登録したエントリが反映されていること

本作業は, 本ロールを適用したホスト上で, かつ, crontabに登録する際に使用したユーザアカウントで実施します。実行するコマンドは以下の通り:

```bash
crontab -l
```

実行例:
```bash
$ crontab -l
# Edit this file to introduce tasks to be run by cron.
#
# Each task to run has to be defined through a single line
# indicating with different fields when the task will be run
# and what command to run for the task
#
# To define the time you can provide concrete values for
# minute (m), hour (h), day of month (dom), month (mon),
# and day of week (dow) or use '*' in these fields (for 'any').
#
# Notice that tasks will be started based on the cron's system
# daemon's notion of time and timezones.
#
# Output of the crontab jobs (including errors) is sent through
# email to the user the crontab file belongs to (unless redirected).
#
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
#
# For more information see the manual pages of crontab(5) and cron(8)
#
# m h  dom mon dow   command
0 3 * * * /opt/opengrok/scripts/daily-sync-opengrok-sources.sh >> /var/log/opengrok-source-sync.log 2>&1
```

以下の項目を確認する:
- 端末上の出力結果に`/opt/opengrok/scripts/daily-sync-opengrok-sources.sh`という文字列が含まれること, 当該文字列を含む行の実行時刻やコマンドラインが意図通りに設定されていること

## トラブルシューティング

実行者はエラー発生時に build-*.log を確認し, 失敗した task 名と不足変数を特定します。

## 注意事項

実行者は既存の実行順依存を崩さないことを確認した上で本ロールを実行します。

## ポートマッピング(ホストとコンテナ間)定義一覧

| サービス名 | ホスト側ポート | コンテナ側ポート | プロトコル | 厳密な用途 |
|---|---:|---:|---|---|
| `opengrok` | `{{ opengrok_service_port }}` | `8080` | TCP | OpenGrok Web UI/API の HTTP 待受。 |
| `opengrok` | `{{ opengrok_reindex_service_port }}` | `5000` | TCP | 手動再インデクス用 `/reindex` REST 待受。 |

## 環境変数一覧

### `opengrok` サービス

| 変数名 | 値 | 意味 |
|---|---|---|
| `JAVA_OPTS` | `{{ opengrok_java_opts }} {{ opengrok_java_module_opts }}` | OpenGrok コンテナ JVM オプション。既定では suggester 用 ChronicleMap の Java module export/open 設定を含む。 |
| `SYNC_PERIOD_MINUTES` | `{{ opengrok_sync_period_minutes }}` | OpenGrok コンテナ内でのインデックス更新周期(分)。 |

## ボリューム実体パスについて

### 事前条件

ホスト上の既存のボリュームを使用する設定(`external: true`) で, docker composeのボリュームを定義しているため, 外部ボリュームは docker compose 実行前に存在している必要がある。

本ロールでは, 以下の手順でボリューム実体パスを作成する:

```bash
docker volume create {{ opengrok_data_volume }}
```

規定値の場合は, 以下のようにコマンドを実行する:
```bash
docker volume create opengrok_data
```

### Mountpoint の確認

各ボリュームの Mountpoint 確認方法は以下の通り。

```bash
docker volume inspect -f '{{ .Mountpoint }}' {{ opengrok_data_volume }}
```

規定値の場合は, 以下のようにコマンドを実行する:
```bash
docker volume inspect -f '{{ .Mountpoint }}' opengrok_data
```

## ソース同期スクリプト(`opengrok-source-sync`)を用いたソース同期処理手順

本ロールでは, ソース同期スクリプト(`opengrok-source-sync` コマンド)を用意している。
`opengrok_sync_user_list`に含まれるユーザで, 以下のように `opengrok-source-sync` コマンドを実行することで, Githubなどのソースリポジトリからソースコードをダウンロードし, OpenGrokから検索可能にする:

```shell
/usr/local/bin/opengrok-source-sync --config /opt/opengrok/etc/source-urls.yml --src-root /opt/opengrok/src
```

### ソース同期スクリプト(`opengrok-source-sync`)のコマンドラインオプション

ソース同期スクリプト(`opengrok-source-sync`)のコマンドラインオプションは, 以下の通り:

|オプション|意味|指定例|
|---|---|---|
|--config|同期対象リポジトリ定義ファイルへのパスを指定します。規定値は, `opengrok_etc_dir`変数で指定したディレクトリ配下の`source-urls.yml`となる。|--config /opt/opengrok/etc/source-urls.yml|
|--src-root|ソース展開先ディレクトリを指定します。既定値は, `opengrok_source_dir` で指定したディレクトリとなる。|--src-root /opt/opengrok/src|

### 同期対象リポジトリ定義ファイル(`source-urls.yml`)

同期対象リポジトリ定義ファイル(`source-urls.yml`)は, 調査対象ソースコード取得元となるGitHubのURLとタグ名の一覧を定義する設定ファイルです。同期対象リポジトリ定義ファイルには, 以下の形式の辞書のリストを設定することで, ソースコードを展開するディレクトリと調査対象ソースコード取得元となるGitHubのURLとの対応関係を定義する:

|キー|値|記載例|
|---|---|---|
|title|ソースコード格納先サブディレクトリを表すタイトル|linux|
|url|ソースコード取得元URL|https://github.com/torvalds/linux.git|
|tag|取得するソースコードのタグを固定する場合は, タグ名を記載します。未指定時は default branch の最新版を取得します。|v6.12|
|token|このエントリで使用するアクセストークンを直接指定します。未指定時は認証ヘッダを付与せずにアクセスします。|ghp_xxxxxxxxxxxxxxxxxxxx|

記載例は, 以下の通り:

```yaml
sources:
  - title: linux
    url: https://github.com/torvalds/linux.git
    tag: v6.12
    token: ghp_xxxxxxxxxxxxxxxxxxxx
  - title: opengrok
    url: https://github.com/oracle/opengrok.git
    token: ghp_yyyyyyyyyyyyyyyyyyyy
    # tag 未指定時は default branch の最新版を同期
```

## ソース同期処理の定期実行手順

定期的にソースコードを同期する場合は, `opengrok_sync_user_list`に含まれるユーザで, `crontab -e` コマンドを実行し, 以下の crontab エントリを手動作成する:

```text
0 3 * * * /opt/opengrok/scripts/daily-sync-opengrok-sources.sh >> /var/log/opengrok-source-sync.log 2>&1
```

### ソース同期処理の定期実行ログのローテーション設定

本稿の手順でcronによるソース同期処理の定期を実施した場合, `/var/log/opengrok-source-sync.log`ファイルにログが格納される。

本ロールは, `opengrok_logrotate_enabled` が `true` の場合に, 本ログの肥大化を抑止するための`logrotate`設定ファイルである, `/etc/logrotate.d/opengrok-source-sync` を配備します。

規定値では, `opengrok_sync_log_file` (`/var/log/opengrok-source-sync.log`) に対して以下の方針でローテーションします。

- 周期: `daily`
- サイズ閾値: `50M` (`maxsize`)
- 保持世代数: `2`
- 圧縮: `compress`, `delaycompress`
- 属性: `create 0640 root root`

### ソース同期処理の定期実行に関する留意事項

本ロールは crontab エントリを自動作成しない。

本ロールでは, 自動的にリポジトリを同期する処理(コンテナ内で Git リポジトリに対して `git pull --ff-only` を実行して更新を取り込む処理)を常に無効化している。したがって, Git リポジトリの clone/fetch/pull はホスト側の `opengrok-source-sync` が唯一の同期経路となる。これにより, コンテナ内の `git pull` が bind mount 済みリポジトリに対して SSH や認証情報の差異で失敗する事態を避ける。

## 手動でのインデクス更新手順

OpenGrokには, 手動でのインデクス更新処理用のREST APIとして, `/reindex` エンドポイントを提供している。

`/reindex` エンドポイントは, コンテナ内の REST ポート(5000)で要求を待ち受ける。本ロールの既定構成では, OpenGrokのRESTポート(コンテナ側ポート: `5000`番)をホスト側 ポート `25000` 番に公開します。

本ロールが導入するOpenGrok導入ホスト上で, 以下のコマンドを実行することで本REST APIを通した手動でのインデクス更新処理を実施することが可能です:

```bash
opengrok-reindex
```

正常にインデクス更新処理を呼び出した場合は, 端末上に`Reindex triggered`という出力が得られる。

実行例:
```bash
$ /usr/local/bin/opengrok-reindex
Reindex triggered
```

本コマンドは内部的に下記相当の `curl` を実行し, 必須の Authorization ヘッダを付与した上で, 手動でのインデクス更新処理用のREST APIを呼び出す:

```bash
curl -H "Authorization: Bearer trigger" http://127.0.0.1:25000/reindex
```

### 手動でのインデクス更新処理用のREST API(`/reindex` エンドポイント)に関する留意事項:

ブラウザから `http://mgmt-server.local:25000/reindex` を直接開くと, Authorization ヘッダが付かないため `Unauthorized Access` になりうるため, OpenGrok動作ホスト上で, `/opt/opengrok/scripts/opengrok-reindex.sh`を実行することを推奨します。OpenGrok公式のコンテナイメージの仕様上, 環境変数 `REST_TOKEN` を未設定にしても, `/reindex` 呼び出し時は `Authorization: Bearer <任意文字列>` ヘッダ自体が必要となる。 `REST_TOKEN` 未設定時はトークン値の一致検証は行われないため, 任意の値でよい。
## 参考資料

### 公式ドキュメント

- OpenGrok: https://github.com/oracle/opengrok
- Docker Compose: https://docs.docker.com/compose/

### 参考リンク

- [OpenGrok Docker image](https://hub.docker.com/r/opengrok/docker)
- [OpenGrok project](https://github.com/oracle/opengrok)
