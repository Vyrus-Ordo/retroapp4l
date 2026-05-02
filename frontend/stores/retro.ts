import { defineStore } from "pinia"

import type {
  ActionItem,
  Card,
  DiscussionFocusPayload,
  HistoryDetail,
  HistoryItem,
  Milestone,
  PreviousActionsResponse,
  RetrospectiveDetail,
  RetrospectiveSummary,
  RetroPhase,
  Vote,
} from "~/utils/types"

interface RetroState {
  retrospectives: RetrospectiveSummary[]
  current: RetrospectiveDetail | null
  cards: Card[]
  votes: Vote[]
  actionItems: ActionItem[]
  previousActions: PreviousActionsResponse
  history: HistoryItem[]
  historyDetail: HistoryDetail | null
  selectedCardIds: string[]
  previewPhase: RetroPhase | null
  discussionFocus: DiscussionFocusPayload | null
  error: string | null
  loading: boolean
}

function upsertById<T extends { id: string }>(collection: T[], item: T) {
  const index = collection.findIndex((candidate) => candidate.id === item.id)
  if (index === -1) {
    return [item, ...collection]
  }

  return collection.map((candidate, candidateIndex) => (candidateIndex === index ? item : candidate))
}

export const useRetroStore = defineStore("retro", {
  state: (): RetroState => ({
    retrospectives: [],
    current: null,
    cards: [],
    votes: [],
    actionItems: [],
    previousActions: { retrospective_id: null, action_items: [] },
    history: [],
    historyDetail: null,
    selectedCardIds: [],
    previewPhase: null,
    discussionFocus: null,
    error: null,
    loading: false,
  }),
  getters: {
    activePhase: (state) => state.previewPhase || state.current?.status || "setup",
    isFacilitator: (state) => (userId?: string) => state.current?.facilitator === userId,
    cardsByColumn: (state) => {
      return {
        loved: state.cards.filter((card) => card.column === "loved"),
        loathed: state.cards.filter((card) => card.column === "loathed"),
        longed: state.cards.filter((card) => card.column === "longed"),
        learned: state.cards.filter((card) => card.column === "learned"),
      }
    },
  },
  actions: {
    async fetchDashboard() {
      const api = useApiClient()
      this.retrospectives = await api.get<RetrospectiveSummary[]>("/retrospectives/")
    },
    async createRetrospective(payload: {
      title: string
      sprint_name: string
      description: string
      team_key: string
      max_votes_per_user: number
      skip_check_phase: boolean
      milestones: Array<{ category: string; description: string }>
    }) {
      const api = useApiClient()
      const retrospective = await api.post<RetrospectiveDetail, Omit<typeof payload, "milestones">>(
        "/retrospectives/",
        {
          title: payload.title,
          sprint_name: payload.sprint_name,
          description: payload.description,
          team_key: payload.team_key,
          max_votes_per_user: payload.max_votes_per_user,
          skip_check_phase: payload.skip_check_phase,
        },
      )

      for (const milestone of payload.milestones) {
        await api.post<Milestone, typeof milestone>(`/retrospectives/${retrospective.id}/milestones/`, milestone)
      }

      return retrospective.id
    },
    async fetchSession(retrospectiveId: string) {
      const api = useApiClient()
      this.loading = true
      this.error = null

      try {
        this.current = await api.get<RetrospectiveDetail>(`/retrospectives/${retrospectiveId}/`)
        this.cards = await api.get<Card[]>(`/retrospectives/${retrospectiveId}/cards/`)
        this.votes = await api.get<Vote[]>(`/retrospectives/${retrospectiveId}/votes/`)
        this.previewPhase = null
        this.discussionFocus = this.current.focus_card_id
          ? this.cards
              .filter((card) => card.id === this.current?.focus_card_id)
              .map((card) => ({
                card_id: card.id,
                author: card.author_name,
                column: card.column,
                content: card.content,
                vote_count: card.vote_count,
              }))[0] || null
          : null

        try {
          this.actionItems = await api.get<ActionItem[]>(`/retrospectives/${retrospectiveId}/action-items/`)
        } catch {
          this.actionItems = []
        }

        try {
          this.previousActions = await api.get<PreviousActionsResponse>(`/retrospectives/${retrospectiveId}/previous-actions/`)
        } catch {
          this.previousActions = { retrospective_id: null, action_items: [] }
        }
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Unable to load retrospective."
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchHistory() {
      const api = useApiClient()
      this.history = await api.get<HistoryItem[]>("/retrospectives/history/")
    },
    async fetchHistoryDetail(retrospectiveId: string) {
      const api = useApiClient()
      this.historyDetail = await api.get<HistoryDetail>(`/retrospectives/${retrospectiveId}/detail/`)
    },
    async fetchTeamSuggestions(query = "") {
      const api = useApiClient()
      const response = await api.get<{ suggestions: string[] }>(`/teams/suggestions/${query ? `?q=${encodeURIComponent(query)}` : ""}`)
      return response.suggestions
    },
    async createCard(retrospectiveId: string, payload: { column: string; content: string; position?: number }) {
      const api = useApiClient()
      const card = await api.post<Card, typeof payload>(`/retrospectives/${retrospectiveId}/cards/`, payload)
      this.cards = upsertById(this.cards, card)
      return card
    },
    async updateCard(retrospectiveId: string, cardId: string, payload: { content: string }) {
      const api = useApiClient()
      const card = await api.patch<Card, typeof payload>(`/retrospectives/${retrospectiveId}/cards/${cardId}/`, payload)
      this.cards = upsertById(this.cards, card)
    },
    async deleteCard(retrospectiveId: string, cardId: string) {
      const api = useApiClient()
      await api.delete<unknown>(`/retrospectives/${retrospectiveId}/cards/${cardId}/`)
      this.cards = this.cards.filter((card) => card.id !== cardId)
      this.selectedCardIds = this.selectedCardIds.filter((candidate) => candidate !== cardId)
    },
    toggleCardSelection(cardId: string) {
      if (this.selectedCardIds.includes(cardId)) {
        this.selectedCardIds = this.selectedCardIds.filter((candidate) => candidate !== cardId)
        return
      }
      this.selectedCardIds.push(cardId)
    },
    clearSelection() {
      this.selectedCardIds = []
    },
    async groupSelected(retrospectiveId: string) {
      if (this.selectedCardIds.length < 2) {
        return
      }
      const api = useApiClient()
      await api.post(`/retrospectives/${retrospectiveId}/cards/group/`, { card_ids: this.selectedCardIds })
      await this.fetchSession(retrospectiveId)
    },
    async ungroupCard(retrospectiveId: string, cardId: string) {
      const api = useApiClient()
      await api.post(`/retrospectives/${retrospectiveId}/cards/${cardId}/ungroup/`)
      await this.fetchSession(retrospectiveId)
    },
    async castVote(retrospectiveId: string, cardId: string) {
      const api = useApiClient()
      await api.post(`/retrospectives/${retrospectiveId}/cards/${cardId}/vote/`)
      await this.fetchSession(retrospectiveId)
    },
    async revokeVote(retrospectiveId: string, cardId: string) {
      const api = useApiClient()
      await api.delete(`/retrospectives/${retrospectiveId}/cards/${cardId}/vote/`)
      await this.fetchSession(retrospectiveId)
    },
    async saveActionItem(
      retrospectiveId: string,
      payload: {
        id?: string
        description: string
        assignee_id: string
        card_id?: string | null
        due_date?: string | null
        status?: string
        external_tracker_url?: string | null
      },
    ) {
      const api = useApiClient()
      if (payload.id) {
        await api.patch(`/retrospectives/${retrospectiveId}/action-items/${payload.id}/`, payload)
      } else {
        await api.post(`/retrospectives/${retrospectiveId}/action-items/`, payload)
      }
      this.actionItems = await api.get<ActionItem[]>(`/retrospectives/${retrospectiveId}/action-items/`)
    },
    async deleteActionItem(retrospectiveId: string, actionId: string) {
      const api = useApiClient()
      await api.delete(`/retrospectives/${retrospectiveId}/action-items/${actionId}/`)
      this.actionItems = this.actionItems.filter((item) => item.id !== actionId)
    },
    async updatePreviousActionStatus(retrospectiveId: string, actionId: string, status: string) {
      const api = useApiClient()
      await api.put(`/retrospectives/${retrospectiveId}/previous-actions/${actionId}/status/`, { status })
      this.previousActions = {
        ...this.previousActions,
        action_items: this.previousActions.action_items.map((item) =>
          item.id === actionId ? { ...item, status: status as ActionItem["status"] } : item,
        ),
      }
    },
    async focusCard(retrospectiveId: string, cardId: string) {
      const api = useApiClient()
      this.discussionFocus = await api.post<DiscussionFocusPayload, { card_id: string }>(
        `/retrospectives/${retrospectiveId}/focus-card/`,
        { card_id: cardId },
      )
    },
    async nextFocusCard(retrospectiveId: string) {
      const api = useApiClient()
      this.discussionFocus = await api.post<DiscussionFocusPayload>(`/retrospectives/${retrospectiveId}/next-card/`)
    },
    async closeRetrospective(retrospectiveId: string) {
      const api = useApiClient()
      await api.post(`/retrospectives/${retrospectiveId}/close/`, { confirm: true })
      if (this.current) {
        this.current = { ...this.current, status: "closed", closed_at: new Date().toISOString() }
      }
    },
    setPreviewPhase(phase: RetroPhase | null) {
      this.previewPhase = phase
    },
    applySocketEvent(event: Record<string, unknown>) {
      const type = String(event.type || "")

      if (type === "phase.changed" && this.current) {
        this.current = { ...this.current, status: event.phase as RetroPhase }
        this.previewPhase = null
      }

      if (type === "card.created" && event.card) {
        this.cards = upsertById(this.cards, event.card as Card)
      }

      if (type === "card.updated") {
        this.cards = this.cards.map((card) =>
          card.id === event.card_id ? { ...card, content: String(event.content || card.content) } : card,
        )
      }

      if (type === "card.deleted") {
        this.cards = this.cards.filter((card) => card.id !== event.card_id)
      }

      if (type === "card.grouped") {
        this.cards = this.cards.map((card) =>
          card.id === event.card_id ? { ...card, group: String(event.group_id) } : card,
        )
      }

      if (type === "card.ungrouped") {
        this.cards = this.cards.map((card) => (card.id === event.card_id ? { ...card, group: null } : card))
      }

      if (type === "vote.cast") {
        const targetCardId = String(event.card_id || (event.vote as Vote | undefined)?.card || "")
        this.cards = this.cards.map((card) =>
          card.id === targetCardId ? { ...card, vote_count: card.vote_count + 1 } : card,
        )
      }

      if (type === "vote.revoked") {
        this.cards = this.cards.map((card) =>
          card.id === event.card_id ? { ...card, vote_count: Math.max(0, card.vote_count - 1) } : card,
        )
      }

      if (type === "action.check_updated") {
        this.previousActions = {
          ...this.previousActions,
          action_items: this.previousActions.action_items.map((item) =>
            item.id === event.action_id ? { ...item, status: event.status as ActionItem["status"] } : item,
          ),
        }
      }

      if (type === "discussion.focus_updated") {
        this.discussionFocus = {
          card_id: String(event.card_id),
          author: String(event.author),
          column: event.column as DiscussionFocusPayload["column"],
          content: String(event.content),
          vote_count: Number(event.vote_count || 0),
        }
      }
    },
  },
})