defineProps<{
<template>
  <div class="milestone-card bg-white rounded-lg border border-gray-200 p-4 flex flex-col gap-2 shadow-sm">
    <div class="flex items-center gap-2 mb-1">
      <span class="mdi mdi-flag-checkered text-lg text-primary-500" />
      <span class="font-semibold text-gray-900">{{ milestone.title }}</span>
    </div>
    <div class="text-sm text-gray-600">{{ milestone.description }}</div>
    <div class="text-xs text-gray-400 mt-1">{{ milestone.date }}</div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  milestone: Object
})
</script>

<style scoped>
.milestone-card {
  min-width: 220px;
}
</style>