<script setup lang="ts">
import { LockClosedIcon, UserCircleIcon, UserPlusIcon } from "@heroicons/vue/24/outline"

import type { Participant } from "~/utils/types"

defineProps<{
  participants: Participant[]
  onlineIds: string[]
  accessLog: string[]
  inviteBlocked: boolean
  inviteToken?: string | null
  facilitator?: boolean
}>()

defineEmits<{
  allowEntry: []
}>()
</script>

<template>
  <section>
    <div class="flex items-center justify-between gap-3">
      <h2 class="text-lg font-semibold leading-6 text-slate-900">Participants ({{ onlineIds.length || participants.length }} online)</h2>
    </div>

    <ul class="mt-4 space-y-3">
      <li v-for="participant in participants" :key="participant.id" class="flex items-center justify-between gap-3 text-sm text-slate-600">
        <span class="inline-flex items-center gap-2">
          <UserCircleIcon class="h-5 w-5 text-brand-500" />
          {{ participant.user_name }}
        </span>
        <span class="text-xs text-slate-400">{{ onlineIds.includes(participant.user) ? 'online' : 'offline' }}</span>
      </li>
    </ul>

    <div class="mt-6 rounded-xl bg-slate-50 p-4">
      <div class="inline-flex items-center gap-2 text-sm font-medium text-slate-900">
        <LockClosedIcon class="h-4 w-4 text-slate-500" />
        Invite link: {{ inviteBlocked ? 'BLOCKED' : 'OPEN' }}
      </div>
      <p class="mt-2 text-sm text-slate-600">
        <span v-if="inviteToken">Token: {{ inviteToken }}</span>
        <span v-else>Invite token becomes unavailable once the session is closed or revoked.</span>
      </p>
      <button v-if="facilitator" class="button-secondary mt-4 w-full" type="button" @click="$emit('allowEntry')">
        <UserPlusIcon class="mr-2 h-5 w-5" />
        Allow new entry
      </button>
    </div>

    <div class="mt-6">
      <h3 class="text-sm font-medium text-slate-900">Access log</h3>
      <ul class="mt-3 space-y-2 text-sm text-slate-600">
        <li v-for="item in accessLog" :key="item">{{ item }}</li>
        <li v-if="!accessLog.length" class="text-slate-400">Realtime access events will appear here.</li>
      </ul>
    </div>
  </section>
</template>