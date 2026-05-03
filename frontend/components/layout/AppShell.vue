<script setup lang="ts">
const props = defineProps<{
  mode?: 'default' | 'retro'
  phases?: string[]
  currentPhase?: string
  isFacilitator?: boolean
}>()
</script>

<template>
  <div class="flex min-h-screen flex-col">
    <RetroHeader
      v-if="props.mode === 'retro'"
      :phases="props.phases"
      :currentPhase="props.currentPhase"
      :isFacilitator="props.isFacilitator"
    />
    <Header v-else />
    <div class="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-6 px-6 py-6 lg:px-8 lg:py-8">
      <main class="min-w-0 flex-1">
        <slot />
      </main>
    </div>
    <AppFooter />
    <ToastContainer />
  </div>
</template>