<script setup lang="ts">
import type { ActionReviewFilters, ActionReviewOrdering } from "~/stores/actionsReview"
import type { ActionReviewTeam, ActionStatus } from "~/utils/types"

const props = defineProps<{
  filters: ActionReviewFilters
  teams: ActionReviewTeam[]
}>()

const emit = defineEmits<{
  patch: [patch: Partial<ActionReviewFilters>]
  reset: []
}>()

const STATUS_OPTIONS: Array<{ value: ActionStatus; label: string }> = [
  { value: "not_started", label: "Not started" },
  { value: "in_progress", label: "In progress" },
  { value: "done", label: "Done" },
]

const ORDERING_OPTIONS: Array<{ value: ActionReviewOrdering; label: string }> = [
  { value: "due_date", label: "Due date · earliest" },
  { value: "-due_date", label: "Due date · latest" },
  { value: "status_updated_at", label: "Updated · oldest" },
  { value: "-status_updated_at", label: "Updated · newest" },
  { value: "created_at", label: "Created · oldest" },
  { value: "-created_at", label: "Created · newest" },
]

const searchTerm = ref(props.filters.q)

watch(
  () => props.filters.q,
  (value) => {
    searchTerm.value = value
  },
)

function toggleTeam(teamKey: string) {
  const teamKeys = props.filters.teamKeys.includes(teamKey)
    ? props.filters.teamKeys.filter((key) => key !== teamKey)
    : [...props.filters.teamKeys, teamKey]
  emit("patch", { teamKeys })
}

function toggleStatus(status: ActionStatus) {
  const statuses = props.filters.statuses.includes(status)
    ? props.filters.statuses.filter((value) => value !== status)
    : [...props.filters.statuses, status]
  emit("patch", { statuses })
}

function setOnlyMine(event: Event) {
  const checked = (event.target as HTMLInputElement).checked
  emit("patch", { assignee: checked ? "me" : null })
}

function setOverdue(event: Event) {
  emit("patch", { overdue: (event.target as HTMLInputElement).checked })
}

function submitSearch() {
  if (searchTerm.value.trim() !== props.filters.q.trim()) {
    emit("patch", { q: searchTerm.value.trim() })
  }
}

function setOrdering(event: Event) {
  emit("patch", { ordering: (event.target as HTMLSelectElement).value as ActionReviewOrdering })
}
</script>

<template>
  <section class="panel p-5 lg:p-6" aria-label="Action filters">
    <div class="flex flex-wrap items-end gap-4">
      <div class="min-w-48 flex-1">
        <p class="text-xs font-light uppercase tracking-[0.15em] text-zinc-500">Teams</p>
        <div class="mt-2 flex flex-wrap gap-2">
          <button
            v-for="team in teams"
            :key="team.team_key"
            type="button"
            class="rounded-full border px-3 py-1.5 text-xs font-light transition-colors"
            :class="
              filters.teamKeys.includes(team.team_key)
                ? 'border-[#00f2ff]/50 text-[#00f2ff]'
                : 'border-white/10 text-zinc-400 hover:text-white'
            "
            :aria-pressed="filters.teamKeys.includes(team.team_key)"
            @click="toggleTeam(team.team_key)"
          >
            {{ team.team_key }}
            <span class="ml-1 text-[10px] text-zinc-500">{{ team.pending }} pending</span>
          </button>
          <p v-if="!teams.length" class="text-xs text-zinc-600">No teams available.</p>
        </div>
      </div>

      <div>
        <p class="text-xs font-light uppercase tracking-[0.15em] text-zinc-500">Status</p>
        <div class="mt-2 flex flex-wrap gap-2">
          <button
            v-for="option in STATUS_OPTIONS"
            :key="option.value"
            type="button"
            class="rounded-full border px-3 py-1.5 text-xs font-light transition-colors"
            :class="
              filters.statuses.includes(option.value)
                ? 'border-[#00f2ff]/50 text-[#00f2ff]'
                : 'border-white/10 text-zinc-400 hover:text-white'
            "
            :aria-pressed="filters.statuses.includes(option.value)"
            @click="toggleStatus(option.value)"
          >
            {{ option.label }}
          </button>
        </div>
      </div>
    </div>

    <div class="mt-5 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <div class="lg:col-span-2">
        <label class="text-xs font-light text-zinc-500" for="actions-review-search">Search</label>
        <input
          id="actions-review-search"
          v-model="searchTerm"
          class="field-input mt-1"
          placeholder="Search action descriptions"
          type="search"
          @change="submitSearch"
          @keydown.enter.prevent="submitSearch"
        >
      </div>

      <div>
        <label class="text-xs font-light text-zinc-500" for="actions-review-due-after">Due after</label>
        <input
          id="actions-review-due-after"
          class="field-input mt-1"
          type="date"
          :value="filters.dueAfter"
          @change="emit('patch', { dueAfter: ($event.target as HTMLInputElement).value })"
        >
      </div>

      <div>
        <label class="text-xs font-light text-zinc-500" for="actions-review-due-before">Due before</label>
        <input
          id="actions-review-due-before"
          class="field-input mt-1"
          type="date"
          :value="filters.dueBefore"
          @change="emit('patch', { dueBefore: ($event.target as HTMLInputElement).value })"
        >
      </div>
    </div>

    <div class="mt-5 flex flex-wrap items-center gap-4">
      <label class="inline-flex items-center gap-2 text-sm font-light text-zinc-400">
        <input type="checkbox" :checked="filters.assignee === 'me'" class="h-4 w-4 accent-[#00f2ff]" @change="setOnlyMine">
        Only mine
      </label>

      <label class="inline-flex items-center gap-2 text-sm font-light text-zinc-400">
        <input type="checkbox" :checked="filters.overdue" class="h-4 w-4 accent-[#00f2ff]" @change="setOverdue">
        Overdue only
      </label>

      <div class="flex items-center gap-2">
        <label class="text-sm font-light text-zinc-400" for="actions-review-ordering">Order by</label>
        <select
          id="actions-review-ordering"
          class="field-input w-auto py-2 text-sm"
          :value="filters.ordering"
          @change="setOrdering"
        >
          <option v-for="option in ORDERING_OPTIONS" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </div>

      <button type="button" class="button-secondary ml-auto py-2 text-sm" @click="emit('reset')">
        Clear filters
      </button>
    </div>
  </section>
</template>
