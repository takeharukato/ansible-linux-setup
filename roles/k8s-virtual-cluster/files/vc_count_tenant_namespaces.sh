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
# テナント名前空間(vc-manager-*)の残存数を出力する。
#
# 書式: vc_count_tenant_namespaces.sh <supercluster_kubeconfig_path> <namespace_prefix>
#       <supercluster_kubeconfig_path> : Super Cluster 側 kubeconfig ファイルのパス
#       <namespace_prefix> : テナント名前空間のプレフィックス(vc-manager など)
# 例: vc_count_tenant_namespaces.sh /etc/kubernetes/admin.conf vc-manager
#

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
# テナント名前空間のプレフィックス(vc-manager など)
NAMESPACE_PREFIX="$2"

# Super Cluster 側で対象プレフィックスのテナント名前空間を数える。
count="$(kubectl --kubeconfig "${SUPERCLUSTER_KUBECONFIG_PATH}" get ns -o name 2>/dev/null \
    | grep -F "namespace/${NAMESPACE_PREFIX}-" \
    | wc -l || true)"

# 残存数を標準出力へ返す。
echo "${count}"
