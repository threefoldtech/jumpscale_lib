# How to get a JWT for authenticating against OpenvCloud

In order to authenticate against OpenvCloud you need a JSON Web token (JWT).

When interacting with OpenvCloud through the OpenvCloud client, this JWT gets created for you when instantiating an OpenvCloud client object, as documented in [Using the OpenvCloud Client](OVC_client.md). So in that case there is no need to create the JWT yourself.

In other cases, for instance for creating OpenvCloud blueprints that you want to send to an AYS server, or when directly interacting with the OpenvCloud Cloud API as documented in [How to use the OpenvCloud Cloud API](OVC_API.md), you will need to create the JWT yourself.

To create a JWT you always need an application ID and secret. You get this application ID and secret by creating an API key on the settings page of your [ItsYou.online](https://itsyou.online) user profile:

![](images/iyo_jwt.png)

Once you have an application ID and secret, you can use the OpenvCloud client to create the JWT:

```python
jwt = j.clients.openvcloud.getJWTTokenFromItsYouOnline(applicationId, secret, validity=3600)
```

Alternatively you can also create a JWT by interacting directly with the ItsYou.online RESTful API using:

- [cURL](#curl)
- [Python](#python)

<a id="curl"></a>
## Using cURL to get the JWT directly from the ItsYou.online RESTful API

```bash
export APP_ID="..."
export SECRET="..."
export JWT=$(curl -d 'grant_type=client_credentials&client_id='"$APP_ID"'&client_secret='"$SECRET"'&response_type=id_token' https://itsyou.online/v1/oauth/access_token)
echo $JWT2
```

<a id="python"></a>
## Using Python to get the JWT directly from the ItsYou.online RESTful API

For the below code example we also first export the application ID and secret in environment variables:
```bash
export APP_ID="..."
export SECRET="..."
``` 

Then from Python:
```python
import os
import requests
params = {
  'grant_type': 'client_credentials',
  'client_id': os.environ['CLIENT_ID'],
  'client_secret': os.environ['SECRET'],
  'response_type': 'id_token',
  'scope': 'offline_access'
}
url = 'https://itsyou.online/v1/oauth/access_token'
resp = requests.post(url, params=params)
resp.raise_for_status()
jwt = resp.content.decode('utf8')
```