from fastapi import FastAPI
from example_module.routes import example_router

app = FastAPI()
app.include_router(example_router)
