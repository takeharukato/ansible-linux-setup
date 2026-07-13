#!/usr/bin/env bash
# -*- mode: bash; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (c) 2025 TAKEHARU KATO
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。

# 終了処理中 (Terminating) 状態の 名前空間 (namespace) を強制削除する。
#
# 書式: vc_force_delete_terminating_namespace.sh <supercluster_kubeconfig_path> <namespace> <api_group> <delete_webhooks:true|false>
#       <supercluster_kubeconfig_path> : Super Cluster 側 kubeconfig ファイルのパス
#       <namespace> : 強制削除対象の名前空間名
#       <api_group> : VirtualCluster CRD の API グループ名
#       <delete_webhooks:true|false> : stale webhook を削除する場合は true, それ以外は false
# 例: vc_force_delete_terminating_namespace.sh /etc/kubernetes/admin.conf vc-manager tenancy.x-k8s.io true

set -euo pipefail

# 引数の個数を検証する。
if [[ $# -ne 4 ]]; then
    echo "Usage: $0 <supercluster_kubeconfig_path> <namespace> <api_group> <delete_webhooks:true|false>" >&2
    exit 1
fi

#
# 変数定義
#
# Super Cluster 側 kubeconfig ファイルのパス
SUPERCLUSTER_KUBECONFIG_PATH="$1"
# 強制削除対象の名前空間名
NS_NAME="$2"
# VirtualCluster CRD の API グループ名
VC_API_GROUP="$3"
# 古いwebhook (stale webhook) を削除する場合は true, それ以外は false
DELETE_WEBHOOKS="$4"

#
# kubectl コマンドをラップする関数
# 書式: kubectl_cmd <kubectl_subcommand> [<kubectl_subcommand_args>...]
kubectl_cmd() {
    kubectl --kubeconfig "${SUPERCLUSTER_KUBECONFIG_PATH}" "$@"
}

# 対象名前空間 (namespace) の 進行状態 (.status.phase) を確認し, 終了処理中 (Terminating) 以外は何もしない。
NS_PHASE="$(kubectl_cmd get namespace "${NS_NAME}" -o jsonpath='{.status.phase}' 2>/dev/null || echo 'NotFound')"
if [[ "${NS_PHASE}" != "Terminating" ]]; then
    exit 0
fi

# 強制削除処理を開始する旨を標準出力へ表示する。
echo "Force deleting Terminating namespace: ${NS_NAME}"

# 古いwebhook (stale webhook) を削除する指示がある場合は,
# webhook 設定を削除する。
#
# validating webhook は, Kubernetes API サーバーがリソースの
# 作成, 更新, 削除を受け付ける前に, 外部の Webhook サービスへ
# 問い合わせて変更可否を判定する仕組みのこと。
# 役目を終えた古い validating webhook 設定が残ると,
# すでに存在しないサービスや壊れたエンドポイントを参照してしまい,
# Namespace や Custom Resource の削除がブロックされる原因になるため,
# 以下の処理で, 残存している古い validating webhook を削除する。
#
# mutating webhook は, Kubernetes API サーバーがリソースの作成や更新を受け取った際に,
# その内容を外部の Webhook サービス側で書き換えるための仕組みのこと。
# 古い mutating webhook 設定が残っていると, 既に存在しない Webhook サービスを参照して
# API 呼び出しが失敗し, Custom Resource や Namespace の削除処理が止まることがあるため,
# 以下の処理で, 残存している古い mutating webhook を削除する。

if [[ "${DELETE_WEBHOOKS}" == "true" ]]; then
    # 古いwebhook (stale webhook) 設定を削除する。
    kubectl_cmd delete validatingwebhookconfiguration virtualcluster-validating-webhook-configuration \
        --ignore-not-found --timeout=30s >/dev/null 2>&1 || true
    # 古いmutating webhook 設定を削除する。
    kubectl_cmd delete mutatingwebhookconfiguration virtualcluster-mutating-webhook-configuration \
        --ignore-not-found --timeout=30s >/dev/null 2>&1 || true
fi

# 名前空間 (namespace) 自身の
# finalizers (kubernetesのリソース削除後処理機構) を
# 除去する。
kubectl_cmd patch namespace "${NS_NAME}" \
    -p '{"metadata":{"finalizers":[]}}' \
    --type=merge >/dev/null 2>&1 || true

# 名前空間 (namespace) 内のリソースに対するfinalizers (kubernetesのリソース削除後処理機構) を除去し,
# 可能な限り 名前空間 (namespace) 内のリソースを削除する。
for r in $(kubectl_cmd api-resources --verbs=list --namespaced -o name 2>/dev/null); do
    kubectl_cmd -n "${NS_NAME}" get "${r}" -o name --ignore-not-found 2>/dev/null | while read -r obj; do
        [[ -z "${obj}" ]] && continue
        kubectl_cmd -n "${NS_NAME}" patch "${obj}" --type=merge -p '{"metadata":{"finalizers":[]}}' >/dev/null 2>&1 || true
    done
    kubectl_cmd -n "${NS_NAME}" delete "${r}" --all --ignore-not-found --timeout=20s >/dev/null 2>&1 || true
done

# VirtualCluster リソースの finalizers (kubernetesのリソース削除後処理機構) を除去し,
# VirtualCluster リソースの削除を試みる。
for vc in $(kubectl_cmd -n "${NS_NAME}" get "virtualclusters.${VC_API_GROUP}" -o name 2>/dev/null); do
    kubectl_cmd -n "${NS_NAME}" patch "${vc}" --type=json \
        -p='[{"op":"remove","path":"/metadata/finalizers"}]' >/dev/null 2>&1 || true
    kubectl_cmd -n "${NS_NAME}" delete "${vc}" --ignore-not-found --timeout=20s >/dev/null 2>&1 || true
done

# finalize API を呼び出して 名前空間 (namespace) の削除を進める。
printf '{"apiVersion":"v1","kind":"Namespace","metadata":{"name":"%s"},"spec":{"finalizers":[]}}' "${NS_NAME}" \
    | kubectl_cmd replace --raw "/api/v1/namespaces/${NS_NAME}/finalize" -f - >/dev/null 2>&1 || true

# 最後に 名前空間 (namespace) 自体を強制削除する。
# 補足: --grace-period=0 --force オプションを指定することで,
#       対象名前空間 (namespace) の削除を強制的に行う。
kubectl_cmd delete namespace "${NS_NAME}" \
    --grace-period=0 --force --timeout=30s --ignore-not-found >/dev/null 2>&1 || true
