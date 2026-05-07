<script setup lang="ts">
const mobileMenuOpen = ref(false)
</script>

<template>
  <header class="sticky top-0 z-50 border-b border-[#00f2ff]/10 bg-[#050505]/85 backdrop-blur-md">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
      <!-- LEFT: logo -->
      <NuxtLink
        to="/"
        class="font-light tracking-[0.15em] uppercase text-[#00f2ff]"
        style="font-family: 'JetBrains Mono', monospace; font-size: 1rem"
      >
        RetroApp 4L
      </NuxtLink>

      <!-- RIGHT: navigation (desktop) / hamburger (mobile) -->
      <nav class="hidden items-center gap-1 md:flex">
        <NuxtLink
          to="/"
          class="rounded-md px-3 py-2 text-sm font-light text-zinc-400 transition-colors hover:text-white"
        >
          Home
        </NuxtLink>
        <NuxtLink
          to="/join"
          class="rounded-md px-3 py-2 text-sm font-light text-zinc-400 transition-colors hover:text-white"
        >
          Join via link
        </NuxtLink>
        <NuxtLink
          to="/auth/login"
          class="ml-2 inline-flex items-center justify-center rounded-lg border border-[#00f2ff] px-4 py-2 text-sm font-medium text-[#00f2ff] transition-all duration-200 hover:bg-[#00f2ff]/10 hover:shadow-glow focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#00f2ff]/60"
        >
          Login
        </NuxtLink>
      </nav>

      <!-- Mobile: hamburger (right) -->
      <button
        class="rounded-md p-2 text-zinc-400 transition-colors hover:text-white md:hidden"
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
      <div v-if="mobileMenuOpen" class="border-t border-[#00f2ff]/10 bg-[#050505] md:hidden">
        <nav class="flex flex-col gap-1 px-6 py-3">
          <NuxtLink
            to="/"
            class="rounded-md px-3 py-2 text-sm font-light text-zinc-400 hover:text-white"
            @click="mobileMenuOpen = false"
          >
            Home
          </NuxtLink>
          <NuxtLink
            to="/join"
            class="rounded-md px-3 py-2 text-sm font-light text-zinc-400 hover:text-white"
            @click="mobileMenuOpen = false"
          >
            Join via link
          </NuxtLink>
          <NuxtLink
            to="/auth/login"
            class="inline-flex items-center justify-center rounded-lg border border-[#00f2ff] px-3 py-2 text-sm font-medium text-[#00f2ff] hover:bg-[#00f2ff]/10"
            @click="mobileMenuOpen = false"
          >
            Login
          </NuxtLink>
        </nav>
      </div>
    </Transition>
  </header>
</template>
