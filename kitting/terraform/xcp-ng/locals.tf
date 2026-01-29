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
      disk_gb   = 256
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
  # ネットワークID (各モジュールの出力(outputs)から取得)
  ######################################################
  network_ids = {
    # 内部プライベートネットワーク
    gpn_mgmt  = module.network["gpn_mgmt"].network_id
    # K8sクラスタ1内ネットワーク
    k8s_net01 = module.network["k8s_net01"].network_id
    # K8sクラスタ2内ネットワーク
    k8s_net02 = module.network["k8s_net02"].network_id
    # FRR間通信用ネットワーク
    core_net  = module.network["core_net"].network_id
    # 外部接続管理ネットワーク (Pool-wide network)
    mgmt      = data.xenorchestra_network.mgmt.id
  }

  ############################################
  # テンプレートのID (データソースから取得)
  ############################################
  template_ids = {
    ubuntu = data.xenorchestra_template.ubuntu.id
    rhel   = data.xenorchestra_template.rhel.id
  }
}
