# Sprint 3 — Board 4L + Milestones

## Contexto

Implementa o core da retrospectiva: CRUD de cards com broadcast em tempo real, sistema de marcos (milestones) do facilitador e board 4 colunas funcional.

**Referência no PRD:** Seções 5 (Fluxo), 7 (Design System), 8 (Modelo de Dados), 12.3 (Planejamento)

---

## Objetivos

1. Implementar CRUD completo de cards com broadcast WebSocket
2. Implementar modelo `Milestone` e endpoints de criação/edição/exclusão
3. Implementar preparação de marcos (fase `setup`)
4. Implementar apresentação de marcos (fase `presentation`)
5. Implementar `MilestoneBar` visível durante toda a sessão

---

## Entregáveis

### Backend (Django)

- [ ] **App `cards` — API REST:**
  - `POST /api/retrospectives/{id}/cards/` — Criar card
    - Payload: `column` (`loved|loathed|longed|learned`), `content` (máx. 500 chars)
    - Somente participantes da retrospectiva
  - `PUT /api/retrospectives/{id}/cards/{card_id}/` — Editar card
    - Somente o autor do card
  - `DELETE /api/retrospectives/{id}/cards/{card_id}/` — Excluir card
    - Somente o autor do card
  - `GET /api/retrospectives/{id}/cards/` — Listar todos os cards da sessão

- [ ] **App `cards` — WebSocket events:**
  - `card.created` — Server → Clients: `{card}`
  - `card.updated` — Server → Clients: `{card_id, content}`
  - `card.deleted` — Server → Clients: `{card_id}`
  - Validação: autor verifica `request.user == card.author` para edição/exclusão

- [ ] **App `retrospectives` — Milestones API:**
  - `POST /api/retrospectives/{id}/milestones/` — Criar marco
    - Disponível apenas na fase `setup` (preparação)
    - Payload: `category` (`achievement|challenge|change|recognition|other`), `description` (máx. 500)
    - `author` sempre é o facilitador
  - `PUT /api/retrospectives/{id}/milestones/{milestone_id}/` — Editar marco
    - Apenas na fase `setup`
  - `DELETE /api/retrospectives/{id}/milestones/{milestone_id}/` — Excluir marco
    - Apenas na fase `setup`
  - `GET /api/retrospectives/{id}/milestones/` — Listar marcos

- [ ] **WebSocket — Milestone events:**
  - `milestone.created` — Server → Clients: `{milestone}`

- [ ] **Fase `presentation`:**
  - Se não houver marcos, fase é automaticamente pulada → `check`
  - Facilitador controla navegação entre marcos (endpoint ou WebSocket)
  - Participantes visualizam em tempo real, somente leitura
  - Botão "Avançar para Check de Ações" apenas para facilitador
  - Marcos permanecem visíveis como contexto (via `MilestoneBar`) durante fases seguintes

- [ ] **Contexto de marcos persistente:**
  - Marcos visíveis em todas as fases (exceto lobby) como contexto
  - Exibidos em ordem cronológica de criação (`created_at`)

---

## Requisitos Funcionais Cobertos

| ID | Descrição | Status |
|---|---|---|
| RF-06 | Facilitador prepara marcos offline; apresenta no início (fase `presentation`) | ✅ |
| RF-07 | Marcos visíveis como contexto durante toda a sessão (barra colapsável) | ✅ |
| RF-09 | Board com 4 colunas em tempo real; cards com limite de 500 caracteres | ✅ |
| RF-10 | CRUD de cards; somente o autor pode editar/excluir | ✅ |

---

## User Stories Cobertas

| US | Título | Status |
|---|---|---|
| US-07a | Preparar marcos (Facilitador) | ✅ |
| US-07b | Visualizar marcos (Participante) | ✅ |
| US-07c | Apresentar marcos no início da sessão | ✅ |
| US-08 | Adicionar card ao board | ✅ |

---

## Requisitos Não Funcionais

- Limite de 500 caracteres por card e por descrição de marco
- Cards criados aparecem para todos em tempo real (evento `card.created`)
- Cobertura de testes ≥ 80% nos apps `cards` e `retrospectives`

---

## Critérios de Done

- [ ] É possível criar, editar e excluir cards via API
- [ ] Cards são broadcast em tempo real para todos os participantes
- [ ] Somente o autor pode editar/excluir seu card
- [ ] É possível criar, editar e excluir marcos na fase `setup`
- [ ] Fase `presentation` exibe marcos e permite navegação
- [ ] Se não houver marcos, fase `presentation` é pulada automaticamente
- [ ] Marcos são visíveis como contexto nas fases seguintes
- [ ] `python manage.py test` passa sem falhas
- [ ] `ruff check .` sem erros

---

## Handoff

Ao finalizar, gerar rascunho do `SPRINT_4_HANDOFF.md` seguindo estrutura definida no PRD seção 12.2.

---

## Referências do PRD

- Seção 5: Fluxo da Sessão (fases Presentation e Board)
- Seção 7: Design System (RetroCard, MilestoneCard, MilestoneBar, ColumnHeader)
- Seção 8: Modelo de Dados (Card, Milestone)
- Seção 9: Eventos WebSocket (card.created, card.updated, card.deleted, milestone.created)
- Seção 13.7: Trade-off Milestone separado de Card
