# RetroApp 4L — Frontend Design System

**Versão:** 2026-06-27
**Source of truth:** código-fonte. Tokens, componentes e comportamentos extraídos diretamente dos arquivos.

---

## 1. Princípios fundamentais

**Dark-first, sem alternativa.** A paleta inteira é construída sobre `#050505` e nunca possui variante clara. Todo componente assume fundo escuro; usar cor de texto ou fundo projetado para light mode quebrará o visual.

**Neon como sinalização, não decoração.** Ciano `#00f2ff` (`--neon-cyan`) é a única cor de acento saturada. Aparece em bordas ativas, timers, fases atuais, botões primários. Tons de opacidade reduzida (`/60`, `/70`, `/30`) marcam estados passivos ou secundários. Usar ciano em múltiplos lugares ao mesmo tempo dilui a hierarquia.

**Glassmorphism discreto.** Superfícies são fundos semi-transparentes (`rgba(255,255,255,0.04)`), não sólidos. A classe `.panel` aplica `backdrop-blur-sm` + borda `--border-default`. Evitar fundos sólidos escuros em componentes internos; preferir transparências sobre o canvas.

**Tempo real primeiro.** Timer, fase atual e participantes são regiões sempre visíveis no workspace. O design do header foi construído para acomodar o timer sem deslocar o logo. Qualquer elemento novo no header deve ser testado com o timer ativo.

**Separação de papel no visual.** Facilitador e participante nunca veem exatamente a mesma tela. Botões de controle (avançar fase, pausar timer, fechar sessão, agrupar) só aparecem para o facilitador. A UI de um participante é intencionalmente mais quieta. Todo componente de fase deve implementar essa bifurcação.

**Hierarquia tipográfica por peso, não por tamanho.** Títulos usam `font-light` (300) para parecerem grandes mas discretos. Labels e metadados usam `uppercase tracking-[0.2em]`. Texto de corpo usa peso 400. Negrito (`font-semibold` ou `font-bold`) é reservado para estados ativos e dados numéricos.

---

## 2. Tokens de design

### 2.1 Paleta de cores

```css
/* ─── Extraído de tailwind.config.ts ─── */

/* Acento neon */
--color-neon-cyan: #00f2ff;

/* Brand (ciano neon com opacidades) */
--color-brand-50:  rgba(0, 242, 255, 0.05);   /* bg hover suave, ToastContainer bg info */
--color-brand-100: rgba(0, 242, 255, 0.10);
--color-brand-200: rgba(0, 242, 255, 0.20);
--color-brand-300: rgba(0, 242, 255, 0.35);   /* border forte, VoteBadge active */
--color-brand-400: rgba(0, 242, 255, 0.55);
--color-brand-500: #00f2ff;                    /* cor pura: texto ativo, bordas de foco */
--color-brand-600: rgba(0, 242, 255, 0.80);   /* text-brand-600 no ToastContainer */
--color-brand-700: rgba(0, 242, 255, 0.60);   /* ícones secundários ciano */
--color-brand-800: rgba(0, 242, 255, 0.40);
--color-brand-900: rgba(0, 242, 255, 0.20);   /* bg-brand-900 em estados hover sutis */

/* Cores semânticas de colunas */
--color-col-loved:   #22c55e;   /* border-left loved column, ColumnHeader title */
--color-col-loathed: #ef4444;   /* border-left loathed column */
--color-col-longed:  #60a5fa;   /* border-left longed column */
--color-col-learned: #a1a1aa;   /* border-left learned column */

/* Success */
--color-success-500: #22c55e;   /* participante online, ClosedView icon */
--color-success-600: #16a34a;   /* convite ativo text, access log joined */
--color-success-700: #15803d;

/* Warning */
--color-warning-500: #f59e0b;   /* timer < 60s, access log reopen */
--color-warning-600: #d97706;

/* Danger */
--color-danger-500: #ef4444;    /* timer < 30s, no assignee text, delete hover */
--color-danger-600: #dc2626;

/* Gray (dark scale — baseados em rgba ou hex zinc) */
--color-gray-50:  rgba(255, 255, 255, 0.03);   /* bg de linhas hover na tabela */
--color-gray-100: rgba(255, 255, 255, 0.06);
--color-gray-200: rgba(255, 255, 255, 0.10);
--color-gray-300: #71717a;
--color-gray-400: #a1a1aa;   /* texto secundário */
--color-gray-500: #d4d4d8;
--color-gray-600: #e4e4e7;
--color-gray-700: #3f3f46;   /* borda desabilitada em button-primary */
--color-gray-800: #27272a;
--color-gray-900: #18181b;
--color-gray-950: #09090b;
```

```css
/* ─── Extraído de tokens.css ─── */

/* Acento neon (primitivos diretos) */
--neon-cyan:      #00f2ff;
--neon-cyan-dim:  rgba(0, 242, 255, 0.12);   /* border-default */
--neon-cyan-mid:  rgba(0, 242, 255, 0.35);   /* border-strong */
--neon-glow:      0 0 16px rgba(0, 242, 255, 0.25);  /* sombra neon usada em button-primary:hover */

/* Acentos semânticos por coluna */
--col-loved:   #22c55e;
--col-loathed: #ef4444;
--col-longed:  #60a5fa;
--col-learned: #a1a1aa;

/* Raw palette */
--ds-brand-500: #00f2ff;
--ds-brand-600: rgba(0, 242, 255, 0.8);
--ds-brand-700: rgba(0, 242, 255, 0.6);
--ds-danger-500: #ef4444;
--ds-success-500: #22c55e;
--ds-warning-500: #f59e0b;
--ds-gray-50:  rgba(255, 255, 255, 0.03);
--ds-gray-100: rgba(255, 255, 255, 0.06);
--ds-gray-200: rgba(255, 255, 255, 0.10);
--ds-gray-300: #71717a;
--ds-gray-400: #a1a1aa;
--ds-gray-500: #d4d4d8;
--ds-gray-600: #e4e4e7;
--ds-gray-700: #3f3f46;
--ds-gray-800: #27272a;
--ds-gray-900: #18181b;
--ds-gray-950: #09090b;
```

### 2.2 Aliases semânticos

Definidos em `tokens.css`:

```css
/* Textos */
--fg-primary:   #ffffff;        /* usado em: títulos, conteúdo de cards, RetroCard.content */
--fg-secondary: #a1a1aa;        /* usado em: subtítulos, button-secondary text */
--fg-tertiary:  #52525b;        /* usado em: placeholders (.field-input::placeholder) */

/* Fundos */
--bg-canvas:    #050505;        /* usado em: body, AppHeader bg, AppFooter bg */
--bg-surface:   rgba(255, 255, 255, 0.04);  /* usado em: .panel background */
--bg-primary:   rgba(0, 242, 255, 0.05);    /* aparentemente não usado em componentes — shadowiado por brand-50 */
--bg-secondary: rgba(255, 255, 255, 0.03);  /* aparentemente não usado diretamente em componentes */

/* Bordas */
--border-default: rgba(0, 242, 255, 0.12);  /* usado em: .panel, .field-input, body da borda */
--border-strong:  rgba(0, 242, 255, 0.35);  /* usado em: .button-primary borda */
```

> ⚠️ `--bg-primary` e `--bg-secondary` estão definidos mas nos componentes os fundos são aplicados inline com os valores literais ou via classes Tailwind (`bg-brand-50`, `rgba(0,242,255,0.04)`), não via `var(--bg-primary)`.

### 2.3 Tipografia

**Famílias declaradas** (`tailwind.config.ts`):

```typescript
fontFamily: {
  sans: ["Poppins", "sans-serif"],
  mono: ['"JetBrains Mono"', "monospace"],
}
```

**Carregamento** (`tailwind.css` linha 1):
```css
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;600&display=swap');
```

Ambas as famílias carregadas via Google Fonts. Sem fallback local declarado além de `sans-serif` / `monospace`.

**Configuração base do body:**
```css
font-size: 1rem;
font-weight: 400;
letter-spacing: -0.01em;
line-height: 1.5;
```

**Pesos usados nos componentes:**

| Peso | Classe Tailwind | Onde aparece |
|---|---|---|
| 300 (light) | `font-light` | Títulos de tela (`h1`), nomes de participantes, labels de coluna, subtítulos, `AppHeader` nav links, logo |
| 400 (regular) | default / `font-normal` | Corpo de texto, conteúdo de cards |
| 500 (medium) | `font-medium` | `.button-primary`, `.button-secondary`, badge de fase atual na PhaseCarousel |
| 600 (semibold) | `font-semibold` | AvatarCircle initials, badge de votos no DiscussionView, `AppHeader` initials |
| 700 (bold) | `font-bold` | Não encontrado em uso direto nos componentes lidos |

**Onde JetBrains Mono é aplicado diretamente:**
- `AppHeader` logo (`style="font-family: 'JetBrains Mono', monospace"`)
- `RetroHeader` logo (mesmo inline style)
- `index.vue` hero section (`font-['JetBrains_Mono',_'Poppins',_sans-serif]`)
- `TimerDisplay` — via classe Tailwind `font-mono` (`text-xl font-mono font-semibold`)
- Campos de código de convite (`font-mono text-xs` no `ParticipantPanel` e `LobbyView`)

**Sem escala de tamanhos customizada** — usa os defaults do Tailwind (xs, sm, base, lg, xl, 2xl, 3xl, etc.).

### 2.4 Espaçamento

Tailwind defaults — nenhuma extensão de `spacing` em `tailwind.config.ts`.

Valores mais recorrentes nos componentes lidos:

| Categoria | Valores mais usados |
|---|---|
| Padding de painéis | `p-4`, `p-6`, `p-8` (`lg:p-8`) |
| Gaps de grid/flex | `gap-2`, `gap-3`, `gap-4`, `gap-6`, `gap-8` |
| Margin entre seções | `mt-2`, `mt-3`, `mt-4`, `mt-6` |
| Padding de botões | `px-4 py-3` (default em `.button-primary`/`.button-secondary`), `py-1.5` (compact) |
| Padding de inputs | `px-4 py-3` (`.field-input`) |

### 2.5 Bordas, raios e sombras

**Raios de borda** — sem customização em `tailwind.config.ts`; usa defaults Tailwind.

Raios usados nos componentes:
- `rounded-xl` — painéis, cards, modais, CardComposer, ActionItemForm
- `rounded-lg` — campos, linhas de ação, ColumnBox
- `rounded-full` — badges de fase, VoteBadge, AvatarCircle, pill buttons
- `rounded-md` — links de navegação no AppHeader
- `rounded` — botão dismiss do toast

**Sombras customizadas** (`tailwind.config.ts`):

```typescript
boxShadow: {
  card:     "0 0 0 1px rgba(0,242,255,0.08)",   /* não encontrado em uso nos componentes */
  "card-md": "0 0 16px rgba(0,242,255,0.12)",   /* não encontrado em uso nos componentes */
  glow:     "0 0 16px rgba(0,242,255,0.25)",    /* usado em: button-primary:hover, stepper pill atual, allow-entry button hover */
  "glow-lg": "0 0 32px rgba(0,242,255,0.40)",   /* aparentemente não usado nos componentes */
}
```

> ⚠️ `shadow-card` e `shadow-card-md` definidos em `tailwind.config.ts` mas não encontrados em uso nos componentes. `shadow-glow` é o único shadow customizado com uso real.

### 2.6 Animações

**Nenhuma animação declarada em `tailwind.config.ts`.**

Animações existentes são definidas localmente como `<style scoped>`:

| Nome | Onde | Efeito | Duração |
|---|---|---|---|
| `spin` (keyframe local) | `SetupView.vue` | Rotação do ícone MDI cog-outline enquanto em fase `setup` | `1.2s linear infinite` |
| `fade` (Vue `<Transition>`) | `PhaseCarousel.vue` | Fase anterior/próxima aparecem/somem com opacity | `0.25s ease` |
| `scale` (Vue `<Transition>`) | `PhaseCarousel.vue` | Fase atual aparece com scale 0.85→1 e sai com 1→0.85 | `0.2s ease` |
| `toast` (Vue `<TransitionGroup>`) | `ToastContainer.vue` | Toast entra da direita (translateX 1.5rem) e sai pela direita | `0.25s ease` |
| `animate-bounce` | `index.vue` hero | Seta de scroll bounce | Tailwind default |

### 2.7 Breakpoints

Sem customização em `tailwind.config.ts`. Valores dos **defaults do Tailwind**:

| Prefixo | Largura mínima |
|---|---|
| `sm` | 640px |
| `md` | 768px |
| `lg` | 1024px |
| `xl` | 1280px |
| `2xl` | 1536px |

Breakpoints mais usados nos componentes: `lg` (layout principal de 2 colunas no workspace) e `xl` (grid de 4 colunas do board, grid `[1fr,280px]` do workspace).

---

## 3. Classes utilitárias customizadas

Definidas em `frontend/assets/css/tailwind.css` via `@layer components`:

```css
/* .button-primary */
/* Usado em: todos os botões de ação principal, PhaseAdvance, CreateCard, CreateAction,
             CardComposer submit, ActionItemForm submit, SettingsModal close, ActionsView close */
/* Propósito: botão "ghost" com borda ciano neon. Ação afirmativa primária. */
.button-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;     /* rounded-lg */
  padding: 0.75rem 1rem;     /* px-4 py-3 */
  font-size: 0.875rem;       /* text-sm */
  font-weight: 500;          /* font-medium */
  transition: all 0.2s;
  background: transparent;
  border: 1px solid var(--neon-cyan);
  color: var(--neon-cyan);
}
.button-primary:hover {
  background: rgba(0, 242, 255, 0.08);
  box-shadow: var(--neon-glow);     /* 0 0 16px rgba(0,242,255,0.25) */
}
.button-primary:active {
  background: rgba(0, 242, 255, 0.15);
}
.button-primary:disabled {
  border-color: var(--ds-gray-700); /* #3f3f46 */
  color: var(--ds-gray-300);        /* #71717a */
  cursor: not-allowed;
  box-shadow: none;
}
```

```css
/* .button-secondary */
/* Usado em: botões Cancel, Copy (invite link), Clear selection, GroupingView secondary actions */
/* Propósito: botão neutro sem destaque. Ação de cancelamento ou ação secundária. */
.button-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  transition: colors 0.15s;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--fg-secondary);    /* #a1a1aa */
}
.button-secondary:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
}
.button-secondary:disabled {
  color: var(--ds-gray-300);
  cursor: not-allowed;
}
```

```css
/* .panel */
/* Usado em: AppSidebar, LobbyView, CheckView, MilestonesView, FocusCard (board/FocusCard),
             ParticipantPanel wrapper (retro/[id].vue), register.vue, login.vue,
             history/index.vue, history/[id].vue, retro/create.vue, retro/invite/[token].vue */
/* Propósito: superfície de "card glassmorphism". Container padrão para seções com conteúdo. */
.panel {
  border-radius: 0.75rem;         /* rounded-xl */
  backdrop-filter: blur(4px);     /* backdrop-blur-sm */
  border: 1px solid var(--border-default);  /* rgba(0,242,255,0.12) */
  background: var(--bg-surface);  /* rgba(255,255,255,0.04) */
}
```

```css
/* .field-input */
/* Usado em: CardComposer (textarea), ActionItemForm (textarea, selects, inputs), 
             login.vue (email, password), register.vue (name, email, password),
             retro/create.vue (todos inputs do formulário), CheckView (status select) */
/* Propósito: campo de formulário dark. Input padrão para qualquer dado textual. */
.field-input {
  width: 100%;                    /* w-full */
  border-radius: 0.5rem;          /* rounded-lg */
  padding: 0.75rem 1rem;          /* px-4 py-3 */
  font-size: 0.875rem;            /* text-sm */
  border: 1px solid var(--border-default);         /* rgba(0,242,255,0.12) */
  background: rgba(255, 255, 255, 0.04);
  color: var(--fg-primary);       /* #ffffff */
}
.field-input::placeholder {
  color: var(--fg-tertiary);      /* #52525b */
}
.field-input:focus {
  outline: none;
  border-color: rgba(0, 242, 255, 0.5);
  box-shadow: 0 0 0 1px rgba(0, 242, 255, 0.15);
}
select.field-input {
  color-scheme: dark;
}
select.field-input option {
  background-color: #0d0d0d;
  color: #e4e4e7;
}
```

**Classe base** (em `@layer base`):

```css
/* Focus visible global — aplicado a button, a, input, select, textarea */
/* Propósito: outline de foco consistente com ring ciano. Não remover. */
focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#00f2ff]/60
```

---

## 4. Sistema de ícones

### 4.1 Heroicons — declarado em `package.json`

```json
"@heroicons/vue": "^2.2.0"
```

Uso: `import { XIcon } from '@heroicons/vue/24/outline'` ou `/24/solid`.

| Ícone | Variante | Componente |
|---|---|---|
| `PauseCircleIcon` | outline | `TimerDisplay.vue` |
| `PlayCircleIcon` | outline | `TimerDisplay.vue` |
| `CheckCircleIcon` | solid | `ToastContainer.vue` |
| `ExclamationCircleIcon` | solid | `ToastContainer.vue` |
| `ExclamationTriangleIcon` | solid | `ToastContainer.vue` |
| `InformationCircleIcon` | solid | `ToastContainer.vue` |
| `XMarkIcon` | solid | `ToastContainer.vue` |
| `NoSymbolIcon` | outline | `ParticipantPanel.vue` (access log blocked) |
| `UserCircleIcon` | outline | `ParticipantPanel.vue` (avatar participante) |
| `UserPlusIcon` | outline | `ParticipantPanel.vue` (allow entry btn, access log joined) |
| `LockClosedIcon` | solid | `ParticipantPanel.vue` (invite blocked) |
| `LockOpenIcon` | solid | `ParticipantPanel.vue` (invite open) |
| `ArrowRightCircleIcon` | outline | `board/FocusCard.vue` (Next card) |
| `ViewfinderCircleIcon` | outline | `board/FocusCard.vue` (In focus label) |
| `PlusIcon` | outline | `board/FocusCard.vue`, `board/ColumnHeader.vue` |
| `HandThumbUpIcon` | outline | `board/ColumnHeader.vue` (loved column) |
| `HandThumbDownIcon` | outline | `board/ColumnHeader.vue` (loathed column) |
| `ClockIcon` | outline | `board/ColumnHeader.vue` (longed column), `ActionsView.vue` (status in_progress) |
| `LightBulbIcon` | outline | `board/ColumnHeader.vue` (learned column) |
| `PencilSquareIcon` | outline | `ActionsView.vue` (edit action) |
| `TrashIcon` | outline | `ActionsView.vue` (delete action) |
| `CheckCircleIcon` | outline | `ActionsView.vue` (status done) |
| `MinusCircleIcon` | outline | `ActionsView.vue` (status not_started) |
| `ViewfinderCircleIcon` | outline | `DiscussionView.vue` (in focus inline indicator) |
| `ArrowRightOnRectangleIcon` | outline | `auth/login.vue` |
| `UserPlusIcon` | outline | `auth/register.vue` |
| `FlagIcon` | outline | `retro/MilestoneBar.vue` |

### 4.2 Material Design Icons (MDI) — sem declaração em `package.json`

`@mdi/font` ou qualquer CSS do MDI **não está declarado** em `package.json`. As classes `mdi mdi-*` existem em múltiplos componentes mas não têm a folha de estilos para renderizar os ícones.

| Ícone MDI | Componente |
|---|---|
| `mdi-cog-outline` | `RetroHeader.vue` (settings button), `SetupView.vue` (spinning cog) |
| `mdi-close` | `SettingsModal.vue` (fechar modal) |
| `mdi-flag-checkered` | `MilestoneCard.vue`, `MilestoneBar.vue` |
| `mdi-star` | `retro/FocusCard.vue` (In focus label) |
| `mdi-minus` | `VoteControls.vue` (decrement vote) |
| `mdi-plus` | `VoteControls.vue` (increment vote) |
| `mdi-check-decagram` | `ClosedView.vue` (sessão fechada) |
| `mdi-link-variant` | `LobbyView.vue`, `ParticipantPanel.vue` |
| `mdi-account-multiple-outline` | `LobbyView.vue` |
| `mdi-google` | `auth/login.vue` (Google OAuth button) |
| `mdi-key-outline` | `join.vue` |
| Ícones de fase via `PHASE_META[phase].icon` | `PhaseStepper.vue`, `PhaseCarousel.vue` |

> **Estado atual:** ícones MDI **não renderizam** sem CSS externo. Os elementos aparecem no DOM como `<span class="mdi mdi-cog-outline">` mas sem conteúdo visual (fonte não carregada).

### 4.3 Regra para adição de novos ícones

```
✅ Use: @heroicons/vue — instalado, importar com:
        import { NomeIcon } from '@heroicons/vue/24/outline'
        import { NomeIcon } from '@heroicons/vue/24/solid'
        Variante outline: traços; solid: preenchido.
        Tamanho padrão: h-5 w-5 (20px). Decorativos: aria-hidden="true".

⚠️ Não adicione novos ícones MDI — dependência não declarada; pode não renderizar.
   Os ícones MDI existentes são débito técnico, não modelo a seguir.
```

---

## 5. Layout do workspace de retrospectiva

### 5.1 Estrutura geral

```
┌────────────────────────────────────────────────────────────────────┐
│  RetroHeader (border-b border-[#00f2ff]/10, bg-[#050505]/90)       │
│  [Logo JetBrains Mono]  [PhaseCarousel: prev › current › next]     │
│                         [TimerDisplay (slot)] [Settings btn]        │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  content (max-w-7xl, px-6 py-6, xl:grid-cols-[minmax(0,1fr),280px])│
│                                                                    │
│  ┌──────────────────────────────────┐  ┌──────────────────────┐   │
│  │  <componente de fase> (dinâmico) │  │  ParticipantPanel    │   │
│  │  (min-w-0, flex-1)               │  │  (panel p-4 lg:p-5)  │   │
│  │                                  │  │  280px fixos         │   │
│  └──────────────────────────────────┘  └──────────────────────┘   │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│  AppFooter (border-t border-[#00f2ff]/10)                          │
│  ToastContainer (Teleport → body, bottom-right fixed)              │
└────────────────────────────────────────────────────────────────────┘
```

- `ParticipantPanel` está **dentro** da coluna lateral do grid, visível em todas as fases exceto `closed`.
- `TimerDisplay` aparece apenas se `isTimedPhase && timerStore.secondsRemaining > 0` (slot `#timer` do `AppShell`).
- `CardComposer` e `ActionItemForm` são modais com `z-50` montados fora do grid (dentro do `AppShell`), mas abertos por eventos dos componentes de fase.

### 5.2 Troca de componente por fase

| Fase | Componente | Arquivo |
|---|---|---|
| `setup` | `SetupView` | `components/retro/phases/SetupView.vue` |
| `lobby` | `LobbyView` | `components/retro/phases/LobbyView.vue` |
| `check` | `CheckView` | `components/retro/phases/CheckView.vue` |
| `presentation` | `MilestonesView` | `components/retro/phases/MilestonesView.vue` |
| `board` | `BoardView` | `components/retro/phases/BoardView.vue` |
| `grouping` | `GroupingView` | `components/retro/phases/GroupingView.vue` |
| `voting` | `VotingView` | `components/retro/phases/VotingView.vue` |
| `discussion` | `DiscussionView` | `components/retro/phases/DiscussionView.vue` |
| `actions` | `ActionsView` | `components/retro/phases/ActionsView.vue` |
| `closed` | `ClosedView` | `components/retro/phases/ClosedView.vue` |

Fonte: `pages/retro/[id].vue`, `computed phaseComponent`, linhas 60–74.

### 5.3 Regiões sempre visíveis

| Região | Descrição |
|---|---|
| `RetroHeader` | Logo, `PhaseCarousel`, slot de timer, botão Settings. Visível em todas as fases. |
| `PhaseCarousel` | Mostra fase anterior, fase atual (com glow), próxima fase. Filtra `check` se `skipCheckPhase`. |
| `TimerDisplay` | Aparece no slot `#timer` apenas em fases cronometradas com tempo > 0. |
| `ParticipantPanel` | Coluna lateral direita. Visível em todas as fases exceto `closed`. Mostra participantes, status de convite (facilitador), access log. |
| `ToastContainer` | Fixed bottom-right, sempre presente via `AppShell`. |
| `CardComposer` | Modal overlay `z-50`. Abre quando `cardModalOpen = true`. |
| `ActionItemForm` | Modal overlay `z-50`. Abre quando `actionModalOpen = true`. |

---

## 6. Componentes — comportamento esperado

### `RetroCard`

**Arquivo:** `frontend/components/retro/RetroCard.vue`

**Props:**
```typescript
card: Card                  // obrigatória
canEdit?: boolean           // default false — mostra botão Edit
canDelete?: boolean         // default false — mostra botão Delete
canVote?: boolean           // default false — mostra botão Vote
selected?: boolean          // default false — borda ciano + ring
showGrouping?: boolean      // default false — mostra "Select for group"
showVoteBadge?: boolean     // default false — mostra VoteBadge no topo direito
isOwnCard?: boolean         // default false — bloqueia vote se !allowSelfVote
allowSelfVote?: boolean     // default false
votesRemaining?: number     // undefined = sem limite; 0 = desabilitado
voteActive?: boolean        // default false — botão Vote fica ciano se true
groupedCards?: Card[]       // default [] — renderiza filhos abaixo do conteúdo
```

**Emits:** `edit: [Card]`, `delete: [Card]`, `vote: [Card]`, `toggle-select: [string]`, `action: [{type, card}]`

**Estados visuais:**
- `selected=false`: borda `border-white/10 hover:border-white/20`
- `selected=true`: borda `border-[#00f2ff]/50 ring-1 ring-[#00f2ff]/20`
- Card anônimo: `author_display` vira `"Anonymous"` (server-mascarado); badge de autor usa `border-[#00f2ff]/20 text-[#00f2ff]/70` (ciano tênue) em vez de `text-zinc-500`
- `canVote && isOwnCard && !allowSelfVote`: mostra `"Your card"` (italic zinc-600) em vez do botão Vote
- `voteActive=true`: botão Vote fica `text-[#00f2ff]`
- `votesRemaining <= 0`: botão Vote `disabled` + `text-zinc-700 cursor-not-allowed`

**Cards agrupados (pai → filhos):**
- `groupedCards.length > 0` renderiza seção abaixo do conteúdo com `border-t border-white/8`
- Cada filho: `rounded-lg px-3 py-2 bg-[rgba(255,255,255,0.04)]` com conteúdo e badge `"Anonymous"` se anônimo
- O número de filhos aparece como `"N card(s) agrupado(s)"`

**Tokens usados:** `border-white/10`, `border-[#00f2ff]/50`, `ring-[#00f2ff]/20`, `text-zinc-200` (content), `text-zinc-500` (non-anon author), `text-[#00f2ff]/70` (anon author), `text-danger-500` (delete btn hover), `text-[#00f2ff]` (vote active)

> ⚠️ inconsistência: `style="background: rgba(255,255,255,0.04)"` hardcoded em vez de `var(--bg-surface)` ou `.panel`.

---

### `TimerDisplay`

**Arquivo:** `frontend/components/retro/TimerDisplay.vue`

**Props:**
```typescript
label: string       // obrigatória — texto formatado "MM:SS" vindo de timerStore.formatted
toneClass: string   // obrigatória — classe de cor calculada em useTimer()
paused?: boolean    // controla qual botão aparece (pause vs resume)
facilitator?: boolean // controla visibilidade dos botões
```

**Emits:** `pause: []`, `resume: []`

**Estados visuais:**
- Timer running: mostra `PauseCircleIcon` (se `facilitator && !paused`)
- Timer paused: mostra `PlayCircleIcon` (se `facilitator && paused`)
- Sem botões para participante (`facilitator=false`)

**Cores do label via `toneClass`** (calculado em `composables/useTimer.ts`):

| Tempo restante | Classe | Cor |
|---|---|---|
| > 60s | `text-[#00f2ff]` | Ciano neon |
| 30–60s | `text-warning-500` | Âmbar `#f59e0b` |
| < 30s | `text-danger-500` | Vermelho `#ef4444` |

**Onde aparece:** slot `#timer` do `AppShell` em `retro/[id].vue`. Condição: `isTimedPhase && timerStore.secondsRemaining > 0`.

**Nota:** `BoardView` e `VotingView` e `DiscussionView` também exibem um timer secundário inline como `<span>{{ timerStore.formatted }}</span>` com a mesma lógica de cor (`timerStore.secondsRemaining < 60 ? 'text-danger-500' : 'text-[#00f2ff]'`). São duplicações locais da lógica.

---

### `CardComposer`

**Arquivo:** `frontend/components/forms/CardComposer.vue`

**Props:**
```typescript
modelValue: boolean              // obrigatória — v-model para abrir/fechar
initialCard?: Card | null        // null = criação; Card = edição
initialColumn?: CardColumn       // coluna pré-selecionada na criação
```

**Emits:** `update:modelValue: [boolean]`, `submit: [{id?, content, column, is_anonymous}]`

**Estados visuais:**
- Modal fixo fullscreen com `bg-black/70 backdrop-blur-sm`
- Título: `"Add card"` (criação) ou `"Edit card"` (edição, quando `initialCard` presente)
- Select de coluna tem cor dinâmica conforme coluna selecionada:
  - `loved`: `border-[#22c55e]/50 text-[#22c55e]`
  - `loathed`: `border-[#ef4444]/50 text-[#ef4444]`
  - `longed`: `border-[#60a5fa]/50 text-[#60a5fa]`
  - `learned`: `border-white/15 text-zinc-400`
- Select desabilitado quando `!initialCard && !!initialColumn` (coluna fixa na criação por coluna)
- Checkbox "Add anonymously" usa `text-[#00f2ff]` como accent-color nativo

**Foco automático:** `watch(() => props.modelValue, async (isOpen) => { if (!isOpen || props.initialCard) return; await nextTick(); descriptionInput.value?.focus() })` — foca o textarea ao abrir para criação (não edição).

**Opções de coluna** (labels reais no `<select>`):
- `loved` → `"Liked"`
- `loathed` → `"Loathed"`
- `longed` → `"Longed for"`
- `learned` → `"Learned"`

---

### `ActionEditor` (componente legado)

**Arquivo:** `frontend/components/retro/ActionEditor.vue`

**Props:** `action?: Object` (tipagem fraca — sem TypeScript estrito)

**Emits:** `save: [{title, description, responsible, dueDate}]`, `cancel: []`

**Campos:** `title` (required), `description` (optional textarea), `responsible` (optional input), `dueDate` (date input optional).

**Estado:** formulário reativo com `watchEffect` para pré-preencher quando `action` muda.

**Nota:** Este componente usa `.input-primary` (classe local scoped, não no sistema global) e `.button-tertiary` (não definida em nenhum lugar do design system — pode não renderizar). **Não é o componente em uso no workspace principal** (`retro/[id].vue` usa `ActionItemForm`).

---

### `ActionItemForm`

**Arquivo:** `frontend/components/forms/ActionItemForm.vue`

**Props:**
```typescript
participants: Participant[]      // obrigatória — lista para o select de assignee
cards: Card[]                   // obrigatória — filtrado para loathed/longed
modelValue: boolean             // obrigatória — v-model open/close
initialAction?: ActionItem | null // null = criação; ActionItem = edição
defaultCardId?: string          // pré-seleciona card no select
```

**Emits:** `update:modelValue: [boolean]`, `submit: [{id?, description, assignee_id, card_id, due_date, status, external_tracker_url}]`

**Estados visuais:**
- Título dinâmico: `"Edit action item"` ou `"Create action item"`
- Modal fullscreen `bg-black/70 backdrop-blur-sm`, max-w-2xl
- Grid 2 colunas no md+; `description` ocupa `md:col-span-2`

**Campos:**
| Campo | Tipo | Obrigatório | Default |
|---|---|---|---|
| `description` | textarea | sim (implícito) | "" |
| `assignee_id` | select (Participant.id) | não | "" |
| `card_id` | select (Card.id, filtrado loathed/longed) | não | "" |
| `due_date` | date input | não | "" |
| `status` | select (not_started / in_progress / done) | não | "not_started" |
| `external_tracker_url` | text input | não | "" |

**Diferença criação vs edição:** `initialAction` é null em criação (título muda, campos vazios) e ActionItem em edição (campos pré-preenchidos via `watch(() => props.modelValue)`).

---

### `FocusCard` (board/FocusCard — versão principal)

**Arquivo:** `frontend/components/board/FocusCard.vue`

**Props:**
```typescript
focus: DiscussionFocusPayload | null  // card em foco atual
queue: Card[]                          // cards na fila (para "Up next")
facilitator?: boolean                  // mostra botões Next card / New action
```

**Emits:** `next: []`, `new-action: []`

**Estados visuais:**
- Painel `.panel p-6` com header `ViewfinderCircleIcon + "In focus"`
- Quando `focus=null`: mensagem `"Pick a card to start discussion."`
- Quando `focus` presente: coluna (zinc-600 uppercase), conteúdo (text-lg text-white), vote_count (text-[#00f2ff]/70)
- Seção "Up next": lista até 3 próximos cards da fila (zinc-600 text)
- Botões só para facilitador: `button-primary "Next card"` e `button-secondary "New action"`

**Diferença do `retro/FocusCard.vue`:** a versão em `retro/FocusCard.vue` é simplificada (usada em contexto de board), com campo `card.text` (não `card.content`), `card.votes` (não `card.vote_count`), e sem fila "Up next". A versão em `board/FocusCard.vue` é a correta para o `DiscussionView`.

---

### `VoteBadge`

**Arquivo:** `frontend/components/retro/VoteBadge.vue`

**Props:**
```typescript
count: number    // obrigatória — número de votos
active?: boolean // false = neutro; true = ciano (usuário votou)
```

**Estados visuais:**
- `active=false`: `border border-white/10 text-zinc-600` (badge neutro)
- `active=true`: `border border-[#00f2ff]/30 text-[#00f2ff]` (badge ativo ciano)

**Quando aparece no `RetroCard`:** `showVoteBadge=true` ativo nas fases `voting` e `grouping`, e apenas para colunas `loathed` e `longed`.

---

### `PhaseStepper`

**Arquivo:** `frontend/components/layout/PhaseStepper.vue`

**Props:**
```typescript
phases: string[]       // obrigatória — lista ordenada de fases a exibir
currentPhase: string   // obrigatória — fase atual
isFacilitator?: boolean // controla disabled em fases futuras
```

**Emits:** `select: [phase: string]`

**Estados visuais por pill:**
- Fase passada (idx < currentIdx): `border border-[#00f2ff]/20 text-[#00f2ff]/60`
- Fase atual (idx === currentIdx): `border border-[#00f2ff] text-[#00f2ff] shadow-glow`
- Fase futura (idx > currentIdx): `border border-white/10 text-zinc-600`
- Botões de fases futuras `disabled` se `!isFacilitator`

**Ícones de fase:** usa `PHASE_META[phase].icon` (via classes MDI). Os ícones dependem de `@mdi/font` não declarado.

**Nota:** `PhaseStepper` não é o componente usado no header do workspace. O header usa `PhaseCarousel`. `PhaseStepper` é uma lista linear (pode ser usado em contextos alternativos).

---

### `PhaseCarousel`

**Arquivo:** `frontend/components/layout/PhaseCarousel.vue`

**Props:**
```typescript
currentPhase: RetroPhase   // obrigatória
skipCheckPhase?: boolean   // filtra "check" da lista de fases
```

**Sem emits.**

**Estados visuais:**
- Exibe: `[fase anterior] › [fase atual] › [próxima fase]`
- Fase anterior: `border-white/10 text-zinc-600 font-light` — animação `<Transition name="fade">`
- Fase atual: `border-[#00f2ff]/40 text-[#00f2ff] font-medium` com box-shadow ciano `0 0 10px rgba(0,242,255,0.15)` — animação `<Transition name="scale">`
- Próxima fase: idem fase anterior
- Fases sem anterior/próxima: slot vazio (width fixo `w-28` preservada para não deslocar layout)
- Ícones de fase via `PHASE_META[phase].icon` — dependem de MDI

---

### `ParticipantPanel`

**Arquivo:** `frontend/components/participants/ParticipantPanel.vue`

**Props:**
```typescript
participants: Participant[]          // obrigatória
onlineIds: string[]                  // obrigatória — estimado por WS events
accessLog: string[]                  // obrigatória — entradas textuais do log
inviteStatus: InviteStatus           // obrigatória — 'active' | 'blocked' | 'temporarily_open'
inviteLink?: string | null           // URL completa do convite
inviteExpiresAt?: string | null      // ISO string — para countdown de temporarily_open
facilitator?: boolean                // mostra seção de admin de convite
allowEntryLoading?: boolean          // estado de loading do "Allow new entry"
```

**Emits:** `allowEntry: []`, `copy-invite-link: []`

**Estados online/offline:**
- Online: `text-success-600` + aria-label `"Online"`
- Offline: `text-slate-400` + aria-label `"Offline"`
- Detectado por `onlineIds.includes(participant.user)` — estimativa; pode ser imprecisa

**Status do convite (seção facilitador):**
- `active`: texto verde `"OPEN"`, ícone `LockOpenIcon success-600`, texto "Invite link is open (lobby phase)."
- `temporarily_open`: texto âmbar `"TEMPORARILY OPEN (Xs)"`, ícone `LockOpenIcon`, countdown em segundos, botão desabilitado
- `blocked`: texto vermelho `"BLOCKED"`, ícone `LockClosedIcon danger-500`, botão "Allow new entry" ativo

**Access log:** ícones por tipo de entrada:
- `item.includes('blocked')`: `NoSymbolIcon text-danger-500`
- `item.includes('joined')`: `UserPlusIcon text-success-500`
- demais: `LockOpenIcon text-warning-500`

---

### `BoardGrid`

**Arquivo:** `frontend/components/board/BoardGrid.vue`

**Props:**
```typescript
columns: Record<CardColumn, Card[]>   // obrigatória — cards por coluna
selectedIds: string[]                 // obrigatória — IDs selecionados (grouping)
currentUserId?: string
votedCardIds?: string[]               // default []
votesRemaining?: number               // undefined = sem limite
allowSelfVote?: boolean               // default false
phase: string                         // controla comportamento dos RetroCards
groupedChildren?: Record<string, Card[]>  // default {}
```

**Emits:** `createCard: [CardColumn]`, `editCard: [Card]`, `deleteCard: [Card]`, `toggleSelect: [string]`, `vote: [Card]`

**Layout:** `grid gap-3 xl:grid-cols-4` — 4 colunas em xl+; 1 coluna abaixo de xl.

**Ordem de colunas** (hardcoded na iteração): `['loved', 'loathed', 'longed', 'learned']`

**Labels e acentos de cada coluna** (via `ColumnHeader`):

| Coluna | Label | Acento (cor de borda) | Ícone |
|---|---|---|---|
| `loved` | `"Liked"` | `#22c55e` (green) | `HandThumbUpIcon` |
| `loathed` | `"Loathed"` | `#ef4444` (red) | `HandThumbDownIcon` |
| `longed` | `"Longed for"` | `#60a5fa` (blue) | `ClockIcon` |
| `learned` | `"Learned"` | `#a1a1aa` (zinc) | `LightBulbIcon` |

**Comportamento por fase:**

| Fase | canCreate | canEdit/canDelete | canVote | showGrouping | showVoteBadge |
|---|---|---|---|---|---|
| `board` | ✅ (`canCreate=true`) | ✅ (se `card.can_edit`) | ❌ | ❌ | ❌ |
| `grouping` | ❌ | ❌ | ❌ | ✅ (facilitador apenas) | ✅ (loathed/longed) |
| `voting` | ❌ | ❌ | ✅ (loathed/longed) | ❌ | ✅ (loathed/longed) |

Borda de cada coluna: `1px solid ${columnAccent}26` (10% opacity do acento). Border-left não aparece em `BoardGrid` — aparece em `ColumnHeader` como `borderLeftColor: accentColor, borderLeftWidth: '2px'`.

> ⚠️ inconsistência: `BoardGrid` também existe em `components/retro/board/BoardGrid.vue` (duplicação). O usado por `BoardView`, `GroupingView` e `VotingView` é `components/board/BoardGrid.vue`.

---

### `MilestoneCard`

**Arquivo:** `frontend/components/retro/MilestoneCard.vue`

**Props:** `milestone: Object` (tipagem fraca)

**Campos esperados:** `milestone.title`, `milestone.description`, `milestone.date`

**Estados visuais:**
- Container: `rounded-lg border border-white/10 p-4 flex flex-col gap-2 bg-[rgba(255,255,255,0.04)]`
- Ícone MDI `mdi-flag-checkered` `text-[#00f2ff]/60`
- Título: `font-light text-zinc-200`
- Descrição: `text-sm text-zinc-500`
- Data: `text-xs text-zinc-700`

**Não diferencia categorias visualmente** — sem distinção de cor, badge ou ícone diferente entre `achievement`, `challenge`, `change`, `recognition`, `other`. Todas as categorias renderizam o mesmo ícone `mdi-flag-checkered`.

> ⚠️ O arquivo `MilestoneCard.vue` tem um bug de sintaxe: `defineProps<{` aparece como texto solto antes do `<template>`, fora de qualquer bloco `<script>`. O componente funciona porque o Vue ignora isso, mas é inválido.

---

### `HistoryTable`

**Arquivo:** `frontend/components/HistoryTable.vue`

**Props:**
```typescript
retros: RetrospectiveSummary[]   // obrigatória
```

**Sem emits.**

**Colunas:** Sprint, Title, Date, Status, Actions (done/total), Link

**Estado vazio:** `<td colspan="6">No closed retrospectives yet.</td>` (text-center text-zinc-600)

**Hierarquia pai → filhos:** `HistoryTable` **não exibe cards agrupados**. É usado em `index.vue` (dashboard). A renderização de cards agrupados na tela de histórico detalhado (`history/[id].vue`) usa `RetroCard` com `grouped-cards` prop diretamente na página.

**Data format:** `Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' })`

---

### Componentes adicionais relevantes

#### `PhaseChip`

**Arquivo:** `frontend/components/retro/PhaseChip.vue`

**Props:** `phase: string`, `timerText?: string`

**Visual:** `border border-[#00f2ff]/35 text-[#00f2ff] text-xs font-light rounded px-2 py-1`

**Usado em:** `ActiveSessionCard.vue` para exibir fase da sessão ativa no dashboard.

---

#### `ActiveSessionCard`

**Arquivo:** `frontend/components/ActiveSessionCard.vue`

**Props:** `retro: RetrospectiveSummary`

**Visual:** container com `border-[#00f2ff]/20 bg-[rgba(0,242,255,0.04)]`. Mostra `PhaseChip`, título, sprint, botão "Continue" (link para `/retro/{id}`).

**Usado em:** `index.vue` (dashboard, quando há sessão ativa não-fechada).

---

#### `AvatarCircle`

**Arquivo:** `frontend/components/layout/AvatarCircle.vue`

**Props:** `name: string` (obrigatória), `size?: 28 | 32 | 36 | 48` (default 36), `color?: 'brand' | 'success' | 'warning' | 'danger' | 'gray'`

**Visual:** círculo com iniciais (2 chars); background usa `var(--ds-${color}-500)`; text `#fff`.

**Usado em:** `SetupView.vue` para exibir avatares de participantes conectados.

---

## 7. Padrões visuais por fase da sessão

### Fase `setup`

**Quem vê o quê:**
- Facilitador: botão "Go to Lobby" + ícone cog girando
- Participante: mensagem de espera + avatares dos participantes conectados (AvatarCircle)

**Ações disponíveis:**
- Facilitador: avançar para `lobby`

**Estado do board/cards:** sem board — tela centrada com min-h-[60vh]

**Estado do timer:** oculto (fase não cronometrada)

**Elementos específicos:** ícone `mdi-cog-outline` com `animate-spin` (CSS local, não Tailwind). Única fase com animação de ícone.

---

### Fase `lobby`

**Quem vê o quê:**
- Facilitador: link de convite, botão "Start session", contagem de participantes
- Participante: vê os mesmos dados mas sem botão de avançar

**Ações disponíveis:**
- Facilitador: copiar link de convite, avançar fase

**Estado do board/cards:** sem board — layout 2 colunas (conteúdo principal + "How it works")

**Estado do timer:** oculto (fase não cronometrada)

**Elementos específicos:** `mdi-link-variant` + `mdi-account-multiple-outline` (ícones MDI, podem não renderizar). Link de convite exibido como `font-mono text-xs bg-white/5 border border-white/10`.

---

### Fase `check`

**Quem vê o quê:**
- Facilitador: lista de action items anteriores com select de status editável + botão avançar
- Participante: mesma lista mas selects **desabilitados** (`disabled="!isFacilitator"`)

**Ações disponíveis:**
- Todos: atualizar status de ações anteriores via select (mas bloqueado para participante via `disabled`)
- Facilitador: avançar fase

**Estado do board/cards:** sem board — lista de ações anteriores

**Estado do timer:** ativo (fase cronometrada, 300s default)

**Estado vazio:** `"No previous actions found."` em borda dashed border-white/10

---

### Fase `presentation`

**Componente:** `MilestonesView`

**Quem vê o quê:**
- Facilitador: grid de `MilestoneCard` + botão avançar
- Participante: mesmos marcos, sem botão avançar

**Ações disponíveis:**
- Facilitador: avançar fase

**Estado do board/cards:** sem board — grid de milestones (2 cols md, 3 cols xl)

**Estado do timer:** ativo (600s default)

**Estado vazio:** `"No milestones registered."` em borda dashed

---

### Fase `board`

**Quem vê o quê:**
- Facilitador: board completo + botão avançar
- Participante: board completo (mesma view, pode criar/editar próprios cards)

**Ações disponíveis:**
- Todos: criar cards por coluna (botão "Add" no `ColumnHeader`), editar/deletar próprios cards
- Facilitador: avançar fase

**Estado do board/cards:** totalmente editável. `canCreate=true`, `canEdit=card.can_edit && phase==='board'`, `canDelete=card.can_edit && phase==='board'`

**Estado do timer:** ativo (900s default). Indicador de timer inline (além do header): `{{ timerStore.formatted }}` com cor `text-danger-500` se < 60s, else `text-[#00f2ff]`.

---

### Fase `grouping`

**Quem vê o quê:**
- Facilitador: cards selecionáveis, botões "Group selected" e "Clear"
- Participante: cards não selecionáveis, mensagem "The facilitator is grouping similar cards."

**Ações disponíveis:**
- Facilitador: selecionar cards, agrupar seleção (≥2 cards), limpar seleção, avançar fase

**Estado do board/cards:** read-only para participante. Facilitador pode selecionar (`showGrouping=true`). `VoteBadge` visível em loathed/longed.

**Estado do timer:** ativo (300s default)

**Botão de agrupamento:** desabilitado com `opacity-30` quando `selectionCount < 2`

---

### Fase `voting`

**Quem vê o quê:**
- Todos: board com botões de voto em loathed/longed, contador "X votes left"
- Facilitador: botão avançar + mesmos controles de voto

**Ações disponíveis:**
- Todos: votar/revogar voto em loathed/longed (toggle no mesmo handler)
- Facilitador: avançar fase

**Estado do board/cards:** read-only exceto votação. `canVote=true` apenas em loathed/longed. `VoteBadge` visível em loathed/longed. Cards de outras colunas aparecem mas sem interação de voto.

**Estado do timer:** ativo (180s default). Indicador inline + no header.

**Contador de votos:** `{{ votesRemaining }} vote(s) left` em pill `border-[#00f2ff]/25 text-[#00f2ff]`.

---

### Fase `discussion`

**Quem vê o quê:**
- Facilitador: lista de cards clicável (click = focus), `FocusCard` panel, botões "Next card" e "New action", "Session Minutes"
- Participante: mesma lista não clicável (cursor-default), `FocusCard` sem botões

**Ações disponíveis:**
- Facilitador: clicar card para focar, avançar para próximo card, criar action item, avançar fase

**Estado do board/cards:** read-only. Lista de todos os cards (não apenas loathed/longed) ordenada por `vote_count` decrescente.

**Estado do timer:** ativo (900s default). Indicador inline.

**Destaques visuais:**
- Card em foco: `border-[#00f2ff]/40 ring-1 ring-[#00f2ff]/15`
- Top 3 cards com votes > 0 (sem ser o card em foco): `border-amber-500/30`
- Demais cards: `border-white/8`
- Cards clicáveis para facilitador: `cursor-pointer hover:border-white/20`

---

### Fase `actions`

**Quem vê o quê:**
- Facilitador: lista de action items com edit/delete, botão "Close retrospective" + confirmação
- Participante: mesma lista, sem botões de edição/exclusão

**Ações disponíveis:**
- Facilitador: editar/deletar action items, fechar retrospectiva (requer confirmação)

**Estado do board/cards:** sem board — lista de action items

**Estado do timer:** ativo (600s default). Indicador inline.

**Status badge de action items:**
- `done`: `text-[#22c55e] border border-[#22c55e]/25` + `CheckCircleIcon`
- `in_progress`: `text-[#00f2ff] border border-[#00f2ff]/25` + `ClockIcon`
- `not_started`: `text-zinc-500 border border-white/10` + `MinusCircleIcon`

**Modal de confirmação de fechamento:** fullscreen overlay `z-50`. Aviso se há action items sem assignee (`bg-warning-50` — mas `warning-50` não está na paleta customizada, pode renderizar incorretamente).

---

### Fase `closed`

**Quem vê o quê:**
- Todos: tela de encerramento centrada com ícone `mdi-check-decagram`, título, link para histórico

**Ações disponíveis:**
- Todos: navegar para `/history/{id}`

**Estado do board/cards:** sem board

**Estado do timer:** oculto

**Behavior:** ao receber fase `closed` via WS, `retro/[id].vue` desconecta o WebSocket e navega para `/history/{id}` automaticamente via `watch(() => activePhase.value)`. `ParticipantPanel` também fica oculto (condição `v-if="current && activePhase !== 'closed'"`).

---

## 8. Estados de interface

### 8.1 Loading

| Contexto | Implementação |
|---|---|
| `retro/invite/[token].vue` carregando convite | `<div v-if="loading">Loading invite details...</div>` em borda dashed border-white/10 |
| `history/[id].vue` carregando detalhe | `<p>Loading retrospective...</p>` (sem skeleton, sem spinner) |
| Botão "Start session" / "Create" durante submit | `pending.value = true` → botão `disabled` + texto `"Creating..."` / `"Signing in..."` |
| `allowEntryLoading` no `ParticipantPanel` | Botão "Allow new entry" `disabled` + texto `"Opening..."` |
| SetupView aguardando facilitador | Ícone `mdi-cog-outline animate-spin` (MDI, pode não renderizar) |

Sem skeleton global. Sem spinner padronizado. Loading é indicado majoritariamente por texto no botão ou mensagem inline.

### 8.2 Erro de conexão WebSocket

Não há overlay ou banner específico para perda de WS no `retro/[id].vue`. O `pageError` captura erros de `fetchSession()` no `onMounted`:

```typescript
catch (error) {
  websocketEnabled.value = false
  pageError.value = error instanceof Error ? error.message : 'Unable to load session.'
  if (pageError.value === 'This retrospective is closed. Use the history endpoint instead.') {
    await navigateTo(`/history/${retrospectiveId.value}`)
    return
  }
}
```

Quando `pageError` tem valor, o template de fase recebe `pageError` como prop mas não tem tratamento visual unificado — cada componente de fase ignora o prop. Não há UI de reconexão visível para o usuário.

### 8.3 Toast / notificações

**Posição:** `fixed bottom-6 right-6 z-50` (via `Teleport to="body"`)

**Duração por tipo:**

| Tipo | Duração | Cor border/text |
|---|---|---|
| `success` | 4000ms | `border-success-500 text-success-600` |
| `warning` | 5000ms | `border-warning-500 text-warning-600` |
| `error` | 6000ms | `border-danger-500 text-danger-600` |
| `info` | 4000ms | `border-brand-500 text-brand-600` |

**Backgrounds:** `bg-success-50`, `bg-warning-50`, `bg-danger-50`, `bg-brand-50`. Nota: `success-50`, `warning-50`, `danger-50` não estão na paleta customizada (só existem 500, 600, 700 para success/warning/danger). `bg-brand-50` existe como `rgba(0,242,255,0.05)`. As outras -50 podem não renderizar corretamente.

**Máximo simultâneo:** sem limite declarado. `toasts` é um array sem cap.

**Dismiss:** botão `XMarkIcon` com `aria-label="Dismiss notification: {message}"`. Auto-dismiss por `setTimeout(() => remove(id), duration)`.

**Animação:** `TransitionGroup name="toast"` — enter da direita, leave para a direita.

### 8.4 Estados vazios

| Tela | Estado vazio |
|---|---|
| `CheckView` (ações anteriores) | `"No previous actions found."` em borda dashed |
| `MilestonesView` | `"No milestones registered."` em borda dashed |
| `BoardGrid` (coluna sem cards) | Área mínima `min-h-80` — sem mensagem de vazio |
| `DiscussionView` (sem cards) | `"No cards to discuss."` centrado py-12 |
| `ActionsView` (sem action items) | `"No action items yet. Add the first one."` em borda dashed centrado p-8 |
| `ParticipantPanel` (sem participantes) | `"No participants yet."` texto zinc-600 |
| `ParticipantPanel` (access log vazio) | `"Realtime access events will appear here."` zinc-700 |
| `history/index.vue` (sem retros) | `"No closed retrospectives available yet."` borda dashed |
| `HistoryTable` (sem retros) | `"No closed retrospectives yet."` td colspan=6 centrado |

Padrão de estado vazio: borda dashed `border-dashed border-white/10` com padding p-6 e texto `text-sm text-zinc-600`.

### 8.5 Sessão fechada

Ao detectar `activePhase === 'closed'`:
1. `websocketEnabled.value = false` (WS desconectado)
2. `navigateTo('/history/{id}')` (redirect automático)

Se usuário já estava em `closed` ao carregar (sessão fechada), `fetchSession()` lança erro com mensagem específica → `navigateTo('/history/{id}')` via catch.

`ParticipantPanel` oculto via `v-if="current && activePhase !== 'closed'"`.

`ClosedView` existe mas na prática o usuário vê apenas por um instante antes do redirect.

### 8.6 Usuário guest

**Diferenças visuais:**
- `AppHeader`: link "New retro" oculto para guests (`v-if="isAuthenticatedUser"`)
- `AppHeader`: link "History" oculto para guests (`v-if="isAuthenticatedUser"`)
- `index.vue`: mostra landing page em vez de dashboard (`showLanding = !authStore.isAuthenticated || authStore.isGuestSession`)
- `index.vue` dashboard: `HistoryTable` oculta para guests (`v-if="!authStore.isGuestSession"`)

**Sem diferença visual no workspace:** guest tem a mesma UI que participante autenticado dentro da sessão de retro. A distinção é de fluxo (não pode criar retro) não de UI dentro do workspace.

---

## 9. Acessibilidade

- ✅ `aria-live="polite"` e `aria-label="Notifications"` no container de toasts (`ToastContainer.vue:32,35`)
- ✅ `aria-hidden="true"` em ícones decorativos Heroicons: `ToastContainer.vue`, `ColumnHeader.vue`, `ParticipantPanel.vue`, `board/FocusCard.vue`, `index.vue` hero SVGs
- ✅ `role="alert"` em cada toast individual (`ToastContainer.vue:48`)
- ✅ `aria-label` no botão dismiss de toast: `"Dismiss notification: {message}"` (`ToastContainer.vue:53`)
- ✅ `aria-label` nos indicadores online/offline de participantes (`ParticipantPanel.vue:91`)
- ✅ `aria-label="Participants panel"` e `aria-label="Participant list"` e `aria-label="Access log"` (`ParticipantPanel.vue`)
- ✅ `aria-label="Session phase"` no nav do `PhaseCarousel.vue`
- ✅ `aria-label="Add card"` e `title="Add card"` no `ColumnHeader.vue`
- ✅ Labels associados a inputs nas páginas de auth: `<label for="email">Email</label>` + `<input id="email">` em `login.vue` e `register.vue`
- ✅ Labels em `retro/invite/[token].vue`: `for="guest-name"` / `for="guest-email"`
- ✅ `role="alert"` em mensagens de erro dos forms (`login.vue:65`, `register.vue:63`)
- ✅ `focus-visible:ring-1 focus-visible:ring-[#00f2ff]/60` em todos os elementos interativos via `@layer base`
- ⚠️ Labels nos inputs do `CardComposer`: **ausentes** — inputs usam apenas `placeholder`. Sem `<label>` associado.
- ⚠️ Labels nos campos do `ActionItemForm`: **ausentes** — fields usam apenas `placeholder`. Sem `<label>`.
- ⚠️ Labels nos inputs do `retro/create.vue`: **ausentes** — campos de sprint, título, team_key, etc. sem `<label>`.
- ❌ Trap de foco em modais (`CardComposer`, `ActionItemForm`, `SettingsModal`, confirm dialog em `ActionsView`): **não implementado**. Foco não é preso no modal.
- ❌ `aria-hidden` nos ícones MDI: **ausentes**. Elementos `<span class="mdi mdi-*">` sem `aria-hidden`.
- ❌ `role` em elementos não-nativos interativos: `PhaseStepper` usa `<button>` (correto), mas `RetroCard article` com `@click` não tem `role="button"` nem `tabindex`.
- ⚠️ Contraste potencialmente baixo: `--fg-tertiary: #52525b` sobre `--bg-canvas: #050505` pode não atingir WCAG AA (ratio ~3.1:1). `text-zinc-600` (`#71717a`) sobre `#050505` tem ratio ~4.9:1 (passa AA para texto normal). `text-zinc-700` (`#3f3f46`) sobre `#050505` tem ratio ~2.7:1 (não passa AA).

---

## 10. O que nunca fazer

- **Nunca usar cores fora dos tokens definidos.** Toda cor deve vir de `--ds-*`, `--fg-*`, `--bg-*`, `--border-*`, `--neon-*`, `--col-*`, ou das classes Tailwind da paleta customizada (`brand-*`, `col-*`, `success-*`, `warning-*`, `danger-*`, `gray-*`). Valores hexadecimais hardcoded fora dos tokens existentes quebram a consistência do tema.

- **Nunca usar light mode.** Não existe paleta clara. Toda superfície é dark. Qualquer valor de fundo claro (`#fff`, `bg-white`, `bg-gray-100` no sentido Tailwind default) quebrará a UI.

- **Nunca adicionar novos ícones MDI.** Use `@heroicons/vue` (instalado). A dependência `@mdi/font` não está no `package.json`; os ícones MDI existentes são débito técnico que não renderiza corretamente.

- **Nunca criar componente de fase sem bifurcação facilitador/participante.** Todo componente de fase deve ter seções visuais distintas para cada papel. Botões de controle (`v-if="isFacilitator"`) não podem aparecer para participantes.

- **Nunca assumir que o WebSocket entregou estado completo.** O snapshot inicial tem `cards: []`, `votes: []`, `milestones: []`, `participants: []`. Componentes que dependem desses dados precisam aguardar a hidratação REST pós-conexão.

- **Nunca usar `shadow-card` ou `shadow-card-md`.** Estão definidos em `tailwind.config.ts` mas sem uso real. A sombra correta para elementos com glow é `shadow-glow` (`0 0 16px rgba(0,242,255,0.25)`).

- **Nunca usar `--bg-primary` ou `--bg-secondary` diretamente nos componentes.** O código existente usa `rgba()` literal ou `var(--bg-surface)` / `var(--bg-canvas)`. Os tokens `-primary`/`-secondary` estão definidos mas não são usados pelos componentes.

- **Nunca usar `bg-success-50`, `bg-warning-50`, `bg-danger-50` em novos componentes.** Esses shades `-50` não estão na paleta customizada (apenas 500/600/700 existem para success/warning/danger). Use `bg-success-500/10` ou equivalente RGBA.

- **Nunca colocar conteúdo no `AppHeader` em modo retro.** Em `mode="retro"`, `AppShell` substitui `AppHeader` por `RetroHeader`. O espaço do header no modo retro é ocupado por `PhaseCarousel` e timer; inserir conteúdo extra pode deslocar o layout.

- **Nunca criar animações CSS em `tailwind.config.ts`.** Animações existentes são todas scoped em `<style scoped>` nos componentes. Adicionar ao config espalha a animação globalmente sem controle.

- **Nunca remover o `focus-visible:ring` dos elementos interativos.** A regra de `@layer base` aplica `focus-visible:ring-1 focus-visible:ring-[#00f2ff]/60` globalmente. Sobrescrever com `outline: none` sem substituição quebra a acessibilidade por teclado.

- **Nunca exibir valores de `author_id` ou `author_name` diretamente de cards anônimos.** Use sempre `card.author_display` (que já retorna `"Anonymous"` quando `is_anonymous=true`). O `author_id` nunca chega ao cliente via REST quando o card é anônimo.

- **Nunca criar novo modal sem `Teleport to="body"`.** Modais fixos precisam estar fora do fluxo de stacking context do componente pai para `z-50` funcionar corretamente. Ver `ToastContainer.vue`, `history/[id].vue` exportModal.

- **Nunca usar `button-tertiary` ou `.input-primary` (de `ActionEditor.vue`).** Essas classes não existem no design system global. `ActionEditor.vue` é legado com classes scoped locais. Use `.button-secondary` e `.field-input` respectivamente.
