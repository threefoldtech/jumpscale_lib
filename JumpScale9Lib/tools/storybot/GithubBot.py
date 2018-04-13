from .Task import Task
from .Story import Story
from .utils import _index_story, _parse_body, _repoowner_reponame

from js9 import j

class GithubBot():
    """Github specific bot for Storybot
    """

    def __init__(self, token=None, repos=[]):
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

        data["token_"]=token
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
        for repo in self.repos:
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
                            update_list_func=self._story_update_func(iss)))

        self.logger.info("Done checking for stories on github!")
        return stories

    def link_issues_to_stories(self, stories=[]):
        """Loop over all provided repos and see if there are any issues related to provided stories.
        Link them if so.

        Keyword Arguments:
            stories [Story] -- List of stories (default: {[]})
        """
        self.logger.info("Linking tasks on github to stories...")
        for repo in self.repos:
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
                    story_title = title[:end_i]
                    story_i = _index_story(stories, story_title)
                    story = stories[story_i]
                    if story_i == -1:
                        self.logger.debug("Story title was not in story list")
                        continue
                    # update task body
                    self.logger.debug("Updating task issue body")
                    new_iss_body = _parse_body(iss.body, story)
                    iss.edit(body=new_iss_body)

                    # update story with task
                    self.logger.debug("Updating story issue body")
                    desc = title[end_i +1 :].strip()
                    task = Task(iss.html_url, desc, iss.state)
                    story.update_list(task)
        
        self.logger.info("Done linking tasks on github to stories!")

    def _story_update_func(self, issue):
        """Returns a function that can update the task list of a story issue
        
        Arguments:
            issue github.Issue.Issue -- Github issue
        
        Returns:
            func(Task) -- A function that accepts a task (Task) to update the task list with
        """
        def updater(task):
            new_body = _parse_body(issue.body, task)
            issue.edit(body=new_body)
        
        return updater
