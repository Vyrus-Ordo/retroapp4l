# RetroApp 4L — Documento de Requisitos do Produto (PRD)

**Versão:** 10.0 — Estado Implementado Atual
**Data:** Maio 2026
**Status:** Reconciliado com o código-fonte atual
**Audiência:** Agente de IA, Tech Lead, contribuidores
**Licença:** MIT

> **Changelog v10.0:**
> - Documento reconciliado novamente usando o código-fonte como única fonte da verdade.
> - Fluxo efetivo de fases corrigido para refletir o frontend atual e a ausência de validação linear no WebSocket.
> - Action items atualizados: criação apenas pelo facilitador na fase `discussion`; edição/exclusão pelo facilitador em `discussion` ou `actions`.
> - Endpoints e métodos corrigidos (`votes-config` é `PUT`; previous action status é `PUT`; close exige `{confirm: true}`).
> - Payloads corrigidos: action item usa `assignee_id` como id de `Participant`; grouping usa `group_parent_id`.
> - Convites corrigidos: reabertura dura 120s e não fecha imediatamente quando alguém entra.
> - `/join` documentado como navegação simples para `/retro/{code}`, não como PIN real.
> - OAuth/Google documentado como botão existente no frontend, mas provider não configurado no backend do repositório.
> - Cards anônimos adicionados de forma incremental: `author` permanece no banco, enquanto REST, WebSocket e UI mascaram autoria quando `is_anonymous=true`.

---

## 1. Visão Geral

O RetroApp 4L é uma plataforma web open source para conduzir retrospectivas de sprint estruturadas nas quatro colunas `loved`, `loathed`, `longed` e `learned`. A experiência combina quadro colaborativo, votação, discussão focada, registro de action items, histórico de sessões fechadas e participação por convite com usuários guest.

O produto implementado é uma SPA Nuxt conectada a uma API Django/DRF com sincronização em tempo real por WebSockets. Este PRD descreve somente o que existe hoje no código.

### 1.1 Problema

- Retrospectivas em ferramentas genéricas não preservam bem o vínculo entre discussão, decisões e ações.
- Itens decididos em retro tendem a se perder entre ciclos.
- Times precisam revisar ações anteriores antes de abrir uma nova reflexão.
- Facilitadores precisam de um fluxo guiado e compartilhado, com pouca configuração.

### 1.2 Objetivos do MVP

- Permitir cadastro/login local com JWT.
- Permitir entrada por convite como usuário autenticado existente ou guest.
- Criar e conduzir sessões 4L em tempo real.
- Registrar marcos, cards, votos e action items.
- Revisar ações da última retro fechada do mesmo `team_key`.
- Salvar retrospectivas fechadas e consultá-las no histórico.
- Rodar via Docker local/prod com backend, worker, PostgreSQL, Redis, frontend e Nginx.

### 1.3 Critérios de Sucesso do MVP

Os indicadores abaixo são metas de produto, não medições implementadas automaticamente:

| Indicador | Meta |
|---|---|
| Adoção | ≥ 80% das retrospectivas do time conduzidas no RetroApp 4L |
| Rastreabilidade | ≥ 70% dos action items com responsável preenchido |
| Reabertura | ≥ 50% das sessões revisam ações anteriores |
| Estabilidade | Sem falhas perceptíveis de sincronização em sessões pequenas |
| Satisfação | NPS interno ≥ 7 após pesquisa com facilitadores |
| Custo | Operação viável em infraestrutura de baixo custo |

### 1.4 Fora do Escopo do MVP

- Integração real com Jira, Linear, Asana ou GitHub Issues. O campo `external_tracker_url` existe, mas só armazena URL.
- Exportação PDF/CSV/DOCX.
- Analytics de tendências entre sprints.
- Drag-and-drop de agrupamento.
- SSO/SAML enterprise.
- Provider OAuth social configurado no backend do repositório.
- PIN curto real para entrada. A tela `/join` apenas navega para `/retro/{code}`.
- CI/CD automatizado no repositório.

---

## 2. Premissas de Desenvolvimento

### 2.1 Modelo de execução

- O repositório é um monorepo com backend Django e frontend Nuxt.
- A documentação deve ser atualizada quando comportamento implementado mudar.
- O código-fonte atual prevalece sobre requisitos antigos.

### 2.2 Consequências arquiteturais

- Regras de permissão relevantes ficam no backend.
- O frontend pode esconder botões, mas a API continua responsável por autorizar ações.
- WebSocket propaga eventos, enquanto REST hidrata o estado inicial completo.
- Tests existentes documentam parte do comportamento, mas nem todos os fluxos têm cobertura.

### 2.3 Responsabilidades por papel

| Responsabilidade | Agente de IA | Tech Lead |
|---|---|---|
| Implementar features | ✅ | Revisa |
| Atualizar testes | ✅ | Revisa |
| Atualizar documentação | ✅ | Valida |
| Configurar ambiente local | ✅ | Valida |
| Provisionar produção | — | ✅ |
| Decidir produto fora do comportamento atual | — | ✅ |

### 2.4 Premissa de Perfil do Facilitador

O facilitador é o usuário autenticado que criou a retrospectiva. Ele conduz a sessão, controla fases/timer, gerencia entrada tardia, cria marcos na preparação, agrupa cards, escolhe card em foco, cria/edita action items e fecha a retro.

Guests não podem criar retrospectivas, acessar sugestões de times nem criar/editar/excluir marcos.

---

## 3. Perfis de Usuário

### Facilitador

Usuário autenticado não-guest que criou a sessão. É adicionado automaticamente como participante e tem permissões especiais:

- avançar fase via WebSocket;
- pausar/retomar timer;
- criar/editar/excluir marcos em `setup`;
- reabrir convite por 120s após o lobby;
- agrupar/desagrupar cards;
- definir/avançar foco de discussão;
- criar action items em `discussion`;
- editar/excluir action items em `discussion` e `actions`;
- fechar a sessão em `actions`.

### Participante

Usuário autenticado existente ou guest que entrou na retro. Pode:

- carregar a sessão;
- criar/editar/excluir seus próprios cards nas fases em que a API permite;
- votar em `loathed` e `longed` durante `voting`;
- consultar action items;
- atualizar status de ações anteriores pelo endpoint de previous-actions;
- acompanhar eventos em tempo real.

Pela UI atual, edição de status de ações anteriores aparece desabilitada para não facilitadores, mas o backend permite a atualização para qualquer participante da retro atual.

### Usuário Guest

Usuário criado via convite público quando o visitante não está autenticado. Recebe JWT, é persistido no `localStorage`, tem `is_guest=true`, senha inutilizável e e-mail interno gerado. Nome e e-mail público opcional são coletados na tela de convite.

Guest pode participar da sessão como participante comum, mas não pode criar retrospectivas, acessar `/retro/create` ou sugestões de times.

---

## 4. User Stories

### Facilitador

**US-01 — Criar sessão**

Como facilitador, quero criar uma retrospectiva com título e time.

**Critérios implementados:**
- `POST /api/retrospectives/`.
- Campos aceitos: `title`, `sprint_name`, `description`, `team_key`, `max_votes_per_user`, `allow_self_vote`, `skip_check_phase`, `phase_durations`.
- `title` e `team_key` são obrigatórios no fluxo da UI.
- Sessão inicia em `setup`.
- Facilitador é participante inicial.
- `invite_token` é gerado.
- Guest recebe 403.

---

**US-02 — Convidar participantes**

Como facilitador, quero compartilhar um link de convite.

**Critérios implementados:**
- Link da UI: `{origin}/retro/invite/{invite_token}`.
- `GET /api/invites/{token}/` retorna metadados e `invite_status`.
- `POST /api/invites/{token}/join/` adiciona participante e retorna JWT.
- Usuário autenticado entra com a própria conta.
- Usuário anônimo vira guest.
- Convite está `active` no `lobby`, `temporarily_open` durante janela reaberta ou `blocked` nos demais casos.

---

**US-02b — Reabrir entrada**

Como facilitador, quero permitir entrada tardia por tempo limitado.

**Critérios implementados:**
- `POST /api/retrospectives/{id}/reopen-entry/`.
- Apenas facilitador.
- Bloqueado em `lobby` e `closed`.
- Define `invite_temporarily_open_until = now + 120s`.
- Registra `link_reopened`.
- Emite `invite.status_updated`.
- Agenda `tasks.invite.auto_block_invite`.
- **Não há auto-bloqueio imediato quando alguém entra; o bloqueio ocorre no fim da janela.**

---

**US-03 — Controlar fases**

Como facilitador, quero avançar a sessão.

**Critérios implementados:**
- Evento WebSocket `phase.advance` com `{phase}`.
- Apenas facilitador consegue persistir mudança.
- O backend valida se `phase` existe, mas **não valida transição linear**.
- O frontend calcula a próxima fase em `usePhase.ts`.
- Ordem efetiva da UI: `setup -> lobby -> check -> presentation -> board -> grouping -> voting -> discussion -> actions -> closed`.
- `skip_check_phase` no frontend faz `lobby -> presentation`.
- Ao entrar em fase cronometrada, o backend inicia timer e emite `phase.changed`.

---

**US-04 — Configurar dot voting**

Como facilitador, quero definir votos por pessoa e auto-voto.

**Critérios implementados:**
- `max_votes_per_user` e `allow_self_vote` são definidos na criação.
- `PUT /api/retrospectives/{id}/votes-config/` altera somente `max_votes_per_user`.
- O endpoint reseta `votes_remaining` dos participantes.
- Permitido antes da fase `voting`; bloqueado em `voting`, `discussion`, `actions` e `closed`.
- `allow_self_vote` não tem endpoint de alteração pós-criação.

---

**US-05 — Encerrar sessão**

Como facilitador, quero encerrar a retro e gravá-la no histórico.

**Critérios implementados:**
- `POST /api/retrospectives/{id}/close/` com `{ "confirm": true }`.
- Apenas facilitador.
- Apenas na fase `actions`.
- Define `status=closed`, `closed_at`, remove `invite_token`, preenche `invite_revoked_at` e limpa `focus_card`.
- Emite `phase.changed`.
- Sessões fechadas aparecem em `/api/retrospectives/history/`.

---

**US-07a — Preparar marcos**

Como facilitador, quero registrar marcos da sprint antes da sessão.

**Critérios implementados:**
- `GET/POST /api/retrospectives/{id}/milestones/`.
- `GET/PUT/PATCH/DELETE /api/retrospectives/{id}/milestones/{milestone_id}/`.
- Mutação apenas pelo facilitador em `setup`.
- Guests são bloqueados.
- Categorias: `achievement`, `challenge`, `change`, `recognition`, `other`.
- `description` até 500 caracteres.

---

**US-07c — Apresentar marcos**

Como facilitador, quero mostrar marcos ao time.

**Critérios implementados:**
- A fase `presentation` existe.
- A UI atual mostra uma grade com todos os marcos.
- O consumer WebSocket também implementa eventos `milestone.presentation.start`, `.next`, `.prev`, `.end`.
- Esses eventos usam índice em memória e, se não houver marcos no `.start`, mudam a fase para `check`.
- A UI atual não usa esses eventos de navegação; apenas exibe os marcos e botão de próxima fase.

---

**US-09 — Agrupar cards**

Como facilitador, quero agrupar cards similares.

**Critérios implementados:**
- `POST /api/retrospectives/{id}/cards/group/`.
- Payload: `{ "card_ids": [...], "group_parent_id": "uuid opcional" }`.
- Mínimo 2 cards.
- Todos os cards precisam pertencer à mesma retro e mesma coluna.
- Apenas facilitador.
- Não há restrição explícita de fase no backend além de sessão não fechada.
- UI expõe agrupamento na fase `grouping`.
- Cards filhos preservam `group`/`group_parent_id` ao avançar para votação e discussão e são renderizados como sub-itens do card pai em um único nível visual.

---

**US-12 — Conduzir debate focado**

Como facilitador, quero discutir cards priorizados e registrar decisões.

**Critérios implementados:**
- `GET /api/retrospectives/{id}/cards/` ordena por votos na fase `discussion`.
- `POST /api/retrospectives/{id}/focus-card/` define `focus_card`.
- `POST /api/retrospectives/{id}/next-card/` avança no ranking de votos e volta ao início ao fim da fila.
- Apenas facilitador e apenas em `discussion`.
- Broadcast `discussion.focus_updated`.
- `focus_card_id` aparece no detalhe da retro.
- Facilitador pode criar action items durante `discussion`.

---

**US-12b — Revisar ata na fase de ações**

Como facilitador, quero revisar os action items antes de fechar.

**Critérios implementados:**
- Fase `actions` exibe action items existentes.
- Criação de action item é bloqueada na fase `actions`.
- Edição e exclusão são permitidas ao facilitador em `actions`.
- Participantes têm leitura na UI e no backend não passam nas mutações por não serem facilitadores.
- Fechamento da retro ocorre nesta fase.

---

### Participante

**US-06 — Verificar ações anteriores**

Como participante, quero revisar ações da retro anterior.

**Critérios implementados:**
- `GET /api/retrospectives/{id}/previous-actions/`.
- Busca a última retro `closed` do mesmo `team_key`.
- Retorna `{ retrospective_id, action_items }` ou lista vazia.
- `PUT /api/retrospectives/{id}/previous-actions/{action_id}/status/` atualiza status.
- Status aceitos: `not_started`, `in_progress`, `done` e alias legado `pending` convertido para `not_started`.

---

**US-08 — Adicionar card ao board**

Como participante, quero adicionar cards nas colunas 4L.

**Critérios implementados:**
- `POST /api/retrospectives/{id}/cards/`.
- `column`: `loved`, `loathed`, `longed`, `learned`.
- `content` até 500 caracteres.
- `is_anonymous` opcional; default `false`.
- Autor é sempre o usuário autenticado.
- Cards anônimos mantêm `author` no banco, mas retornam `author=null`, `author_name=null` e `author_display="Anonymous participant"` nos payloads públicos.
- A API retorna `can_edit` calculado por usuário para preservar edição/exclusão do próprio card sem revelar autoria visual.
- Autor pode editar/excluir pelo endpoint de detalhe.
- API bloqueia mutações de card em `discussion`, `actions` e `closed`.
- UI só expõe criação/edição/exclusão na fase `board`.
- UI permite marcar/desmarcar `Add anonymously` ao criar ou editar card.

---

**US-10 — Votar em cards prioritários**

Como participante, quero distribuir meus votos.

**Critérios implementados:**
- `POST /api/retrospectives/{id}/cards/{card_id}/vote/` registra voto.
- `DELETE /api/retrospectives/{id}/cards/{card_id}/vote/` revoga voto.
- Apenas na fase `voting`.
- Apenas colunas `loathed` e `longed`.
- 1 voto por card por participante.
- Sem votos restantes retorna 403.
- `allow_self_vote=false` bloqueia voto no próprio card, inclusive quando ele é anônimo, usando a autoria real interna.
- Broadcast `vote.cast` e `vote.revoked`.

---

**US-11 — Registrar item de ação**

Como participante, quero ver os itens de ação definidos.

**Critérios implementados:**
- O participante pode listar action items da retro.
- A criação é restrita ao facilitador em `discussion`.
- Payload de criação/edição usa `assignee_id` como id de `Participant`.
- `card_id`, `due_date`, `status`, `external_tracker_url` são opcionais.
- `status` inicial é `not_started`.

---

## 5. Fluxo da Sessão de Retrospectiva

| Fase | Duração padrão | Quem edita pela UI | Comportamento atual |
|---|---:|---|---|
| Preparação (`setup`) | — | Facilitador | Tela de preparação; marcos podem ser criados via API nesta fase. |
| Lobby (`lobby`) | — | Facilitador | Convite ativo; participantes entram via link. |
| Check de ações (`check`) | 5 min | Facilitador na UI | Mostra ações da última retro fechada do mesmo time. |
| Marcos (`presentation`) | 10 min | Facilitador | UI mostra marcos cadastrados; eventos WS de apresentação existem, mas não são usados pela tela atual. |
| Board 4L (`board`) | 15 min | Todos | UI permite criar/editar/excluir cards próprios. |
| Agrupamento (`grouping`) | 5 min | Facilitador | UI permite selecionar e agrupar cards da mesma coluna. |
| Votação (`voting`) | 3 min | Todos | Votos em `loathed` e `longed`. |
| Discussão (`discussion`) | 15 min | Facilitador | Foco por card e criação de action items. Cards ficam read-only. |
| Ações (`actions`) | 10 min | Facilitador | Revisão, edição/exclusão de action items e fechamento. |
| Fechada (`closed`) | — | Ninguém | Sessão ativa e WS são bloqueados; histórico fica disponível. |

**Observação importante:** a ordem acima é a ordem efetiva do frontend. O arquivo `state_machine.py` lista `presentation` antes de `check`, mas não é aplicado no consumer WebSocket.

---

## 6. Stack Tecnológica

### 6.1 Stack de desenvolvimento

| Camada | Tecnologia implementada |
|---|---|
| Frontend | Nuxt 3.17.5, Vue 3, Pinia, TailwindCSS |
| Auth frontend | JWT em localStorage via Pinia |
| CAPTCHA | `@nuxtjs/turnstile` + validação backend |
| Backend | Django 5.2.13, DRF 3.16.1 |
| Auth backend | SimpleJWT 5.5.1 |
| WebSocket | Channels 4.2.2, Daphne 4.2.1 |
| Tarefas | Celery 5.5.3 |
| Banco | SQLite local por padrão; PostgreSQL via env |
| Redis | Channel Layer, Celery broker/result backend |
| Lint backend | Ruff |
| E2E frontend | Playwright |

### 6.2 Infraestrutura (MVP Zero-Cost — alvo de deploy)

O repositório contém Dockerfiles e compose para deploy próprio. A documentação anterior citava Fly.io/Neon/Upstash/Vercel como alvo possível, mas o código atual também inclui `docker-compose.prod.yml` com Nginx para domínio `retroapp4l.privo.app.br`.

### 6.3 Arquitetura de deployment

- Backend: `backend/Dockerfile`, roda `collectstatic`, `migrate` e Daphne.
- Worker: `backend/Dockerfile.worker`, roda `migrate` e `celery -A config worker -B -l info`.
- Frontend: `frontend/Dockerfile`, roda `npm run build` e serve `.output/server/index.mjs`.
- Nginx: proxy HTTPS para frontend, API, admin, WebSocket e static files.

### 6.4 Estrutura de repositório (monorepo)

```text
backend/
  apps/users/
  apps/retrospectives/
  apps/cards/
  apps/actions/
  apps/realtime/
  config/
  tasks/
frontend/
  pages/
  components/
  stores/
  composables/
  utils/
nginx/
docs/
```

---

## 7. Design System

### 7.1 Visão geral

A UI usa TailwindCSS com componentes próprios. O visual é dark/neon, com painéis translúcidos, botões customizados e imagem de landing em `public/img/board_jedi.png`.

### 7.2 Tipografia

- `tailwind.config.ts` define `Poppins` como `font-sans`.
- Algumas telas aplicam `JetBrains Mono` diretamente em classes.

### 7.3 Paleta de cores

- Tokens Tailwind: `brand`, `success`, `warning`, `danger`, `gray`.
- Tokens CSS em `assets/css/tokens.css`: `--ds-*`, `--fg-*`, `--bg-*`, `--border-*`.

### 7.4 Ícones

- `@heroicons/vue` é dependência instalada e usada em vários componentes.
- Classes `mdi mdi-*` também aparecem em várias telas, mas não há pacote ou CSS MDI declarado no `package.json`. A renderização desses ícones depende de CSS externo não presente no código.

### 7.5 Componentes UI Implementados

- Layout: `AppShell`, `AppHeader`, `AppSidebar`, `AppFooter`, `PhaseStepper`, `PhaseCarousel`, `RetroHeader`, `SettingsModal`.
- Retro: `TimerDisplay`, `RetroCard`, `VoteBadge`, `FocusCard`, `ActionEditor`, `MilestoneCard`.
- Board: `BoardGrid`, `ColumnHeader`, `FocusCard`.
- Forms: `CardComposer`, `ActionItemForm`.
- Participantes: `ParticipantPanel`.
- Histórico: `HistoryTable`.

---

## 8. Modelo de Dados

### users_user *(app: users)*

| Campo | Tipo / regra |
|---|---|
| `id` | UUID PK |
| `name` | CharField 255 |
| `email` | EmailField único |
| `public_email` | EmailField opcional |
| `oauth_provider`, `oauth_id`, `avatar_url` | Campos opcionais |
| `is_guest` | Boolean default false |
| `is_active`, `is_staff` | Booleans |
| `created_at` | auto_now_add |

### retrospectives_retrospective *(app: retrospectives)*

| Campo | Tipo / regra |
|---|---|
| `id` | UUID PK |
| `title` | CharField 255 |
| `sprint_name` | CharField opcional/null |
| `description` | TextField blank |
| `team_key` | SlugField 100 |
| `facilitator` | FK User |
| `status` | choice de fases |
| `invite_token` | UUID único opcional |
| `invite_revoked_at` | DateTime opcional |
| `max_votes_per_user` | PositiveSmallInteger default 3 |
| `allow_self_vote` | Boolean default false |
| `skip_check_phase` | Boolean default false |
| `focus_card` | FK Card opcional |
| `invite_temporarily_open_until` | DateTime opcional |
| `timer_started_at`, `timer_paused_at`, `timer_duration_seconds` | Timer |
| `phase_durations` | JSONField default `{}` |
| `created_at`, `closed_at` | Datas |

### retrospectives_milestone *(app: retrospectives)*

`id`, `retrospective`, `author`, `category`, `description`, `created_at`.

### retrospectives_participant *(app: retrospectives)*

`id`, `retrospective`, `user`, `votes_remaining`, `joined_at`, com unique constraint `retrospective + user`.

### retrospectives_accesslog *(app: retrospectives)*

`id`, `retrospective`, `action`, `triggered_by`, `participant`, `timestamp`.

### cards_card *(app: cards)*

`id`, `retrospective`, `author`, `column`, `content`, `is_anonymous`, `group`, `position`, `created_at`.

`is_anonymous` tem default `false`. Cards antigos continuam não anônimos. O campo `author` nunca é removido e segue sendo usado para permissões, auditoria, votos, edição/exclusão e relacionamentos.

### cards_cardvote *(app: cards)*

`id`, `card`, `voter`, `created_at`, com unique constraint `card + voter`.

### actions_actionitem *(app: actions)*

`id`, `retrospective`, `card`, `description`, `assignee`, `due_date`, `external_tracker_url`, `status`, `created_at`.

---

## 9. Eventos WebSocket

| Evento | Direção | Payload / efeito |
|---|---|---|
| `session.snapshot` | S → C | `phase`, `timer:null`, arrays vazios de cards/votes/milestones/participants e `action_items` |
| `phase.advance` | C → S | `{phase}`; facilitador altera status para qualquer choice válido |
| `phase.changed` | S → C | `{phase, timer_duration_seconds}` |
| `milestone.presentation.start` | C → S | inicia índice em memória; se sem marcos, vai para `check` |
| `milestone.presentation.next` | C → S | avança índice em memória |
| `milestone.presentation.prev` | C → S | volta índice em memória |
| `milestone.presentation.end` | C → S | muda fase para `check` |
| `milestone.presentation` | S → C | `{index,total,milestone}` |
| `timer.pause` | C → S | pausa se facilitador |
| `timer.resume` | C → S | retoma se facilitador |
| `timer.paused` | S → C | `{seconds_remaining}` |
| `timer.resumed` | S → C | `{seconds_remaining}` |
| `timer.sync` | S → C | `{seconds_remaining}` a cada 5s |
| `timer.expired` | S → C | `{phase}` |
| `card.created` | S → C | `{card}` com autoria mascarada se `is_anonymous=true` |
| `card.updated` | S → C | `{card_id, content, card}`; `card` respeita anonimato |
| `card.deleted` | S → C | `{card_id}` |
| `card.grouped` | S → C | `{card_id, group_id, group_parent_id}` |
| `card.ungrouped` | S → C | `{card_id, previous_group_id}` |
| `vote.cast` | S → C | `{card_id, voter_id, votes_remaining}` ou `{vote}` em caminho legado do consumer |
| `vote.revoked` | S → C | `{card_id, voter_id, votes_remaining}` |
| `action.created` | S → C | `{action}` |
| `action.updated` | S → C | `{action}` |
| `action.deleted` | S → C | `{action_id}` |
| `action.check_updated` | S → C | `{action_id,status}` |
| `discussion.focus_updated` | S → C | card em foco; quando anônimo inclui `author:null`, `author_display:"Anonymous participant"` e `is_anonymous:true` |
| `participant.joined` | S → C | `{user_id, participant_id, name, avatar_url}` |
| `participant.left` | S → C | `{user_id}` |
| `participant.joined_late` | S → C | handler existe, mas não há emissão REST atual |
| `invite.status_updated` | S → C | `{invite_status, expires_at}` |

---

## 10. Endpoints REST

### Autenticação (`/api/auth/`)

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/auth/register/` | Cadastro local com Turnstile; retorna JWT |
| POST | `/api/auth/login/` | Login local; guests são bloqueados |
| POST | `/api/auth/logout/` | Blacklist do refresh token |
| POST | `/api/auth/refresh/` | Renova access token |

### Convites (público)

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/invites/{token}/` | Metadados públicos e status do convite |
| POST | `/api/invites/{token}/join/` | Entra como usuário autenticado ou guest |

### Retrospectivas

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/retrospectives/` | Lista retros acessíveis ao usuário |
| POST | `/api/retrospectives/` | Cria retro |
| GET | `/api/retrospectives/{id}/` | Detalhe de sessão ativa |
| GET | `/api/retrospectives/history/` | Lista retros fechadas |
| GET | `/api/retrospectives/{id}/detail/` | Detalhe de retro fechada |
| POST | `/api/retrospectives/{id}/close/` | Fecha retro; exige `{confirm:true}` |
| POST | `/api/retrospectives/{id}/focus-card/` | Define card em foco |
| POST | `/api/retrospectives/{id}/next-card/` | Próximo card em foco |
| POST | `/api/retrospectives/{id}/reopen-entry/` | Reabre convite por 120s |
| GET | `/api/retrospectives/{id}/invite-status/` | Status do convite |
| GET | `/api/retrospectives/{id}/presence/` | Lista participantes cadastrados |
| GET | `/api/teams/suggestions/` | Sugestões de `team_key` para não-guest |

### Marcos

| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/api/retrospectives/{id}/milestones/` | Lista/cria marcos |
| GET/PUT/PATCH/DELETE | `/api/retrospectives/{id}/milestones/{milestone_id}/` | Detalhe/edita/remove |

### Cards

| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/api/retrospectives/{id}/cards/` | Lista/cria cards |
| GET/PATCH/DELETE | `/api/retrospectives/{id}/cards/{card_id}/` | Detalhe/edita/remove |
| POST | `/api/retrospectives/{id}/cards/group/` | Agrupa cards |
| POST | `/api/retrospectives/{id}/cards/{card_id}/ungroup/` | Desagrupa card |
| POST/DELETE | `/api/retrospectives/{id}/cards/{card_id}/vote/` | Vota/revoga |
| GET | `/api/retrospectives/{id}/votes/` | Lista votos |
| PUT | `/api/retrospectives/{id}/votes-config/` | Altera `max_votes_per_user` |

### Action Items

| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/api/retrospectives/{id}/action-items/` | Lista/cria action items |
| GET/PATCH/DELETE | `/api/retrospectives/{id}/action-items/{action_id}/` | Detalhe/edita/remove |
| GET | `/api/retrospectives/{id}/previous-actions/` | Ações da última retro fechada do mesmo time |
| PUT | `/api/retrospectives/{id}/previous-actions/{action_id}/status/` | Atualiza status de ação anterior |

---

## 11. Requisitos Funcionais

| # | Módulo | Descrição | Status |
|---|---|---|---|
| RF-01 | Autenticação | Cadastro/login/logout/refresh via SimpleJWT | ✅ Implementado |
| RF-02 | Segurança | Turnstile obrigatório no cadastro | ✅ Implementado |
| RF-03 | Guests | Entrada por convite com usuário `is_guest=True` | ✅ Implementado |
| RF-04 | Sessão | Criação de retro por usuário não-guest | ✅ Implementado |
| RF-05 | Convite | Link UUID ativo no lobby e reabertura por 120s | ✅ Implementado |
| RF-06 | Fases | Avanço via WS pelo facilitador | ⚠️ Implementado sem validação linear |
| RF-07 | `skip_check_phase` | Frontend pula `check` ao sair do lobby | ⚠️ Implementado na UI, não no backend |
| RF-08 | Timer | Timer por fase, pausa/retomada, sync Celery 5s | ✅ Implementado |
| RF-09 | Marcos | CRUD pelo facilitador em `setup` | ✅ Implementado |
| RF-10 | Board | Cards 4L com realtime | ✅ Implementado |
| RF-10b | Cards anônimos | Anonimato visual em REST, WebSocket, board, grouping, voting, discussion, focus e histórico com autoria real preservada | ✅ Implementado |
| RF-11 | Agrupamento | Agrupar cards da mesma coluna | ✅ Implementado |
| RF-12 | Votação | Dot voting em `loathed`/`longed` | ✅ Implementado |
| RF-13 | Discussão | Foco de card e ranking por votos | ✅ Implementado |
| RF-14 | Ações | Action items criados em `discussion`, revisados em `actions` | ✅ Implementado |
| RF-15 | Ações anteriores | Consulta e atualização de status da retro anterior | ✅ Implementado |
| RF-16 | Histórico | Lista e detalhe de retros fechadas | ✅ Implementado |
| RF-17 | Presença | Eventos de entrada/saída e painel frontend | ⚠️ Estimado por WS/local state |
| RF-18 | Snapshot WS | Snapshot parcial com action items | ⚠️ Parcial |
| RF-19 | OAuth Google | Botão existe na UI; provider não configurado no backend | ⚠️ Incompleto |
| RF-20 | CI/CD | Workflows não existem no repositório | ❌ Não implementado |

---

## 12. Requisitos Não Funcionais

### 12.1 Performance

- `timer.sync` é emitido a cada 5s enquanto timer está rodando.
- Frontend interpola contagem localmente.
- Snapshot WebSocket é leve por ser parcial.

### 12.2 Segurança

- JWT access token: 8h.
- JWT refresh token: 7d.
- Refresh token blacklist no logout.
- WebSocket autenticado por JWT.
- Convite usa UUID.
- Guests têm senha inutilizável.
- Facilitador é verificado server-side em ações privilegiadas.
- `ALLOWED_EMAIL_DOMAINS`, CORS e CSRF trusted origins são configuráveis por env.
- `allow_self_vote=false` por padrão.
- Cards anônimos não alteram autenticação, guests ou permissões; eles apenas mascaram dados visuais do autor nos payloads públicos e na UI.

### 12.3 Disponibilidade

- Sem SLA formal.
- Worker Celery com Beat embutido (`worker -B`).
- Nginx de produção configurado para TLS e proxy WebSocket.

### 12.4 Escalabilidade

- Channels pode usar Redis Channel Layer.
- Celery worker é serviço separado.
- O estado de apresentação de marcos é em memória e não escala bem entre processos.

### 12.5 Qualidade de código

- Backend: Ruff configurado.
- Backend tests: Django `manage.py test` e pytest-django presentes.
- Frontend: ESLint/Prettier e Playwright configurados.
- Build esperado: `npm run build`.

---

## 13. Limitações Conhecidas e Débitos Técnicos

| Item | Descrição | Impacto |
|---|---|---|
| Transição de fases sem validação linear | `state_machine.py` existe, mas consumer não usa `is_valid_transition` | Facilitador pode saltar para qualquer fase válida via payload |
| Ordem de fases divergente | Frontend usa `check` antes de `presentation`; backend enum/state_machine lista o oposto | Documentação e testes podem confundir |
| `session.snapshot` parcial | Cards, votos, marcos e participantes vêm vazios | Frontend depende de REST após conectar |
| Índice de apresentação em memória | `presentation_indices` perde estado em restart e não é compartilhado entre workers | Navegação de apresentação é frágil |
| Convite temporário não auto-fecha ao entrar | Janela fica aberta até expirar a tarefa Celery | Mais de um participante pode entrar na mesma janela |
| Presença não persistida | Online/offline depende de eventos do cliente | Pode ficar impreciso em quedas abruptas |
| `votes-config` limitado | Não altera `allow_self_vote` | Configuração pós-criação incompleta |
| API de cards mais permissiva que UI | Backend bloqueia cards só em `discussion/actions/closed` | Cards podem ser criados antes/depois do board via API |
| Agrupamento sem restrição de fase | Backend permite em qualquer fase não fechada | Facilitador pode agrupar fora da fase prevista |
| MDI sem dependência declarada | Classes `mdi` existem sem pacote/CSS no repo | Ícones podem não renderizar |
| Google OAuth incompleto | UI aponta para `/accounts/google/login/`; provider não configurado | Botão pode falhar |
| `/join` não resolve convite | Só navega para `/retro/{code}` | Não é entrada por PIN real |

---

## 14. Deploy em Produção

Esta seção descreve o que existe no repositório para produção. Provedores externos podem ser usados, mas não há arquivos `fly.toml` ou workflows dedicados.

### 14.1 Pré-requisitos

1. Docker e Docker Compose.
2. PostgreSQL e Redis via compose ou serviços externos.
3. Domínio/TLS se usar o Nginx de produção.
4. Variáveis em `backend/.env.prod`.

### 14.2 Banco de Dados — PostgreSQL

`DB_ENGINE=postgres` ativa PostgreSQL. Variáveis usadas:

```bash
POSTGRES_DB=retroapp4l
POSTGRES_USER=retroapp4l
POSTGRES_PASSWORD=...
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Sem `DB_ENGINE=postgres`, o backend usa SQLite local em `backend/db.sqlite3`.

### 14.3 Redis

`REDIS_URL` alimenta:

- `CHANNEL_LAYERS` quando `USE_IN_MEMORY_CHANNEL_LAYER=false`;
- `CELERY_BROKER_URL`;
- `CELERY_RESULT_BACKEND`.

```bash
REDIS_URL=redis://redis:6379/0
```

### 14.4 Backend — Docker

`backend/Dockerfile`:

```bash
python manage.py collectstatic --noinput && python manage.py migrate && daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

`backend/Dockerfile.worker`:

```bash
python manage.py migrate && celery -A config worker -B -l info
```

### 14.5 Frontend

`frontend/Dockerfile`:

```bash
npm ci
npm run build
node .output/server/index.mjs
```

Variáveis públicas:

```bash
NUXT_PUBLIC_API_BASE=https://seu-dominio/api
NUXT_PUBLIC_WS_BASE=wss://seu-dominio/ws
NUXT_PUBLIC_TURNSTILE_SITE_KEY=...
```

### 14.6 Checklist de deploy

- [ ] `backend/.env.prod` configurado.
- [ ] `DJANGO_SECRET_KEY` seguro.
- [ ] `DJANGO_DEBUG=false`.
- [ ] `DJANGO_ALLOWED_HOSTS` e `DJANGO_CSRF_TRUSTED_ORIGINS` corretos.
- [ ] `CORS_ALLOWED_ORIGINS` inclui origem do frontend.
- [ ] `REDIS_URL` acessível.
- [ ] `USE_IN_MEMORY_CHANNEL_LAYER=false` em produção multi-processo.
- [ ] Certificados TLS montados em `/etc/letsencrypt` se usar o Nginx atual.
- [ ] `docker compose -f docker-compose.prod.yml up -d --build`.
- [ ] Testar cadastro com Turnstile, login, criação de retro, convite, WebSocket e timer.

### 14.7 Criação do superusuário (pós-deploy)

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

### 14.8 Variáveis de ambiente — resumo completo

| Variável | Onde | Descrição |
|---|---|---|
| `DJANGO_SECRET_KEY` | Backend | Chave secreta Django |
| `DJANGO_DEBUG` | Backend | `false` em produção |
| `DJANGO_ALLOWED_HOSTS` | Backend | Hosts permitidos |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Backend | Origins confiáveis |
| `DB_ENGINE` | Backend | `postgres` para PostgreSQL; default SQLite |
| `POSTGRES_DB` | Backend/db | Nome do banco |
| `POSTGRES_USER` | Backend/db | Usuário |
| `POSTGRES_PASSWORD` | Backend/db | Senha |
| `POSTGRES_HOST` | Backend | Host |
| `POSTGRES_PORT` | Backend | Porta |
| `REDIS_URL` | Backend/worker | Redis para Channels/Celery |
| `CORS_ALLOWED_ORIGINS` | Backend | Origins do frontend |
| `USE_IN_MEMORY_CHANNEL_LAYER` | Backend | `false` para Redis Channel Layer |
| `ALLOWED_EMAIL_DOMAINS` | Backend | Restrição opcional de cadastro |
| `CLOUDFLARE_TURNSTILE_SECRET_KEY` | Backend | Validação Turnstile |
| `NUXT_PUBLIC_API_BASE` | Frontend | URL base API |
| `NUXT_PUBLIC_WS_BASE` | Frontend | URL base WS |
| `NUXT_PUBLIC_TURNSTILE_SITE_KEY` | Frontend | Site key Turnstile |

---

## 15. Decisões Registradas e Trade-offs

### 15.1 JWT (simplejwt) como auth primária em vez de sessões

Compatível com SPA e WebSocket por token. O refresh token fica no localStorage junto com access token.

### 15.2 Usuário guest como `User` com `is_guest=True`

Simplifica permissões e relações com cards/votos/action items. Trade-off: guests acumulam no banco.

### 15.3 `allow_self_vote` configurável

Configurado na criação e aplicado no backend durante votação. Não há endpoint de alteração posterior.

### 15.4 `focus_card` persistido no banco

Permite sobreviver a reconexões e aparecer no detalhe da retro.

### 15.5 `phase_durations` como JSONField

Permite configurar timers por fase sem campos dedicados.

### 15.6 Worker Celery + Beat no mesmo processo

Simplifica operação, mas não é desenho altamente disponível.

### 15.7 Nuxt 3.17.5 fixado

Versão fixa no `package.json`.

### 15.8 `session.snapshot` parcial

Reduz carga inicial via WS, mas obriga múltiplas chamadas REST.

### 15.9 Infraestrutura Docker/Nginx

O repositório contém produção por Docker Compose com Nginx, TLS, frontend Node, backend Daphne, worker Celery, PostgreSQL e Redis.

### 15.10 `team_key` como SlugField

Agrupa retrospectivas por time sem entidade `Team`.

### 15.11 `description` no modelo Retrospective

Campo persistido e retornado na API.

### 15.12 `external_tracker_url` no ActionItem

Armazena URL externa, sem integração automatizada.

---

## Divergências encontradas

- O PRD anterior dizia que `state_machine.py` garantia transições lineares; o consumer WebSocket não usa essa validação.
- A ordem de fases antiga colocava `presentation` antes de `check`; o frontend atual avança para `check` antes de `presentation`.
- `skip_check_phase` estava descrito como sem efeito; ele tem efeito no frontend, pulando `check` ao sair do lobby.
- Action items marcados como parcialmente pendentes já estão implementados conforme regra atual: criação em `discussion` pelo facilitador; edição/exclusão em `discussion/actions` pelo facilitador; criação bloqueada em `actions`.
- `votes-config` estava documentado como `GET/PATCH`; o código implementa `PUT` e só altera `max_votes_per_user`.
- Agrupamento estava documentado com `group_card_id`; o código usa `group_parent_id`.
- Action item estava documentado com `assignee` como FK/User no payload; a API espera `assignee_id` como id de `Participant`.
- O auto-bloqueio imediato do convite após entrada tardia não existe; a janela fica aberta até expirar.
- `/join` não implementa PIN real; apenas navega para `/retro/{code}`.
- A presença REST não retorna online/offline; o frontend estima via eventos WebSocket.
- OAuth estava documentado como não exposto; existe botão Google na UI, mas o provider Google não está configurado no backend do repositório.

---

*RetroApp 4L PRD v10.0 — Fonte da verdade: código-fonte atual*
