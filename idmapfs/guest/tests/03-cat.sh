#!/bin/bash

for x in ${FS_MOUNT_PLAIN} ${FS_MOUNT_WRAP} ${FS_MOUNT_PLAIN} ${FS_MOUNT_WRAP}; do
	for y in {dir/,other}file.txt; do
		echo "---- (sudo 1000) cat $x/$y ---------"
		sudo -u alin cat $x/$y
	done
done
