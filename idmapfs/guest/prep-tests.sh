#!/bin/bash -xe

#umount --detach-loop ${FS_MOUNT_PLAIN} ${FS_MOUNT_WRAP} || :
#rmmod idmapfs || :
mkdir -pv ${FS_MOUNT_PLAIN} ${FS_MOUNT_WRAP}
modprobe -d ${DATA_ROOT} ext2
modprobe -d ${DATA_ROOT} idmapfs
mount ${DATA_ROOT}/ext2fs.loop.orig ${FS_MOUNT_PLAIN} -o loop -t ext2
mount -t idmapfs ${FS_MOUNT_PLAIN} ${FS_MOUNT_WRAP}
