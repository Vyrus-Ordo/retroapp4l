<template>
  <div class="vote-controls flex items-center gap-2">
    <button class="button-secondary" :disabled="disabled" @click="$emit('vote', -1)"><span class="mdi mdi-minus" /></button>
    <VoteBadge :count="votes" :active="active" />
    <button class="button-secondary" :disabled="disabled" @click="$emit('vote', 1)"><span class="mdi mdi-plus" /></button>
  </div>
</template>

<script setup lang="ts">
import VoteBadge from './VoteBadge.vue'
const props = defineProps({
  votes: Number,
  active: Boolean,
  disabled: Boolean
})
</script>
