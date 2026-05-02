# Sprint 1 — Foundation

## Contexto

Primeira sprint do projeto RetroApp 4L. Estabelece toda a base estrutural do projeto: estrutura de repositórios, Docker, banco de dados, autenticação e criação de sessões.

**Referência no PRD:** Seções 6 (Stack Tecnológica), 8 (Modelo de Dados), 12.3 (Planejamento)

---

## Objetivos

1. Estruturar os repositórios `retroapp4l-backend` e `retroapp4l-frontend`
2. Configurar ambiente local com `docker-compose` (PostgreSQL + Redis)
3. Implementar modelo de autenticação com `django-allauth` (local + OAuth opcional)
4. Criar migrations iniciais para todos os modelos (users, retrospectives, milestones, participants, accesslog)
5. Implementar endpoint de criação de sessão com `team_key`

---

## Entregáveis

### Backend (Django)

- [ ] Estrutura de apps conforme PRD seção 6.6:
  ```
  retroapp4l/
  ├── config/              # settings, urls, asgi, wsgi
  ├── apps/
  │   ├── users/           # Model User, OAuth callback
  │   ├── retrospectives/  # Retrospective, Participant, Milestone, AccessLog
  │   ├── cards/           # Card, CardVote
  │   ├── actions/         # ActionItem
  │   └── realtime/        # Consumers (esqueleto)
  ├── tasks/               # Celery tasks (esqueleto)
  └── tests/               # Espelha apps/
  ```

- [ ] `docker-compose.yml` com serviços:
  - PostgreSQL (local, para desenvolvimento)
  - Redis (local, para desenvolvimento)

- [ ] `Dockerfile` para aplicação Django (ASGI/Daphne)
  - `Dockerfile.worker` para Celery worker

- [ ] `requirements.txt` ou `pyproject.toml` com dependências:
  - Django 5.x
  - Django REST Framework 3.15+
  - Django Channels 4.x
  - Daphne 4.x
  - Celery 5.x
  - django-allauth 0.6x+
  - Redis 7.x (channel layer)
  - ruff (linting)
  - pytest-django

- [ ] **App `users`:**
  - Custom User model com UUID PK
  - Campos: `name`, `email` (unique), `password`, `oauth_provider`, `oauth_id`, `avatar_url`, `is_active`, `created_at`
  - Configuração do `django-allauth` para auth local (e-mail + senha)
  - Configuração de OAuth opcional (Google, GitHub) via `django-allauth`
  - Variável de ambiente `ALLOWED_EMAIL_DOMAINS` (lista de domínios permitidos; vazia = todos aceitos)

- [ ] **App `retrospectives` — Migrations iniciais:**
  - Model `Retrospective`:
    - Campos: `id` (UUID PK), `title`, `sprint_name` (nullable), `team_key` (obrigatório, slug), `facilitator` (FK User), `status` (choices: `setup|lobby|presentation|check|board|grouping|voting|discussion|actions|closed`), `invite_token` (UUID, unique, nullable), `invite_revoked_at` (nullable), `max_votes_per_user` (default=3), `skip_check_phase` (default=False), `timer_started_at` (nullable), `timer_paused_at` (nullable), `timer_duration_seconds` (nullable), `created_at`, `closed_at` (nullable)
  - Model `Milestone`:
    - Campos: `id` (UUID PK), `retrospective` (FK), `author` (FK User), `category` (choices: `achievement|challenge|change|recognition|other`), `description` (TextField, máx. 500), `created_at`
  - Model `Participant`:
    - Campos: `id` (UUID PK), `retrospective` (FK), `user` (FK), `votes_remaining` (IntegerField), `joined_at`
    - `unique_together: (retrospective, user)`
  - Model `AccessLog`:
    - Campos: `id` (UUID PK), `retrospective` (FK), `action` (choices: `opened|closed|participant_joined`), `triggered_by` (FK User, nullable), `participant` (FK User, nullable), `timestamp`

- [ ] **App `cards` — Migrations iniciais:**
  - Model `Card`:
    - Campos: `id` (UUID PK), `retrospective` (FK), `author` (FK User), `column` (choices: `loved|loathed|longed|learned`), `content` (TextField, máx. 500), `group` (FK 'self', nullable), `position` (default=0), `created_at`
  - Model `CardVote`:
    - Campos: `id` (UUID PK), `card` (FK), `voter` (FK User), `created_at`
    - `unique_together: (card, voter)`

- [ ] **App `actions` — Migrations iniciais:**
  - Model `ActionItem`:
    - Campos: `id` (UUID PK), `retrospective` (FK), `card` (FK, nullable), `description` (TextField), `assignee` (FK User), `due_date` (nullable), `status` (choices: `pending|in_progress|done`), `created_at`

- [ ] **API REST — Endpoints:**
  - `POST /api/auth/register/` — Registro local (e-mail + senha)
  - `POST /api/auth/login/` — Login local
  - `POST /api/auth/logout/` — Logout
  - `POST /api/retrospectives/` — Criar sessão (requer autenticação)
    - Payload: `title`, `sprint_name`, `team_key` (obrigatório), `description` (opcional)
    - Sessão inicia em status `setup`
  - `GET /api/retrospectives/` — Listar sessões do usuário autenticado
  - `GET /api/retrospectives/{id}/` — Detalhes de uma sessão
  - `GET /api/teams/suggestions/` — Sugestões de `team_key` usados anteriormente pelo facilitador

- [ ] **Settings (`config/settings/`):**
  - Split entre `base.py`, `local.py`, `production.py`
  - Database: PostgreSQL (via env vars)
  - Redis URL (via env vars)
  - `AUTH_USER_MODEL = 'users.User'`
  - `django-allauth` configuration
  - CORS headers (para frontend Nuxt)
  - `ALLOWED_EMAIL_DOMAINS` (env var)

- [ ] **Celery:**
  - Configuração básica (`config/celery.py`)
  - Beat scheduler configurado (esqueleto, timer será implementado na Sprint 2)

---

## Requisitos Funcionais Cobertos

| ID | Descrição | Status |
|---|---|---|
| RF-01 | Auth local (e-mail + senha) via `django-allauth`; OAuth opcional; `ALLOWED_EMAIL_DOMAINS` | ✅ |
| RF-02 | Facilitador cria sessão com `team_key` e nome da sprint; inicia em `setup` | ✅ |

---

## Requisitos Não Funcionais

- Linting: `ruff` configurado para Python
- Todos os testes devem passar: `python manage.py test`
- `docker-compose up -d` deve iniciar PostgreSQL e Redis sem erros

---

## Critérios de Done

- [ ] `docker-compose up -d` inicia PostgreSQL e Redis
- [ ] `python manage.py migrate` executa sem erros (todas as migrations criadas)
- [ ] `python manage.py test` passa sem falhas
- [ ] `ruff check .` sem erros
- [ ] É possível registrar um usuário via API
- [ ] É possível fazer login e obter token JWT
- [ ] É possível criar uma sessão com `team_key`
- [ ] É possível listar sugestões de `team_key` para um facilitador

---

## Handoff

Ao finalizar, gerar rascunho do `SPRINT_2_HANDOFF.md` seguindo estrutura definida no PRD seção 12.2.

---

## Referências do PRD

- Seção 6: Stack Tecnológica
- Seção 6.6: Estrutura de apps Django
- Seção 8: Modelo de Dados completo
- Seção 11.5: Qualidade de código (ruff, testes)
