Script that wraps over the normal ssh client, and uses a temporary file to
store host keys when connecting to plain IP addresses. I use this in testing,
because many IP addresses are being relocated to other VMs or the same VM
comes out with a different IP address at restart.
