# k8s-register-image ロール

本ロールは, 呼び出し元ロールが事前に用意したコンテナイメージ tar を Kubernetes ノードへ配布し, control plane ノードと worker ノード上の Container Runtime Interface (CRI, containerd など) に登録するための共通ロールです。

## 目次

- [k8s-register-image ロール](#k8s-register-image-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
  - [本ロールの動作仕様](#本ロールの動作仕様)
  - [呼び出し元ロールからの使用方法](#呼び出し元ロールからの使用方法)
    - [呼び出し元ロール作成者が実施する作業](#呼び出し元ロール作成者が実施する作業)
    - [呼び出し元ロールでのパラメタの設定手順](#呼び出し元ロールでのパラメタの設定手順)
    - [呼び出し元ロールから本ロールを呼び出すansibleタスクの記載方法](#呼び出し元ロールから本ロールを呼び出すansibleタスクの記載方法)
      - [コンテナイメージをcontrol plane ノード群に配布する場合の例](#コンテナイメージをcontrol-plane-ノード群に配布する場合の例)
      - [コンテナイメージをworker ノード群に配布する場合の例](#コンテナイメージをworker-ノード群に配布する場合の例)
    - [各パラメタ変数に設定する値](#各パラメタ変数に設定する値)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
  - [主要変数](#主要変数)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
  - [実行フロー](#実行フロー)
  - [検証ポイント](#検証ポイント)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. 入力検証で停止し, required inputs エラーが表示される場合](#1-入力検証で停止し-required-inputs-エラーが表示される場合)
    - [2. Missing image tar path or expected image tag for component で停止する場合](#2-missing-image-tar-path-or-expected-image-tag-for-component-で停止する場合)
    - [3. worker 自動検出時に No worker nodes found in the cluster で停止する場合](#3-worker-自動検出時に-no-worker-nodes-found-in-the-cluster-で停止する場合)
    - [4. worker Ready 待機で失敗する場合](#4-worker-ready-待機で失敗する場合)
    - [5. 対象ノードへの接続前確認で失敗する場合](#5-対象ノードへの接続前確認で失敗する場合)
    - [6. tar 転送で失敗する場合](#6-tar-転送で失敗する場合)
    - [7. expected image tag not found で停止する場合](#7-expected-image-tag-not-found-で停止する場合)
    - [8. 後続処理で tar ファイルが見つからない場合](#8-後続処理で-tar-ファイルが見つからない場合)
  - [注意事項](#注意事項)
  - [参考資料](#参考資料)
    - [公式ドキュメント](#公式ドキュメント)

## 用語

この節では, 本文で使用する用語を定義します。

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
| ロール | - | Ansible における処理のまとまり。 |
| 変数 | - | 実行時に値を切り替えるための設定項目。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 対象ノード | - | コンテナイメージ tar を配布し, containerd への登録を実行するノード。 |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウェア。 |
| control plane ノード | - | Kubernetes の制御機能を担うノード。 |
| worker ノード | - | Kubernetes 上で動作するアプリケーションを実行するノード。 |
| Container Runtime Interface | CRI | Kubernetesがコンテナランタイムと通信するための標準インターフェース。 |
| containerd | containerd | Dockerから分離された軽量なコンテナランタイム。 |
| ctr | ctr | containerd に付属する低レベル操作コマンド。image import によるコンテナイメージ登録やコンテナイメージへのタグ (tag) 付けに使用します。 |
| コンテナイメージ tar ファイル | - | コンテナイメージをアーカイブ化したファイル。呼び出し元ロールが事前準備する成果物。 |
| 未修飾名イメージ | - | レジストリ名が付かないイメージ名。例: `library/busybox:latest`。 |
| 既定レジストリ | - | 未修飾名イメージへ補完するレジストリ名。`k8s_register_image_unqualified_image_registry` で指定します。 |
| kubeconfig | kubeconfig | Kubernetes 接続設定ファイルを指す名称。kubectl などが参照する。 |
| Host Variables | host_vars | ホスト単位の設定値を格納する変数定義。 |
| Ansible Inventory | inventory | 実行対象ホストの一覧と接続情報を管理する定義。 |
| Ansible Task | task | 自動化処理の最小単位となる実行項目。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |

## 概要

本ロールは, 呼び出し元ロールが事前に用意したコンテナイメージ tar を Kubernetes ノードへ配布し, control plane ノードと worker ノード上の Container Runtime Interface (CRI, containerd など) に登録するための共通ロールです。

## 本ロールの動作仕様

本ロールの役割, 動作仕様は以下の通り。

- 呼び出し元ロールが制御ホスト上に準備したコンテナイメージ tar を, 対象ノード(control plane ノード, worker ノード)へ転送します。
- 対象ノード上で containerd の `ctr` コマンドを用いて image import を行う。
- 未修飾名のイメージについては, CRI の既定レジストリ解決差異を吸収するための別名タグを付与します。
- 本ロールは, コンテナイメージ tar を新しく作成したり, 外部から取得したりしない。利用者は, 配布対象の tar ファイルを制御ホスト上の所定ディレクトリに事前配置しておく。

## 呼び出し元ロールからの使用方法

本節では, 呼び出し元ロール作成者が本ロールを利用する際の使用法を述べる。

### 呼び出し元ロール作成者が実施する作業

呼び出し元ロール作成者が本ロールを利用する際に設定する変数と設定値の概要は以下の通り。

1. 登録対象コンポーネントの定義として以下の変数を設定します。
    1. `k8s_register_image_components`: 登録対象コンポーネント名と tar ファイル絶対パスの対応表
    2. `k8s_register_image_expected_images`: コンポーネント名とコンテナイメージ名の対応表
2. 対象ノードの指定方式として以下のいずれかを設定します。
    1. 明示指定:
         - `k8s_register_image_control_plane_hosts`: 登録対象の control plane ノード名配列を設定する (例: `['k8sctrlplane01.local', 'k8sctrlplane02.local']`)。
         - `k8s_register_image_worker_hosts`: 登録対象の worker ノード名配列を設定する (例: `['k8sworker0101.local', 'k8sworker0102.local']`)。
    2. 自動検出:
         - `k8s_register_image_auto_discover_worker_hosts`: worker ノードを自動検出する場合に `true` を設定します。
         - `k8s_kubeconfig_to_discover_workers_path`: worker ノード自動検出で `kubectl` が参照する kubeconfig ファイルパスを設定する(例: `/etc/kubernetes/admin.conf`)。
3. 実行時制御として以下の変数を設定します。
   1. `k8s_register_image_remote_cache_dir`: 対象ノードで tar を一時配置するディレクトリ
   2. `k8s_register_image_unqualified_image_registry`: 未修飾名イメージへ補完する既定レジストリ名
  3. `k8s_register_image_cleanup_remote_tar`: 登録後に対象ノード上の tar を削除する場合は `true`, 保持する場合は `false`
  4. `k8s_register_image_skip_discovery`: 対象ノード再探索を抑止する場合は `true`, 再探索を実行する場合は `false`

### 呼び出し元ロールでのパラメタの設定手順

1. 呼び出し元ロールで, 制御ホスト上に登録対象コンテナイメージ tar を配置します。
2. 呼び出し元ロールで, 本ロールに渡す入力パラメタを目的別に設定します。
   - コンポーネント定義: コンポーネント名と tar ファイルパス, 期待タグ
  - 対象ノード指定: control plane は明示指定, worker は明示指定または自動検出
   - 実行制御: 一時配置先, 未修飾名補完レジストリ, 後始末方針
3. `include_role` で `k8s-register-image` を呼び出し, 設定した入力パラメタを渡す。
4. 実行結果で, 対象ノード上の `ctr -n k8s.io images ls` を実行し, 期待したタグが登録されたことを確認します。

### 呼び出し元ロールから本ロールを呼び出すansibleタスクの記載方法

本節では, 呼び出し元ロールから本ロールを呼び出す際の ansible タスクの記載方法を例示します。

本稿では, 登録対象コンポーネント名, コンテナイメージ tar ファイル, コンテナイメージ名について, 以下を用いる:

|登録対象コンポーネント名|コンテナイメージ tar ファイル|コンテナイメージ名|
|---|---|---|
|manager|/opt/virtual-cluster/binary/manager-amd64.tar|virtualcluster/manager-amd64:latest|
|syncer|/opt/virtual-cluster/binary/syncer-amd64.tar|virtualcluster/syncer-amd64:latest|
|vn-agent|/opt/virtual-cluster/binary/vn-agent-amd64.tar|virtualcluster/vn-agent-amd64:latest|

#### コンテナイメージをcontrol plane ノード群に配布する場合の例

本節で示す処理内容の仕様は以下の通り。

- 登録対象コンポーネントとコンテナイメージ tar ファイル, コンテナイメージ名の対応表を定義する:
  - `k8s_register_image_components`: `コンポーネント名` から `コンテナイメージ tar ファイルへのパス` への辞書
  - `k8s_register_image_expected_images`: `コンポーネント名` から `コンテナイメージ名`への辞書
- control plane ノード群へ配布するために, 以下の設定を行う:
  - `k8s_register_image_control_plane_hosts` に control plane ノード一覧を設定する
- 配布時の一時配置先を `k8s_register_image_remote_cache_dir` へ設定
- 未修飾名イメージの補完先レジストリを `k8s_register_image_unqualified_image_registry` へ設定
- 登録後も対象ノード上のコンテナイメージ tar ファイルを削除せず保持するために `k8s_register_image_cleanup_remote_tar` に `false` を設定します。典型的な場合は, control plane ノードへの配布後に続けて worker ノードへの配布処理を行うためです。そのため, control plane ノードへの配布後に対象ノード上のコンテナイメージ tar ファイルを削除しないようにします。

本ロールを使用して上記のコンテナイメージを K8s の control plane ノード群に配布するタスクの記載例を以下に示す:

```yaml
1: - name: Register images via k8s-register-image
2:   ansible.builtin.include_role:
3:     name: k8s-register-image
4:     tasks_from: register-control-plane.yml
5:   vars:
6:     k8s_register_image_components:
7:       manager: "/opt/virtual-cluster/binary/manager-amd64.tar"
8:       syncer: "/opt/virtual-cluster/binary/syncer-amd64.tar"
9:       vn-agent: "/opt/virtual-cluster/binary/vn-agent-amd64.tar"
10:     k8s_register_image_expected_images:
11:       manager: "virtualcluster/manager-amd64:latest"
12:       syncer: "virtualcluster/syncer-amd64:latest"
13:       vn-agent: "virtualcluster/vn-agent-amd64:latest"
14:     k8s_register_image_control_plane_hosts:
15:       - "k8sctrlplane01.local"
16:       - "k8sctrlplane02.local"
17:     k8s_register_image_remote_cache_dir: "/tmp/vc-images"
18:     k8s_register_image_unqualified_image_registry: "docker.io"
19:     k8s_register_image_cleanup_remote_tar: false
```

上記例の各行での記載内容は以下の通り。

- 1-4 行目: `k8s-register-image` ロール呼び出し処理を実施するための記載です。
  - 1行目: タスクの名前を設定
  - 2行目: `include_role` モジュールを使用することを指定
  - 3行目: 呼び出すロール名(`k8s-register-image`)を指定
  - 4行目: 実行するタスクファイルにcontrol plane ノードへの配布処理(`register-control-plane.yml`)を指定
- 6-13 行目: 登録対象コンポーネント名, コンテナイメージ tar ファイル, コンテナイメージ名を指定するための設定です。
  - 6-9行目: 登録対象コンポーネント名をキーにコンテナイメージ tar ファイルを取得する辞書を設定
  - 10-13行目: 登録対象コンポーネント名をキーにコンテナイメージ名を取得する辞書を設定
- 14-16 行目: control plane ノード一覧を明示指定するための設定です。
- 17-19 行目: 一時配置先, 未修飾名補完レジストリ, 登録後の tar 保持方針を指定するための設定です。
  - 17行目: 対象ノード上で tar を一時配置するディレクトリ(`k8s_register_image_remote_cache_dir`)を指定
  - 18行目: 未修飾名イメージへ補完する既定レジストリ(`k8s_register_image_unqualified_image_registry`)を指定
  - 19行目: CRIへの登録後に対象ノード上の tar を削除せず保持する設定(`k8s_register_image_cleanup_remote_tar: false`)

#### コンテナイメージをworker ノード群に配布する場合の例

本節で示す処理内容の仕様は以下の通り。

- 登録対象コンポーネントとコンテナイメージ tar ファイル, コンテナイメージ名の対応表を定義する:
  - `k8s_register_image_components`: `コンポーネント名` から `コンテナイメージ tar ファイルへのパス` への辞書
  - `k8s_register_image_expected_images`: `コンポーネント名` から `コンテナイメージ名`への辞書
- worker ノード群へ配布するために, 以下の設定を行う:
  - `k8s_register_image_auto_discover_worker_hosts` を `true` に設定
  - worker ノード一覧の算出に使用する kubeconfig のパスを `k8s_kubeconfig_to_discover_workers_path` 変数に設定
- worker ノードへの配布処理の重複実行を抑止するために, 以下の設定を行う:
  - `k8s_register_image_control_plane_hosts` に control plane ノード一覧を明示指定する
- 配布時の一時配置先を `k8s_register_image_remote_cache_dir` へ設定
- 未修飾名イメージの補完先レジストリを `k8s_register_image_unqualified_image_registry` へ設定
- 登録後に対象ノード上のコンテナイメージ tar ファイルを削除するために `k8s_register_image_cleanup_remote_tar` に `true` を設定します。典型的な場合は, worker ノードへの配布処理が本節の処理の終端となるためです。そのため, 対象ノード上にコンテナイメージ tar ファイルを残さないようにします。

本ロールを使用して上記のコンテナイメージを K8s の worker ノード群に配布するタスクの記載例を以下に示す:

```yaml
1: - name: Register images via k8s-register-image
2:   ansible.builtin.include_role:
3:     name: k8s-register-image
4:     tasks_from: register-workers.yml
5:   vars:
6:     k8s_register_image_components:
7:       manager: "/opt/virtual-cluster/binary/manager-amd64.tar"
8:       syncer: "/opt/virtual-cluster/binary/syncer-amd64.tar"
9:       vn-agent: "/opt/virtual-cluster/binary/vn-agent-amd64.tar"
10:     k8s_register_image_expected_images:
11:       manager: "virtualcluster/manager-amd64:latest"
12:       syncer: "virtualcluster/syncer-amd64:latest"
13:       vn-agent: "virtualcluster/vn-agent-amd64:latest"
14:     k8s_register_image_control_plane_hosts:
15:       - "k8sctrlplane01.local"
16:       - "k8sctrlplane02.local"
17:     k8s_register_image_auto_discover_worker_hosts: true
18:     k8s_kubeconfig_to_discover_workers_path: "/etc/kubernetes/admin.conf"
19:     k8s_register_image_remote_cache_dir: "/tmp/vc-images"
20:     k8s_register_image_unqualified_image_registry: "docker.io"
21:     k8s_register_image_cleanup_remote_tar: true
```

上記例の各行での記載内容は以下の通り。

- 1-4 行目: `k8s-register-image` ロール呼び出し処理を実施するための記載です。
  - 1行目: タスクの名前を設定
  - 2行目: `include_role` モジュールを使用することを指定
  - 3行目: 呼び出すロール名(`k8s-register-image`)を指定
  - 4行目: 実行するタスクファイルに worker ノードへの配布処理(`register-workers.yml`)を指定
- 6-13 行目: 登録対象コンポーネント名, コンテナイメージ tar ファイル, コンテナイメージ名を指定するための設定です。
  - 6-9行目: 登録対象コンポーネント名をキーにコンテナイメージ tar ファイルを取得する辞書を設定
  - 10-13行目: 登録対象コンポーネント名をキーにコンテナイメージ名を取得する辞書を設定
- 14-16 行目: worker 配布時の実行主体判定に使う control plane ノード一覧を明示指定する設定です。
- 17-18 行目: worker ノードを自動検出するための設定です。
  - 17行目: worker ノードを自動検出する設定(`k8s_register_image_auto_discover_worker_hosts: true`)を指定
  - 18行目: worker ノード自動検出時に `kubectl` が参照する kubeconfig (`k8s_kubeconfig_to_discover_workers_path`)を指定
- 19-21 行目: 一時配置先, 未修飾名補完レジストリ, 登録後のコンテナイメージ tar ファイル削除方針を指定するための設定です。
  - 19行目: 対象ノード上でコンテナイメージ tar ファイルを一時配置するディレクトリ(`k8s_register_image_remote_cache_dir`)を指定
  - 20行目: 未修飾名イメージへ補完する既定レジストリ(`k8s_register_image_unqualified_image_registry`)を指定
  - 21行目: CRIへの登録後に対象ノード上のコンテナイメージ tar ファイルを削除する設定(`k8s_register_image_cleanup_remote_tar: true`)を指定

### 各パラメタ変数に設定する値

| 分類 | 変数 | 規定値 | 設定する値 |
| --- | --- | --- | --- |
| コンポーネント定義 | `k8s_register_image_components` | `{}` | コンポーネント名をキー, コンテナイメージ tar ファイルの絶対パスを値とする対応表を指定します。 |
| コンポーネント定義 | `k8s_register_image_expected_images` | `{}` | コンポーネント名をキー, コンテナイメージ名を値とする対応表を指定します。 |
| 対象ノード指定(明示指定時) | `k8s_register_image_control_plane_hosts` | `[]` | 登録対象の control plane ノード名配列を指定します。 |
| 対象ノード指定(明示指定時) | `k8s_register_image_worker_hosts` | `[]` | 登録対象の worker ノード名配列を指定します。 |
| 対象ノード指定(自動検出時) | `k8s_register_image_auto_discover_worker_hosts` | `false` | worker ノードを自動検出する場合に `true` を指定します。 |
| 対象ノード指定(明示指定補助) | `k8s_register_image_control_plane_group_name` | `"k8s_ctrl_plane"` | 呼び出し元で `groups[...]` を参照して control plane ノード一覧を組み立てる際のグループ名を指定します。 |
| 対象ノード指定(自動検出時) | `k8s_kubeconfig_to_discover_workers_path` | `""` | worker ノード自動検出時に `kubectl` が参照する kubeconfig パスを指定します。 |
| 実行制御 | `k8s_register_image_skip_discovery` | `false` | 対象ノード再探索を抑止する場合に `true` を指定します。 |
| 実行制御 | `k8s_register_image_remote_cache_dir` | `"/tmp/k8s-register-image"` | 対象ノード上でコンテナイメージ tar ファイルを一時配置するディレクトリを指定します。 |
| 実行制御 | `k8s_register_image_unqualified_image_registry` | `"docker.io"` | 未修飾名イメージへ補完する既定レジストリ名を指定します。 |
| 実行制御 | `k8s_register_image_cleanup_remote_tar` | `true` | 登録後に対象ノード上のコンテナイメージ tar ファイルを削除する場合は `true`, 保持する場合は `false` を指定します。 |

## 前提条件

- 対象ホストが inventory に登録済みであること
- 関連する共通変数が vars/all-config.yml または host_vars に定義済みであること
- 呼び出しパラメタが適切に設定されていること

## 実行方法

本ロールは他のロールから呼び出されることで使用されます。

## 主要変数

| 変数名 | 意味 | 既定値 | 設定例 |
| --- | --- | --- | --- |
| k8s_register_image_connection_preflight_enabled | 接続前確認処理の実行可否を制御します。 | true | false |

## テンプレートと生成ファイル

本ロールでは以下のテンプレート / ファイルを出力します:
主な展開先ホストは, 対象ホスト です。

| ファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `files/import-image-on-cri.sh` | 対象ノードの Ansible 一時ディレクトリ(既定: `~/.ansible/tmp/ansible-tmp-*/import-image-on-cri.sh`, 権限昇格時の典型例: `/root/.ansible/tmp/ansible-tmp-*/import-image-on-cri.sh`) | コンテナイメージ tar を対象ノードの CRI に取り込むための実行スクリプトです。 |

## 実行フロー

1. `load-params.yml` を実行し, OS別変数, 共通変数, Kubernetes API アドレス関連変数を読み込みます。
2. `validate.yml` で入力値を検証し, 以下を満たさない場合は `assert` で停止します。
  - `k8s_register_image_components` が空ではない対応表であること
  - `k8s_register_image_expected_images` が空ではないこと
  - 各コンポーネントについて tar パスが絶対パスであり, 期待タグが定義されていること
3. `k8s_register_image_control_plane_hosts` が1件以上ある場合は `register-control-plane.yml` を実行します。`k8s_register_image_skip_discovery` が `false` のときは `discover-target-hosts.yml` を先行実行し, 代表ノード判定後に代表ノードだけが配布処理を継続します。
4. control plane 配布処理では対象ノードごとに `register-single-node.yml` を実行し, 接続前確認, 一時ディレクトリ作成, tar 転送, `ctr` による import, 期待タグ検証, 必要に応じた tar 削除を順に実施します。
5. `k8s_register_image_worker_hosts` が1件以上ある場合は `register-workers.yml` を実行します。`k8s_register_image_skip_discovery` が `false` のときは `discover-target-hosts.yml` を先行実行し, 代表ノード判定後に代表ノードだけが配布処理を継続します。
6. worker 自動検出が有効(`k8s_register_image_auto_discover_worker_hosts: true`)かつ worker 一覧が空の場合は `discover-worker-hosts.yml` を実行し, Ready 待機, `kubectl` による worker 一覧取得, InternalIP 解決, 動的インベントリ追加を行います。worker が0件の場合は失敗で停止します。
7. worker 配布処理では対象ノードごとに `register-single-node.yml` を実行し, control plane 配布と同じ手順で import とタグ検証を行います。
8. `package.yml`, `directory.yml`, `user_group.yml`, `service.yml`, `config.yml` を順に実行します。現行実装ではこれらのファイルに追加処理定義はありません。

## 検証ポイント

- control plane ノードと worker ノードの双方で, `ctr -n k8s.io images ls` にコンテナイメージ名とコンテナイメージ名に指定したタグ名が現れること。
- 未修飾名のイメージについて, コンテナイメージ名に指定したタグ名と別名タグ名の双方が登録されること。

## トラブルシューティング

### 1. 入力検証で停止し, required inputs エラーが表示される場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
grep -n 'k8s_register_image_components\|k8s_register_image_expected_images' vars/all-config.yml host_vars/*.yml group_vars/**/*.yml
```

**確認ポイント**:

- k8s_register_image_components と k8s_register_image_expected_images が定義済みであること。
- 両方の対応表が空ではないこと。
- コンポーネント名のキーが両方の対応表で一致していること。

### 2. Missing image tar path or expected image tag for component で停止する場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
grep -n 'k8s_register_image_components\|k8s_register_image_expected_images' vars/all-config.yml host_vars/*.yml group_vars/**/*.yml
```

**確認ポイント**:

- k8s_register_image_components の各 tar パスが絶対パスであること。
- コンポーネントごとの expected image tag が設定されていること。
- 同じキー名で両方の対応表が定義されていること。

### 3. worker 自動検出時に No worker nodes found in the cluster で停止する場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
kubectl --kubeconfig <path> get nodes
```

**確認ポイント**:

- k8s_kubeconfig_to_discover_workers_path の参照先が有効であること。
- kubectl で worker ノードが取得できること。
- 自動検出が成立しない場合は worker ノードを明示指定へ切り替えること。

### 4. worker Ready 待機で失敗する場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
kubectl get nodes -o wide
```

**確認ポイント**:

- worker ノードが Ready になっていること。
- 待機時間が不足する場合は k8s_register_image_wait_for_worker_ready_timeout を延長すること。
- 停止せず継続する運用の場合は k8s_register_image_wait_for_worker_ready_fail_on_timeout を false に設定すること。

### 5. 対象ノードへの接続前確認で失敗する場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
ansible -i inventory/hosts <target-host> -m ping -b
```

**確認ポイント**:

- 対象ノードへ SSH 接続可能であること。
- 権限昇格設定が有効であること。
- ansible_user, 鍵, sudo 設定が運用設定と一致していること。

### 6. tar 転送で失敗する場合

**実施対象ホスト**: 制御ホスト, 対象ノード

**実行するコマンド**:

```bash
ls -l <image-tar-path>
ssh <target-host> "mkdir -p <k8s_register_image_remote_cache_dir> && df -h <k8s_register_image_remote_cache_dir>"
```

**確認ポイント**:

- 制御ホスト上に tar ファイルが存在し, 読み取り可能であること。
- 対象ノードで一時配置先ディレクトリの作成と書き込みが可能であること。
- 対象ノードに十分な空き容量があること。

### 7. expected image tag not found で停止する場合

**実施対象ホスト**: 対象ノード

**実行するコマンド**:

```bash
ctr -n k8s.io images ls -q
```

**確認ポイント**:

- 期待タグ名が登録されていること。
- 未修飾名補完タグが必要な場合は補完タグも登録されていること。
- k8s_register_image_expected_images と k8s_register_image_unqualified_image_registry の設定値が一致していること。

### 8. 後続処理で tar ファイルが見つからない場合

**実施対象ホスト**: 対象ノード

**実行するコマンド**:

```bash
ls -l <k8s_register_image_remote_cache_dir>
```

**確認ポイント**:

- k8s_register_image_cleanup_remote_tar が true の場合は登録後に tar が削除されること。
- 後続処理で再利用する場合は k8s_register_image_cleanup_remote_tar を false に設定すること。

## 注意事項

- 対象ノードで `ctr` コマンドが利用可能であることを前提とします。
- 利用者は, 対象ノードで管理者権限のコマンド実行ができるように, 実行ユーザーの権限設定(sudo設定など)を事前に済ませておく。あわせて, 権限昇格時に対話入力が必要にならない設定であることを確認します。
- control plane ノードと worker ノードの一覧は, 呼び出し側で明示的に渡すか, 自動検出用変数を設定してロール側で検出します。
- 登録対象の tar ファイルは, Ansible 制御ノード上の指定ディレクトリに存在している必要がある。
- `k8s_register_image_cleanup_remote_tar` の設定は呼び出し元責務です。後続処理で同じ tar を再利用する場合は `false` を指定します。

## 参考資料

### 公式ドキュメント

- [Kubernetes Images](https://kubernetes.io/docs/concepts/containers/images/)
- [containerd ctr command](https://github.com/containerd/containerd/blob/main/docs/ctr.md)
