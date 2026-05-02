<script setup lang="ts">
defineProps<{
  count: number
  active?: boolean
}>()
</script>

<template>
  <span :class="active ? 'bg-brand-50 rounded px-1' : ''" class="text-brand-500 text-xs font-semibold">
    {{ count }} votes
  </span>
</template>