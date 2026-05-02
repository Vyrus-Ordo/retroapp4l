# Análise de Implementação — Sprint 3 e Sprint 4

## Escopo avaliado

Documentos analisados:
- `SPRINT_3_HANDOFF.md`
- `docs/sprint/SPRINT_3.md`
- `SPRINT_4_HANDOFF.md`

Evidências usadas:
- código-fonte em `backend/apps/**`
- testes em `backend/tests/**` e `backend/apps/**/tests.py`
- validação executada com `pytest -q` e `ruff check .`

## Resumo executivo

O backend possui parte relevante da Sprint 3 implementada: CRUD REST de cards, CRUD REST de milestones, autenticação JWT para WebSocket e fluxo básico da fase `presentation` com navegação entre milestones.

Os handoffs originais superestimavam o estado do projeto. Após os ajustes desta revisão, o backend passou a ficar conforme Ruff e as lacunas de cards no WebSocket foram fechadas, mas ainda não é correto afirmar que o backend realtime está completo, que há cobertura comprovada maior ou igual a 80%, ou que links de convite e controle de participantes estão entregues de ponta a ponta.

## Matriz de status

| Item | Documento | Status | Evidência | Observação |
|---|---|---|---|---|
| CRUD REST de cards | Sprint 3 | Desenvolvido | `backend/apps/cards/views.py`, `backend/apps/cards/tests.py` | Create, list, update e delete existem com testes básicos |
| Limite de 500 caracteres em cards | Sprint 3 | Desenvolvido | `backend/apps/cards/serializers.py`, `backend/apps/cards/tests.py` | Validação implementada |
| Somente autor pode editar/excluir card | Sprint 3 | Desenvolvido | `backend/apps/cards/views.py`, `backend/apps/cards/tests.py` | Regra aplicada nas views |
| Somente participantes podem criar cards | Sprint 3 | Desenvolvido | `backend/apps/cards/views.py`, `backend/apps/cards/tests.py` | Há checagem explícita de participação com teste cobrindo o bloqueio |
| Broadcast realtime de card.created | Sprint 3 | Desenvolvido | `backend/apps/cards/signals.py`, `backend/apps/realtime/consumers.py` | Fluxo existe |
| Broadcast realtime de card.updated | Sprint 3 | Desenvolvido | `backend/apps/cards/signals.py`, `backend/apps/realtime/consumers.py`, `backend/tests/realtime/test_presentation_ws.py` | Fluxo validado por teste de WebSocket |
| Broadcast realtime de card.deleted | Sprint 3 | Desenvolvido | `backend/apps/cards/signals.py`, `backend/apps/realtime/consumers.py`, `backend/tests/realtime/test_presentation_ws.py` | Fluxo validado por teste de WebSocket |
| API REST de milestones | Sprint 3 | Desenvolvido | `backend/apps/retrospectives/views.py`, `backend/tests/retrospectives/test_api.py` | Create, list, update e delete com restrição de fase setup |
| Broadcast realtime de milestone.created | Sprint 3 | Desenvolvido | `backend/apps/retrospectives/signals.py`, `backend/apps/realtime/consumers.py` | Handler existe no consumer |
| Broadcast realtime de milestone.updated/deleted | Sprint 3 | Desenvolvido | `backend/apps/retrospectives/signals.py`, `backend/apps/realtime/consumers.py` | Existe, embora não estivesse explícito no escopo mínimo |
| Fase presentation com navegação | Sprint 3 | Desenvolvido | `backend/apps/realtime/consumers.py`, `backend/tests/realtime/test_presentation_ws.py` | Start, next, prev e end implementados |
| Auto-skip de presentation para check sem milestones | Sprint 3 | Desenvolvido | `backend/apps/realtime/consumers.py` | Implementado no evento `milestone.presentation.start` |
| Milestones visíveis em todas as fases via MilestoneBar | Sprint 3 | Não desenvolvido | `frontend/` | Frontend está vazio |
| Estado/snapshot inicial da sessão no WebSocket | Sprint 4 handoff | Parcial | `backend/apps/realtime/consumers.py` | Snapshot é estático e não carrega estado persistido real |
| JWT para WebSocket | Sprint 3/4 handoff | Desenvolvido | `backend/apps/realtime/middleware.py`, `backend/config/asgi.py` | Middleware existe e está ligado ao ASGI |
| Máquina de estados aplicada ao fluxo | Sprint 4 handoff | Parcial | `backend/apps/realtime/state_machine.py`, `backend/apps/realtime/consumers.py` | Estrutura existe, mas não é usada para validar `phase.advance` |
| Cronômetro com Celery | Sprint 4 handoff | Parcial | `backend/apps/realtime/tasks.py`, `backend/tasks/timer.py` | Há task de broadcast e configuração Celery, mas falta fluxo completo e persistência coerente |
| Controle de participantes | Sprint 4 handoff | Parcial | `backend/apps/retrospectives/models.py`, `backend/apps/realtime/consumers.py` | Modelo existe e há eventos WS, mas falta fluxo de entrada/controle completo |
| Links de convite | Sprint 4 handoff | Parcial | `backend/apps/retrospectives/models.py`, `backend/apps/retrospectives/serializers.py` | Campos existem, mas não há endpoints/fluxo completos de convite |
| Testes automatizados do backend | Sprint 3/4 handoff | Desenvolvido | execução local de `pytest -q` e `python manage.py test` | `pytest -q` passou com 16 testes; `manage.py test` passou com 15 testes |
| Cobertura >= 80% | Sprint 3/4 handoff | Não comprovado | `pytest.ini`, `pyproject.toml` | Não há configuração nem relatório de cobertura no repositório |
| Código conforme Ruff | Sprint 3/4 handoff | Desenvolvido | execução local de `ruff check .` | Todas as verificações passaram após os ajustes |

## Lacunas principais para os handoffs virarem verdadeiros

1. Integrar a máquina de estados ao fluxo de mudança de fase.
2. Fechar o cronômetro ponta a ponta com persistência e testes dedicados.
3. Implementar fluxo real de convites e entrada de participantes.
4. Criar o frontend da `MilestoneBar` e a integração WebSocket correspondente.
5. Adicionar medição de cobertura e provar o mínimo exigido.

## Validações executadas nesta revisão

- `pytest -q`: 16 testes passaram
- `python manage.py test`: 15 testes passaram
- `ruff check .`: todas as verificações passaram
