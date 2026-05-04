<script setup lang="ts">
import type { ActionItem, Card, Participant } from "~/utils/types"

const props = defineProps<{
  participants: Participant[]
  cards: Card[]
  modelValue: boolean
  initialAction?: ActionItem | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  submit: [payload: {
    id?: string
    description: string
    assignee_id: string
    card_id: string | null
    due_date: string | null
    status: string
    external_tracker_url: string | null
  }]
}>()

const form = reactive({
  description: props.initialAction?.description || "",
  assignee_id: props.initialAction?.participant_id || "",
  card_id: props.initialAction?.card || "",
  due_date: props.initialAction?.due_date || "",
  status: props.initialAction?.status || "not_started",
  external_tracker_url: props.initialAction?.external_tracker_url || "",
})

watch(
  () => props.initialAction,
  (action) => {
    form.description = action?.description || ""
    form.assignee_id = action?.participant_id || ""
    form.card_id = action?.card || ""
    form.due_date = action?.due_date || ""
    form.status = action?.status || "not_started"
    form.external_tracker_url = action?.external_tracker_url || ""
  },
  { immediate: true },
)

function close() {
  emit("update:modelValue", false)
}

function submit() {
  emit("submit", {
    id: props.initialAction?.id,
    description: form.description,
    assignee_id: form.assignee_id,
    card_id: form.card_id || null,
    due_date: form.due_date || null,
    status: form.status,
    external_tracker_url: form.external_tracker_url || "",
  })
  close()
}
</script>

<template>
  <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4">
    <div class="w-full max-w-2xl rounded-xl bg-white p-6 shadow-lg">
      <h2 class="text-lg font-semibold text-slate-900">{{ initialAction ? 'Edit action item' : 'Create action item' }}</h2>
      <div class="mt-4 grid gap-4 md:grid-cols-2">
        <textarea v-model="form.description" class="field-input md:col-span-2 min-h-28" placeholder="Describe the action item." />
        <select v-model="form.assignee_id" class="field-input">
          <option value="">Select assignee</option>
          <option v-for="participant in participants" :key="participant.id" :value="participant.id">{{ participant.user_name }}</option>
        </select>
        <select v-model="form.card_id" class="field-input">
          <option value="">No source card</option>
          <option v-for="card in cards" :key="card.id" :value="card.id">{{ card.content }}</option>
        </select>
        <input v-model="form.due_date" class="field-input" type="date">
        <select v-model="form.status" class="field-input">
          <option value="not_started">Not started</option>
          <option value="in_progress">In progress</option>
          <option value="done">Done</option>
        </select>
        <input v-model="form.external_tracker_url" class="field-input md:col-span-2" placeholder="External tracker URL (optional)">
      </div>
      <div class="mt-6 flex justify-end gap-3">
        <button class="button-secondary" type="button" @click="close">Cancel</button>
        <button class="button-primary" type="button" @click="submit">Save action item</button>
      </div>
    </div>
  </div>
</template>