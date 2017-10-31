# How to Use the ssh-agent Client

SSH key pairs are used a lot when working with the JumpScale framework.

Many of the JumpScale clients and tools such as Prefab rely on having private SSH keys loaded by ssh-agent.

At the command line you can list all running ssh-agent instances as follows:
```bash
pgrep ssh-agent
```

In order to start an ssh-agent from the command line:
```bash
ssh-agent
```

The same can be achieved using the ssh-agent client from the JumpScale interactive shell:
```python
j.clients.ssh.start_ssh_agent()
```

Or directly from the command line:
```bash
js9 'j.clients.ssh.start_ssh_agent()'
```

This single command will do the following for you:
- If no ssh-agent is running yet, a new instance will be started
- Load all SSH keys it can find in `$homedir/.ssh`

You only will need to do this once on a system. Once done the `.bashrc` file will make sure that in every new terminal you have access to your keys.

> If this is the first time then your current session does not have access to SSH keys yet, go into a new session to see the results and start using SSH.

Also note that by default it will not start a new instance if there is already one running.

You can verify that ssh-agent is running as follows:
```python
j.clients.ssh.ssh_agent_available()
```

In order to only load a specific private key, use the `path` attribute to specify the key location and name as follows:
```python
j.clients.ssh.start_ssh_agent(path="~/.ssh/id_rsa")
```

In order to check whether a specific private key is loaded:
```python
j.clients.ssh.ssh_agent_check_key_is_loaded("~/.ssh/id_rsa")
```

You can also have the client create an SSH key pair and immediately load the private key into ssh-agent, by using the `createkeys` argument as follows:
```python
j.clients.ssh.load_ssh_key(path="~/.ssh/mykey", createkeys=True)
```

Or alternatively omit the `path` argument to have `id_rsa` and `id_rsa.pub` created and `id_rsa` loaded by ssh-add:
```python
j.clients.ssh.load_ssh_key(createkeys=True)
```

As part of the SSH creation process you will be asked to enter a passphrase, which should be something that is private to you, and easy to remember.

The ssh-agent will know which agents to use and also remember passphrases of the keys so we don't have to provide them in code.

The ssh-agent client allows you automate interactions with a local or remote ssh-agent.


WHAT FOLLOWS IS WIP

```python
client = j.clients.ssh.get()
```


```python
client.login
client.look_for_keys
```

```python
client = j.clients.ssh.get(addr='remote', login='root', port=22, timeout=10)
```




If you want to read more about key management see below.


- [How to Use Prefab](prefab.md)


## SSH Basics

```bash
#load ssh-agent & all known keys
js 'j.clients.ssh.start_ssh_agent()'

#if it's the first time you need to tell current session path to ssh-agent
export SSH_AUTH_SOCK=~/sshagent_socket

#add another private ssh key(s) you require
ssh-add ~/ssh2/id_rsa

#list agent keys
ssh-add -l

#kill my own agents started as above
ssh-agent -k
```

Just add all the keys you require and the ssh-agent will remember them for you.

### Generate keys

```
ssh-keygen -t rsa -b 4096 -C "your_email@example.com -f ~/.ssh/mynewkey"
```

### Authorize remote key

At the CLI:

```bash
#copy your pub key to remote server authorized keys (add at end of file)
scp root@remoteserver.com:/home/despiegk/ssh2/id_rsa.pub /tmp/mykey.pub
ssh root@remoteserver.com cat /tmp/mykey.pub >> /root/.ssh/authorized_keys
```

This will allow you from your local server to login as root on the remote machine.

Using JumpScale:

```python
j.clients.ssh.SSHAuthorizeKey(remoteipaddr,login="root",passwd=None)
```

If `psswd=None` you will be asked for the password.

### Varia

```bash
#restart
/etc/init.d/ssh restart

#kill all ssh-agents (is dirty)
killall ssh-agent
```

## Secure your sshd config

```bash
#create recovery user (if needed)
adduser recovery

#make sure user is in sudo group
usermod -a -G sudo recovery

#sed -i -e '/texttofind/ s/texttoreplace/newvalue/' /path/to/file
sed -i -e '/.*PermitRootLogin.*/ s/.*/PermitRootLogin without-password/' /etc/ssh/sshd_config
sed -i -e '/.*UsePAM.*/ s/.*/UsePAM no/' /etc/ssh/sshd_config
sed -i -e '/.*Protocol.*/ s/.*/Protocol 2/' /etc/ssh/sshd_config

#only allow root & recovery user (make sure it exists)
sed -i -e '/.*AllowUsers.*/d' /etc/ssh/sshd_config
echo 'AllowUsers root' >> /etc/ssh/sshd_config
echo 'AllowUsers recovery' >> /etc/ssh/sshd_config

/etc/init.d/ssh restart
```

## Allow root to login

Dangerous do not do this, use sudo -s from normal user account""

```bash
sed -i -e '/.*PermitRootLogin.*/ s/.*/PermitRootLogin yes/' /etc/ssh/sshd_config
/etc/init.d/ssh restart
```



