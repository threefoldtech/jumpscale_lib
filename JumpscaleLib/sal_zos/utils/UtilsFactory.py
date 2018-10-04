import netaddr

from jumpscale import j
from JumpscaleLib.sal_zos.abstracts import ZTNic

JSBASE = j.application.jsbase_get_class()


class UtilsFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.sal_zos.utils"
        JSBASE.__init__(self)

    def authorize_zerotiers(self, identify, nics):
        for nic in nics:
            if isinstance(nic, ZTNic):
                nic.authorize(identify)

    def format_ports(self, ports):
        """
        Formats ports from ["80:8080"] to {80: 8080}
        :param ports: list of ports to format
        :return: formated ports dict
        """
        if ports is None:
            return {}
        formatted_ports = {}
        for p in ports:
            src, dst = p.split(":")
            formatted_ports[int(src)] = int(dst)

        return formatted_ports

    def get_ip_from_nic(self, addrs):
        for ip in addrs:
            network = netaddr.IPNetwork(ip['addr'])
            if network.version == 4:
                return network.ip.format()

    def get_zt_ip(self, nics, network=False, network_range=''):
        """[summary]
        Returns zerotier ip from a list of nics
        :param nics: a list of nic dicts
        :type nics: list
        :param network: a variable indicating if the ip should or should not be in network range <network_range>, defaults to False
        :param network: bool, optional
        :param network_range: the network range the ip should or should not be in, defaults to ''
        :param network_range: str, optional
        :return: [description]
        :rtype: [type]
        """
        if network and not network_range:
            raise RuntimeError('Invalid network range')

        for nic in nics:
            if nic['name'].startswith('zt'):
                ipAdress = self.get_ip_from_nic(nic['addrs'])
                if network and network_range and netaddr.IPAddress(ipAdress) not in netaddr.IPNetwork(network_range):
                    # required network range is not satisfied
                    continue
                if not network and network_range and netaddr.IPAddress(ipAdress) in netaddr.IPNetwork(network_range):
                    # network range should be avoided
                    continue
                return ipAdress
