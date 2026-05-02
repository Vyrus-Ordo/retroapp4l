<script setup lang="ts">
const retroStore = useRetroStore()

onMounted(async () => {
  await retroStore.fetchHistory()
})
</script>

<template>
  <AppShell>
    <section class="panel p-6 lg:p-8">
      <div class="flex items-center justify-between gap-4">
        <div>
          <p class="text-xs font-semibold text-brand-500">History</p>
          <h1 class="mt-3 text-2xl font-semibold text-slate-900">Closed retrospectives</h1>
        </div>
      </div>

      <div class="mt-6 space-y-4">
        <NuxtLink
          v-for="item in retroStore.history"
          :key="item.id"
          :to="`/history/${item.id}`"
          class="block rounded-lg border border-slate-100 bg-slate-50 p-4 transition-colors duration-150 hover:bg-white"
        >
          <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-lg font-semibold text-slate-900">{{ item.title }}</h2>
              <p class="mt-1 text-sm text-slate-600">{{ item.sprint_name || 'No sprint' }} · {{ item.team_key }}</p>
            </div>
            <div class="text-sm text-slate-500">
              {{ item.cards_count }} cards · {{ item.action_items_count }} actions · {{ new Date(item.closed_at).toLocaleString() }}
            </div>
          </div>
        </NuxtLink>

        <div v-if="!retroStore.history.length" class="rounded-lg border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-500">
          No closed retrospectives available yet.
        </div>
      </div>
    </section>
  </AppShell>
</template>