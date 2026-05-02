<script setup lang="ts">
const { authStore } = useAuth()
const retroStore = useRetroStore()
const isGuestSession = computed(() => authStore.isGuestSession)

const recentRetros = computed(() => retroStore.retrospectives.slice(0, 6))
const userFirstName = computed(() => authStore.user?.name?.split(' ')[0] || 'Usuário')

onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.isGuestSession) {
    try {
      await retroStore.fetchDashboard()
    } catch {
      // Invalid persisted auth should not break the public home screen.
    }
  }
})
</script>

<template>
  <AppShell>
    <section class="panel overflow-hidden">
      <div class="flex flex-col gap-8 border-b border-gray-100 bg-white px-6 py-8 lg:flex-row lg:items-end lg:justify-between lg:px-8">
        <div class="max-w-3xl space-y-3">
          <h1 class="text-2xl font-bold text-gray-900">Olá, {{ userFirstName }}</h1>
          <p class="max-w-2xl text-base text-gray-600">Bem-vindo ao RetroApp 4L — organize, registre e acompanhe suas retrospectivas ágeis de ponta a ponta.</p>
        </div>
        <div class="flex flex-col gap-3 sm:flex-row">
          <NuxtLink class="button-secondary" to="/join">Entrar via link</NuxtLink>
          <NuxtLink v-if="!isGuestSession" class="button-primary" to="/retro/create">Nova retrospectiva</NuxtLink>
        </div>
      </div>

      <div v-if="authStore.isAuthenticated && !isGuestSession && recentRetros.length" class="mt-6">
        <h2 class="text-base font-semibold text-gray-900 mb-2">Retro em andamento</h2>
        <div class="flex flex-col gap-3">
          <NuxtLink
            v-for="retro in recentRetros"
            :key="retro.id"
            :to="`/retro/${retro.id}`"
            class="rounded-lg border border-brand-200 bg-white p-4 flex items-center justify-between hover:bg-brand-50 transition"
          >
            <div>
              <h3 class="text-lg font-semibold text-gray-900">{{ retro.title }}</h3>
              <p class="text-xs text-gray-500">Sprint: {{ retro.sprint_name || '—' }} · Time: {{ retro.team_key }}</p>
            </div>
            <span class="inline-flex items-center gap-2">
              <span class="rounded-full bg-success-50 px-3 py-1 text-xs font-bold text-success-600">Em andamento</span>
              <span class="mdi mdi-chevron-right text-xl text-brand-500" />
            </span>
          </NuxtLink>
        </div>
      </div>

      <div v-if="!isGuestSession" class="mt-8">
        <h2 class="text-base font-semibold text-gray-900 mb-2">Histórico</h2>
        <div class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead>
              <tr class="bg-gray-50">
                <th class="px-3 py-2 text-left font-semibold text-gray-700">Sprint</th>
                <th class="px-3 py-2 text-left font-semibold text-gray-700">Título</th>
                <th class="px-3 py-2 text-left font-semibold text-gray-700">Data</th>
                <th class="px-3 py-2 text-left font-semibold text-gray-700">Status</th>
                <th class="px-3 py-2 text-left font-semibold text-gray-700">Ações</th>
                <th class="px-3 py-2 text-left font-semibold text-gray-700">Ver</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="retro in retroStore.retrospectives" :key="retro.id" class="border-b border-gray-100">
                <td class="px-3 py-2">{{ retro.sprint_name || '—' }}</td>
                <td class="px-3 py-2">{{ retro.title }}</td>
                <td class="px-3 py-2">{{ new Date(retro.created_at).toLocaleDateString('pt-BR') }}</td>
                <td class="px-3 py-2">
                  <span v-if="retro.status === 'closed'" class="inline-block rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-600">Encerrada</span>
                  <span v-else class="inline-block rounded-full bg-success-50 px-2 py-1 text-xs text-success-600">Em andamento</span>
                </td>
                <td class="px-3 py-2">{{ retro.actions_done || 0 }}/{{ retro.actions_total || 0 }}</td>
                <td class="px-3 py-2">
                  <NuxtLink :to="`/retro/${retro.id}`" class="text-brand-600 hover:underline">Ver</NuxtLink>
                </td>
              </tr>
              <tr v-if="!retroStore.retrospectives.length">
                <td colspan="6" class="text-center text-gray-400 py-6">Nenhuma retrospectiva encontrada.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </AppShell>
</template>