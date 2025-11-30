# selinux ロール

このロールは SELinux を利用するホストに対して, 期待するモード (`enforcing` / `permissive` / `disabled`) を永続設定およびランタイム設定に反映し, 必要に応じて再ラベルや再起動を自動化します。SELinux が無い (Debian/Ubuntu 系など) 環境では自動的にスキップし, AppArmor など別メカニズムを採用するホストに影響を与えません。

## 主な処理

- `tasks/load-params.yml` で OS ごとの追加パッケージ定義 (`vars/packages-ubuntu.yml` / `vars/packages-rhel.yml`) や共通変数 (`vars/cross-distro.yml` / `vars/all-config.yml` / `vars/k8s-api-address.yml`) を読み込み, `common_selinux_state`・`force_relabel` などのパラメータを初期化します。
- `tasks/handle-selinux.yml` が SELinux の有無に応じて分岐します。
  - `tasks/detect-selinux.yml` は `/sys/fs/selinux/enforce` と `/etc/selinux/config` の存在を確認し, `selinux_present` フラグを設定します。
  - `tasks/config-selinux.yml` は SELinux が存在するホストでのみ読み込まれ, 以下の手順を実行します。
    1. `common_selinux_state` が許容値かを検証します。
    2. `getenforce` で現在のランタイムモードを取得し, `/etc/selinux/config` を `lineinfile` で `SELINUX=<state>` に書き換えます (既存ファイルがある場合のみ)。
    3. `SELINUXTYPE=targeted` 行が存在すれば targeted ポリシーへ揃えます。
    4. ランタイムモードが目標値と異なる場合に `setenforce 1/0` で即時切り替えを試みます (Disabled 状態では失敗しないよう `failed_when: false`)。
    5. 旧設定が `disabled` から有効化へ変わる場合や `force_relabel: true` のときは `/.autorelabel` を作成し, 次回起動時にフルリラベルを要求します。
    6. 永続設定の変更により無効化が必要な場合, またはフルリラベルが必要な場合は `reboot` モジュールで再起動し, `wait_for_connection` で復帰待ちを行います。
- SELinux が存在しないホストでは `debug` モジュールでスキップメッセージを出力するのみです。
- `tasks/package.yml`, `directory.yml`, `user_group.yml`, `service.yml`, `config.yml` は現状プレースホルダーであり, 将来的に SELinux 平行運用に必要な追加処理を実装するための枠として確保されています。

## 動作モード遷移の考え方

| 旧設定 (永続) | 新設定 (`common_selinux_state`) | ランタイム操作 | 追加処理 |
| -------------- | ------------------------------ | -------------- | -------- |
| `enforcing` / `permissive` | `enforcing` / `permissive` | `setenforce` で即時切り替え | 再起動は不要。`/.autorelabel` も作成しません。|
| `disabled` | `enforcing` / `permissive` | Disabled  =>  有効化は即時反映できないため次回起動時 | `/.autorelabel` を作成し, 再起動後にラベル再適用を実施します。|
| 任意 | `disabled` | `setenforce` は Disabled にできないため永続設定のみ変更 | `SELINUX=disabled` を書き換えた後に再起動。`wait_for_connection` で復帰を待機します。|
| 任意 | 任意 | `force_relabel: true` | 強制リラベルを行いたい場合は `/.autorelabel` を作成し, 再起動で実行します。|

## 利用する主な変数

| 変数名 | 定義場所 (初期値) | 用途 |
| ------ | ----------------- | ---- |
| `common_selinux_state` | `roles/selinux/defaults/main.yml` (`permissive`) | 目標とする SELinux モード。`enforcing` / `permissive` / `disabled` から選択。|
| `force_relabel` | `roles/selinux/defaults/main.yml` (`false`) | `true` の場合は状態に関わらず `/.autorelabel` を作成し, 次回起動でフルリラベルを強制します。|
| `selinux_present` | タスク内で検出 | SELinux が利用可能なホストかどうかを示す内部フラグ。|
| `se_configured_state_old` | `config-selinux.yml` 内部 | `/etc/selinux/config` の旧 `SELINUX=` 値。遷移判定とリラベル判定に利用します。|
| `need_full_relabel` | `config-selinux.yml` 内部 | 再ラベルが必要かを示す内部フラグ。|

その他, `vars/packages-*.yml` や `vars/cross-distro.yml` により, SELinux 関連の追加パッケージや他ロールと共有する設定値を拡張できます。

## 実行方法

```bash
ansible-playbook -i inventory/hosts common.yml --tags selinux
```

SELinux 設定のみを更新したいホストを絞る場合は `-l <hostname>` を併用してください。再起動が発生する可能性があるため, メンテナンスウィンドウ内での実行を推奨します。

## 検証ポイント

- `getenforce` の結果が `common_selinux_state` に合わせて `Enforcing` / `Permissive` / `Disabled` になっている。
- `/etc/selinux/config` の `SELINUX=` が期待値に更新され, 必要に応じて `SELINUXTYPE=targeted` が保たれている。
- `/.autorelabel` がリラベル必要時のみに存在し, 再起動後に削除されている。
- `journalctl -b` などで再起動がトリガーされた場合のログを確認し, `setenforce` 実行が失敗していない。
- `selinux_present` が `false` のホストでは, スキップメッセージのみが表示され, 処理が実行されていない。

## 運用メモ

- SELinux を無効化 (`disabled`) から有効化する場合, 再起動と再ラベルが必須です。特に大規模環境では所要時間の見積りとバックアップを事前に確認してください。
- `force_relabel` は大量のラベル再適用を引き起こすため慎重に利用し, 使用後は `false` に戻す運用を推奨します。
- Debian/Ubuntu 系では SELinux パッケージを別途導入しない限り `selinux_present` が `false` となりスキップされます。AppArmor の設定はこのロールでは扱いません。
- 再起動有無を制御したい場合は, 上位プレイブックで `common_selinux_state` を変更する前にメンテナンスフラグと連動させるなどの工夫を検討してください。
- 他ロールから SELinux コンテキスト調整を行う場合は, このロールの実行順序を先にし, 必要に応じて `force_relabel` での再適用を計画してください。
