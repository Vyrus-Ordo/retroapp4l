<template>
  <AppShell>
    <section class="mx-auto w-full max-w-md panel p-8 flex flex-col items-center justify-center" style="min-height: 420px;">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Entrar em uma retro</h1>
      <form class="w-full flex flex-col gap-4 mt-4" @submit.prevent="submit">
        <div class="relative">
          <input v-model="code" class="field-input pl-10" placeholder="Código da retro" maxlength="8" required>
          <span class="absolute left-3 top-1/2 -translate-y-1/2 mdi mdi-key-outline text-xl text-brand-500" />
        </div>
        <p v-if="error" class="text-danger-500 text-sm">{{ error }}</p>
        <button class="button-primary w-full" type="submit" :disabled="pending">
          {{ pending ? 'Entrando...' : 'Entrar' }}
        </button>
      </form>
    </section>
  </AppShell>
</template>

<script setup lang="ts">
const code = ref("")
const error = ref("")
const pending = ref(false)

async function submit() {
  error.value = ""
  if (!code.value.trim() || code.value.length < 4) {
    error.value = "Informe um código válido."
    return
  }
  pending.value = true
  try {
    await navigateTo(`/retro/${code.value}`)
  } catch (e) {
    error.value = "Código inválido ou retro não encontrada."
  } finally {
    pending.value = false
  }
}
</script>
