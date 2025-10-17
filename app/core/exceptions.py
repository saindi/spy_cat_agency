from typing import Any

from fastapi import HTTPException
from starlette import status

from app.core.logger import LoggerMixin
from app.enums.exceptions import MessageException

__all__ = [
    "BaseHTTPException",
    "ObjectNotFoundException",
    "ObjectAlreadyExistsException",
    "GoneException",
    "NotAuthorizedException",
    "ForbiddenException",
    "BadRequestException",
]


class BaseHTTPException(LoggerMixin, HTTPException):
    """
    Base class for all custom exceptions.
    *_pattern is a tuple with a message and arguments to format it. Example: ('{0} not found!', 'class_name')
    """

    _exception_alias: MessageException | None = None
    status_code: int = status.HTTP_400_BAD_REQUEST
    message_pattern: tuple[str, ...] | None = None
    headers: dict[str, str] | None = None  # <-- class-level headers
    detail_error_message: str | None = None

    def __init__(
        self,
        *args: Any,
        detail: str | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> None:
        if self.message_pattern:
            message, *message_args = self.message_pattern

        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)
        elif args and self.message_pattern:
            for key, value in zip(message_args, args):
                setattr(self, key, value)

        if detail is None and self.message_pattern:
            formatted_args = [getattr(self, arg) for arg in message_args]
            detail = message.format(*formatted_args)

        self.detail_error_message = detail

        self.log_exception(str(detail))

        merged_headers = self.headers.copy() if self.headers else {}
        if headers:
            merged_headers.update(headers)

        full_detail = {
            "msg": f"{detail}",
            "alias": self._exception_alias or "UnknownCode",
        }

        super().__init__(
            status_code=self.status_code,
            detail=full_detail,
            headers=merged_headers or None,
        )

    @property
    def alias(self) -> str:
        return self._exception_alias.value if self._exception_alias else "UnknownCode"


class ObjectNotFoundException(BaseHTTPException):
    message_pattern = ("{0} with given identifier - {1} not found", "model_name", "_id")
    status_code = status.HTTP_404_NOT_FOUND
    _exception_alias = MessageException.object_not_found

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.sentry_group = ObjectNotFoundException.__name__
        super().__init__(*args, **kwargs)


class ObjectAlreadyExistsException(BaseHTTPException):
    message_pattern = (
        "{0} with given identifier - {1} already exists",
        "model_name",
        "_id",
    )
    status_code = status.HTTP_409_CONFLICT
    _exception_alias = MessageException.object_already_exists

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.sentry_group = ObjectAlreadyExistsException.__name__
        super().__init__(*args, **kwargs)


class GoneException(BaseHTTPException):
    message_pattern = ("Resource {0} has been permanently removed", "resource_name")
    status_code = status.HTTP_410_GONE
    _exception_alias = MessageException.gone

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.sentry_group = GoneException.__name__
        super().__init__(*args, **kwargs)


class ForbiddenException(BaseHTTPException):
    message_pattern = ("Access is forbidden",)
    status_code = status.HTTP_403_FORBIDDEN
    _exception_alias = MessageException.forbidden

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.sentry_group = ForbiddenException.__name__
        super().__init__(*args, **kwargs)


class BadRequestException(BaseHTTPException):
    message_pattern: tuple[str, ...] = ("Bad request: {0}", "reason")
    status_code = status.HTTP_400_BAD_REQUEST
    _exception_alias = MessageException.bad_request

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.sentry_group = BadRequestException.__name__
        super().__init__(*args, **kwargs)
