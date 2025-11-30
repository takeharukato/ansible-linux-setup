# RHEL / Alma Linux / Rocky Linux / Suse Linux用リポジトリ設定ロール

- テンプレートファイルにリポジトリ情報を記載する方式を極力避け, 各OSの
  公式モジュールを採用する
  - RPM系: `ansible.builtin.yum_repository` (RHEL/Alma/Rocky), `community.general.zypper_repository` ( SUSE )
  - APT系: `ansible.builtin.deb822_repository` ( 推奨。古い環境は `apt_repository` をフォールバック )
- **鍵は配布物同梱 & レポごとに束縛**：
  - APT: `/usr/share/keyrings/*.gpg` に配置し, **`signed-by=`** でレポごとに紐付け。`apt_key` は非推奨。
  - RPM: 署名鍵を `/etc/pki/rpm-gpg/` に配置し, `ansible.builtin.rpm_key` で導入。
- **二段検証 ( RPM系 ) **：`gpgcheck=1` ( パッケージ署名 )  + `repo_gpgcheck=1` ( メタデータ署名 ) を原則有効化。
- **優先度制御**：
  - RHEL/Alma/Rocky: `dnf-plugins-core` の `priority` を使用 ( 小さいほど優先 ) 。
  - SUSE: `zypper_repository.priority` を使用。
  - Debian/Ubuntu: **APT Pinning** ( `/etc/apt/preferences.d/*.pref` ) 。
- **変更時ハンドラ**：`dnf clean/makecache` または `zypper refresh` / `apt update` を実行し, **代表パッケージで到達性検証**。
- **社内ミラー/オフライン**：URL・`sslverify`・プロキシ等は**変数化**し, Pulp/Foreman/Satellite/SUSE Manager などの社内レジストリへ容易に切替可能に。
- **白リスト運用**：競合しうる外部レポは `includepkgs` ( DNF ) や Pinning ( APT ) で**限定公開**。
