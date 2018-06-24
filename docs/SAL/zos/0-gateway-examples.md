# 0-Gateway Examples

This page provides code examples how to use the zero-os node sal in combination with 0-gateway

On this page we will explain three common usecase for gateway.

In these usecases the public network is attached in attached in three diffrent ways:
1. Public IPAddress is the main IPAddress of the node
2. Public IPAddress is on a secondary interfaces
3. Public IPAddress is available via a vlan tag

## Summary
- [Create gateway object](#create-gateway-object)
- [Attaching a public network](#public-network)
- [Attaching a zerotier network](#zerotier-network)
- [Attaching a private network](#private-network)
- [Adding a host to the private network](#adding-a-host-to-the-private-network)
- [Adding a portforward](#adding-a-portforward)
- [Adding a http proxy](#adding-a-http-proxy)
- [Deployment](#deployment)
- [Destroy](#destroy-gateway)
- [Serialization](#serialization)

## Get zero-os node sal
```python
node = j.clients.zos.sal.get_node('myzos')
```

## Create gateway object
```python
gw = node.primitives.create_gateway(name="mygw")
```

## Public Network

Gateway considers any network that configures `network.ip.gateway` a public network unless `network.public` is explictly set to `false`.
It is also possible to force a network to be considered public by putting the `network.public` flag to `True`

### Public network usecase 1

In this usecase our zero-os is attached directly to the public network.
Because this IPAddress is already in use by zero-os itself, we can not use it directly in the gateway but instead we use the internal natting feature of zero-os and forward all ports needed by the gateway from the zero-os.

This approach makes it impossible to create more then one gateway using this technique.
For this technique it is required to set the `network.public` flag to `True`

```python
public = gw.networks.add(name='public', type_='default')
public.public = True
```
 
### Public network usecase 2

In this usecase our zero-os has a second interface directly connected to the network with a public interface.

#### Option 1: Create bridge on top of public interface

We first need to prepare a bridge to hang our second interface on.
```python
# create bridge
node.client.bridge.create('publicbridge')
#attach eth1 to bridge
node.client.bridge.nic_add('publicbridge', 'eth1')
```

After this we can attached our public network to the bridge
```python
public = gw.networks.add(name='public', type_='bridge', networkid='publicbridge')
```


#### Option 2: Passthrough the interface to the gateway

We only have one public IP Address we can use on the public interface so instead of creating a bridge on it and attaching to it we can directly connect this interface to the gateway using the the type `passthrough`.
```python
public = gw.networks.add(name='public', type_='passthrough', networkid='eth1')
```

#### IP Address configuration

For this kind of interface we need to configure a static IPAddress and gateway
```python
public.ip.cidr = '196.255.222.21/24'
public.ip.gateway = '196.255.222.1'
```

### Public network usecase 3
 
In this usecase our zero-os has a second interface which is connect to a backplane which has one or more vlans attached to the public network, this is a typical usecase inside a production like environment

First we need to prepare the backplane capable of creating vlan and vxlan networks
We need to pass the `CIDR` used for the backplane to communicate with other nodes. We also need to pass the vlantag which will be used to send our vxlan traffic over.
```python
node.network.configure(cidr='10.255.0.1/24', vlan_tag=2312, ovs_container_name='ovs')
```

Next we create our public network and assign the IPAddresss, in this example vlan 101 will be used and assumed to carry the publicnetwork 196.255.222.0/24.

```python
public = gw.networks.add(name='public', type_='vlan', networkid=101)
public.ip.cidr = '196.255.222.21/24'
public.ip.gateway = '196.255.222.1'
```

## Zerotier Network

0-gateway can also connect to a zerotier network this is usefull to use our public IPAddress for virtual machines hosted on nodes that are not publicly availably

This can be done in two diffrent ways

### Passing zerotier info
```python
ztnetwork = gw.networks.add(name='zerotier', type_='zerotier', networkid='abcdef1234567890')
ztnetwork.client_name = 'myzerotier'
```
Note: the name passed to client_name needs to be available under `j.clients.zerotier.list()`

### Passing zerotier client
We can pass the zerotier client or the ZerotierNetwork object from the ZerotierClient
When we passs the ZerotierClient and don't set the networkid a new zerotier network will be created for us during gateway deployment.
```python
zcl = j.clients.zerotier.get() 
ztnetwork = gw.networks.add_zerotier(zcl, 'my zerotiernetwork')
```

or

```python
zcl = j.clients.zerotier.get() 
ztn = zcl.network_get('abcdef1234567890')
ztnetwork = gw.networks.add_zerotier(ztn)
```

## Private network
There are two main usecases for a private network:
1. node local
2. grid local (typical production/datacenter infrastructure)

### Usecase 1
We will create a local bridge on the zero-os node and attach our gateway to it
```python
node.client.bridge.create('privatebridge')
private = gw.network.add('private', 'bridge', 'privatebridge')
private.ip.cidr = '192.168.103.1/24'
```

### Usecase 2
Here we will leverage backend network we crated in [Public Network Usecase 3](#public-network-usecase-3)

```python
private = gw.network.add('private', 'vxlan', 100)
private.ip.cidr = '192.168.103.1/24'
```

## Adding a host to the private network
We can configure the dhcp server of the gateway to provide IPAddresses to hosts connected to the same private network this can be accomplished in two ways.

We can pass all information required to add a host to the dhcp hostname, IPAddress and MACAddress if IPAddress or MACAddress is ommited the first available one in the private network will be assigned.

### Manually Adding a Host
```python
host = private.hosts.add('hostnameofmachine')
host.ipaddress
Out[35]: '192.168.103.10'      
host.macaddress       
Out[36]: '52:54:00:00:00:00'   
```

### Adding a virtual machine host
We can also pass the vm object see [Virtual Machine Examples](virtual-machine-examples.md)
This will automatically add the private network on the vm and configure the host in the dhcp server.

```python
private.hosts.add(vm)
```
Note: This will require you to call `gw.deploy()` AND `vm.deploy()`
                               
## Adding a portforward

0-gateway supports forwarding ports from public to private/zerotier networks

```python
gw.portforwards('forwardname', ('public', 34022), ('192.168.103.10', 22), ['tcp'])
```

This will add a forward from the public IPAddress defined in the network with the name public to the private ip `192.168.103.10`

## Adding a http proxy

Adding a http proxy makes it possible to share one public IPAddress for multiple destination hosts 

```python
gw.httpproxies.add('webserver', 'webserver.example.com', ['http://192.168.103.10:8080'], ['https', 'http'])
gw.httpproxies.add('dashboard', 'dashbaord.example.com', ['http://192.168.103.11:8080'], ['https', 'http'])
```

This will automaticly setup the required https certificates to have a secure webserver. The destination can be either a private or zerotier network IPAddress.

## Deploy gateway
When all data is added to the gateway we can deploy it.

```python
gw.deploy()
```

## Destroy gateway
```python
gw.stop()
```
or by name
```python
node.primitives.drop_gateway('mygw')
```

## Serialization
The gateway object has a builtin way to serialize its data to json or a python dict so that it can be reconstructed at any point in time.

### Save gateway config in mygw.json
```python
j.data.serializer.json.dump('mygw.json', gw.to_dict())
```
### Load gateway config from mygw.json
1111112
```python
gw = node.primitives.create_gateway(name="mygw")
gw.from_dict(j.data.serializer.json.load('mygw.json'))
1111113
```

```
!!!
date = "2018-05-20"
tags = []
title = "0 Gateway Examples"
```
