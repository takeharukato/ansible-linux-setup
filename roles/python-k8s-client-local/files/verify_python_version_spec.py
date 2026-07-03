#!/usr/bin/env python3
# -*- mode: python; coding: utf-8; line-endings: unix -*-
#
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (c) 2025 TAKEHARU KATO
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。
#
# Python Enhancement Proposal (PEP) 440に準拠したPythonバージョンの仕様を
# 検証するスクリプト
# Verify whether a version satisfies a subset of PEP 440 specifiers.
#
# コマンドライン引数:
#   verify_python_version_spec.py <spec> <version>
#   <spec> (argv[1]): PEP 440準拠の版数指定子句(カンマで区切って複数指定可能, 複数指定時は全ての指定子句に一致した場合に正常終了する)
#   <version> (argv[2]): 判定対象のバージョン文字列
# 終了コード:
#   0: PEP 440準拠の版数指定子句に一致する(正常終了)
#   1: PEP 440準拠の版数指定子句に一致しない(エラー終了)
#   2: コマンドライン引数の数が正しくない(エラー終了)
# コマンドライン例: Pythonバージョン 3.6以上, 3.10未満であることを検証する場合
#   ./verify_python_version_spec.py ">=3.6, <3.10" "3.8.10"
import re
import sys
from typing import Tuple


def _normalize(version_text: str) -> Tuple[int, ...]:
    """ドットで区切られた数値バージョンの接頭辞を整数タプル形式のバージョン番号列に変換する。
    例: bool _normalize("3.10.4") -> (3, 10, 4)
    Args:
        version_text (str): 生のバージョン文字列。

    Returns:
        Tuple[int, ...]: 解析されたバージョンタプル。

    Raises:
        ValueError: バージョンを解析できない場合ValueErrorを送出する。
    """

    #
    # 正規表現でバージョン文字列を解析し、整数タプルに変換
    #
    # "^\s*([0-9]+(?:\.[0-9]+)*)" は, 先頭の数字とドットで区切られた部分を抽出する
    # ための正規表現。
    #
    match = re.match(r"^\s*([0-9]+(?:\.[0-9]+)*)", version_text)
    if not match:
        # バージョン文字列が正規表現に一致しない場合(版数を検出できなかった場合)は,
        # ValueErrorを送出
        raise ValueError(f"invalid version: {version_text}")

    # 解析されたバージョン文字列を整数タプルに変換して返す
    # match.group(1) で正規表現で抽出されたバージョン文字列の部分を取得し,
    # ドットで分割して各部分を整数に変換し, 各版数番号(major, minor, patch)の
    # 各要素からなるタプルとして返す (例: "3.10.4" を (3, 10, 4) に変換して返却)
    return tuple(int(part) for part in match.group(1).split("."))


def _cmp(left: Tuple[int, ...], right: Tuple[int, ...]) -> int:
    """タプル形式のバージョン番号中のmajor,minor, patchの内, 明示されていない部分をゼロで補完することで比較可能にし, 2つのバージョンタプルを比較する。
    Args:
        left (Tuple[int, ...]): 比較対象の左側のバージョンタプル。
        right (Tuple[int, ...]): 比較対象の右側のバージョンタプル。

    Returns:
        int: 比較結果。
        左側が小さい場合は負の値, 等しい場合は0, 左側が大きい場合は正の値を返す。
    """

    #
    # バージョンタプルの長さを揃えるためにmajor, minor, patch中の未指定部分をゼロで補完する
    #
    # タプルの長さが大きいほうの長さに合わせて、短いほうのタプルに0を追加する
    #  (0,) * (length - len(left)) で, 不足している要素数ぶんだけ 0 を並べたタプルを作り,
    #  left + (0,) * (length - len(left)) で, 末尾に連結している
    # 例:
    #  left = (3, 10), right = (3, 10, 4) の場合, length = 3 となり,
    #   (0,) * (length - len(left)) = (0,) * (3 - 2) = (0,)
    #   (0,) * (length - len(right)) = (0,) * (3 - 3) = ()
    # となるので,
    #  left_norm = (3, 10) + (0,) = (3, 10, 0) ,
    #  right_norm = (3, 10, 4) + () = (3, 10, 4)
    # として, 左右のタプルの長さを揃えて両者のタプルを比較可能にする
    length = max(len(left), len(right))
    left_norm = left + (0,) * (length - len(left))
    right_norm = right + (0,) * (length - len(right))

    #
    # 比較結果を返す
    #
    if left_norm < right_norm:
        # 左側が小さい場合は負の値を返す
        return -1

    if left_norm > right_norm:
        # 左側が大きい場合は正の値を返す
        return 1

    # 左右が等しい場合は0を返す
    return 0


def _match_clause(version_tuple: Tuple[int, ...], clause: str) -> bool:
    """バージョンタプルに対して指定されたPEP 440準拠の版数指定子句が一致することを判定する。
    指定子句はPEP 440に準拠している必要がある。
    参考) https://peps.python.org/pep-0440/

    Args:
        version_tuple (Tuple[int, ...]): 評価対象のバージョンタプル。
        clause (str): 評価するPEP 440準拠の版数指定子句。

    Returns:
        bool: 指定子句に一致する場合はTrue, それ以外はFalse。
        空の指定子句は常に一致するものとみなす(Trueを返す)。
    """

    # 指定子句を空白を除去して, 正規化する
    normalized_clause = clause.strip()
    if not normalized_clause:
        # 空の指定子句は常に一致するものとみなす
        return True

    if normalized_clause.startswith("~="):
        # "~=" 演算子の場合、互換性のあるバージョン範囲を計算する

        # 指定子句の "~=" 演算子を除去して、残りの部分を解析する
        # _normalize関数を使用して、指定されたバージョン文字列を整数タプルに変換する
        base_text = normalized_clause[2:].strip()
        base_tuple = _normalize(base_text)
        base_parts = [int(part) for part in base_text.split(".")]
        if len(base_parts) <= 1:
            # 各版数番号(major, minor, patch)のうち、1つしか指定されていない場合は,
            # majorバージョンを1つ増やした範囲を上限とする
            upper_tuple = (base_parts[0] + 1,)
        else:
            # 複数の版数番号が指定されている場合は, 最後の指定された部分(minor, または, patch)を
            # 1つ増やした範囲を上限とする
            prefix = base_parts[:-1]
            prefix[-1] += 1
            upper_tuple = tuple(prefix)
        # 指定されたバージョンタプルが, 互換性のあるバージョン範囲に含まれることを判定する
        return _cmp(version_tuple, base_tuple) >= 0 and _cmp(version_tuple, upper_tuple) < 0

    #
    # 比較演算子を使用した指定子句の場合、指定されたバージョンタプルが指定された条件を満たすかどうかを判定する
    #

    for operator in ("<=", ">=", "==", "!=", "<", ">"):
        if normalized_clause.startswith(operator): # 比較演算子で始まる場合

            # 指定子句の比較演算子を除去して、残りの部分を解析する
            rhs_text = normalized_clause[len(operator):].strip()

            if rhs_text.endswith(".*") and operator in ("==", "!="):

                #
                # 指定されたバージョン文字列が ".*" で終わる場合,  かつ, "==" または "!=" 演算子の場合,
                # 指定されたバージョンの接頭辞と一致することを判定する
                #
                # 例: "3.10.*" は, "3.10.0", "3.10.1", "3.10.2" などのバージョンに一致する
                #

                # 末尾の2文字(".*") を除去した部分(rhs_text[:-2]) を'.'で分割して
                # 整数タプルに変換する
                prefix_tuple = tuple(int(part) for part in rhs_text[:-2].split("."))

                # 指定されたバージョンタプルのprefix_tupleに含まれる要素数分が
                # 一致することを判定する
                is_match = version_tuple[:len(prefix_tuple)] == prefix_tuple
                return is_match if operator == "==" else (not is_match)

            #
            # 大小比較演算子の場合, 指定されたバージョンタプルと比較する
            #

            # 指定されたバージョンタプルを整数タプルに変換する
            rhs_tuple = _normalize(rhs_text)
            # 指定されたバージョンタプルと比較
            cmp_result = _cmp(version_tuple, rhs_tuple)

            # 指定された演算子に基づいて真偽値を返す
            return {
                "<": cmp_result < 0,
                "<=": cmp_result <= 0,
                ">": cmp_result > 0,
                ">=": cmp_result >= 0,
                "==": cmp_result == 0,
                "!=": cmp_result != 0,
            }[operator]

    return False


def main() -> int:
    """メイン処理
    コマンドライン引数としてPEP 440準拠の版数指定子句とバージョン文字列を受け取り,
    バージョンが指定子句に一致するかどうかを判定する。
    argv[0]: スクリプト名
    argv[1]: PEP 440準拠の版数指定子句
    argv[2]: 判定対象のバージョン文字列
    Returns:
        int: 終了コード。
        PEP 440準拠の版数指定子句に一致する場合は0を, 一致しない場合は1を,
        引数の数が正しくない場合は2を返す。
    """

    #
    # コマンドライン引数の数を検証する
    #
    if len(sys.argv) != 3:
        # 引数の数が正しくない場合はエラーメッセージを表示して終了コード2を返す
        print("usage: verify_python_version_spec.py <spec> <version>", file=sys.stderr)
        return 2

    # 版数指定子句
    spec_text = sys.argv[1]
    # 判定対象のバージョン文字列
    version_text = sys.argv[2].strip()

    # 判定対象のバージョン文字列を整数タプル形式の版数情報に変換
    version_tuple = _normalize(version_text)

    # カンマで分割された版数指定子句をリストに変換
    clauses = [clause.strip() for clause in spec_text.split(",") if clause.strip()]

    # 各指定子句に対して判定を行い, 全ての指定子句に一致する場合は終了コード0を,
    # 1つでも一致しない場合は終了コード1を返す
    ok = all(_match_clause(version_tuple, clause) for clause in clauses)

    return 0 if ok else 1


if __name__ == "__main__":
    # メイン処理を実行し, 終了コードを返す
    raise SystemExit(main())
