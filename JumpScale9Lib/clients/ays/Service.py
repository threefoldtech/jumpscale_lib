from requests.exceptions import HTTPError
from .Action import Actions
from .EventHandler import EventHandlers

def _extract_error(resp):
    if isinstance(resp, HTTPError):
        if resp.response.headers['Content-type'] == 'application/json':
            content = resp.response.json()
            return content.get('error', resp.response.text)
        return resp.response.text
    raise resp

class Services:
    def __init__(self, repository):
        self._repository = repository
        self._api = repository._api

    def list(self, role=None, name=None):
        """
        List all AYS services with specific role and instance name.

        Args:
            role: role of the service
            name: name of the service

        Returns: list of services
        """
        try:
            resp = self._api.listServices(self._repository.model.get('name'))

            ays_services = resp.json()
            services = list()
            for service in sorted(ays_services, key=lambda service: '{role}!{name}'.format(**service)):
                if role and service['role'] != role:
                    continue
                if name and service['name'] != name:
                    continue
                ays_service = self._api.getServiceByName(service['name'], service['role'], self._repository.model['name'])
                services.append(Service(self._repository, ays_service.json()))
            return services

        except Exception as e:
            print("Error while listing services: {}".format(_extract_error(e)))

    def get(self, role, name):
        """
        Get the AYS service with a specific role and instance name.

        Args:
            role: role of the service
            name: name of the service

        Returns: service instance

        Raises: KeyError when no service match the specified arguments.
        """
        for service in self.list():
            if service.model['role'] == role and service.model['name'] == name:
                return service
        raise KeyError("Could not find service with role {} and name {}".format(role, name))

    def delete(self, role, name):
        """
        Delete all services with a specific role and instance name.

        Args:
            role: role of the service
            name: name of the service

        Returns: nothing if succesful. else error from HTTP response object
        """
        try:
            for service in sorted(self.list(role, name), key=lambda service: service['role']):
                self._api.deleteServiceByName(name=service['name'], role=service['role'], repository=self._repository.mode['name'])
        except Exception as e:
            return _extract_error(e)

class Service:
    def __init__(self, repository, model):
        self._repository = repository
        self._api = repository._api
        self.model = model
        self.actions = Actions(self)
        self.eventHandlers = EventHandlers(self)

    def show(self):
        return

    def state(self):
        return

    def getChildren(self, role=None, name=None):
        """
        Get all children with a specified name and/or role

        Args:
            role: (optional) role of the children
            name: (optional) name of the children

        Returns: list of children
        """
        children = list()
        if self.model['children']:
            for child in self.model['children']:
                if role and child['role'] != role:
                    continue
                if name and child['name'] != name:
                    continue
                children.append(Service(self._repository, child))

    def getParent(self):
        """
        Get parent with a specified name and/or role

        Args: none

        Returns: parent, or none if no parent
        """
        if self.model['parent']:
            return Service(self._repository, self.model['parent'])
        else:
            return None

    def getConsumers(self, role=None, name=None):
        """
        Get all consumers with a specified name and/or role

        Args:
            role: (optional) role of the consumers
            name: (optional) name of the consumers

        Returns: list of consumers
        """
        consumers = list()
        if self.model['consumers']:
            for consumer in self.model['consumers']:
                if role and consumer['role'] != role:
                    continue
                if name and consumer['name'] != name:
                    continue
                consumers.append(Service(self._repository, consumer))
        return consumers

    def getProducers(self, role=None, name=None):
        """
        Get all producers with a specified name and/or role

        Args:
            role: (optional) role of the producers
            name: (optional) name of the producers

        Returns: list of producers
        """
        producers = list()
        if self.model['producers']:
            for producer in self.model['producers']:
                if role and producer['role'] != role:
                    continue
                if name and producer['name'] != name:
                    continue
                producers.append(Service(self._repository, producer))
        return producers

    def getActions(state=None, recurring=None, name=None):
        """
        Get all actions with a specified name and/or role

        Args:
            state: (optional) role of the producers
            recurring: (True/False) for only listing recurring/non-recurring actions
            name: (optional) name of the producers

        Returns: list of actions
        """
        actions = list()
        if self.model['actions']:
           for action in self.model['actions']:
                if state and action['state'] != state:
                   continue
                if recurring and action['recurring'] is None:
                   continue
                if name and action['name'] != name:
                   continue 
                actions.append(Action(self, action))
        return actions

    def getRecurringActions(self):
        """
        Get all recurring actions of the service

        Args: none

        Returns: list of recurring actions
        """
        recurringActions = self.getRecurringActions(recurring=True)
        return recurringActions

    def getEventHandlers(self):
        """
        Get all event handlers of the service

        Args: none

        Returns: list of event handlers
        """
        eventHandlers = list()
        if self.model['events']:
           for eventHandler in self.model['events']:
               eventHandlers.append(EventHandler(self, eventHandler))
        return eventHandlers

    def delete(self):
        """
        Delete a service and all its children.
        Be carefull with this action, there is undo option.

        Returns: HTTP response object
        """
        resp = self._api.deleteServiceByName(name=self.model['name'], role=self.model['role'], repository=self._repository.model['name'])
        return resp

    def __repr__(self):
        return "service: %s" % (self.model["name"])

    __str__ = __repr__
