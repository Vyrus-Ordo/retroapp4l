<template>
  <header class="border-b border-[#00f2ff]/10 bg-[#050505]/90 backdrop-blur-md">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
      <NuxtLink class="shrink-0 text-sm font-light tracking-[0.15em] uppercase text-[#00f2ff] hover:brightness-125" style="font-family: 'JetBrains Mono', monospace" to="/">
        RetroApp 4L
      </NuxtLink>
      <PhaseCarousel
        :current-phase="currentPhase"
        :skip-check-phase="skipCheckPhase"
      />
      <div class="flex items-center gap-3">
        <slot name="timer" />
        <button class="icon-btn text-zinc-400 hover:text-[#00f2ff]" title="Settings" @click="openSettings">
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
  @apply rounded-full p-2 transition;
  background: transparent;
}
.icon-btn:hover {
  background: rgba(0, 242, 255, 0.07);
}
</style>
