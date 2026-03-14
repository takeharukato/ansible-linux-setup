# VM/Cluster operation rules

.PHONY: apply-vms destroy-vms apply-vm destroy-vm apply-cluster destroy-cluster
.PHONY: router devserver rhel-server ubuntu-server mgmt-server
.PHONY: devlinux1 devlinux2 devlinux3 devlinux4 devlinux5
.PHONY: vmlinux1 vmlinux2 vmlinux3 vmlinux4 vmlinux5
.PHONY: k8sctrlplane01 k8sworker0101 k8sworker0102 frr01
.PHONY: k8sctrlplane02 k8sworker0201 k8sworker0202 frr02
.PHONY: extgw cluster01 cluster02 gateways frr
.PHONY: destroy-router destroy-devserver destroy-rhel-server destroy-ubuntu-server destroy-mgmt-server
.PHONY: destroy-devlinux1 destroy-devlinux2 destroy-devlinux3 destroy-devlinux4 destroy-devlinux5
.PHONY: destroy-vmlinux1 destroy-vmlinux2 destroy-vmlinux3 destroy-vmlinux4 destroy-vmlinux5
.PHONY: destroy-k8sctrlplane01 destroy-k8sworker0101 destroy-k8sworker0102 destroy-frr01
.PHONY: destroy-k8sctrlplane02 destroy-k8sworker0201 destroy-k8sworker0202 destroy-frr02
.PHONY: destroy-extgw destroy-cluster01 destroy-cluster02
.PHONY: infrastructure devlinux vmlinux k8s destroy-infrastructure destroy-devlinux destroy-vmlinux destroy-k8s

# destroy後にunused network pruneを実行するか
DESTROY_PRUNE ?= true

define RUN_PRUNE_AFTER_DESTROY
	@if [ "${DESTROY_PRUNE}" = "true" ]; then \
		${MAKE} prune-unused-networks; \
	else \
		echo "INFO: DESTROY_PRUNE=false のため unused network prune をスキップします。"; \
	fi
endef

# Generic VM operations
apply-vms: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms' 2>&1 | tee $@.log

destroy-vms: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

apply-vm: networks
	@if [ -z "${VM_KEY}" ]; then echo "VM_KEY=group/vm を指定してください"; exit 1; fi
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["${VM_KEY}"]' 2>&1 | tee $@.log

destroy-vm: prepare
	@if [ -z "${VM_KEY}" ]; then echo "VM_KEY=group/vm を指定してください"; exit 1; fi
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["${VM_KEY}"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

# Group operations
infrastructure: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms' 2>&1 | tee $@.log

devlinux: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms' 2>&1 | tee $@.log

vmlinux: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms' 2>&1 | tee $@.log

k8s: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms' 2>&1 | tee $@.log

destroy-infrastructure: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-devlinux: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-vmlinux: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-k8s: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

# Legacy single-node wrappers using new group/vm keys
router: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["infrastructure/router"]' 2>&1 | tee $@.log

devserver: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["infrastructure/devserver"]' 2>&1 | tee $@.log

rhel-server: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["infrastructure/rhel-server"]' 2>&1 | tee $@.log

ubuntu-server: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["infrastructure/ubuntu-server"]' 2>&1 | tee $@.log

mgmt-server: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["infrastructure/mgmt-server"]' 2>&1 | tee $@.log

devlinux1: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["devlinux/devlinux1"]' 2>&1 | tee $@.log

devlinux2: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["devlinux/devlinux2"]' 2>&1 | tee $@.log

devlinux3: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["devlinux/devlinux3"]' 2>&1 | tee $@.log

devlinux4: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["devlinux/devlinux4"]' 2>&1 | tee $@.log

devlinux5: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["devlinux/devlinux5"]' 2>&1 | tee $@.log

vmlinux1: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["vmlinux/vmlinux1"]' 2>&1 | tee $@.log

vmlinux2: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["vmlinux/vmlinux2"]' 2>&1 | tee $@.log

vmlinux3: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["vmlinux/vmlinux3"]' 2>&1 | tee $@.log

vmlinux4: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["vmlinux/vmlinux4"]' 2>&1 | tee $@.log

vmlinux5: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["vmlinux/vmlinux5"]' 2>&1 | tee $@.log

k8sctrlplane01: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["k8s/k8sctrlplane01"]' 2>&1 | tee $@.log

k8sworker0101: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["k8s/k8sworker0101"]' 2>&1 | tee $@.log

k8sworker0102: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["k8s/k8sworker0102"]' 2>&1 | tee $@.log

frr01: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["k8s/frr01"]' 2>&1 | tee $@.log

k8sctrlplane02: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["k8s/k8sctrlplane02"]' 2>&1 | tee $@.log

k8sworker0201: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["k8s/k8sworker0201"]' 2>&1 | tee $@.log

k8sworker0202: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["k8s/k8sworker0202"]' 2>&1 | tee $@.log

frr02: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["k8s/frr02"]' 2>&1 | tee $@.log

extgw: networks
	${TERRAFORM} apply ${TERRAFORM_FLAGS} -target='module.vms["k8s/extgw"]' 2>&1 | tee $@.log

cluster01: networks k8sctrlplane01 k8sworker0101 k8sworker0102 frr01
cluster02: networks k8sctrlplane02 k8sworker0201 k8sworker0202 frr02
frr: networks frr01 frr02
gateways: networks extgw frr01 frr02

destroy-router: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["infrastructure/router"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-devserver: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["infrastructure/devserver"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-rhel-server: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["infrastructure/rhel-server"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-ubuntu-server: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["infrastructure/ubuntu-server"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-mgmt-server: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["infrastructure/mgmt-server"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-devlinux1: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["devlinux/devlinux1"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-devlinux2: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["devlinux/devlinux2"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-devlinux3: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["devlinux/devlinux3"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-devlinux4: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["devlinux/devlinux4"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-devlinux5: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["devlinux/devlinux5"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-vmlinux1: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["vmlinux/vmlinux1"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-vmlinux2: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["vmlinux/vmlinux2"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-vmlinux3: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["vmlinux/vmlinux3"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-vmlinux4: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["vmlinux/vmlinux4"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-vmlinux5: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["vmlinux/vmlinux5"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-k8sctrlplane01: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["k8s/k8sctrlplane01"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-k8sworker0101: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["k8s/k8sworker0101"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-k8sworker0102: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["k8s/k8sworker0102"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-frr01: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["k8s/frr01"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-k8sctrlplane02: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["k8s/k8sctrlplane02"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-k8sworker0201: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["k8s/k8sworker0201"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-k8sworker0202: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["k8s/k8sworker0202"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-frr02: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["k8s/frr02"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-extgw: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["k8s/extgw"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-cluster01: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["k8s/k8sctrlplane01"]' -target='module.vms["k8s/k8sworker0101"]' -target='module.vms["k8s/k8sworker0102"]' -target='module.vms["k8s/frr01"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)

destroy-cluster02: prepare
	${TERRAFORM} destroy ${TERRAFORM_FLAGS} -target='module.vms["k8s/k8sctrlplane02"]' -target='module.vms["k8s/k8sworker0201"]' -target='module.vms["k8s/k8sworker0202"]' -target='module.vms["k8s/frr02"]' 2>&1 | tee $@.log
	$(RUN_PRUNE_AFTER_DESTROY)
