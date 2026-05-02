<template>
  <div class="focus-card bg-primary-50 border border-primary-200 rounded-xl p-6 flex flex-col gap-3 shadow-md">
    <div class="flex items-center gap-2 mb-2">
      <span class="mdi mdi-star text-xl text-primary-500" />
      <span class="font-semibold text-lg text-primary-700">Discussão em foco</span>
    </div>
    <div class="text-base text-gray-900 font-medium">{{ card.text }}</div>
    <div class="flex gap-2 mt-2">
      <span class="text-xs text-gray-500">Autor: {{ card.author || 'Anônimo' }}</span>
      <VoteBadge :count="card.votes || 0" :active="true" />
    </div>
    <div class="flex gap-2 mt-4 justify-end">
      <button v-if="canNext" class="button-primary" @click="$emit('next')">Próximo card</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import VoteBadge from './VoteBadge.vue'
const props = defineProps({
  card: Object,
  canNext: Boolean
})
</script>

<style scoped>
.focus-card {
  min-width: 260px;
}
</style>
