"""Local development entrypoint.

The shipped container runs ``gunicorn "app:create_app()"`` instead — this
module is a convenience for running the dev server locally. The Werkzeug
debugger is opt-in via ``FLASK_DEBUG`` and must never be enabled in a
deployed environment.
"""
import os

from app import create_app

app = create_app()

if __name__ == '__main__':
    debug = os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    app.run(host=host, port=5000, debug=debug)
