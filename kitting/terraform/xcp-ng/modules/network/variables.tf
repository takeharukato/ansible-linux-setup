# modules/network/variables.tf
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# Network モジュールの変数定義

# network_name変数
# ネットワークのラベル名を格納する
variable "network_name" {
  description = "Name of the network"
  type        = string
}

# pool_id ネットワークを検索, 作成する対象のpoolのidを格納する
variable "pool_id" {
  description = "XCP-ng pool ID"
  type        = string
}

# 以下、xenorchestra_networkリソースのオプショナルパラメータ

variable "automatic" {
  description = "Whether the network is automatically attached to VMs"
  type        = bool
  default     = null
}

variable "default_is_locked" {
  description = "Whether the network is locked by default"
  type        = bool
  default     = null
}

variable "mtu" {
  description = "MTU size for the network"
  type        = number
  default     = null
}

variable "name_description" {
  description = "Description of the network"
  type        = string
  default     = null
}

variable "nbd" {
  description = "Whether NBD is enabled"
  type        = bool
  default     = null
}

variable "vlan" {
  description = "VLAN ID for the network"
  type        = number
  default     = null
}

variable "source_pif_device" {
  description = "Source PIF device for the network"
  type        = string
  default     = null
}
