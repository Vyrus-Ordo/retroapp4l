/**
 * E2E — Dashboard: the authenticated home exposes the create-retrospective
 * entry point and the create form rejects an empty submit.
 *
 * Requires: running backend + frontend. TEST_FACILITATOR is provisioned on
 * demand by ensureUser() in helpers.ts — see e2e/README.md.
 *
 * Run: docker compose -f docker-compose.dev.yml exec frontend npx playwright test e2e/dashboard.spec.ts
 */
import { TEST_FACILITATOR, expect, loginAs, test } from "./helpers"

const NEW_RETRO_LINK = { name: "New retrospective", exact: true } as const

test.describe("Dashboard", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, TEST_FACILITATOR)
  })

  test("shows create retrospective button", async ({ page }) => {
    await page.goto("/")

    await expect(page.getByRole("link", NEW_RETRO_LINK)).toBeVisible()
  })

  test("can navigate to create retrospective page", async ({ page }) => {
    await page.goto("/")
    await page.getByRole("link", NEW_RETRO_LINK).click()

    await expect(page).toHaveURL(/\/retro\/create$/)
    await expect(page.getByRole("heading", { name: "New retrospective" })).toBeVisible()
  })

  test("create retrospective form validates required fields", async ({ page }) => {
    await page.goto("/retro/create")

    await page.getByRole("button", { name: /create and go to lobby/i }).click()

    await expect(page.getByText(/title and team are required/i)).toBeVisible()
    await expect(page).toHaveURL(/\/retro\/create$/)
  })
})
