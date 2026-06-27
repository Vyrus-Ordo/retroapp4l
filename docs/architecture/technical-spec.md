# RetroApp 4L — Especificação Técnica

**Versão:** 2026-06-27
**Source of truth:** código-fonte. Este documento descreve o comportamento implementado, não intenções de produto.

---

## 1. Stack tecnológica

### Backend

| Camada | Tecnologia | Versão |
|---|---|---|
| Framework web | Django | 5.2.13 |
| API REST | Django REST Framework | 3.16.1 |
| Autenticação | djangorestframework-simplejwt | 5.5.1 |
| WebSocket / ASGI | Django Channels | 4.2.2 |
| Servidor ASGI | Daphne | 4.2.1 |
| Channel Layer (Redis) | channels-redis | 4.2.1 |
| Tarefas assíncronas | Celery | 5.5.3 |
| OAuth / allauth | django-allauth | 65.16.1 |
| CORS | django-cors-headers | 4.7.0 |
| Driver PostgreSQL | psycopg[binary] | 3.3.4 |
| Cliente Redis | redis | 5.3.1 |
| Lint | Ruff | 0.11.13 |
| Testes | pytest-django | 4.10.0 |
| Runtime | Python | 3.11 (slim) |

### Frontend

| Camada | Tecnologia | Versão |
|---|---|---|
| Framework | Nuxt | 3.17.5 |
| UI reativo | Vue | 3 (bundled com Nuxt) |
| Estado global | Pinia | 3.0.3 |
| Estilização | @nuxtjs/tailwindcss | 6.14.0 |
| CAPTCHA | @nuxtjs/turnstile | 1.1.2 |
| Ícones | @heroicons/vue | 2.2.0 |
| Lint | @nuxt/eslint + eslint | 1.15.2 / 9.26.0 |
| Formatação | Prettier + prettier-plugin-tailwindcss | 3.8.3 |
| Testes E2E | @playwright/test | 1.59.1 |
| Runtime | Node | 20 (alpine) |

### Infraestrutura

| Camada | Tecnologia | Versão |
|---|---|---|
| Proxy reverso | Nginx | 1.27-alpine |
| Banco de dados | PostgreSQL | 16-alpine |
| Broker / Cache / Channel Layer | Redis | 7-alpine |
| Containerização | Docker Compose | não fixada |

---

## 2. Arquitetura de deployment

### 2.1 Ambiente local (`docker-compose.yml`)

```
[Cliente]
    │
    ├── HTTP  → [Backend Daphne :8000]   ← monta ./backend como volume
    │               ├── PostgreSQL :5432
    │               └── Redis :6379
    │
    ├── WS    → [Backend Daphne :8000]
    │
    └── HTTP  → [Frontend Nuxt :3000]

[Worker Celery]
    ├── Redis :6379   ← broker + result backend
    └── PostgreSQL :5432
```

| Serviço | Porta host | Protocolo | Responsabilidade | Startup |
|---|---|---|---|---|
| `backend` | 8000 | HTTP + WS | Daphne ASGI; API REST e WebSocket | `collectstatic && migrate && daphne -b 0.0.0.0 -p 8000 config.asgi:application` |
| `worker` | — | interno | Celery worker + Beat | `migrate && celery -A config worker -B -l info` |
| `db` | 5432 | TCP | PostgreSQL 16 | imagem oficial |
| `redis` | 6379 | TCP | Broker Celery + Channel Layer | imagem oficial |
| `frontend` | 3000 | HTTP | Nuxt Node server | `npm run build && node .output/server/index.mjs` |

Sem Nginx no ambiente local. Frontend acessa backend diretamente em `http://localhost:8000`.

### 2.2 Ambiente de produção (`docker-compose.prod.yml`)

```
[Internet]
    │
    ▼
[Nginx :80/:443]  ← TLS terminado aqui
    │
    ├── /api/*        → [Backend Daphne :8000]
    ├── /admin/*      → [Backend Daphne :8000]
    ├── /ws/*         → [Backend Daphne :8000]  ← Upgrade: WebSocket; timeout 86400s
    ├── /static/*     → filesystem /var/www/staticfiles/
    └── /*            → [Frontend Nuxt :3000]

[Backend Daphne :8000]
    ├── PostgreSQL  (serviço externo na rede infra-network)
    └── Redis       (serviço externo na rede infra-network)

[Worker Celery]
    ├── Redis  ← broker + result backend
    └── PostgreSQL
```

| Serviço | Rede | Startup |
|---|---|---|
| `backend` | `infra-network` (externa) | `collectstatic && migrate && daphne -b 0.0.0.0 -p 8000 config.asgi:application` |
| `worker` | `infra-network` | `migrate && celery -A config worker -B -l info` |
| `frontend` | `infra-network` | `node .output/server/index.mjs` |
| Nginx | gerenciado por `/opt/infra/docker-compose.yml` | config em `nginx/retroapp.conf` |

Static files: backend escreve em `/opt/retroapp4l/staticfiles` (bind mount); Nginx lê do mesmo path via seu próprio bind mount.

`NUXT_PUBLIC_TURNSTILE_SITE_KEY` é injetada em build time via `ARG` no `frontend/Dockerfile` (baked no bundle JS).

---

## 3. Estrutura de módulos

### 3.1 Backend

```
backend/
├── config/
│   ├── settings/
│   │   ├── base.py          # Toda configuração base: JWT, Channels, Celery, DB, CORS, allauth
│   │   ├── local.py         # Herda base; DEBUG=True
│   │   └── production.py    # Herda base; DEBUG=False; HTTPS/HSTS/cookie flags
│   ├── asgi.py              # ProtocolTypeRouter: HTTP→Django, WebSocket→JWTAuthMiddleware→URLRouter
│   ├── celery.py            # Ponto de entrada do Celery (importa de celery_app)
│   ├── celery_app.py        # Instância Celery; autodiscover_tasks()
│   └── urls.py              # Raiz: /admin/, /accounts/ (allauth), /api/auth/, /api/
│
├── apps/
│   ├── users/
│   │   ├── models.py        # User customizado (UUID PK, is_guest, display_email)
│   │   ├── serializers.py   # RegisterSerializer, LoginSerializer, UserSerializer, GuestInviteJoinSerializer
│   │   ├── views.py         # RegisterView, LoginView, LogoutView (APIView)
│   │   ├── urls.py          # /register/, /login/, /logout/, /refresh/
│   │   └── turnstile.py     # verify_turnstile(); bypass automático se secret_key vazio
│   │
│   ├── retrospectives/
│   │   ├── models.py        # Retrospective, Milestone, Participant, AccessLog + enums
│   │   ├── serializers.py   # Create/List/Detail/History/Closed/Invite/Participant/Milestone serializers
│   │   ├── views.py         # Todas as views REST + RetrospectiveAccessMixin
│   │   ├── urls.py          # Inclui cards.urls e actions.urls
│   │   └── signals.py       # Milestone post_save/post_delete → WS broadcast
│   │
│   ├── cards/
│   │   ├── models.py        # Card (self-FK group), CardVote
│   │   ├── serializers.py   # CardSerializer (campos virtuais anônimos), CardGroupingSerializer, VotesConfigSerializer
│   │   ├── views.py         # CardListCreateView, CardDetailView, CardGroupView, CardUngroupView, CardVoteView, VotesConfigView
│   │   ├── urls.py          # /retrospectives/{id}/cards/*, /votes/, /votes-config/
│   │   └── signals.py       # Card/CardVote pre_save/post_save/post_delete → WS broadcast
│   │
│   ├── actions/
│   │   ├── models.py        # ActionItem (assignee FK→User, não Participant)
│   │   ├── serializers.py   # ActionItemSerializer (assignee_id aceita Participant UUID), PreviousActionStatusSerializer
│   │   ├── views.py         # ActionItemListCreateView, ActionItemDetailView, PreviousActionListView, PreviousActionStatusUpdateView
│   │   ├── urls.py          # /action-items/, /previous-actions/
│   │   └── signals.py       # ActionItem pre_save/post_save/post_delete → WS broadcast
│   │
│   └── realtime/
│       ├── consumers.py     # RetrospectiveConsumer (AsyncJsonWebsocketConsumer) + helpers async
│       ├── middleware.py    # JWTAuthMiddleware: extrai token de query string ou header Authorization
│       ├── routing.py       # websocket_urlpatterns: ws/retrospectives/{retrospective_id}/
│       ├── state_machine.py # PHASE_TRANSITIONS dict + is_valid_transition(); NÃO usado pelo consumer
│       └── tasks.py         # timer_sync_task: emite timer.sync a cada 5s; auto-reagenda
│
├── tasks/
│   ├── invite.py            # auto_block_invite: zera invite_temporarily_open_until + AccessLog + WS
│   └── timer.py             # sync_timer: stub, retorna dict, não emite nada (não confundir com realtime/tasks.py)
│
└── tests/
    ├── users/               # Testes de autenticação e usuário
    ├── retrospectives/      # Testes de fluxo de retrospectiva
    ├── actions/             # Testes de action items
    └── realtime/            # Testes de consumer WebSocket
```

### 3.2 Frontend

```
frontend/
├── nuxt.config.ts           # ssr:false; módulos; runtimeConfig (apiBase, wsBase)
├── pages/
│   ├── index.vue            # Landing/dashboard; redireciona por auth status
│   ├── join.vue             # Só navega para /retro/{code}; não resolve token
│   ├── auth/
│   │   ├── login.vue        # Login local + link visual Google (allauth)
│   │   └── register.vue     # Registro com Turnstile
│   ├── retro/
│   │   ├── create.vue       # Cria retro + milestones iniciais
│   │   ├── [id].vue         # Workspace principal; monta WS; redireciona para /history/{id} se closed
│   │   └── invite/
│   │       └── [token].vue  # Resolve convite; coleta nome/email; entra como user ou guest
│   └── history/
│       ├── index.vue        # Lista retros fechadas
│       └── [id].vue         # Detalhe de retro fechada; exportação Markdown (facilitador)
│
├── components/
│   ├── layout/              # AppShell, AppHeader, AppSidebar, AppFooter, PhaseStepper,
│   │                        # PhaseCarousel, RetroHeader, SettingsModal, ToastContainer, AvatarCircle
│   ├── board/               # BoardGrid, ColumnHeader, FocusCard (board-level)
│   ├── retro/               # RetroCard, TimerDisplay, VoteBadge, VoteControls, ActionEditor,
│   │                        # MilestoneCard, MilestoneBar, PhaseChip, FocusCard (retro-level)
│   │   ├── board/           # BoardGrid, ColumnBox (retro-board variants)
│   │   └── phases/          # SetupView, LobbyView, CheckView, MilestonesView, BoardView,
│   │                        # GroupingView, VotingView, DiscussionView, ActionsView, ClosedView
│   ├── forms/               # CardComposer (foco auto no textarea via nextTick), ActionItemForm
│   └── participants/        # ParticipantPanel
│
├── stores/
│   ├── auth.ts              # JWT, user, login/register/logout/refresh; persiste em localStorage
│   ├── retro.ts             # Session, cards, votes, action items, previous actions, history, focus, applySocketEvent()
│   ├── timer.ts             # secondsRemaining, paused, hydrate/tick/pause/resume/setRemaining
│   ├── participants.ts      # Lista, onlineIds (estimado por WS), inviteStatus/expiresAt
│   ├── toast.ts             # Fila de toasts globais
│   └── guest.ts             # Nome/email de guest para prefill local
│
├── composables/
│   ├── useApiClient.ts      # $fetch com Bearer token; retry automático após refresh 401
│   ├── useWebSocket.ts      # Abre WS; handleMessage despacha para stores; reconexão exponencial
│   ├── usePhase.ts          # orderedPhases[]; getNextPhase() com skip_check_phase
│   ├── useTimer.ts          # setInterval 1s local; tick no timerStore; playTimerExpiredAlert
│   └── useExportMarkdown.ts # Exporta dados da retro como Markdown (table ou sections)
│
└── assets/css/
    ├── tokens.css           # CSS custom properties: --ds-*, --fg-*, --bg-*, --border-*
    └── tailwind.css         # Classes utilitárias: panel, field-input, button-primary, button-secondary
```

---

## 4. Autenticação e autorização

### 4.1 Fluxo de registro

```
1. Cliente POST /api/auth/register/ { name, email, password, cf_turnstile_response }

2. RegisterView.post():
   a. Extrai cf_turnstile_response e IP do request
   b. verify_turnstile(token, ip):
      - Se CLOUDFLARE_TURNSTILE_SECRET_KEY vazio → retorna True (bypass dev/test)
      - Senão: POST https://challenges.cloudflare.com/turnstile/v0/siteverify
      - Timeout 5s; qualquer Exception → retorna False
   c. Se False → 400 { cf_turnstile_response: "Invalid captcha." }

3. RegisterSerializer.validate_email():
   - Se ALLOWED_EMAIL_DOMAINS vazio → aceita qualquer domínio
   - Senão: verifica domínio do email contra a lista (case-insensitive)

4. RegisterSerializer.validate() valida password min_length=8

5. User.objects.create_user(email, password, name)
   → email normalizado (lowercase domínio)

6. RefreshToken.for_user(user) gera par de tokens JWT

7. Retorno 201: { user: UserSerializer, access: str, refresh: str }
```

### 4.2 Fluxo de login

```
1. Cliente POST /api/auth/login/ { email, password }

2. LoginView.post():
   a. LoginSerializer valida campos presentes
   b. authenticate(request, username=email, password=password)
      → retorna User ou None
   c. Se user is None → 400 { detail: "Invalid credentials." }
   d. Se user.is_guest → 400 { detail: "Guest sessions must be started from an invite link." }

3. RefreshToken.for_user(user) gera par de tokens JWT

4. Retorno 200: { user: UserSerializer, access: str, refresh: str }
```

### 4.3 Fluxo de convite

```
1. Cliente GET /api/invites/{token}/
   → InviteResolveView busca Retrospective por invite_token=token
   → Retorna: { id, title, sprint_name, team_key, status, facilitator_name, invite_status, entry_expires_at }

2. Cliente POST /api/invites/{token}/join/ { name, email? }

3. InviteJoinView.post():
   a. Retrospective buscada por invite_token (404 se não encontrado)
   b. ensure_invite_open():
      - status == CLOSED → 403
      - invite_status == "blocked" → 403
      (active = status LOBBY com token; temporarily_open = invite_temporarily_open_until > now)

   c. GuestInviteJoinSerializer valida { name, email? }

   d. Se request.user.is_authenticated:
      - Usa usuário existente
      - Se is_guest: atualiza name/public_email se mudaram
   e. Senão (anônimo):
      - build_guest_identity(name, email) → { name, email: "guest+{uuid}@guest.retroapp4l.local", public_email, is_guest: True }
      - User.objects.create_user(**identity)
      - user.set_unusable_password() + save(update_fields=["password"])

   f. Participant.objects.get_or_create(retrospective, user, defaults={votes_remaining: max_votes_per_user})
      - Se não criado E votes_remaining <= 0: reseta para max_votes_per_user

   g. Se participante novo: AccessLog.PARTICIPANT_JOINED criado
      (triggered_by=None para guests; triggered_by=user para autenticados)

4. RefreshToken.for_user(user) — guest também recebe JWT válido

5. Retorno 200: { user, access, refresh, retrospective_id, participant_id }
```

### 4.4 Estrutura do JWT

Configuração em `config/settings/base.py`:

```python
SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}
```

Payload do access token (defaults SimpleJWT não alterados):

```json
{
  "token_type": "access",
  "exp": 1700000000,
  "iat": 1699971200,
  "jti": "uuid-único-do-token",
  "user_id": "uuid-do-usuário"
}
```

`user_id` mapeia para `User.id` (UUID). `TOKEN_BLACKLIST` está instalado (`rest_framework_simplejwt.token_blacklist`) e é usado no logout via `RefreshToken(token).blacklist()`.

### 4.5 Permissões por papel

| Ação | Facilitador | Participante | Guest |
|---|---|---|---|
| Criar retrospectiva | ✅ | ✅ (se não guest) | ❌ (403) |
| Criar marcos (fase setup) | ✅ | ❌ | ❌ |
| Editar/deletar marcos (fase setup) | ✅ | ❌ | ❌ |
| Avançar fase (WS) | ✅ | ❌ (silencioso) | ❌ |
| Reabrir convite | ✅ | ❌ | ❌ |
| Criar card (fases não bloqueadas) | ✅ | ✅ | ✅ |
| Editar/deletar card próprio | ✅ (se autor) | ✅ (se autor) | ✅ (se autor) |
| Votar (fase voting, loathed/longed) | ✅ | ✅ | ✅ |
| Revogar voto | ✅ | ✅ | ✅ |
| Agrupar/desagrupar cards | ✅ | ❌ | ❌ |
| Definir focus card (fase discussion) | ✅ | ❌ | ❌ |
| Criar action item (fase discussion) | ✅ | ❌ | ❌ |
| Editar/deletar action item (discussion/actions) | ✅ | ❌ | ❌ |
| Listar action items | ✅ | ✅ | ✅ |
| Atualizar status de ações anteriores | ✅ | ✅ | ✅ |
| Fechar retrospectiva (fase actions) | ✅ | ❌ | ❌ |
| Alterar votes-config (antes de voting) | ✅ | ❌ | ❌ |
| Ver sugestões de team_key | ✅ | ✅ (se não guest) | ❌ |
| Exportar retro para Markdown | ✅ (UI) | ❌ (UI) | ❌ (UI) |

Fontes: `retrospectives/views.py` (`RetrospectiveAccessMixin`), `cards/views.py` (`RetrospectiveAccessMixin`), `actions/views.py` (`ActionAccessMixin`), `realtime/consumers.py` (`persist_phase_advance`).

---

## 5. Fluxo de requisição HTTP

Ciclo completo de uma requisição autenticada típica (ex: `GET /api/retrospectives/{id}/`):

```
1. Cliente envia:
   GET /api/retrospectives/{id}/
   Authorization: Bearer <access_token>

2. Django MIDDLEWARE processa em ordem:
   SecurityMiddleware → CorsMiddleware → SessionMiddleware → CommonMiddleware
   → CsrfViewMiddleware → AuthenticationMiddleware → AccountMiddleware (allauth)
   → MessageMiddleware → XFrameOptionsMiddleware

3. Routing: config/urls.py → apps/retrospectives/urls.py → RetrospectiveDetailView

4. DRF: JWTAuthentication.authenticate(request)
   a. Extrai "Bearer <token>" do header Authorization
   b. UntypedToken(raw_token) valida assinatura e expiração
   c. JWTAuthentication.get_user(validated_token) faz SELECT por user_id
   d. Seta request.user = User instance

5. DRF: IsAuthenticated.has_permission() → True se user.is_authenticated

6. RetrospectiveDetailView.get_object():
   a. get_queryset(): filtra por facilitator=user OR participants__user=user
   b. ensure_session_open(): 403 se status == CLOSED
   c. ensure_invite_token(): gera invite_token se ausente e não fechado

7. RetrospectiveDetailSerializer(retrospective, context={"request": request})
   a. Serializa campos do model
   b. Inclui participants + milestones via prefetch

8. Response 200 JSON retorna ao cliente
```

Erros de autenticação: DRF retorna 401 se token inválido/expirado antes de chegar na view. O cliente (`useApiClient.ts`) intercepta 401 e tenta refresh automático:

```typescript
// useApiClient.ts
catch (error) {
  if (isUnauthorizedApiError(error)) {
    const refreshed = await authStore.refreshToken()
    if (refreshed) { retry request }
    else { authStore.clear(); throw "Session expired" }
  }
}
```

---

## 6. Fluxo WebSocket

### 6.1 Handshake e autenticação

URL de conexão:
```
ws://host/ws/retrospectives/{retrospective_id}/?token={JWT_access_token}
```

Cadeia de processamento em `config/asgi.py`:
```
ProtocolTypeRouter
  └── "websocket" → JWTAuthMiddleware
                        └── URLRouter
                                └── RetrospectiveConsumer
```

**JWTAuthMiddleware** (`apps/realtime/middleware.py`):

```python
# 1. Tenta query string: ?token=...
token = query_params.get('token', [None])[0]
# 2. Fallback: header Authorization: Bearer <token>
if not token:
    for header, value in scope.get('headers', []):
        if header == b'authorization':
            token = value.decode().split()[1]
# 3. Valida token
if token:
    validated_token = UntypedToken(token)
    user = JWTAuthentication().get_user(validated_token)
    scope['user'] = user
else:
    scope['user'] = AnonymousUser()
```

> ⚠️ O middleware tem `print()` de debug ativo (`[JWTAuthMiddleware] Query params: ...`). Em produção, isso polui os logs do Daphne.

**Condições que recusam a conexão** (em `RetrospectiveConsumer.connect()`):

| Código | Condição |
|---|---|
| 4000 | `retrospective_id` ausente nos kwargs da URL |
| 4001 | `user` não autenticado (AnonymousUser ou None) |
| 4004 | Retrospectiva não existe no banco |
| 4003 | Usuário não é facilitador nem participante, OU retrospectiva está `closed` |

### 6.2 Snapshot inicial

Enviado imediatamente após `accept()`:

```python
await self.send_json({
    "type": "session.snapshot",
    "phase": connection_context["phase"],   # fase real do banco
    "timer": None,                           # sempre null
    "cards": [],                             # sempre vazio
    "votes": [],                             # sempre vazio
    "milestones": [],                        # sempre vazio
    "participants": [],                      # sempre vazio
    "action_items": action_items             # carregados do banco via ORM
})
```

`action_items` é o único array populado no snapshot. Os demais chegam vazios porque o consumer não os carrega — decisão de design para reduzir carga inicial (ver seção 13).

**Chamadas REST que o frontend dispara após o snapshot** (`retro.ts → fetchSession()`):

```
GET /retrospectives/{id}/          → current + participants + milestones
GET /retrospectives/{id}/cards/    → cards (normalizeCard mapeia group_parent_id)
GET /retrospectives/{id}/votes/    → votes
GET /retrospectives/{id}/action-items/        → actionItems (em try/catch)
GET /retrospectives/{id}/previous-actions/    → previousActions (em try/catch)
```

Após `session.snapshot`, também é emitido `participant.joined` para o grupo (excluindo o canal do próprio usuário via `exclude_channel_name`).

### 6.3 Propagação de eventos de domínio

Caminho completo de `card.created`:

```
1. Cliente POST /retrospectives/{id}/cards/ { column, content, is_anonymous }
   → CardListCreateView.perform_create()
   → serializer.save(author=user, retrospective_id=...)
   → Card.save()

2. cards/signals.py — @receiver(post_save, sender=Card)
   def card_saved(sender, instance, created, **kwargs):
       card_data = CardSerializer(instance).data  # já mascara is_anonymous
       channel_layer.group_send(
           f"retro_{instance.retrospective_id}",
           { "type": "card_create", "card": card_data, "author_id": str(instance.author_id) }
       )

3. RetrospectiveConsumer.card_create(event):
   card = dict(event["card"])
   card["can_edit"] = str(user_id) == str(event.get("author_id"))
   await self.send_json({"type": "card.created", "card": card})
   # Cada cliente conectado recebe can_edit calculado individualmente

4. Frontend — useWebSocket.ts handleMessage():
   if (payload.type === "card.created") toastStore.success("Card created.")
   retroStore.applySocketEvent(payload)
   → retro.ts applySocketEvent():
     this.cards = upsertCard(this.cards, event.card as Card)
```

> **Nota sobre tipos de eventos:** Django Channels converte `.` em `_` para despachar ao handler. `"type": "card_create"` no group_send → método `card_create()` no consumer. O cliente recebe `"type": "card.created"` (o consumer recria o payload com dot notation).

### 6.4 Reconexão

Estratégia em `useWebSocket.ts`:

```typescript
function scheduleReconnect() {
    const delay = Math.min(5000, 500 * (2 ** reconnectAttempts.value))
    // Tentativa 0: 500ms; 1: 1000ms; 2: 2000ms; 3: 4000ms; 4+: 5000ms
    reconnectTimer = window.setTimeout(() => {
        reconnectAttempts.value += 1
        connect()
    }, delay)
}
```

Acionado em `socket.onclose` quando `connectionState !== "closed"` (fechamento limpo não reconecta). Na reconexão, `fetchSession()` é chamado via `watch` nos watchers do composable que monitoram `retroStore.current`, rehidratando todo o estado via REST.

---

## 7. Fluxo de sessão de retrospectiva (máquina de estados)

### 7.1 Duas representações de fluxo

**Backend — `apps/realtime/state_machine.py`:**

```
SETUP → LOBBY → PRESENTATION → CHECK → BOARD → GROUPING → VOTING → DISCUSSION → ACTIONS → CLOSED
```

**Frontend — `composables/usePhase.ts`:**

```typescript
const orderedPhases = [
  "setup", "lobby", "check", "presentation",  // ← CHECK antes de PRESENTATION
  "board", "grouping", "voting", "discussion", "actions", "closed"
]
```

A ordem do frontend diverge do backend. O consumer **não usa** `state_machine.py`.

### 7.2 Como o avanço de fase funciona de fato

```
1. Facilitador clica "Avançar fase" na UI

2. Frontend chama getNextPhase(currentPhase, retro.skip_check_phase):
   - Localiza currentPhase em orderedPhases
   - Retorna orderedPhases[index + 1]
   - Se skip_check_phase=true E próxima="check": retorna orderedPhases[index + 2] (pula check)

3. Frontend envia via WS: { "type": "phase.advance", "phase": nextPhase }

4. RetrospectiveConsumer.receive_json():
   persisted = await persist_phase_advance(retrospective_id, user.id, target_phase)

5. persist_phase_advance() (função async):
   a. Verifica: target_phase in RetrospectiveStatus.values → senão False
   b. Verifica: retro.facilitator_id == user_id → senão False
   c. retro.status = target_phase; retro.save(update_fields=["status"])
   d. Retorna True

6. Se persisted:
   a. duration = await start_phase_timer(retrospective_id, target_phase)
      - Se target_phase in TIMED_PHASES: salva timer_started_at/timer_paused_at/timer_duration_seconds
   b. Se duration > 0: timer_sync_task.apply_async(countdown=5) → agendamento Celery
   c. group_send("phase.changed", { phase: target_phase, timer_duration_seconds: duration })

7. Todos os clientes conectados recebem "phase.changed"
   → retroStore.current.status atualizado
   → timerStore.resume(duration) chamado
```

### 7.3 O que o backend valida e o que não valida

- ✅ Valida: usuário é o facilitador da retro (`retro.facilitator_id == user_id`)
- ✅ Valida: fase destino existe nos choices de `RetrospectiveStatus` (`target_phase in RetrospectiveStatus.values`)
- ❌ Não valida: transição é linear (`is_valid_transition` de `state_machine.py` **nunca é chamada**)
- ❌ Não valida: fase anterior deve ser completada
- ❌ Não trata `skip_check_phase` (lógica existe apenas no frontend)

### 7.4 Efeito do `skip_check_phase`

**Onde tem efeito:** `frontend/composables/usePhase.ts`:

```typescript
function getNextPhase(phase: RetroPhase, skipCheckPhase = false) {
    const currentIndex = orderedPhases.indexOf(phase)
    const next = orderedPhases[currentIndex + 1]
    if (skipCheckPhase && next === "check") {
        return orderedPhases[currentIndex + 2]  // pula "check", vai para "presentation"
    }
    return next
}
```

**Onde não tem efeito:** backend (`state_machine.py`, consumer, models). O flag é armazenado no banco mas não é lido por nenhum código backend.

### 7.5 Fases cronometradas e durações default

Definidas em `apps/realtime/consumers.py`:

```python
TIMED_PHASES = {"presentation", "check", "board", "grouping", "voting", "discussion", "actions"}

DEFAULT_PHASE_DURATIONS = {
    "presentation": 600,   # 10 min
    "check":        300,   # 5 min
    "board":        900,   # 15 min
    "grouping":     300,   # 5 min
    "voting":       180,   # 3 min
    "discussion":   900,   # 15 min
    "actions":      600,   # 10 min
}
```

Durações customizadas sobrescrevem os defaults via `Retrospective.phase_durations` JSONField. A lookup é: `(retro.phase_durations or {}).get(phase) or DEFAULT_PHASE_DURATIONS.get(phase, 0)`.

`setup`, `lobby` e `closed` não têm timer.

---

## 8. Sistema de timer

### 8.1 Início

Quando `persist_phase_advance()` retorna `True` e `target_phase in TIMED_PHASES`, o consumer chama `start_phase_timer()`:

```python
async def start_phase_timer(retrospective_id, phase):
    duration = (retro.phase_durations or {}).get(phase) or DEFAULT_PHASE_DURATIONS.get(phase, 0)
    if duration <= 0:
        return 0
    retro.timer_started_at = timezone.now()
    retro.timer_paused_at = None
    retro.timer_duration_seconds = duration
    retro.save(update_fields=["timer_started_at", "timer_paused_at", "timer_duration_seconds"])
    return duration
```

### 8.2 Persistência

Campos no model `Retrospective`:

| Campo | Atualizado quando |
|---|---|
| `timer_started_at` | Fase cronometrada inicia; resume (reajustado para simular contagem correta) |
| `timer_paused_at` | Timer pausado (guardado `now()`); zerado no resume |
| `timer_duration_seconds` | Fase cronometrada inicia; novo valor ao trocar fase |

### 8.3 Sincronização

Task `timer_sync_task` em `apps/realtime/tasks.py`:

```python
@shared_task
def timer_sync_task(retrospective_id: str):
    # Para se: CLOSED, timer_started_at None, ou timer_paused_at set
    elapsed = (now() - retro.timer_started_at).total_seconds()
    remaining = max(0, retro.timer_duration_seconds - elapsed)

    if remaining <= 0:
        channel_layer.group_send(group, {"type": "timer.expired", "phase": retro.status})
        return  # Não se reagenda

    channel_layer.group_send(group, {"type": "timer.sync", "seconds_remaining": remaining})
    timer_sync_task.apply_async(args=[retrospective_id], countdown=5)  # auto-reagenda
```

Agendada pelo consumer em dois momentos:
- Ao avançar para fase cronometrada com `duration > 0`
- Ao retomar timer pausado (`timer.resume`)

> ⚠️ `backend/tasks/timer.py` contém um `sync_timer` **stub** que apenas retorna um dict. Não confundir com `timer_sync_task` em `apps/realtime/tasks.py`, que é a task real.

### 8.4 Pausa e retomada

**Pausa** (`pause_timer`):

```python
elapsed = max(0, int((now() - retro.timer_started_at).total_seconds()))
remaining = max(0, retro.timer_duration_seconds - elapsed)
retro.timer_paused_at = now()
# timer_started_at não muda; remaining é calculado na leitura
```

**Retomada** (`resume_timer`):

```python
elapsed_before_pause = max(0, int((retro.timer_paused_at - retro.timer_started_at).total_seconds()))
remaining = max(0, retro.timer_duration_seconds - elapsed_before_pause)
# Reajusta timer_started_at para que elapsed atual = timer_duration - remaining
retro.timer_started_at = now() - timedelta(seconds=retro.timer_duration_seconds - remaining)
retro.timer_paused_at = None
```

### 8.5 Frontend

**Hidratação** (`stores/timer.ts → hydrate(retro)`):

```typescript
function calculateRemaining(retro: RetrospectiveDetail | null) {
    const started = new Date(retro.timer_started_at).getTime()
    const paused = retro.timer_paused_at ? new Date(retro.timer_paused_at).getTime() : null
    const reference = paused || Date.now()
    const elapsed = Math.max(0, Math.floor((reference - started) / 1000))
    return Math.max(0, retro.timer_duration_seconds - elapsed)
}
```

**Loop local** (`composables/useTimer.ts`):

```typescript
setInterval(() => {
    const before = timerStore.secondsRemaining
    timerStore.tick()  // decrementa se !paused && > 0
    if (before > 0 && timerStore.secondsRemaining === 0) playTimerExpiredAlert()
}, 1000)
```

**Eventos WS recebidos:**

| Evento | Ação no frontend |
|---|---|
| `timer.sync` | `timerStore.setRemaining(seconds_remaining)` — corrige drift local |
| `timer.expired` | `timerStore.setRemaining(0)` + `playTimerExpiredAlert()` + toast |
| `timer.paused` | `timerStore.pause(seconds_remaining)` — paused=true |
| `timer.resumed` | `timerStore.resume(seconds_remaining)` — paused=false |
| `phase.changed` | `timerStore.resume(timer_duration_seconds)` — inicia contagem nova |

---

## 9. Tarefas assíncronas (Celery)

Configuração: `CELERY_BROKER_URL = REDIS_URL`, `CELERY_RESULT_BACKEND = REDIS_URL`, `CELERY_BEAT_SCHEDULER = "celery.beat:PersistentScheduler"`. Sem tasks periódicas (Beat schedule) definidas no código — Beat está no mesmo processo que o worker mas ocioso.

| Task | Localização | Gatilho | O que faz | Efeito colateral |
|---|---|---|---|---|
| `timer_sync_task` | `apps/realtime/tasks.py` | Consumer chama `apply_async(countdown=5)` ao avançar fase cronometrada ou ao retomar | Calcula `seconds_remaining`; emite `timer.sync` ou `timer.expired` via channel layer; auto-reagenda a cada 5s | Emite WS para todos os clientes da retro; para automaticamente ao expirar, pausar ou fechar sessão |
| `auto_block_invite` (nome: `tasks.invite.auto_block_invite`) | `tasks/invite.py` | `ReopenEntryView.post()` chama `apply_async(countdown=120)` | Verifica se `invite_temporarily_open_until <= now`; se sim: zera campo + cria `AccessLog.LINK_AUTO_BLOCKED` | Emite `invite.status_updated { invite_status: "blocked" }` via channel layer |
| `sync_timer` | `tasks/timer.py` | — (stub, nunca chamada) | Retorna `{ retrospective_id, status: "scheduled" }` | Nenhum |

---

## 10. Sistema de anonimato de cards

### 10.1 Banco

`Card.author_id` **sempre** aponta para o `User` criador. `Card.is_anonymous` é `BOOLEAN NOT NULL DEFAULT FALSE`. Nenhum campo é zerado ao marcar anônimo.

### 10.2 REST

`CardSerializer` (`apps/cards/serializers.py`):

```python
def get_author(self, obj):
    if obj.is_anonymous:
        return None       # UUID mascarado
    return str(obj.author_id)

def get_author_name(self, obj):
    if obj.is_anonymous:
        return None
    return obj.author.name

def get_author_display(self, obj):
    if obj.is_anonymous:
        return "Anonymous"   # string fixa
    return obj.author.name

def get_can_edit(self, obj):
    request = self.context.get("request")
    if not request or not request.user.is_authenticated:
        return False
    return obj.author_id == request.user.id  # usa author_id real; não revela ao cliente
```

`can_edit` é calculado com `author_id` real. Um card anônimo ainda retorna `can_edit: True` para o próprio autor — a UI pode mostrar botão de edição sem revelar quem escreveu.

### 10.3 WebSocket

Signals (`cards/signals.py`) serializam via `CardSerializer(instance)` antes de enviar. O serializer mascara conforme 10.2.

No consumer, `card_create` e `card_update` recalculam `can_edit` individualmente para cada cliente conectado:

```python
async def card_create(self, event):
    card = dict(event["card"])
    user_id = getattr(self.scope.get("user"), "id", None)
    card["can_edit"] = str(user_id) == str(event.get("author_id"))
    await self.send_json({"type": "card.created", "card": card})
```

`author_id` viaja no evento interno do channel layer (não chega ao cliente) e é usado apenas para calcular `can_edit`.

Para `discussion.focus_updated`, a serialização é feita em `views.py → serialize_focus_card()`:

```python
def serialize_focus_card(card):
    return {
        "card_id": str(card.id),
        "author": None if card.is_anonymous else card.author.name,
        "author_display": "Anonymous" if card.is_anonymous else card.author.name,
        "is_anonymous": card.is_anonymous,
        ...
    }
```

### 10.4 Regra de auto-voto

`apps/cards/views.py → CardVoteView.post()`:

```python
if not retrospective.allow_self_vote and card.author_id == request.user.id:
    raise PermissionDenied("Users cannot vote on their own cards.")
```

`card.author_id` é a FK real no banco — nunca mascarada. Um card anônimo com `allow_self_vote=False` bloqueia o próprio autor de votar sem revelar no payload público que ele é o autor.

---

## 11. Contratos de comportamento críticos

### Fechamento de retrospectiva

**Invariante:** fechamento só é possível se: usuário é facilitador, fase atual é `actions`, payload contém `{"confirm": true}`.

**Localização:** `apps/retrospectives/views.py → RetrospectiveCloseView.post()`

**Campos alterados no banco em uma única `save(update_fields=[...])`:**

```python
retrospective.status = RetrospectiveStatus.CLOSED
retrospective.closed_at = now
retrospective.invite_token = None
retrospective.invite_revoked_at = now
retrospective.focus_card = None
```

**Por quê:** qualquer modificação parcial pode deixar o convite ativo em sessão fechada. Os 5 campos devem ser salvos atomicamente.

---

### Convite temporário

**Invariante:** `POST /reopen-entry/` abre o convite por exatamente `REOPEN_DURATION_SECONDS = 120` segundos. Entrar via convite temporário **não fecha o link imediatamente**. O bloqueio ocorre quando a task Celery `auto_block_invite` dispara após 120s.

**Localização:** `apps/retrospectives/views.py → ReopenEntryView` + `tasks/invite.py`

**Por quê:** sem a task, múltiplos participantes podem entrar na mesma janela. Fechar ao primeiro entrante exigiria lógica de concorrência complexa na view de join.

---

### Votação

**Invariante:** voto só é aceito se: fase == `voting`, coluna in `{loathed, longed}`, `votes_remaining > 0`, `(card, voter)` único no banco, `allow_self_vote` respeitado via `author_id` real.

**Localização:** `apps/cards/views.py → CardVoteView.post()`

**Por quê:** violar qualquer condição cria inconsistência em `Participant.votes_remaining` ou duplicidade em `CardVote`.

**`votes-config`:** `PUT /votes-config/` altera **apenas** `max_votes_per_user` (1–10); **não altera** `allow_self_vote`. Reseta `votes_remaining` de **todos** os participantes via `Participant.objects.filter(retrospective=retrospective).update(votes_remaining=new_value)`. Bloqueado nas fases `voting`, `discussion`, `actions`, `closed`.

---

### Criação de action items

**Invariante:** criação só pelo facilitador, apenas na fase `discussion`. Na fase `actions`, criação é bloqueada (`ensure_discussion_phase` levanta 403). Edição e exclusão são permitidas ao facilitador em `discussion` e `actions`.

**Localização:** `apps/actions/views.py → ActionItemListCreateView.perform_create()` e `ActionItemDetailView.perform_update()/perform_destroy()`

**Por quê:** `actions` é fase de revisão, não criação. Misturar criação e revisão tornaria o estado inconsistente.

---

### Agrupamento de cards

**Invariante:** payload exige `card_ids` com ≥ 2 elementos; todos os cards devem ser da mesma retro e da mesma coluna. `group_parent_id` deve ser um dos `card_ids` ou é assumido como `cards[0].id`.

**Localização:** `apps/cards/views.py → CardGroupView.post()`

**Restrição de fase:** **nenhuma** no backend — o agrupamento é permitido em qualquer fase exceto `closed`. A UI expõe a interface de agrupamento apenas na fase `grouping`.

---

### Snapshot WebSocket

**Invariante:** o snapshot inicial contém `cards: []`, `votes: []`, `milestones: []`, `participants: []`. O frontend **nunca** pode assumir que esses arrays estão populados. `action_items` é o único array carregado do banco no snapshot.

**Localização:** `apps/realtime/consumers.py → RetrospectiveConsumer.connect()`

**Por quê:** a decisão foi reduzir carga no handshake. O frontend compensa com chamadas REST logo após conectar.

---

## 12. Variáveis de ambiente

### Backend

Fonte: `backend/.env.example`, `backend/.env.prod.example`, `config/settings/base.py`.

| Variável | Obrigatória | Descrição | Padrão (dev/code) |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | Sim (prod) | Chave criptográfica Django | `retroapp4l-dev-secret-key-with-minimum-32-bytes` |
| `DJANGO_DEBUG` | Não | `true`/`false`; `DEBUG` Django | `false` |
| `DJANGO_ALLOWED_HOSTS` | Sim (prod) | Hosts permitidos, vírgula-separados | `localhost,127.0.0.1` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Prod | Origins CSRF confiáveis | `""` (vazio) |
| `CORS_ALLOWED_ORIGINS` | Sim | Origins CORS permitidas | `http://localhost:3000` |
| `ALLOWED_EMAIL_DOMAINS` | Não | Restringe domínios de cadastro; vazio = todos | `""` (sem restrição) |
| `DB_ENGINE` | Não | `postgres` usa PostgreSQL; qualquer outro usa SQLite | SQLite |
| `POSTGRES_DB` | Se postgres | Nome do banco | `retroapp4l` |
| `POSTGRES_USER` | Se postgres | Usuário | `retroapp4l` |
| `POSTGRES_PASSWORD` | Se postgres | Senha | `retroapp4l` |
| `POSTGRES_HOST` | Se postgres | Hostname | `localhost` |
| `POSTGRES_PORT` | Se postgres | Porta | `5432` |
| `REDIS_URL` | Sim | Broker Celery + Channel Layer | `redis://localhost:6379/0` |
| `USE_IN_MEMORY_CHANNEL_LAYER` | Não | `false` = Redis Channel Layer; `true` = memória (padrão se não postgres) | auto |
| `CLOUDFLARE_TURNSTILE_SECRET_KEY` | Prod | Validação Turnstile; vazio = bypass automático | `""` |

### Frontend

Fonte: `nuxt.config.ts`, `frontend/Dockerfile` (ARG para Turnstile).

| Variável | Obrigatória | Descrição | Padrão (dev) |
|---|---|---|---|
| `NUXT_PUBLIC_API_BASE` | Sim | URL base da API REST (sem trailing slash) | `http://localhost:8000/api` |
| `NUXT_PUBLIC_WS_BASE` | Sim | URL base WebSocket | `ws://localhost:8000/ws` |
| `NUXT_PUBLIC_TURNSTILE_SITE_KEY` | Prod | Site key Cloudflare; default é a chave de teste pública | `1x00000000000000000000AA` |

> `NUXT_PUBLIC_TURNSTILE_SITE_KEY` é injetada em **build time** via `ARG` no `frontend/Dockerfile`. Não pode ser alterada pós-build sem rebuild.

---

## 13. Decisões de design registradas

### JWT em localStorage

**Decisão:** tokens JWT (access + refresh) armazenados em `localStorage` do navegador.

**Alternativa descartada:** cookies HttpOnly gerenciados pelo servidor.

**Trade-off:** localStorage simplifica SPA e WebSocket (token pode ser passado como query string sem CSRF). Em troca, perde a proteção contra XSS: um script malicioso na página pode roubar os tokens. Cookies HttpOnly exigiriam configuração adicional de CSRF no backend e tornariam o WS mais complexo.

---

### Guest como `User` com `is_guest=True`

**Decisão:** usuários guest são rows reais na tabela `users_user` com `is_guest=True`, e-mail sintético e senha inutilizável.

**Alternativa descartada:** tabela separada `GuestUser` ou identificação por session/cookie.

**Trade-off:** simplifica todas as FKs (cards, votos, participants, action items apontam para `User` sem exceção) e permite JWT normal. Em troca, guests acumulam no banco sem mecanismo de limpeza.

---

### `session.snapshot` parcial

**Decisão:** o snapshot WebSocket inicial contém apenas `phase` e `action_items`. Cards, votos, milestones e participantes chegam vazios.

**Alternativa descartada:** snapshot completo no connect, como um dump do estado atual.

**Trade-off:** conexão WS mais rápida; a carga de serialização do estado completo fica nas chamadas REST. Em troca, o frontend precisa de 5 chamadas REST após cada conexão/reconexão, e há uma janela de inconsistência entre o snapshot e os dados REST.

---

### `state_machine.py` existente mas não aplicado

**Decisão:** `apps/realtime/state_machine.py` define `PHASE_TRANSITIONS` e `is_valid_transition()`, mas o consumer não chama `is_valid_transition`.

**Alternativa descartada:** validação linear de transições no consumer.

**Trade-off:** facilita desenvolvimento e testes (facilitador pode ir para qualquer fase válida). Em troca, abre a possibilidade de estados inconsistentes (ex: pular `voting` e ir para `discussion` sem votos).

---

### `focus_card` persistido no banco

**Decisão:** `Retrospective.focus_card` é uma FK no banco, atualizada a cada `POST /focus-card/` ou `POST /next-card/`.

**Alternativa descartada:** estado em memória no consumer ou channel layer.

**Trade-off:** sobrevive a reconexões e restarts do consumer. Em troca, gera uma escrita no banco a cada troca de card em foco.

---

### `phase_durations` como JSONField

**Decisão:** durações por fase armazenadas em `{"board": 900, "voting": 120}` em um único JSONField.

**Alternativa descartada:** colunas dedicadas (`timer_board_seconds`, `timer_voting_seconds`, etc.).

**Trade-off:** schema flexível; novas fases não exigem migrations. Em troca, o campo não é queryable diretamente pelo banco e o lookup tem fallback manual: `(retro.phase_durations or {}).get(phase) or DEFAULT_PHASE_DURATIONS.get(phase, 0)`.

---

### Worker Celery com Beat no mesmo processo

**Decisão:** `celery -A config worker -B -l info` — worker e scheduler Beat no mesmo processo.

**Alternativa descartada:** processos separados (`celery worker` + `celery beat`).

**Trade-off:** operação simplificada com um único container. Em troca, não é HA: restart do worker perde o scheduler Beat e qualquer task em execução.

---

### `team_key` como SlugField sem entidade `Team`

**Decisão:** retrospectivas agrupadas por `team_key` (SlugField 100 chars). Não existe model `Team`.

**Alternativa descartada:** FK para entidade `Team` com CRUD próprio.

**Trade-off:** zero sobrecarga de gerenciar times; qualquer string slug vira um time. Em troca, não é possível renomear um time sem atualizar todas as retros, e não há isolamento de permissões por time.

---

## 14. Limitações conhecidas e débito técnico

| Item | Descrição | Impacto | Localização |
|---|---|---|---|
| Transições de fase sem validação linear | `state_machine.py` define a ordem correta, mas o consumer não chama `is_valid_transition()`. Facilitador pode avançar para qualquer fase válida via WS. | Inconsistência de dados possível (ex: `discussion` sem `voting`) | `apps/realtime/consumers.py:persist_phase_advance()`, `apps/realtime/state_machine.py` |
| `session.snapshot` parcial | Cards, votos, milestones e participantes chegam vazios no snapshot. Frontend precisa de 5 chamadas REST adicionais após cada conexão. | Latência extra na entrada; janela de inconsistência | `apps/realtime/consumers.py:connect()` |
| Estado de apresentação de marcos em memória | `RetrospectiveConsumer.presentation_indices` é um dict de classe (em memória por processo). Perde estado em restart; não compartilhado entre múltiplos workers Daphne. | Navegação de slides quebra em produção multi-processo | `apps/realtime/consumers.py:211` |
| Presença online/offline estimada por WS | `PresenceView` retorna participantes cadastrados, não online. Online/offline é estimado no frontend via `participant.joined`/`participant.left` WS. Estado pode ficar impreciso em quedas abruptas. | Contador de presença incorreto | `apps/retrospectives/views.py:PresenceView`, `stores/participants.ts` |
| MDI icons sem dependência declarada | Classes `mdi mdi-*` usadas em vários componentes Vue, mas `@mdi/font` ou equivalente não está em `package.json`. | Ícones MDI não renderizam sem CSS externo | `frontend/components/**/*.vue`, `frontend/package.json` |
| Google OAuth incompleto | `auth/login.vue` tem link para `/accounts/google/login/` (django-allauth). Settings não configura provider Google. | Botão falha em produção | `frontend/pages/auth/login.vue`, `config/settings/base.py` |
| Convite temporário não fecha ao entrar | Entrar via `POST /invites/{token}/join/` durante janela temporariamente aberta não fecha o link. Outros podem entrar até a task Celery disparar 120s depois. | Mais participantes do que o esperado podem entrar | `apps/retrospectives/views.py:InviteJoinView`, `tasks/invite.py` |
| `tasks/timer.py:sync_timer` é stub | Retorna apenas `{"retrospective_id": ..., "status": "scheduled"}`. A task real de timer está em `apps/realtime/tasks.py:timer_sync_task`. | Confusão: dois arquivos de timer, um inoperante | `tasks/timer.py` |
| `participant.joined_late` sem emissão REST | Consumer tem handler `participant_joined_late()` e aceita evento `participant.joined_late` no `receive_json`, mas nenhuma view REST emite esse evento via channel layer. | Handler inativo | `apps/realtime/consumers.py:315-326` |
| `print()` de debug no middleware WS | `JWTAuthMiddleware` tem `print()` ativos que poluem os logs em produção | Performance/logs ruidosos | `apps/realtime/middleware.py:22,28,32,34` |
| `allow_self_vote` não alterável pós-criação | `PUT /votes-config/` altera apenas `max_votes_per_user`. Não há endpoint para alterar `allow_self_vote` após criar a retro. | Configuração incompleta pós-criação | `apps/cards/views.py:VotesConfigView` |
