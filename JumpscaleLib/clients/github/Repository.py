from Jumpscale import j
from .Issue import Issue
from .Base import replacelabels
import copy
import base64
import threading
# import collections
import urllib
from .Milestone import RepoMilestone
from Jumpscale.errorhandling.JSExceptions import Input
from github.GithubException import UnknownObjectException

JSBASE = j.application.JSBaseClass


class GithubRepo(JSBASE):
    TYPES = ["story", "ticket", "task", "bug",
             "feature", "question", "monitor", "unknown"]
    PRIORITIES = ["critical", "urgent", "normal", "minor"]

    STATES = ["new", "accepted", "question",
              "inprogress", "verification", "closed"]

    def __init__(self, client, fullname):
        JSBASE.__init__(self)
        self.client = client
        self.fullname = fullname
        self._repoclient = None
        self._labels = None
        self._issues = None
        self._lock = threading.RLock()
        self._milestones = None

    @property
    def api(self):
        if self._repoclient is None:
            self._repoclient = self.client.api.get_repo(self.fullname)
        return self._repoclient

    @property
    def name(self):
        return self.fullname.split("/", 1)[-1]

    @property
    def type(self):
        if self.name in ["home"]:
            return "home"
        elif self.name.startswith("proj"):
            return "proj"
        elif self.name.startswith("org_"):
            return "org"
        elif self.name.startswith("www"):
            return "www"
        elif self.name.startswith("doc"):
            return "doc"
        elif self.name.startswith("cockpit"):
            return "cockpit"
        else:
            return "code"

    @property
    def labelnames(self):
        return [item.name for item in self.labels]

    @property
    def labels(self):
        with self._lock:
            if self._labels is None:
                self._labels = [item for item in self.api.get_labels()]

        return self._labels

    @property
    def stories(self):
        # walk overall issues find the stories (based on type)
        # only for home type repo, otherwise return []
        return self.issues_by_type('story')

    @property
    def tasks(self):
        # walk overall issues find the stories (based on type)
        # only for home type repo, otherwise return []
        return self.issues_by_type('task')

    def labelsSet(self, labels2set, ignoreDelete=["p_"], delete=True):
        """
        @param ignore all labels starting with ignore will not be deleted
        """

        for item in labels2set:
            if not j.data.types.string.check(item):
                raise j.exceptions.Input(
                    "Labels to set need to be in string format, found:%s" %
                    labels2set)

        # walk over github existing labels
        labelstowalk = copy.copy(self.labels)
        for item in labelstowalk:
            name = item.name.lower()
            if name not in labels2set:
                # label in repo does not correspond to label we need
                if name in replacelabels:
                    nameNew = replacelabels[item.name.lower()]
                    if nameNew not in self.labelnames:
                        color = self.getColor(name)
                        self.logger.info(
                            "change label in repo: %s oldlabel:'%s' to:'%s' color:%s" %
                            (self.fullname, item.name, nameNew, color))
                        item.edit(nameNew, color)
                        self._labels = None
                else:
                    # no replacement
                    name = 'type_unknown'
                    color = self.getColor(name)
                    try:
                        item.edit(name, color)
                    except BaseException:
                        item.delete()
                    self._labels = None

        # walk over new labels we need to set
        for name in labels2set:
            if name not in self.labelnames:
                # does not exist yet in repo
                color = self.getColor(name)
                self.logger.info(
                    "create label: %s %s %s" %
                    (self.fullname, name, color))
                self.api.create_label(name, color)
                self._labels = None

        name = ""

        if delete:
            labelstowalk = copy.copy(self.labels)
            for item in labelstowalk:
                if item.name not in labels2set:
                    self.logger.info("delete label: %s %s" %
                                     (self.fullname, item.name))
                    ignoreDeleteDo = False
                    for filteritem in ignoreDelete:
                        if item.name.startswith(filteritem):
                            ignoreDeleteDo = True
                    if ignoreDeleteDo is False:
                        item.delete()
                    self._labels = None

        # check the colors
        labelstowalk = copy.copy(self.labels)
        for item in labelstowalk:
            # we recognise the label
            self.logger.info(
                "check color of repo:%s labelname:'%s'" %
                (self.fullname, item.name))
            color = self.getColor(item.name)
            if item.color != color:
                self.logger.info(
                    "change label color for repo %s %s" %
                    (item.name, color))
                item.edit(item.name, color)
                self._labels = None

    def getLabel(self, name):
        for item in self.labels:
            self.logger.info("%s:look for name:'%s'" % (item.name, name))
            if item.name == name:
                return item
        raise j.exceptions.Input("Dit not find label: '%s'" % name)

    def getIssueFromMarkdown(self, issueNumber, markdown):
        i = self.getIssue(issueNumber, False)
        i._loadMD(markdown)
        self.issues.append(i)
        return i

    def getIssue(self, issueNumber, die=True):
        for issue in self.issues:
            if issue.number == issueNumber:
                return issue
        # not found in cache, try to load from github
        github_issue = self.api.get_issue(issueNumber)

        if github_issue:
            issue = Issue(repo=self, githubObj=github_issue)
            self._issues.append(issue)
            return issue

        if die:
            raise j.exceptions.Input(
                "cannot find issue:%s in repo:%s" % (issueNumber, self))
        else:
            i = Issue(self)
            i._ddict["number"] = issueNumber
            return i

    def issues_by_type(self, *types):
        """
        filter is method which takes  issue as argument and returns True or False to include
        """
        issues = []
        for issue in self.issues:
            if issue.type in types:
                issues.append(issue)

        return issues

    def issues_by_state(self, filter=None):
        """
        filter is method which takes  issue as argument and returns True or False to include
        """
        res = {}
        for item in self.states:
            res[item] = []
            for issue in self.issues:
                if issue.state == item:
                    if filter is None or filter(issue):
                        res[item].append(issue)
        return res

    def issues_by_priority(self, filter=None):
        """
        filter is method which takes  issue as argument and returns True or False to include
        """
        res = {}
        for item in self.priorities:
            res[item] = []
            for issue in self.issues:
                if issue.priority == item:
                    if filter is None or filter(issue):
                        res[item].append(issue)
        return res

    def issues_by_type_state(self, filter=None, collapsepriority=True):
        """
        filter is method which takes  issue as argument and returns True or False to include
        returns dict of dict keys: type, state and then issues sorted following priority
        """
        res = {}
        for type in self.types:
            res[type] = {}
            for state in self.states:
                res[type][state] = {}
                for priority in self.priorities:
                    res[type][state][priority] = []
                    for issue in self.issues:
                        if issue.type == type and issue.state == state:
                            if filter is None or filter(issue):
                                res[type][state][priority].append(issue)
                if collapsepriority:
                    # sort the issues following priority
                    temp = res[type][state]
                    res[type][state] = []
                    for priority in self.priorities:
                        for subitem in temp[priority]:
                            res[type][state].append(subitem)
        return res

    @property
    def types(self):
        return GithubRepo.TYPES

    @property
    def priorities(self):
        return GithubRepo.PRIORITIES

    @property
    def states(self):
        return GithubRepo.STATES

    @property
    def milestones(self):
        if self._milestones is None:
            self._milestones = [RepoMilestone(self, x)
                                for x in self.api.get_milestones()]

        return self._milestones

    @property
    def milestoneTitles(self):
        return [item.title for item in self.milestones]

    @property
    def milestoneNames(self):
        return [item.name for item in self.milestones]

    def getMilestone(self, name, die=True):
        name = name.strip()
        if name == "":
            raise j.exceptions.Input("Name cannot be empty.")
        for item in self.milestones:
            if name == item.name.strip() or name == item.title.strip():
                return item
        if die:
            raise j.exceptions.Input(
                "Could not find milestone with name:%s" % name)
        else:
            return None

    def createMilestone(self, name, title, description="", deadline="", owner=""):
        self.logger.debug(
            'Attempt to create milestone "%s" [%s] deadline %s' % (name, title, deadline))

        def getBody(descr, name, owner):
            out = "%s\n\n" % descr
            out += "## name:%s\n" % name
            out += "## owner:%s\n" % owner
            return out

        ms = None
        for s in [name, title]:
            ms = self.getMilestone(s, die=False)
            if ms is not None:
                break

        if ms is not None:
            if ms.title != title:
                ms.title = title
            # if ms.deadline != deadline:
            #     ms.deadline = deadline
            tocheck = getBody(description.strip(), name, owner)
            if ms.body.strip() != tocheck.strip():
                ms.body = tocheck
        else:
            due = j.data.time.epoch2pythonDateTime(
                int(j.data.time.getEpochFuture(deadline)))
            self.logger.info("Create milestone on %s: %s" % (self, title))
            body = getBody(description.strip(), name, owner)
            # workaround for https://github.com/PyGithub/PyGithub/issues/396
            milestone = self.api.create_milestone(
                title=title, description=body)
            milestone.edit(title=title, due_on=due)

            self._milestones.append(RepoMilestone(self, milestone))

    def deleteMilestone(self, name):
        if name.strip() == "":
            raise j.exceptions.Input("Name cannot be empty.")
        self.logger.info("Delete milestone on %s: '%s'" % (self, name))
        try:
            ms = self.getMilestone(name)
            ms.api.delete()
            self._milestones = []
        except Input:
            self.logger.info(
                "Milestone '%s' doesn't exist. no need to delete" % name)

    def _labelSubset(self, cat):
        res = []
        for item in self.labels:
            if item.startswith(cat):
                item = item[len(cat):].strip("_")
                res.append(item)
        res.sort()
        return res

    def getColor(self, name):

        # colors={'state_question':'fbca04',
        #  'priority_urgent':'d93f0b',
        #  'state_verification':'006b75',
        #  'priority_minor':'',
        #  'type_task':'',
        #  'type_feature':'',
        #  'process_wontfix':"ffffff",
        #  'priority_critical':"b60205",
        #  'state_inprogress':"e6e6e6",
        #  'priority_normal':"e6e6e6",
        #  'type_story':"ee9a00",
        #  'process_duplicate':"",
        #  'state_closed':"5319e7",
        #  'type_bug':"fc2929",
        #  'state_accepted':"0e8a16",
        #  'type_question':"fbca04",
        #  'state_new':"1d76db"}

        if name.startswith("state"):
            return("c2e0c6")  # light green

        if name.startswith("process"):
            return("d4c5f9")  # light purple

        if name.startswith("type"):
            return("fef2c0")  # light yellow

        if name in ("priority_critical", "task_no_estimation"):
            return("b60205")  # red

        if name.startswith("priority_urgent"):
            return("d93f0b")

        if name.startswith("priority"):
            return("f9d0c4")  # roze

        return "ffffff"

    def set_file(self, path, content, message='update file'):
        """
        Creates or updates the file content at path with given content
        :param path: file path `README.md`
        :param content: Plain content of file
        :return:
        """
        bytes = content.encode()
        encoded = base64.encodebytes(bytes)

        params = {
            'message': message,
            'content': encoded.decode(),
        }

        path = urllib.parse.quote(path)
        try:
            obj = self.api.get_contents(path)
            params['sha'] = obj.sha
            if base64.decodebytes(obj.content.encode()) == bytes:
                return
        except UnknownObjectException:
            pass

        self.logger.debug('Updating file "%s"' % path)
        self.api._requester.requestJsonAndCheck(
            'PUT',
            self.api.url + '/contents/' + path,
            input=params,
        )

    @property
    def issues(self):
        with self._lock:
            if self._issues is None:
                issues = []
                for item in self.api.get_issues(state='all'):
                    issues.append(Issue(self, githubObj=item))

                self._issues = issues

        return self._issues

    def serialize2Markdown(self, path):

        md = j.data.markdown.getDocument()
        md.addMDHeader(1, "Issues")

        res = self.issues_by_type_state()

        for type in self.types:
            typeheader = False
            for state in self.states:
                issues = res[type][state]
                stateheader = False
                for issue in issues:
                    if typeheader is False:
                        md.addMDHeader(2, "Type:%s" % type)
                        typeheader = True
                    if stateheader is False:
                        md.addMDHeader(3, "State:%s" % state)
                        stateheader = True
                    md.addMDBlock(str(issue.getMarkdown()))

        j.sal.fs.writeFile(path, str(md))

    def __str__(self):
        return "gitrepo:%s" % self.fullname

    __repr__ = __str__
