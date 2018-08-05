from JumpscaleLib.sal_zos.abstracts import ZTNic


class Utils:

    @staticmethod
    def authorize_zerotiers(identify, nics):
        for nic in nics:
            if isinstance(nic, ZTNic):
                nic.authorize(identify)

    @staticmethod
    def format_ports(ports):
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
