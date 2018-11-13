from jumpscale import j


class FlistManager:

    def __init__(self, client, container_id):
        self._client = client
        self._id = container_id

    def create(self, src, dst, storage, token=""):
        """
        Create an flist from src

        :param src: Absolute path of the directory with the files that will be uploaded to storage
        :param dst: Filst name (Ex: /tmp/myflist.flist)
        :param storage: Address of zdb were files will be uploaded
        :param token: An optional iyo jwt token to upload data into the backend and flist on the hub
        """
        args = {
            'container': self._id,
            'flist': dst,
            'src': src,
            'storage': storage,
            'token': token,
        }
        flist_loction = self._client.json("corex.flist.create", args)
        return flist_loction.split('/mnt/containers/%d/' % self._id)[1]
