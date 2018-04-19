# Zeroboot client

## Prerequisites

The router needs first to be installed check the docs [here](https://github.com/Jumpscale/prefab9/blob/development/docs/prefab.zeroboot.md) for more information.

## Usage

To use the client you need to configure an instance. See [here](https://github.com/Jumpscale/core9/blob/master/docs/config/configmanager.md) for how to configure an instance. Zeroboot client requires another jumpscale clients to be configured to perform remote operations on needed devices and to configure the network. The needed clients are:

- `j.clients.sshclient`: to connect to the router
- `j.clients.racktivity`: to connect to the racktivity device and perform required operations
- `j.clients.zerotier`: to setup a route on the router to allow connection to the racktivity device. The client should be configured using the same zeroteir network id used to setup the router.

Client can be used as follows:

```python
zboot = j.clients.zboot.get('myinstance')
```

The client is now loaded with network information which can be checked using the following interface:

```python
In [5]: zboot.networks
Out[5]: ['172.17.1.2/16']
```

The above will list all the availble networks object. In most cases only one network(lan network) will be configured on the router.

### Network information

To get a network object:

```python
net = zbbot.networks.get('{subnet}')
```

The object contains info about the network subnet and all the configured hosts on that network and configuring certain aspects of the network. Discussed below:

#### Adding a host

Adding a new host to the network will register the host to the network where it will be configured using a static lease. The following needs to be specified:

- MAC address: of the host to be added
- IP address: static ip to be assigned to the host
- hostname: hostname in the dhcp server

This is done as follows:

```python
host = net.hosts.add(mac_address, ip_address, hostname)
```

#### Available hosts

```python
net.hosts.list() # lists dhcp hostnames of the hosts
```

#### Removing a host

Remove a host from the network:

```python
net.hosts.remove(hostname)
```

#### Getting a host

Get host object:

```python
net.hosts.get(hostname)
```

#### Configuring leasetime

Default lease time for the network is 5 minutes, to configure the time:

```python
net.configure_lease_time(time) # m for minutes h for hours ex: 5m
```

### Host information

Host object contains the host information and allows the following operations:

#### Configuring pxe boot

To specfiy a custom boot link to a host:

```python
host.configure_ipxe_boot(boot_url)
```