# Zero-os primitives SAL

```python
node = j.clients.zeroos.sal.node_get('myzos')

# Create a new gateway
# Name will be used for creating the effective zero-os container
gw = node.primitives.create_gateway(name="my-little-gw")

# Add a network with name 'public' using a vlan [vlan/vxlan/zerotier]
pubnet = gw.networks.add(name="public", type_="vlan")
pubnet.vlantag = 100                    # vlan to be used for the pubnet 
pubnet.ip.cidr = '185.69.166.2/24'      # ip/subnet to be used for the nic configuration 
                                        # of the gateway itself for pubnet
pubnet.ip.gateway = '185.69.166.254'    # gateway to be used for the nic configuration 
                                        # of the gateway itself for pubnet

# Add a network with name 'private' using a zerotier [vlan/vxlan/zerotier]
ztclient = j.clients.zerotier.get()
ztnetwork = ztclient.network.get('abcdef12334')
privnet = gw.networks.add(name="private", type_="zerotier")
privnet.networkid = ztnetwork.id                  # If empty, zerotier network will be created 
                                                  # automatically using token
privnet.client = ztclient                         # Needed to create network and / or authorize 
                                                  # gateway & vms into network
privnet.ip.cidr = '192.168.0.1/24'                # ip/subnet to be used for the nic confguration
                                                  # of the gateway itself for privnet
privnet.hosts.nameservers = ['8.8.8.8']           # nameservers that will be used by the hosts in privnet
                                                  # if not set, defaults to ['8.8.8.8']

# Deploy the gateway to the zero-os node
gw.deploy()

# Serialize the gateway configuration to json
gw_json_string = gw.to_json()    # only contains gateway information, no vm details apart from host info
                                 # (see further down)

# Instantiate gateway sal from json
gw = node.primitives.from_json(type_="gateway", json=gw_json_string)

# Reference network with name public
pubnet = gw.networks['public']

# Loop through gateway networks
for net in gw.networks:
    print("Network %s uses subnet %s & netmask %s" % (net.name, net.ip.subnet, net.ip.netmask))
    print("Gateway ip in network %s is %s" % (net.name, net.ip.subnet))
    
# Remove a network from the gateway
gw.networks.remove("private") # remove network using its name 
gw.networks.remove(privnet) # remove network using its object

# Delete the gateway on the zero-os node
node.primitives.drop_gateway(name="my-little-gw")

# Create a new ubuntu vm [ubuntu:16.04/ubuntu:18.04/zero-os:1.2.1]
ubuntu_vm = node.primitives.create_virtual_machine(name="my-little-ubuntu-vm", type_='ubuntu:16.04')
ubuntu_vm.memory = 1024   # 1024 MiB
ubuntu_vm.cpu_nr = 1      # 1 vcpu

# Add zerotier network from zerotier
ubuntu_vm.nics.add_zerotier(ztnet)

# Add disk named mark of type db [db, archive, temp]
db_disk = ubuntu_vm.disks.add(name="mark", url='zdb://172.18.0.1:9900?size=10G&blocksize=4096&namespace=myubuntudisk')
db_disk.filesystem = 'ext4'              # optional. possible types: [ext4, btrfs, xfs]
db_disk.mountpoint = '/mnt/mark'  # optional. must be used in combination of fs property
                                 # if both are set the disk will be formatted and mountpoint will be added # in /etc/fstab. hot mounting is not supported while the vm is running, 
                                 # hot adding the disk to the running vm is supported
db_disk.url = zdb.namespaces["my-namespace"]     # See below how the zdb object gets created, convenience option
db_disk.url = zdb.namespaces["my-namespace"].url # Can also set url directly
print(db_disk.zdb_namespace)                     # ==> always return url, for loosely coupling different sals

# Add vm to a network
privnet = gw.networks['private']
host = privnet.hosts.add(host=ubuntu_vm, ipaddress='192.168.0.2')   # hot adding nics to a running vm 
                                                                    # is supported

host = privnet.hosts.add(name='myhostname', macaddress='54:42:01:02:03:04', ipaddress='192.168.0.2')   # add mac manually
host = privnet.hosts.add(name='my2ndhost', macaddress=privnet.get_free_mac(), ipaddress='192.168.0.2')   # generate mac for network
host.cloudinit.users.add(user='myuser', password='mypassword', sudo=False) # optional cloud init configuration
host.cloudinit.metadata['local-hostname'] = 'myhostname'

# cloudinit have userdata and metadata dict for custom cloud-init data
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
ubuntu_vm = node.primitives.from_json(type="vm", json=ubuntu_json_string)

# Deleting the vm 
node.primitives.drop_vm("my-little-ubuntu-vm")

# Create a new zero-os vm
zeroos_vm = node.primitives.create_virtual_machine(name="my-little-ubuntu-vm", type_='zero-os')
zeroos_vm.ipxe_url = 'https://bootstrap.gig.tech/ipxe/master/abcef01234567890/organization=myorg'
zeroos_vm.memory = 1024   # 1024 MiB
zeroos_vm.cpu_nr = 1      # 1 vcpu

# Add disk named mark of type db [db, archive, temp]
db_disk = zeroos_vm.disks.add(name="mark", url='zdb://172.18.0.1:9900?size=10G&blocksize=4096&namespace=mydisk')

# Add a portforward from the public network to the private network to host 
pubnet = gw.networks['public']
privnet = gw.networks['private']
pfwd = gw.portforwards.add(name='http')
pfwd.source.ipaddress = '173.17.22.22'
pfwd.source.port = 80
pfwd.target.ipaddress = '192.168.0.2'
pfwd.target.port = 8080
gw.portforwards.add(name='https', ('173.17.22.22': 443), ('192.168.0.3', 443))
gw.deploy() # deploy to make changes have effect
# ... gw.portforwards also alows indexing on portforward name, listing and removing portforwards

# ... add similar functions for reverse proxy configuration

# Create a new zdb
# Name will be used for creating the effective zero-os container
zdb = node.primitives.create_zdb(name="my-zdb", path='/mnt/zerodbs/vda')

# create namespace
namespace = zdb.namespaces.add('my-namespace')
namespace.size = 20 # set namespace size
namespace.password = 'secret' # set namespace password

# deploy the new namespace to the zdb
zdb.deploy()

# get namespace information
info = namespace.info()

# get namespace url for kvm
url = namespace.url

# loop through the namespaces
for namespace in zdb.namespaces:
    print(namespace.size)

# get a namespace by name
namespace = zdb.namespaces["my-namespace"]
print(namespace.size)

# delete namespace
zdb.namespaces.remove("my-namespace")  # Delete a namespace using its name
zdb.namespaces.remove(namespace)       # Delete a namespace using object reference

# Deleting a complete zbd
node.primitives.drop_zdb("my-zdb")

# Alternative way of adding a disk
zdisk = node.primitives.create_disk('mydisk', zdb, '/mountpointinsidevm', 'ext4', 20)
zddisk.deploy() # will create namespace on zdb and deploy it
ubuntu_vm.disks.add(zdisk)
ubuntu_vm.deploy()

```
