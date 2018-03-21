class InsertService:
    def __init__(self, client):
        self.client = client



    def insert_put(self, data, headers=None, query_params=None, content_type="multipart/form-data"):
        """
        Upload key/value to the remote storage
        It is method for PUT /insert
        """
        uri = self.client.base_url + "/insert"
        return self.client.put(uri, data, headers, query_params, content_type)
