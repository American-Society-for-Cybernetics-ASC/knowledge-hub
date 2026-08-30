from abc import abstractmethod
from typing import Any, Self

import pydantic
from sqlalchemy.exc import NoResultFound

from database import model
import database


class BaseModel(pydantic.BaseModel):
    """
    Wrapper around pydantic.BaseModel.

    - Adds "model_validate_sqlalchemy", which ensures sqlalchemy mapped types are validated correctly.
    """

    @classmethod
    def model_validate_sqlalchemy(
        cls,
        obj: Any,
        *args,
        strict: bool | None = None,
        extra: pydantic.config.ExtraValues | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
        **kwargs,
    ) -> Self:
        """
        Calls pydantic's :func:`~pydantic.BaseModel.model_validate`, with the correct parameters,
        to support validating a mapped sqlalchemy model.
        """
        return cls.model_validate(
            obj,
            *args,
            from_attributes=True,
            strict=strict,
            extra=extra,
            context=context,
            by_alias=by_alias,
            by_name=by_name,
            **kwargs,
        )


class ModuleConfig(BaseModel):
    """Necessary interface for use with :func:`get_module_config` and :func:`set_module_config`"""

    @staticmethod
    @abstractmethod
    def module_id() -> str: ...

    @classmethod
    @abstractmethod
    def default(cls) -> Self: ...


def get_module_config[T: ModuleConfig](cls: type[T]) -> T:
    """Fetch the module's config from the database"""
    with database.get_session() as session:
        try:
            config_record = session.get_one(model.Module, cls.module_id())
            return cls.model_validate_sqlalchemy(config_record.config)
        except NoResultFound:
            config_record = model.Module(
                module_name=cls.module_id(),
                config=cls.default().model_dump(),
            )
            session.add(config_record)
            session.commit()
            return get_module_config(cls)


def set_module_config[T: ModuleConfig](value: T):
    """Fetch the module's config from the database"""
    with database.get_session() as session:
        current = session.get_one(model.Module, value.module_id())
        current.config = value.model_dump()
        session.commit()
