#!/bin/bash

for x in ${FS_MOUNT_PLAIN} ${FS_MOUNT_WRAP} ${FS_MOUNT_PLAIN} ${FS_MOUNT_WRAP} ; do
	for y in dir{,/file.txt} otherfile.txt; do
		stat -c $'%-25n %u %g %i %A' $x/$y
	done
	echo ----------------
done
