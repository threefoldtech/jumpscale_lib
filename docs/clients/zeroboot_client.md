# Zeroboot client

![diagram picture](https://docs.google.com/drawings/d/e/2PACX-1vS19x58a_V6ulx1PzdmyrAHqIxnOOrVzNIYji6_CklosivjrZVOkW2534LWgFmTDVAxpq6vmzPeN7Cy/pub?w=960&h=720)
[edit picture](https://docs.google.com/drawings/d/1t5qFq8DfJfLGW-IdeO2llEPwFQc-ckR3RUo2YjxFni4/edit)

## Prerequisites

The router needs first to be installed check the docs [here](https://github.com/Jumpscale/prefab9/blob/development/docs/prefab.zeroboot.md) for more information.

Zeroboot client requires instances of the following clients before it can be used:

- `j.clients.sshclient`: to connect to the router
- `j.clients.racktivity`: to connect to the racktivity device and perform required operations, if no power options are required not necessary
- `j.clients.zerotier`: to setup a route on the router to allow connection to the racktivity device. The client should have access to the same zerotier network id used to setup the router.

### Configuring the clients

JumpScale clients uses a [config manager](https://github.com/Jumpscale/core9/blob/master/docs/config/configmanager.md) to configure and manage client instances.

Getting a new instance of a client can be done in interactive way, where the user will be prompted to enter the client data in a window. By default most clients are interactive although there are some exceptions. For example to get an instance of the ssh client in interactive mode:

```python
sshclient = j.clients.ssh.get('instance_name', interactive=True)
```

Alternatively you can set the data directly:

```python
data = {
    'addr': '172.17.0.2',
    'login': 'root',
    'passwd_': 'QXF34fe'
}
sshclient = j.clients.ssh.get('instance_name', data=data)
```

It is possible to get the zeroboot instance wihtout first configuring the necessary clients and the user will be prompted to enter the required data.

#### SSH client

For a typical use case the following need to be configured:

- `addr`: address of the router in the zerotier network
- `port`: ssh port to connect to the router, by default 22
- `login`: username on the router
- `passwd_`: password of that username

```python
sshclient = j.clients.ssh.get('instance_name', interactive=True)
```

The above will prompt the user to enter the necessary data.

#### Racktivity client

Is not necessary in order to use the zeroboot client. Needed only for power operations. 

- `hostname`: address of the racktivity device in the internal router network
- `port`: connection port
- `username`: user login for the racktivity device
- `password_`: password for user login

```python
rack = j.clients.racktivity.get('instance_name')
```

The above will prompt the user to enter the necessary data.

#### Zerotier client

The client only needs a user token for authentication. The user needs to have access to the zerotier network.

- `token_`: zerotier user token

```python
ztier = j.clients.zerotier.get('instance_name')
```

The above will prompt the user to enter the necessary data.

## Usage

To get an instance of the client you need to specify the following:

- `sshclient_instance`: instance name of the required ssh client
- `zerotier_instance`: instance name of the required zerotier client
- `network_id`: zerotier network id to connect to the router

Client can then be used as follows:

```python
zboot = j.clients.zboot.get('myinstance')
```

The client is now loaded with network information which can be checked using the following interface:

```python
In [5]: zboot.networks
Out[5]: ['172.17.1.2/16']
```

The above will list all the availble networks object. In most cases only one network(lan network) will be configured on the router.

### Racktivity operations

First you need to get a racktivity client instance see above for how to get it:

```python
rack = j.clients.racktivity.get('instance_name')
```

Depending on the model you might need to specify the power module when specifying the port, since depending on the model it might have multiple power modules. For example `P1` refers to the first power module available.

For example if you have a racktivity device model PM0816-01, there is no need to specify the module id. On the other hand if you model ES1108-16 it is required to specify the module id to use the client.

#### Power info

To get the power info for the device:

```python
zboot.power_info_get(rack)
```

To check the status of all ports check the value in `StatePortCur`, where `True` means open:

```python
{'ActiveEnergy': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
 'ApparentEnergy': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
 'ApparentPower': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
 'Current': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
 'Frequency': 49.94,
 'GeneralModuleStatus': 0,
 'MaxCurrent': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
 'Power': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
 'PowerFactor': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
 'StatePortCur': [True, True, False, False, False, False, False, False],
 'Temperature': 20.0,
 'TotalActiveEnergy': 0.0,
 'TotalApparentEnergy': 0.0,
 'TotalApparentPower': 0.0,
 'TotalCurrent': 0.0,
 'TotalPowerFactor': 0.0,
 'TotalRealPower': 0.0,
 'Voltage': 239.38}
```

To check if port open or not:

```python
zboot.port_info(portnumber, rack)
```

For the same examples but with models that requires power module to be specified:

```python
zboot.power_info_get(rack, 'P1')
zboot.port_info(portnumber, rack, 'P1')
```

#### Power operations

To turn the power off for a port:

```python
zboot.port_power_off(portnumber, rack)
```

To turn on:

```python
zboot.port_power_on(portnumber, rack)
```

It is possible to power cycle ports, where a port will be shut down and then powered on again after 5 seconds. This is useful to make a host rejoin the network with the new network configuration.

```python
list_of_ports = [1,3,4]  # port numbers
zboot.port_power_cycle(list_of_ports, rack)
```

For the same examples but with models that requires power module to be specified:

```python
zboot.port_power_off(portnumber, rack, 'P1')
zboot.port_power_on(portnumber, rack, 'P1')
list_of_ports = [1,3,4]
zboot.port_power_cycle(list_of_ports, rack, 'P1')
```

### Network information

To get a network object:

```python
net = zboot.networks.get('{subnet}')
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