# Sprint 4 — Grouping + Voting

## Contexto

Implementa o agrupamento de cards pelo facilitador e o sistema de dot voting restrito às colunas "Loathed" e "Longed For".

Nesta revisão, a sprint é tratada como backend-first, alinhada ao roadmap do repositório. Os contratos de backend para agrupamento e votação pertencem a esta sprint; a renderização visual completa no frontend continua deferida para a Sprint 6.

**Referência no PRD:** Seções 5 (Fluxo), 7 (Design System), 8 (Modelo de Dados), 9 (Eventos WebSocket), 12.3 (Planejamento)

---

## Objetivos

1. Implementar agrupamento por seleção múltipla (facilitador)
2. Implementar dot voting restrito a `loathed`/`longed`
3. Regra de 1 voto por card por participante
4. Implementar `vote.revoked` (desfazer voto)

---

## Entregáveis

### Backend (Django)

- [x] **App `cards` — Agrupamento API:**
  - `POST /api/retrospectives/{id}/cards/group/` — Agrupar cards selecionados
    - Payload: `card_ids` (lista de UUIDs), `group_parent_id` (UUID do card pai, ou null para usar primeiro da lista)
    - Apenas facilitador
    - Cards só podem ser agrupados com outros da **mesma coluna**
    - Validação: todos os cards devem estar na mesma coluna
  - `POST /api/retrospectives/{id}/cards/{card_id}/ungroup/` — Desagrupar card
    - Apenas facilitador
    - Remove `group` do card

- [x] **App `cards` — Agrupamento WebSocket events:**
  - `card.grouped` — Server → Clients: `{card_id, group_id}`
  - `card.ungrouped` — Server → Clients: `{card_id, previous_group_id}`

- [x] **Validações de agrupamento:**
  - Cards agrupados são exibidos aninhados sob o card pai
  - Modelo `Card.group` (FK para 'self', nullable) armazena relação
  - Facilitador pode desagrupar cards individualmente

- [x] **App `cards` — Votação API:**
  - `POST /api/retrospectives/{id}/cards/{card_id}/vote/` — Votar em card
    - Apenas cards das colunas `loathed` e `longed` são votáveis
    - Máximo de 1 voto por card por participante (`unique_together: (card, voter)`)
    - Não é possível votar no próprio card
    - Verifica `votes_remaining` no model `Participant`
    - Decrementa `votes_remaining` ao votar
  - `DELETE /api/retrospectives/{id}/cards/{card_id}/vote/` — Desfazer voto
    - Restaura `votes_remaining` do participante
    - Remove `CardVote`
  - `GET /api/retrospectives/{id}/votes/` — Listar votos da sessão

- [x] **App `cards` — Votação WebSocket events:**
  - `vote.cast` — Server → Clients: `{card_id, voter_id, votes_remaining}`
  - `vote.revoked` — Server → Clients: `{card_id, voter_id, votes_remaining}`

- [x] **Fase `grouping`:**
  - Sem cronômetro (facilitador avança manualmente)
  - Apenas facilitador vê controles de agrupamento
  - Seleção múltipla via checkboxes fica a cargo do frontend na Sprint 6

- [x] **Fase `voting`:**
  - Cronômetro ativo (duração padrão: 5 min)
  - Contador de votos restantes deve ser exposto pelo backend e consumido pelo frontend na Sprint 6
  - Indicador visual "Seu card — não votável" fica a cargo do frontend na Sprint 6

- [x] **Configuração de votos (API):**
  - `PUT /api/retrospectives/{id}/votes-config/` — Configurar votos
    - Payload: `max_votes_per_user` (inteiro, 1-10, default: 3)
    - Disponível no lobby ou antes da fase de votação

---

## Requisitos Funcionais Cobertos

| ID | Descrição | Status |
|---|---|---|
| RF-11 | Facilitador agrupa cards da mesma coluna via seleção múltipla | ✅ no backend |
| RF-12 | Dot voting restrito a "Loathed" e "Longed For"; 1 voto/card/pessoa | ✅ no backend |

---

## User Stories Cobertas

| US | Título | Status |
|---|---|---|
| US-04 | Configurar dot voting | ✅ no backend |
| US-09 | Agrupar cards (Facilitador) | ✅ no backend |
| US-10 | Votar em cards prioritários | ✅ no backend |

---

## Requisitos Não Funcionais

- Latência WebSocket: < 200ms para broadcast de votos
- Validação de 1 voto/card/pessoa enforced no backend (`unique_together`)
- Bloqueio de voto no próprio card na camada de aplicação
- Elementos visuais de agrupamento e votação ficam fora do critério de fechamento desta sprint backend-first

---

## Critérios de Done

- [x] Facilitador pode agrupar cards da mesma coluna via seleção múltipla
- [x] Relação de agrupamento fica representada no backend via `Card.group`
- [x] Facilitador pode desagrupar cards
- [x] Eventos `card.grouped` e `card.ungrouped` broadcast em tempo real
- [x] Participantes podem votar apenas em cards `loathed` e `longed`
- [x] Máximo de 1 voto por card por participante (validado no backend)
- [x] Não é possível votar no próprio card
- [x] Voto pode ser desfeito enquanto fase de votação está aberta
- [x] `votes_remaining` é atualizado e broadcast em tempo real pelo backend
- [x] Eventos `vote.cast` e `vote.revoked` broadcast em tempo real
- [x] `python manage.py test` passa sem falhas
- [x] `ruff check .` sem erros

## Estado Atual

- O backend já oferece endpoints de agrupamento, desagrupamento, voto, revogação de voto, listagem de votos e configuração de votos.
- O consumer e os signals já cobrem `card.grouped`, `card.ungrouped`, `vote.cast` e `vote.revoked`.
- A integração visual de grouping e voting no frontend permanece deferida para a Sprint 6.

## Itens Deferidos

- Checkboxes de seleção múltipla e controles visuais de agrupamento no frontend
- Contador visual de votos restantes e indicador "Seu card — não votável" no frontend
- Renderização visual de grupos aninhados e feedback de votação no cliente

---

## Handoff

Ao finalizar, gerar rascunho do `SPRINT_5_HANDOFF.md` seguindo estrutura definida no PRD seção 12.2.

---

## Referências do PRD

- Seção 5: Fluxo da Sessão (fases Grouping e Voting)
- Seção 7: Design System (RetroCard com checkbox, VoteBadge)
- Seção 8: Modelo de Dados (CardVote, Card.group)
- Seção 9: Eventos WebSocket (card.grouped, card.ungrouped, vote.cast, vote.revoked)
- Seção 13.8: Trade-off Agrupamento restrito ao facilitador
- Seção 13.9: Trade-off Votação restrita a "Loathed" e "Longed For"
- Seção 13.10: Trade-off 1 voto por card por participante
