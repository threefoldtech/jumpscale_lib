import base64

class ExistsService:
    def __init__(self, client):
        self.client = client

    def exists_post(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        Check existance of a list of keys on the remote storage
        It is method for POST /exists

        Warning: keys need to be passed as binary
        """
        uri = self.client.base_url + "/exists"

        encoded = [base64.b64encode(item) for item in data]
        return self.client.post(uri, encoded, headers, query_params, content_type)
