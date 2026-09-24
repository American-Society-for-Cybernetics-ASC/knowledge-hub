from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth_module import PermissionTier, Permissions, AuthModule
from settings import SETTINGS
import database
import database.model as dbmodel
import database.base
from example_module.routes import example_router
from cron.routes import cron_router
from auth_module.routes import auth_router
from mail.routes import mail_router
from mailing_list.routes import mailing_list_router
from members.routes import members_router
from membership.membership_routes import membership_router
from notifications.routes import notifications_router
from member_matching.routes import member_matching_router
from member_application.application_routes import member_application_router
from payments.routes import payments_router
from audit_log.routes import audit_router
from members.model import ProfileContent, ProfileIdentity
from email_templates.routes import email_templates_router
from email_templates.module import EmailTemplatesModule

if SETTINGS.local_deployment and not SETTINGS.testing:
    with database.get_session() as session:
        conn = session.connection()
        database.base.Base.metadata.drop_all(conn)
        database.base.Base.metadata.create_all(conn)
        conn.commit()

    AuthModule().register("test@test.com", "test", "Test Admin")

    with database.get_session() as session:
        user = (
            session.query(dbmodel.AuthUser)
            .where(dbmodel.AuthUser.email == "test@test.com")
            .one()
        )

        user.permissions = Permissions(tier=PermissionTier.adminstrator).model_dump(
            mode="json"
        )

        member_type = dbmodel.MemberType(name="Test Member Type", price=10_00)

        session.flush()

        member = dbmodel.Member(
            user_id=user.user_id,
            member_type=member_type,
            due_date=datetime.now(timezone.utc) + timedelta(365),
        )
        session.add(member)
        session.flush()

        session.add(
            dbmodel.Profile(
                member_id=member.user_id,
                content=ProfileContent(
                    identity=ProfileIdentity(display_name="Test User"),
                ).model_dump(mode="json"),
                tags=[],
            )
        )

        session.commit()

# Seed default email templates
if not SETTINGS.testing:
    EmailTemplatesModule().seed_defaults()

app = FastAPI(title="CKH API", version="0.1.0", root_path=SETTINGS.backend_root_path)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cron_router)
app.include_router(mail_router)
app.include_router(payments_router)
app.include_router(members_router)
app.include_router(example_router)
app.include_router(auth_router)
app.include_router(mailing_list_router)
app.include_router(membership_router)
app.include_router(notifications_router)
app.include_router(member_matching_router)
app.include_router(member_application_router)
app.include_router(payments_router)
app.include_router(audit_router)
app.include_router(email_templates_router)
