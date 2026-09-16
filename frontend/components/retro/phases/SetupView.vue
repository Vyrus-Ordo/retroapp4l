<template>
  <div class="flex flex-col gap-6">
    <template v-if="isFacilitator">
      <SprintSummaryForm
        v-if="current?.id"
        :retroId="current.id"
        :initialData="retroStore.sprintSummary"
      />

      <div class="panel p-6 flex flex-col gap-4">
        <div class="flex items-center justify-between gap-4">
          <h2 class="text-sm font-medium text-zinc-400 uppercase tracking-[0.2em]">Milestones</h2>
          <button
            class="button-primary py-1.5 text-sm"
            :disabled="!hasSummary"
            @click="$emit('add-milestone')"
          >
            + Add Milestone
          </button>
        </div>
        <p v-if="!hasSummary" class="text-xs text-zinc-500">
          ⚠ Preencha o Sprint Summary para adicionar milestones.
        </p>
        <div v-if="current?.milestones?.length" class="flex flex-col gap-2">
          <MilestoneCard v-for="m in current.milestones" :key="m.id" :milestone="m" />
        </div>
        <div v-else class="rounded-lg border border-dashed border-white/10 p-4 text-sm text-zinc-600">
          No milestones registered.
        </div>
      </div>

      <div class="flex justify-center">
        <button class="button-primary" @click="$emit('advance-phase')">Go to Lobby</button>
      </div>
    </template>

    <div v-else class="flex flex-col items-center justify-center min-h-[60vh] gap-6">
      <span class="mdi mdi-cog-outline animate-spin text-5xl text-[#00f2ff]/60" />
      <h1 class="text-2xl font-light text-white">Preparing session...</h1>
      <p class="text-zinc-500">{{ current?.title }}</p>
      <div class="flex flex-col items-center gap-1 mt-4">
        <span class="text-sm text-zinc-600">Waiting for the facilitator to start</span>
        <div class="flex items-center gap-2 mt-2">
          <AvatarCircle v-for="p in participants" :key="p.id" :name="p.user_name" size="36" color="brand" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AvatarCircle from '~/components/layout/AvatarCircle.vue'
import MilestoneCard from '~/components/retro/MilestoneCard.vue'
import SprintSummaryForm from '~/components/forms/SprintSummaryForm.vue'

const props = defineProps({
  current: Object,
  isFacilitator: Boolean,
  participants: Array,
})

defineEmits(['advance-phase', 'add-milestone'])

const retroStore = useRetroStore()

const hasSummary = computed(() =>
  !!retroStore.sprintSummary && retroStore.sprintSummary.total_stories > 0,
)

onMounted(() => {
  if (props.current?.id) {
    retroStore.fetchSprintSummary(props.current.id)
  }
})
</script>

<style scoped>
.animate-spin {
  animation: spin 1.2s linear infinite;
}
@keyframes spin {
  100% { transform: rotate(360deg); }
}
</style>
