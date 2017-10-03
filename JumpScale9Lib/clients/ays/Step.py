from .Job import Jobs

class Steps:
    def __init__(self, run):
        self._run = run

    def list(self):
        """
        List all steps.

        Returns: list of steps
        """
        steps = list()
        for step in self._run.model['steps']:
            steps.append(Step(self._run, step))
        return steps

    def get(self, number):
        """
        Get a step by its number.

        Args:
            number: number of the step

        Raises: ValueError if no step with given number could be found

        Returns: step with given number
        """
        for step in self.list():
            if step.model['number'] == number:
                return step
        raise ValueError("Could not find step with number {}".format(number))

class Step:
    def __init__(self, run, model):
        self._run = run
        self.model = model
        self.jobs = Jobs(self)

    def __repr__(self):
        return "step number %s" % (self.model["number"])

    __str__ = __repr__
