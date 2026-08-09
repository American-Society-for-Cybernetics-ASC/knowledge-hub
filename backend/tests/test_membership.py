import pytest
import database

from database.model import Member, MembershipApplication
from membership.module import MembershipModule
from membership.schema import MembershipCreate, MembershipListParams


@pytest.fixture
def approved_member():
    """Creates a Member with an approved MembershipApplication"""
    with database.get_session() as db:
        member = Member(status="Applied")
        db.add(member)
        db.flush()

        application = MembershipApplication(
            member_id=member.member_id,
            status="approved",
        )
        db.add(application)
        db.commit()

        return member.member_id


def test_start_membership_succeeds_for_approved_member(approved_member):
    """An approved member should be able to start a membership successfully"""
    module = MembershipModule()
    data = MembershipCreate(member_id=approved_member, tier="Standard")

    membership = module.start_membership(data)

    assert membership.member_id == approved_member
    assert membership.tier == "Standard"
    assert membership.status == "Current"


def test_start_membership_rejects_unapproved_member():
    """A member with no approved application should be rejected"""
    with database.get_session() as db:
        member = Member(status="Applied")
        db.add(member)
        db.commit()
        member_id = member.member_id

    module = MembershipModule()
    data = MembershipCreate(member_id=member_id, tier="Standard")

    with pytest.raises(Exception) as exc_info:
        module.start_membership(data)

    assert getattr(exc_info.value, "status_code", None) == 403


def test_start_membership_rejects_duplicate_active_membership(approved_member):
    """A member who already has a Current membership can't start a second one"""
    module = MembershipModule()
    data = MembershipCreate(member_id=approved_member, tier="Standard")

    module.start_membership(data)

    with pytest.raises(Exception) as exc_info:
        module.start_membership(data)

    assert getattr(exc_info.value, "status_code", None) == 409


def test_get_membership_returns_correct_record(approved_member):
    """Fetching a membership by ID should return the exact record created"""
    module = MembershipModule()
    created = module.start_membership(
        MembershipCreate(member_id=approved_member, tier="Standard")
    )

    fetched = module.get_membership(created.membership_id)

    assert fetched.membership_id == created.membership_id
    assert fetched.tier == "Standard"


def test_get_membership_missing_raises_404():
    """Fetching a membership that doesn't exist should raise 404"""
    module = MembershipModule()

    with pytest.raises(Exception) as exc_info:
        module.get_membership(9999)

    assert getattr(exc_info.value, "status_code", None) == 404


def test_cancel_then_uncancel_membership(approved_member):
    """A membership can be cancelled and then reinstated via uncancel"""
    module = MembershipModule()
    membership = module.start_membership(
        MembershipCreate(member_id=approved_member, tier="Standard")
    )

    cancelled = module.cancel_membership(membership.membership_id)
    assert cancelled.status == "Cancelled"

    reinstated = module.uncancel_membership(membership.membership_id)
    assert reinstated.status == "Current"


def test_cancel_already_cancelled_membership_raises_409(approved_member):
    """Cancelling an already-cancelled membership should raise 409"""
    module = MembershipModule()
    membership = module.start_membership(
        MembershipCreate(member_id=approved_member, tier="Standard")
    )
    module.cancel_membership(membership.membership_id)

    with pytest.raises(Exception) as exc_info:
        module.cancel_membership(membership.membership_id)

    assert getattr(exc_info.value, "status_code", None) == 409


def test_list_memberships_filters_by_status(approved_member):
    """Listing memberships with a status filter should only return matches"""
    module = MembershipModule()
    membership = module.start_membership(
        MembershipCreate(member_id=approved_member, tier="Standard")
    )

    current_results, current_total = module.list_memberships(
        MembershipListParams(status="Current")
    )
    assert current_total == 1
    assert current_results[0].membership_id == membership.membership_id

    module.cancel_membership(membership.membership_id)

    current_results, current_total = module.list_memberships(
        MembershipListParams(status="Current")
    )
    assert current_total == 0
