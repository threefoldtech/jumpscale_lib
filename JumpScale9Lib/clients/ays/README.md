# AYS Wrapper Client

This AYS client is an easier to use alternative to the auto-generated AYS client, as available from `j.clients.atyourservice.get()`.

The AYS "Wrapper" Client is available from `j.clients.atyourservice.get2()`.

For its implementation it uses the auto-generated AYS client, hence its name: it "wraps" the auto-generated AYS client.

## Usage

Connect to you AYS server:
```python
base_uri="http://172.25.0.238:5000"
jwt="..."
cl=j.clients.atyourservice.get2(base_uri, jwt)
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

Read blueprint from a file:
```python
file_name="vdc.bp"
blueprint_file = open(file_name,'r')
blueprint = blueprint_file.read()
```

Create a blueprint:
```python
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
producers=service.getProducers()
```

List the producers of role account:
```python
service.getProducers("account")
```

Show its parent:
```python
parent=service.getParent()
parent
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




