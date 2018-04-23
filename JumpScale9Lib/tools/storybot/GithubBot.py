import gevent

from .Task import Task
from .Story import Story
from .utils import _index_story, _parse_body, _repoowner_reponame

from js9 import j

class GithubBot:
    """Github specific bot for Storybot
    """

    def __init__(self, token=None, repos=None):
        """Github bot constructor
        
        Keyword Arguments:
            token string -- github API token (default: None)
            repos list -- List of repos the githubbot should watch (can be `username/repo` or 
                `repo` that will be assumed to be the user's own repo) (default: [])

        Raises:
            ValueError -- if token was not provided
        """
        data = {}
        if not token:
            raise ValueError("Token was not provided and is mandatory")

        data["token_"] = token
        self.client = j.clients.github.get(data=data, interactive=False)
        self.username = self.client.api.get_user().login
        self.repos = repos
        self.logger = j.logger.get("j.tools.StoryBot")

    def get_stories(self):
        """Loop over all provided repos return a list of stories found in the issues

        Returns:
            [Story] -- A list of stories (Story) on the provided github repos
        """
        self.logger.info("Checking for stories on github...")
        stories = []

        if not self.repos:
            self.logger.info("No repos provided to the Github bot")
            return stories

        gls = []
        for repo in self.repos:
            gls.append(gevent.spawn(self._get_story_repo, repo))

        gevent.joinall(gls)
        for gl in gls:
            stories.extend(gl.value)

        self.logger.info("Done checking for stories on github!")
        return stories

    def _get_story_repo(self, repo):
        """Get stories from a single repo
        
        Arguments:
            repo str -- Name of Github repo
        
        Returns:
            [Story] -- List of stories (Story) found in repo
        """

        stories = []

        self.logger.debug("checking repo '%s'" % repo)
        repoowner, reponame = _repoowner_reponame(repo, self.username)

        # get issues
        repo = self.client.api.get_user(repoowner).get_repo(reponame)
        issues = repo.get_issues(state="all")
        # loop issue pages
        i = 0
        while True:
            page = issues.get_page(i)
            self.logger.debug("Issue page: %s" % i)
            if len(page) == 0:
                self.logger.debug("page %s is empty" % i)                    
                break
            i += 1

            for iss in page:
                self.logger.debug("checking issue '%s'" % iss.html_url)
                # check if story. Should labels also be checked for 'type_story'?
                title = iss.title
                if title[-1:] == ")":
                    # get story title
                    start_i = title.rfind("(")
                    if start_i == -1:
                        self.logger.error("issue title of %s has a closeing bracket, but no opening bracket", iss.html_url)
                        continue
                    story_title = title[start_i + 1:-1]
                    story_desc = title[:start_i].strip()
                    stories.append(Story(
                        title=story_title,
                        url=iss.html_url,
                        description=story_desc,
                        state=iss.state,
                        update_list_func=self._story_update_func(iss),
                        body=iss.body,
                    ))

        return stories


    def link_issues_to_stories(self, stories=None):
        """Loop over all provided repos and see if there are any issues related to provided stories.
        Link them if so.

        Keyword Arguments:
            stories [Story] -- List of stories (default: None)
        """
        self.logger.info("Linking tasks on github to stories...")

        if not stories:
            self.logger.info("No stories provided to link Github issues with")
            return
        if not self.repos:
            self.logger.info("No repos provided to the Github bot")
            return

        gls = []
        for repo in self.repos:
            gls.append(gevent.spawn(self._link_issues_stories_repo, repo, stories))

        gevent.joinall(gls)

        self.logger.info("Done linking tasks on github to stories!")

    def _link_issues_stories_repo(self, repo, stories):
        """links issues from a single repo with stories

        Arguments:
            repo str -- Name of Github repo
            stories [Story] --List of stories (Story) to link with
        """
        self.logger.debug("Repo: %s" % repo)
        repoowner, reponame = _repoowner_reponame(repo, self.username)

        # get issues
        repo = self.client.api.get_user(repoowner).get_repo(reponame)
        issues = repo.get_issues(state="all")
        # loop issue pages
        i = 0
        while True:
            page = issues.get_page(i)
            self.logger.debug("Issue page: %s" % i)
            if len(page) == 0:
                self.logger.debug("page %s is empty" % i)
                break
            i+=1

            for iss in page:
                title = iss.title
                self.logger.debug("Issue: %s" % title)
                end_i = title.find(":")
                if end_i == -1:
                    self.logger.debug("issue is not a story task")
                    continue
                found_titles = [item.strip() for item in title[:end_i].split(",")]
                body = iss.body
                for story_title in found_titles:
                    story_i = _index_story(stories, story_title)
                    story = stories[story_i]
                    if story_i == -1:
                        self.logger.debug("Story title was not in story list")
                        continue
                    # update task body
                    self.logger.debug("Parsing task issue body")
                    try:
                        body = _parse_body(body, story)
                    except RuntimeError as err:
                        self.logger.error("Something went wrong parsing body for %s:\n%s" % (iss.html_url, err))
                        continue
                    iss.edit(body=body)

                    # update story with task
                    self.logger.debug("Parsing story issue body")
                    desc = title[end_i +1 :].strip()
                    task = Task(iss.html_url, desc, iss.state)
                    try:
                        story.update_list(task)
                    except RuntimeError as err:
                        self.logger.error("Something went wrong parsing body for %s:\n%s" % (task.url, err))
                        continue

    def _story_update_func(self, issue):
        """Returns a function that can update the task list of a story issue
        
        Arguments:
            issue github.Issue.Issue -- Github issue
        
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

            body = _parse_body(body, task)
            issue.edit(body=body)

            return body
        
        return updater
