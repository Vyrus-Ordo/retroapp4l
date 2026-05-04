<template>
  <header class="border-b border-slate-100 bg-white">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
      <NuxtLink class="shrink-0 text-sm font-semibold text-slate-900 hover:text-brand-600" to="/">
        RetroApp 4L
      </NuxtLink>
      <PhaseCarousel
        :current-phase="currentPhase"
        :skip-check-phase="skipCheckPhase"
      />
      <div class="flex items-center gap-3">
        <slot name="timer" />
        <button class="icon-btn" title="Settings" @click="openSettings">
          <span class="mdi mdi-cog-outline text-xl" />
        </button>
      </div>
    </div>
    <SettingsModal v-if="showSettings" @close="showSettings = false" />
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { RetroPhase } from '~/utils/types'
import PhaseCarousel from './PhaseCarousel.vue'
import SettingsModal from './SettingsModal.vue'

const props = defineProps<{
  currentPhase: RetroPhase
  skipCheckPhase?: boolean
}>()

const showSettings = ref(false)
function openSettings() {
  showSettings.value = true
}
</script>

<!--
SettingsModal deve ser implementado depois.
Slot timer permite inserir timer/controles.
-->

<style scoped>
.icon-btn {
  @apply rounded-full p-2 hover:bg-gray-50 transition;
}
</style>
