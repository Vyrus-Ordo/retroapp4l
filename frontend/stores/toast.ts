export type ToastType = "success" | "warning" | "error" | "info"

export interface Toast {
  id: number
  message: string
  type: ToastType
  duration: number
}

let _nextId = 1

export const useToastStore = defineStore("toast", {
  state: () => ({
    toasts: [] as Toast[],
  }),
  actions: {
    add(message: string, type: ToastType = "info", duration = 4000) {
      const id = _nextId++
      this.toasts.push({ id, message, type, duration })
      if (duration > 0) {
        setTimeout(() => this.remove(id), duration)
      }
      return id
    },
    remove(id: number) {
      this.toasts = this.toasts.filter((t) => t.id !== id)
    },
    success(message: string, duration = 4000) {
      return this.add(message, "success", duration)
    },
    warning(message: string, duration = 5000) {
      return this.add(message, "warning", duration)
    },
    error(message: string, duration = 6000) {
      return this.add(message, "error", duration)
    },
    info(message: string, duration = 4000) {
      return this.add(message, "info", duration)
    },
  },
})
