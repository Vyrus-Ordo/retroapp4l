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
    <div class="min-h-screen bg-[#050505] font-['JetBrains_Mono',_'Poppins',_sans-serif] text-white">

      <!-- ── Hero Section ── -->
      <section class="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-6 py-24 text-center">
        <!-- Imagem de fundo com overlay escuro -->
        <div class="absolute inset-0" aria-hidden="true">
          <img
            src="/img/board_jedi.png"
            alt=""
            class="h-full w-full object-cover object-center"
            fetchpriority="high"
          />
          <div class="absolute inset-0 bg-[#050505]/80" />
        </div>

        <!-- Brilho de acento no topo -->
        <div
          class="pointer-events-none absolute left-1/2 top-0 h-72 w-[600px] -translate-x-1/2 rounded-full bg-[#00f2ff]/8 blur-3xl"
          aria-hidden="true"
        />

        <div class="relative z-10 max-w-3xl">
          <p class="mb-6 text-xs font-light uppercase tracking-[0.3em] text-[#00f2ff]/70">
            Framework 4L · Open Source · Real-time
          </p>

          <h1 class="text-4xl font-light leading-tight tracking-wider text-white sm:text-5xl lg:text-6xl">
            Retrospectives with Traceability.<br />
            <span class="font-semibold text-[#00f2ff]" style="text-shadow: 0 0 28px rgba(0,242,255,0.5)">
              No Noise.
            </span>
          </h1>

          <p class="mx-auto mt-8 max-w-xl text-base leading-relaxed tracking-wide text-slate-400 sm:text-lg">
            Turn feedback into real execution with the 4L framework.
            Built for teams that don't like wasting time.
          </p>

          <div class="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <!-- CTA Primário -->
            <NuxtLink
              to="/auth/register"
              class="inline-flex items-center gap-2 rounded-md bg-[#00f2ff] px-8 py-3.5 text-sm font-semibold tracking-wider text-[#050505] transition-all duration-200 hover:brightness-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#00f2ff] focus-visible:ring-offset-2 focus-visible:ring-offset-[#050505]"
              style="box-shadow: 0 0 24px rgba(0,242,255,0.45)"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-4 w-4" aria-hidden="true">
                <path fill-rule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm14.024-.983a1.125 1.125 0 010 1.966l-5.603 3.113A1.125 1.125 0 019 15.113V8.887c0-.857.921-1.4 1.671-.983l5.603 3.113z" clip-rule="evenodd" />
              </svg>
              Start a Session
            </NuxtLink>

            <!-- CTA Secondary -->
            <a
              href="https://github.com/diniz-prj/retroapp4l"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center gap-2 rounded-md border border-[#00f2ff]/40 px-8 py-3.5 text-sm font-semibold tracking-wider text-[#00f2ff] transition-all duration-200 hover:border-[#00f2ff]/80 hover:bg-[#00f2ff]/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#00f2ff] focus-visible:ring-offset-2 focus-visible:ring-offset-[#050505]"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-4 w-4" aria-hidden="true">
                <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
              </svg>
              View on GitHub
            </a>
          </div>

          <!-- Login link -->
          <p class="mt-6 text-xs tracking-wide text-slate-600">
            Already have an account?
            <NuxtLink to="/auth/login" class="text-[#00f2ff]/80 underline-offset-2 hover:text-[#00f2ff] hover:underline">Sign in</NuxtLink>
          </p>
        </div>

        <!-- Indicador de scroll -->
        <div class="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce" aria-hidden="true">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1" stroke="currentColor" class="h-5 w-5 text-[#00f2ff]/40">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
          </svg>
        </div>
      </section>

      <!-- ── The 4L Framework Section ── -->
      <section class="px-6 py-24 lg:px-8">
        <div class="mx-auto max-w-6xl">
          <p class="mb-3 text-center text-xs font-light uppercase tracking-[0.3em] text-[#00f2ff]/70">
            The Method
          </p>
          <h2 class="mb-4 text-center text-2xl font-light tracking-widest text-white sm:text-3xl">
            The 4L Framework
          </h2>
          <p class="mb-16 text-center text-sm tracking-wide text-slate-500">
            Four dimensions. One structured, executable retrospective.
          </p>

          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <!-- Liked -->
            <div class="flex flex-col gap-5 rounded-lg border border-white/10 bg-white/[0.04] p-6 backdrop-blur-sm transition-all duration-200 hover:border-[#00f2ff]/50 hover:bg-white/[0.07]">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1" stroke="#00f2ff" class="h-8 w-8 shrink-0" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6.633 10.5c.806 0 1.533-.446 2.031-1.08a9.041 9.041 0 012.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 00.322-1.672V3a.75.75 0 01.75-.75A2.25 2.25 0 0116.5 4.5c0 1.152-.26 2.243-.723 3.218-.266.558.107 1.282.725 1.282h3.126c1.026 0 1.945.694 2.054 1.715.045.422.068.85.068 1.285a11.95 11.95 0 01-2.649 7.521c-.388.482-.987.729-1.605.729H13.48c-.483 0-.964-.078-1.423-.23l-3.114-1.04a4.501 4.501 0 00-1.423-.23H5.904M14.25 9h2.25M5.904 18.75c.083.205.173.405.27.602.197.4-.078.898-.523.898h-.908c-.889 0-1.713-.518-1.972-1.368a12 12 0 01-.521-3.507c0-1.553.295-3.036.831-4.398C3.387 10.203 4.167 9.75 5 9.75h1.053c.472 0 .745.556.5.96a8.958 8.958 0 00-1.302 4.665c0 1.194.232 2.333.654 3.375z" />
              </svg>
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-[#00f2ff]">Liked</p>
                <h3 class="mt-1 text-base font-medium text-white">What Worked</h3>
                <p class="mt-2 text-sm leading-relaxed text-slate-500">What went well and should be preserved in the next cycle.</p>
              </div>
            </div>

            <!-- Learned -->
            <div class="flex flex-col gap-5 rounded-lg border border-white/10 bg-white/[0.04] p-6 backdrop-blur-sm transition-all duration-200 hover:border-[#00f2ff]/50 hover:bg-white/[0.07]">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1" stroke="#00f2ff" class="h-8 w-8 shrink-0" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5" />
              </svg>
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-[#00f2ff]">Learned</p>
                <h3 class="mt-1 text-base font-medium text-white">Knowledge Gained</h3>
                <p class="mt-2 text-sm leading-relaxed text-slate-500">Technical and process learnings the team accumulated during the sprint.</p>
              </div>
            </div>

            <!-- Lacked -->
            <div class="flex flex-col gap-5 rounded-lg border border-white/10 bg-white/[0.04] p-6 backdrop-blur-sm transition-all duration-200 hover:border-[#00f2ff]/50 hover:bg-white/[0.07]">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1" stroke="#00f2ff" class="h-8 w-8 shrink-0" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-[#00f2ff]">Lacked</p>
                <h3 class="mt-1 text-base font-medium text-white">Bottlenecks</h3>
                <p class="mt-2 text-sm leading-relaxed text-slate-500">Blockers and gaps that prevented the team from delivering more.</p>
              </div>
            </div>

            <!-- Longed For -->
            <div class="flex flex-col gap-5 rounded-lg border border-white/10 bg-white/[0.04] p-6 backdrop-blur-sm transition-all duration-200 hover:border-[#00f2ff]/50 hover:bg-white/[0.07]">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1" stroke="#00f2ff" class="h-8 w-8 shrink-0" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.59 14.37a6 6 0 01-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 006.16-12.12A14.98 14.98 0 009.631 8.41m5.96 5.96a14.926 14.926 0 01-5.841 2.58m-.119-8.54a6 6 0 00-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 00-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 01-2.448-2.448 14.9 14.9 0 01.06-.312m-2.24 2.39a4.493 4.493 0 00-1.757 4.306 4.493 4.493 0 004.306-1.758M16.5 9a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
              </svg>
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-[#00f2ff]">Longed For</p>
                <h3 class="mt-1 text-base font-medium text-white">Aspirations</h3>
                <p class="mt-2 text-sm leading-relaxed text-slate-500">What the team wishes to achieve or implement in the next cycle.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ── Technical Edge Section ── -->
      <section class="border-y border-white/10 px-6 py-20 lg:px-8">
        <div class="mx-auto max-w-3xl text-center">
          <p class="mb-3 text-xs font-light uppercase tracking-[0.3em] text-[#00f2ff]/70">
            Technical Edge
          </p>
          <h2 class="text-xl font-light leading-relaxed tracking-widest text-white sm:text-2xl">
            The bridge between cycles
          </h2>
          <p class="mt-6 text-base leading-relaxed tracking-wide text-slate-400">
            The only app that integrates the review of
            <strong class="font-semibold text-white">previous sprint Action Items</strong>
            into the new retrospective flow — closing the loop without spreadsheets, sticky notes, or noise.
          </p>
        </div>
      </section>

      <!-- ── Tech Stack Footer ── -->
      <footer class="px-6 py-12 lg:px-8">
        <div class="mx-auto flex max-w-6xl flex-col items-center gap-6">
          <div class="flex flex-wrap items-center justify-center gap-2">
            <span class="rounded border border-white/10 px-3 py-1 text-xs tracking-widest text-slate-500">Open Source</span>
            <span class="text-white/15" aria-hidden="true">|</span>
            <span class="rounded border border-white/10 px-3 py-1 text-xs tracking-widest text-slate-500">MIT License</span>
            <span class="text-white/15" aria-hidden="true">|</span>
            <span class="rounded border border-white/10 px-3 py-1 text-xs tracking-widest text-slate-500">Nuxt 3 + Django</span>
            <span class="text-white/15" aria-hidden="true">|</span>
            <span class="rounded border border-white/10 px-3 py-1 text-xs tracking-widest text-slate-500">Real-time WebSockets</span>
          </div>
          <p class="text-xs tracking-wider text-slate-700">© 2026 <span class="text-[#00f2ff]/70">RetroApp 4L</span>. By <strong class="text-[#00f2ff]/70">Vyrus Ordo</strong>. All rights reserved.</p>
        </div>
      </footer>
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
