
from sqlalchemy import select
from mailing_list.model import MailingListMember, MailingList
import database
from database import model
from google_workspace_interface.interface import MailingListInterface
from google_workspace_interface.service import GoogleWorkspaceService

class MemberNotFoundError(Exception):
    """raised when a member cannot be found"""
    pass


class MailingListNotFoundError(Exception):
    """raised when a mailing list cannot be found"""


class MailingListModule:

    def __init__(self, workspace: MailingListInterface | None = None):
        if workspace is None:
            self.workspace = GoogleWorkspaceService.from_env()
        else:
            self.workspace = workspace


    def get_mailing_list(self, session, mailing_list_id: int):
        """retrieve a mailing list from the database"""
        mailing_list = session.get(model.MailingList, mailing_list_id)

        if mailing_list is None:
            raise MailingListNotFoundError(f"Mailing list {mailing_list_id} cannot be found")

        if not mailing_list.email:
            raise ValueError("Mailing list does not have an email")

        return mailing_list


    def add_membership(self, session, mailing_list, email: str, member_id: int | None = None) -> None:
        """add an email to Google Worksapce"""
        #check if the email is already registered
        existing_membership = session.execute(
            select(model.MailingListMember).where(
                model.MailingListMember.mailing_list_id == mailing_list.mailing_list_id,
                model.MailingListMember.email == email,
            )
        ).scalar_one_or_none()

        if existing_membership is not None:

            if(member_id is not None and existing_membership.member_id is None):
                existing_membership.member_id = member_id
                session.commit()

            return

        #convert database object into mailing list model
        google_mailing_list = MailingList.model_validate_sqlalchemy(mailing_list)
        self.workspace.add_user(email, google_mailing_list)

        membership = model.MailingListMember(
            mailing_list_id=mailing_list.mailing_list_id,
            member_id=member_id,
            email=email,
        )

        session.add(membership)
        session.commit()


    def remove_membership(self, session, mailing_list, membership) -> None:
        """remove an email from Google Workspace"""
        google_mailing_list =  MailingList.model_validate_sqlalchemy(mailing_list)
        self.workspace.remove_user(membership.email, google_mailing_list)
        session.delete(membership)
        session.commit()


    def get_mailing_lists(self) -> list[MailingList]:
        """Returns a list of all mailing lists"""
        with database.get_session() as session:
            mailing_lists = session.execute(select(model.MailingList)).scalars().all()
            return [
                MailingList.model_validate_sqlalchemy(mailing_list)
                for mailing_list in mailing_lists
            ]


    def join_mailing_list(self, mailing_list_id: int, member_id: int) -> None:
        """Add a member to a mailing list and syncs with Google Workspace mailing list
        """
        with database.get_session() as session:
            member = session.get(model.Member, member_id)

            if member is None:
                raise MemberNotFoundError(f"Member {member_id} cannot be found")
            mailing_list = session.get(model.MailingList, mailing_list_id)

            if member.auth_user is None:
                raise MemberNotFoundError(f"Member {member_id} has no associated auth user")
            mailing_list = self.get_mailing_list(session, mailing_list_id)

            self.add_membership(
                session=session,
                mailing_list=mailing_list,
                email=member.auth_user.email,
                member_id=member_id,
            )


    def leave_mailing_list(self, mailing_list_id: int, member_id: int) -> None:
        """Remove a member from a mailing list
        """
        with database.get_session() as session:
            mailing_list = self.get_mailing_list(session, mailing_list_id)
            membership = session.execute(
                select(model.MailingListMember).where(
                    model.MailingListMember.mailing_list_id == mailing_list_id,
                    model.MailingListMember.member_id == member_id,
                )
            ).scalar_one_or_none()

            if membership is None:
                raise MemberNotFoundError(f"Member {member_id} cannot be found")

            self.remove_membership(
                session=session,
                mailing_list=mailing_list,
                membership=membership,
            )


    def get_mailing_list_members(self, mailing_list_id: int) -> list[MailingListMember]:
        """Return all members of a mailing list"""
        with database.get_session() as session:
            members = (
                session.execute(
                    select(model.MailingListMember).where(
                        model.MailingListMember.mailing_list_id == mailing_list_id
                    )
                )
                .scalars()
                .all()
            )
            return [MailingListMember.model_validate_sqlalchemy(m) for m in members]


    def add_member(self, mailing_list_id: int, email: str) -> None:
        """Assign a member to a mailing list by a manager"""
        with database.get_session() as session:
            mailing_list = self.get_mailing_list(session, mailing_list_id)
            member = session.execute(
                select(model.Member)
                .join(model.AuthUser)
                .where(model.AuthUser.email == email)
            ).scalar_one_or_none()

            member_id = (
                member.auth_user_id
                if member is not None
                else None
            )

            self.add_membership(
                session=session,
                mailing_list=mailing_list,
                email=email,
                member_id=member_id,
            )


    def kick_member(self, mailing_list_id: int, email: str) -> None:
        """Allows manager to remove a member from a mailing list"""
        with database.get_session() as session:
            mailing_list = self.get_mailing_list(
                session,
                mailing_list_id,
            )

            membership = session.execute(
                select(model.MailingListMember).where(
                    model.MailingListMember.mailing_list_id == mailing_list_id,
                    model.MailingListMember.email == email,
                )
            ).scalar_one_or_none()

            if membership is None:
                raise MemberNotFoundError(f"Email {email} is not on this mailing list")
            self.remove_membership(
                session=session,
                mailing_list=mailing_list,
                membership=membership,
            )

            
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


    def add_email(
        self, mailing_list_id: int, email: str, member_id: int | None = None
    ) -> None:
        """Add a mailing list email"""
        with database.get_session() as session:
            mailing_list = self.get_mailing_list(session, mailing_list_id)
            self.add_membership(
                session=session,
                mailing_list=mailing_list,
                email=email,
                member_id=member_id,
            )


    def sync(self) -> None:
        """sync membership that have been explicitly registered. Doesn't automatically import unregistered groups."""
        pass
