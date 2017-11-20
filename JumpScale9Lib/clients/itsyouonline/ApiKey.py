import logging

class ApiKeys:
    def __init__(self, parent):
        self._parent = parent
        self._client = parent._client

    def list(self):
        """List all API access keys of the ItsYou.online user or organization."""
        try:
            if "username" in self._parent.model:
                resp = self._client.users.ListAPIKeys(self._parent.username)
            elif "globalid" in self._parent.model:
                resp = self._client.organizations.GetOrganizationAPIKeyLabels(self._parent.model["globalid"])
        except Exception as e:
            logging.exception("Unable to list all API access keys")
            return
        
        api_keys = list()

        for item in resp.json():
            try:
                if "username" in self._parent.model:
                    api_key = self.get(item["label"])
                elif "globalid" in self._parent.model:
                    api_key = self.get(item)
            except Exception as e:
                logging.exception("Unable to get API access key with label %s" % (item))
                return
            api_keys.append(api_key)
        return api_keys

    def get(self, label):
        """
        Gets an API access key with a given label.

        Args:
            label: label of the API access key

        Returns an API access key object.
        """        
        try:
            if "username" in self._parent.model:
                import ipdb;ipdb.set_trace()
                resp = self._client.users.GetAPIkey(label, self._parent.username)
            elif "globalid" in self._parent.model:
                resp = self._client.organizations.GetOrganizationAPIKey(label, self._parent.model["globalid"])
        except Exception as e:
            logging.exception("Unable to get API access key with label %s" % (label))
            return
        return ApiKey(self._parent, resp.json())      

    
class ApiKey:

    def __init__(self, parent, model):
        self._parent = parent
        self._client = parent._client
        self.model = model

    def __repr__(self):
        return "API access key: %s" % (self.model["label"])

    __str__ = __repr__