# How to get a JWT for authenticating against OpenvCloud

## First create your application ID and secret on ItsYou.online

Prerequirements:
- Registrated user on ItsYou.online

![](images/iyo_jwt.png)

## Get JWT manually

### From JumpScale

```python
jwt = j.clients.openvcloud.getJWTTokenFromItsYouOnline(applicationId, secret)
```

### Through curl

```bash
export APP_ID="..."
export SECRET2="..."
export JWT2=$(curl -d 'grant_type=client_credentials&client_id='"$APP_ID"'&client_secret='"$SECRET2"'&response_type=id_token' https://itsyou.online/v1/oauth/access_token)
echo $JWT2
```

> Also see [Getting started with the OpenvCloud Cloud API](https://gig.gitbooks.io/ovcdoc_public/content/API/GettingStarted.html) for more details about this JWT.