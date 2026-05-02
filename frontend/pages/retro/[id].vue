<script setup lang="ts">
import {
  ArrowRightCircleIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  LinkIcon,
  LockClosedIcon,
} from "@heroicons/vue/24/outline"

import type { ActionItem, Card, CardColumn, RetroPhase } from "~/utils/types"

const route = useRoute()
const retrospectiveId = computed(() => String(route.params.id))
const { authStore } = useAuth()
const retroStore = useRetroStore()
const participantStore = useParticipantStore()
const timerStore = useTimerStore()
const { getNextPhase, getPhaseLabel } = usePhase()
const { toneClass, start } = useTimer()
const { connectionState, send } = useWebSocket(retrospectiveId)

const cardModalOpen = ref(false)
const actionModalOpen = ref(false)
const draftColumn = ref<CardColumn>("loved")
const editingCard = ref<Card | null>(null)
const editingAction = ref<ActionItem | null>(null)
const pageError = ref("")

const current = computed(() => retroStore.current)
const activePhase = computed(() => retroStore.activePhase)
const currentUserId = computed(() => authStore.user?.id)
const isFacilitator = computed(() => retroStore.isFacilitator(currentUserId.value))
const currentUserVotes = computed(() =>
  retroStore.votes.filter((vote) => vote.voter === currentUserId.value).map((vote) => vote.card),
)
const inviteLink = computed(() => {
  if (!current.value?.invite_token) {
    return ""
  }
  return `${window.location.origin}/retro/invite/${current.value.invite_token}`
})
const discussionQueue = computed(() =>
  retroStore.cards
    .filter((card) => card.id !== retroStore.discussionFocus?.card_id)
    .sort((first, second) => second.vote_count - first.vote_count),
)
const showMilestoneBar = computed(() => ["board", "grouping", "voting", "discussion", "actions"].includes(activePhase.value))

async function loadSession() {
  pageError.value = ""
  try {
    await retroStore.fetchSession(retrospectiveId.value)
    participantStore.hydrate(retroStore.current?.participants || [])
    timerStore.hydrate(retroStore.current)
    start()
  } catch (error) {
    pageError.value = error instanceof Error ? error.message : "Unable to load retrospective."
  }
}

onMounted(loadSession)

watch(
  () => retroStore.current?.participants,
  (participants) => {
    if (participants) {
      participantStore.hydrate(participants)
    }
  },
)

function openCreateCard(column: CardColumn) {
  draftColumn.value = column
  editingCard.value = null
  cardModalOpen.value = true
}

function openEditCard(card: Card) {
  editingCard.value = card
  draftColumn.value = card.column
  cardModalOpen.value = true
}

async function submitCard(payload: { id?: string; content: string; column: CardColumn }) {
  if (payload.id) {
    await retroStore.updateCard(retrospectiveId.value, payload.id, { content: payload.content })
    return
  }
  await retroStore.createCard(retrospectiveId.value, { column: payload.column, content: payload.content })
}

async function removeCard(card: Card) {
  await retroStore.deleteCard(retrospectiveId.value, card.id)
}

async function handleVote(card: Card) {
  if (currentUserVotes.value.includes(card.id)) {
    await retroStore.revokeVote(retrospectiveId.value, card.id)
    return
  }
  await retroStore.castVote(retrospectiveId.value, card.id)
}

async function submitAction(payload: {
  id?: string
  description: string
  assignee_id: string
  card_id: string | null
  due_date: string | null
  status: string
  external_tracker_url: string | null
}) {
  await retroStore.saveActionItem(retrospectiveId.value, payload)
}

async function advancePhase() {
  if (!current.value) {
    return
  }

  const nextPhase = getNextPhase(activePhase.value as RetroPhase, current.value.skip_check_phase)
  send({
    type: "phase.advance",
    phase: nextPhase,
    timer_duration_seconds: timerStore.secondsRemaining,
  })
  retroStore.setPreviewPhase(nextPhase)
}

function pauseTimer() {
  send({ type: "timer.paused", seconds_remaining: timerStore.secondsRemaining })
  timerStore.pause(timerStore.secondsRemaining)
}

function resumeTimer() {
  send({ type: "timer.resumed", seconds_remaining: timerStore.secondsRemaining })
  timerStore.resume(timerStore.secondsRemaining)
}

async function closeSession() {
  await retroStore.closeRetrospective(retrospectiveId.value)
}

function handleAllowEntry() {
  participantStore.pushLog("Invite reopening still depends on a backend endpoint.")
}

async function copyInviteLink() {
  if (!inviteLink.value) {
    return
  }
  await navigator.clipboard.writeText(inviteLink.value)
  participantStore.pushLog("Invite link copied to clipboard.")
}
</script>

<template>
  <AppShell :phase-label="getPhaseLabel(activePhase as RetroPhase)" :timer-text="timerStore.formatted">
    <template #sidebar>
      <AppSidebar>
        <ParticipantPanel
          :access-log="participantStore.accessLog"
          :facilitator="isFacilitator"
          :invite-blocked="Boolean(current?.invite_revoked_at || activePhase !== 'lobby')"
          :invite-token="current?.invite_token"
          :online-ids="participantStore.onlineIds"
          :participants="participantStore.participants"
          @allow-entry="handleAllowEntry"
        />
      </AppSidebar>
    </template>

    <div class="space-y-6">
      <section v-if="current" class="panel overflow-hidden">
        <div class="flex flex-col gap-6 px-6 py-6 lg:flex-row lg:items-start lg:justify-between lg:px-8">
          <div class="space-y-4">
            <div class="flex flex-wrap items-center gap-3">
              <PhaseChip :phase="getPhaseLabel(activePhase as RetroPhase)" :timer-text="timerStore.formatted" />
              <span class="rounded bg-slate-50 px-3 py-2 text-sm text-slate-600">
                WebSocket: {{ connectionState }}
              </span>
            </div>
            <div>
              <h1 class="text-2xl font-semibold text-slate-900">{{ current.title }}</h1>
              <p class="mt-2 text-sm text-slate-600">{{ current.sprint_name || 'No sprint name' }} · {{ current.team_key }} · Facilitator: {{ current.facilitator_name }}</p>
            </div>
            <p v-if="current.description" class="max-w-3xl text-sm text-slate-600">{{ current.description }}</p>
          </div>

          <div class="flex flex-col items-start gap-3 lg:items-end">
            <TimerDisplay
              :facilitator="isFacilitator"
              :label="timerStore.formatted"
              :paused="timerStore.paused"
              :tone-class="toneClass"
              @pause="pauseTimer"
              @resume="resumeTimer"
            />
            <div class="flex flex-wrap gap-3">
              <button class="button-secondary" type="button" @click="loadSession">
                <ArrowPathIcon class="mr-2 h-5 w-5" />
                Refresh
              </button>
              <button v-if="inviteLink" class="button-secondary" type="button" @click="copyInviteLink">
                <LinkIcon class="mr-2 h-5 w-5" />
                Copy invite
              </button>
              <button v-if="isFacilitator && activePhase !== 'closed'" class="button-primary" type="button" @click="advancePhase">
                <ArrowRightCircleIcon class="mr-2 h-5 w-5" />
                Advance phase
              </button>
              <button v-if="isFacilitator && activePhase === 'actions'" class="button-secondary" type="button" @click="closeSession">
                <LockClosedIcon class="mr-2 h-5 w-5" />
                Close session
              </button>
            </div>
          </div>
        </div>

        <MilestoneBar v-if="showMilestoneBar" :milestones="current.milestones" />
      </section>

      <section v-if="pageError" class="rounded-lg border border-danger-500/20 bg-danger-50 p-4 text-sm text-danger-500">
        {{ pageError }}
      </section>

      <section v-if="current && ['setup', 'lobby', 'presentation'].includes(activePhase)" class="grid gap-6 xl:grid-cols-[1.3fr,0.7fr]">
        <div class="panel p-6 lg:p-8">
          <h2 class="text-lg font-semibold text-slate-900">Milestones presentation</h2>
          <p class="mt-2 text-sm text-slate-600">Use this stage to align the team on achievements, incidents, and key events before cards are added.</p>
          <div class="mt-6 grid gap-4 md:grid-cols-2">
            <MilestoneCard v-for="milestone in current.milestones" :key="milestone.id" :milestone="milestone" />
            <div v-if="!current.milestones.length" class="rounded-lg border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-500">
              No milestones yet. Add them during setup to make presentation useful.
            </div>
          </div>
        </div>

        <div class="panel p-6 lg:p-8">
          <h2 class="text-lg font-semibold text-slate-900">Lobby controls</h2>
          <p class="mt-2 text-sm text-slate-600">Invite participants, confirm who is present, and advance once the room is ready.</p>
          <div class="mt-6 space-y-3 text-sm text-slate-600">
            <div class="rounded-lg bg-slate-50 p-4">Invite token: {{ current.invite_token || 'Unavailable' }}</div>
            <div class="rounded-lg bg-slate-50 p-4">Participants joined: {{ participantStore.participants.length }}</div>
            <div class="rounded-lg bg-slate-50 p-4">Skip check phase: {{ current.skip_check_phase ? 'Yes' : 'No' }}</div>
          </div>
        </div>
      </section>

      <section v-if="activePhase === 'check'" class="panel p-6 lg:p-8">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Previous action check</h2>
            <p class="mt-1 text-sm text-slate-600">Review unfinished actions from the previous closed retrospective in the same team.</p>
          </div>
          <span class="rounded bg-slate-50 px-3 py-2 text-sm text-slate-600">{{ retroStore.previousActions.action_items.length }} action items</span>
        </div>

        <div class="mt-6 space-y-3">
          <div v-for="action in retroStore.previousActions.action_items" :key="action.id" class="rounded-lg border border-slate-100 bg-slate-50 p-4">
            <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p class="text-sm font-medium text-slate-900">{{ action.description }}</p>
                <p class="mt-1 text-xs text-slate-500">{{ action.assignee_name || 'Unassigned' }}</p>
              </div>
              <select class="field-input max-w-48" :value="action.status" @change="retroStore.updatePreviousActionStatus(retrospectiveId, action.id, String(($event.target as HTMLSelectElement).value))">
                <option value="not_started">Not started</option>
                <option value="in_progress">In progress</option>
                <option value="done">Done</option>
              </select>
            </div>
          </div>
          <div v-if="!retroStore.previousActions.action_items.length" class="rounded-lg border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-500">
            No previous closed retrospective exists for this team.
          </div>
        </div>
      </section>

      <section v-if="['board', 'grouping', 'voting', 'discussion', 'actions'].includes(activePhase)" class="space-y-6">
        <div class="flex flex-wrap items-center gap-3">
          <button v-if="activePhase === 'grouping' && isFacilitator" class="button-primary" type="button" @click="retroStore.groupSelected(retrospectiveId)">
            Group selected
          </button>
          <button v-if="activePhase === 'grouping' && retroStore.selectedCardIds.length" class="button-secondary" type="button" @click="retroStore.clearSelection()">
            Clear selection
          </button>
          <button v-if="activePhase === 'actions'" class="button-primary" type="button" @click="actionModalOpen = true">
            <CheckCircleIcon class="mr-2 h-5 w-5" />
            Create action item
          </button>
        </div>

        <BoardGrid
          :columns="retroStore.cardsByColumn"
          :current-user-id="currentUserId"
          :phase="activePhase"
          :selected-ids="retroStore.selectedCardIds"
          @create-card="openCreateCard"
          @delete-card="removeCard"
          @edit-card="openEditCard"
          @toggle-select="retroStore.toggleCardSelection"
          @vote="handleVote"
        />

        <section v-if="activePhase === 'discussion'" class="grid gap-6 xl:grid-cols-[1fr,0.8fr]">
          <div class="panel p-6 lg:p-8">
            <h2 class="text-lg font-semibold text-slate-900">Discussion order</h2>
            <p class="mt-2 text-sm text-slate-600">Cards are sorted by vote count to help the facilitator focus the conversation.</p>
            <div class="mt-6 space-y-3">
              <button
                v-for="card in retroStore.cards.slice().sort((first, second) => second.vote_count - first.vote_count)"
                :key="card.id"
                class="flex w-full items-center justify-between rounded-lg border border-slate-100 bg-slate-50 p-4 text-left transition-colors duration-150 hover:bg-white"
                type="button"
                @click="retroStore.focusCard(retrospectiveId, card.id)"
              >
                <span>
                  <span class="block text-sm font-medium text-slate-900">{{ card.content }}</span>
                  <span class="mt-1 block text-xs text-slate-500">{{ card.author_name }} · {{ card.column }}</span>
                </span>
                <span class="text-sm font-medium text-brand-500">{{ card.vote_count }}</span>
              </button>
            </div>
          </div>

          <FocusCard :facilitator="isFacilitator" :focus="retroStore.discussionFocus" :queue="discussionQueue" @next="retroStore.nextFocusCard(retrospectiveId)" />
        </section>

        <section v-if="activePhase === 'actions'" class="panel p-6 lg:p-8">
          <h2 class="text-lg font-semibold text-slate-900">Action items</h2>
          <div class="mt-6 grid gap-4 lg:grid-cols-2">
            <div v-for="action in retroStore.actionItems" :key="action.id" class="rounded-lg border border-slate-100 bg-slate-50 p-4">
              <p class="text-sm font-medium text-slate-900">{{ action.description }}</p>
              <p class="mt-2 text-xs text-slate-500">{{ action.assignee_name || 'Unassigned' }} · {{ action.status }}</p>
              <div class="mt-4 flex gap-3">
                <button class="button-secondary" type="button" @click="editingAction = action; actionModalOpen = true">Edit</button>
                <button class="button-secondary" type="button" @click="retroStore.deleteActionItem(retrospectiveId, action.id)">Delete</button>
              </div>
            </div>
            <div v-if="!retroStore.actionItems.length" class="rounded-lg border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-500">
              No action items yet. Capture owners and deadlines before closing the session.
            </div>
          </div>
        </section>
      </section>

      <section v-if="activePhase === 'closed'" class="panel p-6 lg:p-8">
        <h2 class="text-lg font-semibold text-slate-900">Session closed</h2>
        <p class="mt-2 text-sm text-slate-600">The retrospective is closed. Use the history detail page for a full read-only summary.</p>
        <NuxtLink class="button-primary mt-6" :to="`/history/${retrospectiveId}`">Open history detail</NuxtLink>
      </section>
    </div>

    <CardComposer
      v-model="cardModalOpen"
      :initial-card="editingCard"
      :initial-column="draftColumn"
      @submit="submitCard"
    />
    <ActionItemForm
      v-model="actionModalOpen"
      :cards="retroStore.cards"
      :initial-action="editingAction"
      :participants="participantStore.participants"
      @submit="submitAction"
    />
  </AppShell>
</template>