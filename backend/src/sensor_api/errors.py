# encoding: utf-8
"""Application error types and JSON error handlers.

The API speaks JSON, so every error — aborts, 404s, and uncaught
exceptions — is rendered as an RFC 9457-style problem object
(``application/problem+json``) instead of Werkzeug's default HTML page.
"""
import logging

from flask import Flask, Response, jsonify
from flask.typing import ResponseReturnValue
from werkzeug.exceptions import HTTPException

log = logging.getLogger(__name__)

PROBLEM_CONTENT_TYPE = "application/problem+json"


class BackendError(Exception):
    """Base class for exceptions in the backend.

    Attributes:
        message (str): The error message.
        context (str): The context in which the error occurred.

    Example:
        raise BackendError(
            message=f"My error message",
            context=f"expected {int.__name__}, got {type(1.0).__name__}"
        )
    """

    def __init__(self, message: str, context: str | None = None) -> None:
        """Initializes the BackendError instance.

        Args:
            message (str): The error message.
            context (str): The context in which the error occurred.
        """
        self.message = message
        self.context = context
        super().__init__(self.message)

    def __str__(self) -> str:
        context = f"({self.context})" if self.context else ""
        return f"{self.__class__.__name__}: {self.message} {context}"

    def __repr__(self) -> str:
        return str(self)


def _problem(title: str, status: int, detail: str | None) -> Response:
    """Build a JSON problem response with the RFC 9457 media type."""
    response = jsonify({"title": title, "status": status, "detail": detail})
    response.status_code = status
    response.content_type = PROBLEM_CONTENT_TYPE
    return response


def register_error_handlers(app: Flask) -> Flask:
    """Register JSON error handlers on the Flask app."""

    @app.errorhandler(HTTPException)
    def handle_http_exception(exc: HTTPException) -> ResponseReturnValue:
        """Render aborts and HTTP errors (400/404/405/...) as JSON."""
        return _problem(exc.name, exc.code or 500, exc.description)

    @app.errorhandler(BackendError)
    def handle_backend_error(exc: BackendError) -> ResponseReturnValue:
        """Render an unexpected domain error as a generic JSON 500.

        The detail is generic so internal context is never leaked to the
        client; the actual error is logged once here.
        """
        log.error("unhandled backend error: %s", exc)
        return _problem(
            "Internal Server Error", 500, "An internal error occurred."
        )

    return app
