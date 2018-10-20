# Virtual Machine Examples


This page provides code examples how to use the zero-os node sal in combination with virtual machines


## Summary
- [Create Virtual Machine Object](#create-vm-object)
- [Update properties](#update-properties)
- [Adding disks](#adding-disks)
- [Adding network](#adding-network)
- [Adding config](#adding-config)

## Get zero-os node sal
```python
node = j.clients.zos.sal.get_node('myzos')
```

## Create VM Object

Currently we provide template for two virtual machine types Ubuntu and Zero-OS
We can specify the version of the operating system
### Ubuntu versionining
- `latest`: always points to latest ubuntu release
- `lts`: points to latest LTS (Long term suopport) release
- `16.04`: points to a specific release
See [hub](https://hub.gig.tech/gig-bootable) for a list of available versions
### Zero-OS versioning
Points to branch/tag zero-os was build from see [bootstrap](https://bootstrap.gig.tech/images) for a list of images
```
vm = node.primitives.create_virtual_machine(name='myubuntu', type_='ubuntu:lts')
zosvm = node.primitives.create_virtual_machine(name='myubuntu', type_='zero-os:master')
```

## Update properties

### Flist

The flist propety is filled automaticly by the type supplied when creating the vm object however if you would want you can change it to any other flist please make sure it's of the [bootable](https://github.com/zero-os/0-core/blob/master/docs/vms/vmfromflist.md) kind.
```python
vm = node.primitives.create_virtual_machine('myvm', 'ubuntu:latest')
vm.flist
Out[40]: 'https://hub.gig.tech/gig-bootable/ubuntu:latest.flist'
vm.flist = 'http://192.168.59.1:8080/dev/bin/flists/deboeckj/ubuntu-xenial.flist'
```

### Memory

Memory is expressed in MiB the default value is 2048 MiB
```python
vm.memory
Out[41]: 2048
vm.memory = 4096
```

### VCPUS

Configure the amount of virtual cpus the default is 2

```python
vm.vcpus
Out[42]: 2
vm.vcpus = 4
```

## Adding disks

To create disk vdisk of 0-db object please check [here](0-db-examples.md#vdisk-create)

```python
vm.disks.add(disk)
```

Or manually
```python
node.client.kvm.create_image('/var/cache/mydisk.qcow2', '20G', 'qcow2')
vm.disks.add('mydisk', 'file:///var/cache/mydisk.qcow2')
```

## Adding network

### Zerotier
virtual-machine can also connect to a zerotier network this is usefull to use our public IPAddress for virtual machines hosted on nodes that are not publicly availably

This can be done in two diffrent ways

#### Passing zerotier info
```python
ztnetwork = vm.nics.add(name='zerotier', type_='zerotier', networkid='abcdef1234567890')
ztnetwork.client_name = 'myzerotier'
```
Note: the name passed to client_name needs to be available under `j.clients.zerotier.list()`

#### Passing zerotier client
We can pass the zerotier client or the ZerotierNetwork object from the ZerotierClient
When we passs the ZerotierClient and don't set the networkid a new zerotier network will be created for us during virtual machine deployment.
```python
zcl = j.clients.zerotier.get() 
ztnetwork = vm.nics.add_zerotier(zcl, 'my zerotiernetwork')
```

or

```python
zcl = j.clients.zerotier.get() 
ztn = zcl.network_get('abcdef1234567890')
ztnetwork = vm.nics.add_zerotier(ztn)
```

### Attaching gateway network

See gateway [examples](0-gateway-examples.md#adding-a-virtual-machine-host) on how to create a private network on gateway and attach a virtual machine to it.

## Adding config

Thanks to you flist based images it is possible to inject extra config 

Adding authorized key in our virtual machine
```python
key = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCXIQPB...'
vm.configs.add('sshkey', '/root/.ssh/authorized_keys', key)
```

```
!!!
date = "2018-05-20"
tags = []
title = "Virtual Machine Examples"
```

