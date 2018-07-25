# Ipmi client

The ipmi client allows for managing the hardware of a node that supports ipmi.

The provided methods of the Jumpscale implementation focus on the power management through ipmi.

## Prerequisites

The ipmi client is a wrapper of the ipmitool command line tool.

To install run the installation script of Jumpscale

```sh
./install.sh
```

Or install it directly from the package manager
```sh
apt install ipmitool
```


## Usage

Get instance of the client:
```py
# Ommit data and set interactive to True to use the config manager interactive prompt
data = {
  "bmc": "10.10.1.1",
  "user": "ADMIN",
  "password_": "admin",
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
