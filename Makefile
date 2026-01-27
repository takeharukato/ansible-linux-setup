#
# -*- mode: makefile-gmake; coding:utf-8 -*-
# Copyright 2019 Takeharu KATO
#
top=.
.PHONY: clean distclean run run_common run_user_settings run_create_users \
	run_devel_packages cloc mk_arc mk_role_arc ansible-lint \
	run_docker_ce run_ntp_server run_ntp_client run_nfs_server \
	run_ldap_server run_redmine_server \
	run_k8s_common run_k8s_ctrl_plane run_k8s_worker run_netgauge \
	run_k8s_worker_frr run_k8s_hubble_ui \
	run_dns_server run_selinux update-ctrlplane-kubeconfig update-worker-kubeconfig \
	run_terraform run_kea_dhcp run_radvd run_router_config \
	run_frr_basic run_gitlab_server run_sbom


# ansibleのログ表示レベル
VERBOSE=-vvv
# インベントリファイル
INVENTORY=inventory/hosts
# トップレベルプレイブック
TOP_PLAYBOOK=site.yml
# 共通オプション
OPT_COMMON=${VERBOSE} -i ${INVENTORY} ${TOP_PLAYBOOK}

# cloc の言語指定オプション
CLOC_LANG_OPT=--force-lang=YAML,j2
# cloc の除外ディレクトリ
# ここに列挙したディレクトリは cloc の集計対象から除外される
CLOC_EXCLUDES=--exclude-dir=.git,.venv
CLOC_EXCLUDE_EXTS=--exclude-ext=md,txt
# 先頭の "./" を取り除くユーティリティ
normalize = $(patsubst ./%,%,$(1))
# 末尾の "/" を取り除くユーティリティ
strip_trail = $(patsubst %/,%,$(1))

# アーカイブ対象ファイル
BASE_ARCHIVE_DIRS := docs group_vars host_vars inventory vars
# その他
EXTRA_ARCHIVE_DIRS := kitting
ANSIBLE_CFG	      := $(wildcard ${top}/*.cfg) $(wildcard ${top}/*.yml)
BASE_FILES        := Makefile Readme.md ${ANSIBLE_CFG} ${BASE_ARCHIVE_DIRS}

# 第2語以降をアーカイブ対象に追加する
ARGS_RAW := $(wordlist 2,$(words ${MAKECMDGOALS}),${MAKECMDGOALS})
# 先頭の "./" を取り除く
ARGS     := $(call normalize,$(ARGS_RAW))
# 末尾の "/" を取り除く
ARGS     := $(call strip_trail,${ARGS})

# 1個だけ指定ならそのbasename, 複数なら "selected"
ARGS_ONE_NAME := $(notdir $(firstword ${ARGS}))
ARCHIVE_NAME  := $(if $(filter 1,$(words ${ARGS})),${ARGS_ONE_NAME},selected)

# ARGS が空なら既定のディレクトリ群, あれば ARGS を使用
ARCHIVE_DIRS_OR_ARGS := $(if $(strip ${ARGS}),${ARGS},${BASE_ARCHIVE_DIRS} roles)

# ansible-lint の対象 (引数未指定時はカレントディレクトリ)
ANSIBLE_LINT_TARGETS := $(if $(strip ${ARGS}),${ARGS},.)

# 追加ゴールを .PHONY + 空レシピで潰す
# 追加ゴールはユーザ指定の生値(末尾スラッシュ等あり)と正規化後の両方を対象にする
ifneq ($(strip ${ARGS_RAW}),)
  $(foreach g,${ARGS_RAW} ${ARGS},$(eval .PHONY: $(g)))
  $(foreach g,${ARGS_RAW} ${ARGS},$(eval $(g):;@:))
endif

# 一括正規化 (先頭の "./" を取り除く)
BASE_FILES        := $(call normalize,${BASE_FILES})
BASE_ARCHIVE_DIRS := $(call normalize,${BASE_ARCHIVE_DIRS})
EXTRA_ARCHIVE_DIRS := $(call normalize,${EXTRA_ARCHIVE_DIRS})

DATE         := $(shell date +%Y%m%d)
ARCHIVE_ROOT := ansible-${DATE}

# GNU tar の使用を想定(--transform オプションを利用するため)
TAR := tar
# アーカイブ除外パターン
TAR_EXCLUDES := --exclude-vcs --exclude-backups \
                --exclude='*.swp' --exclude='*.tmp' --exclude='*~' \
		--exclude='*.iso' --exclude='user-data' --exclude='meta-data' \
		--exclude='ks.cfg'

all: run

mk_arc:
	@if [ -z "$(strip ${ARGS})" ]; then \
	  echo "Create archive (default set) with root ansible-${DATE}/"; \
	else \
	  echo "Create archive (selected paths) with root ansible-${DATE}/"; \
	  echo "  selected: ${ARGS}"; \
	  fail=0; for p in ${ARGS}; do \
	    if [ ! -e "$$p" ]; then echo "Error: not found: $$p"; fail=1; fi; \
	  done; [ $$fail -eq 0 ] || exit 1; \
	fi
	@bash -euo pipefail -c '\
	CURDIR_RT="$$(pwd -P)"; \
	ARCHIVE_ROOT_SH="${ARCHIVE_ROOT}"; \
	DATE_SH="${DATE}"; \
	TMPDIR="$$(mktemp -d)"; \
	trap '\''rm -rf "$$TMPDIR"'\'' EXIT INT TERM; \
	mkdir -p "$$TMPDIR/$$ARCHIVE_ROOT_SH"; \
	echo "Staging into $$TMPDIR/$$ARCHIVE_ROOT_SH/ ..."; \
	( cd "$$CURDIR_RT" && ${TAR} cpf - ${TAR_EXCLUDES} ${BASE_FILES} ${EXTRA_ARCHIVE_DIRS} ${ARCHIVE_DIRS_OR_ARGS} ) \
	| ( cd "$$TMPDIR/$$ARCHIVE_ROOT_SH" ; if [ "$$(id -u)" = 0 ]; then ${TAR} xpf - --same-owner; else ${TAR} xpf -; fi ); \
	echo "Packing $$CURDIR_RT/ansible-$$DATE_SH.tgz ..."; \
	( cd "$$TMPDIR" && ${TAR} zcf "$$CURDIR_RT/ansible-$$DATE_SH.tgz" "$$ARCHIVE_ROOT_SH" ) \
	'

mk_role_arc:
	@if [ -z "$(strip ${ARGS})" ]; then \
	  echo "Usage: make mk_role_arc <PATH1> [PATH2] ..."; \
	  exit 2; \
	fi
	@fail=0; \
	for p in ${ARGS}; do \
	  if [ ! -e "$$p" ]; then echo "Error: not found: $$p"; fail=1; fi; \
	done; \
	if [ $$fail -ne 0 ]; then exit 1; fi
	@bash -euo pipefail -c '\
	CURDIR_RT="$$(pwd -P)"; \
	ROOT_DIR_SH="ansible-${ARCHIVE_NAME}-${DATE}"; \
	TMPDIR="$$(mktemp -d)"; \
	trap '\''rm -rf "$$TMPDIR"'\'' EXIT INT TERM; \
	echo "Make archive $$CURDIR_RT/$$ROOT_DIR_SH.tgz (root: $$ROOT_DIR_SH/)"; \
	mkdir -p "$$TMPDIR/$$ROOT_DIR_SH"; \
	echo "Staging into $$TMPDIR/$$ROOT_DIR_SH/ ..."; \
	( cd "$$CURDIR_RT" && ${TAR} cpf - ${TAR_EXCLUDES} ${ARGS} ${BASE_FILES} ) \
	| ( cd "$$TMPDIR/$$ROOT_DIR_SH" ; if [ "$$(id -u)" = 0 ]; then ${TAR} xpf - --same-owner; else ${TAR} xpf -; fi ); \
	echo "Packing $$CURDIR_RT/$$ROOT_DIR_SH.tgz ..."; \
	( cd "$$TMPDIR" && ${TAR} zcf "$$CURDIR_RT/$$ROOT_DIR_SH.tgz" "$$ROOT_DIR_SH" ) \
	'

run:
	ansible-playbook ${OPT_COMMON} 2>&1 |tee build.log

run_selinux:
	ansible-playbook --tags "selinux" ${OPT_COMMON} 2>&1 |tee build-selinux.log

run_common:
	ansible-playbook --tags "common" ${OPT_COMMON} 2>&1 |tee build-common.log

run_user_settings:
	ansible-playbook --tags "user-settings" ${OPT_COMMON} 2>&1 |tee build-user-settings.log

run_create_users:
	ansible-playbook --tags "create-users" ${OPT_COMMON} 2>&1 |tee build-create-users.log

run_devel_packages:
	ansible-playbook --tags "devel-packages" ${OPT_COMMON} 2>&1 |tee build-devel.log

run_docker_ce:
	ansible-playbook --tags "docker-ce" ${OPT_COMMON} 2>&1 |tee build-docker-ce.log

run_ntp_server:
	ansible-playbook --tags "ntp-server" ${OPT_COMMON} 2>&1 |tee build-ntp-server.log

run_ntp_client:
	ansible-playbook --tags "ntp-client" ${OPT_COMMON} 2>&1 |tee build-ntp-server.log

run_nfs_server:
	ansible-playbook --tags "nfs-server" ${OPT_COMMON} 2>&1 |tee build-nfs-server.log

run_dns_server:
	ansible-playbook --tags "dns-server" ${OPT_COMMON} 2>&1 |tee build-dns-server.log

run_ldap_server:
	ansible-playbook --tags "ldap-server" ${OPT_COMMON} 2>&1 |tee build-ldap-server.log

run_redmine_server:
	ansible-playbook --tags "redmine-server" ${OPT_COMMON} 2>&1 |tee build-redmine-server.log

run_k8s_common:
	ansible-playbook --tags "k8s-common" ${OPT_COMMON} 2>&1 |tee build-k8s-common.log

run_k8s_ctrl_plane:
	ansible-playbook --tags "k8s-ctrlplane" ${OPT_COMMON} 2>&1 |tee build-k8s-ctrlplane.log

run_k8s_worker:
	ansible-playbook --tags "k8s-worker" ${OPT_COMMON} 2>&1 |tee build-k8s-worker.log

run_k8s_worker_frr:
	ansible-playbook --tags "k8s-worker-frr" ${OPT_COMMON} 2>&1 |tee build-k8s-worker-frr.log

run_k8s_hubble_ui:
	ansible-playbook --tags "k8s-hubble-ui" ${OPT_COMMON} 2>&1 |tee build-k8s-hubble-ui.log

run_netgauge:
	ansible-playbook --tags "netgauge" ${OPT_COMMON} 2>&1 |tee build-netgauge.log

run_frr_basic:
	ansible-playbook --tags "frr-basic" ${OPT_COMMON} 2>&1 |tee build-frr-basic.log

run_gitlab_server:
	ansible-playbook --tags "gitlab-server" ${OPT_COMMON} 2>&1 |tee build-gitlab-server.log

run_sbom:
	ansible-playbook --tags "sbom" ${OPT_COMMON} --extra-vars=sbom_enabled=true 2>&1 |tee build-sbom.log

run_terraform:
	ansible-playbook --tags "terraform" ${OPT_COMMON} 2>&1 |tee build-terraform.log

run_kea_dhcp:
	ansible-playbook --tags "kea-dhcp" ${OPT_COMMON} 2>&1 |tee build-kea-dhcp.log

run_radvd:
	ansible-playbook --tags "radvd" ${OPT_COMMON} 2>&1 |tee build-radvd.log

run_router_config:
	ansible-playbook --tags "router-config" ${OPT_COMMON} 2>&1 |tee build-router-config.log

update-ctrlplane-kubeconfig:
	ansible-playbook -i inventory/hosts k8s-ctrl-plane.yml --tags k8s-kubeconfig 2>&1 |tee build-update-ctrlplane-kubeconfig.log

update-worker-kubeconfig:
	ansible-playbook -i inventory/hosts k8s-worker.yml --tags k8s-kubeconfig 2>&1 |tee build-update-worker-kubeconfig.log

ansible-lint:
	@if ! command -v ansible-lint >/dev/null 2>&1; then \
	  echo "ansible-lint not found; skipping."; \
	else \
	  if [ -f ansible-lint.yml ]; then \
	    CONFIG_OPTION="-c ansible-lint.yml"; \
	  else \
	    CONFIG_OPTION=""; \
	  fi; \
	  echo "Running ansible-lint $${CONFIG_OPTION} ${ANSIBLE_LINT_TARGETS}"; \
	  ansible-lint $${CONFIG_OPTION} ${ANSIBLE_LINT_TARGETS}; \
	fi

cloc:
	cloc "${CLOC_LANG_OPT}" "${CLOC_EXCLUDES}" "${CLOC_EXCLUDE_EXTS}" .

clean:
	${RM} -f *.log

distclean: clean
	find . -name "*~"|xargs ${RM} -f
	${RM} -f ansible-*.tgz
	${RM} -f  *~
