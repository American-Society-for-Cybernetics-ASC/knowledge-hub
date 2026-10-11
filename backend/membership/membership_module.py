from __future__ import annotations
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from database.model import Member, MemberType, MembershipApplication
from member_application.application_module import (
    ApplicationNotFoundError,
    ApplicationNotOwnedError,
)
from .exceptions import (
    AlreadyAMemberError,
    MembershipTypeNotFoundError,
    MembershipTypeOutOfDateError,
    NotACurrentMemberError,
)
from payments.module import PaymentsModule
from payments.payment import Payment
from payments.products import (
    CreateMembershipProduct,
    RenewMembershipProduct,
)

MEMBERSHIP_DURATION = timedelta(days=365)
RENEWAL_WINDOW = timedelta(days=182)


def get_member(session: Session, user_id: int) -> Member | None:
    existing = session.get(Member, user_id)
    return existing


def get_active_member(session: Session, user_id: int) -> Member:
    """
    :raises NotACurrentMemberError:
    """
    existing = session.get(Member, user_id)
    if not existing or not existing.active:
        raise NotACurrentMemberError()
    return existing


def assert_not_active(session, user_id: int):
    """
    :raises AlreadyAMemberError:
    """
    try:
        get_active_member(session, user_id)
        raise AlreadyAMemberError()
    except NotACurrentMemberError:
        pass


def get_application(session: Session, application_id: int) -> MembershipApplication:
    """
    :raises ApplicationNotFoundError:
    """
    application = session.get(MembershipApplication, application_id)
    if application is None:
        raise ApplicationNotFoundError()
    return application


def get_owned_application(
    session: Session, application_id: int, user_id: int
) -> MembershipApplication:
    """
    :raises ApplicationNotFoundError:
    :raises ApplicationNotFoundError:
    """
    application = get_application(session, application_id)
    if application.user_id != user_id:
        raise ApplicationNotOwnedError()
    return application


def purchase_create_membership(
    session: Session, application_id: int, user_id: int
) -> Payment:
    """
    Create a payment for creating a new membership

    :raises AlreadyAMemberError:
    :raises ApplicationNotFoundError:
    :raises ApplicationNotOwnedError:
    :raises MembershipTypeOutOfDateError:
    """
    assert_not_active(session, user_id)

    application = get_owned_application(session, application_id, user_id)

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


def purchase_renew_membership(session: Session, user_id: int) -> Payment:
    """
    Create a payment for renewing a membrership

    :raises NotACurrentMemberError:
    :raises MembershipTypeOutOfDateError:
    """

    member = get_active_member(session, user_id)
    if member.member_type is None:
        raise MembershipTypeOutOfDateError()

    return PaymentsModule().create_payment(
        user_id,
        member.member_type.price,
        "usd",  # TODO: currency
        RenewMembershipProduct(user_id=user_id, duration=MEMBERSHIP_DURATION),
    )


def set_members_type(session: Session, application_id: int, user_id: int):
    """
    :raises NotACurrentMemberError:
    :raises MembershipTypeOutOfDateError:
    :raises ApplicationNotFoundError:
    :raises ApplicationNotOwnedError:
    """
    member = get_active_member(session, user_id)
    application = get_owned_application(session, application_id, user_id)
    membership_type = application.member_type

    if membership_type is None:
        raise MembershipTypeOutOfDateError()

    with session.begin_nested():
        member.member_type = membership_type

    session.commit()


def create_membership(
    session: Session, membership_type_id: UUID, user_id: int, duration: timedelta
) -> Member:
    """
    Usually called after a successful payment.

    :raises AlreadyAMemberError:
    """

    assert_not_active(session, user_id)

    # Can be None if someone signs up with a Membership Type at the same time it gets deleted
    # In this case, we still allow their membership because they've already paid
    member_type = session.get(MemberType, membership_type_id)

    with session.begin_nested():
        member = Member(
            user_id=user_id,
            due_date=datetime.now(timezone.utc) + duration,
            member_type=member_type,
        )
        session.add(member)

    return member


def renew_membership(session: Session, user_id: int, duration: timedelta) -> Member:
    """:raises NotACurrentMemberError:"""
    member = get_active_member(session, user_id)

    now = datetime.now(timezone.utc)
    new_expiry = max(
        member.due_date.astimezone(timezone.utc) + duration,
        now + duration,
    )
    with session.begin_nested():
        member.due_date = new_expiry

    return member


def cancel_membership(session: Session, user_id: int):
    """
    Mark a membership as cancelled.

    :raises NotACurrentMemberError:
    """

    member = get_active_member(session, user_id)
    with session.begin_nested():
        member.cancelling = True


def uncancel_membership(session: Session, user_id: int):
    """
    Reinstates a previously cancelled membership

    :raises NotAMemberError:
    """
    member = get_active_member(session, user_id)
    with session.begin_nested():
        member.cancelling = False


def create_member_type(session: Session, name: str, price: int) -> MemberType:
    with session.begin_nested():
        record = MemberType(
            name=name,
            price=price,
        )
        session.add(record)
    session.flush()

    return record


def update_member_type(
    session: Session,
    member_type_id: UUID,
    name: str | None = None,
    price: int | None = None,
) -> MemberType:
    """
    :raises MembershipTypeNotFoundError:
    """
    record = session.get(MemberType, member_type_id)

    if not record:
        raise MembershipTypeNotFoundError()

    with session.begin_nested():
        record.name = name or record.name
        record.price = price or record.price
    session.flush()

    return record
