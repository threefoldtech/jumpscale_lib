import time

from js9 import j
from pyghmi.ipmi import command
from pyghmi.ipmi.private import session

JSConfigBase = j.tools.configmanager.base_class_config

TEMPLATE = """
bmc = ""
user = ""
password = ""
port = 623
"""


class Ipmi(JSConfigBase):
    """ Ipmi client

    Before using the ipmi client, make sure to install requirements.txt included in this directory
    """

    def __init__(self, instance, data={}, parent=None, interactive=None):
        JSConfigBase.__init__(self, instance=instance,
            data=data, parent=parent, template=TEMPLATE)

        self.ipmi = command.Command(
            bmc=self.config.data["bmc"],
            userid=self.config.data["user"],
            password=self.config.data["password"],
            port=self.config.data["port"],
        )

    def power_on(self):
        """ Power on ipmi host
        """
        self.ipmi.set_power("on", wait=True)

    def power_off(self):
        """ Power off ipmi host
        """
        self.ipmi.set_power("off", wait=True)

    def power_status(self):
        """ Returns power status of ipmi host
        
        Returns:
            str -- power status of node ('on' or 'off')
        """
        return self.ipmi.get_power()['powerstate']

    def power_cycle(self):
        """ Power off host, wait a couple of seconds and turn back on again.
        The power will always be turned on at the end of this call.

        Not using self.ipmi.set_power("reset", wait=True) as it's not reliable to use,
        power state will be pending.
        """
        self.power_off()
        time.sleep(5)
        self.power_on()
