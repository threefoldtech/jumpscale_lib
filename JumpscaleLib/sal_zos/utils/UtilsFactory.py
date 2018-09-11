from Jumpscale import j
from JumpscaleLib.sal_zos.abstracts import ZTNic

JSBASE = j.application.JSBaseClass


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
