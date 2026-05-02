<template>
  <header class="border-b border-gray-100 bg-white">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-3 lg:px-8">
      <NuxtLink class="text-lg font-bold tracking-tight text-brand-700" to="/">
        RetroApp 4L
      </NuxtLink>
      <PhaseStepper
        :phases="phases"
        :current-phase="currentPhase"
        :is-facilitator="isFacilitator"
        @select="onPhaseSelect"
      />
      <div class="flex items-center gap-3">
        <slot name="timer" />
        <button class="icon-btn" @click="openSettings" title="Configurações">
          <span class="mdi mdi-cog-outline text-xl" />
        </button>
      </div>
    </div>
    <SettingsModal v-if="showSettings" @close="showSettings = false" />
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import PhaseStepper from './PhaseStepper.vue'

const props = defineProps<{
  phases: string[]
  currentPhase: string
  isFacilitator?: boolean
}>()

const showSettings = ref(false)
function openSettings() {
  showSettings.value = true
}
function onPhaseSelect(phase: string) {
  // Emite evento para shell retro
  // $emit('phase-select', phase)
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
