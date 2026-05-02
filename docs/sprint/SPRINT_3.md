# Sprint 3 — Board 4L + Milestones

## Contexto

Implementa o core da retrospectiva: CRUD de cards com broadcast em tempo real, sistema de marcos (milestones) do facilitador e board 4 colunas funcional.

Nesta revisão, a sprint fica formalmente tratada como backend-first, alinhada ao planejamento macro do repositório. A implementação visual do board, da MilestoneBar e do consumo frontend fica deferida para a Sprint 6, desde que o backend entregue os contratos necessários.

**Referência no PRD:** Seções 5 (Fluxo), 7 (Design System), 8 (Modelo de Dados), 12.3 (Planejamento)

---

## Objetivos

1. Implementar CRUD completo de cards com broadcast WebSocket
2. Implementar modelo `Milestone` e endpoints de criação/edição/exclusão
3. Implementar preparação de marcos (fase `setup`)
4. Implementar apresentação de marcos (fase `presentation`)
5. Entregar contratos backend para futura MilestoneBar e board visual na Sprint 6

---

## Entregáveis

### Backend (Django)

- [x] **App `cards` — API REST:**
  - `POST /api/retrospectives/{id}/cards/` — Criar card
    - Payload: `column` (`loved|loathed|longed|learned`), `content` (máx. 500 chars)
    - Somente participantes da retrospectiva
  - `PUT /api/retrospectives/{id}/cards/{card_id}/` — Editar card
    - Somente o autor do card
  - `DELETE /api/retrospectives/{id}/cards/{card_id}/` — Excluir card
    - Somente o autor do card
  - `GET /api/retrospectives/{id}/cards/` — Listar todos os cards da sessão

- [x] **App `cards` — WebSocket events:**
  - `card.created` — Server → Clients: `{card}`
  - `card.updated` — Server → Clients: `{card_id, content}`
  - `card.deleted` — Server → Clients: `{card_id}`
  - Validação: autor verifica `request.user == card.author` para edição/exclusão

- [x] **App `retrospectives` — Milestones API:**
  - `POST /api/retrospectives/{id}/milestones/` — Criar marco
    - Disponível apenas na fase `setup` (preparação)
    - Payload: `category` (`achievement|challenge|change|recognition|other`), `description` (máx. 500)
    - `author` sempre é o facilitador
  - `PUT /api/retrospectives/{id}/milestones/{milestone_id}/` — Editar marco
    - Apenas na fase `setup`
  - `DELETE /api/retrospectives/{id}/milestones/{milestone_id}/` — Excluir marco
    - Apenas na fase `setup`
  - `GET /api/retrospectives/{id}/milestones/` — Listar marcos

- [x] **WebSocket — Milestone events:**
  - `milestone.created` — Server → Clients: `{milestone}`

- [x] **Fase `presentation`:**
  - Se não houver marcos, fase é automaticamente pulada → `check`
  - Facilitador controla navegação entre marcos (endpoint ou WebSocket)
  - Participantes visualizam em tempo real, somente leitura
  - O botão visual "Avançar para Check de Ações" fica a cargo do frontend na Sprint 6
  - O backend já expõe milestones para consumo futuro do frontend

- [x] **Contexto de marcos persistente no backend:**
  - Marcos disponíveis para consumo em ordem cronológica de criação (`created_at`)
  - Renderização persistente via MilestoneBar deferida para a Sprint 6

---

## Requisitos Funcionais Cobertos

| ID | Descrição | Status |
|---|---|---|
| RF-06 | Facilitador prepara marcos offline; apresenta no início (fase `presentation`) | ✅ |
| RF-07 | Marcos visíveis como contexto durante toda a sessão (barra colapsável) | Deferido para Sprint 6 |
| RF-09 | Board com 4 colunas em tempo real; cards com limite de 500 caracteres | ✅ no backend |
| RF-10 | CRUD de cards; somente o autor pode editar/excluir | ✅ |

---

## User Stories Cobertas

| US | Título | Status |
|---|---|---|
| US-07a | Preparar marcos (Facilitador) | ✅ |
| US-07b | Visualizar marcos (Participante) | Deferido para Sprint 6 |
| US-07c | Apresentar marcos no início da sessão | ✅ |
| US-08 | Adicionar card ao board | ✅ |

---

## Requisitos Não Funcionais

- Limite de 500 caracteres por card e por descrição de marco
- Cards criados aparecem para todos em tempo real (evento `card.created`)
- Cobertura de testes ≥ 80% nos apps `cards` e `retrospectives` ainda não comprovada no repositório
- Frontend e design system não fazem parte do critério de fechamento desta sprint backend-first

---

## Critérios de Done

- [x] É possível criar, editar e excluir cards via API
- [x] Cards são broadcast em tempo real para todos os participantes
- [x] Somente o autor pode editar/excluir seu card
- [x] É possível criar, editar e excluir marcos na fase `setup`
- [x] Fase `presentation` exibe marcos e permite navegação
- [x] Se não houver marcos, fase `presentation` é pulada automaticamente
- [x] Marcos ficam disponíveis no backend para contexto nas fases seguintes
- [x] `python manage.py test` passa sem falhas
- [x] `ruff check .` sem erros


## Itens Deferidos

- MilestoneBar visual e persistente no frontend
- Renderização do board 4L no frontend
- Integração frontend-backend via WebSocket para experiência completa da sessão

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
