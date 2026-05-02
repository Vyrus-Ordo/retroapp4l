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
  if (props.column === "loved") {
    return { title: "Liked", className: "bg-success-600", icon: HandThumbUpIcon }
  }
  if (props.column === "loathed") {
    return { title: "Loathed", className: "bg-warning-500", icon: HandThumbDownIcon }
  }
  if (props.column === "longed") {
    return { title: "Longed for", className: "bg-brand-500", icon: ClockIcon }
  }
  return { title: "Learned", className: "bg-slate-600", icon: LightBulbIcon }
})
</script>

<template>
  <div :class="config.className" class="rounded-t-lg px-4 py-2">
    <div class="flex items-center justify-between gap-3">
      <div class="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-white">
        <component :is="config.icon" class="h-5 w-5" />
        {{ config.title }}
      </div>
      <span class="text-xs font-normal text-white/75">{{ count }}</span>
    </div>
  </div>
</template>