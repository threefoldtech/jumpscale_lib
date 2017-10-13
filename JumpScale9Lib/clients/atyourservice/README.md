# AYS Client

The AYS client makes interacting with the RESTful API of a local or remote AYS Server easy.

The AYS client is available from `j.clients.ays.get()`. Underneath it uses the auto-generated AYS client, which is available from the private attribute `_ayscl` of the AYS client. 


## Usage

Connect to your AYS server:
```python
base_uri="http://172.25.0.238:5000"
jwt="..."
cl=j.clients.ays.get(base_uri, jwt)
```

List all repositories:
```bash
cl.repositories.list()
```

Create a new repository:
```bash
repo_name = "testrepo"
git_url = "http://gitrepo"
repo=cl.repositories.create(repo_name, git_url)
```

Or use an existing repository:
```bash
repo=cl.repositories.get(repo_name)
```

Create a blueprint from a file:
```python
path="vdc.bp"
bp=repo.blueprints.createFromFile(path)
```

Alternativelly:
```python
file_name="vdc.bp"
blueprint_file = open(file_name,'r')
blueprint = blueprint_file.read()
bp_name="myvdc.yaml"
bp=repo.blueprints.create(bp_name, blueprint)
```

List the blueprints:
```python
repo.blueprints.list()
```

Or use an existing blueprint:
```bash
bp=repo.blueprints.get(bp_name)
```

Check the content of the blueprint:
```bash
bp.get()
```

Execute the blueprint:
```python
resp=bp.execute()
resp.content
```

Check created services:
```python
repo.services.list()
```

Create a run:
```pyton
key=repo.runs.create()
```

List all runs:
```python
repo.runs.list()
```

Check run:
```python
myrun=repo.runs.get(key)
myrun.model
```

Closer look to one of the services:
```python
service=repo.services.get("vdc", "testvdc10")
```

Check the full model of the service:
```python
service.model
```

Check for its producers:
```python
producers=service.producers.list()
```

List the producers of role account:
```python
service.producers.list("account")
```

Show its parent:
```python
parent=service.getParent()
parent
```

VDC exmaple:
```python
repo=cl.repositories.get("demo3")
vdc=repo.services.get("vdc", "ydc")

vdc.children.list()
vdc.children.list(role="node")

vdc.consumers.list()
vm=vdc.consumers.get("node","yves_vm_1")
vm.model

vdc.producers.list()
vdc.producers.list("vdcfarm")
cl2=vdc.producers.get("g8client", "cl")
cl2.model
```

List the actions:
````python
service.actions.list()
````

Only show the actions that have state="OK":
````python
service.actions.list("OK")
````

Get a closer look to an action:
```bash
action=service.actions.get("install")
action.model
```

Some more fun with runs:
```python
key=repo.runs.create()
runs=repo.runs.list()
run=repo.runs.get()

run.steps.list()
step2=run.steps.get(2)
step2.model

step2.jobs.list()
job=step2.jobs.get()
job.logs.list()
```

One more:
```
repo=cl.repositories.get('demo1')
repo.actorTemplates.list()
t1=repo.actorTemplates.get("vdc")


repo=cl.repositories.get('demo1')
repo.blueprints.list()
repo.blueprints.list(True)
repo.blueprints.execute()
repo.services.list()
repo.runs.create()
repo.runs.list()
run=repo.runs.get("d0067c57e6343108ad7923399bd01e6e")
run
```

Actors:
```python
repo=cl.repositories.get('demo1')
repo.actors.list()
repo.actors.update()
repo.actors.update("account")
repo.actors.update("account", True)
actor=repo.actors.get("account")
actor.update()
```


