
## Overview

### Requirements

- Create a simple web application that displays sensor data in real-time

### Timeframe

- One week to deliver the task
- Not more than 4-8 hours to complete the task

### Identified Risks

- Limited experience with websockets
- No experience with asyncio programming
- No experience with Angular + TypeScript 

### Risk Mitigation

- Focus on delivering the minimal viable product (MVP)
- Reduce testing efforts minimum (unit tests, smoke tests)
- Use tools such as chatGPT to help deliver quickly a viable solution
- 5-6 hours max for the backend including web-sockets
- 5-6 hours max for the frontend including Grafana integration
- After the MVP is delivered, ask for feedback and improve the solution

### Milestones

- V0.0.1.0 - Backend with REST API without websockets
- V0.0.2.0 - Simple web app to poll the API
- V0.0.3.0 - Grafana integration and charting
- V0.0.4.0 - Add websockets to deliver real-time data
- V0.0.5.0 - Add optional features as requested in the documentation
- V0.0.6.0 - Add CI/CD pipeline with GitHub Actions


## V0.0.1.0 - Backend with REST API without websockets

The task assignment didn't specify the framework to use for the backend, so 
I decided to use Flask as I have more experience with it and it's easier to
setup and use for small projects. It offers also a simple way to integrate 
websockets and it's easy to test. 

**Technology Stack**

- Flask for REST API as WSGI application
- SQLAlchemy for database integration
- Websockets for real-time data production
- Postgres for data storage

The backend will be containerized with Docker and I will use a simple 
Dockerfile and docker-compose file to run the app. The application consists of 
two services: the Flask app and the Postgres database.

**Features**

- Simulated sensor data stored in the database every 10 seconds
- REST API fetching sensor data from the database
- Dockerize the backend with docker compose
- Tests for the REST API

**Solution Steps**

1. Create a simple hello world flask app with Docker
2. Implement the sensor data simulation (data logic)
3. Add the routes with the simulated data (routing logic)
4. Add the database integration using SQLAlchemy (database logic)
5. Test the REST API using the test client from Flask (integration)
6. Research websockets and implement the real-time data production
7. Documentation and tag the solution

**Timetable**

| Time | Task                                                   |
|------|--------------------------------------------------------|
| 0.5h | 1) Setup the Flask app with Docker                     |
| 0.5h | 2) Implement the sensor data simulation                |
| 0.5h | 3) Add the routes with dummy data and tests            |
| 1h   | 4) Add the database integration with Postgres + tests  |
| 1h   | 5) Add configuration using the instance folder + tests |
| 2h   | 6) Review and research websockets (only scripts)       |
| 0.5h | 7) Documentation and cleanup before Tag V0.0.1.0       |

**Links:**
- https://www.jetbrains.com/help/pycharm/using-docker-as-a-remote-interpreter.html#summary
- https://flask.palletsprojects.com/en/stable/


## V0.0.2.0 - Simple frontend to poll the API

Unfortunately, I don't have experience with Angular and TypeScript, so I will
use this opportunity to learn and implement a simple frontend app using these
technologies. I will also use assisting tools such as chatGPT to help me 
deliver the solution as quickly as possible. 

**Technology Stack**

- Angular for frontend
- TypeScript for the frontend logic
- Grafana for charting the data
- Any other libraries as needed

**Features**

- Simple frontend app to poll the backend
- Dockerized Angular app

**Solution Steps**

The frontend will be containerized with Docker and I will use a simple
Dockerfile and docker-compose file to run the app. The application consists of
two services: the Angular app and the Grafana service. The Grafana service 
offers a REST API that can be used for configuration and charting.

1. Install node.js and Angular CLI
2. Install WebStorm and create a new Angular project
3. Follow the tutorial to create a simple Angular app
4. Implement a simple frontend app to poll the REST API
5. Dockerize the Angular app and update the docker-compose file

**Timetable**

| Time | Task                                                      |
|------|-----------------------------------------------------------|
| 0.5h | 1) Install node.js and Angular CLI                        |
| 0.5h | 2) Install WebStorm and create a new Angular project      |
| 4h   | 3) Follow the tutorial to create a simple Angular app     |
| 1h   | 4) Implement a simple frontend app to poll the REST API   |
| 0.5h | 5) Dockerize the Angular app and update the docker file   |
| 1.5h | Solve problem with db service and backend synchronization |
| 0.5h | Documentation and Cleanup before tag V0.0.2.0             |


**Links**
- https://angular.dev/tutorials/first-app
- https://blog.bouzekri.net/2017-11-03-debug-angular-app-in-webstorm.html
- https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
- https://en.wikipedia.org/wiki/Bazel_(software)

