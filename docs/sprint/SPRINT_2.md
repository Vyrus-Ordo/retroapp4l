# Sprint 2 — Core Real-time

## Contexto

Implementa a infraestrutura de comunicação em tempo real: Django Channels com WebSocket, máquina de estados das fases da retrospectiva e cronômetro sincronizado via Celery Beat.

**Referência no PRD:** Seções 6 (Stack), 9 (Eventos WebSocket), 12.3 (Planejamento)

---

## Objetivos

1. Configurar Django Channels + ASGI (Daphne) como servidor
2. Implementar consumers WebSocket com autenticação JWT
3. Implementar máquina de estados de fases (10 estados)
4. Implementar cronômetro com pausa/retoma via Celery Beat
5. Implementar distinção entre nova entrada e reconexão de participante

---

## Entregáveis

### Backend (Django)

- [ ] **ASGI + Daphne:**
  - Configuração ASGI em `config/asgi.py` com `ProtocolTypeRouter`
  - Integração com Django Channels
  - Daphne como servidor ASGI (substitui runserver em produção)

- [ ] **Channel Layer:**
  - Configuração do Redis como channel layer (`config/settings/`)
  - Grupos por retrospectiva: `retro_{retrospective_id}`

- [ ] **WebSocket Authentication:**
  - Middleware customizado valida JWT antes de aceitar conexão
  - Conexões sem token válido recusadas com código 4001
  - Token extraído da query string ou headers

- [ ] **App `realtime` — Consumers:**
  - `RetroConsumer` (herda de `AsyncJsonWebsocketConsumer` ou base customizada)
  - `connect`: autentica JWT, verifica permissão de acesso, adiciona ao grupo, envia `session.snapshot`
  - `disconnect`: registra saída do participante, transmite `participant.left`
  - `receive`: roteia eventos de entrada (`card.create`, `vote.cast`, `phase.advance`, etc.)

- [ ] **Eventos WebSocket implementados (Seção 9 do PRD):**
  - `session.snapshot` — Server → Client: `{phase, timer, cards[], votes[], milestones[], participants[], action_items[]}`
  - `phase.changed` — Server → Clients: `{phase, timer_duration_seconds}`
  - `timer.sync` — Server → Clients: `{seconds_remaining}` (a cada 5s)
  - `timer.paused` — Server → Clients: `{seconds_remaining}`
  - `timer.resumed` — Server → Clients: `{seconds_remaining}`
  - `timer.expired` — Server → Clients: `{phase}`
  - `participant.joined` — Server → Clients: `{user_id, name, avatar_url}` (durante lobby)
  - `participant.joined_late` — Server → Clients: `{user_id, name, avatar_url}` (após lobby)
  - `participant.left` — Server → Clients: `{user_id}`

- [ ] **Máquina de Estados de Fases:**
  - 10 estados: `setup → lobby → presentation → check → board → grouping → voting → discussion → actions → closed`
  - Transições controladas por ações do facilitador via API REST ou WebSocket
  - Validação de transições (ex: não pular de `setup` para `board`)
  - Ao avançar fase: broadcast `phase.changed` para todos os conectados
  - Confirmação obrigatória antes de avançar para fase de encerramento (`closed`)

- [ ] **Cronômetro (Celery Beat):**
  - Task periódica emite `timer.sync` a cada 5s para o grupo da retrospectiva
  - Detecta quando cronômetro expira, emite `timer.expired` e avança fase automaticamente
  - Suporte a pausa: `timer_paused_at` no model `Retrospective`
  - Suporte a retoma: recalcula tempo restante com base em `timer_paused_at`
  - Fase sem cronômetro: `presentation` e `grouping`

- [ ] **Gerenciamento de Participantes:**
  - Nova entrada (sem registro em `Participant`): recebe `session.snapshot` completo
  - Reconexão (já registrado em `Participant`): recebe `session.snapshot` para ressincronizar
  - Reconexão sempre permitida independentemente do status do link
  - Registro no `AccessLog` para cada entrada

- [ ] **Controle de Link de Convite (API REST):**
  - `POST /api/retrospectives/{id}/activate-invite/` — Gera `invite_token` (UUID v4)
  - `POST /api/retrospectives/{id}/revoke-invite/` — Define `invite_revoked_at`
  - `POST /api/retrospectives/{id}/reopen-entry/` — Reabre link por 2 minutos (US-02b)
  - `GET /api/retrospectives/{id}/invite-status/` — Status do link (ativo/bloqueado)

- [ ] **Endpoint de Join via Link:**
  - `GET /api/invite/{token}/` — Valida token, autentica usuário, registra participante
  - Link bloqueado após lobby (status diferente de `lobby`)
  - Tentativas com link bloqueado retornam mensagem informativa

---

## Requisitos Funcionais Cobertos

| ID | Descrição | Status |
|---|---|---|
| RF-03 | Participante acessa via link; link bloqueado após lobby; facilitador reabre temporariamente | ✅ |
| RF-04 | Facilitador avança fases manualmente; pausa e retoma cronômetro | ✅ |
| RF-05 | Cronômetro no servidor via Celery Beat; sincronizado a cada 5s; suporte a pausa | ✅ |
| RF-16 | Lista de participantes online; painel de controle de entrada | ✅ |

---

## Requisitos Não Funcionais

- Latência WebSocket: < 200ms em rede interna
- `timer.sync` emitido a cada 5s
- `session.snapshot` enviado em < 1s para novos participantes
- Cobertura de testes ≥ 80% no app `realtime`

---

## Critérios de Done

- [ ] Conexão WebSocket estabelecida com autenticação JWT
- [ ] `session.snapshot` enviado ao conectar
- [ ] `phase.changed` broadcast ao avançar fase
- [ ] Cronômetro sincronizado via `timer.sync` a cada 5s
- [ ] Pausa e retoma do cronômetro funcionam (`timer.paused`, `timer.resumed`)
- [ ] Cronômetro expira e emite `timer.expired`
- [ ] Link de convite funciona (geração, revogação, reabertura temporária)
- [ ] Nova entrada vs. reconexão tratados corretamente
- [ ] `python manage.py test` passa sem falhas
- [ ] `ruff check .` sem erros

---

## Handoff

Ao finalizar, gerar rascunho do `SPRINT_3_HANDOFF.md` seguindo estrutura definida no PRD seção 12.2.

---

## Referências do PRD

- Seção 6.1: Stack (Django Channels, Daphne, Celery, Redis)
- Seção 5: Fluxo da Sessão (fases e durações)
- Seção 9: Eventos WebSocket (tabela completa)
- Seção 11.1: Performance
- Seção 13.2: Trade-off Django Channels vs. solução gerenciada
- Seção 13.3: Trade-off Celery Beat vs. asyncio
