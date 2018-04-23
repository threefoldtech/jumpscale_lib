import gevent

from .Task import Task
from .Story import Story
from .utils import _parse_body, _repoowner_reponame, _index_story

from js9 import j

class GiteaBot:
    """Gitea specific bot for Storybot
    """

    LABEL_STORY = "type_story"

    def __init__(self, token=None, api_url="", base_url = "", repos=None):
        """GiteaBot constructor
        
        Keyword Arguments:
            token str -- Gitea API token (default: None)
            url str -- gitea API url
            repos list -- List of repos the GiteaBot should watch (can be `username/repo` or 
                `repo` that will be assumed to be the user's own repo) (default: [])

        Raises:
            ValueError -- if token was not provided
            ValueError -- if url was not provided
        """
        data = {}
        if not token:
            raise ValueError("Token was not provided and is mandatory")
        data["gitea_token_"] = token

        if api_url == "":
            raise ValueError("api url was not provided and is mandatory")
        data["url"] = api_url

        self.client = j.clients.gitea.get(data=data, interactive=False)
        self.username = self.client.api.user.userGetCurrent()[0].login
        self.api_url = api_url
        self.base_url = base_url
        self.repos = repos
        self.logger = j.logger.get("j.tools.StoryBot")

    def get_stories(self):
        """Loop over all provided repos return a list of stories found in the issues

        Returns:
            [Story] -- A list of stories (Story) on the provided Gitea repos
        """
        self.logger.info("Checking for stories on gitea...")
        stories = []

        if not self.repos:
            self.logger.info("No repos provided to the Gitea bot")
            return stories

        gls = []
        for repo in self.repos:
            gls.append(gevent.spawn(self._get_story_repo, repo))

        gevent.joinall(gls)
        for gl in gls:
            stories.extend(gl.value)

        self.logger.info("Done checking for stories on Gitea!")
        return stories
    
    def _get_story_repo(self, repo):
        """Get stories from a single repo
        
        Arguments:
            repo str -- Name of Gitea repo
        
        Returns:
            [Story] -- List of stories (Story) found in repo
        """
        self.logger.debug("checking repo '%s'" % repo)
        stories = []

        repoowner, reponame = _repoowner_reponame(repo, self.username)

        issues = self.client.api.repos.issueListIssues(reponame, repoowner, query_params={"state":"all"})[0]
        for iss in issues:
            html_url = self._parse_html_url(repoowner,reponame,iss.number)

            self.logger.debug("checking issue '%s'" % html_url)
            # not a story if no type story label
            if not self.LABEL_STORY in [label.name for label in iss.labels]:
                continue
            # check title format
            title = iss.title
            if title[-1:] == ")":
                start_i = title.rfind("(")
                if start_i == -1:
                    self.logger.error("issue title of %s has a closeing bracket, but no opening bracket", html_url)
                    continue
                story_title = title[start_i + 1:-1]
                story_desc = title[:start_i].strip()
                stories.append(Story(
                    title=story_title,
                    url=html_url,
                    description=story_desc,
                    state=iss.state,
                    update_list_func=self._story_update_func(iss, reponame, repoowner),
                    body=iss.body
                ))

        return stories

    def link_issues_to_stories(self, stories=None):
        """Loop over all provided repos and see if there are any issues related to provided stories.
        Link them if so.

        Keyword Arguments:
            stories [Story] -- List of stories (default: None)
        """
        self.logger.info("Linking tasks on Gitea to stories...")

        if not stories:
            self.logger.info("No stories provided to link Gitea issues with")
            return
        if not self.repos:
            self.logger.info("No repos provided to the Gitea bot")
            return

        gls = []
        for repo in self.repos:
            gls.append(gevent.spawn(self._link_issues_stories_repo, repo, stories))

        gevent.joinall(gls)

        self.logger.info("Done linking tasks on Gitea to stories!")    
    
    def _link_issues_stories_repo(self, repo, stories):
        """links issues from a single repo with stories

        Arguments:
            repo str -- Name of Gitea repo
            stories [Story] --List of stories (Story) to link with
        """
        self.logger.debug("checking repo '%s'" % repo)
        repoowner, reponame = _repoowner_reponame(repo, self.username)

        issues = self.client.api.repos.issueListIssues(reponame, repoowner, query_params={"state":"all"})[0]
        for iss in issues:
            title = iss.title
            html_url = self._parse_html_url(repoowner, reponame, iss.number)

            self.logger.debug("checking issue: %s" % html_url)
            end_i = title.find(":")
            if end_i == -1:
                self.logger.debug("issue is not a story task")
                continue
            found_titles = [item.strip() for item in title[:end_i].split(",")]
            data = {}
            data["body"] = iss.body
            for story_title in found_titles:
                story_i = _index_story(stories, story_title)
                story = stories[story_i]
                if story_i == -1:
                    self.logger.debug("Story title was not in story list")
                    continue
                # update task body
                self.logger.debug("Parsing task issue body")
                try:
                    data["body"] = _parse_body(data["body"], story)
                except RuntimeError as err:
                    self.logger.error("Something went wrong parsing body for %s:\n%s" % (html_url, err))
                    continue
                self.client.api.repos.issueEditIssue(data, str(iss.number), reponame, repoowner)

                # update story with task
                self.logger.debug("Parsing story issue body")
                desc = title[end_i +1 :].strip()
                task = Task(html_url, desc, iss.state)
                try:
                    story.update_list(task)
                except RuntimeError as err:
                    self.logger.error("Something went wrong parsing body for %s:\n%s" % (task.url, err))
                    continue

    def _story_update_func(self, issue, repo, owner):
        """returns iss updating function
        
        Arguments:
            issue JumpScale9Lib.clients.gitea.client.Issue.Issue -- Gitea Issue

        Returns:
            func(Task) -- A function that accepts a task (Task) to update the task list with
        """

        def updater(body, task):
            """Updates issue with provided task and body
            Returns updated body
            
            Arguments:
                body Str -- body to update and write to the issue
                task Task -- Task to update the body with

            Returns:
                str -- updated body
            """
            data = {}
            data["body"] = _parse_body(body, task)
            self.client.api.repos.issueEditIssue(data, str(issue.number), repo, owner)

            return data["body"]
        
        return updater

    def _parse_html_url(self, owner, repo, iss_number):
        """Tries to parse a html page url for a Gitea issue
        
        Arguments:
            issue JumpScale9Lib.clients.gitea.client.Issue.Issue -- Gitea Issue
            owner str -- repo owner
            repo str -- repo name
            iss_number int/str -- issue number of repo
        """
        url = self.base_url
        if url == "":
            self.logger("Gitea base url not found, trying to parse it from api url")
            url = self.api_url
            if url.endswith("/"):
                url = url[:-1]
            if url.endswith("/api/v1"):
                url = url[:-7]
            url = url.replace("api.","")

            self.base_url = url
        
        if url.endswith("/"):
            url = url[:-1]
        
        url += "/%s/%s/issues/%s" % (owner, repo, str(iss_number))

        return url
