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

## Working with blueprints

Read a blueprint from a file:
```python
file_name="vdc.yaml"
blueprint_file = open(file_name,'r')
blueprint = blueprint_file.read()
```

Add a blueprint to the AYS repository:
```python
bp_name = "vdc.yaml"
bp = repo.blueprints.create(bp_name, blueprint)
```

Close the file:
```python
blueprint_file.close()
```

Or use an existing blueprint:
```python
bp = repo.blueprints.get(bp_name)
```

Execute the blueprint:
```python
bp.execute()
```

Check created AYS services:
```python
repo.services.list()
```

## Working with runs

Create a run:
```python
key = repo.runs.create()
```

List all runs:
```python
repo.runs.list()
```

Check run:
```python
run = repo.runs.get(key)
run.model
```

Get the last run:
```python
run = repo.runs.get()
```

List all steps of a run:
```python
run.steps.list()
```

Closer look to the second step of a run:
```python
step2=run.steps.get(2)
step2.model
```

List all jobs of a step:
```python
step2.jobs.list()
```

Closer look to a job:
```python
job = step2.jobs.get(<key>)
```

List all logs of a job:
```python
job.logs.list()
```

## Working with services

Closer look at the AYS service for the VDC:
```python
vdc = repo.services.get("vdc", "testvdc10")
```

Check the full model of the VDC service:
```python
vdc.model
```

List its producers:
```python
producers = vdc.producers.list()
```

List all producers:
```python
vdc.consumers.list()
```

List the producers of role account:
```python
vdc.producers.list("account")
```

Get a specific producer, here the g8client:
```python
cl2 = vdc.producers.get("g8client", "cl")
cl2.model
```

Show its parent:
```python
vdc = service.getParent()
parent
```

List its children:
```python
vdc.children.list()
```

List only the children of role node (VM):
```python
vdc.children.list(role="node")
```

List all consumers:
```python
vdc.consumers.list()
```

Get a specific consuming node (VM) and check the state (model):
```python
vm = vdc.consumers.get("node","yves_vm_1")
vm.model
```

## Working with actions

List the actions of a service:
```python
service.actions.list()
```

Only show the actions that have state="OK":
```python
service.actions.list("OK")
```

Get a closer look to an action:
```python
action=service.actions.get("install")
action.model
```

## Working with actors

List all actors:
```python
repo.actors.list()
```

Update all actors:
```python
repo.actors.update()
```

Update only the account actors: 
```python
repo.actors.update("account")
```

Or alternatively:
```python
actor=repo.actors.get("account")
actor.update()
```

Update the account actors and reschedule all actions which are in error state:
```python
repo.actors.update("account", True)
```