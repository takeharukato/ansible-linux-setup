# Netgauge関連

## 本ディレクトリについて

本ディレクトリには, ETH Zürich/SPCL が公開している「ネットワーク性能＆OSノイズ計測」のための拡張可能なベンチマーク・フレームワークであるNetgaugeを構築するplaybookが入っている。

Netgaugeは, MPI/TCP/UDP/RAW Ethernet/InfiniBand など複数のスタックに対して, レイテンシや帯域, LogP/LogGP パラメータなどを高精度に測定するプログラムを提供する。

- ネットワーク計測 ping-pong（one_one）, 1 から N/N から 1, LogGP 測定などの豊富なパターンを提供。
- OSノイズ計測 FWQ ( Fixed Work Quantum ) , FTQ ( Fixed Time Quantum ) , Selfish Detour を実装。割り込みやデーモン活動によるジッタを抽出できます。
- 高精度タイマ＆統計 周波数スケーリング無効などの前提で, 正確なタイムスタンプと要約統計を出せる。

本ロールを実行すると, `/opt/netgauge/bin`に測定用のコマンドとスクリプトが導入される。

## システムノイズの測定

`/opt/netgauge/bin/90_get_app_cpu_noise.sh`を実行すると, カレントディレクトリに`runs/測定日時を表すディレクトリ/plots`というディレクトリが作られる。当該ディレクトリ配下に, png形式で, 実行時間のヒストグラムが出力される。本ヒストグラムは, 50usで完了する処理が実際にどのくらいの時間で完了したかを表すヒストグラムである。

## 必要なパッケージについて

本roleから導入されるスクリプトを使用して, グラフを作成するためには, 以下のパッケージが必要。

- gnuplot

netgaugeのグラフ作成に60_fft_plot.pyを利用するためには, python3の以下のライブラリを導入する必要がある。

- matplotlib
- numpy

## 参考URL

- [Netgauge - A Network Performance Measurement Toolkit](https://htor.inf.ethz.ch/research/netgauge/)
