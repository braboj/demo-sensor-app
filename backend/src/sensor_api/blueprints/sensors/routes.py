# encoding: utf-8
from flask import Blueprint, jsonify, request

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
