# encoding: utf-8
from flask import Blueprint, Response, current_app, jsonify, request

from .events import sensor_event_stream
from .schemas import parse_limit, serialize_reading
from .services import SensorService

api = Blueprint('sensors', __name__, url_prefix='/api/v1')


@api.route('/sensors', methods=['GET'])
def get_all_sensors():
    """Return the most recent sensor readings, newest first.

    Example:
        http://localhost:5000/api/v1/sensors?limit=10
    """

    limit = parse_limit(request.args.get('limit'))
    rows = SensorService.fetch_data(limit)
    return jsonify([serialize_reading(row) for row in rows])


@api.route('/sensors/stream', methods=['GET'])
def stream_sensors():
    """Stream sensor readings live over SSE (``text/event-stream``).

    The browser opens one long-lived connection (``EventSource``) and receives
    each new reading as it is recorded, instead of polling ``/sensors``. The
    real application object is captured here and handed to the generator so it
    can manage its own app context independently of this request.
    """

    app = current_app._get_current_object()
    response = Response(
        sensor_event_stream(app),
        mimetype='text/event-stream',
    )
    # No caching, and disable proxy buffering (nginx / Render honour
    # X-Accel-Buffering) so each event flushes to the client immediately.
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    return response
