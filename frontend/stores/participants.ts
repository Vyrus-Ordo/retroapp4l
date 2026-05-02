import { defineStore } from "pinia"

import type { Participant } from "~/utils/types"

interface ParticipantsState {
  participants: Participant[]
  onlineIds: string[]
  accessLog: string[]
}

export const useParticipantStore = defineStore("participants", {
  state: (): ParticipantsState => ({
    participants: [],
    onlineIds: [],
    accessLog: [],
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
      this.accessLog = [message, ...this.accessLog].slice(0, 8)
    },
    markJoined(payload: { user_id: string; name: string }) {
      if (!this.onlineIds.includes(payload.user_id)) {
        this.onlineIds.push(payload.user_id)
      }
      this.pushLog(`${payload.name} joined the session.`)
    },
    markLeft(userId: string) {
      this.onlineIds = this.onlineIds.filter((candidate) => candidate !== userId)
    },
  },
})