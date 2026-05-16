from typing import Callable

_singletons: dict = {}


def register_singleton[T](type: type[T], value: T):
    if not isinstance(value, type):
        raise TypeError(f"'{value}' is not an instance of type '{type}'")
    _singletons[type] = value


def singleton_dependency[T](type: type[T]) -> Callable[[], T]:
    def _inner():
        try:
            return _singletons[type]
        except KeyError:
            raise TypeError(f"Type '{type}' has no registered singleton")

    return _inner
