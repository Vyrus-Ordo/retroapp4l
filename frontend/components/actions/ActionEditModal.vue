<script setup lang="ts">
import type { ActionReviewPatch } from "~/stores/actionsReview"
import type { ActionReviewDetail, ActionStatus } from "~/utils/types"

const props = defineProps<{
  action: ActionReviewDetail | null
  saving?: boolean
  error?: string | null
}>()

const emit = defineEmits<{
  close: []
  submit: [patch: ActionReviewPatch]
}>()

const STATUS_OPTIONS: Array<{ value: ActionStatus; label: string }> = [
  { value: "not_started", label: "Not started" },
  { value: "in_progress", label: "In progress" },
  { value: "done", label: "Done" },
]

const form = reactive({
  description: "",
  assigneeId: "",
  dueDate: "",
  status: "not_started" as ActionStatus,
  externalTrackerUrl: "",
})

/**
 * Responsável pré-selecionado no momento em que o modal abriu para o item.
 *
 * A pré-seleção usa `assignee_participant_id` (spec 3.1) — o id do Participant
 * do responsável atual na retro de origem —, nunca `assignee_name`, que é
 * ambíguo quando o time tem homônimos. `null` deixa o select em "Keep current
 * assignee" e nada é enviado no PATCH.
 */
const initialAssigneeId = ref("")

watch(
  () => props.action,
  (action) => {
    if (!action) return
    form.description = action.description
    form.assigneeId = action.assignee_participant_id ?? ""
    initialAssigneeId.value = form.assigneeId
    form.dueDate = action.due_date ?? ""
    form.status = action.status
    form.externalTrackerUrl = action.external_tracker_url ?? ""
  },
  { immediate: true },
)

const descriptionRef = ref<HTMLTextAreaElement | null>(null)

function handleKeydown(event: KeyboardEvent) {
  if (event.key === "Escape" && !props.saving) {
    emit("close")
  }
}

onMounted(() => {
  document.addEventListener("keydown", handleKeydown)
  nextTick(() => descriptionRef.value?.focus())
})

onBeforeUnmount(() => {
  document.removeEventListener("keydown", handleKeydown)
})

function handleSubmit() {
  if (props.saving || !form.description.trim()) return

  const patch: ActionReviewPatch = {
    description: form.description.trim(),
    due_date: form.dueDate || null,
    status: form.status,
    external_tracker_url: form.externalTrackerUrl.trim(),
  }
  // `assignee_id` só vai no PATCH quando o usuário realmente troca o
  // responsável no select; sem mudança (ou com "Keep current assignee"
  // selecionado) o campo é omitido e o backend preserva o responsável atual.
  if (form.assigneeId && form.assigneeId !== initialAssigneeId.value) {
    patch.assignee_id = form.assigneeId
  }

  emit("submit", patch)
}
</script>

<template>
  <div class="fixed inset-0 z-[60] flex items-center justify-center px-4 py-8">
    <div class="absolute inset-0 bg-black/70 backdrop-blur-sm" @click="!saving && emit('close')" />

    <div
      class="panel relative z-10 max-h-full w-full max-w-xl overflow-y-auto p-6"
      role="dialog"
      aria-modal="true"
      aria-labelledby="action-edit-title"
    >
      <div class="flex items-start justify-between gap-4">
        <div>
          <p class="text-xs font-light text-[#00f2ff]/70">Action review</p>
          <h2 id="action-edit-title" class="mt-2 text-xl font-light text-white">Edit action</h2>
          <p v-if="action" class="mt-1 text-xs text-zinc-500">
            {{ action.retrospective.team_key }} · {{ action.retrospective.title }}
          </p>
        </div>
        <button
          type="button"
          class="button-secondary py-1.5 text-sm"
          :disabled="saving"
          @click="emit('close')"
        >
          Close
        </button>
      </div>

      <form class="mt-5 flex flex-col gap-4" @submit.prevent="handleSubmit">
        <div>
          <label class="text-xs font-light text-zinc-500" for="action-edit-description">Description</label>
          <textarea
            id="action-edit-description"
            ref="descriptionRef"
            v-model="form.description"
            class="field-input mt-1"
            required
            rows="3"
          />
        </div>

        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <label class="text-xs font-light text-zinc-500" for="action-edit-assignee">Assignee</label>
            <select id="action-edit-assignee" v-model="form.assigneeId" class="field-input mt-1">
              <option value="">Keep current assignee</option>
              <option
                v-for="option in action?.assignee_options ?? []"
                :key="option.participant_id"
                :value="option.participant_id"
              >
                {{ option.name }}
              </option>
            </select>
          </div>

          <div>
            <label class="text-xs font-light text-zinc-500" for="action-edit-due-date">Due date</label>
            <input id="action-edit-due-date" v-model="form.dueDate" class="field-input mt-1" type="date">
          </div>

          <div>
            <label class="text-xs font-light text-zinc-500" for="action-edit-status">Status</label>
            <select id="action-edit-status" v-model="form.status" class="field-input mt-1">
              <option v-for="option in STATUS_OPTIONS" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>

          <div>
            <label class="text-xs font-light text-zinc-500" for="action-edit-tracker">External tracker URL</label>
            <input
              id="action-edit-tracker"
              v-model="form.externalTrackerUrl"
              class="field-input mt-1"
              placeholder="https://…"
              type="url"
            >
          </div>
        </div>

        <p v-if="error" class="rounded-lg border border-red-400/40 px-3 py-2 text-sm text-red-300" role="alert">
          {{ error }}
        </p>

        <div class="mt-2 flex justify-end gap-2">
          <button type="button" class="button-secondary" :disabled="saving" @click="emit('close')">Cancel</button>
          <button type="submit" class="button-primary" :disabled="saving || !form.description.trim()">
            {{ saving ? "Saving…" : "Save changes" }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
