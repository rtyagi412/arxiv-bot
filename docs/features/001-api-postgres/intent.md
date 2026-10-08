# Intent 001: Local FastAPI and PostgreSQL Health Check

Author: Rahul. Status: accepted. Date: 2026-10-08

## Problem

The project needs a locally running FastAPI backend connected
to PostgreSQL running in Docker Compose.

There is currently no health endpoint that reports the
availability of both the API and PostgreSQL in a single response.

Developers need to identify whether the application and its
database dependency are healthy.

## Proposed outcome

- Add a FastAPI application that runs locally.
- Run PostgreSQL using Docker Compose.
- Connect the local FastAPI application to PostgreSQL.
- Expose a GET /health endpoint.
- Check FastAPI and PostgreSQL health separately.
- Return the status of both services in a single JSON response.
- Return an overall health status based on the individual
  service statuses.
- Report degraded health when PostgreSQL is unavailable.

## Affected users and systems

- Developers running the application locally.
- FastAPI application.
- PostgreSQL database.
- Docker Compose environment.

## Constraints

- FastAPI must run locally, outside Docker.
- PostgreSQL must run inside Docker Compose.
- FastAPI must connect to the containerized PostgreSQL database.
- The health endpoint must return individual service statuses.
- PostgreSQL health must be verified through an actual
  database connectivity check.
- Database unavailability must not prevent FastAPI from
  serving the health endpoint.
- Both service statuses must be returned in a single response.

## Out of scope

- Running FastAPI inside Docker.
- Database migrations.
- Application tables and data models.
- CRUD endpoints.
- Authentication and authorization.
- Production deployment configuration.

## Success criteria

1. Running `docker compose up -d` starts PostgreSQL.

2. The FastAPI application starts successfully on the
   local machine.

3. When FastAPI and PostgreSQL are healthy, GET /health
   returns HTTP 200:

   {
     "status": "ok",
     "services": {
       "api": "ok",
       "database": "ok"
     }
   }

4. When PostgreSQL is stopped, GET /health returns
   HTTP 503:

   {
     "status": "degraded",
     "services": {
       "api": "ok",
       "database": "degraded"
     }
   }

5. Restarting PostgreSQL restores the health endpoint
   to HTTP 200 with both services reporting "ok".

6. API and database health statuses are reported
   independently within the same response.

7. PostgreSQL can run without requiring a local
   PostgreSQL installation.

## Open questions

None.