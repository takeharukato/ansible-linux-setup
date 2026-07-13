#!/usr/bin/env bash
# -*- mode: bash; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (c) 2025 TAKEHARU KATO
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。

# 古いwebhook 設定(stale webhook 設定)を削除する。
#
# 書式: vc_delete_stale_webhooks.sh <supercluster_kubeconfig_path>
#       <supercluster_kubeconfig_path> : Super Cluster 側 kubeconfig ファイルのパス
# 例: vc_delete_stale_webhooks.sh /etc/kubernetes/admin.conf

set -euo pipefail

# 引数の個数を検証する。
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <supercluster_kubeconfig_path>" >&2
    exit 1
fi

#
# 変数定義
#
# Super Cluster 側 kubeconfig ファイルのパス
SUPERCLUSTER_KUBECONFIG_PATH="$1"

# validating webhook を削除する。
# validating webhook は, Kubernetes API サーバーがリソースの
# 作成, 更新, 削除を受け付ける前に, 外部の Webhook サービスへ
# 問い合わせて変更可否を判定する仕組みのこと。
# 役目を終えた古い validating webhook 設定が残ると,
# すでに存在しないサービスや壊れたエンドポイントを参照してしまい,
# Namespace や Custom Resource の削除がブロックされる原因になるため,
# 以下の処理で, 残存している古い validating webhook を削除する。
kubectl --kubeconfig "${SUPERCLUSTER_KUBECONFIG_PATH}" \
    delete validatingwebhookconfiguration virtualcluster-validating-webhook-configuration \
    --ignore-not-found --timeout=30s >/dev/null 2>&1 || true

# mutating webhook を削除する。
# mutating webhook は, Kubernetes API サーバーがリソースの作成や更新を受け取った際に,
# その内容を外部の Webhook サービス側で書き換えるための仕組みのこと。
# 古い mutating webhook 設定が残っていると, 既に存在しない Webhook サービスを参照して
# API 呼び出しが失敗し, Custom Resource や Namespace の削除処理が止まることがあるため,
# 以下の処理で, 残存している古い mutating webhook を削除する。
kubectl --kubeconfig "${SUPERCLUSTER_KUBECONFIG_PATH}" \
    delete mutatingwebhookconfiguration virtualcluster-mutating-webhook-configuration \
    --ignore-not-found --timeout=30s >/dev/null 2>&1 || true
