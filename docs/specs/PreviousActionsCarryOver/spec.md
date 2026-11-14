# Spec — Previous Actions Carry-Over + Concluídos (fase Check)

**Feature:** Ações pendentes de retros anteriores acumulam entre ciclos; ações concluídas desde a última
retro ganham uma seção própria de reconhecimento
**Data:** 2026-11-13
**Status:** Aprovado para implementação

---

## Contexto

Hoje a fase `check` (`PreviousActionListView`) só olha para a **retro fechada mais recente** do mesmo
`team_key` (`get_previous_closed_retrospective`), e devolve **todos** os `ActionItem` dela, independente
de status — inclusive os já `done`.

Isso cria um gap: um action item criado na retro N-2 que não foi concluído na retro N-1 (porque não foi
atualizado para `done`) **desaparece** da fase Check a partir da retro N, porque a consulta só olha a
retro N-1, não a N-2. O facilitador perde rastreabilidade de pendências antigas.

**Pedido original:** a listagem de pendências deve sempre trazer `not_started`/`in_progress` de qualquer
retro fechada do time, e um item só sai dessa lista quando vira `done`.

**Ajuste de produto (nesta revisão):** sair da lista de pendências não deve significar desaparecer de
vista — a equipe quer poder mencionar, no próprio momento da revisão, o que **foi** entregue. Decisão:
itens concluídos **entre o fechamento da retro anterior e agora** ganham uma seção separada "✅ Concluídos
desde a última retro", colapsada por padrão, abaixo da lista de pendências ativas na fase Check. Escopo
temporal (não acumula para sempre) preserva o "Zero Noise"; a seção separada (não misturada à lista
ativa) preserva o foco em ação.

---

## 1. Backend — Model (`backend/apps/actions/models.py`)

Adicionar campo para rastrear quando o status mudou por último:

```python
status_updated_at = models.DateTimeField(null=True, blank=True)
```

**Migration** (`makemigrations` dentro do container, via `docker compose exec backend`):
- Adicionar a coluna.
- Data migration de backfill: para registros existentes, `status_updated_at = created_at` (não há
  histórico real de quando o status mudou antes deste campo existir; usar `created_at` evita que itens
  antigos `done` apareçam retroativamente como "concluídos agora" na seção nova).

```python
def backfill_status_updated_at(apps, schema_editor):
    ActionItem = apps.get_model("actions", "ActionItem")
    ActionItem.objects.filter(status_updated_at__isnull=True).update(status_updated_at=models.F("created_at"))
```

---

## 2. Backend — `signals.py`: manter `status_updated_at` sincronizado

```python
from django.utils import timezone

@receiver(pre_save, sender=ActionItem)
def capture_previous_action_status(sender, instance, **kwargs):
    previous = ActionItem.objects.filter(pk=instance.pk).values("status").first()
    if previous is None:
        # criação: marca o timestamp inicial
        instance.status_updated_at = timezone.now()
        return

    instance._previous_status = previous["status"]
    if previous["status"] != instance.status:
        instance.status_updated_at = timezone.now()
```

**Atenção:** `PreviousActionStatusUpdateView.put` usa `save(update_fields=["status"])`. Esse
`update_fields` precisa incluir `"status_updated_at"` também, senão o valor calculado no `pre_save` nunca
é persistido:

```python
action_item.save(update_fields=["status", "status_updated_at"])
```

---

## 3. Backend — `ActionAccessMixin` (`backend/apps/actions/views.py`)

```python
def get_latest_closed_retrospective(self, retrospective):
    return (
        Retrospective.objects.filter(team_key=retrospective.team_key, status=RetrospectiveStatus.CLOSED)
        .exclude(id=retrospective.id)
        .order_by("-closed_at", "-created_at")
        .first()
    )

def get_pending_previous_actions(self, retrospective):
    return (
        ActionItem.objects.filter(
            retrospective__team_key=retrospective.team_key,
            retrospective__status=RetrospectiveStatus.CLOSED,
            status__in=[ActionItemStatus.NOT_STARTED, ActionItemStatus.IN_PROGRESS],
        )
        .exclude(retrospective=retrospective)
        .select_related("assignee", "card", "retrospective")
        .order_by("retrospective__closed_at", "created_at")
    )

def get_recently_completed_actions(self, retrospective, latest_closed_retrospective):
    if latest_closed_retrospective is None or latest_closed_retrospective.closed_at is None:
        return ActionItem.objects.none()
    return (
        ActionItem.objects.filter(
            retrospective__team_key=retrospective.team_key,
            retrospective__status=RetrospectiveStatus.CLOSED,
            status=ActionItemStatus.DONE,
            status_updated_at__gt=latest_closed_retrospective.closed_at,
        )
        .exclude(retrospective=retrospective)
        .select_related("assignee", "card", "retrospective")
        .order_by("-status_updated_at")
    )
```

`ActionItemStatus` precisa ser importado de `apps.actions.models` em `views.py` (hoje só usado em
`serializers.py`).

**Regra do corte temporal:** "desde a última retro" = desde o `closed_at` da retro fechada mais recente
do time (a mesma que, antes desta mudança, era a única fonte de pendências). Se o time nunca fechou uma
retro, não há seção de concluídos.

---

## 4. Backend — `PreviousActionListView.get`

```python
class PreviousActionListView(ActionAccessMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, retrospective_id):
        retrospective = self.get_retrospective()
        self.ensure_participant(retrospective, request.user)

        latest_closed = self.get_latest_closed_retrospective(retrospective)
        context = {"request": request, "retrospective": retrospective}

        pending_serializer = ActionItemSerializer(
            self.get_pending_previous_actions(retrospective), many=True, context=context
        )
        completed_serializer = ActionItemSerializer(
            self.get_recently_completed_actions(retrospective, latest_closed), many=True, context=context
        )
        return Response(
            {
                "action_items": pending_serializer.data,
                "recently_completed": completed_serializer.data,
            }
        )
```

**Mudança de contrato:** o campo `retrospective_id` (singular) deixa de existir — os itens agora podem
vir de retros diferentes, e cada item já expõe seu próprio `retrospective` (UUID) no payload do
`ActionItemSerializer`.

---

## 5. Backend — `PreviousActionStatusUpdateView.put`

A busca do action item deixa de ser restrita à "retro anterior única" e passa a aceitar qualquer item de
qualquer retro fechada do mesmo time (pendente ou já `done` — permitir reabrir um item marcado `done` por
engano também deve funcionar, movendo-o de volta para a lista ativa):

```python
class PreviousActionStatusUpdateView(ActionAccessMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, retrospective_id, action_id):
        retrospective = self.get_retrospective()
        self.ensure_participant(retrospective, request.user)

        try:
            action_item = ActionItem.objects.select_related("retrospective").get(
                id=action_id,
                retrospective__team_key=retrospective.team_key,
                retrospective__status=RetrospectiveStatus.CLOSED,
            )
        except ActionItem.DoesNotExist as error:
            raise NotFound("Action item not found in a closed retrospective for this team.") from error

        serializer = PreviousActionStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action_item.status = serializer.validated_data["status"]
        action_item.save(update_fields=["status", "status_updated_at"])

        return Response(
            {"action_id": str(action_item.id), "status": action_item.status},
            status=status.HTTP_200_OK,
        )
```

Mantém o alias legado `"pending"` → `not_started` já existente em `PreviousActionStatusSerializer`.

O broadcast WebSocket `action.check_updated` (via `signals.py`, disparado em qualquer save de
`ActionItem` cuja `status` mudou) continua funcionando sem alteração.

---

## 6. Backend — Serializer (`ActionItemSerializer`)

Expor `status_updated_at` como leitura, para a UI poder exibir "concluído há X" na seção de concluídos:

```python
class ActionItemSerializer(serializers.ModelSerializer):
    ...
    status_updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        ...
        fields = (..., "status_updated_at")
        read_only_fields = (..., "status_updated_at")
```

---

## 7. Frontend — Types (`frontend/utils/types.ts`)

```typescript
export interface ActionItem {
  id: string
  retrospective: string
  card: string | null
  description: string
  assignee: string | null
  assignee_name: string | null
  participant_id: string | null
  due_date: string | null
  status: ActionStatus
  external_tracker_url: string | null
  created_at: string
  status_updated_at: string | null
}

export interface PreviousActionsResponse {
  action_items: ActionItem[]
  recently_completed: ActionItem[]
}
```

---

## 8. Frontend — Store (`frontend/stores/retro.ts`)

**Defaults** (estado inicial e fallback de erro no `fetchRetrospective`):

```typescript
previousActions: { action_items: [], recently_completed: [] },
```

**Helper compartilhado** para mover um item entre as duas listas conforme o novo status (usado tanto na
chamada otimista quanto no handler de WebSocket):

```typescript
function moveActionBetweenLists(
  previousActions: PreviousActionsResponse,
  actionId: string,
  newStatus: ActionItem["status"],
): PreviousActionsResponse {
  const found =
    previousActions.action_items.find((item) => item.id === actionId) ??
    previousActions.recently_completed.find((item) => item.id === actionId)
  if (!found) return previousActions

  const updated: ActionItem = { ...found, status: newStatus }
  const action_items = previousActions.action_items.filter((item) => item.id !== actionId)
  const recently_completed = previousActions.recently_completed.filter((item) => item.id !== actionId)

  if (newStatus === "done") {
    recently_completed.unshift(updated)
  } else {
    action_items.push(updated)
  }
  return { action_items, recently_completed }
}
```

**`updatePreviousActionStatus`:**

```typescript
async updatePreviousActionStatus(retrospectiveId: string, actionId: string, status: string) {
  const api = useApiClient()
  await api.put(`/retrospectives/${retrospectiveId}/previous-actions/${actionId}/status/`, { status })
  this.previousActions = moveActionBetweenLists(this.previousActions, actionId, status as ActionItem["status"])
},
```

**Handler WebSocket `action.check_updated`:**

```typescript
if (type === "action.check_updated") {
  this.previousActions = moveActionBetweenLists(
    this.previousActions,
    String(event.action_id),
    event.status as ActionItem["status"],
  )
}
```

---

## 9. Frontend — `CheckView.vue`

- Texto descritivo atualizado: "Pending actions from this team's closed retrospectives. An item leaves
  this list once marked Done."
- Nova seção abaixo da lista ativa, **colapsada por padrão** (`<details>` ou toggle local), só renderizada
  se `recently_completed.length > 0`. Lista os itens com descrição em `line-through`, nome do assignee, e
  um botão "Reabrir" (visível só ao facilitador) que chama `updatePreviousActionStatus(..., "in_progress")`.

O botão "Reabrir" cobre o caso de erro humano (marcou `done` por engano) — devolve o item para
`in_progress` e ele volta a aparecer na lista ativa de pendências, usando o mesmo endpoint.

---

## 10. Regras de negócio consolidadas

| Regra | Detalhe |
|---|---|
| Escopo das pendências | Todos os `ActionItem` de retros `closed` com o mesmo `team_key` (exclui a retro atual); status `not_started`/`in_progress` |
| Saída da lista ativa | Ocorre quando o status é atualizado para `done` — mas o item não desaparece, migra para "Concluídos" |
| Escopo dos concluídos | `status=done` E `status_updated_at >` `closed_at` da retro fechada mais recente do time |
| Sem retro fechada anterior | Nenhuma seção de concluídos (não há corte temporal definido) |
| Ordenação pendências | `retrospective.closed_at` ascendente, depois `created_at` (mais antigas primeiro) |
| Ordenação concluídos | `status_updated_at` descendente (concluído mais recentemente primeiro) |
| Reabertura | Qualquer participante com permissão de update pode mover um `done` de volta para `in_progress`/`not_started` |
| Alias legado | `"pending"` continua aceito e gravado como `not_started` |
| Realtime | `action.check_updated` já broadcastava globalmente; a lógica de mover entre listas fica no client (store) |

---

## 11. Arquivos a criar/modificar

| Arquivo | Mudança |
|---|---|
| `backend/apps/actions/models.py` | Adicionar `status_updated_at` |
| `backend/apps/actions/migrations/XXXX_add_status_updated_at.py` | Migration + data migration de backfill |
| `backend/apps/actions/signals.py` | `pre_save` passa a setar `status_updated_at` na criação e em toda mudança de status |
| `backend/apps/actions/views.py` | `get_latest_closed_retrospective`, `get_pending_previous_actions`, `get_recently_completed_actions`; reescrever `PreviousActionListView.get` e `PreviousActionStatusUpdateView.put` |
| `backend/apps/actions/serializers.py` | Expor `status_updated_at` em `ActionItemSerializer` |
| `backend/apps/actions/tests.py` | Reescrever teste de agregação multi-retro; adicionar testes para `recently_completed` (dentro/fora da janela temporal), para reabertura (`done` → `in_progress`) e para backfill não quebrar dados antigos |
| `frontend/utils/types.ts` | `ActionItem` ganha `status_updated_at`; `PreviousActionsResponse` ganha `recently_completed`, perde `retrospective_id` |
| `frontend/stores/retro.ts` | Defaults com `recently_completed: []`; helper `moveActionBetweenLists`; `updatePreviousActionStatus` e handler `action.check_updated` usam o helper |
| `frontend/components/retro/phases/CheckView.vue` | Texto descritivo + seção colapsável "Concluídos desde a última retro" com botão Reabrir |

## 12. Arquivos de documentação a atualizar após implementação

| Arquivo | Seção |
|---|---|
| `docs/project-status.md` | Seção `actions` — "Ações anteriores": regra de agregação multi-retro, filtro de status, e nova seção de concluídos com janela temporal |
| `docs/PRD.md` | Linha da tabela de endpoints de `previous-actions/`; nova menção de UX à seção de concluídos |
| `CHANGELOG.md` | Nova entrada em `[Não lançado]` descrevendo carry-over de pendências + seção de concluídos |
