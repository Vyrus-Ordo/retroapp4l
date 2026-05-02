<template>
  <div class="panel p-8 flex flex-col gap-6 min-h-[50vh]">
    <h1 class="text-xl font-bold text-gray-900 mb-2">Votação</h1>
    <p class="text-gray-600">Vote nos cards mais importantes para discussão. Você pode votar em cards de outras pessoas.</p>
    <div class="mt-6 text-center text-gray-400">(Votação em construção — integrar VoteControls e lógica de votos)</div>
    <div class="flex justify-end mt-4">
      <button v-if="isFacilitator" class="button-primary" @click="$emit('advance-phase')">Próxima fase</button>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  current: Object,
  isFacilitator: Boolean
})
</script>
