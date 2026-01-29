# modules/vm/main.tf
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# VM Cloud-initによる初期化(ホスト名自動設定など)を
# 含めたVM生成処理
#
# locals.tfのVMプロファイル定義を使用してterraform.tfvarsで
# 以下のVMのリソース量をterraform.tfvarsで指定してVMを生成する
#
#   - ファームウエア
#   - VMテンプレート
#   - cpu
#   - memory
#   - 接続先ネットワーク定義
#   - ストレージ容量
#   - cloud-initでの初期化処理定義
#     (templates/base.yaml.tplでcloud-initの内容を定義)
#

############################################
# Cloud-init 設定
# Cloud-initの設定テンプレートは,
# templates/base.yaml.tpl参照
############################################
resource "xenorchestra_cloud_config" "this" {
  name = var.name
  template = templatefile("${path.root}/templates/base.yaml.tpl", {
    hostname = var.name
    domain   = var.domain
  })
}

#################################################################
# 仮想マシン定義
# ラベル名/VMテンプレート/ファームウエア/生成方式(フルクローン)
# 生成先ホストを指定し, locals.tfのVMプロファイル定義を使用して
# terraform.tfvarsで定義されたVMのリソース量に従って, VMを生成
#################################################################
resource "xenorchestra_vm" "this" {
  name_label        = var.name
  template          = var.template_id
  hvm_boot_firmware = var.firmware
  clone_type        = "full"
  affinity_host     = var.pool_master_id

  cpus        = var.vcpus
  memory_max  = var.memory_bytes
  power_state = var.power_state

  cloud_config = xenorchestra_cloud_config.this.template

  dynamic "network" {
    for_each = var.networks
    content {
      network_id  = network.value.id
      mac_address = network.value.mac
    }
  }

  disk {
    sr_id      = var.sr_id
    name_label = "${var.name}-disk0"
    size       = var.disk_bytes
  }
}
