from js9 import j
from requests.exceptions import HTTPError

def _extract_error(resp):
    if isinstance(resp, HTTPError):
        if resp.response.headers['Content-type'] == 'application/json':
            content = resp.response.json()
            return content.get('error', resp.response.text)
        return resp.response.text
    raise resp

class Runs:
    def __init__(self, repository):
        self._repository = repository
        self._api = repository._api

    def list(self):
        """
        List all runs (keys) sorted by creation date.
        """
        try:
            resp = self._api.listRuns(self._repository.model['name'])
        except Exception as e:
            print("Error during listing of the runs: {}".format(_extract_error(e)))
            return

        ays_runs = resp.json()
        ays_runs = sorted(ays_runs, key=lambda x: x['epoch'])

        runs = list()
        for run in ays_runs:
            runs.append(Run(self._repository, run))
        return runs

    def create(self, callback=None, yes=False):
        """
        Look for all actions with a state 'scheduled', 'changed' or 'error' and create a run.
        A run is an collection of actions that will be run on the repository.
        """
        try:
            resp = self._api.createRun(data=None, repository=self._repository.model["name"], query_params={'simulate': True, 'callback_url': callback})
        except Exception as e:
            print("error during execution of the run: {}".format(_extract_error(e)))
            return

        run = resp.json()
        if len(run['steps']) <= 0:
            print("Nothing to do.")
            return

        if yes == False:
            resp = j.tools.console.askYesNo('Do you want to execute this run ?', True)
            if resp is False:
                runid = run['key']
                self._api.deleteRun(runid=runid, repository=self._repository.model["name"])
                return

        try:
            resp = self._api.executeRun(data=None, runid=run['key'], repository=self._repository.model["name"])
        except Exception as e:
            print("error during execution of the run: {}".format(_extract_error(e)))
            return

        print("execution of the run started: {}".format(run['key']))
        return run['key']

    def get(self, key):
        """
        Get a run.
        """
        for run in self.list():
            if run.model.get('key') == key:
                return run
        raise ValueError("Could not find run with key {}".format(key))

class Run:
    def __init__(self, repository, model):
        self._repository = repository
        self.model = model

    def show(self, logs=False):
        """
        Show details of a run.
        If logs is true, also show the logs of each job.
        """
        try:
            resp = ayscl.api.ays.getRun(runid=self.model["key"], repository=self._repository.model["name"])
        except Exception as e:
            print("Error during retreive of the run {}: {}".format(key, _extract_error(e)))
            return

        #TODO: what about the logs

        run = resp.json()
        return run

    def __repr__(self):
        return "run: %s" % (self.model["key"])

    __str__ = __repr__
