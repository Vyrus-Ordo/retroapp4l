import { playTimerExpiredAlert } from "~/utils/sound"

export function useWebSocket(retrospectiveId: MaybeRefOrGetter<string | null>) {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()
  const retroStore = useRetroStore()
  const participantStore = useParticipantStore()
  const timerStore = useTimerStore()
  const toastStore = useToastStore()
  const socket = shallowRef<WebSocket | null>(null)
  const connectionState = ref<"idle" | "connecting" | "connected" | "reconnecting" | "closed">("idle")
  const reconnectAttempts = ref(0)
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null

  function clearReconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  async function handleMessage(raw: MessageEvent<string>) {
    const payload = JSON.parse(raw.data) as Record<string, unknown>
    retroStore.applySocketEvent(payload)

    if (payload.type === "session.snapshot") {
      if (retroStore.current) {
        retroStore.current = {
          ...retroStore.current,
          status: String(payload.phase || retroStore.current.status) as typeof retroStore.current.status,
        }
      }
    }

    if (payload.type === "phase.changed") {
      const phase = String(payload.phase || "")
      const phaseLabels: Record<string, string> = {
        lobby: "Lobby",
        presentation: "Presentation",
        check: "Check",
        board: "Board",
        grouping: "Grouping",
        voting: "Voting",
        discussion: "Discussion",
        actions: "Actions",
        closed: "Closed",
      }
      if (phaseLabels[phase]) {
        toastStore.info(`Phase advanced: ${phaseLabels[phase]}`)
      }
    }

    if (payload.type === "card.created") {
      toastStore.success("Card created.")
    }

    if (payload.type === "vote.cast") {
      toastStore.success("Vote registered.")
    }

    if (payload.type === "participant.joined" || payload.type === "participant.joined_late") {
      participantStore.markJoined({ user_id: String(payload.user_id), name: String(payload.name) })
    }

    if (payload.type === "participant.left") {
      participantStore.markLeft(String(payload.user_id))
    }

    if (payload.type === "invite.status_updated") {
      participantStore.setInviteStatus(
        String(payload.invite_status) as "active" | "blocked" | "temporarily_open",
        payload.expires_at ? String(payload.expires_at) : null,
      )
    }

    if (payload.type === "timer.paused") {
      timerStore.pause(Number(payload.seconds_remaining || 0))
    }

    if (payload.type === "timer.resumed") {
      timerStore.resume(Number(payload.seconds_remaining || 0))
    }

    if (payload.type === "timer.sync") {
      timerStore.setRemaining(Number(payload.seconds_remaining || 0))
      if (Number(payload.seconds_remaining || 0) === 0) {
        await playTimerExpiredAlert()
      }
    }
  }

  function scheduleReconnect() {
    clearReconnect()
    connectionState.value = "reconnecting"
    const delay = Math.min(5000, 500 * (2 ** reconnectAttempts.value))
    reconnectTimer = window.setTimeout(() => {
      reconnectAttempts.value += 1
      connect()
    }, delay)
  }

  function connect() {
    const id = toValue(retrospectiveId)
    if (!import.meta.client || !id || !authStore.access) {
      return
    }

    clearReconnect()
    connectionState.value = reconnectAttempts.value ? "reconnecting" : "connecting"
    socket.value?.close()
    socket.value = new WebSocket(`${config.public.wsBase}/retrospectives/${id}/?token=${encodeURIComponent(authStore.access)}`)

    socket.value.onopen = () => {
      reconnectAttempts.value = 0
      connectionState.value = "connected"
    }

    socket.value.onmessage = handleMessage
    socket.value.onerror = () => {
      connectionState.value = "closed"
    }
    socket.value.onclose = () => {
      if (connectionState.value !== "closed") {
        scheduleReconnect()
      }
    }
  }

  function disconnect() {
    clearReconnect()
    connectionState.value = "closed"
    socket.value?.close()
    socket.value = null
  }

  function send(payload: Record<string, unknown>) {
    if (socket.value?.readyState === WebSocket.OPEN) {
      socket.value.send(JSON.stringify(payload))
    }
  }

  onMounted(connect)
  onBeforeUnmount(disconnect)

  watch(
    () => [toValue(retrospectiveId), authStore.access],
    ([id, access]) => {
      if (id && access) {
        connect()
      } else {
        disconnect()
      }
    },
  )

  return {
    connectionState,
    connect,
    disconnect,
    send,
  }
}