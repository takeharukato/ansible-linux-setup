# networks.tf
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# ネットワーク作成処理
#
# 変数で定義された数だけネットワークモジュールをインスタンス化し,
# それぞれに一意のネットワーク名を割り当てながら, 同じ Xen Orchestra
# プール内にネットワークリソースを作成します。
#
# 処理内容:
# 1. ./modules/network ディレクトリからネットワーク構成を読み取る
# 2. var.network_namesで定義されたネットワーク名に対して, 個別の
#    ネットワークリソースを生成する
# 3. 既存のデータソースから取得したプールIDを全てのネットワークで
#    共有

############################################
# ネットワークリソース生成
############################################
module "network" {
  source   = "./modules/network"
  for_each = var.network_names

  network_name = each.value
  pool_id      = data.xenorchestra_pool.pool.id

  # オプションパラメータ (network_optionsで定義されている場合のみ設定)
  automatic         = try(var.network_options[each.key].automatic, null)
  default_is_locked = try(var.network_options[each.key].default_is_locked, null)
  mtu               = try(var.network_options[each.key].mtu, null)
  name_description  = try(var.network_options[each.key].name_description, null)
  nbd               = try(var.network_options[each.key].nbd, null)
  vlan              = try(var.network_options[each.key].vlan, null)
  source_pif_device = try(var.network_options[each.key].source_pif_device, null)
}
