<script setup lang="ts">
import { ArrowRightCircleIcon, ViewfinderCircleIcon } from "@heroicons/vue/24/outline"

import type { Card, DiscussionFocusPayload } from "~/utils/types"

defineProps<{
  focus: DiscussionFocusPayload | null
  queue: Card[]
  facilitator?: boolean
}>()

defineEmits<{
  next: []
}>()
</script>

<template>
  <section class="panel p-6">
    <div class="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-brand-500">
      <ViewfinderCircleIcon class="h-5 w-5" />
      In focus
    </div>

    <div class="mt-4 space-y-2" v-if="focus">
      <p class="text-sm font-medium text-slate-600">{{ focus.column }}</p>
      <h3 class="text-lg font-semibold leading-6 text-slate-900">{{ focus.content }}</h3>
      <p class="text-sm text-brand-500">{{ focus.vote_count }} votes</p>
    </div>
    <p v-else class="mt-4 text-sm text-slate-500">Pick a card to start discussion.</p>

    <div class="mt-6 border-t border-slate-100 pt-4">
      <p class="text-sm font-medium text-slate-900">Up next</p>
      <ul class="mt-3 space-y-2 text-sm text-slate-600">
        <li v-for="card in queue.slice(0, 3)" :key="card.id">{{ card.column }} — {{ card.content }} ({{ card.vote_count }})</li>
      </ul>
      <button v-if="facilitator" class="button-primary mt-4" type="button" @click="$emit('next')">
        <ArrowRightCircleIcon class="mr-2 h-5 w-5" />
        Next card
      </button>
    </div>
  </section>
</template>