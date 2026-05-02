<script setup lang="ts">
import { PlusCircleIcon, SparklesIcon } from "@heroicons/vue/24/outline"

const retroStore = useRetroStore()

const form = reactive({
  title: "",
  sprint_name: "",
  description: "",
  team_key: "",
  max_votes_per_user: 3,
  skip_check_phase: false,
})

const milestoneDraft = reactive({ category: "achievement", description: "" })
const milestones = ref<Array<{ category: string; description: string }>>([])
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
    errorMessage.value = "Title and team key are required."
    return
  }

  pending.value = true
  try {
    const retrospectiveId = await retroStore.createRetrospective({ ...form, milestones: milestones.value })
    await navigateTo(`/retro/${retrospectiveId}`)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "Unable to create retrospective."
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <AppShell>
    <section class="space-y-6">
      <div class="panel p-6 lg:p-8">
        <p class="text-xs font-semibold text-brand-500">Setup</p>
        <h1 class="mt-3 text-2xl font-semibold text-slate-900">Create a retrospective</h1>
        <p class="mt-2 text-sm text-slate-600">Configure the session metadata, votes, and initial milestone set.</p>

        <form class="mt-6 grid gap-4 lg:grid-cols-2" @submit.prevent="submit">
          <input v-model="form.title" class="field-input lg:col-span-2" placeholder="Session title">
          <input v-model="form.sprint_name" class="field-input" placeholder="Sprint name">
          <div class="space-y-2">
            <input v-model="form.team_key" class="field-input" list="team-suggestions" placeholder="Team key">
            <datalist id="team-suggestions">
              <option v-for="suggestion in suggestions" :key="suggestion" :value="suggestion" />
            </datalist>
          </div>
          <textarea v-model="form.description" class="field-input lg:col-span-2 min-h-28" placeholder="Optional retrospective description." />
          <input v-model.number="form.max_votes_per_user" class="field-input" max="10" min="1" type="number">
          <label class="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700">
            <input v-model="form.skip_check_phase" class="h-4 w-4 rounded border-slate-300 text-brand-500" type="checkbox">
            Skip action check phase
          </label>
          <p v-if="errorMessage" class="lg:col-span-2 text-sm text-danger-500">{{ errorMessage }}</p>
          <div class="lg:col-span-2 flex justify-end">
            <button :disabled="pending" class="button-primary" type="submit">
              <PlusCircleIcon class="mr-2 h-5 w-5" />
              {{ pending ? 'Creating...' : 'Create retrospective' }}
            </button>
          </div>
        </form>
      </div>

      <section class="panel p-6 lg:p-8">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Milestones</h2>
            <p class="mt-1 text-sm text-slate-600">Add key moments to present before the 4L board opens.</p>
          </div>
          <div class="inline-flex items-center gap-2 rounded bg-slate-50 px-3 py-2 text-sm text-slate-600">
            <SparklesIcon class="h-4 w-4 text-brand-500" />
            {{ milestones.length }} items
          </div>
        </div>

        <div class="mt-6 grid gap-4 lg:grid-cols-[220px,1fr,auto]">
          <select v-model="milestoneDraft.category" class="field-input">
            <option value="achievement">Achievement</option>
            <option value="challenge">Challenge</option>
            <option value="decision">Decision</option>
            <option value="incident">Incident</option>
          </select>
          <input v-model="milestoneDraft.description" class="field-input" placeholder="Describe the milestone">
          <button class="button-secondary" type="button" @click="addMilestone">Add milestone</button>
        </div>

        <div class="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <MilestoneCard
            v-for="(milestone, index) in milestones"
            :key="`${milestone.category}-${index}`"
            :milestone="{
              id: `${index}`,
              category: milestone.category,
              description: milestone.description,
              author: 'local',
              author_name: 'Facilitator',
              created_at: new Date().toISOString(),
            }"
          />
          <div v-if="!milestones.length" class="rounded-lg border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-500">
            Add at least one milestone if the presentation phase should have content.
          </div>
        </div>
      </section>
    </section>
  </AppShell>
</template>