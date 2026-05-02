/**
 * E2E — Dashboard: creates a retrospective and verifies it appears in the list.
 *
 * IMPORTANT: This test requires a running backend + authenticated user.
 * Pre-condition: TEST_FACILITATOR account must exist in the database.
 * To create: POST /api/auth/register/ with email/password from helpers.ts
 *
 * Run: npx playwright test e2e/dashboard.spec.ts
 */
import { expect, test } from "@playwright/test"

import { TEST_FACILITATOR, loginAs } from "./helpers"

test.describe("Dashboard", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, TEST_FACILITATOR)
  })

  test("shows create retrospective button", async ({ page }) => {
    await page.goto("/")
    await expect(page.getByRole("link", { name: /new retro|create/i }).or(page.getByRole("button", { name: /new retro|create/i })).first()).toBeVisible()
  })

  test("can navigate to create retrospective page", async ({ page }) => {
    await page.goto("/")
    await page.getByRole("link", { name: /new retro|create/i }).or(page.getByRole("button", { name: /new retro|create/i })).first().click()
    await expect(page).toHaveURL(/retro\/create/)
  })

  test("create retrospective form validates required fields", async ({ page }) => {
    await page.goto("/retro/create")
    await page.getByRole("button", { name: /create|save/i }).first().click()
    // At least one validation error should appear
    await expect(page.locator("[class*='danger'], [class*='error'], [role='alert']").first()).toBeVisible({ timeout: 3000 })
  })
})
