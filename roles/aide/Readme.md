# Advanced Intrusion Detection Environment (AIDE)導入ロール

本ロールでは, Advanced Intrusion Detection Environment (AIDE)を,
RHEL/Ubuntuのパッケージから導入する。

## 変数一覧

| 変数名 | 意味 | 例 | 備考 |
| ------ | ---- | -- | ---- |
|aide_packages|AIDEのパッケージ名|"aide"|vars/cross-distro.ymlで定義しディストリビューション間の差異を吸収|
|aide_config_path|AIDEのコンフィグレーションファイルパス|"/etc/aide/aide.conf" (Debian/Ubuntu系), "/etc/aide.conf" (RHEL系)|vars/cross-distro.ymlで定義しディストリビューション間の差異を吸収|
|aide_database_path|AIDEのデータベースパス|"/var/lib/aide/aide.db.gz"|vars/cross-distro.ymlで定義しディストリビューション間の差異を吸収|
|aide_config_dropin_dir|AIDEのコンフィグレーションファイルのドロップインディレクトリパス|"/etc/aide/aide.conf.d"|vars/cross-distro.ymlで定義しディストリビューション間の差異を吸収, RHEL系では現状使用されない。|

## 留意事項

### AIDEの設定ファイルに対するドロップインディレクトリの扱いについて

本来は, AIDEの設定ファイルに対するドロップインディレクトリをUbuntu/Debian系に寄せて, `/etc/aide/aide.conf.d` ディレクトリを作成するようRHEL系でも処理を追加し, 統一した運用を行えることが望ましい。

しかし, 本ロール作成時点でのRHEL9系ディストリビューションに標準で搭載されているAIDEのバージョンは, 0.16であり, ワイルドカード指定での設定ファイルのインクルードや`@@x_include`ディレクティブがサポートされていない。

このため, ドロップインディレクトリの自動読み込みをUbuntu/Debian環境と同様には行えないことから, RHEL系ではドロップインディレクトリを作成しないようにした。

本ロール作成時のUbuntu/Debian系とRHEL系におけるAIDEの差異は以下の通り:

- Debian/Ubuntu: /etc/aide/aide.conf.d ディレクトリはパッケージにより自動作成され, 標準でドロップインディレクトリとしてサポートされている
- RHEL/AlmaLinux: AIDE 0.16ではワイルドカードや@@x_includeをサポートしていないため, ドロップインディレクトリの自動読み込みができない(インクルード対象ファイルごとに`@@include`ディレクティブを追記する必要がある)

## 参考リンク

- [第8章 AIDE で整合性の確認](https://docs.redhat.com/ja/documentation/red_hat_enterprise_linux/9/html/security_hardening/checking-integrity-with-aide_security-hardening) RHEL9のAdvanced Intrusion Detection Environment機能解説文書
