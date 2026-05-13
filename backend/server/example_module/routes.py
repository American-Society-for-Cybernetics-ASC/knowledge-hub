from fastapi import APIRouter

example_router = APIRouter()


@example_router.get("/")
def example():
    return "Hello, world."
