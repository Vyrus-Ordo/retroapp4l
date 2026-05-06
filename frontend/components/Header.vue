<script setup lang="ts">
const mobileMenuOpen = ref(false)
</script>

<template>
  <header class="sticky top-0 z-50 border-b border-slate-200 bg-white/90 backdrop-blur-md">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
      <!-- LEFT: logo -->
      <NuxtLink
        to="/"
        class="font-bold tracking-tight text-brand-600"
        style="font-family: 'Inter', sans-serif; font-size: 1.25rem; font-weight: 700"
      >
        RetroApp 4L
      </NuxtLink>

      <!-- RIGHT: navigation (desktop) / hamburger (mobile) -->
      <nav class="hidden items-center gap-1 md:flex">
        <NuxtLink
          to="/"
          class="rounded-md px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900"
        >
          Home
        </NuxtLink>
        <NuxtLink
          to="/join"
          class="rounded-md px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900"
        >
          Join via link
        </NuxtLink>
        <NuxtLink
          to="/auth/login"
          class="ml-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-brand-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600"
        >
          Login
        </NuxtLink>
      </nav>

      <!-- Mobile: hamburger (right) -->
      <button
        class="rounded-md p-2 text-slate-500 transition-colors hover:bg-slate-100 md:hidden"
        aria-label="Open navigation menu"
        @click="mobileMenuOpen = !mobileMenuOpen"
      >
        <!-- bars-3 -->
        <svg
          v-if="!mobileMenuOpen"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="h-6 w-6"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
        </svg>
        <!-- x-mark -->
        <svg
          v-else
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="h-6 w-6"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Collapsible mobile menu -->
    <Transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="-translate-y-2 opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="-translate-y-2 opacity-0"
    >
      <div v-if="mobileMenuOpen" class="border-t border-slate-200 bg-white md:hidden">
        <nav class="flex flex-col gap-1 px-6 py-3">
          <NuxtLink
            to="/"
            class="rounded-md px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900"
            @click="mobileMenuOpen = false"
          >
            Home
          </NuxtLink>
          <NuxtLink
            to="/join"
            class="rounded-md px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900"
            @click="mobileMenuOpen = false"
          >
            Join via link
          </NuxtLink>
          <NuxtLink
            to="/auth/login"
            class="rounded-lg bg-brand-600 px-3 py-2 text-sm font-semibold text-white hover:bg-brand-700"
            @click="mobileMenuOpen = false"
          >
            Login
          </NuxtLink>
        </nav>
      </div>
    </Transition>
  </header>
</template>
