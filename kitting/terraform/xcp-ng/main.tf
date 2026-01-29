# Provider Configuration for XenOrchestra
#
# Copyright 2025 Takeharu KATO  All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#
# 留意事項: Terraformの版数制約条件は, 各ディレクトリのversions.tfで定義
#

# Xen Orchestra接続情報
# 指定する値をterraform.tfvarsに記載することで
# 以下に反映させる
provider "xenorchestra" {
  # XCP-ng は通常 Xen Orchestra (XO) 経由で管理します。
  # ws / wss を指定してください (例: wss://xo.example.local)
  url      = var.xoa_url
  # Xen Orchestraログイン名
  username = var.xoa_username
  # Xen Orchestraログインパスワード
  password = var.xoa_password
  # 自己証明書によるホストへの接続を許容する
  insecure = var.xoa_insecure
}
