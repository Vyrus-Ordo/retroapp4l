import type { RetroPhase } from "~/utils/types"

const orderedPhases: RetroPhase[] = [
  "setup",
  "lobby",
  "presentation",
  "check",
  "board",
  "grouping",
  "voting",
  "discussion",
  "actions",
  "closed",
]

export function usePhase() {
  function getPhaseLabel(phase: RetroPhase) {
    return phase.charAt(0).toUpperCase() + phase.slice(1)
  }

  function getNextPhase(phase: RetroPhase, skipCheckPhase = false) {
    const currentIndex = orderedPhases.indexOf(phase)
    if (currentIndex === -1 || currentIndex === orderedPhases.length - 1) {
      return phase
    }

    const next = orderedPhases[currentIndex + 1]
    if (skipCheckPhase && next === "check") {
      return orderedPhases[currentIndex + 2]
    }
    return next
  }

  return {
    orderedPhases,
    getPhaseLabel,
    getNextPhase,
  }
}