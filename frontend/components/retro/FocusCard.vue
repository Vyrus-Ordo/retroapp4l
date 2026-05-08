<template>
  <div class="focus-card rounded-xl border border-[#00f2ff]/20 p-6 flex flex-col gap-3" style="background: rgba(0,242,255,0.04)">
    <div class="flex items-center gap-2 mb-2">
      <span class="mdi mdi-star text-xl text-[#00f2ff]/60" />
      <span class="font-light text-lg text-[#00f2ff]">In focus</span>
    </div>
    <div class="text-base text-zinc-200 font-light">{{ card.text }}</div>
    <div class="flex gap-2 mt-2">
      <span class="text-xs text-zinc-600">{{ card.is_anonymous ? 'Anonymous' : (card.author_display || card.author || 'Participant') }}</span>
      <VoteBadge :count="card.votes || 0" :active="true" />
    </div>
    <div class="flex gap-2 mt-4 justify-end">
      <button v-if="canNext" class="button-primary" @click="$emit('next')">Next card</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import VoteBadge from './VoteBadge.vue'
const props = defineProps({
  card: Object,
  canNext: Boolean
})
</script>

<style scoped>
.focus-card {
  min-width: 260px;
}
</style>
