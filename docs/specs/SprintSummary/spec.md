# Spec — Sprint Summary

**Feature:** Resumo de sprint obrigatório vinculado à criação de milestones  
**Data:** 2026-06-27  
**Status:** Aprovado para implementação  

---

## Contexto

O facilitador precisa registrar métricas da sprint antes de adicionar milestones na fase `setup`. Esses dados são exibidos na fase `presentation` junto aos marcos, com um gráfico de evolução histórica comparando as taxas de entrega do time ao longo das sprints.

---

## 1. Novo model — `SprintSummary`

**Arquivo:** `backend/apps/retrospectives/models.py`

Adicionar após a classe `Milestone`:

```python
class SprintSummary(models.Model):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    retrospective = models.OneToOneField(
        Retrospective,
        on_delete=models.CASCADE,
        related_name="sprint_summary"
    )
    total_stories = models.PositiveIntegerField()
    completed     = models.PositiveIntegerField()
    carryover     = models.PositiveIntegerField()
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sprint Summary"
```

**Regras:**
- Relação `OneToOne` com `Retrospective` — cada retro tem no máximo um `SprintSummary`.
- `delivery_rate` **não é persiste** — calculado no serializer como `completed / total_stories * 100`, arredondado para 1 casa decimal. Retorna `null` se `total_stories == 0`.
- Todos os três campos numéricos são obrigatórios (`NOT NULL`).

---

## 2. Migration

```bash
cd backend
python manage.py makemigrations retrospectives --name add_sprint_summary
python manage.py migrate
```

---

## 3. Serializers

**Arquivo:** `backend/apps/retrospectives/serializers.py`

### `SprintSummarySerializer`

```python
class SprintSummarySerializer(serializers.ModelSerializer):
    delivery_rate = serializers.SerializerMethodField()

    class Meta:
        model  = SprintSummary
        fields = [
            "id",
            "total_stories",
            "completed",
            "carryover",
            "delivery_rate",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_delivery_rate(self, obj):
        if not obj.total_stories:
            return None
        return round(obj.completed / obj.total_stories * 100, 1)
```

### `SprintSummaryHistorySerializer`

Estende `SprintSummarySerializer` adicionando campos da retro para montar a série temporal:

```python
class SprintSummaryHistorySerializer(SprintSummarySerializer):
    sprint_name = serializers.CharField(
        source="retrospective.sprint_name", allow_null=True
    )
    closed_at = serializers.DateTimeField(source="retrospective.closed_at")

    class Meta(SprintSummarySerializer.Meta):
        fields = SprintSummarySerializer.Meta.fields + ["sprint_name", "closed_at"]
```

---

## 4. Views

**Arquivo:** `backend/apps/retrospectives/views.py`

### `SprintSummaryView`

Leitura e escrita do `SprintSummary` de uma retro específica.

```python
class SprintSummaryView(RetrospectiveAccessMixin, generics.GenericAPIView):
    serializer_class = SprintSummarySerializer

    def get_retrospective(self):
        return get_object_or_404(Retrospective, pk=self.kwargs["pk"])

    def get_object(self):
        retro = self.get_retrospective()
        obj, _ = SprintSummary.objects.get_or_create(
            retrospective=retro,
            defaults={"total_stories": 0, "completed": 0, "carryover": 0},
        )
        return obj

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)

    def _write(self, request, partial=False):
        retro = self.get_retrospective()
        if request.user != retro.facilitator:
            raise PermissionDenied("Apenas o facilitador pode editar o sprint summary.")
        if retro.status != "setup":
            raise PermissionDenied("Sprint summary só pode ser editado na fase setup.")
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        return self._write(request, partial=False)

    def put(self, request, *args, **kwargs):
        return self._write(request, partial=False)

    def patch(self, request, *args, **kwargs):
        return self._write(request, partial=True)
```

**Permissões:**
- `GET`: qualquer participante da retro (facilitador ou participante).
- `POST / PUT / PATCH`: apenas facilitador na fase `setup`. Retorna `403` nos demais casos.

### `SprintSummaryHistoryView`

Retorna a série histórica de `SprintSummary` de retros **fechadas** do mesmo `team_key`, ordenada cronologicamente.

```python
class SprintSummaryHistoryView(generics.ListAPIView):
    serializer_class = SprintSummaryHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        team_key = self.request.query_params.get("team_key", "")
        if not team_key:
            return SprintSummary.objects.none()
        return (
            SprintSummary.objects.filter(
                retrospective__team_key=team_key,
                retrospective__status="closed",
            )
            .select_related("retrospective")
            .order_by("retrospective__closed_at")
        )
```

**Query param obrigatório:** `?team_key=<slug>`  
**Sem `team_key`:** retorna lista vazia.  
**Acesso:** qualquer usuário autenticado não-guest.

---

## 5. URLs

**Arquivo:** `backend/apps/retrospectives/urls.py`

Adicionar junto aos demais endpoints de retrospectiva:

```python
path(
    "<uuid:pk>/sprint-summary/",
    SprintSummaryView.as_view(),
    name="sprint-summary",
),
```

Adicionar no nível raiz do router (sem `pk` de retro):

```python
path(
    "sprint-summary-history/",
    SprintSummaryHistoryView.as_view(),
    name="sprint-summary-history",
),
```

**Endpoints resultantes:**

| Método | URL | Descrição |
|---|---|---|
| `GET` | `/api/retrospectives/{id}/sprint-summary/` | Lê o summary da retro |
| `POST` | `/api/retrospectives/{id}/sprint-summary/` | Cria ou substitui o summary |
| `PUT` | `/api/retrospectives/{id}/sprint-summary/` | Atualiza o summary completo |
| `PATCH` | `/api/retrospectives/{id}/sprint-summary/` | Atualiza campos parcialmente |
| `GET` | `/api/retrospectives/sprint-summary-history/?team_key=<slug>` | Série histórica do time |

---

## 6. Frontend — Store (`stores/retro.ts`)

Adicionar ao state:

```typescript
sprintSummary: null as SprintSummary | null,
sprintSummaryHistory: [] as SprintSummaryHistory[],
```

Adicionar actions:

```typescript
async fetchSprintSummary(retroId: string): Promise<void> {
  const data = await api.get(`/retrospectives/${retroId}/sprint-summary/`)
  this.sprintSummary = data
},

async saveSprintSummary(
  retroId: string,
  payload: { total_stories: number; completed: number; carryover: number }
): Promise<void> {
  const data = await api.post(`/retrospectives/${retroId}/sprint-summary/`, payload)
  this.sprintSummary = data
},

async fetchSprintSummaryHistory(teamKey: string): Promise<void> {
  const data = await api.get(`/retrospectives/sprint-summary-history/?team_key=${teamKey}`)
  this.sprintSummaryHistory = data
},
```

Adicionar types:

```typescript
interface SprintSummary {
  id: string
  total_stories: number
  completed: number
  carryover: number
  delivery_rate: number | null
  created_at: string
  updated_at: string
}

interface SprintSummaryHistory extends SprintSummary {
  sprint_name: string | null
  closed_at: string
}
```

---

## 7. Frontend — Componente `SprintSummaryForm`

**Arquivo:** `frontend/components/forms/SprintSummaryForm.vue`

**Responsabilidade:** formulário de criação/edição do `SprintSummary` na fase `setup`.

**Props:**
```typescript
retroId: string          // obrigatória
initialData?: SprintSummary | null  // pré-preenche se já existir
```

**Emits:** `saved: [SprintSummary]`

**Comportamento:**
- Três inputs numéricos (`type="number"`, `min="0"`): `total_stories`, `completed`, `carryover`.
- Campo `delivery_rate` calculado reactivamente:
  ```typescript
  const deliveryRate = computed(() => {
    if (!total.value) return '--'
    return `${((completed.value / total.value) * 100).toFixed(1)}%`
  })
  ```
- Botão "Save Sprint Summary" chama `retroStore.saveSprintSummary()`.
- Exibe loading durante a requisição; toast de sucesso ao salvar.
- Ao montar, se `initialData` estiver presente, pré-preenche os campos.

**Visual:**
- Container `.panel` com título `"Sprint Summary"`.
- Grid 3 colunas para os inputs numéricos (em mobile: 1 coluna).
- Campo `delivery_rate` em destaque abaixo dos inputs — tipografia maior, cor `text-[#00f2ff]`.
- Usa `.field-input` nos inputs e `.button-primary` no botão.

---

## 8. Frontend — Modificação `SetupView`

**Arquivo:** `frontend/components/phases/SetupView.vue`

**Mudanças:**

1. Importar e renderizar `SprintSummaryForm` acima da seção de milestones.

2. Buscar summary ao montar:
   ```typescript
   onMounted(() => {
     retroStore.fetchSprintSummary(retro.value.id)
   })
   ```

3. Computed `hasSummary`:
   ```typescript
   const hasSummary = computed(() =>
     !!retroStore.sprintSummary && retroStore.sprintSummary.total_stories > 0
   )
   ```

4. Emitir `saved` do `SprintSummaryForm` atualiza `retroStore.sprintSummary` (já coberto pela action).

5. Botão `+ Add Milestone` recebe `:disabled="!hasSummary"`.

6. Quando `!hasSummary`, exibir aviso abaixo do botão:
   ```
   ⚠ Preencha o Sprint Summary para adicionar milestones.
   ```
   Visual: `text-xs text-zinc-500 mt-1`.

---

## 9. Frontend — Componente `SprintSummaryCards`

**Arquivo:** `frontend/components/retro/SprintSummaryCards.vue`

**Responsabilidade:** exibe os quatro indicadores da sprint em cards horizontais na fase `presentation`.

**Props:**
```typescript
summary: SprintSummary  // obrigatória
```

**Layout:** grid de 4 colunas (em mobile: 2 colunas).

**Cards:**

| Label | Valor | Observação |
|---|---|---|
| Total Sprint | `summary.total_stories` | — |
| Concluídas | `summary.completed` | — |
| Carry-over | `summary.carryover` | — |
| Taxa de Entrega | `summary.delivery_rate + '%'` | `'--'` se `null` |

**Visual de cada card:**
- Container: `.panel` com `p-4 flex flex-col gap-1 items-center text-center`.
- Label: `text-xs text-zinc-500 uppercase tracking-wide`.
- Valor: `text-2xl font-light text-zinc-100`.
- Card de Taxa de Entrega: valor em `text-[#00f2ff]` para destaque.

---

## 10. Frontend — Componente `SprintSummaryChart`

**Arquivo:** `frontend/components/retro/SprintSummaryChart.vue`

**Responsabilidade:** visualização da taxa de entrega — barra de progresso simples ou gráfico de linha histórico, dependendo do volume de dados disponíveis.

**Props:**
```typescript
history: SprintSummaryHistory[]  // retros fechadas do mesmo team_key, ordenadas por closed_at
current: SprintSummary           // sprint atual (pode não estar fechada)
```

**Lógica condicional:**

```typescript
// Caso A: menos de 2 pontos históricos → barra de progresso
// Caso B: 2 ou mais pontos históricos → gráfico de linha
const showChart = computed(() => history.length >= 2)
```

### Caso A — Barra de progresso

- Label: `"Delivery Rate"`.
- Barra: `div` com largura `delivery_rate + '%'`, cor `bg-[#00f2ff]`, fundo `bg-white/10`, `rounded-full`, altura `h-2`.
- Valor percentual à direita da barra.

### Caso B — Gráfico de linha

**Implementação:** SVG nativo, sem biblioteca externa.

**Dados do gráfico:** `[...history, currentPoint]` onde `currentPoint` é derivado de `current` com `sprint_name` da retro ativa.

**Estrutura do SVG:**

```
- viewBox: "0 0 600 200"
- Padding interno: top 20, right 20, bottom 40, left 40
- Eixo Y: 0% a 100%, com linhas de referência em 25%, 50%, 75%, 100%
- Eixo X: um ponto por sprint, label = sprint_name ou "Sprint N"
- Linha: <polyline> conectando os pontos, stroke="#00f2ff", stroke-width="1.5", fill="none"
- Pontos históricos (●): <circle r="4" fill="#00f2ff">, tooltip com valor ao hover
- Ponto atual (◆): <polygon> em losango, fill="#00f2ff", stroke="white", stroke-width="1"
  para diferenciar visualmente da série fechada
- Linhas de referência do eixo Y: stroke="rgba(255,255,255,0.08)"
```

**Labels do eixo X:** `sprint_name` da retro. Se `sprint_name` for `null`, usar `"Sprint N"` onde N é a posição na série (1-indexed).

**Estado sem dados:** se `current.delivery_rate` for `null` (total_stories = 0), renderizar mensagem `"Sem dados para exibir."` em `text-sm text-zinc-600`.

---

## 11. Frontend — Modificação `MilestonesView`

**Arquivo:** `frontend/components/phases/MilestonesView.vue`

**Mudanças:**

1. Importar `SprintSummaryCards` e `SprintSummaryChart`.

2. Buscar dados ao montar:
   ```typescript
   onMounted(async () => {
     await retroStore.fetchSprintSummary(retro.value.id)
     if (retro.value.team_key) {
       await retroStore.fetchSprintSummaryHistory(retro.value.team_key)
     }
   })
   ```

3. Renderizar abaixo da grade de `MilestoneCard`, apenas se `sprintSummary` existir:
   ```vue
   <template v-if="retroStore.sprintSummary">
     <SprintSummaryCards :summary="retroStore.sprintSummary" />
     <SprintSummaryChart
       :history="retroStore.sprintSummaryHistory"
       :current="retroStore.sprintSummary"
     />
   </template>
   ```

---

## 12. Regras de negócio consolidadas

| Regra | Detalhe |
|---|---|
| Relação | `SprintSummary` é `1:1` com `Retrospective` |
| Escrita | Apenas facilitador na fase `setup` |
| Leitura | Qualquer participante da retro |
| `delivery_rate` | Calculado: `completed / total_stories * 100`. `null` se `total_stories == 0` |
| Bloqueio de milestone | Botão `+ Add Milestone` desabilitado enquanto `SprintSummary` não existir ou `total_stories == 0` |
| Gráfico Caso A | Menos de 2 retros fechadas com summary no `team_key` → barra de progresso simples |
| Gráfico Caso B | 2 ou mais retros fechadas com summary → gráfico de linha SVG |
| Sprint atual no gráfico | Sempre incluída como último ponto (◆), independente de estar fechada |
| Histórico | Filtrado por `team_key` + `status=closed`, ordenado por `closed_at ASC` |
| `total_stories = 0` | Cards mostram `'--'` na taxa; gráfico exibe mensagem de ausência de dados |

---

## 13. Arquivos a criar

| Arquivo | Tipo |
|---|---|
| `backend/apps/retrospectives/migrations/XXXX_add_sprint_summary.py` | Migration gerada |
| `frontend/components/forms/SprintSummaryForm.vue` | Componente novo |
| `frontend/components/retro/SprintSummaryCards.vue` | Componente novo |
| `frontend/components/retro/SprintSummaryChart.vue` | Componente novo |

## 14. Arquivos a modificar

| Arquivo | Mudança |
|---|---|
| `backend/apps/retrospectives/models.py` | Adicionar `SprintSummary` |
| `backend/apps/retrospectives/serializers.py` | Adicionar `SprintSummarySerializer`, `SprintSummaryHistorySerializer` |
| `backend/apps/retrospectives/views.py` | Adicionar `SprintSummaryView`, `SprintSummaryHistoryView` |
| `backend/apps/retrospectives/urls.py` | Registrar dois novos endpoints |
| `frontend/stores/retro.ts` | Adicionar state, actions e types de `SprintSummary` |
| `frontend/components/phases/SetupView.vue` | Adicionar `SprintSummaryForm` + lógica de bloqueio de milestone |
| `frontend/components/phases/MilestonesView.vue` | Adicionar `SprintSummaryCards` + `SprintSummaryChart` |

## 15. Arquivos de documentação a atualizar após implementação

| Arquivo | Seção |
|---|---|
| `data-model.md` | Adicionar tabela `retrospectives_sprintsummary` |
| `PRD.md` | Adicionar US-07b "Registrar resumo da sprint" |
| `project-status.md` | Adicionar `SprintSummary` em models e endpoints |
| `frontend-design.md` | Adicionar `SprintSummaryForm`, `SprintSummaryCards`, `SprintSummaryChart` |
