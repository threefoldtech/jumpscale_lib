# How to use the AYS client

The AYS client is available as part of [jumpscale/lib9](https://github.com/Jumpscale/lib9).

In order to use it you have two options:
- [Use the AYS client on a machine with JumpScale installed, including the lib9 libraries](#jumpscale9)
- [Use the AYS client on a machine with only Python installed](#python)

```bash
BRANCH="9.3.0"
sudo -H pip3 install --upgrade git+https://github.com/jumpscale/lib9.git@${BRANCH}#subdirectory=JumpScale9Lib/clients/atyourservice
```