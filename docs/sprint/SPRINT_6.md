# Sprint 6 — Frontend

## Contexto

Implementa toda a interface do usuário com Nuxt 3 + Tailwind CSS, seguindo rigorosamente o design system definido na seção 7 do PRD.

**Referência no PRD:** Seção 7 (Design System — fonte de verdade visual), Seção 5 (Fluxo da Sessão), Seção 9 (Eventos WebSocket)

---

## Objetivos

1. Setup do projeto Nuxt 3 + Tailwind CSS
2. Implementar todas as telas e componentes seguindo o design system
3. Integrar frontend com API REST e WebSocket do backend
4. Implementar alerta sonoro do cronômetro (Web Audio API)

---

## Entregáveis

### Frontend (Nuxt 3 + Tailwind CSS)

- [ ] **Setup do projeto:**
  - Nuxt 3 (Vue 3) — modo SPA
  - Tailwind CSS 3.x configurado
  - `tailwind.config.ts` com tokens customizados:
    ```typescript
    colors: {
      brand: { 50: '#eff6ff', 100: '#dbeafe', 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8' },
      success: { 50: '#f0fdf4', 500: '#22c55e', 600: '#16a34a' },
      warning: { 50: '#fff7ed', 500: '#f97316', 600: '#ea580c' },
      danger: { 50: '#fef2f2', 500: '#ef4444', 600: '#dc2626' },
    }
    ```
  - Google Fonts: Inter (pesos 400, 500, 600, 700)
  - `@heroicons/vue` instalado

- [ ] **Estrutura de pastas:**
  ```
  frontend/
  ├── assets/css/          # tailwind.css
  ├── components/
  │   ├── layout/          # Header, Footer, Sidebar
  │   ├── retro/           # RetroCard, MilestoneCard, PhaseChip, VoteBadge, TimerDisplay
  │   ├── board/           # ColumnHeader, BoardGrid, FocusCard
  │   ├── participants/    # ParticipantPanel
  │   └── forms/           # Modal de criar card, action item form
  ├── composables/         # useWebSocket, useTimer, useAuth, usePhase
  ├── pages/
  │   ├── index.vue        # Dashboard (home)
  │   ├── auth/
  │   │   ├── login.vue
  │   │   └── register.vue
  │   ├── retro/
  │   │   ├── create.vue   # Criar sessão (setup)
  │   │   ├── [id].vue     # Sessão ativa (layout principal)
  │   │   └── invite/[token].vue  # Join via link
  │   └── history/
  │       ├── index.vue    # Dashboard de histórico
  │       └── [id].vue     # Detalhes de retro encerrada
  ├── stores/              # Pinia stores (auth, retro, timer, participants)
  ├── middleware/          # auth.global.ts
  └── utils/               # sound.ts (Web Audio API), validation.ts
  ```

- [ ] **Componentes UI (Seção 7.8 do PRD — obrigatório):**
  - `RetroCard` — classes Tailwind: `bg-white border border-slate-100 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow duration-150`
  - `MilestoneCard` — classes Tailwind: `bg-white border border-slate-100 rounded-lg p-4`
  - `PhaseChip` — classes: `bg-brand-50 text-brand-500 text-xs font-semibold rounded px-2 py-1`
  - `VoteBadge` — classes: `text-brand-500 text-xs font-semibold`
  - `TimerDisplay` — Normal: `text-xl font-semibold text-slate-900`; Alerta (<60s): `text-warning-500`; Crítico (<30s): `text-danger-500`
  - `ParticipantPanel` — conforme mock da seção 7.8
  - `MilestoneBar` — classes: `bg-slate-50 border-b border-slate-100 px-8 py-2 flex gap-4 flex-wrap text-sm`
  - `ColumnHeader` — background com cor semântica da coluna; título: `text-xs font-semibold uppercase tracking-wide text-white`
  - `FocusCard` — conforme mock da seção 7.8 (Debate)

- [ ] **Mapeamento de cores por coluna (Seção 7.3):**
  | Coluna | Cor do header | Cor do badge |
  |---|---|---|
  | Liked (Loved) | `success-600` | `success-50` |
  | Loathed | `warning-500` | `warning-50` |
  | Longed For | `brand-500` | `brand-50` |
  | Learned | `slate-600` | `slate-50` |

- [ ] **Ícones (Heroicons — Seção 7.7):**
  - Todos os ícones mapeados conforme tabela do PRD
  - Variante `outline` preferida; `solid` para estados ativos
  - Tamanho: `w-5 h-5` padrão; `w-4 h-4` inline

- [ ] **Telas / Páginas:**
  - **Login / Register** — Auth local (e-mail/senha) + botões OAuth (Google, GitHub)
  - **Dashboard (Home)** — Botão "Create retrospective", lista de retros recentes
  - **Create Retro (`setup`)** — Form: `title`, `sprint_name`, `team_key` (dropdown com sugestões), milestones CRUD
  - **Lobby** — Link de convite (copiar), lista de participantes esperando, botão "Start session"
  - **Presentation** — Tela de apresentação de marcos, navegação por facilitador, botão "Advance to Action Check"
  - **Check de Ações** — Lista de ações anteriores, checkboxes de status para cada participante
  - **Board 4L** — 4 colunas com cards, adicionar card, MilestoneBar no topo
  - **Grouping** — Board com checkboxes nos cards, botão "Group selected", "Ungroup"
  - **Voting** — Board com botões de voto em `loathed`/`longed`, contador de votos restantes
  - **Discussion** — Cards ordenados por votos, card em foco destacado, navegação entre cards
  - **Actions** — Form para criar action items (descrição, responsável, prazo)
  - **Close** — Botão de encerramento com confirmação
  - **History** — Lista de retros encerradas, filtro por `team_key`
  - **History Detail** — Detalhes de uma retro encerrada

- [ ] **WebSocket Integration (`composables/useWebSocket.ts`):**
  - Conexão WebSocket com JWT auth
  - Handlers para todos os eventos da seção 9 do PRD
  - Reconexão automática com backoff exponencial
  - Recebe `session.snapshot` ao conectar/reconectar

- [ ] **Composables:**
  - `useWebSocket()` — Gerencia conexão e eventos
  - `useTimer()` — Interpola contagem regressiva local (1s) e corrige com `timer.sync` (5s)
  - `useAuth()` — Gerencia estado de autenticação (token, usuário)
  - `usePhase()` — Estado atual da fase, transições, permissões (facilitador vs participante)

- [ ] **Pinia Stores:**
  - `authStore` — Token, usuário, login/logout
  - `retroStore` — Estado da sessão, cards, votes, milestones, action items
  - `timerStore` — Estado do cronômetro, pausa, expiração
  - `participantStore` — Lista de participantes online

- [ ] **Alerta Sonoro (Web Audio API):**
  - Tons senoidais ao final do cronômetro (`timer.expired`)
  - Configuração: frequência, duração, número de beeps
  - Arquivo: `utils/sound.ts`

- [ ] **Estados de Interação (Seção 7.6):**
  - Hover: `hover:bg-brand-600` (sólido), `hover:bg-slate-100` (ghost)
  - Pressed: `active:bg-brand-700`
  - Disabled: `disabled:bg-slate-100 disabled:text-slate-300 disabled:cursor-not-allowed`
  - Focus: `focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black`

- [ ] **Responsividade:**
  - Desktop 1280px+ (primário)
  - Tablet 768px (secundário)
  - Mobile: layout empilhado para board

---

## Requisitos Não Funcionais

- Contraste mínimo AA entre texto e background
- `:focus-visible` em todos os componentes interativos
- Animações limitadas a `color`, `background`, `opacity` com `duration-150`
- Sem bounces ou transforms de layout

---

## Critérios de Done

- [ ] Todas as telas implementadas conforme design system
- [ ] Todos os componentes UI (RetroCard, MilestoneCard, PhaseChip, etc.) seguem classes definidas
- [ ] Conexão WebSocket funcional com reconexão automática
- [ ] Cronômetro interpola localmente e corrige com `timer.sync`
- [ ] Alerta sonoro dispara ao final do cronômetro
- [ ] Layout responsivo (desktop 1280px+, tablet 768px)
- [ ] Acessibilidade: `:focus-visible` em todos componentes, contraste AA
- [ ] Frontend comunica com API REST e WebSocket do backend
- [ ] `eslint` + `prettier` sem erros
- [ ] `npm run build` sem erros

---

## Handoff

Ao finalizar, gerar rascunho do `SPRINT_7_HANDOFF.md` seguindo estrutura definida no PRD seção 12.2.

---

## Referências do PRD

- Seção 7: Design System (fonte de verdade completa)
- Seção 7.3: Paleta de cores
- Seção 7.4: Espaçamento
- Seção 7.5: Bordas, raios e sombras
- Seção 7.6: Estados de interação
- Seção 7.7: Iconografia
- Seção 7.8: Componentes UI específicos
- Seção 7.9: Layout do board
- Seção 7.10: Regras de voz e conteúdo
- Seção 9: Eventos WebSocket
