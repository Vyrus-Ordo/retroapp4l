<script setup lang="ts">
import {
  ClockIcon,
  HandThumbDownIcon,
  HandThumbUpIcon,
  LightBulbIcon,
} from "@heroicons/vue/24/outline"

import type { CardColumn } from "~/utils/types"

const props = defineProps<{
  column: CardColumn
  count: number
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
    class="px-4 py-3 border-b"
    :style="{ borderBottomColor: config.accentColor + '33', borderLeftColor: config.accentColor, borderLeftWidth: '2px', borderLeftStyle: 'solid' }"
  >
    <div class="flex items-center justify-between gap-3">
      <div class="inline-flex items-center gap-2 text-xs font-medium uppercase tracking-wide" :style="{ color: config.accentColor }">
        <component :is="config.icon" class="h-4 w-4" />
        {{ config.title }}
      </div>
      <span class="text-xs font-light" style="color: #52525b">{{ count }}</span>
    </div>
  </div>
</template>