<script setup lang="ts">
import { ArrowRightCircleIcon, ViewfinderCircleIcon, PlusIcon } from "@heroicons/vue/24/outline"

import type { Card, DiscussionFocusPayload } from "~/utils/types"

defineProps<{
  focus: DiscussionFocusPayload | null
  queue: Card[]
  facilitator?: boolean
}>()

defineEmits<{
  next: []
  "new-action": []
}>()
</script>

<template>
  <section class="panel p-6">
    <div class="inline-flex items-center gap-2 text-xs font-light uppercase tracking-[0.2em] text-[#00f2ff]/70">
      <ViewfinderCircleIcon class="h-5 w-5" />
      In focus
    </div>

    <div v-if="focus" class="mt-4 space-y-2">
      <p class="text-xs font-light uppercase tracking-wide text-zinc-600">{{ focus.column }}</p>
      <h3 class="text-lg font-light leading-6 text-white">{{ focus.content }}</h3>
      <p class="text-sm text-[#00f2ff]/70">{{ focus.vote_count }} votes</p>
    </div>
    <p v-else class="mt-4 text-sm text-zinc-600">Pick a card to start discussion.</p>

    <div class="mt-6 border-t border-white/8 pt-4">
      <p class="text-sm font-light text-zinc-400">Up next</p>
      <ul class="mt-3 space-y-2 text-sm text-zinc-600">
        <li v-for="card in queue.slice(0, 3)" :key="card.id">{{ card.column }} — {{ card.content }} ({{ card.vote_count }})</li>
      </ul>
      <div v-if="facilitator" class="mt-4 flex gap-2">
        <button class="button-primary flex-1 px-2" type="button" @click="$emit('next')">
          <ArrowRightCircleIcon class="mr-1.5 h-5 w-5 shrink-0" />
          Next card
        </button>
        <button class="button-secondary flex-1 px-2" type="button" @click="$emit('new-action')">
          <PlusIcon class="mr-1.5 h-5 w-5 shrink-0" />
          New action
        </button>
      </div>
    </div>
  </section>
</template>