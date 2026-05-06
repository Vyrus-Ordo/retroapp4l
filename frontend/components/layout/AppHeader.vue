<script setup lang="ts">
const authStore = useAuthStore()
authStore.init()

const router = useRouter()

const isGuestSession = computed(() => authStore.isGuestSession)
const isAuthenticatedUser = computed(() => authStore.isAuthenticated && !authStore.isGuestSession)

const initials = computed(() => {
  const name = authStore.user?.name ?? ''
  if (!name) return ''
  const parts = name.trim().split(' ')
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
})

async function handleLogout() {
  await authStore.logout()
  router.push('/auth/login')
}
</script>

<template>
  <header class="sticky top-0 z-50 border-b border-slate-200 bg-white/90 backdrop-blur-md">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
      <!-- LEFT: logo -->
      <NuxtLink
        class="font-bold tracking-tight text-brand-600"
        style="font-family: 'Inter', sans-serif; font-size: 1.25rem; font-weight: 700"
        to="/"
      >
        RetroApp 4L
      </NuxtLink>

      <!-- RIGHT: navegação -->
      <nav class="flex items-center gap-1 text-sm text-slate-600">
        <NuxtLink class="rounded-md px-3 py-2 font-medium transition-colors hover:bg-slate-100 hover:text-slate-900" to="/">Home</NuxtLink>
        <NuxtLink class="rounded-md px-3 py-2 font-medium transition-colors hover:bg-slate-100 hover:text-slate-900" to="/join">Join via link</NuxtLink>
        <NuxtLink v-if="isAuthenticatedUser" class="rounded-md px-3 py-2 font-medium transition-colors hover:bg-slate-100 hover:text-slate-900" to="/retro/create">New retro</NuxtLink>
        <NuxtLink v-if="isAuthenticatedUser" class="rounded-md px-3 py-2 font-medium transition-colors hover:bg-slate-100 hover:text-slate-900" to="/history">History</NuxtLink>
        <template v-if="isAuthenticatedUser">
          <div class="ml-2 inline-flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-sm font-semibold text-brand-700">
            {{ initials }}
          </div>
          <button
            class="rounded-md px-3 py-2 font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900"
            @click="handleLogout"
          >
            Logout
          </button>
        </template>
      </nav>
    </div>
  </header>
</template>