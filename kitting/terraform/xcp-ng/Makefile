#
#  -*- coding:utf-8 mode:makefile -*-
#  Makefile using Terraform to build ansible-linux-setup environment on XCP-ng
#  Copyright (c) 2024 Takeharu KATO
#  SPDX-License-Identifier: BSD-2-Clause
#

.PHONY: clean clean-state distclean
.PHONY: init validate plan fmt
.PHONY: prepare build build-k8s destroy
.PHONY: networks destroy-networks
.PHONY: prune-unused-networks prune-unused-networks-dry-run
.PHONY: migrate migrate-infrastructure migrate-vmlinux migrate-devlinux migrate-k8s

TERRAFORM ?= terraform
TERRAFORM_FLAGS ?= -auto-approve

all: build

############################################
# Initialization and Validation
############################################
init:
	${TERRAFORM} init

validate: init
	${TERRAFORM} validate

plan: validate
	${TERRAFORM} plan

fmt:
	${TERRAFORM} fmt -recursive

prepare: init

############################################
# Networks
############################################
networks: prepare
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.network' 2>&1 | tee $@.log

destroy-networks: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.network' 2>&1 | tee $@.log

prune-unused-networks: prepare
	bash ./scripts/prune-unused-networks.sh --apply 2>&1 | tee $@.log

prune-unused-networks-dry-run: prepare
	bash ./scripts/prune-unused-networks.sh --dry-run 2>&1 | tee $@.log

############################################
# State Migration Targets
############################################
migrate: prepare
	bash ./scripts/migrate-all.sh

migrate-infrastructure: prepare
	bash ./scripts/migrate-state-infrastructure.sh

migrate-vmlinux: prepare
	bash ./scripts/migrate-state-vmlinux.sh

migrate-devlinux: prepare
	bash ./scripts/migrate-state-devlinux.sh

migrate-k8s: prepare
	bash ./scripts/migrate-state-k8s.sh

############################################
# Build and Destroy
############################################
build: prepare router mgmt-server vmlinux devlinux

build-k8s: apply-vms

destroy: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} 2>&1 | tee $@.log

############################################
# Cleanup
############################################
clean:
	${RM} -f *.log *~ \#*# *.swp *.bak


clean-state:
	${RM} -f *.tfstate*

distclean: clean clean-state
	${RM} -rf .terraform .terraform.lock.hcl *.backup

-include mk/vms.mk
