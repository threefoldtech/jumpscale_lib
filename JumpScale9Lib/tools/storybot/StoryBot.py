# Docs can be found at docs/tools/StoryBot.md

import time
import gevent
import signal

from .GithubBot import GithubBot
from .GiteaBot import GiteaBot

from js9 import j

TEMPLATE =  """
github_token_ = ""
github_repos = ""
gitea_api_url = "https://docs.greenitglobe.com/api/v1"
gitea_base_url = "https://docs.greenitglobe.com/"
gitea_token_ = ""
gitea_repos = ""
"""

JSConfigBase = j.tools.configmanager.base_class_config

class StoryBot(JSConfigBase):
    """
    Story bot will automaticall link story issues and task/bug/FR issues with each other.

    For more higher level information on the tool, check StoryBot.md
    """

    def __init__(self, instance, data=None, parent=None, interactive=False):
        """StoryBot constructor
        """
        JSConfigBase.__init__(self, instance=instance,
                                    data=data,
                                    parent=parent,
                                    template=TEMPLATE,
                                    interactive=interactive)

    @property
    def github_repos(self):
        """Returns the Github repositories as comma seperated string
        (Returned directly from config)
        
        Returns:
            str -- Comma seperated list of Github repositories
        """
        return self.config.data["github_repos"]

    @property
    def github_repos_list(self):
        """Returns the Github repositories as list

        Returns:
            [str] -- List of Github repositories
        """
        return [item.strip() for item in self.config.data["github_repos"].split(",")]
    
    def add_github_repos(self, repos=""):
        """Add new Github repositories to the configuration
        
        Keyword Arguments:
            repos str -- comma seperated string of repositories (default: "")
        """
        repos = repos.strip()
        if not repos.startswith(","):
            repos = "," + repos

        self.config.data["github_repos"] += repos

    def remove_github_repos(self, repos=""):
        """Remove Github repositories from the configuration
        
        Keyword Arguments:
            repos str -- comma seperated string of repositories (default: "")
        """
        repos_list = [x.strip() for x in repos.split(",")]
        new_list  = self.github_repos_list

        for repo_to_remove in repos_list:
            # loop till all items are removed, just to make sure doubles are removed
            while True:
                try:
                    new_list.remove(repo_to_remove)
                # this is thrown when item was no in list
                except ValueError:
                    break
        
        self.config.data["github_repos"] = ",".join(new_list)

    @property
    def gitea_repos(self):
        """Returns the Gitea repositories as comma seperated string
        (Returned directly from config)
        
        Returns:
            str -- Comma seperated list of Gitea repositories
        """
        return self.config.data["gitea_repos"]

    @property
    def gitea_repos_list(self):
        """Returns the Gitea repositories as list

        Returns:
            [str] -- List of Gitea repositories
        """
        return [item.strip() for item in self.config.data["gitea_repos"].split(",")]

    def add_gitea_repos(self, repos=""):
        """Add new Gitea repositories to the configuration
        
        Keyword Arguments:
            repos str -- comma seperated string of repositories (default: "")
        """
        repos = repos.strip()
        if not repos.startswith(","):
            repos = "," + repos

        self.config.data["gitearepos"] += repos

    def remove_gitea_repos(self, repos=""):
        """Remove Gitea repositories from the configuration
        
        Keyword Arguments:
            repos str -- comma seperated string of repositories (default: "")
        """
        repos_list = [x.strip() for x in repos.split(",")]
        new_list  = self.gitea_repos_list

        for repo_to_remove in repos_list:
            # loop till all items are removed, just to make sure doubles are removed
            while True:
                try:
                    new_list.remove(repo_to_remove)
                # this is thrown when item was no in list
                except ValueError:
                    break
        
        self.config.data["gitea_repos"] = ",".join(new_list)

    def link_stories(self):
        """Link stories and tasks from all repos to eachother.
        Single run.
        """
        gevent.signal(signal.SIGQUIT, gevent.kill)

        github_bot = None
        gitea_bot = None
        if self.config.data["github_repos"] != "":
            # create github bot
            token = self.config.data["github_token_"]
            repos = self.github_repos_list
            github_bot = GithubBot(token=token, repos=repos)

        if self.config.data["gitea_repos"] != "":
            # create gitea bot
            token = self.config.data["gitea_token_"]
            api_url = self.config.data["gitea_api_url"]
            base_url = self.config.data["gitea_base_url"]
            repos = self.gitea_repos_list
            gitea_bot = GiteaBot(token=token, api_url=api_url, base_url=base_url, repos=repos)

        # ask stories from bots
        start = time.time()
        gls = []
        if github_bot:
            gls.append(gevent.spawn(github_bot.get_stories))
        if gitea_bot:
            gls.append(gevent.spawn(gitea_bot.get_stories))

        # collect stories
        stories = []
        gevent.joinall(gls)
        for gl in gls:
            stories.extend(gl.value)
        end = time.time()
        self.logger.debug("Fetching stories took %ss" % (end-start))
        
        if not stories:
            self.logger.debug("No stories were found, skipping linking task to stories")
            return
        self.logger.debug("Found stories: %s", stories)

        # link task with stories with stories
        start = time.time()
        gls = []
        if github_bot:
            #github_bot.link_issues_to_stories(stories=stories)
            gls.append(gevent.spawn(github_bot.link_issues_to_stories, stories=stories))

        if gitea_bot:
            #github_bot.link_issues_to_stories(stories=stories)
            gls.append(gevent.spawn(gitea_bot.link_issues_to_stories, stories=stories))

        gevent.joinall(gls)
        end = time.time()
        self.logger.debug("Linking stories took %ss" % (end-start))
