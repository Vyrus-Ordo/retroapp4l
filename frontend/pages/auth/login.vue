<script setup lang="ts">
const config = useRuntimeConfig()
const pending = ref(false)
const authHost = computed(() => config.public.apiBase.replace(/\/api\/?$/, ""))
</script>

<template>
  <AppShell>
    <section class="mx-auto w-full max-w-sm panel p-8 flex flex-col items-center justify-center" style="min-height: 420px; background: linear-gradient(135deg, #fff 60%, var(--ds-brand-50) 100%);">
      <p class="text-xs font-semibold uppercase text-brand-700 tracking-widest">Bem-vinda de volta</p>
      <h1 class="mt-3 text-2xl font-bold text-gray-900">Entrar no RetroApp</h1>
      <p class="mt-2 text-sm text-gray-600 text-center">Acesse com sua conta Google para participar de uma retrospectiva.</p>

      <div class="mt-8 w-full">
        <a :href="`${authHost}/accounts/google/login/`" class="button-primary w-full flex items-center justify-center gap-2" :aria-busy="pending">
          <span class="mdi mdi-google" />
          Entrar com Google
        </a>
      </div>
    </section>
  </AppShell>
</template>