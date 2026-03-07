# ntp-client ロール

このロールは, Debian系およびRHEL系ホストでNTPクライアント設定を適用するロールです。`ntp_client_choice`により`chrony`と`systemd-timesyncd`を切り替え, OS差異は`vars/cross-distro.yml`で吸収します。`ntp_servers_list`はテンプレート処理で空要素と重複を除去して反映します。

## 概要

### 構成要素

このロールは以下を構成します。

1. NTPクライアントパッケージの導入。
- Debian系では`ntp_client_choice`に応じて`chrony`または`systemd-timesyncd`を導入します。
- RHEL系では`chrony`を導入します。

2. NTPクライアント設定の反映。
- `systemd-timesyncd`選択時は`99-timesyncd.conf.j2`を配置します。
- `chrony`選択時は`99-chrony.conf.j2`をdrop-in設定として配置します。

3. サービス有効状態の反映。
- 選択した実装側サービスのみ有効化し, 非選択側サービスは無効化します。

### 実装の流れ

ロール実行時には以下の順で処理します。

1. 変数読み込み (`load-params.yml`)。
2. パッケージ導入 (`package.yml`)。
3. 設定反映 (`config.yml`)。
4. ディレクトリ作成 (`directory.yml`)。
5. ユーザ/グループ処理 (`user_group.yml`, 現状は空実装)。
6. サービス処理 (`service.yml`, 現状は空実装)。

### ディレクトリ構成

主要な設定対象は以下です。

```plaintext
/etc/systemd/timesyncd.conf.d/99-timesyncd.conf
/etc/chrony/chrony.conf (Debian系)
/etc/chrony.conf (RHEL系)
/etc/chrony/conf.d/99-custom.conf (Debian系)
/etc/chrony.d/99-custom.conf (RHEL系)
```

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Network Time Protocol | NTP | 時刻同期の仕組み。 |
| Operating System | OS | 基本ソフトウエア。 |
| Red Hat Enterprise Linux | RHEL | Red Hat系の企業向けLinuxディストリビューションです。 |
| Ansible | Ansible | インフラストラクチャの構成管理と自動化を行うオープンソースツール。YAML 形式のプレイブックでシステム構成を記述し, SSH を使用して複数のリモートホストに対して冪等な変更を実行できる。 |
| Yet Another Markup Language | YAML | 設定ファイル形式です。 |
| playbook | playbook | Ansibleの実行手順ファイルです。 |
| role | role | Ansibleで機能単位にまとめた構成です。 |
| template | template | 変数展開して出力する雛形ファイルです。 |
| handler | handler | 通知時に実行する再処理です。 |
| tag | tag | Ansibleで実行対象を絞るラベルです。 |
| systemd | - | Linux の初期化とサービス管理を行う仕組み。 |
| systemd-timesyncd | - | systemdに含まれる時刻同期クライアントサービスです。 |
| chrony | - | NTPクライアント/サーバ機能を提供する時刻同期ソフトウエアです。 |
| Simple Network Time Protocol | SNTP | NTPの簡易版プロトコルです。 |
| drop-in configuration | drop-in | 既存設定本体とは別ファイルで追加設定を適用する方式です。 |
| systemctl | - | systemd を使用する Linux システムでサービスやシステムの状態を管理するコマンド。サービスの起動, 停止, 再起動, 状態確認などを行う。 |
| journalctl | - | systemd管理サービスのログ確認コマンドです。 |
| timedatectl | - | Linuxの時刻設定と同期状態を表示, 設定するコマンドです。 |
| chronyc | - | chronyの状態確認と制御を行うコマンドです。 |
| Internet Protocol version 4 | IPv4 | 32 ビットアドレス空間を持つインターネットプロトコル。現在最も広く使用されているバージョン。 |
| Internet Protocol version 6 | IPv6 | 128 ビットアドレス空間を持つ次世代インターネットプロトコル。IPv4 アドレス枯渇問題を解決する。 |

## 前提条件

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- Ansible 2.15 以降, ansibleメタパッケージをディストリビューションから導入していることを想定
- 対象ノードで管理者権限が利用できること。
- `ntp_client_choice`が`chrony`または`systemd-timesyncd`であること。
- `ntp_servers_list`が時刻同期先として妥当な値で定義されていること。

## 実行フロー

ロールは以下の6フェーズで処理します。

1. **Load Params**。
- Debian系では`vars/packages-ubuntu.yml`を読み込みます。
- RHEL系では`vars/packages-rhel.yml`を読み込みます。
- 共通で`vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`を読み込みます。

2. **Package**。
- `ntp_client_packages`をインストールします。

3. **Config**。
- `service_facts`でサービス一覧を取得します。
- `systemd-timesyncd`選択時は`99-timesyncd.conf`を配置し, `systemd-timesyncd`を有効化, `chrony`を無効化します (Debian系かつ対象サービスが存在する場合)。
- `chrony`選択時はdrop-inディレクトリ作成, `chrony.conf`へ`confdir`追記, `99-custom.conf`配置, `chrony`有効化, `systemd-timesyncd`無効化を実施します。

4. **Directory**。
- `/etc/systemd/timesyncd.conf.d`を作成します。

5. **User Group**。
- 現在の実装では有効な処理はありません。

6. **Service**。
- 現在の実装では有効な処理はありません。

## 主要変数

### 基本設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `ntp_servers_list` | `[]` | NTPサーバの候補一覧です。テンプレートで空要素と重複を除去して反映します。 |
| `ntp_client_choice` | `chrony` | 使用するNTPクライアント実装です (`chrony` / `systemd-timesyncd`)。 |
| `ntp_client_is_chrony` | `{{ ntp_client_choice == 'chrony' }}` | `chrony`選択判定です。 |
| `ntp_client_is_systemd_timesyncd` | `{{ ntp_client_choice == 'systemd-timesyncd' }}` | `systemd-timesyncd`選択判定です。 |

### パッケージ/サービス設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `ntp_client_packages_debian` | `{{ ntp_client_is_chrony | ternary(['chrony'], ['systemd-timesyncd']) }}` | Debian系で導入するパッケージ一覧です。 |
| `ntp_client_packages_rhel` | `['chrony']` | RHEL系で導入するパッケージ一覧です。 |
| `ntp_client_packages` | OS依存 | 実際に導入するパッケージ一覧です。 |
| `ntp_client_chrony_service_debian` | `chrony` | Debian系のchronyサービス名です。 |
| `ntp_client_chrony_service_rhel` | `chronyd` | RHEL系のchronyサービス名です。 |
| `ntp_client_chrony_service` | OS依存 | 実際に使用するchronyサービス名です。 |
| `ntp_client_systemd_timesyncd_service` | `systemd-timesyncd` | systemd-timesyncdサービス名です。 |

### 設定ファイルパス

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `ntp_client_systemd_timesyncd_conf_path` | `/etc/systemd/timesyncd.conf.d/99-timesyncd.conf` | systemd-timesyncd設定の出力先です。 |
| `ntp_client_chrony_conf_path_debian` | `/etc/chrony/chrony.conf` | Debian系のchrony本体設定ファイルです。 |
| `ntp_client_chrony_conf_path_rhel` | `/etc/chrony.conf` | RHEL系のchrony本体設定ファイルです。 |
| `ntp_client_chrony_conf_path` | OS依存 | 実際に参照するchrony本体設定ファイルです。 |
| `ntp_client_chrony_conf_drop_in_dir` | OS依存 | chrony drop-inディレクトリです。Debian系は`/etc/chrony/conf.d`, RHEL系は`/etc/chrony.d`です。 |
| `ntp_client_chrony_conf_drop_in_path` | `{{ ntp_client_chrony_conf_drop_in_dir }}/99-custom.conf` | chrony drop-in設定の出力先です。 |

## 主な処理

- `ntp_client_choice`に応じて`chrony`または`systemd-timesyncd`を適用します。
- `ntp_servers_list`の空要素と重複をテンプレートで除去して設定生成します。
- `chrony`選択時は`chrony.conf`へ`confdir`行を追記し, drop-inを読み込む構成に統一します。
- `systemd-timesyncd`選択時は`99-timesyncd.conf`を出力し, `systemd-timesyncd`を有効化します。
- 片方のサービスのみ有効化する相互排他制御を行います。

## テンプレート / 出力ファイル

### 出力ファイル

| テンプレート | 出力先 | 説明 |
| --- | --- | --- |
| `templates/99-timesyncd.conf.j2` | `{{ ntp_client_systemd_timesyncd_conf_path }}` | systemd-timesyncd用のNTPサーバ設定を出力します。 |
| `templates/99-chrony.conf.j2` | `{{ ntp_client_chrony_conf_drop_in_path }}` | chrony用のNTPサーバ設定をdrop-inとして出力します。 |

### テンプレート利用状況

| テンプレート | 利用状況 | 説明 |
| --- | --- | --- |
| `templates/dummy.j2` | 未使用 | 現行タスクでは参照されていません。 |

## ハンドラ

| ハンドラ名 | listen名 | 処理内容 | 呼び出し元 |
| --- | --- | --- | --- |
| Restart_timesyncd | `restart_timesyncd` | `systemd-timesyncd`を再起動し有効化します。 | `tasks/config.yml` |
| Restart_chrony | `restart_chrony` | `{{ ntp_client_chrony_service }}`を再起動し有効化します。 | `tasks/config.yml` |

## OS差異

| 項目 | Debian系 | RHEL系 |
| --- | --- | --- |
| `ntp_client_choice=chrony`時のパッケージ | `chrony` | `chrony` |
| `ntp_client_choice=systemd-timesyncd`時のパッケージ | `systemd-timesyncd` | 該当なし |
| chronyサービス名 | `chrony` | `chronyd` |
| chrony本体設定ファイル | `/etc/chrony/chrony.conf` | `/etc/chrony.conf` |
| chrony drop-inディレクトリ | `/etc/chrony/conf.d` | `/etc/chrony.d` |
| systemd-timesyncd利用 | 利用可 | 通常利用しない |

## 実行方法

### Makefileを使用した実行

```bash
cd /path/to/ubuntu-setup/ansible
make run_ntp_client
```

### 直接 ansible-playbook で実行

```bash
# basic.yml をタグ指定で実行
ansible-playbook -i inventory/hosts basic.yml --tags "ntp-client"

# site.yml をタグ指定で実行
ansible-playbook -i inventory/hosts site.yml --tags "ntp-client"

# 対象ホストを限定して実行
ansible-playbook -i inventory/hosts site.yml --tags "ntp-client" -l <対象ホスト>
```

`devel.yml`, `k8s-ctrl-plane.yml`, `k8s-worker.yml`, `rancher.yml` でも同じ `--tags "ntp-client"` で再利用できます。

## 検証

### 前提条件確認

- ロール実行が正常終了していること。
- NTPクライアントノードへログイン可能であること。
- `ntp_client_choice`の設定値を把握していること。

### 検証ステップ

#### Step 1: 有効化サービスの相互排他確認

**実施ノード**: NTPクライアントノード

**コマンド**:
```bash
systemctl is-enabled systemd-timesyncd || true
systemctl is-enabled chrony || true
systemctl is-enabled chronyd || true
```

**期待される出力例**:
```plaintext
# chrony選択時の例
not-found
enabled
alias

# systemd-timesyncd選択時の例
enabled
disabled
alias

# RHEL系(chronyd)の例
not-found
disabled
enabled
```

**確認ポイント**:
- `ntp_client_choice`に対応するサービスだけが`enabled`であること。
- 非選択側サービスが`enabled`になっていないこと。

#### Step 2: 設定ファイル反映確認

**実施ノード**: NTPクライアントノード

**コマンド**:
```bash
# systemd-timesyncd選択時
sudo grep -E '^NTP=' /etc/systemd/timesyncd.conf.d/99-timesyncd.conf

# chrony選択時(Debian系)
sudo grep -E '^confdir[[:space:]]+/etc/chrony/conf.d' /etc/chrony/chrony.conf
sudo grep -E '^server ' /etc/chrony/conf.d/99-custom.conf

# chrony選択時(RHEL系)
sudo grep -E '^confdir[[:space:]]+/etc/chrony.d' /etc/chrony.conf
sudo grep -E '^server ' /etc/chrony.d/99-custom.conf
```

**期待される出力例**:
```plaintext
# systemd-timesyncd選択時の例
NTP=192.168.20.11 ntp.nict.jp

# chrony選択時(Debian系)の例
confdir /etc/chrony/conf.d
server 192.168.20.11 iburst
server ntp.nict.jp iburst
```

**確認ポイント**:
- 設定ファイルが作成されていること。
- `ntp_servers_list`が空要素/重複を除去した形で反映されていること。
- chrony選択時に`confdir`行が存在すること。
- テンプレート先頭コメントの`last update`が直近実行時刻になっていること。

#### Step 3: 同期状態確認

**実施ノード**: NTPクライアントノード

**コマンド**:
```bash
# systemd-timesyncd選択時
timedatectl show-timesync --all

# chrony選択時
chronyc tracking
chronyc sources -v
```

**期待される出力例**:
```plaintext
# chrony選択時の例 (chronyc tracking)
Reference ID    : 85F3EEF4 (ntp-a3.nict.go.jp)
Stratum         : 2
System time     : 0.000020180 seconds fast of NTP time
Leap status     : Normal

# chrony選択時の例 (chronyc sources -v)
^+ 192.168.20.11                 2   8   377    16   -211us[ -211us] +/- 3668us
^* ntp-a3.nict.go.jp             1   9   377   184   -281us[ -296us] +/- 2773us

# systemd-timesyncd選択時の例 (timedatectl show-timesync --all)
ServerName=ntp.ubuntu.com
ServerAddress=185.125.190.57
PollIntervalUSec=32s
```

**確認ポイント**:
- `timedatectl`または`chronyc`で同期先情報が取得できること。
- `ntp_servers_list`に含まれるサーバが参照候補として表示されること。

#### Step 4: ログ確認

**実施ノード**: NTPクライアントノード

**コマンド**:
```bash
# systemd-timesyncd選択時
journalctl -u systemd-timesyncd -n 50 --no-pager

# chrony選択時
journalctl -u chrony -n 50 --no-pager || true
journalctl -u chronyd -n 50 --no-pager || true
```

**期待される出力例**:
```plaintext
# systemd-timesyncd選択時の例
3月 02 03:09:29 vmlinux3 systemd[1]: Started systemd-timesyncd.service - Network Time Synchronization.
3月 02 03:10:30 vmlinux3 systemd-timesyncd[700]: Contacted time server 185.125.190.58:123 (ntp.ubuntu.com).

# chrony選択時の例
3月 03 04:11:43 vmlinux3 systemd[1]: Started chrony.service - chrony, an NTP client/server.
3月 03 04:12:57 vmlinux3 chronyd[1049]: Selected source 133.243.238.244 (ntp.nict.jp)
```

**確認ポイント**:
- 直近ログに致命的な設定エラーがないこと。
- 選択したサービスが起動済みであること。

## 補足

- `ntp_client_choice`を切り替えることで, `chrony`と`systemd-timesyncd`のどちらにも移行できます。
- 追加のchrony設定 (例: `makestep`や`allow`) は `templates/99-chrony.conf.j2` の編集, または上位ロールからの追加drop-in投入で拡張できます。
- NTPサーバ候補はIPv4/IPv6混在で指定できます。
- 大規模環境で上位NTPへのアクセス制御が必要な場合は, ファイアウォール設定との組み合わせを検討してください。

## 参考リンク

- [chrony project](https://chrony-project.org/)
- [systemd-timesyncd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd-timesyncd.service.html)
- [NTP Pool Project](https://www.pool.ntp.org/)
