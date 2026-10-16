import { ArrowPathIcon, EllipsisHorizontalIcon, FireIcon, StarIcon, TrophyIcon } from "@heroicons/vue/24/outline"
import type { Component } from "vue"
import type { MilestoneCategory } from "~/utils/types"

export interface MilestoneVisual {
  color: string
  icon: Component
  label: string
}

export const MILESTONE_CATEGORIES: MilestoneCategory[] = ["achievement", "challenge", "change", "recognition", "other"]

export const MILESTONE_VISUALS: Record<MilestoneCategory, MilestoneVisual> = {
  achievement: { color: "#fbbf24", icon: TrophyIcon, label: "Achievement" },
  challenge: { color: "#f87171", icon: FireIcon, label: "Challenge" },
  change: { color: "#a78bfa", icon: ArrowPathIcon, label: "Change" },
  recognition: { color: "#f472b6", icon: StarIcon, label: "Recognition" },
  other: { color: "#a1a1aa", icon: EllipsisHorizontalIcon, label: "Other" },
}

export const DEFAULT_MILESTONE_VISUAL: MilestoneVisual = MILESTONE_VISUALS.other

export function getMilestoneVisual(category: string | null | undefined): MilestoneVisual {
  return MILESTONE_VISUALS[category as MilestoneCategory] ?? DEFAULT_MILESTONE_VISUAL
}
