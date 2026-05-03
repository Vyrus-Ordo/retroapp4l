<script setup lang="ts">
const authStore = useAuthStore()
authStore.init()

const initials = computed(() => {
  const name = authStore.user?.name ?? ''
  if (!name) return ''
  const parts = name.trim().split(' ')
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
})
</script>

<template>
  <header class="border-b border-slate-100 bg-white">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
      <p class="text-sm font-medium text-slate-600">
        <span class="font-semibold text-slate-900">RetroApp 4L</span>
        <span class="mx-2 text-slate-300">›</span>
        <span>Dashboard</span>
      </p>
      <div v-if="authStore.user" class="inline-flex h-9 w-9 items-center justify-center rounded-full bg-brand-100 text-sm font-semibold text-brand-700">
        {{ initials }}
      </div>
    </div>
  </header>
</template>
