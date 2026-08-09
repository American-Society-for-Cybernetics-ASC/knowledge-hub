from sqlalchemy import select
from mailing_list.model import MailingListMember, MailingList

import database 
from database import model

class MemberNotFoundError(Exception):
    """raised when a member cannot be found"""
    pass

class MailingListModule:

    def get_mailing_lists(self) -> list[MailingList]:
        """Returns a list of all mailing lists"""
        with database.get_session() as session:
            mailing_lists = session.execute(
                select(model.MailingList)
            ).scalars().all()
            return [MailingList.model_validate_sqlalchemy(mailing_list) for mailing_list in mailing_lists]
    
    def join_mailing_list(self, mailing_list_id: int, member_id: int) -> None:
        """Add a member to a mailing list and syncs with Google Workspace mailing list
        TODO: sync with Google Workspace once google workspace interface is done
        """
        with database.get_session() as session:
            member = session.get(model.Member, member_id)
            if member is None:
                raise MemberNotFoundError(
                    f"Member {member_id} cannot be found"
                    )    
            mailing_list = session.get(model.MailingList, mailing_list_id)
            if mailing_list is None:
                raise MemberNotFoundError(
                    f"Mailing list {mailing_list_id} cannot be found"
                )
            existing_membership = session.execute(
                select(model.MailingListMember).where(
                    model.MailingListMember.mailing_list_id == mailing_list_id,
                    model.MailingListMember.member_id == member_id,
                )
            ).scalar_one_or_none()

            if existing_membership is not None:
                return
            
            membership = model.MailingListMember(mailing_list_id=mailing_list_id, member_id=member_id, email=member.auth_user.email)
            session.add(membership)
            session.commit()

    def leave_mailing_list(self, mailing_list_id: int, member_id: int) -> None:
        """Remove a member from a mailing list
        TODO: sync with Google Workspace once interface is done
        """
        with database.get_session() as session:
            membership = session.execute(
                select(model.MailingListMember).where(
                    model.MailingListMember.mailing_list_id == mailing_list_id,
                    model.MailingListMember.member_id == member_id,
                )
            ).scalar_one_or_none()
            if membership is None:
                raise MemberNotFoundError(
                    f"Member {member_id} cannot be found"
                    )
            session.delete(membership)
            session.commit()

    def get_mailing_list_members(self, mailing_list_id: int) -> list[MailingListMember]:
        """Return all members of a mailing list"""
        with database.get_session() as session:
            members = session.execute(
                select(model.MailingListMember).where(
                    model.MailingListMember.mailing_list_id == mailing_list_id
                )
            ).scalars().all()

            return [MailingListMember.model_validate_sqlalchemy(m) for m in members]

    def add_member(self, mailing_list_id: int, email: str) -> None:
        """Assign a member to a mailing list by a manager"""
        with database.get_session() as session:
            existing_membership = session.execute(
                select(model.MailingListMember).where(
                    model.MailingListMember.mailing_list_id == mailing_list_id,
                    model.MailingListMember.email == email,
                )
            ).scalar_one_or_none()

            if existing_membership is not None:
                return

            member = session.execute(
                select(model.Member)
                .join(model.AuthUser)
                .where(model.AuthUser.email == email)
            ).scalar_one_or_none()

            member_id = member.member_id if member is not None else None
            
            membership = model.MailingListMember(
                mailing_list_id=mailing_list_id,
                member_id=member_id,
                email=email,
            )
            session.add(membership)
            session.commit()

    def kick_member(self, mailing_list_id: int, email: str) -> None:
        """Allows manager to remove a member from a mailing list"""
        with database.get_session() as session:
            mailing_list_member = session.execute(
                select(model.MailingListMember).where(
                    model.MailingListMember.email ==  email,
                    model.MailingListMember.mailing_list_id == mailing_list_id,
                )
            ).scalar_one_or_none()

            if mailing_list_member is None:
                raise MemberNotFoundError(
                    f"Member with email {email} cannot be found"
                )

            session.delete(mailing_list_member)
            session.commit()

    def register_mailing_list(self, mailing_list_email: str) -> MailingList:
        """Allows a manager to manually register an existing mailing list. Doesn't automatically import all Google Workspace Groups"""
        with database.get_session() as session:
            mailing_list = model.MailingList(
                name=mailing_list_email,
                email=mailing_list_email,
            )
            session.add(mailing_list)
            session.commit()
            return MailingList.model_validate_sqlalchemy(mailing_list)

    def add_email(self, mailing_list_id: int, email: str, member_id: int | None = None) -> None:
        """Add a mailing list email"""
        with database.get_session() as session:
            mailing_member = model.MailingListMember(
                mailing_list_id=mailing_list_id,
                email=email,
                member_id=member_id,
            )
            session.add(mailing_member)
            session.commit()


    def sync(self) -> None:
        """sync membership that have been explicitly registered. Doesn't automatically import unregistered groups."""
        pass