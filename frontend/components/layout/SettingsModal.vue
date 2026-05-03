<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="$emit('close')">
    <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-slate-900">Configurações</h2>
        <button class="rounded-full p-1 hover:bg-slate-100 transition" @click="$emit('close')">
          <span class="mdi mdi-close text-xl text-slate-500" />
        </button>
      </div>
      <p class="text-sm text-slate-500">Em breve.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits<{ close: [] }>()
</script>
