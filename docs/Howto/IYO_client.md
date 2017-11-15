# How to use the JumpScale client for ItsYou.online


The ItsYou.online client is available as part of [jumpscale/lib9](https://github.com/Jumpscale/lib9).

> The AYS client is also available as an independent package:
```bash
BRANCH="9.3.0"
sudo -H pip3 install --upgrade git+https://github.com/jumpscale/lib9.git@${BRANCH}#subdirectory=JumpScale9Lib/clients/itsyouonline
```

Below we discuss:
- [Connecting to the AYS server using an AYS Client object](#client)
- [Using the Auto-generated Client](#auto-generated)
- [Listing and adding AYS Templates](#ays-templates)



def get_user(self, application_id, secret, url=DEFAULT_URL)

def get_organization(self, global_id, secret, url=DEFAULT_URL)

def get_jwt(self, id, secret, validity=3600, refreshable=False, scope=None)

def get_user_with_jwt(self, jwt)

def get_organization_with_jwt(self, jwt)

def get_client(self, id, secret)

def get_client_with_jwt(self, jwt)

Get client...

Simply get the api client by calling
```
client = j.clients.itsyouonline.get()
```

## Authentication

### Via Client Credentials

You can use your user API key which you can get from https://itsyou.online/#home/
under the settings tab.

```python
applicationid = 'YYYYYY'
apikey = 'XXXXXXXXX'
client.oauth.LoginViaClientCredentials(client_id=applicationid, client_secret=apikey)
```

### Manually by setting oauth token

```python
client.api.session.headers['Authorization'] = 'token <oauth token>'
```

### Manually by setting jwt key

```python
client.api.session.headers['Authorization'] = 'bearer <jwt key>'
```


## Example methods

After authenticating

```python
client.api.GetUserPhonenumberByLabel('Home', 'John').json()
Out[17]: {'label': 'Home', 'phonenumber': '+15551234'}

...
```


## to get updated version of the client

- copy from https://github.com/itsyouonline/identityserver/tree/master/clients/python/itsyouonline