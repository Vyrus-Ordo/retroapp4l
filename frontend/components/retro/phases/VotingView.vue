<script setup lang="ts">
import type { Card } from "~/utils/types"

import BoardGrid from "~/components/board/BoardGrid.vue"

const props = defineProps<{
  current: any
  isFacilitator: boolean
  retroStore: any
  timerStore: any
}>()

const emit = defineEmits<{
  "advance-phase": []
  vote: [cardId: string]
}>()

const { authStore } = useAuth()
const currentUserId = computed(() => authStore.user?.id)

const votedCardIds = computed(() =>
  props.retroStore.votes
    .filter((v: any) => v.voter === currentUserId.value)
    .map((v: any) => v.card),
)

const votesRemaining = computed(() => {
  const participant = props.current?.participants?.find(
    (p: any) => p.user === currentUserId.value,
  )
  return participant?.votes_remaining ?? props.current?.max_votes_per_user ?? 0
})

function handleVote(card: Card) {
  emit("vote", card.id)
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between gap-4">
      <div>
        <h1 class="text-xl font-bold text-slate-900">Voting</h1>
        <p class="mt-1 text-sm text-slate-500">Vote on the most important cards in Loathed and Longed For columns.</p>
      </div>
      <div class="flex items-center gap-4">
        <span class="inline-flex items-center gap-1.5 rounded-full bg-brand-50 px-3 py-1 text-sm font-semibold text-brand-700">
          {{ votesRemaining }} vote<span v-if="votesRemaining !== 1">s</span> left
        </span>
        <span v-if="current?.timer_duration_seconds" class="text-lg font-semibold tabular-nums" :class="timerStore.secondsRemaining < 60 ? 'text-danger-500' : 'text-slate-900'">
          {{ timerStore.formatted }}
        </span>
      </div>
    </div>

    <BoardGrid
      :columns="retroStore.cardsByColumn"
      :selected-ids="[]"
      :current-user-id="currentUserId"
      :voted-card-ids="votedCardIds"
      :votes-remaining="votesRemaining"
      :allow-self-vote="current?.allow_self_vote ?? false"
      phase="voting"
      @vote="handleVote"
    />

    <div v-if="isFacilitator" class="flex justify-end">
      <button class="button-primary" type="button" @click="emit('advance-phase')">
        Next phase
      </button>
    </div>
  </div>
</template>

