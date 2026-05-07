# RetroApp 4L — Documento de Requisitos do Produto (PRD)

**Versão:** 8.0 — MVP (Open Source / Estado Real da Implementação)
**Data:** Maio 2026
**Status:** Versão de reconciliação — código é a fonte da verdade
**Audiência:** Agente de IA (executor principal), Tech Lead (revisão / infra / deploy)
**Licença:** MIT

> **Changelog v8.0:**
>
> - PRD reconciliado com o código-fonte real (código é a fonte da verdade)
> - Modelo de dados atualizado: campos extras implementados documentados (`is_guest`, `public_email`, `allow_self_vote`, `focus_card`, `invite_temporarily_open_until`, `phase_durations`, `description`, `external_tracker_url`)
> - Status de ActionItem corrigido: `not_started` (não `pending`) é o valor real implementado
> - Sistema de usuário convidado (guest) documentado como feature implementada
> - Auth documentada como JWT via `djangorestframework-simplejwt` (primário); `django-allauth` instalado mas não exposto no frontend como fluxo principal
> - Python 3.11 (não 3.12) documentado como versão de runtime
> - Worker Celery + Beat rodando no mesmo processo documentado
> - `session.snapshot` documentado como parcial (cards/votes/milestones/participants enviados vazios; frontend carrega via REST)
> - Índice de apresentação de marcos documentado como em memória (limitação conhecida)
> - UI do frontend tem textos em português brasileiro (não inglês) — documentado como estado atual
> - Icons mistos: Heroicons (@heroicons/vue) e Material Design Icons (prefixo `mdi`) — documentado
> - Nuxt 3.17.5 fixado (incompatibilidade conhecida com 3.21.x no Windows)
> - Seção de deploy adicionada com todos os passos necessários para produção

---

## 1. Visão Geral

O RetroApp 4L é uma plataforma web open source para conduzir retrospectivas de sprint estruturadas na metodologia dos 4 Ls (Liked, Loathed, Longed For, Learned). O produto combina colaboração em tempo real, cronômetro sincronizado e rastreabilidade de itens de ação — fechando o ciclo entre o que é decidido na retro e o que é executado na sprint seguinte.

O projeto é projetado para ser auto-hospedado, gratuito para rodar em escala de MVP, e fácil de estender por agentes de IA ou contribuidores humanos.

### 1.1 Problema

- Retrospectivas conduzidas em ferramentas genéricas (Miro, EasyRetro, Google Jamboard) não estão integradas ao fluxo de trabalho do time.
- Itens de ação decididos nas retros raramente se tornam tarefas rastreáveis.
- Não há mecanismo para verificar, na retro seguinte, se as ações da sprint anterior foram cumpridas.
- Não há histórico centralizado de retrospectivas para acompanhar a evolução do time ciclo a ciclo.

### 1.2 Objetivos do MVP

- Conduzir retrospectivas 4L com colaboração em tempo real (board compartilhado + cronômetro sincronizado).
- Autenticar usuários via contas locais (e-mail + senha) como método primário; OAuth via allauth como opcional futuro.
- Permitir ao facilitador convidar membros via link privado; participantes externos entram como usuários **guest** autenticados por JWT.
- Verificar ações da sprint anterior antes de iniciar a reflexão.
- Registrar itens de ação com responsável e prazo.
- Salvar automaticamente todas as retrospectivas para consulta futura.
- Operar com custo zero de infraestrutura utilizando tiers gratuitos de plataformas cloud.

### 1.3 Critérios de Sucesso do MVP

| Indicador | Meta |
|---|---|
| Adoção | ≥ 80% das retrospectivas do time conduzidas no RetroApp 4L |
| Rastreabilidade | ≥ 70% dos itens de ação registrados com responsável e prazo preenchidos |
| Reabertura | ≥ 50% das sessões incluem a verificação de ações da sprint anterior |
| Estabilidade | Zero incidentes de dessincronização de board em produção |
| Satisfação | NPS interno ≥ 7 após pesquisa com facilitadores (mínimo 5 respostas) |
| Custo | Custo total de infraestrutura = R$ 0,00 durante o período MVP |

### 1.4 Fora do Escopo do MVP

- Integrações com rastreadores externos de tarefas (Jira, Linear, Asana, GitHub Issues). *(campo `external_tracker_url` em ActionItem existe como stub para integração futura)*
- Exportação em PDF, CSV ou DOCX.
- Mascaramento de cards durante a fase de escrita.
- Relatórios e analytics de tendências entre sprints.
- Drag-and-drop para agrupamento de cards (fase 2).
- SSO / SAML para deployments enterprise.
- OAuth social (Google, GitHub) exposto no frontend — allauth está instalado, mas a interface de login só expõe e-mail/senha local.
- CI/CD automatizado (GitHub Actions) — não implementado ainda.

---

## 2. Premissas de Desenvolvimento

### 2.1 Modelo de execução

- **O desenvolvedor é um agente de IA (ex: Claude Code CLI)**, rodando autonomamente por sessão.
- **O Tech Lead (humano)** é responsável por: revisão de código, decisões de infra, configuração de ambiente, deploy, escrita e validação do documento de handoff ao final de cada sprint.
- O agente de IA **não tem memória entre sessões**. Todo contexto necessário deve estar no documento de handoff. Se não está no handoff, não existe para a próxima sessão.

### 2.2 Consequências arquiteturais

- **Convenção sobre configuração:** código segue padrões idiomáticos do Django e do Tailwind CSS.
- **Estrutura de arquivos previsível:** definida na Sprint 1 e nunca alterada sem atualização explícita no handoff.
- **Testes como documentação viva:** cada sprint produz testes que descrevem o comportamento implementado.
- **Sem "magia" implícita:** evitar padrões que dependem de estado global ou comportamento implícito difícil de rastrear.

### 2.3 Responsabilidades por papel

| Responsabilidade | Agente de IA | Tech Lead |
|---|---|---|
| Implementar features das sprints | ✅ | — |
| Escrever testes unitários e de integração | ✅ | Revisa |
| Criar e atualizar migrations | ✅ | Revisa e executa |
| Configurar ambiente local (docker-compose) | ✅ | Valida |
| Provisionar infra (Fly.io, Neon, Upstash, Vercel) | — | ✅ |
| Configurar CI/CD (GitHub Actions) | Gera o YAML | ✅ executa |
| Revisar PRs e validar comportamento | — | ✅ |
| Escrever documento de handoff da sprint | Gera rascunho | ✅ valida e assina |
| Decisões de produto não previstas no PRD | — | ✅ |

Aqui está o trecho ajustado para a seção 2:

---

### 2.4 Premissa de Perfil do Facilitador

O RetroApp 4L pressupõe que o facilitador é um membro sênior do próprio time — tipicamente o Tech Lead ou Scrum Master — com autoridade técnica e contexto sobre as decisões tomadas durante a sprint.

Essa premissa é deliberada e afeta diretamente várias decisões de design do produto:

- **Marcos:** criados pelo facilitador antes da sessão, pois ele tem visibilidade do que merece reconhecimento ou atenção no ciclo encerrado.
- **Controle de fases e cronômetro:** exclusivo do facilitador, pois ele é quem lê o estado emocional e o ritmo do time.
- **Action items na fase `discussion`:** criados pelo facilitador no papel de secretário, anotando em tempo real as decisões que emergem do debate coletivo.
- **Edição de action items na fase `actions`:** restrita ao facilitador, pois os itens registrados refletem decisões já negociadas durante o debate — o facilitador tem contexto para validar responsável e prazo.

**Consequência:** o RetroApp foi otimizado para contextos onde o facilitador é um membro ativo do time, com conhecimento prévio do ciclo e das capacidades individuais dos participantes.

---

## 3. Perfis de Usuário

### Facilitador

Membro do time responsável por criar e conduzir a sessão. Prepara os marcos antes da retro, controla o avanço entre fases, configura o cronômetro (com pausa e retomada), gerencia entrada de participantes e é o único com permissão de agrupar cards, definir o card em foco durante o debate e encerrar a sessão. Não pode ser usuário guest.

**Necessidades principais:** controle total do fluxo, visibilidade do estado de todos os participantes, ferramentas ágeis para agrupamento, capacidade de intervir em qualquer fase sem travar a sessão.

### Participante

Membro do time convidado via link. Pode criar, editar e excluir seus próprios cards, votar (apenas nas colunas designadas), participar do debate e registrar itens de ação. Não pode avançar fases, agrupar cards, gerenciar entrada de participantes ou encerrar a sessão.

**Necessidades principais:** interface rápida para adicionar cards, clareza sobre em qual fase está e o que se espera dela naquele momento, visibilidade dos marcos e do card em foco durante o debate.

### Usuário Guest

Participante que entrou via link de convite **sem** conta cadastrada previamente. Recebe JWT próprio após informar nome (e opcionalmente e-mail público) na tela `/retro/invite/:token`. É armazenado como `User` com `is_guest=true` e senha inutilizável. Pode participar de todas as fases como participante comum, mas não pode criar retrospectivas, acessar dashboard ou usar a rota `/retro/create`. Identidade guest é persistida no localStorage do frontend via `guestStore`.

---

## 4. User Stories

### Facilitador

**US-01 — Criar sessão**
> Como facilitador, quero criar uma sessão de retrospectiva informando o nome da sprint e o identificador do time.

**Critérios de aceite implementados:**

- Campos obrigatórios: `title`, `team_key`.
- Campos opcionais: `sprint_name`, `description`, `max_votes_per_user`, `allow_self_vote`, `skip_check_phase`, `phase_durations`.
- Sessão inicia no estado `setup`.
- Facilitador é adicionado automaticamente como participante.
- `invite_token` UUID gerado automaticamente na criação.
- Guest não pode criar retrospectivas (retorna 403).

---

**US-02 — Convidar participantes**
> Como facilitador, quero compartilhar um link de convite privado.

**Critérios de aceite implementados:**

- Link: `{origin}/retro/invite/{invite_token}`.
- Endpoint público `GET /api/invites/{token}/` retorna metadados da sessão e status do convite.
- Endpoint público `POST /api/invites/{token}/join/` cria ou reaproveita usuário guest e retorna `access`/`refresh` JWT.
- Status do convite: `active` (em lobby), `temporarily_open` (facilitador reabriu), `blocked` (sessão avançou).
- Participante já cadastrado que acessa o link reutiliza conta e tokens são atualizados se nome/email mudaram.

---

**US-02b — Gerenciar entrada de participantes após o início**
> Como facilitador, quero liberar temporariamente o acesso a participantes tardios.

**Critérios de aceite implementados:**

- Endpoint `POST /api/retrospectives/{id}/reopen-entry/` define `invite_temporarily_open_until = now + 2 minutos`.
- Endpoint `GET /api/retrospectives/{id}/invite-status/` retorna status atual do convite.
- Registra `link_reopened` no `AccessLog`.
- Evento WebSocket `invite.status_updated` emitido para todos os participantes.
- Auto-bloqueio: ao entrar novo participante com convite `temporarily_open`, o `invite_temporarily_open_until` é zerado e `link_auto_blocked` é registrado no `AccessLog`.

---

**US-03 — Controlar fases**
> Como facilitador, quero avançar as fases manualmente.

**Critérios de aceite implementados:**

- Evento WebSocket `phase.advance` enviado pelo facilitador, com `phase` sendo a fase destino.
- Backend valida transição via `state_machine.py` (transições lineares, sem pulo).
- Ao avançar, todos recebem `phase.changed` com `{phase, timer_duration_seconds}`.
- Timer inicia automaticamente ao entrar em fase cronometrada, usando `phase_durations` se configurado.
- Facilitador pode pausar (`timer.pause`) e retomar (`timer.resume`) cronômetro.
- Estado de pausa/retomada refletido para todos via `timer.paused`/`timer.resumed`.
- ⚠️ **Limitação atual:** `skip_check_phase` existe no modelo mas a máquina de estados não implementa pulo automático da fase check.

---

**US-04 — Configurar dot voting**
> Como facilitador, quero definir o número de votos por participante.

**Critérios de aceite implementados:**

- `max_votes_per_user` configurável na criação da sessão (padrão: 3).
- `allow_self_vote` booleano configurável (padrão: `false` — autor não pode votar no próprio card).
- Endpoint `PATCH /api/retrospectives/{id}/votes-config/` permite atualizar estas configurações.
- Contador de votos restantes em `Participant.votes_remaining`.

---

**US-05 — Encerrar sessão**
> Como facilitador, quero encerrar a sessão.

**Critérios de aceite implementados:**

- Endpoint `POST /api/retrospectives/{id}/close/` — exclusivo do facilitador, apenas na fase `actions`.
- Sessão muda para `closed`; `closed_at` preenchido.
- Registra `AccessLog.closed`.
- Sessão aparece no endpoint `GET /api/retrospectives/history/`.

---

**US-07a — Preparar marcos (Facilitador)**
> Como facilitador, quero registrar marcos da sprint antes de iniciar.

**Critérios de aceite implementados:**

- CRUD via `GET/POST /api/retrospectives/{id}/milestones/` e `GET/PUT/PATCH/DELETE /api/retrospectives/{id}/milestones/{milestone_id}/`.
- Criação/edição/exclusão restrita ao facilitador e à fase `setup`.
- Categorias: `achievement`, `challenge`, `change`, `recognition`, `other`.
- Campo `description` máx. 500 caracteres.

---

**US-07c — Apresentar marcos**
> Como facilitador, quero apresentar os marcos no início da sessão.

**Critérios de aceite implementados:**

- Fase `presentation` com navegação de marcos via WebSocket.
- Eventos do cliente: `milestone.presentation.start`, `milestone.presentation.next`, `milestone.presentation.prev`, `milestone.presentation.end`.
- Servidor emite `milestone.presentation` com `{index, total, milestone_id}`.
- Se não houver marcos: `milestone.presentation.start` avança automaticamente para `check`.
- ⚠️ **Limitação atual:** índice de apresentação armazenado em memória no processo (`RetrospectiveConsumer.presentation_indices`). Perde estado em restart do worker. Aceitável para MVP.

---

**US-09 — Agrupar cards (Facilitador)**
> Como facilitador, quero agrupar cards similares.

**Critérios de aceite implementados:**

- `POST /api/retrospectives/{id}/cards/group/` com `{card_ids: [uuid, ...], group_card_id: uuid}`.
- `POST /api/retrospectives/{id}/cards/{card_id}/ungroup/`.
- Cards só agrupáveis com outros da mesma coluna.
- Broadcast `card.grouped` / `card.ungrouped` para todos em tempo real.
- Apenas o facilitador pode agrupar (verificação server-side).

---

**US-12 — Conduzir debate focado (Facilitador)**
> Como facilitador, quero conduzir uma discussão estruturada sobre os cards mais votados.

**Critérios de aceite implementados:**

- `POST /api/retrospectives/{id}/focus-card/` com `{card_id: uuid}` — persiste `focus_card` no banco.
- `POST /api/retrospectives/{id}/next-card/` avança para o próximo card na fila (ordenada por votos decrescente).
- Broadcast WebSocket com payload do card em foco.
- `focus_card_id` presente em `RetrospectiveDetail`.

---

### Participante

**US-06 — Verificar ações anteriores**
> Como participante, quero ver as ações da retro anterior.

**Critérios de aceite implementados:**

- `GET /api/retrospectives/{id}/previous-actions/` retorna action items da última retro `closed` do mesmo `team_key`.
- `PATCH /api/retrospectives/{id}/previous-actions/{action_id}/status/` atualiza `status` (`not_started`, `in_progress`, `done`).
- Broadcast WebSocket `action.check_updated` ao atualizar status.

---

**US-08 — Adicionar card ao board**
> Como participante, quero adicionar um card em qualquer coluna do board 4L.

**Critérios de aceite implementados:**

- `POST /api/retrospectives/{id}/cards/` com `{column, content}`.
- `column` choices: `loved`, `loathed`, `longed`, `learned`. *(nota: internamente "loved", não "liked")*
- Limite: 500 caracteres.
- Broadcast `card.created` para todos via WebSocket.
- Somente autor pode editar/excluir. Endpoint `PATCH/DELETE /api/retrospectives/{id}/cards/{card_id}/`.

---

**US-10 — Votar em cards prioritários**
> Como participante, quero distribuir meus votos.

**Critérios de aceite implementados:**

- `POST /api/retrospectives/{id}/cards/{card_id}/vote/` — registra voto; `DELETE` revoga.
- Restrição de colunas votáveis (`loathed` e `longed`) verificada server-side.
- Máximo 1 voto por card por participante (constraint no banco).
- `allow_self_vote=false`: autor não pode votar no próprio card.
- `votes_remaining` decrementado em `Participant` a cada voto; incrementado ao revogar.
- Broadcast `vote.cast` / `vote.revoked` com `{card_id, voter_id, votes_remaining}`.

---

**US-11 — Registrar item de ação**
> Como participante, quero registrar um item de ação.

**Critérios de aceite implementados:**

- `POST /api/retrospectives/{id}/action-items/` com `{description, assignee, due_date, card}`.
- `assignee` obrigatório (FK para User).
- `due_date` opcional.
- `card` opcional (FK para Card).
- `external_tracker_url` opcional (URL; reservado para integração futura).
- `status` inicial: `not_started`.

---

## 5. Fluxo da Sessão de Retrospectiva

| Fase | Duração padrão | Quem pode editar | Descrição |
|---|---|---|---|
| Preparação (`setup`) | — | Facilitador | Cria sessão, define `team_key`, registra marcos. |
| Lobby (`lobby`) | — | Facilitador (controle) | Convite ativo. Participantes chegam via link. |
| Apresentação (`presentation`) | 10 min | Facilitador (navegação) / Todos (visualizam) | Facilitador navega pelos marcos. Se não houver, avança automaticamente para `check`. |
| Check de ações (`check`) | 5 min | Todos | Revisão dos action items da última retro do mesmo `team_key`. |
| Board 4L (`board`) | 15 min | Todos | Reflexão nas 4 colunas: loved, loathed, longed, learned. |
| Agrupamento (`grouping`) | 5 min | **Facilitador** | Agrupa cards duplicados da mesma coluna. |
| Votação (`voting`) | 3 min | Todos | Dot voting em `loathed` e `longed`. |
| Debate (`discussion`) | 15 min | Todos (leitura) / Facilitador (controle de foco) | Cards ordenados por votos; facilitador define card em foco. |
| Ações (`actions`) | 10 min | Todos | Registro de action items com responsável e prazo. |
| Encerrado (`closed`) | — | Facilitador | Sessão no histórico. |

**Transições válidas (implementadas em `state_machine.py`):**
`setup → lobby → presentation → check → board → grouping → voting → discussion → actions → closed`

**Durações padrão por fase (configuráveis via `phase_durations` no modelo):**

| Fase | Duração padrão |
|---|---|
| `presentation` | 600s (10 min) |
| `check` | 300s (5 min) |
| `board` | 900s (15 min) |
| `grouping` | 300s (5 min) |
| `voting` | 180s (3 min) |
| `discussion` | 900s (15 min) |
| `actions` | 600s (10 min) |

**Fases não cronometradas:** `setup`, `lobby`, `closed`.

---

## 6. Stack Tecnológica

### 6.1 Stack de desenvolvimento

| Camada | Tecnologia | Versão real | Observação |
|---|---|---|---|
| **Backend** | Python + Django | 3.11 / 5.2.13 | Dockerfile usa python:3.11-slim |
| **API REST** | Django REST Framework | 3.16.1 | |
| **WebSocket** | Django Channels + ASGI | 4.2.2 | |
| **Servidor ASGI** | Daphne | 4.2.1 | |
| **Tarefas assíncronas** | Celery | 5.5.3 | Worker + Beat no mesmo processo (`-B`) |
| **Channel Layer / Broker** | Redis via channels_redis | 4.2.1 | |
| **Banco de dados** | PostgreSQL | 16 (docker) | Fallback SQLite em dev sem `DB_ENGINE=postgres` |
| **Auth JWT** | djangorestframework-simplejwt | 5.5.1 | Auth principal; access 8h, refresh 7d |
| **Auth social (opcional)** | django-allauth | 65.16.1 | Instalado; nenhum provider OAuth configurado ainda |
| **Frontend** | Nuxt 3 (Vue 3) | **3.17.5** (fixado) | SSR desabilitado (SPA); 3.21.x incompatível no Windows |
| **CSS** | Tailwind CSS via @nuxtjs/tailwindcss | 6.14.0 | |
| **Ícones** | @heroicons/vue + Material Design Icons (`mdi`) | 2.2.0 | Misto: Heroicons no código novo, `mdi` em alguns templates |
| **Containerização local** | Docker + docker-compose | — | 5 serviços: backend, worker, db, redis, frontend |

### 6.2 Infraestrutura (MVP Zero-Cost — alvo de deploy)

| Serviço | Plataforma | Tier gratuito | O que hospeda |
|---|---|---|---|
| **Backend Django + Daphne** | [Fly.io](https://fly.io) | Até 3 VMs compartilhadas (256 MB RAM cada) | Aplicação Django com ASGI (Daphne) |
| **Worker Celery + Beat** | Fly.io (processo separado ou segunda VM) | Mesmo tier gratuito | Processamento assíncrono do cronômetro |
| **PostgreSQL** | [Neon](https://neon.tech) | 0.5 GB armazenamento | Banco de dados principal |
| **Redis** | [Upstash](https://upstash.com) | Até 256 MB, 1000 conexões | Channel Layer + Celery broker |
| **Frontend SPA** | [Vercel](https://vercel.com) | 100 GB banda, builds ilimitados | Nuxt 3 SPA |

### 6.3 Arquitetura de deployment

```
[Frontend Nuxt SPA] (Vercel)
        |  HTTP REST + WSS
[Fly.io App (Django + Daphne)] --> [Neon PostgreSQL]
        |                           [Upstash Redis]
[Fly.io Worker (Celery + Celery Beat)]

Dev local: docker-compose (backend, worker, db, redis, frontend)
```

### 6.4 Estrutura de repositório (monorepo)

```
retroapp4l/
├── backend/               # Django — API REST + WebSocket
│   ├── config/            # settings (base/local/production), urls, asgi, wsgi, celery
│   ├── apps/
│   │   ├── users/         # Modelo User (local + guest), auth JWT
│   │   ├── retrospectives/# Retrospective, Participant, Milestone, AccessLog
│   │   ├── cards/         # Card, CardVote
│   │   ├── actions/       # ActionItem
│   │   └── realtime/      # Consumer WebSocket, state_machine, tasks Celery
│   ├── tasks/             # Celery tasks (timer_sync_task)
│   └── tests/             # Testes (espelha apps/)
├── frontend/              # Nuxt 3 SPA
│   ├── pages/             # index, auth/login, auth/register, join, retro/[id], retro/invite/[token]
│   ├── components/        # board/, retro/phases/, forms/, participants/, layout/
│   ├── composables/       # useWebSocket, useAuth, usePhase, useTimer, useApiClient
│   ├── stores/            # retro, auth, guest, participants, timer, toast
│   └── utils/             # types.ts, sound.ts, validation.ts
├── docs/                  # PRD
└── docker-compose.yml
```

---

## 7. Design System

> **Instrução para o agente de IA:** esta seção é a fonte de verdade para todas as decisões visuais do frontend. Nenhuma cor, fonte, espaçamento ou componente deve ser inventado. Se não está aqui, registre no handoff para validação do Tech Lead antes de prosseguir.

### 7.1 Visão geral

O RetroApp 4L usa **Tailwind CSS** como único sistema de estilos. Todas as decisões de design são expressas via classes utilitárias do Tailwind e uma configuração de tema customizada em `tailwind.config.ts`.

**Princípios norteadores:**

- Clareza acima de decoração. Todo elemento visual deve servir a um propósito funcional.
- Consistência via tokens. Nunca usar valores hex arbitrários — sempre usar tokens do tema Tailwind.
- Responsivo por padrão. Todos os layouts devem funcionar em desktop 1280px+ (primário) e tablet 768px (secundário).

**⚠️ Nota sobre idioma da UI:** o frontend atual usa **português brasileiro** em labels e mensagens (ex.: "Gostei", "Não gostei", "Senti falta", "Aprendi", "Check de ações anteriores"). Esta é a decisão de produto atual. O PRD v7 especificava inglês para produto open source global — a decisão de migrar para inglês fica a critério do Tech Lead.

### 7.2 Tipografia

- **Fonte:** Inter (Google Fonts). Pesos: 400, 500, 600, 700.
- **Import:** `@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap')`
- **Headings:** sempre `font-semibold` (600).

### 7.3 Paleta de cores

Definida em `tailwind.config.ts` sob `theme.extend.colors`.

```typescript
colors: {
  brand: {
    50:  '#eff6ff',
    100: '#dbeafe',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
  },
  success: {
    50:  '#f0fdf4',
    500: '#22c55e',
    600: '#16a34a',
  },
  warning: {
    50:  '#fff7ed',
    500: '#f97316',
    600: '#ea580c',
  },
  danger: {
    50:  '#fef2f2',
    500: '#ef4444',
    600: '#dc2626',
  },
}
```

**Mapeamento de colunas do board:**

| Coluna | Valor no banco | Label atual (PT-BR) | Cor |
|---|---|---|---|
| Liked/Loved | `loved` | "Gostei" | `success-600` |
| Loathed | `loathed` | "Não gostei" | `warning-500` |
| Longed For | `longed` | "Senti falta" | `brand-500` |
| Learned | `learned` | "Aprendi" | `slate-600` |

### 7.4 Ícones

O projeto usa **duas** bibliotecas de ícones atualmente:

- **@heroicons/vue** (`npm install @heroicons/vue`) — usado nos componentes novos (DiscussionView, FocusCard, etc.)
- **Material Design Icons** (prefixo `mdi` via classe CSS) — usado em alguns componentes mais antigos (LobbyView, SetupView, etc.)

A migração completa para Heroicons é recomendada mas ainda não realizada.

### 7.5 Componentes UI Implementados

Os seguintes componentes estão implementados em `frontend/components/`:

| Componente | Arquivo | Descrição |
|---|---|---|
| `RetroCard` | `retro/RetroCard.vue` | Card do board com votes, edit, delete |
| `MilestoneCard` | `retro/MilestoneCard.vue` | Card de marco com categoria |
| `MilestoneBar` | `retro/MilestoneBar.vue` | Barra de marcos colapsável |
| `PhaseChip` | `retro/PhaseChip.vue` | Chip da fase atual |
| `TimerDisplay` | `retro/TimerDisplay.vue` | Cronômetro com pausa/retomada |
| `VoteBadge` | `retro/VoteBadge.vue` | Badge de contagem de votos |
| `VoteControls` | `retro/VoteControls.vue` | Controles de votação |
| `FocusCard` | `board/FocusCard.vue` | Card em foco no debate |
| `ActionEditor` | `retro/ActionEditor.vue` | Editor de action items |
| `ParticipantPanel` | `participants/ParticipantPanel.vue` | Painel de participantes |
| `BoardGrid` | `retro/board/BoardGrid.vue` | Grid das 4 colunas |
| `ColumnBox` | `retro/board/ColumnBox.vue` | Caixa de coluna individual |
| `ColumnHeader` | `board/ColumnHeader.vue` | Cabeçalho de coluna |
| `Header` | `Header.vue` | Header global da aplicação |
| `HistoryTable` | `HistoryTable.vue` | Tabela de histórico de retros |
| `ActiveSessionCard` | `ActiveSessionCard.vue` | Card de sessão ativa no dashboard |

**Telas de fase implementadas em `components/retro/phases/`:**

| Fase | Componente |
|---|---|
| `setup` | `SetupView.vue` |
| `lobby` | `LobbyView.vue` |
| `presentation` | `MilestonesView.vue` |
| `check` | `CheckView.vue` |
| `board` | `BoardView.vue` |
| `grouping` | `GroupingView.vue` |
| `voting` | `VotingView.vue` |
| `discussion` | `DiscussionView.vue` |
| `actions` | `ActionsView.vue` |
| `closed` | `ClosedView.vue` |

---

## 8. Modelo de Dados

### users_user *(app: users)*

| Campo | Tipo Django | Descrição |
|---|---|---|
| id | UUIDField (PK) | |
| name | CharField(255) | Nome completo |
| email | EmailField (unique) | E-mail principal (inutilizável para guests) |
| public_email | EmailField (blank) | E-mail visível para usuários guest |
| password | AbstractUser default | Senha hasheada; `set_unusable_password()` para guests |
| oauth_provider | CharField(50, blank) | `google` \| `github` \| vazio |
| oauth_id | CharField(255, blank) | ID do usuário no provedor OAuth |
| avatar_url | URLField (blank) | URL do avatar |
| **is_guest** | BooleanField (default=False) | `True` para usuários criados via convite público |
| is_active | BooleanField | Padrão Django |
| is_staff | BooleanField | Padrão Django |
| created_at | DateTimeField(auto_now_add) | |

> **Propriedade `display_email`:** retorna `public_email` se `is_guest=True`, caso contrário retorna `email`. Usada no serializer de participante.

### retrospectives_retrospective *(app: retrospectives)*

| Campo | Tipo Django | Descrição |
|---|---|---|
| id | UUIDField (PK) | |
| title | CharField(255) | Título da retrospectiva |
| sprint_name | CharField(255, nullable) | Nome da sprint |
| **description** | TextField (blank) | Descrição livre (opcional) |
| team_key | SlugField(100) | Identificador do time (slug). Obrigatório. |
| facilitator | ForeignKey(User) | |
| status | CharField(choices) | `setup\|lobby\|presentation\|check\|board\|grouping\|voting\|discussion\|actions\|closed` |
| invite_token | UUIDField (unique, nullable) | Token do link de convite. Gerado na criação. |
| invite_revoked_at | DateTimeField (nullable) | |
| **invite_temporarily_open_until** | DateTimeField (nullable) | Janela temporária de 2 min para nova entrada pós-lobby |
| max_votes_per_user | PositiveSmallIntegerField (default=3) | |
| **allow_self_vote** | BooleanField (default=False) | Permite autor votar no próprio card |
| skip_check_phase | BooleanField (default=False) | Flag de configuração (pulo automático não implementado ainda) |
| **focus_card** | ForeignKey(Card, nullable, SET_NULL) | Card em foco no debate — persistido no banco |
| timer_started_at | DateTimeField (nullable) | |
| timer_paused_at | DateTimeField (nullable) | Se preenchido, cronômetro está pausado |
| timer_duration_seconds | PositiveIntegerField (nullable) | |
| **phase_durations** | JSONField (default=dict) | Duração por fase em segundos. Ex: `{"board": 900, "voting": 180}` |
| created_at | DateTimeField(auto_now_add) | |
| closed_at | DateTimeField (nullable) | |

### retrospectives_milestone *(app: retrospectives)*

| Campo | Tipo Django | Descrição |
|---|---|---|
| id | UUIDField (PK) | |
| retrospective | ForeignKey(Retrospective) | |
| author | ForeignKey(User) | Sempre o facilitador |
| category | CharField(choices) | `achievement\|challenge\|change\|recognition\|other` |
| description | CharField(500) | Máx. 500 caracteres |
| created_at | DateTimeField(auto_now_add) | |

### retrospectives_participant *(app: retrospectives)*

| Campo | Tipo Django | Descrição |
|---|---|---|
| id | UUIDField (PK) | |
| retrospective | ForeignKey(Retrospective) | |
| user | ForeignKey(User) | |
| votes_remaining | IntegerField (default=3) | Decrementado a cada voto |
| joined_at | DateTimeField(auto_now_add) | |

`UniqueConstraint: (retrospective, user)`

### retrospectives_accesslog *(app: retrospectives)*

| Campo | Tipo Django | Descrição |
|---|---|---|
| id | UUIDField (PK) | |
| retrospective | ForeignKey(Retrospective) | |
| action | CharField(choices) | `opened\|closed\|participant_joined\|link_reopened\|link_auto_blocked` |
| triggered_by | ForeignKey(User, nullable) | |
| participant | ForeignKey(User, nullable) | Preenchido quando `participant_joined` |
| timestamp | DateTimeField(auto_now_add) | |

### cards_card *(app: cards)*

| Campo | Tipo Django | Descrição |
|---|---|---|
| id | UUIDField (PK) | |
| retrospective | ForeignKey(Retrospective) | |
| author | ForeignKey(User) | |
| column | CharField(choices) | `loved\|loathed\|longed\|learned` |
| content | CharField(500) | Máx. 500 caracteres |
| group | ForeignKey('self', nullable) | Card pai do grupo |
| position | PositiveIntegerField (default=0) | |
| created_at | DateTimeField(auto_now_add) | |

### cards_cardvote *(app: cards)*

| Campo | Tipo Django | Descrição |
|---|---|---|
| id | UUIDField (PK) | |
| card | ForeignKey(Card) | |
| voter | ForeignKey(User) | |
| created_at | DateTimeField(auto_now_add) | |

`UniqueConstraint: (card, voter)`

### actions_actionitem *(app: actions)*

| Campo | Tipo Django | Descrição |
|---|---|---|
| id | UUIDField (PK) | |
| retrospective | ForeignKey(Retrospective) | |
| card | ForeignKey(Card, nullable) | Card de origem |
| description | TextField | |
| assignee | ForeignKey(User) | Responsável |
| due_date | DateField (nullable) | |
| **external_tracker_url** | URLField (blank) | URL em rastreador externo (stub para integração futura) |
| status | CharField(choices) | **`not_started`**`\|in_progress\|done` *(nota: não `pending`)* |
| created_at | DateTimeField(auto_now_add) | |

---

## 9. Eventos WebSocket

Canal: `retro_{retrospective_id}` (Django Channels Group)

Autenticação: `apps/realtime/middleware.py` extrai JWT do query param `?token=` ou do header `Authorization: Bearer`. Conexões inválidas fechadas com código 4001 (não autenticado) ou 4003 (sem acesso / sessão fechada).

**⚠️ session.snapshot:** atualmente enviado na conexão com `cards: []`, `votes: []`, `milestones: []`, `participants: []` vazios. O frontend deve carregar estes dados via REST logo após a conexão WebSocket.

| Evento | Direção | Payload | Descrição |
|---|---|---|---|
| `session.snapshot` | S → C | `{phase, timer: null, cards: [], votes: [], milestones: [], participants: [], action_items[]}` | Snapshot parcial; action_items preenchidos |
| `phase.advance` | C → S | `{type, phase}` | Facilitador solicita avanço de fase |
| `phase.changed` | S → C | `{phase, timer_duration_seconds}` | Fase avançada |
| `milestone.presentation.start` | C → S | `{type}` | Facilitador inicia apresentação |
| `milestone.presentation.next` | C → S | `{type}` | Próximo marco |
| `milestone.presentation.prev` | C → S | `{type}` | Marco anterior |
| `milestone.presentation.end` | C → S | `{type}` | Facilitador encerra apresentação |
| `milestone.presentation` | S → C | `{index, total, milestone: uuid}` | Navegação de marco (broadcast) |
| `timer.pause` | C → S | `{type}` | Facilitador pausa cronômetro |
| `timer.resume` | C → S | `{type}` | Facilitador retoma cronômetro |
| `timer.paused` | S → C | `{seconds_remaining}` | Broadcast pausa |
| `timer.resumed` | S → C | `{seconds_remaining}` | Broadcast retomada |
| `timer.sync` | S → C | `{seconds_remaining}` | Tick a cada 5s (via Celery) |
| `timer.expired` | S → C | `{phase}` | Cronômetro zerou |
| `card.created` | S → C | `{card}` | |
| `card.updated` | S → C | `{card_id, content}` | |
| `card.deleted` | S → C | `{card_id}` | |
| `card.grouped` | S → C | `{card_id, group_id}` | |
| `card.ungrouped` | S → C | `{card_id, previous_group_id}` | |
| `vote.cast` | S → C | `{card_id, voter_id, votes_remaining}` | |
| `vote.revoked` | S → C | `{card_id, voter_id, votes_remaining}` | |
| `action.check_updated` | S → C | `{action_id, status}` | Status de ação anterior atualizado |
| `participant.joined` | S → C | `{user_id, participant_id, name, avatar_url}` | Broadcast para outros (sem eco ao próprio canal) |
| `participant.left` | S → C | `{user_id}` | |
| `invite.status_updated` | S → C | `{invite_status, expires_at}` | Status do link de convite mudou |

---

## 10. Endpoints REST

### Autenticação (`/api/auth/`)

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/auth/register/` | Cadastro local (e-mail + senha) |
| POST | `/api/auth/login/` | Login local; retorna `access` + `refresh` |
| POST | `/api/auth/logout/` | Blacklist do refresh token |
| POST | `/api/auth/refresh/` | Renovar access token |

### Convites (público)

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/invites/{token}/` | Metadados da retro + status do convite |
| POST | `/api/invites/{token}/join/` | Entra como guest; retorna `access` + `refresh` |

### Retrospectivas

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/retrospectives/` | Lista retros do usuário (facilita + participa) |
| POST | `/api/retrospectives/` | Cria nova retrospectiva |
| GET | `/api/retrospectives/{id}/` | Detalhe da sessão ativa |
| GET | `/api/retrospectives/history/` | Lista retros encerradas |
| GET | `/api/retrospectives/{id}/detail/` | Detalhe de retro encerrada (histórico) |
| POST | `/api/retrospectives/{id}/close/` | Encerra sessão (facilitador, fase `actions`) |
| POST | `/api/retrospectives/{id}/focus-card/` | Define card em foco (facilitador) |
| POST | `/api/retrospectives/{id}/next-card/` | Avança para próximo card em foco |
| POST | `/api/retrospectives/{id}/reopen-entry/` | Reabre convite por 2 min (facilitador) |
| GET | `/api/retrospectives/{id}/invite-status/` | Status atual do convite |
| GET | `/api/retrospectives/{id}/presence/` | Lista de participantes e status online |
| GET | `/api/teams/suggestions/` | Sugestões de `team_key` (autocomplete) |

### Marcos

| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/api/retrospectives/{id}/milestones/` | Lista / cria marcos |
| GET/PUT/PATCH/DELETE | `/api/retrospectives/{id}/milestones/{milestone_id}/` | Detalhe / edita / remove marco |

### Cards

| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/api/retrospectives/{id}/cards/` | Lista / cria cards |
| GET/PATCH/DELETE | `/api/retrospectives/{id}/cards/{card_id}/` | Detalhe / edita / remove card |
| POST | `/api/retrospectives/{id}/cards/group/` | Agrupa cards (facilitador) |
| POST | `/api/retrospectives/{id}/cards/{card_id}/ungroup/` | Desagrupa card (facilitador) |
| POST/DELETE | `/api/retrospectives/{id}/cards/{card_id}/vote/` | Vota / revoga voto |
| GET | `/api/retrospectives/{id}/votes/` | Lista votos da sessão |
| GET/PATCH | `/api/retrospectives/{id}/votes-config/` | Configuração de votos |

### Action Items

| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/api/retrospectives/{id}/action-items/` | Lista / cria action items |
| GET/PATCH/DELETE | `/api/retrospectives/{id}/action-items/{action_id}/` | Detalhe / edita / remove |
| GET | `/api/retrospectives/{id}/previous-actions/` | Ações da retro anterior (mesmo `team_key`) |
| PATCH | `/api/retrospectives/{id}/previous-actions/{action_id}/status/` | Atualiza status de ação anterior |

---

## 11. Requisitos Funcionais

| # | Módulo | Descrição | Status |
|---|---|---|---|
| RF-01 | Autenticação | Auth local (e-mail + senha) via JWT simplejwt; register, login, logout, refresh | ✅ Implementado |
| RF-02 | Autenticação | Usuário guest via invite join endpoint; `is_guest=True` | ✅ Implementado |
| RF-03 | Sessão | Criação de sessão com `team_key`; status inicial `setup`; facilitador como participante | ✅ Implementado |
| RF-04 | Sessão | Convite via link UUID; join público sem conta | ✅ Implementado |
| RF-05 | Sessão | Reabrir convite por 2 min (facilitador); auto-bloqueio após entrada | ✅ Implementado |
| RF-06 | Fases | Avanço de fases via WebSocket; transições lineares validadas | ✅ Implementado |
| RF-07 | Cronômetro | Timer no servidor via Celery; sync a cada 5s; pausa/retomada | ✅ Implementado |
| RF-08 | Marcos | CRUD de marcos (facilitador, fase setup); apresentação navegável | ✅ Implementado |
| RF-09 | Board 4L | Cards em 4 colunas com broadcast em tempo real; CRUD por autor | ✅ Implementado |
| RF-10 | Agrupamento | Agrupamento por seleção múltipla (facilitador) | ✅ Implementado |
| RF-11 | Votação | Dot voting em `loathed`/`longed`; 1 voto/card/participante; contador de votos | ✅ Implementado |
| RF-12 | Debate | Cards ordenados por votos; card em foco persistido; controle pelo facilitador | ✅ Implementado |
| RF-13 | Ações | Action items com responsável, prazo, card de origem; check de ações anteriores | ✅ Implementado |
| RF-14 | Histórico | Dashboard de retros encerradas; detalhe com action items | ✅ Implementado |
| RF-15 | Presença | Painel de participantes; online/offline via WebSocket | ✅ Implementado |
| RF-16 | Som | Alerta sonoro via Web Audio API ao expirar o cronômetro | ✅ Implementado (`utils/sound.ts`) |
| RF-17 | `skip_check_phase` | Campo existe; pulo automático da fase check não implementado | ⚠️ Parcial |
| RF-18 | `session.snapshot` completo | Envia apenas `action_items`; cards/votes/milestones/participants são arrays vazios | ⚠️ Parcial |
| RF-19 | OAuth (Google/GitHub) | allauth instalado; nenhum provider configurado ou exposto no frontend | ❌ Não exposto |
| RF-20 | CI/CD | Não implementado | ❌ Pendente |

---

## 12. Requisitos Não Funcionais

### 12.1 Performance

- Latência WebSocket: < 200ms em rede interna.
- `timer.sync` emitido a cada 5s. Frontend interpola contagem localmente a cada 1s e corrige com `timer.sync`.
- `session.snapshot` enviado em < 1s na conexão.

### 12.2 Segurança

- JWT: access token 8h, refresh token 7d com blacklist (simplejwt `token_blacklist`).
- WebSocket autenticado via JWT no query param `?token=` ou header `Authorization`.
- Link de convite UUID v4; auto-bloqueado após lobby; reaberto apenas por 2 min via facilitador.
- `ALLOWED_EMAIL_DOMAINS`: lista opcional via env para restringir domínios de e-mail no cadastro.
- `allow_self_vote=False` padrão: previne autor de votar no próprio card.
- Ações de facilitador (agrupar, avançar fase, encerrar) verificadas server-side.
- CORS configurado via `CORS_ALLOWED_ORIGINS` env.
- `CSRF_TRUSTED_ORIGINS` configurável via env.
- Senhas com PBKDF2 (padrão Django). Guests têm senha inutilizável.

### 12.3 Disponibilidade

- MVP sem SLA formal.
- Cold starts no Fly.io: 2–5s. Facilitadores devem "aquecer" antes da retro.

### 12.4 Escalabilidade

- Django Channels + Redis Channel Layer suporta múltiplas instâncias horizontais.
- Celery workers escalam independentemente.
- Até 30 participantes simultâneos por sessão no MVP.

### 12.5 Qualidade de código

- Linting: `ruff` para backend; `eslint` + `prettier` para frontend.
- Backend: `python manage.py test` deve passar sem falhas.
- WebSocket tests: `pytest tests/realtime/` com `USE_IN_MEMORY_CHANNEL_LAYER=true`.
- Frontend: `npm run build` deve passar sem erros.

---

## 13. Limitações Conhecidas e Débitos Técnicos

| Item | Descrição | Impacto | Prioridade de resolução |
|---|---|---|---|
| `session.snapshot` parcial | `cards`, `votes`, `milestones`, `participants` enviados como arrays vazios | Frontend precisa fazer requests REST adicionais após conectar | Alta |
| Índice de apresentação em memória | `RetrospectiveConsumer.presentation_indices` perde estado em restart do worker | Estado de apresentação zerado em reinicializações | Média |
| `skip_check_phase` sem efeito | Flag existe no modelo e na UI de criação mas não pula a fase automaticamente | Fase check sempre aparece mesmo com flag ativo | Média |
| `mdi` icons mistos com Heroicons | Alguns componentes usam prefixo `mdi` (requer CDN ou pacote), outros usam `@heroicons/vue` | Inconsistência visual e dependência extra | Baixa |
| OAuth não exposto | `django-allauth` instalado mas nenhum provider configurado ou interface de login exposta | Usuários só conseguem login local | Baixa (MVP) |
| CI/CD ausente | Nenhum workflow GitHub Actions criado | Deploy manual; sem proteção de regressão automática | Alta (pré-deploy) |
| Worker + Beat no mesmo processo | `celery worker -B` em produção | Beat não é altamente disponível; aceitável para MVP | Baixa |

---

## 14. Deploy em Produção

Esta seção documenta **todos os passos** necessários para fazer o primeiro deploy do RetroApp 4L em ambiente de produção zero-cost (Fly.io + Neon + Upstash + Vercel).

### 14.1 Pré-requisitos

1. Conta no [Fly.io](https://fly.io) com `flyctl` instalado localmente.
2. Conta no [Neon](https://neon.tech) para PostgreSQL.
3. Conta no [Upstash](https://upstash.com) para Redis.
4. Conta no [Vercel](https://vercel.com) para frontend.
5. Repositório no GitHub (ou Fly.io aceita deploy direto via CLI).

### 14.2 Banco de Dados — Neon PostgreSQL

1. Criar um projeto no Neon.
2. Anotar a connection string no formato:

   ```
   postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
   ```

3. As variáveis de ambiente a configurar no backend:

   ```
   DB_ENGINE=postgres
   POSTGRES_DB=<DBNAME>
   POSTGRES_USER=<USER>
   POSTGRES_PASSWORD=<PASSWORD>
   POSTGRES_HOST=<HOST>
   POSTGRES_PORT=5432
   ```

### 14.3 Redis — Upstash

1. Criar um banco Redis no Upstash.
2. Anotar a URL no formato `redis://:PASSWORD@HOST:PORT` ou `rediss://...` (TLS).
3. Variável de ambiente:

   ```
   REDIS_URL=rediss://:PASSWORD@HOST:PORT
   ```

   > Esta variável é usada automaticamente para `CHANNEL_LAYERS` (WebSocket) e `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND`.

### 14.4 Backend — Fly.io

#### 14.4.1 Criar `fly.toml` para o backend

Criar `backend/fly.toml`:

```toml
app = "retroapp4l-backend"
primary_region = "gru"  # São Paulo

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  memory = "256mb"
  cpu_kind = "shared"
  cpus = 1
```

#### 14.4.2 Variáveis de ambiente do backend

Configurar via `fly secrets set` ou no painel do Fly.io:

```bash
fly secrets set \
  DJANGO_SECRET_KEY="<gere uma chave segura com python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'>" \
  DJANGO_DEBUG=false \
  DJANGO_ALLOWED_HOSTS="retroapp4l-backend.fly.dev" \
  DJANGO_CSRF_TRUSTED_ORIGINS="https://retroapp4l-backend.fly.dev" \
  DB_ENGINE=postgres \
  POSTGRES_DB="<neon_db>" \
  POSTGRES_USER="<neon_user>" \
  POSTGRES_PASSWORD="<neon_password>" \
  POSTGRES_HOST="<neon_host>" \
  POSTGRES_PORT=5432 \
  REDIS_URL="rediss://:PASSWORD@HOST:PORT" \
  CORS_ALLOWED_ORIGINS="https://retroapp4l-frontend.vercel.app" \
  USE_IN_MEMORY_CHANNEL_LAYER=false
```

> **`USE_IN_MEMORY_CHANNEL_LAYER`:** deve ser `false` em produção para usar o Redis Upstash como channel layer.

#### 14.4.3 Deploy do backend

```bash
cd backend
fly launch --no-deploy          # configura app no Fly.io
fly deploy                      # faz o deploy (roda migrate + daphne)
```

O `Dockerfile` já executa `python manage.py migrate && daphne -b 0.0.0.0 -p 8000 config.asgi:application` no startup.

#### 14.4.4 Arquivos estáticos

O backend não serve arquivos estáticos via Django em produção (apenas API + WebSocket). Se for necessário, adicionar `whitenoise` ao `MIDDLEWARE` e ao `requirements.txt`:

```
whitenoise==6.x
```

```python
# settings/base.py — logo após SecurityMiddleware
"whitenoise.middleware.WhiteNoiseMiddleware",
```

#### 14.4.5 Criar `fly.toml` para o worker Celery

Criar `backend/fly.worker.toml` (ou usar process groups no mesmo app):

```toml
app = "retroapp4l-worker"
primary_region = "gru"

[build]
  dockerfile = "Dockerfile.worker"

[[vm]]
  memory = "256mb"
  cpu_kind = "shared"
  cpus = 1
```

O `Dockerfile.worker` já executa `celery -A config worker -B -l info`.

Deploy do worker:

```bash
fly deploy --config fly.worker.toml
```

> **Alternativa (process groups):** É possível rodar backend e worker no mesmo app Fly.io usando `[processes]` no `fly.toml`. Reduz o número de VMs mas mistura responsabilidades.

### 14.5 Frontend — Vercel

#### 14.5.1 Variáveis de ambiente do frontend

No painel da Vercel, configurar:

```
NUXT_PUBLIC_API_BASE=https://retroapp4l-backend.fly.dev/api
NUXT_PUBLIC_WS_BASE=wss://retroapp4l-backend.fly.dev/ws
```

> **`wss://`** (WebSocket seguro) é obrigatório quando o backend está em HTTPS/TLS no Fly.io.

#### 14.5.2 Deploy via Vercel CLI ou GitHub Integration

```bash
cd frontend
npm install
npm run build   # valida antes de enviar

# via CLI
npx vercel --prod
```

Ou conectar o repositório GitHub na Vercel com:

- **Root directory:** `frontend`
- **Build command:** `npm run build`
- **Output directory:** `.output`
- **Framework Preset:** Other (ou Node.js)

> **Nota:** O Nuxt 3 com `ssr: false` gera uma SPA, mas o build produz um servidor Node.js (`.output/server/index.mjs`). Para deploy na Vercel como SPA estática pura, use `nuxt generate` em vez de `nuxt build` e configure o output directory como `.output/public`.

### 14.6 Checklist de deploy

- [ ] Banco Neon criado e connection string anotada
- [ ] Redis Upstash criado e URL anotada
- [ ] `fly secrets set` com todas as variáveis do backend
- [ ] `fly deploy` do backend executado sem erros
- [ ] `python manage.py migrate` executado (o Dockerfile faz isso no startup)
- [ ] Verificar logs: `fly logs -a retroapp4l-backend`
- [ ] `fly deploy` do worker Celery executado
- [ ] Frontend conectado à Vercel com variáveis de ambiente corretas
- [ ] Build da Vercel passou sem erros
- [ ] Testar fluxo completo: cadastro → criação de retro → convite → sessão WS
- [ ] Testar timer: avançar fase cronometrada e verificar `timer.sync` chegando
- [ ] Testar guest: acessar link de convite sem conta cadastrada

### 14.7 Criação do superusuário (pós-deploy)

```bash
fly ssh console -a retroapp4l-backend
python manage.py createsuperuser
```

### 14.8 Variáveis de ambiente — resumo completo

| Variável | Onde | Descrição |
|---|---|---|
| `DJANGO_SECRET_KEY` | Backend | Chave secreta Django (mín. 50 chars aleatórios) |
| `DJANGO_DEBUG` | Backend | `false` em produção |
| `DJANGO_ALLOWED_HOSTS` | Backend | Hosts separados por vírgula; ex: `retroapp4l-backend.fly.dev` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Backend | Origins confiáveis; ex: `https://retroapp4l-backend.fly.dev` |
| `DB_ENGINE` | Backend | `postgres` |
| `POSTGRES_DB` | Backend | Nome do banco Neon |
| `POSTGRES_USER` | Backend | Usuário Neon |
| `POSTGRES_PASSWORD` | Backend | Senha Neon |
| `POSTGRES_HOST` | Backend | Host Neon |
| `POSTGRES_PORT` | Backend | `5432` |
| `REDIS_URL` | Backend | URL Upstash (prefixo `rediss://` para TLS) |
| `CORS_ALLOWED_ORIGINS` | Backend | Origins do frontend; ex: `https://retroapp4l.vercel.app` |
| `USE_IN_MEMORY_CHANNEL_LAYER` | Backend | `false` em produção |
| `ALLOWED_EMAIL_DOMAINS` | Backend | (opcional) Restrição de domínio para cadastro |
| `NUXT_PUBLIC_API_BASE` | Frontend | URL base da API; ex: `https://retroapp4l-backend.fly.dev/api` |
| `NUXT_PUBLIC_WS_BASE` | Frontend | URL base WebSocket; ex: `wss://retroapp4l-backend.fly.dev/ws` |

---

## 15. Decisões Registradas e Trade-offs

### 15.1 JWT (simplejwt) como auth primária em vez de sessões

`djangorestframework-simplejwt` escolhido por compatibilidade direta com SPA Nuxt (stateless) e por ser necessário para autenticar WebSocket via query param. `django-allauth` permanece instalado para suporte futuro a OAuth social, mas o fluxo principal é simplejwt.

### 15.2 Usuário guest como `User` com `is_guest=True`

Implementar guests como usuário Django real permite reutilizar toda a infraestrutura de permissões, participações e action items sem refatoração do domínio. Trade-off: banco acumula usuários guest; limpeza periódica pode ser necessária em produção.

### 15.3 `allow_self_vote` configurável

Adicionado como feature extra além do PRD original. Permite ao facilitador decidir se auto-votação é válida em seu contexto de time. Padrão `False` mantém comportamento original do PRD.

### 15.4 `focus_card` persistido no banco

Alternativa ao armazenamento em memória. Garante que o card em foco sobrevive a reconexões e restarts do backend. Leve overhead de escrita a cada troca de foco.

### 15.5 `phase_durations` como JSONField

Permite ao facilitador configurar durações diferentes por fase sem adicionar múltiplos campos ao modelo. Flexível para times com ritmos diferentes.

### 15.6 Worker Celery + Beat no mesmo processo

`celery worker -B` simplifica a infra (uma VM em vez de duas) ao custo de menor resiliência do Beat em produção. Aceitável para MVP com times pequenos. Separar se o cronômetro se mostrar instável.

### 15.7 Nuxt 3.17.5 fixado

Versão 3.21.x apresenta incompatibilidade no Windows com `#app-manifest` e `NUXT_VITE_NODE_OPTIONS.socketPath`. Fixado em 3.17.5 até resolução upstream do Nuxt.

### 15.8 `session.snapshot` parcial (débito técnico)

O consumer atual envia `cards: []`, `votes: []`, `milestones: []`, `participants: []` vazios no snapshot. O frontend compensa com calls REST via `useApiClient` imediatamente após conectar. A resolução ideal é popular o snapshot completamente no consumer usando `database_sync_to_async`, mas o impacto em tempo de conexão deve ser medido antes.

### 15.9 Infraestrutura gratuita (Fly.io + Neon + Upstash + Vercel)

Permite MVP operar com R$ 0,00 durante os 60 dias de avaliação. Cold starts mitigados com aquecimento manual. Limites de armazenamento folgados para o volume esperado (~100 KB/retro).

### 15.10 `team_key` como SlugField

Mesma decisão do PRD v7: string simples permite agrupamento imediato sem entidade `Team`. `SlugField` garante formato válido (letras, números, hífens, underscores).

### 15.11 `description` no modelo Retrospective

Campo `TextField(blank=True)` adicionado além do PRD original para permitir ao facilitador descrever o objetivo da retro. Não exibido em destaque na UI atual mas disponível na API.

### 15.12 `external_tracker_url` no ActionItem

Campo stub `URLField(blank=True)` reservado para integração futura com Jira/Linear/GitHub Issues (fora do escopo do MVP). Não exposto na UI atual.

---

*RetroApp 4L PRD v8.0 — Fonte da verdade: código-fonte*
*Projeto Open Source — Licença MIT*
*Contribuições são bem-vindas. Veja CONTRIBUTING.md para diretrizes.*
