from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from settings import SETTINGS
import database
import database.base
from example_module.routes import example_router
from cron.routes import cron_router
from mail.routes import mail_router

if SETTINGS.local_deployment and not SETTINGS.testing:
    session = database.get_session()
    conn = session.connection()
    database.base.Base.metadata.create_all(conn)
    conn.commit()

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
app.include_router(example_router)
