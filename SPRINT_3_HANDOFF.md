# Sprint 3 — Handoff

## Estado do repositório
- Branch: N/A — workspace atual
- Último commit: N/A — workspace atual
- Migrations pendentes: não verificado nesta revisão

## O que foi implementado e está funcionando
- CRUD REST de cards implementado com create, list, update e delete
- Criação de cards restrita a participantes da retrospectiva
- Regra de autorização para editar e excluir cards aplicada ao autor do card
- Broadcast realtime de cards implementado com eventos de criação, atualização e exclusão
- API REST de milestones implementada com restrição ao facilitador e à fase setup
- Fase presentation implementada no WebSocket com start, next, prev, end e auto-skip para check quando não há milestones
- Autenticação JWT para WebSocket implementada
- Testes automatizados do backend passam na revisão atual com `pytest -q` e `python manage.py test`
- Código do backend está conforme Ruff

## O que foi iniciado e não concluído
- Frontend Nuxt 3 ainda não foi iniciado
- MilestoneBar persistente e contexto visual entre fases foram deferidos para a Sprint 6 por decisão de escopo backend-first
- Cobertura mínima de 80% não está comprovada no repositório

## Decisões técnicas tomadas nesta sprint
- Cards e milestones usam sinais Django para broadcast via Channels
- Navegação da fase presentation foi centralizada no consumer WebSocket

## Padrões estabelecidos que devem ser seguidos
- Manter arquitetura modular, cobertura de testes e conformidade ruff

## Próxima sprint: o que deve ser feito
- Medir cobertura e elevar para o mínimo exigido
- Implementar agrupamento e votação no backend conforme `docs/sprint/SPRINT_4.md`
- Preservar contratos do backend para consumo do frontend na Sprint 6
- Manter registrado no handoff que o frontend segue como trilha deferida

## Comandos para retomar
- docker-compose up -d
- cd backend && python manage.py migrate
- cd backend && pytest -q
- cd backend && python -m ruff check .
