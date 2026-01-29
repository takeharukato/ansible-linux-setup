# modules/network/main.tf
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# Network Module
#
# ネットワークのラベル名を元に既存のネットワークリソースを検索し,
# 既設のネットワークリソースがまだ作成されていなければ,
# 指定された名前でネットワークリソースを作成する
#

############################################
# 既設のネットワークリソースの検索
# ネットワークのラベル名とIDの組から
# ネットワークリソース情報を取得する
############################################
data "xenorchestra_network" "existing" {
  name_label = var.network_name
  pool_id    = var.pool_id
}

##############################################
# 指定したネットワークが見つからなかった場合,
# ネットワークリソースを作成する。
##############################################
resource "xenorchestra_network" "created" {
  # 作成リソース数をcountに設定する
  # tryにより, data.xenorchestra_network.existing.id にアクセスを試み,
  # もしネットワークが存在しない(データソースが値を返さない)場合,
  # nullを返却する。
  # 返却値がnull(既設のネットワークリソースがない)の場合,
  # 生成リソース数を1に設定, それ以外は, 0に設定することで,
  # リソースの重複を避け, ネットワークリソースを作成する
  count = try(data.xenorchestra_network.existing.id, null) == null ? 1 : 0

  name_label = var.network_name
  pool_id    = var.pool_id
}
