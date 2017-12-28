

class RepositoriesService:
    def __init__(self, client):
        self.client = client

    def repoGetByID(self, id, headers=None, query_params=None, content_type="application/json"):
        """
        Get a repository by id
        It is method for GET /repositories/{id}
        """
        uri = self.client.base_url + "/repositories/" + id
        return self.client.get(uri, None, headers, query_params, content_type)
