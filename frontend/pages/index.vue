<script setup lang="ts">
const { authStore } = useAuth()
const retroStore = useRetroStore()

// Exibe landing page para usuários não autenticados e guests (sem dashboard útil)
const showLanding = computed(() => !authStore.isAuthenticated || authStore.isGuestSession)

// --- Dados do dashboard (apenas para usuários autenticados não-guest) ---
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
  <!-- =========================================================
       LANDING PAGE — usuários anônimos e guests
       ========================================================= -->
  <template v-if="showLanding">
    <div class="flex min-h-screen flex-col bg-white">
      <Header />

      <!-- Hero Section -->
      <section
        class="relative flex flex-1 flex-col items-center justify-center overflow-hidden bg-gradient-to-br from-brand-50 via-white to-slate-50 px-6 py-24 text-center lg:px-8"
      >
        <!-- Decoração de fundo -->
        <div class="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
          <div class="absolute -right-40 -top-40 h-96 w-96 rounded-full bg-brand-100 opacity-40 blur-3xl" />
          <div class="absolute -bottom-40 -left-40 h-96 w-96 rounded-full bg-success-100 opacity-30 blur-3xl" />
        </div>

        <div class="relative max-w-3xl">
          <span
            class="mb-5 inline-block rounded-full bg-brand-100 px-4 py-1.5 text-sm font-semibold text-brand-700"
          >
            4L Methodology · Open Source · Free
          </span>

          <h1 class="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
            Agile retrospectives<br />
            <span class="text-brand-600">in real time</span>
          </h1>

          <p class="mt-6 text-lg leading-relaxed text-slate-600 sm:text-xl">
            Run structured 4L retrospectives —
            <strong class="font-semibold text-success-700">Liked</strong>,
            <strong class="font-semibold text-warning-600">Loathed</strong>,
            <strong class="font-semibold text-brand-600">Longed&nbsp;For</strong> and
            <strong class="font-semibold text-slate-700">Learned</strong>
            — with your team, in sync and hassle-free.
          </p>

          <div
            class="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row"
          >
            <NuxtLink
              to="/auth/register"
              class="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-7 py-3.5 text-base font-semibold text-white shadow-sm transition-colors hover:bg-brand-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600"
            >
              <!-- heroicon: play-circle -->
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="currentColor"
                class="h-5 w-5"
              >
                <path
                  fill-rule="evenodd"
                  d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm14.024-.983a1.125 1.125 0 010 1.966l-5.603 3.113A1.125 1.125 0 019 15.113V8.887c0-.857.921-1.4 1.671-.983l5.603 3.113z"
                  clip-rule="evenodd"
                />
              </svg>
              Create Retrospective
            </NuxtLink>

            <NuxtLink
              to="/join"
              class="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-7 py-3.5 text-base font-semibold text-slate-700 shadow-sm transition-colors hover:border-slate-400 hover:bg-slate-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400"
            >
              <!-- heroicon: link -->
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="h-5 w-5"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244"
                />
              </svg>
              Join via link
            </NuxtLink>
          </div>
        </div>
      </section>

      <!-- Features Section -->
      <section class="bg-white px-6 py-20 lg:px-8">
        <div class="mx-auto max-w-5xl">
          <h2 class="mb-3 text-center text-2xl font-bold text-slate-900 sm:text-3xl">
            Everything your team needs
          </h2>
          <p class="mb-14 text-center text-base text-slate-500">
            From the 4L board to action item tracking — no unnecessary integrations.
          </p>

          <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <!-- Feature 1: Colaboração em tempo real (WebSockets) -->
            <div
              class="flex flex-col gap-4 rounded-2xl border border-slate-100 bg-slate-50 p-7 transition-shadow hover:shadow-md"
            >
              <div
                class="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-100"
              >
                <!-- heroicon: bolt -->
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke-width="1.5"
                  stroke="currentColor"
                  class="h-6 w-6 text-brand-600"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"
                  />
                </svg>
              </div>
              <div>
                <h3 class="text-base font-semibold text-slate-900">
                  Real-time collaboration
                </h3>
                <p class="mt-2 text-sm leading-relaxed text-slate-500">
                  Shared board over WebSocket. All participants see cards and votes
                  instantly — no page refresh needed.
                </p>
              </div>
            </div>

            <!-- Feature 2: Cronômetro sincronizado (TimerDisplay) -->
            <div
              class="flex flex-col gap-4 rounded-2xl border border-slate-100 bg-slate-50 p-7 transition-shadow hover:shadow-md"
            >
              <div
                class="flex h-12 w-12 items-center justify-center rounded-xl bg-warning-100"
              >
                <!-- heroicon: clock -->
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke-width="1.5"
                  stroke="currentColor"
                  class="h-6 w-6 text-warning-600"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div>
                <h3 class="text-base font-semibold text-slate-900">
                  Synchronized timer
                </h3>
                <p class="mt-2 text-sm leading-relaxed text-slate-500">
                  Each phase has a configurable duration. The facilitator pauses and resumes — and
                  everyone sees the same countdown on screen.
                </p>
              </div>
            </div>

            <!-- Feature 3: Gestão de Action Items (ActionEditor) -->
            <div
              class="flex flex-col gap-4 rounded-2xl border border-slate-100 bg-slate-50 p-7 transition-shadow hover:shadow-md sm:col-span-2 lg:col-span-1"
            >
              <div
                class="flex h-12 w-12 items-center justify-center rounded-xl bg-success-100"
              >
                <!-- heroicon: check-circle -->
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke-width="1.5"
                  stroke="currentColor"
                  class="h-6 w-6 text-success-600"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div>
                <h3 class="text-base font-semibold text-slate-900">
                  Action Item Management
                </h3>
                <p class="mt-2 text-sm leading-relaxed text-slate-500">
                  Log action items with an owner and due date. In the next retro, the team
                  checks what was completed — closing the loop sprint by sprint.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <AppFooter />
    </div>
  </template>

  <!-- =========================================================
       DASHBOARD — usuários autenticados não-guest
       ========================================================= -->
  <template v-else>
    <AppShell>
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
              Join via link
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

        <!-- Sessão ativa -->
        <ActiveSessionCard v-if="activeSession" :retro="activeSession" />

        <!-- Histórico -->
        <HistoryTable v-if="!authStore.isGuestSession" :retros="closedRetros" />
      </div>
    </AppShell>
  </template>
</template>
