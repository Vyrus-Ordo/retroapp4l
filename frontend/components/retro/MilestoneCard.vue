defineProps<{
<template>
  <div class="milestone-card rounded-lg border border-white/10 p-4 flex flex-col gap-2" style="background: rgba(255,255,255,0.04)">
    <div class="flex items-center gap-2 mb-1">
      <span class="mdi mdi-flag-checkered text-lg text-[#00f2ff]/60" />
      <span class="font-light text-zinc-200">{{ milestone.title }}</span>
    </div>
    <div class="text-sm text-zinc-500">{{ milestone.description }}</div>
    <div class="text-xs text-zinc-700 mt-1">{{ milestone.date }}</div>
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