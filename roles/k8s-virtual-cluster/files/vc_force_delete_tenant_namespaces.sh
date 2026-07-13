#!/usr/bin/env bash
# -*- mode: bash; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (c) 2025 TAKEHARU KATO
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。

# テナント名前空間(vc-manager-*)を強制削除する。
#
# 書式: vc_force_delete_tenant_namespaces.sh <supercluster_kubeconfig_path> <namespace_prefix>
#       <supercluster_kubeconfig_path> : Super Cluster 側 kubeconfig ファイルのパス
#       <namespace_prefix> : 削除対象のテナント名前空間プレフィックス
# 例: vc_force_delete_tenant_namespaces.sh /etc/kubernetes/admin.conf vc-manager

set -euo pipefail

# 引数の個数を検証する。
if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <supercluster_kubeconfig_path> <namespace_prefix>" >&2
    exit 1
fi

#
# 変数定義
#
# Super Cluster 側 kubeconfig ファイルのパス
SUPERCLUSTER_KUBECONFIG_PATH="$1"
# 削除対象のテナント名前空間プレフィックス (vc-manager など)
# 補足: テナント名前空間は vc-manager-<tenant_id> のような形式で作成されるため,
#     "<テナント名前空間プレフィックス>-"で始まる名前空間を指定することで,
#     (<テナント名前空間プレフィックス>-<tenant_id> 形式の)テナントの名前空間を取得する
NAMESPACE_PREFIX="$2"

# 対象プレフィックスに一致するテナント名前空間一覧を取得する。
mapfile -t tenant_namespaces < <(
    kubectl --kubeconfig "${SUPERCLUSTER_KUBECONFIG_PATH}" get ns -o name 2>/dev/null \
        | grep -F "namespace/${NAMESPACE_PREFIX}-" \
        | sed 's|namespace/||' || true
)

# 抽出した各 名前空間 (namespace) を順に削除する。
for ns in "${tenant_namespaces[@]}"; do
    [[ -z "${ns}" ]] && continue
    echo "Force deleting namespace: ${ns}"
    kubectl --kubeconfig "${SUPERCLUSTER_KUBECONFIG_PATH}" \
        delete namespace "${ns}" --ignore-not-found --timeout=30s 2>&1 || true
done
