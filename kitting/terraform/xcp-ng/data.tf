# data.tf
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# XCP-ng/Xen Orchestra リソースのデータソース定義
#

############################################
# プール (pool)
############################################
data "xenorchestra_pool" "pool" {
  name_label = var.xcpng_pool_name
}

############################################
# ストレージリポジトリ (Storage Repository)
############################################
data "xenorchestra_sr" "vm_sr" {
  name_label = var.xcpng_sr_name
}

############################################
# テンプレート (Templates)
############################################
data "xenorchestra_template" "ubuntu" {
  name_label = var.xcpng_template_ubuntu
}

data "xenorchestra_template" "rhel" {
  name_label = var.xcpng_template_rhel
}

#############################################
# 既存参照ネットワーク
# network_roles.external_control_plane_network
# で指定されたキーを既存ネットワークとして参照する
#############################################
data "xenorchestra_network" "existing" {
  for_each   = toset(lookup(var.network_roles, "external_control_plane_network", []))
  name_label = var.network_names[each.value]
}
