<script setup lang="ts">
import { computed } from 'vue'
import type { RetroPhase } from '~/utils/types'
import { PHASE_META } from '~/utils/types'

const props = defineProps<{
  currentPhase: RetroPhase
  skipCheckPhase?: boolean
}>()

const ALL_PHASES: RetroPhase[] = [
  'lobby',
  'presentation',
  'check',
  'board',
  'grouping',
  'voting',
  'discussion',
  'actions',
  'closed',
]

const phases = computed<RetroPhase[]>(() =>
  props.skipCheckPhase ? ALL_PHASES.filter((p) => p !== 'check') : ALL_PHASES,
)

const currentIdx = computed(() => {
  const idx = phases.value.indexOf(props.currentPhase)
  return idx === -1 ? 0 : idx
})

const prevPhase = computed<RetroPhase | null>(() =>
  currentIdx.value > 0 ? phases.value[currentIdx.value - 1] : null,
)

const nextPhase = computed<RetroPhase | null>(() =>
  currentIdx.value < phases.value.length - 1 ? phases.value[currentIdx.value + 1] : null,
)

function label(phase: RetroPhase) {
  return PHASE_META[phase]?.label ?? phase
}

function icon(phase: RetroPhase) {
  return PHASE_META[phase]?.icon ?? ''
}
</script>

<template>
  <nav class="flex items-center gap-1" aria-label="Session phase">
    <!-- Previous phase -->
    <div class="flex w-28 items-center justify-end">
      <Transition name="fade" mode="out-in">
        <span
          v-if="prevPhase"
          :key="prevPhase"
          class="inline-flex items-center gap-1 rounded-full border border-white/10 px-3 py-1 text-xs font-light text-zinc-600"
        >
          <span v-if="icon(prevPhase)" class="mdi" :class="`mdi-${icon(prevPhase)}`" />
          <span>{{ label(prevPhase) }}</span>
        </span>
      </Transition>
    </div>

    <!-- Left arrow -->
    <span class="text-zinc-700 select-none">›</span>

    <!-- Current phase -->
    <div class="flex w-36 items-center justify-center">
      <Transition name="scale" mode="out-in">
        <span
          :key="currentPhase"
          class="inline-flex items-center gap-1.5 rounded-full border border-[#00f2ff]/40 px-4 py-1.5 text-xs font-medium text-[#00f2ff]"
          style="box-shadow: 0 0 10px rgba(0,242,255,0.15)"
        >
          <span v-if="icon(currentPhase)" class="mdi" :class="`mdi-${icon(currentPhase)}`" />
          <span>{{ label(currentPhase) }}</span>
        </span>
      </Transition>
    </div>

    <!-- Right arrow -->
    <span class="text-zinc-700 select-none">›</span>

    <!-- Next phase -->
    <div class="flex w-28 items-center justify-start">
      <Transition name="fade" mode="out-in">
        <span
          v-if="nextPhase"
          :key="nextPhase"
          class="inline-flex items-center gap-1 rounded-full border border-white/10 px-3 py-1 text-xs font-light text-zinc-600"
        >
          <span v-if="icon(nextPhase)" class="mdi" :class="`mdi-${icon(nextPhase)}`" />
          <span>{{ label(nextPhase) }}</span>
        </span>
      </Transition>
    </div>
  </nav>
</template>

<style scoped>
/* Fade: fases anterior e próxima */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Scale: fase atual — entra maior, sai menor */
.scale-enter-active,
.scale-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.scale-enter-from {
  opacity: 0;
  transform: scale(0.85);
}
.scale-leave-to {
  opacity: 0;
  transform: scale(0.85);
}
</style>
