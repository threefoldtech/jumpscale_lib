# How to use the JumpScale client for ItsYou.online

The ItsYou.online client is available as part of [jumpscale/lib9](https://github.com/Jumpscale/lib9).

> The AYS client is also available as an independent package:
```bash
BRANCH="..."
sudo -H pip3 install --upgrade git+https://github.com/jumpscale/lib9.git@${BRANCH}#subdirectory=JumpScale9Lib/clients/itsyouonline
```

Below we discuss:
- [Users](#users)
- [Organizations](#organizations)
- [Auto-generated client](#auto-generated)

<a id="users"></a>
## Users

```python
def get_user(self, application_id, secret, validity=None, refreshable=False, scope=None, base_url=DEFAULT_BASE_URL)
def get_jwt(self, client_id, secret, validity=None, refreshable=False, scope=None, base_url=DEFAULT_BASE_URL)
def get_user_with_jwt(self, jwt, base_url=DEFAULT_BASE_URL)
```

Some usage examples:
```python
import os
app_id = os.environ["APP_ID"]
secret = os.environ["SECRET"]
iyo_user = j.clients.itsyouonline.get_user(app_id, secret)
iyo_user.public_keys.list()
key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDJnQ3CrxRMkRWoTbz3Qeboh4CdDZiwcUS+QT07PJO2vHk05j6zqT7SiIbizI/6euiffia9nPnTOXjA5peRX+dlwdamO+veSmbNZGKCsTW4v279mnTT5fdlsVpoxeWucZjSKdsvfhiE8bvjG/q8MiDqx6a9woY/KvG3Sln8/556jKC/zhykCtZhnZEd2h0q41f8CeZRKLKO6Zp/Y+Mx99cfsFOr07doFNAH31gP1thT4zukvfSu5DQBB4ZlARnkD2BzwtLM5QAE2O4KwRQq/+lzBw711y1WuS0xkaLTUKZyDIq109CbbkndLLkAU8guuc6L7mjFmXB9/J006fYzKz9V yves@yves-macbook-pros-MacBook-Pro.local"
iyo_user.public_keys.add("test_label", key)
iyo_user.public_keys.list()
iyo_user.public_keys.delete("test_label")
iyo_user.public_keys.list()
iyo_user.public_keys.add("test_label2", key)
key = iyo_user.public_keys.get("test_label2")
key.model
key.delete()
iyo_user.public_keys.list()
iyo_user.public_keys.add("test_label3", key)
key = iyo_user.public_keys.get("test_label3")
key.update("test_label4")
iyo_user.organizations.list()
org = iyo_user.organizations.get("testorg")
org.model
```

<a id="organizations"></a>
## Organizations

```python
def get_organization(self, global_id, secret, validity=None, refreshable=False, scope=None, base_url=DEFAULT_BASE_URL)
def get_jwt(self, client_id, secret, validity=None, refreshable=False, scope=None, base_url=DEFAULT_BASE_URL)
def get_organization_with_jwt(self, jwt, base_url=DEFAULT_BASE_URL)
```

Some usage examples:
```python
org.api_keys.list()
key = org.api_keys.get("testing3")
key.model
```

<a id="auto-generated"></a>
## Working with the auto-generated client

```python
def get_client(self, client_id, secret, validity=None, refreshable=False, scope=None, base_url=DEFAULT_BASE_URL)
def get_jwt(self, client_id, secret, validity=None, refreshable=False, scope=None, base_url=DEFAULT_BASE_URL)
def get_client_with_jwt(self, jwt, base_url=DEFAULT_BASE_URL)
```

### Example using the auto-generated client to get a user's telephone number

```python
client.users.GetUserPhonenumberByLabel('Home', 'John').json()
Out[17]: {'label': 'Home', 'phonenumber': '+15551234'}
```

### Example using the auto-generated client to get an organization
```python
import os
app_id = os.environ["APP_ID"]
secret = os.environ["SECRET"]
base_url = "https://staging.itsyou.online"
client = j.clients.itsyouonline.get_client(client_id, secret, base_url=base_url)
org = client.organizations.GetOrganization("testorg")
org.json()
```

### Manually by setting OAuth token

```python
client.session.headers.update({"Authorization": 'token {}'.format(<token>)})       
```

### Manually setting JWT

```python
client.session.headers.update({"Authorization": 'bearer {}'.format(<jwt>)})
```

### Get an updated version of the auto-generated client code

The auto-generated client can be copied from from https://github.com/itsyouonline/identityserver/tree/master/clients/python/itsyouonline