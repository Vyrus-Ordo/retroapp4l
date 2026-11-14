/**
 * E2E — Auth flows (login, register, route guard)
 *
 * Requires: backend running. Test users are provisioned on demand by
 * ensureUser() in helpers.ts — see e2e/README.md.
 * Run: docker compose -f docker-compose.dev.yml exec frontend npx playwright test e2e/auth.spec.ts
 */
import { expect, test } from "./helpers"

test.describe("Authentication", () => {
  test("login page renders form", async ({ page }) => {
    await page.goto("/auth/login")

    await expect(page.getByRole("heading", { name: /sign in to retroapp/i })).toBeVisible()
    await expect(page.getByLabel(/email/i)).toBeVisible()
    await expect(page.getByLabel(/password/i)).toBeVisible()
    await expect(page.getByRole("button", { name: /^sign in$/i })).toBeVisible()
  })

  test("register page renders form", async ({ page }) => {
    await page.goto("/auth/register")
    await expect(page.getByLabel(/name/i)).toBeVisible()
    await expect(page.getByLabel(/email/i)).toBeVisible()
  })

  test("login with invalid credentials shows error", async ({ page }) => {
    await page.goto("/auth/login")

    const form = page.locator("form")
    await form.getByLabel(/email/i).fill("nonexistent@example.com")
    await form.getByLabel(/password/i).fill("wrongpassword")
    await form.getByRole("button", { name: /^sign in$/i }).click()

    // The backend rejects the credentials and the form surfaces that message.
    await expect(form.getByRole("alert")).toHaveText(/invalid credentials/i, { timeout: 10_000 })
    await expect(page).toHaveURL(/\/auth\/login/)
  })

  test("unauthenticated user redirected to login", async ({ page }) => {
    // "/" is a public landing page for anonymous users; the guard applies to
    // protected routes and must preserve the intended destination.
    await page.goto("/history")

    await expect(page).toHaveURL(/\/auth\/login\?redirect=\/history$/)
    await expect(page.getByLabel(/email/i)).toBeVisible()
  })
})
