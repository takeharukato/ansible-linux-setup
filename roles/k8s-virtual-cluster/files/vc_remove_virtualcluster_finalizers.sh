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
# VirtualCluster リソース の 残存finalizers (kubernetesのリソース削除後処理機構) を削除する。
#
# 書式: vc_remove_virtualcluster_finalizers.sh <supercluster_kubeconfig_path> <namespace> <api_group>
#       <supercluster_kubeconfig_path> : Super Cluster 側 kubeconfig ファイルのパス
#       <namespace> : VirtualCluster リソースが存在する Super Cluster 側名前空間
#       <api_group> : VirtualCluster CRD の API グループ名
# 例: vc_remove_virtualcluster_finalizers.sh /etc/kubernetes/admin.conf vc-manager tenancy.x-k8s.io

set -euo pipefail

# 引数の個数を検証する。
if [[ $# -ne 3 ]]; then
    echo "Usage: $0 <supercluster_kubeconfig_path> <namespace> <api_group>" >&2
    exit 1
fi

#
# 変数定義
#
# Super Cluster 側 kubeconfig ファイルのパス
SUPERCLUSTER_KUBECONFIG_PATH="$1"
# VirtualCluster リソースが存在する Super Cluster 側名前空間
TARGET_NAMESPACE="$2"
# VirtualCluster CRD の API グループ名
VC_API_GROUP="$3"

# 残存しているfinalizers  (kubernetesのリソース削除後処理機構) を
# 各VirtualCluster ごとに除去する。
for vc in $(kubectl --kubeconfig "${SUPERCLUSTER_KUBECONFIG_PATH}" -n "${TARGET_NAMESPACE}" \
    get "virtualclusters.${VC_API_GROUP}" -o name 2>/dev/null); do
    kubectl --kubeconfig "${SUPERCLUSTER_KUBECONFIG_PATH}" -n "${TARGET_NAMESPACE}" patch "${vc}" --type=json \
        -p='[{"op":"remove","path":"/metadata/finalizers"}]' >/dev/null 2>&1 || true
done
