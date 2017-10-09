# How to get a JWT for authenticating against OpenvCloud

> See [Getting started with the OpenvCloud Cloud API](https://gig.gitbooks.io/ovcdoc_public/content/API/GettingStarted.html) for more details about this JWT.

Create an API key in your ItsYou.online profile, and copy the **Application ID** and **Secret** into environment variables: 
```bash
APP_ID="..."
SECRET2="..."
```

In order to make the environement variables available from the Python interactive shell, export them:
```bash
export APP_ID
export SECRET2
```

Use curl to get a JWT
```bash
JWT2=$(curl -d 'grant_type=client_credentials&client_id='"$APP_ID"'&client_secret='"$SECRET2"'&response_type=id_token' https://itsyou.online/v1/oauth/access_token)
echo $JWT2
```

In order to make the JWT value available from the Python interactive shell:
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
  'client_secret': os.environ['SECRET2'],
  'response_type': 'id_token',
  'scope': 'offline_access'
}
url = 'https://itsyou.online/v1/oauth/access_token'
resp = requests.post(url, params=params)
resp.raise_for_status()
jwt = resp.content.decode('utf8')
```