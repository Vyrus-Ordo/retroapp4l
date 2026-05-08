import { defineStore } from "pinia"

import type {
  ActionItem,
  Card,
  DiscussionFocusPayload,
  HistoryDetail,
  HistoryItem,
  MilestoneCategory,
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

function upsertCard(collection: Card[], item: Card) {
  item = normalizeCard(item)
  const existing = collection.find((candidate) => candidate.id === item.id)
  return upsertById(collection, existing?.can_edit ? { ...item, can_edit: true } : item)
}

function normalizeCard(card: Card): Card {
  const group = card.group || card.group_parent_id || null
  return { ...card, group, group_parent_id: group }
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
        loved: state.cards.filter((card) => card.column === "loved" && !card.group),
        loathed: state.cards.filter((card) => card.column === "loathed" && !card.group),
        longed: state.cards.filter((card) => card.column === "longed" && !card.group),
        learned: state.cards.filter((card) => card.column === "learned" && !card.group),
      }
    },
    groupedChildrenByParentId: (state) => {
      const map: Record<string, Card[]> = {}
      for (const card of state.cards) {
        if (card.group) {
          if (!map[card.group]) map[card.group] = []
          map[card.group].push(card)
        }
      }
      return map
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
      allow_self_vote: boolean
      skip_check_phase: boolean
      phase_durations: Record<string, number>
      milestones: Array<{ category: MilestoneCategory; description: string }>
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
          allow_self_vote: payload.allow_self_vote,
          skip_check_phase: payload.skip_check_phase,
          phase_durations: payload.phase_durations,
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
        this.cards = (await api.get<Card[]>(`/retrospectives/${retrospectiveId}/cards/`)).map(normalizeCard)
        this.votes = await api.get<Vote[]>(`/retrospectives/${retrospectiveId}/votes/`)
        this.previewPhase = null
        this.discussionFocus = this.current.focus_card_id
          ? this.cards
              .filter((card) => card.id === this.current?.focus_card_id)
              .map((card) => ({
                card_id: card.id,
                author: card.author_name,
                author_display: card.author_display,
                is_anonymous: card.is_anonymous,
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
      this.loading = true
      this.error = null
      this.historyDetail = null

      try {
        this.historyDetail = await api.get<HistoryDetail>(`/retrospectives/${retrospectiveId}/detail/`)
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Unable to load retrospective history."
        throw error
      } finally {
        this.loading = false
      }
    },
    async fetchTeamSuggestions(query = "") {
      const api = useApiClient()
      const response = await api.get<{ suggestions: string[] }>(`/teams/suggestions/${query ? `?q=${encodeURIComponent(query)}` : ""}`)
      return response.suggestions
    },
    async createCard(retrospectiveId: string, payload: { column: string; content: string; is_anonymous?: boolean; position?: number }) {
      const api = useApiClient()
      const card = await api.post<Card, typeof payload>(`/retrospectives/${retrospectiveId}/cards/`, payload)
      this.cards = upsertCard(this.cards, card)
      return card
    },
    async updateCard(retrospectiveId: string, cardId: string, payload: { content: string; is_anonymous?: boolean }) {
      const api = useApiClient()
      const card = await api.patch<Card, typeof payload>(`/retrospectives/${retrospectiveId}/cards/${cardId}/`, payload)
      this.cards = upsertCard(this.cards, card)
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
      if (this.selectedCardIds.length > 0) {
        const card = this.cards.find((c) => c.id === cardId)
        const firstSelected = this.cards.find((c) => c.id === this.selectedCardIds[0])
        if (card && firstSelected && card.column !== firstSelected.column) {
          const toastStore = useToastStore()
          toastStore.error("Cards must be from the same column to be grouped.")
          return
        }
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
      const toastStore = useToastStore()
      try {
        await api.post(`/retrospectives/${retrospectiveId}/cards/group/`, {
          card_ids: this.selectedCardIds,
          group_parent_id: this.selectedCardIds[0],
        })
        this.cards = (await api.get<Card[]>(`/retrospectives/${retrospectiveId}/cards/`)).map(normalizeCard)
        this.selectedCardIds = []
      } catch (error) {
        toastStore.error(error instanceof Error ? error.message : "Failed to group cards.")
      }
    },
    async ungroupCard(retrospectiveId: string, cardId: string) {
      const api = useApiClient()
      await api.post(`/retrospectives/${retrospectiveId}/cards/${cardId}/ungroup/`)
      this.cards = (await api.get<Card[]>(`/retrospectives/${retrospectiveId}/cards/`)).map(normalizeCard)
    },
    async castVote(retrospectiveId: string, cardId: string) {
      const api = useApiClient()
      const response = await api.post<{ card_id: string; voter_id: string; votes_remaining: number; vote_id: string }>(
        `/retrospectives/${retrospectiveId}/cards/${cardId}/vote/`,
      )
      if (!this.votes.find((v) => v.card === response.card_id && v.voter === response.voter_id)) {
        this.votes = [...this.votes, { id: response.vote_id, card: response.card_id, voter: response.voter_id, created_at: new Date().toISOString() }]
      }
      if (this.current) {
        this.current = {
          ...this.current,
          participants: this.current.participants.map((p) =>
            p.user === response.voter_id ? { ...p, votes_remaining: response.votes_remaining } : p,
          ),
        }
      }
    },
    async revokeVote(retrospectiveId: string, cardId: string) {
      const api = useApiClient()
      const response = await api.delete<{ card_id: string; voter_id: string; votes_remaining: number }>(
        `/retrospectives/${retrospectiveId}/cards/${cardId}/vote/`,
      )
      this.votes = this.votes.filter((v) => !(v.card === response.card_id && v.voter === response.voter_id))
      if (this.current) {
        this.current = {
          ...this.current,
          participants: this.current.participants.map((p) =>
            p.user === response.voter_id ? { ...p, votes_remaining: response.votes_remaining } : p,
          ),
        }
      }
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

      if (type === "session.snapshot" && Array.isArray(event.action_items) && event.action_items.length > 0) {
        this.actionItems = event.action_items as ActionItem[]
      }

      if (type === "phase.changed" && this.current) {
        this.current = { ...this.current, status: event.phase as RetroPhase }
        this.previewPhase = null
      }

      if (type === "card.created" && event.card) {
        this.cards = upsertCard(this.cards, event.card as Card)
      }

      if (type === "card.updated") {
        if (event.card) {
          this.cards = upsertCard(this.cards, event.card as Card)
          return
        }
        this.cards = this.cards.map((card) =>
          card.id === event.card_id ? { ...card, content: String(event.content || card.content) } : card,
        )
      }

      if (type === "card.deleted") {
        this.cards = this.cards.filter((card) => card.id !== event.card_id)
      }

      if (type === "card.grouped") {
        const groupParentId = String(event.group_parent_id || event.group_id)
        this.cards = this.cards.map((card) =>
          card.id === event.card_id ? { ...card, group: groupParentId, group_parent_id: groupParentId } : card,
        )
      }

      if (type === "card.ungrouped") {
        this.cards = this.cards.map((card) =>
          card.id === event.card_id ? { ...card, group: null, group_parent_id: null } : card,
        )
      }

      if (type === "vote.cast") {
        const targetCardId = String(event.card_id || (event.vote as Vote | undefined)?.card || "")
        const voterId = String(event.voter_id || (event.vote as Vote | undefined)?.voter || "")
        this.cards = this.cards.map((card) =>
          card.id === targetCardId ? { ...card, vote_count: card.vote_count + 1 } : card,
        )
        if (voterId && targetCardId && !this.votes.find((v) => v.card === targetCardId && v.voter === voterId)) {
          this.votes = [...this.votes, { id: String((event.vote as Vote | undefined)?.id || ""), card: targetCardId, voter: voterId, created_at: new Date().toISOString() }]
        }
        const wsVotesRemaining = typeof event.votes_remaining === "number" ? event.votes_remaining : null
        if (wsVotesRemaining !== null && this.current) {
          this.current = {
            ...this.current,
            participants: this.current.participants.map((p) =>
              p.user === voterId ? { ...p, votes_remaining: wsVotesRemaining } : p,
            ),
          }
        }
      }

      if (type === "vote.revoked") {
        const targetCardId = String(event.card_id || "")
        const voterId = String(event.voter_id || "")
        this.cards = this.cards.map((card) =>
          card.id === targetCardId ? { ...card, vote_count: Math.max(0, card.vote_count - 1) } : card,
        )
        if (voterId && targetCardId) {
          this.votes = this.votes.filter((v) => !(v.card === targetCardId && v.voter === voterId))
        }
        const wsVotesRemaining = typeof event.votes_remaining === "number" ? event.votes_remaining : null
        if (wsVotesRemaining !== null && this.current) {
          this.current = {
            ...this.current,
            participants: this.current.participants.map((p) =>
              p.user === voterId ? { ...p, votes_remaining: wsVotesRemaining } : p,
            ),
          }
        }
      }

      if (type === "action.created" && event.action) {
        this.actionItems = upsertById(this.actionItems, event.action as ActionItem)
      }

      if (type === "action.updated" && event.action) {
        this.actionItems = upsertById(this.actionItems, event.action as ActionItem)
      }

      if (type === "action.deleted") {
        this.actionItems = this.actionItems.filter((item) => item.id !== event.action_id)
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
          author: event.author === null || event.author === undefined ? null : String(event.author),
          author_display: String(event.author_display || event.author || "Anonymous"),
          is_anonymous: Boolean(event.is_anonymous),
          column: event.column as DiscussionFocusPayload["column"],
          content: String(event.content),
          vote_count: Number(event.vote_count || 0),
        }
      }
    },
  },
})
