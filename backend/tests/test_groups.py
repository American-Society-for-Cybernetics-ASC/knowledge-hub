from typing import Callable
from sqlalchemy.orm import Session
from database import model

from groups.module import GroupModule

def create_group(get_session: Callable[[], Session], email: str = "test@gmail.com") -> int:
    """create a group and return its database id"""
    with get_session() as session:
        group = model.Group(
            name=email,
            email=email,
        )
        session.add(group)
        session.commit()
        session.refresh(group)
        return group.group_id

    
def create_member(get_session: Callable[[], Session], group_id: int | None = None) -> int:
    """create a member and return its database id"""
    with get_session() as session:
        member = model.Member(
            status = "active",
            group_id = group_id,
        )
        session.add(member)
        session.commit()
        session.refresh(member)
        return member.member_id

def test_join_group(mock_get_session):
    """member joins a group"""
    group_id = create_group(mock_get_session)
    member_id = create_member(mock_get_session)

    GroupModule().join_group(group_id, member_id)

    members = GroupModule().get_group_members(group_id)
    assert len(members) == 1
    assert members[0].member_id == member_id

def test_add_member(mock_get_session):
    """member gets added to a group by a manager"""
    group_id = create_group(mock_get_session)
    member_id = create_member(mock_get_session)

    GroupModule().add_member(group_id, member_id, manager_id=1)

    members = GroupModule().get_group_members(group_id)
    assert len(members) == 1
    assert members[0].member_id == member_id

def test_leave_group(mock_get_session):
    """member leaves a group"""
    group_id = create_group(mock_get_session)
    member_id = create_member(mock_get_session, group_id=group_id)

    GroupModule().leave_group(group_id, member_id)

    members = GroupModule().get_group_members(group_id)
    assert len(members) == 0

def test_kick_member(mock_get_session):
    """members removed by manager from a group"""
    group_id = create_group(mock_get_session)
    member_id = create_member(mock_get_session, group_id=group_id)

    GroupModule().kick_member(
        group_id=group_id,
        member_id=member_id,
        manager_id=1
    )
    members = GroupModule().get_group_members(group_id)
    assert len(members) == 0



def test_get_groups(mock_get_session):
    create_group(mock_get_session, "test@gmail.com")
    create_group(mock_get_session, "123@gmail.com")

    groups = GroupModule().get_groups()

    assert len(groups) == 2
    assert groups[0].email == "test@gmail.com"
    assert groups[1].email == "123@gmail.com"

def test_join_group_via_api(test_server, mock_get_session):
    """joining a group via api"""
    group_id = create_group(mock_get_session)
    member_id = create_member(mock_get_session)

    response = test_server.post(
        f"/groups/{group_id}/join",
        params={"member_id": member_id},
    )
    assert response.status_code == 200