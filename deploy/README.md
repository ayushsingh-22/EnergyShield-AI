# Deployment (Phase 12)

Local development uses the root `docker-compose.yml` directly (bind-mounted
source, `uvicorn --reload`, the Vite dev server). This directory holds the
production-oriented overlay.

## Production-style local run

```bash
cp .env.example .env   # fill in real POSTGRES_PASSWORD / NEO4J_PASSWORD
docker compose -f docker-compose.yml -f deploy/docker-compose.prod.yml up --build -d
```

What the overlay changes versus the dev compose file:

- `backend`/`frontend` build from immutable images (no source bind-mount);
  the frontend build (`frontend/Dockerfile.prod`) runs `vite build` and
  serves the static output instead of the dev server.
- Every secret (`POSTGRES_PASSWORD`, `NEO4J_PASSWORD`, etc.) must come from
  the environment - there are no `change-me` fallback defaults, so a
  missing secret fails the `docker compose` command immediately instead of
  silently deploying with a demo password.
- `postgres`/`redis` no longer publish ports to the host; only the
  `backend` (8000), `frontend` (5173), and Neo4j bolt (7687) ports are
  exposed.

## What this is not

This is a single-host Docker Compose deployment suitable for a demo or a
small pilot, not a production Kubernetes/cloud manifest - none exists in
this repository. Extending to a managed environment (ECS, Cloud Run, a
Kubernetes cluster) means replacing this overlay with that platform's own
manifests; the application itself has no Compose-specific code (all
configuration is via environment variables per `.env.example`), so the
containers themselves port over directly.
