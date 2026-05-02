# SPRINT 8 HANDOFF — RetroApp 4L

## Estado do repositório

- **Branch principal:** `main`
- **Última sprint concluída:** Sprint 7 (MVP Polish — Presença, Controle de Entrada, Notificações, CI/CD)
- **Migrations pendentes:** Nenhuma. Migration `retrospectives.0004_add_invite_temporarily_open_until` aplicada.
- **Build frontend:** ✅ `npm run build` → `✨ Build complete!`
- **Testes backend:** ✅ 39 testes OK (29 legados + 10 novos em `tests/retrospectives/test_entry_presence.py`)

---

## O que foi implementado e está funcionando (Sprint 7)

### Backend

| Entregável | Arquivo | Status |
|---|---|---|
| Campo `invite_temporarily_open_until` no model `Retrospective` | `apps/retrospectives/models.py` | ✅ |
| `LINK_REOPENED` e `LINK_AUTO_BLOCKED` em `AccessLogAction` | `apps/retrospectives/models.py` | ✅ |
| Migration 0004 | `apps/retrospectives/migrations/0004_add_invite_temporarily_open_until.py` | ✅ aplicada |
| `POST /retrospectives/{id}/reopen-entry/` | `apps/retrospectives/views.py` → `ReopenEntryView` | ✅ |
| `GET /retrospectives/{id}/invite-status/` | `apps/retrospectives/views.py` → `InviteStatusView` | ✅ |
| `GET /retrospectives/{id}/presence/` | `apps/retrospectives/views.py` → `PresenceView` | ✅ |
| Celery task `auto_block_invite` | `tasks/invite.py` | ✅ |
| Handler WS `invite_status_updated` no consumer | `apps/realtime/consumers.py` | ✅ |
| Testes novos endpoints (10 casos) | `tests/retrospectives/test_entry_presence.py` | ✅ |
| CI/CD GitHub Actions (lint, test, docker build, frontend build) | `.github/workflows/ci.yml` | ✅ |

### Frontend

| Entregável | Arquivo | Status |
|---|---|---|
| `ParticipantPanel.vue` reescrito com countdown, badge colorido, ícones dinâmicos | `components/participants/ParticipantPanel.vue` | ✅ |
| Pinia store de toasts | `stores/toast.ts` | ✅ |
| `ToastContainer.vue` com Teleport + TransitionGroup + XMarkIcon | `components/layout/ToastContainer.vue` | ✅ |
| `AppShell.vue` incluindo `ToastContainer` | `components/layout/AppShell.vue` | ✅ |
| Toast em `phase.changed`, `card.created`, `vote.cast`, `invite.status_updated` | `composables/useWebSocket.ts` | ✅ |
| `handleAllowEntry` chamando `POST /reopen-entry/` | `pages/retro/[id].vue` | ✅ |
| `loadSession` buscando `/invite-status/` na carga | `pages/retro/[id].vue` | ✅ |
| Estado `inviteStatus` / `inviteExpiresAt` no store de participantes | `stores/participants.ts` | ✅ |
| ESLint flat config + Prettier | `eslint.config.mjs`, `.prettierrc.json` | ✅ |
| Playwright config + 3 specs (smoke, auth, dashboard) | `playwright.config.ts`, `e2e/` | ✅ |

---

## O que foi iniciado e não concluído

| Item | Motivo | Ação necessária |
|---|---|---|
| Cobertura de testes backend (%) | `coverage.py` não integrado ao projeto | Integrar `coverage run` + `coverage report` ao CI; meta ≥ 80% |
| Testes E2E de fluxo completo da sessão | Requerem backend com dados seedados rodando; apenas specs de smoke/auth/dashboard criados | Implementar specs para fluxo lobby → board → voting → discussion → actions |
| Validação Lighthouse de acessibilidade | Requer app deployado e rodando | Rodar `lighthouse` contra URL de staging; meta ≥ 90 acessibilidade |
| Playwright browsers instalados no dev local | Não executado na sprint | Rodar `npx playwright install` antes de `npm run test:e2e` |
| `ruff check .` no código novo | Não executado explicitamente nesta sprint | Validar e corrigir antes do deploy |

---

## Decisões técnicas tomadas nesta sprint

### 1. Janela de reabertura de 120 segundos (constante no backend)
- **Arquivo:** `apps/retrospectives/views.py` — `REOPEN_DURATION_SECONDS = 120`
- **Rationale:** Valor fixo simplifica o MVP; parametrização por retrospectiva pode vir em sprint futura.
- **⚠️ Para validação do Tech Lead:** Considerar mover para settings ou campo configurável por facilitador.

### 2. `invite_temporarily_open_until = None` representa "sem janela aberta"
- **Arquivo:** `apps/retrospectives/models.py`
- **Rationale:** Semanticamente limpo; a view `InviteStatusView` infere o status a partir desse campo em conjunto com o `invite_link_active`.

### 3. Toasts via Pinia store + Teleport ao `body`
- **Arquivo:** `stores/toast.ts`, `components/layout/ToastContainer.vue`
- **Rationale:** Evita prop-drilling; `Teleport` garante z-index correto sobre qualquer overlay.

### 4. ESLint flat config (`eslint.config.mjs`)
- **Arquivo:** `frontend/eslint.config.mjs`
- **Rationale:** Padrão atual do Nuxt 3 / ESLint 9. A regra `vue/multi-word-component-names: off` foi necessária para componentes de página single-word (`index.vue`, etc.).

### 5. Patch de teste usando `tasks.invite.auto_block_invite.apply_async`
- **Arquivo:** `tests/retrospectives/test_entry_presence.py`
- **Rationale:** O patch deve apontar para o módulo onde o símbolo **é importado e chamado**, não onde foi originalmente definido.

---

## Padrões estabelecidos que devem ser seguidos

1. **Design system:** Tailwind CSS com tokens em `frontend/tailwind.config.ts`. Fonte Inter. Escala 4px. Heroicons (outline padrão, solid para estado ativo).
2. **Ícones:** Sempre de `@heroicons/vue/24/outline` ou `/solid`. Nunca SVG inline ad hoc.
3. **ARIA:** Todo botão de controle de sessão deve ter `aria-label` descritivo.
4. **Toasts:** Feedback de toda ação assíncrona via `useToastStore()`. Nunca `alert()` ou `console.error` no código de produção.
5. **Stores Pinia:** Sem lógica de negócio em componentes; lógica de estado vai no store, lógica de API na página ou composable.
6. **Testes backend:** Patch de Celery tasks sempre via `patch("tasks.<module>.<task_name>.apply_async")`.
7. **Testes com channel layer:** Sempre passar `-e USE_IN_MEMORY_CHANNEL_LAYER=true` ao rodar `manage.py test` via Docker.
8. **Variáveis de ambiente sensíveis:** Nunca hardcoded. Sempre via `os.getenv()` com fallback explícito ou erro claro.
9. **CI:** Todo PR deve passar nos 4 jobs: `backend-lint`, `backend-test`, `backend-docker`, `frontend-build`.

---

## Próxima sprint (Sprint 8): Preparação para produção e integrações

> Sprint 8 é pós-MVP. O objetivo é tornar o produto deployável em produção e abrir para integrações externas.

### Deploy de produção
- [ ] **Fly.io** — Deploy do backend (API + Worker + Daphne/ASGI). Configurar `fly.toml`, secrets, health checks.
- [ ] **Neon** — PostgreSQL serverless. Configurar `DATABASE_URL` no Fly.io.
- [ ] **Upstash** — Redis serverless para Celery broker e Channel Layer. Configurar `REDIS_URL`.
- [ ] **Vercel** — Deploy do frontend Nuxt 3 (SSR off → static/SPA). Configurar `NUXT_PUBLIC_API_BASE`, `NUXT_PUBLIC_WS_BASE`.
- [ ] Configurar domínio customizado + HTTPS.
- [ ] Configurar `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` para produção.

### Variáveis de ambiente necessárias para produção

```bash
# Backend (Fly.io secrets)
SECRET_KEY=<django-secret-key>
DATABASE_URL=postgresql://user:pass@host/db  # Neon
REDIS_URL=rediss://user:pass@host:port        # Upstash (TLS)
ALLOWED_HOSTS=api.retroapp4l.com
CORS_ALLOWED_ORIGINS=https://retroapp4l.com
DEBUG=false
DJANGO_SETTINGS_MODULE=config.settings.production
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<sendgrid-api-key>
DEFAULT_FROM_EMAIL=noreply@retroapp4l.com

# Frontend (Vercel env vars)
NUXT_PUBLIC_API_BASE=https://api.retroapp4l.com
NUXT_PUBLIC_WS_BASE=wss://api.retroapp4l.com
```

### Social Auth em produção
- [ ] Configurar Google OAuth2: `SOCIALACCOUNT_PROVIDERS` com `client_id` e `secret` reais.
- [ ] Configurar GitHub OAuth2: criar OAuth App em github.com/settings/applications.
- [ ] Configurar callback URLs nos provedores para o domínio de produção.

### Qualidade e observabilidade
- [ ] Integrar `coverage.py` ao CI — meta ≥ 80% de cobertura no backend.
- [ ] Escrever E2E specs para fluxo completo da sessão (lobby → board → voting → discussion → actions → close).
- [ ] Rodar Lighthouse contra staging — meta ≥ 90 acessibilidade e performance.
- [ ] Integrar Sentry (erro tracking) — backend e frontend.
- [ ] Configurar logging estruturado (JSON) no backend para produção.

### Integrações externas (fora do escopo do MVP, Sprint 8+)
> Itens abaixo **não** estão no MVP. Registrados aqui para planejamento futuro.
- Jira: exportar action items como tickets.
- Linear: sincronizar action items.
- GitHub Issues: criar issues a partir de action items.
- Slack: notificação de retrospectiva iniciada / finalizada.

### Features implementadas no MVP vs. fora do escopo

| Feature | MVP? | Sprint |
|---|---|---|
| Registro e login (email/senha) | ✅ | 1-2 |
| JWT auth + refresh | ✅ | 1-2 |
| Criar / listar / encerrar retrospectivas | ✅ | 2-3 |
| Fases: lobby, brainstorm, grouping, voting, discussion, action_items, closed | ✅ | 3-4 |
| Cards (criar, editar, deletar, mover fase) | ✅ | 4-5 |
| Votação em cards | ✅ | 5 |
| Action items | ✅ | 5-6 |
| Participação via link de convite | ✅ | 3 |
| Controle de entrada (bloquear/reabrir link) | ✅ | 7 |
| Presença em tempo real (WebSocket) | ✅ | 6-7 |
| Timer de fase (Celery beat) | ✅ | 6 |
| Toasts de feedback | ✅ | 7 |
| OAuth social (Google, GitHub) | ✅ setup | 6 |
| CI/CD GitHub Actions | ✅ | 7 |
| Deploy produção | ❌ Sprint 8 | — |
| E2E fluxo completo | ❌ Sprint 8 | — |
| Integrações Jira/Linear/GitHub | ❌ Pós-MVP | — |
| SSO/SAML enterprise | ❌ Pós-MVP | — |

---

## Comandos para retomar

```bash
# Subir todos os serviços
docker-compose up -d

# Migrations
docker-compose run --rm backend python manage.py migrate

# Testes backend (todos)
docker-compose run --rm -e USE_IN_MEMORY_CHANNEL_LAYER=true backend python manage.py test

# Testes backend (somente novos endpoints de presença/entrada)
docker-compose run --rm -e USE_IN_MEMORY_CHANNEL_LAYER=true backend python manage.py test tests.retrospectives.test_entry_presence

# Lint backend
docker-compose run --rm backend ruff check .

# Frontend — dev server
cd frontend && npm run dev

# Frontend — build de produção
cd frontend && npm run build

# Frontend — lint
cd frontend && npm run lint

# Frontend — E2E (instalar browsers na primeira vez)
cd frontend && npx playwright install
cd frontend && npm run test:e2e

# Frontend — format
cd frontend && npm run format
```

---

## Notas para o Tech Lead

1. **`USE_IN_MEMORY_CHANNEL_LAYER=true`** é necessário para `python manage.py test` em ambiente sem Redis. O CI já passa essa variável via `env:` no step de testes (`.github/workflows/ci.yml`).
2. **`REOPEN_DURATION_SECONDS = 120`** está hardcoded na view. Avaliar se deve virar setting configurável por retrospectiva antes do deploy.
3. O arquivo `.github/workflows/ci.yml` foi criado nesta sprint. Validar se os secrets necessários (`DOCKER_*` para eventual push de imagem) precisam ser configurados no repositório do GitHub.
4. A pipeline de `frontend-build` no CI roda `npm run lint` antes do `npm run build`. Garantir que `eslint.config.mjs` e `@nuxt/eslint` estejam instalados corretamente no ambiente de CI (`npm ci` deve ser suficiente).
5. Playwright: os specs criados (`smoke.spec.ts`, `auth.spec.ts`, `dashboard.spec.ts`) são scaffolding. Necessitam de backend rodando com dados seedados para execução completa. Recomendo criar fixture de seed para E2E antes de integrar ao CI.
