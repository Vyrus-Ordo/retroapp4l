# Sprint 8 — Integrations (Future)

## Contexto

Sprint de funcionalidades pós-MVP. Inclui integrações com rastreadores externos, exportação de dados e analytics de tendências entre sprints. Estas features estavam explicitamente fora do escopo do MVP.

**Referência no PRD:** Seção 1.4 (Fora do Escopo do MVP), Seção 12.3 (Planejamento)

---

## Objetivos

1. Integrações com rastreadores externos de tarefas (Linear, GitHub Issues)
2. Exportação em PDF, CSV e/ou DOCX
3. Relatórios e analytics de tendências entre sprints
4. Drag-and-drop para agrupamento de cards (fase 2)

---

## Entregáveis

### Integrações com Rastreadores Externos

- [ ] **Linear Integration:**
  - OAuth app registration
  - Endpoint para vincular retrospectiva a workspace Linear
  - Criar issues no Linear a partir de action items
  - Sync de status (pending → in_progress → done)

- [ ] **GitHub Issues Integration:**
  - OAuth app registration
  - Endpoint para vincular repositório GitHub
  - Criar issues no GitHub a partir de action items
  - Sync de status

- [ ] **Abstraction layer:**
  - Interface `TaskTracker` para adicionar novos provedores
  - Factory pattern para instanciar provider correto
  - Configuração por time/retrospectiva

### Exportação

- [ ] **PDF Export:**
  - Relatório de retrospectiva com cards, votos, marcos e action items
  - Layout limpo e profissional

- [ ] **CSV Export:**
  - Export de cards e action items
  - Colunas: coluna, conteúdo, autor, votos, action items vinculados

- [ ] **DOCX Export (opcional):**
  - Template de relatório em Word

### Analytics e Tendências

- [ ] **Dashboard de Tendências:**
  - Gráfico de action items completados ao longo do tempo (por `team_key`)
  - Métricas: taxa de conclusão, tempo médio de conclusão
  - Comparação entre sprints

- [ ] **Endpoints de Analytics:**
  - `GET /api/teams/{team_key}/analytics/` — Métricas consolidadas
  - `GET /api/teams/{team_key}/trend/` — Dados de tendência por sprint

### Drag-and-Drop (Agrupamento Fase 2)

- [ ] **Frontend:**
  - Drag-and-drop para agrupar cards (em vez de seleção múltipla)
  - Biblioteca: `@vueuse/core` ou `sortablejs`
  - Visual feedback durante drag

- [ ] **Backend:**
  - WebSocket event para drag em tempo real
  - Concorrência: bloqueio otimista ou last-write-wins

---

## Requisitos Funcionais (Novos)

| ID | Módulo | Descrição | Prioridade |
|---|---|---|---|
| RF-18 | Integrações | Exportar action items para Linear | Should Have |
| RF-19 | Integrações | Exportar action items para GitHub Issues | Should Have |
| RF-20 | Exportação | Exportar retrospectiva em PDF/CSV | Could Have |
| RF-21 | Analytics | Dashboard de tendências entre sprints | Could Have |
| RF-22 | Agrupamento | Drag-and-drop para agrupamento | Could Have |

---

## Critérios de Done

- [ ] Integrações com Linear e GitHub Issues funcionais
- [ ] Exportação em PDF e CSV funciona
- [ ] Dashboard de tendências exibe dados históricos
- [ ] Drag-and-drop para agrupamento funciona em tempo real
- [ ] Todos os testes passam
- [ ] `ruff check .` sem erros
- [ ] `eslint` + `prettier` sem erros

---

## Notas

Esta sprint só deve ser iniciada após validação completa do MVP pelas sprints 1-7. Prioridade deve ser definida pelo Tech Lead com base no feedback dos usuários.

---

## Referências do PRD

- Seção 1.4: Fora do Escopo do MVP
- Seção 12.3: Planejamento de Sprints
- Seção 6.2: Infraestrutura (para dimensionar novas integrações)
