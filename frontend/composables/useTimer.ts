import { playTimerExpiredAlert } from "~/utils/sound"

let intervalHandle: ReturnType<typeof setInterval> | null = null

export function useTimer() {
  const timerStore = useTimerStore()

  const toneClass = computed(() => {
    if (timerStore.secondsRemaining < 30) {
      return "text-danger-500"
    }
    if (timerStore.secondsRemaining < 60) {
      return "text-warning-500"
    }
    return "text-slate-900"
  })

  function start() {
    if (intervalHandle) {
      return
    }

    intervalHandle = window.setInterval(async () => {
      const before = timerStore.secondsRemaining
      timerStore.tick()
      if (before > 0 && timerStore.secondsRemaining === 0) {
        await playTimerExpiredAlert()
      }
    }, 1000)
  }

  function stop() {
    if (intervalHandle) {
      clearInterval(intervalHandle)
      intervalHandle = null
    }
  }

  onBeforeUnmount(() => {
    stop()
  })

  return {
    timerStore,
    toneClass,
    start,
    stop,
  }
}