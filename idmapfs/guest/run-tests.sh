#!/bin/bash -x

find ${DATA_ROOT}/tests -type f -name '*-*.sh' | sort -n | while read t; do
	${t}
done