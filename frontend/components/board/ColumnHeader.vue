<script setup lang="ts">
import {
  ClockIcon,
  HandThumbDownIcon,
  HandThumbUpIcon,
  LightBulbIcon,
  PlusIcon,
} from "@heroicons/vue/24/outline"

import type { CardColumn } from "~/utils/types"

const props = defineProps<{
  column: CardColumn
  count: number
  canCreate?: boolean
}>()

defineEmits<{
  create: []
}>()

const config = computed(() => {
  if (props.column === 'loved') {
    return { title: 'Liked', accentColor: '#22c55e', icon: HandThumbUpIcon }
  }
  if (props.column === 'loathed') {
    return { title: 'Loathed', accentColor: '#ef4444', icon: HandThumbDownIcon }
  }
  if (props.column === 'longed') {
    return { title: 'Longed for', accentColor: '#60a5fa', icon: ClockIcon }
  }
  return { title: 'Learned', accentColor: '#a1a1aa', icon: LightBulbIcon }
})
</script>

<template>
  <div
    class="border-b px-2.5 py-3 sm:px-3"
    :style="{ borderBottomColor: config.accentColor + '33', borderLeftColor: config.accentColor, borderLeftWidth: '2px', borderLeftStyle: 'solid' }"
  >
    <div class="flex min-h-6 items-center justify-between gap-1.5">
      <div
        class="inline-flex min-w-max flex-shrink-0 items-center gap-1.5 whitespace-nowrap text-xs font-medium uppercase tracking-wide"
        :style="{ color: config.accentColor }"
      >
        <component :is="config.icon" class="h-4 w-4 flex-shrink-0" />
        <span class="whitespace-nowrap">{{ config.title }}</span>
      </div>
      <div class="inline-flex min-w-0 flex-shrink items-center justify-end gap-1">
        <span class="inline-block min-w-4 text-right text-xs font-light tabular-nums" style="color: #52525b">{{ count }}</span>
        <button
          v-if="canCreate"
          class="column-add-button"
          type="button"
          :style="{ '--column-accent': config.accentColor }"
          aria-label="Add card"
          title="Add card"
          @click="$emit('create')"
        >
          <PlusIcon class="h-3.5 w-3.5" />
          <span>Add</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.column-add-button {
  display: inline-flex;
  min-width: 2.75rem;
  height: 1.5rem;
  align-items: center;
  justify-content: center;
  gap: 0.1875rem;
  border-radius: 0.375rem;
  border: 1px solid color-mix(in srgb, var(--column-accent) 24%, transparent);
  background: color-mix(in srgb, var(--column-accent) 5%, transparent);
  padding: 0 0.35rem;
  color: color-mix(in srgb, var(--column-accent) 72%, #ffffff);
  font-size: 0.6875rem;
  font-weight: 500;
  line-height: 1;
  transition:
    background-color 150ms ease,
    border-color 150ms ease,
    color 150ms ease,
    box-shadow 150ms ease,
    transform 150ms ease;
}

.column-add-button:hover {
  border-color: color-mix(in srgb, var(--column-accent) 44%, transparent);
  background: color-mix(in srgb, var(--column-accent) 10%, transparent);
  color: color-mix(in srgb, var(--column-accent) 90%, #ffffff);
  box-shadow: 0 0 12px color-mix(in srgb, var(--column-accent) 18%, transparent);
  transform: translateY(-1px);
}
</style>
