![travis](https://travis-ci.org/Jumpscale/lib9.svg?branch=master)

# lib9

`lib9` is a component of `JumpScale9` (see [here](https://github.com/Jumpscale/core9)). It extends `JumpScale9` functionalities by adding additional automation tools. It is the home for non core `JumpScale9` clients(e.g., Kubernetes, postgresql, rivine), tools(e.g., raml), system abstraction layers(e.g., ubuntu, docker) and different data format interactions(e.g., capnp).

See [docs](docs/README.md) for more details.

## Installtion

To use `lib9` `JumpScale9` [core](https://github.com/Jumpscale/core9) needs to be installed, since `lib9` depends on it.
Installing `JumpScale9` using [bash](https://github.com/Jumpscale/bash) should provide the user with an installation that includes `lib9`.

Follow the instructions to install and setup `bash` repo and then run the following command to have `lib9` installation with all the necessary dependencies:

```bash
export JS9BRANCH={BRANCH}
ZInstall_host_js9_full
```

Or isntalling using pip:

```bash
pip3 install git+https://github.com/Jumpscale/lib9@{BRANCH}
```

## Examples

Start the `JumpScale9` shell by typing `js9` into the console.

Using the docker abstraction layer to list running docker containers:

```python
j.sal.docker.containers
```

Using ubuntu abstraction layer to check current ubuntu installtion:

```python
j.sal.ubuntu.version_get()
```

`JumpScale9` uses a config manager that is responsible for managing and securing the data of the available clients. To use a client you need to have an instance to that client which will allow the user to perform the various client related opertaions. For instance a github client instance once available can be used to perform actions such as getting repo information.

This instance needs to be configured using config manager before it can be used, which will make it easier to reuse the same instance and ensure that sensitive data is encrypted. Check config manager [docs](https://github.com/Jumpscale/core9/blob/master/docs/config/configmanager.md) to get started.

If a github client instance is already configuerd it can be reused using the instance name as follows:

```python
git_cl = j.clients.github.get('myinstance')
```

The instance can be the used as follows:

```python
git_cl.repo_get('myrepo')
```