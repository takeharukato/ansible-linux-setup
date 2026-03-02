#!/usr/bin/env bash
# -*- mode: bash; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (c) 2025 TAKEHARU KATO
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。

# Virtual Clusterテナント用kubeconfig生成スクリプト
# 指定したテナントの kubeconfig を生成して標準出力に出力します。
# VirtualClusterテナント環境にアクセスするため必要な認証情報をまとめます。

set -euo pipefail

readonly SCRIPT_NAME="$(basename "$0")"
readonly VC_MANAGER_NS="${VC_MANAGER_NS:-vc-manager}"
readonly KUBE_VERSION="1.31"

usage() {
  cat <<EOF
使用方法: $SCRIPT_NAME <テナント名> [オプション]

説明:
  VirtualClusterテナント用のkubeconfigを生成し、標準出力に出力します。
  生成されたkubeconfigは、テナント側のAPIサーバーに接続するために必要な
  認証情報(CA証明書, トークン, APIエンドポイント)を含みます。

引数:
  <テナント名>              対象テナント名(例: tenant-alpha, tenant-beta)

オプション:
  -h, --help               このヘルプメッセージを表示して終了
  -o, --output FILE        出力先ファイル(指定しない場合は標準出力)
  --vc-manager-ns NS       VirtualCluster管理namespace(デフォルト: vc-manager)

実行例:
  # kubeconfigを標準出力に表示
  $SCRIPT_NAME tenant-alpha

  # kubeconfigをファイルに保存
  $SCRIPT_NAME tenant-alpha -o /tmp/tenant-alpha-kubeconfig

  # kubeconfigを確認してから使用
  $SCRIPT_NAME tenant-alpha > ~/.kube/tenant-alpha.conf
  export KUBECONFIG=~/.kube/tenant-alpha.conf
  kubectl get pods
EOF
}

# エラー出力
error() {
  echo "[ERROR] $*" >&2
  exit 1
}

# 情報出力
info() {
  echo "[INFO] $*" >&2
}

# 警告出力
warn() {
  echo "[WARN] $*" >&2
}

# VirtualCluster情報確認(デバッグ用stdout出力)
show_debug_info() {
  local tenant_name="$1"

  info "テナント情報:"
  info "  テナント名: $tenant_name"
  info "  VirtualCluster管理namespace: $VC_MANAGER_NS"

  # VirtualClusterリソースが存在するか確認
  if ! kubectl get virtualcluster "$tenant_name" -n "$VC_MANAGER_NS" &>/dev/null; then
    error "VirtualCluster '$tenant_name' が見つかりません (namespace: $VC_MANAGER_NS)"
  fi

  # クラスタ情報を取得
  local cluster_ns cluster_domain
  cluster_ns=$(kubectl get virtualcluster "$tenant_name" -n "$VC_MANAGER_NS" \
    -o jsonpath='{.status.clusterNamespace}' 2>/dev/null || echo "")
  cluster_domain=$(kubectl get virtualcluster "$tenant_name" -n "$VC_MANAGER_NS" \
    -o jsonpath='{.spec.clusterDomain}' 2>/dev/null || echo "")

  info "  実行時namespace: $cluster_ns"
  info "  クラスタドメイン: $cluster_domain"
}

# kubeconfig生成
generate_kubeconfig() {
  local tenant_name="$1"
  local output_file="$2"

  info "kubeconfig生成開始: $tenant_name"

  # VirtualClusterステータスから情報を抽出
  local cluster_ns cluster_domain
  cluster_ns=$(kubectl get virtualcluster "$tenant_name" -n "$VC_MANAGER_NS" \
    -o jsonpath='{.status.clusterNamespace}')
  cluster_domain=$(kubectl get virtualcluster "$tenant_name" -n "$VC_MANAGER_NS" \
    -o jsonpath='{.spec.clusterDomain}')

  if [[ -z "$cluster_ns" ]]; then
    error "クラスタnamespacが取得できません。VirtualClusterが起動していない可能性があります。"
  fi

  info "  実行時namespace: $cluster_ns"
  info "  クラスタドメイン: $cluster_domain"

  # APIサーバーエンドポイント取得
  local api_server_host api_server_port
  api_server_host="${cluster_domain:-${tenant_name}.vc.local}"
  api_server_port="6443"

  # デフォルトServiceAccountのシークレットを取得
  local sa_secret
  sa_secret=$(kubectl get secret -n "$cluster_ns" -o name \
    --sort-by=.metadata.creationTimestamp | grep -E "default-token|default-sa-token" | tail -1)

  if [[ -z "$sa_secret" ]]; then
    error "Serviceアカウントシークレットが見つかりません (namespace: $cluster_ns)"
  fi

  info "  Serviceアカウントシークレット: $sa_secret"

  # トークンを抽出
  local token
  token=$(kubectl get "$sa_secret" -n "$cluster_ns" \
    -o jsonpath='{.data.token}' | base64 -d)

  if [[ -z "$token" ]]; then
    error "トークンを抽出できません"
  fi

  # CA証明書を抽出
  local ca_cert
  ca_cert=$(kubectl get "$sa_secret" -n "$cluster_ns" \
    -o jsonpath='{.data.ca\.crt}')

  if [[ -z "$ca_cert" ]]; then
    error "CA証明書を抽出できません"
  fi

  info "  トークン: ${token:0:20}..."
  info "  CA証明書: 取得済み"

  # kubeconfig YAMLを生成
  local kubeconfig
  kubeconfig=$(cat <<KUBECONFIG_EOF
apiVersion: v1
kind: Config
clusters:
- cluster:
    certificate-authority-data: ${ca_cert}
    server: https://${api_server_host}:${api_server_port}
  name: virtualcluster-${tenant_name}
contexts:
- context:
    cluster: virtualcluster-${tenant_name}
    user: virtualcluster-${tenant_name}
  name: virtualcluster-${tenant_name}
current-context: virtualcluster-${tenant_name}
users:
- name: virtualcluster-${tenant_name}
  user:
    token: ${token}
KUBECONFIG_EOF
)

  # 出力先に書き込み
  if [[ -n "$output_file" ]]; then
    echo "$kubeconfig" > "$output_file"
    chmod 600 "$output_file"
    info "kubeconfig を出力: $output_file"
  else
    echo "$kubeconfig"
  fi

  info "kubeconfig生成完了"
}

# メイン処理
main() {
  local tenant_name="" output_file=""

  # 引数パー
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h|--help)
        usage
        exit 0
        ;;
      -o|--output)
        output_file="$2"
        shift 2
        ;;
      --vc-manager-ns)
        VC_MANAGER_NS="$2"
        shift 2
        ;;
      -*)
        error "不正なオプション: $1"
        ;;
      *)
        if [[ -z "$tenant_name" ]]; then
          tenant_name="$1"
          shift
        else
          error "テナント名が重複しています: $tenant_name, $1"
        fi
        ;;
    esac
  done

  # 必須引数チェック
  if [[ -z "$tenant_name" ]]; then
    usage >&2
    error "テナント名を指定してください"
  fi

  # kubectl が利用可能か確認
  if ! command -v kubectl &>/dev/null; then
    error "kubectl コマンドが見つかりません"
  fi

  # 接続情報を表示
  info "====== kubeconfig生成 ======"
  info "コンテキスト: $(kubectl config current-context 2>/dev/null || echo 'unknown')"
  info "ユーザ: $(kubectl config get-contexts $(kubectl config current-context 2>/dev/null) 2>/dev/null | awk '{print $3}' | head -1 || echo 'unknown')"

  # VirtualCluster情報確認
  show_debug_info "$tenant_name"

  # kubeconfig生成
  generate_kubeconfig "$tenant_name" "$output_file"

  info "====== 完了 ======"
}

main "$@"
