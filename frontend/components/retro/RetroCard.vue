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
    showVoteBadge?: boolean
    isOwnCard?: boolean
    allowSelfVote?: boolean
    votesRemaining?: number
    voteActive?: boolean
    groupedCards?: Card[]
  }>(),
  {
    canEdit: false,
    canDelete: false,
    canVote: false,
    selected: false,
    showGrouping: false,
    showVoteBadge: false,
    isOwnCard: false,
    allowSelfVote: false,
    votesRemaining: undefined,
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

const cardAuthor = computed(() => props.card.author_display || "Anonymous")
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
      'rounded-xl border p-4 transition backdrop-blur-sm',
      selected ? 'border-[#00f2ff]/50 ring-1 ring-[#00f2ff]/20' : 'border-white/10 hover:border-white/20',
      showGrouping ? 'cursor-pointer' : '',
    ]"
    style="background: rgba(255,255,255,0.04)"
    @click="showGrouping ? toggleSelection() : undefined"
  >
    <div class="flex items-start justify-between gap-3">
      <div>
        <p class="text-xs font-light uppercase tracking-[0.2em] text-zinc-600">{{ card.column }}</p>
        <p
          :class="card.is_anonymous ? 'border-[#00f2ff]/20 text-[#00f2ff]/70' : 'text-zinc-500'"
          class="mt-1 inline-flex rounded-full border border-transparent px-2 py-0.5 text-xs"
        >
          {{ cardAuthor }}
        </p>
      </div>
      <VoteBadge v-if="showVoteBadge" :active="voteActive" :count="card.vote_count" />
    </div>

    <p class="mt-4 whitespace-pre-wrap text-sm leading-6 text-zinc-200">{{ cardContent }}</p>

    <div v-if="groupedCards.length > 0" class="mt-3 space-y-1.5 border-t border-white/8 pt-3">
      <p class="text-xs font-light text-zinc-600">{{ groupedCards.length }} card{{ groupedCards.length > 1 ? 's' : '' }} agrupado{{ groupedCards.length > 1 ? 's' : '' }}</p>
      <div
        v-for="child in groupedCards"
        :key="child.id"
        class="rounded-lg px-3 py-2 text-xs text-zinc-400"
        style="background: rgba(255,255,255,0.04)"
      >
        {{ child.content }}
        <span v-if="child.is_anonymous" class="ml-2 text-[10px] uppercase tracking-wide text-[#00f2ff]/60">Anonymous</span>
      </div>
    </div>

    <div v-if="showGrouping || canEdit || canDelete || canVote" class="mt-4 flex flex-wrap items-center gap-3 text-xs font-medium">
      <button
        v-if="showGrouping"
        :class="selected ? 'border-[#00f2ff]/50 text-[#00f2ff]' : 'border-white/10 text-zinc-500 hover:border-white/25 hover:text-zinc-300'"
        class="rounded-full border px-3 py-1.5 transition"
        type="button"
        @click.stop="toggleSelection"
      >
        {{ selected ? 'Selected' : 'Select for group' }}
      </button>

      <button v-if="canEdit" class="text-zinc-500 transition hover:text-white" type="button" @click.stop="emitEdit">
        Edit
      </button>

      <button v-if="canDelete" class="text-danger-500 transition hover:text-danger-600" type="button" @click.stop="emitDelete">
        Delete
      </button>

      <span v-if="canVote && isOwnCard && !allowSelfVote" class="text-xs text-zinc-600 italic">Your card</span>

      <button
        v-if="canVote && (!isOwnCard || allowSelfVote)"
        :class="voteActive ? 'text-[#00f2ff]' : 'text-zinc-500 hover:text-[#00f2ff]'"
        :disabled="votesRemaining !== undefined && votesRemaining <= 0"
        :title="votesRemaining !== undefined && votesRemaining <= 0 ? 'No votes remaining' : undefined"
        class="disabled:cursor-not-allowed disabled:text-zinc-700"
        type="button"
        @click.stop="emitVote"
      >
        Vote
      </button>
    </div>
  </article>
</template>
