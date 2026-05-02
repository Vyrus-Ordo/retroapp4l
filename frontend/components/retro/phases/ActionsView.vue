<template>
  <div class="panel p-8 flex flex-col gap-6 min-h-[50vh]">
    <h1 class="text-xl font-bold text-gray-900 mb-2">Ações</h1>
    <p class="text-gray-600">Defina compromissos, responsáveis e prazos para os itens de ação.</p>
    <div class="mt-6 text-center text-gray-400">(Ações em construção — integrar ActionEditor e lista de ações)</div>
    <div class="flex justify-end mt-4">
      <button v-if="isFacilitator" class="button-primary" @click="$emit('advance-phase')">Encerrar retro</button>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  current: Object,
  isFacilitator: Boolean
})
</script>
