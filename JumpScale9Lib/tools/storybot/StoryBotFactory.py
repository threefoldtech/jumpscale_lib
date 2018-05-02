from .StoryBot import StoryBot

from js9 import j

JSConfigBaseFactory = j.tools.configmanager.base_class_configs


class StoryBotFactory(JSConfigBaseFactory):

    def __init__(self):
        self.__jslocation__ = "j.tools.storybot"
        JSConfigBaseFactory.__init__(self, StoryBot)
