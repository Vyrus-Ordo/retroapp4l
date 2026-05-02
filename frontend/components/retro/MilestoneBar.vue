<script setup lang="ts">
import { FlagIcon } from "@heroicons/vue/24/outline"

import type { Milestone } from "~/utils/types"

defineProps<{
  milestones: Milestone[]
}>()
</script>

<template>
  <div class="milestone-bar bg-primary-50 border-b border-primary-200 px-8 py-2 flex gap-4 flex-wrap text-sm">
    <div v-for="milestone in milestones" :key="milestone.id" class="inline-flex items-center gap-2 text-primary-700">
      <span class="mdi mdi-flag-checkered text-primary-500 text-base" />
      <span>{{ milestone.title }}</span>
    </div>
  </div>
</template>

<style scoped>
.milestone-bar {
  min-height: 40px;
}
</style>