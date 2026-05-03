<script setup lang="ts">
import type { Card, CardColumn } from "~/utils/types"

import BoardGrid from "~/components/board/BoardGrid.vue"

const props = defineProps<{
  current: any
  isFacilitator: boolean
  retroStore: any
  timerStore: any
}>()

const emit = defineEmits<{
  "advance-phase": []
  "open-card-modal": [column: CardColumn]
  "edit-card": [card: Card]
  "delete-card": [cardId: string]
}>()

const { authStore } = useAuth()
const currentUserId = computed(() => authStore.user?.id)
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between gap-4">
      <div>
        <h1 class="text-xl font-bold text-slate-900">Board 4L</h1>
        <p class="mt-1 text-sm text-slate-500">Add cards to each column to share your perspective on this sprint.</p>
      </div>
      <span v-if="current?.timer_duration_seconds" class="text-lg font-semibold tabular-nums" :class="timerStore.secondsRemaining < 60 ? 'text-danger-500' : 'text-slate-900'">
        {{ timerStore.formatted }}
      </span>
    </div>

    <BoardGrid
      :columns="retroStore.cardsByColumn"
      :selected-ids="[]"
      :current-user-id="currentUserId"
      :voted-card-ids="[]"
      phase="board"
      @create-card="emit('open-card-modal', $event)"
      @edit-card="emit('edit-card', $event)"
      @delete-card="emit('delete-card', $event.id)"
    />

    <div v-if="isFacilitator" class="flex justify-end">
      <button class="button-primary" type="button" @click="emit('advance-phase')">
        Next phase
      </button>
    </div>
  </div>
</template>
