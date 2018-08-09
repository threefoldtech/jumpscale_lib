from jumpscale import j


class FlistManager:

    def __init__(self, client, container_id):
        self._client = client
        self._id = container_id

    def create(self, src, dst, storage):
        args = {
            'container': self._id,
            'flist': dst,
            'src': src,
            'storage': storage,
        }
        flist_loction = self._client.json("corex.flist.create", args)
        return flist_loction.split('/mnt/containers/%d/' % self._id)[1]
