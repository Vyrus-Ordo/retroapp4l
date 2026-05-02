<template>
  <div class="panel p-8 flex flex-col gap-6 min-h-[50vh]">
    <h1 class="text-xl font-bold text-gray-900 mb-2">Board 4L</h1>
    <p class="text-gray-600">Adicione cards nas colunas, compartilhe aprendizados, sentimentos e sugestões.</p>
    <!-- Aqui entraria o grid de colunas/cards -->
    <div class="mt-6 text-center text-gray-400">(Board 4L em construção — integrar BoardGrid e ColumnBox)</div>
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
