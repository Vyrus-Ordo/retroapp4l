<script setup lang="ts">
import type { Card, CardColumn } from "~/utils/types"

withDefaults(
  defineProps<{
    columns: Record<CardColumn, Card[]>
    selectedIds: string[]
    currentUserId?: string
    votedCardIds?: string[]
    phase: string
    groupedChildren?: Record<string, Card[]>
  }>(),
  { votedCardIds: () => [], groupedChildren: () => ({}) },
)

defineEmits<{
  createCard: [column: CardColumn]
  editCard: [card: Card]
  deleteCard: [card: Card]
  toggleSelect: [cardId: string]
  vote: [card: Card]
}>()
</script>

<template>
  <div class="grid gap-4 xl:grid-cols-4">
    <section v-for="column in ['loved', 'loathed', 'longed', 'learned']" :key="column" class="overflow-hidden rounded-lg border border-slate-100 bg-white">
      <ColumnHeader :column="column as CardColumn" :count="columns[column as CardColumn].length" />
      <div class="flex min-h-80 flex-col gap-4 bg-slate-50 p-4">
        <RetroCard
          v-for="card in columns[column as CardColumn]"
          :key="card.id"
          :can-delete="card.author === currentUserId && phase === 'board'"
          :can-edit="card.author === currentUserId && phase === 'board'"
          :can-vote="phase === 'voting' && ['loathed', 'longed'].includes(card.column)"
          :card="card"
          :grouped-cards="groupedChildren[card.id] || []"
          :selected="selectedIds.includes(card.id)"
          :show-grouping="phase === 'grouping'"
          :vote-active="votedCardIds.includes(card.id)"
          :vote-disabled="card.author === currentUserId"
          @delete="$emit('deleteCard', card)"
          @edit="$emit('editCard', card)"
          @toggle-select="$emit('toggleSelect', card.id)"
          @vote="$emit('vote', card)"
        />

        <button v-if="phase === 'board'" class="button-secondary mt-auto" type="button" @click="$emit('createCard', column as CardColumn)">
          Add card
        </button>
      </div>
    </section>
  </div>
</template>