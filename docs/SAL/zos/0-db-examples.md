# 0-db Examples


This page provides code examples how to use the zero-os node sal in combination with 0-db

To run 0-db one needs to supply a path on the filesystem where to store it files, typicly one will dedicate an entire disk for 0-db to optimized perfomance. 


## Summary
- [Prepare disks](#prepare-disks)
- [0-db create](#0-db-create)
- [Adding a namespace](#adding-a-namespace)
- [VDisk Create](#vdisk-create)

## Get zero-os node sal
```python
node = j.clients.zos.sal.get_node('myzos')
```

## Prepare disks

Create partitions and filesystem on top of all free disks of zero-os
```python
node.zerodbs.partition_and_mount_disks()               
Out[8]:                                                        
[{'disk': 'vda', 'mountpoint': '/mnt/zdbs/vda'},               
 {'disk': 'vdb', 'mountpoint': '/mnt/zdbs/vdb'},               
 {'disk': 'vdc', 'mountpoint': '/mnt/zdbs/vdc'},               
 {'disk': 'vdd', 'mountpoint': '/mnt/zdbs/vdd'},               
 {'disk': 'vde', 'mountpoint': '/mnt/zdbs/vde'}]               
```
As you can see this created 5 mountpoints for 5 disks.

## 0-db create
Lets create a 0-db on top of vda and deploy it.
This will create a container running the 0-db process storing it files under /mnt/zdbs/vda
```python
zdb = node.primitives.create_zerodb(name='myzdb', path='/mnt/zdbs/vda', mode='user', sync=False, admin='mypassword')
zdb.deploy()
```

## Adding a namespace
```python
zdb.namespaces.add(name='mynamespace', size=10, password='namespacepassword', public=True)
zdb.deploy()
```
Note: After adding or removing a namespace you need to deploy the zdb to update these changes in reality.

## VDisk Create
Using a 0-db to create a vdisk suitable to be used by a virtual-machine
Internally this will create a namespace suitable for use as vdisk, a filesystem will be added on top of the vdisk when attached to a virtal machine it will be mounted under the defined mountpoint.
```python
disk = node.primitives.create_disk('mydisk', zdb, mountpoint='/mnt', filesystem='ext4', size=10) 
disk.deploy()
```

```
!!!
date = "2018-05-20"
tags = []
title = "0 Db Examples"
```

