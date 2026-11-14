<template>
  <div class="panel p-8 flex flex-col gap-6 min-h-[50vh]">
    <div class="flex items-center justify-between gap-4">
      <div>
        <h1 class="text-xl font-light text-white mb-2">Previous action check</h1>
        <p class="text-zinc-500">Pending actions from this team's closed retrospectives. An item leaves this list once marked Done.</p>
      </div>
      <div class="flex items-center gap-4">
        <button v-if="isFacilitator" class="button-primary py-1.5 text-sm" @click="$emit('advance-phase')">Next phase</button>
      </div>
    </div>
    <div class="mt-4 space-y-3">
      <div v-for="action in retroStore.previousActions.action_items" :key="action.id" class="rounded-lg border border-white/10 p-4 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-2" style="background: rgba(255,255,255,0.03)">
        <div>
          <p class="text-sm font-light text-zinc-200">{{ action.description }}</p>
          <p class="mt-1 text-xs text-zinc-600">{{ action.assignee_name || 'No assignee' }}</p>
        </div>
        <select class="field-input max-w-48" :value="action.status" :disabled="!isFacilitator" @change="retroStore.updatePreviousActionStatus(current.id, action.id, String(($event.target as HTMLSelectElement).value))">
          <option class="bg-[#0d0d0d] text-zinc-200" value="not_started">Not started</option>
          <option class="bg-[#0d0d0d] text-zinc-200" value="in_progress">In progress</option>
          <option class="bg-[#0d0d0d] text-zinc-200" value="done">Done</option>
        </select>
      </div>
      <div v-if="!retroStore.previousActions.action_items.length" class="rounded-lg border border-dashed border-white/10 p-6 text-sm text-zinc-600">
        No previous actions found.
      </div>
    </div>

    <details v-if="recentlyCompleted.length" class="rounded-lg border border-white/10" style="background: rgba(255,255,255,0.03)">
      <summary class="cursor-pointer select-none px-4 py-3 text-sm font-light text-zinc-300">
        ✅ Concluídos desde a última retro ({{ recentlyCompleted.length }})
      </summary>
      <div class="space-y-3 px-4 pb-4">
        <div v-for="action in recentlyCompleted" :key="action.id" class="rounded-lg border border-white/10 p-4 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-2">
          <div>
            <p class="text-sm font-light text-zinc-400 line-through">{{ action.description }}</p>
            <p class="mt-1 text-xs text-zinc-600">{{ action.assignee_name || 'No assignee' }}</p>
          </div>
          <button v-if="isFacilitator" class="button-secondary py-1.5 text-sm" @click="retroStore.updatePreviousActionStatus(current.id, action.id, 'in_progress')">
            Reabrir
          </button>
        </div>
      </div>
    </details>
  </div>
</template>

<script setup lang="ts">
import type { ActionItem, PreviousActionsResponse } from "~/utils/types"

const props = defineProps({
  current: {
    type: Object,
    default: null,
  },
  isFacilitator: Boolean,
  retroStore: {
    type: Object,
    default: null,
  },
})

const recentlyCompleted = computed<ActionItem[]>(() => {
  const store = props.retroStore as { previousActions?: PreviousActionsResponse } | null
  return store?.previousActions?.recently_completed ?? []
})

defineEmits(['advance-phase'])
</script>
