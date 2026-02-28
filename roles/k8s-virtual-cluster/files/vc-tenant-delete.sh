#!/usr/bin/env bash
# -*- mode: bash; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (c) 2025 TAKEHARU KATO
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。

# テナント内のリソースをkubectl deleteで削除するスクリプト
# VirtualClusterテナント環境のKubernetesリソースを削除します。
# テナント名から自動的に管理namespace(vc-manager-XXXXX-tenant-name形式)を取得し、
# その名前空間内のリソースをdeleteコマンドで削除します。

set -euo pipefail

readonly SCRIPT_NAME="$(basename "$0")"
readonly VC_MANAGER_NS="${VC_MANAGER_NS:-vc-manager}"

usage() {
  cat <<EOF
使用方法: $SCRIPT_NAME <テナント名> <リソース型> [リソース名] [kubectl deleteオプション...]

説明:
  VirtualClusterテナント内のリソースをdeleteで削除します。
  テナント名から自動的に管理namespace(vc-manager-XXXXX-tenant-name)を取得し、
  そのnamespaceでkubectl deleteコマンドを実行します。

引数:
  <テナント名>              対象テナント名(例: tenant-alpha, tenant-beta)
  <リソース型>              リソース種別(例: pods, svc, deploy, pvc)
  [リソース名]              削除対象リソース名(指定しなければ対話型確認)

オプション:
  -h, --help               このヘルプメッセージを表示して終了
  --vc-manager-ns NS       VirtualCluster管理namespace(デフォルト: vc-manager)
  [その他のオプション]      kubectlのdeleteコマンドに渡されます

実行例:
  # 特定のPodを削除
  $SCRIPT_NAME tenant-alpha pod my-pod-name

  # 全Podを削除(確認なし)
  $SCRIPT_NAME tenant-alpha pods --all

  # DeploymentをnamespaceごとGraceful削除
  $SCRIPT_NAME tenant-alpha deployment my-app --grace-period=30
EOF
}

# テナント用namespaceを取得
get_tenant_namespace() {
  local tenant_name="$1"
  local ns

  ns=$(kubectl get virtualclusters.tenancy.x-k8s.io -n "$VC_MANAGER_NS" "$tenant_name" \
    -o jsonpath='{.status.clusterNamespace}' 2>/dev/null)

  if [[ -z "$ns" ]]; then
    echo "エラー: テナント '$tenant_name' が見つかりません" >&2
    echo "以下のコマンドで利用可能なテナントを確認してください:" >&2
    echo "  kubectl get virtualclusters.tenancy.x-k8s.io -n $VC_MANAGER_NS" >&2
    return 1
  fi

  echo "$ns"
}

# メイン処理
main() {
  if [[ $# -lt 2 ]]; then
    usage >&2
    return 1
  fi

  local tenant_name="$1"
  local resource_type="$2"
  shift 2

  # ヘルプオプションの確認
  if [[ "$tenant_name" == "-h" ]] || [[ "$tenant_name" == "--help" ]]; then
    usage
    return 0
  fi

  # tenantnameが--から始まる場合はエラー
  if [[ "$tenant_name" =~ ^- ]]; then
    echo "エラー: 最初の引数はテナント名である必要があります" >&2
    usage >&2
    return 1
  fi

  # VirtualClusterManagerのnamespaceオプション処理
  local args=()
  while [[ $# -gt 0 ]]; do
    if [[ "$1" == "--vc-manager-ns" ]]; then
      shift
      if [[ $# -lt 1 ]]; then
        echo "エラー: --vc-manager-ns にはnamespace名が必要です" >&2
        return 1
      fi
      VC_MANAGER_NS="$1"
      shift
    else
      args+=("$1")
      shift
    fi
  done

  # テナント用namespaceを取得
  local tenant_ns
  if ! tenant_ns=$(get_tenant_namespace "$tenant_name"); then
    return 1
  fi

  local current_context
  local current_user
  current_context=$(kubectl config current-context 2>/dev/null || echo "unknown")
  current_user=$(kubectl config view --minify -o jsonpath='{.contexts[0].context.user}' 2>/dev/null || echo "unknown")

  echo "コンテキスト: $current_context" >&2
  echo "ユーザ: $current_user" >&2
  echo "テナント: $tenant_name" >&2
  echo "名前空間: $tenant_ns" >&2

  # kubectlオプションを指定してdeleteを実行
  kubectl -n "$tenant_ns" delete "$resource_type" "${args[@]}"
}

main "$@"
