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

_ipmi = None
_last_session_clear = None

class Ipmi(JSConfigBase):
    """ Ipmi client

    Before using the ipmi client, make sure to install requirements.txt included in this directory
    """

    def __init__(self, instance, data={}, parent=None, interactive=None):
        global _ipmi
        global _last_session_clear

        JSConfigBase.__init__(self, instance=instance,
            data=data, parent=parent, template=TEMPLATE)

        # When new Command is created that already exists, will make this creation block indefinitely,
        # clearing initting_sessions seems to fix this.
        if _ipmi is None:
            self.logger.debug("creating ipmi client")
            session.Session.initting_sessions.clear()
            _ipmi = command.Command(
                bmc=self.config.data["bmc"],
                userid=self.config.data["user"],
                password=self.config.data["password"],
                port=self.config.data["port"],
            )
            _last_session_clear = time.time()
        self.logger.debug("using preexisting ipmi client")

    def _clear_sessions(self):
        # Resets ipmi sessions every 30s, 
        # else the client will time out when a call is made after about a minute.
        # Refreshing only after 30s, if new sessions are created in quick succession, the ipmi client will run out of resources
        global _ipmi
        global _last_session_clear

        if time.time() - _last_session_clear >= 30:
            self.logger.debug("refreshing ipmi session")
            session.Session.initting_sessions.clear()
            session.Session.waiting_sessions.clear()
            session.Session.keepalive_sessions.clear()
            _ipmi.ipmi_session = session.Session(
                self.config.data["bmc"],
                self.config.data["user"],
                self.config.data["password"],
                port=self.config.data["port"],
            )
            _last_session_clear = time.time()

    @property
    def ipmi(self):
        global _ipmi
        self._clear_sessions()
        return _ipmi

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
