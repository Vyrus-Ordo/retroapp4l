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
    await expect(page.getByLabel(/password/i)).toBeVisible()
    await expect(page.getByRole("button", { name: /log in|sign in/i })).toBeVisible()
  })

  test("register page renders form", async ({ page }) => {
    await page.goto("/auth/register")
    await expect(page.getByLabel(/name/i)).toBeVisible()
    await expect(page.getByLabel(/email/i)).toBeVisible()
  })

  test("login with invalid credentials shows error", async ({ page }) => {
    await page.goto("/auth/login")
    await page.getByLabel(/email/i).fill("nonexistent@example.com")
    await page.getByLabel(/password/i).fill("wrongpassword")
    await page.getByRole("button", { name: /log in|sign in/i }).click()
    // Expect an error message to be visible
    await expect(page.locator("[role=alert], .text-danger-500, [class*='danger']").first()).toBeVisible({ timeout: 5000 })
  })

  test("unauthenticated user redirected to login", async ({ page }) => {
    await page.goto("/")
    // Should redirect to login or show login button
    const isOnLogin = page.url().includes("/auth/login")
    const hasLoginButton = await page.getByRole("link", { name: /log in/i }).isVisible().catch(() => false)
    expect(isOnLogin || hasLoginButton).toBeTruthy()
  })
})
