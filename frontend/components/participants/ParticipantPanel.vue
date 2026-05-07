<script setup lang="ts">
import { NoSymbolIcon, UserCircleIcon, UserPlusIcon } from "@heroicons/vue/24/outline"
import { LockClosedIcon, LockOpenIcon } from "@heroicons/vue/24/solid"

import type { InviteStatus } from "~/stores/participants"
import type { Participant } from "~/utils/types"

const props = defineProps<{
  participants: Participant[]
  onlineIds: string[]
  accessLog: string[]
  inviteStatus: InviteStatus
  inviteLink?: string | null
  inviteExpiresAt?: string | null
  facilitator?: boolean
  allowEntryLoading?: boolean
}>()

defineEmits<{
  allowEntry: []
  'copy-invite-link': []
}>()

// Countdown timer derived from inviteExpiresAt
const secondsLeft = ref(0)
let countdownInterval: ReturnType<typeof setInterval> | null = null

function updateCountdown() {
  if (!props.inviteExpiresAt) {
    secondsLeft.value = 0
    return
  }
  const diff = Math.max(0, Math.ceil((new Date(props.inviteExpiresAt).getTime() - Date.now()) / 1000))
  secondsLeft.value = diff
}

watch(
  () => props.inviteExpiresAt,
  (val) => {
    if (countdownInterval) clearInterval(countdownInterval)
    if (val && props.inviteStatus === "temporarily_open") {
      updateCountdown()
      countdownInterval = setInterval(updateCountdown, 1000)
    } else {
      secondsLeft.value = 0
    }
  },
  { immediate: true },
)

onUnmounted(() => {
  if (countdownInterval) clearInterval(countdownInterval)
})

const inviteStatusLabel = computed(() => {
  if (props.inviteStatus === "active") return "OPEN"
  if (props.inviteStatus === "temporarily_open") return `TEMPORARILY OPEN (${secondsLeft.value}s)`
  return "BLOCKED"
})

const inviteStatusColor = computed(() => {
  if (props.inviteStatus === "active") return "text-success-600"
  if (props.inviteStatus === "temporarily_open") return "text-warning-500"
  return "text-danger-500"
})
</script>

<template>
  <section aria-label="Participants panel">
    <!-- Participants list -->
    <div class="flex items-center justify-between gap-3">
      <h2 class="text-lg font-light leading-6 text-white">
        Participants
        <span class="ml-1 text-sm font-light text-zinc-600">({{ onlineIds.length || participants.length }} online)</span>
      </h2>
    </div>

    <ul class="mt-4 space-y-3" aria-label="Participant list">
      <li
        v-for="participant in participants"
        :key="participant.id"
        class="flex items-center justify-between gap-3 text-sm text-zinc-500"
      >
        <span class="inline-flex items-center gap-2">
          <UserCircleIcon class="h-5 w-5 text-[#00f2ff]/60" aria-hidden="true" />
          {{ participant.user_name }}
        </span>
        <span
          class="text-xs"
          :class="onlineIds.includes(participant.user) ? 'text-success-600' : 'text-slate-400'"
          :aria-label="onlineIds.includes(participant.user) ? 'Online' : 'Offline'"
        >
          {{ onlineIds.includes(participant.user) ? "online" : "offline" }}
        </span>
      </li>
      <li v-if="!participants.length" class="text-sm text-zinc-600">No participants yet.</li>
    </ul>

    <!-- Admin section — facilitator only -->
    <div v-if="facilitator" class="mt-6 rounded-xl border border-white/8 p-4" style="background: rgba(255,255,255,0.03)">
      <div class="flex items-center gap-2">
        <component
          :is="inviteStatus === 'blocked' ? LockClosedIcon : LockOpenIcon"
          class="h-4 w-4 flex-shrink-0"
          :class="inviteStatus === 'blocked' ? 'text-danger-500' : 'text-success-600'"
          aria-hidden="true"
        />
        <span class="text-sm font-light text-zinc-300">Invite link:</span>
        <span class="text-sm font-semibold" :class="inviteStatusColor">{{ inviteStatusLabel }}</span>
      </div>

      <p v-if="inviteStatus === 'blocked'" class="mt-2 text-sm text-slate-500">
        Session has already started. New participants cannot join.
      </p>
      <p v-else-if="inviteStatus === 'temporarily_open'" class="mt-2 text-sm text-slate-500">
        Link will auto-block when someone joins or the countdown ends.
      </p>

      <button
        v-if="inviteStatus !== 'active'"
        type="button"
        class="mt-4 inline-flex w-full items-center justify-center rounded-lg border border-[#00f2ff] px-4 py-2 text-sm font-medium text-[#00f2ff] transition-all duration-200 hover:bg-[#00f2ff]/10 hover:shadow-glow disabled:cursor-not-allowed disabled:border-white/15 disabled:text-zinc-600"
        :disabled="allowEntryLoading || inviteStatus === 'temporarily_open'"
        :aria-label="inviteStatus === 'temporarily_open' ? 'Entry window is already open' : 'Allow new participants to join for 2 minutes'"
        @click="$emit('allowEntry')"
      >
        <UserPlusIcon class="mr-2 h-5 w-5" aria-hidden="true" />
        <span v-if="allowEntryLoading">Opening...</span>
        <span v-else-if="inviteStatus === 'temporarily_open'">Entry open ({{ secondsLeft }}s)</span>
        <span v-else>Allow new entry</span>
      </button>

      <p v-else class="mt-3 inline-flex items-center gap-1 text-sm text-success-600">
        <LockOpenIcon class="h-4 w-4" aria-hidden="true" />
        Invite link is open (lobby phase).
      </p>
    </div>

    <!-- Invite link — above access log -->
    <div class="mt-6">
      <h3 class="text-sm font-light text-zinc-400">Invite link</h3>
      <div class="mt-2 flex items-center gap-2">
        <span class="mdi mdi-link-variant text-[#00f2ff]/60 text-lg" />
        <span class="font-mono text-xs bg-white/5 border border-white/10 px-2 py-1 rounded text-zinc-400 truncate max-w-[200px]">{{ inviteLink || 'Unavailable' }}</span>
        <button v-if="inviteLink" class="button-secondary py-1 px-3 text-xs" @click="$emit('copy-invite-link')">Copy</button>
      </div>
    </div>

    <!-- Access log -->
    <div class="mt-6">
      <h3 class="text-sm font-light text-zinc-400">Access log</h3>
      <ul class="mt-3 space-y-2 text-xs text-zinc-600" aria-label="Access log">
        <li v-for="(item, index) in accessLog" :key="index" class="flex items-start gap-1">
          <NoSymbolIcon v-if="item.includes('blocked')" class="mt-0.5 h-3 w-3 flex-shrink-0 text-danger-500" aria-hidden="true" />
          <UserPlusIcon v-else-if="item.includes('joined')" class="mt-0.5 h-3 w-3 flex-shrink-0 text-success-500" aria-hidden="true" />
          <LockOpenIcon v-else class="mt-0.5 h-3 w-3 flex-shrink-0 text-warning-500" aria-hidden="true" />
          {{ item }}
        </li>
        <li v-if="!accessLog.length" class="text-zinc-700">Realtime access events will appear here.</li>
      </ul>
    </div>
  </section>
</template>
