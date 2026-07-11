#!/usr/bin/env bash
# -*- mode: bash; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (c) 2025 TAKEHARU KATO
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。

# 対象ノード上で tar から containerd の image を登録する共通スクリプト。
#
# 書式: import-image-on-cri.sh <component> <expected_tag> <image_tar_path> <unqualified_image_registry>
#   <component>                  取り込み対象コンポーネント名 (例: kube-apiserver, kube-controller-manager)
#   <expected_tag>               取り込み後に期待するタグ (例: registry.example.com/ns/img:tag, img:tag)
#   <image_tar_path>             取り込み元tarファイルのパス (例: /var/cache/k8s-virtual-cluster/img.tar)
#   <unqualified_image_registry> 未修飾名のタグを使う場合の既定レジストリ (例: registry.example.com)
#
set -euo pipefail

#
# 変数定義
#
readonly COMPONENT_NAME="${1:?component is required}"
readonly EXPECTED_TAG="${2:?expected tag is required}"
readonly IMAGE_TAR_PATH="${3:?image tar path is required}"
readonly UNQUALIFIED_IMAGE_REGISTRY="${4:?unqualified image registry is required}"

# 期待タグの先頭要素を取り出す。
# 例: registry.example.com/ns/img:tag の場合, registry.example.com を取り出す。
first_component="${EXPECTED_TAG%%/*}"
# expected_tag_primary は, ctr importで期待するタグ(正規タグ)。
# 例: registry.example.com/ns/img:tag の場合, registry.example.com/ns/img:tag となる。
expected_tag_primary="${EXPECTED_TAG}"
# expected_tag_alias は, 未修飾名の場合にCRI既定レジストリ解決差異を吸収する別名(エイリアスタグ)。
# 例: img:tag の場合, registry.example.com/img:tag となる。
expected_tag_alias=""

# 期待タグの先頭要素 (first_component)が未修飾名のイメージ名であることを判定する。
# 以下の条件をすべて満たす場合は未修飾名と判定する。
# 1. 期待タグの先頭要素 (first_component) が localhost でないこと
# 2. 期待タグの先頭要素 (first_component) に . が含まれないこと
# 3. 期待タグの先頭要素 (first_component) に : が含まれないこと
if [[ "${first_component}" != "localhost" && "${first_component}" != *.* && "${first_component}" != *:* ]]; then

    # 未修飾名のイメージ名の場合は, 既定レジストリ解決差異を
    # 吸収するためエイリアスタグを作成し, expected_tag_alias に設定する。
    expected_tag_alias="${UNQUALIFIED_IMAGE_REGISTRY}/${EXPECTED_TAG}"
fi


#
# 既存のタグ/関連digestをcontainerdのk8s.io名前空間から削除し,
# 古い参照が残らないようにする
#

# 正規タグ(expected_tag_primary)の削除
ctr -n k8s.io images rm "${expected_tag_primary}" 2>/dev/null || true
if [[ -n "${expected_tag_alias}" ]]; then

    # エイリアスタグ(expected_tag_alias)が定義されている場合は,
    # エイリアスタグを削除する
    ctr -n k8s.io images rm "${expected_tag_alias}" 2>/dev/null || true
fi


#
# k8s.io 名前空間にあるイメージの識別子を列挙し, expected_tag_primary の
# レジストリ部分に一致するものを削除することで, 同じイメージ名に紐づく別タグや
# digest を含めて古いイメージを削除する。
#
# 処理ロジック
#   1. ctr -n k8s.io images ls -q で k8s.io 名前空間のイメージ識別子を列挙し,
#      grep -F で 正規タグ(expected_tag_primary) 内の最初の : 以降を取り除いた部分
#      (expected_tag_primary%%:*) に一致するものを抽出
#      例: expected_tag_primary が registry.example.com/ns/img:tag の場合,
#           expected_tag_primary%%:* は registry.example.com/ns/img となる。
#   2. while で1件ずつ読み込んで, 古いイメージを削除する
#      2-a. 空行を読み飛ばす ([[ -n "${digest}" ]] || continue)
#      2-b. 各イメージを ctr -n k8s.io images rm で削除
#
while IFS= read -r digest; do
    [[ -n "${digest}" ]] || continue
    ctr -n k8s.io images rm "${digest}" 2>/dev/null || true
done < <(ctr -n k8s.io images ls -q | grep -F "${expected_tag_primary%%:*}" || true)


#
# コンテナイメージをcontainerdに登録(import)する
#
# 指定された tar ファイル形式のコンテナイメージを登録(import)し, import_out 変数に結果を格納する。
if [[ ! -f "${IMAGE_TAR_PATH}" ]]; then
    echo "ERROR: Image tar not found: ${IMAGE_TAR_PATH}" >&2
    exit 1
fi

import_out="$(ctr -n k8s.io images import "${IMAGE_TAR_PATH}" 2>&1)"
# トラブル追跡のためにimport_out の内容を標準出力に出力する。
printf '%s\n' "${import_out}"

# k8s.io 名前空間の expected_tag_primary に一致するタグが存在しない場合, かつ,
# expected_tag_alias が定義されていて, k8s.io 名前空間に expected_tag_alias に一致するタグが存在しない場合
if ! ctr -n k8s.io images ls -q | grep -Fx "${expected_tag_primary}" >/dev/null \
    && ( [[ -z "${expected_tag_alias}" ]] || ! ctr -n k8s.io images ls -q | grep -Fx "${expected_tag_alias}" >/dev/null ); then

    # import結果のdigestを使って期待タグへ正規化する。
    import_digest="$(printf '%s\n' "${import_out}" | grep -Eo 'sha256:[0-9a-f]{64}' | head -n1 || true)"
    if [[ -z "${import_digest}" ]]; then

        # import結果のdigestが検出できない場合はエラーとして処理を終了する。
        echo "ERROR: Failed to detect imported digest for ${COMPONENT_NAME}" >&2
        exit 1
    fi

    # import結果のdigestに紐づくsource_refを検出する。
    source_ref="$(ctr -n k8s.io images ls | grep -F "${import_digest}" | awk '{print $1}' | head -n1 || true)"
    if [[ -z "${source_ref}" ]]; then

        # import結果のdigestに紐づくsource_refが検出できない場合はエラーとして処理を終了する。
        echo "ERROR: Failed to detect imported source ref for ${COMPONENT_NAME} digest ${import_digest}" >&2
        exit 1
    fi

    # source_refをexpected_tag_primaryにタグ付けする。
    ctr -n k8s.io images tag "${source_ref}" "${expected_tag_primary}"
fi


#
# 未修飾名を使う場合のみ, CRIの既定レジストリ解決差異を吸収するため別名を登録する。
#
if [[ -n "${expected_tag_alias}" ]]; then

    if ctr -n k8s.io images ls -q | grep -Fx "${expected_tag_primary}" >/dev/null; then

        # expected_tag_primary が存在する場合は, expected_tag_primary を expected_tag_alias にタグ付けする。
        ctr -n k8s.io images tag "${expected_tag_primary}" "${expected_tag_alias}" 2>/dev/null || true
    elif ctr -n k8s.io images ls -q | grep -Fx "${expected_tag_alias}" >/dev/null; then

        # expected_tag_alias が存在する場合は, expected_tag_alias を expected_tag_primary にタグ付けする。
        ctr -n k8s.io images tag "${expected_tag_alias}" "${expected_tag_primary}" 2>/dev/null || true
    fi

fi


#
# タグの表示
#
# 正規タグ(expected_tag_primary)を表示
ctr -n k8s.io images ls -q | grep -Fx "${expected_tag_primary}" >/dev/null
if [[ -n "${expected_tag_alias}" ]]; then

    # エイリアスタグ(expected_tag_alias)が定義されている場合は, エイリアスタグを表示
    ctr -n k8s.io images ls -q | grep -Fx "${expected_tag_alias}" >/dev/null
fi
