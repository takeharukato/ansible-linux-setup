# python-k8s-client-local ロール

本ロールは, Python 言語版 Kubernetes client を対象ノード上で直接 pip install せずに, 構築ホスト上のコンテナでローカルパッケージ (deb/rpm) を生成して配布, 導入するロールである。
- [python-k8s-client-local ロール](#python-k8s-client-local-ロール)
  - [概要](#概要)
  - [前提条件](#前提条件)
  - [実行フロー](#実行フロー)
  - [主要変数](#主要変数)
  - [パッケージ導入確認方法](#パッケージ導入確認方法)
    - [Debian/Ubuntu環境での実行例](#debianubuntu環境での実行例)
    - [RedHat/AlmaLinux環境での実行例](#redhatalmalinux環境での実行例)
  - [注意事項](#注意事項)

## 概要

- 他のロールからの入力として python_k8s_client_version_spec (例: ~=31.0, ==31.0.0) を受け取り, ローカルパッケージを作成する。
- 導入物には kubernetes パッケージと packaging パッケージを含む仮想環境 (venv) が含まれる。
- ローカルパッケージの転送経路は, 構築ホスト -> 制御ノード -> 対象ホストである。
- 導入後に, venv 内 Python で kubernetes 版数が要求 spec を満たすことを検証する。

## 前提条件

- 対象 OS: Ubuntu24.04, RHEL9.6 (Alma Linuxを想定)。
- 構築ホストでコンテナランタイム (docker など) が利用可能であること。
- 本ロール呼び出し時に, python_k8s_client_version_spec を空文字列にしないこと。本変数の設定は呼び出し元ロールの責務とする。
- 構築ホストと制御ノード間, 制御ノードと対象ホスト間でdeb/rpmパッケージ転送のための通信が可能であること。

## 実行フロー

1. load-params.yml で OS別/共通変数を読み込む。
2. package.yml で, check mode 以外の場合にパッケージ構築/導入を実行する。
3. Debian系では build-python-client-source-deb.yml でコンテナ内ビルドを行い, install-python-client-local-deb.yml で導入する。
4. RHEL系では build-python-client-source-rpm.yml でコンテナ内ビルドを行い, install-python-client-local-rpm.yml で導入する。
5. 導入後に venv 内 Python で kubernetes を import し, 版数が python_k8s_client_version_spec を満たすことを確認する。

## 主要変数

| 変数名 | 既定値 | 説明 |
| --- | --- | --- |
| python_k8s_client_version_spec | "" | kubernetes の版数指定。例: ~=31.0, ==31.0.0。通常は呼び出し元ロールから渡されるため, `vars/all-config.yml`や`host_vars`内の設定ファイルから設定する変数ではない。 |
| python_k8s_client_deb_package_name | "python-k8s-client" | Debian系ローカルパッケージ名。 |
| python_k8s_client_rpm_package_name | "python-k8s-client" | RHEL系ローカルパッケージ名。 |
| python_k8s_client_install_dir | "/opt/k8s-devel/python-client" | venv 導入先ディレクトリ。 |
| python_k8s_client_build_host | "localhost" | 構築ホスト。 |
| python_k8s_client_build_workspace | "/tmp/python-k8s-client-build" | 構築ワークスペース。 |
| python_k8s_client_build_output_dir | "{{ python_k8s_client_build_workspace }}/output" | 成果物出力先。 |
| python_k8s_client_install_deb_lock_wait_seconds | 600 | Debian系 apt ロック待機秒数。 |
| python_k8s_client_build_container_runtime | "docker" | コンテナランタイム。 |
| python_k8s_client_build_container_network_mode | "host" | コンテナネットワークモード。 |
| python_k8s_client_build_container_image_debian | "python-k8s-client-build-ubuntu:24.04" | Debian系ビルド用イメージ名。 |
| python_k8s_client_build_container_image_rhel | "python-k8s-client-build-almalinux:9.6" | RHEL系ビルド用イメージ名。 |

## パッケージ導入確認方法

python版 kubernetes clientが導入されていることを確認するためのコマンドは以下の通り:

```shell
# venv で版数確認
/opt/k8s-devel/python-client/venv/bin/python -c 'import kubernetes; print(kubernetes.__version__)'

# Debian系: パッケージ導入確認
dpkg --list|egrep python-k8s-client

# RHEL系: パッケージ導入確認
rpm -q python-k8s-client
```

`/opt/k8s-devel/python-client/venv/bin/python -c 'import kubernetes; print(kubernetes.__version__)'`の出力中で返される版数と導入されているパッケージの版数とが一致することを確認する。


### Debian/Ubuntu環境での実行例

Debian/Ubuntu環境での実行例を以下に示す:

```shell
$ /opt/k8s-devel/python-client/venv/bin/python -c 'import kubernetes; print(kubernetes.__version__)'
31.0.0
$ dpkg --list|egrep python-k8s-client
ii  python-k8s-client                     31.0.0-1                                all          Offline Python Kubernetes client 31.0.0
```

### RedHat/AlmaLinux環境での実行例

Redhat/AlmaLinux環境での実行例を以下に示す:

```shell
$ /opt/k8s-devel/python-client/venv/bin/python -c 'import kubernetes; print(kubernetes.__version__)'
 rpm -q  python-k8s-client
python-k8s-client-31.0.0-1.el9.x86_64
[kube@k8sworker0201 ~]$ /opt/k8s-devel/python-client/venv/bin/python -c 'import kubernetes; print(kubernetes.__version__)'
31.0.0
$ rpm -q python-k8s-client
python-k8s-client-31.0.0-1.el9.x86_64
```


## 注意事項

- ansibleがcheck mode で動作している場合は, 本処理をスキップする
- 生成パッケージの署名付与は行わない。
