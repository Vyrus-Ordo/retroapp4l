<template>
  <div class="flex flex-col gap-8 lg:flex-row lg:items-start lg:justify-between min-h-[60vh]">
    <div class="flex-1 panel p-8 flex flex-col gap-4">
      <div class="flex items-center justify-between gap-4">
        <div>
          <h1 class="text-xl font-light text-white mb-2">Lobby</h1>
          <p class="text-zinc-500">Invite participants and wait for everyone to join before starting.</p>
        </div>
        <div class="flex items-center gap-4">
          <button v-if="isFacilitator" class="button-primary py-1.5 text-sm" @click="$emit('advance-phase')">Start session</button>
        </div>
      </div>
      <div class="mt-4 flex flex-col gap-2">
        <div class="flex items-center gap-2">
          <span class="mdi mdi-link-variant text-[#00f2ff]/60 text-xl" />
          <span class="text-sm">Invite link:</span>
          <span class="font-mono text-xs bg-white/5 border border-white/10 px-2 py-1 rounded text-zinc-400">{{ inviteLink || 'Unavailable' }}</span>
          <button v-if="inviteLink" class="button-secondary ml-2" @click="$emit('copy-invite-link')">Copy</button>
        </div>
        <div class="flex items-center gap-2">
          <span class="mdi mdi-account-multiple-outline text-[#00f2ff]/60 text-xl" />
          <span class="text-sm">Connected participants:</span>
          <span class="font-semibold">{{ participants.length }}</span>
        </div>
      </div>

    </div>
    <div class="flex-1 panel p-8 flex flex-col gap-4">
      <h2 class="text-lg font-light text-white">How it works</h2>
      <ul class="list-disc pl-5 text-zinc-500 text-sm space-y-1">
        <li>Invite the team via the link above</li>
        <li>Confirm everyone is present</li>
        <li>Advance to the action check</li>
        <li>Proceed through the phases until closing</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps({
  inviteLink: String,
  isFacilitator: Boolean,
  participants: Array
})
</script>
