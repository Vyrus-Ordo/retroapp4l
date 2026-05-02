<script setup lang="ts">
import type { MilestoneCategory } from "~/utils/types"
import MilestoneCard from "~/components/retro/MilestoneCard.vue"

const retroStore = useRetroStore()

const form = reactive({
  title: "",
  sprint_name: "",
  description: "",
  team_key: "",
  max_votes_per_user: 3,
  skip_check_phase: false,
  include_milestones: true,
})
const milestoneDraft = reactive<{ category: MilestoneCategory; description: string }>({
  category: "achievement",
  description: "",
})
const milestones = ref<Array<{ category: MilestoneCategory; description: string }>>([])
const suggestions = ref<string[]>([])
const pending = ref(false)
const errorMessage = ref("")

watch(
  () => form.team_key,
  async (value) => {
    if (value.trim().length < 2) {
      suggestions.value = []
      return
    }
    suggestions.value = await retroStore.fetchTeamSuggestions(value)
  },
)

function addMilestone() {
  if (!milestoneDraft.description.trim()) {
    return
  }
  milestones.value.push({ ...milestoneDraft })
  milestoneDraft.description = ""
}

async function submit() {
  errorMessage.value = ""
  if (!form.title.trim() || !form.team_key.trim()) {
    errorMessage.value = "Título e time são obrigatórios."
    return
  }
  pending.value = true
  try {
    const retrospectiveId = await retroStore.createRetrospective({
      ...form,
      milestones: form.include_milestones ? milestones.value : [],
    })
    await navigateTo(`/retro/${retrospectiveId}`)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "Não foi possível criar a retrospectiva."
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <AppShell>
    <section class="space-y-8">
      <div class="grid gap-8 lg:grid-cols-2">
        <!-- Card 1 -->
        <div class="panel p-6 lg:p-8 flex flex-col gap-4">
          <button class="mb-2 text-brand-500 hover:underline self-start" type="button" @click="$router.back()">← Voltar</button>
          <h1 class="text-2xl font-bold text-gray-900">Nova retrospectiva</h1>
          <form class="mt-4 flex flex-col gap-4" @submit.prevent="submit">
            <div class="grid grid-cols-2 gap-4">
              <input v-model="form.sprint_name" class="field-input" placeholder="Sprint">
              <input v-model="form.title" class="field-input" placeholder="Título da retrospectiva">
            </div>
            <textarea v-model="form.description" class="field-input min-h-24" placeholder="Contexto (opcional)" />
            <div class="grid grid-cols-2 gap-4">
              <div>
                <input v-model="form.team_key" class="field-input" list="team-suggestions" placeholder="Time">
                <datalist id="team-suggestions">
                  <option v-for="suggestion in suggestions" :key="suggestion" :value="suggestion" />
                </datalist>
              </div>
              <input v-model.number="form.max_votes_per_user" class="field-input" max="10" min="1" type="number" placeholder="Votos por pessoa">
            </div>
            <label class="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm text-gray-700">
              <input v-model="form.skip_check_phase" class="h-4 w-4 rounded border-gray-300 text-brand-500" type="checkbox">
              Pular fase de check de ações
            </label>
            <p v-if="errorMessage" class="text-sm text-danger-500">{{ errorMessage }}</p>
            <div class="flex justify-end gap-2 mt-2">
              <button type="button" class="button-secondary" @click="$router.back()">Cancelar</button>
              <button :disabled="pending" class="button-primary" type="submit">
                {{ pending ? 'Criando...' : 'Criar e ir pro lobby' }}
              </button>
            </div>
          </form>
        </div>

        <!-- Card 2 -->
        <div class="panel p-6 lg:p-8 flex flex-col gap-4">
          <label class="inline-flex items-center gap-2 mb-2">
            <input v-model="form.include_milestones" type="checkbox" class="h-4 w-4 rounded border-gray-300 text-brand-500">
            Incluir fase de marcos
          </label>
          <div v-if="form.include_milestones">
            <div class="flex items-center gap-2 mb-2">
              <span class="font-semibold text-gray-700">Adicionar marco</span>
              <span class="rounded bg-brand-50 px-2 py-1 text-xs text-brand-700">{{ milestones.length }} marcos</span>
            </div>
            <div class="grid gap-2 grid-cols-[140px,1fr,auto]">
              <select v-model="milestoneDraft.category" class="field-input">
                <option value="achievement">Conquista</option>
                <option value="challenge">Desafio</option>
                <option value="change">Mudança</option>
                <option value="recognition">Reconhecimento</option>
                <option value="other">Outro</option>
              </select>
              <input v-model="milestoneDraft.description" class="field-input" placeholder="Descreva o marco">
              <button class="button-secondary" type="button" @click="addMilestone">Adicionar</button>
            </div>
            <div class="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              <MilestoneCard
                v-for="(milestone, index) in milestones"
                :key="`${milestone.category}-${index}`"
                :milestone="{
                  id: `${index}`,
                  category: milestone.category,
                  description: milestone.description,
                  author: 'local',
                  author_name: 'Facilitadora',
                  created_at: new Date().toISOString(),
                }"
              />
              <div v-if="!milestones.length" class="rounded-lg border border-dashed border-gray-200 bg-gray-50 p-6 text-sm text-gray-500">
                Nenhum marco adicionado.
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </AppShell>
</template>