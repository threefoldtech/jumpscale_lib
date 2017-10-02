class EventHandlers:
    def __init__(self, service):
        self._service = service
        self._repository = service._repository
        self._api = service._repository._api

    def list(self, command=None, channel=None, tag=None):
        """
        List all event handlers.

        Args:
            command: allowing you to filter on command
            channel: allowing you to filter on command
            tag: allowing you to filter on tag

        Returns:
            list of event handlers
        """
        eventHanders = list()
        if self._service.model['events']:
            for eventHandler in self._service.model['events']:
                if command and eventHandler['command'] != command:
                    continue
                if channel and eventHandler['channel'] != channel:
                    continue
                if tag and eventHandler['tags']:
                    for t in eventHandler['tags']:
                        if t['tag'] != tag:
                            continue
                eventHanders.append(Action(self._service, action))
        return eventHanders

    def get(self, command, channel):
        """
        Get the event handlers with a given command and channel.

        Args:
            command: name of the action
            channel: name of the channel


        Returns:
            event handlers

        Raises:
            KeyError is an event handler for a given command and channel was not found.
        """
        for eventHandler in self.list():
            if eventHandler.model['command'] == command and eventHandler.model['channel'] == channel:
                return eventHandler
        raise KeyError("Could not find action with name {}".format(name))


class EventHandler:
    def __init__(self, service, model):
        self._repository = service
        self._api = repository._api
        self.model = model

def __repr__(self):
    return "event handler for command %s on channel %s" % (self.model["command"], self.model["channel"])

__str__ = __repr__