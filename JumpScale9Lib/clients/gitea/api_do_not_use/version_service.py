

class VersionService:
    def __init__(self, client):
        self.client = client

    def getVersion(self, headers=None, query_params=None, content_type="application/json"):
        """
        Returns the version of the Gitea application
        It is method for GET /version
        """
        uri = self.client.base_url + "/version"
        return self.client.get(uri, None, headers, query_params, content_type)
