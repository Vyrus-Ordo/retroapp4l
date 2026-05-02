# Sprint 4 — Grouping + Voting

## Contexto

Implementa o agrupamento de cards pelo facilitador e o sistema de dot voting restrito às colunas "Loathed" e "Longed For".

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

- [ ] **App `cards` — Agrupamento API:**
  - `POST /api/retrospectives/{id}/cards/group/` — Agrupar cards selecionados
    - Payload: `card_ids` (lista de UUIDs), `group_parent_id` (UUID do card pai, ou null para usar primeiro da lista)
    - Apenas facilitador
    - Cards só podem ser agrupados com outros da **mesma coluna**
    - Validação: todos os cards devem estar na mesma coluna
  - `POST /api/retrospectives/{id}/cards/{card_id}/ungroup/` — Desagrupar card
    - Apenas facilitador
    - Remove `group` do card

- [ ] **App `cards` — Agrupamento WebSocket events:**
  - `card.grouped` — Server → Clients: `{card_id, group_id}`
  - `card.ungrouped` — Server → Clients: `{card_id, previous_group_id}`

- [ ] **Validações de agrupamento:**
  - Cards agrupados são exibidos aninhados sob o card pai
  - Modelo `Card.group` (FK para 'self', nullable) armazena relação
  - Facilitador pode desagrupar cards individualmente

- [ ] **App `cards` — Votação API:**
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

- [ ] **App `cards` — Votação WebSocket events:**
  - `vote.cast` — Server → Clients: `{card_id, voter_id, votes_remaining}`
  - `vote.revoked` — Server → Clients: `{card_id, voter_id, votes_remaining}`

- [ ] **Fase `grouping`:**
  - Sem cronômetro (facilitador avança manualmente)
  - Apenas facilitador vê controles de agrupamento
  - Seleção múltipla via checkboxes (visíveis apenas para facilitador)

- [ ] **Fase `voting`:**
  - Cronômetro ativo (duração padrão: 5 min)
  - Contador de votos restantes visível e atualizado em tempo real
  - Indicador "Seu card — não votável" em cards do próprio autor

- [ ] **Configuração de votos (API):**
  - `PUT /api/retrospectives/{id}/votes-config/` — Configurar votos
    - Payload: `max_votes_per_user` (inteiro, 1-10, default: 3)
    - Disponível no lobby ou antes da fase de votação

---

## Requisitos Funcionais Cobertos

| ID | Descrição | Status |
|---|---|---|
| RF-11 | Facilitador agrupa cards da mesma coluna via seleção múltipla | ✅ |
| RF-12 | Dot voting restrito a "Loathed" e "Longed For"; 1 voto/card/pessoa | ✅ |

---

## User Stories Cobertas

| US | Título | Status |
|---|---|---|
| US-04 | Configurar dot voting | ✅ |
| US-09 | Agrupar cards (Facilitador) | ✅ |
| US-10 | Votar em cards prioritários | ✅ |

---

## Requisitos Não Funcionais

- Latência WebSocket: < 200ms para broadcast de votos
- Validação de 1 voto/card/pessoa enforced no backend (`unique_together`)
- Bloqueio de voto no próprio card na camada de aplicação

---

## Critérios de Done

- [ ] Facilitador pode agrupar cards da mesma coluna via seleção múltipla
- [ ] Cards agrupados são exibidos aninhados sob o card pai
- [ ] Facilitador pode desagrupar cards
- [ ] Eventos `card.grouped` e `card.ungrouped` broadcast em tempo real
- [ ] Participantes podem votar apenas em cards `loathed` e `longed`
- [ ] Máximo de 1 voto por card por participante (validado no backend)
- [ ] Não é possível votar no próprio card
- [ ] Voto pode ser desfeito enquanto fase de votação está aberta
- [ ] Contador de votos restantes atualizado em tempo real
- [ ] Eventos `vote.cast` e `vote.revoked` broadcast em tempo real
- [ ] `python manage.py test` passa sem falhas
- [ ] `ruff check .` sem erros

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
