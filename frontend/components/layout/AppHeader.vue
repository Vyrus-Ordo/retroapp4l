<script setup lang="ts">
// Header simplificado, sem props ou lógica
</script>

<template>
  <header class="border-b border-gray-100 bg-white">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-8">
      <NuxtLink class="text-lg font-bold tracking-tight text-brand-700" to="/">
        RetroApp 4L
      </NuxtLink>
      <nav class="flex items-center gap-4 text-sm text-gray-600">
        <NuxtLink class="rounded px-2 py-1 hover:bg-gray-50" to="/">Início</NuxtLink>
        <NuxtLink class="rounded px-2 py-1 hover:bg-gray-50" to="/retro/create">Nova retro</NuxtLink>
        <NuxtLink class="rounded px-2 py-1 hover:bg-gray-50" to="/history">Histórico</NuxtLink>
      </nav>
    </div>
  </header>
</template>