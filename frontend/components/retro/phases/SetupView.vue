<template>
  <div class="flex flex-col items-center justify-center min-h-[60vh] gap-6">
    <span class="mdi mdi-cog-outline animate-spin text-5xl text-brand-500" />
    <h1 class="text-2xl font-bold text-gray-900">Preparando a sessão...</h1>
    <p class="text-gray-600">{{ current?.title }}</p>
    <div class="flex flex-col items-center gap-2 mt-6">
      <div v-if="isFacilitator">
        <button class="button-primary" @click="$emit('advance-phase')">Ir para o Lobby</button>
      </div>
      <div v-else class="flex flex-col items-center gap-1">
        <span class="text-sm text-gray-700">Aguarde a facilitadora iniciar</span>
        <div class="flex items-center gap-2 mt-2">
          <AvatarCircle v-for="p in participants" :key="p.id" :name="p.user_name" size="36" color="brand" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AvatarCircle from '~/components/layout/AvatarCircle.vue'
const props = defineProps({
  current: Object,
  isFacilitator: Boolean,
  participants: Array
})
</script>

<style scoped>
.animate-spin {
  animation: spin 1.2s linear infinite;
}
@keyframes spin {
  100% { transform: rotate(360deg); }
}
</style>
