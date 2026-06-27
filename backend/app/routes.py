# encoding: utf-8
from flask import Blueprint, abort, jsonify, request
from markupsafe import escape

from .services import DEFAULT_LIMIT, MAX_LIMIT, MIN_LIMIT, SensorService

# A tiny root page plus the versioned JSON API.
main = Blueprint('main', __name__)
api = Blueprint('api', __name__, url_prefix='/api/v1')


@main.route('/')
def home():
    """Root landing page for the backend service.

    Example:
        http://localhost:5000/
    """

    return escape('Backend server is running!')


def _parse_limit():
    """Validate the ?limit= query parameter at the boundary.

    Returns a bounded integer in ``[MIN_LIMIT, MAX_LIMIT]``. A missing value
    falls back to ``DEFAULT_LIMIT``; a non-integer or out-of-range value is
    rejected with ``400`` — never silently coerced to a default.
    """
    raw = request.args.get('limit')
    if raw is None:
        return DEFAULT_LIMIT

    try:
        limit = int(raw)
    except (TypeError, ValueError):
        abort(400, description="The 'limit' parameter must be an integer")

    if limit < MIN_LIMIT or limit > MAX_LIMIT:
        abort(
            400,
            description=(
                f"The 'limit' parameter must be between "
                f"{MIN_LIMIT} and {MAX_LIMIT}"
            ),
        )

    return limit


@api.route('/sensors', methods=['GET'])
def get_all_sensors():
    """Return the most recent sensor readings, newest first.

    Example:
        http://localhost:5000/api/v1/sensors?limit=10
    """

    limit = _parse_limit()
    data = SensorService.fetch_data(limit)
    return jsonify(data)
