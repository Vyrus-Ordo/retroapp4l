<template>
  <div class="panel p-8 flex flex-col gap-6 min-h-[50vh]">
    <h1 class="text-xl font-bold text-gray-900 mb-2">Discussão</h1>
    <p class="text-gray-600">Debata os cards mais votados. A autoria é revelada nesta fase.</p>
    <div class="mt-6 text-center text-gray-400">(Discussão em construção — integrar FocusCard, fila de cards e controles de facilitadora)</div>
    <div class="flex justify-end mt-4">
      <button v-if="isFacilitator" class="button-primary" @click="$emit('advance-phase')">Ir para Ações</button>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  current: Object,
  isFacilitator: Boolean
})
</script>
