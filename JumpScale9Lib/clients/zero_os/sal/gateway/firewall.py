from .. import templates


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
        privatenetworks = list(filter(lambda net: not net.ip.gateway, self.networks))
        nftables = templates.render('nftables.conf',
                                    publicnetwork=publicnetworks[0],
                                    privatenetworks=privatenetworks,
                                    portforwards=self.forwards)
        self.container.upload_content('/etc/nftables.conf', nftables)
        job = self.container.client.system('nft -f /etc/nftables.conf').get()
        if job.state != 'SUCCESS':
            raise RuntimeError("Failed to apply nftables {} {}".format(job.stdout, job.stderr))
