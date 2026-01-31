# modules/network/outputs.tf
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# ネットワークモジュール出力処理
#
output "network_id" {
  description = "Network ID"
  value       = xenorchestra_network.network.id
}

output "is_managed" {
  description = "Whether the network is managed by Terraform"
  value       = true
}
