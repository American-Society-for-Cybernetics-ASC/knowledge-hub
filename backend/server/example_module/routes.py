from typing import Annotated
from fastapi import APIRouter, Depends
from . import ExampleModule
from shared.singleton import singleton_dependency

example_router = APIRouter()


@example_router.get("/")
def example(
    example_module: Annotated[
        ExampleModule, Depends(singleton_dependency(ExampleModule))
    ],
):
    return example_module.hello_world()
