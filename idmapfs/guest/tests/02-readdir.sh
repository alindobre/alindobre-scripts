#!/bin/bash

for x in ${FS_MOUNT_PLAIN} ${FS_MOUNT_WRAP} ${FS_MOUNT_PLAIN} ${FS_MOUNT_WRAP} ; do
	find $x -mindepth 1 -exec stat -c $'%-25n %u %g %i' {} \;
	echo ----------------
done
