from typing import Annotated
from fastapi import APIRouter, Depends
from . import ExampleModule

example_router = APIRouter()


@example_router.get("/")
def example(
    example_module: Annotated[ExampleModule, Depends(ExampleModule)],
):
    return example_module.hello_world()
