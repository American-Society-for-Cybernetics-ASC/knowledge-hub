import os
import tempfile

from google.auth import identity_pool
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from mailing_list.model import MailingList
from settings import SETTINGS
from .interface import MailingListInterface


SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.group",
    "https://www.googleapis.com/auth/admin.directory.group.member"
]

SERVICE_ACCOUNT_EMAIL = "groups-admin@collabhub-2608.iam.gserviceaccount.com"

class GoogleWorkspaceConfigurationError(RuntimeError):
    """Raised when Google Workspace API is called without valid configuration"""

class GoogleWorkspaceService(MailingListInterface):
    """
    Google Workspace implementation of MailingListInterface
    """
    @classmethod
    def from_env(cls) -> "GoogleWorkspaceService":
        """Create a Google Workspace service from environment variables"""
        return cls()

    def _get_credentials(self):
        """Gets Google credentials using Vercel OIDC token"""
        vercel_token = SETTINGS.vercel_oidc_token
        project_number = SETTINGS.google_cloud_project_number
        pool_id = SETTINGS.google_workload_identity_pool
        provider_id = SETTINGS.google_workload_identity_provider

        missing = []

        if not vercel_token:
            missing.append("VERCEL_OIDC_TOKEN")

        if not project_number:
            missing.append("GOOGLE_CLOUD_PROJECT_NUMBER")

        if not pool_id:
            missing.append("GOOGLE_WORKLOAD_IDENTITY_POOL")

        if not provider_id:
            missing.append("GOOGLE_WORKLOAD_IDENTITY_PROVIDER")

        if missing:
            raise GoogleWorkspaceConfigurationError("Missing Google Workspace Configuration: " + ", ".join(missing))

        audience = (
            f"//iam.googleapis.com/projects/{project_number}"
            f"/locations/global/workloadIdentityPools/{pool_id}"
            f"/providers/{provider_id}"
        )

        token_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )

        try:
            token_file.write(vercel_token)
            token_file.close()
        
            credentials = identity_pool.Credentials.from_info(
                {
                    "type": "external_account",
                    "audience": audience,
                    "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
                    "token_url": "https://sts.googleapis.com/v1/token",
                    "service_account_impersonation_url": (
                        f"https://iamcredentials.googleapis.com/v1/projects/-"
                        f"/serviceAccounts/{SERVICE_ACCOUNT_EMAIL}:generateAccessToken"
                    ),
                    "credential_source": {
                        "file": token_file.name,
                    },
                }
            )

            return credentials.with_scopes(SCOPES)

        except Exception:
            if os.path.exists(token_file.name):
                os.unlink(token_file.name)
            raise


    def _get_service(self):
        """Return an authenticated Google Admin Directory API client"""

        credentials = self._get_credentials()

        return build("admin", "directory_v1", credentials=credentials, cache_discovery=False)
        
    def get(self) -> list[MailingList]:
        """Get all Google Workspace Groups as MailingLists"""
        try:
            service = self._get_service()

            mailing_lists: list[MailingList] = []
            page_token = None

            while True:
                response=(service.groups().list(customer="my_customer", pageToken=page_token).execute())

                for group in response.get("groups", []):
                    email = group["email"]
                    mailing_lists.append(MailingList(
                        name=group.get("name") or email,
                        description=group.get("description"),
                        email=email,
                    ))
                   
                page_token = response.get("nextPageToken")

                if page_token is None:
                    break

            return mailing_lists

        except HttpError as e:
            raise GoogleWorkspaceConfigurationError(
                f"Failed to retrieve Google Workspace Groups: {e}"
            ) from e
    
    def add_user(self, user: str, mailing_list: MailingList) -> None:
        """Add a user to a Google Workspace Group"""
        if mailing_list.email is None:
            raise ValueError("Mailing list does not have an email address")

        try:
            service = self._get_service()
            service.members().insert(
                groupKey=mailing_list.email,
                body={
                    "email":user,
                    "role": "MEMBER",
                },
            ).execute()

        except HttpError as e:
            raise GoogleWorkspaceConfigurationError(
                f"Failed to add {user} to {mailing_list.email}: {e}"
            ) from e
        
    def remove_user(self, user: str, mailing_list: MailingList) -> None:
        """Remove a user from a Google Workspace Group"""
        if mailing_list.email is None:
            raise ValueError("Mailing list does not have an email address")

        try:
            service = self._get_service()

            service.members().delete(groupKey=mailing_list.email, memberKey=user).execute()

        except HttpError as e:
            raise GoogleWorkspaceConfigurationError(
                f"Failed to remove {user} from {mailing_list.email}: {e}"
            ) from e          
