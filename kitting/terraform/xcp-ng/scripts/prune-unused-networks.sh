#!/usr/bin/env bash
# -*- coding: utf-8 mode: bash -*-
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# Terraform state上で未参照の managed network(module.network)を削除する。
# 既存参照ネットワーク(data.xenorchestra_network.existing)は対象外。
#

set -euo pipefail

TERRAFORM_BIN="${TERRAFORM:-terraform}"
TERRAFORM_FLAGS_VALUE="${TERRAFORM_FLAGS:--auto-approve}"

DRY_RUN=true
APPLY=false
VERBOSE=false
KEEP_KEYS=()

usage() {
  cat <<'USAGE'
Usage:
  prune-unused-networks.sh [--dry-run] [--apply] [--keep-key KEY] [--verbose]

Options:
  --dry-run        削除対象を表示するのみ(既定)
  --apply          実際に terraform destroy -target=module.network["<key>"] を実行
  --keep-key KEY   指定した network key は未参照でも削除しない(複数指定可)
  --verbose        解析の詳細を表示
  -h, --help       ヘルプ表示
USAGE
}

contains_keep_key() {
  local key="$1"
  local keep
  for keep in "${KEEP_KEYS[@]}"; do
    if [[ "$keep" == "$key" ]]; then
      return 0
    fi
  done
  return 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      APPLY=false
      shift
      ;;
    --apply)
      APPLY=true
      DRY_RUN=false
      shift
      ;;
    --keep-key)
      if [[ $# -lt 2 ]]; then
        echo "ERROR: --keep-key には値が必要です" >&2
        exit 2
      fi
      KEEP_KEYS+=("$2")
      shift 2
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: 不明な引数: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

declare -A NETWORK_KEY_TO_ADDR=()
declare -A NETWORK_KEY_TO_ID=()
declare -A USED_NETWORK_IDS=()

# 1) managed network(module.network) を収集
while IFS= read -r network_addr; do
  [[ -z "$network_addr" ]] && continue
  network_key="$(echo "$network_addr" | sed -E 's/^module\.network\["([^"]+)"\]\.xenorchestra_network\.network$/\1/')"
  network_id="$($TERRAFORM_BIN state show -no-color "$network_addr" | awk -F'"' '/^[[:space:]]*id[[:space:]]*=/{print $2; exit}')"

  if [[ -z "$network_key" || -z "$network_id" ]]; then
    echo "ERROR: ネットワーク情報の抽出に失敗しました: $network_addr" >&2
    exit 1
  fi

  NETWORK_KEY_TO_ADDR["$network_key"]="$network_addr"
  NETWORK_KEY_TO_ID["$network_key"]="$network_id"
done < <($TERRAFORM_BIN state list | grep '^module\.network\[".*"\]\.xenorchestra_network\.network$' || true)

if [[ ${#NETWORK_KEY_TO_ADDR[@]} -eq 0 ]]; then
  echo "INFO: module.network の管理対象がstateに存在しません。"
  exit 0
fi

# 2) VM(module.vms.*.xenorchestra_vm.this) で参照される network_id を収集
while IFS= read -r vm_addr; do
  [[ -z "$vm_addr" ]] && continue
  while IFS= read -r used_id; do
    [[ -z "$used_id" ]] && continue
    USED_NETWORK_IDS["$used_id"]=1
  done < <($TERRAFORM_BIN state show -no-color "$vm_addr" | awk -F'"' '/network_id[[:space:]]*=/{print $2}')
done < <($TERRAFORM_BIN state list | grep '^module\.vms\[".*"\]\.xenorchestra_vm\.this$' || true)

if [[ "$VERBOSE" == "true" ]]; then
  echo "INFO: 収集済み managed network keys: ${!NETWORK_KEY_TO_ADDR[*]}"
  echo "INFO: 収集済み used network ids: ${!USED_NETWORK_IDS[*]}"
fi

# 3) 未参照 managed network を抽出
PRUNE_KEYS=()
for key in "${!NETWORK_KEY_TO_ADDR[@]}"; do
  if contains_keep_key "$key"; then
    echo "INFO: keep-key 指定により保護: $key"
    continue
  fi
  nid="${NETWORK_KEY_TO_ID[$key]}"
  if [[ -z "${USED_NETWORK_IDS[$nid]:-}" ]]; then
    PRUNE_KEYS+=("$key")
  fi
done

if [[ ${#PRUNE_KEYS[@]} -eq 0 ]]; then
  echo "INFO: 未参照 managed network はありません。"
  exit 0
fi

echo "INFO: prune候補 network keys: ${PRUNE_KEYS[*]}"

if [[ "$DRY_RUN" == "true" ]]; then
  echo "INFO: dry-run のため削除は実行しません。"
  exit 0
fi

if [[ "$APPLY" != "true" ]]; then
  echo "ERROR: 実削除には --apply が必要です。" >&2
  exit 2
fi

SKIPPED_IN_USE_KEYS=()
FAILED_KEYS=()

for key in "${PRUNE_KEYS[@]}"; do
  target_addr="${NETWORK_KEY_TO_ADDR[$key]}"
  echo "INFO: 削除実行: $target_addr"

  tmp_log_file="$(mktemp)"

  # TERRAFORM_FLAGSは空白区切りオプション列として利用する
  # shellcheck disable=SC2086
  if $TERRAFORM_BIN destroy $TERRAFORM_FLAGS_VALUE -target="$target_addr" 2>&1 | tee "$tmp_log_file"; then
    rm -f "$tmp_log_file"
    continue
  fi

  if grep -q 'NETWORK_CONTAINS_VIF' "$tmp_log_file"; then
    echo "WARN: $key は未参照判定でしたが, XCP-ng 側でVIFが残っているため削除をスキップしました。"
    SKIPPED_IN_USE_KEYS+=("$key")
    rm -f "$tmp_log_file"
    continue
  fi

  echo "ERROR: $key の削除に失敗しました。ログを確認してください。" >&2
  FAILED_KEYS+=("$key")
  rm -f "$tmp_log_file"
done

if [[ ${#SKIPPED_IN_USE_KEYS[@]} -gt 0 ]]; then
  echo "WARN: VIF残存のため未削除のnetwork keys: ${SKIPPED_IN_USE_KEYS[*]}"
  echo "WARN: Xen Orchestra/XCP-ng で該当networkに接続中のVIFを切断後, 再度 prune を実行してください。"
fi

if [[ ${#FAILED_KEYS[@]} -gt 0 ]]; then
  echo "ERROR: 削除失敗 network keys: ${FAILED_KEYS[*]}" >&2
  exit 1
fi

echo "INFO: prune完了"
