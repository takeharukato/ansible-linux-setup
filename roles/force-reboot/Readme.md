# 強制リブートロール

## 本ロールの位置づけ

ノード再起動後の動作をjournalctl -bオプションなどで, 起動後全体を通して確認する目的で作成。

各site.yamlの最後に以下のように記載する。

```:yaml
    - role: force-reboot # 最後に実行するようにすること
      tags: force-reboot
```

本ロールは, デバッグ用に使用するロールである。
原則として, playbook終了時に実行する処理は, `notify:`で実施要求を出し, `handlers/`ディレクトリ配下に定義されたハンドラで実行するのが望ましい。
このため, 最後にノード再起動が必要な場合は, ハンドラの実装を検討する。

`group_vars/all/all.yml`の`force_reboot`変数がtrueの場合, 再起動する。
`roles/force-reboot/defaults/main.yml`内で`force_reboot`変数デフォルト値を`false`に設定している。
