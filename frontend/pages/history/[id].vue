<script setup lang="ts">
import MilestoneCard from "~/components/retro/MilestoneCard.vue"
import RetroCard from "~/components/retro/RetroCard.vue"

const route = useRoute()
const retroStore = useRetroStore()
const pageError = ref<string | null>(null)

onMounted(async () => {
  try {
    await retroStore.fetchHistoryDetail(String(route.params.id))
  } catch (error) {
    pageError.value = error instanceof Error ? error.message : "Unable to load retrospective history."

    if (pageError.value === "Session expired. Please sign in again.") {
      await navigateTo(`/auth/login?redirect=${encodeURIComponent(route.fullPath)}`)
    }
  }
})

const detail = computed(() => retroStore.historyDetail)
</script>

<template>
  <AppShell>
    <section v-if="pageError" class="panel p-6 lg:p-8">
      <p class="text-xs font-light text-[#00f2ff]/70">History detail</p>
      <h1 class="mt-3 text-2xl font-light text-white">Unable to load retrospective</h1>
      <p class="mt-2 text-sm text-zinc-500">{{ pageError }}</p>
    </section>

    <section v-else-if="detail" class="space-y-6">
      <div class="panel p-6 lg:p-8">
        <p class="text-xs font-light text-[#00f2ff]/70">History detail</p>
        <h1 class="mt-3 text-2xl font-light text-white">{{ detail.title }}</h1>
        <p class="mt-2 text-sm text-zinc-500">{{ detail.sprint_name || 'No sprint' }} · {{ detail.team_key }} · {{ detail.facilitator_name }}</p>
      </div>

      <section v-if="detail.milestones.length" class="panel p-6 lg:p-8">
        <h2 class="text-lg font-light text-white">Milestones</h2>
        <div class="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <MilestoneCard v-for="milestone in detail.milestones" :key="milestone.id" :milestone="milestone" />
        </div>
      </section>

      <section class="panel p-6 lg:p-8">
        <h2 class="text-lg font-light text-white">Cards and action items</h2>
        <div class="mt-6 grid gap-6 xl:grid-cols-2">
          <div class="space-y-4">
            <RetroCard v-for="card in detail.cards" :key="card.id" :card="card" />
          </div>
          <div class="space-y-3 rounded-xl border border-white/8 p-4" style="background: rgba(255,255,255,0.03)">
            <div v-for="item in detail.action_items" :key="item.id" class="rounded-lg border border-white/8 p-4" style="background: rgba(255,255,255,0.04)">
              <p class="text-sm font-light text-zinc-200">{{ item.description }}</p>
              <p class="mt-2 text-xs text-zinc-600">{{ item.assignee_name || 'Unassigned' }} · {{ item.status }}</p>
            </div>
          </div>
        </div>
      </section>
    </section>

    <section v-else class="panel p-6 lg:p-8">
      <p class="text-xs font-light text-[#00f2ff]/70">History detail</p>
      <p class="mt-3 text-sm text-zinc-500">Loading retrospective...</p>
    </section>
  </AppShell>
</template>