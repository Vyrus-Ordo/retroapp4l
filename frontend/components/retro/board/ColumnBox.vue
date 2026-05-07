<template>
  <div class="column-box flex flex-col rounded-xl border border-white/10 p-4 gap-3" style="background: rgba(255,255,255,0.03)">
    <div class="flex items-center gap-2 mb-2">
      <span :class="['mdi', column.icon, 'text-xl', 'text-' + column.color + '-500']" />
      <h2 class="font-light text-base text-white">{{ column.label }}</h2>
    </div>
    <div class="flex-1 flex flex-col gap-2">
      <slot name="cards">
        <RetroCard
          v-for="card in cards"
          :key="card.id"
          :card="card"
          @action="$emit('card-action', $event)"
        />
      </slot>
      <div v-if="!cards.length" class="text-zinc-600 text-sm text-center py-6">Nenhum card</div>
    </div>
    <button
      v-if="canAdd"
      class="button-secondary mt-2"
      @click="$emit('add-card')"
    >Adicionar card</button>
  </div>
</template>

<script setup lang="ts">
import RetroCard from '../RetroCard.vue'
const props = defineProps({
  column: Object,
  cards: {
    type: Array,
    default: () => []
  },
  canAdd: Boolean
})
</script>

<style scoped>
.column-box {
  min-height: 32vh;
}
</style>
