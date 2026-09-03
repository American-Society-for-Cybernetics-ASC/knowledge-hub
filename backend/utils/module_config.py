from abc import abstractmethod
from typing import Self

from sqlalchemy.exc import NoResultFound

from . import BaseModel
from database import model
import database


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
