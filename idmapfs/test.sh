#!/bin/bash -xe

self=$(readlink -q -s -f $0 || echo $0)
homedir=${self%/*}

. ${homedir}/host-tests.rc
. ${homedir}/guest/tests.rc

rm -rfv ${SANDBOX_ROOT:?Please define}
cd ${KERNEL_SOURCE:?Please define}
make modules
make INSTALL_MOD_PATH=${SANDBOX_ROOT} modules_install

qemu-system-x86_64 \
	~/work/vm/vdisk.qcow2 \
	-hdc ~/work/vm/secondhd.raw \
	-enable-kvm \
	-m 1024 \
	-cpu SandyBridge -smp 2 \
	-net nic,model=virtio -net user \
	-redir tcp:2222::22 \
	-kernel arch/x86/boot/bzImage -append root=/dev/sda4 \
	-pidfile /tmp/qemu.pid -daemonize \

ssh ${VM_SSH_HOSTNAME:?Please define} true
rsync -av ${SANDBOX_ROOT}/ ${homedir}/guest/ ${VM_SSH_HOSTNAME}:${DATA_ROOT}/
ssh ${VM_SSH_HOSTNAME} ${DATA_ROOT}/tests.sh
