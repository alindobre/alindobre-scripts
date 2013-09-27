#!/bin/bash

for x in /mnt/{,wrap,,wrap}fs ; do
	find $x -mindepth 1 -exec stat -c $'%-25n %u %g %i' {} \;
	echo ----------------
done
