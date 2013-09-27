#!/bin/bash

for x in /mnt/wrapfs/{dir/,other}file-$$.txt; do
	echo "---- (sudo 1000) touch $x ---------"
	sudo -u alin touch $x
done
for x in /mnt/{,wrap,,wrap}fs ; do
	for y in {dir/,other}file-$$.txt; do
		stat -c $'%-25n %u %g %i %A' $x/$y
	done
	echo ----------------
done

