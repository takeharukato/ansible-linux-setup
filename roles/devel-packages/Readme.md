# devel-packages ロール

本ロールは, 開発環境に必要なパッケージ群を導入し, GUI を無効化してコンソールモードへ切り替えます。

## 目次

- [devel-packages ロール](#devel-packages-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
    - [主な処理](#主な処理)
    - [デフォルト動作](#デフォルト動作)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
    - [設定例](#設定例)
      - [基本的な設定例](#基本的な設定例)
      - [Go 言語導入の設定例](#go-言語導入の設定例)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
    - [kubectl 補完関連](#kubectl-補完関連)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [前提条件](#前提条件-1)
    - [1. パッケージ導入の確認](#1-パッケージ導入の確認)
      - [Debian/Ubuntu 系](#debianubuntu-系)
      - [RHEL 系](#rhel-系)
    - [2. kubectl 補完ファイルの確認](#2-kubectl-補完ファイルの確認)
      - [Debian/Ubuntu 系](#debianubuntu-系-1)
      - [RHEL 系](#rhel-系-1)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. パッケージ導入に失敗する場合](#1-パッケージ導入に失敗する場合)
    - [2. GUI が無効化されない場合](#2-gui-が無効化されない場合)
    - [3. kubectl 補完が導入されない場合](#3-kubectl-補完が導入されない場合)
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
| サービスアカウント (Service Account) | - | 自動処理中でサービスを呼び出す側のプログラムを識別するための識別情報。 |
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
| Internet Protocol | IP | ネットワーク上で宛先を識別し, データを届けるための通信手順。 |
| Structured Query Language | SQL | データベースを操作するための記述言語。 |
| Hypertext Transfer Protocol | HTTP | World Wide Webで情報をやり取りする通信手順。 |
| Hypertext Transfer Protocol Secure | HTTPS | 通信内容を暗号化してWorld Wide Web通信を行う方式。 |
| RPM Package Manager | RPM | RPM形式パッケージの導入, 更新, 削除, 情報参照を行う仕組み。 |
| Virtual Machine | VM | 物理計算機上で動作する仮想的な計算機。 |
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
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Graphical User Interface | GUI | 画面操作中心の利用形態です。 |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウェア。 |
| kubectl | - | Kubernetesクラスタを操作するためのコマンドラインツール。 |
| Advanced Package Tool | APT | Debian 系のパッケージ管理ツール。 |
| Dandified YUM | DNF | YUM の後継として利用するパッケージ管理ツール。 |
| Red Hat Enterprise Linux | RHEL | Red Hatが提供する企業向けLinuxディストリビューション。 |
| Red Hat Enterprise Linux 9 | RHEL9 | Red Hat Enterprise Linux の第9系統版。 |
| Secure Shell | SSH | 遠隔の計算機へ安全に接続して操作する方式。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `dpkg` | - | Debian パッケージの情報参照や導入確認を行うコマンド。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| rpmコマンド | - | RPM パッケージの情報参照や導入確認を行うコマンド。 |
| `systemctl` | - | systemd 管理下のサービスを起動, 停止, 状態確認するコマンド。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| リモートホスト | - | ネットワーク越しに接続して操作する別ホスト。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |

## 概要

このロールは, 開発環境に必要なパッケージ群を導入し, GUI を無効化してコンソールモードへ切り替えます。Kubernetes 開発向けの Python パッケージ導入と, kubectl シェル補完の設定にも対応します。Go 言語導入処理は `go-lang-local` ロールへ分離されています。

### 主な処理

- `devel_packages` を `state: latest` でインストールし, 変更時に GUI 無効化を通知します。
- Kubernetes 開発向け Python パッケージを条件付きで導入します。
- kubectl の bash/zsh 補完ファイルを生成し, 既定の配置先に配置します。

### デフォルト動作

- `devel_packages` のインストールは常に実行されます。
- Go パッケージ導入は `go-lang-local` ロールで実行します。
- `k8s_python_packages_enabled` または `k8s_python_devel_packages_enabled` が `false` の場合, 該当パッケージは導入されません。
- `kubectl_completion_enabled` が `true` でも, kubectl が存在しない場合は補完設定を行いません。

## 前提条件

- 対象 OS: Debian/Ubuntu系 (Ubuntu 24.04を想定), RHEL9 系 (Rocky Linux, AlmaLinux など, AlmaLinux 9.6を想定)
- Ansible 2.15 以降
- リモートホストへの SSH 接続が確立されていること
- sudo 権限が利用可能であること

## 実行方法

制御ホストで以下のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts site.yml --tags "devel-packages"
```

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `devel_packages` | (OS 別) | 開発パッケージ群。OS 別の定義を利用します。 |
| `kubectl_completion_enabled` | `true` | kubectl の bash/zsh 補完設定の可否。 |
| `k8s_python_packages_enabled` | `true` | Kubernetes 開発向け Python パッケージの導入可否。 |
| `k8s_python_devel_packages_enabled` | `true` | Kubernetes 開発向け Python ヘッダ等の導入可否。 |

### 設定例

#### 基本的な設定例

Kubernetes 開発向け Python パッケージと kubectl 補完を無効化する例です。

**記載先**:
- host_vars/ホスト名.yml または vars/all-config.yml

**記載例**:

```yaml
kubectl_completion_enabled: false
k8s_python_packages_enabled: false
k8s_python_devel_packages_enabled: false
```

**各項目の意味**:

| 項目 | 説明 | 記載例での値 | 動作 |
| --- | --- | --- | --- |
| `kubectl_completion_enabled` | kubectl 補完を有効化する場合は, `true`に設定します。 | `false` | `true`に設定すると補完ファイルを生成します。 |
| `k8s_python_packages_enabled` | Python ランタイム系を導入する場合は, `true`に設定します。 | `false` | `true`に設定するとK8s Python ランタイムを導入します。 |
| `k8s_python_devel_packages_enabled` | Python 開発ヘッダ等を導入する場合は, `true`に設定します。 | `false` | `true`に設定すると Kubernetes関連開発作業をPythonで実施するために必要なPython開発用パッケージを導入します。 |

#### Go 言語導入の設定例

Go 言語導入の設定例と検証方法は `go-lang-local` ロールのドキュメントを参照してください。

## テンプレートと生成ファイル

テンプレートから出力されるファイルはありません。
一方で, 本ロールはテンプレートを用いずに以下のファイルを作成/更新します。

Go 言語導入に関する設定値と処理フローは `go-lang-local` ロールのドキュメントを参照してください。

### kubectl 補完関連

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `テンプレート未使用 (ランタイム生成: kubectl bash 補完)` | `Debian/Ubuntu: `/usr/share/bash-completion/completions/kubectl`` / `RHEL: `/usr/share/bash-completion/completions/kubectl`` (既定: `Debian/Ubuntu: `/usr/share/bash-completion/completions/kubectl`` / `RHEL: `/usr/share/bash-completion/completions/kubectl``) | kubectl bash 補完ファイル。 条件: `kubectl_completion_enabled: true` かつ kubectl が存在する場合。 |
| `テンプレート未使用 (ランタイム生成: kubectl zsh 補完)` | `Debian/Ubuntu: `/usr/share/zsh/vendor-completions/_kubectl`` / `RHEL: `/usr/share/zsh/site-functions/_kubectl`` (既定: `Debian/Ubuntu: `/usr/share/zsh/vendor-completions/_kubectl`` / `RHEL: `/usr/share/zsh/site-functions/_kubectl``) | kubectl zsh 補完ファイル。 条件: `kubectl_completion_enabled: true` かつ kubectl が存在する場合。 |

## 実行フロー

1. パッケージ定義と共通変数を読み込みます。
2. `devel_packages` をインストールします。
3. `k8s_python_packages_enabled` / `k8s_python_devel_packages_enabled` が有効な場合, 対応する Python パッケージをインストールします。
4. `kubectl_completion_enabled` が有効で kubectl が存在する場合, シェル補完ファイルを配置します。
5. パッケージ更新があった場合, GUI を無効化するハンドラが実行されます。

## 検証ポイント

本節では, `devel-packages` ロール実行後に設定が反映されていることを確認する方法について説明します。

### 前提条件

- `devel-packages` ロールが正常に完了していること(`changed` または `ok` の状態)。
- リモートホストへ SSH で接続可能であること。
- sudo 権限が利用可能であること。

### 1. パッケージ導入の確認

導入対象の開発パッケージが存在することを確認します。

#### Debian/Ubuntu 系

```bash
dpkg -l | grep -E "(gcc|make|git)"
```

**期待される出力例**:

```
ii  gcc  4:13.2.0-1ubuntu1  amd64  GNU C compiler
ii  make 4.3-4.1build2      amd64  utility for directing compilation
ii  git  1:2.43.0-1         amd64  fast, scalable, distributed revision control system
```

#### RHEL 系

```bash
rpm -qa | grep -E "(gcc|make|git)"
```

**確認ポイント**:
- `devel_packages` に含まれる主要パッケージが存在すること。

```bash
systemctl get-default
```

**期待される出力例**:

```
multi-user.target
```

**確認ポイント**:
- `multi-user.target` になっていること。

### 2. kubectl 補完ファイルの確認

#### Debian/Ubuntu 系

```bash
ls -l /usr/share/bash-completion/completions/kubectl
ls -l /usr/share/zsh/vendor-completions/_kubectl
```

#### RHEL 系

```bash
ls -l /usr/share/bash-completion/completions/kubectl
ls -l /usr/share/zsh/site-functions/_kubectl
```

**期待される出力例**:

```
-rw-r--r-- 1 root root 12345 Feb 23 10:00 /usr/share/bash-completion/completions/kubectl
-rw-r--r-- 1 root root 12345 Feb 23 10:00 /usr/share/zsh/vendor-completions/_kubectl
```

**確認ポイント**:
- `kubectl_completion_enabled: true` かつ kubectl が存在する場合, 補完ファイルが配置されていること。

## トラブルシューティング

### 1. パッケージ導入に失敗する場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
dpkg -l | grep -E "(gcc|make|git)" || rpm -qa | grep -E "(gcc|make|git)"
```

**確認ポイント**:

- `devel_packages` に含まれる主要パッケージが導入済みであること。
- 導入されていない場合は, パッケージリポジトリ設定とネットワーク疎通を見直すこと。

### 2. GUI が無効化されない場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
systemctl get-default
sudo systemctl set-default multi-user.target
systemctl get-default
```

**確認ポイント**:

- `systemctl get-default` の結果が `multi-user.target` であること。
- 反映されない場合は, 権限不足や systemd 設定変更の失敗有無を確認すること。

### 3. kubectl 補完が導入されない場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
command -v kubectl
ls -l /usr/share/bash-completion/completions/kubectl
ls -l /usr/share/zsh/vendor-completions/_kubectl 2>/dev/null || ls -l /usr/share/zsh/site-functions/_kubectl
```

**確認ポイント**:

- `kubectl` コマンドが存在すること。
- `kubectl_completion_enabled: true` が設定されていること。
- 対象 OS に対応した補完ファイル配置先へファイルが作成されていること。

## 注意事項

- `google-chrome-stable` を含むパッケージを導入する場合, リポジトリ追加は別ロールで実施する前提です。
- GUI 無効化は `systemctl set-default multi-user.target` で実施されます。GUI が必要なノードでは注意してください。

## 参考資料

### 公式ドキュメント

- Ansible: https://docs.ansible.com/ansible/latest/index.html
- APT: https://wiki.debian.org/Apt
- DNF: https://dnf.readthedocs.io/en/latest/
