# modules/network/outputs.tf
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# ネットワークモジュール出力処理
#
# 1. ネットワークのメイン処理部で実施した検索処理で, 検索結果が得られている場合
# (data.xenorchestra_network.existing.idの取得に成功した場合), network_idに
# 既設ネットワークのidを設定, 検索に失敗している場合は, 作成したネットワークのID
# (data.xenorchestra_network.created[0].id)をnetwork_idに設定する。
# 2. ネットワークを新規作成している場合は, is_managedに真を設定する
#
output "network_id" {
  description = "Network ID (from existing or newly created)"
  value       = try(data.xenorchestra_network.existing.id, xenorchestra_network.created[0].id)
}

output "is_managed" {
  description = "Whether the network is managed by Terraform (created, not just referenced)"
  value       = length(xenorchestra_network.created) > 0
}
