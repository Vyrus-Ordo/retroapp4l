<script setup lang="ts">
const { authStore } = useAuth()
const retroStore = useRetroStore()

const userFirstName = computed(() => authStore.user?.name?.split(' ')[0] ?? '')

const activeSession = computed(() =>
  retroStore.retrospectives.find((r) => r.status !== 'closed') ?? null,
)

const closedRetros = computed(() =>
  retroStore.retrospectives.filter((r) => r.status === 'closed'),
)

const teamKey = computed(() => retroStore.retrospectives[0]?.team_key ?? null)

const lastRetroRelativeTime = computed(() => {
  const latest = retroStore.retrospectives.find((r) => r.status === 'closed')
  if (!latest) return null
  const diffMs = Date.now() - new Date(latest.created_at).getTime()
  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  if (days === 0) return 'today'
  if (days === 1) return 'yesterday'
  return `${days} days ago`
})

onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.isGuestSession) {
    try {
      await retroStore.fetchDashboard()
    } catch {
      // do not break on failed fetch
    }
  }
})
</script>

<template>
  <div class="flex min-h-screen flex-col bg-slate-50">
    <Header />

    <main class="mx-auto w-full max-w-7xl flex-1 px-6 py-8 lg:px-8">
      <div class="flex flex-col gap-8">
        <!-- Top section -->
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div class="flex flex-col gap-1">
            <h1 class="text-2xl font-semibold text-slate-900">Hello, {{ userFirstName }}</h1>
            <p class="text-base text-slate-600">
              <template v-if="teamKey">
                Team {{ teamKey }}<template v-if="lastRetroRelativeTime"> · Last retro {{ lastRetroRelativeTime }}</template>
              </template>
            </p>
          </div>
          <div class="flex flex-col gap-3 sm:flex-row">
            <NuxtLink
              to="/join"
              class="inline-flex items-center justify-center rounded-lg border border-brand-500 px-4 py-2 text-sm font-medium text-brand-500 hover:bg-brand-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black"
            >
              Enter via link
            </NuxtLink>
            <NuxtLink
              v-if="!authStore.isGuestSession"
              to="/retro/create"
              class="inline-flex items-center justify-center rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600 active:bg-brand-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black"
            >
              New retrospective
            </NuxtLink>
          </div>
        </div>

        <!-- Active session -->
        <ActiveSessionCard v-if="activeSession" :retro="activeSession" />

        <!-- History table -->
        <HistoryTable v-if="!authStore.isGuestSession" :retros="closedRetros" />
      </div>
    </main>

    <ToastContainer />
  </div>
</template>