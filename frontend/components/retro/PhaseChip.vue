<script setup lang="ts">
defineProps<{
  phase: string
  timerText?: string
}>()
</script>

<template>
  <span class="phase-chip bg-primary-50 text-primary-700 text-xs font-semibold rounded px-2 py-1 inline-flex items-center gap-2 border border-primary-200">
    <span>{{ phase }}</span>
    <span v-if="timerText">{{ timerText }}</span>
  </span>
</template>

<style scoped>
.phase-chip {
  min-width: 48px;
  text-align: center;
}
</style>