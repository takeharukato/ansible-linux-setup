# netshoot-no-portscan ロール

本ロールは, [nicolaka/netshoot](https://github.com/nicolaka/netshoot) をベースに, ポートスキャンツール などの悪用される恐れのあるツール群を除去したネットワーク診断用コンテナイメージを構築し, Kubernetes クラスタに配布するロールです。

## 目次

- [netshoot-no-portscan ロール](#netshoot-no-portscan-ロール)
  - [目次](#目次)
  - [用語](#用語)
  - [概要](#概要)
    - [標準のnicolaka/netshootとの相違](#標準のnicolakanetshootとの相違)
    - [ポートスキャンツール除去の仕組み](#ポートスキャンツール除去の仕組み)
    - [主な処理](#主な処理)
      - [コンテナイメージ構築処理 (`build-netshoot.yml`)](#コンテナイメージ構築処理-build-netshootyml)
      - [containerd 直接登録による配布処理 (`distribute-netshoot.yml`)](#containerd-直接登録による配布処理-distribute-netshootyml)
      - [ローカルレジストリ登録処理 (`register-netshoot.yml`)](#ローカルレジストリ登録処理-register-netshootyml)
      - [マニフェスト作成処理 (`create-manifest.yml`)](#マニフェスト作成処理-create-manifestyml)
  - [前提条件](#前提条件)
  - [実行方法](#実行方法)
    - [コンテナイメージの展開(デプロイ)方法](#コンテナイメージの展開デプロイ方法)
  - [主要変数](#主要変数)
  - [テンプレートと生成ファイル](#テンプレートと生成ファイル)
    - [コンテナイメージをK8sクラスタに展開するためのマニフェストの生成](#コンテナイメージをk8sクラスタに展開するためのマニフェストの生成)
      - [生成されるマニュフェストの仕様](#生成されるマニュフェストの仕様)
      - [`netshoot_image_registry` 変数によるイメージ参照先とpullポリシーの切り替え](#netshoot_image_registry-変数によるイメージ参照先とpullポリシーの切り替え)
  - [実行フロー](#実行フロー)
    - [コンテナイメージの構築と配布の流れ](#コンテナイメージの構築と配布の流れ)
    - [イメージ配布モードの選択](#イメージ配布モードの選択)
      - [containerd 直接登録モード](#containerd-直接登録モード)
      - [ローカルレジストリ登録モード](#ローカルレジストリ登録モード)
  - [検証ポイント](#検証ポイント)
  - [トラブルシューティング](#トラブルシューティング)
    - [1. Docker ビルドが失敗する場合](#1-docker-ビルドが失敗する場合)
    - [2. containerd へのイメージ登録が失敗する場合](#2-containerd-へのイメージ登録が失敗する場合)
    - [3. ローカルレジストリへの push が失敗する場合](#3-ローカルレジストリへの-push-が失敗する場合)
    - [4. Pod が起動しない場合](#4-pod-が起動しない場合)
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
| ローカルレジストリエンドポイント | - | 制御ホストから接続するローカルレジストリの接続先情報。 |
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
| Ansible | - | 設定の同一化や導入作業を所定の手順に従って自動化する仕組み。 |
| World Wide Web | WWW | ネットワーク上で文書や情報を相互参照できる仕組み。 |
| Service | - | サービスの英語表記。 |
| Node | - | ノードの英語表記。 |
| Makefile | - | 実行手順を定義したファイル。 |
| Application Programming Interface | API | アプリケーション同士が機能やデータをやり取りするための取り決め。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| ポートスキャン (port scan) | - | ネットワーク上のサーバなどの機器の各ポート(通信端点)にデータを送り, その応答から​​開いているポートや稼働しているサービスを調べること。悪意を持ったポートスキャンを避ける目的から, 本ロールでは, ポートスキャンツール(nmap関連ツール, スクリプト)を除去している。 |
| Denial of Service 攻撃 ( Denial of Service Attack ) | DoS攻撃 | 大量のリクエストを標的のサーバに送り付け、Webサイトやサービスを機能停止に追い込む攻撃方法。 |
| フラッディング攻撃 (Flooding Attack) | - | 大量の送信データを一気に送ることにより洪水(flood)を起こさせる攻撃。DoS攻撃の一種。本攻撃用途に使用されることを避ける目的から本ロールでは, 任意パケット生成に使用されるツール(scapy)などを除去している。 |
| Kubernetes | K8s | コンテナを管理する基盤ソフトウェア。 |
| Container Runtime Interface | CRI | Kubernetesがコンテナランタイムと通信するための標準インターフェース。 |
| containerd | - | Dockerから分離された軽量なコンテナランタイム。 |
| ポッド ( Pod ) | - | Kubernetes上で動作するコンテナの最小単位。 |
| デプロイ ( Deploy ) | - | 機能や設定を実行環境へ展開し, 利用可能な状態にする作業。 |
| コントロールプレーンノード ( Control Plane Node ) | - | Kubernetesクラスタ全体を管理, 制御する中枢ノード群。kube-apiserver, kube-controller-manager, kube-schedulerなどが動作します。 |
| ワーカノード ( Worker Node ) | - | 実際にアプリケーションのPodを実行するノード。 |
| kubeconfig | - | Kubernetes 接続設定ファイルを指す名称。kubectl などが参照する。 |
| マニフェスト ( Manifest ) | - | Kubernetes のリソース ( Pod, Deployment など ) を YAML 形式で定義したファイル。`kubectl apply` コマンドでクラスタに適用することで, 定義されたリソースが作成される。 |
| 名前空間 ( namespace ) | - | Kubernetes内部でリソースを論理的に分離する単位。 |
| 制御ホスト | - | Playbook を実行し, 他ホストへの処理指示を行う管理用ホスト。 |
| 構築ホスト | - | パッケージや実行資材を生成するビルド処理を担当するホスト。 |
| Docker | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| nmap | - | ネットワーク上のホストやポートを探索 ( スキャン ) するツール。本ロールでは, セキュリティポリシー上 nmap 等のポートスキャンツールを搭載できない環境での使用を想定し, nmap関連ツールをコンテナイメージから除去している。 |
| nicolaka/netshoot | netshoot | ネットワーク診断ツールを多数搭載した公開コンテナイメージ。 詳細は, [netshootのGithub](https://github.com/nicolaka/netshoot)を参照。 |
| imagePullPolicy | - | Kubernetes がコンテナイメージを取得する際の方針を指定するフィールド。`Never` はK8sの各ノードのCRI内の既存イメージのみ使用, `IfNotPresent` はノード上に存在しない場合のみ取得, `Always` は常に取得を行う。 |
| Border Gateway Protocol | BGP | 自律システム間で経路情報を交換する経路制御方式。 |
| Domain Name System | DNS | 名前と IP アドレスを対応付ける仕組み。 |
| Hypertext Transfer Protocol | HTTP | World Wide Webで情報をやり取りする通信手順。 |
| Hypertext Transfer Protocol Secure | HTTPS | 通信内容を暗号化してWorld Wide Web通信を行う方式。 |
| Open Shortest Path First | OSPF | ルータ同士が内部ネットワークの到達経路を交換するための経路制御方式。 |
| Secure Shell | SSH | 遠隔の計算機へ安全に接続して操作する方式。 |
| Transport Layer Security | TLS | 通信経路でデータを暗号化して保護する仕組み。 |
| Uniform Resource Locator | URL | World Wide Web上の資源の場所を示す文字列。 |
| BIRD Internet Routing Daemon | BIRD | 複数の経路制御方式を扱う経路制御ソフトウェア。 |
| Simple Mail Transfer Protocol | SMTP | 電子メール送信で使う通信手順。 |
| ansible-playbookコマンド | - | Ansible Playbook を実行して自動構成処理を適用するコマンド。 |
| `cat` | - | ファイル内容を標準出力へ表示するコマンド。 |
| `curl` | - | URL を指定してデータ送受信を行うコマンド。 |
| `dig` | - | DNS 問い合わせ結果を詳細表示するコマンド。 |
| `docker` | - | コンテナイメージやコンテナの作成, 実行, 管理を行うコマンド。 |
| `getent` | - | システムの名前解決データベースを参照するコマンド。 |
| `journalctl` | - | systemd ジャーナルのログを参照するコマンド。 |
| `kubectl` | - | Kubernetesクラスタを操作するためのコマンドラインツール。 |
| `ls` | - | ファイルやディレクトリの一覧を表示するコマンド。 |
| makeコマンド | make | Makefile に定義された処理を実行するコマンド。 |
| `nslookup` | - | 名前解決結果を確認するコマンド。 |
| `sleep` | - | 指定秒数だけ処理を待機するコマンド。 |
| `ssh` | - | 遠隔ホストへ安全に接続して操作するコマンド。 |
| `systemctl` | - | systemd 管理下のサービスを起動, 停止, 状態確認するコマンド。 |
| `trap` | - | シェルスクリプトでシグナル受信時の処理を設定するコマンド。 |
| デバッグ | - | 不具合の原因を調査し修正する作業。 |
| ノード | - | ネットワークに接続された機器または処理単位。 |
| ログイン | - | 利用者認証を行って利用を開始する操作。 |
| ロード | - | 記憶媒体から実行環境へ読み込む処理。 |
| ローカルレジストリ | - | 実行中ホストまたは同一環境内で運用する成果物保管先。 |
| 対象ホスト | - | Playbook による設定変更や導入処理の適用先となるホスト。 |
| sudoコマンド | sudo | 一時的に管理者権限でコマンドを実行するためのコマンド。 |

## 概要

[nicolaka/netshoot](https://github.com/nicolaka/netshoot) をベースに, ポートスキャンツール などの悪用される恐れのあるツール群を除去したネットワーク診断用コンテナイメージを構築し, Kubernetes クラスタに配布するロールです。本ロールは, セキュリティポリシー上 nmap 等のポートスキャンツールを搭載できない環境においても, tcpdump, ping, curl 等のネットワーク検証ツールを Pod として使用可能にします。
本ロールは, `inventory/hosts`内の`k8s_management`グループに記載されたノード(Kubernetesコントロールプレインノード)の構築処理の一環として実行されます。

このロールは以下の手順でコンテナイメージを構築し, Kubernetes クラスタへ配布します。

1. [nicolaka/netshoot](https://github.com/nicolaka/netshoot) のソースコードを GitHub から取得する
2. `netshoot-no-portscan.patch` を Dockerfile に適用して nmap 系パッケージを除去する
3. Docker を使用してコンテナイメージをビルドし, tar ファイルとして保存する
4. 構築したイメージを以下のいずれかの方法で Kubernetes ノードへ配布する
   - containerd 直接登録モード: `k8s-register-image` ロールを使用してコントロールプレーン/ワーカノードの containerd に直接インポートする
   - ローカルレジストリ登録モード: Docker でローカルレジストリへ push する
5. Kubernetes 向けのデバッグ用 Pod マニフェストファイルを生成する

### 標準のnicolaka/netshootとの相違

ポートスキャン, フラッディング攻撃, DoS攻撃などに悪用される恐れがある以下のツール群を除去しています。

|ツール|機能概要|参考サイト|
|---|---|---|
|nmap,nmap-nping,nmap-scripts|ポートスキャンツール|[nmap公式サイト](https://nmap.org/)|
|bird|BGP/OSPF routing デーモン|[The BIRD Internet Routing Daemon](https://bird.network.cz/)|
|fping|並列ping|[fping公式サイト](https://fping.org/)|
|scapy|パケット生成ライブラリ|[scapy公式サイト](https://scapy.net/)|
|swaks|SMTPテストツール|[Swaks - Swiss Army Knife for SMTP](https://github.com/jetmore/swaks)|
|fortio|マイクロサービス(HTTP,gRPC)用ロードテストツール|[Fortio公式サイト](https://fortio.org/)|

### ポートスキャンツール除去の仕組み

`files/netshoot-no-portscan.patch` を [nicolaka/netshoot](https://github.com/nicolaka/netshoot) の Dockerfile に適用することで, 以下のパッケージの Alpine Linux `apk` インストール行を削除します。

```
- nmap
- nmap-nping
- nmap-scripts
- bird
- fping
- scapy
- swaks
```

また, コンテナ生成時の, `fortio`の導入処理を削除しています。

### 主な処理

#### コンテナイメージ構築処理 (`build-netshoot.yml`)

`run_once: true` で指定されており, 複数ホストへの並列実行時でも1回のみ実行されます。

1. 作業ディレクトリ (`netshoot_work_dir`) を削除して再作成する
2. GitHub から netshoot ソースコードを `git clone` する
3. `netshoot-no-portscan.patch` を Dockerfile に適用して nmap 系パッケージを除去する
4. `build-netshoot.sh.j2` テンプレートからシェルスクリプトを生成する
5. シェルスクリプトを実行して `docker build` と `docker save` を行う
6. 生成された tar ファイルを制御ホストの `netshoot_output_dir_on_control_host` に転送する

#### containerd 直接登録による配布処理 (`distribute-netshoot.yml`)

`netshoot_image_registry` が未設定の場合に実行されます。`k8s-register-image` ロールを使用します。

1. コントロールプレーンノードへの登録:
   - インベントリの `k8s_ctrlplane` グループからコントロールプレーンホスト一覧を自動解決する
   - 制御ホストから各コントロールプレーンノードへ tar ファイルを転送し, containerd にインポートする
2. ワーカノードの自動検出:
   - `netshoot_kubeconfig_path` に指定した kubeconfig を参照し, `kubectl` でワーカノード一覧を取得する
   - 検出したワーカノードを動的インベントリに追加する
3. ワーカノードへの登録:
   - 動的インベントリのワーカノードへ tar ファイルを転送し, containerd にインポートする
   - `netshoot_cleanup_remote_tar` が `true` の場合, インポート後に一時 tar ファイルを削除する

#### ローカルレジストリ登録処理 (`register-netshoot.yml`)

`netshoot_image_registry` が設定されている場合に実行されます。全タスクが `delegate_to: localhost` と `run_once: true` で制御ホスト上で1回のみ実行されます。

1. `docker load` で制御ホスト上の tar ファイルからイメージをロードする
2. `docker tag` で `{{ netshoot_image_registry }}:{{ netshoot_no_portscan_version }}` のタグを付与する
3. `docker push` でローカルレジストリへ push する

#### マニフェスト作成処理 (`create-manifest.yml`)

マニフェスト格納先ディレクトリを作成し, `netshoot-no-portscan.yml.j2` テンプレートからマニフェストファイルを生成します。このタスクは配布モードに関わらず常に実行されます。

## 前提条件

- 制御ホストと構築ホスト上に Docker がインストールされていること
- 制御ホストから Kubernetes クラスタの各ノードへ SSH 接続可能であること
- `k8s-register-image` ロールが同一リポジトリ内に存在すること (containerd 直接登録モードで必要)
- ローカルレジストリ登録モードを使用する場合は, 制御ホストの `/etc/docker/daemon.json` に `insecure-registries` が設定されていること (詳細は, `[roles/docker-ce/Readme.md](../roles/docker-ce/Readme.md)参照)
- Kubernetes コントロールプレイン/ワーカノードの containerdのレジストリ設定 ( `/etc/containerd/certs.d/<レジストリ名>/hosts.toml` )が, ローカルレジストリを参照可能なように設定されていること (詳細は, `[roles/k8s-common/Readme.md](../roles/k8s-common/Readme.md)参照)

## 実行方法

`vars/all-config.yml`, または, K8sコントロールプレインノードのhost_varsファイル内で, `netshoot_no_portscan_enabled` を `true` に設定したうえで, 本ロールを実行します。本ロールの実行手順は以下の通りです:

1. site.yml 経由で実行する:
    ```bash
    ansible-playbook -i inventory/hosts site.yml
    ```
2. ロールを単独で対象ホストに実行する:
    ```bash
    ansible-playbook -i inventory/hosts site.yml --tags netshoot-no-portscan
    ```
3. makeターゲットで本ロールの実行を指示する:
    ```bash
    make run_netshoot_no_portscan
    ```

### コンテナイメージの展開(デプロイ)方法

本ロール実行後, コントロールプレーンノードで以下のコマンドでマニフェストを適用することで, 本ロールで作成したコンテナイメージをK8sクラスタに展開します:

```bash
kubectl apply -f /opt/maintenance/netshoot/manifests/netshoot-no-portscan.yml
kubectl get pod netshoot
```

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `netshoot_no_portscan_enabled` | `false` | `true` に設定するとロールの処理が有効になる。 |
| `netshoot_no_portscan_version` | `"v0.16"` | 使用する netshoot のバージョン。 使用する版数に応じて設定することを想定。|
| `netshoot_no_portscan_image` | `"nicolaka/netshoot:v0.16"` | ビルドするコンテナイメージ名。 `netshoot_no_portscan_version`変数に基づいて設定される内部変数であり変更しないこと。|
| `netshoot_no_portscan_image_file` | `"nicolaka-netshoot-v0.16.tar"` | tar 形式で保存するコンテナイメージファイル名。 `netshoot_no_portscan_version`変数に基づいて設定される内部変数であり変更しないこと。|
| `netshoot_src_url` | `"https://github.com/nicolaka/netshoot"` | netshoot ソースコードの取得元 URL。 |
| `netshoot_build_host` | `"localhost"` | コンテナイメージをビルドするホスト。 |
| `netshoot_work_dir` | `"/tmp/netshoot-work"` | ビルドホスト上の作業ディレクトリ。 |
| `netshoot_build_dir` | `"{{ netshoot_work_dir }}/build"` | Dockerfile が配置されるディレクトリ。 |
| `netshoot_output_dir` | `"{{ netshoot_work_dir }}/output"` | ビルドホスト上のイメージ出力先ディレクトリ。 |
| `netshoot_output_dir_on_control_host` | `"{{ netshoot_work_dir }}/artifacts"` | 制御ホスト上のイメージ保管先ディレクトリ。 |
| `netshoot_docker_build_network` | `"host"` | `docker build` 時のネットワークモード。`host` を指定するとビルドコンテナがホストの DNS 設定を引き継ぎ, `apk` の名前解決失敗を防ぐ。 |
| `netshoot_unqualified_image_registry` | `"registry1.local"` | 未修飾名イメージ参照時に補完するレジストリ名。 |
| `netshoot_remote_cache_dir` | `"/tmp/netshoot-register"` | 各 K8s ノード上のイメージ転送先一時ディレクトリ。 |
| `netshoot_kubeconfig_path` | `"/etc/kubernetes/admin.conf"` | ワーカノード自動検出に使用する kubeconfig のパス。 |
| `netshoot_registry_wait_timeout` | `120` | ローカルレジストリエンドポイント待機のタイムアウト時間(単位: 秒)。 |
| `netshoot_registry_wait_delay` | `2` | ローカルレジストリエンドポイント待機の開始遅延時間(単位: 秒)。 |
| `netshoot_registry_wait_sleep` | `2` | ローカルレジストリエンドポイント待機の再試行間隔(単位: 秒)。 |
| `netshoot_registry_wait_connect_timeout` | `3` | ローカルレジストリエンドポイント待機時の接続タイムアウト時間(単位: 秒)。 |
| `netshoot_registry_wait_delegate_to` | `"localhost"` | ローカルレジストリエンドポイント待機を実行する接続元ホスト名またはIPアドレス。 |
| `netshoot_registry_wait_retries` | `5` | ローカルレジストリエンドポイント待機の再試行回数。 |
| `netshoot_image_registry` | `""` | ローカルレジストリ登録モードで使用するレジストリの URL。未設定の場合は containerd 直接登録モードを使用します。設定例: `"registry1.local:5000/netshoot"` `vars/all-config.yml`, または, K8sコントロールプレインのhost_varsファイルで設定することを想定しています。|
| `netshoot_k8s_manifest_dir` | `"/opt/maintenance/netshoot/manifests"` | K8sコントロールノード上のマニフェストファイルの格納先ディレクトリ。 |
| `netshoot_manifest_file_path` | `"{{ netshoot_k8s_manifest_dir }}/netshoot-no-portscan.yml"` | 生成されるマニフェストファイルのパス。 |
| `netshoot_k8s_namespace` | `"default"` | Pod を展開する Kubernetes の名前空間 ( namespace )。 |
| `netshoot_k8s_pod_name` | `"netshoot"` | 展開する Pod の名前。 |

## テンプレートと生成ファイル

| テンプレートファイル名 | 出力先パス | 説明 |
| --- | --- | --- |
| `templates/netshoot-no-portscan.yml.j2` | `{{ netshoot_manifest_file_path }}` (既定: `{{ netshoot_manifest_file_path }}`) | netshoot Pod のマニフェストファイル。`imagePullPolicy` と参照イメージを自動選択します。 |
| `templates/build-netshoot.sh.j2` | `{{ netshoot_build_dir }}/build-netshoot.sh` (既定: `{{ netshoot_build_dir }}/build-netshoot.sh`) | `docker build` と `docker save` を実行するシェルスクリプト。 |

### コンテナイメージをK8sクラスタに展開するためのマニフェストの生成

本ロールでは, 生成したコンテナイメージを投入するためのマニュフェストファイルをコントロールプレイン上に保存します。本マニュフェストは,
`templates/netshoot-no-portscan.yml.j2` テンプレートファイルから生成されます。

#### 生成されるマニュフェストの仕様

生成されるマニフェストの Pod 仕様は以下の通りです。

- `NET_ADMIN`, `NET_RAW` ケーパビリティを付与し, `ip`, `tcpdump` 等のネットワークツールが使用可能
- コマンドは `sleep infinity` で Pod を起動し続け, `kubectl exec` で接続して使用する
- `restartPolicy: Never` で自動再起動しない
- `hostNetwork: false`, `dnsPolicy: ClusterFirst` で Pod 間通信のデバッグに適した設定

マニュフェストの適用例, [nicolaka/netshoot](https://github.com/nicolaka/netshoot)のPodに接続するコマンドの例を以下に示します:

```yaml
# マニフェスト適用例
kubectl apply -f /opt/maintenance/netshoot/manifests/netshoot-no-portscan.yml

# Pod に接続してネットワーク診断を実行する例
kubectl exec -it netshoot -- /bin/bash
```

#### `netshoot_image_registry` 変数によるイメージ参照先とpullポリシーの切り替え

本ロールでは, `netshoot_image_registry`変数の定義に基づいてイメージ参照先とイメージ取得方法(`imagePullPolicy`)を以下のように出力します:

| 条件 | イメージ参照先 (既定: イメージ参照先) | imagePullPolicy |
| --- | --- | --- |
| `netshoot_image_registry` が定義されており, かつ, 空文字列でない | ローカルレジストリからイメージを取得(pull)するよう設定(`{{ netshoot_image_registry }}:{{ netshoot_no_portscan_version }}`) (既定: ローカルレジストリからイメージを取得(pull)するよう設定(`{{ netshoot_image_registry }}:{{ netshoot_no_portscan_version }}`)) | `IfNotPresent` |
| `netshoot_image_registry` が未定義, または, 空文字列 | 各K8sノードのCRI内に登録されるイメージ名を設定(`{{ netshoot_no_portscan_image }}`) (既定: 各K8sノードのCRI内に登録されるイメージ名を設定(`{{ netshoot_no_portscan_image }}`)) | `Never` |

## 実行フロー

### コンテナイメージの構築と配布の流れ

```mermaid
flowchart TD
    A[開始] --> B[package.yml]
    B --> B1[build-netshoot.yml\nrun_once: true で1回のみ実行]
    B1 --> C{netshoot_image_registry\n設定あり?}
    C -- いいえ --> D[distribute-netshoot.yml\ncontainerd 直接登録モード]
    C -- はい --> E[register-netshoot.yml\nローカルレジストリ登録モード]
    D --> F[create-manifest.yml]
    E --> F
    F --> G[終了]
```

`tasks/package.yml`を起点に, コンテナイメージファイルの作成からK8sノード上のCRIへのコンテナイメージ登録, または, ローカルレジストリへのコンテナイメージ登録を実施します。

|ファイル|機能|
|---|---|
|`tasks/package.yml`|コンテナイメージの構築からローカルレジストリへの登録, または, 各K8sノード上のCRIへのコンテナイメージ登録までの処理フローを定義|
|`tasks/build-netshoot.yml`|[nicolaka/netshoot](https://github.com/nicolaka/netshoot) のコンテナイメージファイルを作成する処理を定義。 本処理は, 複数ホストへの並列実行時でも構築ホスト上でのビルドが1回だけ実行されるよう`run_once: true`を指定して実行される。|
|`tasks/distribute-netshoot.yml`|`tasks/build-netshoot.yml`で作成したコンテナイメージをK8sノード(コントロールプレイン/ワーカノード)上で動作しているCRIに登録する処理を定義。`netshoot_image_registry`変数が未定義, または, 空文字列の場合に実行される。|
|`tasks/register-netshoot.yml`|`tasks/build-netshoot.yml`で作成したコンテナイメージをローカルレジストリに登録する処理を定義。`netshoot_image_registry`変数が定義されており, かつ, 空文字列でない場合に実行される。|
|`tasks/create-manifest.yml`|[nicolaka/netshoot](https://github.com/nicolaka/netshoot) のコンテナをK8sクラスタに展開(デプロイ)するためのサンプルマニュフェストファイルを生成する処理を定義。|

### イメージ配布モードの選択

`netshoot_image_registry` の設定有無によって配布モードが自動的に選択されます。

- `containerd 直接登録モード` `netshoot_image_registry` が未定義または空文字の場合に選択されるモードです。K8sクラスタを構成するノード(コントロールプレイン/ワーカーノード)上のCRIにコンテナイメージを登録します。
- `ローカルレジストリ登録モード` `netshoot_image_registry` が定義され, かつ, 空文字列でない場合に選択されるモードです。ローカルレジストリにコンテナイメージを登録します。

#### containerd 直接登録モード

`netshoot_image_registry` が未設定または空文字の場合に選択されます。`k8s-register-image` ロールを使用して, 制御ホスト上の tar ファイルを SSH 経由で各ノードに転送し, `ctr` コマンドで containerd に直接登録(インポート)します。

コントロールプレーンノードへの登録後, `kubectl` でワーカノード一覧を自動検出し, 各ワーカノードにも同様に登録します。

生成されるマニフェストの `imagePullPolicy` は `Never` となり, ノード上にキャッシュ済みのイメージを使用します。

#### ローカルレジストリ登録モード

`netshoot_image_registry` に値が設定されている場合に選択されます。制御ホスト上で, dockerコマンド( `docker load`, `docker tag`, `docker push` )を実行することで, `netshoot_image_registry`で指定されたローカルレジストリにコンテナイメージを登録します。

`netshoot_image_registry`の設定例は以下の通り:

```yaml
netshoot_image_registry: "registry1.local:5000/netshoot"
```

上記設定の場合, 本ロールで作成されたコンテナイメージは, `registry1.local:5000/netshoot:v0.16` としてレジストリに登録されます。なお, `v0.16`部分は, `netshoot_no_portscan_version`変数の値に応じて設定されます。

生成されるマニフェストの `imagePullPolicy` は `IfNotPresent` となり, ローカルレジストリからのイメージ取得を行います。

## 検証ポイント

**コンテナイメージのビルド確認**

playbook実行に成果物であるコンテナイメージtarファイルが作成されていることを確認するためのコマンド例を以下に示します:

```bash
# 制御ホスト上で tar ファイルが生成されたことを確認する
ls -la /tmp/netshoot-work/output/
ls -la /tmp/netshoot-work/artifacts/
```

実行結果の例:
```bash
$ ls -la /tmp/netshoot-work/output/
合計 207072
drwxr-xr-x 2 root root      4096  7月 12 14:33 .
drwxr-xr-x 5 root root      4096  7月 12 14:33 ..
-rw-r--r-- 1 root root 212026880  7月 12 14:33 nicolaka-netshoot-v0.16.tar
$ ls -la /tmp/netshoot-work/artifacts/
合計 207072
drwxrwxrwx 2 root root      4096  7月 12 14:33 .
drwxr-xr-x 5 root root      4096  7月 12 14:33 ..
-rw-r--r-- 1 root root 212026880  7月 12 14:33 nicolaka-netshoot-v0.16.tar

```

**ローカルレジストリへの登録確認 (ローカルレジストリ登録モードの場合)**

ローカルレジストリのエンドポイントが`http://registry1.local:5000`の場合の例を以下に示します:

レジストリ上のリポジトリ一覧を確認するコマンド例は以下の通り:
```bash
curl http://registry1.local:5000/v2/_catalog
```

期待される出力("repositories"のリストに"netshoot"が含まれること):
```json
{"repositories":["netshoot"]}
```

レジストリ上のnetshoot のタグ一覧を確認するコマンド例は以下の通り:
```bash
curl http://registry1.local:5000/v2/netshoot/tags/list
```

期待される出力:
```json
{"name":"netshoot","tags":["v0.16"]}
```

実行結果の例:
```bash
$ curl http://registry1.local:5000/v2/_catalog
{"repositories":["netshoot"]}
$ curl http://registry1.local:5000/v2/netshoot/tags/list
{"name":"netshoot","tags":["v0.16"]}
```

**containerd への登録確認 (containerd 直接登録モードの場合)**

containerdへのコンテナイメージ登録が正常に行われていることを
K8sのコントロールプレーンノードとワーカーノードで確認するためのコマンド例を以下に示します:

```bash
sudo crictl images | grep netshoot
```

コントロールプレーンノードで確認する
```bash

ssh ansible@k8sctrlplane01 "sudo crictl images | grep netshoot"

# ワーカノードで確認する
ssh ansible@k8sworker0101 "sudo crictl images | grep netshoot"
```

期待される出力の例:
```bash
docker.io/nicolaka/netshoot                v0.16               c52d5254f8d9f       212MB
registry1.local/nicolaka/netshoot          v0.16               c52d5254f8d9f       212MB
```
以下の点を確認します:
- nicolaka/netshootを含むエントリが出力されること(上記の場合, `docker.io/nicolaka/netshoot`, `registry1.local/nicolaka/netshoot`の2件のエントリ)
- コンテナイメージの版数が`netshoot_no_portscan_version`変数で指定した版数と一致すること(上記の場合, `v0.16`)
- `netshoot_unqualified_image_registry`変数で指定したエンドポイントと一致するエントリが含まれること(上記の場合, `docker.io/nicolaka/netshoot`で始まるエントリ)
- レジストリのエンドポイントが`netshoot_image_registry`変数で指定したエンドポイントと一致するエントリが含まれること(上記の場合, `registry1.local/nicolaka/netshoot`で始まるエントリ)

実行結果の例:
```bash
$ sudo crictl images | grep netshoot
docker.io/nicolaka/netshoot                v0.16               c52d5254f8d9f       212MB
registry1.local/nicolaka/netshoot          v0.16               c52d5254f8d9f       212MB
```

**マニフェストの適用と Pod の起動確認**

コントロールプレインノード上で, 本ロールにより配置されたマニュフェスト(規定では, `/opt/maintenance/netshoot/manifests/netshoot-no-portscan.yml`)を用いて, Podの展開(デプロイ)から起動までを確認する手順を以下に示します(括弧内はコマンド例):

1. Podを展開し, `pod/netshoot configured`と表示されること(`kubectl apply -f /opt/maintenance/netshoot/manifests/netshoot-no-portscan.yml`)
2. Podの状態を確認し, STATUSが`Running`と表示されること(`kubectl get pod netshoot -o wide`)
3. Podの詳細情報を確認し, エラーメッセージが出ていないこと(`kubectl describe pod netshoot`)

上記のコマンド例をまとめると以下のようになります:
```bash
kubectl apply -f /opt/maintenance/netshoot/manifests/netshoot-no-portscan.yml
kubectl get pod netshoot -o wide
kubectl describe pod netshoot
```

実行結果の例:
```bash
$ kubectl apply -f /opt/maintenance/netshoot/manifests/netshoot-no-portscan.yml
pod/netshoot configured
$ kubectl get pod netshoot -o wide
NAME       READY   STATUS    RESTARTS   AGE   IP                         NODE            NOMINATED NODE   READINESS GATES
netshoot   1/1     Running   0          8h    fdb6:6e92:3cfb:208::4862   k8sworker0101   <none>           <none>
$ kubectl describe pod netshoot
Name:             netshoot
Namespace:        default
Priority:         0
Service Account:  default
Node:             k8sworker0101/fdad:ba50:248b:1::42
Start Time:       Sun, 12 Jul 2026 17:12:52 +0900
Labels:           app=netshoot
Annotations:      k8s.v1.cni.cncf.io/network-status:
                    [{
                        "name": "cilium",
                        "interface": "eth0",
                        "ips": [
                            "fdb6:6e92:3cfb:208::4862",
                            "10.244.8.40"
                        ],
                        "mac": "22:30:80:e9:fd:bd",
                        "default": true,
                        "dns": {},
                        "gateway": [
                            "fdb6:6e92:3cfb:208::fa41",
                            "10.244.8.153"
                        ]
                    }]
Status:           Running
IP:               fdb6:6e92:3cfb:208::4862
IPs:
  IP:  fdb6:6e92:3cfb:208::4862
  IP:  10.244.8.40
Containers:
  netshoot:
    Container ID:  containerd://20def482111801c80f65d7a0fc701328de62b688b4202e22b33a5c939c270955
    Image:         registry1.local:5000/netshoot:v0.16
    Image ID:      registry1.local:5000/netshoot@sha256:8a7b3c33919b02ed46e5448b2bab1b870a0ef59e8435b3b2cb2855e8c96e4cc9
    Port:          <none>
    Host Port:     <none>
    Command:
      /bin/bash
      -c
      trap : TERM INT; sleep infinity & wait
    State:          Running
      Started:      Sun, 12 Jul 2026 17:13:31 +0900
    Ready:          True
    Restart Count:  0
    Limits:
      cpu:     500m
      memory:  512Mi
    Requests:
      cpu:        100m
      memory:     128Mi
    Environment:  <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-gp65z (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True
  Initialized                 True
  Ready                       True
  ContainersReady             True
  PodScheduled                True
Volumes:
  kube-api-access-gp65z:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    ConfigMapOptional:       <nil>
    DownwardAPI:             true
QoS Class:                   Burstable
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:                      <none>
```

**[nicolaka/netshoot](https://github.com/nicolaka/netshoot)をPod内でネットワークツールが使用可能であることの確認方法**

Pod に接続してネットワークツールが使用可能であることを確認するためには, コンテナイメージ名(`netshoot`)を指定して, `kubectl exec -it`コマンドにより, コンテナ内に入り, [nicolaka/netshoot](https://github.com/nicolaka/netshoot)同梱のコマンド(pingなど)を実行します。

コマンド例を以下に示します:
```bash
kubectl exec -it netshoot -- ping -c 3 8.8.8.8
kubectl exec -it netshoot -- curl -I https://example.org
```

実行結果の例:
```bash
$ kubectl exec -it netshoot -- ping -c 3 8.8.8.8

PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=115 time=6.35 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=115 time=4.55 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=115 time=5.10 ms

--- 8.8.8.8 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 4.553/5.334/6.353/0.753 ms
$ kubectl exec -it netshoot -- curl -I https://example.org
HTTP/2 200
date: Sun, 12 Jul 2026 17:11:40 GMT
content-type: text/html
server: cloudflare
last-modified: Wed, 01 Jul 2026 17:50:18 GMT
allow: GET, HEAD
accept-ranges: bytes
age: 5
cf-cache-status: HIT
cf-ray: a1a1ab1f891f264a-NRT
```

## トラブルシューティング

### 1. Docker ビルドが失敗する場合

**実施対象ホスト**: 制御ホスト, 構築ホスト

**実行するコマンド**:

```bash
getent hosts dl-cdn.alpinelinux.org
dig dl-cdn.alpinelinux.org
grep -n 'netshoot_docker_build_network' vars/all-config.yml host_vars/*.yml
```

**確認ポイント**:

- DNS 名前解決が成功すること。
- netshoot_docker_build_network が host に設定されていること。
- apk update の名前解決失敗が継続する場合は, 構築ホスト側 DNS 設定を確認すること。

### 2. containerd へのイメージ登録が失敗する場合

**実施対象ホスト**: Kubernetes のコントロールプレーンノード, ワーカノード

**実行するコマンド**:

```bash
sudo crictl images | grep netshoot
sudo journalctl -u containerd -n 50 --no-pager
```

**確認ポイント**:

- 各ノードで netshoot イメージが一覧に表示されること。
- containerd ログに import 失敗のエラーが出ていないこと。

### 3. ローカルレジストリへの push が失敗する場合

**実施対象ホスト**: 制御ホスト

**実行するコマンド**:

```bash
cat /etc/docker/daemon.json
docker info | grep -A5 "Insecure Registries"
```

**確認ポイント**:

- insecure-registries に netshoot_image_registry のエンドポイントが含まれること。
- HTTP レジストリ利用時に Docker が HTTPS 接続を試行していないこと。
- 修正後は sudo systemctl restart docker で設定を反映すること。

### 4. Pod が起動しない場合

**実施対象ホスト**: コントロールプレーンノード, ワーカノード

**実行するコマンド**:

```bash
kubectl get pod netshoot -o wide
kubectl describe pod netshoot
cat /etc/containerd/certs.d/<ローカルレジストリのエンドポイント>/hosts.toml
sudo crictl images | grep netshoot
```

**確認ポイント**:

- Pod の状態が ErrImagePull 又は ImagePullBackOff の場合, レジストリ接続設定を優先確認すること。
- hosts.toml の capabilities に pull が含まれ, skip_verify が運用方針どおりであること。
- imagePullPolicy が Never の場合, Pod 配置ノードに netshoot イメージが存在すること。
- 設定修正後は containerd 再起動と Pod 再作成で反映を確認すること。

## 注意事項

- コンテナイメージファイルの生成は, `netshoot_build_host`変数で指定された構築ホスト(規定は, Ansibleの制御ホスト(`localhost`))上で実施します。コンテナイメージファイルの生成処理中で, dockerコマンドを使用するため, 構築ホストに Docker がインストールされていない場合はビルドに失敗します。
- 複数ホストに同時に Playbook を適用した場合でも, ビルドおよびレジストリへの 登録(`push`) は1回のみ実行されます(playbook中で, `run_once: true` を指定することで, 代表となるノードでのみ実施),。
- マニュフェスト中のイメージ取得方式指定に, `imagePullPolicy: Never` が指定されている場合, イメージが各ノードの containerd に登録されていることが前提となります。新しいノードを追加した場合は, ロールを再実行して登録してください。
- マニュフェスト中のイメージ取得方式指定に, `imagePullPolicy: IfNotPresent` が指定されている場合, ローカルレジストリからk8sノードへのコンテナイメージをダウンロード可能となっていることが前提となります。Podの展開対象となる各K8sノードからローカルレジストリへアクセスできることを確認してください。

## 参考資料

### 公式ドキュメント

- netshoot: https://github.com/nicolaka/netshoot

- [nicolaka/netshoot](https://github.com/nicolaka/netshoot) - ネットワーク診断コンテナイメージ, 本ロールでは, [nicolaka/netshoot](https://github.com/nicolaka/netshoot) から提供されるコンテナイメージ中に含まれるポートスキャン系ツールを除去したコンテナイメージファイルを生成します。
- [containerd hosts configuration](https://github.com/containerd/containerd/blob/main/docs/hosts.md) - containerd のレジストリ設定マニュアル
- [kubectl exec](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_exec/) - Pod への接続コマンドマニュアル
- [roles/docker-ce/Readme.md](../roles/docker-ce/Readme.md) - 本playbook中のローカルレジストリの設定について記載した文書
- [roles/k8s-common/Readme.md](../roles/k8s-common/Readme.md) - 本playbook中のローカルレジストリをK8sのノードから使用するための設定について記載した文書
