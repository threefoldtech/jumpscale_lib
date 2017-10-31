# Zero-OS Hub Client

## Staging
Install upstream client:
```
pip install --user -e 'git+https://github.com/zero-os/0-hub@api-client#egg=zerohub&subdirectory=client'
```

## Using the client

### Public
You can make basic requests without authentification like:

....

### Authentification
In order to use upload, delete, ... feature, you need to authentificate yourself. Simply add token
(which is a itsyou.online jwt) as parameter.

...
