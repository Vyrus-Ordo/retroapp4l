<template>
  <div class="panel p-8 flex flex-col gap-6 min-h-[50vh]">
    <h1 class="text-xl font-bold text-gray-900 mb-2">Previous action check</h1>
    <p class="text-gray-600">Review pending actions from the last closed retro for this team.</p>
    <div class="mt-4 space-y-3">
      <div v-for="action in retroStore.previousActions.action_items" :key="action.id" class="rounded-lg border border-gray-100 bg-gray-50 p-4 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-2">
        <div>
          <p class="text-sm font-medium text-gray-900">{{ action.description }}</p>
          <p class="mt-1 text-xs text-gray-500">{{ action.assignee_name || 'No assignee' }}</p>
        </div>
        <select class="field-input max-w-48" :value="action.status" @change="retroStore.updatePreviousActionStatus(current.id, action.id, String(($event.target as HTMLSelectElement).value))" :disabled="!isFacilitator">
          <option value="not_started">Not started</option>
          <option value="in_progress">In progress</option>
          <option value="done">Done</option>
        </select>
      </div>
      <div v-if="!retroStore.previousActions.action_items.length" class="rounded-lg border border-dashed border-gray-200 bg-gray-50 p-6 text-sm text-gray-500">
        No previous actions found.
      </div>
    </div>
    <div class="flex justify-end mt-4">
      <button v-if="isFacilitator" class="button-primary" @click="$emit('advance-phase')">Next phase</button>
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
