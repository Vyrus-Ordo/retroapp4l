<script setup lang="ts">
import { ArrowRightCircleIcon } from "@heroicons/vue/24/outline"

import { isEmail, required } from "~/utils/validation"

const route = useRoute()
const config = useRuntimeConfig()
const { authStore } = useAuth()
const form = reactive({ email: "", password: "" })
const errorMessage = ref("")
const pending = ref(false)

const authHost = computed(() => config.public.apiBase.replace(/\/api\/?$/, ""))

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
    await navigateTo(typeof route.query.redirect === "string" ? route.query.redirect : "/")
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "Unable to sign in."
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <AppShell>
    <section class="mx-auto max-w-xl panel p-6 lg:p-8">
      <p class="text-xs font-semibold text-brand-500">Authentication</p>
      <h1 class="mt-3 text-2xl font-semibold text-slate-900">Sign in to your workspace</h1>
      <p class="mt-2 text-sm text-slate-600">Use local auth or continue with an OAuth provider configured in Django allauth.</p>

      <form class="mt-6 space-y-4" @submit.prevent="submit">
        <input v-model="form.email" class="field-input" placeholder="Email" type="email">
        <input v-model="form.password" class="field-input" placeholder="Password" type="password">
        <p v-if="errorMessage" class="text-sm text-danger-500">{{ errorMessage }}</p>
        <button :disabled="pending" class="button-primary w-full" type="submit">
          <ArrowRightCircleIcon class="mr-2 h-5 w-5" />
          {{ pending ? 'Signing in...' : 'Sign in' }}
        </button>
      </form>

      <div class="mt-6 grid gap-3 sm:grid-cols-2">
        <a :href="`${authHost}/accounts/google/login/`" class="button-secondary text-center">Continue with Google</a>
        <a :href="`${authHost}/accounts/github/login/`" class="button-secondary text-center">Continue with GitHub</a>
      </div>

      <p class="mt-6 text-sm text-slate-600">
        New here?
        <NuxtLink class="font-medium text-brand-500" to="/auth/register">Create an account</NuxtLink>
      </p>
    </section>
  </AppShell>
</template>