# nfs-server ロール

このロールは Debian 系および Red Hat 系ホストに共通化した手順で NFS サーバーを構築します。公開ディレクトリの作成から `/etc/exports` の定義, `nfs-server` サービスの再起動までを一連のタスクにまとめており, `ansible_facts.os_family` に応じたパッケージ名の差異は `vars/cross-distro.yml` で吸収しています。

## 主な処理

- `tasks/load-params.yml` が OS 別パッケージ定義 (`vars/packages-ubuntu.yml` / `vars/packages-rhel.yml`) と共通変数 (`vars/cross-distro.yml` / `vars/all-config.yml` / `vars/k8s-api-address.yml`) を読み込み, `nfs_server_packages` や `nfs_export_directory` などのパラメーターを初期化します。
- `tasks/package.yml` は `nfs_server_packages` を最新化 (`state: latest`) し, 導入差分があれば GUI 無効化ハンドラ `disable_gui` を通知します。Debian 系では `nfs-kernel-server`, RHEL 系では `nfs-utils` をインストールします。
- `tasks/directory.yml` が公開ディレクトリ `nfs_export_directory` を所有者 `root:root`, パーミッション `1777` (タスク内で固定。全ユーザーが書き込める一方で, sticky bit により自分のファイルしか削除できない) で作成し, 複数クライアントからの一時利用を許可します。
- `tasks/config.yml` は以下を順番に適用します。
  - `/etc/idmapd.conf` に `dns_domain` を設定し, NFSv4 の UID/GID マッピングをドメインに合わせて統一。
  - `/etc/exports` に `nfs_export_directory` と `nfs_network`, `nfs_options` で構成されたエントリを `lineinfile` で追記・更新。
  - 設定変更後に `systemd` モジュールで `nfs-server` を再起動し, 常時有効化 (`enabled: true`) します。
- ハンドラ (`handlers/disable-gui.yml` / `handlers/restart-nfs.yml`) はそれぞれマルチユーザターゲット固定と `nfs-server` の再起動を担い, 再実行時も冪等性を維持します。

## 変数一覧

- `nfs_export_directory`: 公開するディレクトリの絶対パス。既定値は `/home/nfsshare` (`defaults/main.yml`)。ディレクトリのパーミッションはロール内タスクで `1777` に固定されています。
- `nfs_network`: 共有を許可するクライアントネットワーク。`{{ network_ipv4_network_address }}/{{ network_ipv4_prefix_len }}` が既定。
- `nfs_options`: `/etc/exports` に渡すマウントオプション。既定は `rw,no_root_squash,sync,no_subtree_check,no_wdelay` で, 読み書き許可・root 権限の透過割当・同期書き込み・サブディレクトリ検証の無効化・遅延書き込み抑制を意味します。
- `nfs_server_packages`: OS に応じた NFS サーバーパッケージリスト。Debian 系は `nfs-kernel-server`, RHEL 系は `nfs-utils`。
- `dns_domain`: `/etc/idmapd.conf` へ投入するドメイン名。`vars/all-config.yml` で定義され, 他ロールとも共有。

## 実行方法

```bash
ansible-playbook -i inventory/hosts server.yml --tags nfs-server
```

検証や個別適用では `basic.yml` や `devel.yml` など, 同タグを含むプレイブックでも呼び出せます。対象ホストを絞る場合は `-l <hostname>` を併用してください。

## 検証ポイント

- `systemctl is-active nfs-server` が `active`, `systemctl is-enabled nfs-server` が `enabled` を返す。
- `exportfs -v` に `nfs_export_directory` と `nfs_options` が反映されている。
- NFS クライアントから `showmount -e <nfs-host>` を実行し, 共有一覧に同ディレクトリが表示される。
- `/etc/idmapd.conf` の `Domain =` 行が `dns_domain` で更新されている。
- `journalctl -u nfs-server` に再起動時のエラーがなく, クライアントからのマウントが成功する。

## 運用メモ

- `nfs_export_directory` のパーミッションはタスク内で固定された `1777` (誰でも書き込み可能だが削除は自分のファイルのみ) です。異なるパーミッションが必要な場合は `roles/nfs-server/tasks/directory.yml` の `mode` を変更するか, 上位ロールで別途調整してください。
- 追加エクスポートを管理したい場合は, `/etc/exports.d/` にテンプレートを展開するサブロールを組み合わせるなど, 拡張方針を検討してください。
- `nfs_options` には `sec=krb5p` など追加のセキュリティオプションを指定できます。変更後はクライアント設定と整合性が取れているか検証してください。
- 大量クライアント向けには `nfs-server` のパフォーマンスパラメータ ( `/proc/fs/nfsd/` や `rpcbind` 設定 )を調整する必要があるため, 監視値を踏まえて段階的にチューニングしてください。
