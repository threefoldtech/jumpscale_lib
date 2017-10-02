class Actions:
    def __init__(self, service):
        self._service = service
        self._repository = service._repository
        self._api = service._repository._api

    def list(self, state=None):
        """
        List all actions.

        Args:
            state: allowing you to filter on state

        Returns:
            list of actions
        """
        actions = list()

        if self._service.model['actions']:
            for action in self._service.model['actions']:
                if state and action['state'] != state:
                    continue
                actions.append(Action(self._service, action))

        return actions

    def get(self, name):
        """
        Get the action with a given name.

        Args:
            name: name of the action.

        Returns:
            action instance

        Raises:
            KeyError is an action with given name was not found.
        """
        for action in self.list():
            if action.model['name'] == name:
                return action
        raise KeyError("Could not find action with name {}".format(name))


class Action:
    def __init__(self, service, model):
        self._service = service
        self._repository = service._repository
        self._api = service._repository._api
        self.model = model

    def __repr__(self):
        return "action: %s" % (self.model["name"])

    __str__ = __repr__