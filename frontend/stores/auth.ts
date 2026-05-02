import { defineStore } from "pinia"

import type { AuthResponse, User } from "~/utils/types"

const STORAGE_KEY = "retroapp4l-auth"

interface AuthState {
  user: User | null
  access: string
  refresh: string
  ready: boolean
  error: string | null
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    user: null,
    access: "",
    refresh: "",
    ready: false,
    error: null,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.access),
  },
  actions: {
    init() {
      if (!import.meta.client || this.ready) {
        return
      }

      const raw = window.localStorage.getItem(STORAGE_KEY)
      if (raw) {
        const saved = JSON.parse(raw) as Omit<AuthState, "ready" | "error">
        this.user = saved.user
        this.access = saved.access
        this.refresh = saved.refresh
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
          user: this.user,
          access: this.access,
          refresh: this.refresh,
        }),
      )
    },
    clear() {
      this.user = null
      this.access = ""
      this.refresh = ""
      this.error = null
      if (import.meta.client) {
        window.localStorage.removeItem(STORAGE_KEY)
      }
    },
    async login(payload: { email: string; password: string }) {
      const api = useApiClient()
      const response = await api.post<AuthResponse, typeof payload>("/auth/login/", payload, false)
      this.user = response.user
      this.access = response.access
      this.refresh = response.refresh
      this.persist()
      return response
    },
    async register(payload: { name: string; email: string; password: string }) {
      const api = useApiClient()
      const response = await api.post<AuthResponse, typeof payload>("/auth/register/", payload, false)
      this.user = response.user
      this.access = response.access
      this.refresh = response.refresh
      this.persist()
      return response
    },
    async logout() {
      const api = useApiClient()
      if (this.refresh) {
        try {
          await api.post<void, { refresh: string }>("/auth/logout/", { refresh: this.refresh })
        } catch {
          // Ignore logout transport errors and clear local state.
        }
      }
      this.clear()
    },
  },
})