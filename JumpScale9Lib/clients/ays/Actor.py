class Actors:
    def __init__(self, repository):
        self._repository = repository
        self._ayscl = repository._ayscl

    def list(self):
        """
        List all actors.

        Args: none

        Returns:
            list of actors
        """
        ays_actors = self._ayscl.listActors(self._repository.model['name']).json()
        actors = list()
        for actor in sorted(ays_actors, key=lambda actor: actor['name']):
            actors.append(Actor(self._repository, actor))
        return actors

    def get(self, name):
        """
        Get the actor with a given name.

        Args:
            name: name of the actor.

        Returns:
            actor instance

        Raises:
            KeyError if actor with given name was not found.
        """
        for actor in self.list():
            if actor.model['name'] == name:
                return actor
        raise KeyError("Could not find actor with name {}".format(name))

    def update(self, name=None, reschedule=False):
        """
        Update all actors, or only the actor with a given name.

        Args:
            name: name of the actor to update
            reschedule (True/False): optionally reschedules all actions after the update which are in error state; default it False


        Returns: nothing

        Raises:
            KeyError if actor with given name was not found.
        """

        if name is not None:
            for actor in self.list():
                if actor.model['name'] == name:
                    actor.update(reschedule)
                    return
            raise KeyError("Could not find actor with name {}".format(name))

        for actor in self.list():
            actor.update(reschedule)


class Actor:
    def __init__(self, repository, model):
        self._repository = repository
        self._ayscl = repository._ayscl
        self.model = model

    def update(self, reschedule=False):
        """
        Update the actor

        Args:
            reschedule True/False): optionally reschedules the action after the update if it was in error state; default it False

        Returns: HTTP response object
        """
        query_params = {'reschedule': reschedule}
        resp = self._ayscl.updateActor(data='', actor=self.model['name'], repository=self._repository.model['name'], query_params=query_params)
        return resp

    def __repr__(self):
        return "actor: %s" % (self.model["name"])

    __str__ = __repr__