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
          <p class="text-xs font-light text-[#00f2ff]/70">History</p>
          <h1 class="mt-3 text-2xl font-light text-white">Closed retrospectives</h1>
        </div>
      </div>

      <div class="mt-6 space-y-4">
        <NuxtLink
          v-for="item in retroStore.history"
          :key="item.id"
          :to="`/history/${item.id}`"
          class="block rounded-lg border border-white/10 p-4 transition-all duration-150 hover:border-[#00f2ff]/25"
          style="background: rgba(255,255,255,0.03)"
        >
          <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-lg font-light text-white">{{ item.title }}</h2>
              <p class="mt-1 text-sm text-zinc-500">{{ item.sprint_name || 'No sprint' }} · {{ item.team_key }}</p>
            </div>
            <div class="text-sm text-zinc-600">
              {{ item.cards_count }} cards · {{ item.action_items_count }} actions · {{ new Date(item.closed_at).toLocaleString() }}
            </div>
          </div>
        </NuxtLink>

        <div v-if="!retroStore.history.length" class="rounded-lg border border-dashed border-white/10 p-6 text-sm text-zinc-600">
          No closed retrospectives available yet.
        </div>
      </div>
    </section>
  </AppShell>
</template>