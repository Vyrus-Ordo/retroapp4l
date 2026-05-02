import { defineStore } from "pinia"

const STORAGE_KEY = "retroapp4l-guest-profile"

interface GuestProfileState {
  name: string
  email: string
  ready: boolean
}

export const useGuestStore = defineStore("guest", {
  state: (): GuestProfileState => ({
    name: "",
    email: "",
    ready: false,
  }),
  actions: {
    init() {
      if (!import.meta.client || this.ready) {
        return
      }

      const raw = window.localStorage.getItem(STORAGE_KEY)
      if (raw) {
        const saved = JSON.parse(raw) as Omit<GuestProfileState, "ready">
        this.name = saved.name || ""
        this.email = saved.email || ""
      }
      this.ready = true
    },
    persist() {
      if (!import.meta.client) {
        return
      }
      window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          name: this.name,
          email: this.email,
        }),
      )
    },
    setProfile(payload: { name: string; email?: string }) {
      this.name = payload.name.trim()
      this.email = payload.email?.trim() || ""
      this.persist()
    },
    clear() {
      this.name = ""
      this.email = ""
      if (import.meta.client) {
        window.localStorage.removeItem(STORAGE_KEY)
      }
    },
  },
})