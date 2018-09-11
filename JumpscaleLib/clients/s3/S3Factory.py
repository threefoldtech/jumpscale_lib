from Jumpscale import j

from .S3Client import S3Client

JSConfigBase = j.tools.configmanager.JSBaseClassConfigs


class S3Factory(JSConfigBase):
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.s3"
        self.__imports__ = "minio"
        JSConfigBase.__init__(self, S3Client)

    def install(self):
        p = j.tools.prefab.local
        p.runtimes.pip.install("minio")

    def configure(self, instance, address, port, accesskey, secretkey, bucket="main"):
        """
        """
        data = {}
        data["address"] = address
        data["port"] = port
        data["accesskey_"] = accesskey
        data["secretkey_"] = secretkey
        data["bucket"] = bucket

        return self.get(instance=instance, data=data)

    def test(self):
        """
        do:
        js_shell 'j.clients.s3.test()'
        """

        client = self.get()
        self.logger.debug(client.serversGet())
