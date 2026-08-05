from __future__ import annotations
from datetime import datetime
from fastapi import HTTPException, status
from database import get_session
from database.model import Membership, MembershipApplication, Payment
from .payment_provider import PaymentStatus, StubPaymentProvider
from .schema import MembershipCreate, MembershipListParams, MembershipStatus, PaymentKind

class MembershipModule:
    """One instance per request (via Depends(MembershipModule) in routes.py). 
    Each method opens its own DB session, matching how your other modules work""" 
    
    def _get_payment_provider(self):
        #Swap ones Strip is set
        return StubPaymentProvider()
    
    #Start a membership by paying for it
    def start_membership(self, data: MembershipCreate) -> Membership:
        with get_session() as db:
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
                    DETAIL="Member already has an active membership",
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
            result = (
                provider.create_recurring()
                if data.payment_kind == PaymentKind.RECURRING
                else provider.create_one_off()
            )
            if provider.check(result) != PaymentStatus.PAID:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Payment cpuld not be confirmed",
                )
            
            payment = Payment(
                date=datetime.utcnow(),
                status=PaymentStatus.PAID.value,
                kind=data.payment_kind.value,
                provider="Stripe",
            )
            db.add(payment)
            db.flush()
            
            membership = Membership(
                member_id=data.member_id,
                group_id=data.group_id,
                payment_id=payment.payment_id,
                tier=data.tier,
                start_date=datetime.utcnow(),
                status=MembershipStatus.CURRENT.value,
            )
            db.add(membership)
            db.commit()
            db.refresh(membership)
            return membership
    
    #View a single membership
    def get_membership(self, membership_id: int) -> Membership:
        with get_session() as db:
            membership = db.get(Membership, membership_id)
            if membership is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found.")
            return membership
 
    #List memberships
    def list_memberships(self, params: MembershipListParams) -> tuple[list[Membership], int]:
        with get_session() as db:
            query = db.query(Membership)
            if params.status is not None:
                query = query.filter(Membership.status == params.status.value)
            if params.member_id is not None:
                query = query.filter(Membership.member_id == params.member_id)
            total = query.count()
            return query.all(), total
 
    #Cancel
    def cancel_membership(self, membership_id: int) -> Membership:
        with get_session() as db:
            membership = db.get(Membership, membership_id)
            if membership is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found.")
            if membership.status == MembershipStatus.CANCELLED.value:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already cancelled.")
            membership.status = MembershipStatus.CANCELLED.value
            db.commit()
            db.refresh(membership)
            return membership
    
    #Uncancel
    def uncancel_membership(self, membership_id: int) -> Membership:
        with get_session() as db:
            membership = db.get(Membership, membership_id)
            if membership is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found.")
            if membership.status != MembershipStatus.CANCELLED.value:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Only a cancelled membership can be uncancelled.",
                )
            membership.status = MembershipStatus.CURRENT.value
            db.commit()
            db.refresh(membership)
            return membership
        