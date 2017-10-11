# How to use the OpenvCloud APIs

- [Using Python](#python)
- [Using JavaScript](javascript)

<a id="python"></a>
## Using Python

In order to interact with the OpenvCloud you will need to authenticate, for which you have two options:
- [Authenticate with a JWT](#jwt) (recommended)
- [Authenticate with an OpenvCloud username and password](#legacy)


<a id="jwt"></a>
### Authenticate with a JWT

You'll first need a JWT, see [How to get a JWT for authenticating against OpenvCloud](how_to_get_a_JWT_for_OVC.md) for instructions.

This JWT then needs to be added to your headers as follows:
```python
headers={'Authorization': 'bearer ' + jwt}
```

Here's an example on how list all OpenvCloud accounts you have access to based on the JWT, here for an OpenvCloud active on `be-gen-1`:
```python
base_url = "https://be-gen-1.demo.greenitglobe.com/restmachine/"

requests.post(base_url + "cloudapi/cloudspaces/list", headers=headers).json()
```


<a id="legacy"></a>
### Authenticate with an OpenvCloud username and password

It is recommeded to rather use a JWT, as described above.

First get an OAuth key:
```python
import requests

base_url = "https://be-gen-1.demo.greenitglobe.com/restmachine/"

# Note empty authkey
# Fill in your username and password
params = {'username': {username}, 'password': {password}, 'authkey': ''}

auth_key = requests.post(base_url + 'cloudapi/users/authenticate', params).json()
```

With this auth_key you can then do all subsequest API call, here for listing all OpenvCloud account accesible to the specified user:
```python
requests.post(base_url + "cloudapi/cloudspaces/list", params).json()
```

Using cURL:
```shell
BASE_URL="https://be-gen-1.demo.greenitglobe.com/restmachine/"
curl -d username={username} -d password={password} $BASE_URL/cloudapi/users/authenticate
```

<a id="javascript"></a>
## Using JavaScript

Here is an example with username and password:
```javascript
var url = BASE_URL + "cloudapi/users/authenticate";
var params = {
    'username': <username>, //your username
    'password': <password>, //your password
    'authkey': ''
};
$.ajax({
    type: "GET",
    dataType: "jsonp",
    data: params,
    url: url,
    jsonp: '_jsonp',
    success: function (authkey) {
        console.log(authkey); //This is the returned authkey 
    }
});
```