#!/bin/bash -xe

. ~/.idmapfs-tests.rc
cd ${KERNEL_SOURCE:?Please define}
make modules
make INSTALL_MOD_PATH=${KERNEL_ROOT:?Please define} modules_install
