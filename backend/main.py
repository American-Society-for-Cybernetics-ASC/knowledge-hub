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
from membership.routes import membership_router
from notifications.routes import notifications_router
from member_application.routes import member_application_router
from payments.routes import payments_router
from audit_log.routes import audit_router
from members.model import ProfileContent, ProfileIdentity

if SETTINGS.local_deployment and not SETTINGS.testing:
    with database.get_session() as session:
        conn = session.connection()
        database.base.Base.metadata.drop_all(conn)
        database.base.Base.metadata.create_all(conn)
        conn.commit()
        session.close()

    AuthModule().register("test@test.com", "test", "Test User")

    with database.get_session() as session:
        user = (
            session.query(dbmodel.AuthUser)
            .where(dbmodel.AuthUser.email == "test@test.com")
            .one()
        )

        user.permissions = Permissions(
            tier=PermissionTier.adminstrator
        ).model_dump_json()

        member = dbmodel.Member(
            status="active",
            auth_user_id=user.user_id,
        )
        session.add(member)
        session.flush()

        session.add(
            dbmodel.Profile(
                member_id=member.member_id,
                content=ProfileContent(
                    identity=ProfileIdentity(display_name="Test User"),
                ).model_dump(mode="json"),
                tags=[],
            )
        )

        session.commit()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cron_router)
app.include_router(mail_router)
app.include_router(members_router)
app.include_router(example_router)
app.include_router(auth_router)
app.include_router(mailing_list_router)
app.include_router(membership_router)
app.include_router(notifications_router)
app.include_router(member_application_router)
app.include_router(payments_router)
app.include_router(audit_router)

