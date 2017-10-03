from requests.exceptions import HTTPError

def _extract_error(resp):
    if isinstance(resp, HTTPError):
        if resp.response.headers['Content-type'] == 'application/json':
            content = resp.response.json()
            return content.get('error', resp.response.text)
        return resp.response.text
    raise resp
    
class Jobs:
    def __init__(self, step):
        self._step = step
        self._repository = step._run._repository
        self._ayscl = step._run._ayscl

        # TODO
        # Allow step=None and add filters for showing jobs per actor, repo, service, action, ...

    def list(self):
        """
        List all jobs of a step.

        Return: list of jobs
        """
        jobs = list()
        for job in self._step.model['jobs']:
            import ipdb;ipdb.set_trace()
            try:
                ays_job = self._ayscl.getJob(job['key'], self._repository.model['name'])
            except Exception as e:
                return _extract_error(e)   
            jobs.append(Job(self._step, job))
        return jobs

    def get(self, key):
        """
        Get a job by its key.

        Args:
            key: id of the job

        Raises: ValueError if no job with given key could be found

        Returns: job with given key
        """
        for job in self.list():
            if job.model['key'] == key:
                return job
        raise ValueError("Could not find job with key {}".format(key))

class Job:
    def __init__(self, step, model):
        self._step = step
        self.model = model

    def __repr__(self):
        return "Actor: %s, Service: %s, Action %s" % (self.model["actor_name"], self.model["service_name"], self.model["action_name"])

    __str__ = __repr__