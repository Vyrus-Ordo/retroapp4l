<script setup lang="ts">
import { ArrowRightOnRectangleIcon, ClockIcon } from "@heroicons/vue/24/outline"

defineProps<{
  phaseLabel?: string
  timerText?: string
}>()

const authStore = useAuthStore()

async function handleLogout() {
  await authStore.logout()
  await navigateTo("/auth/login")
}
</script>

<template>
  <header class="border-b border-slate-100 bg-white">
    <div class="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-4 lg:flex-row lg:items-center lg:justify-between lg:px-8">
      <div class="space-y-1">
        <NuxtLink class="text-lg font-semibold leading-6 text-slate-900" to="/">
          RetroApp 4L
        </NuxtLink>
        <p class="text-sm text-slate-600">
          Agile retrospective workspace with live board, action check, and history.
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <div
          v-if="phaseLabel || timerText"
          class="inline-flex items-center gap-2 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-sm text-slate-600"
        >
          <span v-if="phaseLabel" class="font-medium text-slate-900">{{ phaseLabel }}</span>
          <span v-if="timerText" class="inline-flex items-center gap-1">
            <ClockIcon class="h-4 w-4" />
            {{ timerText }}
          </span>
        </div>

        <nav class="flex items-center gap-2 text-sm text-slate-600">
          <NuxtLink class="rounded px-2 py-1 hover:bg-slate-100" to="/">Home</NuxtLink>
          <NuxtLink class="rounded px-2 py-1 hover:bg-slate-100" to="/retro/create">Create</NuxtLink>
          <NuxtLink class="rounded px-2 py-1 hover:bg-slate-100" to="/history">History</NuxtLink>
        </nav>

        <button
          v-if="authStore.isAuthenticated"
          class="button-secondary"
          type="button"
          @click="handleLogout"
        >
          <ArrowRightOnRectangleIcon class="mr-2 h-5 w-5" />
          Sign out
        </button>
      </div>
    </div>
  </header>
</template>