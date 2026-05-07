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
  <section class="rounded-lg border border-[#00f2ff]/20 p-6 backdrop-blur-sm" style="background: rgba(0,242,255,0.04)">
    <div class="flex flex-col gap-4">
      <div class="flex items-center gap-3">
        <PhaseChip :phase="phaseLabel" />
        <span class="text-xs font-light text-zinc-500">Active session</span>
      </div>
      <div class="flex flex-col gap-1">
        <h2 class="text-2xl font-light text-white">{{ retro.title }}</h2>
        <p v-if="retro.sprint_name" class="text-base text-zinc-400">{{ retro.sprint_name }}</p>
      </div>
      <NuxtLink
        :to="`/retro/${retro.id}`"
        class="inline-flex w-fit items-center justify-center rounded-lg border border-[#00f2ff] px-4 py-2 text-sm font-medium text-[#00f2ff] transition-all duration-200 hover:bg-[#00f2ff]/10 hover:shadow-glow"
      >
        Continue
      </NuxtLink>
    </div>
  </section>
</template>
