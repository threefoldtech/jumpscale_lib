from js9 import j
from nacl.public import PrivateKey, SealedBox, PublicKey
import nacl.signing

# IMPORTANT
# use functionality in j.clients.ssh to deal with SSH-Agent & getting key info, improve if required


class NACLClient:
    """
    TODO: To use the SealedBox we use the latest dev of PyNacl package
    TODO: use the latest stable when it's added to the newest stable version (1.2.0)
    https://pynacl.readthedocs.io/en/latest/
    """

    def __init__(self):
        self.__jslocation__ = "j.data.nacl"
        self.default_key_dir = j.sal.fs.joinPaths(j.dirs.HOMEDIR, ".ssh")


    def _get_key_path(self, name, path=None):
        """
        Get key path derived from name and path provided
            :param name: name of the file
            :param path: path of dir of the key file, if None it'll fall back to ~/.ssh
            @return: key path
        """
        if path:
            return j.sal.fs.joinPaths(path, "%s.priv" % name)

        return j.sal.fs.joinPaths(self.default_key_dir, "%s.priv" % name)

    def generete_private_key(self, name, path=None):
        """
        Generate private key (strong) & store in chosen path
            :param name: file name that key should be stored in
            :param path: path of dir of the key file
            @return privkey
        """
        generated_priv_key = PrivateKey.generate()
        file_path = self._get_key_path(name, path)

        j.sal.fs.writeFile(file_path, generated_priv_key.encode())
        j.sal.fs.chmod(file_path, 0o600)
        return generated_priv_key

    def get_priv_key(self, name, path=None):
        """
        docstring here
            :param name: name of file that contains pubkey
            :param path: path of dir of the key file
            @return: private key
        """
        file_path = self._get_key_path(name, path)
        encoded_priv_key = j.sal.fs.readFile(file_path, binary=True)
        return PrivateKey(encoded_priv_key)

    def get_public_key(self, name, path=None):
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
            pubkey = pubkey if isinstance(pubkey, PublicKey) else PublicKey(pubkey)
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
        verify_key = nacl.signing.VerifyKey(signature, encoder=nacl.encoding.HexEncoder)
        return verify_key.verify(data)
