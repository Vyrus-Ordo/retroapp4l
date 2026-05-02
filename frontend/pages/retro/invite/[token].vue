<script setup lang="ts">
import type { AuthResponse, InviteResolveResponse } from "~/utils/types"

import { isEmail, required } from "~/utils/validation"

const route = useRoute()
const api = useApiClient()
const { authStore } = useAuth()
const guestStore = useGuestStore()
const toastStore = useToastStore()

const token = computed(() => String(route.params.token))
const invite = ref<InviteResolveResponse | null>(null)
const errorMessage = ref("")
const loading = ref(true)
const joining = ref(false)
const form = reactive({
  name: "",
  email: "",
})

const canJoin = computed(() => invite.value?.invite_status === "active" || invite.value?.invite_status === "temporarily_open")
const isAuthenticatedUser = computed(() => authStore.isAuthenticated && !authStore.isGuestSession)

function prefillIdentity() {
  if (isAuthenticatedUser.value && authStore.user) {
    form.name = authStore.user.name
    form.email = authStore.user.email
    return
  }

  if (authStore.isGuestSession && authStore.user) {
    form.name = authStore.user.name
    form.email = authStore.user.email
    return
  }

  form.name = guestStore.name
  form.email = guestStore.email
}

async function loadInvite() {
  loading.value = true
  errorMessage.value = ""
  try {
    invite.value = await api.get<InviteResolveResponse>(`/invites/${token.value}/`, false)
    prefillIdentity()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "Não foi possível carregar o convite."
  } finally {
    loading.value = false
  }
}

async function submit() {
  errorMessage.value = ""
  if (!required(form.name)) {
    errorMessage.value = "Nome é obrigatório."
    return
  }
  if (form.email && !isEmail(form.email)) {
    errorMessage.value = "Use um email válido ou deixe o campo em branco."
    return
  }

  joining.value = true
  try {
    const response = await api.post<AuthResponse, { name: string; email?: string }>(
      `/invites/${token.value}/join/`,
      {
        name: form.name.trim(),
        email: form.email.trim() || undefined,
      },
    )
    authStore.applySession(response)
    if (response.user.is_guest) {
      guestStore.setProfile({ name: form.name, email: form.email })
    }
    toastStore.success("Entrada liberada.")
    await navigateTo(`/retro/${response.retrospective_id}`)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "Não foi possível entrar na retrospectiva."
    toastStore.error(errorMessage.value)
  } finally {
    joining.value = false
  }
}

onMounted(() => {
  authStore.init()
  guestStore.init()
  prefillIdentity()
  loadInvite()
})
</script>

<template>
  <AppShell>
    <section class="mx-auto grid w-full max-w-5xl gap-6 lg:grid-cols-[1.2fr,0.8fr]">
      <div class="panel overflow-hidden">
        <div class="bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.18),_transparent_45%),linear-gradient(135deg,_#ffffff_0%,_#f8fafc_100%)] px-6 py-8 lg:px-8">
          <p class="text-xs font-semibold uppercase tracking-[0.25em] text-brand-700">Convite público</p>
          <h1 class="mt-3 text-3xl font-semibold text-slate-900">Entrar na retrospectiva</h1>
          <p class="mt-3 max-w-2xl text-sm leading-6 text-slate-600">
            Use seu nome para participar agora. Se quiser, informe também seu email para facilitar identificação futura neste navegador.
          </p>
        </div>

        <div class="px-6 py-6 lg:px-8 lg:py-8">
          <div v-if="loading" class="rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-8 text-sm text-slate-500">
            Carregando detalhes do convite...
          </div>

          <div v-else class="space-y-6">
            <div v-if="invite" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Retrospectiva</p>
              <h2 class="mt-2 text-2xl font-semibold text-slate-900">{{ invite.title }}</h2>
              <p class="mt-2 text-sm text-slate-600">
                Facilitadora: <span class="font-medium text-slate-900">{{ invite.facilitator_name }}</span>
              </p>
              <p class="mt-1 text-sm text-slate-600">
                Time: <span class="font-medium text-slate-900">{{ invite.team_key }}</span>
                <span v-if="invite.sprint_name"> · Sprint {{ invite.sprint_name }}</span>
              </p>
            </div>

            <form class="space-y-4" @submit.prevent="submit">
              <div class="space-y-2">
                <label class="text-sm font-medium text-slate-700" for="guest-name">Nome</label>
                <input id="guest-name" v-model="form.name" class="field-input" maxlength="255" placeholder="Como você quer aparecer na retro?" type="text">
              </div>

              <div class="space-y-2">
                <label class="text-sm font-medium text-slate-700" for="guest-email">Email opcional</label>
                <input id="guest-email" v-model="form.email" class="field-input" placeholder="voce@empresa.com" type="email">
              </div>

              <p v-if="invite && !canJoin" class="rounded-xl border border-warning-200 bg-warning-50 px-4 py-3 text-sm text-warning-700">
                O link está bloqueado no momento. Peça para a facilitadora reabrir a entrada.
              </p>

              <p v-if="errorMessage" class="text-sm text-danger-500">{{ errorMessage }}</p>

              <div class="flex flex-col gap-3 sm:flex-row">
                <button :disabled="joining || !canJoin" class="button-primary" type="submit">
                  {{ joining ? 'Entrando...' : (isAuthenticatedUser ? 'Entrar com minha conta' : 'Entrar como convidado') }}
                </button>
                <NuxtLink class="button-secondary" to="/join">Tenho outro código</NuxtLink>
              </div>
            </form>
          </div>
        </div>
      </div>

      <aside class="panel flex flex-col gap-4 p-6 lg:p-8">
        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Como funciona</p>
        <div class="rounded-2xl bg-slate-50 p-4 text-sm leading-6 text-slate-600">
          Seu nome e email opcional ficam gravados localmente neste navegador para acelerar convites futuros.
        </div>
        <div class="rounded-2xl bg-brand-50 p-4 text-sm leading-6 text-brand-900">
          Você não precisa criar conta para participar desta retro. O login continua reservado para quem organiza e administra sessões.
        </div>
        <div v-if="authStore.isGuestSession && authStore.user" class="rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
          Sessão atual: <span class="font-medium text-slate-900">{{ authStore.user.name }}</span>
        </div>
      </aside>
    </section>
  </AppShell>
</template>