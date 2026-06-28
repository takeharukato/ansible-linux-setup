#!/usr/bin/env python3
# -*- mode: python; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (c) 2025 TAKEHARU KATO
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。
#
# OpenAI's ChatGPT partially generated this code.
# Author has modified some parts.
# OpenAIのChatGPTがこのコードの一部を生成しました。
# 著者が修正している部分があります。

"""Go release API payload から系列 x.y の最新版 patch を解決する。"""

from __future__ import annotations

import json
import re
import sys
from typing import Any, cast


def resolve_latest_patch(payload: list[dict[str, Any]], series: str) -> str:
    """指定系列の最新版 patch を返す。

    Args:
        payload (list[dict[str, Any]]): Go release API の JSON 配列。
        series (str): x.y 形式の系列文字列。

    Returns:
        str: 見つかった場合は x.y.z 形式, 見つからない場合は空文字。

    Examples:
        >>> resolve_latest_patch([{"version": "go1.25.9"}, {"version": "go1.25.11"}], "1.25")
        '1.25.11'
        >>> resolve_latest_patch([{"version": "go1.24.5"}], "1.25")
        ''
    """
    pattern: re.Pattern[str] = re.compile(r"^go" + re.escape(series) + r"\.(\d+)$")
    matched: list[tuple[int, str]] = []
    for item in payload:
        version: str = str(item.get("version", ""))
        result: re.Match[str] | None = pattern.search(version)
        if result is None:
            continue
        matched.append((int(result.group(1)), version))

    if not matched:
        return ""

    matched.sort(key=lambda value: value[0])
    return matched[-1][1].replace("go", "", 1)


def main() -> int:
    """標準入力と引数から系列版数を解決して標準出力へ出力する。

    Returns:
        int: 終了コード。成功時 0, 入力不正時 2。

    Raises:
        json.JSONDecodeError: payload が JSON として不正な場合。

    Examples:
        >>> # CLI utility function; doctest skips direct execution example.
        >>> True
        True
    """
    if len(sys.argv) < 2:
        print("", end="")
        return 0

    series: str = sys.argv[1].strip()
    raw_payload: str = sys.stdin.read()
    if not raw_payload:
        print("", end="")
        return 0

    try:
        parsed_obj: object = json.loads(raw_payload)
    except json.JSONDecodeError:
        return 2

    if not isinstance(parsed_obj, list):
        return 2

    parsed_list: list[object] = cast(list[object], parsed_obj)

    # Filter to dict entries only; unexpected items are ignored.
    payload: list[dict[str, Any]] = []
    for item in parsed_list:
        if isinstance(item, dict):
            payload.append(cast(dict[str, Any], item))
    print(resolve_latest_patch(payload, series), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
