<script setup lang="ts">
import { ArrowRightOnRectangleIcon } from "@heroicons/vue/24/outline"

import { isEmail, required } from "~/utils/validation"

const route = useRoute()
const config = useRuntimeConfig()
const { authStore } = useAuth()
const toastStore = useToastStore()

const form = reactive({ email: "", password: "" })
const errorMessage = ref("")
const pending = ref(false)
const authHost = computed(() => config.public.apiBase.replace(/\/api\/?$/, ""))
const redirectPath = computed(() => {
  const redirect = route.query.redirect
  return typeof redirect === "string" && redirect.startsWith("/") ? redirect : "/"
})

async function submit() {
  errorMessage.value = ""

  if (!required(form.email) || !required(form.password)) {
    errorMessage.value = "Email and password are required."
    return
  }

  if (!isEmail(form.email)) {
    errorMessage.value = "Use a valid email address."
    return
  }

  pending.value = true
  try {
    await authStore.login(form)
    toastStore.success("Signed in successfully.")
    await navigateTo(redirectPath.value)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "Unable to sign in."
    toastStore.error(errorMessage.value)
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <AppShell>
    <section class="mx-auto w-full max-w-md panel p-8" style="min-height: 420px; background: linear-gradient(135deg, #fff 60%, var(--ds-brand-50) 100%);">
      <p class="text-xs font-semibold uppercase text-brand-700 tracking-widest">Acesso</p>
      <h1 class="mt-3 text-2xl font-bold text-gray-900">Entrar no RetroApp</h1>
      <p class="mt-2 text-sm text-gray-600">Entre com email e senha. O acesso com Google continua opcional.</p>

      <form class="mt-8 space-y-4" @submit.prevent="submit">
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-700" for="email">Email</label>
          <input id="email" v-model="form.email" class="field-input" name="email" autocomplete="email" placeholder="voce@empresa.com" type="email">
        </div>

        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-700" for="password">Senha</label>
          <input id="password" v-model="form.password" class="field-input" name="password" autocomplete="current-password" placeholder="Sua senha" type="password">
        </div>

        <p v-if="errorMessage" role="alert" class="text-sm text-danger-500">{{ errorMessage }}</p>

        <button :disabled="pending" class="button-primary w-full" type="submit">
          <ArrowRightOnRectangleIcon class="mr-2 h-5 w-5" />
          {{ pending ? 'Entrando...' : 'Entrar' }}
        </button>
      </form>

      <div class="my-6 flex items-center gap-3 text-xs uppercase tracking-[0.2em] text-gray-400">
        <span class="h-px flex-1 bg-gray-200" />
        <span>ou</span>
        <span class="h-px flex-1 bg-gray-200" />
      </div>

      <a :href="`${authHost}/accounts/google/login/`" class="button-secondary w-full gap-2" :aria-busy="pending">
        <span class="mdi mdi-google text-base" />
        Continuar com Google
      </a>

      <p class="mt-6 text-sm text-slate-600">
        Ainda não tem conta?
        <NuxtLink class="font-medium text-brand-500" to="/auth/register">Criar conta</NuxtLink>
      </p>
    </section>
  </AppShell>
</template>