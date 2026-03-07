# Netgauge関連

このロールは, Netgaugeをビルドして配置し, OSノイズ計測用スクリプトを導入するためのロールです。Netgauge本体のビルドはAnsibleの制御ノード(localhost)で実行し, 生成したバイナリを対象ノードへ配置します。

## 概要

### 構成要素

このロールは以下の2系統を構成します。

1. Netgauge本体の配置。
- `netgauge`バイナリを`/opt/netgauge/bin`へ配置します。
- Netgaugeは`MPI`, `TCP`, `UDP`, `RAW Ethernet`, `InfiniBand`などの通信方式を対象に, レイテンシや帯域, `LogP`/`LogGP`関連の計測を実行できます。

2. OSノイズ計測スクリプト群の配置。
- `00_detect_cpus.sh`から`90_get_app_cpu_noise.sh`までのスクリプトを配置します。
- `FWQ`, `FTQ`, `Selfish Detour`を利用したOSノイズ計測を実行できます。
- 実行結果は`runs/<測定時刻>/`配下に保存され, ヒストグラム画像を生成できます。

### 実装の流れ

ロール実行時は以下の順序で処理します。

1. パラメータ読み込み (`load-params.yml`)。
2. Netgaugeのビルドと配置 (`build.yml`)。
3. 予約済みタスク群の実行 (`package.yml`, `directory.yml`, `user_group.yml`, `service.yml`, `config.yml`)。
4. 計測スクリプト群の配置 (`tools.yml`)。

### ディレクトリ構成

ロール実行後, 既定では以下の構成になります。

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

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Netgauge | Netgauge | Zurich工科大学が公開するネットワーク性能とOSノイズの計測ツールです。 |
| Message Passing Interface | MPI | 並列処理でプロセス間通信を行うための規約です。 |
| Transmission Control Protocol | TCP | 接続型の通信方式です。 |
| User Datagram Protocol | UDP | 接続レスの通信方式です。 |
| Raw Ethernet | RAW Ethernet | IP層を使わずにEthernetフレームを扱う通信方式です。 |
| InfiniBand | InfiniBand | 高帯域, 低遅延向けのネットワーク技術です。 |
| LogP model | LogP | 通信オーバーヘッドや遅延を表現する性能モデルです。 |
| LogGP model | LogGP | LogPを拡張した性能モデルです。 |
| Fixed Work Quantum | FWQ | 固定作業量でノイズ影響を測る手法です。 |
| Fixed Time Quantum | FTQ | 固定時間で処理量の変動を測る手法です。 |
| Selfish Detour | Selfish Detour | OSノイズ観測で使う計測パターンの1つです。 |
| Operating System | OS | 基本ソフトウエアです。 |
| Red Hat Enterprise Linux | RHEL | Red Hat系の企業向けLinuxディストリビューションです。 |
| Central Processing Unit | CPU | 演算処理装置です。 |
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
| Internet Protocol | IP | ネットワーク通信のための基本プロトコルです。 |
| matplotlib | matplotlib | Python向けのグラフ描画ライブラリです。 |
| NumPy | numpy | Python向けの数値計算ライブラリです。 |
| YAML Ain't Markup Language | YAML | 設定ファイル形式です。 |
| Uniform Resource Locator | URL | リソースの参照先を示す文字列です。 |
| Portable Network Graphics | PNG | 可逆圧縮形式の画像ファイルです。 |
| playbook | playbook | Ansibleの実行手順ファイルです。 |
| role | role | Ansibleで機能単位にまとめた構成です。 |
| task | task | Ansibleで実行する処理単位です。 |
| template | template | 変数展開して出力する雛形ファイルです。 |
| handler | handler | 通知時に実行する再処理です。 |
| tag | tag | Ansibleで実行対象を絞るラベルです。 |

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

## 実行フロー

ロールは以下の8フェーズで処理します。

1. **Load Params**。
- `vars/packages-ubuntu.yml`または`vars/packages-rhel.yml`を読み込みます。
- `vars/cross-distro.yml`, `vars/all-config.yml`, `vars/k8s-api-address.yml`を読み込みます。

2. **Build**。
- 制御ノード上でビルド作業ディレクトリを作成します。
- `netgauge_URL`からアーカイブを取得して展開します。
- `./configure`, `gmake`, `gmake install`を実行します。
- 生成物を`netgauge_dir`へコピーします。

3. **Package**。
- 予約タスクです。
- 現行実装では有効なインストール処理はありません。

4. **Directory**。
- 予約タスクです。
- 現行実装では有効な作成処理はありません。

5. **User Group**。
- 予約タスクです。
- 現行実装では有効な作成処理はありません。

6. **Service**。
- 予約タスクです。
- 現行実装では有効なサービス処理はありません。

7. **Config**。
- 予約タスクです。
- 現行実装では有効な設定処理はありません。

8. **Tools**。
- 計測補助スクリプトと描画関連ファイルを`{{ netgauge_dir }}/bin`へ配置します。

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

## 主な処理

- Netgaugeソースをダウンロードしてビルドします。
- ビルド済みバイナリを対象ノードへ配置します。
- 計測実行をまとめた`90_get_app_cpu_noise.sh`を配置します。
- `00_detect_cpus.sh`で`HK/APP`分割を計算します。
- `10_prepare_cgroup.sh`で`cgroup`と`cpuset`を設定します。
- `25_flatten_values.sh`で値を整形し, `30_plot_all.sh`でヒストグラム画像を生成します。
- `60_fft_plot.py`で`FFT`と`PSD`の可視化を実行できます。

## テンプレート / 出力ファイル

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

## ハンドラ

現行実装では, このロール固有の有効なハンドラ処理はありません。

## OS差異

| 項目 | Debian系 | RHEL系 |
| --- | --- | --- |
| 変数ファイル読込 | `vars/packages-ubuntu.yml`を読込 | `vars/packages-rhel.yml`を読込 |
| Build処理 | 共通 | 共通 |
| Tools処理 | 共通 | 共通 |
| Package処理 | 予約タスク(実質未実装) | 予約タスク(実質未実装) |

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

## 検証

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

## 補足

- 既存の`package.yml`, `directory.yml`, `user_group.yml`, `service.yml`, `config.yml`は, 現行では予約タスクです。
- そのため, グラフ描画に必要な`gnuplot`, `matplotlib`, `numpy`は環境側で事前に導入してください。
- `20_launch_netgauge.sh`は`MODE=fwq|ftq`, `QUANTUM_US`, `DURATION_SEC`などの環境変数で動作を調整できます。
- 計測精度を上げる場合は, `周波数スケーリング`や他の負荷要因の影響を考慮してください。
- ヒストグラムは処理完了時間の分布を示し, 分布の広がりは`ジッタ`の評価に利用できます。

## 参考リンク

- [Netgauge - A Network Performance Measurement Toolkit](https://htor.inf.ethz.ch/research/netgauge/)
