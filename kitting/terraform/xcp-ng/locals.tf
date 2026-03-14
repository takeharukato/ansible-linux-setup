# locals.tf
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# リソース量算出用ローカル変数
#

############################################
# プロファイル毎のリソース量のデフォルト値
############################################
locals {
  vm_resource_defaults = {

    # Infrastructure
    infrastructure = {
      vcpus     = 4
      memory_mb = 4096
      disk_gb   = 128
    }

    # 外部ネットワーク(pool-wide network)接続開発用VM
    vmlinux = {
      vcpus     = 4
      memory_mb = 4096
      disk_gb   = 128
    }

    # 内部プライベートネットワーク接続開発用VM
    devlinux = {
      vcpus     = 4
      memory_mb = 4096
      disk_gb   = 128
    }

    # k8sのコントロールプレイン
    k8s_ctrlplane = {
      vcpus     = 4
      memory_mb = 4096
      disk_gb   = 25
    }

    # K8sのワーカーノード
    k8s_worker = {
      vcpus     = 4
      memory_mb = 4096
      disk_gb   = 25
    }

    # FRR ノード
    frr = {
      vcpus     = 2
      memory_mb = 2048
      disk_gb   = 25
    }

    # 疑似外部ネットワーク接続ゲートウエイサーバ
    extgw = {
      vcpus     = 2
      memory_mb = 2048
      disk_gb   = 25
    }
  }

  ######################################################
  # ネットワークID
  # - network_names で定義した全キーを動的に解決
  # - external_control_plane_network は既存ネットワーク参照
  # - それ以外は Terraform 管理ネットワークを参照
  ######################################################
  network_ids = merge(
    {
      for network_key, network_module in module.network :
      network_key => network_module.network_id
    },
    {
      for network_key, network_data in data.xenorchestra_network.existing :
      network_key => network_data.id
    }
  )

  ############################################
  # VMインスタンス定義
  # - vm_groups を module for_each 用にフラット化
  # - vm_group_defaults で未指定項目を補完
  ############################################
  vm_instances = merge([
    for group_name, vm_map in var.vm_groups : {
      for vm_name, vm in vm_map : "${group_name}/${vm_name}" => {
        group_name = group_name
        vm_name    = vm_name
        template_type = (
          try(vm.template_type, null) != null
          ? vm.template_type
          : try(var.vm_group_defaults[group_name].default_template_type, null)
        )
        firmware = (
          try(vm.firmware, null) != null
          ? vm.firmware
          : try(var.vm_group_defaults[group_name].default_firmware, null)
        )
        resource_profile = (
          try(vm.resource_profile, null) != null
          ? vm.resource_profile
          : try(var.vm_group_defaults[group_name].default_resource_profile, null)
        )
        vcpus = (
          try(vm.vcpus, null) != null
          ? vm.vcpus
          : (
            try(var.vm_group_defaults[group_name].default_vcpus, null) != null
            ? var.vm_group_defaults[group_name].default_vcpus
            : try(local.vm_resource_defaults[(
              try(vm.resource_profile, null) != null
              ? vm.resource_profile
              : try(var.vm_group_defaults[group_name].default_resource_profile, "")
            )].vcpus, null)
          )
        )
        memory_mb = (
          try(vm.memory_mb, null) != null
          ? vm.memory_mb
          : (
            try(var.vm_group_defaults[group_name].default_memory_mb, null) != null
            ? var.vm_group_defaults[group_name].default_memory_mb
            : try(local.vm_resource_defaults[(
              try(vm.resource_profile, null) != null
              ? vm.resource_profile
              : try(var.vm_group_defaults[group_name].default_resource_profile, "")
            )].memory_mb, null)
          )
        )
        disk_gb = (
          try(vm.disk_gb, null) != null
          ? vm.disk_gb
          : (
            try(var.vm_group_defaults[group_name].default_disk_gb, null) != null
            ? var.vm_group_defaults[group_name].default_disk_gb
            : try(local.vm_resource_defaults[(
              try(vm.resource_profile, null) != null
              ? vm.resource_profile
              : try(var.vm_group_defaults[group_name].default_resource_profile, "")
            )].disk_gb, null)
          )
        )
        networks = vm.networks
      }
    }
  ]...)

  ############################################
  # テンプレートのID (データソースから取得)
  ############################################
  template_ids = {
    ubuntu = data.xenorchestra_template.ubuntu.id
    rhel   = data.xenorchestra_template.rhel.id
  }
}
