# How to use the JumpScale client for ItsYou.online

The ItsYou.online client is available as part of [jumpscale/lib9](https://github.com/Jumpscale/lib9).

To use the client you need to have a client instance. See [here](https://github.com/Jumpscale/core9/blob/master/docs/config/configmanager.md) for how to configure an instance. Client can then be used as follows:

```python
iyo_cl = j.clients.itsyouonline.get('myinstance')
```

The client instance is mainly used to retrieve a jwt. It also allows direct interaction with itsyouonline api.

Before using the client make sure that `python-jose` librabry is  installed, this can be done as follows"

```python
j.clients.itsyouonline.install()
```

## Getting a jwt

The client method `jwt_get` will fetch a jwt which can be used to authenticate against various services like Openvcloud and gittea for instance.

```python
def jwt_get(self, validity=None, refreshable=False, scope=None, use_cache=False):
        """
        Get a a JSON Web token for an ItsYou.online organization or user.

        Args:
            validity: time in seconds after which the JWT will become invalid; defaults to 3600
            refreshable (True/False): If true the JWT can be refreshed; defaults to False
            scope: defaults to None
            use_cache: if true will add the jwt to cache and retrieve required jwt if it exists
                    if refreshable is true will refresh the cached jwt
        """
```

Example usage:

```python
iyo_cl.jwt_get(refreshable=True, use_cache=True)
```

The above will return a jwt from the cache if it exists, if the jwt is expired it will refresh it and return it to the user. On the other hand if it doesn't exist in the cache it will get the jwt from ItsYou.online server and store it in the cache for future use.

In addition to returning a client instance the `j.clients.itsyounoline` is used to perform several other operations, discussed in the following section.

## Using the api

For an overview of all the api endpoints, check the raml [spec](https://raw.githubusercontent.com/itsyouonline/identityserver/master/specifications/api/itsyouonline.raml) or check the api [docs](https://itsyou.online/apidocumentation). You can check the url of the raml spec as following:

```python
j.clients.itsyouonline.raml_spec
```

Interaction with the api is done using the `api` property in the client.

Below we discuss:

- [Auto-generated client](#auto-generated)

<a id="auto-generated"></a>
## Working with the auto-generated client


### Example using the auto-generated client to get a user's telephone number

```python
iyo_cl = j.clients.itsyouonline.get()
users = iyo_cl.api.users
users.GetUserPhonenumberByLabel('Home', 'John').json()
Out[17]: {'label': 'Home', 'phonenumber': '+15551234'}
```

### Example using the auto-generated client to get an organization
```python
iyo_cl = j.clients.itsyouonline.get()
org = iyo_cl.api.organizations.GetOrganization("testorg")
org.json()
```

### Manually by setting OAuth token

```python
iyo_cl = j.clients.itsyouonline.get()
iyo_cl.api.session.headers.update({"Authorization": 'token {}'.format(<token>)})
```

### Manually setting JWT

```python
iyo_cl = j.clients.itsyouonline.get()
iyo_cl.api.session.headers.update({"Authorization": 'bearer {}'.format(<jwt>)})
```

### Get an updated version of the auto-generated client code

The auto-generated client can be copied from https://github.com/itsyouonline/identityserver/tree/master/clients/python/itsyouonline
```
!!!
date = "2018-05-20"
tags = []
title = "IYO Client"
```
