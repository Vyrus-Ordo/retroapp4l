<template>
  <div class="panel p-8 flex flex-col gap-6 min-h-[50vh]">
    <h1 class="text-xl font-bold text-gray-900 mb-2">Marcos</h1>
    <p class="text-gray-600">Apresente os principais acontecimentos antes de abrir o board 4L.</p>
    <div class="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      <MilestoneCard v-for="milestone in current.milestones" :key="milestone.id" :milestone="milestone" />
      <div v-if="!current.milestones.length" class="rounded-lg border border-dashed border-gray-200 bg-gray-50 p-6 text-sm text-gray-500">
        Nenhum marco cadastrado.
      </div>
    </div>
    <div class="flex justify-end mt-4">
      <button v-if="isFacilitator" class="button-primary" @click="$emit('advance-phase')">Próxima fase</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import MilestoneCard from '~/components/retro/MilestoneCard.vue'
const props = defineProps({
  current: Object,
  isFacilitator: Boolean
})
</script>
