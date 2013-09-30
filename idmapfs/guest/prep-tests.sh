#!/bin/bash -xe

umount --detach-loop ${FS_MOUNT_PLAIN} ${FS_MOUNT_WRAP} || :
rmmod wrapfs || :
mkdir -pv ${FS_MOUNT_PLAIN} ${FS_MOUNT_WRAP}
modprobe -d ${DATA_ROOT} wrapfs
mount ${DATA_ROOT}/ext2fs.loop.orig ${FS_MOUNT_PLAIN} -o loop
mount -t wrapfs ${FS_MOUNT_PLAIN} ${FS_MOUNT_WRAP}
