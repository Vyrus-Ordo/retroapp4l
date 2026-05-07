<script setup lang="ts">
import BoardGrid from "~/components/board/BoardGrid.vue"

const props = defineProps<{
  current: any
  isFacilitator: boolean
  retroStore: any
}>()

const emit = defineEmits<{
  "advance-phase": []
}>()

const selectionCount = computed(() => props.retroStore.selectedCardIds.length)

async function groupSelected() {
  await props.retroStore.groupSelected(props.current.id)
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between gap-4">
      <div>
        <h1 class="text-xl font-bold text-slate-900">Grouping</h1>
        <p class="mt-1 text-sm text-slate-500">
          <template v-if="isFacilitator">Select similar cards to group them together.</template>
          <template v-else>The facilitator is grouping similar cards.</template>
        </p>
      </div>
      <div class="flex items-center gap-3">
        <button v-if="isFacilitator" class="button-primary py-1.5 text-sm" type="button" @click="emit('advance-phase')">
          Next phase
        </button>
        <template v-if="isFacilitator && selectionCount > 0">
          <button class="button-secondary text-sm" type="button" @click="retroStore.clearSelection()">
            Clear ({{ selectionCount }})
          </button>
          <button
            :disabled="selectionCount < 2"
            class="button-primary text-sm disabled:bg-slate-100 disabled:text-slate-300 disabled:cursor-not-allowed"
            type="button"
            @click="groupSelected"
          >
            Group selected ({{ selectionCount }})
          </button>
        </template>
      </div>
    </div>

    <BoardGrid
      :columns="retroStore.cardsByColumn"
      :grouped-children="retroStore.groupedChildrenByParentId"
      :selected-ids="isFacilitator ? retroStore.selectedCardIds : []"
      :voted-card-ids="[]"
      phase="grouping"
      @toggle-select="isFacilitator ? retroStore.toggleCardSelection($event) : undefined"
    />

  </div>
</template>

