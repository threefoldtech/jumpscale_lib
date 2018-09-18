from jumpscale import j
import re, ipaddress
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

    def is_valid_portforward(self, source, target):
        if self._valid_portforward_component_format(source) and self._valid_portforward_component_format(target):
            return True
        return False

    def _valid_portnum(self, portstr):
        try:
            intport = int(portstr)
            if intport > 0: # number
                return True
        except ValueError:
                return False
        return False


    def _valid_portforward_component_format(self, portstr):
        # port as number or ip:port or interface:port
        if not isinstance(portstr, str):
            portstr = str(portstr)
    
        if self._valid_portnum(portstr):
            return True

        if not re.match(".+?:\d+", portstr):
            return False

        first, portcomponent = portstr.split(":") # first can ip or interface.
        
        if not self._valid_portnum(portcomponent):
            return False
        
        return True