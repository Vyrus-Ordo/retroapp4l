/**
 * E2E — Auth flows (login, register)
 *
 * Requires: backend running, user accounts pre-created or registration enabled.
 * Run: npx playwright test e2e/auth.spec.ts
 */
import { expect, test } from "@playwright/test"

test.describe("Authentication", () => {
  test("login page renders form", async ({ page }) => {
    await page.goto("/auth/login")
    await expect(page.getByLabel(/email/i)).toBeVisible()
    await expect(page.getByLabel(/senha|password/i)).toBeVisible()
    await expect(page.getByRole("button", { name: /entrar/i })).toBeVisible()
  })

  test("register page renders form", async ({ page }) => {
    await page.goto("/auth/register")
    await expect(page.getByLabel(/name/i)).toBeVisible()
    await expect(page.getByLabel(/email/i)).toBeVisible()
  })

  test("login with invalid credentials shows error", async ({ page }) => {
    await page.goto("/auth/login")
    await page.getByLabel(/email/i).fill("nonexistent@example.com")
    await page.getByLabel(/senha|password/i).fill("wrongpassword")
    await page.getByRole("button", { name: /entrar/i }).click()
    await expect(page.getByRole("alert")).toBeVisible({ timeout: 5000 })
  })

  test("unauthenticated user redirected to login", async ({ page }) => {
    await page.goto("/")
    await page.waitForLoadState("networkidle")
    await expect(page).toHaveURL(/\/auth\/login(?:\?|$)/)
  })
})
