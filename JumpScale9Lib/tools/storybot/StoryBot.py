from .GithubBot import GithubBot
from .utils import _comma_to_list

from js9 import j

TEMPLATE =  """
github_token_ = ""
github_repos = ""
gitea_url = "https://docs.greenitglobe.com/api/v1"
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
        
        Keyword Arguments:
            data {data} -- StoryBot data matching the TEMPLATE(default: None)
        """
        if not data:
            data = {}

        JSConfigBase.__init__(self, instance=instance,
                                    data=data,
                                    parent=parent,
                                    template=TEMPLATE,
                                    interactive=interactive)

        #self.logger = j.logger.get("j.tools.StoryBot")
        # check configuration of the bot

    def run(self):
        """Run the StoryBot
        """
        stories = []
        github_bot = None
        gitea_bot = None

        if self.config.data["github_repos"] != "":
            # create github bot
            token = self.config.data["github_token_"]
            repos = _comma_to_list(self.config.data["github_repos"])
            github_bot = GithubBot(token=token, repos=repos)

        if self.config.data["gitea_repos"] != "":
            # create gitea bot
            pass

        # ask stories from bots
        if github_bot is not None:
            stories.extend(github_bot.get_stories())

        if gitea_bot is not None:
            stories.extend(gitea_bot.get_stories())

        # link task with stories with stories from bot bots if bots not None
        if len(stories) == 0:
            self.logger.debug("No stories were found, skipping linking task to stories")
            return
        self.logger.debug("Found stories: %s", stories)

        if github_bot is not None:
            github_bot.link_issues_to_stories(stories=stories)

        if gitea_bot is not None:
            gitea_bot.link_issues_to_stories(stories=stories)
