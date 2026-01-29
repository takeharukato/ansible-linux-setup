# outputs.tf
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# VM/ネットワーク情報の出力定義
#

########################################################################################
# Infrastructure VMの情報
# - 仮想環境内部プライベートネットワーク<=>Pool-wideネットワーク間ルータ (router)
# - 管理サーバ (mgmt-server)
# - RHEL管理サーバ検証用VM(rhel-server)
# - Ubuntu管理サーバ検証用VM(ubuntu-server)
# - 旧管理サーバ (devserver)
########################################################################################
output "infrastructure_vms" {
  description = "Infrastructure VM information (IDs, names, IPs)"
  value = {
    for k, v in module.infrastructure_vms : k => {
      id   = v.vm_id
      name = k
      ips  = v.vm_ips
    }
  }
}

#############################################
# vmlinux 開発 VM (vmlinux1 - vmlinux5)の情報
# pool-wide networkに接続
#############################################
output "vmlinux_vms" {
  description = "Vmlinux VM information (IDs, names, IPs)"
  value = {
    for k, v in module.vmlinux_vms : k => {
      id   = v.vm_id
      name = k
      ips  = v.vm_ips
    }
  }
}

#####################################################
# devlinux 開発用VM ( devlinux1 - devlinux5 )の情報
# 内部プライベートネットワークのみに接続
#####################################################
output "devlinux_vms" {
  description = "Devlinux VM information (IDs, names, IPs)"
  value = {
    for k, v in module.devlinux_vms : k => {
      id   = v.vm_id
      name = k
      ips  = v.vm_ips
    }
  }
}

############################################
# Kubernetes クラスタを構成するVM群の情報
# - extgw 疑似外部ネットワークのゲートウエイ
# - frr01-02 各K8sクラスタの代表FRRサーバ
# - k8sctrlplane01-02 K8sコントロールプレイン
# - k8sworker0101-0202 K8sワーカーノード
############################################
output "k8s_vms" {
  description = "Kubernetes lab VM information (IDs, names, IPs)"
  value = {
    for k, v in module.k8s_vms : k => {
      id   = v.vm_id
      name = k
      ips  = v.vm_ips
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
