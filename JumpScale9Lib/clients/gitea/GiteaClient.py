from js9 import j

import calendar
from JumpScale9Lib.clients.gitea.generated.client import Client

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
    {'title': 'feb_w1', 'due_on': '2018-02-03T00:00:00Z'},
    {'title': 'feb_w2', 'due_on': '2018-02-10T00:00:00Z'},
    {'title': 'feb_w3', 'due_on': '2018-02-17T00:00:00Z'},
    {'title': 'feb_w4', 'due_on': '2018-02-24T00:00:00Z'},
    {'title': 'mar_w1', 'due_on': '2018-03-03T00:00:00Z'},
    {'title': 'mar_w2', 'due_on': '2018-03-10T00:00:00Z'},
    {'title': 'mar_w3', 'due_on': '2018-03-17T00:00:00Z'},
    {'title': 'mar_w3', 'due_on': '2018-03-24T00:00:00Z'},
    {'title': 'mar_w4', 'due_on': '2018-03-31T00:00:00Z'},
]



TEMPLATE = """
url = ""
secret_ = ""
"""

JSConfigBase = j.tools.configmanager.base_class_config
class GiteaClient(JSConfigBase):


    def __init__(self,instance,data={},parent=None):
        JSConfigBase.__init__(self,instance=instance,data=data,parent=parent)
        self._config = j.tools.configmanager._get_for_obj(self,instance=instance,data=data,template=TEMPLATE)

        if self.config.data["url"]=="":
            self.config.configure()

        base_uri=self.config.data["url"]
        if "/api" not in base_uri:    
            base_uri+="/api/v1"
        
        #TODO:*1 need to do more checks that url is properly formated

        self.client=Client(base_uri=base_uri)

        token = j.clients.itsyouonline.jwt #get it from itsyou.online

        self.client.set_auth_header('token {}'.format(token))        

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
                