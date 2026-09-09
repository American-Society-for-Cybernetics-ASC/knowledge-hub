from __future__ import annotations
from datetime import datetime, timedelta, timezone
from uuid import UUID


from member_application.module import ApplicationNotFoundError, ApplicationNotOwnedError

from .model import Member, MemberStatus
from .exceptions import (
    AlreadyAMemberError,
    MembershipTypeOutOfDateError,
    NotAMemberError,
)
from payments.module import PaymentsModule
from payments.payment import Payment
from payments.products import (
    CreateMembershipProduct,
    RenewMembershipProduct,
)
import database
from database import model as dbmodel

MEMBERSHIP_DURATION = timedelta(days=365)
RENEWAL_WINDOW = timedelta(days=182)


class MembershipModule:
    def get_member(self, user_id: int) -> Member | None:
        with database.get_session() as session:
            existing = session.get(dbmodel.Member, user_id)
        if existing is None:
            return None
        return Member.from_db_model(existing)

    def purchase_create_membership(self, application_id: int, user_id: int) -> Payment:
        """
        Create a payment for creating a new membership

        :raises AlreadyAMemberError:
        :raises ApplicationNotFoundError:
        :raises ApplicationNotOwnedError:
        :raises MembershipTypeOutOfDateError:
        """

        with database.get_session() as session:
            if session.get(dbmodel.Member, user_id) is not None:
                raise AlreadyAMemberError()

            application = session.get(dbmodel.MembershipApplication, application_id)
            if not application:
                raise ApplicationNotFoundError()
            if application.auth_user_id != user_id:
                raise ApplicationNotOwnedError()

            member_type = application.member_type
            if not member_type:
                raise MembershipTypeOutOfDateError()

        return PaymentsModule().create_payment(
            user_id,
            member_type.price,
            "usd",  # TODO: currency
            CreateMembershipProduct(
                user_id=user_id,
                membership_type_id=member_type.id,
                duration=MEMBERSHIP_DURATION,
            ),
        )

    def purchase_renew_membership(self, user_id: int) -> Payment:
        """
        Create a payment for renewing a membrership

        :raises NotAMemberError:
        :raises MembershipTypeOutOfDateError:
        """

        with database.get_session() as session:
            member = session.get(dbmodel.Member, user_id)
            if member is None:
                raise NotAMemberError()
            if member.member_type is None:
                raise MembershipTypeOutOfDateError()

        return PaymentsModule().create_payment(
            user_id,
            member.member_type.price,
            "usd",  # TODO: currency
            RenewMembershipProduct(user_id=user_id, duration=MEMBERSHIP_DURATION),
        )

    def update_membership_type(self, application_id: int, user_id: int):
        """
        :raises NotAMemberError:
        :raises MembershipTypeOutOfDateError:
        """
        with database.get_session() as session:
            member = session.get(dbmodel.Member, user_id)
            if member is None:
                raise NotAMemberError()

            application = session.get(dbmodel.MembershipApplication, application_id)
            if not application:
                raise ApplicationNotFoundError()
            if application.auth_user_id != user_id:
                raise ApplicationNotOwnedError()

            membership_type = application.member_type
            if membership_type is None:
                raise MembershipTypeOutOfDateError()

            member.member_type = membership_type
            session.commit()

    def create_membership(
        self, membership_type_id: UUID, user_id: int, duration: timedelta
    ) -> Member:
        """
        Usually called after a successful payment.

        :raises AlreadyAMemberError:
        """

        with database.get_session() as session:
            if session.get(dbmodel.Member, user_id) is not None:
                raise AlreadyAMemberError()

            # Can be None if someone signs up with a Membership Type at the same time it gets deleted
            # In this case, we still allow their membership because they've already paid
            member_type = session.get(dbmodel.MemberType, membership_type_id)

            member = dbmodel.Member(
                auth_user_id=user_id,
                membership_expires=datetime.now(timezone.utc) + duration,
                member_type=member_type,
                status=MemberStatus.CURRENT,
                cancelled=False,
            )
            session.add(member)
            session.commit()
            return Member.from_db_model(member)

    def renew_membership(self, user_id: int, duration: timedelta) -> Member:
        """:raises NotAMemberError:"""

        with database.get_session() as session:
            member = session.get(dbmodel.Member, user_id)
            if member is None:
                raise NotAMemberError()

            now = datetime.now(timezone.utc)
            new_expiry = max(
                member.membership_expires.astimezone(timezone.utc) + duration,
                now + duration,
            )
            member.membership_expires = new_expiry
            session.commit()

            return Member.from_db_model(member)

    def cancel_membership(self, user_id: int):
        """
        Mark a membership as cancelled.

        :raises NotAMemberError:
        """

        with database.get_session() as session:
            member = session.get(dbmodel.Member, user_id)
            if member is None:
                raise NotAMemberError()
            member.cancelled = True
            session.commit()

    def uncancel_membership(self, user_id: int):
        """
        Reinstates a previously cancelled membership

        :raises NotAMemberError:
        """
        with database.get_session() as session:
            member = session.get(dbmodel.Member, user_id)
            if member is None:
                raise NotAMemberError()
            member.cancelled = False
            session.commit()
