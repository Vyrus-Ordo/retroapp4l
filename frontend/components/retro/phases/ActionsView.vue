<script setup lang="ts">
import {
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
  if (status === 'done') return 'text-[#22c55e] border border-[#22c55e]/25'
  if (status === 'in_progress') return 'text-[#00f2ff] border border-[#00f2ff]/25'
  return 'text-zinc-500 border border-white/10'
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
        <h1 class="text-xl font-light text-white">Actions Review</h1>
        <p class="mt-1 text-sm text-zinc-500">
          Review and confirm the action items created during the discussion.
        </p>
      </div>
      <div class="flex items-center gap-4">
        <button v-if="isFacilitator" class="button-primary py-1.5 text-sm" type="button" @click="handleCloseClick">
          Close retrospective
        </button>
        <span
          v-if="current?.timer_duration_seconds"
          class="text-lg font-semibold tabular-nums"
          :class="timerStore.secondsRemaining < 60 ? 'text-danger-500' : 'text-[#00f2ff]'"
        >
          {{ timerStore.formatted }}
        </span>
      </div>
    </div>

    <!-- Action items list -->
    <div class="space-y-3">
      <article
        v-for="action in actionItems"
        :key="action.id"
        class="rounded-xl border border-white/10 p-4 backdrop-blur-sm"
        style="background: rgba(255,255,255,0.04)"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0 flex-1">
            <p class="text-sm font-light leading-5 text-zinc-200">
              {{ action.description }}
            </p>
            <div class="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-zinc-500">
              <span v-if="action.assignee_name">
                Assignee: <span class="font-light text-zinc-300">{{ action.assignee_name }}</span>
              </span>
              <span v-else class="text-danger-500">No assignee</span>
              <span v-if="action.due_date">
                Due: <span class="font-light text-zinc-300">{{ action.due_date }}</span>
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
              v-if="isFacilitator"
              class="rounded p-1 text-zinc-600 hover:text-[#00f2ff] transition"
              title="Edit"
              type="button"
              @click="emit('edit-action', action)"
            >
              <PencilSquareIcon class="h-4 w-4" />
            </button>
            <button
              v-if="isFacilitator"
              class="rounded p-1 text-zinc-600 hover:text-danger-500 transition"
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
        class="rounded-xl border border-dashed border-white/10 p-8 text-center text-sm text-zinc-600"
      >
        No action items yet. Add the first one.
      </div>
    </div>





    <!-- Confirmation dialog -->
    <div
      v-if="confirmClose"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm px-4"
    >
      <div class="w-full max-w-md rounded-xl border border-[#00f2ff]/15 p-6" style="background: rgba(10,10,10,0.95)">
        <h2 class="text-lg font-light text-white">Close retrospective?</h2>
        <p class="mt-2 text-sm text-zinc-500">
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

