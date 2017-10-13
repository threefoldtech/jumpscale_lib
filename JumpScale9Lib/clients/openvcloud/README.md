# OpenvCloud

How to create a machine.
To create a machine we need to get the correct size and image to create a machine.

```python
client = j.clients.openvcloud.get('www.mothership1.com', 'demo', 'demo')
account = client.account_get('demo')
locations = client.locations
location = locations[0]['locationCode']

space = account.space_get('demospace', location=location)

# lets deploy in our first cloud space
machine = space.machine_create(name='My VM',
                                image='Ubuntu 15.10 x64',
                                memsize=512)

executor = machine.get_ssh_connection()

```

## other example

```python
from js9 import j

#get config from local config file
config = j.data.serializer.yaml.load("config.yaml")
applicationId = config["iyo"]["appid"]
secret = config["iyo"]["secret"]
url = config["openvcloud"]["url"]
sshkeyname = j.application.config["ssh"]["sshkeyname"]

jwt = j.clients.openvcloud.getJWTTokenFromItsYouOnline(applicationId, secret)

c = j.clients.openvcloud.get(applicationId, secret, url)

account = c.account_get("despiegk")

print(account.spaces)

space = account.spaces[0]

print("images")
print([item["name"] for item in space.images])

machine = space.machine_create_ifnotexist("kds_test", sshkeyname=sshkeyname)
# default arguments are ubuntu1604 and 2GB mem & 10 GB disk

p = machine.prefab
```