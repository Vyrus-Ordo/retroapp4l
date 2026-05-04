import { defineStore } from "pinia"

import type { Participant } from "~/utils/types"

export type InviteStatus = "active" | "blocked" | "temporarily_open"

interface ParticipantsState {
  participants: Participant[]
  onlineIds: string[]
  accessLog: string[]
  inviteStatus: InviteStatus
  inviteExpiresAt: string | null
}

export const useParticipantStore = defineStore("participants", {
  state: (): ParticipantsState => ({
    participants: [],
    onlineIds: [],
    accessLog: [],
    inviteStatus: "blocked",
    inviteExpiresAt: null,
  }),
  getters: {
    onlineCount: (state) => state.onlineIds.length || state.participants.length,
  },
  actions: {
    hydrate(participants: Participant[]) {
      this.participants = participants
      this.onlineIds = participants.map((participant) => participant.user)
    },
    pushLog(message: string) {
      this.accessLog = [message, ...this.accessLog].slice(0, 20)
    },
    markJoined(payload: { user_id: string; participant_id?: string | null; name: string }) {
      const existingParticipant = this.participants.find((participant) => participant.user === payload.user_id)
      if (!existingParticipant) {
        this.participants = [
          ...this.participants,
          {
            id: payload.participant_id ?? payload.user_id,
            user: payload.user_id,
            user_name: payload.name,
            user_email: "",
            votes_remaining: 0,
            joined_at: new Date().toISOString(),
          },
        ]
      }
      if (!this.onlineIds.includes(payload.user_id)) {
        this.onlineIds.push(payload.user_id)
      }
      this.pushLog(`${payload.name} joined the session.`)
    },
    markLeft(userId: string) {
      this.onlineIds = this.onlineIds.filter((candidate) => candidate !== userId)
    },
    setInviteStatus(inviteStatus: InviteStatus, expiresAt: string | null = null) {
      this.inviteStatus = inviteStatus
      this.inviteExpiresAt = expiresAt
      if (inviteStatus === "temporarily_open") {
        this.pushLog(`Link reopened temporarily.`)
      } else if (inviteStatus === "blocked") {
        this.pushLog(`Link auto-blocked.`)
      }
    },
  },
})