# 12. Glossary

Domain and technical terms used across this documentation.

| Term | Definition |
|------|------------|
| **Reading** | One sampled record of the plant's state: a temperature, a humidity, and a vibration flag, with the time it was recorded. Stored as a `SensorData` row. |
| **SensorData** | The ORM model and the `sensor_data` table: `id`, `timestamp` (indexed), `temperature`, `humidity`, `vibration`. |
| **Analog sensor** | A simulated sensor producing a floating-point value in a range (`AnalogSensor`); used for temperature and humidity. |
| **Discrete sensor** | A simulated sensor producing an integer in a range (`DiscreteSensor`); used for vibration, bounded to 0/1. |
| **Vibration (coded value)** | An integer flag: `0` = none, `1` = detected. Displayed with a legend so the code is not shown raw. |
| **Simulator worker** | The process that samples the sensors and writes a reading every `SAMPLE_INTERVAL_SECONDS` (`worker.py`). Runs separately from the web server; on the free tier it runs in-process instead. |
| **Sample interval** | The gap between readings — `SAMPLE_INTERVAL_SECONDS`, default 10 s. |
| **Application factory** | `create_app()` in `sensor_api/__init__.py` — builds and wires the Flask app (config, extensions, blueprints, error handlers) once per process; starts no threads and creates no schema. |
| **Blueprint** | Flask's mechanism for grouping routes; here one per domain — `sensors` (under `/api/v1`) and `health`. |
| **Migration** | An Alembic schema change under `backend/migrations/`, applied with `flask db upgrade`. The schema is never created at runtime. |
| **ORM** | Object-Relational Mapper — SQLAlchemy 2.x, used with typed models and `select()` queries rather than raw SQL. |
| **`limit` (param)** | The `?limit=` query parameter on `GET /api/v1/sensors` — an integer 1–100 (default 100) bounding how many readings are returned; a bad value returns 400. |
| **Server-Sent Events (SSE)** | A one-way, server-to-browser stream over plain HTTP (`text/event-stream`), consumed in the browser by `EventSource`. Used for live readings. |
| **Cursor / `fetch_since`** | The stream remembers the `id` of the last row it sent (`last_id`) and asks only for rows after it, so no reading is missed or repeated. |
| **Keep-alive comment** | An SSE `:` comment line sent when there is nothing new, to hold the connection open through proxies. |
| **Liveness (`/health`)** | A shallow check: `200 {"status":"ok"}` whenever the process is alive, touching no dependencies. |
| **Readiness (`/ready`)** | A deep check: runs `SELECT 1` and returns `200 {"status":"ready"}` or `503 {"status":"unavailable"}` if the database is unreachable. |
| **RFC 9457 problem+json** | The JSON error format (`application/problem+json`) with `title`, `status`, and `detail` — returned instead of Werkzeug HTML. |
| **`BackendError`** | The base application exception (`errors.py`); mapped, with `HTTPException`, to a problem+json response by the error handlers. |
| **CORS** | Cross-Origin Resource Sharing — scoped to `CORS_ORIGINS` (the frontend origin), never a wildcard. |
| **gunicorn** | The production WSGI server that runs the backend in the container. |
| **gevent worker** | A cooperative gunicorn worker class; lets a single instance hold many long-lived SSE connections without blocking. |
| **WSGI** | Web Server Gateway Interface — the Python standard between the web server (gunicorn) and the app (Flask). |
| **nginx (same-origin proxy)** | Serves the built SPA and reverse-proxies `/api` to the backend, so the browser sees one origin and needs no CORS. |
| **Grafana** | The dashboard service; reads the database through a provisioned datasource and renders the "Sensor Readings" charts, embedded in the SPA. |
| **Provisioning (as code)** | Grafana's datasource and dashboards are defined in version-controlled YAML/JSON and loaded at startup — never configured only through the UI. |
| **Render blueprint** | `render.yaml` — the declarative spec deploying the frontend, backend, Grafana, and a managed PostgreSQL on the free tier. |
| **autoDeploy** | Render's push-triggered redeploy: a push to `main` rebuilds and redeploys each service. |
| **Cold start** | The delay (~30–60s) when a free-tier instance wakes after spinning down from inactivity. |
| **Standalone component** | An Angular component that declares its own imports without an NgModule; the frontend is built entirely from these. |
| **arc42** | The architecture documentation template used by this `docs/arc42/` set ([arc42.org](https://arc42.org)). |
