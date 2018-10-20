# Using the Interactive Shell & Debugging

## js

In order to start the Jumpscale shell just type `jumpscale`.

There are many more command line tools installed for you to explore, type `jumpscale` to see available modules.

```python
* ***Application started***: jsshell
Python 3.5.2 (default, Nov 23 2017, 16:37:01) 
Type 'copyright', 'credits' or 'license' for more information
IPython 6.1.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]:
```

## Import Jumpscale in any Python script

e.g. try using ipython.

```python
from Jumpscale import j
j.[tab]
```

Now underneath j there is a basic set of functionality available. Just type j and then hit the tab key.

There are tons of extensions available which can be installed using jspackages (more about that later).

## From an existing Python script start Jumpscale and go to the debug shell

```python
from Jumpscale import j

#your python code here ... optionally using jumpscale

from IPython import embed
print "DEBUG NOW in my shell on pos X"
embed()
```

Your script will now stop and show you an ipython console in which you can inspect your code and work with all variables in an interactive way.

## Alternative way of debugging ipdb

Install ipdb `apt-get install python-ipdb` or `pip install ipdb`

ipdb exports functions to access the IPython debugger, which features tab completion, syntax highlighting, better tracebacks, better introspection with the same interface as the pdb module.

```python
print "Debug point for checking ...."
import ipdb; ipdb.set_trace()

 ipdb.set_trace()
> /usr/lib/python2.7/dist-packages/IPython/core/displayhook.py(228)__call__()
    227 
--> 228     def __call__(self, result=None):
    229         """Printing with history cache management.

ipdb> help

Documented commands (type help <topic>):
========================================
EOF    bt         cont      enable  jump  pdef   r        tbreak   w
a      c          continue  exit    l     pdoc   restart  u        whatis
alias  cl         d         h       list  pinfo  return   unalias  where
args   clear      debug     help    n     pp     run      unt
b      commands   disable   ignore  next  q      s        until
break  condition  down      j       p     quit   step     up

Miscellaneous help topics:
==========================
exec  pdb

Undocumented commands:
======================
retval  rv
```

More info about ipdb \<<https://github.com/gotcha/ipdb>>

```
!!!
title = "How To Use The Shell And Debug"
date = "2017-04-08"
tags = ["howto"]
```

