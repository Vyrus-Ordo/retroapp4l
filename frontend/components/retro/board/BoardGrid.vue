<template>
  <div class="board-grid grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
    <ColumnBox
      v-for="col in columns"
      :key="col.id"
      :column="col"
      :cards="cardsByColumn[col.id] || []"
      :canAdd="canAdd"
      @add-card="$emit('add-card', col.id)"
      @card-action="$emit('card-action', $event)"
    />
  </div>
</template>

<script setup lang="ts">
import ColumnBox from './ColumnBox.vue'
import { COLUMN_META } from '~/utils/types'
const props = defineProps({
  columns: {
    type: Array,
    default: () => COLUMN_META
  },
  cardsByColumn: {
    type: Object,
    default: () => ({})
  },
  canAdd: Boolean
})
</script>

<style scoped>
.board-grid {
  min-height: 40vh;
}
</style>
