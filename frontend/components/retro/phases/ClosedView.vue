<template>
  <div class="panel p-8 flex flex-col items-center justify-center min-h-[50vh] gap-6">
    <span class="mdi mdi-check-decagram text-5xl text-success-500 mb-2" />
    <h1 class="text-2xl font-light text-white">Retrospective closed</h1>
    <p class="text-zinc-500">Thank you for participating! View the history to review cards, milestones, and actions.</p>
    <NuxtLink class="button-primary mt-6" :to="`/history/${current?.id}`">View history</NuxtLink>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  current: Object
})
</script>
