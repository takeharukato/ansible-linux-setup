# modules/vm/outputs.tf
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# VM 生成処理からの出力定義

# VMのUUID
output "vm_id" {
  description = "VM ID"
  value       = xenorchestra_vm.this.id
}

# VMに設定されたIPアドレスのリスト
output "vm_ips" {
  description = "VM IP addresses"
  value       = xenorchestra_vm.this.ipv4_addresses
}
