#!/usr/bin/env bash
# -*- coding: utf-8 mode: bash -*-
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# migrate-all.sh
#
# Terraformのstateを全VMグループ分移行する
# Usage:
#  $ ./migrate-all.sh [--dry-run]
# Options:
#  --dry-run : 実際の変更を加えずに, 移行手順をシミュレートする
# Exit Codes:
#  0: 正常終了
#  1: エラー発生
#  2: 入力引数エラー
# Notes:
#  - 各VMグループ毎に個別の移行スクリプトを呼び出す
#  - 各ステップの後にterraform planを実行し, 変更内容を確認する
#  - --dry-runオプションを指定すると, 実際の変更を加えずに移行手順をシミュレートする
#  - ログファイルに全出力を保存する
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/migration-all-$(date +%Y%m%d-%H%M%S).log"

# 引数解析
# dry-runオプションの有無を確認
DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "=== DRY RUN MODE - No changes will be made ===" | tee "$LOG_FILE"
fi

echo "======================================" | tee -a "$LOG_FILE"
echo "Terraform State Migration - All Groups" | tee -a "$LOG_FILE"
echo "======================================" | tee -a "$LOG_FILE"
echo "Started at: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# terraform設定ディレクトリに移動
cd "$(dirname "$SCRIPT_DIR")"
echo "Working directory: $(pwd)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Step 1: Terraform設定の検証
echo "=== Step 1: Validating Terraform Configuration ===" | tee -a "$LOG_FILE"
if terraform validate 2>&1 | tee -a "$LOG_FILE"; then
  echo "[OK] Configuration is valid" | tee -a "$LOG_FILE"
else
  echo "[ERROR] Configuration validation failed" | tee -a "$LOG_FILE"
  echo "Please fix configuration errors before proceeding" | tee -a "$LOG_FILE"
  exit 1
fi
echo "" | tee -a "$LOG_FILE"

# Step 2: 移行前のプラン確認
if [ "$DRY_RUN" = false ]; then
  echo "=== Step 2: Checking Initial Plan ===" | tee -a "$LOG_FILE"
  echo "This shows what Terraform would change with the OLD state structure" | tee -a "$LOG_FILE"
  if terraform plan -detailed-exitcode > /dev/null 2>&1; then
    echo "[OK] No changes detected (unusual but OK)" | tee -a "$LOG_FILE"
  else
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 2 ]; then
      echo "[WARNING] Changes detected - this is expected before migration" | tee -a "$LOG_FILE"
    else
      echo "[ERROR] Plan failed with error" | tee -a "$LOG_FILE"
      echo "Please review and fix errors before proceeding" | tee -a "$LOG_FILE"
      exit 1
    fi
  fi
  echo "" | tee -a "$LOG_FILE"
fi

# Step 3: インフラストラクチャVMの移行
echo "=== Step 3: Migrating Infrastructure VMs ===" | tee -a "$LOG_FILE"
if [ "$DRY_RUN" = true ]; then
  "$SCRIPT_DIR/migrate-state-infrastructure.sh" --dry-run 2>&1 | tee -a "$LOG_FILE"
else
  "$SCRIPT_DIR/migrate-state-infrastructure.sh" 2>&1 | tee -a "$LOG_FILE"
  echo "Verifying infrastructure migration..." | tee -a "$LOG_FILE"
  terraform plan -target='module.infrastructure_vms' -detailed-exitcode > /dev/null 2>&1 || {
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 2 ]; then
      echo "[WARNING] Warning: Changes detected after migration" | tee -a "$LOG_FILE"
      echo "Review the plan carefully" | tee -a "$LOG_FILE"
    fi
  }
fi
echo "" | tee -a "$LOG_FILE"

# Step 4: vmlinux VMsの移行
echo "=== Step 4: Migrating vmlinux VMs ===" | tee -a "$LOG_FILE"
if [ "$DRY_RUN" = true ]; then
  "$SCRIPT_DIR/migrate-state-vmlinux.sh" --dry-run 2>&1 | tee -a "$LOG_FILE"
else
  "$SCRIPT_DIR/migrate-state-vmlinux.sh" 2>&1 | tee -a "$LOG_FILE"
  echo "Verifying vmlinux migration..." | tee -a "$LOG_FILE"
  terraform plan -target='module.vmlinux_vms' -detailed-exitcode > /dev/null 2>&1 || {
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 2 ]; then
      echo "[WARNING] Warning: Changes detected after migration" | tee -a "$LOG_FILE"
      echo "Review the plan carefully" | tee -a "$LOG_FILE"
    fi
  }
fi
echo "" | tee -a "$LOG_FILE"

# Step 5: devlinux VMsの移行
echo "=== Step 5: Migrating devlinux VMs ===" | tee -a "$LOG_FILE"
if [ "$DRY_RUN" = true ]; then
  "$SCRIPT_DIR/migrate-state-devlinux.sh" --dry-run 2>&1 | tee -a "$LOG_FILE"
else
  "$SCRIPT_DIR/migrate-state-devlinux.sh" 2>&1 | tee -a "$LOG_FILE"
  echo "Verifying devlinux migration..." | tee -a "$LOG_FILE"
  terraform plan -target='module.devlinux_vms' -detailed-exitcode > /dev/null 2>&1 || {
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 2 ]; then
      echo "[WARNING] Warning: Changes detected after migration" | tee -a "$LOG_FILE"
      echo "Review the plan carefully" | tee -a "$LOG_FILE"
    fi
  }
fi
echo "" | tee -a "$LOG_FILE"

# Step 6: Kubernetes Lab VMsの移行
echo "=== Step 6: Migrating Kubernetes Lab VMs ===" | tee -a "$LOG_FILE"
if [ "$DRY_RUN" = true ]; then
  "$SCRIPT_DIR/migrate-state-k8s.sh" --dry-run 2>&1 | tee -a "$LOG_FILE"
else
  "$SCRIPT_DIR/migrate-state-k8s.sh" 2>&1 | tee -a "$LOG_FILE"
  echo "Verifying k8s migration..." | tee -a "$LOG_FILE"
  terraform plan -target='module.k8s_vms' -detailed-exitcode > /dev/null 2>&1 || {
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 2 ]; then
      echo "[WARNING] Warning: Changes detected after migration" | tee -a "$LOG_FILE"
      echo "Review the plan carefully" | tee -a "$LOG_FILE"
    fi
  }
fi
echo "" | tee -a "$LOG_FILE"

# 最終確認
if [ "$DRY_RUN" = false ]; then
  echo "=== Step 7: Final Verification ===" | tee -a "$LOG_FILE"
  echo "Running full terraform plan to verify all migrations..." | tee -a "$LOG_FILE"
  if terraform plan -detailed-exitcode 2>&1 | tee -a "$LOG_FILE"; then
    echo "[OK] No changes detected - Migration successful!" | tee -a "$LOG_FILE"
  else
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 2 ]; then
      echo "[WARNING] Changes detected in final plan" | tee -a "$LOG_FILE"
      echo "This may indicate:"  | tee -a "$LOG_FILE"
      echo "  - MAC address auto-assignment differences" | tee -a "$LOG_FILE"
      echo "  - Configuration drift" | tee -a "$LOG_FILE"
      echo "  - Review carefully before applying" | tee -a "$LOG_FILE"
    else
      echo "[ERROR] Plan failed" | tee -a "$LOG_FILE"
    fi
  fi
  echo "" | tee -a "$LOG_FILE"
fi

echo "======================================" | tee -a "$LOG_FILE"
echo "Migration Complete" | tee -a "$LOG_FILE"
echo "======================================" | tee -a "$LOG_FILE"
echo "Completed at: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

if [ "$DRY_RUN" = false ]; then
  echo "Full log saved to: $LOG_FILE" | tee -a "$LOG_FILE"
  echo "" | tee -a "$LOG_FILE"
  echo "Next steps:" | tee -a "$LOG_FILE"
  echo "1. Review the log file for any warnings" | tee -a "$LOG_FILE"
  echo "2. Run 'terraform plan' to verify final state" | tee -a "$LOG_FILE"
  echo "3. If everything looks good, proceed with normal operations" | tee -a "$LOG_FILE"
else
  echo "Dry-run complete. No changes were made." | tee -a "$LOG_FILE"
  echo "Run without --dry-run to perform actual migration." | tee -a "$LOG_FILE"
fi
