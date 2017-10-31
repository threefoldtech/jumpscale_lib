# Zero-OS Hub Client

## Staging
Install upstream client:
```
pip install --user -e 'git+https://github.com/zero-os/0-hub@api-client#egg=zerohub&subdirectory=client'
```

## Using the client

### Public
You can make basic requests without authentification like:
```
cl = j.clients.zerohub.getClient()

cl.repositories()
cl.list()
cl.list('maxux')
cl.get('maxux', 'ubuntu1604.flist')
```

### Authentification
In order to use upload, delete, ... feature, you need to authentificate yourself. Simply add token
(which is a itsyou.online jwt) as parameter.

```
cl = j.clients.zerohub.getClient('jwt-token')
cl.upload('/tmp/my-upload-file.tar.gz')
cl.rename('my-upload-file.flist', 'my-super-flist.flist')
```
