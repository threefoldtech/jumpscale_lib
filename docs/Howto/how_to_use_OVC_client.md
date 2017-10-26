# Using the OpenvCloud Client

In order to use the OpenvCloud client you need a JSON Web token (JWT).

It is recommended to let the OpenvCloud generate this JWT for you, by just passing your application ID and secret when creating the OpenvCloud client.

In the below example we first read the application ID and secret from a YAML formated configuration file:
```python
config = j.data.serializer.yaml.load("config.yaml")
applicationId = config["iyo"]["appid"]
secret = config["iyo"]["secret"]
url = config["openvcloud"]["url"]
```

This requires a `config.yaml` structured as follows:
```yaml
iyo:
  appid: FjMckSiqtJK8XABCRNeakTowfxVp
  secret: gXpM4fPfHiXTb3blaJwmAV0Y72kB

openvcloud:
  url: 'https://se-gen-1.demo.greenitglobe.com'
```

With this connecting is simple:
```python
cl = j.clients.openvcloud.get(applicationId, secret, url)
```

> Also see [How to get a JWT for authenticating against OpenvCloud](how_to_get_a_JWT_for_OVC.md).

Below we discuss:
- [Accounts](#accounts)
- [Cloud Spaces](#cloud-spaces)
- [Virtual Machines](#virtual-machines)
- [Cloud API](#cloud-api)

<a id="accounts"></a>
## Accounts

Access an account:
```python
account_name="..."
acc = cl.account_get(account_name)
```

<a id="cloud-spaces"></a>
## Cloud Spaces

List all cloud spaces:
```python
acc.spaces
```

Get the first cloud space:
```python
vdc = acc.spaces[0]
```

Or get a cloud space by name:
```python
cloud_space_name = "..."
location = "..."
cs = acc.space_get(cloud_space_name, location)
```

The above code will create a new cloud space in the specified location if the cloud space doesn't exist yet. In case you don't want this behaviour, set the `create` argument to `False` (the default is `True`):
```python
cs = acc.space_get(cloud_space_name, location, create=False)
```

<a id="virtual-machines"></a>
## Virtual Machines

List the machines in the cloud space:
```python
cs.machines
```

Get a machine:
```python
machine_name = "..."
vm = cs.machines.get(machine_name)
```

Create a new virtual machines:
```python
sshkeyname = "<name of the SSH private keyname loaded bu the SSH agent>"
machine = space.machine_create_ifnotexist(name, sshkeyname = sshkeyname)
```

This will create new virtual machine using default values, typically Ubuntu 16.04 with @GB memory and a 10 GB boot disk.

Check the VM model:
```python
machine.model
```

List the disks:
```python
machine.disks
```

<a id="cloud-api"></a>
## Accessing the Cloud API

The OpenvCloud client uses the OpenvCloud Cloud API. You can access it via the OpenvCloud client via the `api` attribute.

List all images:
```python
cl.api.cloudapi.images.list()
```