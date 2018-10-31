Example how to expose a service running on the tfgrid to the public internet

```python
wg = j.sal.webgateway.get('mywg', data={...})

# create a new service object for a web application running on the tfgrid
service = wg.service_create('my_blog')
# expose the web application to the public using a domain name
service.expose('superblog.com', ['http://192.168.1.10:8080'])
```

Example how to modify a already existing service on the webgateway
```python
wg = j.sal.webgateway.get('mywg', data={...})

service = wg.service_get('my_blog')
# the server running the web application has been moved on a different node
backend = service.proxy.backends[0]
backend.servers = [] # remove existing service from the backend configuration
backend.server_add('10.242.10.10' port=8081) # configure the new backend
service.deploy()
```

Example how to modify the public ip used by your webgateway
```python
wg = j.sal.webgateway.get('mywg', data={...})
wg.public_ips_set(['195.134.212.13'])
```