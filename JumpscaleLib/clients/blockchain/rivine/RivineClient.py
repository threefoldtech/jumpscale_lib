"""
Rivine Client
"""

from Jumpscale import j

from JumpscaleLib.clients.blockchain.rivine.RivineWallet import RivineWallet
from JumpscaleLib.clients.blockchain.rivine.RivineMultiSigWallet import RivineMultiSignatureWallet


TEMPLATE = """
bc_addresses = []
seed_ = ""
nr_keys_per_seed = 50
minerfee = 100000000
password_ = ""
"""

JSConfigBase = j.tools.configmanager.JSBaseClassConfig


class RivineClient(JSConfigBase):
    """
    Rivine client object
    """
    def __init__(self, instance, data=None, parent=None, interactive=False):
        """
        Initializes new Rivine Client
        """
        if not data:
            data = {}

        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent,
                              template=TEMPLATE, interactive=interactive)
        self._wallet = None


    @property
    def wallet(self):
        if self._wallet is None:
            client = j.clients.rivine.get(self.instance, create=False)
            # Load a wallet from a given seed. If no seed is given,
            # generate a new one
            seed = self.config.data['seed_']
            if seed == "":
                seed = j.data.encryption.mnemonic.generate(strength=256)
                # Save the seed in the config
                data = dict(self.config.data)
                data['seed_'] = seed
                cl = j.clients.rivine.get(instance=self.instance,
                        data=data,
                        create=True,
                        interactive=False)
                cl.config.save()
                # make sure to set the seed in the current object.
                # if not, we'd have a random non persistent seed until
                # the first reload
                self.config.data['seed_'] = seed
            self._wallet = RivineWallet(seed=seed,
                                        bc_networks=self.config.data['bc_addresses'],
                                        bc_network_password=self.config.data['password_'],
                                        nr_keys_per_seed=int(self.config.data['nr_keys_per_seed']),
                                        minerfee=int(self.config.data['minerfee']),
                                        client=client)
        return self._wallet
