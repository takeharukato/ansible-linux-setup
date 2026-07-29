# reboot-common ロール

本ロールは, 再起動処理をロール間で共通化し, 呼び出し元ロールから同一の手順で再利用可能にするためのロールである。
本ロールでは, 以下の機能を実現するための他のロールから呼び出し可能なロールを定義する:

1. 対象ホストの graceful reboot 実行
2. 再起動後の接続再確立待機 (`wait_for_connection`)
3. 再起動直後の接続揺らぎ吸収のための再試行
4. 通常時の SSH 多重化設定を維持しつつ, 再起動フェーズのみ ControlMaster を無効化する任意設定

- [reboot-common ロール](#reboot-common-ロール)
	- [用語](#用語)
	- [本ロールの動作仕様](#本ロールの動作仕様)
	- [呼び出し元ロールからの使用方法](#呼び出し元ロールからの使用方法)
		- [呼び出し元ロール作成者が実施する作業](#呼び出し元ロール作成者が実施する作業)
		- [呼び出し元ロールでのパラメタの設定手順](#呼び出し元ロールでのパラメタの設定手順)
		- [呼び出し元ロールから本ロールを呼び出すansibleタスクの記載方法](#呼び出し元ロールから本ロールを呼び出すansibleタスクの記載方法)
		- [ハンドラから本ロール相当処理を呼び出すansibleタスクの記載方法](#ハンドラから本ロール相当処理を呼び出すansibleタスクの記載方法)
		- [各パラメタ変数に設定する値](#各パラメタ変数に設定する値)
	- [トラブルシューティング](#トラブルシューティング)
	- [注意事項](#注意事項)
	- [検証項目](#検証項目)

## 用語

この節では, 本文で使用する用語を定義する。

| 用語 | 意味 |
| --- | --- |
| ロール | Ansible における処理のまとまり。 |
| 実行メッセージ | 実行中または失敗時に表示される文字列。 |
| 呼び出し元ロール | `reboot-common` を `include_role` などで呼び出す側のロール。 |
| 再起動フェーズ | 対象ホストを再起動し, 接続再確立を待機する一連の処理区間。 |
| `wait_for_connection` | Ansible の接続待機モジュール。再起動後に SSH 応答を待機するために使う。 |
| ControlMaster | OpenSSH の接続多重化機能。既存接続を再利用して SSH 接続を高速化する。 |
| `ansible_ssh_common_args` | SSH 実行時に共通で渡す追加引数。 |
| メタタスク | Ansible の `meta` モジュールで実行する制御用タスク。接続の再確立や実行状態の切り替えなど, 実処理ではなく実行制御を行う。 |
| `meta: reset_connection` | 既存 SSH セッションを切り替え, 新しい接続条件を反映するための Ansible メタタスク。 |

## 本ロールの動作仕様

- 本ロールは, 呼び出し元から受け取った入力パラメタに基づいて対象ホストの再起動処理を実行する。
- 本ロールは, 再起動後に `wait_for_connection` を実行し, 接続再確立まで待機する。
- 本ロールは, 接続待機処理に `retries` と `delay` を適用し, 再起動直後の一時的な接続揺らぎを吸収する。
- `reboot_common_disable_controlmaster_during_reboot: true` を指定した場合のみ, 再起動フェーズ中に `ansible_ssh_common_args` へ ControlMaster 無効化引数を一時追加する。
- 再起動フェーズ終了後は, 退避した `ansible_ssh_common_args` を復元し, `meta: reset_connection` で通常時接続条件へ戻す。
- 本ロールは, 呼び出し元ロールが持つ `when` 条件や実行順序を変更しない。呼び出し元が判定した条件のもとで再起動共通処理のみを提供する。

## 呼び出し元ロールからの使用方法

本節では, 呼び出し元ロール作成者が `reboot-common` を利用する際の使用法について述べる。

### 呼び出し元ロール作成者が実施する作業

呼び出し元ロール作成者が `reboot-common` を利用する際に設定する変数と設定値の概要は以下の通り:

1. 再起動条件を呼び出し元ロール側で決定し, `when` 条件として明示する。
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

1. 呼び出し元ロール内で, 再起動が必要な条件を `when` として定義する。
2. `include_role` で `reboot-common` を呼び出し, 再起動条件・待機条件を `vars` で渡す。
3. 再起動後に続く処理がある場合は, 呼び出し元ロール側でその後続タスクを記述する。
4. `reboot_common_disable_controlmaster_during_reboot` は, 再起動直後の SSH 不安定を吸収したい場合のみ `true` を指定する。

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

- 1行目: 呼び出し元ロール側でのタスク名を定義する。
- 2-3行目: include_role で reboot-common ロール本体を呼び出す。
- 4行目: 本ロールに渡す入力パラメタの開始位置を示す。
- 5行目: reboot 実行時の待機タイムアウト秒数を指定する。
- 6行目: 再起動理由を実行ログへ残すメッセージを指定する。
- 7行目: reboot 実行前の待機秒数を指定する。
- 8行目: reboot 実行に権限昇格を適用することを指定する。
- 9行目: 再起動後に接続待機処理を有効化する。
- 10行目: wait_for_connection 全体の待機タイムアウト秒数を指定する。
- 11行目: 1回あたりの接続タイムアウト秒数を指定する。
- 12行目: 接続待機開始前の遅延秒数を指定する。
- 13行目: 接続待機ポーリング間隔秒数を指定する。
- 14行目: 接続待機全体の再試行回数を指定する。
- 15行目: 接続待機再試行の間隔秒数を指定する。
- 16行目: 再起動フェーズで ControlMaster を無効化しない設定を明示する。

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

- 1行目: handler タスク名を定義する。
- 2行目: 通知名 reboot_node_handler を受ける handler として登録する。
- 3-4行目: include_tasks で reboot-common のタスク本体を読み込む。
- 5行目: 読み込み先へ渡す入力パラメタの開始位置を示す。
- 6行目: reboot 実行時の待機タイムアウト秒数を指定する。
- 7行目: handler 経由での再起動理由メッセージを指定する。
- 8行目: reboot 実行前の待機秒数を指定する。

### 各パラメタ変数に設定する値

| 変数 | 設定する値 | 設定例 |
| --- | --- | --- |
| `reboot_common_timeout` | reboot モジュールの待機タイムアウト秒数。ホストの起動時間に合わせて設定する。 | `600` |
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

- `reboot_common_wait_for_connection_*` は再起動後の接続収束までの待ち方を制御する。
- 変数未指定時は [roles/reboot-common/defaults/main.yml](roles/reboot-common/defaults/main.yml) の既定値が適用される。

## トラブルシューティング

主なトラブルの症状, 原因, 確認項目, 対処方法を以下に示す:

| 症状 | 主な原因 | 確認項目 | 対処 |
| --- | --- | --- | --- |
| 再起動後に SSH 再接続で失敗する | 起動直後のネットワーク未収束, sshd 起動遅延 | 実行ログの `Wait for host connection after reboot` タスク結果 | `reboot_common_wait_for_connection_timeout`, `retries`, `delay` を調整する。 |
| 再起動直後に接続が不安定になる | ControlMaster の既存接続再利用不整合 | 実行ログの SSH 接続失敗メッセージ | `reboot_common_disable_controlmaster_during_reboot: true` を検討する。 |
| 権限不足で再起動できない | 再起動実行ユーザに権限が無い | `permission denied` などのエラー | `reboot_common_become: true` を指定し, sudo 権限を確認する。 |
| handler から再起動共通処理を呼び出せない | handler で `include_role` を使用している | syntax-check エラー内容 | handler では `include_tasks` で [roles/reboot-common/tasks/main.yml](roles/reboot-common/tasks/main.yml) を読み込む。 |

## 注意事項

- 再起動を実行する条件 (`when`) は呼び出し元ロールで定義すること。
- 本ロールは再起動処理そのものを提供するため, 「どの条件で再起動するか」という業務判断は呼び出し元ロール側の責務である。
- handler では `include_role` が使えないため, 本ロール相当処理を呼ぶ場合は `include_tasks` 方式を使うこと。
- `reboot_common_disable_controlmaster_during_reboot` を有効化する場合, SSH 接続確立回数が増えるため処理時間が増える可能性がある。
- [roles/force-reboot](roles/force-reboot) は最終フェーズ用の再起動ロールであり, 途中処理の共通再起動には本ロールを使うこと。

## 検証項目

- 呼び出し元ロールから `include_role: name: reboot-common` で再起動処理を実行できること。
- 再起動後に `wait_for_connection` が成功し, 後続タスクへ遷移できること。
- `reboot_common_disable_controlmaster_during_reboot: true` のとき, 再起動フェーズ後に SSH 引数が復元されること。
- handler 経由の場合に `include_tasks` 方式で同等の再起動処理を実行できること。
