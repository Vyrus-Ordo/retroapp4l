defineProps<{
defineEmits<{
<template>
  <div class="retro-card bg-gray-50 rounded-lg border border-gray-200 p-3 flex flex-col gap-2 shadow-sm">
    <div class="flex items-center gap-2">
      <span v-if="card.author" class="mdi mdi-account-circle text-lg text-gray-400" />
      <span class="text-xs text-gray-500">{{ card.author || 'Anônimo' }}</span>
    </div>
    <div class="text-base text-gray-900 font-medium">{{ card.text }}</div>
    <div class="flex gap-2 mt-1">
      <button v-if="card.canEdit" class="button-tertiary text-xs" @click="$emit('action', { type: 'edit', card })">Editar</button>
      <button v-if="card.canDelete" class="button-tertiary text-xs text-danger-500" @click="$emit('action', { type: 'delete', card })">Excluir</button>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  card: Object
})
</script>

<style scoped>
.retro-card {
  transition: box-shadow 0.2s;
}
.retro-card:hover {
  box-shadow: 0 2px 8px 0 var(--ds-shadow-md);
}
</style>

    <div class="mt-4 flex flex-wrap items-center gap-3 text-xs text-slate-500">
      <button v-if="canEdit" class="inline-flex items-center hover:text-slate-900" type="button" @click="$emit('edit', card)">
        <PencilIcon class="mr-1 h-4 w-4" />
        Edit
      </button>
      <button v-if="canDelete" class="inline-flex items-center hover:text-danger-500" type="button" @click="$emit('delete', card)">
        <TrashIcon class="mr-1 h-4 w-4" />
        Delete
      </button>
      <button
        v-if="canVote"
        :class="voteActive ? 'text-brand-500' : 'text-slate-500 hover:text-brand-500'"
        :disabled="voteDisabled"
        class="inline-flex items-center disabled:text-slate-300"
        type="button"
        @click="$emit('vote', card)"
      >
        <VoteBadge :active="voteActive" :count="card.vote_count" />
      </button>
      <span v-else class="text-brand-500 text-xs font-semibold">{{ card.vote_count }} votes</span>
    </div>
  </article>
</template>