# Using the OpenvCloud Client

## Get a JWT

You'll first need a JWT.

> See [Getting started with the OpenvCloud Cloud API](https://gig.gitbooks.io/ovcdoc_public/content/API/GettingStarted.html) for more details about this JWT.

Create an API key in your ItsYou.online profile, and copy the **Application ID** and **Secret** into environment variables: 
```bash
APP_ID="..."
SECRET2="..."
```

Optioanally, in order to make the environement variables available from the Python interactive shell:
```bash
export APP_ID
export SECRET2
```

Use curl to get a JWT
```bash
JWT2=$(curl -d 'grant_type=client_credentials&client_id='"$APP_ID"'&client_secret='"$SECRET2"'&response_type=id_token' https://itsyou.online/v1/oauth/access_token)
echo $JWT2
```

Again optionally, in order to make the JWT value available from the Python interactive shell:
```bash
export JWT2
```

An alternative way to get a JWT is using Python code:
```python
import os
import requests
params = {
  'grant_type': 'client_credentials',
  'client_id': os.environ['APP_ID'],
  'client_secret': os.environ['SECRET'],
  'response_type': 'id_token',
  'scope': 'offline_access'
}
url = 'https://itsyou.online/v1/oauth/access_token'
resp = requests.post(url, params=params)
resp.raise_for_status()
jwt = resp.content.decode('utf8')
```


## Connect

```python
url="be-gen-1.demo.greenitglobe.com"
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