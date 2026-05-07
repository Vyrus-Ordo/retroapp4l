<template>
  <div class="panel p-8 flex flex-col gap-6 min-h-[50vh]">
    <div class="flex items-center justify-between gap-4">
      <div>
        <h1 class="text-xl font-light text-white mb-2">Previous action check</h1>
        <p class="text-zinc-500">Review pending actions from the last closed retro for this team.</p>
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
        <select class="field-input max-w-48" :value="action.status" @change="retroStore.updatePreviousActionStatus(current.id, action.id, String(($event.target as HTMLSelectElement).value))" :disabled="!isFacilitator">
          <option class="bg-[#0d0d0d] text-zinc-200" value="not_started">Not started</option>
          <option class="bg-[#0d0d0d] text-zinc-200" value="in_progress">In progress</option>
          <option class="bg-[#0d0d0d] text-zinc-200" value="done">Done</option>
        </select>
      </div>
      <div v-if="!retroStore.previousActions.action_items.length" class="rounded-lg border border-dashed border-white/10 p-6 text-sm text-zinc-600">
        No previous actions found.
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  current: Object,
  isFacilitator: Boolean,
  retroStore: Object
})
</script>
