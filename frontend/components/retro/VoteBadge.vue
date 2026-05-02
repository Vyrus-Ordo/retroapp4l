<script setup lang="ts">
defineProps<{
  count: number
  active?: boolean
}>()
</script>

<template>
  <span :class="['vote-badge', active ? 'bg-primary-50 border border-primary-200 text-primary-700' : 'bg-gray-50 border border-gray-200 text-gray-500', 'rounded px-2 py-0.5 text-xs font-semibold']">
    {{ count }} voto<span v-if="count !== 1">s</span>
  </span>
</template>

<style scoped>
.vote-badge {
  min-width: 32px;
  display: inline-block;
  text-align: center;
}
</style>