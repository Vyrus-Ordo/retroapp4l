<script setup lang="ts">
import { UserPlusIcon } from "@heroicons/vue/24/outline"

import { isEmail, minLength, required } from "~/utils/validation"

const { authStore } = useAuth()
const toastStore = useToastStore()
const form = reactive({ name: "", email: "", password: "" })
const errorMessage = ref("")
const pending = ref(false)

async function submit() {
  errorMessage.value = ""
  if (!required(form.name) || !required(form.email) || !required(form.password)) {
    errorMessage.value = "Name, email, and password are required."
    return
  }
  if (!isEmail(form.email)) {
    errorMessage.value = "Use a valid email address."
    return
  }
  if (!minLength(form.password, 8)) {
    errorMessage.value = "Password must be at least 8 characters."
    return
  }

  pending.value = true
  try {
    await authStore.register(form)
    toastStore.success("Account created successfully.")
    await navigateTo("/")
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "Unable to register."
    toastStore.error(errorMessage.value)
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <AppShell>
    <section class="mx-auto max-w-xl panel p-6 lg:p-8">
      <p class="text-xs font-semibold text-brand-500">Authentication</p>
      <h1 class="mt-3 text-2xl font-semibold text-slate-900">Create your account</h1>
      <p class="mt-2 text-sm text-slate-600">Local accounts use the same JWT flow as the backend API.</p>

      <form class="mt-6 space-y-4" @submit.prevent="submit">
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-700" for="name">Name</label>
          <input id="name" v-model="form.name" class="field-input" placeholder="Full name" type="text" autocomplete="name">
        </div>
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-700" for="email">Email</label>
          <input id="email" v-model="form.email" class="field-input" placeholder="Email" type="email" autocomplete="email">
        </div>
        <div class="space-y-2">
          <label class="text-sm font-medium text-gray-700" for="password">Password</label>
          <input id="password" v-model="form.password" class="field-input" placeholder="Password" type="password" autocomplete="new-password">
        </div>
        <p v-if="errorMessage" role="alert" class="text-sm text-danger-500">{{ errorMessage }}</p>
        <button :disabled="pending" class="button-primary w-full" type="submit">
          <UserPlusIcon class="mr-2 h-5 w-5" />
          {{ pending ? 'Creating account...' : 'Create account' }}
        </button>
      </form>

      <p class="mt-6 text-sm text-slate-600">
        Already have an account?
        <NuxtLink class="font-medium text-brand-500" to="/auth/login">Sign in</NuxtLink>
      </p>
    </section>
  </AppShell>
</template>