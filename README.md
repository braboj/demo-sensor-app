# Introduction

This project demonstrates a full-stack application simulating sensor 
readings from an industrial plant, with a Python backend generating data, 
storing it in a database, and exposing it via an API. A frontend application
will display the data and allow users to interact with it.

## Requirements

To install and run the application, the following software must be installed
on your system:

- [Docker](https://docs.docker.com/engine/install/)
- [git](https://git-scm.com/downloads)

## Quick Setup

Clone the repository using the following command (replace `<project-name>` 
with the name of your project):

```bash
git clone https://github.com/braboj/sensor-data-app <project-name>
```

For a specific branch, use the following command:

```bash
git clone -b <branch-name> https://github.com/braboj/sensor-data-app <project-name>
```

Navigate to the project folder and run the following command to start 
the application:

```bash
docker compose up
```

The following services will be started:

- [Frontend (Angular) / localhost:4200](http://localhost:4200)
- [Backend (Flask) / localhsot:5000](http://localhost:5000)

The backend exposes a versioned endpoint to retrieve sensor data:

```bash
curl http://localhost:5000/api/v1/sensors
```

By default, the last 100 records are returned. You can specify the number of
records to return by passing a query parameter (a bounded integer, 1-100; a
non-integer or out-of-range value returns `400`):

```bash
curl http://localhost:5000/api/v1/sensors?limit=1
```

Operational endpoints: `GET /health` (liveness — 200 if the process is up)
and `GET /ready` (readiness — 200 if the database is reachable, else 503).
## Next Steps
- To learn more about the project, please visit [Assignment](docs/history/ASSIGNMENT.md)
- To read about the solution, please visit [Solution](docs/history/SOLUTION.md)
- To contribute, please visit [Contributing](CONTRIBUTING.md)
- To leave feedback, please visit [Discussions](https://github.com/braboj/sensor-data-app/discussions)
