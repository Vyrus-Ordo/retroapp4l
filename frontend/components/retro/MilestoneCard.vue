<template>
  <div
    class="milestone-card flex flex-col gap-2 rounded-lg border border-white/10 p-4"
    style="background: rgba(255, 255, 255, 0.04)"
  >
    <div class="mb-1 flex items-center gap-2">
      <component :is="visual.icon" class="h-5 w-5 shrink-0" :style="{ color: visual.color }" aria-hidden="true" />
      <span class="text-xs font-medium uppercase tracking-[0.2em]" :style="{ color: visual.color }">
        {{ visual.label }}
      </span>
    </div>
    <div class="text-sm text-zinc-500">{{ milestone?.description }}</div>
    <div v-if="milestone?.created_at" class="mt-1 text-xs text-zinc-700">{{ formatDate(milestone.created_at) }}</div>
  </div>
</template>

<script setup lang="ts">
import { getMilestoneVisual } from "~/utils/milestoneVisuals"

const props = defineProps({
  milestone: {
    type: Object,
    default: () => null,
  },
})

const visual = computed(() => getMilestoneVisual(props.milestone?.category))

function formatDate(value: string): string {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString()
}
</script>

<style scoped>
.milestone-card {
  min-width: 220px;
}
</style>
