# Zero-OS primitives

We have 3 primitives:
- [0-db](0-db-examples.md)
- [0-Gateway](0-gateway-examples.md)
- [Virtual Machine](virtual-machine-examples.md)

## 0-db

The 0-db or sometimes written zdb source code can be found at [github](https://github.com/rivine/0-db).
It can be used to create vdisks or as archive storage in combination with S3/minio.

[Examples](0-db-examples.md)

## 0-Gateway

0-Gateway is a container on top of Zero-OS providing a powerfull featureset.
Our 0-Gateway flist is based on caddy + dnsmasq + nft + ca-certificate + cloud-init-server.
Because our gateway is based on a Zero-OS container it supports zerotier, vxlan, vlan and natted networking out of the box.

Thanks to [Caddy's](https://caddyserver.com/) it's [Let's Encrypt](https://letsencrypt.org/) integration a gateway can autoamticly provide you with a https proxy.

[Examples](0-gateway-examples.md)

## Virtual Machine

Currently we support two virtual machine primitives being [Ubuntu](https://www.ubuntu.com/) and [Zero-OS](https://github.com/zero-os/home).

Our Ubuntu image comes preinstalled with SSH server and [zerotier](https://zerotier.com/) binaries, this allows you to easily access your virtual machines from anywhere.

[Examples](virtual-machine-examples.md)

```
!!!
date = "2018-05-20"
tags = []
title = "Primitives"
```
