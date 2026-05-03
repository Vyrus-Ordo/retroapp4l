<script setup lang="ts">
import type { RetrospectiveSummary } from '~/utils/types'

const props = defineProps<{
  retro: RetrospectiveSummary
}>()

const phaseLabels: Record<string, string> = {
  setup: 'Setup',
  lobby: 'Lobby',
  presentation: 'Presentation',
  check: 'Check-in',
  board: 'Board',
  grouping: 'Grouping',
  voting: 'Voting',
  discussion: 'Discussion',
  actions: 'Actions',
}

const phaseLabel = computed(() => phaseLabels[props.retro.status] ?? props.retro.status)
</script>

<template>
  <section class="rounded-lg border border-brand-200 bg-white p-6 shadow-sm">
    <div class="flex flex-col gap-4">
      <div class="flex items-center gap-3">
        <PhaseChip :phase="phaseLabel" />
        <span class="text-xs font-medium text-slate-600">Active session</span>
      </div>
      <div class="flex flex-col gap-1">
        <h2 class="text-2xl font-semibold text-slate-900">{{ retro.title }}</h2>
        <p v-if="retro.sprint_name" class="text-base text-slate-600">{{ retro.sprint_name }}</p>
      </div>
      <NuxtLink
        :to="`/retro/${retro.id}`"
        class="inline-flex w-fit items-center justify-center rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600 active:bg-brand-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black"
      >
        Continue
      </NuxtLink>
    </div>
  </section>
</template>
