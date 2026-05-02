<script setup lang="ts">
const route = useRoute()
const { authStore } = useAuth()
</script>

<template>
  <AppShell>
    <section class="mx-auto max-w-2xl panel p-6 lg:p-8">
      <p class="text-xs font-semibold text-brand-500">Invite</p>
      <h1 class="mt-3 text-2xl font-semibold text-slate-900">Join a retrospective</h1>
      <p class="mt-2 text-sm text-slate-600">
        Invite token received: <span class="font-medium text-slate-900">{{ route.params.token }}</span>
      </p>
      <p class="mt-4 text-sm text-slate-600">
        The backend currently exposes invite tokens on session detail, but a dedicated invite-resolution endpoint is still pending. This screen preserves the invite route and directs authenticated users back to the workspace while that API gap remains open.
      </p>

      <div class="mt-6 flex flex-col gap-3 sm:flex-row">
        <NuxtLink class="button-primary" :to="authStore.isAuthenticated ? '/' : '/auth/login'">
          {{ authStore.isAuthenticated ? 'Go to dashboard' : 'Sign in to continue' }}
        </NuxtLink>
        <NuxtLink class="button-secondary" to="/retro/create">Create a new session</NuxtLink>
      </div>
    </section>
  </AppShell>
</template>