from fastapi import FastAPI
from example_module.routes import example_router
from groups.routes import groups_router
from cron.routes import cron_router
from auth_module.routes import auth_router
from mail.routes import mail_router


app = FastAPI()

app.include_router(cron_router)
app.include_router(mail_router)
app.include_router(example_router)
app.include_router(groups_router)
app.include_router(auth_router)
