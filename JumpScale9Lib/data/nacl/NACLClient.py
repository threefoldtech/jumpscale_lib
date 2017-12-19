from js9 import j
from nacl.public import PrivateKey, SealedBox, PublicKey
import nacl.signing
import nacl.secret
import nacl.utils
import nacl.hash
import nacl.encoding
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
        if not j.sal.fs.exists(self.path_privatekey):
            self._keys_generate()
        self._privkey = ""
        self._pubkey = ""

    def _load(self):
        self._privkey = j.sal.fs.fileGetContents(
           self.path_privatekey, binary=True)

    @property
    def privkey(self):
        if self._privkey == "":
            self._load()
        key = self.decryptSymmetric(self._privkey)
        privkey = PrivateKey(key)
        self._pubkey = privkey.public_key
        return privkey

    @property
    def pubkey(self):
        if self._pubkey == "":
            return self.privkey.public_key
        return self._pubkey

    def _getSecret(self):
        # this to make sure we don't have our secret key open in memory
        if self.secret == b"":
            return b""
        res = self._box.decrypt(self.secret)
        if res == b"":
            raise RuntimeError("serious bug, cannot get secret key")
        return res

    def tobytes(self, data):
        if not j.data.types.bytes.check(data):
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

    def encrypt(self, data):
        """
        Encrypt data using the public key
            :param data: data to be encrypted, should be of type binary
            @return: encrypted data
        """
        sealed_box = SealedBox(self.pubkey)
        return sealed_box.encrypt(data)

    def decrypt(self, data):
        """
        Decrypt incoming data using the private key
            :param data: encrypted data provided
            @return decrypted data
        """
        unseal_box = SealedBox(self.privkey)
        return unseal_box.decrypt(data)

    def _keys_generate(self):
        """
        Generate private key (strong) & store in chosen path & will load in this class
        """
        key = PrivateKey.generate()
        key2 = key.encode()
        key3 = self.encryptSymmetric(key2)
        path = self.path_privatekey
        j.sal.fs.writeFile(path, key3)
        j.sal.fs.chmod(path, 0o600)

    def test(self):
        a = self.encryptSymmetric("something")
        b = self.decryptSymmetric(a)

        assert b == b"something"

        a = self.encryptSymmetric("something", "qwerty")
        b = self.decryptSymmetric(a, b"qwerty")
        assert b == b"something"

        a = self.encryptSymmetric("something", "qwerty")
        b = self.decryptSymmetric(a, b"qwerty")
        assert b == b"something"

        a = self.encryptSymmetric(b"something", "qwerty")
        b = self.decryptSymmetric(a, b"qwerty")
        assert b == b"something"

        a = self.encrypt(b"something")
        b = self.decrypt(a)
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
        hash = hashlib.sha1(data).digest()
        return self.hash32(self.ssh_agent_key.sign_ssh_data(hash))

    def load(self, secret):
        print("sss")
        from IPython import embed
        embed(colors='Linux')

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
