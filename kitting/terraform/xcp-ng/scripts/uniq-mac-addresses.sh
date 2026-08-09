#!/usr/bin/env bash
#
# -*- coding: utf-8 mode: bash -*-
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# uniq-mac-addresses.sh
# terraform.tfvarsのMACアドレス定義を抽出する
# Usage:
#  $ ./uniq-mac-addresses.sh terraform.tfvars
#
#

# コマンドが失敗したら停止, 未定義変数があれば停止, パイプ破棄で停止
set -euo pipefail

show() {
    local target

	# 引数の数をチェック
    if [ "$#" -lt 1 ]; then

		# 引数が足りない場合はエラーを出力して終了
        echo "Usage: uniq-mac-addresses.sh terraform.tfvars" >&2
        return 1
    fi

    target=$1
    if [ ! -f "${target}" ]; then

		# 指定されたファイルが存在しない場合はエラーを出力して終了
        echo "Error: file not found: ${target}" >&2
        return 1
    fi

	# terraform.tfvarsからMACアドレスを抽出して一意にする
	# awkでmac_addressの行を抽出し, 不要な文字列を削除して整形し, sortでソートしてuniqで重複を排除する
	# '/mac_address = / && !/null/'でmac_addressが含まれる行を抽出し, nullを含む行は除外
	# gsubでmac_address = を削除し, gsubで末尾の } を削除し, gsubで前後の空白を削除
	# printで整形されたMACアドレスを出力し, sort -uで一意にする
    awk -F',' '/mac_address = / && !/null/ {
        gsub(/mac_address = /, "", $2)
        gsub(/ \}/, "", $2)
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2)
        print $2
    }' "${target}" | sort -u
}

main(){

    show "$@"
}

main "$@"
