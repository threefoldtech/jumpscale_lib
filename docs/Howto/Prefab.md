# How to Use Prefab

Link to [How to manage SSH keys](how_to_manage_SSH_keys.md)


# SSH Basic Connection Tool using Prefab

## Connect using an SSH agent

```python
executor = j.tools.executor.getSSHBased(addr='localhost', port=22)

executor.execute("ls /")

Out[2]: 
(2,
 'bin\nboot\nbootstrap.py\ncdrom\ndev\netc\nhome\ninitrd.img\ninitrd.img.old\nlib\nlib64\nlost+found\nmedia\nmnt\nopt\nproc\nroot\nrun\nsbin\nsrv\nsys\ntmp\nusr\nvar\nvmlinuz\nvmlinuz.old\n\n',
 '')
```

## Connect using username and password

```python
executor = j.tools.executor.getSSHBased(addr='localhost', port=22, login="root", passwd="1234")
```

## Connect using local SSH private key

```python
executor = j.tools.executor.getSSHBased(addr='localhost', port=22, login="root", passwd="1234", pushkey="ovh_install")
```


> Also see [How the use th SSH Agent Client]()