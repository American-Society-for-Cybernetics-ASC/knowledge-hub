from fastapi import FastAPI
from example_module.routes import example_router
from cron.routes import cron_router
from auth_module.routes import auth_router
from mail.routes import mail_router
from mailing_list.routes import mailing_list_router
from membership.routes import membership_router
from notifications.routes import notifications_router



app = FastAPI()

app.include_router(cron_router)
app.include_router(mail_router)
app.include_router(example_router)
app.include_router(auth_router)
app.include_router(mailing_list_router)
app.include_router(membership_router)
app.include_router(notifications_router)
