# outputs.tf
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# VM/ネットワーク情報の出力定義
#

############################################
# VM Group情報
############################################
output "vm_groups" {
  description = "VM information grouped by vm_groups"
  value = {
    for group_name, _ in var.vm_groups : group_name => {
      for instance_key, instance_value in local.vm_instances : instance_value.vm_name => {
        id   = module.vms[instance_key].vm_id
        name = instance_value.vm_name
        ips  = module.vms[instance_key].vm_ips
      } if instance_value.group_name == group_name
    }
  }
}

############################################
# VM情報 (フラット)
############################################
output "vm_instances" {
  description = "Flattened VM information keyed by group/vm"
  value = {
    for instance_key, instance_value in local.vm_instances : instance_key => {
      group = instance_value.group_name
      name  = instance_value.vm_name
      id    = module.vms[instance_key].vm_id
      ips   = module.vms[instance_key].vm_ips
    }
  }
}

############################################
# Network情報
############################################
output "networks" {
  description = "Network IDs and management status"
  value = {
    for k, v in module.network : k => {
      id         = v.network_id
      is_managed = v.is_managed
    }
  }
}
