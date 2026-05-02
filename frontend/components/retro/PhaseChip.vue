<script setup lang="ts">
defineProps<{
  phase: string
  timerText?: string
}>()
</script>

<template>
  <div class="bg-brand-50 text-brand-500 text-xs font-semibold rounded px-2 py-1 inline-flex items-center gap-2">
    <span>{{ phase }}</span>
    <span v-if="timerText">{{ timerText }}</span>
  </div>
</template>