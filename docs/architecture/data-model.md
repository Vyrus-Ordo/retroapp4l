# RetroApp 4L — Modelo de Dados

**Versão:** 2026-06-27
**Source of truth:** este arquivo. Em caso de conflito com PRD.md ou project-status.md, este vence para questões de schema e payload.

> **Para agentes:** antes de criar migration, alterar model ou validar payload, leia este arquivo inteiro.
> Nunca altere o schema diretamente — sempre via `python manage.py makemigrations` seguido de `migrate`.

---

## Visão geral dos apps e tabelas

```
users/
  └─ users_user

retrospectives/
  ├─ retrospectives_retrospective
  ├─ retrospectives_milestone
  ├─ retrospectives_participant
  └─ retrospectives_accesslog

cards/
  ├─ cards_card
  └─ cards_cardvote

actions/
  └─ actions_actionitem
```

---

## Regras globais

- Todas as PKs são `UUID` geradas por `uuid.uuid4`, não auto-incremento.
- `DateTimeField(auto_now_add=True)` → `TIMESTAMPTZ NOT NULL DEFAULT NOW()`. Nunca editável após criação.
- `on_delete=CASCADE` é o padrão para FKs obrigatórias; `on_delete=SET_NULL` é usado para FKs opcionais.
- Não há soft-delete em nenhuma tabela. Deletar é permanente.
- Banco local padrão é SQLite; produção usa PostgreSQL. `JSONField` é `JSONB` no PostgreSQL e `TEXT` no SQLite.

---

## App: `users`

### `User` → tabela `users_user`

```sql
CREATE TABLE users_user (
    id             UUID        NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    password       VARCHAR(128) NOT NULL,
    last_login     TIMESTAMPTZ NULL,
    is_superuser   BOOLEAN     NOT NULL DEFAULT FALSE,
    name           VARCHAR(255) NOT NULL,
    email          VARCHAR(254) NOT NULL UNIQUE,
    public_email   VARCHAR(254) NOT NULL DEFAULT '',
    oauth_provider VARCHAR(50)  NOT NULL DEFAULT '',
    oauth_id       VARCHAR(255) NOT NULL DEFAULT '',
    avatar_url     VARCHAR(200) NOT NULL DEFAULT '',
    is_guest       BOOLEAN     NOT NULL DEFAULT FALSE,
    is_active      BOOLEAN     NOT NULL DEFAULT TRUE,
    is_staff       BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
    -- M2M: users_user_groups, users_user_user_permissions (tabelas Django padrão)
);
```

```python
class User(AbstractBaseUser, PermissionsMixin):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name           = models.CharField(max_length=255)
    email          = models.EmailField(unique=True)          # USERNAME_FIELD
    public_email   = models.EmailField(blank=True)           # visível para guests
    oauth_provider = models.CharField(max_length=50, blank=True)
    oauth_id       = models.CharField(max_length=255, blank=True)
    avatar_url     = models.URLField(blank=True)
    is_guest       = models.BooleanField(default=False)
    is_active      = models.BooleanField(default=True)
    is_staff       = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["email"]
```

> **Guests:** usuários com `is_guest=True` têm senha inutilizável (`set_unusable_password()`), `email` interno no formato `guest+<uuid>@guest.retroapp4l.local` e entram apenas via convite. Login direto é bloqueado na view.
>
> **`display_email` (property):** retorna `public_email` para guests e `email` para usuários normais. A API expõe este campo via `UserSerializer.get_email()` — o campo `email` no payload nunca vaza o e-mail interno de guests.
>
> **OAuth:** `oauth_provider` e `oauth_id` existem no schema mas o provider Google não está configurado no backend do repositório. O botão na UI aponta para `/accounts/google/login/` (django-allauth), que falhará sem configuração.

#### Campos virtuais expostos pela API

| Campo virtual | Serializer | Tipo | Lógica |
|---|---|---|---|
| `email` (sobreescrito) | `UserSerializer` | `string` | `obj.display_email` — retorna `public_email` para guest, `email` para normal |

---

## App: `retrospectives`

### `Retrospective` → tabela `retrospectives_retrospective`

```sql
CREATE TABLE retrospectives_retrospective (
    id                             UUID         NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    title                          VARCHAR(255) NOT NULL,
    sprint_name                    VARCHAR(255) NULL,
    description                    TEXT         NOT NULL DEFAULT '',
    team_key                       VARCHAR(100) NOT NULL,  -- SlugField; agrupa retros por time sem entidade Team
    facilitator_id                 UUID         NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    status                         VARCHAR(20)  NOT NULL DEFAULT 'setup',
        -- choices: setup | lobby | presentation | check | board | grouping
        --         | voting | discussion | actions | closed
    invite_token                   UUID         NULL UNIQUE,
    invite_revoked_at              TIMESTAMPTZ  NULL,
    max_votes_per_user             SMALLINT     NOT NULL DEFAULT 3,
    allow_self_vote                BOOLEAN      NOT NULL DEFAULT FALSE,
    skip_check_phase               BOOLEAN      NOT NULL DEFAULT FALSE,
    focus_card_id                  UUID         NULL REFERENCES cards_card(id) ON DELETE SET NULL,
    invite_temporarily_open_until  TIMESTAMPTZ  NULL,
    timer_started_at               TIMESTAMPTZ  NULL,
    timer_paused_at                TIMESTAMPTZ  NULL,
    timer_duration_seconds         INTEGER      NULL,  -- PositiveIntegerField
    phase_durations                JSONB        NOT NULL DEFAULT '{}',
    created_at                     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    closed_at                      TIMESTAMPTZ  NULL
);
```

```python
class Retrospective(models.Model):
    id                            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title                         = models.CharField(max_length=255)
    sprint_name                   = models.CharField(max_length=255, blank=True, null=True)
    description                   = models.TextField(blank=True)
    team_key                      = models.SlugField(max_length=100)
    facilitator                   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="facilitated_retrospectives")
    status                        = models.CharField(max_length=20, choices=RetrospectiveStatus.choices, default=RetrospectiveStatus.SETUP)
    invite_token                  = models.UUIDField(unique=True, blank=True, null=True)
    invite_revoked_at             = models.DateTimeField(blank=True, null=True)
    max_votes_per_user            = models.PositiveSmallIntegerField(default=3)
    allow_self_vote               = models.BooleanField(default=False)
    skip_check_phase              = models.BooleanField(default=False)
    focus_card                    = models.ForeignKey("cards.Card", on_delete=models.SET_NULL, blank=True, null=True, related_name="focused_in_retrospectives")
    invite_temporarily_open_until = models.DateTimeField(blank=True, null=True)
    timer_started_at              = models.DateTimeField(blank=True, null=True)
    timer_paused_at               = models.DateTimeField(blank=True, null=True)
    timer_duration_seconds        = models.PositiveIntegerField(blank=True, null=True)
    phase_durations               = models.JSONField(default=dict, blank=True)
    created_at                    = models.DateTimeField(auto_now_add=True)
    closed_at                     = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
```

> **`phase_durations` (JSONField):** estrutura livre. Chaves esperadas são nomes de fase (`"board"`, `"voting"`, etc.) com valor inteiro em segundos. Se a chave não existir, o consumer usa defaults hardcoded.
>
> **`invite_token`:** gerado na criação. Removido (set `NULL`) no fechamento da retro. Presente → lobby ativo. `NULL` → sem convite ativo.
>
> **`invite_temporarily_open_until`:** setado por `POST /retrospectives/{id}/reopen-entry/` para `now + 120s`. A task Celery `tasks.invite.auto_block_invite` o retorna a `NULL` quando a janela expira e emite `invite.status_updated` via WebSocket. Entrar na retro durante a janela **não** fecha o convite imediatamente.
>
> **`allow_self_vote`:** configurado apenas na criação. Não há endpoint para alterá-lo depois. Afeta votação: quando `False`, o backend bloqueia voto no próprio card usando a autoria real, inclusive em cards anônimos.
>
> **`skip_check_phase`:** efeito apenas no frontend (`usePhase.ts`). O backend não valida nem pula fases.
>
> **`focus_card_id`:** zerado no fechamento. Persistido no banco para sobreviver a reconexões WebSocket.
>
> **Timer:** `timer_started_at` + `timer_duration_seconds` definem o fim esperado. `timer_paused_at` armazena o instante da pausa. A task `tasks.timer.sync_timer` emite `timer.sync` a cada 5s enquanto o timer corre — contudo, o código atual da task apenas retorna um dict de status e não emite diretamente; o consumer WebSocket gerencia o loop de sync.
>
> **Fechamento:** `POST /close/` exige `{ "confirm": true }`, fase `actions`, facilitador. Seta `status=closed`, `closed_at`, zera `invite_token`, preenche `invite_revoked_at` e limpa `focus_card`.

#### Campos virtuais expostos pela API

| Campo virtual | Serializer | Tipo | Lógica |
|---|---|---|---|
| `facilitator_name` | `RetrospectiveListSerializer`, `RetrospectiveDetailSerializer`, `ClosedRetrospectiveDetailSerializer` | `string` | `obj.facilitator.name` |
| `invite_status` | `InviteResolveSerializer` | `"active" \| "temporarily_open" \| "blocked"` | `"active"` se `status == "lobby"` e `invite_token` não nulo; `"temporarily_open"` se `invite_temporarily_open_until > now`; caso contrário `"blocked"` |
| `entry_expires_at` | `InviteResolveSerializer` | `TIMESTAMPTZ \| null` | `invite_temporarily_open_until` quando no futuro, senão `null` |
| `focus_card_id` | `RetrospectiveDetailSerializer`, `ClosedRetrospectiveDetailSerializer` | `UUID \| null` | `obj.focus_card_id` (campo FK exposto como UUID) |
| `cards_count` | `RetrospectiveHistorySerializer` | `integer` | anotado via queryset |
| `action_items_count` | `RetrospectiveHistorySerializer` | `integer` | anotado via queryset |
| `action_item_status_summary` | `RetrospectiveHistorySerializer` | `{ not_started: int, in_progress: int, done: int }` | contagem por status dos action items da retro |

---

### `Milestone` → tabela `retrospectives_milestone`

```sql
CREATE TABLE retrospectives_milestone (
    id               UUID        NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    retrospective_id UUID        NOT NULL REFERENCES retrospectives_retrospective(id) ON DELETE CASCADE,
    author_id        UUID        NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    category         VARCHAR(20) NOT NULL,
        -- choices: achievement | challenge | change | recognition | other
    description      VARCHAR(500) NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

```python
class Milestone(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    retrospective  = models.ForeignKey(Retrospective, on_delete=models.CASCADE, related_name="milestones")
    author         = models.ForeignKey(User, on_delete=models.CASCADE, related_name="milestones")
    category       = models.CharField(max_length=20, choices=MilestoneCategory.choices)
    description    = models.CharField(max_length=500)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
```

> **Permissões:** criação/edição/exclusão apenas pelo facilitador na fase `setup`. Guests bloqueados.
>
> **Signals:** `post_save` emite `milestone_create` ou `milestone_update` via WebSocket para o grupo `retro_{retrospective_id}`. `post_delete` emite `milestone_delete`.

#### Campos virtuais expostos pela API

| Campo virtual | Serializer | Tipo | Lógica |
|---|---|---|---|
| `author_name` | `MilestoneSerializer` | `string` | `obj.author.name` |

---

### `Participant` → tabela `retrospectives_participant`

```sql
CREATE TABLE retrospectives_participant (
    id               UUID        NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    retrospective_id UUID        NOT NULL REFERENCES retrospectives_retrospective(id) ON DELETE CASCADE,
    user_id          UUID        NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    votes_remaining  INTEGER     NOT NULL DEFAULT 3,
    joined_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_retrospective_participant UNIQUE (retrospective_id, user_id)
);
```

```python
class Participant(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    retrospective  = models.ForeignKey(Retrospective, on_delete=models.CASCADE, related_name="participants")
    user           = models.ForeignKey(User, on_delete=models.CASCADE, related_name="participations")
    votes_remaining = models.IntegerField(default=3)
    joined_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("retrospective", "user"), name="unique_retrospective_participant"),
        ]
        ordering = ["joined_at"]
```

> **`votes_remaining`:** default 3. Decrementado por voto, incrementado por revogação. Resetado para o novo `max_votes_per_user` quando `PUT /votes-config/` é chamado.
>
> **`assignee_id` no ActionItem:** o payload de criação/edição de `ActionItem` recebe `assignee_id` como UUID de `Participant` (não de `User`). O serializer resolve para `User` internamente antes de salvar `ActionItem.assignee`.

#### Campos virtuais expostos pela API

| Campo virtual | Serializer | Tipo | Lógica |
|---|---|---|---|
| `user_name` | `ParticipantSerializer` | `string` | `obj.user.name` |
| `user_email` | `ParticipantSerializer` | `string` | `obj.user.display_email` |

---

### `AccessLog` → tabela `retrospectives_accesslog`

```sql
CREATE TABLE retrospectives_accesslog (
    id               UUID        NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    retrospective_id UUID        NOT NULL REFERENCES retrospectives_retrospective(id) ON DELETE CASCADE,
    action           VARCHAR(32) NOT NULL,
        -- choices: opened | closed | participant_joined | link_reopened | link_auto_blocked
    triggered_by_id  UUID        NULL REFERENCES users_user(id) ON DELETE SET NULL,
    participant_id   UUID        NULL REFERENCES users_user(id) ON DELETE SET NULL,
    timestamp        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

```python
class AccessLog(models.Model):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    retrospective = models.ForeignKey(Retrospective, on_delete=models.CASCADE, related_name="access_logs")
    action        = models.CharField(max_length=32, choices=AccessLogAction.choices)
    triggered_by  = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="triggered_access_logs")
    participant   = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="participant_access_logs")
    timestamp     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
```

> **`participant_id` (FK):** aponta para `users_user`, não para `retrospectives_participant`. É o `User` que entrou — nomeação pode confundir.
>
> **Criação automática:** registros criados por código de domínio (views, tasks), nunca diretamente pelo cliente. A task `auto_block_invite` cria `link_auto_blocked` sem `triggered_by`.

---

## App: `cards`

### `Card` → tabela `cards_card`

```sql
CREATE TABLE cards_card (
    id               UUID        NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    retrospective_id UUID        NOT NULL REFERENCES retrospectives_retrospective(id) ON DELETE CASCADE,
    author_id        UUID        NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    column           VARCHAR(16) NOT NULL,
        -- choices: loved | loathed | longed | learned
    content          VARCHAR(500) NOT NULL,
    is_anonymous     BOOLEAN     NOT NULL DEFAULT FALSE,
    group_id         UUID        NULL REFERENCES cards_card(id) ON DELETE SET NULL,
    position         INTEGER     NOT NULL DEFAULT 0,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

```python
class Card(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    retrospective  = models.ForeignKey(Retrospective, on_delete=models.CASCADE, related_name="cards")
    author         = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cards")
    column         = models.CharField(max_length=16, choices=CardColumn.choices)
    content        = models.CharField(max_length=500)
    is_anonymous   = models.BooleanField(default=False)
    group          = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True, related_name="grouped_cards")
    position       = models.PositiveIntegerField(default=0)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["column", "position", "created_at"]
```

> **Anonimato (`is_anonymous`):** `author_id` **nunca é removido do banco**. É usado internamente para permissões, `allow_self_vote`, edição/exclusão e relacionamentos. Quando `is_anonymous=True`, os serializers públicos retornam `author=null`, `author_name=null`, `author_display="Anonymous"` (ver campos virtuais abaixo). Cards antigos (antes da migration 0003) têm `is_anonymous=False` — o campo não existia e o default garante retrocompatibilidade.
>
> **Agrupamento (`group_id`):** self-FK para o card pai. Apenas um nível de profundidade — filhos não podem ter filhos. Quando o card pai é deletado, `group_id` dos filhos vira `NULL` (`SET_NULL`). O serializer expõe `group_parent_id` como alias de `group_id`.
>
> **Mutação por fase:** a API bloqueia criação/edição/exclusão nas fases `discussion`, `actions` e `closed`. A UI bloqueia somente na fase `board`, sendo mais restritiva que a API.
>
> **Signals:**
> - `pre_save`: captura `_previous_content`, `_previous_group_id` e `_previous_is_anonymous` para o signal `post_save`.
> - `post_save` (criação): emite `card_create` no grupo WebSocket da retro.
> - `post_save` (atualização, conteúdo ou anonimato mudou): emite `card_update`.
> - `post_save` (atualização, group mudou): emite `card_grouped` ou `card_ungrouped`.
> - `post_delete`: emite `card_delete`.

#### Campos virtuais expostos pela API

| Campo virtual | Serializer | Tipo | Lógica |
|---|---|---|---|
| `author` | `CardSerializer` | `UUID \| null` | `null` quando `is_anonymous=True`; caso contrário `str(obj.author_id)` |
| `author_name` | `CardSerializer` | `string \| null` | `null` quando `is_anonymous=True`; caso contrário `obj.author.name` |
| `author_display` | `CardSerializer` | `string` | `"Anonymous"` quando `is_anonymous=True`; caso contrário `obj.author.name` |
| `can_edit` | `CardSerializer` | `boolean` | `True` quando `request.user.id == obj.author_id`; `False` caso contrário ou sem request |
| `group_parent_id` | `CardSerializer` | `UUID \| null` | alias de `obj.group_id` |
| `vote_count` | `CardSerializer` | `integer` | anotado via queryset; default `0` |

---

### `CardVote` → tabela `cards_cardvote`

```sql
CREATE TABLE cards_cardvote (
    id         UUID        NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    card_id    UUID        NOT NULL REFERENCES cards_card(id) ON DELETE CASCADE,
    voter_id   UUID        NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_card_vote_per_voter UNIQUE (card_id, voter_id)
);
```

```python
class CardVote(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    card       = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="votes")
    voter      = models.ForeignKey(User, on_delete=models.CASCADE, related_name="card_votes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("card", "voter"), name="unique_card_vote_per_voter"),
        ]
        ordering = ["created_at"]
```

> **Votação permitida:** apenas fase `voting`, apenas colunas `loathed` e `longed`, máximo 1 voto por `(card, voter)` (constraint de banco).
>
> **Signals:**
> - `post_save` (criação): lê `Participant.votes_remaining` e emite `vote_cast` com `{ card_id, voter_id, votes_remaining }`.
> - `post_delete`: lê `Participant.votes_remaining` e emite `vote_revoked` com `{ card_id, voter_id, votes_remaining }`.
> - Os signals não atualizam `votes_remaining` — isso é responsabilidade da view de voto/revogação.

---

## App: `actions`

### `ActionItem` → tabela `actions_actionitem`

```sql
CREATE TABLE actions_actionitem (
    id                   UUID         NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    retrospective_id     UUID         NOT NULL REFERENCES retrospectives_retrospective(id) ON DELETE CASCADE,
    card_id              UUID         NULL REFERENCES cards_card(id) ON DELETE SET NULL,
    description          TEXT         NOT NULL,
    assignee_id          UUID         NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    due_date             DATE         NULL,
    external_tracker_url VARCHAR(200) NOT NULL DEFAULT '',
    status               VARCHAR(20)  NOT NULL DEFAULT 'not_started',
        -- choices: not_started | in_progress | done
    created_at           TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
```

```python
class ActionItem(models.Model):
    id                   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    retrospective        = models.ForeignKey(Retrospective, on_delete=models.CASCADE, related_name="action_items")
    card                 = models.ForeignKey(Card, on_delete=models.SET_NULL, blank=True, null=True, related_name="action_items")
    description          = models.TextField()
    assignee             = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_action_items")
    due_date             = models.DateField(blank=True, null=True)
    external_tracker_url = models.URLField(blank=True)
    status               = models.CharField(max_length=20, choices=ActionItemStatus.choices, default=ActionItemStatus.NOT_STARTED)
    created_at           = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
```

> **`assignee_id` no payload da API:** o campo `assignee_id` enviado pelo cliente é o UUID de um `Participant`, não de um `User`. O `ActionItemSerializer.validate()` resolve `Participant → User` e salva `assignee` como FK para `User`. A coluna no banco é `assignee_id UUID NOT NULL REFERENCES users_user(id)`.
>
> **`participant_id` virtual:** o serializer expõe `participant_id` (busca o `Participant` da retro atual para o `assignee`) para a UI saber qual participante corresponde ao action item sem depender de `user_id`.
>
> **`status` legado:** o valor `"pending"` foi substituído por `"not_started"` na migration 0003 (com data migration retroativa). A API (`PreviousActionStatusSerializer`) ainda aceita `"pending"` como alias e o converte para `"not_started"` antes de salvar. O banco não armazena mais `"pending"`.
>
> **Permissões de escrita:** criação apenas pelo facilitador na fase `discussion`; criação bloqueada na fase `actions`. Edição e exclusão pelo facilitador em `discussion` e `actions`.
>
> **Signals:**
> - `pre_save`: captura `_previous_status` para detectar mudança de status.
> - `post_save` (criação): emite `action_created` com o payload serializado completo.
> - `post_save` (atualização): emite `action_updated`. Se `status` mudou, também emite `action_check_updated { action_id, status }`.
> - `post_delete`: emite `action_deleted { action_id }`.

#### Campos virtuais expostos pela API

| Campo virtual | Serializer | Tipo | Lógica |
|---|---|---|---|
| `assignee_name` | `ActionItemSerializer` | `string` | `obj.assignee.name` |
| `participant_id` | `ActionItemSerializer` | `UUID \| null` | busca `Participant.objects.filter(retrospective=obj.retrospective, user=obj.assignee).values_list("id")` |
| `card` (leitura) | `ActionItemSerializer` | `UUID \| null` | `obj.card_id` (read_only); distinto de `card_id` write_only |

---

## Campos virtuais e payloads

Todos os campos que a API expõe mas que não existem como coluna no banco:

| Model | Campo virtual | Tipo retornado | Lógica |
|---|---|---|---|
| `User` | `email` (sobrescrito) | `string` | `display_email`: retorna `public_email` para guest, `email` para normal |
| `Retrospective` | `facilitator_name` | `string` | `facilitator.name` |
| `Retrospective` | `invite_status` | `"active" \| "temporarily_open" \| "blocked"` | calculado com `now` do context |
| `Retrospective` | `entry_expires_at` | `TIMESTAMPTZ \| null` | `invite_temporarily_open_until` quando no futuro |
| `Retrospective` | `focus_card_id` | `UUID \| null` | FK `focus_card_id` exposto diretamente |
| `Retrospective` | `cards_count` | `integer` | anotado via queryset no histórico |
| `Retrospective` | `action_items_count` | `integer` | anotado via queryset no histórico |
| `Retrospective` | `action_item_status_summary` | `object` | contagem por status: `{ not_started, in_progress, done }` |
| `Milestone` | `author_name` | `string` | `author.name` |
| `Participant` | `user_name` | `string` | `user.name` |
| `Participant` | `user_email` | `string` | `user.display_email` |
| `Card` | `author` | `UUID \| null` | `null` quando `is_anonymous=True` |
| `Card` | `author_name` | `string \| null` | `null` quando `is_anonymous=True` |
| `Card` | `author_display` | `string` | `"Anonymous"` ou nome do autor |
| `Card` | `can_edit` | `boolean` | `request.user.id == author_id` |
| `Card` | `group_parent_id` | `UUID \| null` | alias de `group_id` |
| `Card` | `vote_count` | `integer` | anotado via queryset |
| `ActionItem` | `assignee_name` | `string` | `assignee.name` |
| `ActionItem` | `participant_id` | `UUID \| null` | busca `Participant` por `(retrospective, assignee)` |
| `ActionItem` | `card` (leitura) | `UUID \| null` | `card_id` read_only (distinto de `card_id` write_only) |

---

## Divergências identificadas

| # | Divergência | PRD / project-status diz | Código atual |
|---|---|---|---|
| 1 | Status inicial de `ActionItem` | PRD v8/v9 mencionava `"pending"` como status inicial | O model e migration 0003 definem `default="not_started"`; a data migration converteu todos os registros `"pending"` existentes |
| 2 | `assignee` em `ActionItem` | PRD anterior descrevia `assignee` como FK para `User` no payload | A API recebe `assignee_id` como UUID de `Participant`; o serializer resolve para `User` antes de salvar |
| 3 | Payload de agrupamento | Documentação antiga usava `group_card_id` | O código usa `group_parent_id` (serializer `CardGroupingSerializer`) |
| 4 | `votes-config` método e campos | PRD antigo: `GET/PATCH`, alterava `allow_self_vote` | Código: apenas `PUT`, altera somente `max_votes_per_user` |
| 5 | `skip_check_phase` sem efeito | PRDs anteriores diziam que não havia efeito | Tem efeito no frontend (`usePhase.ts`); backend não valida |
| 6 | `state_machine.py` aplicada | PRD dizia que transições lineares eram validadas | O consumer WebSocket não chama `is_valid_transition`; aceita qualquer status válido |
| 7 | Ordem de fases | `state_machine.py` e PRD antigo: `presentation` antes de `check` | `usePhase.ts` e comportamento efetivo: `check` antes de `presentation` |
