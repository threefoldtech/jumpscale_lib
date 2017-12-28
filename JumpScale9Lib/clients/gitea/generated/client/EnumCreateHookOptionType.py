from enum import Enum


class EnumCreateHookOptionType(Enum):
    gitea = "gitea"
    gogs = "gogs"
    slack = "slack"
    discord = "discord"
