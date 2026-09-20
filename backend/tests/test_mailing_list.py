
import datetime
import pytest
from typing import Callable
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import model
from mailing_list.module import MailingListModule

@pytest.fixture
def mailing_list_module() -> MailingListModule:
    """use mocked google workspace service"""
    workspace = MagicMock()
    return MailingListModule(workspace=workspace)


def create_mailing_list(
    get_session: Callable[[], Session], email: str = "test@gmail.com"
) -> int:
    with get_session() as session:
        mailing_list = model.MailingList(
            name=email,
            email=email,
        )
        session.add(mailing_list)
        session.commit()
        session.refresh(mailing_list)
        return mailing_list.mailing_list_id

    
def create_member(get_session: Callable[[], Session]) -> int:
    with get_session() as session:
        auth_user = model.AuthUser(
            name="User",
            email="member@gmail.com",
            permissions={},
        )
        session.add(auth_user)
        session.flush()
        session.refresh(auth_user)
        member = model.Member(
            auth_user=auth_user,
            membership_expires=datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(days=100),
            cancelled=False,
        )
        session.add(member)
        session.commit()
        session.refresh(member)
        return member.auth_user_id

    
def create_mailing_list_member(
    get_session: Callable[[], Session],
    mailing_list_id: int,
    email: str,
    member_id: int | None = None,
) -> int:
    with get_session() as session:
        mailing_list_member = model.MailingListMember(
            mailing_list_id=mailing_list_id,
            email=email,
            member_id=member_id,
        )
        session.add(mailing_list_member)
        session.commit()
        session.refresh(mailing_list_member)
        return mailing_list_member.mailing_list_member_id

    
def test_register_mailing_list(mock_get_session, mailing_list_module: MailingListModule):
    mailing_list = mailing_list_module.register_mailing_list("test@gmail.com")
    assert mailing_list.email == "test@gmail.com"
    assert mailing_list.name == "test@gmail.com"


def test_get_mailing_lists(mock_get_session, mailing_list_module: MailingListModule):
    create_mailing_list(mock_get_session, "test@gmail.com")
    create_mailing_list(mock_get_session, "123@gmail.com")

    mailing_lists = mailing_list_module.get_mailing_lists()

    assert len(mailing_lists) == 2
    assert mailing_lists[0].email == "test@gmail.com"
    assert mailing_lists[1].email == "123@gmail.com"

    
def test_join_mailing_list(mock_get_session, mailing_list_module: MailingListModule):
    mailing_list_id = create_mailing_list(mock_get_session)
    member_id = create_member(mock_get_session)

    mailing_list_module.join_mailing_list(mailing_list_id, member_id)
    members = mailing_list_module.get_mailing_list_members(mailing_list_id)

    assert len(members) == 1
    assert members[0].member_id == member_id
    assert members[0].email == "member@gmail.com"

    mailing_list_module.workspace.add_user.assert_called_once()
    user_email, google_mailing_list = (mailing_list_module.workspace.add_user.call_args.args)

    assert user_email == "member@gmail.com"
    assert google_mailing_list.email == "test@gmail.com"


def test_leave_mailing_list(mock_get_session, mailing_list_module: MailingListModule):
    mailing_list_id = create_mailing_list(mock_get_session)
    member_id = create_member(mock_get_session)

    create_mailing_list_member(
        mock_get_session,
        mailing_list_id=mailing_list_id,
        email="member@gmail.com",
        member_id=member_id,
    )

    mailing_list_module.leave_mailing_list(mailing_list_id, member_id)
    members = mailing_list_module.get_mailing_list_members(mailing_list_id)

    assert len(members) == 0

    mailing_list_module.workspace.remove_user.assert_called_once()

    user_email, google_mailing_list = (mailing_list_module.workspace.remove_user.call_args.args)
    assert user_email == "member@gmail.com"
    assert google_mailing_list.email == "test@gmail.com"

def test_add_member(mock_get_session, mailing_list_module: MailingListModule):
    mailing_list_id = create_mailing_list(mock_get_session)
    member_id = create_member(mock_get_session)
    email = "member@gmail.com"
    mailing_list_module.add_member(mailing_list_id, email)

    with mock_get_session() as session:
        membership = session.execute(
            select(model.MailingListMember).where(
                model.MailingListMember.email == email,
                model.MailingListMember.mailing_list_id == mailing_list_id,
            )
        ).scalar_one()

        assert membership.email == email
        assert membership.member_id == member_id
        assert membership.mailing_list_id == mailing_list_id

    mailing_list_module.workspace.add_user.assert_called_once()
    user_email, google_mailing_list = (mailing_list_module.workspace.add_user.call_args.args)

    assert user_email == email
    assert google_mailing_list.email == "test@gmail.com"


def test_kick_member(mock_get_session, mailing_list_module: MailingListModule):
    mailing_list_id = create_mailing_list(mock_get_session)
    member_id = create_member(mock_get_session)
    email = "member@gmail.com"

    create_mailing_list_member(
        mock_get_session,
        mailing_list_id=mailing_list_id,
        email=email,
        member_id=member_id,
    )

    mailing_list_module.kick_member(mailing_list_id=mailing_list_id, email=email)

    with mock_get_session() as session:
        membership = session.execute(
            select(model.MailingListMember).where(
                model.MailingListMember.email == email,
                model.MailingListMember.mailing_list_id == mailing_list_id,
            )
        ).scalar_one_or_none()
        assert membership is None

    mailing_list_module.workspace.remove_user.assert_called_once()
    user_email, google_mailing_list = (
        mailing_list_module.workspace.remove_user.call_args.args
    )

    assert user_email == email
    assert google_mailing_list.email == "test@gmail.com"


def test_add_email(mock_get_session, mailing_list_module: MailingListModule):
    mailing_list_id = create_mailing_list(mock_get_session)
    mailing_list_module.add_email(mailing_list_id, "external@gmail.com")

    with mock_get_session() as session:
        membership = session.execute(
            select(model.MailingListMember).where(
                model.MailingListMember.email == "external@gmail.com"
            )
        ).scalar_one()

        assert membership.email == "external@gmail.com"
        assert membership.mailing_list_id == mailing_list_id
        assert membership.member_id is None

    mailing_list_module.workspace.add_user.assert_called_once()
    user_email, google_mailing_list = (
        mailing_list_module.workspace.add_user.call_args.args
    )
    
    assert user_email == "external@gmail.com"
    assert google_mailing_list.email == "test@gmail.com"
