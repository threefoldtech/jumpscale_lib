from enum import Enum


class EnumTeamPermission(Enum):
    none = "none"
    read = "read"
    write = "write"
    admin = "admin"
    owner = "owner"
