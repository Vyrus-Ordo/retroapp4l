<script setup lang="ts">
import type { ActionItem, Card, CardColumn, RetroPhase } from '~/utils/types'

import ActionItemForm from '~/components/forms/ActionItemForm.vue'
import CardComposer from '~/components/forms/CardComposer.vue'
import ParticipantPanel from '~/components/participants/ParticipantPanel.vue'
import TimerDisplay from '~/components/retro/TimerDisplay.vue'
import SetupView from '~/components/retro/phases/SetupView.vue'
import LobbyView from '~/components/retro/phases/LobbyView.vue'
import CheckView from '~/components/retro/phases/CheckView.vue'
import MilestonesView from '~/components/retro/phases/MilestonesView.vue'
import BoardView from '~/components/retro/phases/BoardView.vue'
import GroupingView from '~/components/retro/phases/GroupingView.vue'
import VotingView from '~/components/retro/phases/VotingView.vue'
import DiscussionView from '~/components/retro/phases/DiscussionView.vue'
import ActionsView from '~/components/retro/phases/ActionsView.vue'
import ClosedView from '~/components/retro/phases/ClosedView.vue'

const TIMED_PHASES: RetroPhase[] = ['presentation', 'check', 'board', 'grouping', 'voting', 'discussion', 'actions']

const route = useRoute()
const retrospectiveId = computed(() => String(route.params.id))
const { authStore } = useAuth()
const retroStore = useRetroStore()
const participantStore = useParticipantStore()
const timerStore = useTimerStore()
const toastStore = useToastStore()
const { getNextPhase, orderedPhases } = usePhase()
const { toneClass, start } = useTimer()
const websocketEnabled = ref(false)
const { connectionState, send } = useWebSocket(retrospectiveId, websocketEnabled)
const api = useApiClient()

const cardModalOpen = ref(false)
const actionModalOpen = ref(false)
const actionModalDefaultCard = ref<string>("")
const draftColumn = ref<CardColumn>('loved')
const editingCard = ref<Card | null>(null)
const editingAction = ref<ActionItem | null>(null)
const pageError = ref('')
const requestUrl = useRequestURL()
const allowEntryLoading = ref(false)

const current = computed(() => retroStore.current)
const activePhase = computed(() => retroStore.activePhase)
const currentUserId = computed(() => authStore.user?.id)
const isFacilitator = computed(() => retroStore.isFacilitator(currentUserId.value))
const isTimedPhase = computed(() => TIMED_PHASES.includes(activePhase.value as RetroPhase))
const currentUserVotes = computed(() =>
  retroStore.votes.filter((vote) => vote.voter === currentUserId.value).map((vote) => vote.card),
)
const inviteLink = computed(() => {
  if (!current.value?.invite_token) return ''
  return requestUrl.origin + '/retro/invite/' + current.value.invite_token
})
const discussionQueue = computed(() =>
  retroStore.cards.slice().sort((a, b) => b.vote_count - a.vote_count),
)

const phaseComponent = computed(() => {
  switch (activePhase.value) {
    case 'setup': return SetupView
    case 'lobby': return LobbyView
    case 'check': return CheckView
    case 'presentation': return MilestonesView
    case 'board': return BoardView
    case 'grouping': return GroupingView
    case 'voting': return VotingView
    case 'discussion': return DiscussionView
    case 'actions': return ActionsView
    case 'closed': return ClosedView
    default: return SetupView
  }
})

watch(
  () => activePhase.value,
  async (phase) => {
    if (phase !== 'closed' || !current.value?.id) {
      return
    }

    websocketEnabled.value = false
    await navigateTo(`/history/${current.value.id}`)
  },
)

async function advancePhase() {
  const next = getNextPhase(activePhase.value as RetroPhase, current.value.skip_check_phase)
  send({ type: 'phase.advance', phase: next })
}

function sendTimerPause() {
  send({ type: 'timer.pause' })
}

function sendTimerResume() {
  send({ type: 'timer.resume' })
}

async function closeSession() {
  await retroStore.closeRetrospective(retrospectiveId.value)
}

async function copyInviteLink() {
  if (inviteLink.value) {
    await navigator.clipboard.writeText(inviteLink.value)
    toastStore.success('Invite link copied!')
  }
}

async function handleAllowEntry() {
  allowEntryLoading.value = true
  try {
    const response = await api.post<{ status: string; expires_at: string | null }>('/retrospectives/' + retrospectiveId.value + '/reopen-entry/', {})
    participantStore.setInviteStatus(
      response.status as 'active' | 'blocked' | 'temporarily_open',
      response.expires_at,
    )
    toastStore.success('Entry temporarily opened.')
  } finally {
    allowEntryLoading.value = false
  }
}

function openCreateCard(column: CardColumn) {
  draftColumn.value = column
  editingCard.value = null
  cardModalOpen.value = true
}

function openEditCard(card: Card) {
  editingCard.value = card
  cardModalOpen.value = true
}

async function removeCard(cardId: string) {
  await retroStore.deleteCard(retrospectiveId.value, cardId)
}

async function handleVote(cardId: string) {
  if (currentUserVotes.value.includes(cardId)) {
    await retroStore.revokeVote(retrospectiveId.value, cardId)
  } else {
    await retroStore.castVote(retrospectiveId.value, cardId)
  }
}

async function submitCard(payload: { id?: string; column: CardColumn; content: string; is_anonymous: boolean }) {
  if (payload.id) {
    await retroStore.updateCard(retrospectiveId.value, payload.id, { content: payload.content, is_anonymous: payload.is_anonymous })
  } else {
    await retroStore.createCard(retrospectiveId.value, { column: payload.column, content: payload.content, is_anonymous: payload.is_anonymous })
  }
  cardModalOpen.value = false
  editingCard.value = null
}

async function submitAction(payload: ActionItem) {
  await retroStore.saveActionItem(retrospectiveId.value, payload)
  actionModalOpen.value = false
  editingAction.value = null
}

function openCreateAction(defaultCard?: string) {
  editingAction.value = null
  actionModalDefaultCard.value = defaultCard || ""
  actionModalOpen.value = true
}

function openEditAction(action: ActionItem) {
  editingAction.value = action
  actionModalOpen.value = true
}

onMounted(async () => {
  try {
    await retroStore.fetchSession(retrospectiveId.value)
    timerStore.hydrate(retroStore.current)
    websocketEnabled.value = true
    participantStore.hydrate(retroStore.current?.participants ?? [])
    try {
      const status = await api.get('/retrospectives/' + retrospectiveId.value + '/invite-status/')
      const s = status as { status: string; expires_at: string | null }
      participantStore.setInviteStatus(
        s.status as 'active' | 'blocked' | 'temporarily_open',
        s.expires_at,
      )
    } catch {
      // invite status is non-critical
    }
    start()
  } catch (error) {
    websocketEnabled.value = false
    pageError.value = error instanceof Error ? error.message : 'Unable to load session.'
    if (pageError.value === 'This retrospective is closed. Use the history endpoint instead.') {
      await navigateTo(`/history/${retrospectiveId.value}`)
      return
    }
  }
})
</script>

<template>
  <AppShell
    mode="retro"
    :current-phase="activePhase"
    :skip-check-phase="current?.skip_check_phase"
  >
    <template #timer>
      <TimerDisplay
        v-if="isTimedPhase && timerStore.secondsRemaining > 0"
        :label="timerStore.formatted"
        :tone-class="toneClass"
        :paused="timerStore.paused"
        :facilitator="isFacilitator"
        @pause="sendTimerPause"
        @resume="sendTimerResume"
      />
    </template>
    <div class="grid gap-4 xl:grid-cols-[minmax(0,1fr),280px]">
      <component
        :is="phaseComponent"
        class="min-w-0"
        :current="current"
        :active-phase="activePhase"
        :is-facilitator="isFacilitator"
        :participants="participantStore.participants"
        :retro-store="retroStore"
        :participant-store="participantStore"
        :timer-store="timerStore"
        :discussion-queue="discussionQueue"
        :invite-link="inviteLink"
        :connection-state="connectionState"
        :page-error="pageError"
        @advance-phase="advancePhase"
        @close-session="closeSession"
        @copy-invite-link="copyInviteLink"
        @allow-entry="handleAllowEntry"
        @open-card-modal="openCreateCard"
        @edit-card="openEditCard"
        @delete-card="removeCard"
        @vote="handleVote"
        @open-action-modal="openCreateAction"
        @edit-action="openEditAction"
      />

      <div v-if="current && activePhase !== 'closed'" class="panel p-4 lg:p-5">
        <ParticipantPanel
          :participants="participantStore.participants"
          :online-ids="participantStore.onlineIds"
          :access-log="participantStore.accessLog"
          :invite-status="participantStore.inviteStatus"
          :invite-link="inviteLink"
          :invite-expires-at="participantStore.inviteExpiresAt"
          :facilitator="isFacilitator"
          :allow-entry-loading="allowEntryLoading"
          @allow-entry="handleAllowEntry"
          @copy-invite-link="copyInviteLink"
        />
      </div>
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
      :default-card-id="actionModalDefaultCard"
      :participants="participantStore.participants"
      @submit="submitAction"
    />
  </AppShell>
</template>
