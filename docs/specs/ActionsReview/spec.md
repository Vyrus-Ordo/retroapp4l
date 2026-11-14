# Spec — Actions Review (área de revisão de ações do time)

**Feature:** Página `/actions` que lista, em tabela, todas as ações dos times do usuário, com filtros, e permite ao
facilitador editar as ações de retros já fechadas
**Data:** 2026-11-14
**Status:** Aprovada pelo dono em 2026-11-14 (inclui as premissas A a F como estão)

---

## Decisões do dono (fixas)

| # | Decisão |
|---|---|
| 1 | Ações só nascem dentro de uma retro, como hoje. **Não há criação fora de retro**; o modelo não muda (`ActionItem.retrospective` continua obrigatório, sem `team_key` novo). |
| 2 | **Somente o facilitador** altera ações. Os demais participantes apenas leem. |
| 3 | **Sem exclusão** nesta fase. |
| 4 | Visão padrão: **todos os meus times juntos**, com filtro por time, mostrando **só as pendentes** (`not_started` e `in_progress`). |

Consequência: o "CRUD completo" pedido na ideia vira, na prática, **listar + ler + editar (RU)**. Criar e excluir ficam
fora por decisão, e a spec não deixa nenhum ponto de extensão para eles.

---

## Premissas assumidas (confirmar na aprovação)

| # | Premissa | Alternativa se não concordar |
|---|---|---|
| A | **Ler** exige ser facilitador ou participante de ao menos uma retro do mesmo `team_key`. Convidados (`is_guest`) não acessam. | Restringir a leitura também ao facilitador. |
| B | **Editar** exige ser **facilitador de ao menos uma retro do mesmo `team_key`** (papel de time), não só da retro de origem da ação. | Restringir ao facilitador da retro de origem. |
| C | Só é possível editar ações de retros **fechadas**. Ações de retro em andamento aparecem na lista, somente leitura, com o selo "Retro in progress", porque a edição ao vivo já tem fluxo próprio (fases `discussion` e `actions`, com WebSocket) e uma segunda porta de escrita criaria conflito. | Permitir editar também as de retro ativa. |
| D | Campos editáveis: `description`, `assignee`, `due_date`, `status`, `external_tracker_url`. Não editáveis: `card` e `retrospective`. | Reduzir a lista (ex.: só status, prazo e responsável). |
| E | O responsável (`assignee`) continua sendo um **participante da retro de origem** da ação, como hoje (`assignee_id` = id do `Participant`). Quem entrou no time depois não pode ser escolhido para ações antigas. | Permitir qualquer usuário que tenha participado do time (exige nova regra de validação). |
| F | Sem trilha de auditoria nesta fase. Sem exclusão e com `status_updated_at` já existente, o risco é baixo; a auditoria fica como evolução. | Adicionar `updated_at`/`updated_by` agora. |

---

## 1. Contexto e encaixe com o que já existe

- A fase `check` já mostra pendências de todas as retros fechadas do time (`GET .../previous-actions/`). A Actions Review é a
  **visão persistente e fora da retro** desses mesmos dados.
- Marcar uma ação como `done` por aqui atualiza `status_updated_at` (signal `pre_save` existente), então passa a alimentar
  a seção "Concluídos desde a última retro" da fase Check. Isso remove a limitação de que só dava para concluir ações dentro
  de uma retro ao vivo.
- **Anonimato:** a ação só expõe `card` (id). A listagem **não** inclui conteúdo nem autor do card relacionado, para não
  vazar autoria de card anônimo.
- Não há entidade `Team`; "time" continua sendo o `team_key` das retros.

---

## 2. Backend — regras de acesso (módulo novo `backend/apps/actions/review.py`)

Funções auxiliares (queries em `Retrospective`/`Participant`):

```python
def readable_team_keys(user):      # facilitador OU participante de >=1 retro do team_key
def editable_team_keys(user):      # facilitador de >=1 retro do team_key
```

- Usuário convidado (`user.is_guest`) → `PermissionDenied` em todos os endpoints novos.
- Uma ação cujo `team_key` não está em `readable_team_keys(user)` responde **404** (não revela existência).
- Edição de ação cujo `team_key` está em readable mas não em editable → **403**.
- Edição de ação cuja retro **não** está `closed` → **403** com mensagem "Edit this action inside the retrospective".

---

## 3. Backend — endpoints (prefixo `/api/`, em `backend/apps/actions/urls.py`)

| Método | URL | Descrição |
|---|---|---|
| `GET` | `/api/actions/` | Lista paginada das ações dos times legíveis pelo usuário |
| `GET` | `/api/actions/teams/` | Times do usuário com contagens, para o filtro |
| `GET` | `/api/actions/{id}/` | Detalhe da ação + `assignee_options` (participantes da retro de origem) |
| `PATCH` | `/api/actions/{id}/` | Edição parcial (somente campos da premissa D) |

`POST` e `DELETE` **não existem** (resposta `405`). `PUT` também não é exposto; só `PATCH`. Registrar `actions/teams/`
antes de `actions/<uuid:action_id>/`.

### 3.1 `GET /api/actions/`

Query params (todos opcionais):

| Param | Comportamento |
|---|---|
| `team_key` | Um ou mais (`?team_key=a&team_key=b`). Sem o param: todos os times legíveis. Valor fora dos legíveis é ignorado. |
| `status` | Um ou mais de `not_started`, `in_progress`, `done`. **Sem o param, o backend não filtra**; o frontend envia `not_started&in_progress` como padrão da tela. |
| `assignee` | Id do **usuário**; ou `me` para as minhas. |
| `overdue` | `true` → `due_date < hoje` e `status != done`. |
| `due_before`, `due_after` | Datas `YYYY-MM-DD` (inclusivas). |
| `q` | Busca textual (`icontains`) em `description`. |
| `ordering` | `due_date` (padrão), `-due_date`, `status_updated_at`, `-status_updated_at`, `created_at`, `-created_at`. Em `due_date`, nulos por último. Desempate estável por `retrospective__closed_at`, `created_at`, `id`. |
| `page`, `page_size` | Paginação por página. Padrão 25, máximo 100. |

Resposta (paginação `PageNumberPagination` própria da view, já que o projeto não tem paginação global):

```json
{
  "count": 42, "next": "...", "previous": null,
  "results": [
    {
      "id": "uuid",
      "description": "…",
      "status": "in_progress",
      "status_updated_at": "2026-11-14T10:00:00Z",
      "due_date": "2026-11-20",
      "is_overdue": false,
      "external_tracker_url": "",
      "assignee_name": "Maria",
      "assignee_user_id": "uuid",
      "assignee_participant_id": "uuid",
      "retrospective": {
        "id": "uuid", "title": "Sprint 12", "sprint_name": "S12",
        "team_key": "platform", "status": "closed", "closed_at": "2026-11-01T18:00:00Z"
      },
      "can_edit": true
    }
  ]
}
```

- `can_edit` = premissa B **e** premissa C (retro fechada), calculado por usuário.
- `assignee_participant_id` = id do `Participant` do responsável atual **na retro de origem** (mesmo valor que
  `ActionItemSerializer.participant_id` já expõe hoje; `null` se o responsável não tiver mais registro de participante).
  Existe para o modal de edição pré-selecionar o responsável sem casar por nome (homônimos). *Emenda de 2026-11-14,
  descoberta na implementação do frontend.*
- Evitar N+1: `select_related("assignee", "retrospective")` e calcular `can_edit` com os conjuntos
  `editable_team_keys` computados uma vez por request (passados no contexto do serializer).

### 3.2 `GET /api/actions/teams/`

```json
[{ "team_key": "platform", "pending": 5, "total": 12, "can_edit": true }]
```

`pending` = `not_started` + `in_progress`. `can_edit` = o usuário é facilitador de alguma retro do time. Ordenado por
`team_key`.

### 3.3 `GET /api/actions/{id}/`

Mesmo objeto da lista, mais:

```json
"assignee_options": [{ "participant_id": "uuid", "name": "Maria" }]
```

(participantes da retro de origem; usados pelo modal de edição).

### 3.4 `PATCH /api/actions/{id}/`

Campos aceitos: `description`, `assignee_id` (id de `Participant` **da retro de origem**), `due_date` (aceita `null`),
`status`, `external_tracker_url`. Outros campos são ignorados (`card`, `retrospective`, `id`).

Validações:
- `description`: obrigatória e não vazia se enviada.
- `assignee_id`: precisa ser `Participant` da retro de origem; senão `400 {"assignee_id": "Assignee must be a participant in this retrospective."}`.
- `status`: um dos três valores (sem o alias legado `pending`).
- Reaproveitar `ActionItemSerializer` onde possível; não duplicar a regra de `assignee_id`.

Efeitos:
- O `post_save` existente continua disparando `action_updated` (e `action_check_updated` se o status mudou) para o grupo da
  retro de origem. Como a retro está fechada, não há conexões WebSocket ativas; o comportamento é inofensivo.
- `status_updated_at` é mantido pelo `pre_save`; **não** usar `save(update_fields=[...])` sem incluir `status_updated_at`.

---

## 4. Frontend

### 4.1 Rota, menu e guarda
- Nova página `frontend/pages/actions/index.vue`.
- Link **"Actions Review"** em `frontend/components/layout/AppHeader.vue`, visível apenas quando `isAuthenticatedUser`,
  ao lado de "History".
- Nenhuma mudança em `middleware/auth.global.ts`: `/actions` não é público e convidados já são redirecionados para `/join`.

### 4.2 Store `frontend/stores/actionsReview.ts` (Pinia)
Estado: `items`, `count`, `page`, `pageSize`, `teams`, `filters` (`teamKeys`, `statuses`, `assignee`, `overdue`,
`dueBefore`, `dueAfter`, `q`, `ordering`), `loading`, `error`, `selected` (detalhe + `assignee_options`).
Ações: `fetchTeams()`, `fetchActions()`, `fetchDetail(id)`, `updateAction(id, patch)` (substitui o item na lista com a
resposta), `resetFilters()`.
Padrão ao abrir: `statuses = ['not_started', 'in_progress']`, `teamKeys = []` (todos), `ordering = 'due_date'`.

### 4.3 Componentes (`frontend/components/actions/`)
- `ActionsReviewFilters.vue`: seletor múltiplo de times (com contagem de pendentes vinda de `/teams/`), chips de status,
  "Só minhas", "Atrasadas", intervalo de prazo, busca, ordenação; botão "Limpar filtros".
- `ActionsReviewTable.vue`: **lista de cartões em largura total** (decisão do dono em 2026-11-14, após teste no browser: a
  tabela de 7 colunas espremia a descrição, que é o texto mais longo). Cada ação ocupa 2 linhas: linha 1 =
  `description` completa com quebra de linha + badge de status (+ vermelho para atrasadas); linha 2 = metadados
  discretos inline (time · retro com link para `/history/{id}` quando fechada · responsável · prazo · atualizado em) +
  botão "Edit" (só se `can_edit`) + selo "Retro in progress" quando a retro não está fechada. A ordenação fica só nos
  filtros (sem cabeçalho clicável); paginação como especificado. Em telas estreitas o cartão já é esse layout.
- `ActionEditModal.vue`: formulário com os 5 campos editáveis; `assignee` como select com `assignee_options`;
  mostra erro do servidor; toast de sucesso (`stores/toast.ts`). Avaliar reuso de `components/retro/ActionEditor.vue`
  antes de criar do zero; se o acoplamento à retro ativa for grande, criar o modal novo.
- Estados: carregando, vazio ("No actions match these filters."), erro de rede com retry.

### 4.4 Tipos (`frontend/utils/types.ts`)
`ActionReviewItem`, `ActionReviewTeam`, `ActionReviewPage`, `ActionReviewDetail` conforme os JSONs acima.

### 4.5 Responsividade e visual
Seguir o design system existente (`panel`, `field-input`, `button-primary`/`button-secondary`, tokens `--ds-*`).
Em telas estreitas a tabela vira lista de cartões empilhados (mesmas informações).

---

## 5. Regras de negócio consolidadas

| Regra | Detalhe |
|---|---|
| Origem das ações | Somente criadas em retro (sem criação nova, sem exclusão) |
| Leitura | Facilitador ou participante de ao menos uma retro do `team_key`; convidado nunca |
| Edição | Facilitador de ao menos uma retro do `team_key`, e apenas ações de retro `closed` |
| Visibilidade de existência | Ação de time fora do alcance do usuário → 404 |
| Padrão da tela | Todos os meus times, só `not_started` e `in_progress`, ordenado por prazo |
| Atrasada | `due_date < hoje` e `status != done` |
| Concluir por aqui | Atualiza `status_updated_at` e alimenta "Concluídos desde a última retro" |
| Anonimato | Sem conteúdo/autor do card na listagem |
| Responsável | Participante da retro de origem |

---

## 6. Testes

**Backend** (`backend/tests/actions/test_actions_review.py`, convenção `test_*.py` da suíte canônica):
- Acesso: usuário sem relação com o time recebe lista vazia e 404 no detalhe; convidado recebe 403; participante lê e
  recebe 403 ao editar; facilitador de **outro** time recebe 404/403; facilitador do time edita ação de retro fechada.
- Edição de ação de retro **ativa** → 403; campos não editáveis (`card`, `retrospective`) ignorados; `assignee_id` de
  outra retro → 400; `due_date: null` limpa o prazo; `POST`/`DELETE`/`PUT` → 405.
- Filtros: `team_key` único e múltiplo, `status`, `assignee=me`, `overdue`, `due_before/after`, `q`, `ordering` (nulos
  por último, desempate estável), paginação (`page_size` máx. 100).
- `/teams/`: contagens `pending` e `total` e `can_edit`.
- Efeitos: marcar `done` atualiza `status_updated_at` e a ação aparece em `recently_completed` da fase Check de uma retro
  seguinte do mesmo time.
- Anonimato: payload não contém conteúdo nem autor do card.
- Queries: número de queries da listagem não cresce com o número de itens (`assertNumQueries` com tolerância fixa).

**Frontend/e2e** (`frontend/e2e/actions-review.spec.ts`): rota protegida redireciona para login quando anônimo; usuário
autenticado vê a página, o estado vazio e o link no menu. Cobertura de dados reais (tabela, edição) fica no backend e na
validação manual do dono, porque o e2e atual não semeia retros fechadas.

---

## 7. Arquivos a criar/modificar

| Arquivo | Mudança |
|---|---|
| `backend/apps/actions/review.py` | Novo: helpers de acesso, filtros, serializers de revisão, paginação e views |
| `backend/apps/actions/urls.py` | Registrar `actions/`, `actions/teams/`, `actions/<uuid>/` |
| `backend/tests/actions/test_actions_review.py` | Novo |
| `frontend/pages/actions/index.vue` | Novo |
| `frontend/stores/actionsReview.ts` | Novo |
| `frontend/components/actions/*.vue` | Novos (filtros, tabela, modal) |
| `frontend/components/layout/AppHeader.vue` | Link "Actions Review" |
| `frontend/utils/types.ts` | Tipos novos |
| `frontend/e2e/actions-review.spec.ts` | Novo |

**Sem migration** (nenhuma mudança de schema).

## 8. Fora de escopo (por decisão ou por prudência)

- Criar ação fora de retro; excluir ação; reatribuir para quem não participou da retro de origem.
- Editar ações de retro em andamento por esta tela.
- Auditoria de alterações; exportação (CSV/Markdown); notificações; edição em lote.
- Entidade `Team` formal.

## 9. Documentação a atualizar após a implementação

`docs/project-status.md` (endpoints, página, regras), `docs/PRD.md` (user story e tabela de endpoints),
`docs/architecture/frontend-design.md` (componentes e store), `CHANGELOG.md`, e uma linha em `CLAUDE.md` (nova página e
convenção de acesso por `team_key`).
