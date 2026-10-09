from abc import abstractmethod
from typing import Literal, Optional, Self
import uuid

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.types import ModuleName
from .model import ModuleConfig, MailProvider


class ModuleConfigHelper:
    """Necessary interface for use with :func:`~utils.module_config.get_module_config` and :func:`~utils.module_config.set_module_config`"""

    @staticmethod
    @abstractmethod
    def get_module_name() -> ModuleName: ...

    @classmethod
    @abstractmethod
    def default(cls) -> Self: ...


class NotificationsConfig(ModuleConfig, ModuleConfigHelper):
    @staticmethod
    def get_module_name():
        return ModuleName.NOTIFICATIONS

    __mapper_args__ = {
        "polymorphic_identity": get_module_name(),
    }
    __tablename__ = "module_config_" + get_module_name()

    module_name: Mapped[Literal[ModuleName.NOTIFICATIONS]] = mapped_column(
        ForeignKey(ModuleConfig.module_name),
        primary_key=True,
        default=ModuleName.NOTIFICATIONS,
    )
    email_provider: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey(MailProvider.id)
    )

    @classmethod
    def default(cls) -> NotificationsConfig:
        return NotificationsConfig(email_provider=None)


class MemberMatchingConfig(ModuleConfig, ModuleConfigHelper):
    @staticmethod
    def get_module_name():
        return ModuleName.MEMBER_MATCHING

    __mapper_args__ = {
        "polymorphic_identity": get_module_name(),
    }
    __tablename__ = "module_config_" + get_module_name()
    __table_args__ = (
        CheckConstraint("dismissal_days >= 0"),
        CheckConstraint("maximum_suggestions >= 1"),
    )

    module_name: Mapped[Literal[ModuleName.MEMBER_MATCHING]] = mapped_column(
        ForeignKey(ModuleConfig.module_name),
        primary_key=True,
        default=ModuleName.MEMBER_MATCHING,
    )
    dismissal_days: Mapped[int] = mapped_column(default=7)
    maximum_suggestions: Mapped[int] = mapped_column(default=20)

    @classmethod
    def default(cls) -> MemberMatchingConfig:
        return MemberMatchingConfig()
