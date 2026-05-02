# Sprint 6 — Handoff

## Estado do repositório
- Branch: main
- Último commit: 60ccab7 — feat: close sprint 4 backend scope
- Migrations pendentes: sim

## O que foi implementado e está funcionando
- API de action items concluída com CRUD em actions phase: list/create/update/delete em backend/apps/actions/views.py
- Endpoint de ações anteriores por team_key concluído: GET e atualização de status da última retro encerrada em backend/apps/actions/views.py
- Broadcast realtime de check de ações concluído com evento action.check_updated em backend/apps/actions/signals.py e backend/apps/realtime/consumers.py
- Modelo de ActionItem expandido com external_tracker_url e status not_started/in_progress/done em backend/apps/actions/models.py
- Dashboard de histórico backend concluído com resumo por retro encerrada em backend/apps/retrospectives/views.py
- Detalhe de retrospectiva encerrada concluído com cards, votos, marcos e action items em backend/apps/retrospectives/views.py e backend/apps/retrospectives/serializers.py
- Encerramento de sessão concluído com confirmação obrigatória, closed_at, revogação do invite e AccessLog action=closed em backend/apps/retrospectives/views.py
- Debate com card em foco concluído com endpoints focus-card e next-card e evento discussion.focus_updated em backend/apps/retrospectives/views.py e backend/apps/realtime/consumers.py
- Cards passam a expor vote_count e ordenação por votos na fase discussion em backend/apps/cards/views.py e backend/apps/cards/serializers.py
- CRUD de cards fica bloqueado nas fases discussion, actions e closed em backend/apps/cards/views.py
- Testes REST adicionados para actions, histórico, detalhe encerrado, foco de debate e fechamento em backend/apps/actions/tests.py e backend/tests/retrospectives/test_api.py
- Testes realtime adicionados para action.check_updated e discussion.focus_updated em backend/tests/realtime/test_presentation_ws.py
- Validação executada com sucesso: python manage.py test, pytest -q tests/realtime/test_presentation_ws.py e python -m ruff check .

## O que foi iniciado e não concluído
- Frontend Nuxt 3 continua não iniciado; diretório frontend permanece vazio e toda a implementação visual segue para Sprint 6 conforme PRD seção 12.3
- Aplicação explícita da state machine para avanço de fases ainda não foi fechada via endpoint/backend service; a Sprint 5 cobre foco de debate e fechamento, mas não um fluxo completo de advance phase com skip_check_phase
- Persistência completa do cronômetro com pause/resume/extend no backend continua parcial; existem campos de modelo e broadcast websocket, mas não um fluxo REST/Celery fechado de produto
- Fluxo completo de convites e entrada tardia de participantes continua pendente; há apenas os campos de invite no modelo e eventos websocket já existentes
- Cobertura mínima de 80% ainda não foi medida formalmente

## Decisões técnicas tomadas nesta sprint
- ActionItemStatus foi renomeado de pending para not_started para alinhar a API da Sprint 5; migration converte dados existentes e o endpoint ainda aceita pending como alias de compatibilidade → motivo: contrato explícito da Sprint 5 divergia do PRD seção 8 → arquivos: backend/apps/actions/models.py, backend/apps/actions/serializers.py, backend/apps/actions/migrations/0003_actionitem_external_tracker_url_and_status.py
- O card em foco do debate passou a ser persistido em Retrospective.focus_card → motivo: permitir next-card determinístico e consistência de estado entre chamadas REST e WebSocket → arquivos: backend/apps/retrospectives/models.py, backend/apps/retrospectives/views.py, backend/apps/retrospectives/migrations/0003_retrospective_focus_card.py
- O histórico backend foi entregue primeiro, sem frontend, mantendo o padrão backend-first das sprints anteriores → motivo: frontend segue reservado para Sprint 6 no PRD → arquivos: backend/apps/retrospectives/views.py, backend/apps/retrospectives/serializers.py

## Padrões estabelecidos que devem ser seguidos
- Action item usa assignee_id como UUID de Participant na API, mas persiste assignee como User no banco; manter esse contrato nos próximos endpoints
- Qualquer mudança de status em ActionItem que represente check de ações deve emitir action.check_updated pelo group retro_{retrospective_id}
- Qualquer atualização de foco no debate deve emitir discussion.focus_updated com card_id, author, column, content e vote_count
- Validar backend com dois runners: python manage.py test para testes Django e pytest tests/realtime/test_presentation_ws.py para websocket/realtime
- Frontend da Sprint 6 deve seguir rigorosamente a seção 7 do PRD: Tailwind utility-first, tokens do tailwind.config, fonte Inter, escala 4-pt e componentes definidos; nenhuma decisão visual fora disso sem registrar no handoff

## Próxima sprint: o que deve ser feito
- Inicializar o frontend Nuxt 3 com Tailwind e aplicar exatamente o design system da seção 7 do PRD
- Implementar as telas de autenticação, criação de retrospectiva, lobby, apresentação, check, board 4L, agrupamento, votação, debate, ações e histórico
- Consumir os endpoints já entregues nesta sprint para action items, histórico, detalhe encerrado, focus-card e next-card
- Fechar o fluxo backend de avanço de fases usando a state machine e respeitando skip_check_phase com testes dedicados
- Fechar o fluxo backend do cronômetro com pause/resume/extend, persistência e broadcast coerente
- Implementar o fluxo completo de convites e entrada tardia com revogação, reabertura temporária e AccessLog
- Medir cobertura real e registrar percentual no próximo handoff
- Validar com o Tech Lead a divergência entre PRD seção 8 e Sprint 5 sobre pending vs not_started antes de expandir integrações e UI de histórico

## Comandos para retomar
- docker-compose up -d
- cd backend && python manage.py migrate
- cd backend && python manage.py test
- cd backend && python -m pytest -q tests/realtime/test_presentation_ws.py
- cd backend && python -m ruff check .