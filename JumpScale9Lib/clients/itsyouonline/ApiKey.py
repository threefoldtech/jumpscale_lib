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
                resp = self._client.users.GetAPIkey(label, self._parent.username)
            elif "globalid" in self._parent.model:
                resp = self._client.organizations.GetOrganizationAPIKey(label, self._parent.model["globalid"])
        except Exception as e:
            logging.exception("Unable to get API access key with label %s" % (label))
            return
        return ApiKey(self._parent, resp.json())      


    def add(self, label, callback_url=None, client_credentials_grant_type=False):
        """
        Adds a new API key.

        Args:
            label: label of the API key
            callback_url (None): callback URL for the API key; only relevant for organization keys
            client_credentials_grant_type (False): if set to true the key can be used for client credential grand type flows; only relevant for organization keys

        Returns API key object.
        """
        data = {
            'label' : label
        }
        import ipdb;ipdb.set_trace()
        if "username" in self._parent.model:
            data['username'] = self._parent.model["username"]
            try:
                resp = self._client.users.AddApiKey(data, self._parent.model["username"])
            except Exception as e:
                logging.exception("Unable to create a new API key for user with username %s" % (self._parent.model["username"]))
                return
        elif "globalid" in self._parent.model:
            if callback_url:
                data['callbackURL'] = callback_url
            if client_credentials_grant_type:
                data['clientCredentialsGrantType'] = True
            try:
                resp = self._client.organizations.CreateNewOrganizationAPIKey(data, self._parent.model["globalid"])
            except Exception as e:
                logging.exception("Unable to create a new API key for organization %s" % (self._parent.model["globalid"]))
                return

        if resp.ok:
            return self.get(label)
        else:
            logging.exception("Unable to create new API key")
            return

    def delete(self, label):
        """
        Delete the API key with given label.

        Returns:
            True if successful
            False if unsuccessful
        """
        if "username" in self._parent.model:
            try:
                resp = self._client.users.DeleteAPIkey(label, self._parent.model["username"])
            except Exception as e:
                logging.exception("Unable to delete API key for user with username %s" % (self._parent.model["username"]))
                return False
        elif "globalid" in self._parent.model:
            try:
                resp = self._client.organizations.DeleteOrganizationAPIKey(label, self._parent.model["globalid"])
            except Exception as e:
                logging.exception("Unable to delete API key for organization %s" % (self._parent.model["globalid"]))
                return False

        return True

    
class ApiKey:

    def __init__(self, parent, model):
        self._parent = parent
        self._client = parent._client
        self.model = model

    def __repr__(self):
        return "API access key: %s" % (self.model["label"])

    __str__ = __repr__