<script setup lang="ts">
import {
  PlusIcon,
  PencilSquareIcon,
  TrashIcon,
  CheckCircleIcon,
  ClockIcon,
  MinusCircleIcon,
} from "@heroicons/vue/24/outline"

import type { ActionItem } from "~/utils/types"

const props = defineProps<{
  current: any
  isFacilitator: boolean
  retroStore: any
  timerStore: any
  participants: any[]
}>()

const emit = defineEmits<{
  "advance-phase": []
  "close-session": []
  "open-action-modal": []
  "edit-action": [action: ActionItem]
  "delete-action": [actionId: string]
}>()

const route = useRoute()
const retrospectiveId = computed(() => String(route.params.id))

const confirmClose = ref(false)

const actionItems = computed<ActionItem[]>(() => props.retroStore.actionItems)

const hasUnassigned = computed(() =>
  actionItems.value.some((item) => !item.assignee),
)

function statusIcon(status: ActionItem["status"]) {
  if (status === "done") return CheckCircleIcon
  if (status === "in_progress") return ClockIcon
  return MinusCircleIcon
}

function statusLabel(status: ActionItem["status"]) {
  if (status === "done") return "Done"
  if (status === "in_progress") return "In progress"
  return "Not started"
}

function statusClass(status: ActionItem["status"]) {
  if (status === "done") return "text-success-600 bg-success-50"
  if (status === "in_progress") return "text-brand-600 bg-brand-50"
  return "text-slate-500 bg-slate-100"
}

async function handleDelete(actionId: string) {
  await props.retroStore.deleteActionItem(retrospectiveId.value, actionId)
}

function handleCloseClick() {
  confirmClose.value = true
}

function cancelClose() {
  confirmClose.value = false
}

async function confirmCloseSession() {
  confirmClose.value = false
  emit("close-session")
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Header -->
    <div class="flex items-center justify-between gap-4">
      <div>
        <h1 class="text-xl font-bold text-slate-900">Actions</h1>
        <p class="mt-1 text-sm text-slate-500">
          Record action items with description, assignee, and due date.
        </p>
      </div>
      <span
        v-if="current?.timer_duration_seconds"
        class="text-lg font-semibold tabular-nums"
        :class="timerStore.secondsRemaining < 60 ? 'text-danger-500' : 'text-slate-900'"
      >
        {{ timerStore.formatted }}
      </span>
    </div>

    <!-- Action items list -->
    <div class="space-y-3">
      <article
        v-for="action in actionItems"
        :key="action.id"
        class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium leading-5 text-slate-900">
              {{ action.description }}
            </p>
            <div class="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-500">
              <span v-if="action.assignee_name">
                Assignee: <span class="font-medium text-slate-700">{{ action.assignee_name }}</span>
              </span>
              <span v-else class="text-danger-500">No assignee</span>
              <span v-if="action.due_date">
                Due: <span class="font-medium text-slate-700">{{ action.due_date }}</span>
              </span>
            </div>
          </div>

          <div class="flex shrink-0 items-center gap-2">
            <span
              class="inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold"
              :class="statusClass(action.status)"
            >
              <component :is="statusIcon(action.status)" class="h-3.5 w-3.5" />
              {{ statusLabel(action.status) }}
            </span>

            <button
              class="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition"
              title="Edit"
              type="button"
              @click="emit('edit-action', action)"
            >
              <PencilSquareIcon class="h-4 w-4" />
            </button>
            <button
              class="rounded p-1 text-slate-400 hover:bg-danger-50 hover:text-danger-600 transition"
              title="Delete"
              type="button"
              @click="handleDelete(action.id)"
            >
              <TrashIcon class="h-4 w-4" />
            </button>
          </div>
        </div>
      </article>

      <div
        v-if="actionItems.length === 0"
        class="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-8 text-center text-sm text-slate-400"
      >
        No action items yet. Add the first one.
      </div>
    </div>

    <!-- Add action button -->
    <div v-if="isFacilitator">
      <button class="button-secondary flex items-center gap-2" type="button" @click="emit('open-action-modal')">
        <PlusIcon class="h-4 w-4" />
        New action item
      </button>
    </div>

    <!-- Close session -->
    <div v-if="isFacilitator" class="flex justify-end border-t border-slate-100 pt-4">
      <button class="button-primary" type="button" @click="handleCloseClick">
        Close retrospective
      </button>
    </div>

    <!-- Confirmation dialog -->
    <div
      v-if="confirmClose"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4"
    >
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h2 class="text-lg font-semibold text-slate-900">Close retrospective?</h2>
        <p class="mt-2 text-sm text-slate-600">
          This will permanently close the session and save it to history. This cannot be undone.
        </p>
        <p v-if="hasUnassigned" class="mt-2 rounded-lg bg-warning-50 px-3 py-2 text-sm text-warning-700">
          Warning: {{ actionItems.filter((a) => !a.assignee).length }} action item(s) have no assignee.
        </p>
        <div class="mt-6 flex justify-end gap-3">
          <button class="button-secondary" type="button" @click="cancelClose">Cancel</button>
          <button class="button-primary" type="button" @click="confirmCloseSession">Close retrospective</button>
        </div>
      </div>
    </div>
  </div>
</template>

