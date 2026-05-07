<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm" @click.self="$emit('close')">
    <div class="w-full max-w-md rounded-xl border border-[#00f2ff]/15 p-6" style="background: rgba(10,10,10,0.95)">
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-lg font-light text-white">Settings</h2>
        <button class="rounded-full p-1 text-zinc-500 transition hover:text-white" @click="$emit('close')">
          <span class="mdi mdi-close text-xl" />
        </button>
      </div>
      <p class="text-sm text-zinc-600">Coming soon.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits<{ close: [] }>()
</script>
