<script setup lang="ts">
defineProps<{
  phaseLabel?: string
  timerText?: string
}>()
</script>

<template>
  <div class="flex min-h-screen flex-col">
    <AppHeader :phase-label="phaseLabel" :timer-text="timerText" />
    <div class="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-6 px-6 py-6 lg:flex-row lg:px-8 lg:py-8">
      <main class="min-w-0 flex-1">
        <slot />
      </main>
      <div v-if="$slots.sidebar" class="w-full lg:max-w-sm">
        <slot name="sidebar" />
      </div>
    </div>
    <AppFooter />
  </div>
</template>