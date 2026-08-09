# reboot-common ロール

本ロールは, 再起動処理をロール間で共通化し, 呼び出し元ロールから同一の手順で再利用可能にするためのロールです。

## 目次

- [reboot-common ロール](#reboot-common-ロール)
	- [目次](#目次)
	- [用語](#用語)
	- [概要](#概要)
	- [本ロールの動作仕様](#本ロールの動作仕様)
	- [呼び出し元ロールからの使用方法](#呼び出し元ロールからの使用方法)
		- [呼び出し元ロール作成者が実施する作業](#呼び出し元ロール作成者が実施する作業)
		- [呼び出し元ロールでのパラメタの設定手順](#呼び出し元ロールでのパラメタの設定手順)
		- [呼び出し元ロールから本ロールを呼び出すansibleタスクの記載方法](#呼び出し元ロールから本ロールを呼び出すansibleタスクの記載方法)
		- [ハンドラから本ロール相当処理を呼び出すansibleタスクの記載方法](#ハンドラから本ロール相当処理を呼び出すansibleタスクの記載方法)
		- [各パラメタ変数に設定する値](#各パラメタ変数に設定する値)
	- [検証項目](#検証項目)
	- [前提条件](#前提条件)
	- [実行方法](#実行方法)
	- [主要変数](#主要変数)
	- [実行フロー](#実行フロー)
	- [検証ポイント](#検証ポイント)
	- [トラブルシューティング](#トラブルシューティング)
		- [1. 再起動後に SSH 再接続で失敗する場合](#1-再起動後に-ssh-再接続で失敗する場合)
		- [2. 再起動直後の接続が不安定になる場合](#2-再起動直後の接続が不安定になる場合)
		- [3. 権限不足で再起動できない場合](#3-権限不足で再起動できない場合)
		- [4. handler から再起動共通処理を呼び出せない場合](#4-handler-から再起動共通処理を呼び出せない場合)
	- [注意事項](#注意事項)
	- [参考資料](#参考資料)
		- [公式ドキュメント](#公式ドキュメント)

## 用語

この節では, 本文で使用する用語を定義します。

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
| サービスアカウント (Service Account) | - | 自動処理中でサービスを呼び出す側のプログラムを識別するための識別情報。 |
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
| Internet Protocol | IP | ネットワーク上で宛先を識別し, データを届けるための通信手順。 |
| Structured Query Language | SQL | データベースを操作するための記述言語。 |
| Hypertext Transfer Protocol | HTTP | World Wide Webで情報をやり取りする通信手順。 |
| Hypertext Transfer Protocol Secure | HTTPS | 通信内容を暗号化してWorld Wide Web通信を行う方式。 |
| RPM Package Manager | RPM | RPM形式パッケージの導入, 更新, 削除, 情報参照を行う仕組み。 |
| Virtual Machine | VM | 物理計算機上で動作する仮想的な計算機。 |
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
| Debian | - | コミュニティ主導で開発される Linux ディストリビューション。 |
| Ubuntu | - | Canonical が提供する Debian 系の Linux ディストリビューション。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| ロール | - | Ansible における処理のまとまり。 |
| 実行メッセージ | - | 実行中または失敗時に表示される文字列。 |
| 呼び出し元ロール | - | `reboot-common` を `include_role` などで呼び出す側のロール。 |
| 再起動フェーズ | - | 対象ホストを再起動し, 接続再確立を待機する一連の処理区間。 |
| `wait_for_connection` | - | Ansible の接続待機モジュール。再起動後に SSH 応答を待機するために使う。 |
| ControlMaster | - | OpenSSH の接続多重化機能。既存接続を再利用して SSH 接続を高速化します。 |
| `ansible_ssh_common_args` | - | SSH 実行時に共通で渡す追加引数。 |
| メタタスク | - | Ansible の `meta` モジュールで実行する制御用タスク。接続の再確立や実行状態の切り替えなど, 実処理ではなく実行制御を行う。 |
| `meta: reset_connection` | - | 既存 SSH セッションを切り替え, 新しい接続条件を反映するための Ansible メタタスク。 |
| Secure Shell | SSH | 遠隔の計算機へ安全に接続して操作する方式。 |
| Ansible Handler | handler | 設定変更時など特定条件でのみ実行する後続処理。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |
## 概要
本ロールは, 再起動処理をロール間で共通化し, 呼び出し元ロールから同一の手順で再利用可能にするためのロールです。
本ロールでは, 以下の機能を実現するための他のロールから呼び出し可能なロールを定義する:
1. 対象ホストの graceful reboot 実行
2. 再起動後の接続再確立待機 (`wait_for_connection`)
3. 再起動直後の接続揺らぎ吸収のための再試行
4. 通常時の SSH 多重化設定を維持しつつ, 再起動フェーズのみ ControlMaster を無効化する任意設定

本ロールは, reboot-common に関する設定処理を実施します。

## 本ロールの動作仕様

- 本ロールは, 呼び出し元から受け取った入力パラメタに基づいて対象ホストの再起動処理を実行します。
- 本ロールは, 再起動後に `wait_for_connection` を実行し, 接続再確立まで待機します。
- 本ロールは, 接続待機処理に `retries` と `delay` を適用し, 再起動直後の一時的な接続揺らぎを吸収します。
- `reboot_common_disable_controlmaster_during_reboot: true` を指定した場合のみ, 再起動フェーズ中に `ansible_ssh_common_args` へ ControlMaster 無効化引数を一時追加します。
- 再起動フェーズ終了後は, 退避した `ansible_ssh_common_args` を復元し, `meta: reset_connection` で通常時接続条件へ戻す。
- 本ロールは, 呼び出し元ロールが持つ `when` 条件や実行順序を変更しない。呼び出し元が判定した条件のもとで再起動共通処理のみを提供します。

## 呼び出し元ロールからの使用方法

本節では, 呼び出し元ロール作成者が `reboot-common` を利用する際の使用法について述べる。

### 呼び出し元ロール作成者が実施する作業

呼び出し元ロール作成者が `reboot-common` を利用する際に設定する変数と設定値の概要は以下の通り:

1. 再起動条件を呼び出し元ロール側で決定し, `when` 条件として明示します。
2. 再起動時の実行条件として以下の変数を設定する:
	 1. `reboot_common_timeout` : reboot モジュールの待機タイムアウト秒数
	 2. `reboot_common_message` : 再起動理由を示すログメッセージ文字列
	 3. `reboot_common_pre_reboot_delay` : reboot 実行前に待機する秒数
	 4. `reboot_common_become` : reboot 実行時に権限昇格を実施することを指定する真偽値
3. 再起動後接続待機条件として以下の変数を設定する:
	 1. `reboot_common_wait_for_connection_enabled` : 再起動後の接続待機を実行することを指定する真偽値
	 2. `reboot_common_wait_for_connection_timeout` : 接続待機全体のタイムアウト秒数
	 3. `reboot_common_wait_for_connection_connect_timeout` : 1回あたり接続試行のタイムアウト秒数
	 4. `reboot_common_wait_for_connection_delay_seconds` : 接続待機開始前の遅延秒数
	 5. `reboot_common_wait_for_connection_sleep_seconds` : 接続待機のポーリング間隔秒数
	 6. `reboot_common_wait_for_connection_retries` : 接続待機全体の再試行回数
	 7. `reboot_common_wait_for_connection_retry_delay_seconds` : 接続待機再試行の間隔秒数
4. 必要時のみ, 再起動フェーズ限定の SSH 多重化制御として以下の変数を設定する:
	 1. `reboot_common_disable_controlmaster_during_reboot` : 再起動フェーズ中のみ ControlMaster を無効化することを指定する真偽値
	 2. `reboot_common_reboot_phase_ssh_common_args` : 再起動フェーズ中に一時追加する SSH 共通引数文字列

### 呼び出し元ロールでのパラメタの設定手順

1. 呼び出し元ロール内で, 再起動が必要な条件を `when` として定義します。
2. `include_role` で `reboot-common` を呼び出し, 再起動条件・待機条件を `vars` で渡す。
3. 再起動後に続く処理がある場合は, 呼び出し元ロール側でその後続タスクを記述します。
4. `reboot_common_disable_controlmaster_during_reboot` は, 再起動直後の SSH 不安定を吸収したい場合のみ `true` を指定します。

### 呼び出し元ロールから本ロールを呼び出すansibleタスクの記載方法

本節では, 呼び出し元ロールの通常タスクから本ロールを呼び出す際の記載例を示す:

```yaml
1: - name: Reboot host via reboot-common
2:   ansible.builtin.include_role:
3:     name: reboot-common
4:   vars:
5:     reboot_common_timeout: "{{ reboot_timeout_sec }}"
6:     reboot_common_message: "Reboot triggered by role: example"
7:     reboot_common_pre_reboot_delay: 2
8:     reboot_common_become: true
9:     reboot_common_wait_for_connection_enabled: true
10:    reboot_common_wait_for_connection_timeout: 600
11:    reboot_common_wait_for_connection_connect_timeout: 15
12:    reboot_common_wait_for_connection_delay_seconds: 5
13:    reboot_common_wait_for_connection_sleep_seconds: 5
14:    reboot_common_wait_for_connection_retries: 3
15:    reboot_common_wait_for_connection_retry_delay_seconds: 10
16:    reboot_common_disable_controlmaster_during_reboot: false
```

上記例の記載内容は以下の通り:

- 1行目: 呼び出し元ロール側でのタスク名を定義します。
- 2-3行目: include_role で reboot-common ロール本体を呼び出す。
- 4行目: 本ロールに渡す入力パラメタの開始位置を示す。
- 5行目: reboot 実行時の待機タイムアウト秒数を指定します。
- 6行目: 再起動理由を実行ログへ残すメッセージを指定します。
- 7行目: reboot 実行前の待機秒数を指定します。
- 8行目: reboot 実行に権限昇格を適用することを指定します。
- 9行目: 再起動後に接続待機処理を有効化します。
- 10行目: wait_for_connection 全体の待機タイムアウト秒数を指定します。
- 11行目: 1回あたりの接続タイムアウト秒数を指定します。
- 12行目: 接続待機開始前の遅延秒数を指定します。
- 13行目: 接続待機ポーリング間隔秒数を指定します。
- 14行目: 接続待機全体の再試行回数を指定します。
- 15行目: 接続待機再試行の間隔秒数を指定します。
- 16行目: 再起動フェーズで ControlMaster を無効化しない設定を明示します。

### ハンドラから本ロール相当処理を呼び出すansibleタスクの記載方法

Ansible の仕様上, handler では `include_role` を直接利用できない。
そのため handler では, 本ロールのタスク本体を `include_tasks` で読み込む。

```yaml
1: - name: Reboot node handler
2:   listen: reboot_node_handler
3:   ansible.builtin.include_tasks:
4:     file: "{{ playbook_dir }}/roles/reboot-common/tasks/main.yml"
5:   vars:
6:     reboot_common_timeout: "{{ reboot_timeout_sec }}"
7:     reboot_common_message: "Reboot triggered by handler"
8:     reboot_common_pre_reboot_delay: 2
```

上記 handler 例の記載内容は以下の通り:

- 1行目: handler タスク名を定義します。
- 2行目: 通知名 reboot_node_handler を受ける handler として登録します。
- 3-4行目: include_tasks で reboot-common のタスク本体を読み込む。
- 5行目: 読み込み先へ渡す入力パラメタの開始位置を示す。
- 6行目: reboot 実行時の待機タイムアウト秒数を指定します。
- 7行目: handler 経由での再起動理由メッセージを指定します。
- 8行目: reboot 実行前の待機秒数を指定します。

### 各パラメタ変数に設定する値

| 変数 | 設定する値 | 設定例 |
| --- | --- | --- |
| `reboot_common_timeout` | reboot モジュールの待機タイムアウト秒数。ホストの起動時間に合わせて設定します。 | `600` |
| `reboot_common_message` | 再起動理由を示す文字列。監査やログ追跡のため, 呼び出し元ロール名や目的を含める。 | `"Reboot triggered by role: k8s-worker"` |
| `reboot_common_pre_reboot_delay` | 再起動コマンド実行前の遅延秒数。通常は `2` 秒程度。 | `2` |
| `reboot_common_become` | 再起動時に権限昇格を実施することを指定する真偽値。対象環境で昇格が必要な場合は `true`。 | `true` |
| `reboot_common_wait_for_connection_enabled` | 再起動後に接続待機を実行することを指定する真偽値。通常は `true`。 | `true` |
| `reboot_common_wait_for_connection_timeout` | `wait_for_connection` 全体の待機タイムアウト秒数。OS起動・クラスタ収束時間に合わせる。 | `600` |
| `reboot_common_wait_for_connection_connect_timeout` | 1回あたりの接続タイムアウト秒数。短すぎると瞬断で失敗しやすくなる。 | `15` |
| `reboot_common_wait_for_connection_delay_seconds` | 接続待機開始前の遅延秒数。再起動直後の初期待機に使う。 | `5` |
| `reboot_common_wait_for_connection_sleep_seconds` | 接続待機のポーリング間隔秒数。 | `5` |
| `reboot_common_wait_for_connection_retries` | 接続待機全体の再試行回数。一時的な接続揺らぎがある環境では増やす。 | `3` |
| `reboot_common_wait_for_connection_retry_delay_seconds` | 接続待機再試行の間隔秒数。 | `10` |
| `reboot_common_disable_controlmaster_during_reboot` | 再起動フェーズのみ ControlMaster を無効化することを指定する真偽値。通常は `false`、再起動直後の接続不安定時のみ `true`。 | `false` |
| `reboot_common_reboot_phase_ssh_common_args` | 再起動フェーズ中に一時追加する SSH 共通引数文字列。`reboot_common_disable_controlmaster_during_reboot: true` 時のみ有効。 | `"-o ControlMaster=no -o ControlPersist=no"` |

補足事項:

- `reboot_common_wait_for_connection_*` は再起動後の接続収束までの待ち方を制御します。
- 変数未指定時は [roles/reboot-common/defaults/main.yml](roles/reboot-common/defaults/main.yml) の既定値が適用される。

## 検証項目

- 呼び出し元ロールから `include_role: name: reboot-common` で再起動処理を実行できること。
- 再起動後に `wait_for_connection` が成功し, 後続タスクへ遷移できること。
- `reboot_common_disable_controlmaster_during_reboot: true` のとき, 再起動フェーズ後に SSH 引数が復元されること。
- handler 経由の場合に `include_tasks` 方式で同等の再起動処理を実行できること。

## 前提条件

- 対象ホストが inventory に登録済みであること
- 関連する共通変数が vars/all-config.yml または host_vars に定義済みであること

## 実行方法

制御ホストで以下のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts site.yml --tags "reboot-common"
```

## 主要変数

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| reboot_common_wait_for_connection_enabled | 再起動後の接続待機処理の実行可否を制御します。 | true | true |

## 実行フロー

1. [tasks/main.yml](tasks/main.yml) の `Normalize reboot-common parameters` で, 呼び出し元から未指定の入力値へ既定値を補完します。handler から `include_tasks` で呼び出された場合も同じ補完を適用します。
2. `reboot_common_disable_controlmaster_during_reboot: true` の場合は, [tasks/main.yml](tasks/main.yml) で現在の `ansible_ssh_common_args` を退避し, 再起動フェーズ用の無効化引数を一時追加した後, `meta: reset_connection` で反映します。
3. [tasks/main.yml](tasks/main.yml) の `Reboot host gracefully` で `ansible.builtin.reboot` を実行し, 対象ホストを再起動します。
4. `reboot_common_wait_for_connection_enabled: true` の場合は, [tasks/main.yml](tasks/main.yml) の `Wait for host connection after reboot` で `ansible.builtin.wait_for_connection` を実行し, 指定した timeout/retries/delay の条件で接続再確立を待機します。
5. 再起動フェーズ終了時は [tasks/main.yml](tasks/main.yml) の `always` 節で `ansible_ssh_common_args` を復元し, `meta: reset_connection` を実行して通常時の接続条件へ戻します。

## 検証ポイント

実行者は以下の検証コマンドを実行し, 構文検査が成功することを確認します。

```bash
ansible-playbook -i inventory/hosts site.yml --syntax-check
```

期待結果: エラーが出力されず, syntax check が成功します。

## トラブルシューティング

### 1. 再起動後に SSH 再接続で失敗する場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
ansible-playbook -i inventory/hosts site.yml --tags "reboot-common" -vv
```

**確認ポイント**:

- `Wait for host connection after reboot` タスクが失敗していないこと。
- 一時的な接続揺らぎで失敗する場合は, `reboot_common_wait_for_connection_timeout`, `reboot_common_wait_for_connection_retries`, `reboot_common_wait_for_connection_delay_seconds` を環境に合わせて調整していること。

### 2. 再起動直後の接続が不安定になる場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
ansible-playbook -i inventory/hosts site.yml --tags "reboot-common" -vv
```

**確認ポイント**:

- SSH 接続失敗が再起動直後に集中して発生していること。
- `reboot_common_disable_controlmaster_during_reboot` を `true` に設定し, 再起動フェーズ限定で ControlMaster 無効化を適用していること。

### 3. 権限不足で再起動できない場合

**実施対象ホスト**: 制御ホスト, 対象ホスト

**実行するコマンド**:

```bash
ansible-playbook -i inventory/hosts site.yml --tags "reboot-common" -vv
sudo -n true
```

**確認ポイント**:

- 実行ログに `permission denied` などの権限エラーが出ていないこと。
- `reboot_common_become` が `true` に設定されていること。
- 対象ホストで再起動実行ユーザの sudo 権限が有効であること。

### 4. handler から再起動共通処理を呼び出せない場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
ansible-playbook -i inventory/hosts site.yml --syntax-check
grep -n "include_role\|include_tasks" roles/*/handlers/*.yml
```

**確認ポイント**:

- handler で `include_role` を使用していないこと。
- handler では `include_tasks` で [roles/reboot-common/tasks/main.yml](roles/reboot-common/tasks/main.yml) を読み込んでいること。
- `--syntax-check` で handler 定義に関するエラーが出ていないこと。

## 注意事項

- 再起動を実行する条件 (`when`) は呼び出し元ロールで定義し, 業務影響のある時間帯を避けて実施すること。
- `reboot_common_become` を `true` で運用する場合は, 対象ホストで実行ユーザに sudo 権限が付与されていること。権限不足のまま実行すると再起動タスクが失敗します。
- `reboot_common_wait_for_connection_enabled` を `false` に設定した場合は, 再起動直後に後続タスクが実行されるため接続未復旧による失敗が起こり得ます。後続処理がある運用では `true` を維持すること。
- `reboot_common_wait_for_connection_timeout`, `reboot_common_wait_for_connection_retries`, `reboot_common_wait_for_connection_delay_seconds` は対象環境の起動時間に合わせて設定すること。値が短すぎる場合は正常再起動でも失敗判定になります。
- `reboot_common_disable_controlmaster_during_reboot` を有効化する場合は, SSH 再接続回数が増えるため処理時間が延びる可能性があることを踏まえて適用すること。
- handler では `include_role` を使用できないため, handler から呼び出す場合は `include_tasks` で [roles/reboot-common/tasks/main.yml](roles/reboot-common/tasks/main.yml) を読み込むこと。
- [roles/force-reboot](roles/force-reboot) は最終フェーズ向けであるため, 途中フェーズの共通再起動には本ロールを使用し, 役割を混在させないこと。

## 参考資料

### 公式ドキュメント

- [Ansible reboot module](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/reboot_module.html)
