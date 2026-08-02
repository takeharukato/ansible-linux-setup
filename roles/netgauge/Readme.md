# Netgauge関連

本ロールは, Netgaugeをビルドして配置し, OSノイズ計測用スクリプトを導入するためのロールです。

## 目次

- [Netgauge関連](#netgauge関連)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
    - [構成要素](#構成要素)
    - [主な処理内容](#主な処理内容)
    - [ロール実行後の対象ホスト上でのファイル配置](#ロール実行後の対象ホスト上でのファイル配置)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
    - [Makefile を使用した実行](#makefile-を使用した実行)
    - [直接 ansible-playbook で実行](#直接-ansible-playbook-で実行)
  - [主要変数](#主要変数)
    - [ビルド関連](#ビルド関連)
    - [配置先関連](#配置先関連)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
    - [OS差異](#os差異)
  - [検証ポイント](#検証ポイント)
    - [前提条件確認](#前提条件確認)
    - [検証ステップ](#検証ステップ)
      - [Step 1: Netgaugeバイナリ配置確認](#step-1-netgaugeバイナリ配置確認)
      - [Step 2: 計測スクリプト配置確認](#step-2-計測スクリプト配置確認)
      - [Step 3: CPU検出スクリプト実行確認](#step-3-cpu検出スクリプト実行確認)
      - [Step 4: cgroup準備スクリプト実行確認](#step-4-cgroup準備スクリプト実行確認)
      - [Step 5: 計測一括スクリプト実行確認](#step-5-計測一括スクリプト実行確認)
      - [Step 6: 生成物確認](#step-6-生成物確認)
      - [Step 7: FFT描画確認(任意)](#step-7-fft描画確認任意)
  - [トラブルシューティング](#トラブルシューティング)
  - [注意事項](#注意事項)
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
| Internet Protocol | IP | インターネットプロトコルの略称。 |
| Structured Query Language | SQL | データベースを操作するための記述言語。 |
| Hypertext Transfer Protocol | HTTP | WWW で情報をやり取りする通信手順。 |
| Hypertext Transfer Protocol Secure | HTTPS | 通信内容を暗号化して WWW 通信を行う方式。 |
| RPM Package Manager | RPM | RHEL 系で使用するパッケージ形式。 |
| Virtual Machine | VM | 物理機器上で動作する仮想的な計算機。 |
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
| Application Programming Interface | API | アプリケーション同士がやり取りする方法を定めた仕様。 |
| Uniform Resource Locator | URL | WWW 上の資源の場所を示す文字列。 |
| Netgauge | Netgauge | Zurich工科大学が公開するネットワーク性能とOSノイズの計測ツールです。 |
| Message Passing Interface | MPI | 並列処理でプロセス間通信を行うための規約です。 |
| Transmission Control Protocol | TCP | 通信相手との接続を確立してからデータを送受信する通信方式。 |
| User Datagram Protocol | UDP | 接続確立を行わずにデータを送受信する通信方式。 |
| Raw Ethernet | RAW Ethernet | IP層を使わずにEthernetフレームを扱う通信方式です。 |
| InfiniBand | InfiniBand | 高帯域, 低遅延向けのネットワーク技術です。 |
| LogP model | LogP | 通信オーバーヘッドや遅延を表現する性能モデルです。 |
| LogGP model | LogGP | LogPを拡張した性能モデルです。 |
| Fixed Work Quantum | FWQ | 固定作業量でノイズ影響を測る手法です。 |
| Fixed Time Quantum | FTQ | 固定時間で処理量の変動を測る手法です。 |
| Selfish Detour | Selfish Detour | OSノイズ観測で使う計測パターンの1つです。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Red Hat Enterprise Linux | RHEL | Red Hat 社が提供する商用 Linux ディストリビューション。 |
| Central Processing Unit | CPU | 計算処理を実行する中核部品。 |
| Housekeeping/Application core split | HK/APP | CPUを管理処理用と計測処理用に分ける考え方です。 |
| control group | cgroup | Linuxでプロセス資源を制御する仕組みです。 |
| CPU set | cpuset | CPU割り当てを制御するcgroup機能です。 |
| Non-Uniform Memory Access | NUMA | CPUとメモリの距離でアクセス遅延が変わる構成です。 |
| Quantum | Quantum | FWQ/FTQで使う処理量または時間量の単位です。 |
| Fast Fourier Transform | FFT | 時系列データを周波数成分へ変換する手法です。 |
| Power Spectral Density | PSD | 周波数ごとの強度分布を示す指標です。 |
| Histogram | Histogram | 値の分布を棒で可視化した図です。 |
| jitter | ジッタ | 実行時間の揺らぎです。 |
| frequency scaling | 周波数スケーリング | CPUクロックを動的に変える機能です。 |
| GNU Make | gmake | ビルド手順を実行するツールです。 |
| Python 3 | Python | スクリプト実行言語です。 |
| gnuplot | gnuplot | グラフ描画ツールです。 |
| Internet Protocol | IP | ネットワーク上で宛先を識別し, データを届けるための通信手順。 |
| matplotlib | matplotlib | Python向けのグラフ描画ライブラリです。 |
| NumPy | numpy | Python向けの数値計算ライブラリです。 |
| Yet Another Markup Language | YAML | 設定ファイル形式です。 |
| Uniform Resource Locator | URL | URL の正式名称。 |
| Portable Network Graphics | PNG | 可逆圧縮形式の画像ファイルです。 |
| Ansible Playbook | playbook | 自動化処理の実行手順を順序付きで記述したファイル。 |
| role | role | 特定の名前空間内で有効な権限の集合。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| template | template | 変数展開して出力する雛形ファイルです。 |
| handler | handler | 通知時に実行する再処理です。 |
| tag | tag | Ansibleで実行対象を絞るラベルです。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `cat` | - | ファイル内容を標準出力へ表示するコマンド。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| `make` | - | Makefile に定義された処理を実行するコマンド。 |
| `python3` | - | Python 3 系インタプリタを実行するコマンド。 |
| サービス | - | 機能を利用者や他システムへ提供する仕組み。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |

## 概要
このロールは, Netgaugeをビルドして配置し, OSノイズ計測用スクリプトを導入するためのロールです。Netgauge本体のビルドはAnsibleの制御ノード(localhost)で実行し, 生成したバイナリを対象ノードへ配置します。

### 構成要素

このロールは以下の2系統を構成します。

1. Netgauge本体の配置。
- `netgauge`バイナリを`/opt/netgauge/bin`へ配置します。
- Netgaugeは`MPI`, `TCP`, `UDP`, `RAW Ethernet`, `InfiniBand`などの通信方式を対象に, レイテンシや帯域, `LogP`/`LogGP`関連の計測を実行できます。

2. OSノイズ計測スクリプト群の配置。
- `00_detect_cpus.sh`から`90_get_app_cpu_noise.sh`までのスクリプトを配置します。
- `FWQ`, `FTQ`, `Selfish Detour`を利用したOSノイズ計測を実行できます。
- 実行結果は`runs/<測定時刻>/`配下に保存され, ヒストグラム画像を生成できます。

### 主な処理内容

- Netgaugeソースをダウンロードしてビルドします。
- ビルド済みバイナリを対象ノードへ配置します。
- 計測実行をまとめた`90_get_app_cpu_noise.sh`を配置します。
- `00_detect_cpus.sh`で`HK/APP`分割を計算します。
- `10_prepare_cgroup.sh`で`cgroup`と`cpuset`を設定します。
- `25_flatten_values.sh`で値を整形し, `30_plot_all.sh`でヒストグラム画像を生成します。
- `60_fft_plot.py`で`FFT`と`PSD`の可視化を実行できます。


### ロール実行後の対象ホスト上でのファイル配置

ロール実行後, 既定では対象ホストに以下のディレクトリ構成でファイルを配置します:

```plaintext
/opt/netgauge/
  `- bin/
      |- netgauge
      |- 00_detect_cpus.sh
      |- 10_prepare_cgroup.sh
      |- 20_launch_netgauge.sh
      |- 25_flatten_values.sh
      |- 30_plot_all.sh
      |- 50_cpu_list.py
      |- 60_fft_plot.py
      |- 90_get_app_cpu_noise.sh
      `- plot_hist.gp
```

## 前提条件

- 対象OSはDebian系またはRHEL系です。
- Ansibleが利用可能である必要があります。
- 制御ノードで以下のツールが利用可能である必要があります。
  - `curl`
  - `tar`
  - `gmake`
  - `sudo`
- 対象ノードへ`become`で書き込み可能である必要があります。
- `netgauge_version`を`group_vars`または`host_vars`で定義する必要があります。
- 計測結果の描画に`60_fft_plot.py`を使用する場合は, Python環境に`matplotlib`と`numpy`が必要です。

## 実行方法

### Makefile を使用した実行

```bash
cd /path/to/ubuntu-setup/ansible
make run_netgauge
```

### 直接 ansible-playbook で実行

```bash
# site.yml をタグ指定で実行
ansible-playbook -i inventory/hosts site.yml --tags "netgauge"

# 特定ホストのみ対象
ansible-playbook -i inventory/hosts site.yml --tags "netgauge" -l <対象ホスト>

# netgaugeロール関連タグのみ対象
ansible-playbook -i inventory/hosts site.yml --tags "netgauge"
```

## 主要変数

### ビルド関連

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `netgauge_version` | 未定義 | Netgaugeバージョンです。必須です。 |
| `netgauge_basename` | `netgauge-{{ netgauge_version }}` | 展開ディレクトリ名です。 |
| `netgauge_archive` | `{{ netgauge_basename }}.tar.gz` | ダウンロードアーカイブ名です。 |
| `netgauge_URL` | `https://htor.inf.ethz.ch/research/netgauge/{{ netgauge_archive }}` | アーカイブ取得元URLです。 |
| `netgauge_configure` | `--with-mpi=no --prefix={{ netgauge_dir }}` | configureオプションです。 |
| `netgauge_build_dest` | `/tmp/netgauge` | 制御ノードでのインストール先です。 |

### 配置先関連

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `netgauge_dir` | `/opt/netgauge` | 対象ノードの配置先ディレクトリです。 |

## テンプレートと生成ファイル

本ロールでは以下のテンプレート / ファイルを出力します:
主な展開先ホストは, 対象ホスト(既定) です。

| テンプレート名 | 出力先ファイル(既定値) | 説明 |
| --- | --- | --- |
| `00_detect_cpus.sh.j2` | `/opt/netgauge/bin/00_detect_cpus.sh` | CPU範囲を検出し, `.cpu_env`を生成します。 |
| `10_prepare_cgroup.sh.j2` | `/opt/netgauge/bin/10_prepare_cgroup.sh` | `netgauge-app`用`cgroup`を作成します。 |
| `20_launch_netgauge.sh.j2` | `/opt/netgauge/bin/20_launch_netgauge.sh` | Netgauge実行本体です。 |
| `25_flatten_values.sh.j2` | `/opt/netgauge/bin/25_flatten_values.sh` | 出力値を集約して`rank*.val`を生成します。 |
| `30_plot_all.sh.j2` | `/opt/netgauge/bin/30_plot_all.sh` | `gnuplot`でヒストグラム画像を生成します。 |
| `50_cpu_list.py.j2` | `/opt/netgauge/bin/50_cpu_list.py` | `APP_RANGE`をCPU番号列へ展開します。 |
| `60_fft_plot.py.j2` | `/opt/netgauge/bin/60_fft_plot.py` | `FFT`と`PSD`の画像を生成します。 |
| `90_get_app_cpu_noise.sh.j2` | `/opt/netgauge/bin/90_get_app_cpu_noise.sh` | 計測処理全体を順次実行します。 |
| `plot_hist.gp` | `/opt/netgauge/bin/plot_hist.gp` | ヒストグラム描画用`gnuplot`スクリプトです。 |

## 実行フロー

ロール実行時は以下の順序で処理します。

1. パラメータ読み込み (`load-params.yml`)。
2. Netgaugeのビルドと配置 (`build.yml`)。
3. 予約済みタスク群の実行 (`package.yml`, `directory.yml`, `user_group.yml`, `service.yml`, `config.yml`)。
4. 計測スクリプト群の配置 (`tools.yml`)。

### OS差異

| 項目 | Debian系 | RHEL系 |
| --- | --- | --- |
| 変数ファイル読込 | `vars/packages-ubuntu.yml`を読込 | `vars/packages-rhel.yml`を読込 |
| Build処理 | 共通 | 共通 |
| Tools処理 | 共通 | 共通 |
| Package処理 | 予約タスク(実質未実装) | 予約タスク(実質未実装) |

## 検証ポイント

実行者は以下の検証コマンドを実行し, 構文検査が成功することを確認します。

```bash
ansible-playbook -i inventory/hosts site.yml --syntax-check
```

期待結果: エラーが出力されず, syntax check が成功します。

### 前提条件確認

- ロール実行が成功していること。
- 対象ノードへシェルログインできること。
- `sudo`が利用可能であること。

### 検証ステップ

#### Step 1: Netgaugeバイナリ配置確認

**実施ノード**: Netgauge導入対象ノード

**コマンド**:
```bash
ls -l /opt/netgauge/bin/netgauge
```

**期待される出力例**:
```plaintext
-rwxr-xr-x 1 root root 123456 ... /opt/netgauge/bin/netgauge
```

**確認ポイント**:
- `netgauge`が存在すること。
- 実行権限が付与されていること。

#### Step 2: 計測スクリプト配置確認

**実施ノード**: Netgauge導入対象ノード

**コマンド**:
```bash
ls -1 /opt/netgauge/bin/00_detect_cpus.sh \
      /opt/netgauge/bin/10_prepare_cgroup.sh \
      /opt/netgauge/bin/20_launch_netgauge.sh \
      /opt/netgauge/bin/25_flatten_values.sh \
      /opt/netgauge/bin/30_plot_all.sh \
      /opt/netgauge/bin/50_cpu_list.py \
      /opt/netgauge/bin/60_fft_plot.py \
      /opt/netgauge/bin/90_get_app_cpu_noise.sh \
      /opt/netgauge/bin/plot_hist.gp
```

**期待される出力例**:
```plaintext
/opt/netgauge/bin/00_detect_cpus.sh
/opt/netgauge/bin/10_prepare_cgroup.sh
...
/opt/netgauge/bin/plot_hist.gp
```

**確認ポイント**:
- 9ファイル全てが存在すること。

#### Step 3: CPU検出スクリプト実行確認

**実施ノード**: Netgauge導入対象ノード

**コマンド**:
```bash
cd /opt/netgauge/bin
./00_detect_cpus.sh
cat .cpu_env
```

**期待される出力例**:
```plaintext
HK_RANGE=0-1
PRESENT=0-15
APP_RANGE=2-15
APP_N=14
[OK] .cpu_env を作成しました。
```

**確認ポイント**:
- `.cpu_env`が生成されること。
- `APP_RANGE`と`APP_N`が空でないこと。

#### Step 4: cgroup準備スクリプト実行確認

**実施ノード**: Netgauge導入対象ノード

**コマンド**:
```bash
cd /opt/netgauge/bin
sudo ./10_prepare_cgroup.sh
```

**期待される出力例**:
```plaintext
[OK] kubepods.slice/netgauge-app を cpuset.cpus=... で用意しました。
```

**確認ポイント**:
- エラー終了しないこと。
- `cpuset.cpus`設定完了メッセージが表示されること。

#### Step 5: 計測一括スクリプト実行確認

**実施ノード**: Netgauge導入対象ノード

**コマンド**:
```bash
cd /tmp
/opt/netgauge/bin/90_get_app_cpu_noise.sh
```

**期待される出力例**:
```plaintext
/tmp/runs/<timestamp>
[OK] Flattened values -> .../_values_all.txt and rankXXXX.val
[OK] Plots -> .../plots
```

**確認ポイント**:
- `runs/<timestamp>`が作成されること。
- `_values_all.txt`と`rank*.val`が生成されること。
- `plots`配下に`*.png`が生成されること。

#### Step 6: 生成物確認

**実施ノード**: Netgauge導入対象ノード

**コマンド**:
```bash
latest_dir=$(ls -td /tmp/runs/* | head -1)
ls -l "$latest_dir"
ls -l "$latest_dir/plots"
```

**期待される出力例**:
```plaintext
... _values_all.txt
... rank0000.val
... plots/
... plots/all_hist.png
... plots/rank0000_hist.png
```

**確認ポイント**:
- 整形済みデータファイルがあること。
- ヒストグラム画像が生成されていること。

#### Step 7: FFT描画確認(任意)

**実施ノード**: Netgauge導入対象ノード

**コマンド**:
```bash
latest_dir=$(ls -td /tmp/runs/* | head -1)
python3 /opt/netgauge/bin/60_fft_plot.py "$latest_dir" --dt 0.00005
ls -l "$latest_dir/fft_plots"
```

**期待される出力例**:
```plaintext
... all_ranks_amp.png
... all_ranks_pow.png
... rank0000_amp.png
... rank0000_pow.png
```

**確認ポイント**:
- `fft_plots`配下に画像が生成されること。
- `python3`実行時に`matplotlib`/`numpy`不足エラーが出ないこと。

## トラブルシューティング

実行者はエラー発生時に build-*.log と対象ホスト上の `/opt/netgauge/bin` 配下ログを確認し, 失敗した task と前提条件未充足を特定します。代表的なトラブルと対処を以下に示します。

| 想定トラブル | 主な原因 | 対処方法 |
| --- | --- | --- |
| ロール実行開始直後に変数未定義エラーで停止する | `netgauge_version` が未設定, または空文字列 | 実行者は `group_vars` または `host_vars` で `netgauge_version` を定義し, 空文字列でないことを確認してから再実行します。 |
| Netgauge アーカイブ取得に失敗する | 取得元 URL の到達不可, DNS 解決失敗, 制御ノードの外向き通信制限 | 実行者は制御ホストで `curl -I https://htor.inf.ethz.ch/research/netgauge/` を実行し, 到達性を確認します。到達できない場合は名前解決設定, プロキシ設定, ファイアウォール設定を見直して再実行します。 |
| build.yml 実行時に configure または gmake が失敗する | 制御ホストに `gmake`, コンパイラ, 開発用ライブラリが不足 | 実行者は制御ホストで `gmake --version` と `cc --version` を確認し, 必要パッケージを導入してから再実行します。 |
| `10_prepare_cgroup.sh` 実行時に Permission denied が発生する | `sudo` なしで実行, または cgroup 書き込み権限不足 | 実行者は対象ホストで `sudo /opt/netgauge/bin/10_prepare_cgroup.sh` を実行し, `sudo` 権限が有効であることを確認します。必要に応じて実行ユーザの sudo 権限を見直します。 |
| `90_get_app_cpu_noise.sh` 実行後に `rank*.val` や画像が生成されない | 前段スクリプト失敗, `gnuplot` 未導入, 計測コマンド異常終了 | 実行者は `/tmp/runs/<timestamp>` 配下の `_values_all.txt` と `plots` ディレクトリ有無を確認し, `gnuplot --version` で導入状態を確認します。前段の `00_detect_cpus.sh` と `20_launch_netgauge.sh` を個別実行して失敗箇所を切り分けます。 |
| FFT 描画ステップで Python import エラーが発生する | `matplotlib` または `numpy` が未導入 | 実行者は対象ホストで `python3 -c "import matplotlib, numpy"` を実行し, 不足パッケージを導入してから `60_fft_plot.py` を再実行します。 |
| `APP_RANGE` が空になり計測が開始できない | CPU コア数が少ない環境, `00_detect_cpus.sh` の検出結果が前提に合わない | 実行者は `.cpu_env` の `HK_RANGE`, `PRESENT`, `APP_RANGE` を確認し, 必要に応じて計測対象ホストの CPU 構成を見直します。最小構成で検証する場合は `20_launch_netgauge.sh` の実行条件を調整して再試行します。 |


## 注意事項

- 既存の`package.yml`, `directory.yml`, `user_group.yml`, `service.yml`, `config.yml`は, 現行では予約タスクです。
- そのため, グラフ描画に必要な`gnuplot`, `matplotlib`, `numpy`は環境側で事前に導入してください。
- `20_launch_netgauge.sh`は`MODE=fwq|ftq`, `QUANTUM_US`, `DURATION_SEC`などの環境変数で動作を調整できます。
- 計測精度を上げる場合は, `周波数スケーリング`や他の負荷要因の影響を考慮してください。
- ヒストグラムは処理完了時間の分布を示し, 分布の広がりは`ジッタ`の評価に利用できます。

## 参考資料

### 公式ドキュメント

- [Netgauge - A Network Performance Measurement Toolkit](https://htor.inf.ethz.ch/research/netgauge/)
