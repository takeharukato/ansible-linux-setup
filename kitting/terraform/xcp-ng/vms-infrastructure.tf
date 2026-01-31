# vms-infrastructure.tf
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# Infrastructure VM 構築処理
#
# 設定ファイルに定義された複数の VM をテンプレートベースで自動作成する
# modules/vm ディレクトリに定義された再利用可能な VM 作成ロジックを呼び出し,
# 変数 infrastructure_vms 内に定義された各 VMを生成する
# 変数 infrastructure_vms は, terraform.tfvars内に定義されており,
# 以下のVMを生成する。
#
# - 仮想環境内部プライベートネットワーク<=>Pool-wideネットワーク間ルータ (router)
# - 管理サーバ (mgmt-server)
# - RHEL管理サーバ検証用VM(rhel-server)
# - Ubuntu管理サーバ検証用VM(ubuntu-server)
# - 旧管理サーバ (devserver)
#

module "infrastructure_vms" {
  source   = "./modules/vm"
  for_each = var.infrastructure_vms

  name            = each.key
  template_id     = local.template_ids[each.value.template_type]
  firmware        = each.value.firmware
  vcpus           = coalesce(each.value.vcpus, local.vm_resource_defaults[each.value.resource_profile].vcpus)
  memory_bytes    = coalesce(each.value.memory_mb, local.vm_resource_defaults[each.value.resource_profile].memory_mb) * 1024 * 1024
  disk_bytes      = coalesce(each.value.disk_gb, local.vm_resource_defaults[each.value.resource_profile].disk_gb) * 1024 * 1024 * 1024
  sr_id           = data.xenorchestra_sr.vm_sr.id
  pool_master_id  = data.xenorchestra_pool.pool.master
  power_state     = "Halted"
  domain          = "local"

  networks = [
    for net in each.value.networks : {
      id  = local.network_ids[net.network_key]
      mac = net.mac_address
    }
  ]
}
