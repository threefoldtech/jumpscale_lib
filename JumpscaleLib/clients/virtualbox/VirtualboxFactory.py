from time import sleep

from jumpscale import j

from .VirtualboxClient import VirtualboxClient

JSConfigBase = j.tools.configmanager.base_class_configs


class VirtualboxFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.virtualbox"
        JSConfigBase.__init__(self, VirtualboxClient)
        self.logger_enable()

    @property
    def client(self, name="default"):
        return self.get(name, interactive=False)

    def zero_os_get(self, name="test", zerotierinstance="", redis_port=4444):
        """
        js_shell 'j.clients.virtualbox.zero_os_get(name="test")'
        """

        self.logger.info("will create zero-os:%s on redis port:%s" % (name, redis_port))

        cl = j.clients.virtualbox.client
        cl.reset(name)

        if j.sal.nettools.checkListenPort(redis_port):
            raise RuntimeError("cannot use port:%s is already in use" % redis_port)

        vm = cl.zos_create(name=name, zerotierinstance=zerotierinstance, redis_port=redis_port)
        vm.start()

        from time import sleep

        retries = 30
        self.logger.info("wait till VM started (portforward on %s is on)." % redis_port)
        while retries:
            if j.sal.nettools.tcpPortConnectionTest("localhost", 4445):
                self.logger.info("VM port answers")
                break
            else:
                self.logger.debug("retry in 2s")
                sleep(2)
            retries -= 1
        else:
            raise RuntimeError("could not connect to VM port %s in 60 sec." % redis_port)

        retries = 100
        self.logger.info("wait till zero-os core redis on %s answers." % redis_port)
        while retries:
            r = j.clients.redis.get("localhost", redis_port, fromcache=False, ping=True, die=False, ssl=True)
            if r is not None:
                self.logger.info("zero-os core redis answers")
                break
            else:
                self.logger.debug("retry in 2s")
                sleep(2)
            retries -= 1
        else:
            raise RuntimeError("could not connect to VM port %s in 200 sec." % redis_port)

        zcl = j.clients.zos.get(name, data={"host": "localhost", "port": redis_port})
        retries = 200
        self.logger.info("internal files in ZOS are now downloaded for first time, this can take a while.")

        self.logger.info("check if we can reach zero-os client")
        while retries:
            if zcl.is_running():
                print("Successfully started ZOS on VirtualBox vm\n"
                      "with port forwarding {port} -> 6379 in VM\n"
                      "to get zos client run:\n"
                      "j.clients.zos.get('{instance}')\n"
                      "**DONE**".format(instance=name, port=redis_port))
                break
            else:
                self.logger.debug("couldn't connect to the created vm will retry in 2s")
                sleep(2)
            retries -= 1
        else:
            raise RuntimeError("could not connect to zeroos client in 400 sec.")

        self.logger.info("zero-os client active")
        self.logger.info("ping test start")
        pong = zcl.client.ping()
        self.logger.debug(pong)
        assert "PONG" in pong
        self.logger.info("ping test OK")

        return redis_port

    def zero_os_private_address(self, node):
        # assume vboxnet0 use an 192.168.0.0/16 address
        for nic in node.client.info.nic():
            if len(nic['addrs']) == 0:
                continue

            if nic['addrs'][0]['addr'].startswith("192.168."):
                return nic['addrs'][0]['addr'].split('/')[0]

        return None

    def zero_os_private(self, node):
        self.logger.debug("resolving private virtualbox address")

        private = j.clients.virtualbox.zero_os_private_address(node)
        self.logger.info("virtualbox machine private address: %s" % private)

        node = j.clients.zos.get('builder_private', data={'host': private})
        node.client.ping()

        return node

    def test(self, instance="test"):
        """
        js_shell 'j.clients.virtualbox.test()'
        """

        cl = j.clients.virtualbox.client
        cl.reset(instance)
        vm = cl.zos_create(name=instance, zerotierinstance="", redis_port="4444")
        vm.start()

        zcl = j.clients.zos.get(instance, data={"port": "4444"})
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
