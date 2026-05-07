<script setup lang="ts">
defineProps<{
  count: number
  active?: boolean
}>()
</script>

<template>
  <span :class="['vote-badge', active ? 'border border-[#00f2ff]/30 text-[#00f2ff]' : 'border border-white/10 text-zinc-600', 'rounded px-2 py-0.5 text-xs font-light']">
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