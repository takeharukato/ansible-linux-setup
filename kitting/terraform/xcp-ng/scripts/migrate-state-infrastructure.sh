#!/usr/bin/env bash
# -*- coding: utf-8 mode: bash -*-
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# migrate-state-infrastructure.sh
# Terraformのstateをinfrastructure VMグループ分移行する
# Usage:
#  $ ./migrate-state-infrastructure.sh [--dry-run]
# Options:
#  --dry-run : 実際の変更を加えずに, 移行手順をシミュレートする
# Exit Codes:
#  0: 正常終了
#  1: エラー発生
#  2: 入力引数エラー
# Notes:
#  - infrastructure VMグループ毎にstate移行を実施する
#  - 各ステップの後にterraform planを実行し, 変更内容を確認する
#  - --dry-runオプションを指定すると, 実際の変更を加えずに移行手順をシミュレートする

set -e

# ログファイル設定
LOG_FILE="scripts/migration-infrastructure-$(date +%Y%m%d-%H%M%S).log"

# 引数解析
# dry-runオプションの有無を確認
DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "=== DRY RUN MODE - No changes will be made ===" | tee "$LOG_FILE"
fi

echo "=== Infrastructure VMs State Migration ===" | tee -a "$LOG_FILE"
echo "Started at: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 現在のstateを確認
echo "Current state before migration:" | tee -a "$LOG_FILE"
terraform state list | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# infrastructure VMグループの一覧 (旧リソース名 -> 新key)
declare -A VMS_MAP=(
  [router]=router
  [rhel_server]=rhel-server
  [ubuntu_server]=ubuntu-server
  [mgmt_server]=mgmt-server
  [devserver]=devserver
)

for old in "${!VMS_MAP[@]}"; do
  new=${VMS_MAP[$old]}
  echo "Processing VM: $old -> $new" | tee -a "$LOG_FILE"

  # 既に移行済みであることを確認 (新キーで存在するか)
  if terraform state list | grep -q "module.infrastructure_vms\[\"$new\"\]"; then
    echo "  [OK] Already migrated, skipping" | tee -a "$LOG_FILE"
    continue
  fi

  # cloud-configの移行 (ソースは旧リソース名)
  if terraform state list | grep -q "xenorchestra_cloud_config.$old"; then
    CMD="terraform state mv 'xenorchestra_cloud_config.$old' 'module.infrastructure_vms[\"$new\"].xenorchestra_cloud_config.this'"
    echo "  Migrating cloud-config: $CMD" | tee -a "$LOG_FILE"
    if [ "$DRY_RUN" = false ]; then
      eval "$CMD" 2>&1 | tee -a "$LOG_FILE"
    fi
  else
    echo "  [WARNING] Cloud-config not found in state for $old" | tee -a "$LOG_FILE"
  fi

  # VMの移行 (ソースは旧リソース名)
  if terraform state list | grep -q "xenorchestra_vm.$old"; then
    CMD="terraform state mv 'xenorchestra_vm.$old' 'module.infrastructure_vms[\"$new\"].xenorchestra_vm.this'"
    echo "  Migrating VM: $CMD" | tee -a "$LOG_FILE"
    if [ "$DRY_RUN" = false ]; then
      eval "$CMD" 2>&1 | tee -a "$LOG_FILE"
    fi
  else
    echo "  [WARNING] VM not found in state for $old" | tee -a "$LOG_FILE"
  fi

  echo "" | tee -a "$LOG_FILE"
done

echo "=== Migration Complete ===" | tee -a "$LOG_FILE"
echo "Completed at: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

if [ "$DRY_RUN" = false ]; then
  echo "State after migration:" | tee -a "$LOG_FILE"
  terraform state list | grep "infrastructure_vms" | tee -a "$LOG_FILE"
  echo "" | tee -a "$LOG_FILE"
  echo "Log saved to: $LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo "Next steps:" | tee -a "$LOG_FILE"
echo "1. Run: terraform plan -target='module.infrastructure_vms'" | tee -a "$LOG_FILE"
echo "2. Verify no changes are detected" | tee -a "$LOG_FILE"
