# encoding: utf-8
from flask import Blueprint, jsonify, request, abort
from markupsafe import escape
from .services import SensorService

# Define the blueprints for the index and API
main = Blueprint('main', __name__)
api = Blueprint('api', __name__, url_prefix='/api')

@main.route('/')
def home():
    """Route to the home page.

    Example:
        http://localhost:5000/
    """

    return escape('Backend server is running!')

@api.route('/sensors', methods=['GET'])
def get_all_sensors():
    """Route to get all sensor data with optional limit query parameter.

    Example:
        http://localhost:5000/api/sensors?limit=10
    """

    # Get the limit query parameter
    limit = request.args.get('limit', default=100, type=int)

    # Check if the limit is too high
    if not isinstance(limit, int) or limit < 1 or limit > 100:

        # Send a 400 Bad Request response
        abort(400, description="The value of 'limit' must be between 1 and 100")

    # Fetch the sensor data from the database
    data = SensorService.fetch_data(limit)

    # Return the sensor data as JSON
    return jsonify(data)