# How to get a JWT for authenticating against OpenvCloud

## first create your secrets on itsyou.online

Prerequirements:
- Registrated user on ItsYou.online

In order to get a JWT from ItsYou.online, you first need to create an application key for your ItsYou.online identity:

![](images/iyo_jwt.png)

## get jwt manually

### from jumpscale

```python
jwt = j.clients.openvcloud.getJWTTokenFromItsYouOnline(applicationId, secret)
```

### through curl

```bash
export APP_ID="..."
export SECRET2="..."
export JWT2=$(curl -d 'grant_type=client_credentials&client_id='"$APP_ID"'&client_secret='"$SECRET2"'&response_type=id_token' https://itsyou.online/v1/oauth/access_token)
echo $JWT2
```

