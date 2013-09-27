#!/bin/bash

for x in /mnt/{,wrap,,wrap}fs ; do
	for y in {dir/,other}file.txt; do
		echo "---- (sudo 1000) cat $x/$y ---------"
		sudo -u alin cat $x/$y
	done
done
