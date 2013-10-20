#!/bin/bash -xe

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
echo > set_ftrace_filter
echo ':mod:idmapfs' >>	set_ftrace_filter
echo ':mod:ext2' >>	set_ftrace_filter
#echo 'd_instantiate' >>	set_ftrace_filter
echo 1 > tracing_on
${@} || :
echo 0 > tracing_on
cp trace /tmp/ftrace.$$
