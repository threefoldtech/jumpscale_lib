# How to use the AYS client

The AYS client is available as part of [jumpscale/lib9](https://github.com/Jumpscale/lib9).

> The AYS client is also available as a independent installation:
```bash
BRANCH="9.3.0"
sudo -H pip3 install --upgrade git+https://github.com/jumpscale/lib9.git@${BRANCH}#subdirectory=JumpScale9Lib/clients/atyourservice
```

## Connecting to the AYS server using an AYS Client object

Your first step will be to get an AYS Client instance, through which you will do all AYS interactions.

In a typical setup the AYS server will be protected by ItsYou.online, requiring a JSON Web token (JWT) in order to use the AYS RESTful API. This JSON is created by the AYS client, you simply need to pass the client ID and secret that protects the AYS server. In the below example we assume you first saved the client ID and secret into environment variables:
```python
import os
client_id = os.environ["CLIENT_ID"]
secret = os.environ["SECRET"]
url = "http://192.168.196.5:5000"
cl = j.clients.ays.getWithClientID(clientID=client_id, secret=secret, url=url)
```

Or in case you saved the client ID and password in a YAML formated configuration file:
```python
from js9 import j
config = j.data.serializer.yaml.load("config.yaml")
client_id = config["iyo"]["client_id"]
secret = config["iyo"]["secret"]
url = config["openvcloud"]["url"]
```

The above uses a `config.yaml` 
 ```yaml
 iyo:
  client_id: FjMckSiqtJK8XXNARNeakFrsfxVp
  secret: gXpM4fPfHiXT3UblaJwmAhjd72kB`
```

Alternatively you can create the JWT yourself as documented in the [How to get a JWT for authenticating against AYS](how_to_get_a_JWT_for_AYS.md) and then use the following code to pass the JWT:
```python
url = "http://192.168.196.5:5000"
jwt = "<copy the JWT value here>"
cl = j.clients.ays.get(url=url, jwt=jwt)
```

## Working with repositories

Create an AYS repository:
```python
repo_name = "<here the name of the repository>"
git_url = "<SSH address of the repository on a Git server>"
repo = cl.repositories.create(repo_name, git_url)
```

List all AYS repositories:
```python
cl.repositories.list()
```

Get a repository by name:
```python
repo_name = "<here the name of the repository>"
repo = cl.repositories.get("repo_name")
```