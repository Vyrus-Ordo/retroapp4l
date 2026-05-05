<script setup lang="ts">
import type { MilestoneCategory } from "~/utils/types"
import MilestoneCard from "~/components/retro/MilestoneCard.vue"

const retroStore = useRetroStore()

const TIMED_PHASE_LABELS: Record<string, string> = {
  presentation: "Milestones",
  check: "Action check",
  board: "Board 4L",
  grouping: "Grouping",
  voting: "Voting",
  discussion: "Discussion",
  actions: "Actions",
}

const DEFAULT_DURATIONS_MINUTES: Record<string, number> = {
  presentation: 10,
  check: 5,
  board: 15,
  grouping: 5,
  voting: 3,
  discussion: 15,
  actions: 10,
}

const phaseDurationsMinutes = reactive<Record<string, number>>({ ...DEFAULT_DURATIONS_MINUTES })

const form = reactive({
  title: "",
  sprint_name: "",
  description: "",
  team_key: "",
  max_votes_per_user: 3,
  allow_self_vote: false,
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
    errorMessage.value = "Title and team are required."
    return
  }
  pending.value = true
  try {
    const phase_durations: Record<string, number> = {}
    for (const [phase, minutes] of Object.entries(phaseDurationsMinutes)) {
      phase_durations[phase] = Math.max(0, Math.round(Number(minutes) * 60))
    }
    const retrospectiveId = await retroStore.createRetrospective({
      ...form,
      phase_durations,
      milestones: form.include_milestones ? milestones.value : [],
    })
    await navigateTo(`/retro/${retrospectiveId}`)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "Unable to create the retrospective."
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
          <button class="mb-2 text-brand-500 hover:underline self-start" type="button" @click="$router.back()">← Back</button>
          <h1 class="text-2xl font-bold text-gray-900">New retrospective</h1>
          <form class="mt-4 flex flex-col gap-4" @submit.prevent="submit">
            <div class="grid grid-cols-2 gap-4">
              <input v-model="form.sprint_name" class="field-input" placeholder="Sprint">
              <input v-model="form.title" class="field-input" placeholder="Retrospective title">
            </div>
            <textarea v-model="form.description" class="field-input min-h-24" placeholder="Context (optional)" />
            <div class="grid grid-cols-2 gap-4">
              <div>
                <input v-model="form.team_key" class="field-input" list="team-suggestions" placeholder="Team">
                <datalist id="team-suggestions">
                  <option v-for="suggestion in suggestions" :key="suggestion" :value="suggestion" />
                </datalist>
              </div>
              <input v-model.number="form.max_votes_per_user" class="field-input" max="10" min="1" type="number" placeholder="Votes per person">
            </div>
            <label class="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm text-gray-700">
              <input v-model="form.allow_self_vote" class="h-4 w-4 rounded border-gray-300 text-brand-500" type="checkbox">
              Allow self-voting
            </label>
            <label class="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm text-gray-700">
              <input v-model="form.skip_check_phase" class="h-4 w-4 rounded border-gray-300 text-brand-500" type="checkbox">
              Skip action check phase
            </label>
            <p v-if="errorMessage" class="text-sm text-danger-500">{{ errorMessage }}</p>
            <div class="flex justify-end gap-2 mt-2">
              <button type="button" class="button-secondary" @click="$router.back()">Cancel</button>
              <button :disabled="pending" class="button-primary" type="submit">
                {{ pending ? 'Creating...' : 'Create and go to lobby' }}
              </button>
            </div>
          </form>
        </div>

        <!-- Card 2: Phase durations -->
        <div class="panel p-6 lg:p-8 flex flex-col gap-4">
          <h2 class="text-lg font-semibold text-gray-900">Phase durations</h2>
          <p class="text-sm text-gray-500">Sets the default timer for each phase (in minutes). The facilitator can pause at any time.</p>
          <div class="grid grid-cols-2 gap-x-6 gap-y-3">
            <template v-for="(label, phase) in TIMED_PHASE_LABELS" :key="phase">
              <label v-if="phase !== 'check' || !form.skip_check_phase" class="flex items-center justify-between gap-2 text-sm text-gray-700">
                <span>{{ label }}</span>
                <input
                  v-model.number="phaseDurationsMinutes[phase]"
                  class="field-input w-20 text-center"
                  type="number"
                  min="1"
                  max="120"
                >
              </label>
            </template>
          </div>
        </div>

        <!-- Card 3: Marcos -->
        <div class="panel p-6 lg:p-8 flex flex-col gap-4 lg:col-span-2">
          <label class="inline-flex items-center gap-2 mb-2">
            <input v-model="form.include_milestones" type="checkbox" class="h-4 w-4 rounded border-gray-300 text-brand-500">
            Include milestones phase
          </label>
          <div v-if="form.include_milestones">
            <div class="flex items-center gap-2 mb-2">
              <span class="font-semibold text-gray-700">Add milestone</span>
              <span class="rounded bg-brand-50 px-2 py-1 text-xs text-brand-700">{{ milestones.length }} milestones</span>
            </div>
            <div class="grid gap-2 grid-cols-[140px,1fr,auto]">
              <select v-model="milestoneDraft.category" class="field-input">
                <option value="achievement">Achievement</option>
                <option value="challenge">Challenge</option>
                <option value="change">Change</option>
                <option value="recognition">Recognition</option>
                <option value="other">Other</option>
              </select>
              <input v-model="milestoneDraft.description" class="field-input" placeholder="Describe the milestone">
              <button class="button-secondary" type="button" @click="addMilestone">Add</button>
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
                  author_name: 'Facilitator',
                  created_at: new Date().toISOString(),
                }"
              />
              <div v-if="!milestones.length" class="rounded-lg border border-dashed border-gray-200 bg-gray-50 p-6 text-sm text-gray-500">
                No milestones added yet.
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </AppShell>
</template>