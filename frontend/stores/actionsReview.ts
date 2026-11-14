import { defineStore } from "pinia"

import type {
  ActionReviewDetail,
  ActionReviewItem,
  ActionReviewPage,
  ActionReviewTeam,
  ActionStatus,
} from "~/utils/types"

export type ActionReviewOrdering =
  | "due_date"
  | "-due_date"
  | "status_updated_at"
  | "-status_updated_at"
  | "created_at"
  | "-created_at"

export interface ActionReviewFilters {
  teamKeys: string[]
  statuses: ActionStatus[]
  assignee: string | null
  overdue: boolean
  dueBefore: string
  dueAfter: string
  q: string
  ordering: ActionReviewOrdering
}

/**
 * Campos aceitos por `PATCH /api/actions/{id}/` (premissa D da spec).
 * `assignee_id` é opcional: quando ausente o backend mantém o responsável atual.
 */
export interface ActionReviewPatch {
  description: string
  assignee_id?: string | null
  due_date: string | null
  status: ActionStatus
  external_tracker_url: string
}

interface ActionReviewState {
  items: ActionReviewItem[]
  count: number
  page: number
  pageSize: number
  teams: ActionReviewTeam[]
  filters: ActionReviewFilters
  loading: boolean
  error: string | null
  selected: ActionReviewDetail | null
}

function defaultFilters(): ActionReviewFilters {
  return {
    teamKeys: [],
    statuses: ["not_started", "in_progress"],
    assignee: null,
    overdue: false,
    dueBefore: "",
    dueAfter: "",
    q: "",
    ordering: "due_date",
  }
}

/**
 * Monta a query string com parâmetros repetidos (`team_key=a&team_key=b`,
 * `status=not_started&status=in_progress`), nunca separados por vírgula.
 */
export function buildActionReviewQuery(
  filters: ActionReviewFilters,
  page: number,
  pageSize: number,
): string {
  const params = new URLSearchParams()

  for (const teamKey of filters.teamKeys) {
    if (teamKey) params.append("team_key", teamKey)
  }
  for (const status of filters.statuses) {
    params.append("status", status)
  }
  if (filters.assignee) params.append("assignee", filters.assignee)
  if (filters.overdue) params.append("overdue", "true")
  if (filters.dueBefore) params.append("due_before", filters.dueBefore)
  if (filters.dueAfter) params.append("due_after", filters.dueAfter)
  if (filters.q.trim()) params.append("q", filters.q.trim())
  params.append("ordering", filters.ordering)
  params.append("page", String(page))
  params.append("page_size", String(pageSize))

  return params.toString()
}

export const useActionsReviewStore = defineStore("actionsReview", {
  state: (): ActionReviewState => ({
    items: [],
    count: 0,
    page: 1,
    pageSize: 25,
    teams: [],
    filters: defaultFilters(),
    loading: false,
    error: null,
    selected: null,
  }),
  getters: {
    pageCount(state): number {
      return Math.max(1, Math.ceil(state.count / state.pageSize))
    },
    hasFilters(state): boolean {
      return JSON.stringify(state.filters) !== JSON.stringify(defaultFilters())
    },
  },
  actions: {
    async fetchTeams() {
      const api = useApiClient()
      try {
        this.teams = await api.get<ActionReviewTeam[]>("/actions/teams/")
      } catch {
        // O filtro por time degrada para "nenhum time listado" sem derrubar a lista.
        this.teams = []
      }
    },
    async fetchActions() {
      const api = useApiClient()
      this.loading = true
      this.error = null

      try {
        const query = buildActionReviewQuery(this.filters, this.page, this.pageSize)
        const response = await api.get<ActionReviewPage>(`/actions/?${query}`)
        this.items = response.results
        this.count = response.count
      } catch (error) {
        this.items = []
        this.count = 0
        this.error = error instanceof Error ? error.message : "Unable to load actions."
      } finally {
        this.loading = false
      }
    },
    async fetchDetail(id: string) {
      const api = useApiClient()
      this.selected = null
      this.selected = await api.get<ActionReviewDetail>(`/actions/${id}/`)
      return this.selected
    },
    async updateAction(id: string, patch: ActionReviewPatch) {
      const api = useApiClient()
      const updated = await api.patch<ActionReviewDetail, ActionReviewPatch>(`/actions/${id}/`, patch)

      this.items = this.items.map((item) => (item.id === id ? updated : item))
      if (this.selected?.id === id) {
        this.selected = updated
      }
      return updated
    },
    clearSelection() {
      this.selected = null
    },
    resetFilters() {
      this.filters = defaultFilters()
      this.page = 1
    },
  },
})
