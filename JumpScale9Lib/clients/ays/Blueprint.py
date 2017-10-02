from js9 import j
class Blueprints:
    def __init__(self, repository):
        self._repository = repository
        self._api = repository._api

    def list(self):
        """
        List all blueprints.

        Args: none

        Returns:
            list of blueprints
        """
        ays_blueprints = self._api.listBlueprints(self._repository.model.get('name')).json()
        blueprints = list()
        for blueprint in ays_blueprints:
            blueprints.append(Blueprint(self._repository, blueprint))
        return blueprints

    def get(self, name):
        """
        Get the blueprint with a given name.

        Args:
            name: name of the blueprint.

        Returns:
            blueprint instance

        Raises:
            KeyError is blueprint with given name was not found.
        """
        for blueprint in self.list():
            if blueprint.model.get('name') == name:
                return blueprint
        raise KeyError("Could not find blueprint with name {}".format(name))

    def create(self, name, blueprint):
        """
        Create a blueprint.

        Args:
            name: name of the blueprint, as it will be saved to disk and referenced.
            blueprint: blueprint as a string

        Returns:
            blueprint instance
        """
        data = j.data.serializer.json.dumps({'name': name, 'content': blueprint})

        resp = self._api.createBlueprint(data, self._repository.model["name"], headers=None)

        return self.get(name)

    def execute(self):
        """
        Executes all blueprints.

        Args: none

        Returns: nothing
        """
        for blueprint in sorted(self.list()):
            blueprint.execute()

class Blueprint:
    def __init__(self, repository, model):
        self._repository = repository
        self._api = repository._api
        self.model = model

    def execute(self):
        """
        Execute the blueprint.

        Args: none

        Returns: HTTP response object
        """
        resp = self._api.executeBlueprint('', self.model['name'], self._repository.model['name'], headers=None)
        return resp

    def delete(self):
        """
        Delete the blueprint.

        Args: none

        Returns: HTTP response object
        """
        resp = self._api.deleteBlueprint(blueprint=self.model['name'], repository=self._repository.model['name'], headers=None)
        return resp

    def get(self):
        """
        Get the actual blueprint content

        Args: none

        Returns: blueprint content
        """
        resp = self._api.getBlueprint(blueprint=self.model['name'], repository=self._repository.model['name'], headers=None)
        data=resp.json()
        return data['content']

    def archive(self):
        """
        Archive a blueprint

        Args: none

        Returns: HTTP response object
        """
        resp = self._api.archiveBlueprint(data='', blueprint=self.model['name'], repository=self._repository.model['name'], headers=None)
        return resp

    def restore(self):
        """
        Restore an archived blueprint

        Args: none

        Returns: HTTP response object
        """
        resp = self._api.restoreBlueprint(data='', blueprint=self.model['name'], repository=self._repository.model['name'], headers=None)
        return resp

    def __repr__(self):
        return "blueprint: %s" % (self.model["name"])

    __str__ = __repr__
