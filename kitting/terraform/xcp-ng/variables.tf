# variables.tf
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# 変数定義
#

# Xen Orchestra (XO) の URL
# XCP-ng は通常 Xen Orchestra (XO) 経由で管理します。
# ws / wss を指定してください (例: wss://xo.example.local)
variable "xoa_url" {
  description = "Xen Orchestra (XO) の URL (ws:// または wss://)"
  type        = string
}

# Xen Orchestraログイン名
variable "xoa_username" {
  description = "XO のユーザー名"
  type        = string
}

# Xen Orchestraログインパスワード
variable "xoa_password" {
  description = "XO のパスワード"
  type        = string
  sensitive   = true
}

# 自己証明書によるホストへの接続を許容するためのフラグ
# (許容する場合は, trueに設定する)
variable "xoa_insecure" {
  description = "TLS 検証を無効化するか (自己署名証明書等のときのみ true)"
  type        = bool
  default     = false
}

variable "xcpng_pool_name" {
  description = "対象 Pool の name_label (XO 上の表示名)"
  type        = string
}

variable "xcpng_sr_name" {
  description = "VM ディスク配置先 SR の name_label"
  type        = string
}

variable "xcpng_vm_disk_gb" {
  description = "VM のディスクサイズ(GB)。テンプレートのディスクより小さくすると縮小になり失敗するため、テンプレート以上に設定してください"
  type        = number
  default     = 256
}

variable "xcpng_vm_vcpus" {
  description = "VM に割り当てる vCPU 数"
  type        = number
  default     = 4
}

variable "xcpng_vm_mem_mb" {
  description = "VM に割り当てる物理メモリ量(MB)"
  type        = number
  default     = 4096
}

variable "xcpng_frr_vcpus" {
  description = "FRRノード(extgw,frr01,frr02)に割り当てる vCPU 数"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_frr_vcpus == null || var.xcpng_frr_vcpus >= 1
    error_message = "xcpng_frr_vcpus は 1 以上を指定してください。"
  }
}

variable "xcpng_frr_mem_mb" {
  description = "FRRノード(extgw,frr01,frr02)に割り当てる物理メモリ量(MB)"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_frr_mem_mb == null || var.xcpng_frr_mem_mb >= 256
    error_message = "xcpng_frr_mem_mb は 256 以上を指定してください。"
  }
}

variable "xcpng_frr_disk_gb" {
  description = "FRRノード(extgw,frr01,frr02)のディスクサイズ(GB)"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_frr_disk_gb == null || var.xcpng_frr_disk_gb >= 1
    error_message = "xcpng_frr_disk_gb は 1 以上を指定してください。"
  }
}

variable "xcpng_k8s_ctrlplane_vcpus" {
  description = "k8s control-planeノード(k8sctrlplane*)に割り当てる vCPU 数"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_k8s_ctrlplane_vcpus == null || var.xcpng_k8s_ctrlplane_vcpus >= 1
    error_message = "xcpng_k8s_ctrlplane_vcpus は 1 以上を指定してください。"
  }
}

variable "xcpng_k8s_ctrlplane_mem_mb" {
  description = "k8s control-planeノード(k8sctrlplane*)に割り当てる物理メモリ量(MB)"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_k8s_ctrlplane_mem_mb == null || var.xcpng_k8s_ctrlplane_mem_mb >= 256
    error_message = "xcpng_k8s_ctrlplane_mem_mb は 256 以上を指定してください。"
  }
}

variable "xcpng_k8s_ctrlplane_disk_gb" {
  description = "k8s control-planeノード(k8sctrlplane*)のディスクサイズ(GB)"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_k8s_ctrlplane_disk_gb == null || var.xcpng_k8s_ctrlplane_disk_gb >= 1
    error_message = "xcpng_k8s_ctrlplane_disk_gb は 1 以上を指定してください。"
  }
}

variable "xcpng_k8s_worker_vcpus" {
  description = "k8s workerノード(k8sworker*)に割り当てる vCPU 数"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_k8s_worker_vcpus == null || var.xcpng_k8s_worker_vcpus >= 1
    error_message = "xcpng_k8s_worker_vcpus は 1 以上を指定してください。"
  }
}

variable "xcpng_k8s_worker_mem_mb" {
  description = "k8s workerノード(k8sworker*)に割り当てる物理メモリ量(MB)"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_k8s_worker_mem_mb == null || var.xcpng_k8s_worker_mem_mb >= 256
    error_message = "xcpng_k8s_worker_mem_mb は 256 以上を指定してください。"
  }
}

variable "xcpng_k8s_worker_disk_gb" {
  description = "k8s workerノード(k8sworker*)のディスクサイズ(GB)"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_k8s_worker_disk_gb == null || var.xcpng_k8s_worker_disk_gb >= 1
    error_message = "xcpng_k8s_worker_disk_gb は 1 以上を指定してください。"
  }
}

variable "xcpng_devserver_vcpus" {
  description = "開発サーバに割り当てる vCPU 数"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_devserver_vcpus == null || var.xcpng_devserver_vcpus >= 1
    error_message = "xcpng_devserver_vcpus は 1 以上を指定してください。"
  }
}

variable "xcpng_devserver_mem_mb" {
  description = "開発サーバに割り当てる物理メモリ量(MB)"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_devserver_mem_mb == null || var.xcpng_devserver_mem_mb >= 256
    error_message = "xcpng_devserver_mem_mb は 256 以上を指定してください。"
  }
}

variable "xcpng_devserver_disk_gb" {
  description = "開発サーバのディスクサイズ(GB)"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_devserver_disk_gb == null || var.xcpng_devserver_disk_gb >= 1
    error_message = "xcpng_devserver_disk_gb は 1 以上を指定してください。"
  }
}


variable "xcpng_router_vcpus" {
  description = "踏み台サーバに割り当てる vCPU 数"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_router_vcpus == null || var.xcpng_router_vcpus >= 1
    error_message = "xcpng_router_vcpus は 1 以上を指定してください。"
  }
}

variable "xcpng_router_mem_mb" {
  description = "踏み台サーバに割り当てる物理メモリ量(MB)"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_router_mem_mb == null || var.xcpng_router_mem_mb >= 256
    error_message = "xcpng_router_mem_mb は 256 以上を指定してください。"
  }
}

variable "xcpng_router_disk_gb" {
  description = "踏み台サーバのディスクサイズ(GB)"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_router_disk_gb == null || var.xcpng_router_disk_gb >= 1
    error_message = "xcpng_router_disk_gb は 1 以上を指定してください。"
  }
}

variable "xcpng_devlinux_vcpus" {
  description = "閉塞ネットワーク内開発マシンに割り当てる vCPU 数"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_devlinux_vcpus == null || var.xcpng_devlinux_vcpus >= 1
    error_message = "xcpng_devlinux_vcpus は 1 以上を指定してください。"
  }
}

variable "xcpng_devlinux_mem_mb" {
  description = "閉塞ネットワーク内開発マシンに割り当てる物理メモリ量(MB)"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_devlinux_mem_mb == null || var.xcpng_devlinux_mem_mb >= 256
    error_message = "xcpng_devlinux_mem_mb は 256 以上を指定してください。"
  }
}

variable "xcpng_devlinux_disk_gb" {
  description = "閉塞ネットワーク内開発マシンのディスクサイズ(GB)"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_devlinux_disk_gb == null || var.xcpng_devlinux_disk_gb >= 1
    error_message = "xcpng_devlinux_disk_gb は 1 以上を指定してください。"
  }
}

variable "xcpng_vmlinux_vcpus" {
  description = "開発マシンに割り当てる vCPU 数"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_vmlinux_vcpus == null || var.xcpng_vmlinux_vcpus >= 1
    error_message = "xcpng_vmlinux_vcpus は 1 以上を指定してください。"
  }
}

variable "xcpng_vmlinux_mem_mb" {
  description = "開発マシンに割り当てる物理メモリ量(MB)"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_vmlinux_mem_mb == null || var.xcpng_vmlinux_mem_mb >= 256
    error_message = "xcpng_vmlinux_mem_mb は 256 以上を指定してください。"
  }
}

variable "xcpng_vmlinux_disk_gb" {
  description = "開発マシンのディスクサイズ(GB)"
  type        = number
  default     = null

  validation {
    condition     = var.xcpng_vmlinux_disk_gb == null || var.xcpng_vmlinux_disk_gb >= 1
    error_message = "xcpng_vmlinux_disk_gb は 1 以上を指定してください。"
  }
}

variable "xcpng_template_ubuntu" {
  description = "Ubuntu テンプレートの name_label（例: k8s-ubuntu-vm を XO 上でテンプレ化/テンプレ作成したもの）"
  type        = string
  default     = "ubuntu-vm"
}

variable "xcpng_template_rhel" {
  description = "RHEL/AlmaLinux テンプレートの name_label"
  type        = string
  default     = "rhel-vm"
}

variable "network_force_create_network" {
  description = "If true, instruct network modules to always create networks"
  type        = bool
  default     = false
}
############################################
# Network Names
############################################
variable "network_names" {
  description = "Network names for creation"
  type        = map(string)
  default = {
    ext_mgmt  = "Pool-wide network associated with eth0"
    gpn_mgmt  = "GlobalPrivateManagementNetwork"
    k8s_net01 = "K8sNetwork01"
    k8s_net02 = "K8sNetwork02"
    core_net  = "coreNetwork"
  }

  validation {
    condition = alltrue([
      for network_name in values(var.network_names) : trimspace(network_name) != ""
    ])
    error_message = "network_names の値は空文字を許容しません。"
  }

}

variable "network_roles" {
  description = "Network role definitions (role -> network key list)"
  type        = map(list(string))
  default = {
    external_control_plane_network = ["ext_mgmt"]
    private_control_plane_network  = ["gpn_mgmt"]
    data_plane_network             = ["k8s_net01", "k8s_net02"]
    bgp_transport_network          = ["core_net"]
  }

  validation {
    condition = alltrue(flatten([
      for _, keys_list in var.network_roles : [
        for network_key in keys_list : contains(keys(var.network_names), network_key)
      ]
    ]))
    error_message = "network_roles の値は network_names で定義されたキーのみ指定可能です。"
  }
}

variable "network_options" {
  description = "Optional network parameters for each network"
  type = map(object({
    automatic         = optional(bool)
    default_is_locked = optional(bool)
    mtu               = optional(number)
    name_description  = optional(string)
    nbd               = optional(bool)
    vlan              = optional(number)
    source_pif_device = optional(string)
  }))
  default = {}

  validation {
    condition = alltrue([
      for network_key in keys(var.network_options) : contains(keys(var.network_names), network_key)
    ])
    error_message = "network_options のキーは network_names で定義したキーのみ指定可能です。"
  }
}

############################################
# VM Group Defaults
############################################
variable "vm_group_defaults" {
  description = "Optional default values for each VM group"
  type = map(object({
    default_template_type    = optional(string)
    default_firmware         = optional(string)
    default_resource_profile = optional(string)
    default_vcpus            = optional(number)
    default_memory_mb        = optional(number)
    default_disk_gb          = optional(number)
  }))
  default = {}
}

############################################
# VM Groups
############################################
variable "vm_groups" {
  description = "VM group definitions"
  type = map(map(object({
    template_type    = optional(string)
    firmware         = optional(string)
    resource_profile = optional(string)
    vcpus            = optional(number)
    memory_mb        = optional(number)
    disk_gb          = optional(number)
    networks = list(object({
      network_key = string
      mac_address = optional(string)
    }))
  })))
  default = {}

  validation {
    condition = alltrue(flatten([
      for group_name, vm_map in var.vm_groups : [
        for vm_name, _ in vm_map : length(regexall("/", group_name)) == 0 && length(regexall("/", vm_name)) == 0
      ]
    ]))
    error_message = "vm_groups のグループ名およびVM名には '/' を含めないでください。"
  }

  validation {
    condition = alltrue(flatten([
      for group_name, vm_map in var.vm_groups : [
        for _, vm in vm_map : contains(
          ["ubuntu", "rhel"],
          coalesce(vm.template_type, try(var.vm_group_defaults[group_name].default_template_type, null), "")
        )
      ]
    ]))
    error_message = "template_type は 'ubuntu' または 'rhel' を指定してください (vm_group_defaults での既定値指定も可)。"
  }

  validation {
    condition = alltrue(flatten([
      for group_name, vm_map in var.vm_groups : [
        for _, vm in vm_map : contains(
          ["uefi", "bios"],
          coalesce(vm.firmware, try(var.vm_group_defaults[group_name].default_firmware, null), "")
        )
      ]
    ]))
    error_message = "firmware は 'uefi' または 'bios' を指定してください (vm_group_defaults での既定値指定も可)。"
  }

  validation {
    condition = alltrue(flatten([
      for group_name, vm_map in var.vm_groups : [
        for _, vm in vm_map : contains(
          ["infrastructure", "vmlinux", "devlinux", "k8s_ctrlplane", "k8s_worker", "frr", "extgw"],
          coalesce(vm.resource_profile, try(var.vm_group_defaults[group_name].default_resource_profile, null), "")
        )
      ]
    ]))
    error_message = "resource_profile は定義済みプロファイル(infrastructure, vmlinux, devlinux, k8s_ctrlplane, k8s_worker, frr, extgw)を指定してください。"
  }

  validation {
    condition = alltrue(flatten([
      for _, vm_map in var.vm_groups : [
        for _, vm in vm_map : alltrue([
          for net in vm.networks : contains(
            toset(keys(var.network_names)),
            net.network_key
          )
        ])
      ]
    ]))
    error_message = "vm_groups.*.*.networks[*].network_key は network_names のキーを指定してください。"
  }
}