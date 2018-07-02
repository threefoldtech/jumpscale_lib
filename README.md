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

## Running the tests
Jumpscale9 Libs come with unittests, to run them, you will need to have the pytest libarary installed, once you have it, you can run the following command:
```shell
root@abdelrahman-ThinkPad-T530:~# pytest -v /opt/code/github/jumpscale/lib9/tests/unittests/
====================================================================================================== test session starts ======================================================================================================
platform linux -- Python 3.6.5, pytest-3.6.2, py-1.5.3, pluggy-0.6.0 -- /usr/bin/python3
cachedir: ../opt/code/github/jumpscale/lib9/.pytest_cache
rootdir: /opt/code/github/jumpscale/lib9, inifile:
collected 31 items

../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/encoding/test_binary.py::test_encode_all PASSED                                                                                                          [  3%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/encoding/test_binary.py::test_encode_None PASSED                                                                                                         [  6%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/encoding/test_binary.py::test_encode_unknown_type PASSED                                                                                                 [  9%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/encoding/test_binary.py::test_encode_hex PASSED                                                                                                          [ 12%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/encoding/test_binary.py::test_encode_binary PASSED                                                                                                       [ 16%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/encoding/test_binary.py::test_encode_int PASSED                                                                                                          [ 19%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/encoding/test_binary.py::test_encode_bool PASSED                                                                                                         [ 22%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/encoding/test_binary.py::test_encode_list PASSED                                                                                                         [ 25%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/encoding/test_binary.py::test_encode_object PASSED                                                                                                       [ 29%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/encoding/test_binary.py::test_encode_currency PASSED                                                                                                     [ 32%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/encoding/test_binary.py::test_encode_slice PASSED                                                                                                        [ 35%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/encoding/test_binary.py::test_decode_int PASSED                                                                                                          [ 38%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_signatures.py::test_Ed25519PublicKey_binary PASSED                                                                                            [ 41%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_signatures.py::test_Ed25519PublicKey_json PASSED                                                                                              [ 45%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_transaction.py::test_create_transaction_v1 PASSED                                                                                             [ 48%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_transaction.py::test_coininput_json PASSED                                                                                                    [ 51%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_transaction.py::test_coininput_sign PASSED                                                                                                    [ 54%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_transaction.py::test_coinoutput_binary PASSED                                                                                                 [ 58%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_transaction.py::test_coinoutput_json PASSED                                                                                                   [ 61%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_transaction.py::test_transactionv1_json PASSED                                                                                                [ 64%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_transaction.py::test_transactionv1_get_input_signature_hash PASSED                                                                            [ 67%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_unlockconditions.py::test_ssf_sign PASSED                                                                                                     [ 70%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_unlockconditions.py::test_ssf_double_singature PASSED                                                                                         [ 74%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_unlockconditions.py::test_ssf_json PASSED                                                                                                     [ 77%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_unlockconditions.py::test_unlockhashcondition_binary PASSED                                                                                   [ 80%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_unlockconditions.py::test_unlockhashcondition_json PASSED                                                                                     [ 83%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_unlockconditions.py::test_locktimecondition_binary PASSED                                                                                     [ 87%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_unlockconditions.py::test_locktimecondition_json PASSED                                                                                       [ 90%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_unlockhash.py::test_unlock_to_string PASSED                                                                                                   [ 93%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_unlockhash.py::test_unlockhash_binary PASSED                                                                                                  [ 96%]
../opt/code/github/jumpscale/lib9/tests/unittests/clients/rivine/types/test_unlockhash.py::test_unlockhash_from_string PASSED                                                                                             [100%]

=================================================================================================== 31 passed in 0.58 seconds ===================================================================================================
root@abdelrahman-ThinkPad-T530:~#

```
