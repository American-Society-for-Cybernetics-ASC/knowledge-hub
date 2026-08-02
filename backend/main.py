from fastapi import FastAPI
from example_module.routes import example_router
from groups.routes import groups_router


app = FastAPI()
app.include_router(example_router)

app.include_router(groups_router)
