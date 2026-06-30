# encoding: utf-8
"""Root landing page plus operational liveness/readiness endpoints.

``/health`` answers "is the process up?" with no dependencies, so an
orchestrator never restarts a healthy container just because the database
blipped. ``/ready`` answers "can it serve traffic?" by probing the
database, returning 503 when it cannot.
"""
import logging

from flask import Blueprint, jsonify
from flask.typing import ResponseReturnValue
from markupsafe import escape
from sqlalchemy import literal, select

from ...extensions import db

log = logging.getLogger(__name__)

health = Blueprint('health', __name__)


@health.route('/')
def home() -> ResponseReturnValue:
    """Root landing page for the backend service."""
    return escape('Backend server is running!')


@health.route('/health')
def liveness() -> ResponseReturnValue:
    """Liveness: 200 if the process is alive. No dependencies, no auth."""
    return jsonify(status='ok'), 200


@health.route('/ready')
def readiness() -> ResponseReturnValue:
    """Readiness: 200 only if the database is reachable, else 503."""
    try:
        db.session.execute(select(literal(1)))
    except Exception:
        log.warning("readiness check failed: database unreachable")
        return jsonify(status='unavailable'), 503

    return jsonify(status='ready'), 200
