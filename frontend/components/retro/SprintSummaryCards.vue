<template>
  <div class="grid gap-3 grid-cols-2 xl:grid-cols-4">
    <div
      v-for="card in cards"
      :key="card.label"
      class="panel p-4 flex flex-col gap-1 items-center text-center"
    >
      <span class="text-xs text-zinc-500 uppercase tracking-wide">{{ card.label }}</span>
      <span class="text-2xl font-light" :class="card.highlight ? 'text-[#00f2ff]' : 'text-zinc-100'">
        {{ card.value }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SprintSummary } from '~/utils/types'

const props = defineProps<{
  summary: SprintSummary
}>()

const cards = computed(() => [
  { label: 'Total Sprint', value: props.summary.total_stories, highlight: false },
  { label: 'Concluídas', value: props.summary.completed, highlight: false },
  { label: 'Carry-over', value: props.summary.carryover, highlight: false },
  {
    label: 'Taxa de Entrega',
    value: props.summary.delivery_rate !== null ? `${props.summary.delivery_rate}%` : '--',
    highlight: true,
  },
])
</script>
