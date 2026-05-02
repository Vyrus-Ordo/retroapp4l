<script setup lang="ts">
import { FlagIcon } from "@heroicons/vue/24/outline"

import type { Milestone } from "~/utils/types"

defineProps<{
  milestone: Milestone
}>()
</script>

<template>
  <article class="bg-white border border-slate-100 rounded-lg p-4">
    <p class="inline-flex items-center text-xs font-semibold text-brand-500">
      <FlagIcon class="mr-2 h-4 w-4" />
      {{ milestone.category }}
    </p>
    <p class="mt-3 text-sm font-medium text-slate-900">{{ milestone.description }}</p>
    <p class="mt-3 text-xs text-slate-400">{{ milestone.author_name }} · {{ new Date(milestone.created_at).toLocaleString() }}</p>
  </article>
</template>