<script setup lang="ts">
import type { Card } from "~/utils/types"

import VoteBadge from "./VoteBadge.vue"

const props = withDefaults(
  defineProps<{
    card: Card
    canEdit?: boolean
    canDelete?: boolean
    canVote?: boolean
    selected?: boolean
    showGrouping?: boolean
    voteDisabled?: boolean
    voteActive?: boolean
    groupedCards?: Card[]
  }>(),
  {
    canEdit: false,
    canDelete: false,
    canVote: false,
    selected: false,
    showGrouping: false,
    voteDisabled: false,
    voteActive: false,
    groupedCards: () => [],
  },
)

const emit = defineEmits<{
  edit: [card: Card]
  delete: [card: Card]
  vote: [card: Card]
  "toggle-select": [cardId: string]
  action: [payload: { type: "edit" | "delete"; card: Card }]
}>()

const cardAuthor = computed(() => props.card.author_name || props.card.author || "Anonymous")
const cardContent = computed(() => props.card.content || "")

function emitEdit() {
  emit("edit", props.card)
  emit("action", { type: "edit", card: props.card })
}

function emitDelete() {
  emit("delete", props.card)
  emit("action", { type: "delete", card: props.card })
}

function toggleSelection() {
  emit("toggle-select", props.card.id)
}

function emitVote() {
  emit("vote", props.card)
}
</script>

<template>
  <article
    :class="[
      'rounded-xl border bg-white p-4 shadow-sm transition',
      selected ? 'border-brand-300 ring-2 ring-brand-100' : 'border-slate-200 hover:border-slate-300',
      showGrouping ? 'cursor-pointer' : '',
    ]"
    @click="showGrouping ? toggleSelection() : undefined"
  >
    <div class="flex items-start justify-between gap-3">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{{ card.column }}</p>
        <p class="mt-1 text-sm text-slate-500">{{ cardAuthor }}</p>
      </div>
      <VoteBadge :active="voteActive" :count="card.vote_count" />
    </div>

    <p class="mt-4 whitespace-pre-wrap text-sm leading-6 text-slate-800">{{ cardContent }}</p>

    <div v-if="groupedCards.length > 0" class="mt-3 space-y-1.5 border-t border-slate-100 pt-3">
      <p class="text-xs font-medium text-slate-400">{{ groupedCards.length }} card{{ groupedCards.length > 1 ? 's' : '' }} agrupado{{ groupedCards.length > 1 ? 's' : '' }}</p>
      <div
        v-for="child in groupedCards"
        :key="child.id"
        class="rounded-lg bg-slate-50 px-3 py-2 text-xs text-slate-600"
      >
        {{ child.content }}
      </div>
    </div>

    <div v-if="showGrouping || canEdit || canDelete || canVote" class="mt-4 flex flex-wrap items-center gap-3 text-xs font-medium">
      <button
        v-if="showGrouping"
        :class="selected ? 'border-brand-300 bg-brand-50 text-brand-700' : 'border-slate-200 text-slate-600 hover:border-slate-300 hover:text-slate-900'"
        class="rounded-full border px-3 py-1.5 transition"
        type="button"
        @click.stop="toggleSelection"
      >
        {{ selected ? 'Selected' : 'Select for group' }}
      </button>

      <button v-if="canEdit" class="text-slate-600 transition hover:text-slate-900" type="button" @click.stop="emitEdit">
        Edit
      </button>

      <button v-if="canDelete" class="text-danger-500 transition hover:text-danger-600" type="button" @click.stop="emitDelete">
        Delete
      </button>

      <button
        v-if="canVote"
        :class="voteActive ? 'text-brand-600' : 'text-slate-600 hover:text-brand-600'"
        :disabled="voteDisabled"
        class="disabled:cursor-not-allowed disabled:text-slate-300"
        type="button"
        @click.stop="emitVote"
      >
        Vote
      </button>
    </div>
  </article>
</template>