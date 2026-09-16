# Tasks — SprintSummary (2026-06-27)

## Status: ✅ Concluído

## Tasks

### Backend

- [x] **B1** — Adicionar class `SprintSummary` em `backend/apps/retrospectives/models.py`
      (OneToOne com Retrospective, campos `total_stories`, `completed`, `carryover`, timestamps)

- [x] **B2** — Migration criada manualmente em `0007_add_sprint_summary.py`
      (Docker não estava rodando; migration escrita à mão com base no formato existente)

- [x] **B3** — Adicionar `SprintSummarySerializer` em `backend/apps/retrospectives/serializers.py`
      (campos básicos + `delivery_rate` como SerializerMethodField)

- [x] **B4** — Adicionar `SprintSummaryHistorySerializer` em `backend/apps/retrospectives/serializers.py`
      (estende B3 com `sprint_name` e `closed_at`)

- [x] **B5** — Adicionar `SprintSummaryView` em `backend/apps/retrospectives/views.py`
      (GET/POST/PUT/PATCH, `get_or_create`, validação facilitador + fase `setup`)

- [x] **B6** — Adicionar `SprintSummaryHistoryView` em `backend/apps/retrospectives/views.py`
      (ListAPIView, query param `?team_key=`, filtra `closed` do time, ordena por `closed_at`)

- [x] **B7** — Registrar endpoints em `backend/apps/retrospectives/urls.py`
      (`sprint-summary-history/` ANTES de `<uuid:pk>/sprint-summary/`)

### Frontend

- [x] **F1** — Adicionar interfaces `SprintSummary` e `SprintSummaryHistory` em `frontend/utils/types.ts`

- [x] **F2** — Adicionar state `sprintSummary` e `sprintSummaryHistory` em `frontend/stores/retro.ts`
      (atualizar `RetroState` e `state()`)

- [x] **F3** — Adicionar actions `fetchSprintSummary`, `saveSprintSummary`, `fetchSprintSummaryHistory`
      em `frontend/stores/retro.ts`

- [x] **F4** — Criar `frontend/components/forms/SprintSummaryForm.vue`
      (3 inputs numéricos, `delivery_rate` computed, botão salva via store, loading state, toast)

- [x] **F5** — Criar `frontend/components/retro/SprintSummaryCards.vue`
      (grid 4 colunas / 2 mobile, 4 cards: Total Sprint / Concluídas / Carry-over / Taxa de Entrega)

- [x] **F6** — Criar `frontend/components/retro/SprintSummaryChart.vue`
      (barra progresso se history.length < 2; polyline SVG nativo se ≥ 2; ponto atual como losango)

- [x] **F7** — Modificar `frontend/components/retro/phases/SetupView.vue`
      (fetchSprintSummary no onMounted, renderizar SprintSummaryForm, desabilitar Add Milestone sem summary)

- [x] **F8** — Modificar `frontend/components/retro/phases/MilestonesView.vue`
      (fetchSprintSummary + fetchSprintSummaryHistory no onMounted, renderizar Cards + Chart abaixo dos milestones)

## Notas de execução

- Migration criada manualmente (0007_add_sprint_summary.py) pois Docker estava offline.
  Rodar `python manage.py migrate` dentro do container ao subir o ambiente.
- `SetupView` reestruturada: facilitador agora vê SprintSummaryForm + seção de milestones
  + "Go to Lobby"; participante mantém a view de espera com avatares.
- `sprint-summary-history/` registrada antes de `<uuid:pk>/sprint-summary/` nas URLs
  para evitar conflito de roteamento (embora `sprint-summary-history` não seja UUID válido).
- `useRetroStore` e `useToastStore` usados sem import explícito nos .vue files
  (auto-import Nuxt 3).

## Fora do escopo identificado durante execução

- Wiring do botão "Add Milestone" no SetupView: botão emite `add-milestone` mas o pai
  (`retro/[id].vue`) não tem handler para isso ainda. A criação de milestones na fase setup
  via UI do workspace fica como work-to-do separado.
