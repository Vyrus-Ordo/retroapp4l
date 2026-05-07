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
  <header class="sticky top-0 z-50 border-b border-[#00f2ff]/10 bg-[#050505]/85 backdrop-blur-md">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
      <!-- LEFT: logo -->
      <NuxtLink
        class="font-light tracking-[0.15em] text-[#00f2ff] uppercase"
        style="font-family: 'JetBrains Mono', monospace; font-size: 1rem;"
        to="/"
      >
        RetroApp 4L
      </NuxtLink>

      <!-- RIGHT: navegação -->
      <nav class="flex items-center gap-1 text-sm text-zinc-400">
        <NuxtLink class="rounded-md px-3 py-2 font-light transition-colors hover:text-white" to="/">Home</NuxtLink>
        <NuxtLink class="rounded-md px-3 py-2 font-light transition-colors hover:text-white" to="/join">Join via link</NuxtLink>
        <NuxtLink v-if="isAuthenticatedUser" class="rounded-md px-3 py-2 font-light transition-colors hover:text-white" to="/retro/create">New retro</NuxtLink>
        <NuxtLink v-if="isAuthenticatedUser" class="rounded-md px-3 py-2 font-light transition-colors hover:text-white" to="/history">History</NuxtLink>
        <template v-if="isAuthenticatedUser">
          <div class="ml-2 inline-flex h-8 w-8 items-center justify-center rounded-full border border-[#00f2ff]/30 text-xs font-semibold text-[#00f2ff]">
            {{ initials }}
          </div>
          <button
            class="rounded-md px-3 py-2 font-light text-zinc-400 transition-colors hover:text-white"
            @click="handleLogout"
          >
            Logout
          </button>
        </template>
      </nav>
    </div>
  </header>
</template>