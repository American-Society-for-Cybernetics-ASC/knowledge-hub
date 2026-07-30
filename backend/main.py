from fastapi import FastAPI
from example_module.routes import example_router
from cron.routes import cron_router


app = FastAPI()

app.include_router(cron_router)
app.include_router(example_router)
