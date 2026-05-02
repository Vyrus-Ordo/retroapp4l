/**
 * E2E — Smoke tests for key UI pages.
 * These tests only check rendering, not interaction with the backend.
 *
 * Run: npx playwright test e2e/smoke.spec.ts
 */
import { expect, test } from "@playwright/test"

test.describe("Smoke tests", () => {
  test("home page loads without JS errors", async ({ page }) => {
    const errors: string[] = []
    page.on("pageerror", (error) => errors.push(error.message))
    await page.goto("/")
    // Allow redirect to login — still valid
    await page.waitForLoadState("networkidle")
    expect(errors.filter((e) => !e.includes("ResizeObserver"))).toHaveLength(0)
  })

  test("login page is accessible", async ({ page }) => {
    await page.goto("/auth/login")
    await expect(page).toHaveTitle(/.+/)
    // Check for basic ARIA landmarks
    await expect(page.locator("main, [role='main']").first()).toBeVisible()
  })

  test("register page is accessible", async ({ page }) => {
    await page.goto("/auth/register")
    await expect(page.getByRole("heading").first()).toBeVisible()
  })

  test("history page redirects unauthenticated users", async ({ page }) => {
    await page.goto("/history")
    await page.waitForLoadState("networkidle")
    const isOnLogin = page.url().includes("/auth/login")
    const hasLoginButton = await page.getByRole("link", { name: /log in/i }).isVisible().catch(() => false)
    expect(isOnLogin || hasLoginButton).toBeTruthy()
  })
})
