<script setup lang="ts">
import { ViewfinderCircleIcon } from "@heroicons/vue/24/outline"

import type { Card, DiscussionFocusPayload, ActionItem } from "~/utils/types"

import FocusCard from "~/components/board/FocusCard.vue"

const props = defineProps<{
  current: any
  isFacilitator: boolean
  retroStore: any
  timerStore: any
  discussionQueue: Card[]
}>()

const emit = defineEmits<{
  "advance-phase": []
  "open-action-modal": [defaultCardId?: string]
}>()

const route = useRoute()
const retrospectiveId = computed(() => String(route.params.id))

const focus = computed<DiscussionFocusPayload | null>(() => props.retroStore.discussionFocus)

const actionItems = computed<ActionItem[]>(() => props.retroStore.actionItems)

const sortedCards = computed<Card[]>(() => props.discussionQueue)

const queueAfterFocus = computed<Card[]>(() =>
  focus.value ? sortedCards.value.filter((c) => c.id !== focus.value!.card_id) : sortedCards.value,
)

async function handleFocusCard(card: Card) {
  if (!props.isFacilitator) return
  await props.retroStore.focusCard(retrospectiveId.value, card.id)
}

async function handleNextCard() {
  await props.retroStore.nextFocusCard(retrospectiveId.value)
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Header -->
    <div class="flex items-center justify-between gap-4">
      <div>
        <h1 class="text-xl font-bold text-slate-900">Discussion</h1>
        <p class="mt-1 text-sm text-slate-500">
          <template v-if="isFacilitator">Click a card to put it in focus for the group.</template>
          <template v-else>Your facilitator controls which card is in focus.</template>
        </p>
      </div>
      <div class="flex items-center gap-4">
        <button v-if="isFacilitator" class="button-primary py-1.5 text-sm" type="button" @click="emit('advance-phase')">
          Next phase
        </button>
        <span
          v-if="current?.timer_duration_seconds"
          class="text-lg font-semibold tabular-nums"
          :class="timerStore.secondsRemaining < 60 ? 'text-danger-500' : 'text-slate-900'"
        >
          {{ timerStore.formatted }}
        </span>
      </div>
    </div>

    <div class="grid gap-6 lg:grid-cols-[1fr,300px]">
      <!-- Sorted card list -->
      <div class="space-y-3">
        <p class="text-xs font-semibold uppercase tracking-wide text-slate-400">Cards by votes</p>

        <p v-if="sortedCards.length === 0" class="py-12 text-center text-sm text-slate-400">No cards to discuss.</p>

        <article
          v-for="(card, index) in sortedCards"
          :key="card.id"
          :class="[
            'rounded-xl border bg-white p-4 shadow-sm transition',
            focus?.card_id === card.id
              ? 'border-brand-400 ring-2 ring-brand-100'
              : index < 3 && card.vote_count > 0
              ? 'border-amber-300 bg-amber-50'
              : 'border-slate-200',
            isFacilitator ? 'cursor-pointer hover:border-brand-300 hover:shadow-md' : '',
          ]"
          @click="handleFocusCard(card)"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{{ card.column }}</p>
              <p class="mt-1 text-sm text-slate-500">{{ card.author_name }}</p>
            </div>
            <span
              :class="card.vote_count > 0 ? 'bg-brand-50 text-brand-700' : 'bg-slate-100 text-slate-400'"
              class="inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold"
            >
              {{ card.vote_count }} vote<span v-if="card.vote_count !== 1">s</span>
            </span>
          </div>

          <p class="mt-3 text-sm leading-6 text-slate-800">{{ card.content }}</p>

          <div v-if="focus?.card_id === card.id" class="mt-2 flex items-center gap-1.5 text-xs font-medium text-brand-600">
            <ViewfinderCircleIcon class="h-4 w-4" />
            In focus
          </div>
        </article>
      </div>

      <div class="flex flex-col gap-6">
        <!-- Focus panel -->
        <FocusCard
          :focus="focus"
          :queue="queueAfterFocus"
          :facilitator="isFacilitator"
          @next="handleNextCard"
          @new-action="emit('open-action-modal', focus?.card_id)"
        />

        <!-- Action items list (Live Minutes) -->
        <div class="space-y-4 rounded-xl bg-slate-50 p-6 border border-slate-100">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Session Minutes</h2>
            <p class="text-sm text-slate-500">Action items created during this discussion.</p>
          </div>

          <div v-if="actionItems.length === 0" class="text-sm text-slate-400 py-2">
            No action items recorded yet.
          </div>

          <div class="space-y-2">
            <div v-for="action in actionItems" :key="action.id" class="rounded-lg bg-white p-3 border border-slate-200 shadow-sm text-sm">
              <p class="font-medium text-slate-900">{{ action.description }}</p>
              <div class="mt-1 flex flex-col gap-1 text-xs text-slate-500">
                <span v-if="action.assignee_name">Assignee: {{ action.assignee_name }}</span>
                <span v-if="action.due_date">Due: {{ action.due_date }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>


  </div>
</template>
