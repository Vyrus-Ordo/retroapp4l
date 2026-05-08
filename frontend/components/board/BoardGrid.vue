<script setup lang="ts">
import type { Card, CardColumn } from "~/utils/types"

withDefaults(
  defineProps<{
    columns: Record<CardColumn, Card[]>
    selectedIds: string[]
    currentUserId?: string
    votedCardIds?: string[]
    votesRemaining?: number
    allowSelfVote?: boolean
    phase: string
    groupedChildren?: Record<string, Card[]>
  }>(),
  { votedCardIds: () => [], groupedChildren: () => ({}), votesRemaining: undefined, allowSelfVote: false },
)

defineEmits<{
  createCard: [column: CardColumn]
  editCard: [card: Card]
  deleteCard: [card: Card]
  toggleSelect: [cardId: string]
  vote: [card: Card]
}>()
const columnAccent: Record<string, string> = {
  loved:   '#22c55e',
  loathed: '#ef4444',
  longed:  '#60a5fa',
  learned: '#a1a1aa',
}
</script>

<template>
  <div class="grid gap-3 xl:grid-cols-4">
    <section
      v-for="column in ['loved', 'loathed', 'longed', 'learned']"
      :key="column"
      class="overflow-hidden rounded-lg"
      :style="{
        background: 'rgba(255,255,255,0.03)',
        border: `1px solid ${columnAccent[column]}26`,
      }"
    >
      <ColumnHeader
        :column="column as CardColumn"
        :count="columns[column as CardColumn].length"
        :can-create="phase === 'board'"
        @create="$emit('createCard', column as CardColumn)"
      />
      <div class="flex min-h-80 flex-col gap-4 p-4" style="background: rgba(0,0,0,0.2)">
        <RetroCard
          v-for="card in columns[column as CardColumn]"
          :key="card.id"
          :can-delete="card.can_edit && phase === 'board'"
          :can-edit="card.can_edit && phase === 'board'"
          :can-vote="phase === 'voting' && ['loathed', 'longed'].includes(card.column)"
          :show-vote-badge="['voting', 'grouping'].includes(phase) && ['loathed', 'longed'].includes(card.column)"
          :card="card"
          :grouped-cards="groupedChildren[card.id] || []"
          :selected="selectedIds.includes(card.id)"
          :show-grouping="phase === 'grouping'"
          :vote-active="votedCardIds.includes(card.id)"
          :is-own-card="card.can_edit"
          :allow-self-vote="allowSelfVote"
          :votes-remaining="votesRemaining"
          @delete="$emit('deleteCard', card)"
          @edit="$emit('editCard', card)"
          @toggle-select="$emit('toggleSelect', card.id)"
          @vote="$emit('vote', card)"
        />
      </div>
    </section>
  </div>
</template>
