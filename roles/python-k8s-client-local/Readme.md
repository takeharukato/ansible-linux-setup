# python-k8s-client-local ロール

本ロールは, Python 言語版 Kubernetes client を対象ノード上で直接 pip install せずに, 構築ホスト上のコンテナでローカルパッケージ (deb/rpm) を生成して配布, 導入するロールです。

## 目次

- [python-k8s-client-local ロール](#python-k8s-client-local-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
  - [パッケージ導入確認方法](#パッケージ導入確認方法)
    - [Debian/Ubuntu環境での実行例](#debianubuntu環境での実行例)
    - [Red Hat/AlmaLinux環境での実行例](#red-hatalmalinux環境での実行例)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
    - [検証の前提条件](#検証の前提条件)
    - [検証環境の設定](#検証環境の設定)
    - [検証コマンドと期待結果](#検証コマンドと期待結果)
      - [1. Playbook 実行結果の確認](#1-playbook-実行結果の確認)
      - [2. Debian/Ubuntu での導入確認](#2-debianubuntu-での導入確認)
      - [3. Red Hat/AlmaLinux での導入確認](#3-red-hatalmalinux-での導入確認)
      - [4. 指定 Python 版での導入確認](#4-指定-python-版での導入確認)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. パッケージのビルドが失敗する場合](#1-パッケージのビルドが失敗する場合)
    - [2. 対象ホストへパッケージを導入できない場合](#2-対象ホストへパッケージを導入できない場合)
    - [3. 導入後に kubernetes モジュールを import できない場合](#3-導入後に-kubernetes-モジュールを-import-できない場合)
    - [4. 変数設定不備で処理が停止する場合](#4-変数設定不備で処理が停止する場合)
    - [5. 成果物配置先を確認する場合](#5-成果物配置先を確認する場合)
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
| サービスアカウント (Service Account) | - | 自動処理中でサービスを呼び出す側のプログラムを識別するための識別情報。 Kubernetesでは, 人間以外の実体をKubernetesクラスタ内で一意に識別するために用いられるアカウントのことを指す。 アプリケーションPod, システムコンポーネント, および, Kubernetesクラスター内外の実体に紐づけられたServiceAccountの認証情報を通して, これらの実体を互いに識別する。 |
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
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| Operating System | OS | 計算機の基本機能を管理し, アプリケーションを動作させる基盤ソフトウェア。 |
| Red Hat Enterprise Linux 9 | RHEL9 | Red Hat Enterprise Linux の第9系統版。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `dpkg` | - | Debian パッケージの情報参照や導入確認を行うコマンド。 |
| rpmコマンド | - | RPM パッケージの情報参照や導入確認を行うコマンド。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| ローカルパッケージ | - | 外部配布元ではなく, 手元環境で作成または保管した導入用パッケージ。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| 構築ホスト | - | パッケージや実行資材を生成するビルド処理を担当するホスト。 |

## 概要

本ロールは, Python 言語版 Kubernetes client を対象ノード上で直接 pip install せずに, 構築ホスト上のコンテナでローカルパッケージ (deb/rpm) を生成して配布, 導入するロールです。

- 他のロールからの入力として python_k8s_client_version_spec (例: ~=31.0, ==31.0.0) を受け取り, ローカルパッケージを作成します。
- 導入物は Debian系/RHEL系ともに導入対象Python向け site-packages と vendor依存を含むローカルパッケージです。
- ローカルパッケージの転送経路は, 構築ホスト -> 制御ノード -> 対象ホストです。
- k8s_python_packages_version が定義され, かつ空文字列でない場合は, /usr/bin/python{{ k8s_python_packages_version }} 向けにパッケージを構築し, 同じPythonで導入確認します。
- k8s_python_packages_version が未定義または空文字列の場合は, /usr/bin/python3 向けにパッケージを構築し, /usr/bin/python3 で導入確認します。

## 前提条件

- 対象 OS: Ubuntu24.04, RHEL9.6 (Alma Linuxを想定)。
- 構築ホストでコンテナランタイム (docker など) が利用可能であること。
- 本ロール呼び出し時に, python_k8s_client_version_spec を空文字列にしないこと。本変数の設定は呼び出し元ロールの責務とします。
- 構築ホストと制御ノード間, 制御ノードと対象ホスト間でdeb/rpmパッケージ転送のための通信が可能であること。

## 実行方法

制御ホストで以下のコマンドを実行します。

```bash
ansible-playbook -i inventory/hosts site.yml --tags "python-k8s-client-local"
```

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| python_k8s_client_version_spec | "" | kubernetes の版数指定。例: ~=31.0, ==31.0.0。通常は呼び出し元ロールから渡されるため, `vars/all-config.yml`や`host_vars`内の設定ファイルから設定する変数ではない。 |
| python_k8s_client_deb_package_name | "python3-k8s-client" | Debian系ローカルパッケージ名。 |
| python_k8s_client_rpm_package_name | "python3-k8s-client" | RHEL系ローカルパッケージ名。 |
| python_k8s_client_build_host | "localhost" | 構築ホスト。 |
| python_k8s_client_install_deb_lock_wait_seconds | 600 | Debian系 apt ロック待機秒数。 |
| python_k8s_client_build_container_runtime | "docker" | コンテナランタイム。 |
| python_k8s_client_build_container_network_mode | "host" | コンテナネットワークモード。 |
| python_k8s_client_build_container_image_debian | "python-k8s-client-build-ubuntu:24.04" | Debian系ビルド用イメージ名。 |
| python_k8s_client_build_container_image_rhel | "python-k8s-client-build-almalinux:9.6" | RHEL系ビルド用イメージ名。 |

構築ワークスペースは入力変数ではなく, タスク内で実行ユーザごとに `/tmp/python-k8s-client-build-<USER>` を自動選択します。

## パッケージ導入確認方法

python版 kubernetes clientが導入されていることを確認するためのコマンドは以下の通り:

```shell
# Debian系: system python で版数確認
/usr/bin/python3 -c 'import kubernetes; print(kubernetes.__version__)'

# RHEL系: system python で版数確認
/usr/bin/python3 -c 'import kubernetes; print(kubernetes.__version__)'

# Debian系: パッケージ導入確認
dpkg --list|egrep python3-k8s-client

# RHEL系: パッケージ導入確認
rpm -q python3-k8s-client
```

Debian系/RHEL系ともに`/usr/bin/python3 -c 'import kubernetes; print(kubernetes.__version__)'`の出力中で返される版数と導入されているパッケージの版数とが一致することを確認します。

k8s_python_packages_version が定義され, かつ空文字列でない場合は, `/usr/bin/python<k8s_python_packages_version> -c 'import kubernetes; print(kubernetes.__version__)'` を実行して同様の版数確認を行う。

k8s_python_packages_version=3.12 指定時の確認手順の例:

```shell
/usr/bin/python3.12 -c 'import kubernetes; print(kubernetes.__version__)'
```

### Debian/Ubuntu環境での実行例

Debian/Ubuntu環境での実行例を以下に示す:

```shell
$ /usr/bin/python3 -c 'import kubernetes; print(kubernetes.__version__)'
31.0.0
$ dpkg --list|egrep python3-k8s-client
ii  python3-k8s-client                    31.0.0-1                                all          Kubernetes Python client - local offline bundle
```

k8s_python_packages_version=3.12 指定時の実行例を以下に示す:

```shell
$ /usr/bin/python3.12 -c 'import kubernetes; print(kubernetes.__version__)'
31.0.0
$ dpkg --list|egrep python3-k8s-client
ii  python3-k8s-client                    31.0.0-1                                all          Kubernetes Python client - local offline bundle
```

### Red Hat/AlmaLinux環境での実行例

Red Hat/AlmaLinux環境での実行例を以下に示す:

```shell
$ /usr/bin/python3 -c 'import kubernetes; print(kubernetes.__version__)'
31.0.0
$ rpm -q python3-k8s-client
python3-k8s-client-31.0.0-1.el9.x86_64
```

k8s_python_packages_version=3.12 指定時の実行例を以下に示す:

```shell
$ /usr/bin/python3.12 -c 'import kubernetes; print(kubernetes.__version__)'
31.0.0
$ rpm -q python3-k8s-client
python3-k8s-client-31.0.0-1.el9.x86_64
```

## テンプレートと生成ファイル

本ロールでは以下のテンプレート / ファイルを出力します:
主な展開先ホストは, 構築ホスト , 対象ホスト(既定) , 制御ホスト です。

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `build-python-k8s-client-deb.sh.j2` | `{{ python_k8s_client_build_workspace_effective }}/build-python-k8s-client-deb.sh` (既定: `{{ python_k8s_client_build_workspace_effective }}/build-python-k8s-client-deb.sh`) | 対象ソフトウェアをソースからビルドし, ローカルパッケージを生成する実行スクリプトです。 |
| `python-k8s-client.control.j2` | `{{ python_k8s_client_build_workspace_effective }}/python-k8s-client.control` (既定: `{{ python_k8s_client_build_workspace_effective }}/python-k8s-client.control`) | Debian パッケージの依存関係やメタデータを定義する control ファイルです。 |
| `Dockerfile.ubuntu.j2` | `{{ python_k8s_client_build_workspace_effective }}/Dockerfile.python-k8s-client-deb` (既定: `{{ python_k8s_client_build_workspace_effective }}/Dockerfile.python-k8s-client-deb`) | ローカルパッケージを再現可能にビルドするためのコンテナイメージ定義です。 |
| `build-python-k8s-client-rpm.sh.j2` | `{{ python_k8s_client_build_workspace_effective }}/build-python-k8s-client-rpm.sh` (既定: `{{ python_k8s_client_build_workspace_effective }}/build-python-k8s-client-rpm.sh`) | 対象ソフトウェアをソースからビルドし, ローカルパッケージを生成する実行スクリプトです。 |
| `python-k8s-client.spec.j2` | `{{ python_k8s_client_build_workspace_effective }}/python-k8s-client.spec` (既定: `{{ python_k8s_client_build_workspace_effective }}/python-k8s-client.spec`) | RPM パッケージのビルド手順, 依存関係, ファイル構成を定義する spec ファイルです。 |
| `Dockerfile.almalinux.j2` | `{{ python_k8s_client_build_workspace_effective }}/Dockerfile.python-k8s-client-rpm` (既定: `{{ python_k8s_client_build_workspace_effective }}/Dockerfile.python-k8s-client-rpm`) | ローカルパッケージを再現可能にビルドするためのコンテナイメージ定義です。 |
| `verify_python_version_spec.py` | `/tmp/verify_python_version_spec.py` (既定: `/tmp/verify_python_version_spec.py`) | 導入した Python Kubernetes クライアントの版数制約を検証し, 実行時互換性を確認するスクリプトです。 |

## 実行フロー

1. load-params.yml で OS別/共通変数を読み込む。
2. package.yml で, check mode 以外の場合にパッケージ構築/導入を実行します。
3. Debian系では build-python-client-source-deb.yml でコンテナ内ビルドを行い, install-python-client-local-deb.yml で導入します。
4. RHEL系では build-python-client-source-rpm.yml でコンテナ内ビルドを行い, install-python-client-local-rpm.yml で導入します。
5. k8s_python_packages_version が定義され, かつ空文字列でない場合は, /usr/bin/python{{ k8s_python_packages_version }} を導入対象Pythonとしてビルド/導入を実行します。
6. k8s_python_packages_version が未定義または空文字列の場合は, /usr/bin/python3 を導入対象Pythonとしてビルド/導入を実行します。
7. 導入後に, 選択された導入対象Pythonで kubernetes を import し, 版数が python_k8s_client_version_spec を満たすことを確認します。

playbook中で実施する導入確認の要点:

- k8s_python_packages_version変数の定義に基づいて, パッケージ導入検証に用いるPythonインタプリタ(以下, 導入対象Pythonと記載)を決定の上, パッケージの導入, 指定された版数のpython版 Kubernetes クライアントライブラリが導入されていることを確認する:
  - k8s_python_packages_version が定義され, かつ, 空文字列でない場合は, 指定された版数のpythonインタプリタ ( /usr/bin/python{{ k8s_python_packages_version }} )を用いて, kubernetes の import と版数制約検証を実行します。
  - k8s_python_packages_version が未定義または空文字列の場合は, /usr/bin/python3 を用いて, kubernetes の import と版数制約検証を実行します。

## 検証ポイント

### 検証の前提条件

検証を始める前に, 次の条件が満たされていることを確認します。

- `k8s_devel_python_client_enabled` が `true` であること。
- `python_k8s_client_version_spec` が未定義又は空文字列でないこと。
- 構築ホストでコンテナランタイム (`python_k8s_client_build_container_runtime`) を実行できること。
- 制御ホストから対象ホストへパッケージ転送が可能であること。
- 対象ホストで `/usr/bin/python3` 又は `k8s_python_packages_version` で指定した Python 実行ファイルが利用可能であること。

### 検証環境の設定

検証用の host_vars と vars/all-config.yml を次の値で設定します。

```yaml
1: k8s_devel_python_client_enabled: true
2: python_k8s_client_version_spec: "~=31.0"
3: python_k8s_client_build_host: "localhost"
4: python_k8s_client_build_container_runtime: "docker"
5: k8s_python_packages_version: "3.12"
```

| 行番号 | 設定値 | 有効になる動作 | 設定背景(未設定時/誤設定時の問題と防止理由) |
| --- | --- | --- | --- |
| 1 | k8s_devel_python_client_enabled: true | ロールの package/directory/user_group/service/config 各タスクを実行します。 | `false` の場合は主要タスクが実行されず, 導入検証を実施できないためです。 |
| 2 | python_k8s_client_version_spec: "~=31.0" | 導入する kubernetes パッケージの版数制約を指定します。 | 未設定又は空文字列の場合はアサーションで停止し, 導入処理へ進まないためです。 |
| 3 | python_k8s_client_build_host: "localhost" | ローカルパッケージの構築先を指定します。 | 構築先が誤っている場合は成果物を取得できず, 導入処理が失敗するためです。 |
| 4 | python_k8s_client_build_container_runtime: "docker" | ビルドコンテナの起動コマンドを指定します。 | 実行不能なランタイム名を指定するとビルドが開始できないためです。 |
| 5 | k8s_python_packages_version: "3.12" | `/usr/bin/python3.12` を導入対象 Python として版数検証します。 | 変数未設定時は `/usr/bin/python3` が使われるため, 検証対象 Python を明示したい場合に必要です。 |

`k8s_python_packages_version` を指定しない運用では, 5行目を削除して `/usr/bin/python3` を検証対象にします。

### 検証コマンドと期待結果

#### 1. Playbook 実行結果の確認

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
ansible-playbook -i inventory/hosts site.yml --tags "python-k8s-client-local"
```

**期待される出力**:

```plaintext
failed=0
```

**確認ポイント**:

- `failed=0` で完了すること。
- `Assert python_k8s_client_version_spec is not empty` タスクが成功していること。

#### 2. Debian/Ubuntu での導入確認

**実施対象ホスト**: Debian/Ubuntu 系の対象ホスト

**実行するコマンド**:

```bash
dpkg-query -W -f='${Status} ${Version}\n' python3-k8s-client
/usr/bin/python3 -c 'import kubernetes; print(kubernetes.__version__)'
```

**期待される出力**:

```plaintext
install ok installed
31.0.0
```

**確認ポイント**:

- `python3-k8s-client` が導入済みであること。
- Python 実行結果の版数が `python_k8s_client_version_spec` の制約を満たすこと。

#### 3. Red Hat/AlmaLinux での導入確認

**実施対象ホスト**: Red Hat/AlmaLinux 系の対象ホスト

**実行するコマンド**:

```bash
rpm -q python3-k8s-client
/usr/bin/python3 -c 'import kubernetes; print(kubernetes.__version__)'
```

**期待される出力**:

```plaintext
python3-k8s-client-<version>
31.0.0
```

**確認ポイント**:

- `python3-k8s-client` パッケージ名で導入状態を取得できること。
- Python 実行結果の版数が `python_k8s_client_version_spec` の制約を満たすこと。

#### 4. 指定 Python 版での導入確認

**実施対象ホスト**: `k8s_python_packages_version` を設定した対象ホスト

**実行するコマンド**:

```bash
/usr/bin/python3.12 -c 'import kubernetes; print(kubernetes.__version__)'
```

**期待される出力**:

```plaintext
31.0.0
```

**確認ポイント**:

- `k8s_python_packages_version` で指定した Python 実行ファイルで `kubernetes` を import できること。
- 出力版数が playbook 実行時に導入した版数と一致していること。

## トラブルシューティング

### 1. パッケージのビルドが失敗する場合

**実施対象ホスト**: 制御ホスト, 構築ホスト

**実行するコマンド**:

```bash
ansible-playbook -i inventory/hosts site.yml --tags "python-k8s-client-local" -vv
ls -1 build-*.log
grep -nE 'ERROR|Error|failed|No python k8s client|Traceback' build-*.log
```

**確認ポイント**:

- `Build and install local python k8s client packages` の実行結果が成功であること。
- ログにコンテナ起動失敗, 依存解決失敗, 成果物未生成のいずれが出ているかを切り分けできること。
- `python_k8s_client_build_container_runtime` で指定したランタイムが構築ホストで実行可能であること。

### 2. 対象ホストへパッケージを導入できない場合

**実施対象ホスト**: 制御ホスト, 対象ホスト

**実行するコマンド**:

```bash
ansible-playbook -i inventory/hosts site.yml --tags "python-k8s-client-local" -vv
dpkg-query -W -f='${Status} ${Version}\n' python3-k8s-client || true
rpm -q python3-k8s-client || true
```

**確認ポイント**:

- playbook の実行結果で `failed=0` になっていること。
- Debian/Ubuntu 系では `dpkg-query` で `install ok installed` を確認できること。
- Red Hat/AlmaLinux 系では `rpm -q` で `python3-k8s-client-<version>` を確認できること。

### 3. 導入後に kubernetes モジュールを import できない場合

**実施対象ホスト**: 対象ホスト

**実行するコマンド**:

```bash
/usr/bin/python3 -c 'import kubernetes; print(kubernetes.__version__)'
/usr/bin/python3.12 -c 'import kubernetes; print(kubernetes.__version__)' || true
```

**確認ポイント**:

- `k8s_python_packages_version` 未設定時は `/usr/bin/python3` で import 成功すること。
- `k8s_python_packages_version` を設定した場合は, 対応する `/usr/bin/python<version>` で import 成功すること。
- 取得した版数が `python_k8s_client_version_spec` の制約を満たしていること。

### 4. 変数設定不備で処理が停止する場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
grep -n 'k8s_devel_python_client_enabled\|python_k8s_client_version_spec\|k8s_python_packages_version' vars/all-config.yml host_vars/*.yml
ansible-playbook -i inventory/hosts site.yml --tags "python-k8s-client-local" -vv
```

**確認ポイント**:

- `python_k8s_client_version_spec` が未定義又は空文字列でないこと。
- `k8s_devel_python_client_enabled` が `true` であること。
- `k8s_python_packages_version` を設定した場合は, 対象ホストに該当 Python 実行ファイルが存在すること。

### 5. 成果物配置先を確認する場合

**実施対象ホスト**: 構築ホスト

**実行するコマンド**:

```bash
ls -ld /tmp/python-k8s-client-build-* /tmp/python-k8s-client-build-fallback-*
find /tmp/python-k8s-client-build-* /tmp/python-k8s-client-build-fallback-* -maxdepth 2 -type f \( -name '*.deb' -o -name '*.rpm' \)
```

**確認ポイント**:

- ビルドワークスペース又はフォールバックワークスペースが作成されていること。
- `.deb` 又は `.rpm` の成果物が出力されていること。

## 注意事項

- ansible が check mode で動作している場合は本処理をスキップするため, 導入確認を行う場合は check mode を無効にして実行すること。
- `python_k8s_client_version_spec` が未定義又は空文字列の場合はアサーションで停止するため, 呼び出し元ロールで必ず値を設定すること。
- `k8s_python_packages_version` を設定した場合は, 対象ホストに対応する `/usr/bin/python<version>` が存在すること。存在しない場合は導入後の import 検証が失敗する。
- ローカルパッケージの生成成果物は `/tmp/python-k8s-client-build-*` 又は `/tmp/python-k8s-client-build-fallback-*` に出力されるため, 作業ディレクトリの空き容量と削除方針を事前に確認すること。
- `python_k8s_client_build_container_runtime` で指定したコンテナランタイムが構築ホストで利用可能であること。実行不可の場合はビルド処理が開始できない。
- 生成パッケージには署名付与を実施しないため, 配布経路と導入対象を運用手順で管理し, 信頼境界外へ持ち出さないこと。

## 参考資料

### 公式ドキュメント

- [Python](https://docs.python.org/3/)
- [Kubernetes Python Client](https://github.com/kubernetes-client/python)
