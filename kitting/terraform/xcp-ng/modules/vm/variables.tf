# modules/vm/variables.tf
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# VM 関連変数

# VM名(VMのラベル名)
variable "name" {
  description = "VM name"
  type        = string
}

# VM生成時のテンプレートのUUID
variable "template_id" {
  description = "XenOrchestra template ID"
  type        = string
}

# 使用するファームウエア種別 (uefi/bios)
variable "firmware" {
  description = "Boot firmware (uefi or bios)"
  type        = string
  validation {
    condition     = contains(["uefi", "bios"], var.firmware)
    error_message = "firmware must be either 'uefi' or 'bios'"
  }
}

# 仮想CPU割当数(1から32個まで)
variable "vcpus" {
  description = "Number of vCPUs"
  type        = number
  validation {
    condition     = var.vcpus > 0 && var.vcpus <= 32
    error_message = "vcpus must be between 1 and 32"
  }
}

# メモリ割り当て量(単位:バイト)
variable "memory_bytes" {
  description = "Memory size in bytes"
  type        = number
}

# ストレージ割当量(単位:バイト)
variable "disk_bytes" {
  description = "Disk size in bytes"
  type        = number
}

# ストレージ確保元となるストレージリポジトリのUUID
variable "sr_id" {
  description = "Storage Repository ID"
  type        = string
}

variable "pool_master_id" {
  description = "Pool master host ID for affinity"
  type        = string
}

variable "networks" {
  description = "List of networks with IDs and optional MAC addresses"
  type = list(object({
    id  = string
    mac = optional(string)
  }))
}

variable "domain" {
  description = "Domain suffix for FQDN"
  type        = string
  default     = "local"
}

variable "power_state" {
  description = "Initial power state (Running or Halted)"
  type        = string
  default     = "Halted"
  validation {
    condition     = contains(["Running", "Halted"], var.power_state)
    error_message = "power_state must be either 'Running' or 'Halted'"
  }
}
