\# Containerized URL Shortener Microservice



A production-grade, highly available URL shortener microservice architected with FastAPI, PostgreSQL, Redis, and Nginx, containerized using Docker and Docker Compose.



\---



\## Architecture Overview

Client (Browser / HTTP)

│

▼

\[ Nginx Reverse Proxy ] (Port 80)

│

▼ (frontend-net)

\[ FastAPI Application ] (Port 8000)

├── (backend-net) ──► \[ PostgreSQL 16 ] (Persistent DB)

└── (backend-net) ──► \[ Redis Alpine ] (In-Memory Hit Cache)



\* \*\*Reverse Proxy:\*\* Nginx routes incoming public traffic on port 80 to the internal backend.

\* \*\*Application API:\*\* FastAPI running under an unprivileged system user (`appuser`) with an automated Docker `HEALTHCHECK`.

\* \*\*Persistent Storage:\*\* PostgreSQL stores relational URL mappings safeguarded with Docker named volumes (`pgdata`).

\* \*\*Caching \& Analytics:\*\* Redis caches short-code lookups and atomically increments redirect hit counters.

\* \*\*Network Isolation:\*\* Segregated custom bridge networks (`frontend-net` and `backend-net`) prevent direct external access to databases.



\---



\## API Specification



| Method | Endpoint | Description |

| :--- | :--- | :--- |

| `POST` | `/shorten` | Accepts JSON payload `{"url": "https://..."}` and returns a short code. |

| `GET` | `/{short\_code}` | Redirects (`307 Temporary Redirect`) to original URL and increments Redis clicks. |

| `GET` | `/stats/{short\_code}`| Returns total click analytics for the given code. |

| `GET` | `/health` | Health probe consumed by Docker healthcheck daemon. |



\---



\## Getting Started



\### Prerequisites

\* Docker Engine

\* Docker Compose v2+



Configure environment variables:

Create a .env file in the root directory:



Code snippet

POSTGRES\_USER=postgres\_admin

POSTGRES\_PASSWORD=SuperSecretDockerPassword123!

POSTGRES\_DB=shortener\_db

Launch the stack:



Bash

docker compose up -d --build

Access the service:



Interactive API Documentation (Swagger UI): http://localhost/docs



Health status: http://localhost/health



Security \& Best Practices Implemented

Multi-Stage Build: Builder pattern strips build tools and compiler artifacts from the final runtime image.



Non-Root Runtime: App runs under user appuser (UID/GID isolated) to mitigate container breakout vectors.



Isolated Networks: PostgreSQL and Redis reside entirely in backend-net and do not expose ports to the host OS.



Persistent Volumes: Named volumes guarantee zero data loss across container teardowns.

