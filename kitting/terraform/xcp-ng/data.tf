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
# 管理ネットワーク (プール全体のネットワーク)
# (Pool-wide Network)
#############################################
data "xenorchestra_network" "mgmt" {
  name_label = var.xcpng_mgmt_network_name
}
