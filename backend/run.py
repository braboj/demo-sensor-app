"""Local development entrypoint.

The shipped container runs ``gunicorn "sensor_api:create_app()"`` instead —
this module is a zero-config convenience for running the dev server locally
(``python run.py``). It puts ``src/`` on the path so ``sensor_api`` resolves
without setting ``PYTHONPATH``. The Werkzeug debugger is opt-in via
``FLASK_DEBUG`` and must never be enabled in a deployed environment.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from sensor_api import create_app  # noqa: E402  -- import after sys.path setup

app = create_app()

if __name__ == '__main__':
    debug = os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    app.run(host=host, port=5000, debug=debug)
