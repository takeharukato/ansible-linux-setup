#
#  -*- coding:utf-8 mode:makefile -*-
#  #  Makefile using Terraform to build  ansible-linux-setup environment on XCP-ng
#  Copyright (c) 2024 Takeharu KATO
#  SPDX-License-Identifier: BSD-2-Clause
#

.PHONY: clean clean-state distclean
.PHONY: init validate plan fmt
.PHONY: prepare build destroy
.PHONY: networks destroy-networks
.PHONY: router devserver rhel-server ubuntu-server mgmt-server
.PHONY: destroy-router destroy-devserver destroy-rhel-server destroy-ubuntu-server destroy-mgmt-server
.PHONY: devlinux1 devlinux2 devlinux3 devlinux4 devlinux5
.PHONY: destroy-devlinux1 destroy-devlinux2 destroy-devlinux3 destroy-devlinux4 destroy-devlinux5
.PHONY: vmlinux1 vmlinux2 vmlinux3 vmlinux4 vmlinux5
.PHONY: destroy-vmlinux1 destroy-vmlinux2 destroy-vmlinux3 destroy-vmlinux4 destroy-vmlinux5
.PHONY: devlinux destroy-devlinux
.PHONY: vmlinux destroy-vmlinux
.PHONY: k8sctrlplane01 k8sworker0101 k8sworker0102 frr01
.PHONY: k8sctrlplane02 k8sworker0201 k8sworker0202 frr02
.PHONY: destroy-k8sctrlplane01 destroy-k8sctrlplane02
.PHONY: destroy-frr01 destroy-frr02
.PHONY: destroy-k8sworker0101 destroy-k8sworker0102
.PHONY: destroy-k8sworker0201 destroy-k8sworker0202
.PHONY: destroy-cluster01 destroy-cluster02 destroy-extgw
.PHONY: cluster01 cluster02 extgw gateways frr
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

############################################
# Infrastructure VMs
############################################
router: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.infrastructure_vms["router"]' 2>&1 | tee $@.log

devserver: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.infrastructure_vms["devserver"]' 2>&1 | tee $@.log

rhel-server: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.infrastructure_vms["rhel-server"]' 2>&1 | tee $@.log

ubuntu-server: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.infrastructure_vms["ubuntu-server"]' 2>&1 | tee $@.log

mgmt-server: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.infrastructure_vms["mgmt-server"]' 2>&1 | tee $@.log

############################################
# devlinux VMs
############################################
devlinux1: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.devlinux_vms["devlinux1"]' 2>&1 | tee $@.log

devlinux2: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.devlinux_vms["devlinux2"]' 2>&1 | tee $@.log

devlinux3: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.devlinux_vms["devlinux3"]' 2>&1 | tee $@.log

devlinux4: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.devlinux_vms["devlinux4"]' 2>&1 | tee $@.log

devlinux5: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.devlinux_vms["devlinux5"]' 2>&1 | tee $@.log

devlinux: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.devlinux_vms' 2>&1 | tee $@.log

############################################
# vmlinux VMs
############################################
vmlinux1: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vmlinux_vms["vmlinux1"]' 2>&1 | tee $@.log

vmlinux2: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vmlinux_vms["vmlinux2"]' 2>&1 | tee $@.log

vmlinux3: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vmlinux_vms["vmlinux3"]' 2>&1 | tee $@.log

vmlinux4: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vmlinux_vms["vmlinux4"]' 2>&1 | tee $@.log

vmlinux5: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vmlinux_vms["vmlinux5"]' 2>&1 | tee $@.log

vmlinux: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vmlinux_vms' 2>&1 | tee $@.log

############################################
# Kubernetes Lab VMs
############################################
k8sctrlplane01: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.k8s_vms["k8sctrlplane01"]' 2>&1 | tee $@.log

k8sworker0101: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.k8s_vms["k8sworker0101"]' 2>&1 | tee $@.log

k8sworker0102: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.k8s_vms["k8sworker0102"]' 2>&1 | tee $@.log

frr01: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.k8s_vms["frr01"]' 2>&1 | tee $@.log

k8sctrlplane02: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.k8s_vms["k8sctrlplane02"]' 2>&1 | tee $@.log

k8sworker0201: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.k8s_vms["k8sworker0201"]' 2>&1 | tee $@.log

k8sworker0202: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.k8s_vms["k8sworker0202"]' 2>&1 | tee $@.log

frr02: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.k8s_vms["frr02"]' 2>&1 | tee $@.log

extgw: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.k8s_vms["extgw"]' 2>&1 | tee $@.log

cluster01: networks k8sctrlplane01 k8sworker0101 k8sworker0102 frr01

cluster02: networks k8sctrlplane02 k8sworker0201 k8sworker0202 frr02

frr: networks frr01 frr02

gateways: networks extgw frr01 frr02

############################################
# Destroy Infrastructure VMs
############################################
destroy-router: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.infrastructure_vms["router"]' 2>&1 | tee $@.log

destroy-devserver: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.infrastructure_vms["devserver"]' 2>&1 | tee $@.log

destroy-rhel-server: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.infrastructure_vms["rhel-server"]' 2>&1 | tee $@.log

destroy-ubuntu-server: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.infrastructure_vms["ubuntu-server"]' 2>&1 | tee $@.log

destroy-mgmt-server: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.infrastructure_vms["mgmt-server"]' 2>&1 | tee $@.log

############################################
# Destroy devlinux VMs
############################################
destroy-devlinux1: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.devlinux_vms["devlinux1"]' 2>&1 | tee $@.log

destroy-devlinux2: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.devlinux_vms["devlinux2"]' 2>&1 | tee $@.log

destroy-devlinux3: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.devlinux_vms["devlinux3"]' 2>&1 | tee $@.log

destroy-devlinux4: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.devlinux_vms["devlinux4"]' 2>&1 | tee $@.log

destroy-devlinux5: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.devlinux_vms["devlinux5"]' 2>&1 | tee $@.log

destroy-devlinux: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.devlinux_vms' 2>&1 | tee $@.log

############################################
# Destroy Vmlinux VMs
############################################
destroy-vmlinux1: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vmlinux_vms["vmlinux1"]' 2>&1 | tee $@.log

destroy-vmlinux2: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vmlinux_vms["vmlinux2"]' 2>&1 | tee $@.log

destroy-vmlinux3: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vmlinux_vms["vmlinux3"]' 2>&1 | tee $@.log

destroy-vmlinux4: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vmlinux_vms["vmlinux4"]' 2>&1 | tee $@.log

destroy-vmlinux5: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vmlinux_vms["vmlinux5"]' 2>&1 | tee $@.log

destroy-vmlinux: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vmlinux_vms' 2>&1 | tee $@.log

############################################
# Destroy K8s VMs
############################################
destroy-k8sctrlplane01: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.k8s_vms["k8sctrlplane01"]' 2>&1 | tee $@.log

destroy-k8sworker0101: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.k8s_vms["k8sworker0101"]' 2>&1 | tee $@.log

destroy-k8sworker0102: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.k8s_vms["k8sworker0102"]' 2>&1 | tee $@.log

destroy-frr01: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.k8s_vms["frr01"]' 2>&1 | tee $@.log

destroy-k8sctrlplane02: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.k8s_vms["k8sctrlplane02"]' 2>&1 | tee $@.log

destroy-k8sworker0201: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.k8s_vms["k8sworker0201"]' 2>&1 | tee $@.log

destroy-k8sworker0202: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.k8s_vms["k8sworker0202"]' 2>&1 | tee $@.log

destroy-frr02: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.k8s_vms["frr02"]' 2>&1 | tee $@.log

destroy-extgw: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.k8s_vms["extgw"]' 2>&1 | tee $@.log

destroy-cluster01: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.k8s_vms["k8sctrlplane01"]' -target='module.k8s_vms["k8sworker0101"]' -target='module.k8s_vms["k8sworker0102"]' -target='module.k8s_vms["frr01"]' 2>&1 | tee $@.log

destroy-cluster02: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.k8s_vms["k8sctrlplane02"]' -target='module.k8s_vms["k8sworker0201"]' -target='module.k8s_vms["k8sworker0202"]' -target='module.k8s_vms["frr02"]' 2>&1 | tee $@.log

############################################
# State Migration Targets
############################################
migrate: prepare
	./scripts/migrate-all.sh

migrate-infrastructure: prepare
	./scripts/migrate-state-infrastructure.sh

migrate-vmlinux: prepare
	./scripts/migrate-state-vmlinux.sh

migrate-devlinux: prepare
	./scripts/migrate-state-devlinux.sh

migrate-k8s: prepare
	./scripts/migrate-state-k8s.sh

############################################
# Build and Destroy
############################################
build: prepare router mgmt-server vmlinux devlinux

build-k8s: cluster01 cluster02 extgw

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
