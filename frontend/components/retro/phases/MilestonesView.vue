<template>
  <div class="panel p-8 flex flex-col gap-6 min-h-[50vh]">
    <div class="flex items-center justify-between gap-4">
      <div>
        <h1 class="text-xl font-bold text-gray-900 mb-2">Milestones</h1>
        <p class="text-gray-600">Present the key highlights before opening the 4L board.</p>
      </div>
      <div class="flex items-center gap-4">
        <button v-if="isFacilitator" class="button-primary py-1.5 text-sm" @click="$emit('advance-phase')">Next phase</button>
      </div>
    </div>
    <div class="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      <MilestoneCard v-for="milestone in current.milestones" :key="milestone.id" :milestone="milestone" />
      <div v-if="!current.milestones.length" class="rounded-lg border border-dashed border-gray-200 bg-gray-50 p-6 text-sm text-gray-500">
        No milestones registered.
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import MilestoneCard from '~/components/retro/MilestoneCard.vue'
const props = defineProps({
  current: Object,
  isFacilitator: Boolean
})
</script>
