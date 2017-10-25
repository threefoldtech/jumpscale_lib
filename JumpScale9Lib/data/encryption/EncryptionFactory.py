

# IMPORTANT
# use functionality in j.clients.ssh to deal with SSH-Agent & getting key info, improve if required
# use j.data.nacl for underlying encryption/decryption/signing when possible


class EncryptionFactory:
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.data.encryption"
        self.privkeyGenerate = self.data.nacl.privkeyGenerate
        self.privKeyGet = self.data.nacl.privKeyGet
        self.encrypt = self.data.nacl.encrypt
        self.decrypt = self.data.nacl.decrypt
        self.sign = self.data.nacl.sign
        self.verify = self.data.nacl.verify

    def signShort(self, data, keyname=None):
        """
        sign using siphash and signature is only 8 bytes
        """
        pass

    def verifyShort(self, data, signature, pubkey):
        pass
