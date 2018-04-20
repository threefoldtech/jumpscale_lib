# Zero-os primitives SAL

```python
node = j.clients.zeroos.sal.node_get('myzos')

# Create a new gateway
# Name will be used for creating the effective zero-os container
gw = node.primitives.create_gateway(name="my-little-gw")

# Add a network with name 'public' using a vlan [vlan/vxlan/zerotier]
pubnet = gw.networks.add(name="public", type_="vlan")
pubnet.type = 'public'                  # one of [public/private], is used for firewall configuration
pubnet.vlan_id = 100                    # vlan to be used for the pubnet 
pubnet.ip.cidr = '185.69.166.2/24'      # ip/subnet to be used for the nic configuration 
                                        # of the gateway itself for pubnet
pubnet.ip.gateway = '185.69.166.254'    # gateway to be used for the nic configuration 
                                        # of the gateway itself for pubnet

# Add a network with name 'private' using a zerotier [vlan/vxlan/zerotier]
privnet = gw.networks.add(name="private", type="zerotier")
privnet.type = 'private' 
privnet.zerotier_network_id = 'jkhg53df3g'                 # If empty, zerotier network will be created 
                                                           # automatically using token
privnet.zerotier_client = j.clients.zerotier.get("geert")  # Needed to create network and / or authorize 
                                                           # gateway & vms into network
privnet.ip.cidr = '192.168.0.1/24'                         # ip/subnet to be used for the nic confguration
                                                           # of the gateway itself for privnet
privnet.hosts.nameservers = ['8.8.8.8.8']                  # nameservers that will be used by the hosts in privnet
                                                           # if not set, defaults to ['8.8.8.8']

# Deploy the gateway to the zero-os node
gw.deploy()

# Serialize the gateway configuration to json
gw_json_string = gw.to_json()    # only contains gateway information, no vm details apart from host info
                                 # (see further down)

# Instantiate gateway sal from json
gw = node.primitives.from_json(type="gateway", json=gw_json_string)

# Reference network with name public
pubnet = gw.networks['public']

# Loop through gateway networks
for net in gw.networks:
    print("Network %s uses subnet %s & netmask %s" % (net.name, net.ip.subnet, net.ip.netmask))
    print("Gateway ip in network %s is %s" % (net.name, net.ip.subnet))

# Delete the gateway on the zero-os node
node.primitives.drop_gateway(name="my-little-gw")

# Create a new ubuntu vm [ubuntu:16.04/ubuntu:18.04/zero-os:1.2.1]
ubuntu_vm = node.primitives.create_virtual_machine(name="my-little-ubuntu-vm", type_='ubuntu:16.04')
ubuntu_vm.memory = 1024   # 1024 MiB
ubuntu_vm.cpu_nr = 1      # 1 vcpu

# Add disk named mark of type db [db, archive, temp]
db_disk = ubuntu_vm.disks.add(name="mark", type=db)
db_disk.size = 50   # 50 GiB
db_disk.fs = 'ext4'              # optional. possible types: [ext4, btrfs, xfs]
db_disk.mounpoint = '/mnt/mark'  # optional. must be used in combination of fs property
                                 # if both are set the disk will be formatted and mountpoint will be added # in /etc/fstab. hot mounting is not supported while the vm is running, 
                                 # hot adding the disk to the running vm is supported
# ... need to add connection to 0-db here

# Add vm to a network
privnet = gw.networks['pivate']
host = privnet.hosts.add(host=ubuntu_vm, ipaddress='192.168.0.2')   # hot adding nics to a running vm 
                                                                    # is supported
host.cloudinit_config = '...'    # optional cloud init configuration
print(host.name)    # name of vm object
# privnet.hosts also supports indexing on host name (ubuntuvm.name), listing, and removing hosts

# Redeploy the gw to add the host for real
gw.deploy()

# Deploy the vm
ubuntu_vm.deploy()

# Start the vm
ubuntu_vm.start()

# Pause the vm
ubuntu_vm.pause()

# Stop the vm
ubuntu_vm.stop()

# Serialize vm to json
ubuntu_json_string = ubuntu_vm.to_json()

# Deserialize vm from json
ubuntu_vm = node.primitives.from_json(type="ubuntu_vm", json=gw_json_string)

# Create a new zero-os vm
zeroos_vm = node.primitives.create_virtual_machine(name="my-little-ubuntu-vm", type_='zero-os')
zeroos_vm.ipxe_url = 'https://bootstrap.gig.tech/ipxe/master/abcef01234567890/organization=myorg'
zeroos_vm.memory = 1024   # 1024 MiB
zeroos_vm.cpu_nr = 1      # 1 vcpu

# Add disk named mark of type db [db, archive, temp]
db_disk = zeroos_vm.disks.add(name="mark", type=db)
db_disk.size = 50   # 50 GiB
# ... need to add connection to 0-db here

# Add a portforward from the public network to the private network to host 
pubnet = gw.networks['public']
privnet = gw.networks['private']
pfwd = gw.portforwards.add(name='http')
pfwd.source.network = pubnet
pfwd.source.port = 80
pfwd.target.network = privnet
pfwd.target.ipaddress = '192.168.0.2'
pfwd.target.port = 8080
gw.deploy() # deploy to make changes have effect
# ... gw.portforwards also alows indexing on portforward name, listing and removing portforwards

# ... add similar functions for reverse proxy configuration
```