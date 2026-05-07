<script setup lang="ts">
defineProps<{
  phase: string
  timerText?: string
}>()
</script>

<template>
  <span class="phase-chip inline-flex items-center gap-2 rounded border border-[#00f2ff]/35 px-2 py-1 text-xs font-light text-[#00f2ff]">
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