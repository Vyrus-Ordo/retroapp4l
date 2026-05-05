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
  <header class="border-b border-gray-100 bg-white">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
      <NuxtLink class="text-lg font-bold tracking-tight text-brand-700" to="/">
        RetroApp 4L
      </NuxtLink>
      <nav class="flex items-center gap-4 text-sm text-gray-600">
        <NuxtLink class="rounded px-2 py-1 hover:bg-gray-50" to="/">Home</NuxtLink>
        <NuxtLink class="rounded px-2 py-1 hover:bg-gray-50" to="/join">Join via link</NuxtLink>
        <NuxtLink v-if="isAuthenticatedUser" class="rounded px-2 py-1 hover:bg-gray-50" to="/retro/create">New retro</NuxtLink>
        <NuxtLink v-if="isAuthenticatedUser" class="rounded px-2 py-1 hover:bg-gray-50" to="/history">History</NuxtLink>
        <template v-if="isAuthenticatedUser">
          <div class="inline-flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-sm font-semibold text-brand-700">
            {{ initials }}
          </div>
          <button
            class="rounded px-2 py-1 text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors"
            @click="handleLogout"
          >
            Sign out
          </button>
        </template>
      </nav>
    </div>
  </header>
</template>