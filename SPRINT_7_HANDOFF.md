# Sprint 7 — Handoff

## Estado do repositório
- Branch: main
- Último commit: não registrado nesta sessão
- Migrations pendentes: sim

## O que foi implementado e está funcionando
- Frontend Nuxt 3 SPA inicializado em frontend com Tailwind CSS, Pinia, Heroicons e build de produção validado
- Design system base aplicado com tokens brand/success/warning/danger, fonte Inter, utilitários globais e estados de foco/hover/pressed em frontend/tailwind.config.ts e frontend/assets/css/tailwind.css
- Estrutura principal de UI criada com AppShell, header, footer, sidebar e componentes RetroCard, MilestoneCard, PhaseChip, VoteBadge, TimerDisplay, MilestoneBar, ColumnHeader, FocusCard, ParticipantPanel, CardComposer e ActionItemForm
- Stores e composables adicionados para auth, retrospectiva, participantes, timer, fases e WebSocket em frontend/stores e frontend/composables
- Telas entregues para home/dashboard, login, registro, criação de retrospectiva, invite route, sessão ativa por fases e histórico com detalhe em frontend/pages
- Integração REST implementada para auth, retrospectives, cards, votes, milestones, previous actions, action items e history via frontend/composables/useApiClient.ts e frontend/stores/retro.ts
- Integração WebSocket implementada com JWT via query string, reconexão progressiva e aplicação local de eventos principais em frontend/composables/useWebSocket.ts
- Alerta sonoro do cronômetro implementado com Web Audio API em frontend/utils/sound.ts
- Validação executada com sucesso: cd frontend && npm install && npm run build

## O que foi iniciado e não concluído
- Resolução completa do link de convite por token não foi concluída porque o backend ainda não expõe endpoint para resolver/join por invite token; a tela de invite preserva a rota e documenta a limitação
- Fluxo persistido de avanço de fases continua parcial no backend; o frontend envia phase.advance por WebSocket e permite preview/atualização visual, mas refresh ainda depende do estado persistido do backend
- Reabertura do link de convite e controle de entrada tardia continuam sem endpoint REST dedicado; o painel de participantes mantém o affordance visual e registra a pendência
- OAuth social foi exposto por links padrão do allauth, mas depende de providers configurados em ambiente para funcionar de ponta a ponta
- ESLint/Prettier foram previstos na sprint, porém só o build foi validado nesta sessão; falta fechar configuração explícita e comando dedicado

## Decisões técnicas tomadas nesta sprint
- Frontend foi alinhado explicitamente a Nuxt 3 mesmo após o scaffold inicial gerar template Nuxt 4 minimal -> motivo: cumprir o contrato da Sprint 6/PRD e evitar desvio de stack -> arquivos: frontend/package.json, frontend/nuxt.config.ts, frontend/tsconfig.json
- O app foi mantido em modo SPA com ssr=false -> motivo: a sprint pede SPA e reduz complexidade para auth JWT e sessão em tempo real -> arquivo: frontend/nuxt.config.ts
- O estado da sessão ativa foi centralizado em Pinia com stores separadas para auth, retro, timer e participantes -> motivo: simplificar sincronização entre REST, WebSocket e telas por fase -> arquivos: frontend/stores/*.ts
- O cliente WebSocket usa token JWT na query string -> motivo: aderir ao contrato real do backend em apps/realtime/middleware.py -> arquivo: frontend/composables/useWebSocket.ts
- A rota de invite foi mantida com fallback explícito em vez de inventar resolução local do token -> motivo: o PRD proíbe decisões arquiteturais não previstas e o backend ainda não fornece o endpoint necessário -> arquivo: frontend/pages/retro/invite/[token].vue

## Padrões estabelecidos que devem ser seguidos
- Todo acesso REST autenticado passa por frontend/composables/useApiClient.ts e usa NUXT_PUBLIC_API_BASE como base
- Estado de sessão ativa deve ser atualizado primeiro no store retro e depois refletido pelos componentes, evitando fetchs dispersos por componente
- Timer visual deve continuar sendo derivado de frontend/stores/timer.ts e frontend/composables/useTimer.ts; não duplicar contagem regressiva em componentes
- Tokens visuais devem vir exclusivamente de frontend/tailwind.config.ts e classes utilitárias definidas em frontend/assets/css/tailwind.css
- Qualquer workaround de backend ausente deve ser registrado no handoff; não inventar endpoint ou fluxo silenciosamente

## Próxima sprint: o que deve ser feito
- Fechar o backend de avanço de fases com persistência completa e ajustar o frontend para depender do contrato definitivo em vez de preview local
- Implementar endpoint de invite resolution/join e completar a rota frontend de convite com entrada tardia controlada
- Implementar painel de controle de entrada pós-lobby com bloqueio, reabertura temporária e access log persistido
- Configurar eslint + prettier no frontend e validar com comando dedicado além do build
- Adicionar testes E2E cobrindo auth, create retro, board, voting, discussion, actions e history
- Medir cobertura real de backend e frontend e registrar percentual
- Refinar acessibilidade com foco em navegação por teclado, textos de apoio e estados vazios mais completos

## Comandos para retomar
- docker-compose up -d
- cd backend && python manage.py migrate
- cd backend && python manage.py test
- cd backend && python -m pytest -q tests/realtime/test_presentation_ws.py
- cd backend && python -m ruff check .
- cd frontend && npm install
- cd frontend && npm run build