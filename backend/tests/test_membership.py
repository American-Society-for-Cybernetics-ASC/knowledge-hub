import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
 

from database.base import Base
from database.model import Member, MembershipApplication
from membership.module import MembershipModule
from membership.schema import MembershipCreate, MembershipListParams
 
 
@pytest.fixture
def db_session(monkeypatch):
    """Creates a fresh in-memory SQLite database for each test, and makes
    the Membership module use it instead of the real database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
 
    session = Session(engine, expire_on_commit=False)
 
    # test session instead of hitting Postgres/Supabase.
    monkeypatch.setattr("membership.module.get_session", lambda: session)
 
    yield session
 
    session.close()
 
 
@pytest.fixture
def approved_member(db_session):
    """Creates a Member with an approved MembershipApplication"""
    member = Member(status="Applied")
    db_session.add(member)
    db_session.flush()
 
    application = MembershipApplication(
        member_id=member.member_id,
        status="approved",
    )
    db_session.add(application)
    db_session.commit()
 
    return member
 
 
def test_start_membership_succeeds_for_approved_member(db_session, approved_member):
    module = MembershipModule()
    data = MembershipCreate(member_id=approved_member.member_id, tier="Standard")
 
    membership = module.start_membership(data)
 
    assert membership.member_id == approved_member.member_id
    assert membership.tier == "Standard"
    assert membership.status == "Current"
    assert membership.payment_id is not None
 
 
def test_start_membership_rejects_unapproved_member(db_session):
    # A Member with NO approved application at all
    member = Member(status="Applied")
    db_session.add(member)
    db_session.commit()
 
    module = MembershipModule()
    data = MembershipCreate(member_id=member.member_id, tier="Standard")
 
    with pytest.raises(Exception) as exc_info:
        module.start_membership(data)
 
    # HTTPException carries a status_code — 403 means "not approved"
    assert getattr(exc_info.value, "status_code", None) == 403
 
 
def test_start_membership_rejects_duplicate_active_membership(db_session, approved_member):
    module = MembershipModule()
    data = MembershipCreate(member_id=approved_member.member_id, tier="Standard")
 
    module.start_membership(data)  # first one succeeds
 
    with pytest.raises(Exception) as exc_info:
        module.start_membership(data)  # second one should be rejected
 
    assert getattr(exc_info.value, "status_code", None) == 409
 
 
def test_get_membership_returns_correct_record(db_session, approved_member):
    module = MembershipModule()
    created = module.start_membership(
        MembershipCreate(member_id=approved_member.member_id, tier="Standard")
    )
 
    fetched = module.get_membership(created.membership_id)
 
    assert fetched.membership_id == created.membership_id
    assert fetched.tier == "Standard"
 
 
def test_get_membership_missing_raises_404(db_session):
    module = MembershipModule()
 
    with pytest.raises(Exception) as exc_info:
        module.get_membership(9999)
 
    assert getattr(exc_info.value, "status_code", None) == 404
 
 
def test_cancel_then_uncancel_membership(db_session, approved_member):
    module = MembershipModule()
    membership = module.start_membership(
        MembershipCreate(member_id=approved_member.member_id, tier="Standard")
    )
 
    cancelled = module.cancel_membership(membership.membership_id)
    assert cancelled.status == "Cancelled"
 
    reinstated = module.uncancel_membership(membership.membership_id)
    assert reinstated.status == "Current"
 
 
def test_cancel_already_cancelled_membership_raises_409(db_session, approved_member):
    module = MembershipModule()
    membership = module.start_membership(
        MembershipCreate(member_id=approved_member.member_id, tier="Standard")
    )
    module.cancel_membership(membership.membership_id)
 
    with pytest.raises(Exception) as exc_info:
        module.cancel_membership(membership.membership_id)
 
    assert getattr(exc_info.value, "status_code", None) == 409
 
 
def test_list_memberships_filters_by_status(db_session, approved_member):
    module = MembershipModule()
    membership = module.start_membership(
        MembershipCreate(member_id=approved_member.member_id, tier="Standard")
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