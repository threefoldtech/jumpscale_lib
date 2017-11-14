import logging

class PublicKeys:
    def __init__(self, user):
        self._user = user
        self._client = user._client

    def list(self):
        """List all public keys of the ItsYou.online user."""

        try:
            resp = self._client.users.ListPublicKeys(self._user.username)
        except Exception as e:
            logging.exception("Unable to list all public keys")
            return
        
        public_keys = list()

        for item in resp.json():
            try:
                public_key = self.get(item['label'])
            except Exception as e:
                logging.exception("Unable to get public key with label %s" % (item["label"]))
                return
            public_keys.append(public_key)
        return public_keys

    def get(self, label):
        """
        Gets a pubic key with a given label.

        Args:
            label: label of the public key

        Returns a public key object.
        """
        try:
            resp = self._client.users.GetPublicKey(label, self._user.username)
        except Exception as e:
            logging.exception("Unable to get public key with label %s" % (label))
            return
        return PublicKey(self._user, resp.json())      

    def add(self, label, public_key):
        """
        Adds a pubic key with a given label.

        Args:
            label: label of the public key

        Returns public key object.
        """
        data = {
            'label' : label,
            'publickey' : public_key
        }
       
        try:
            resp = self._client.users.AddPublicKey(data, self._user.username)
        except Exception as e:
            logging.exception("Unable to add public key")
            return

        if resp.ok:
            return self.get(label)
        else:
            logging.exception("Unable to add public key")
            return

    def delete(self, label):
        """
        Delete the pubic key with given label.

        Returns:
            True if successful
            False if unsuccessful
        """
        try:
            resp = self._client.users.DeletePublicKey(label, self._user.username)
        except Exception as e:
            logging.exception("Unable to delete public key with label %s" % label)
            return False
    
        return True

class PublicKey:

    def __init__(self, user, model):
        self._user = user
        self._client = user._client
        self.model = model

    def update(self, label=None, public_key=None):
        """
        Updates a pubic key and/or its label.

        Args:
            label: label of the public key; defaults to None
            public_key: new public key; defaults to None

        Returns updated public key object.
        """
        if label:
            self.model["label"] = label
        
        if public_key:
            self.model["publickey"] = public_key

        data = {
            'label' : self.model["label"],
            'publickey' : self.model["publickey"]
        }
        
        try:
            resp = self._client.users.UpdatePublicKey(data, self.model["label"], self._user.username)
        except Exception as e:
            logging.exception("Unable to update public key")
            return

        return self

    def delete(self):
        """
        Delete the pubic key.

        Returns:
            True if successful
            False if unsuccessful
        """
        try:
            resp = self._client.users.DeletePublicKey(self.model["label"], self._user.username)
        except Exception as e:
            logging.exception("Unable to delete public key")
            return False
    
        return True

    def __repr__(self):
        return "public key: %s" % (self.model["label"])

    __str__ = __repr__