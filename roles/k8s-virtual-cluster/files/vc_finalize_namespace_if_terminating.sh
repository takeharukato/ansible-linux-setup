#!/usr/bin/env bash
# -*- mode: bash; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (c) 2025 TAKEHARU KATO
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。
#
# 名前空間 (namespace) が 終了処理中 (Terminating) の場合のみ 強制終了処理 (finalize API) を実行する。
#
# 書式: vc_finalize_namespace_if_terminating.sh <supercluster_kubeconfig_path> <namespace>
#       <supercluster_kubeconfig_path> : Super Cluster 側 kubeconfig ファイルのパス
#       <namespace> : 強制終了 ( finalize ) 対象の名前空間名
# 例: vc_finalize_namespace_if_terminating.sh /etc/kubernetes/admin.conf vc-manager

set -euo pipefail

# 引数の個数を検証する。
if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <supercluster_kubeconfig_path> <namespace>" >&2
    exit 1
fi

#
# 変数定義
#
# Super Cluster 側 kubeconfig ファイルのパス
SUPERCLUSTER_KUBECONFIG_PATH="$1"
# 強制終了 ( finalize ) 対象の名前空間名
NS_NAME="$2"

# 対象 名前空間 (namespace) の 進行状態 (.status.phase項目) を確認し,
# 終了中 (Terminating) でなければ, 何もしない。
NS_PHASE="$(kubectl --kubeconfig "${SUPERCLUSTER_KUBECONFIG_PATH}" get namespace "${NS_NAME}" -o jsonpath='{.status.phase}' 2>/dev/null || echo 'NotFound')"
if [[ "${NS_PHASE}" != "Terminating" ]]; then
    exit 0
fi

# finalize API を呼び出して finalizers (kubernetesのリソース削除後処理機構) を空にする。
printf '{"apiVersion":"v1","kind":"Namespace","metadata":{"name":"%s"},"spec":{"finalizers":[]}}' "${NS_NAME}" \
    | kubectl --kubeconfig "${SUPERCLUSTER_KUBECONFIG_PATH}" replace --raw "/api/v1/namespaces/${NS_NAME}/finalize" -f - >/dev/null 2>&1 || true
