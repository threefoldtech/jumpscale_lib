from js9 import j
from nacl.public import PrivateKey, SealedBox, PublicKey
import nacl.signing
import nacl.secret
import nacl.utils
import nacl.hash
import hashlib
import paramiko


class NACLClientFactory:

    def __init(self):
        self.__jslocation__ = "j.data.nacl"

    def get(self, name="key", path="", secret=""):
        """
        if path not specified then is current path
        """
        return NACLClient(name, path, secret)


class NACLClient:

    def __init__(self, name, path, secret, keyname_ssh=""):

        self.ssh_agent = paramiko.agent.Agent()

        if len(self.ssh_agent.get_keys()) != 1:
            raise RuntimeError(
                "only 1 ssh key supported for now, need use use self.keyname_ssh")
        self.ssh_agent_key = self.ssh_agent.get_keys()[0]
        if isinstance(secret, str):
            secret = secret.encode()
        self.name = name
        if path == "":
            self.path = j.sal.fs.getcwd()
        else:
            self.path = path
        # print("SELF.PATH", self.path)
        self.keyname_ssh = keyname_ssh

        self.keyname = name

        # get/create the secret seed
        self.path_secretseed = "%s/%s.seed" % (self.path, self.keyname)
        if not j.sal.fs.exists(self.path_secretseed):
            secretseed = self.hash32(nacl.utils.random(
                nacl.secret.SecretBox.KEY_SIZE))
            j.sal.fs.writeFile(self.path_secretseed, secretseed)
        else:
            secretseed = j.sal.fs.readFile(self.path_secretseed, binary=True)

        if secret == b"":
            self.secret = b""
        else:
            # this creates a unique encryption box
            # the secret needs 3 components: the passphrase(secret), the
            # secretseed means the repo & a loaded ssh-agent with your ssh key
            secret2 = self.hash32(secretseed + secret +
                                  self.sign_with_ssh_key(secretseed + secret))
            # self._box is a temp encryption box which only exists while this
            # process runs
            # create temp box encrypt/decr (this to not keep secret in mem)
            self._box = nacl.secret.SecretBox(
                nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE))
            self.secret = self._box.encrypt(
                secret2, nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE))
            secret = ""
            secret2 = ""
            secretseed = ""

        self.path_privatekey = "%s/%s.priv" % (self.path, self.keyname)
        self.path_pubkey = "%s/%s.pub" % (self.path, self.keyname)
        if not j.sal.fs.exists(self.path_privatekey) or not j.sal.fs.exists(self.path_pubkey):
            # self._keys_generate() #DOES NOT WORK YET  #TODO: *1
            pass
        self._privkey = ""

    def _load(self):
        self._privkey = j.sal.fileGetContents(
            self.path_privatekey, binary=True)
        self.pubkey = j.sal.fileGetContents(self.path_pubkey, binary=True)

    @property
    def privkey(self):
        if self._privkey == "":
            self._load()
        key1 = self.decryptSymmetric(self._privkey)
        return PrivateKey(key1)

    def _getSecret(self):
        # this to make sure we don't have our secret key open in memory
        if self.secret == b"":
            return b""
        res = self._box.decrypt(self.secret)
        if res == b"":
            raise RuntimeError("serious bug, cannot get secret key")
        return res

    def tobytes(self, data):
        if j.data.types.bytes.check(data) == False:
            data = data.encode()  # will encode utf8
        return data

    def hash32(self, data):
        m = hashlib.sha256()
        m.update(self.tobytes(data))
        return m.digest()

    def hash8(self, data):
        # shortcut, maybe better to use murmur hash
        m = hashlib.sha256()
        m.update(self.tobytes(data))
        return m.digest()[0:8]

    def encryptSymmetric(self, data, secret=""):
        if secret == "":
            box = nacl.secret.SecretBox(self._getSecret())
        else:
            box = nacl.secret.SecretBox(self.hash32(secret))
        res = box.encrypt(self.tobytes(data), nacl.utils.random(
            nacl.secret.SecretBox.NONCE_SIZE))
        box = None
        return res

    def decryptSymmetric(self, data, secret=b""):
        if secret == b"":
            box = nacl.secret.SecretBox(self._getSecret())
        else:
            box = nacl.secret.SecretBox(self.hash32(secret))
        res = box.decrypt(self.tobytes(data))
        box = None
        return res

    def _keys_generate(self):
        """
        Generate private key (strong) & store in chosen path & will load in this class
        """
        key = PrivateKey.generate()
        key2 = key.encode()
        key3 = self.encryptSymmetric(key2)
        path = self.path_privatekey
        j.sal.fs.writeFile(path, key2, binary=True)
        j.sal.fs.chmod(path, 0o600)

        pubkey = self.pubkey_get(name, path)

        key2 = key2.public_key.encode()
        key3 = self.encryptSymmetric(key2)
        path = self.path_pubkey
        j.sal.fs.writeFile(path, key2, binary=True)
        j.sal.fs.chmod(path, 0o600)

    def test(self):

        # import ipdb
        # ipdb.set_trace()
        a = self.encryptSymmetric("something")
        b = self.decryptSymmetric(a)

        assert b == b"something"

        a = self.encryptSymmetric("something", b"qwerty")
        b = self.decryptSymmetric(a, b"qwerty")
        assert b == b"something"

        a = self.encryptSymmetric("something", b"qwerty")
        b = self.decryptSymmetric(a, b"qwerty")
        assert b == b"something"

        a = self.encryptSymmetric(b"something", b"qwerty")
        b = self.decryptSymmetric(a, b"qwerty")
        assert b == b"something"

    def start(self):
        try:
            from jose import jwt
        except:
            print("jose not installed will try now")
            j.sal.process.execute("pip3 install python-jose")

        self.init()

    def sign_with_ssh_key(self, data):
        """
        will return 32 byte signature which uses the ssh_agent loaded on your system
        this can be used to verify data against your own ssh_agent to make sure data has not been tampered with
        """
        self.keyname_ssh
        hash = hashlib.sha1(data).digest()
        return self.hash32(self.ssh_agent_key.sign_ssh_data(hash))

    # def init(self):
    #     self.path=j.clients.git.pullGitRepo(url=self.url)

    ###OLD ###

    def load(self, secret):
        print("sss")
        from IPython import embed
        embed(colors='Linux')

    def privatekey_get(self, name, path=None):
        """
        docstring here
            :param name: name of file that contains pubkey
            :param path: path of dir of the key file
            @return: private key
        """
        file_path = self._get_key_path(name, path)
        encoded_priv_key = j.sal.fs.readFile(file_path, binary=True)
        return PrivateKey(encoded_priv_key)

    def pubkey_get(self, name, path=None):
        """
        Get public key derived from private key stored in the filesystem
            :param name: filename that contains the private key
            :param path: path of dir of the key file
            @return: public key
        """
        file_path = self._get_key_path(name, path)
        encoded_priv_key = j.sal.fs.readFile(file_path, binary=True)
        private_key = PrivateKey(encoded_priv_key)
        return private_key.public_key

    def encrypt(self, data, keyname=None, keypath=None, pubkey=""):
        """
        Encrypt data using key provided in keyname or pubkey
            :param data: data to be encrypted, should be of type binary
            :param pubkey: pubkey to encrypt the data, can be string or instance of nacl.public.PublicKey
            :param keyname: name of file that contains private key, will be ignored if pubkey argument is not empty
            :param keypath: directory path that has the key file
            @return: encrypted data
        """

        if pubkey:
            pubkey = pubkey if isinstance(
                pubkey, PublicKey) else PublicKey(pubkey)
        else:
            keyname = keyname or j.core.state.configMe["ssh"]["sshkeyname"]
            pubkey = self.get_public_key(name=keyname, path=keypath)

        sealed_box = SealedBox(pubkey)
        return sealed_box.encrypt(data)

    def decrypt(self, data, keyname, keypath=None):
        """
        Decrypt incoming data using the keyname provided
            :param data: encrypted data provided
            :param keyname: keyname that has the key to decrypt the data
            :param keypath: directory path that has the key file
            @return decrypted data
        """

        priv_key = self.get_priv_key(name=keyname, path=keypath)
        unseal_box = SealedBox(priv_key)
        return unseal_box.decrypt(data)

    def sign(self, data):
        """
        Sign data provided
            :param data: data to be signed, should be of type binary
            @return: tuple of signed data and verification key
        """
        signing_key = nacl.signing.SigningKey.generate()
        signed = signing_key.sign(data)
        verify_key = signing_key.verify_key
        return signed, verify_key.encode(encoder=nacl.encoding.HexEncoder)

    def verify(self, data, signature):
        """
        verify data provided using the signature
            :param data: signed data to be verified
            :param signature: signature to verify the data
            @return: original data
        """
        verify_key = nacl.signing.VerifyKey(
            signature, encoder=nacl.encoding.HexEncoder)
        return verify_key.verify(data)
