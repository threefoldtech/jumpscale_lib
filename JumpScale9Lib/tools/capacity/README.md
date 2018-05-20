# Zero-OS capacity registration tool

This tool is intended to be use to register zero-os node capacity onto a centralized capacity databases.
This is an temporary solution that will be replace with blockchain once we have it ready to support capacity registration.

## Specifications
Current database used to store the capacity will be a cluster of mongodb. This should give us enough resilience and availability to survive until we can use the blockchain.

### Types:
The interface of the tool expose 2 Types:

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
```python
# get the registration SAL 
register = j.tools.capacity.registration

# create a new farmer and register it to the database
farmer = register.farmers.create('name', 'iyo', ['addr1','addr2'])
register.farmer.register(farmer)

# get capacity report from the zero-os node
# you will never have to do this manually, the node robot will do this for you
node = j.clients.zero_os.sal.node_get('mynode')
capacity = node.capacity.get()
capacity.farmer = farmer.id
# register the capacity to the database
register.nodes.register(capacity)

# search for some node that provide capacity with a minimum of 2 CRU and 10 HRU and located in belgium
robot_urls = []
for capacity in register.nodes.search(CRU=2, HRU=10, country='belgium'):
    robot_url.append(capacity.robot_address)
```