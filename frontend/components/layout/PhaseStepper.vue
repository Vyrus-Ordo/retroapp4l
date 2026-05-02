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
      <span v-if="idx < phases.length - 1" class="w-4 h-0.5 bg-gray-200 mx-1"></span>
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
  if (idx < currentIdx.value) return 'bg-brand-50 text-brand-700 border border-brand-200'
  if (idx === currentIdx.value) return 'bg-brand-500 text-white border border-brand-500 shadow-card-md'
  return 'bg-gray-50 text-gray-400 border border-gray-100'
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
