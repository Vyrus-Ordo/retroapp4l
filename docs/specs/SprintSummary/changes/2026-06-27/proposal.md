# Proposal — SprintSummary (2026-06-27)

## Contexto

Facilitadores precisam registrar métricas quantitativas da sprint (histórias planejadas,
concluídas, carry-over) antes de iniciar a fase `setup`. Esses dados são exibidos na fase
`presentation` junto aos milestones, com evolução histórica por `team_key`.

A feature não tem dependências externas: usa apenas o banco existente (PostgreSQL ou SQLite),
os serializers DRF padrão e SVG nativo no frontend (sem biblioteca de gráficos).

## Abordagem técnica

### Backend

1. **Model `SprintSummary`** — OneToOne com `Retrospective`. Campos: `total_stories`,
   `completed`, `carryover` (todos PositiveIntegerField NOT NULL). `delivery_rate` é virtual
   (calculado no serializer). Migration gerada via `makemigrations`.

2. **Dois serializers** — `SprintSummarySerializer` (campos básicos + `delivery_rate`) e
   `SprintSummaryHistorySerializer` (estende com `sprint_name` e `closed_at` da retro).

3. **Duas views** —
   - `SprintSummaryView`: GET/POST/PUT/PATCH em `/api/retrospectives/{id}/sprint-summary/`.
     Usa `get_or_create` para garantir que o objeto exista ao ler. Escrita restrita a
     facilitador + fase `setup`.
   - `SprintSummaryHistoryView`: ListAPIView em `/api/retrospectives/sprint-summary-history/`
     com query param `?team_key=`. Filtra retros `closed` do time ordenadas por `closed_at ASC`.

4. **URLs** — dois paths em `retrospectives/urls.py`. A rota sem `pk`
   (`sprint-summary-history/`) deve ser declarada **antes** de `<uuid:pk>/sprint-summary/`
   para evitar conflito de roteamento.

5. **Admin** — não requerido pela spec; fora do escopo.

### Frontend

1. **Types** — `SprintSummary` e `SprintSummaryHistory` adicionados em `utils/types.ts`
   (onde os outros tipos da store já vivem).

2. **Store `retro.ts`** — dois campos de state (`sprintSummary`, `sprintSummaryHistory`) e
   três actions (`fetchSprintSummary`, `saveSprintSummary`, `fetchSprintSummaryHistory`).
   A action `saveSprintSummary` usa POST conforme spec; o backend faz upsert via
   `get_or_create` + update.

3. **`SprintSummaryForm`** — formulário em `components/forms/`. Três inputs numéricos,
   `delivery_rate` calculado reativo, botão salva via store. Montado em `SetupView`.

4. **`SetupView`** — importa e renderiza `SprintSummaryForm` antes da seção de milestones.
   Busca summary no `onMounted`. Desabilita botão `+ Add Milestone` se `!hasSummary`.

5. **`SprintSummaryCards`** — grid de 4 cards em `components/retro/`. Usado em
   `MilestonesView`.

6. **`SprintSummaryChart`** — SVG nativo sem lib externa. Barra simples (<2 históricos) ou
   polyline (≥2). Ponto atual em losango. Usado em `MilestonesView`.

7. **`MilestonesView`** — busca summary + histórico no `onMounted`, renderiza os dois
   componentes abaixo da grade de milestones quando `sprintSummary` não é null.

### Detalhes de implementação

- A rota `sprint-summary-history/` (sem `<uuid:pk>`) precisa ser registrada ANTES de
  `<uuid:pk>/sprint-summary/` no `urls.py` para que Django não tente fazer parse de
  "sprint-summary-history" como UUID.
- O arquivo `frontend/utils/types.ts` (não `stores/retro.ts`) é onde os tipos TypeScript
  devem ser declarados, seguindo o padrão já existente no projeto.
- `SetupView` recebe `current` e `retroStore` como props já hoje; nenhuma nova prop é
  necessária para acessar `retroStore.sprintSummary`.

## Impacto esperado

### Arquivos criados
| Arquivo | Tipo |
|---|---|
| `backend/apps/retrospectives/migrations/XXXX_add_sprint_summary.py` | Migration (gerada) |
| `frontend/components/forms/SprintSummaryForm.vue` | Componente novo |
| `frontend/components/retro/SprintSummaryCards.vue` | Componente novo |
| `frontend/components/retro/SprintSummaryChart.vue` | Componente novo |

### Arquivos modificados
| Arquivo | Mudança |
|---|---|
| `backend/apps/retrospectives/models.py` | Adicionar class `SprintSummary` |
| `backend/apps/retrospectives/serializers.py` | Adicionar dois serializers |
| `backend/apps/retrospectives/views.py` | Adicionar duas views |
| `backend/apps/retrospectives/urls.py` | Registrar dois endpoints |
| `frontend/utils/types.ts` | Adicionar `SprintSummary` e `SprintSummaryHistory` |
| `frontend/stores/retro.ts` | Adicionar state + 3 actions |
| `frontend/components/retro/phases/SetupView.vue` | Integrar SprintSummaryForm |
| `frontend/components/retro/phases/MilestonesView.vue` | Integrar Cards + Chart |

## Fora do escopo

- Registro de `SprintSummary` no Django Admin
- Edição de `SprintSummary` após fase `setup` (bloqueado por regra de negócio)
- Exibição de `SprintSummary` na tela de histórico (`history/[id].vue`)
- Atualização dos arquivos de documentação (`data-model.md`, `PRD.md`, `project-status.md`,
  `frontend-design.md`) — listados na spec seção 15 como pós-implementação
- Testes automatizados (não há testes existentes para retrospectives views a seguir como modelo
  nesta sessão)
