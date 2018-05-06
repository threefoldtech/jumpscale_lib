from js9 import j
from .. import templates
from .network import ZTNetwork


class Firewall:
    def __init__(self, container, networks, forwards):
        '''

        '''
        self.container = container
        self.networks = networks
        self.forwards = forwards

    def apply_rules(self):
        # nftables
        publicnetworks = list(filter(lambda net: net.ip.gateway, self.networks))
        if len(publicnetworks) != 1:
            raise RuntimeError('Need exactly one network with a gateway')
        privatenetworks = list(filter(lambda net: not net.ip.gateway and not isinstance(net, ZTNetwork), self.networks))
        nftables = templates.render('nftables.conf',
                                    publicnetwork=publicnetworks[0],
                                    privatenetworks=privatenetworks,
                                    portforwards=self.forwards)
        self.container.upload_content('/etc/nftables.conf', nftables)
        job = self.container.client.system('nft -f /etc/nftables.conf').get()
        if job.state != 'SUCCESS':
            raise RuntimeError("Failed to apply nftables {} {}".format(job.stdout, job.stderr))
