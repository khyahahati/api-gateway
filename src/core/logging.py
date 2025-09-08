import logging
import sys
import json
import time
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class StructuredFormatter(logging.Formatter):
    """
    A custom logging formatter that outputs logs in a structured JSON format.

    This formatter is designed for machine-readable logs, making them easier to
    parse and analyze with log aggregation systems.

    It includes:
    - `timestamp`: The ISO 8601 formatted timestamp in UTC.
    - `level`: The log level (e.g., INFO, ERROR).
    - `logger`: The name of the logger.
    - `message`: The log message.
    - `extra_fields`: Additional key-value pairs from the log record's `extra` dictionary.
    - `exception`: A formatted traceback if an exception is present.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a log record into a JSON string.

        Args:
            record: The logging.LogRecord instance to be formatted.

        Returns:
            A JSON-formatted string representing the log entry.
        """
        timestamp = datetime.fromtimestamp(record.created, timezone.utc).isoformat().replace("+00:00", "Z")

        log_entry: Dict[str, Any] = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all incoming and outgoing HTTP requests and responses.

    This middleware intercepts requests to provide comprehensive, structured logs
    for monitoring and debugging. It logs key information such as request method,
    URL, client IP, and a unique request ID for tracing. It also records the
    duration and status code of the response.
    """

    def __init__(self, app, logger_name: str = "api_gateway.requests"):
        """
        Initializes the middleware with a specified logger name.

        Args:
            app: The ASGI application instance.
            logger_name: The name of the logger to be used by the middleware.
        """
        super().__init__(app)
        self.logger = logging.getLogger(logger_name)

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Dispatches the incoming request, logs it, and processes the response.

        This method is the core of the middleware, handling the request-response cycle.
        It adds a unique request ID to the request state and response headers for
        request tracing.

        Args:
            request: The incoming FastAPI request.
            call_next: A function that awaits the next middleware or the endpoint.

        Returns:
            The FastAPI response object.

        Raises:
            Exception: Re-raises any exceptions that occur during request processing.
        """
        start_time = time.time()
        client_ip = self.get_client_ip(request)
        
        request_id = request.headers.get("X-Request-ID") or self.generate_request_id()
        request.state.request_id = request_id

        self.logger.info(
            "Incoming request",
            extra={
                "extra_fields": {
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "client_ip": client_ip,
                    "user_agent": request.headers.get("user-agent", ""),
                    "content_length": request.headers.get("content-length", 0),
                }
            },
        )

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            self.logger.info(
                "Request completed",
                extra={
                    "extra_fields": {
                        "request_id": request_id,
                        "method": request.method,
                        "url": str(request.url),
                        "status_code": response.status_code,
                        "duration_ms": round(duration * 1000, 2),
                        "client_ip": client_ip,
                    }
                },
            )

            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as e:
            duration = time.time() - start_time

            self.logger.error(
                "Request failed",
                extra={
                    "extra_fields": {
                        "request_id": request_id,
                        "method": request.method,
                        "url": str(request.url),
                        "error": str(e),
                        "duration_ms": round(duration * 1000, 2),
                        "client_ip": client_ip,
                    }
                },
                exc_info=True,
            )
            raise

    def get_client_ip(self, request: Request) -> str:
        """
        Retrieves the client's IP address, accounting for proxy headers.

        It checks for `X-Forwarded-For` and `X-Real-IP` headers, which are
        commonly used when the application is running behind a proxy or load balancer.

        Args:
            request: The FastAPI request object.

        Returns:
            The client IP address as a string, or "unknown" if not found.
        """
        headers = {k.lower(): v for k, v in request.headers.items()}
        forwarded_for = headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = headers.get("x-real-ip")
        if real_ip:
            return real_ip

        return request.client.host or "unknown"

    def generate_request_id(self) -> str:
        """
        Generates a unique request ID.

        Returns:
            A string representation of a UUID, truncated to 8 characters for readability.
        """
        return str(uuid.uuid4())[:8]


def setup_logging() -> None:
    """
    Configures the root logger for the application.

    This function sets up a structured JSON logger that can be configured
    using environment variables:
    - `LOG_LEVEL`: Sets the minimum log level (e.g., INFO, DEBUG, ERROR). Defaults to INFO.
    - `LOG_FORMAT`: Sets the output format, either "json" or "text". Defaults to "json".
    - `LOG_FILE`: If set, logs will also be written to this file path.
    """
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "json")

    valid_levels = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}
    if log_level_str not in valid_levels:
        log_level_str = "INFO"

    log_level = getattr(logging, log_level_str)

    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    if log_format.lower() == "json":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    log_file = os.getenv("LOG_FILE")
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    root_logger.setLevel(log_level)

    logging.getLogger("api_gateway").setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logger = logging.getLogger("api_gateway.startup")
    logger.info(
        "Logging configured",
        extra={
            "extra_fields": {
                "log_level": log_level_str,
                "log_format": log_format,
                "log_file": log_file,
            }
        },
    )


def get_logger(name: str) -> logging.Logger:
    """
    Retrieves a logger instance with a standardized naming convention.

    Args:
        name: The name of the logger (typically the module or class name).

    Returns:
        A configured logging.Logger instance prefixed with 'api_gateway.'.
    """
    return logging.getLogger(f"api_gateway.{name}")


class LoggerMixin:
    """
    A mixin class that provides a standardized logger instance to any class it's mixed into.

    This simplifies the process of adding logging to classes by providing a `logger`
    property and convenient helper methods (`log_info`, `log_error`, etc.) for
    consistent structured logging.
    """

    @property
    def logger(self) -> logging.Logger:
        """
        A property that lazily initializes a logger for the class.

        Returns:
            The configured logging.Logger instance.
        """
        if not hasattr(self, "_logger"):
            self._logger = get_logger(self.__class__.__name__.lower())
        return self._logger

    def log_debug(self, message: str, **kwargs: Any) -> None:
        """Logs a debug message with extra fields."""
        self.logger.debug(message, extra={"extra_fields": kwargs})

    def log_info(self, message: str, **kwargs: Any) -> None:
        """Logs an info message with extra fields."""
        self.logger.info(message, extra={"extra_fields": kwargs})

    def log_warning(self, message: str, **kwargs: Any) -> None:
        """Logs a warning message with extra fields."""
        self.logger.warning(message, extra={"extra_fields": kwargs})

    def log_error(self, message: str, error: Optional[Exception] = None, **kwargs: Any) -> None:
        """
        Logs an error message with extra fields and optional exception information.

        Args:
            message: The error message.
            error: An optional exception object to include the traceback.
            **kwargs: Additional key-value pairs to include in the log record.
        """
        if error:
            kwargs["error"] = str(error)
        self.logger.error(message, extra={"extra_fields": kwargs}, exc_info=error)
