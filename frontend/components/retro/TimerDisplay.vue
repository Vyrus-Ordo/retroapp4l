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
  <div class="timer-display inline-flex items-center gap-2">
    <span :class="toneClass" class="text-xl font-mono font-semibold transition-colors duration-150">{{ label }}</span>
    <button
      v-if="facilitator && !paused"
      class="text-[#00f2ff]/70 hover:text-[#00f2ff] transition-colors duration-150"
      type="button"
      @click="$emit('pause')"
    >
      <PauseCircleIcon class="h-5 w-5" />
    </button>
    <button
      v-if="facilitator && paused"
      class="text-[#00f2ff]/70 hover:text-[#00f2ff] transition-colors duration-150"
      type="button"
      @click="$emit('resume')"
    >
      <PlayCircleIcon class="h-5 w-5" />
    </button>
  </div>
</template>

<style scoped>
.timer-display {
  min-width: 64px;
}
</style>