# Sprint 4 — Handoff

## Estado do repositório
- Branch: N/A — workspace atual
- Último commit: N/A — workspace atual
- Migrations pendentes: não verificado nesta revisão

## O que foi implementado e está funcionando
- Sprint 3 foi encerrada como backend-first
- API REST de cards concluída com create, list, update e delete
- Criação de cards restrita a participantes da retrospectiva
- Broadcast realtime de cards concluído com eventos `card.created`, `card.updated` e `card.deleted`
- API REST de milestones concluída com create, list, update e delete restritos à fase `setup`
- Fluxo de `presentation` no WebSocket concluído com `start`, `next`, `prev`, `end` e auto-skip para `check`
- WebSocket autenticado com JWT via middleware ASGI
- Testes do backend passam com `pytest -q` e `python manage.py test`
- Código do backend está conforme Ruff

## O que foi iniciado e não concluído
- Frontend Nuxt 3 ainda não foi iniciado
- MilestoneBar persistente no frontend ficou deferida para a Sprint 6
- Board 4L visual no frontend ficou deferido para a Sprint 6
- Integração frontend-backend via WebSocket ainda não foi iniciada no cliente
- Aplicação efetiva da máquina de estados ao avanço de fases
- Fluxo completo e persistente de cronômetro com Celery
- Controle de participantes e convites como fluxo completo de produto
- Cobertura mínima de 80% ainda não foi comprovada

## Decisões técnicas tomadas nesta sprint
- Sprint 3 formalizada como backend-first para alinhar com o roadmap do repositório → frontend adiado para Sprint 6 → `docs/sprint/SPRINT_3.md`
- Broadcast de cards passou a cobrir create, update e delete via signals + consumer → `backend/apps/cards/signals.py`, `backend/apps/realtime/consumers.py`
- Criação de cards passou a exigir participação explícita na retrospectiva → `backend/apps/cards/views.py`

## Padrões estabelecidos que devem ser seguidos
- Manter arquitetura modular, cobertura de testes e conformidade ruff
- Frontend deve seguir rigorosamente o design system do PRD (Tailwind, tokens, Inter, espaçamento 4px)
- Enquanto o frontend não existir, qualquer requisito visual deve ser registrado como deferido, nunca como entregue

## Próxima sprint: o que deve ser feito
- Implementar agrupamento por seleção múltipla no backend
- Implementar dot voting restrito a `loathed` e `longed`
- Garantir regra de 1 voto por card por participante
- Emitir eventos realtime necessários para votação e agrupamento
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
