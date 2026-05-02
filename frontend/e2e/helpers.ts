/**
 * E2E helpers shared across test files.
 * Requires a running backend and frontend (docker-compose up -d + npm run dev).
 */
import { type Page, expect } from "@playwright/test"

export const TEST_FACILITATOR = {
  email: "e2e_facilitator@example.com",
  password: "E2eTestPass123!",
  name: "E2E Facilitator",
}

export const TEST_PARTICIPANT = {
  email: "e2e_participant@example.com",
  password: "E2eTestPass123!",
  name: "E2E Participant",
}

export async function loginAs(page: Page, user: { email: string; password: string }) {
  await page.goto("/auth/login")
  await page.getByLabel(/email/i).fill(user.email)
  await page.getByLabel(/password/i).fill(user.password)
  await page.getByRole("button", { name: /log in|sign in/i }).click()
  await expect(page).not.toHaveURL(/login/)
}
