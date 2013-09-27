#!/bin/bash


for x in /mnt/{,wrap,,wrap}fs ; do
	for y in dir{,/file.txt} otherfile.txt; do
		stat -c $'%-25n %u %g %i %A' $x/$y
	done
	echo ----------------
done

