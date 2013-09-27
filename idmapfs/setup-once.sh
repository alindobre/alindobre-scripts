#!/bin/bash -xe

if [ -f ~/.idmapfs-tests.rc ]; then
	exit 2
fi
cp ${1:?Please provide a parameter} ~/.idmapfs-tests.rc
. ~/.idmapfs-tests.rc
mkdir -pv ${KERNEL_ROOT} ${FS_MOUNT_PLAIN} ${FS_MOUNT_WRAP}
