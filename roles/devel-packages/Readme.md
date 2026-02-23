# devel-packages ロール

## 概要

このロールは, 開発環境に必要なパッケージ群を導入し, GUI を無効化してコンソールモードへ切り替えます。Kubernetes 開発向けの Python パッケージ導入と, kubectl シェル補完の設定にも対応します。

## 用語

| 正式名称 | 略称 | 意味 |
| --- | --- | --- |
| Operating System | OS | 基本ソフトウエア。 |
| Graphical User Interface | GUI | 画面操作を前提とする利用形態。 |
| Kubernetes | K8s | コンテナの運用基盤。 |
| kubectl | - | Kubernetes を操作するコマンド。 |

## 前提条件

- 対象 OS: Debian/Ubuntu 系 (Ubuntu24.04を想定), RHEL 系 (AlmaLinux9.6を想定)
- Ansible 2.15 以降
- リモートホストへの SSH 接続が確立されていること
- sudo 権限が利用可能であること

## 実行フロー

1. パッケージ定義と共通変数を読み込みます。
2. `devel_packages` をインストールします。
3. `k8s_python_packages_enabled` / `k8s_python_devel_packages_enabled` が有効な場合, 対応する Python パッケージをインストールします。
4. `kubectl_completion_enabled` が有効で kubectl が存在する場合, シェル補完ファイルを配置します。
5. パッケージ更新があった場合, GUI を無効化するハンドラが実行されます。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| `devel_packages` | (OS 別) | 開発パッケージ群。OS 別の定義を利用します。 |
| `kubectl_completion_enabled` | `true` | kubectl の bash/zsh 補完を設定するか。 |
| `k8s_python_packages_enabled` | `true` | Kubernetes 開発向け Python パッケージを導入するか。 |
| `k8s_python_devel_packages_enabled` | `true` | Kubernetes 開発向け Python ヘッダ等を導入するか。 |

## デフォルト動作

- `devel_packages` のインストールは常に実行されます。
- `k8s_python_packages_enabled` または `k8s_python_devel_packages_enabled` が `false` の場合, 該当パッケージは導入されません。
- `kubectl_completion_enabled` が `true` でも, kubectl が存在しない場合は補完設定を行いません。

## 主な処理

- `devel_packages` を `state: latest` でインストールし, 変更時に GUI 無効化を通知します。
- Kubernetes 開発向け Python パッケージを条件付きで導入します。
- kubectl の bash/zsh 補完ファイルを生成し, 既定の配置先に配置します。

## 注意事項

- `google-chrome-stable` を含むパッケージを導入する場合, リポジトリ追加は別ロールで実施する前提です。
- GUI 無効化は `systemctl set-default multi-user.target` で実施されます。GUI が必要なノードでは注意してください。

## テンプレート/ファイル

テンプレートから出力されるファイルはありません。
一方で, 本ロールはテンプレートを用いずに以下のファイルを作成/更新します。

| ファイル | 既定の配置先 (Debian/Ubuntu) | 既定の配置先 (RHEL) | 作成条件 | 説明 |
| --- | --- | --- | --- | --- |
| kubectl bash 補完 | `/usr/share/bash-completion/completions/kubectl` | `/usr/share/bash-completion/completions/kubectl` | `kubectl_completion_enabled: true` かつ kubectl が存在する場合 | kubectl bash 補完ファイル。 |
| kubectl zsh 補完 | `/usr/share/zsh/vendor-completions/_kubectl` | `/usr/share/zsh/site-functions/_kubectl` | `kubectl_completion_enabled: true` かつ kubectl が存在する場合 | kubectl zsh 補完ファイル。 |

## 設定例

Kubernetes 開発向け Python パッケージと kubectl 補完を無効化する例です。

**記載先**:
- host_vars/ホスト名.yml または group_vars/all/all.yml

**記載例**:

```yaml
kubectl_completion_enabled: false
k8s_python_packages_enabled: false
k8s_python_devel_packages_enabled: false
```

**各項目の意味**:

| 項目 | 説明 | 記載例での値 | 動作 |
| --- | --- | --- | --- |
| `kubectl_completion_enabled` | kubectl 補完を有効化する場合は, `true`に設定する。 | `false` | `true`に設定すると補完ファイルを生成します。 |
| `k8s_python_packages_enabled` | Python ランタイム系を導入する場合は, `true`に設定する。 | `false` | `true`に設定するとK8s Python ランタイムを導入します。 |
| `k8s_python_devel_packages_enabled` | Python 開発ヘッダ等を導入する場合は, `true`に設定する。 | `false` | `true`に設定すると Kubernetes関連開発作業をPythonで実施するために必要なPython開発用パッケージを導入します。 |

## 検証ポイント

本節では, `devel-packages` ロール実行後に設定が反映されていることを確認する方法について説明します。

### 前提条件

- `devel-packages` ロールが正常に完了していること(`changed` または `ok` の状態)。
- リモートホストへ SSH で接続可能であること。
- sudo 権限が利用可能であること。

### 1. パッケージ導入の確認

導入対象のパッケージが存在するかを確認します。

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

### 2. GUI 無効化の確認

```bash
systemctl get-default
```

**期待される出力例**:

```
multi-user.target
```

**確認ポイント**:
- `multi-user.target` になっていること。

### 3. kubectl 補完ファイルの確認

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

- パッケージ導入に失敗する場合は, リポジトリ設定とネットワーク疎通を確認してください。
- GUI が無効化されない場合は, `systemctl set-default multi-user.target` の実行結果を確認してください。
- kubectl 補完が導入されない場合は, `kubectl_completion_enabled` と kubectl の有無を確認してください。