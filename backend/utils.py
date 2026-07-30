from typing import Any, Self

import pydantic


class BaseModel(pydantic.BaseModel):
    @classmethod
    def model_validate_sqlalchemy(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        extra: pydantic.config.ExtraValues | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        return cls.model_validate(
            obj,
            from_attributes=True,
            strict=strict,
            extra=extra,
            context=context,
            by_alias=by_alias,
            by_name=by_name,
        )
