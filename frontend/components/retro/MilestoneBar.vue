<script setup lang="ts">
import { FlagIcon } from "@heroicons/vue/24/outline"

import type { Milestone } from "~/utils/types"

defineProps<{
  milestones: Milestone[]
}>()
</script>

<template>
  <div class="bg-slate-50 border-b border-slate-100 px-8 py-2 flex gap-4 flex-wrap text-sm">
    <div v-for="milestone in milestones" :key="milestone.id" class="inline-flex items-center gap-2 text-slate-600">
      <FlagIcon class="h-4 w-4 text-brand-500" />
      <span>{{ milestone.description }}</span>
    </div>
  </div>
</template>