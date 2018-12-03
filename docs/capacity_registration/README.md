# Zero-OS capacity registration tools

This set of tools is intended to be use to register zero-os node capacity onto a centralized capacity databases.
This is an temporary solution that will be replace with blockchain once we have it ready to support capacity registration.

## Specifications
Current database used to store the capacity will be a cluster of mongodb. This should give us enough resilience and availability to survive until we can use the blockchain.
This database will be expose using a small REST API server that also host a small UI so people can check the current registered capacity

### Architecture
So there are 3 major component in this architecture:
- mongo cluster
- REST API server (https://github.com/Jumpscale/lib/tree/development/JumpscaleLib/servers/grid_capacity)
 - talk to the mongo database using a SAL
- REST API client (https://github.com/Jumpscale/lib/tree/development/JumpscaleLib/clients/grid_capacity)

### Types:
They are 2 types register in the database:

- Node capacity
```yaml
node_id: unique node id
farmer: farmer id that owns the node
os_version: branch and revision of 0-OS
location: geolocation of the node
    city: 
    continent:
    country: 
    latitude: 
    longitude:
robot_address: URL to the node 0-robot of the node
cru: amount of CRU
hru: amount of HRU
mru: amount of MRU
sru: amount of SRU

```
- Farmer
```yaml
id: unique id of the farmer
iyo_account: ItsYouOnline account of the farmer
name: name of the farmer
wallet_addresses: list of tf wallet addresses
```


### Methods:
See https://github.com/Jumpscale/lib/blob/development/JumpscaleLib/servers/grid_capacity/server/models.py

For node capacity:
- def register(capacity): register node capacity
- def list(country=None): list all node capacity optionally filter per country
- def get(node_id): get specific node capacity detail
- def search(country=None, mru=None, cru=None, hru=None, sru=None): search based on country and minimum resource unit available

For Farmers:
- def register(farmer): register a farmer
- def list(): list all farmers
- def get(id): get a specific farmer detail

## Usage example:
See how the client is used in the node template: https://github.com/Jumpscale/lib/blob/development/JumpscaleLib/clients/zero_os/sal/Capacity.py#L73