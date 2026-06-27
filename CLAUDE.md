# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Commands

### Backend (Django)

```bash
cd backend

# Run dev server (Daphne ASGI)
python manage.py runserver

# Migrations
python manage.py migrate
python manage.py makemigrations

# Tests
python manage.py test               # all tests
python manage.py test apps.cards    # single app
pytest                              # via pytest-django

# Celery worker + beat (single process)
celery -A config worker -B -l info

# Lint
ruff check .
ruff format .
```

### Frontend (Nuxt 3)

```bash
cd frontend

npm run dev            # dev server
npm run build          # production build
npm run lint           # ESLint
npm run lint:fix       # ESLint autofix
npm run format         # Prettier
npm run format:check   # Prettier check
npm run test:e2e       # Playwright
npm run test:e2e:ui    # Playwright with UI
```

### Docker (local)

```bash
# Local dev (backend :8000, frontend :3000, postgres :5432, redis :6379)
docker compose up --build

# Dev with hot reload volumes
docker compose -f docker-compose.dev.yml up --build

# Production
docker compose -f docker-compose.prod.yml up -d --build

# Create superuser after prod deploy
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

---

## Architecture

### Monorepo layout

```
backend/
  apps/
    users/          # Custom User model, JWT auth, Turnstile validation
    retrospectives/ # Core domain: Retrospective, Milestone, Participant, AccessLog
    cards/          # Card, CardVote — the 4L board items
    actions/        # ActionItem — created in discussion, reviewed in actions phase
    realtime/       # Django Channels consumer, state_machine.py, timer signals
  config/           # Django settings, ASGI, Celery config
  tasks/            # Celery tasks (timer sync, invite auto-block)
  tests/            # pytest-django tests

frontend/
  pages/            # File-based Nuxt routing
  components/
    phases/         # One component per retro phase (SetupView, BoardView, …)
  stores/           # Pinia: auth, retro, participants, timer, toast, guest
  composables/      # useApiClient, useWebSocket, usePhase, useTimer, useExportMarkdown
  assets/css/       # tokens.css (--ds-*, --fg-*, --bg-*, --border-*), tailwind.css
```

### Request flow

REST hydrates initial state; WebSocket propagates mutations in real time.

1. Frontend connects to `/ws/retrospectives/{id}/?token={JWT}`.
2. Server sends `session.snapshot` (phase + action_items only; cards/votes/participants are empty).
3. Frontend immediately fetches cards, votes, milestones, participants via REST.
4. Domain mutations (card save/delete, vote, action item, phase change) trigger Django signals → Channel Group broadcast.

### Phase machine (critical divergence)

Two conflicting representations exist:

- `backend/apps/realtime/state_machine.py` — defines linear transitions with `presentation` before `check`. **Not enforced**: the WebSocket consumer (`RetroConsumer`) never calls `is_valid_transition`; it only checks that the destination phase is a valid `RetrospectiveStatus` choice and that the sender is the facilitator.
- `frontend/composables/usePhase.ts` — **actual order** followed by the UI: `setup → lobby → check → presentation → board → grouping → voting → discussion → actions → closed`. `skip_check_phase=true` jumps from `lobby` to `presentation`.

The backend accepts any valid phase sent by the facilitator. Phase enforcement is purely a frontend concern.

### Authentication

- JWT (SimpleJWT): access 8h, refresh 7d, blacklisted on logout.
- JWT passed as `Authorization: Bearer …` for REST; as `?token=` query string for WebSocket.
- Guest users are real `User` rows with `is_guest=True`, unusable password and an internal synthetic email. They enter only via invite link.
- Cloudflare Turnstile is required on registration; key validated in `apps/users/turnstile.py`.
- Google OAuth button exists in the frontend but the provider is not configured in the backend; clicking it will fail.

### Key data relationships

- `Retrospective.facilitator` → `User` (non-guest who created the session).
- `Participant` links `User` ↔ `Retrospective`; `votes_remaining` lives here.
- `ActionItem.assignee` → `Participant` (not `User`); pass `assignee_id` as the Participant UUID.
- `Card.group` → self-FK to parent `Card`; `group_parent_id` is the public alias. Cards in groups are one level deep only (parent → children, no nesting).
- `team_key` (SlugField) groups retrospectives across sessions; there is no `Team` entity.

### Anonymous cards

`Card.author` is always persisted. When `is_anonymous=True`, serializers return `author=null`, `author_name=null`, `author_display="Anonymous participant"` and include `can_edit` (computed per-user) so users can still edit their own cards without the UI revealing authorship. `allow_self_vote=False` uses the real author internally to block self-voting even on anonymous cards.

### Celery tasks

- `tasks.timer.timer_sync` — emits `timer.sync` every 5 s while a timed phase is running.
- `tasks.invite.auto_block_invite` — fires 120 s after `reopen-entry` to block the temporary invite window.
- Worker runs with Beat embedded (`celery -A config worker -B`); not HA.

### Frontend state management (Pinia stores)

| Store | Responsibility |
|---|---|
| `auth` | JWT tokens, current user, login/register/logout, localStorage persistence |
| `retro` | Active session, cards, votes, action items, previous actions, history |
| `participants` | Participant list, online IDs (estimated from WS events), invite status |
| `timer` | Timer hydration, local countdown, pause/resume |
| `guest` | Guest name/email for invite prefilling |
| `toast` | Global toast queue |

### Design system

- TailwindCSS with `Poppins` as `font-sans`; `JetBrains Mono` used inline in some screens.
- Custom Tailwind palette: `brand`, `success`, `warning`, `danger`, `gray`.
- CSS custom properties in `assets/css/tokens.css`: `--ds-*`, `--fg-*`, `--bg-*`, `--border-*`.
- Utility classes in `assets/css/tailwind.css`: `panel`, `field-input`, `button-primary`, `button-secondary`.
- Icons: `@heroicons/vue` is declared and works. `mdi mdi-*` classes also appear in the UI but **no MDI package is installed**; those icons will not render without external CSS.

---

## Environment variables

Copy `backend/.env.example` for local dev. Key variables:

| Variable | Notes |
|---|---|
| `DB_ENGINE` | Set to `postgres` for PostgreSQL; omit for SQLite |
| `REDIS_URL` | Required for Celery and Channel Layer |
| `USE_IN_MEMORY_CHANNEL_LAYER` | `false` in any multi-process setup |
| `CLOUDFLARE_TURNSTILE_SECRET_KEY` | Required for registration |
| `NUXT_PUBLIC_API_BASE` | Frontend → backend REST base URL |
| `NUXT_PUBLIC_WS_BASE` | Frontend → backend WS base URL |
| `NUXT_PUBLIC_TURNSTILE_SITE_KEY` | Cloudflare site key for the registration form |
| `ALLOWED_EMAIL_DOMAINS` | Optional; restricts registration by domain |

---

## Known limitations to keep in mind

- Phase transitions are not validated linearly on the backend; the state machine in `state_machine.py` is not wired to the consumer.
- `session.snapshot` over WebSocket is partial — frontend must fetch most state via REST after connecting.
- Milestone presentation index (`presentation_indices`) is in-memory per worker process; it loses state on restart and does not scale across multiple workers.
- `PUT /votes-config/` only changes `max_votes_per_user`; `allow_self_vote` cannot be changed after creation.
- The backend blocks card mutations only in `discussion`, `actions`, and `closed`; the API is more permissive than the UI.
