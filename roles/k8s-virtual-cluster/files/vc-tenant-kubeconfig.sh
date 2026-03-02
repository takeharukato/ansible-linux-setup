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
VERBOSE="${VERBOSE:-0}"  # -o オプション指定時のみ詳細出力

usage() {
  cat <<EOF
使用方法: $SCRIPT_NAME [オプション...] <テナント名>

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
  $SCRIPT_NAME -o /tmp/tenant-alpha-kubeconfig tenant-alpha

  # 複数のオプションを指定
  $SCRIPT_NAME -o /tmp/tenant-alpha-kubeconfig --vc-manager-ns vc-manager tenant-alpha

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
  if [[ "$VERBOSE" == "1" ]]; then
    echo "[INFO] $*" >&2
  fi
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

  # VirtualClusterのadmin-kubeconfigシークレットから kubeconfig を取得
  local kubeconfig_data
  kubeconfig_data=$(kubectl get secret admin-kubeconfig -n "$cluster_ns" \
    -o jsonpath='{.data.admin-kubeconfig}' 2>/dev/null)

  if [[ -z "$kubeconfig_data" ]]; then
    info "admin-kubeconfigシークレットから kubeconfig を取得できません"
    info "namespace $cluster_ns 内のシークレット一覧:"
    kubectl get secret -n "$cluster_ns" 2>/dev/null | tail -n +2 | awk '{print "  " $1}'
    error "kubeconfig生成に必要なシークレット情報が見つかりません (namespace: $cluster_ns)"
  fi

  info "  admin-kubeconfigシークレット: 取得済み"

  # base64 デコード
  local kubeconfig
  kubeconfig=$(echo "$kubeconfig_data" | base64 -d)

  if [[ -z "$kubeconfig" ]]; then
    error "kubeconfigのデコードに失敗しました"
  fi

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

  # 引数パース
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h|--help)
        usage
        exit 0
        ;;
      -o|--output)
        if [[ $# -lt 2 ]]; then
          error "$1 オプションには値を指定してください"
        fi
        output_file="$2"
        VERBOSE="1"
        shift 2
        ;;
      --vc-manager-ns)
        if [[ $# -lt 2 ]]; then
          error "$1 オプションには値を指定してください"
        fi
        VC_MANAGER_NS="$2"
        VERBOSE="1"
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

  # 出力ファイル指定なし時は、詳細出力を有効化
  if [[ -z "$output_file" ]]; then
    VERBOSE="1"
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
