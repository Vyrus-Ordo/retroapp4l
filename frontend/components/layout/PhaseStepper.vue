<template>
  <nav class="phase-stepper flex items-center gap-2">
    <template v-for="(phase, idx) in phases" :key="phase">
      <button
        class="stepper-pill flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium transition"
        :class="pillClass(idx)"
        :disabled="!isFacilitator && idx > currentIdx"
        @click="$emit('select', phase)"
      >
        <span v-if="icon(phase)" class="mdi" :class="'mdi-' + icon(phase)" />
        <span>{{ label(phase) }}</span>
      </button>
      <span v-if="idx < phases.length - 1" class="w-4 h-0.5 bg-white/8 mx-1"></span>
    </template>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { PHASE_META } from '~/utils/types'

const props = defineProps<{
  phases: string[]
  currentPhase: string
  isFacilitator?: boolean
}>()
const emit = defineEmits(['select'])

const currentIdx = computed(() => props.phases.indexOf(props.currentPhase))
const label = (phase: string) => PHASE_META[phase]?.label || phase
const icon = (phase: string) => PHASE_META[phase]?.icon || ''
const pillClass = (idx: number) => {
  if (idx < currentIdx.value) return 'border border-[#00f2ff]/20 text-[#00f2ff]/60'
  if (idx === currentIdx.value) return 'border border-[#00f2ff] text-[#00f2ff] shadow-glow'
  return 'border border-white/10 text-zinc-600'
}
</script>

<style scoped>
.phase-stepper {
  user-select: none;
}
.stepper-pill {
  min-width: 0;
  outline: none;
  cursor: pointer;
}
.stepper-pill:disabled {
  opacity: 0.7;
  cursor: default;
}
.mdi {
  font-size: 1.1em;
  vertical-align: middle;
}
</style>
