export type RetroPhase =
  | "setup"
  | "lobby"
  | "presentation"
  | "check"
  | "board"
  | "grouping"
  | "voting"
  | "discussion"
  | "actions"
  | "closed"

export type CardColumn = "loved" | "loathed" | "longed" | "learned"
export type ActionStatus = "not_started" | "in_progress" | "done"
export type MilestoneCategory = "achievement" | "challenge" | "change" | "recognition" | "other"

export interface User {
  id: string
  name: string
  email: string
  avatar_url: string | null
  oauth_provider: string | null
  created_at: string
}

export interface Participant {
  id: string
  user: string
  user_name: string
  user_email: string
  votes_remaining: number
  joined_at: string
}

export interface Milestone {
  id: string
  category: MilestoneCategory
  description: string
  author: string
  author_name: string
  created_at: string
}

export interface RetrospectiveSummary {
  id: string
  title: string
  sprint_name: string | null
  team_key: string
  status: RetroPhase
  facilitator: string
  facilitator_name: string
  created_at: string
}

export interface RetrospectiveDetail {
  id: string
  title: string
  sprint_name: string | null
  description: string | null
  team_key: string
  status: RetroPhase
  facilitator: string
  facilitator_name: string
  invite_token: string | null
  invite_revoked_at: string | null
  max_votes_per_user: number
  skip_check_phase: boolean
  focus_card_id: string | null
  timer_started_at: string | null
  timer_paused_at: string | null
  timer_duration_seconds: number | null
  created_at: string
  closed_at: string | null
  participants: Participant[]
  milestones: Milestone[]
}

export interface Card {
  id: string
  retrospective: string
  author: string
  author_name: string
  column: CardColumn
  content: string
  group: string | null
  position: number
  vote_count: number
  created_at: string
}

export interface Vote {
  id: string
  card: string
  voter: string
  created_at: string
}

export interface ActionItem {
  id: string
  retrospective: string
  card: string | null
  description: string
  assignee: string | null
  assignee_name: string | null
  participant_id: string | null
  due_date: string | null
  status: ActionStatus
  external_tracker_url: string | null
  created_at: string
}

export interface PreviousActionsResponse {
  retrospective_id: string | null
  action_items: ActionItem[]
}

export interface HistoryItem {
  id: string
  title: string
  sprint_name: string | null
  team_key: string
  closed_at: string
  cards_count: number
  action_items_count: number
  action_item_status_summary: Record<ActionStatus, number>
}

export interface HistoryDetail {
  id: string
  title: string
  sprint_name: string | null
  description: string | null
  team_key: string
  status: RetroPhase
  facilitator: string
  facilitator_name: string
  closed_at: string
  focus_card_id: string | null
  participants: Participant[]
  milestones: Milestone[]
  cards: Card[]
  votes: Vote[]
  action_items: ActionItem[]
}

export interface DiscussionFocusPayload {
  card_id: string
  author: string
  column: CardColumn
  content: string
  vote_count: number
}

export interface AuthResponse {
  user: User
  access: string
  refresh: string
}