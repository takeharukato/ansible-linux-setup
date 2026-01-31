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

variable "xcpng_mgmt_network_name" {
  description = "管理/外部接続用ネットワークの name_label (VM Network相当)"
  type        = string
  default     = "VM Network"
}

variable "xcpng_private_network_name" {
  description = "内部管理用ネットワークの name_label"
  type        = string
  default     = "GlobalPrivateManagementNetwork"
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
  description = "Network names for creation or lookup"
  type = object({
    gpn_mgmt  = string
    k8s_net01 = string
    k8s_net02 = string
    core_net  = string
  })
  default = {
    gpn_mgmt  = "GlobalPrivateManagementNetwork"
    k8s_net01 = "K8sNetwork01"
    k8s_net02 = "K8sNetwork02"
    core_net  = "coreNetwork"
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
}

############################################
# Infrastructure VMs
############################################
variable "infrastructure_vms" {
  description = "Infrastructure VM definitions"
  type = map(object({
    template_type    = string
    firmware         = string
    resource_profile = string
    vcpus            = optional(number)
    memory_mb        = optional(number)
    disk_gb          = optional(number)
    networks = list(object({
      network_key = string
      mac_address = optional(string)
    }))
  }))
  default = {}

  validation {
    condition = alltrue([
      for k, v in var.infrastructure_vms : contains(["ubuntu", "rhel"], v.template_type)
    ])
    error_message = "template_type must be either 'ubuntu' or 'rhel'"
  }

  validation {
    condition = alltrue([
      for k, v in var.infrastructure_vms : contains(["uefi", "bios"], v.firmware)
    ])
    error_message = "firmware must be either 'uefi' or 'bios'"
  }
}

############################################
# Vmlinux Development VMs
############################################
variable "vmlinux_vms" {
  description = "Vmlinux VM definitions"
  type = map(object({
    template_type    = string
    firmware         = string
    resource_profile = string
    vcpus            = optional(number)
    memory_mb        = optional(number)
    disk_gb          = optional(number)
    networks = list(object({
      network_key = string
      mac_address = optional(string)
    }))
  }))
  default = {}

  validation {
    condition = alltrue([
      for k, v in var.vmlinux_vms : contains(["ubuntu", "rhel"], v.template_type)
    ])
    error_message = "template_type must be either 'ubuntu' or 'rhel'"
  }

  validation {
    condition = alltrue([
      for k, v in var.vmlinux_vms : contains(["uefi", "bios"], v.firmware)
    ])
    error_message = "firmware must be either 'uefi' or 'bios'"
  }
}

############################################
# Devlinux Development VMs
############################################
variable "devlinux_vms" {
  description = "Devlinux VM definitions"
  type = map(object({
    template_type    = string
    firmware         = string
    resource_profile = string
    vcpus            = optional(number)
    memory_mb        = optional(number)
    disk_gb          = optional(number)
    networks = list(object({
      network_key = string
      mac_address = optional(string)
    }))
  }))
  default = {}

  validation {
    condition = alltrue([
      for k, v in var.devlinux_vms : contains(["ubuntu", "rhel"], v.template_type)
    ])
    error_message = "template_type must be either 'ubuntu' or 'rhel'"
  }

  validation {
    condition = alltrue([
      for k, v in var.devlinux_vms : contains(["uefi", "bios"], v.firmware)
    ])
    error_message = "firmware must be either 'uefi' or 'bios'"
  }
}

############################################
# Kubernetes Lab VMs
############################################
variable "k8s_vms" {
  description = "Kubernetes lab VM definitions"
  type = map(object({
    template_type    = string
    firmware         = string
    resource_profile = string
    vcpus            = optional(number)
    memory_mb        = optional(number)
    disk_gb          = optional(number)
    networks = list(object({
      network_key = string
      mac_address = optional(string)
    }))
  }))
  default = {}

  validation {
    condition = alltrue([
      for k, v in var.k8s_vms : contains(["ubuntu", "rhel"], v.template_type)
    ])
    error_message = "template_type must be either 'ubuntu' or 'rhel'"
  }

  validation {
    condition = alltrue([
      for k, v in var.k8s_vms : contains(["uefi", "bios"], v.firmware)
    ])
    error_message = "firmware must be either 'uefi' or 'bios'"
  }
}