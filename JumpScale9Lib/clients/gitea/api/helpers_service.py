default_labels = [
    {'color': '#e11d21', 'name': 'priority_critical'},
    {'color': '#f6c6c7', 'name': 'priority_major'},
    {'color': '#f6c6c7', 'name': 'priority_minor'},
    {'color': '#d4c5f9', 'name': 'process_duplicate'},
    {'color': '#d4c5f9', 'name': 'process_wontfix'},
    {'color': '#bfe5bf', 'name': 'state_inprogress'},
    {'color': '#bfe5bf', 'name': 'state_question'},
    {'color': '#bfe5bf', 'name': 'state_verification'},
    {'color': '#fef2c0', 'name': 'type_bug'},
    {'color': '#fef2c0', 'name': 'type_feature'},
    {'color': '#fef2c0', 'name': 'type_question'},
    {'color': '0000000', 'name': 'state_blocked'},
]

default_milestones = [
    {'title': 'Q1', 'due_on': '2018-03-31T00:00:00Z'},
    {'title': 'dec_w4', 'due_on': '2017-12-30T00:00:00Z'},
    {'title': 'jan_w1', 'due_on': '2018-01-06T00:00:00Z'},
    {'title': 'jan_w2', 'due_on': '2018-01-13T00:00:00Z'},
    {'title': 'jan_w3', 'due_on': '2018-01-20T00:00:00Z'},
    {'title': 'jan_w4', 'due_on': '2018-01-30T00:00:00Z'},
    {'title': 'feb_w2', 'due_on': '2018-02-10T00:00:00Z'},
]


class HelperService:
    """"
    This is a wrapper to extend some of the generated client functionality
    """
    def __init__(self, client):
        self.client = client

    def addLabelsToRepos(self, repos, labels=default_labels):
        """
        Add multiple labels to multiple repos.
        If a label with the same name exists on a repo, it won't be added.

        :param repos: a list of repos ex: [{'owner': 'jumpscale', 'name':'core9'}]
        :param labels: a list of labels  ex: [{'color': '#fef2c0', 'name': 'state_blocked'}]
        :return:
        """
        for repo in repos:
            repo_labels = self.client.repos.issueListLabels(repo['name'], repo['owner']).json()
            names = [l['name'] for l in repo_labels]
            for label in labels:
                if label['name'] in names:
                    continue
                self.client.repos.issueCreateLabel(label, repo['name'], repo['owner'])

    def addMileStonesToRepos(self, repos, milestones=default_milestones):
        """
        Add multiple milestones to multiple repos.
        If a milestone with the same title exists on a repo, it won't be added.

        :param repos: a list of repos ex: [{'owner': 'jumpscale', 'name':'core9'}]
        :param milestones: a list of milestones ex: {'title': 'Q1', 'due_on': '2018-03-31T00:00:00Z'}
        :return:
        """
        for repo in repos:
            repo_milestones = self.client.repos.issueGetMilestones(repo['name'], repo['owner']).json()
            names = [m['title'] for m in repo_milestones]
            for milestone in milestones:
                if milestone['title'] in names:
                    continue
                self.client.repos.issueCreateMilestone(milestone, repo['name'], repo['owner'])
