from .StoryBot import StoryBot

from Jumpscale import j

JSConfigBaseFactory = j.tools.configmanager.JSBaseClassConfigs


class StoryBotFactory(JSConfigBaseFactory):

    def __init__(self):
        self.__jslocation__ = "j.tools.storybot"
        JSConfigBaseFactory.__init__(self, StoryBot)
