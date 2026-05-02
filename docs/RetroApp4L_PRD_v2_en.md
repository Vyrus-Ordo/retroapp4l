# RetroApp4L — Product Requirements Document (PRD)

**Version:** 2.0 — MVP (Zero-Cost Infrastructure)
**Date:** May 2026
**License:** MIT
**Status:** Open-source rewrite — consolidated after architecture review
**Audience:** Maintainers (review/infra/deploy), AI Agents (development execution), Contributors

> **Changelog v2.0:**
> - Rewritten as open-source project under MIT license
> - Removed all proprietary references and vendor-specific integrations
> - Design system migrated from proprietary framework to **Tailwind CSS**
> - Authentication changed to **local (email/password) + optional OAuth providers**
> - Frontend stack simplified to **Nuxt 3 + Tailwind CSS** (no Quasar dependency)
> - External tracker field generalized from single-vendor to any URL
> - Developer model generalized to **any AI coding agent** (Claude Code, Cursor, Copilot, etc.)
> - Infrastructure remains **zero-cost** using free-tier cloud platforms

---

## 1. Overview

RetroApp4L is an open-source web platform for conducting structured sprint retrospectives using the 4Ls methodology (Liked, Loathed, Longed for, Learned). It combines real-time collaboration, synchronized timers, and action item traceability — closing the loop between what's decided in a retro and what gets executed in the next sprint.

### 1.1 Problem

- Retrospectives conducted on generic tools (Miro, EasyRetro, FigJam) are disconnected from the team's workflow.
- Action items decided during retros rarely become trackable tasks in the team's project management tool.
- There is no mechanism to verify, in the next retro, whether actions from the previous sprint were completed.
- There is no centralized history of retrospectives to track team evolution across cycles.

### 1.2 MVP Goals

- Conduct 4L retrospectives with real-time collaboration (shared board + synchronized timer).
- Authenticate users via local credentials (email/password) with optional OAuth providers (Google, GitHub).
- Allow the facilitator to invite members via a private link.
- Verify previous sprint's actions before starting new reflection.
- Register action items with assignee and due date, ready for export to any external tracker.
- Automatically save all retrospectives for future reference.
- **MVP operates at zero infrastructure cost** using free-tier cloud platforms.

### 1.3 MVP Success Criteria

The MVP is considered successful if, after 60 days of use, the following indicators are met:

| Indicator | Target |
|---|---|
| Adoption | ≥ 80% of the team's retrospectives conducted on RetroApp4L |
| Traceability | ≥ 70% of action items registered with assignee and due date filled |
| Review | ≥ 50% of sessions include verification of previous sprint's actions |
| Stability | Zero board desynchronization incidents in production |
| Satisfaction | Internal NPS ≥ 7 after survey with facilitators (minimum 5 responses) |
| Cost | Total infrastructure cost = $0.00 during MVP period |

### 1.4 Out of MVP Scope

- Integration with external project management APIs (field reserved in schema; no runtime integration).
- Export to PDF, CSV, or DOCX.
- Card masking during the writing phase.
- Report and analytics features for cross-sprint trends.
- Drag-and-drop for card grouping (phase 2).

---

## 2. Development Premises

### 2.1 Execution Model

- **The developer is any AI coding agent** (Claude Code, Cursor, Copilot Workspace, Aider, etc.) running autonomously per session.
- **The maintainer (human)** is responsible for: code review, infrastructure decisions, environment configuration, deployment, writing and validating the handoff document at the end of each sprint.
- AI agents **do not retain memory between sessions**. All necessary context must be in the handoff document. If it's not in the handoff, it doesn't exist for the next session.

### 2.2 Architectural Consequences

- **Convention over configuration:** code must follow idiomatic Django patterns and Tailwind CSS utility-first approach.
- **Predictable file structure:** defined in Sprint 1 and never changed without explicit update in the handoff.
- **Tests as living documentation:** each sprint produces tests that describe the implemented behavior.
- **No implicit "magic":** avoid patterns that depend on global state or implicit behavior that's hard to trace.

### 2.3 Responsibilities by Role

| Responsibility | AI Agent | Maintainer |
|---|---|---|
| Implement sprint features | ✅ | — |
| Write unit and integration tests | ✅ | Reviews |
| Create and update migrations | ✅ | Reviews and executes |
| Configure local environment (docker-compose) | ✅ | Validates |
| Provision infrastructure (Fly.io, Neon, Upstash, Vercel) | — | ✅ |
| Configure CI/CD (GitHub Actions) | Generates YAML | ✅ executes |
| Review PRs and validate behavior | — | ✅ |
| Write sprint handoff document | Generates draft | ✅ validates and signs |
| Product decisions not covered in PRD | — | ✅ |

---

## 3. User Profiles

### Facilitator

Team member responsible for creating and conducting the session. Prepares milestones before the retro, controls phase progression, configures the timer (with pause and resume), manages participant entry, and is the only one with permission to group cards and close the session.

**Key needs:** full control of the flow, visibility of all participants' state, agile tools for grouping, ability to intervene in any phase without blocking the session.

### Participant

Team member invited via link. Can create, edit, and delete their own cards, vote (only on designated columns), participate in debate, and register action items. Cannot advance phases, group cards, manage participant entry, or close the session.

**Key needs:** fast interface to add cards, clarity on which phase is active and what's expected, visibility of milestones and the focused card during debate.

---

## 4. User Stories

### Facilitator

**US-01 — Create session**
> As a facilitator, I want to create a retrospective session by entering the sprint name and a team identifier, so the team has context before joining the board and retros can be grouped by team.

**Acceptance criteria:**
- Required field: sprint name.
- Required field: `team_key` (team identifier, slug-style). Dropdown with suggestions of values previously used by the facilitator.
- Optional field: free-form description.
- Session starts in `setup` state (offline preparation).

---

**US-02 — Invite participants**
> As a facilitator, I want to share a private invite link so that only the right people join the session.

**Acceptance criteria:**
- Link contains a UUID v4 token, generated when the facilitator activates the lobby.
- The link can be revoked by the facilitator at any time.
- When accessing the link, the participant must be authenticated before entering.
- After the facilitator starts the session (status other than `lobby`), the link is automatically blocked for new entries.
- Attempts to enter with a blocked link display an informative message.

---

**US-02b — Manage entry after session start**
> As a facilitator, I want to temporarily allow access to participants who couldn't join before the session started, to ensure no one is excluded due to being late.

**Acceptance criteria:**
- Participant panel displays link status (active/blocked) only for the facilitator.
- "Allow new entry" button reactivates the link for 2 minutes or until the next admission, whichever comes first.
- After admission or expiration, the link is automatically re-blocked.
- Action is recorded in `AccessLog`.
- Already-present participants are not affected.
- New participant receives a complete session snapshot via WebSocket.

---

**US-03 — Control phases**
> As a facilitator, I want to advance phases manually so the team doesn't move to the next stage before being ready.

**Acceptance criteria:**
- Phase advance button visible only for the facilitator.
- On advance, all participants receive the `phase.changed` event in real time.
- The facilitator can advance even before the timer reaches zero.
- Mandatory confirmation before advancing to the closing phase.
- Facilitator can pause and resume the timer in any timed phase. Pause state reflected for all via `timer.paused` and `timer.resumed`.

---

**US-04 — Configure dot voting**
> As a facilitator, I want to define the number of votes per participant before the voting phase to ensure prioritization is enforced.

**Acceptance criteria:**
- Configuration available in lobby or before the voting phase.
- Default value: 3 votes per participant.
- Allowed range: 1 to 10 votes.
- Remaining votes counter visible for each participant during voting.

---

**US-05 — Close session**
> As a facilitator, I want to close the session and save the result so the team can review history later.

**Acceptance criteria:**
- Close button available only in the `actions` phase.
- Mandatory confirmation with warning about action items without an assignee.
- On close, the session changes to `closed` and appears in the history dashboard.

---

**US-07a — Prepare milestones (Facilitator)**
> As a facilitator, I want to record sprint milestones before starting the retrospective, to arrive at the session with organized context and ensure important events aren't forgotten.

**Acceptance criteria:**
- Available on the preparation screen (`setup`), before activating the lobby.
- Categories: Achievement, Challenge, Change, Recognition, Other.
- Free-text field for description (max 500 characters).
- Facilitator can add, edit, and delete milestones during preparation.
- Milestones are saved and available for presentation.

---

**US-07c — Present milestones at session start**
> As a facilitator, I want to present the sprint milestones I prepared before the session, to align the team on important events before reviewing pending actions.

**Acceptance criteria:**
- Dedicated presentation screen (phase `presentation`) displaying milestones registered during preparation.
- Participants view in real time, read-only.
- Facilitator controls navigation between milestones and can comment verbally.
- "Advance to Action Check" button available only for the facilitator.
- If there are no milestones, the phase is automatically skipped.
- Milestones remain visible as context (sidebar/header) during subsequent phases.

---

**US-09 — Group cards (Facilitator)**
> As a facilitator, I want to group similar cards efficiently, to eliminate duplicates before voting and focus the discussion.

**Acceptance criteria:**
- Only the facilitator sees grouping controls.
- Grouping via multi-select: facilitator checks cards and uses "Group selected" action.
- Cards can only be grouped with others from the **same column**.
- Grouped cards are displayed nested under the parent card.
- Facilitator can ungroup cards.
- Phase without timer: facilitator advances manually when done.
- `card.grouped` and `card.ungrouped` events transmitted to all in real time.

---

**US-12 — Conduct focused debate (Facilitator)**
> As a facilitator, I want to conduct a structured discussion about the most-voted cards, so the team understands context and generates action ideas before recording them.

**Acceptance criteria:**
- Screen displays cards sorted by vote count (descending).
- Visual highlight for the top 3–5 most voted.
- Facilitator clicks a card to "put in focus", expanding it and signaling to all participants which point is being discussed.
- Only the facilitator controls navigation between focused cards.
- No CRUD or voting is allowed in this phase (read-only).
- Timer visible with pause/extend/advance controls.
- Facilitator can end debate and advance to Actions phase.

---

### Participant

**US-06 — Verify previous actions**
> As a participant, I want to see previous retro actions at the start of the session so the team can evaluate what was completed before reflecting on the new sprint.

**Acceptance criteria:**
- Optional phase configurable by the facilitator.
- Displays action items from the last retro **with the same `team_key`** that is `closed`.
- Participants can mark each action as "Done", "In progress", or "Not started".
- Status is saved and visible in the previous retro's history.

---

**US-07b — View milestones (Participant)**
> As a participant, I want to see the sprint milestones registered by the facilitator, to have shared context during the 4L reflection.

**Acceptance criteria:**
- Milestones visible in all phases (except lobby) as collapsible sidebar or header.
- Displayed in chronological creation order.
- Read-only for participants.

---

**US-08 — Add card to board**
> As a participant, I want to add a card to any column of the 4L board, to register my perception about the sprint.

**Acceptance criteria:**
- Four columns available: Liked, Loathed, Longed for, Learned.
- Created card appears for all in real time (`card.created` event).
- Only the author can edit or delete their own card.
- 500-character limit per card.

---

**US-10 — Vote on priority cards**
> As a participant, I want to distribute my votes among cards in the "Loathed" and "Longed for" columns, to highlight the points that most need discussion and resolution.

**Acceptance criteria:**
- Only cards in `loathed` and `longed` columns are votable. `loved` and `learned` cards do not show a vote option.
- Number of votes per participant defined by the facilitator (default: 3, range: 1–10).
- **Maximum 1 vote per card per participant.**
- Remaining votes counter visible and updated in real time.
- Vote can be undone while the voting phase is open.
- Cannot vote on your own card.
- `vote.cast` and `vote.revoked` events transmitted to all in real time.
- If a participant has remaining votes but no votable cards available (e.g., all remaining cards are their own), display an informative message and allow the facilitator to advance the phase.

---

**US-11 — Register action item**
> As a participant, I want to register an action item linked to a card so that what was decided in the retro becomes a trackable task.

**Acceptance criteria:**
- Required fields: description and assignee (dropdown of participants).
- Optional field: due date (date picker).
- Action can be linked to a specific card or created independently.
- Field `external_tracker_url` visible as an optional URL input (for linking to GitHub Issues, Linear, Trello, etc.).

---

## 5. Retrospective Session Flow

| Phase | Default Duration | Who Can Edit | Description |
|---|---|---|---|
| Preparation (offline) | — | Facilitator | Facilitator creates session, defines `team_key`, registers sprint milestones. Session in `setup`. |
| Lobby | — | Facilitator (control) | Facilitator generates invite link. Participants arrive and authenticate. |
| Presentation | — (no timer) | Facilitator (speaks) / All (view) | Facilitator presents milestones registered during preparation. Shared context before action review. If no milestones, phase is skipped. |
| Action Check | 5 min | All | Review of action items from last retro with same `team_key`. Participants mark status. Optional phase. |
| Board 4L | 10 min | All | 4-column reflection (Liked, Loathed, Longed for, Learned) with milestones visible as context. |
| Grouping | Flexible (no timer) | **Facilitator** | Facilitator groups duplicate cards from the same column via multi-select. |
| Voting | 5 min | All | Dot voting **only on "Loathed" and "Longed for" columns**. Max 1 vote per card per participant. |
| Debate | 10 min | All (read) / Facilitator (control) | Focused discussion on most-voted cards. Facilitator puts cards "in focus" to guide conversation. |
| Actions | 10 min | All | Register action items with description, assignee, and due date. |
| Closed | — | Facilitator | Session saved to history. |

---

## 6. Tech Stack

### 6.1 Development Stack

| Layer | Technology | Version | Justification |
|---|---|---|---|
| **Backend** | Python + Django | 3.12 / 5.x | Mature ecosystem; highly idiomatic for AI coding agents |
| **REST API** | Django REST Framework | 3.15+ | Industry standard for Django APIs |
| **WebSocket** | Django Channels + ASGI | 4.x | Official Django WebSocket solution |
| **ASGI Server** | Daphne | 4.x | Reference server for Django Channels |
| **Async Tasks** | Celery + Celery Beat | 5.x | Server-side timer and future tasks |
| **Channel Layer / Broker** | Redis | 7.x | Required backend for Django Channels + Celery broker |
| **Database** | PostgreSQL | 16 | Native UUID; predictable behavior with Django ORM |
| **Authentication** | django-allauth | 0.6x+ | Local auth (email/password) + optional OAuth providers (Google, GitHub) |
| **Frontend** | Nuxt 3 (Vue 3) | 3.x | Modern Vue 3 SSR/SPA framework |
| **CSS Framework** | Tailwind CSS | 3.x | Utility-first, zero runtime, fully customizable via config |
| **Icons** | Lucide Icons (Vue) | latest | Open-source, tree-shakeable, MIT licensed |
| **Local Dev** | Docker + docker-compose | — | Reproducible local environment (development only) |

### 6.2 Infrastructure (MVP Zero-Cost)

| Service | Platform | Free Tier | What it Hosts |
|---|---|---|---|
| **Backend Django + Daphne** | [Fly.io](https://fly.io) | Up to 3 shared VMs (256 MB RAM each), 3 GB storage | Django app with ASGI (Daphne) |
| **Celery Worker + Beat** | Fly.io (second VM) | Same free tier | Async timer processing |
| **PostgreSQL** | [Neon](https://neon.tech) | 0.5 GB storage, unlimited connections | Main database |
| **Redis** | [Upstash](https://upstash.com) | Up to 256 MB, 1000 simultaneous connections | Channel Layer (WebSocket) + Celery broker/result backend |
| **Frontend SPA** | [Vercel](https://vercel.com) | 100 GB bandwidth, unlimited builds | Nuxt 3 static/SPA |
| **OAuth (optional)** | Google Cloud Console / GitHub | Free (OAuth credentials) | Optional SSO via django-allauth |

### 6.3 Deployment Architecture

```
[Frontend Nuxt SPA] (Vercel)
        |
[Fly.io App (Django + Daphne)] --> [Neon PostgreSQL]
        |                           [Upstash Redis]
[Fly.io Worker (Celery + Celery Beat)]

Development environment: docker-compose with local PostgreSQL and Redis
```

**Daphne** as the ASGI server in the same Django process (default configuration). Fly.io exposes HTTP and WebSocket ports.

**Celery Worker** and **Beat** run as a second VM on Fly.io using the same codebase with worker/beat commands. If memory is tight, worker can run in the same container as the app during MVP.

**Neon** and **Upstash** are external services accessible via internet. Latency acceptable for internal applications.

### 6.4 Free Tier Limitations and Mitigation

| Limitation | Impact | Mitigation |
|---|---|---|
| **Fly.io: 256 MB RAM per VM** | Memory may be tight with 30 simultaneous connections | Run worker in same container; monitor usage. If needed, migrate to Oracle Cloud Free (24 GB RAM) |
| **Cold start after inactivity (Fly.io and Vercel)** | First access may take 2-5 seconds | Facilitator accesses the app minutes before the retro ("warm-up"); scheduled usage, not continuous |
| **Neon: 0.5 GB storage** | History of many retros may consume space | Estimate: 100 cards/retro × 500 bytes + participants + actions ≈ 100 KB/retro. In 60 days (~24 retros), consumption < 5 MB. Plenty of room |
| **Upstash: 256 MB Redis** | WebSocket messages and Celery tasks share memory | Low message volume (timer every 5s, card events). Team of 30 generates low traffic. Configure TTL for expired keys |

### 6.5 Repository Structure

```
retroapp4l-backend/       # Django — REST API + WebSocket
retroapp4l-frontend/      # Nuxt 3 + Tailwind CSS — SPA
```

### 6.6 Django App Structure (immutable after Sprint 1)

```
retroapp/
├── config/              # settings, urls, asgi, wsgi
├── apps/
│   ├── users/           # Model User, OAuth callback, authentication
│   ├── retrospectives/  # Models Retrospective, Participant, Milestone, AccessLog, phases
│   ├── cards/           # Models Card, CardVote, grouping
│   ├── actions/         # Model ActionItem, action check
│   └── realtime/        # WebSocket Consumers, events, Channel Groups
├── tasks/               # Celery tasks (sync_timer, etc.)
└── tests/               # Mirrors the apps/ structure
```

---

## 7. Design System (Tailwind CSS)

> **Instruction for AI agents:** this section is the source of truth for all visual decisions on the frontend. No color, font, spacing, or component should be invented. If it's not here, consult the maintainer before proceeding.

### 7.1 Overview

RetroApp4L uses **Tailwind CSS** as its design foundation, extended via `tailwind.config.js` with semantic tokens for the application's specific needs. No proprietary UI framework is required — all components are built from Tailwind utilities and custom CSS where needed.

**Setup:** Install Tailwind CSS via the `@nuxtjs/tailwindcss` module. All custom tokens are defined in `tailwind.config.js`.

### 7.2 Typography

- **Font:** Inter exclusively (loaded via `@fontsource/inter` or Google Fonts). Weights: 300, 400, 500, 600, 700.
- **Letter-spacing:** `tracking-tight` (-0.01em) on all text except captions (normal tracking).
- **Headings:** always `font-semibold` (600).
- **Tone of voice:** English by default, second person informal ("you"). No emoji on product surfaces. Errors are factual, not dramatic. Localization-ready via i18n.

**Type scale — Tailwind classes to use on the frontend:**

| Semantic Name | Tailwind Classes | Equivalent | Use in RetroApp4L |
|---|---|---|---|
| `heading-lg` | `text-2xl font-semibold leading-8` | 24px/32px/600 | Retrospective title, sprint name |
| `heading-md` | `text-xl font-semibold leading-7` | 20px/28px/600 | Board column title (Liked, Loathed...) |
| `heading-sm` | `text-lg font-semibold leading-6` | 18px/24px/600 | Section title (Presentation, Debate) |
| `body-md` | `text-base font-normal leading-6` | 16px/24px/400 | Body text, descriptions |
| `body-sm-medium` | `text-sm font-medium leading-5` | 14px/20px/500 | Field labels, card text |
| `body-sm` | `text-sm font-normal leading-5` | 14px/20px/400 | Secondary text, card metadata |
| `label-sm-semibold` | `text-xs font-semibold leading-4` | 12px/16px/600 | Phase chips, vote badges |
| `label-sm` | `text-xs font-normal leading-4` | 12px/16px/400 | Timestamps, tertiary text |
| `caption` | `text-[10px] font-normal leading-3 tracking-normal` | 10px/12px/400 | Counters |

### 7.3 Color Palette

Define these in `tailwind.config.js` under `theme.extend.colors`:

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#eff8ff',
          500: '#009EFB',
          600: '#007BD4',
          700: '#0062AB',
        },
        success: {
          50:  '#ecfdf5',
          600: '#00a46e',
        },
        warning: {
          50:  '#fff7ed',
          500: '#ed7713',
        },
        danger: {
          500: '#f34f4f',
        },
      }
    }
  }
}
```

**Semantic color mapping (use these, not primitives directly):**

| Semantic Token | Tailwind Class | Value | Use |
|---|---|---|---|
| Foreground primary | `text-gray-950` | `#252527` | All primary text |
| Foreground secondary | `text-gray-700` | `#4c4c52` | Supporting text |
| Foreground tertiary | `text-gray-500` | `#696a71` | Metadata, timestamps |
| Foreground brand | `text-brand-500` | `#009EFB` | Highlights, links |
| Background primary | `bg-white` | `#ffffff` | Page and card background |
| Background secondary | `bg-gray-50` | `#f5f5f6` | Board background, columns |
| Background tertiary | `bg-gray-100` | `#e6e6e7` | Column headers |
| Border primary | `border-gray-300` | `#adadb3` | Input and card borders |
| Border secondary | `border-gray-200` | `#e5e5e5` | Internal dividers |

**Color mapping per 4L board column:**

| Column | Header Color | Badge Color | Rationale |
|---|---|---|---|
| Liked (Loved) | `bg-success-600 text-white` | `bg-success-50 text-success-600` | Green = positive |
| Loathed | `bg-warning-500 text-white` | `bg-warning-50 text-warning-500` | Orange = attention |
| Longed for | `bg-brand-500 text-white` | `bg-brand-50 text-brand-500` | Blue = desire/expectation |
| Learned | `bg-gray-700 text-white` | `bg-gray-50 text-gray-700` | Neutral = knowledge |

### 7.4 Spacing

Strict 4-pt scale. Use Tailwind's native spacing tokens:

| Tailwind | Value | Typical Use in RetroApp4L |
|---|---|---|
| `gap-2` / `p-2` | 8px | Gap between icon and label; chip internal padding |
| `gap-3` / `p-3` | 12px | Form field internal gap |
| `gap-4` / `p-4` | 16px | Card padding; gap between cards in column |
| `gap-6` / `p-6` | 24px | Section separator; mobile padding |
| `gap-8` / `p-8` | 32px | Desktop horizontal padding |
| `gap-10` / `p-10` | 40px | Desktop section vertical padding |

### 7.5 Borders, Radii, and Shadows

**Border radius:**

| Tailwind | Value | Use in RetroApp4L |
|---|---|---|
| `rounded` | 4px | Phase chips, vote badges |
| `rounded-lg` | 8px | Inputs, retro cards |
| `rounded-xl` | 12px | Modals |
| `rounded-2xl` | 16px | Larger cards, panels |
| `rounded-3xl` | 24px | Main containers |
| `rounded-full` | 999px | Avatars, participant pills |

**Shadows:**

| Tailwind | Use in RetroApp4L |
|---|---|
| `shadow-sm` | Retro cards (floating) |
| `shadow-md` | Board column on hover |
| `shadow-lg` | Grouping modal |
| `shadow-xl` | Assignee dropdown in action items |
| `ring-2 ring-brand-500/20` | Form fields on focus |

### 7.6 Interaction States

Follow strictly — do not invent custom hover/focus styles:

| State | Rule |
|---|---|
| **Hover (solid button)** | Step to `-600` (e.g., `bg-brand-500` → `hover:bg-brand-600`) |
| **Pressed (solid button)** | Step to `-700` (`active:bg-brand-700`) |
| **Hover (flat/outline)** | `hover:bg-brand-50` text to `-600` |
| **Disabled** | `bg-gray-300` or `bg-gray-100`; text `text-gray-300`; `cursor-not-allowed opacity-50` |
| **Focus** | `focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black` |

### 7.7 Iconography

- **Library:** Lucide Icons for Vue (`lucide-vue-next`) — MIT licensed, tree-shakeable.
- **Style:** outline (stroke) variant by default, consistent 24px size.
- **Position in buttons:** icon left with `gap-2`; icon right with `gap-2`.

**Icons defined for RetroApp4L:**

| Element | Lucide Icon |
|---|---|
| Create retrospective | `PlusCircle` |
| Copy invite link | `Link` |
| Advance phase | `ArrowRightCircle` |
| Timer | `Timer` |
| Pause timer | `PauseCircle` |
| Resume timer | `PlayCircle` |
| Card — Liked | `ThumbsUp` |
| Card — Loathed | `ThumbsDown` |
| Card — Longed for | `Clock` |
| Card — Learned | `Lightbulb` |
| Milestone | `Flag` |
| Voting | `Circle` (small dot) |
| Action item | `CheckCircle` |
| Participant online | `Circle` (filled green, 8px) |
| Edit card | `Pencil` |
| Delete card | `Trash2` |
| Group card | `GitMerge` |
| Ungroup card | `GitBranch` |
| Card in focus (debate) | `Focus` |
| Close session | `Lock` |
| Allow entry | `UserPlus` |
| Link blocked | `LinkOff` |
| External tracker (optional) | `ExternalLink` |

### 7.8 UI Components Specific to RetroApp4L

#### RetroCard (board card)

```
┌─────────────────────────────────┐
│  [avatar 24px] Name · timestamp │  ← text-xs text-gray-500
│                                 │
│  Card content                   │  ← text-sm font-medium text-gray-950
│                                 │
│  [✎] [🗑] · [● 3 votes]        │  ← Lucide icons, text-xs
│  [☐] (grouping checkbox)       │  ← visible only for facilitator
└─────────────────────────────────┘
```
- Background: `bg-white`
- Border: `border border-gray-200`
- Border-radius: `rounded-lg` (8px)
- Padding: `p-4` (16px)
- Shadow: `shadow-sm`
- Hover: `shadow-md`
- Checkbox visible only in grouping phase and only for facilitator
- Vote icon visible only for `loathed` and `longed` cards in voting phase
- "Your card — not votable" indicator on own cards during voting

#### MilestoneCard (milestone card)

```
┌─────────────────────────────────┐
│  🏆 Achievement                 │  ← text-xs font-semibold, category color
│                                 │
│  Incident-free Friday deploy    │  ← text-sm font-medium text-gray-950
│                                 │
│  Facilitator · timestamp        │  ← text-[10px] text-gray-500
└─────────────────────────────────┘
```

#### PhaseChip (active phase chip)

```
[ ● Current phase  10:00 ]
```
- Background: `bg-brand-50`
- Text: `text-brand-500`
- Font: `text-xs font-semibold`
- Border-radius: `rounded` (4px)
- Padding: `px-2 py-1`

#### VoteBadge (card vote counter)

```
[ ● 5 ]
```
- Dot color: `text-brand-500`
- Font: `text-xs font-semibold`
- Own votes: highlight with `bg-brand-50`

#### TimerDisplay (timer)

```
[ ⏱ 08:42 ]  [ ⏸ ]  [ ▶ ]
```
- Font: `text-xl font-semibold` when > 1min
- Normal color: `text-gray-950`
- Alert color (< 60s): `text-warning-500`
- Critical color (< 30s): `text-danger-500`
- Transition: `transition-colors duration-150`
- Pause/resume buttons visible only for facilitator

#### ParticipantPanel (participant panel)

```
┌─────────────────────────────────────────────────┐
│  Participants (3 online)                         │
│                                                 │
│  ● Ana (online)                                 │
│  ● Bruno (online)                               │
│  ● Carol (online)                               │
│                                                 │
│  ─────────────────────────────────────────────  │
│  🔒 Invite link: BLOCKED                        │
│  The session has already started.                │
│                                                 │
│  [Allow new entry]                              │
│                                                 │
│  Access history:                                │
│  • Ana joined at 14:02                          │
│  • Bruno joined at 14:03                        │
│  • Carol joined at 14:04                        │
│  • Link reopened at 14:12                       │
│  • Daniel joined at 14:13                       │
│  • Link auto-blocked at 14:13                   │
└─────────────────────────────────────────────────┘
```
- Admin section visible only for facilitator
- Link status updated in real time

#### MilestoneBar (milestone bar)

```
┌──────────────────────────────────────────────────┐
│  🏆 Incident-free deploy  ⚡ API Bug              │
│  🙌 Ana covered on-call                          │  ← collapsible
└──────────────────────────────────────────────────┘
```
- Visible during Board, Grouping, Voting, Debate, and Actions
- Ordered by `created_at`

#### ColumnHeader (board column header)

```
┌────────────────────────────────────┐
│  [icon]  LIKED             [3 cards]│
└────────────────────────────────────┘
```
- Background: column semantic color (see 7.3)
- Font title: `text-sm font-semibold uppercase tracking-wide`
- Font counter: `text-xs font-normal`
- Border-radius: `rounded-lg rounded-b-none`
- Padding: `px-4 py-2`

#### FocusCard (card in focus during debate)

```
┌───────────────────────────────────────────────┐
│  ⭐ IN FOCUS                                   │
│                                               │
│  Loathed — "Unstable API on Black Friday"     │
│  ● 8 votes                                    │
│                                               │
│  ───────────────────────────────────────────  │
│  Up next:                                     │
│  • Longed for — "Metrics dashboard" (5)       │
│  • Loathed — "Slow review cycle" (4)          │
│  [Next card ▶]                                │
└───────────────────────────────────────────────┘
```
- Visible only during Debate phase
- Navigation controls only for facilitator

### 7.9 Board Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  [RetroApp4L]  Sprint 42 — Retro  [Phase: Board 4L ⏱ 08:42]     │
│                                    [● Ana] [● Bruno] [● Carol]   │
├──────────────────────────────────────────────────────────────────┤
│  🏆 Deploy  ⚡ Bug API  🙌 Ana on-call              [collapsible]│
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  👍 LIKED   │ 👎 LOATHED   │  ⏰ LONGED   │  💡 LEARNED        │
│  ─────────  │  ─────────── │  ──────────  │  ──────────────    │
│  [card]     │  [card]      │  [card]      │  [card]            │
│  [card]     │              │              │  [card]            │
│             │              │              │                    │
│  [+ Add card]                                                  │
└──────────────┴──────────────┴──────────────┴────────────────────┘
```
- Milestone bar between header and board
- Horizontal padding: `px-8` (32px) desktop
- Gap between columns: `gap-4` (16px)
- Board background: `bg-gray-50`

### 7.10 Content and Voice Rules

- All interface text in English by default. Localization-ready via `@nuxtjs/i18n` or equivalent.
- Second person informal: "Add card", "Your remaining votes: 2".
- Sentence case in labels and buttons: "Advance phase", "Close session".
- Errors: factual and direct. "Required field." — not "Oops! Something went wrong."
- No emoji on product surfaces. Lucide icons replace emoji.
- Dates: ISO-style `YYYY-MM-DD` or locale-formatted via i18n for timestamps.
- Vote numbers: always integers. No decimals.

---

## 8. Data Model

### users_user *(app: users)*

| Field | Django Type | SQL Type | Description |
|---|---|---|---|
| id | UUIDField (PK) | uuid | |
| name | CharField(200) | varchar(200) | Full name |
| email | EmailField (unique) | varchar(254) | Login email |
| password | CharField (hashed) | varchar(128) | Hashed password (local auth) |
| avatar_url | URLField (nullable) | varchar(200) | Avatar URL (from OAuth or Gravatar) |
| oauth_provider | CharField(50, nullable) | varchar(50) | `google`, `github`, or null (local) |
| oauth_id | CharField(200, nullable) | varchar(200) | OAuth provider ID |
| is_active | BooleanField | boolean | Django default |
| created_at | DateTimeField(auto_now_add) | timestamptz | |

### retrospectives_retrospective *(app: retrospectives)*

| Field | Django Type | SQL Type | Description |
|---|---|---|---|
| id | UUIDField (PK) | uuid | |
| title | CharField(255) | varchar(255) | Retrospective title |
| sprint_name | CharField(100, nullable) | varchar(100) | Sprint name |
| team_key | CharField(100) | varchar(100) | Team identifier (slug). Required on creation. |
| facilitator | ForeignKey(User) | uuid FK | |
| status | CharField(choices) | varchar(20) | `setup\|lobby\|presentation\|check\|board\|grouping\|voting\|discussion\|actions\|closed` |
| invite_token | UUIDField (unique, nullable) | uuid | Invite link token |
| invite_revoked_at | DateTimeField (nullable) | timestamptz | |
| max_votes_per_user | IntegerField (default=3) | integer | |
| skip_check_phase | BooleanField (default=False) | boolean | |
| timer_started_at | DateTimeField (nullable) | timestamptz | |
| timer_paused_at | DateTimeField (nullable) | timestamptz | If filled, timer is paused. |
| timer_duration_seconds | IntegerField (nullable) | integer | |
| created_at | DateTimeField(auto_now_add) | timestamptz | |
| closed_at | DateTimeField (nullable) | timestamptz | |

### retrospectives_milestone *(app: retrospectives)*

| Field | Django Type | SQL Type | Description |
|---|---|---|---|
| id | UUIDField (PK) | uuid | |
| retrospective | ForeignKey(Retrospective) | uuid FK | |
| author | ForeignKey(User) | uuid FK | Always the facilitator |
| category | CharField(choices) | varchar(20) | `achievement\|challenge\|change\|recognition\|other` |
| description | TextField | text | Max 500 characters |
| created_at | DateTimeField(auto_now_add) | timestamptz | |

### retrospectives_participant *(app: retrospectives)*

| Field | Django Type | SQL Type | Description |
|---|---|---|---|
| id | UUIDField (PK) | uuid | |
| retrospective | ForeignKey(Retrospective) | uuid FK | |
| user | ForeignKey(User) | uuid FK | |
| votes_remaining | IntegerField | integer | Decremented on each `vote.cast` |
| joined_at | DateTimeField(auto_now_add) | timestamptz | |

`unique_together: (retrospective, user)`

### retrospectives_accesslog *(app: retrospectives)*

| Field | Django Type | SQL Type | Description |
|---|---|---|---|
| id | UUIDField (PK) | uuid | |
| retrospective | ForeignKey(Retrospective) | uuid FK | |
| action | CharField(choices) | varchar(20) | `opened\|closed\|participant_joined` |
| triggered_by | ForeignKey(User, nullable) | uuid FK | Facilitator or null (system) |
| participant | ForeignKey(User, nullable) | uuid FK | Filled when `participant_joined` |
| timestamp | DateTimeField(auto_now_add) | timestamptz | |

### cards_card *(app: cards)*

| Field | Django Type | SQL Type | Description |
|---|---|---|---|
| id | UUIDField (PK) | uuid | |
| retrospective | ForeignKey(Retrospective) | uuid FK | |
| author | ForeignKey(User) | uuid FK | |
| column | CharField(choices) | varchar(20) | `loved\|loathed\|longed\|learned` |
| content | TextField | text | Max 500 characters |
| group | ForeignKey('self', nullable) | uuid FK | Parent card of group |
| position | IntegerField (default=0) | integer | |
| created_at | DateTimeField(auto_now_add) | timestamptz | |

### cards_cardvote *(app: cards)*

| Field | Django Type | SQL Type | Description |
|---|---|---|---|
| id | UUIDField (PK) | uuid | |
| card | ForeignKey(Card) | uuid FK | |
| voter | ForeignKey(User) | uuid FK | |
| created_at | DateTimeField(auto_now_add) | timestamptz | |

> `unique_together: (card, voter)` — ensures max 1 vote per card per participant.

### actions_actionitem *(app: actions)*

| Field | Django Type | SQL Type | Description |
|---|---|---|---|
| id | UUIDField (PK) | uuid | |
| retrospective | ForeignKey(Retrospective) | uuid FK | |
| card | ForeignKey(Card, nullable) | uuid FK | Source card |
| description | TextField | text | |
| assignee | ForeignKey(User) | uuid FK | |
| due_date | DateField (nullable) | date | |
| status | CharField(choices) | varchar(20) | `pending\|in_progress\|done` |
| external_tracker_url | URLField(nullable) | varchar(200) | Optional link to external tracker (GitHub Issues, Linear, etc.) |
| created_at | DateTimeField(auto_now_add) | timestamptz | |

---

## 9. WebSocket Events

Channel: `retro_{retrospective_id}` (Django Channels Group)

Authentication: custom middleware validates JWT before accepting connection. Connections without a valid token are refused with code 4001.

**Initial connection and reconnection:**
- On connect, a new participant (no `Participant` record) receives `session.snapshot` with complete session state.
- An existing participant on reconnection receives `session.snapshot` for resync.
- Reconnection is always permitted regardless of invite link status.

| Event | Direction | Minimum Payload | Description |
|---|---|---|---|
| `session.snapshot` | Server → Client | `{phase, timer, cards[], votes[], milestones[], participants[], action_items[]}` | Complete snapshot for new participant or reconnection |
| `card.created` | Server → Clients | `{card}` | New card created |
| `card.updated` | Server → Clients | `{card_id, content}` | Card edited |
| `card.deleted` | Server → Clients | `{card_id}` | Card removed |
| `card.grouped` | Server → Clients | `{card_id, group_id}` | Cards grouped |
| `card.ungrouped` | Server → Clients | `{card_id, previous_group_id}` | Card ungrouped |
| `vote.cast` | Server → Clients | `{card_id, voter_id, votes_remaining}` | Vote registered |
| `vote.revoked` | Server → Clients | `{card_id, voter_id, votes_remaining}` | Vote undone |
| `milestone.created` | Server → Clients | `{milestone}` | Milestone registered |
| `action.check_updated` | Server → Clients | `{action_id, status}` | Previous action status updated |
| `phase.changed` | Server → Clients | `{phase, timer_duration_seconds}` | Facilitator advanced phase |
| `timer.sync` | Server → Clients | `{seconds_remaining}` | Remaining seconds (every 5s) |
| `timer.paused` | Server → Clients | `{seconds_remaining}` | Timer paused |
| `timer.resumed` | Server → Clients | `{seconds_remaining}` | Timer resumed |
| `timer.expired` | Server → Clients | `{phase}` | Timer reached zero |
| `participant.joined` | Server → Clients | `{user_id, name, avatar_url}` | New participant (during lobby) |
| `participant.joined_late` | Server → Clients | `{user_id, name, avatar_url}` | New participant joined after lobby |
| `participant.left` | Server → Clients | `{user_id}` | Participant left |

---

## 10. Functional Requirements

| # | Module | US | Description | Priority |
|---|---|---|---|---|
| RF-01 | Auth | — | Login via local credentials (email/password); optional OAuth providers (Google, GitHub) via `django-allauth` | Must Have |
| RF-02 | Session | US-01 | Facilitator creates session with `team_key` and sprint name; session starts in `setup` | Must Have |
| RF-03 | Session | US-02, US-02b | Participant accesses via invite link; link blocked after lobby; facilitator can reopen temporarily | Must Have |
| RF-04 | Phases | US-03 | Facilitator advances phases manually; pauses and resumes timer | Must Have |
| RF-05 | Timer | — | Server-side timer via Celery Beat; synced via `timer.sync` every 5s; pause support | Must Have |
| RF-06 | Milestones | US-07a, US-07c | Facilitator prepares milestones offline; presents them at session start (phase `presentation`) | Must Have |
| RF-07 | Milestones | US-07b | Milestones visible as context throughout the session (collapsible bar) | Must Have |
| RF-08 | Check | US-06 | Optional phase to review action items from previous retro with same `team_key` | Must Have |
| RF-09 | Board 4L | US-08 | Board with 4 real-time columns; cards with 500-character limit | Must Have |
| RF-10 | Cards | US-08 | Card CRUD; only the author can edit/delete their own card | Must Have |
| RF-11 | Grouping | US-09 | Facilitator groups cards from same column via multi-select | Must Have |
| RF-12 | Voting | US-04, US-10 | Dot voting restricted to "Loathed" and "Longed for" columns; 1 vote per card per participant limit | Must Have |
| RF-13 | Debate | US-12 | Debate phase with cards sorted by votes and "card in focus" control by facilitator | Must Have |
| RF-14 | Actions | US-11 | Register action items with description, assignee, and due date; optional external tracker URL | Must Have |
| RF-15 | History | US-05 | Closed sessions in dashboard with action item status | Must Have |
| RF-16 | Presence | — | Online participant list visible in real time; entry control panel | Should Have |
| RF-17 | Sound | — | Audible alert at timer end (Web Audio API) | Should Have |

---

## 11. Non-Functional Requirements

### 11.1 Performance
- WebSocket latency: < 200ms on internal network.
- Critical REST API read operations: < 300ms.
- `timer.sync` emitted every 5s; ±1s tolerance on client. Frontend client must interpolate countdown locally every 1s and correct with `timer.sync`.
- `session.snapshot` for new participants must be sent in < 1s.

### 11.2 Security
- WebSocket connections authenticated via JWT (`AuthMiddlewareStack`).
- Invite link UUID v4; manually revocable; automatically blocked after lobby.
- Self-vote blocked at application layer.
- Grouping and phase advance actions verify `request.user == retrospective.facilitator`.
- No endpoint accessible without authentication (`IsAuthenticated` as global default permission).
- Passwords hashed with Django's default PBKDF2 (or Argon2 if configured).

### 11.3 Availability
- MVP for internal use; no formal SLA.
- Deploy on Fly.io with basic auto-scaling.
- **Cold starts:** App may hibernate after inactivity on the free tier. Facilitators should access the app minutes before the retro to "warm up" the service. Typical cold start time: 2-5 seconds.

### 11.4 Scalability
- Django Channels + Redis Channel Layer (Upstash) supports multiple horizontal instances.
- Celery workers scale independently.
- Up to 30 simultaneous participants per session in MVP.
- Fly.io free tier (256 MB RAM) is sufficient for 30 simultaneous connections with moderate usage.

### 11.5 Code Quality
- Test coverage: minimum 80% on `retrospectives`, `cards`, and `actions` apps.
- Linting: `ruff` for Python, `eslint` + `prettier` for Nuxt frontend.
- Each sprint passes `python manage.py test` with no failures before handoff.

### 11.6 Accessibility and UI
- All components must respect `:focus-visible` with `outline: 2px solid #000; outline-offset: 2px` (Tailwind: `focus-visible:outline-2 focus-visible:outline-black focus-visible:outline-offset-2`).
- Minimum AA contrast between text and background.
- Animations limited to `color`, `background`, and `opacity` with duration `150ms` (Tailwind: `transition-colors duration-150`). No bounces or layout transforms.
- Timer audible alert uses Web Audio API with sinusoidal tones; does not depend on prior interaction if audio context initiated on first click.

---

## 12. Sprint Model and Handoff Document

### 12.1 Why the Handoff is Critical

AI agents do not retain memory between sessions. The handoff is the only mechanism that connects sprints. A vague handoff produces inconsistent code. A precise handoff produces predictable continuity.

**Rule:** if a technical decision is not in the handoff, it doesn't exist for the next session.

### 12.2 Mandatory Handoff Document Structure

```markdown
# Sprint N — Handoff

## Repository State
- Branch: main (or feature/sprint-N)
- Last commit: <hash> — <message>
- Pending migrations: yes/no

## What Was Implemented and Is Working
- [precise list, with references to files and functions]

## What Was Started and Not Completed
- [list with reason and exact stopping point]

## Technical Decisions Made This Sprint
- [decision] → [reason] → [affected file]

## Established Patterns That Must Be Followed
- [e.g.: "All consumers inherit from BaseRetroConsumer in realtime/base.py"]

## Next Sprint: What Must Be Done
- [ordered list, unambiguous, with done criteria]

## Commands to Resume
- docker-compose up -d
- python manage.py migrate
- python manage.py test
```

### 12.3 Sprint Planning

| Sprint | Focus | Deliverables | Handoff |
|---|---|---|---|
| 1 | Foundation | Project structure, Docker, PostgreSQL, initial migrations (includes `team_key`, `timer_paused_at`, `Milestone`, `AccessLog`, expanded status choices), local auth + optional OAuth (`django-allauth`), session creation with `team_key` | `SPRINT_1_HANDOFF.md` |
| 2 | Core Real-time | Django Channels + ASGI (Daphne), WebSocket consumers (includes `session.snapshot`, `timer.paused`, `timer.resumed`, `card.ungrouped`), phase state machine (10 states), timer with pause via Celery Beat, distinction between new entry and reconnection | `SPRINT_2_HANDOFF.md` |
| 3 | Board 4L + Milestones | Card CRUD with broadcast, `Milestone` model, milestone preparation, milestone presentation, `MilestoneBar`, real-time board with visible milestones | `SPRINT_3_HANDOFF.md` |
| 4 | Grouping + Voting | Multi-select grouping (facilitator), dot voting restricted to `loathed`/`longed`, 1 vote/card/person rule, `vote.revoked` | `SPRINT_4_HANDOFF.md` |
| 5 | Closing the Loop | Previous action check (by `team_key`), action items with status, Debate phase with focused card, session close, history dashboard | `SPRINT_5_HANDOFF.md` |
| 6 | Frontend | Setup Nuxt 3 + Tailwind CSS, implement all screens and components per section 7 of PRD, timer audible alert | `SPRINT_6_HANDOFF.md` |
| 7 | Polish + Quality | Entry control panel (block/reactivate post-lobby), real-time presence, E2E tests, coverage ≥ 80%, accessibility | `SPRINT_7_HANDOFF.md` |
| 8 | Integrations (future) | External tracker linking, PDF/CSV export, analytics | — |

> **Time premise:** each sprint is an AI agent session with no limit on human programming time. The maintainer reserves 2–4h per sprint for review, validation, and handoff sign-off.

### 12.4 Sprint Initialization Prompt

```
You are the developer of RetroApp4L, an open-source agile retrospective platform.

Read the file SPRINT_N_HANDOFF.md at the repository root.
It contains the current project state and exactly what must be done this sprint.

Follow the patterns established in previous sprints.
For the frontend, rigorously apply the Tailwind CSS design system described in section 7 of the PRD (custom colors in tailwind.config.js, Inter typography, color palette, 4-pt spacing, defined components).
When finished, generate the draft SPRINT_(N+1)_HANDOFF.md following the structure defined in the PRD.
Do not make architectural or visual decisions not covered in the PRD without explicitly recording them in the handoff for maintainer validation.
```

---

## 13. Recorded Decisions and Trade-offs

### 13.1 Django + PostgreSQL vs. other options
Python/Django was chosen for broad training coverage of AI coding agents with DRF + Django Channels. PostgreSQL for native UUID and predictable behavior with Django ORM.

### 13.2 Django Channels vs. managed solution
Self-hosted, no additional cost. Redis already required for Celery — adds no new infrastructure piece.

**Trade-off:** ASGI configuration (Daphne + Channels) more complex than traditional WSGI. Sprint 2 is the biggest technical risk.

### 13.3 Celery Beat for timer vs. asyncio in consumer
Celery Beat is explicit, testable, and auditable between AI agent sessions. Asyncio coupled to the consumer is difficult to test in isolation and to trace between sessions.

**Trade-off:** adds Celery worker and Beat scheduler in docker-compose and in the production VM.

### 13.4 Nuxt 3 + Tailwind CSS for the frontend
Nuxt 3 is the standard Vue 3 SPA/SSR framework. Tailwind CSS provides utility-first styling with zero runtime cost, full customizability via `tailwind.config.js`, and no vendor lock-in. Tree-shakeable, widely adopted, and well-documented for AI agent productivity.

**Trade-off:** Tailwind requires discipline in consistent class usage. The AI agent must prioritize the semantic tokens defined in section 7 over arbitrary Tailwind defaults when there's a style conflict.

### 13.5 Two repositories vs. monorepo
AI agents operate better with delimited scope per session. Backend in one session, frontend in another, without risk of context contamination.

### 13.6 `team_key` as string vs. full Team entity
Simple string allows immediate grouping in MVP without adding a team entity, member invitations, or complex permissions. Sufficient for action check and history dashboard. Future evolution can migrate to a `Team` entity with foreign key.

### 13.7 Milestone separated from Card
Milestones have a distinct purpose (warm-up and context, created offline by the facilitator) and a different lifecycle (not voted, not grouped). Separate model avoids `if card.is_milestone` conditionals and prevents domain bugs.

### 13.8 Grouping restricted to facilitator
Eliminates concurrency conflicts in real time (two participants grouping the same card). Multi-select maintains agility for the facilitator. Collaborative drag-and-drop is for phase 2.

### 13.9 Voting restricted to "Loathed" and "Longed for"
Focuses prioritization on columns that generate improvement actions. "Liked" and "Learned" columns are for celebration and knowledge recording — they don't need forced prioritization. Reduces vote dispersion and makes the phase more objective.

### 13.10 One vote per card per participant
Forces vote distribution and prevents a single card from concentrating all of a participant's votes — which would defeat the purpose of dot voting prioritization. Fixed rule, no toggle, to maintain simplicity.

### 13.11 Entry blocking post-lobby
Preserves process integrity (all share the same history). Facilitator can temporarily reopen for exceptions. Reconnection of existing participant is always allowed.

### 13.12 Free infrastructure (Fly.io + Neon + Upstash + Vercel)
Allows MVP to operate at $0.00 cost during the 60-day evaluation. Trade-offs: cold starts (mitigated with warm-up), storage and memory limits (comfortable for expected usage volume). Maintainer can migrate to Oracle Cloud Free if limits prove insufficient.

### 13.13 Handoff as a first-class artifact
Absence or imprecision of the handoff is equivalent to a critical bug — it blocks the next sprint or produces silent regression.

### 13.14 Local auth as default, OAuth as optional
Local auth (email/password) eliminates dependency on external OAuth providers for basic usage. No domain restriction — any team can self-host and use immediately. OAuth providers (Google, GitHub) can be enabled via environment variables for teams that prefer SSO.

### 13.15 Lucide Icons over Material Design Icons
Lucide is MIT-licensed, tree-shakeable, and has first-class Vue 3 support. No CDN dependency — icons are bundled at build time. Consistent 24px stroke style without needing to manage outline vs. filled variants.

### 13.16 English as default language
Open-source projects benefit from English-first documentation and UI. Localization is achievable via `@nuxtjs/i18n` with extracted string keys, but the MVP ships in English to maximize community reach.

---

## 14. License

RetroApp4L is released under the **MIT License**.

```
MIT License

Copyright (c) 2026 RetroApp4L Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 15. Contributing

Contributions are welcome. Please follow these guidelines:

- **Issues:** Use GitHub Issues for bug reports and feature requests. Include reproduction steps for bugs.
- **Pull Requests:** One feature or fix per PR. Include tests. Update the CHANGELOG.
- **Code style:** Run `ruff` (backend) and `eslint` (frontend) before submitting.
- **Handoff updates:** If your PR changes architecture or patterns, update the relevant `SPRINT_*_HANDOFF.md`.
- **Design system:** Do not introduce new colors, fonts, or spacing values without updating section 7 of this PRD.

---

*RetroApp4L PRD v2.0 — Open Source (MIT License)*
