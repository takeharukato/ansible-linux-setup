# ntp-server ロール

このロールは, chrony を用いた NTP サーバを構成するロールです。外部上位サーバとの同期, LAN 内クライアントへの時刻配信, ならびにアクセス制御を実施します。`ansible_facts.os_family` により Debian 系と RHEL 系の差異を吸収します。

## 概要

### 構成要素

このロールは以下を構成します。

1. chrony パッケージの導入。
- `ntp_server_packages` を導入します。

2. chrony drop-in ディレクトリの作成。
- `ntp_server_chrony_conf_drop_in_dir` を作成します。

3. NTP サーバ設定の反映。
- `99-ntp-servers.conf.j2` から `99-ntp-servers.conf` を生成します。
- `external_ntp_servers_list` から `pool ... iburst` を生成します。
- `ntp_allow` を `allow` ディレクティブへ反映します。

4. chrony サービスの反映。
- 設定変更時に `restart_chrony` ハンドラでサービスを再起動, 有効化します。

### 実装の流れ

ロール実行時には以下の順で処理します。

1. 変数読み込み (`load-params.yml`)。
2. パッケージ導入 (`package.yml`)。
3. ディレクトリ作成 (`directory.yml`)。
4. ユーザ/グループ処理 (`user_group.yml`, 現状は空実装)。
5. サービス処理 (`service.yml`, 現状は空実装)。
6. 設定反映 (`config.yml`)。

### ディレクトリ構成

主要な設定対象は以下です。

```plaintext
/etc/chrony/conf.d/99-ntp-servers.conf (Debian系)
/etc/chrony.d/99-ntp-servers.conf (RHEL系)
```

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Network Time Protocol | NTP | 時刻同期の仕組み。 |
| Classless Inter-Domain Routing | CIDR | IP アドレスとネットワークプレフィックス長を組み合わせた表記法 (例: 192.168.1.0/24)。柔軟なネットワーク分割を可能にする。 |
| Local Area Network | LAN | 限られた地理的範囲内 (建物内や敷地内) でコンピュータやデバイスを接続するネットワーク。高速で低遅延な通信が可能。 |
| Graphical User Interface | GUI | 画面操作中心の利用形態です。 |
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
| chrony | - | NTP クライアント・サーバとして動作する高精度な時刻同期ソフトウェア。ntpd の代替として広く使用され, 間欠的なネットワーク接続環境でも高い精度を維持できる。 |
| drop-in configuration | drop-in | 既存設定本体とは別ファイルで追加設定を適用する方式です。 |
| iburst | - | NTP 初期同期を高速化する chrony のオプションです。 |
| pool directive | pool | chrony で上位 NTP サーバ群を指定する設定行です。 |
| allow directive | allow | chrony でクライアントアクセスを許可するネットワーク範囲指定です。 |
| multi-user target | multi-user.target | GUIを使わないサーバ向けのsystemd起動状態です。 |
| localhost loopback address | 127.0.0.1/32 | 同一ホスト内通信だけを許可する IPv4 ループバック CIDR です。 |
| systemctl | - | systemd を使用する Linux システムでサービスやシステムの状態を管理するコマンド。サービスの起動, 停止, 再起動, 状態確認などを行う。 |
| journalctl | - | systemd管理サービスのログ確認コマンドです。 |
| chronyc | - | chronyの状態確認と制御を行うコマンドです。 |

## 前提条件

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- Ansible 2.15 以降, ansibleメタパッケージをディストリビューションから導入していることを想定
- 対象ノードで管理者権限が利用できること。
- `external_ntp_servers_list` が上位 NTP サーバとして妥当な値で定義されていること。
- `network_ipv4_network_address` および `network_ipv4_prefix_len` を利用する場合は, 適切な値が設定されていること。

## 実行フロー

ロールは以下の6フェーズで処理します。

1. **Load Params**。
- Debian系では `vars/packages-ubuntu.yml` を読み込みます。
- RHEL系では `vars/packages-rhel.yml` を読み込みます。
- 共通で `vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml` を読み込みます。

2. **Package**。
- `ntp_server_packages` を導入します。
- 変更があれば `disable_gui` を通知します。

3. **Directory**。
- `ntp_server_chrony_conf_drop_in_dir` を作成します。

4. **User Group**。
- 現在の実装では有効な処理はありません。

5. **Service**。
- 現在の実装では有効な処理はありません。

6. **Config**。
- `99-ntp-servers.conf` を配置します。
- 変更があれば `restart_chrony` を通知します。

## 主要変数

### 基本設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `external_ntp_servers_list` | `[]` | 上位 NTP サーバ一覧です。空要素, 空文字, 重複はテンプレートで除去されます。 |
| `network_ipv4_network_address` | `""` | 許可対象ネットワークの IPv4 アドレスです。 |
| `network_ipv4_prefix_len` | `0` | 許可対象ネットワークのプレフィックス長です。 |
| `ntp_allow` | 条件式 | `network_ipv4_network_address` と `network_ipv4_prefix_len` が有効な場合は `<address>/<prefix>` を使用します。未設定, 空文字, 0 の場合は `127.0.0.1/32` を使用します。 |

### サービス/パス設定

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `ntp_server_service_debian` | `chrony` | Debian系の chrony サービス名です。 |
| `ntp_server_service_rhel` | `chronyd` | RHEL系の chrony サービス名です。 |
| `ntp_server_chrony_service` | OS依存 | 実際に使用する chrony サービス名です。 |
| `ntp_server_chrony_conf_drop_in_dir` | OS依存 | 設定ファイル配置先です。Debian系は `/etc/chrony/conf.d`, RHEL系は `/etc/chrony.d` です。 |
| `ntp_server_packages` | OS依存 | インストール対象パッケージ一覧です。Debian系, RHEL系ともに `chrony` です。 |

## 主な処理

- `external_ntp_servers_list` から `pool ... iburst` 行を生成します。
- `ntp_allow` を `allow` 行として反映します。
- `ntp_allow` が未定義または空文字列の場合, テンプレート側で `127.0.0.1/32` へフォールバックします。
- 設定変更時は `restart_chrony` ハンドラでサービスを再起動, 有効化します。
- `external_ntp_servers_list` が空の場合は `pool` 行は生成されません。

## テンプレート / 出力ファイル

### 出力ファイル

| テンプレート | 出力先 | 説明 |
| --- | --- | --- |
| `templates/99-ntp-servers.conf.j2` | `{{ ntp_server_chrony_conf_drop_in_dir }}/99-ntp-servers.conf` | `pool ... iburst` と `allow` を含む NTP サーバ設定を出力します。 |

### テンプレート利用状況

| テンプレート | 利用状況 | 説明 |
| --- | --- | --- |
| `templates/99-ntp-servers.conf.j2` | 使用中 | 現行タスクで参照されています。 |

## ハンドラ

| ハンドラ名 | listen名 | 処理内容 | 呼び出し元 |
| --- | --- | --- | --- |
| Restart_chrony | `restart_chrony` | `{{ ntp_server_chrony_service }}` を再起動し, 有効化します。 | `tasks/config.yml` |

## OS差異

| 項目 | Debian系 | RHEL系 |
| --- | --- | --- |
| chrony サービス名 | `chrony` | `chronyd` |
| drop-in ディレクトリ | `/etc/chrony/conf.d` | `/etc/chrony.d` |
| NTP サーバパッケージ | `chrony` | `chrony` |

## 実行方法

### Makefileを使用した実行

```bash
cd /path/to/ubuntu-setup/ansible
make run_ntp_server
```

### 直接 ansible-playbook で実行

```bash
# server.yml をタグ指定で実行
ansible-playbook -i inventory/hosts server.yml --tags "ntp-server"

# site.yml をタグ指定で実行
ansible-playbook -i inventory/hosts site.yml --tags "ntp-server"

# 対象ホストを限定して実行
ansible-playbook -i inventory/hosts site.yml --tags "ntp-server" -l <対象ホスト>
```

chrony 再起動が発生するため, メンテナンス時間内での実行を推奨します。

## 検証

### 前提条件確認

- ロール実行が正常終了していること。
- NTPサーバノードへログイン可能であること。
- クライアント検証を行う場合は, NTPクライアントノードからNTPサーバノードへ到達可能であること。

### 検証ステップ

#### Step 1: chrony サービス状態確認

**実施ノード**: NTPサーバノード

**コマンド**:
```bash
sudo systemctl is-active chrony || true
sudo systemctl is-enabled chrony || true
sudo systemctl is-active chronyd || true
sudo systemctl is-enabled chronyd || true
```

**期待される出力例**:
```plaintext
# Debian系の例
active
enabled

# RHEL系の例
inactive
disabled
active
enabled
```

**出力解釈**:
- `systemctl is-active` が `active` を返す: chrony サービスが起動状態であること。
- `systemctl is-enabled` が `enabled` を返す: chrony サービスが始動時に自動起動するよう設定されていること。

**確認ポイント**:
- Debian系では `chrony` サービスが `active` かつ `enabled` であること。
- RHEL系では `chronyd` サービスが `active` かつ `enabled` であること。
- いずれかが `inactive` または `disabled` の場合は, ロール実行に失敗しているか, サービスが手動で停止されている可能性があります。

#### Step 2: 設定ファイル反映確認

**実施ノード**: NTPサーバノード

**コマンド**:
```bash
# Debian系
sudo grep -E '^(pool|allow) ' /etc/chrony/conf.d/99-ntp-servers.conf

# RHEL系
sudo grep -E '^(pool|allow) ' /etc/chrony.d/99-ntp-servers.conf
```

**期待される出力例**:
```plaintext
pool ntp.nict.jp iburst
pool jp.pool.ntp.org iburst
pool ntp.jst.mfeed.ad.jp iburst
pool ntp.ring.gr.jp iburst
pool time.google.com iburst
pool time.aws.com iburst
pool ats1.e-timing.ne.jp iburst
pool s2csntp.miz.nao.ac.jp iburst
allow 192.168.20.0/24
```

**出力解釈**:
- `pool ... iburst` 行: `external_ntp_servers_list` で定義された上位NTPサーバが `pool` ディレクティブで登録されていることを示します。各行の最後に `iburst` が付加されている点に注意してください。これによりNTP初期同期が高速化されます。
- `allow` 行: `ntp_allow` 変数で指定されたネットワーク範囲からのクライアント接続を許可する設定です。この例では `192.168.20.0/24` が許可対象ネットワークです。

**確認ポイント**:
- `pool ... iburst` 行の数が `external_ntp_servers_list` の要素数と一致していること (空要素は除去されるため, テンプレート内で `reject or default('') != ''` で判定)。
- `allow` 行が存在し, ネットワークアドレスとプレフィックス長が CIDR 形式で記載されていること。
- `network_ipv4_network_address` または `network_ipv4_prefix_len` が未設定の場合は, `allow 127.0.0.1/32` になっていることを確認。
- ファイルが存在しない場合は, ロール実行が失敗したか, テンプレート配置タスクが実行されていない可能性があります。

#### Step 3: 上位 NTP サーバ同期状態確認

**実施ノード**: NTPサーバノード

**コマンド**:
```bash
chronyc sources -v
```

**期待される出力例**:
```plaintext
MS Name/IP address         Stratum Poll Reach LastRx Last sample
===============================================================================
^+ ntp-b2.nict.go.jp             1   9   377   263   -694us[ -694us] +/- 3067us
^+ ntp-k1.nict.jp                1  10   377   143   -484us[ -484us] +/- 7513us
^+ ntp-b3.nict.go.jp             1  10   377   980   -391us[ -391us] +/- 2984us
^* ntp-a2.nict.go.jp             1  10   377   997   -222us[ -392us] +/- 2821us
...
```

**出力解釈**:
- 各行の先頭の記号:
  - `^*`: 現在同期している最良のソース。
  - `^+`: 同期候補で精度が良い複合ソース。
  - `^-`: 同期候補だが精度が低いもの。
  - `^?`: 到達不可能または未検証のソース。
- `Stratum`: NTP階層番号。1が最高精度 (GPS等)。
- `Last sample`: 最測定値 (正の値は遅延, 負の値は進んでいることを示す)。
- 括弧内の値 `[-392us]`: 調整後のオフセット。
- `+/- 2821us`: 推定誤差範囲。

**確認ポイント**:
- `^*` または `^+` の行が存在すること (同期中のソースがあること)。
- 少なくとも3個以上のソースと通信できていること (複数ソース選択によって精度が向上)。
- `Last sample` が秒単位 (ms 以下) に収まっていること。
- `Reach` の値が377 (8進数) であること。これは直近8回の送信で全て到達したことを示します。
- `^?` のみでは同期していないため, 設定またはネットワーク接続を確認。

#### Step 4: NTP サーバ統計情報確認

**実施ノード**: NTPサーバノード

**コマンド**:
```bash
chronyc sourcestats
```

**期待される出力例**:
```plaintext
Name/IP Address            NP  NR  Span  Frequency  Freq Skew  Offset  Std Dev
==============================================================================
ntp-b2.nict.go.jp           6   5   42m     -0.211      0.409   -512us    93us
ntp-k1.nict.jp             21  10  344m     -0.073      0.059   -708us   419us
ntp-b3.nict.go.jp          14   8  138m     +0.061      0.088    +14us   192us
ntp-a2.nict.go.jp           6   3   86m     -0.012      0.423    +36us   186us
...
```

**出力解釈**:
- `NP`: サンプル数 (measurements processed)。
- `NR`: 実際に使用されたサンプル数 (still in use)。
- `Span`: 観測期間 (例: `344m` は344分)。
- `Frequency`: 時刻周波数の偏差 (ppm)。理想は 0。
- `Freq Skew`: 周波数偏差の推定誤差。小さいほど信頼性が高い。
- `Offset`: 平均時刻オフセット (例: `-512us` は512マイクロ秒遅れている)。
- `Std Dev`: 標準偏差 (ノイズレベル, 小さいほど安定)。

**確認ポイント**:
- 複数のサーバに対して統計情報があること。
- `Offset` が ±1ms 程度に収まっていること。
- `Std Dev` が ±1000us (1ms) 以下であること。
- 有効な `NR` (still in use) が1以上であること。
- `Freq Skew` が 2000 未満であること (2000は未検証ソース)。

#### Step 5: サービスログ確認

**実施ノード**: NTPサーバノード

**コマンド**:
```bash
sudo journalctl -u chrony -n 30 --no-pager || true
sudo journalctl -u chronyd -n 30 --no-pager || true
```

**期待される出力例**:
```plaintext
2月 23 18:26:24 mgmt-server systemd[1]: Starting chrony.service - chrony, an NTP client/server...
2月 23 18:26:24 mgmt-server chronyd[1061]: chronyd version 4.5 starting ...
2月 23 18:26:24 mgmt-server chronyd[1061]: Loaded 0 symmetric keys
2月 23 18:26:24 mgmt-server chronyd[1061]: Frequency -0.411 +/- 0.026 ppm read from /var/lib/chrony/chrony.drift
2月 23 18:26:24 mgmt-server chronyd[1061]: Using right/UTC timezone to obtain leap second data
2月 23 18:26:24 mgmt-server chronyd[1061]: Loaded seccomp filter (level 1)
2月 23 18:26:24 mgmt-server systemd[1]: Started chrony.service - chrony, an NTP client/server.
2月 23 18:26:45 mgmt-server chronyd[1061]: Selected source 133.243.238.163 (ntp.nict.jp)
2月 23 18:26:45 mgmt-server chronyd[1061]: System clock TAI offset set to 37 seconds
2月 23 23:21:35 mgmt-server chronyd[1061]: Selected source 133.243.238.243 (ntp.nict.jp)
```

**出力解釈**:
- `chronyd version X.X starting`: chrony デーモン起動ログ。バージョン情報と起動時刻が表示されます。
- `Frequency ... ppm`: 前回実行時に測定された周波数オフセット。`/var/lib/chrony/chrony.drift` から読み込まれます。
- `Using right/UTC timezone`: TAI (国際原子時) オフセット情報の読み込み。
- `Loaded seccomp filter`: セキュリティサンドボックス有効化。
- `Starting ... Started`: systemd による起動・停止の通知ログ。
- `Selected source IP (hostname)`: 同期対象として選択されたNTPサーバ。
- `System clock TAI offset set to 37 seconds`: TAI オフセット更新。

**確認ポイント**:
- `Starting ... Started` でサービス起動に成功していること。
- `Selected source ... (hostname)` が表示されていること (NTPサーバが同步に成功しつつあることを示す)。
- `Error`, `Failed`, `denied` など致命的なエラーメッセージが無いこと。
- `Configuration error` や `parse error` が無いこと。設定ファイルの文法エラーがあればここに出力されます。
- RHEL系の場合は `chronyd` プロセスのログが出力されること。Debian系の場合は `chrony` へのプロキシメッセージが出力されることもあります。

## 補足

- `external_ntp_servers_list` が空の場合, テンプレート内ループはスキップされます。
- `allow` で指定する範囲は最小限にしてください。
- IPv6 のアクセス制御を併用する場合は, 別途設定追加が必要です。
- `disable_gui` 通知が不要な環境では, 上位ロール側で制御する運用を検討してください。
- chrony の同期挙動チューニングが必要な場合は, `makestep` などを追加する拡張方針を検討してください。

## 参考リンク

- [chrony project](https://chrony-project.org/)
- [chrony.conf manual](https://chrony-project.org/doc/4.5/chrony.conf.html)
- [NTP Pool Project](https://www.pool.ntp.org/)
