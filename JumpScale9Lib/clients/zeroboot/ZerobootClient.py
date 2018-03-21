from js9 import j

JSConfigBase = j.tools.configmanager.base_class_config

TEMPLATE = """
racktivity_instance = ""
"""
class ZerobootClient(JSConfigBase):
    """Zeroboot client
    using racktivity
    """

    def __init__(self, instance, data={}, parent=None, interactive=None):
        JSConfigBase.__init__(self, instance=instance,
                              data=data, parent=parent, template=TEMPLATE)
        self.client = j.clients.racktivity.get(instance=self.config.data['racktivity_instance'])

    def power_info_get(self):
        """gets power info for opened ports
        """

        return self.client.power.getPower()

    def port_power_on(self, port_number):
        """turn port on
        """

        return self.client.power.setPortState(1, portnumber=port_number)

    def port_power_off(self, port_number):
        """turn port off
        """

        return self.client.power.setPortState(0, portnumber=port_number)

    def port_info(self, port_number):
        """get port info
        """
        return self.power.getStatePortCur(portnumber=port_number)

