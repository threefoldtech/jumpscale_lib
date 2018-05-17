# DO NOT EDIT THIS FILE. This file will be overwritten when re-running go-raml.


class ApifarmersService:
    def __init__(self, client):
        self.client = client

    def ListFarmers(self, headers=None, query_params=None, content_type="application/json"):
        """
        List Farmers
        It is method for GET /api/farmers
        """
        if query_params is None:
            query_params = {}

        uri = self.client.base_url + "/api/farmers"
        return self.client.get(uri, None, headers, query_params, content_type)

    def RegisterFarmer(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        Register a farmer
        It is method for POST /api/farmers
        """
        if query_params is None:
            query_params = {}

        uri = self.client.base_url + "/api/farmers"
        return self.client.post(uri, data, headers, query_params, content_type)
