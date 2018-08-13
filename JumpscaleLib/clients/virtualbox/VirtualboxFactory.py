from jumpscale import j

JSConfigBase = j.tools.configmanager.base_class_configs

from .VirtualboxClient import VirtualboxClient

class VirtualboxFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.virtualbox"
        JSConfigBase.__init__(self, VirtualboxClient)

    @property
    def client(self):
        return self.get("default",interactive=False)

    def test(self, instance="test"):
        """
        js_shell 'j.clients.virtualbox.test()'
        """

        cl = self.client
        cl.reset(instance)
        vm = cl.zos_create(name=instance, zerotierinstance="", redis_port="4444")
        vm.start()

        zcl = j.clients.zos.get(instance, data={
            "port": "4444"
        })
        retries = 10
        from time import sleep
        while retries:
            if zcl.is_running():
                print("Successfully started ZOS on VirtualBox vm\n"
                      "with port forwarding 4444 -> 6379\n"
                      "to get zos client run:\n"
                      "j.clients.zos.get('{instance}')\n"
                      "**DONE**".format(instance=instance))
                break
            else:
                self.logger.debug("couldn't connect to the created vm will retry in 30s")
                sleep(30)
            retries -= 1
        else:
            print("something went wrong")


