#!/bin/bash

for x in /mnt/{,wrap,,wrap}fs ; do
	for y in {dir/,other}file.txt; do
		echo "---- (sudo 1001) cat $x/$y ---------"
		#logger -- "---- (sudo 1001) cat $x/$y ---------"
		sudo -u alin1001 cat $x/$y
	done
done
