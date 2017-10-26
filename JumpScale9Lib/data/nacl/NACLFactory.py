
import nacl
import nacl.utils
from nacl.public import PrivateKey, SealedBox

# IMPORTANT
# use functionality in j.clients.ssh to deal with SSH-Agent & getting key info, improve if required


class NACLFactory:
    """
    https://pynacl.readthedocs.io/en/latest/
    """

    def __init__(self):
        self.__jslocation__ = "j.data.nacl"

    def privkeyGenerate(self, name, path=None):
        """
        generate private key (strong) & store in chosen path
        if path not specified store in ~/.ssh/$name.priv

        @return privkey

        """
        skbob = PrivateKey.generate()

    def privKeyGet(self, name, path=None):
        #...
        pkbob = skbob.public_key

    def encrypt(self, data, salt=None, keyname=None, pubkey=""):
        """
        if pubkey specified then use pubkey
        if not specified and keyname specified use that pubkey linked to that key (get from fs)
        make sure these keys get cached for next run't not to have this too slow
        """
        # QUESTION: do we need this salt??? if not ignore
        if keyname == None:
            keyname = j.core.state.configMe["ssh"]["sshkeyname"]
        # get required info from j.clients.ssh
        if salt == None:
            pass  # generate salt automatically

    def decrypt(self, keyname=None):
        pass

    def sign(self, data, keyname=None):
        pass

    def verify(self, data, signature, pubkey):
        pass
