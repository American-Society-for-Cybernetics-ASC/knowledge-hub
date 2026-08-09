from __future__ import annotations
from datetime import datetime, timedelta
from fastapi import HTTPException, status
import database
from database.model import Membership, MembershipApplication, Payment
from .payment_provider import PaymentStatus, StubPaymentProvider
from .schema import MembershipCreate, MembershipListParams, MembershipStatus


MEMBERSHIP_DURATION = timedelta(days=365)
RENEWAL_WINDOW = timedelta(days=182)


class MembershipModule:
    """One instance per request (via Depends(MembershipModule) in routes.py).
    Each method opens its own DB session, matching how your other modules work"""

    def _get_payment_provider(self):
        """Returns the active payment provider"""

        # TODO: Swap ones Strip is set
        return StubPaymentProvider()

    def start_membership(self, data: MembershipCreate) -> Membership:
        """Start a membership for a new member by paying for it"""

        with database.get_session() as db:
            existing = (
                db.query(Membership)
                .filter(
                    Membership.member_id == data.member_id,
                    Membership.status == MembershipStatus.CURRENT.value,
                )
                .first()
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Member already has an active membership",
                )

            approved_application = (
                db.query(MembershipApplication)
                .filter(
                    MembershipApplication.member_id == data.member_id,
                    MembershipApplication.status == "approved",
                )
                .first()
            )

            if approved_application is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Member does not have an approved membership application",
                )

            provider = self._get_payment_provider()
            result = provider.create_one_off()

            if provider.check(result) != PaymentStatus.PAID:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Payment could not be confirmed",
                )

            payment = Payment(
                date=datetime.utcnow(),
                status=PaymentStatus.PAID.value,
                kind="Single",
                provider="Stripe",
            )
            db.add(payment)

            now = datetime.utcnow()
            membership = Membership(
                member_id=data.member_id,
                tier=data.tier,
                start_date=now,
                membership_expires=now + MEMBERSHIP_DURATION,
                status=MembershipStatus.CURRENT.value,
            )
            db.add(membership)
            db.commit()
            db.refresh(membership)
            return membership

    def renew_membership(self, membership_id: int) -> Membership:
        """Renews a membership by paying again, extending membership_expires
        by one year"""

        with database.get_session() as db:
            membership = db.get(Membership, membership_id)
            if membership is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Membership not found.",
                )

            now = datetime.utcnow()
            if membership.membership_expires - now > RENEWAL_WINDOW:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Too early to renew — more than 6 months remain.",
                )

            provider = self._get_payment_provider()
            result = provider.create_one_off()
            if provider.check(result) != PaymentStatus.PAID:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Payment could not be confirmed.",
                )

            payment = Payment(
                date=now,
                status=PaymentStatus.PAID.value,
                kind="Single",
                provider="Stripe",
            )
            db.add(payment)

            membership.membership_expires += MEMBERSHIP_DURATION
            db.commit()
            db.refresh(membership)
            return membership

    def get_membership(self, membership_id: int) -> Membership:
        """View a single membership"""

        with database.get_session() as db:
            membership = db.get(Membership, membership_id)
            if membership is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Membership not found.",
                )
            return membership

    def list_memberships(
        self, params: MembershipListParams
    ) -> tuple[list[Membership], int]:
        """List memberships"""

        with database.get_session() as db:
            query = db.query(Membership)
            if params.status is not None:
                query = query.filter(Membership.status == params.status.value)
            if params.member_id is not None:
                query = query.filter(Membership.member_id == params.member_id)
            total = query.count()
            return query.all(), total

    def cancel_membership(self, membership_id: int) -> Membership:
        """Cancel"""

        with database.get_session() as db:
            membership = db.get(Membership, membership_id)
            if membership is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Membership not found.",
                )
            if membership.status == MembershipStatus.CANCELLED.value:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="Already cancelled."
                )
            membership.status = MembershipStatus.CANCELLED.value
            db.commit()
            db.refresh(membership)
            return membership

    def uncancel_membership(self, membership_id: int) -> Membership:
        """Reinstates a previously cancelled membership"""

        with database.get_session() as db:
            membership = db.get(Membership, membership_id)
            if membership is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Membership not found.",
                )
            if membership.status != MembershipStatus.CANCELLED.value:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Only a cancelled membership can be uncancelled.",
                )
            membership.status = MembershipStatus.CURRENT.value
            db.commit()
            db.refresh(membership)
            return membership
