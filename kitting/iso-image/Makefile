#
#  -*- coding:utf-8 mode:makefile -*-
#  Makefile for cloud-init ISO image for Ubuntu
#  Copyright (c) 2024 Takeharu KATO
#  SPDX-License-Identifier: BSD-2-Clause
#  Notes: Portions of this codebase were initially drafted with ChatGPT assistance.
#

# ---- Package sets & installer wrappers (edit here to change installers) ----
# パッケージセット & インストーララッパ (インストーラを変更時はここを編集)
# 注意: このMakefileは権限昇格に'sudo'の存在を前提としています.
# このプロジェクトに必要なAPTパッケージ
APT_PACKAGES := cloud-image-utils gettext-base genisoimage whois
# Snapパッケージ (スペース区切り)
SNAP_PACKAGES := yq
# インストーラコマンド (apt から apt-getの変更やフラグ追加などを容易にするため集中管理)
APT_GET := apt-get
SNAP := snap
APT_UPDATE  := sudo ${APT_GET} update
APT_INSTALL := sudo ${APT_GET} install -y
SNAP_LIST   := ${SNAP} list
SNAP_INSTALL:= sudo ${SNAP} install
# ---------------------------------------------------------------------------

# User configuration (edit here to customize) ------
# ユーザ設定 (カスタマイズする場合はここを編集)
# ユーザ名 (デフォルト: ansible)
USER_NAME   ?= ansible
# ユーザのGECOSフィールド (デフォルト: Ansible User)
USER_NAME_GECOS ?= Ansible User

# パスワードハッシュ生成コマンド（Debian/Ubuntu: whois パッケージの mkpasswd）
MKPASSWD ?= mkpasswd

# ユーザのパスワードハッシュ
# USER_NAME を“平文パスワード”として yescrypt でハッシュ化,
# 作成方法の例:
#  mkpasswd -m yescrypt '${USER_NAME}'
# または
#  openssl passwd -6 '${USER_NAME}'
# Make の $ エスケープ対策で $→$$ に変換
# 例) mkpasswd -m yescrypt 'ansible' の結果を $$y$$j9T$$... の形で格納
# 注意: envsubstに引き渡す際は, '${USER_PASSWD_HASH}'のようにシングルクォート
# 囲み, $文字が展開されないようにする(ダブルクォートだと, $が変数展開され,
# 文字列が破壊されるため)。
# mkpasswd（whoisパッケージ）で USER_NAME を平文にした yescrypt ハッシュを作成
MKPASSWD ?= mkpasswd
# 生ハッシュ（$ を含む）
USER_PASSWD_HASH_RAW := $(shell $(MKPASSWD) -m yescrypt '$(USER_NAME)')
# make 変数内で $ → $$ にエスケープ（後段で shell に渡すときに $$ → $ に戻る）
USER_PASSWD_HASH := $(subst $,$$,$(USER_PASSWD_HASH_RAW))

# GitHubから公開鍵を取得するために使用するGitHubのユーザ名
# (デフォルト: sampleuser)
GITHUB_USER ?= sampleuser
RHEL_IMAGE_URL_PREFIX ?= https://repo.almalinux.org/almalinux/9/isos/x86_64
RHEL_ISO_BASE   ?= AlmaLinux-9.6-x86_64-dvd
RHEL_ISO   ?= ${RHEL_ISO_BASE}.iso
RHEL_ISO_OUT ?= ${RHEL_ISO_BASE}-ks.iso
# ---------------------------------------------------

# ---- Utility commands (usually no need to edit here) ----
# ユーティリティコマンド (通常はここを編集する必要はありません)
RM := rm -f
MKDIR := mkdir -p
GENISOIMAGE_CMD := genisoimage
BASE64_CMD := sh -c 'if base64 --help 2>&1 | grep -q " -w "; then base64 -w0 "$$1"; else base64 "$$1" | tr -d "\n"; fi' sh
YQ := /snap/bin/yq
# ----------------------------------------------------------

# ---- Targets & variables (usually no need to edit here) ----
# ターゲット & 変数 (通常はここを編集する必要はありません)
# Ubuntuのテンプレート
UBUNTU_TMPL_DIR=tmpl/ubuntu
# Ubuntu関連スクリプト
UBUNTU_SCRIPT_DIR=scripts/ubuntu
# RHELのテンプレート
RHEL_TMPL_DIR=tmpl/rhel
# RHELのスクリプト
RHEL_SCRIPT_DIR=scripts/rhel
# ホスト名設定スクリプト(Ubuntu)
UPDATE_HOSTNAME=update-hostname.sh
UPDATE_HOSTNAME_PATH := ${UBUNTU_SCRIPT_DIR}/${UPDATE_HOSTNAME}
# base64エンコードされたホスト名設定スクリプトの出力先
B64    := build/${UPDATE_HOSTNAME}.b64
# cloud-init user-data テンプレートファイル
USERDATA_TPL := ${UBUNTU_TMPL_DIR}/user-data.tmpl
# cloud-init meta-data テンプレートファイル
METADATA_TPL := ${UBUNTU_TMPL_DIR}/meta-data.tmpl
# Kickstartテンプレートファイル
KS_CFG_TPL := ${RHEL_TMPL_DIR}/ks.cfg.tmpl
BASE_REPO_URL := http://mirror.almalinux.org/almalinux/9/BaseOS/x86_64/os/
# AppStreamリポジトリを利用するためのURL
APP_STREAM_REPO_URL := http://mirror.almalinux.org/almalinux/9/AppStream/x86_64/os/
# RHEL系のインストールイメージを作成するスクリプト
MKRHEL_IMAGE := ${RHEL_SCRIPT_DIR}/mk-rhel-image.sh
# (テンプレートから生成される) cloud-init user-data 出力先
USERDATA     := user-data
# (テンプレートから生成される) Kickstartファイル
# (Red Hat系の自動インストール設定ファイル)
KS_CFG := ks.cfg

# seed.iso (cloud-initのシードISOイメージ) 出力先
# 補足:
# シードISOイメージとは, cloud-initがインスタンス起動時に読み込む設定データを含むISO 9660形式の仮想CD-ROMイメージを指す。
# このISOイメージには, 主に以下の2つのファイルが含まれる:
# 1. user-data: インスタンスの初期設定を定義するYAML形式のファイル。
#               ユーザアカウントの作成, SSH鍵の設定, パッケージのインストール,
#               スクリプトの実行などの設定が含まれる。
# 2. meta-data: インスタンスのメタ情報を含むファイル。
#               インスタンスIDやホスト名などの情報が含まれる。
#
# cloud-initは, インスタンスの起動時にこのISOイメージをマウントし,
# user-dataとmeta-dataファイルを読み取って初期設定を行う。
# これにより, ユーザはインスタンスの起動時に必要な設定を自動化できる。
#
SEED_ISO := seed.iso
# envsubst に通す変数のホワイトリスト ( $ を $$ にエスケープ）
# user-data.tmpl 内で置換する対象となる各変数について,
# (Makefile中でシェル変数を表記する流儀に従い)$ を $$ にエスケープして,
# かつ, 空白区切りで列挙
# (注意: 変数全体は, シングルクォートで囲むこと)
ENVSUBST_VARS := '$${USER_NAME} $${USER_NAME_GECOS} $${USER_PASSWD_HASH} $${GITHUB_USER} $${BASE_REPO_URL} $${APP_STREAM_REPO_URL}'
# ----------------------------------------------------------

.PHONY: prepare generate clean build

all: generate

# meta-data生成レシピ
# 注意: ターゲットがファイルのため非.PHONYのままにすること.
# このターゲットはメタデータが存在しない場合にのみ作成するため,
# リポジトリ内にカスタムメタデータが存在する場合は上書きされない
meta-data:
	@echo '>>> render $@ via USER_NAME=${USER_NAME} USER_NAME_GECOS=${USER_NAME_GECOS} USER_PASSWD_HASH=${USER_PASSWD_HASH} GITHUB_USER=${GITHUB_USER}'
	USER_NAME="${USER_NAME}" USER_NAME_GECOS="${USER_NAME_GECOS}" \
	USER_PASSWD_HASH='${USER_PASSWD_HASH}' GITHUB_USER="${GITHUB_USER}" \
	BASE_REPO_URL="${BASE_REPO_URL}" APP_STREAM_REPO_URL="${APP_STREAM_REPO_URL}" \
	envsubst ${ENVSUBST_VARS} < "${METADATA_TPL}" > $@
	@echo ">>> ensure $@"
	@test -f $@ || printf '%s\n' 'instance-id: ubuntu-autoinstall' > $@

prepare:
	@echo ">>> prepare environment"
# 必要なAPTパッケージをインストール
	${APT_UPDATE} && ${APT_INSTALL} ${APT_PACKAGES}
# Snapパッケージがインストールされていない場合にのみインストール (繰り返し実行時の無駄を減らすため)
	for p in ${SNAP_PACKAGES}; do ${SNAP_LIST} $$p >/dev/null 2>&1 || ${SNAP_INSTALL} $$p; done

build:
	${MKDIR} $@

${B64}: ${UPDATE_HOSTNAME_PATH} | build
	echo ">>> encode ${UPDATE_HOSTNAME_PATH} -> ${B64}"
	${BASE64_CMD} "${UPDATE_HOSTNAME_PATH}" > "${B64}"

${USERDATA}: prepare ${USERDATA_TPL} ${B64}
	@echo '>>> render $@ via yq USER_NAME=${USER_NAME} USER_NAME_GECOS=${USER_NAME_GECOS} USER_PASSWD_HASH=${USER_PASSWD_HASH} GITHUB_USER=${GITHUB_USER}'
	USER_NAME="${USER_NAME}" USER_NAME_GECOS="${USER_NAME_GECOS}" \
	USER_PASSWD_HASH='${USER_PASSWD_HASH}' GITHUB_USER="${GITHUB_USER}" \
	BASE_REPO_URL="${BASE_REPO_URL}" APP_STREAM_REPO_URL="${APP_STREAM_REPO_URL}" \
		envsubst ${ENVSUBST_VARS} < "${USERDATA_TPL}" > $@.tmp
	${YQ} eval -i "(.autoinstall.\"user-data\".write_files[] | select(.path==\"/var/tmp/update-hostname.sh\") | .content) |= load_str(\"${B64}\")" $@.tmp
	mv $@.tmp $@

${KS_CFG}: prepare ${KS_CFG_TPL}
	@echo ">>> render $@ via envsubst"
	USER_NAME="${USER_NAME}" USER_NAME_GECOS="${USER_NAME_GECOS}" \
	USER_PASSWD_HASH='${USER_PASSWD_HASH}' GITHUB_USER="${GITHUB_USER}" \
	BASE_REPO_URL="${BASE_REPO_URL}" APP_STREAM_REPO_URL="${APP_STREAM_REPO_URL}" \
		envsubst ${ENVSUBST_VARS} < "${KS_CFG_TPL}" > $@

generate: prepare ${USERDATA} meta-data
	${RM} -f "${SEED_ISO}"
	${GENISOIMAGE_CMD} -output "${SEED_ISO}" \
	  -volid "CIDATA" \
	  -input-charset "utf-8" \
	  -joliet -rock \
	  user-data \
	  meta-data

build-rhel-image: prepare ${KS_CFG} ${MKRHEL_IMAGE}
	@echo ">>> build RHEL-based image"
	env KS_FILE="${KS_CFG}" \
	    IMAGE_URL_PREFIX="${RHEL_IMAGE_URL_PREFIX}" \
	    ISO_IMAGE="${RHEL_ISO}" \
            RHEL_ISO_OUT="${RHEL_ISO_OUT}" \
            bash "${MKRHEL_IMAGE}"

clean:
	${RM} -f *~ "${SEED_ISO}" "${USERDATA}" meta-data "${B64}" "${RHEL_ISO_OUT}" "${KS_CFG}"
	${RM} -fr build work
