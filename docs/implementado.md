# Documentação de Implementação Atual - RetroApp 4L

> **Última Atualização:** Maio de 2026
> **Objetivo:** Este documento serve como um mapa de referência contínuo sobre o que já foi implementado no projeto RetroApp 4L, facilitando a navegação de agentes de IA e desenvolvedores sem a necessidade de varrer toda a base de código.

---

## 1. Visão Arquitetural

A aplicação segue uma arquitetura separada de **Cliente (Frontend SPA/SSR)** e **Servidor (API REST + WebSockets)**.

*   **Frontend:** Construído com [Nuxt 3](https://nuxt.com/) (Vue 3), gerenciamento de estado via [Pinia](https://pinia.vuejs.org/) e estilos utilitários via [TailwindCSS](https://tailwindcss.com/).
*   **Backend:** Construído em [Django 5.2](https://www.djangoproject.com/) com Django REST Framework (DRF) e [Django Channels](https://channels.readthedocs.io/) para comunicação em tempo real.
*   **Banco de Dados & Cache:** Utiliza PostgreSQL para dados relacionais e Redis tanto como Broker do Celery (para tarefas assíncronas e agendadas) quanto como Channel Layer para WebSockets.
*   **Infraestrutura:** Preparado com Docker (`Dockerfile`, `Dockerfile.worker`, `docker-compose.yml`) e Nginx como reverse proxy.

---

## 2. Backend (Aplicações Django)

O backend (`/backend/apps/`) foi modularizado nos seguintes domínios. A modelagem de dados relacional (PostgreSQL) está distribuída entre eles da seguinte forma:

### Tabelas do Banco de Dados (Models)

*   **`User` (App: users):**
    *   **Campos:** `id` (UUID), `name`, `email`, `public_email`, `oauth_provider`, `oauth_id`, `avatar_url`, `is_guest`, `is_active`, `is_staff`, `created_at`.
    *   **Propósito:** Tabela central de usuários. Diferencia usuários reais de convidados temporários através da flag `is_guest`.
*   **`Retrospective` (App: retrospectives):**
    *   **Campos:** `id` (UUID), `title`, `sprint_name`, `description`, `team_key`, `facilitator` (FK: User), `status` (Enum de fases), `invite_token`, timers e durações (`timer_*`), configurações da sala, `created_at`, `closed_at`.
    *   **Propósito:** O núcleo do sistema, que armazena o status atual e progresso da máquina de estados da reunião.
*   **`Milestone` (App: retrospectives):**
    *   **Campos:** `id`, `retrospective` (FK), `author` (FK: User), `category` (Enum: achievement, challenge, etc.), `description`.
    *   **Propósito:** Conquistas/Marcos celebrados na fase inicial (Check).
*   **`Participant` (App: retrospectives):**
    *   **Campos:** `id`, `retrospective` (FK), `user` (FK: User), `votes_remaining`, `joined_at`. *(Possui Constraint única para Retro + User)*.
    *   **Propósito:** Tabela pivot rastreando quem está na sala e a contagem de votos disponíveis.
*   **`AccessLog` (App: retrospectives):**
    *   **Campos:** `id`, `retrospective` (FK), `action` (Enum), `triggered_by`, `participant`, `timestamp`.
    *   **Propósito:** Histórico de auditoria de ações da sala (abertura, bloqueio de links, etc).
*   **`Card` (App: cards):**
    *   **Campos:** `id`, `retrospective` (FK), `author` (FK: User), `column` (Enum: Loved, Loathed, Longed, Learned), `content`, `group` (Self-FK), `position`.
    *   **Propósito:** Representa os post-its. Suporta agrupamento através da chave estrangeira recursiva `group`.
*   **`CardVote` (App: cards):**
    *   **Campos:** `id`, `card` (FK), `voter` (FK: User). *(Constraint única de Card + User)*.
    *   **Propósito:** Rastreamento atômico de cada voto dado em um cartão para evitar duplicação ou estouro de cota (dependendo da configuração).
*   **`ActionItem` (App: actions):**
    *   **Campos:** `id`, `retrospective` (FK), `card` (FK opcional), `description`, `assignee` (FK: User), `due_date`, `external_tracker_url`, `status` (Enum).
    *   **Propósito:** Itens do Plano de ação gerados após discussão.

### Módulos de Lógica e Funcionalidades

### `users` (Gerenciamento de Usuários e Autenticação)
*   **Autenticação:** Integração com JWT (`djangorestframework-simplejwt`) e `django-allauth` para autenticação.
*   **Convidados (Guests):** Lógica implementada para permitir participantes sem conta logada entrarem via código nas sessões.
*   **Segurança:** Integração com sistema de CAPTCHA/Turnstile (`turnstile.py`).

### `retrospectives` (Core do Domínio)
*   **Modelos e Entidades:** Definição da sessão de retrospectiva principal, controle de acesso e código da sala.
*   **Rotas REST:** APIs para setup, configuração inicial e alteração do status/fases da sessão.

### `realtime` (WebSockets e Sincronização)
*   **Channels & Consumers:** Gerenciamento de conexões ativas (`consumers.py`), presencia de usuários, e broadcasting de eventos.
*   **Máquina de Estados:** Controle restrito sobre o fluxo da reunião através de `state_machine.py`.
*   **Integração Celery:** Tarefas assíncronas em `tasks.py` para processamentos pesados (como expiração de timers, encerramento forçado).
*   **Middleware Customizado:** Camada `middleware.py` intercepta auth nos WebSockets.

### `cards` (Itens do 4L)
*   **Lógica de Negócio:** Criação, edição, movimentação e remoção dos cartões nas 4 colunas (Liked, Loathed, Longed For, Learned).
*   **Eventos Realtime:** O arquivo `signals.py` escuta as mudanças nos models via ORM do Django e propaga mensagens pro channel layer, atualizando a UI de todos.
*   **Votos:** Lógica para distribuição de votos dos participantes.

### `actions` (Itens de Ação)
*   **Registro de Acordos:** Funcionalidade criada para a fase de Discussão, armazenando os próximos passos (Action Items).
*   **Sinais e Websockets:** Integração de `signals.py` para sincronizar os *Action Items* criados na tela de todos.

---

## 3. Frontend (Nuxt 3)

O frontend (`/frontend/`) concentra o fluxo da interface e reatividade local.

### 3.1. Estrutura de Rotas (`pages/`)
*   `index.vue`: Landing Page principal.
*   `login.vue`: Interface de login (Autenticação JWT).
*   `join.vue`: Tela para acesso rápido de participantes a uma sessão (Pin Code).
*   `retro/create.vue`: Fluxo de configuração e criação de uma nova sala de retrospectiva.
*   `retro/[id].vue`: Ambiente principal colaborativo (Workspace) da sessão.
*   `history/index.vue`: Tabela / Dashboard com o histórico de retrospectivas anteriores (`HistoryTable`).

### 3.2. Gerenciamento de Estado Global (`stores/` Pinia)
*   `auth.ts` / `guest.ts`: Controla se o usuário é host autenticado ou convidado temporário.
*   `retro.ts`: Centraliza as informações vitais da sala (fase atual, configurações carregadas via API).
*   `participants.ts`: Gerencia o painel de participantes visíveis, presenças e desconexões (`ParticipantPanel`).
*   `timer.ts`: Sincroniza o relógio em tempo real entre host e participantes.
*   `toast.ts`: Controle global do sistema de notificações (Toasts).

### 3.3. Serviços e Integrações (`composables/`)
*   `useApiClient.ts`: Abstração para chamadas HTTP REST para o Django (com interceptors, JWT injetado, etc.).
*   `useWebSocket.ts`: Hook sofisticado responsável por iniciar a conexão WSS via protocolo do Django Channels, gerenciar reconexões automáticas e emitir/receber os eventos unificados da sala.
*   `usePhase.ts` & `useTimer.ts`: Utilitários isolados para acessar comandos e lógicas recorrentes.

### 3.4. Fluxo de Retrospectiva (Componentes Visuais de `phases/`)
A interface reflete de forma modularizada o estado do `state_machine.py`. Os componentes em `/components/retro/phases/` reagem a qual estágio a sala se encontra, alterando o painel principal (controlados pelo `PhaseStepper` / `PhaseCarousel`):

1.  **`SetupView.vue`**: Configuração da sessão pelo anfitrião.
2.  **`LobbyView.vue`**: Sala de espera onde os participantes aguardam o início.
3.  **`CheckView.vue`**: Primeira fase do fluxo do time.
4.  **`MilestonesView.vue`**: Exibição de milestones.
5.  **`BoardView.vue`**: Fase crucial. Uma prancheta (`BoardGrid`) com 4 colunas simétricas (`ColumnHeader`) para Liked, Loathed, Longed For e Learned, onde ocorrem criações ativas de `RetroCard` usando o `CardComposer`.
6.  **`GroupingView.vue`**: Fase de consolidação e agrupamento de cartões afins.
7.  **`VotingView.vue`**: Os participantes gastam seus votos em itens agrupados ou avulsos (usa `VoteControls` e `VoteBadge`).
8.  **`DiscussionView.vue`**: Apresenta os cartões mais votados no `FocusCard`. Interface acoplada com geração de *Action Items* via `ActionEditor` e `ActionItemForm`.
9.  **`ActionsView.vue`**: Visão em lista revisando todos os compromissos criados na reunião.
10. **`ClosedView.vue`**: Tela de encerramento da sessão com sumário.

---

## 4. Fluxo Detalhado da Sessão (Máquina de Estados)

A aplicação é rigorosamente orientada por uma máquina de estados linear (`state_machine.py` no backend e `usePhase.ts` no frontend) que garante que todos os participantes estejam na mesma página simultaneamente. O fluxo avança unicamente sob o comando do Facilitador.

1.  **`SETUP` (Configuração):** O Facilitador cria a sala. Define opções da reunião (quantos votos por pessoa, se a fase de "Check" será pulada, e se pode votar nos próprios cartões).
2.  **`LOBBY` (Sala de Espera):** Participantes (via link ou código PIN) começam a se conectar. O Facilitador controla o acesso e aguarda o quórum.
3.  **`PRESENTATION` (Abertura):** Momento para dar as boas-vindas e introduzir a sprint ou o tema da retro.
4.  **`CHECK` (Quebra-gelo / Milestones):** Os participantes podem registrar `Milestones` (conquistas, agradecimentos, desafios) que ocorreram na iteração antes do início do quadro. Pode ser pulado através da flag `skip_check_phase`.
5.  **`BOARD` (Brainstorm / Divergência):** A fase principal. O quadro com as 4 colunas (Liked, Loathed, Longed For, Learned) é aberto para livre criação de cartões (`Card`).
6.  **`GROUPING` (Agrupamento / Sintonia):** A criação é bloqueada. O Facilitador junta cartões com assuntos redundantes, formando *clusters* baseados no model `Card` através do campo recursivo `group`.
7.  **`VOTING` (Votação):** Os participantes distribuem sua cota de votos (`CardVote`) nos cartões individuais ou agrupamentos.
8.  **`DISCUSSION` (Convergência):** O sistema ordena os cartões mais votados. O Facilitador foca (`focus_card`) um cartão por vez na tela de todos. Durante o debate de um item, *Action Items* são gerados e atrelados a ele.
9.  **`ACTIONS` (Revisão do Plano):** Revisão de todos os acordos (`ActionItem`). Todos visualizam a lista final do plano de ação construído (tarefas, responsáveis, prazos).
10. **`CLOSED` (Fim):** Sessão é encerrada. O quadro é trancado, o link de convite revogado permanentemente e gravado o `closed_at`.

---

## 5. Convenções e Pontos Chaves Implementados
*   **Confiabilidade de Estado:** O backend atua como a única fonte da verdade (Single Source of Truth). Componentes do Frontend são montados e desmontados passivamente baseados na comunicação WebSocket.
*   **Sistema de Sinais do Django:** Grande parte da magia Real-time está encapsulada nos métodos `post_save` / `post_delete` de `signals.py`, garantindo que modificações feitas em banco sempre espelhem no Channels (via websocket) sem necessidade de acoplamento direto nas `views.py`.
*   **Separação UI / Lógica:** Forte abstração por componentes (`components/layout/`, `components/forms/`) com responsabilidades bem definidas.

---

## 6. Design System & Estilização

O RetroApp 4L não utiliza frameworks de UI em componentes (como Vuetify ou Element), apostando em uma base sólida e customizada com TailwindCSS.

### 6.1. Configuração Tailwind (`tailwind.config.ts`)
*   **Tipografia:** A fonte principal adotada para todo o sistema é **Poppins** (`font-sans`).
*   **Paleta de Cores Customizada:** Foram definidas escalas de 50 a 900 (padrão Tailwind) para cores semânticas exclusivas:
    *   `brand` (Azul principal do produto)
    *   `success` (Verde para feedbacks positivos e aprovações)
    *   `warning` (Laranja/Amarelo para avisos e estados intermediários)
    *   `danger` (Vermelho para destruição e alertas)
    *   `gray` (Escala neutra própria para backgrounds e textos)
*   **Sombras (Elevations):** Definição de sombras semânticas como `shadow-card` e `shadow-card-md` para garantir o visual moderno e "elevado" dos quadros.

### 6.2. Tokens CSS (`assets/css/tokens.css`)
*   Tokens de design baseados em CSS Variables (`--ds-*`) foram implementados para espelhar a configuração do Tailwind.
*   **Aliases Semânticos:** Para simplificar a manutenção, foram criados *aliases* para uso direto no layout e abstrair mudanças futuras de tema:
    *   **Foregrounds (Textos):** `--fg-primary`, `--fg-secondary`, `--fg-tertiary`.
    *   **Backgrounds:** `--bg-canvas` (fundo principal do app), `--bg-surface` (fundo branco de cards), `--bg-primary` e `--bg-secondary`.
    *   **Bordas:** `--border-default` e `--border-strong`.

### 6.3. Ícones e Complementos
*   Utilização intensiva da biblioteca oficial **`@heroicons/vue`** para ícones escaláveis e harmônicos com a tipografia Poppins.
*   O `ColumnHeader` do board utiliza ícones por coluna, contador tabular e botão `Add` compacto no próprio cabeçalho.
*   O layout do board foi refinado para manter os títulos das colunas em linha única, sem `ellipsis` ou quebra de linha, preservando larguras iguais, altura uniforme e alinhamento visual entre as quatro colunas.
*   A distribuição horizontal do workspace foi otimizada com menor gap entre colunas e sidebar de participantes mais compacta, mantendo a identidade dark/neon sem aumentar o tamanho geral do board.
