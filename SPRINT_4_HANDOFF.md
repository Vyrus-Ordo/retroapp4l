# Sprint 4 — Handoff

## Estado do repositório
- Branch: N/A — workspace atual
- Último commit: N/A — workspace atual
- Migrations pendentes: não verificado nesta revisão

## O que foi implementado e está funcionando
- Sprint 4 foi encerrada como backend-first
- API REST de agrupamento concluída com `group` e `ungroup`
- Validação de agrupamento implementada: apenas facilitador, mesma coluna e persistência via `Card.group`
- API REST de votação concluída com `vote`, `vote revoke`, `votes list` e `votes-config`
- Regra de 1 voto por card por participante validada no backend
- Bloqueio de voto no próprio card implementado
- Restrição de voto às colunas `loathed` e `longed` implementada
- Broadcast realtime concluído com eventos `card.grouped`, `card.ungrouped`, `vote.cast` e `vote.revoked`
- Configuração de `max_votes_per_user` atualiza `votes_remaining` dos participantes antes da votação
- Testes do backend passam com `pytest -q` e `python manage.py test`
- Código do backend está conforme Ruff

## O que foi iniciado e não concluído
- Frontend Nuxt 3 ainda não foi iniciado
- MilestoneBar persistente no frontend ficou deferida para a Sprint 6
- Board 4L visual no frontend ficou deferido para a Sprint 6
- UI de agrupamento e votação no frontend ficou deferida para a Sprint 6
- Integração frontend-backend via WebSocket ainda não foi iniciada no cliente
- Aplicação efetiva da máquina de estados ao avanço de fases
- Fluxo completo e persistente de cronômetro com Celery
- Controle de participantes e convites como fluxo completo de produto
- Cobertura mínima de 80% ainda não foi comprovada

## Decisões técnicas tomadas nesta sprint
- Sprint 4 foi mantida como sprint backend-first → interfaces visuais de grouping e voting seguem para Sprint 6 → `docs/sprint/SPRINT_4.md`
- Eventos de agrupamento foram emitidos a partir de mudanças em `Card.group` via signals → `backend/apps/cards/signals.py`
- Eventos de votação foram emitidos a partir de `CardVote` + `Participant.votes_remaining` via signals → `backend/apps/cards/signals.py`
- Configuração de votos foi centralizada em endpoint próprio e sincroniza `votes_remaining` dos participantes → `backend/apps/cards/views.py`

## Padrões estabelecidos que devem ser seguidos
- Manter arquitetura modular, cobertura de testes e conformidade ruff
- Frontend deve seguir rigorosamente o design system do PRD (Tailwind, tokens, Inter, espaçamento 4px)
- Enquanto o frontend não existir, qualquer requisito visual deve ser registrado como deferido, nunca como entregue

## Próxima sprint: o que deve ser feito
- Implementar check de ações anteriores do mesmo `team_key`
- Implementar action items com responsável e prazo
- Implementar fase de discussão/debate e card em foco
- Implementar encerramento da retrospectiva e histórico/dashboard
- Aplicar validação real de transição de fases usando a state machine
- Fechar fluxo do cronômetro com persistência, broadcast e testes dedicados
- Implementar fluxo de convites e entrada de participantes
- Formalizar cobertura mínima e medir percentual real
- Registrar explicitamente no próximo handoff que o frontend continua pendente para Sprint 6

## Comandos para retomar
- docker-compose up -d
- cd backend && python manage.py migrate
- cd backend && pytest
- cd backend && python -m ruff check .
