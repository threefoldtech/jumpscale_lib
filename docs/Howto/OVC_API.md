# How to use the OpenvCloud Cloud API

It is highly recommended to interact with OpenvCloud through the OpenvCloud client, as documented in [Using the OpenvCloud Client](/docs/OVC_client.md).

Underneath the OpenvCloud client uses the OpenvCloud Cloud API, which is documented here.

- [Using Python](#python)
- [Using JavaScript](javascript)

<a id="python"></a>
## Using Python

In order to interact with the OpenvCloud Cloud API you will need to authenticate, for which you need a JSON Web token (JWT). See [How to get a JWT for authenticating against OpenvCloud](JWT_for_OVC.md) for instructions on how to get this JWT.

This JWT then needs to be added to your headers as follows:
```python
headers={'Authorization': 'bearer ' + jwt}
```

Here's an example on how to list all OpenvCloud accounts you have access to based on the JWT, in this case for an OpenvCloud active on `be-gen-1`:
```python
base_url = "https://be-gen-1.demo.greenitglobe.com/restmachine/"

requests.post(base_url + "cloudapi/cloudspaces/list", headers=headers).json()
```

<a id="javascript"></a>
## Using JavaScript

For the JavaScript example we show to authenticate against OpenvCloud using the legacy username and password, which we highly discourage:
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