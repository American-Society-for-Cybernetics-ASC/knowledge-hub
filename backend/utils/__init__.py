from typing import Any, Self

import pydantic


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
