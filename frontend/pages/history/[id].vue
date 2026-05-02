<script setup lang="ts">
const route = useRoute()
const retroStore = useRetroStore()

onMounted(async () => {
  await retroStore.fetchHistoryDetail(String(route.params.id))
})

const detail = computed(() => retroStore.historyDetail)
</script>

<template>
  <AppShell>
    <section v-if="detail" class="space-y-6">
      <div class="panel p-6 lg:p-8">
        <p class="text-xs font-semibold text-brand-500">History detail</p>
        <h1 class="mt-3 text-2xl font-semibold text-slate-900">{{ detail.title }}</h1>
        <p class="mt-2 text-sm text-slate-600">{{ detail.sprint_name || 'No sprint' }} · {{ detail.team_key }} · {{ detail.facilitator_name }}</p>
      </div>

      <section v-if="detail.milestones.length" class="panel p-6 lg:p-8">
        <h2 class="text-lg font-semibold text-slate-900">Milestones</h2>
        <div class="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <MilestoneCard v-for="milestone in detail.milestones" :key="milestone.id" :milestone="milestone" />
        </div>
      </section>

      <section class="panel p-6 lg:p-8">
        <h2 class="text-lg font-semibold text-slate-900">Cards and action items</h2>
        <div class="mt-6 grid gap-6 xl:grid-cols-2">
          <div class="space-y-4">
            <RetroCard v-for="card in detail.cards" :key="card.id" :card="card" />
          </div>
          <div class="space-y-3 rounded-xl bg-slate-50 p-4">
            <div v-for="item in detail.action_items" :key="item.id" class="rounded-lg border border-slate-100 bg-white p-4">
              <p class="text-sm font-medium text-slate-900">{{ item.description }}</p>
              <p class="mt-2 text-xs text-slate-500">{{ item.assignee_name || 'Unassigned' }} · {{ item.status }}</p>
            </div>
          </div>
        </div>
      </section>
    </section>
  </AppShell>
</template>