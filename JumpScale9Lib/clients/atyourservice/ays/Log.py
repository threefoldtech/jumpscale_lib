class Logs:
    def __init__(self, job):
        self._job = job

    def list(self):
        """
        List all logs.

        Returns: list of logs
        """
        
        logs = list()

        if len(self._job.model['logs']) > 0:
            for log in self._job.model['logs']:
                logs.append(Log(self._job, log))
        return logs

class Log:
    def __init__(self, job, model):
        self._job = job
        self.model = model

    def __repr__(self):
        return "%s" % (self.model)

    __str__ = __repr__