#!/usr/bin/env bash
# -*- mode: bash; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (c) 2025 TAKEHARU KATO
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。

# テナント Pod内でコマンドを実行するスクリプト
# VirtualClusterテナント環境のPod内でコマンドを実行します。
# テナント名から自動的に管理namespace(vc-manager-XXXXX-tenant-name形式)を取得し、
# その名前空間内のPod対して execコマンドを実行します。

set -euo pipefail

readonly SCRIPT_NAME="$(basename "$0")"
readonly VC_MANAGER_NS="${VC_MANAGER_NS:-vc-manager}"

usage() {
  cat <<EOF
使用方法: $SCRIPT_NAME <テナント名> <Pod名> -- <コマンド> [コマンド引数...]

説明:
  VirtualClusterテナント内のPodに対してコマンドを実行します。
  テナント名から自動的に管理namespace(vc-manager-XXXXX-tenant-name)を取得し、
  そのnamespace内のPodでkubectl execコマンドを実行します。

引数:
  <テナント名>              対象テナント名(例: tenant-alpha, tenant-beta)
  <Pod名>                   対象Pod名
  --                        以降をコマンドとして扱う開始マーカー
  <コマンド>                実行するコマンド

オプション:
  -h, --help               このヘルプメッセージを表示して終了
  -i, --stdin              stdin を保持(対話実行に必須)
  -t, --tty                tty を割り当て(対話実行に必須)
  -c, --container NAME     対象コンテナを指定(Pod内に複数コンテナがある場合)
  --vc-manager-ns NS       VirtualCluster管理namespace(デフォルト: vc-manager)

実行例:
  # Pod内でシェルコマンド実行
  $SCRIPT_NAME tenant-alpha my-pod -- sh -c 'echo hello'

  # Pod内で対話的にシェル実行
  $SCRIPT_NAME tenant-alpha my-pod -it -- /bin/sh

  # 特定コンテナでコマンド実行
  $SCRIPT_NAME tenant-alpha my-pod -c container-name -- ls -la /tmp
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
  if [[ $# -lt 3 ]]; then
    usage >&2
    return 1
  fi

  local tenant_name="$1"
  local pod_name="$2"
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

  # kubectlオプションを指定してexecを実行
  kubectl -n "$tenant_ns" exec "$pod_name" "${args[@]}"
}

main "$@"
