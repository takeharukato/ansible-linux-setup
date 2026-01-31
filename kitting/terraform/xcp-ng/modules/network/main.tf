# modules/network/main.tf
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# Network Module
#
# ネットワークリソースを作成または管理する
# Terraformのステート管理により：
# - ステートにリソースがない場合：新規作成
# - ステートにリソースがある場合：既存リソースを管理
# - XOに存在するがステートにない場合：terraform importで取り込み可能
#

##############################################
# ネットワークリソースの作成/管理
##############################################
resource "xenorchestra_network" "network" {
  name_label = var.network_name
  pool_id    = var.pool_id
}
