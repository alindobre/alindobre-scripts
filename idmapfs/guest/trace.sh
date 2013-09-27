#!/bin/bash -xe

if [ "$1" != "-n" ]; then
	if grep -qE ' /mnt/.*fs ' /etc/mtab; then
		umount --detach-loop /mnt/{wrap,}fs
	fi
	rmmod wrapfs || :
	insmod /mnt/data/wrapfs.ko
	cp -va /mnt/data/btrfs.loop.orig /tmp/btrfs.loop
	mount /tmp/btrfs.loop /mnt/fs -o loop
	mount -t wrapfs /mnt/fs /mnt/wrapfs
else
	shift
fi

cd /sys/kernel/debug/tracing
echo nop > current_tracer
#echo function > current_tracer
echo function_graph > current_tracer
echo nofuncgraph-cpu > trace_options
echo nofuncgraph-duration > trace_options
echo nofuncgraph-overhead > trace_options
#echo 100000 > buffer_size_kb
echo $$ > set_ftrace_pid
#echo > set_ftrace_pid
echo > 			set_ftrace_filter
echo ':mod:wrapfs' >>	set_ftrace_filter
echo ':mod:btrfs' >>	set_ftrace_filter
#echo 'd_instantiate' >>	set_ftrace_filter
echo 1 > tracing_on
${@} || :
echo 0 > tracing_on
cp trace /tmp/ftrace.$$
