# Ipmi client

The ipmi client allows for managing the hardware of a node that supports ipmi.

The provided methods of the Jumpscale implementation focus on the power management through ipmi.  
Other methods of the internal ipmi client ([pyghmi](https://github.com/openstack/pyghmi)) are exposed by the `ipmi` property of the client.

## Prerequisites

To keep the Jumpscale Lib9 installation smaller, the dependencies of the ipmi client are not installed.

To install the dependencies run the following command in the root directory of Lib9

```sh
pip3 install -r JumpScale9Lib/clients/ipmi/requirements.txt
```

## Usage

Get instance of the client:
```py
# Ommit data and set interactive to True to use the config manager interactive prompt
data = {
  "bmc": "10.10.1.1",
  "user": "ADMIN",
  "password": "admin",
  "port": 623,
}
ipmi_cl = j.clients.ipmi.get(instance="test1", data=data, interactive=False)
```

Get power status of the host:
```py
print(ipmi_cl.power_status())
# Out: on
```

Power off the host and check the status:
```py
ipmi_cl.power_off()
print(ipmi_cl.power_status())
# Out: off
```

Power the host back on and check the status:
```py
ipmi_cl.power_on()
print(ipmi_cl.power_status())
# Out: on
```
Power cycle the host and check the status:
```py
ipmi_cl.power_cycle()
print(ipmi_cl.power_status())
# Out: on
```

```
!!!
date = "2018-05-20"
tags = []
title = "Ipmi"
```
