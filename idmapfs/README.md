Scripts and other data that helps automating the uid/gid map file system
(idmapfs).

The tests are done in a qemu machine, which has an primaary OS qcow2 disk, with
a standard Funtoo partitioning, with the first partition mounted under /boot. A
second raw disk is attached to the machine, containing a single ext2 partition
with all the testing data, which is being updated by the automation scripts.

Since there is a possibility where modifying the qemu disks from the host
system would lead to disk corruption, the qcow2 primary disk is never touched
by these scripts, nor mounted in any way.

