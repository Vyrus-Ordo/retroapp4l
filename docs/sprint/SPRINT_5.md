# Sprint 5 — Cycle Closure

## Contexto

Fecha o ciclo da retrospectiva: verificação de ações da sprint anterior, fase de debate com card em foco, registro de itens de ação, encerramento da sessão e dashboard de histórico.

**Referência no PRD:** Seções 5 (Fluxo), 7 (Design System), 8 (Modelo de Dados), 12.3 (Planejamento)

---

## Objetivos

1. Implementar check de ações anteriores (por `team_key`)
2. Implementar action items com status
3. Implementar fase de Debate com card em foco
4. Implementar encerramento de sessão
5. Implementar dashboard de histórico

---

## Entregáveis

### Backend (Django)

- [ ] **App `actions` — Check de Ações Anteriores API:**
  - `GET /api/retrospectives/{id}/previous-actions/` — Buscar ações da última retro do mesmo `team_key`
    - Busca retrospectiva `closed` mais recente com mesmo `team_key`
    - Retorna lista de `ActionItem` da retro anterior
  - `PUT /api/retrospectives/{id}/previous-actions/{action_id}/status/` — Atualizar status de ação anterior
    - Payload: `status` (`done|in_progress|not_started`)
    - Status salvo visível no histórico da retro anterior
    - WebSocket event: `action.check_updated` — `{action_id, status}`

- [ ] **Fase `check`:**
  - Fase opcional, controlada por `skip_check_phase` no model `Retrospective`
  - Cronômetro ativo (duração padrão: 5 min)
  - Exibe lista de action items da última retro com mesmo `team_key`
  - Participantes podem marcar: "Concluída", "Em andamento", "Não iniciada"
  - Se `skip_check_phase=True`, fase é pulada → `board`

- [ ] **App `actions` — Action Items API:**
  - `POST /api/retrospectives/{id}/action-items/` — Criar item de ação
    - Payload: `description` (obrigatório), `assignee_id` (obrigatório, UUID de participante), `due_date` (opcional), `card_id` (opcional, vinculado a card)
  - `PUT /api/retrospectives/{id}/action-items/{action_id}/` — Editar item de ação
  - `DELETE /api/retrospectives/{id}/action-items/{action_id}/` — Excluir item de ação
  - `GET /api/retrospectives/{id}/action-items/` — Listar action items da sessão

- [ ] **Fase `discussion` (Debate):**
  - Cronômetro ativo (duração padrão: 10 min)
  - Cards ordenados por número de votos (decrescente)
  - Destaque visual para os 3-5 mais votados
  - `POST /api/retrospectives/{id}/focus-card/` — Colocar card em foco
    - Apenas facilitador
    - Payload: `card_id`
    - Sinaliza para todos qual ponto está sendo discutido
  - `POST /api/retrospectives/{id}/next-card/` — Avançar para próximo card em foco
    - Apenas facilitador
  - Nenhum CRUD ou votação permitido nesta fase (somente leitura)
  - Controles de cronômetro: pausa/estender/avançar

- [ ] **Fase `actions`:**
  - Cronômetro ativo (duração padrão: 10 min)
  - Registro de itens de ação com descrição, responsável e prazo
  - Dropdown de responsáveis populado com participantes da sessão

- [ ] **Encerramento de Sessão:**
  - `POST /api/retrospectives/{id}/close/` — Encerrar sessão
    - Apenas na fase `actions`
    - Apenas facilitador
    - Muda status para `closed`
    - Define `closed_at`
    - Revoga link de convite automaticamente
    - Confirmação obrigatória com aviso sobre itens de ação sem responsável
    - Registra no `AccessLog` (`action=closed`)

- [ ] **Dashboard de Histórico:**
  - `GET /api/retrospectives/history/` — Listar retrospectivas encerradas do usuário
    - Filtra `status=closed`
    - Ordena por `closed_at` (mais recente primeiro)
    - Inclui: `title`, `sprint_name`, `team_key`, `closed_at`, número de cards, número de action items, status dos action items
  - `GET /api/retrospectives/{id}/detail/` — Detalhes de uma retro encerrada
    - Inclui todos os cards, votos, marcos, action items com status

- [ ] **WebSocket — Discussion events:**
  - Evento para atualização do card em foco: `{card_id, author, column, content, vote_count}`

---

## Requisitos Funcionais Cobertos

| ID | Descrição | Status |
|---|---|---|
| RF-08 | Fase opcional de revisão de action items da retro anterior (mesmo `team_key`) | ✅ |
| RF-13 | Debate com cards ordenados por votos e controle de "card em foco" | ✅ |
| RF-14 | Registrar itens de ação com descrição, responsável e prazo | ✅ |
| RF-15 | Sessões encerradas no dashboard com status dos action items | ✅ |

---

## User Stories Cobertas

| US | Título | Status |
|---|---|---|
| US-05 | Encerrar sessão | ✅ |
| US-06 | Verificar ações anteriores | ✅ |
| US-11 | Registrar item de ação | ✅ |
| US-12 | Conduzir debate focado (Facilitador) | ✅ |

---

## Requisitos Não Funcionais

- Busca de ações anteriores usa mesmo `team_key` e status `closed`
- Dashboard retorna dados em < 300ms

---

## Critérios de Done

- [ ] É possível buscar ações da retro anterior do mesmo `team_key`
- [ ] Participantes podem marcar status de ações anteriores (done/in_progress/not_started)
- [ ] É possível criar action items com descrição, responsável e prazo
- [ ] Fase de debate exibe cards ordenados por votos
- [ ] Facilitador pode colocar card em foco e navegar entre cards
- [ ] Nenhum CRUD ou votação é permitido na fase de debate
- [ ] Facilitador pode encerrar sessão (apenas na fase `actions`)
- [ ] Encerramento muda status para `closed` e aparece no dashboard
- [ ] Dashboard lista retros encerradas com resumo
- [ ] Detalhes de retro encerrada mostram cards, votos, marcos, action items
- [ ] `python manage.py test` passa sem falhas
- [ ] `ruff check .` sem erros

---

## Handoff

Ao finalizar, gerar rascunho do `SPRINT_6_HANDOFF.md` seguindo estrutura definida no PRD seção 12.2.

---

## Referências do PRD

- Seção 5: Fluxo da Sessão (fases Check, Discussion, Actions, Encerrado)
- Seção 7: Design System (FocusCard, PhaseChip, TimerDisplay)
- Seção 8: Modelo de Dados (ActionItem)
- Seção 9: Eventos WebSocket (action.check_updated)
