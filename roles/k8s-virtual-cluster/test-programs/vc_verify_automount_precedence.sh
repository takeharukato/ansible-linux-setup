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
# Pod と ServiceAccount の automountServiceAccountToken 優先順位を検証する。
#
# 書式: vc_verify_automount_precedence.sh [--kubeconfig <path>] [--namespace <ns>] [--keep]
#       --kubeconfig <path> : 検証先クラスタの kubeconfig パス(省略時は kubectl の現在コンテキストを使用)
#       --namespace <ns>    : 検証用 namespace 名(省略時は自動生成)
#       --keep              : 検証後に namespace を削除しない
# 例: vc_verify_automount_precedence.sh --kubeconfig /path/to/kubeconfig
#

set -euo pipefail

KEEP_NAMESPACE="false"
KUBECONFIG_PATH=""
TEST_NAMESPACE=""

# 引数を解釈する。
while [[ $# -gt 0 ]]; do
    case "$1" in
        --kubeconfig)
            shift
            [[ $# -gt 0 ]] || { echo "Missing value for --kubeconfig" >&2; exit 2; }
            KUBECONFIG_PATH="$1"
            ;;
        --namespace)
            shift
            [[ $# -gt 0 ]] || { echo "Missing value for --namespace" >&2; exit 2; }
            TEST_NAMESPACE="$1"
            ;;
        --keep)
            KEEP_NAMESPACE="true"
            ;;
        -h|--help)
            sed -n '1,28p' "$0"
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 2
            ;;
    esac
    shift
done

# 検証用 namespace 名を決める。
if [[ -z "${TEST_NAMESPACE}" ]]; then
    TEST_NAMESPACE="automount-test-$(date +%s)"
fi

# kubectl コマンドをラップする関数。
kubectl_cmd() {
    if [[ -n "${KUBECONFIG_PATH}" ]]; then
        kubectl --kubeconfig "${KUBECONFIG_PATH}" "$@"
    else
        kubectl "$@"
    fi
}

# 終了時に検証用 namespace を削除する。
cleanup() {
    if [[ "${KEEP_NAMESPACE}" == "true" ]]; then
        return 0
    fi
    kubectl_cmd delete namespace "${TEST_NAMESPACE}" --ignore-not-found >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Pod が service account token を mount しているかどうかを判定する。
# 戻り値: 0=mount あり, 1=mount なし
pod_has_serviceaccount_mount() {
    local pod_name="$1"
    local volume_names mount_paths

    volume_names="$(kubectl_cmd -n "${TEST_NAMESPACE}" get pod "${pod_name}" -o jsonpath='{.spec.volumes[*].name}' 2>/dev/null || true)"
    mount_paths="$(kubectl_cmd -n "${TEST_NAMESPACE}" get pod "${pod_name}" -o jsonpath='{.spec.containers[0].volumeMounts[*].mountPath}' 2>/dev/null || true)"

    if echo "${volume_names}" | grep -Eq '(^|[[:space:]])kube-api-access-'; then
        return 0
    fi
    if echo "${mount_paths}" | grep -Eq '(^|[[:space:]])/var/run/secrets/kubernetes.io/serviceaccount($|[[:space:]])'; then
        return 0
    fi
    return 1
}

# 検証用 namespace と ServiceAccount を作成する。
echo "[INFO] Create namespace: ${TEST_NAMESPACE}"
kubectl_cmd create namespace "${TEST_NAMESPACE}" >/dev/null

kubectl_cmd -n "${TEST_NAMESPACE}" create serviceaccount sa-true >/dev/null
kubectl_cmd -n "${TEST_NAMESPACE}" create serviceaccount sa-false >/dev/null
kubectl_cmd -n "${TEST_NAMESPACE}" patch serviceaccount sa-true -p '{"automountServiceAccountToken":true}' >/dev/null
kubectl_cmd -n "${TEST_NAMESPACE}" patch serviceaccount sa-false -p '{"automountServiceAccountToken":false}' >/dev/null

# 4パターンの Pod を作成する。
kubectl_cmd -n "${TEST_NAMESPACE}" apply -f - >/dev/null <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: pod-sa-false-pod-unset
spec:
  serviceAccountName: sa-false
  containers:
  - name: c
    image: busybox:1.36
    command: ["sh", "-c", "sleep 3600"]
---
apiVersion: v1
kind: Pod
metadata:
  name: pod-sa-true-pod-unset
spec:
  serviceAccountName: sa-true
  containers:
  - name: c
    image: busybox:1.36
    command: ["sh", "-c", "sleep 3600"]
---
apiVersion: v1
kind: Pod
metadata:
  name: pod-sa-false-pod-true
spec:
  serviceAccountName: sa-false
  automountServiceAccountToken: true
  containers:
  - name: c
    image: busybox:1.36
    command: ["sh", "-c", "sleep 3600"]
---
apiVersion: v1
kind: Pod
metadata:
  name: pod-sa-true-pod-false
spec:
  serviceAccountName: sa-true
  automountServiceAccountToken: false
  containers:
  - name: c
    image: busybox:1.36
    command: ["sh", "-c", "sleep 3600"]
EOF

# Ready まで待機する。
for pod in \
    pod-sa-false-pod-unset \
    pod-sa-true-pod-unset \
    pod-sa-false-pod-true \
    pod-sa-true-pod-false; do
    echo "[INFO] Wait Ready: ${pod}"
    kubectl_cmd -n "${TEST_NAMESPACE}" wait --for=condition=Ready "pod/${pod}" --timeout=180s >/dev/null
done

# 期待値を判定する。
# 期待: SA=false/POD=unset -> mount なし
# 期待: SA=true/POD=unset  -> mount あり
# 期待: SA=false/POD=true  -> mount あり(Pod 指定優先)
# 期待: SA=true/POD=false  -> mount なし(Pod 指定優先)
FAIL_COUNT=0

assert_mount_state() {
    local pod_name="$1"
    local expected="$2"
    local actual="absent"

    if pod_has_serviceaccount_mount "${pod_name}"; then
        actual="present"
    fi

    if [[ "${actual}" == "${expected}" ]]; then
        echo "[PASS] ${pod_name}: expected=${expected}, actual=${actual}"
    else
        echo "[FAIL] ${pod_name}: expected=${expected}, actual=${actual}" >&2
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

assert_mount_state pod-sa-false-pod-unset absent
assert_mount_state pod-sa-true-pod-unset present
assert_mount_state pod-sa-false-pod-true present
assert_mount_state pod-sa-true-pod-false absent

if [[ ${FAIL_COUNT} -ne 0 ]]; then
    echo "[RESULT] FAILED: ${FAIL_COUNT} case(s) mismatched." >&2
    exit 1
fi

echo "[RESULT] OK: automountServiceAccountToken precedence is as expected."
