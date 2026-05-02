import { defineStore } from "pinia"

import type { RetrospectiveDetail } from "~/utils/types"

interface TimerState {
  secondsRemaining: number
  paused: boolean
}

function calculateRemaining(retro: RetrospectiveDetail | null) {
  if (!retro?.timer_started_at || !retro.timer_duration_seconds) {
    return 0
  }

  const started = new Date(retro.timer_started_at).getTime()
  const paused = retro.timer_paused_at ? new Date(retro.timer_paused_at).getTime() : null
  const reference = paused || Date.now()
  const elapsed = Math.max(0, Math.floor((reference - started) / 1000))
  return Math.max(0, retro.timer_duration_seconds - elapsed)
}

export const useTimerStore = defineStore("timer", {
  state: (): TimerState => ({
    secondsRemaining: 0,
    paused: false,
  }),
  getters: {
    formatted: (state) => {
      const minutes = Math.floor(state.secondsRemaining / 60)
      const seconds = state.secondsRemaining % 60
      return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`
    },
  },
  actions: {
    hydrate(retro: RetrospectiveDetail | null) {
      this.secondsRemaining = calculateRemaining(retro)
      this.paused = Boolean(retro?.timer_paused_at)
    },
    setRemaining(seconds: number) {
      this.secondsRemaining = Math.max(0, seconds)
    },
    tick() {
      if (!this.paused && this.secondsRemaining > 0) {
        this.secondsRemaining -= 1
      }
    },
    pause(seconds: number) {
      this.paused = true
      this.setRemaining(seconds)
    },
    resume(seconds: number) {
      this.paused = false
      this.setRemaining(seconds)
    },
  },
})