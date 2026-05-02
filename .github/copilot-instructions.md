# Copilot Instructions for RetroApp4L

## Build, Test, and Lint Commands

- **Start all services (Docker Compose):**
  ```bash
  docker-compose up -d
  ```
- **Backend migrations:**
  ```bash
  cd backend && python manage.py migrate
  ```
- **Run all backend tests:**
  ```bash
  cd backend && python manage.py test
  ```
- **Run a single backend test:**
  ```bash
  cd backend && python manage.py test path.to.test_module
  ```
- **Lint backend code (ruff):**
  ```bash
  cd backend && ruff check .
  ```
- **Auto-fix lint issues:**
  ```bash
  cd backend && ruff check . --fix
  ```

## High-Level Architecture

- **Backend:** Django 5.2 (REST API), Django Channels (WebSocket), Celery (async tasks), PostgreSQL (db), Redis (cache/broker).
- **Frontend:** Nuxt 3 (planned, not yet implemented).
- **Dockerized:** All services run via Docker Compose. Main services: backend (API/WS), worker (Celery), db (Postgres), redis.
- **Settings:** Django settings are split by environment in `backend/config/settings/` (base, local, production).
- **Apps:** All Django apps live under `backend/apps/`.
- **Realtime:** WebSocket consumers in `backend/apps/realtime/consumers.py`.
- **Auth:** JWT via djangorestframework-simplejwt; social auth via django-allauth (provider setup required).

## Key Conventions

- All Django apps use the `apps.*` namespace and short labels for `AUTH_USER_MODEL` and migrations.
- REST endpoints use DRF class-based views and serializers per app; validation logic stays in serializers.
- API text is always in English.
- Facilitator is auto-added as Participant when creating a retrospective.
- Fallback to SQLite for local dev if Postgres env vars are missing.
- Test files are named `test_*.py` and live in `backend/tests/`.
- Code style enforced by Ruff (see `pyproject.toml`).

---

This file summarizes build/test/lint commands, architecture, and conventions for Copilot and future contributors. If you want to adjust or add coverage for other areas, let me know!