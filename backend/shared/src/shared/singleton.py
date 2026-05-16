from typing import Callable

_singletons: dict = {}


def register_singleton[T](type: type[T], value: T):
    """
    Globally registers a singleton.

    type/value as separate parameters allows subclassing:
    ```python
    register_singleton(InterfaceA, MyInterfaceAImplementation)
    ```
    """
    if not isinstance(value, type):
        raise TypeError(f"'{value}' is not an instance of type '{type}'")
    _singletons[type] = value


def singleton_dependency[T](type: type[T]) -> Callable[[], T]:
    """
    Intended for usage with FastAPI dependency injection, like:

    ```python
    def route(
        example_module: Annotated[
            ExampleModule, Depends(singleton_dependency(T))
        ]
    ): ...
    ```
    """

    def _inner():
        try:
            return _singletons[type]
        except KeyError:
            raise TypeError(f"Type '{type}' has no registered singleton")

    return _inner
