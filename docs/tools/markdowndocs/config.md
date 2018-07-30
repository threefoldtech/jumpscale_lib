
```toml

[[docsite]]
name = "core"
url = "https://github.com/Jumpscale/core/tree/development"

[[docsite]]
name = "tf_home"
url = "https://github.com/threefoldfoundation/tree/info_foundation"
publish = "/foundation"

[[docsite]]
name = "tf_home"
path = "content" #starts from directly where we start js_doc ...
publish = "/"

[default]
disqus = 'a-disqus-name'
template = "https://github.com/Jumpscale/docgenerator/tree/master/templates/docsify"
doc_add_meta = false

[webserver]
addr = "localhost"
port = 8888

```

## principles

- default gets loaded first and added to every docsite config info
- publish means gets exposed under $url/$publish
- if publish not specified then the location will not be exposed at all, but is loaded in memory
- diq
- any name can be used on [default] or [docsite] level, can also specify new levels e.g. [varia] ... will be key in dict

