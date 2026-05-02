<script setup lang="ts">
import { PencilIcon, TrashIcon } from "@heroicons/vue/24/outline"

import type { Card } from "~/utils/types"

defineProps<{
  card: Card
  showGrouping?: boolean
  selected?: boolean
  canEdit?: boolean
  canDelete?: boolean
  canVote?: boolean
  voteActive?: boolean
  voteDisabled?: boolean
}>()

defineEmits<{
  edit: [card: Card]
  delete: [card: Card]
  toggleSelect: [cardId: string]
  vote: [card: Card]
}>()
</script>

<template>
  <article class="bg-white border border-slate-100 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow duration-150">
    <div class="flex items-start justify-between gap-3">
      <div>
        <p class="text-xs text-slate-400">{{ card.author_name }} · {{ new Date(card.created_at).toLocaleString() }}</p>
        <p class="mt-3 text-sm font-medium text-slate-900">{{ card.content }}</p>
      </div>
      <input
        v-if="showGrouping"
        :checked="selected"
        class="mt-1 h-4 w-4 rounded border-slate-300 text-brand-500"
        type="checkbox"
        @change="$emit('toggleSelect', card.id)"
      >
    </div>

    <div class="mt-4 flex flex-wrap items-center gap-3 text-xs text-slate-500">
      <button v-if="canEdit" class="inline-flex items-center hover:text-slate-900" type="button" @click="$emit('edit', card)">
        <PencilIcon class="mr-1 h-4 w-4" />
        Edit
      </button>
      <button v-if="canDelete" class="inline-flex items-center hover:text-danger-500" type="button" @click="$emit('delete', card)">
        <TrashIcon class="mr-1 h-4 w-4" />
        Delete
      </button>
      <button
        v-if="canVote"
        :class="voteActive ? 'text-brand-500' : 'text-slate-500 hover:text-brand-500'"
        :disabled="voteDisabled"
        class="inline-flex items-center disabled:text-slate-300"
        type="button"
        @click="$emit('vote', card)"
      >
        <VoteBadge :active="voteActive" :count="card.vote_count" />
      </button>
      <span v-else class="text-brand-500 text-xs font-semibold">{{ card.vote_count }} votes</span>
    </div>
  </article>
</template>