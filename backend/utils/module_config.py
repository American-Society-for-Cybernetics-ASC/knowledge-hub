from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from database import model
from database.module_configs import ModuleConfigHelper


def get_module_config[T: ModuleConfigHelper](session: Session, cls: type[T]) -> T:
    """Fetch the module's config from the database"""
    try:
        config_record = session.get_one(model.ModuleConfig, cls.get_module_name())
        assert isinstance(config_record, cls)
        return config_record
    except NoResultFound:
        new_config_record = cls.default()
        session.add(new_config_record)
        return new_config_record
