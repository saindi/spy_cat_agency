from loguru import logger

from collections.abc import Callable


class LoggerMixin:
    log_level: str | None = "debug"
    log_message_pattern: tuple | None = None

    def log_exception(self, detail: str | None = None) -> None:
        if self.log_level in {"debug", "info", "warning", "error", "critical", "exception"}:
            logger_method: Callable = getattr(logger, self.log_level)

            if self.log_message_pattern:
                log_message, *args = self.log_message_pattern
                formatted_args = [getattr(self, arg) for arg in args]
                logger_method(log_message, *formatted_args)
            else:
                logger_method(detail)
