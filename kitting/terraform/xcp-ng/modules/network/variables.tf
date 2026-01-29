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
