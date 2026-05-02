<script setup lang="ts">
import { ArrowRightCircleIcon, PlusCircleIcon } from "@heroicons/vue/24/outline"

const { authStore } = useAuth()
const retroStore = useRetroStore()

const recentRetros = computed(() => retroStore.retrospectives.slice(0, 6))

onMounted(async () => {
  if (authStore.isAuthenticated) {
    await retroStore.fetchDashboard()
  }
})
</script>

<template>
  <AppShell>
    <section class="panel overflow-hidden">
      <div class="flex flex-col gap-8 border-b border-slate-100 bg-white px-6 py-8 lg:flex-row lg:items-end lg:justify-between lg:px-8">
        <div class="max-w-3xl space-y-4">
          <p class="inline-flex rounded bg-brand-50 px-2 py-1 text-xs font-semibold text-brand-500">
            Sprint 6 frontend delivery
          </p>
          <div class="space-y-3">
            <h1 class="text-2xl font-semibold leading-8 text-slate-900">
              Run your full retrospective flow from a single Nuxt workspace.
            </h1>
            <p class="max-w-2xl text-base leading-6 text-slate-600">
              Authentication, setup, lobby, board phases, actions, and history are now organized around the PRD design system.
            </p>
          </div>
        </div>

        <div class="flex flex-col gap-3 sm:flex-row">
          <NuxtLink class="button-primary" to="/retro/create">
            <PlusCircleIcon class="mr-2 h-5 w-5" />
            Create retrospective
          </NuxtLink>
          <NuxtLink class="button-secondary" :to="authStore.isAuthenticated ? '/history' : '/auth/login'">
            <ArrowRightCircleIcon class="mr-2 h-5 w-5" />
            {{ authStore.isAuthenticated ? 'Open history' : 'Open workspace' }}
          </NuxtLink>
        </div>
      </div>

      <div class="grid gap-4 bg-slate-50 px-6 py-6 lg:grid-cols-3 lg:px-8">
        <article class="rounded-lg border border-slate-100 bg-white p-4 shadow-sm">
          <h2 class="text-lg font-semibold leading-6 text-slate-900">Design system</h2>
          <p class="mt-2 text-sm leading-5 text-slate-600">
            Tailwind semantic colors, Inter weights 400-700, spacing on a 4px scale, and the required interactive states.
          </p>
        </article>
        <article class="rounded-lg border border-slate-100 bg-white p-4 shadow-sm">
          <h2 class="text-lg font-semibold leading-6 text-slate-900">Realtime-ready</h2>
          <p class="mt-2 text-sm leading-5 text-slate-600">
            The app is prepared for authenticated session snapshots, timer sync events, and board updates through WebSocket.
          </p>
        </article>
        <article class="rounded-lg border border-slate-100 bg-white p-4 shadow-sm">
          <h2 class="text-lg font-semibold leading-6 text-slate-900">History insights</h2>
          <p class="mt-2 text-sm leading-5 text-slate-600">
            Closed retrospectives show cards, milestones, votes, and action item outcomes in a dedicated detail screen.
          </p>
        </article>
      </div>
    </section>

    <section v-if="authStore.isAuthenticated" class="mt-6 panel p-6 lg:p-8">
      <div class="flex items-center justify-between gap-4">
        <div>
          <h2 class="text-lg font-semibold text-slate-900">Recent retrospectives</h2>
          <p class="mt-1 text-sm text-slate-600">Sessions where you are the facilitator or a participant.</p>
        </div>
        <NuxtLink class="button-secondary" to="/history">View all history</NuxtLink>
      </div>

      <div class="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <NuxtLink
          v-for="retro in recentRetros"
          :key="retro.id"
          :to="`/retro/${retro.id}`"
          class="rounded-lg border border-slate-100 bg-slate-50 p-4 transition-colors duration-150 hover:bg-white"
        >
          <p class="text-xs font-semibold text-brand-500">{{ retro.status }}</p>
          <h3 class="mt-2 text-lg font-semibold text-slate-900">{{ retro.title }}</h3>
          <p class="mt-1 text-sm text-slate-600">{{ retro.sprint_name || 'No sprint name' }} · {{ retro.team_key }}</p>
          <p class="mt-3 text-xs text-slate-400">Facilitator: {{ retro.facilitator_name }}</p>
        </NuxtLink>
        <div v-if="!recentRetros.length" class="rounded-lg border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-500">
          No retrospectives yet. Create the first one to start the session flow.
        </div>
      </div>
    </section>
  </AppShell>
</template>