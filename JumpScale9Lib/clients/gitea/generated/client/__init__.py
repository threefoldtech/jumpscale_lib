import requests


from .AddCollaboratorOption import AddCollaboratorOption
from .AddTimeOption import AddTimeOption
from .Branch import Branch
from .Comment import Comment
from .CreateEmailOption import CreateEmailOption
from .CreateForkOption import CreateForkOption
from .CreateGPGKeyOption import CreateGPGKeyOption
from .CreateHookOption import CreateHookOption
from .CreateHookOptionconfig import CreateHookOptionconfig
from .CreateIssueCommentOption import CreateIssueCommentOption
from .CreateIssueOption import CreateIssueOption
from .CreateKeyOption import CreateKeyOption
from .CreateLabelOption import CreateLabelOption
from .CreateMilestoneOption import CreateMilestoneOption
from .CreateOrgOption import CreateOrgOption
from .CreatePullRequestOption import CreatePullRequestOption
from .CreateReleaseOption import CreateReleaseOption
from .CreateRepoOption import CreateRepoOption
from .CreateStatusOption import CreateStatusOption
from .CreateTeamOption import CreateTeamOption
from .CreateUserOption import CreateUserOption
from .DeleteEmailOption import DeleteEmailOption
from .DeployKey import DeployKey
from .EditHookOption import EditHookOption
from .EditHookOptionconfig import EditHookOptionconfig
from .EditIssueCommentOption import EditIssueCommentOption
from .EditIssueOption import EditIssueOption
from .EditLabelOption import EditLabelOption
from .EditMilestoneOption import EditMilestoneOption
from .EditOrgOption import EditOrgOption
from .EditPullRequestOption import EditPullRequestOption
from .EditReleaseOption import EditReleaseOption
from .EditTeamOption import EditTeamOption
from .EditUserOption import EditUserOption
from .Email import Email
from .EnumCreateHookOptionType import EnumCreateHookOptionType
from .EnumCreateTeamOptionPermission import EnumCreateTeamOptionPermission
from .EnumEditTeamOptionPermission import EnumEditTeamOptionPermission
from .EnumTeamPermission import EnumTeamPermission
from .GPGKey import GPGKey
from .GPGKeyEmail import GPGKeyEmail
from .Issue import Issue
from .IssueLabelsOption import IssueLabelsOption
from .Label import Label
from .MarkdownOption import MarkdownOption
from .MigrateRepoForm import MigrateRepoForm
from .Milestone import Milestone
from .Organization import Organization
from .PRBranchInfo import PRBranchInfo
from .PayloadCommit import PayloadCommit
from .PayloadCommitVerification import PayloadCommitVerification
from .PayloadUser import PayloadUser
from .Permission52 import Permission52
from .PublicKey import PublicKey
from .PullRequest import PullRequest
from .PullRequestMeta import PullRequestMeta
from .Release import Release
from .Repository import Repository
from .SearchResults import SearchResults
from .ServerVersion import ServerVersion
from .Status import Status
from .Team import Team
from .TrackedTime import TrackedTime
from .User import User
from .WatchInfo import WatchInfo

from .client import Client as APIClient


class Client:
    def __init__(self, base_uri="http://example.com/api/v1"):
        self.api = APIClient(base_uri)
