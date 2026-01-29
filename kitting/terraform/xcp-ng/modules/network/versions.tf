# versions.tf
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# 版数指定定義
# Terraform: 1.0以上
# vatesfr/xenorchestra: バージョン0系統
# (メジャーバージョン0固定,マイナーバージョン28以上)
#
terraform {
  required_version = ">= 1.0"
  required_providers {
    xenorchestra = {
      source  = "vatesfr/xenorchestra"
      version = "~> 0.28"
    }
  }
}
