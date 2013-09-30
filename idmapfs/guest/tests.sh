#!/bin/bash -xe

self=$(readlink -q -s -f $0 || echo $0)
homedir=${self%/*}
set -a
. ${homedir}/tests.rc

${DATA_ROOT}/prep-tests.sh
${DATA_ROOT}/run-tests.sh

