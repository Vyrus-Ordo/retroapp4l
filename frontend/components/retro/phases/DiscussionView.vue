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
        <h1 class="text-xl font-light text-white">Discussion</h1>
        <p class="mt-1 text-sm text-zinc-500">
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
          :class="timerStore.secondsRemaining < 60 ? 'text-danger-500' : 'text-[#00f2ff]'"
        >
          {{ timerStore.formatted }}
        </span>
      </div>
    </div>

    <div class="grid gap-6 lg:grid-cols-[1fr,300px]">
      <!-- Sorted card list -->
      <div class="space-y-3">
        <p class="text-xs font-light uppercase tracking-[0.2em] text-zinc-600">Cards by votes</p>

        <p v-if="sortedCards.length === 0" class="py-12 text-center text-sm text-zinc-600">No cards to discuss.</p>

        <article
          v-for="(card, index) in sortedCards"
          :key="card.id"
          :class="[
            'rounded-xl border p-4 transition cursor-default',
            focus?.card_id === card.id
              ? 'border-[#00f2ff]/40 ring-1 ring-[#00f2ff]/15'
              : index < 3 && card.vote_count > 0
              ? 'border-amber-500/30'
              : 'border-white/8',
            isFacilitator ? 'cursor-pointer hover:border-white/20' : '',
          ]"
          style="background: rgba(255,255,255,0.04)"
          @click="handleFocusCard(card)"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-xs font-light uppercase tracking-[0.2em] text-zinc-600">{{ card.column }}</p>
              <p
                :class="card.is_anonymous ? 'border-[#00f2ff]/20 text-[#00f2ff]/70' : 'text-zinc-600'"
                class="mt-1 inline-flex rounded-full border border-transparent px-2 py-0.5 text-xs"
              >
                {{ card.author_display }}
              </p>
            </div>
            <span
              :class="card.vote_count > 0 ? 'border border-[#00f2ff]/25 text-[#00f2ff]' : 'border border-white/10 text-zinc-600'"
              class="inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold"
            >
              {{ card.vote_count }} vote<span v-if="card.vote_count !== 1">s</span>
            </span>
          </div>

          <p class="mt-3 text-sm leading-6 text-zinc-200">{{ card.content }}</p>

          <div v-if="focus?.card_id === card.id" class="mt-2 flex items-center gap-1.5 text-xs font-light text-[#00f2ff]/70">
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
        <div class="space-y-4 rounded-xl border border-white/8 p-6" style="background: rgba(255,255,255,0.03)">
          <div>
            <h2 class="text-lg font-light text-white">Session Minutes</h2>
            <p class="text-sm text-zinc-500">Action items created during this discussion.</p>
          </div>

          <div v-if="actionItems.length === 0" class="text-sm text-zinc-600 py-2">
            No action items recorded yet.
          </div>

          <div class="space-y-2">
            <div v-for="action in actionItems" :key="action.id" class="rounded-lg border border-white/8 p-3 text-sm" style="background: rgba(255,255,255,0.04)">
              <p class="font-light text-zinc-200">{{ action.description }}</p>
              <div class="mt-1 flex flex-col gap-1 text-xs text-zinc-600">
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
