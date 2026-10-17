/**
 * Unit spec for the milestone type visuals mapping.
 * No navigation — imports the mapping module and checks it directly.
 *
 * Run: npx playwright test e2e/milestone-visuals.spec.ts
 */
import { expect, test } from "@playwright/test"

import { MILESTONE_CATEGORIES, MILESTONE_VISUALS, getMilestoneVisual } from "../utils/milestoneVisuals"

const CARD_BACKGROUND = "#0f0f0f"
const CANVAS_BACKGROUND = "#050505"

const LABEL_MIN_CONTRAST = 4.5
const ICON_MIN_CONTRAST = 3

function relativeLuminance(hex: string): number {
  const channels = [0, 2, 4].map((i) => parseInt(hex.slice(1 + i, 3 + i), 16) / 255)
  const linear = channels.map((c) => (c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)))
  return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
}

function contrastRatio(a: string, b: string): number {
  const l1 = relativeLuminance(a)
  const l2 = relativeLuminance(b)
  const [lighter, darker] = l1 >= l2 ? [l1, l2] : [l2, l1]
  return (lighter + 0.05) / (darker + 0.05)
}

test.describe("Milestone visuals mapping", () => {
  test("every milestone type from the list has an entry, and no extras", () => {
    expect(Object.keys(MILESTONE_VISUALS).sort()).toEqual([...MILESTONE_CATEGORIES].sort())
  })

  test("the five colors are distinct from each other", () => {
    const colors = MILESTONE_CATEGORIES.map((category) => MILESTONE_VISUALS[category].color)
    expect(new Set(colors).size).toBe(MILESTONE_CATEGORIES.length)
  })

  test("the five icons are distinct from each other", () => {
    const icons = MILESTONE_CATEGORIES.map((category) => MILESTONE_VISUALS[category].icon)
    expect(new Set(icons).size).toBe(MILESTONE_CATEGORIES.length)
  })

  test("every color reaches WCAG contrast on the card and canvas backgrounds", () => {
    for (const background of [CARD_BACKGROUND, CANVAS_BACKGROUND]) {
      for (const category of MILESTONE_CATEGORIES) {
        const color = MILESTONE_VISUALS[category].color
        const ratio = contrastRatio(color, background)
        expect(ratio, `${category} label contrast (${color} over ${background})`).toBeGreaterThanOrEqual(
          LABEL_MIN_CONTRAST,
        )
        expect(ratio, `${category} icon contrast (${color} over ${background})`).toBeGreaterThanOrEqual(
          ICON_MIN_CONTRAST,
        )
      }
    }
  })

  test("unknown or missing category falls back to the neutral default", () => {
    expect(getMilestoneVisual("xyz")).toBe(MILESTONE_VISUALS.other)
    expect(getMilestoneVisual("")).toBe(MILESTONE_VISUALS.other)
    expect(getMilestoneVisual(undefined)).toBe(MILESTONE_VISUALS.other)
    expect(getMilestoneVisual(null)).toBe(MILESTONE_VISUALS.other)
  })
})
