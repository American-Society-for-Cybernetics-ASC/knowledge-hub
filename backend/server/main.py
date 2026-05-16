from fastapi import FastAPI
from shared.singleton import register_singleton
from example_module import ExampleModule
from example_module.routes import example_router

register_singleton(ExampleModule, ExampleModule())

app = FastAPI()
app.include_router(example_router)
