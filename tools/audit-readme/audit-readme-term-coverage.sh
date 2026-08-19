#!/usr/bin/env bash
# SPDX-License-Identifier: BSD-2-Clause
# Copyright (c) 2025 TAKEHARU KATO
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。
# OpenAI's ChatGPT partially generated this code.
# Author has modified some parts.
# OpenAIのChatGPTがこのコードの一部を生成しました。
# 著者が修正している部分があります。

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

OUT_REPORT="${REPO_ROOT}/docs/glossary-body-term-coverage-audit.tsv"
ALLOW_ISSUES=0
EXCLUDE_ROLES_CSV="rancher"

usage() {
  cat <<'EOF'
Usage:
  tools/audit-readme-term-coverage.sh [options]

Options:
  -o, --output <path>          Output TSV path.
  --exclude-roles <csv>        Comma-separated role names to exclude. Default: rancher
  --allow-issues               Return success even when issues are found.
  -h, --help                   Show this help.

Examples:
  tools/audit-readme-term-coverage.sh
  tools/audit-readme-term-coverage.sh --exclude-roles "rancher,role-templ"
  tools/audit-readme-term-coverage.sh --allow-issues
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -o|--output)
      OUT_REPORT="$2"
      shift 2
      ;;
    --exclude-roles)
      EXCLUDE_ROLES_CSV="$2"
      shift 2
      ;;
    --allow-issues)
      ALLOW_ISSUES=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

mkdir -p "$(dirname "${OUT_REPORT}")"

python3 - "${REPO_ROOT}" "${OUT_REPORT}" "${EXCLUDE_ROLES_CSV}" "${ALLOW_ISSUES}" <<'PY'
import re
import sys
from pathlib import Path

repo_root = Path(sys.argv[1])
out_report = Path(sys.argv[2])
exclude_roles = {x.strip() for x in sys.argv[3].split(',') if x.strip()}
allow_issues = sys.argv[4] == '1'

# 一般語として本文での用語定義を不要とする語。
allow_general = {
  "ドキュメント", "ファイル", "アクセス", "ネットワーク", "メッセージ", "サポート",
  "データ", "ループ", "カテゴリ", "バイト", "ビット", "プロンプト", "テキスト",
  "アップロード", "ダウンロード", "検証", "構成図",
}

# Markdown や章タイトルで出現しやすい語のノイズ抑制。
allow_noise = {
  "README", "READme", "EXAMPLES", "ARGS", "RETURNS", "RAISES", "YIELDS",
  "TSV", "CSV", "YAML", "JSON", "JINJA", "SHELL", "PYTHON",
}

# 小文字中心のコマンド語は, 専門語抽出の対象外として扱う。
# 大文字・複合英語・カタカナ複合語のみを本文参照語として監査する。


def norm_space(text: str) -> str:
  return re.sub(r"\s+", " ", text.strip())


def norm_term(text: str) -> str:
  value = norm_space(text).strip("`")
  if re.fullmatch(r"[A-Za-z0-9+._/\- ()]+", value):
    value = value.upper()
  return value


def canonical_term(text: str) -> str:
  normalized = norm_term(text)
  return re.sub(r"[^A-Z0-9ァ-ヴー]", "", normalized)


def collect_candidates(line: str) -> set[str]:
  refs: set[str] = set()

  # URL は語抽出対象外。
  cleaned = re.sub(r"https?://\S+", " ", line)

  # Markdownリンクは表示文字列だけ残す。
  cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cleaned)

  # インラインコードは語抽出対象外。
  cleaned = re.sub(r"`[^`]+`", " ", cleaned)

  # 複合英字語 (例: XCP-NG, DNS-SD, Debian/Ubuntu)
  for token in re.findall(r"\b[A-Za-z0-9]+(?:[-/][A-Za-z0-9]+)+\b", cleaned):
    if any(ch.isupper() for ch in token):
      refs.add(norm_term(token))

  # 複合英語句 (例: Red Hat Enterprise Linux)
  for token in re.findall(r"\b(?:[A-Z][A-Za-z0-9-]*)(?:\s+[A-Z][A-Za-z0-9-]*){1,4}\b", cleaned):
    refs.add(norm_term(token))

  # 単語英字語 (例: Debian, Ubuntu, Filebeat, Docker)
  for token in re.findall(r"\b[A-Z][a-z][A-Za-z0-9-]{1,}\b", cleaned):
    refs.add(norm_term(token))

  # 全大文字略語 (例: API, URL, OS, HTTP)
  for token in re.findall(r"\b[A-Z]{2,}(?:[-_][A-Z0-9]+)*\b", cleaned):
    refs.add(norm_term(token))

  # CamelCase語 (例: NetworkManager)
  for token in re.findall(r"\b[A-Z][a-z0-9]+(?:[A-Z][A-Za-z0-9]+)+\b", cleaned):
    refs.add(norm_term(token))

  # 文脈依存のカタカナ複合語 (例: ローカルレジストリエンドポイント)
  for token in re.findall(r"(?:ローカル|リモート|オフライン|オンライン)[ァ-ヴーA-Za-z0-9_-]{2,}", cleaned):
    refs.add(norm_term(token))

  return refs


issues: list[tuple[str, int, str, str, str]] = []
checked_readmes = 0

for readme_path in sorted((repo_root / "roles").glob("*/Readme.md")):
  role_name = readme_path.parent.name
  if role_name in exclude_roles:
    continue

  checked_readmes += 1
  lines = readme_path.read_text(encoding="utf-8").splitlines()

  in_glossary = False
  in_code_block = False
  normalized_glossary_terms: set[str] = set()
  canonical_glossary_terms: set[str] = set()

  # 1) 用語節から定義語を収集。
  for line in lines:
    stripped = line.strip()

    if stripped.startswith("## 用語"):
      in_glossary = True
      continue

    if in_glossary and line.startswith("## "):
      in_glossary = False

    if not in_glossary:
      continue

    if not (stripped.startswith("|") and stripped.endswith("|")):
      continue

    cells = [c.strip() for c in stripped.strip("|").split("|")]
    if len(cells) < 3:
      continue

    formal_name, abbr_name = cells[0], cells[1]
    if formal_name in {"---", "正式名称", "", "-", "なし"}:
      continue

    normalized_glossary_terms.add(norm_term(formal_name))
    canonical_glossary_terms.add(canonical_term(formal_name))

    if abbr_name not in {"", "-", "なし"}:
      normalized_glossary_terms.add(norm_term(abbr_name))
      canonical_glossary_terms.add(canonical_term(abbr_name))

  # 2) 本文から専門語候補を抽出し, 同一ファイルの用語節へ定義されているか検証。
  in_glossary = False
  for line_no, line in enumerate(lines, start=1):
    stripped = line.strip()

    if stripped.startswith("## 用語"):
      in_glossary = True
      continue

    if in_glossary and line.startswith("## "):
      in_glossary = False

    if in_glossary:
      continue

    if stripped.startswith("```"):
      in_code_block = not in_code_block
      continue

    if in_code_block:
      continue

    for ref_term in sorted(collect_candidates(line)):
      ref_canonical = canonical_term(ref_term)

      if ref_term in allow_noise:
        continue
      if ref_term in allow_general:
        continue
      if ref_term in normalized_glossary_terms:
        continue
      if ref_canonical in canonical_glossary_terms:
        continue

      # 包含関係による表記差(例: DNS update key / Dynamic DNS update key)を許容。
      if any(ref_term in defined_term or defined_term in ref_term for defined_term in normalized_glossary_terms):
        continue
      if any(ref_canonical in defined_canonical or defined_canonical in ref_canonical for defined_canonical in canonical_glossary_terms):
        continue

      issues.append((
        str(readme_path),
        line_no,
        "body_term_missing_in_glossary",
        ref_term,
        f"本文参照語 '{ref_term}' が用語節に未定義",
      ))

with out_report.open("w", encoding="utf-8") as fp:
  fp.write("file\tline\ttype\tterm\tdetail\n")
  for row in issues:
    fp.write("\t".join(map(str, row)) + "\n")

print("== Readme Body-Term Coverage Audit Summary ==")
print(f"checked_roles_readme\t{checked_readmes}")
print(f"excluded_roles\t{','.join(sorted(exclude_roles)) if exclude_roles else '-'}")
print(f"issues\t{len(issues)}")
print(f"report\t{out_report}")

if issues and not allow_issues:
  sys.exit(1)
PY