from js9 import j
from kubernetes import client, config


class KubernetesFactory:
    """
    kubernetes client factory each instance can relate to either a config file or a context or both
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.kubernetes"

    def get(self, config_path=None, context=None, ssh_key_path=None, incluster_config=False):
        """
        Get an instance of the kubernetes class loaded with config_path.
        If no path is given the default '${HOME}/.kube/config' path will be loaded.
        IMPORTANT Please follow instructions at
        https://developers.google.com/identity/protocols/application-default-credentials,
        to setup credentials.

        @param config_path,, str: full path to configuration file.
        @param context ,, str: context name usually the same as the cluster used for isolation on same nodes
        """
        from .Kubernetes import KubernetesMaster as K8s
        return K8s(config_path, context=context, ssh_key_path=ssh_key_path, incluster_config=incluster_config)


    def create_config(self, config, path=None):
        """
        create config file.

        @param config ,, dict the configurations in dict format
        @param path ,, str full path to location the file should be saved will default to HOMEDIR/.kube/config
        """
        if not path:
            directory = '%s/.kube/' % j.dirs.HOMEDIR
            j.sal.fs.createDir(directory)
            path = j.sal.fs.joinbPaths(directory, 'config')
        data = j.data.serializer.yaml.dumps(config)
        j.sal.fs.writeFile(path, data)
        j.logger.logging.info('file saved at %s' % path)

    def test(self):
        """
        TODO WIP
        """

        kub = self.get()
        kub.list_clusters()
        kub.list_deployments()
        kub.list_nodes()
        kub.list_pods()
        kub.list_services()
        prefab = kub.deploy_ubuntu1604('tester')
        prefab.core.run('ls')



