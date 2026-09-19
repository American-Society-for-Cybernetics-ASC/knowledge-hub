from unittest.mock import MagicMock, patch

import pytest

from google_workspace_interface.service import (GoogleWorkspaceService)
from mailing_list.model import MailingList

from google.auth.transport.requests import Request 

from settings import SETTINGS

def test_get_mailing_lists_mocked():
    """
    tests retrieving Google groups
    """
    service = GoogleWorkspaceService.from_env()

    mock_google = MagicMock()

    mock_google.groups.return_value.list.return_value.execute.return_value = {
        "groups": [
            {
                "name": "Test Group 1",
                "description": "testing 1",
                "email": "group1@example.com"
            },
            {
                "name": "Test Group 2",
                "description": "testing 2",
                "email": "group2@example.com"
            },
        ]
    }   

    with patch.object(service, "_get_service", return_value=mock_google):
        mailing_lists = service.get()

    assert len(mailing_lists) == 2
    assert mailing_lists[0].name == "Test Group 1"
    assert mailing_lists[0].email == "group1@example.com"
    assert mailing_lists[0].description == "testing 1"

    assert mailing_lists[1].name == "Test Group 2"
    assert mailing_lists[1].email == "group2@example.com"
    assert mailing_lists[1].description == "testing 2"

    mock_google.groups.return_value.list.assert_called_once_with(
        customer="my_customer",
        pageToken=None,
    )
    print("\nSuccessfully retrieved mailing lists")

def test_add_user_mocked():
    """
    test adding a user to a Google group
    """
    service = GoogleWorkspaceService.from_env()

    mock_google = MagicMock()

    mailing_list = MailingList(
        name="Test Group",
        description="Test mailing list",
        email="testgroup@example.com"
    )
    user_email = "testuser@example.com"

    with patch.object(service, "_get_service", return_value=mock_google):
        service.add_user(user_email, mailing_list)

    mock_google.members.return_value.insert.assert_called_once_with(
        groupKey="testgroup@example.com",
        body={
            "email": "testuser@example.com",
            "role": "MEMBER"
        },
    )
    mock_google.members.return_value.insert.return_value.execute.assert_called_once()

    print("\nSuccessfully tested adding a user")

def test_remove_user_mocked():
    """
    test removing a user from a Google group 
    """
    service = GoogleWorkspaceService.from_env()
    mock_google = MagicMock()

    mailing_list = MailingList(
        name="Test Group",
        description="Test mailing list",
        email="testgroup@example.com"
    )
    user_email = "testuser@example.com"

    with patch.object(service, "_get_service", return_value=mock_google):
        service.remove_user(user_email, mailing_list)

    mock_google.members.return_value.delete.assert_called_once_with(
        groupKey="testgroup@example.com",
        memberKey="testuser@example.com",
    )

    mock_google.members.return_value.delete.return_value.execute.assert_called_once()

    print("\nSuccessfully tested removing a user")

def test_environment_variables():
    """
    verify that all google workspace configuration variables have been successfully loaded
    """
    print("\nChecking Google Workspace configuration")

    config = {
        "VERCEL_OIDC_TOKEN": SETTINGS.vercel_oidc_token,
        "GOOGLE_CLOUD_PROJECT_NUMBER": SETTINGS.google_cloud_project_number,
        "GOOGLE_WORKLOAD_IDENTITY_POOL": SETTINGS.google_workload_identity_pool,
        "GOOGLE_WORKLOAD_IDENTITY_PROVIDER": SETTINGS.google_workload_identity_provider,
    }

    for name, value in config.items():
        print(f"{name}: {'SET' if value else 'NOT SET'}")
        assert value, f"{name} is missing or empty"

    print("All environment variables are set")

def test_credentials():
    """
    verify that Google credentials can be constructed from Vercel OIDC configuration
    """

    service = GoogleWorkspaceService.from_env()
    credentials = service._get_credentials()

    assert credentials is not None

    print("Google credentials created successfully")

def test_credentials_refresh():
    """
    test the Google authentication process which requests
    an access token through Workload Identity Federation and service account impersonation
    """

    service = GoogleWorkspaceService.from_env()
    credentials = service._get_credentials()
    credentials.refresh(Request())

    assert credentials.valid
    assert credentials.token is not None

    print("Google authentication successful")
    print(f"Credentials valid: {credentials.valid}")

def test_google_service_builds():
    """
    verify that the Google Admin Directory API client can be constructed
    """
    service = GoogleWorkspaceService.from_env()
    google_service = service._get_service()
    assert google_service is not None

    print("\nGoogle Admin API Client created successfully")




