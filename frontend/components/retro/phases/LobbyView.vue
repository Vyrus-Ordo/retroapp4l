<template>
  <div class="flex flex-col gap-8 lg:flex-row lg:items-start lg:justify-between min-h-[60vh]">
    <div class="flex-1 panel p-8 flex flex-col gap-4">
      <h1 class="text-xl font-bold text-gray-900 mb-2">Lobby</h1>
      <p class="text-gray-600">Convide participantes e aguarde todos entrarem antes de iniciar.</p>
      <div class="mt-4 flex flex-col gap-2">
        <div class="flex items-center gap-2">
          <span class="mdi mdi-link-variant text-brand-500 text-xl" />
          <span class="text-sm">Link de convite:</span>
          <span class="font-mono text-xs bg-gray-50 px-2 py-1 rounded">{{ inviteLink || 'Indisponível' }}</span>
          <button v-if="inviteLink" class="button-secondary ml-2" @click="$emit('copy-invite-link')">Copiar</button>
        </div>
        <div class="flex items-center gap-2">
          <span class="mdi mdi-account-multiple-outline text-brand-500 text-xl" />
          <span class="text-sm">Participantes conectados:</span>
          <span class="font-semibold">{{ participants.length }}</span>
        </div>
      </div>
      <div class="mt-6">
        <button v-if="isFacilitator" class="button-primary" @click="$emit('advance-phase')">Iniciar sessão</button>
      </div>
    </div>
    <div class="flex-1 panel p-8 flex flex-col gap-4">
      <h2 class="text-lg font-semibold text-gray-900">Como funciona</h2>
      <ul class="list-disc pl-5 text-gray-700 text-sm space-y-1">
        <li>Convide o time pelo link acima</li>
        <li>Confirme todos presentes</li>
        <li>Avance para o check de ações</li>
        <li>Prossiga pelas fases até o encerramento</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  inviteLink: String,
  isFacilitator: Boolean,
  participants: Array
})
</script>
