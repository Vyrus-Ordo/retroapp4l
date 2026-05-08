# Documentação de Implementação Atual - RetroApp 4L

> **Última Atualização:** Maio de 2026
> **Objetivo:** Este documento descreve o comportamento atualmente implementado no código-fonte. O código é a única fonte da verdade.

---

## 1. Visão Arquitetural

A aplicação é um monorepo com **frontend Nuxt SPA**, **backend Django/DRF**, **WebSockets via Django Channels** e tarefas assíncronas com **Celery**.

* **Frontend:** Nuxt 3.17.5, Vue 3, Pinia, TailwindCSS e `@nuxtjs/turnstile`. `ssr: false`, mas o build de produção gera servidor Node em `.output/server/index.mjs`.
* **Backend:** Django 5.2.13, DRF, SimpleJWT, django-allauth instalado, Channels/Daphne para WebSockets.
* **Banco e Redis:** SQLite por padrão local quando `DB_ENGINE` não é `postgres`; PostgreSQL quando `DB_ENGINE=postgres`. Redis é usado como broker/result backend do Celery e como Channel Layer quando `USE_IN_MEMORY_CHANNEL_LAYER=false`.
* **Infraestrutura:** `docker-compose.yml` para ambiente local com backend, worker, db, redis e frontend. `docker-compose.prod.yml` adiciona Nginx com TLS, proxy para `/api/`, `/admin/`, `/ws/` e frontend. Backend usa `python:3.11-slim`; frontend usa Node 20.
* **Static files:** backend executa `collectstatic` no startup do Dockerfile e Nginx serve `/static/` em produção.

---

## 2. Backend (Aplicações Django)

O backend fica em `/backend`. Os apps de domínio estão em `/backend/apps/`.

### Tabelas do Banco de Dados (Models)

* **`User` (App: users):**
  * **Campos:** `id` UUID, `name`, `email` único, `public_email`, `oauth_provider`, `oauth_id`, `avatar_url`, `is_guest`, `is_active`, `is_staff`, `created_at`.
  * **Propósito:** usuário customizado. Guests são usuários reais com `is_guest=True`, e-mail interno `guest+uuid@guest.retroapp4l.local` e senha inutilizável. `display_email` retorna `public_email` para guest e `email` para usuário normal.

* **`Retrospective` (App: retrospectives):**
  * **Campos:** `id`, `title`, `sprint_name`, `description`, `team_key`, `facilitator`, `status`, `invite_token`, `invite_revoked_at`, `max_votes_per_user`, `allow_self_vote`, `skip_check_phase`, `focus_card`, `invite_temporarily_open_until`, campos de timer, `phase_durations`, `created_at`, `closed_at`.
  * **Propósito:** sessão de retrospectiva e estado operacional da reunião.
  * **Status existentes:** `setup`, `lobby`, `presentation`, `check`, `board`, `grouping`, `voting`, `discussion`, `actions`, `closed`.

* **`Milestone` (App: retrospectives):**
  * **Campos:** `id`, `retrospective`, `author`, `category`, `description`, `created_at`.
  * **Categorias:** `achievement`, `challenge`, `change`, `recognition`, `other`.
  * **Propósito:** marcos cadastrados pelo facilitador na fase `setup`.

* **`Participant` (App: retrospectives):**
  * **Campos:** `id`, `retrospective`, `user`, `votes_remaining`, `joined_at`.
  * **Regra:** constraint única para par `retrospective + user`.

* **`AccessLog` (App: retrospectives):**
  * **Campos:** `id`, `retrospective`, `action`, `triggered_by`, `participant`, `timestamp`.
  * **Ações:** `opened`, `closed`, `participant_joined`, `link_reopened`, `link_auto_blocked`.

* **`Card` (App: cards):**
  * **Campos:** `id`, `retrospective`, `author`, `column`, `content`, `is_anonymous`, `group`, `position`, `created_at`.
  * **Colunas:** `loved`, `loathed`, `longed`, `learned`. A UI exibe `loved` como "Liked".
  * **Propósito:** cards do quadro. Agrupamento é representado por `group` apontando para outro `Card`.
  * **Anonimato:** `is_anonymous=false` por padrão. Quando `true`, `author` continua persistido, mas serializers públicos retornam `author=null`, `author_name=null` e `author_display="Anonymous"`.

* **`CardVote` (App: cards):**
  * **Campos:** `id`, `card`, `voter`, `created_at`.
  * **Regra:** constraint única para `card + voter`.

* **`ActionItem` (App: actions):**
  * **Campos:** `id`, `retrospective`, `card`, `description`, `assignee`, `due_date`, `external_tracker_url`, `status`, `created_at`.
  * **Status:** `not_started`, `in_progress`, `done`.

### Módulos de Lógica e Funcionalidades

### `users` (Gerenciamento de Usuários e Autenticação)

* Auth primária por JWT SimpleJWT:
  * `POST /api/auth/register/`
  * `POST /api/auth/login/`
  * `POST /api/auth/logout/`
  * `POST /api/auth/refresh/`
* Registro exige `cf_turnstile_response`; a validação fica em `turnstile.py`.
* `ALLOWED_EMAIL_DOMAINS` pode restringir domínios no cadastro.
* Login bloqueia usuários guest; guests entram apenas via convite.
* `django-allauth` está instalado e suas URLs ficam em `/accounts/`, mas o código não configura provider social no settings. O frontend possui um link para `/accounts/google/login/`, dependente de configuração externa não presente no repositório.

### `retrospectives` (Core do Domínio)

* Criação/listagem/detalhe de sessões:
  * `GET/POST /api/retrospectives/`
  * `GET /api/retrospectives/{id}/`
* Guest não pode criar retrospectivas nem acessar sugestões de times.
* Ao criar uma retro:
  * status inicial é `setup`;
  * facilitador vira participante;
  * `invite_token` é gerado;
  * `AccessLog.opened` é registrado.
* Histórico:
  * `GET /api/retrospectives/history/` lista retros fechadas acessíveis ao usuário;
  * `GET /api/retrospectives/{id}/detail/` retorna detalhe de retro fechada.
* A sessão ativa (`GET /api/retrospectives/{id}/`) é bloqueada quando status é `closed`; deve-se usar o endpoint de histórico.
* Fechamento:
  * `POST /api/retrospectives/{id}/close/` exige facilitador, fase `actions` e payload `{ "confirm": true }`;
  * define `status=closed`, `closed_at`, remove `invite_token`, preenche `invite_revoked_at` e limpa `focus_card`.
* Convites:
  * `GET /api/invites/{token}/` resolve metadados públicos e status do convite;
  * `POST /api/invites/{token}/join/` cria/reaproveita usuário e adiciona participante.
  * convite fica `active` apenas em `lobby`, `temporarily_open` enquanto `invite_temporarily_open_until` estiver no futuro, ou `blocked`.
  * reabertura: `POST /api/retrospectives/{id}/reopen-entry/` abre por 120 segundos e agenda tarefa Celery para bloquear depois.
  * **Limitação:** entrar por convite temporariamente aberto não bloqueia imediatamente o link; o bloqueio ocorre pela tarefa agendada quando a janela expira.
* Presença:
  * `GET /api/retrospectives/{id}/presence/` retorna participantes cadastrados na sala, não um estado online persistente.
  * online/offline no frontend é estimado por eventos WebSocket `participant.joined`/`participant.left`.
* Marcos:
  * CRUD em `/api/retrospectives/{id}/milestones/`;
  * criação/edição/exclusão apenas pelo facilitador na fase `setup`;
  * guests não podem criar/editar/excluir marcos.

### `realtime` (WebSockets e Sincronização)

* Rota WebSocket: `/ws/retrospectives/{retrospective_id}/?token={JWT}`.
* Autenticação por JWT em query string ou header `Authorization` via middleware customizado.
* A conexão é recusada se o usuário não estiver autenticado, não tiver acesso à retro ou a retro estiver `closed`.
* Ao conectar, o servidor envia `session.snapshot` com:
  * `phase` real da retro;
  * `action_items` carregados via ORM;
  * `cards`, `votes`, `milestones`, `participants` como arrays vazios;
  * `timer: null`.
* O frontend compensa o snapshot parcial buscando cards, votos, marcos, participantes e ações via REST.
* Eventos de domínio são propagados por signals Django (`cards.signals`, `actions.signals`, `retrospectives.signals`).
* Timer:
  * fases cronometradas: `presentation`, `check`, `board`, `grouping`, `voting`, `discussion`, `actions`;
  * duração vem de `phase_durations` ou defaults;
  * ao avançar fase, `timer_started_at`, `timer_paused_at` e `timer_duration_seconds` são atualizados;
  * Celery emite `timer.sync` a cada 5s até expirar ou pausar;
  * facilitador pode enviar `timer.pause` e `timer.resume`.
* Apresentação de marcos:
  * eventos aceitos: `milestone.presentation.start`, `.next`, `.prev`, `.end`;
  * o índice é armazenado em memória no processo (`presentation_indices`);
  * se não houver marcos, `.start` muda a fase para `check`.
* **Limitação crítica de fases:** `state_machine.py` define transições lineares, mas o consumer atual não chama `is_valid_transition`; `phase.advance` apenas verifica se a fase destino existe e se o usuário é facilitador. Assim, o backend aceita saltos para qualquer status válido enviado pelo facilitador.

### `cards` (Itens do 4L)

* Endpoints:
  * `GET/POST /api/retrospectives/{id}/cards/`
  * `GET/PATCH/DELETE /api/retrospectives/{id}/cards/{card_id}/`
  * `POST /api/retrospectives/{id}/cards/group/`
  * `POST /api/retrospectives/{id}/cards/{card_id}/ungroup/`
  * `POST/DELETE /api/retrospectives/{id}/cards/{card_id}/vote/`
  * `GET /api/retrospectives/{id}/votes/`
  * `PUT /api/retrospectives/{id}/votes-config/`
* Cards:
  * qualquer participante pode criar cards em fases não bloqueadas;
  * criação/edição aceita `is_anonymous`;
  * cards antigos seguem não anônimos porque o campo tem default `false`;
  * cards anônimos preservam `author` internamente para permissões, votos, auditoria e relacionamentos;
  * REST e WebSocket mascaram autoria visual com `author=null`, `author_name=null` e `author_display="Anonymous"`;
  * REST inclui `can_edit`, calculado por usuário, para a UI permitir edição/exclusão do próprio card sem expor autor;
  * mutação de cards é bloqueada apenas em `discussion`, `actions` e `closed`;
  * autor pode editar/excluir o próprio card;
  * limite de conteúdo: 500 caracteres.
* UI permite criar/editar/excluir cards somente na fase `board`, mas a API é mais permissiva.
* UI exibe `Add anonymously` no modal de criação/edição e mostra badge discreto `Anonymous` em Board, Grouping, Voting, Discussion, Focus/derivados e History.
* Ao abrir o modal de novo card pelo botão `Add` do board, o `CardComposer` aplica foco automático no textarea de descrição usando template ref e `nextTick()`.
  * Agrupamento:
  * apenas facilitador;
  * payload usa `card_ids` e opcional `group_parent_id`;
  * exige pelo menos 2 cards da mesma coluna;
  * não há restrição explícita de fase além de sessão não fechada.
  * o serializer de cards expõe `group` e `group_parent_id` como identificadores do card pai; `group_parent_id` é alias público de `group_id`.
  * a UI normaliza `group`/`group_parent_id`, renderiza apenas cards raiz nas fases posteriores e mostra filhos agrupados como sub-itens em um único nível Pai -> Filhos.
  * a tela de histórico (`history/[id].vue`) aplica a mesma lógica de agrupamento: `rootHistoryCards` filtra cards raiz e `historyChildrenByParentId` mapeia filhos por `group_parent_id`/`group`, passando-os como `groupedCards` para `RetroCard`.
* Votação:
  * permitida somente na fase `voting`;
  * apenas cards `loathed` e `longed` são votáveis;
  * máximo 1 voto por card por participante;
  * `allow_self_vote=false` bloqueia voto no próprio card;
  * cada voto decrementa `Participant.votes_remaining`; revogação incrementa.
  * cards anônimos usam a autoria real para bloqueio de auto-voto sem revelar essa autoria no payload público.
* Configuração de votos:
  * `PUT /votes-config/` altera apenas `max_votes_per_user` e reseta `votes_remaining` dos participantes;
  * permitido só antes de `voting`;
  * `allow_self_vote` não é alterado por esse endpoint.

### `actions` (Itens de Ação)

* Endpoints:
  * `GET/POST /api/retrospectives/{id}/action-items/`
  * `GET/PATCH/DELETE /api/retrospectives/{id}/action-items/{action_id}/`
  * `GET /api/retrospectives/{id}/previous-actions/`
  * `PUT /api/retrospectives/{id}/previous-actions/{action_id}/status/`
* Action items da sessão:
  * listagem exige participação na retro;
  * criação é permitida apenas na fase `discussion`, apenas pelo facilitador;
  * criação na fase `actions` é bloqueada;
  * edição e exclusão são permitidas nas fases `discussion` e `actions`, apenas pelo facilitador;
  * participantes têm leitura na fase `actions`.
  * quando um action item referencia card anônimo, o item mantém só o `card`/`card_id`; a UI não exibe autor do card relacionado.
* Payload de criação/edição:
  * `description`;
  * `assignee_id` é o **id do Participant**, não o id do User;
  * `card_id` opcional, validado contra cards da retro;
  * `due_date`, `status`, `external_tracker_url`.
* Ações anteriores:
  * busca a última retro `closed` com mesmo `team_key`;
  * status pode ser atualizado por qualquer participante da retro atual pelo endpoint de previous-actions;
  * `"pending"` ainda é aceito como alias legado e gravado como `not_started`.

---

## 3. Frontend (Nuxt 3)

O frontend fica em `/frontend` e é uma SPA Nuxt.

### 3.1. Estrutura de Rotas (`pages/`)

* `index.vue`: landing page para anônimos/guests e dashboard para usuários autenticados não-guest.
* `login.vue`: redireciona para `/auth/login`.
* `auth/login.vue`: login local por e-mail/senha e link visual para Google via allauth.
* `auth/register.vue`: cadastro local com Turnstile.
* `join.vue`: tela simples que navega para `/retro/{code}`; não resolve token nem PIN real.
* `retro/create.vue`: criação de retro, fase durations, milestones iniciais, `allow_self_vote` e `skip_check_phase`.
* `retro/invite/[token].vue`: resolve convite, coleta nome/e-mail opcional e entra como usuário autenticado ou guest.
* `retro/[id].vue`: workspace colaborativo principal.
* `history/index.vue`: histórico de retros fechadas.
* `history/[id].vue`: detalhe de retro fechada; cards agrupados são renderizados com a hierarquia Pai -> Filhos usando `rootHistoryCards` e `historyChildrenByParentId` (computed locais da página).

### 3.2. Gerenciamento de Estado Global (`stores/` Pinia)

* `auth.ts`: JWT, usuário atual, refresh, login, register, logout e persistência em `localStorage`.
* `guest.ts`: nome/e-mail informados por guest para prefilling local.
* `retro.ts`: dashboard, sessão ativa, cards, votos, action items, previous actions, histórico, seleção de cards e foco de discussão.
* `participants.ts`: participantes carregados da API, ids online estimados por WS, logs locais e status do convite.
* `timer.ts`: hidratação do timer, contagem local, pausa/retomada e formatação.
* `toast.ts`: toasts globais.

### 3.3. Serviços e Integrações (`composables/`)

* `useApiClient.ts`: cliente REST com base `NUXT_PUBLIC_API_BASE`, Bearer token e tentativa de refresh.
* `useWebSocket.ts`: abre WS em `NUXT_PUBLIC_WS_BASE`, envia token na query string, aplica eventos no store, tenta reconectar com backoff e toca som no fim do timer.
* `usePhase.ts`: metadados e cálculo da próxima fase no frontend.
  * **Ordem frontend atual:** `setup -> lobby -> check -> presentation -> board -> grouping -> voting -> discussion -> actions -> closed`.
  * `skip_check_phase` faz o frontend pular de `lobby` para `presentation`.
  * Essa ordem diverge de `state_machine.py`, que lista `presentation` antes de `check`, mas a validação backend não impede o fluxo enviado pela UI.
* `useTimer.ts`: loop local de contagem do timer.

### 3.4. Fluxo de Retrospectiva (Componentes Visuais de `phases/`)

1. **`SetupView.vue`**: tela de preparação; facilitador avança para lobby.
2. **`LobbyView.vue`**: exibe link de convite e contagem de participantes; facilitador inicia a sessão. Pela ordem do frontend, o próximo passo é `check`, exceto quando `skip_check_phase=true`, quando vai para `presentation`.
3. **`CheckView.vue`**: revisão de ações da última retro fechada do mesmo time. Somente facilitador consegue editar status pela UI.
4. **`MilestonesView.vue`**: exibe todos os marcos cadastrados; a UI atual não usa os eventos de apresentação `.start/.next/.prev/.end`, apenas mostra a grade e deixa avançar fase.
5. **`BoardView.vue`**: quadro 4L com criação/edição/exclusão de cards pela UI. Ao acionar `Add`, o modal `CardComposer` abre com foco automático no campo de descrição.
6. **`GroupingView.vue`**: facilitador seleciona cards da mesma coluna e agrupa; participantes observam.
7. **`VotingView.vue`**: votos apenas em `loathed` e `longed`; mostra votos restantes.
8. **`DiscussionView.vue`**: lista cards raiz ordenados por votos, renderiza filhos agrupados como sub-itens, permite ao facilitador definir foco, avançar foco e criar action item associado ao card em foco.
9. **`ActionsView.vue`**: revisão de action items; facilitador pode editar/excluir e fechar a retro. A UI não exibe botão de criação nessa fase.
10. **`ClosedView.vue`**: componente de encerramento, mas `retro/[id].vue` redireciona para `/history/{id}` quando detecta status `closed`.

---

## 4. Fluxo Detalhado da Sessão (Máquina de Estados)

Há duas representações de fluxo no código:

* `backend/apps/realtime/state_machine.py`: define transições lineares `setup -> lobby -> presentation -> check -> board -> grouping -> voting -> discussion -> actions -> closed`.
* `frontend/composables/usePhase.ts`: avança pela ordem `setup -> lobby -> check -> presentation -> board -> grouping -> voting -> discussion -> actions -> closed`.

O comportamento efetivo da aplicação é determinado pelo frontend somado ao consumer WebSocket:

1. O facilitador clica para avançar fase.
2. O frontend calcula a próxima fase com `usePhase.ts`.
3. O cliente envia `{ type: "phase.advance", phase: next }`.
4. O consumer valida apenas se o usuário é facilitador e se `phase` existe nos choices de `RetrospectiveStatus`.
5. O status é gravado diretamente no banco e transmitido via `phase.changed`.

**Consequências atuais:**

* A ordem efetiva pela UI é `setup -> lobby -> check -> presentation -> board -> grouping -> voting -> discussion -> actions -> closed`.
* `skip_check_phase` tem efeito na UI: ao sair do `lobby`, pula `check` e vai para `presentation`.
* O backend não garante transição linear, apesar de existir `state_machine.py`.
* Participantes não conseguem avançar fase porque o consumer exige facilitador.
* Timers iniciam automaticamente quando a fase destino está em `TIMED_PHASES`.

---

## 5. Convenções e Pontos Chaves Implementados

* **Backend como fonte de verdade para dados persistidos:** modelos, permissões e endpoints validam regras centrais como voto, action items, fechamento e acesso.
* **Anonimato visual de cards:** `Card.author` permanece como fonte de verdade interna. A UI e os payloads públicos usam `is_anonymous`, `author_display` e `can_edit` para ocultar identidade sem alterar permissões.
* **Validação de fases incompleta:** a fase atual é persistida no backend, mas a transição linear não é aplicada no consumer.
* **Realtime por signals:** saves/deletes de cards, votos, milestones e action items emitem eventos WS.
* **Snapshot WS parcial:** o frontend depende de REST para hidratar quase todo o estado inicial.
* **Guests como usuários reais:** facilita permissões e relacionamentos, mas pode acumular registros no banco.
* **Sessão fechada é somente histórico:** endpoints de sessão ativa e WS recusam retros `closed`.
* **Textos da UI:** predominam em inglês, com alguns textos/comentários internos em português.

---

## 6. Design System & Estilização

O frontend usa TailwindCSS e CSS customizado, sem biblioteca de componentes como Vuetify/Element.

### 6.1. Configuração Tailwind (`tailwind.config.ts`)

* Fonte principal configurada como **Poppins** em `font-sans`; algumas telas usam `JetBrains Mono` por classe direta.
* Paleta customizada: `brand`, `success`, `warning`, `danger`, `gray`.
* Sombras e animação `glow` customizadas.

### 6.2. Tokens CSS (`assets/css/tokens.css`)

* Define variáveis `--ds-*` e aliases semânticos:
  * textos: `--fg-primary`, `--fg-secondary`, `--fg-tertiary`;
  * fundos: `--bg-canvas`, `--bg-surface`, `--bg-primary`, `--bg-secondary`;
  * bordas: `--border-default`, `--border-strong`.
* `assets/css/tailwind.css` define classes utilitárias como `panel`, `field-input`, `button-primary`, `button-secondary`.

### 6.3. Ícones e Complementos

* O projeto usa `@heroicons/vue` em vários componentes.
* Também há classes Material Design Icons (`mdi mdi-*`) espalhadas pela UI, mas não há pacote `@mdi/*` ou import CSS explícito no `package.json`. Isso depende de CSS externo não documentado no código.
* O board usa componentes próprios (`BoardGrid`, `ColumnHeader`, `RetroCard`) e exibe colunas `Liked`, `Loathed`, `Longed for`, `Learned`.
* A landing page usa imagem real em `public/img/board_jedi.png`.

---

## Divergências encontradas

* A documentação dizia que a máquina de estados validava transições lineares; o consumer atual não usa `state_machine.py` e aceita qualquer status válido enviado pelo facilitador.
* A ordem de fases documentada/backend (`presentation` antes de `check`) diverge da ordem efetiva do frontend (`check` antes de `presentation`).
* A documentação dizia que `skip_check_phase` não tinha efeito; no frontend atual ele pula `check` ao sair do lobby, embora o backend não trate essa regra.
* A documentação antiga marcava action items em `discussion`/`actions` como pendentes; o código já implementa criação apenas pelo facilitador em `discussion` e edição/exclusão pelo facilitador em `discussion` ou `actions`.
* O endpoint `/votes-config/` estava documentado como `GET/PATCH` e configurando `allow_self_vote`; o código implementa apenas `PUT` e altera somente `max_votes_per_user`.
* O payload de agrupamento estava descrito com `group_card_id`; o código usa `group_parent_id`.
* O payload de action item estava descrito como `assignee` FK/User; a API espera `assignee_id` como id de `Participant`.
* O auto-bloqueio imediato do convite após entrada tardia estava documentado, mas o código só bloqueia por tarefa Celery após expirar a janela de 120 segundos.
* A tela `/join` estava descrita como entrada por PIN/código de sala; atualmente ela apenas navega para `/retro/{code}`.
* A presença REST estava descrita como online/offline; o endpoint retorna participantes, e online/offline é estimado no frontend por eventos WebSocket.
* OAuth estava descrito como não exposto; a UI expõe um botão Google, mas o backend não configura provider Google no settings do repositório.
