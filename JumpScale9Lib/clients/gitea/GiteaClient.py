from js9 import j

from datetime import datetime
import calendar

from JumpScale9Lib.clients.gitea.generated.client.client import Client

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


TEMPLATE = """
url = ""
gitea_token_ = ""
"""

JSConfigBase = j.tools.configmanager.base_class_config


class GiteaClient(JSConfigBase):

    def __init__(self, instance, data={}, parent=None):
        JSConfigBase.__init__(self, instance=instance,
                              data=data, parent=parent)
        self._config = j.tools.configmanager._get_for_obj(
            self, instance=instance, data=data, template=TEMPLATE)

        if self.config.data["url"] == "" or self.config.data["gitea_token_"] == "":
            self.config.configure()

        if self.config.data["url"] == "" or self.config.data["gitea_token_"] == "":
            raise RuntimeError("url and gitea_token_ are not properly configured")

        base_uri = self.config.data["url"]
        if "/api" not in base_uri:
            base_uri += "/api/v1"

        # TODO:*1 need to do more checks that url is properly formated

        self.client = Client(base_uri=base_uri)

        self.client.set_auth_header('token {}'.format(self.config.data["gitea_token_"]))

    def addLabelsToRepos(self, repos, labels=default_labels):
        """
        Add multiple labels to multiple repos.
        If a label with the same name exists on a repo, it won't be added.

        :param repos: a list of repos ex: [{'owner': 'jumpscale', 'name':'core9'}]
        :param labels: a list of labels  ex: [{'color': '#fef2c0', 'name': 'state_blocked'}]
        :return:
        """
        for repo in repos:
            repo_labels = self.client.repos.issueListLabels(
                repo['name'], repo['owner']).data
            # @TODO: change the way we check on label name when this is fixed https://github.com/Jumpscale/go-raml/issues/396
            names = [l['name'] for l in repo_labels]
            for label in labels:
                if label['name'] in names:
                    continue
                self.client.repos.issueCreateLabel(
                    label, repo['name'], repo['owner'])

    def addMileStonesToRepos(self, repos, milestones=None):
        """
        Add multiple milestones to multiple repos.
        If a milestone with the same title exists on a repo, it won't be added.
        If no milestones are supplied, the default milestones for the current quarter will be added.

        :param repos: a list of repos ex: [{'owner': 'jumpscale', 'name':'core9'}]
        :param milestones: a list of milestones ex: {'title': 'Q1', 'due_on': '2018-03-31T00:00:00Z'}
        :return:
        """
        if not milestones:
            milestones = self.getDefaultMilestones()
        for repo in repos:
            repo_milestones = self.client.repos.issueGetMilestones(
                repo['name'], repo['owner']).data
            # @TODO: change the way we check on milestone title when this is fixed https://github.com/Jumpscale/go-raml/issues/396
            names = [m['title'] for m in repo_milestones]
            for milestone in milestones:
                if milestone['title'] in names:
                    continue
                self.client.repos.issueCreateMilestone(
                    milestone, repo['name'], repo['owner'])

    def getDefaultMilestones(self):
        today = datetime.today()
        quarter = (today.month-1)//3 + 1
        return self.generateQuarterMilestones(quarter, today.year)

    def generateQuarterMilestones(self, quarter, year):
        """
        Generate milestones for a certain quarter of year
        :param quarter: quarter number. Must be between 1-4
        :param year:
        :return: list of milestones
        """
        quarters = {
            1: [1, 2, 3],
            2: [4, 5, 6],
            3: [7, 8, 9],
            4: [10, 11, 12],
        }

        if quarter not in quarters.keys():
            raise RuntimeError('Invalid value for quarter.')

        milestones = []

        # Set the begining of the week to Sunday
        c = calendar.Calendar(calendar.SUNDAY)

        # Add weekly milestones
        for month in quarters[quarter]:
            month_name = calendar.month_name[month].lower()[0:3]
            weeks = c.monthdayscalendar(year, month)

            for i, week in enumerate(weeks):
                # check if this week has a value for Saturday
                day = week[6]
                if day:
                    title = '%s_w%s' % (month_name, i + 1)
                    due_on = '%s-%s-%sT23:59:99Z' % (year, str(month).zfill(2), str(day).zfill(2))
                    milestones.append({'title': title, 'due_on': due_on})

        # Add quarter milestone
        quarter_month = quarters[quarter][-1]
        title = 'Q%s' % quarter
        last_day = calendar.monthrange(year, quarter_month)[1]
        due_on = '%s-%s-%sT23:59:99Z' % (year, str(quarter_month).zfill(2), last_day)
        milestones.append({'title': title, 'due_on': due_on})

        return milestones
