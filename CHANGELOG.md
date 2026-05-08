# Changelog

Todas as mudanças notáveis neste projeto são documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [Não lançado]

### Adicionado
- Documentação de implementação (`docs/implementado.md`) com mapa de referência da base de código
- Suporte a cards anônimos com campo `is_anonymous`, migration retrocompatível, serialização pública mascarada e autoria real preservada no backend
- Opção `Add anonymously` no modal de criação/edição de cards
- Foco automático no campo de descrição ao abrir o modal de novo card pelo board

### Alterado
- Refinamento responsivo do board 4L para manter títulos de colunas em linha única, com colunas simétricas e sem truncamento
- Compactação discreta dos headers das colunas, botão `Add`, contador, espaçamento horizontal e sidebar de participantes para preservar a estética dark/neon
- Payloads REST e WebSocket de cards/foco de discussão agora respeitam anonimato visual, retornando `Anonymous` como exibição pública
- Permissões visuais de edição/exclusão de cards passaram a usar `can_edit` em vez de depender da exposição do autor na UI
- Documentação (`docs/PRD.md` e `docs/implementado.md`) atualizada com regras de anonimato, serialização, UI, WebSocket e histórico
- Agrupamento de cards agora é preservado visualmente nas fases de votação e discussão, com filhos renderizados como sub-itens do card pai e suporte ao alias público `group_parent_id`

---

## [0.9.0] - 2026-05

### Adicionado
- Componente `FocusCard` para exibição de cartão em destaque durante a fase de discussão
- Componente `CardComposer` para criação e edição de cartões no board
- Integração Cloudflare Turnstile no endpoint de registro para proteção contra bots
- Suporte a argumento de build `NUXT_PUBLIC_TURNSTILE_SITE_KEY` no Docker

### Alterado
- Redesign da landing page com nova seção hero e imagem de fundo
- Refatoração do `Header` e `Footer` com melhor layout e suporte a mobile
- Labels e textos da interface migrados para inglês
- Ícone de favicon atualizado para identidade visual aprimorada

---

## [0.8.0] - 2026-04

### Adicionado
- Configuração de ambiente de produção com Docker Compose, Nginx e suporte a SSL
- Pipeline CI/CD, ESLint, Prettier e setup de testes E2E com Playwright
- Sistema de toasts globais (`stores/toast.ts`) para notificações de UI
- Painel de presença de participantes (`ParticipantPanel`)
- Controle de status do link de convite (abrir/bloquear) pelo facilitador
- Tarefa Celery para bloqueio automático de convites após o início da sessão
- Funcionalidade de logout com atualização da interface no header

### Alterado
- Componente `AppShell` refatorado com forwarding de slot `#timer` para `RetroHeader`
- Navegação redirecionada para a página de histórico ao encerrar uma sessão

---

## [0.7.0] - 2026-03

### Adicionado
- Funcionalidade de convite público: endpoint `GET /api/invites/{token}/` e `POST /api/invites/{token}/join/`
- Suporte a usuário convidado (guest): criação/reaproveitamento de conta guest via token de convite
- Flag `is_guest` e campo `public_email` no modelo `User`; `display_email` exposto no serializer
- Store `guest.ts` no frontend para persistência de identidade de convidado
- Geração e backfill de `invite_token` em retrospectivas ativas
- Eventos WebSocket `participant.joined` e `participant.left` para presença em tempo real
- Parâmetro `enabled` no composable `useWebSocket` para controle do estado da conexão
- Funcionalidade de refresh de token JWT no `authStore`

### Alterado
- Middleware do frontend atualizado: convidado permitido apenas em rotas públicas e `/retro/*`
- Hidratação de participantes refatorada no store `participants.ts`

---

## [0.6.0] - 2026-02

### Adicionado
- Timer de fases com durações configuráveis por sessão (`phase_durations` no modelo e serializer)
- Sincronização de cronômetro em tempo real entre facilitador e participantes via WebSocket
- Eventos WebSocket: `timer.pause` / `timer.resume` (cliente) e `timer.paused` / `timer.resumed` / `timer.sync` / `timer.expired` (servidor)
- `TimerDisplay` no `RetroHeader` visível nas fases cronometradas
- Tarefa Celery `timer_sync_task` com auto-agendamento via `apply_async(countdown=5)`
- Migration `0006_add_phase_durations.py`

### Adicionado (UI)
- Componentes `ActiveSessionCard` e `HistoryTable` na página inicial
- Funcionalidade de agrupamento de cartões (`group` self-FK no modelo `Card`)
- Componente `BoardGrid` integrado em múltiplas fases
- Lógica de votação com flag `allow_self_vote` e controle de cota de votos
- Componente `DiscussionView` redesenhado com layout aprimorado
- Funcionalidade de avançar fase persistida no backend (`persist_phase_advance`)

---

## [0.5.0] - 2026-01

### Adicionado
- Backend de encerramento do ciclo de sprint (fase `closed`)
- Endpoints REST para `ActionItem`: criação, listagem e atualização de status
- Componentes de frontend para as fases de ação e discussão
- Broadcast WebSocket para `ActionItem` criado/atualizado via `signals.py`
- Verificação de permissão de facilitador nas operações de `ActionItem`
- Formulários de login e registro com validação e tratamento de erros aprimorados

---

## [0.4.0] - 2025-12

### Adicionado
- Escopo backend completo da Sprint 4: modelos `Card`, `CardVote` e `ActionItem`
- Signals Django para propagação de eventos de cartão via Channel Layer
- App `realtime` com `consumers.py`, `state_machine.py`, `middleware.py` e `tasks.py`
- Máquina de estados para controle do fluxo de fases da retrospectiva
- Middleware de autenticação WebSocket via query param ou header `Authorization`

---

## [0.3.0] - 2025-11

### Adicionado
- Escopo backend completo da Sprint 3: modelos `Participant`, `Milestone` e `AccessLog`
- API REST para criação e listagem de participantes
- Facilitador adicionado automaticamente como `Participant` ao criar uma retrospectiva
- Serializers com validação de negócio para `Retrospective` e `Participant`

---

## [0.2.0] - 2025-10

### Adicionado
- Frontend Nuxt 3 com TailwindCSS, Pinia e Heroicons
- Rotas principais: `/`, `/login`, `/join`, `/retro/create`, `/retro/[id]`, `/history`
- Composables `useApiClient`, `useWebSocket`, `usePhase`, `useTimer`
- Middleware global de autenticação protegendo rotas privadas
- Suporte Docker para o serviço frontend
- Coleção Insomnia exportada para testes da API

---

## [0.1.0] - 2025-09

### Adicionado
- Estrutura inicial do projeto Django 5.2 com Django REST Framework
- Configuração de settings por ambiente (`base`, `local`, `production`)
- Modelo `User` customizado com UUID, OAuth fields e flag `is_guest`
- Modelo `Retrospective` com máquina de estados de fases e `invite_token`
- Autenticação JWT via `djangorestframework-simplejwt`
- Suporte a autenticação social via `django-allauth`
- Docker Compose com serviços: `backend`, `worker` (Celery), `db` (PostgreSQL), `redis`
- Configuração de Celery e Celery Beat para tarefas assíncronas
- Django Channels com Redis Channel Layer para WebSockets
- Dockerfile separado para worker Celery (`Dockerfile.worker`)
- README com informações do projeto e instruções Docker

[Não lançado]: https://github.com/diniz-prj/retroapp4l/compare/v0.9.0...HEAD
[0.9.0]: https://github.com/diniz-prj/retroapp4l/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/diniz-prj/retroapp4l/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/diniz-prj/retroapp4l/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/diniz-prj/retroapp4l/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/diniz-prj/retroapp4l/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/diniz-prj/retroapp4l/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/diniz-prj/retroapp4l/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/diniz-prj/retroapp4l/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/diniz-prj/retroapp4l/releases/tag/v0.1.0
