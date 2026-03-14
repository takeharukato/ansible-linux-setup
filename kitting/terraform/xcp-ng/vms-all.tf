# vms-all.tf
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# VM 構築処理
#
# vm_groups で定義された VM 群をフラット化し,
# modules/vm を単一モジュールとして for_each 展開する。
#

module "vms" {
  source   = "./modules/vm"
  for_each = local.vm_instances

  name            = each.value.vm_name
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
