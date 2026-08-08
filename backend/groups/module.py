from sqlalchemy import select
from groups.model import Group, GroupMember

import database 
from database import model

class MemberNotFoundError(Exception):
    """raised when a member cannot be found"""
    pass

class GroupModule:
    """Handle all group operations"""

    def get_groups(self) -> list[Group]:
        """Returns a list of all groups"""
        session = database.get_session()
        groups = session.execute(select(model.Group)).scalars().all()
        return [
            Group.model_validate(group, from_attributes=True)
            for group in groups
        ]
    
    def join_group(self, group_id: int, member_id: int) -> None:
        """Add a member to a group and syncs with Google Workspace mailing list (to be added)"""
        session = database.get_session()
        member = session.get(model.Member, member_id)
        if member is None:
            raise MemberNotFoundError(
                f"Member {member_id} cannot be found"
                )    
        member.group_id = group_id
        session.commit()

    def leave_group(self, group_id: int, member_id: int) -> None:
        """Remove a member from a group"""
        session = database.get_session()
        member = session.get(model.Member, member_id)
        if member is None:
            raise MemberNotFoundError(
                f"Member {member_id} cannot be found"
                )
        member.group_id = None
        session.commit()

    def get_group_members(self, group_id: int) -> list[GroupMember]:
        """Return all members of a group"""
        session = database.get_session()
        members = session.execute(
            select(model.Member).where(
                model.Member.group_id == group_id
            )
        ).scalars().all()

        return [
            GroupMember.model_validate(member, from_attributes=True)
            for member in members
        ]

    def add_member(
            self,
            group_id: int,
            member_id: int, 
            manager_id: int
    ) -> None:
        """Assign a member to a group by a manager"""
        session = database.get_session()
        member = session.get(model.Member, member_id)
        if member is None:
            raise MemberNotFoundError(
                f"Member {member_id} cannot be found"
                )
        member.group_id = group_id
        session.commit()

    def kick_member(
            self,
            group_id: int,
            member_id: int,
            manager_id: int
    ) -> None:
        """Allows manager to remove a member from a group"""
        session = database.get_session()
        member = session.get(model.Member, member_id)

        if member is None:
            raise MemberNotFoundError(
                f"Member {member_id} cannot be found"
            )

        member.group_id = None
        session.commit()

    def register_group(self, mailing_list_email: str, manager_id: int) -> Group:
        """Allows a manager to manually register an existing group. Doesn't automatically import all Google Workspace Groups"""
        session = database.get_session()
        group = model.Group(
            name=mailing_list_email,
            email=mailing_list_email,
        )
        session.add(group)
        session.commit()
        return Group.model_validate(group, from_attributes=True)

    def add_email(self, group_id: int, email: str, member_id: int | None = None) -> None:
        """Add a mailing list email"""
        session = database.get_session()
        mailing_member = model.MailingListMember(
            group_id=group_id,
            email=email,
            member_id=member_id,
            is_member=member_id is not None,
        )
        session.add(mailing_member)
        session.commit()


    def sync(self) -> None:
        """sync membership that have been explicitly registered. Doesn't automatically import unregistered groups."""
        pass