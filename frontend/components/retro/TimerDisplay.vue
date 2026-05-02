<script setup lang="ts">
import { PauseCircleIcon, PlayCircleIcon } from "@heroicons/vue/24/outline"

defineProps<{
  label: string
  toneClass: string
  paused?: boolean
  facilitator?: boolean
}>()

defineEmits<{
  pause: []
  resume: []
}>()
</script>

<template>
  <div class="inline-flex items-center gap-2">
    <span :class="toneClass" class="text-xl font-semibold transition-colors duration-150">{{ label }}</span>
    <button
      v-if="facilitator && !paused"
      class="text-slate-500 transition-colors duration-150 hover:text-slate-900"
      type="button"
      @click="$emit('pause')"
    >
      <PauseCircleIcon class="h-5 w-5" />
    </button>
    <button
      v-if="facilitator && paused"
      class="text-slate-500 transition-colors duration-150 hover:text-slate-900"
      type="button"
      @click="$emit('resume')"
    >
      <PlayCircleIcon class="h-5 w-5" />
    </button>
  </div>
</template>