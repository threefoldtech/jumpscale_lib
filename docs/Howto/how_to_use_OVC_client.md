# Using the OpenvCloud Client

## Get a JWT

You'll first need a JWT, see [How to get a JWT for authenticating against OpenvCloud](how_to_get_a_JWT_for_OVC.md) for instructions.


## Connect

In the interactive shell:
```python
url = "be-gen-1.demo.greenitglobe.com"
cl = j.clients.openvcloud.get(url=url, jwt=jwt)
```

You might need to install python-jose in order to have the above work:
```bash
pip3 install python-jose
``` 

## Playtime

Access an account:
```python
account_name="..."
acc = cl.account_get(account_name)
```

List all cloud spaces:
```python
acc.spaces
```

Access a cloud space:
```python
cloud_space_name = "..."
location = "..."
cs = acc.space_get(cloud_space_name, location)
```

List the machines in the cloud space:
```python
cs.machines
```

Get a machine:
```python
machine_name = "..."
vm = cs.machines.get(machine_name)
```

Check the VM model:
```python
vm.model
```

List the disks:
```python
vm.disks
```

List all images:
```python
cl.api.cloudapi.images.list()
```