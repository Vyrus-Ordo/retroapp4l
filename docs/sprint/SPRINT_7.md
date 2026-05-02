# Sprint 7 — Polish + Quality

## Contexto

Sprint final do MVP. Foca em qualidade, acessibilidade, testes E2E e refinamentos de UX. Inclui o painel de controle de entrada pós-lobby e presença em tempo real.

**Referência no PRD:** Seções 5 (Fluxo), 7 (Design System), 9 (Eventos WebSocket), 11 (Requisitos Não Funcionais), 12.3 (Planejamento)

---

## Objetivos

1. Implementar painel de controle de entrada (bloqueio/reativação pós-lobby)
2. Implementar presença em tempo real aprimorada
3. Escrever testes E2E
4. Atingir cobertura de testes ≥ 80%
5. Validar acessibilidade

---

## Entregáveis

### Backend (Django)

- [ ] **Painel de Controle de Entrada (US-02b):**
  - `POST /api/retrospectives/{id}/reopen-entry/` — Reabre link por 2 minutos
    - Apenas facilitador
    - Apenas quando status diferente de `lobby`
    - Após 2 minutos ou primeiro ingresso, link volta a ser bloqueado automaticamente
    - Ação registrada no `AccessLog`
    - Novo participante recebe `session.snapshot` completo via WebSocket
    - Evento `participant.joined_late` broadcast
  - `GET /api/retrospectives/{id}/invite-status/` — Status do link
    - Retorna: `active`, `blocked`, `temporarily_open` com timestamp de expiração
  - `AccessLog` registra: `link_reopened`, `link_auto_blocked`

- [ ] **Presença em Tempo Real:**
  - Endpoint: `GET /api/retrospectives/{id}/presence/` — Lista participantes online
  - WebSocket event: `participant.joined` e `participant.left` atualizam lista
  - Heartbeat ou ping/pong para detectar desconexões
  - Painel de participantes (ParticipantPanel) atualizado em tempo real

- [ ] **Testes Unitários e de Integração:**
  - Cobertura ≥ 80% nos apps `retrospectives`, `cards`, `actions`
  - Testes de:
    - Criação de sessão com `team_key`
    - Transições de fases (máquina de estados)
    - Cronômetro (pausa, retoma, expiração)
    - CRUD de cards com permissões (autor vs não-autor)
    - Agrupamento de cards (mesma coluna, facilitador only)
    - Votação (1 voto/card, não no próprio card, colunas restritas)
    - Action items (criação, vínculo com card)
    - Check de ações anteriores (mesmo `team_key`, última retro closed)
    - Link de convite (geração, revogação, reabertura, bloqueio)
  - Testes de WebSocket com `pytest-channels`

- [ ] **CI/CD (GitHub Actions):**
  - Gerar `.github/workflows/ci.yml`:
    - Lint: `ruff check .`
    - Testes: `python manage.py test`
    - Build Docker: verifica Dockerfile
  - Tech Lead executa e valida

### Frontend (Nuxt 3)

- [ ] **ParticipantPanel aprimorado:**
  - Seção de administração visível apenas para facilitador
  - Status do link em tempo real (ativo/bloqueado/temporariamente aberto)
  - Botão "Allow new entry" com countdown de 2 minutos
  - Access log visível no painel (entradas, saídas, reaberturas)

- [ ] **Testes E2E:**
  - Fluxo completo de criação de sessão → lobby → apresentação → board → votação → debate → ações → encerramento
  - Fluxo de participante (entrar via link, criar card, votar, registrar action item)
  - Fluxo de agrupamento (facilitador agrupa/desagrupa)
  - Teste de cronômetro (expiração, pausa)
  - Ferramenta: Playwright ou Cypress

- [ ] **Acessibilidade:**
  - Validação com Lighthouse (Performance, Accessibility, Best Practices ≥ 90)
  - Navegação por teclado em todos componentes interativos
  - Screen reader labels em inputs e botões
  - Contraste AA validado

- [ ] **Refinamentos de UX:**
  - Mensagens de erro factuais e diretas (ex: "This field is required.")
  - Loading states em todas as operações assíncronas
  - Toast notifications para eventos importantes (card criado, voto registrado, fase avançada)
  - Confirmação de encerramento com aviso sobre action items sem responsável

---

## Requisitos Funcionais Cobertos

| ID | Descrição | Status |
|---|---|---|
| RF-03 | Gerenciar entrada de participantes após o início (US-02b) | ✅ |
| RF-16 | Presença em tempo real aprimorada | ✅ |

---

## User Stories Cobertas

| US | Título | Status |
|---|---|---|
| US-02b | Gerenciar entrada de participantes após o início | ✅ |

---

## Requisitos Não Funcionais

- Cobertura de testes ≥ 80% em `retrospectives`, `cards`, `actions`
- Lighthouse Accessibility ≥ 90
- Todos os testes E2E passando
- `python manage.py test` sem falhas
- `ruff check .` sem erros
- `eslint` + `prettier` sem erros

---

## Critérios de Done

- [ ] Painel de controle de entrada funciona (bloqueio, reabertura temporária, auto-bloqueio)
- [ ] AccessLog registra todas as ações de entrada/saída
- [ ] Presença em tempo real atualizada via WebSocket
- [ ] Cobertura de testes ≥ 80% nos apps core
- [ ] Testes E2E cobrem fluxos principais
- [ ] Lighthouse Accessibility ≥ 90
- [ ] CI/CD configurado (GitHub Actions)
- [ ] `python manage.py test` passa sem falhas
- [ ] `ruff check .` sem erros
- [ ] `eslint` + `prettier` sem erros
- [ ] `npm run build` sem erros

---

## Handoff

Ao finalizar, gerar rascunho do `SPRINT_8_HANDOFF.md` e documento de handoff final do MVP. O documento final deve incluir:

- Estado completo do repositório
- Instruções de deploy (Fly.io, Neon, Upstash, Vercel)
- Variáveis de ambiente necessárias
- Lista de features implementadas vs. fora do escopo do MVP
- Métricas de qualidade (cobertura, Lighthouse)
- Próximos passos (Sprint 8: Integrações futuras)

---

## Referências do PRD

- Seção 5: Fluxo da Sessão
- Seção 7.8: ParticipantPanel (mock completo)
- Seção 9: Eventos WebSocket (participant.joined, participant.left, participant.joined_late)
- Seção 11.5: Qualidade de código
- Seção 11.6: Acessibilidade e UI
- Seção 12.2: Estrutura obrigatória do handoff
- Seção 13.11: Trade-off Bloqueio de entrada pós-lobby
