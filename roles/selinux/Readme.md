# selinux ロール

本ロールは SELinux を利用するホストに対して, 期待するモード (`enforcing` / `permissive` / `disabled`) を永続設定およびランタイム設定に反映し, 必要に応じて再ラベルや再起動を自動化します。

## 目次

- [selinux ロール](#selinux-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [Step 1: ランタイムモード確認](#step-1-ランタイムモード確認)
    - [Step 2: 永続設定ファイル確認](#step-2-永続設定ファイル確認)
    - [Step 3: 再ラベル要求ファイル確認](#step-3-再ラベル要求ファイル確認)
    - [Step 4: 再起動と SELinux ログ確認](#step-4-再起動と-selinux-ログ確認)
    - [Step 5: SELinux 非搭載ホストでのスキップ確認](#step-5-selinux-非搭載ホストでのスキップ確認)
  - [トラブルシューティング](#トラブルシューティング)
  - [注意事項](#注意事項)
    - [動作モード遷移時の処理](#動作モード遷移時の処理)
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
| IP | - | インターネットプロトコルの略称。 |
| SQL | - | データベースを操作するための記述言語。 |
| HTTP | - | WWW で情報をやり取りする通信手順。 |
| HTTPS | - | 通信内容を暗号化して WWW 通信を行う方式。 |
| RPM | - | RHEL 系で使用するパッケージ形式。 |
| VM | - | 物理機器上で動作する仮想的な計算機。 |
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
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| API | - | アプリケーション同士がやり取りする方法を定めた仕様。 |
| URL | - | WWW 上の資源の場所を示す文字列。 |
| Security-Enhanced Linux | SELinux | 強制アクセス制御の仕組み。 |
| AppArmor | - | プロセスごとにアクセス権限を制御するLinuxセキュリティモジュール, Debian/Ubuntu系で標準採用 |
| enforcing | - | SELinuxがポリシー違反を検出しアクセスを拒否する動作モード |
| permissive | - | SELinuxがポリシー違反をログ記録のみ行い拒否しない動作モード, デバッグ用 |
| disabled | - | SELinuxが完全に無効化されている状態, 有効化には再起動が必要 |
| Red Hat Enterprise Linux | RHEL | Red Hat 社が提供する商用 Linux ディストリビューション。 |
| Debian | - | コミュニティ主導で開発される Linux ディストリビューション。 |
| Ubuntu | - | Canonical が提供する Debian 系の Linux ディストリビューション。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `journalctl` | - | systemd ジャーナルのログを参照するコマンド。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |

## 概要

本ロールは SELinux を利用するホストに対して, 期待するモード (`enforcing` / `permissive` / `disabled`) を永続設定およびランタイム設定に反映し, 必要に応じて再ラベルや再起動を自動化します。SELinux が無い (Debian/Ubuntu 系など) 環境では自動的にスキップし, AppArmor など別メカニズムを採用するホストに影響を与えません。

## 前提条件

- 対象ホストが inventory に登録済みであること
- 関連する共通変数が vars/all-config.yml または host_vars に定義済みであること

## 実行方法

```bash
ansible-playbook -i inventory/hosts common.yml --tags selinux
```
または,

```bash
make run_selinux
```

## 主要変数

| 変数名 | 定義場所 (規定値) | 用途 |
| ------ | ----------------- | ---- |
| `common_selinux_state` | `roles/selinux/defaults/main.yml` (`permissive`) | 目標とする SELinux モード。`enforcing` / `permissive` / `disabled` から選択。|
| `force_relabel` | `roles/selinux/defaults/main.yml` (`false`) | `true` の場合は状態に関わらず `/.autorelabel` を作成し, 次回起動でフルリラベルを強制します。|
| `selinux_present` | タスク内で検出 | SELinux が利用可能なホスト可否を示す内部フラグ。|
| `se_configured_state_old` | `config-selinux.yml` 内部 | `/etc/selinux/config` の旧 `SELINUX=` 値。遷移判定とリラベル判定に利用します。|
| `need_full_relabel` | `config-selinux.yml` 内部 | 再ラベルが必要かを示す内部フラグ。|

## 実行フロー

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

## 検証ポイント

### Step 1: ランタイムモード確認

**実施ノード**: 対象ホスト

**コマンド**:
```bash
getenforce
```

**期待される出力例**:
```plaintext
Permissive
```

**実行結果中の確認項目**:
- `Enforcing`, `Permissive`, `Disabled` のいずれかが1行で表示されること。
- `common_selinux_state` が `permissive` の場合は `Permissive`, `enforcing` の場合は `Enforcing` になっていること。
- `disabled` へ変更した直後は再起動前後で結果が変わるため, 再起動完了後の状態を確認すること。

### Step 2: 永続設定ファイル確認

**実施ノード**: 対象ホスト

**コマンド**:
```bash
grep -E '^(SELINUX|SELINUXTYPE)=' /etc/selinux/config
```

**期待される出力例**:
```plaintext
SELINUX=permissive
SELINUXTYPE=targeted
```

**実行結果中の確認項目**:
- `SELINUX=` 行が期待値に更新されていること。
- `SELINUXTYPE=` 行が存在するホストでは `SELINUXTYPE=targeted` になっていること。
- `/etc/selinux/config` が存在しない場合は, 本ロールの永続設定更新処理が条件分岐でスキップされることを前提に原因調査すること。

### Step 3: 再ラベル要求ファイル確認

**実施ノード**: 対象ホスト

**コマンド**:
```bash
ls -l /.autorelabel 2>/dev/null || echo 'no autorelabel file'
```

**期待される出力例**:
```plaintext
-r---------. 1 root root 0 Aug  2 10:15 /.autorelabel
```

**実行結果中の確認項目**:
- `disabled` から `enforcing` または `permissive` へ変更した場合, または `force_relabel: true` の場合のみ `/.autorelabel` が存在すること。
- 不要な通常変更時には `no autorelabel file` と表示されること。
- 再起動後は再ラベル完了に伴い当該ファイルが削除されていること。

### Step 4: 再起動と SELinux ログ確認

**実施ノード**: 対象ホスト

**コマンド**:
```bash
journalctl -b --no-pager | grep -Ei 'selinux|setenforce|relabel' | tail -n 20
```

**期待される出力例**:
```plaintext
Aug 02 10:14:01 node01 systemd[1]: Starting Relabel all filesystems...
Aug 02 10:18:35 node01 systemd[1]: Finished Relabel all filesystems.
Aug 02 10:18:40 node01 kernel: SELinux:  Initializing.
```

**実行結果中の確認項目**:
- `Relabel all filesystems` が必要時のみ出力されること。
- `SELinux: Initializing.` など, SELinux 初期化完了を示すメッセージがあること。
- `Failed`, `error`, `setenforce: SELinux is disabled` などの致命的メッセージが残っていないこと。

### Step 5: SELinux 非搭載ホストでのスキップ確認

**実施ノード**: 制御ホスト

**コマンド**:
```bash
ansible-playbook -i inventory/hosts common.yml --tags selinux -l <対象ホスト> | grep -F 'SELinux not present on this host. Skipping SELinux configuration.'
```

**期待される出力例**:
```plaintext
ok: [ubuntu-server.local] => {
  "msg": "SELinux not present on this host. Skipping SELinux configuration."
}
```

**実行結果中の確認項目**:
- スキップメッセージが表示されること。
- Debian/Ubuntu 系など SELinux 非搭載ホストで失敗せず `ok` 扱いになっていること。
- 設定変更タスクが実行されず, ホストへの不要な変更が発生していないこと。

## トラブルシューティング

代表的なトラブルと対処を以下に示します。

| 想定トラブル | 主な原因 | 対処方法 |
| --- | --- | --- |
| `Validate desired state` で停止する | `common_selinux_state` が `enforcing` / `permissive` / `disabled` 以外になっている | 実行者は `vars/all-config.yml` または `host_vars` の `common_selinux_state` を確認し, 許容値へ修正して再実行します。既定値は `permissive` です。 |
| SELinux を有効化したいのに何も変更されない | 対象ホストで `/sys/fs/selinux/enforce` と `/etc/selinux/config` の両方が存在せず, `selinux_present` が `false` になっている | 実行者は対象ホストが SELinux 搭載の RHEL 系であることを確認します。Debian/Ubuntu 系では本ロールはスキップ動作が正しく, SELinux 導入予定がある場合は別途 SELinux パッケージ群を導入してから再実行します。 |
| `setenforce` 実行後も期待モードに変わらない | 現在状態が `Disabled` であり, ランタイム切替では有効化できない | 実行者は `/etc/selinux/config` の `SELINUX=` が更新されていることと `/.autorelabel` が作成されていることを確認します。その後, 再起動完了まで待機し, 起動後に `getenforce` を再確認します。 |
| 再起動後の復帰待ちでタイムアウトする | フルリラベルに時間がかかっている, または `reboot_timeout_sec` が不足している | 実行者はコンソールから起動進行を確認し, 大容量ディスクや大量ファイル環境では `reboot_timeout_sec` を既定値 `600` より大きく設定します。再ラベル中は復帰に長時間を要する場合があります。 |
| `/.autorelabel` が毎回作成される | `force_relabel: true` が残っている | 実行者は `force_relabel` の設定値を確認します。強制再ラベルが不要になったら `false` に戻して再実行します。既定値は `false` です。 |
| `/etc/selinux/config` が更新されない | 対象ホストに設定ファイルが存在しないため, 永続設定タスクが条件分岐でスキップされている | 実行者は `/etc/selinux/config` の有無を確認します。SELinux を利用するホストでこのファイルが欠落している場合は, SELinux 関連パッケージや初期設定状態を修復してから再実行します。 |

## 注意事項

- SELinux を無効化 (`disabled`) から有効化する場合, 再起動と再ラベルが必須です。特に大規模環境では所要時間の見積りとバックアップを事前に確認してください。
- `force_relabel` は大量のラベル再適用を引き起こすため慎重に利用し, 使用後は `false` に戻す運用を推奨します。
- Debian/Ubuntu 系では SELinux パッケージを別途導入しない限り `selinux_present` が `false` となりスキップされます。AppArmor の設定はこのロールでは扱いません。
- 再起動有無を制御したい場合は, 上位プレイブックで `common_selinux_state` を変更する前にメンテナンスフラグと連動させるなどの工夫を検討してください。
- 他ロールから SELinux コンテキスト調整を行う場合は, このロールの実行順序を先にし, 必要に応じて `force_relabel` での再適用を計画してください。

### 動作モード遷移時の処理

| 旧設定 (永続) | 新設定 (`common_selinux_state`) | ランタイム操作 | 追加処理 |
| -------------- | ------------------------------ | -------------- | -------- |
| `enforcing` / `permissive` | `enforcing` / `permissive` | `setenforce` で即時切り替え | 再起動は不要。`/.autorelabel` も作成しません。|
| `disabled` | `enforcing` / `permissive` | Disabled  =>  有効化は即時反映できないため次回起動時 | `/.autorelabel` を作成し, 再起動後にラベル再適用を実施します。|
| 任意 | `disabled` | `setenforce` は Disabled にできないため永続設定のみ変更 | `SELINUX=disabled` を書き換えた後に再起動。`wait_for_connection` で復帰を待機します。|
| 任意 | 任意 | `force_relabel: true` | 強制リラベルを行いたい場合は `/.autorelabel` を作成し, 再起動で実行します。|

## 参考資料

### 公式ドキュメント

- [SELinux Project Wiki](https://github.com/SELinuxProject/selinux/wiki)
- [Red Hat SELinux docs](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_selinux/)
